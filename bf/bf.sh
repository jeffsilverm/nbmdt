#!/usr/bin/env bash
# bf.sh — Browser/Network Failure Lab controller (controller-first edition)
#
# USAGE:
#   sudo ./bf.sh <OPERATION> <SUBSYSTEM>
#
# OPERATIONS:
#   test | break | fix | all
#   (all = test → break → test → fix → test, with sanity stops)
#
# SUBSYSTEMS (case-insensitive):
#   dns
#   ssl | tls
#   routing-isp
#   routing-local
#   local-connectivity
#   wifi
#   nic
#   packet-loss
#
# ENV OVERRIDES (optional):
#   PUBLIC_TARGET=1.1.1.1     # for routing-isp checks
#   HTTPS_HOST=https://example.com
#   DNS_NAME=example.com
#   LOSS_PCT=74             # tc netem loss percentage for packet-loss
#
# REQUIREMENTS:
#   - Run as root for break/fix (and some test ops).
#   - nftables preferred; iptables is used as fallback.
#   - tc (iproute2) for packet-loss simulation.
#
# TEACHING NOTES:
#   This script centralizes the demo flow so students memorize: test → break → test → fix → test.
#   It only touches state that it creates, and drops breadcrumbs in /tmp/bflab_* to allow clean fixes.
#   One of the openssl errors it is going to check for touches /etc/hosts
#
# # Any comment that has a unicode emoticon e.g. 💣 is [supposed to be] a joke.
set -euo pipefail


# ---------- helpers ----------
require_root() { [[ $EUID -eq 0 ]] || { lecho  "🌧 $WHITE_ON_RED  Please run as root (sudo)."; exit 1; }; }
has(){ command -v "$1" >>$LOG_FILE 2>&1; }
has_nft(){ has nft; } ; has_ipt(){ has iptables; } ; has_ip6t(){ has ip6tables; }
# Colors for VT-100 (ANSI X3.64) escape sequences.  This will also work on a linux console
WHITE_ON_RED='\033[37;41m'
BLACK_ON_RED='\033[30;41m'
BLACK_ON_YELLOW='\033[30;43m'
WHITE_ON_GREEN='\033[37;42m'
BLACK_ON_GREEN='\033[30;42m'
RESET='\033[0m'

lecho() { echo -e "$@ ${RESET}" ; return 0; }


primary_iface() {
  # Choose a harmless target that exercises normal routing.
  # local target="${PUBLIC_TARGET:-1.1.1.1}"
  local dev

  if ip -4 route get "$PUBLIC_TARGET" 2>>"$LOG_FILE" >/tmp/.rt.$$; then
    dev=$(awk '{for(i=1;i<=NF;i++) if($i=="dev"){print $(i+1); exit}}' /tmp/.rt.$$)
    rm -f /tmp/.rt.$$ 
    [[ -n "$dev" ]] && { echo  "$dev"; return; }
  fi

  # Fallback: first UP non-loopback interface
  ip -o link show up | awk -F': ' '$2 !~ /lo/ {print $2; exit}'
}

default_gw(){ ip route show default 2>>$LOG_FILE | awk '/default via/ {print $3; exit}'; }

# echo1 I actually thought of second, but I didn't want to call it echo3.
# Write the arguments both the stdout and the log file unconditionally.
echo1() { lecho  $@ | tee -a $LOG_FILE ; }

VERBOSE_FLAG=$([[ "${3-}" == "verbose" ]] && echo true || echo false)    # If $3 is unset, then expand to empty string

# echo2 is a good idea, I just thought of it too late.  But if I ever refactor this bash script....
echo2() {
# If the verbose flag is set, then log the arguments to both stdout and the log file, otherwise
# just the log file
  if $VERBOSE_FLAG; then
    echo1 $@
  fi
  lecho $@ >> $LOG_FILE
  
}



# For testing purposes only!
# lecho  "🌧 $${BLACK_ON_RED} ERROR: Network unreachable ${RESET} Error"
# lecho  "❌ ${WHITE_ON_RED} ERROR: Network unreachable ${RESET} Error"
# lecho  "⚠️ ${BLACK_ON_YELLOW} WARNING: DNS lookup slow ${RESET} Warning"
# lecho  "✅ ${WHITE_ON_GREEN} SUCCESS: Link up and verified ${RESET} Okay"
# lecho  "✅✅ ${BLACK_ON_GREEN} OK: Counters nominal ${RESET} Okay"


# if PUBLIC_TARGET, HTTPS_HOST, or DNS_NAME are defined by the caller of this script, then
# use those values.
# jeffsilverm.ddns.net works better for test purposes than example.com or f5.com
PUBLIC_TARGET="${PUBLIC_TARGET:-1.1.1.1}"
HTTPS_HOST="${HTTPS_HOST:-https://jeffsilverm.ddns.net}"
DNS_NAME="${DNS_NAME:-example.com}"

NFT_FAMILY="inet"
NFT_DNS="bflab_dns"
IPT_CHAIN="BFLAB"
DATE=$(date -Isec)		# date string in ISO 8601 format, suitable for use in a filename
LOG_FILE="/tmp/$0_${DATE}.log"
echo  $DATE > $LOG_FILE
echo  "Log file, if any, in $LOG_FILE"

SSL_CA_DIR="/tmp/bflab_ssl_ca"
SSL_CA_KEY="$SSL_CA_DIR/ca.key"
SSL_CA_CRT="$SSL_CA_DIR/ca.crt"
SSL_CA_IDX="$SSL_CA_DIR/index.txt"      # This appears in the SSL_CACNF file

SSL_DEMO_DIR="/tmp/bflab_ssl_demo"
SSL_SRV_KEY="$SSL_DEMO_DIR/server.key"
SSL_SRV_CSR="$SSL_DEMO_DIR/server.csr"
SSL_SRV_BAD_CRT="$SSL_DEMO_DIR/server_BAD.crt"
SSL_SRV_GOOD_CRT="$SSL_DEMO_DIR/server_GOOD.crt"
SSL_SRV_PID="$SSL_DEMO_DIR/server.pid"
SSL_SRV_PORT="${SSL_SRV_PORT:-8443}"

DNS_TEST_REAL_HOST="google.com"
DNS_TEST_FAKE_HOST="g00gle.com"
DNS_GOOGLE_IPv4_ADDR="142.251.32.46"

HOST_TO_TEST=$DNS_TEST_REAL_HOST
# If the network isn't working (because I broke it), then relying on the network
# to get a critical IPv4 address is probably a bad idea.
if HOST_TO_TEST_IPv4_ADDR=$(dig +short $HOST_TO_TEST); then
    echo2 "dig is working"; 
  else
    echo1 "🌧 $WHITE_ON_RED  dig +short $HOST_TO_TEST failed.  Why?  Don't know.  Using $DNS_GOOGLE_IPv4_ADDR"
    HOST_TO_TEST_IPv4_ADDR=$DNS_GOOGLE_IPv4_ADDR
  fi


ensure_nft_table(){ local t="$1"; nft list table $NFT_FAMILY "$t" >>$LOG_FILE 2>&1 || nft add table $NFT_FAMILY "$t"; }
delete_nft_table(){ local t="$1"; nft list table $NFT_FAMILY "$t" >>$LOG_FILE 2>&1 && nft delete table $NFT_FAMILY "$t" || true; }

ensure_ipt_chain(){
  iptables -nL "$IPT_CHAIN" >>$LOG_FILE 2>&1 || iptables -N "$IPT_CHAIN"
  iptables -C OUTPUT -j "$IPT_CHAIN" >>$LOG_FILE 2>&1 || iptables -A OUTPUT -j "$IPT_CHAIN"
  if has_ip6t; then
    ip6tables -nL "$IPT_CHAIN" >>$LOG_FILE 2>&1 || ip6tables -N "$IPT_CHAIN"
    ip6tables -C OUTPUT -j "$IPT_CHAIN" >>$LOG_FILE 2>&1 || ip6tables -A OUTPUT -j "$IPT_CHAIN"
  fi
}
flush_ipt_chain(){
  iptables -D OUTPUT -j "$IPT_CHAIN" 2>>$LOG_FILE || true
  iptables -F "$IPT_CHAIN" 2>>$LOG_FILE || true
  iptables -X "$IPT_CHAIN" 2>>$LOG_FILE || true
  if has_ip6t; then
    ip6tables -D OUTPUT -j "$IPT_CHAIN" 2>>$LOG_FILE || true
    ip6tables -F "$IPT_CHAIN" 2>>$LOG_FILE || true
    ip6tables -X "$IPT_CHAIN" 2>>$LOG_FILE || true
  fi
}

# ---------- dns ----------
test_dns(){
# Network Troubleshooting 101:
#   Step 1: It’s DNS.
#   Step 2: No, really — it’s DNS.
#   Step 3: OK, fine… it was the firewall.
  echo  "== DNS test == " | tee -a $LOG_FILE
  if has dig; then
    echo  "Using dig" | tee -a $LOG_FILE
    dig +time=2 +tries=1 "$DNS_NAME" >>$LOG_FILE 2>&1 && { lecho  "✅ $BLACK_ON_GREEN  DNS OK ($DNS_NAME) $RESET"; return 0; }
    lecho  "❌ $BLACK_ON_RED DNS failed ($DNS_NAME)"  |  tee -a $LOG_FILE ; return 1
  else
    echo  "Using getent" | tee -a $LOG_FILE
    getent hosts "$DNS_NAME" >> $LOG_FILE 2>&1 && { lecho  "✅ $BLACK_ON_GREEN  DNS OK via getent ($DNS_NAME) $RESET"; return 0; }
    lecho  "❌ $BLACK_ON_RED DNS failed via getent ($DNS_NAME) $RESET" |  tee -a $LOG_FILE ; return 1
  fi
}
break_dns(){
  require_root; echo  "== DNS break: drop UDP/TCP 53 ==" | tee -a $LOG_FILE
  if has_nft; then
    echo  "Using NFT" | tee -a $LOG_FILE
    ensure_nft_table "$NFT_DNS"
    nft 'add chain inet '"$NFT_DNS"' out { type filter hook output priority 0 ; }' 2>>$LOG_FILE || true
    nft add rule inet "$NFT_DNS" out udp dport 53 drop 2>>$LOG_FILE || true
    nft add rule inet "$NFT_DNS" out tcp dport 53 drop 2>>$LOG_FILE || true
  elif has_ipt; then
    echo  "Using iptables" | tee -a $LOG_FILE
    ensure_ipt_chain
    iptables -A "$IPT_CHAIN" -p udp --dport 53 -j DROP
    iptables -A "$IPT_CHAIN" -p tcp --dport 53 -j DROP
    if has_ip6t; then
      ip6tables -A "$IPT_CHAIN" -p udp --dport 53 -j DROP
      ip6tables -A "$IPT_CHAIN" -p tcp --dport 53 -j DROP
    fi
  else
    lecho  "🌧 $WHITE_ON_RED  No nftables/iptables available." | tee -a $LOG_FILE
    exit 1
  fi
}
fix_dns(){
  require_root; echo  "== DNS fix: remove rules ==" | tee -a $LOG_FILE
  if has_nft; then delete_nft_table "$NFT_DNS"; elif has_ipt; then flush_ipt_chain; fi
}


# ---------- routing-isp (beyond border) ----------
# ⚙️ The OSI model, simplified:
#   7. Application
#   6. Presentation
#   5. Session
#   4. Transport
#   3. Network
#   2. Data Link
#   1. Physical
#   0. User: "Why doesn’t it work?"   😢
test_routing_isp(){ echo  "== Routing (ISP) test: ping ${PUBLIC_TARGET} ==" | tee -a $LOG_FILE
ping -c 2 -W 1 "${PUBLIC_TARGET}" >> $LOG_FILE 2>&1 && { lecho  "✅ $BLACK_ON_GREEN  Reachable: ${PUBLIC_TARGET}"; return 0; } || { lecho  "❌ $BLACK_ON_RED Unreachable: ${PUBLIC_TARGET}"; return 1; } | tee -a $LOG_FILE; }
#break_routing_isp(){ require_root; echo1 "== Routing (ISP) break: blackhole ${PUBLIC_TARGET} ==" ; lecho  "${PUBLIC_TARGET}" > /tmp/bflab_isp_target; ip route replace blackhole "${PUBLIC_TARGET}" || true; }

# Resolve a token to one or more IPv4 addresses (A records).
# If the token is already an IPv4 (optionally with /CIDR), just echo it back.
_resolve_ipv4s() {
  local name="$1"
  # IPv4 or IPv4/CIDR
  if [[ "$name" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}(/([0-9]|[12][0-9]|3[0-2]))?$ ]]; then
    printf '%s\n' "$name"
    return 0
  fi

  # Try dig (A records)
  if command -v dig >/dev/null 2>&1; then
    dig +short A "$name" 2>>"$LOG_FILE" | awk '/^[0-9.]+$/' | sort -u
  fi

  # Fallback: getent (ahostsv4)
  if command -v getent >/dev/null 2>&1; then
    getent ahostsv4 "$name" 2>>"$LOG_FILE" | awk '{print $1}' | awk '/^[0-9.]+$/' | sort -u
  fi
}

break_routing_isp(){
  require_root
  local target="${PUBLIC_TARGET:-${1:-}}"
  [[ -z "$target" ]] && target="1.1.1.1"

  echo "== Routing (ISP) break: blackhole '${target}' ==" | tee -a "$LOG_FILE"

  # Resolve to IPv4s or accept IP/CIDR
  mapfile -t _ips < <(_resolve_ipv4s "$target")
  if [[ ${#_ips[@]} -eq 0 ]]; then
    echo "🌧 Could not resolve or parse '$target' into IPv4(s)." | tee -a "$LOG_FILE"
    exit 1
  fi

  # Record destinations we blackhole (one per line) for later fixes
  : > /tmp/bflab_isp_targets

  local dest
  for ip in "${_ips[@]}"; do
    # If no CIDR given, force /32 host route to avoid classful surprises
    if [[ "$ip" == */* ]]; then
      dest="$ip"
    else
      dest="$ip/32"
    fi
    echo "Blackholing $dest" | tee -a "$LOG_FILE"
    # replace is idempotent per-destination; add would also work if unique
    if ip route replace blackhole "$dest" 2>>"$LOG_FILE"; then
      printf '%s\n' "$dest" >> /tmp/bflab_isp_targets
    else
      echo "🌧 Failed to blackhole $dest (see log)" | tee -a "$LOG_FILE"
    fi
  done
}





## fix_routing_isp() ### { require_root; lecho  "== Routing (ISP) fix: remove blackhole ==" | tee -a $LOG_FILE; [[ -f /tmp/bflab_isp_target ]] && { ip route del blackhole "$(cat /tmp/bflab_isp_target)" 2>>$LOG_FILE || true; rm -f /tmp/bflab_isp_target; } || true; }
fix_routing_isp(){
  require_root
  echo "== Routing (ISP) fix: remove blackhole routes ==" | tee -a "$LOG_FILE"

  local found=0

  # Strict pass: only lines that are exactly "blackhole <DEST>"
  while read -r line; do
    # Skip empty
    [[ -z "${line// /}" ]] && continue
    # Tokenize the line into positional parameters
    set -- $line
    if [[ $# -eq 2 && "$1" == "blackhole" ]]; then
      echo "Deleting blackhole route to '$2'" | tee -a "$LOG_FILE"
      if ip route del "$2" 2>>"$LOG_FILE"; then
        echo "✅ Removed blackhole $2" | tee -a "$LOG_FILE"
        found=1
      else
        echo "🌧 Failed to delete blackhole $2 (see log)" | tee -a "$LOG_FILE"
      fi
    fi
  done < <(ip -4 route list 2>>"$LOG_FILE" | fgrep blackhole)

  # Fallback: if nothing matched the strict pattern, try a safer parse
  if [[ $found -eq 0 ]]; then
    while read -r dst; do
      [[ -z "${dst:-}" ]] && continue
      echo "Fallback deleting blackhole '$dst'" | tee -a "$LOG_FILE"
      ip route del "$dst" 2>>"$LOG_FILE" || true
    done < <(ip -4 route list 2>>"$LOG_FILE" | awk '$1=="blackhole"{print $2}')
  fi

  # Clean up the older breadcrumb (no longer relied upon)
  rm -f /tmp/bflab_isp_target
}


# ---------- routing-local (default gateway) ----------
test_routing_local(){
  echo  "== Routing (local) test: default route/gateway =="
  local gw; gw=$(default_gw)
  [[ -z "${gw:-}" ]] && { lecho  "❌ $BLACK_ON_RED No default route"; return 1; }
  echo  "Gateway: $gw"; ping -c 2 -W 1 "$gw" >/dev/null 2>&1 && { lecho  "✅ $BLACK_ON_GREEN  GW reachable"; return 0; } || { lecho  "❌ $BLACK_ON_RED GW unreachable"; return 1; }
}

break_routing_local(){
  require_root; echo  "== Routing (local) break: remove defaults ==" | tee -a $LOG_FILE
  ip route show default > /tmp/bflab_default_route.txt || true
  ip -6 route show default > /tmp/bflab_default_route6.txt || true
  ip route del default 2>>$LOG_FILE || true
  ip -6 route del default 2>>$LOG_FILE || true
  if $VERBOSE_FLAG; then
    echo  "== Default IPv4 gateway (route) ==" >> $LOG_FILE
    cat /tmp/bflab_default_route.txt >> $LOG_FILE
    echo  "== Default IPv6 gateway (route) ==" >> $LOG_FILE
    cat /tmp/bflab_default_route6.txt >> $LOG_FILE
  fi
}
fix_routing_local(){
  require_root; echo  "== Routing (local) fix: restore defaults ==" | tee -a $LOG_FILE
  if [[ -s /tmp/bflab_default_route.txt ]]; then
    while read -r line; do ip route add ${line#default } 2>>$LOG_FILE || true; done < /tmp/bflab_default_route.txt
    rm -f /tmp/bflab_default_route.txt
  fi
  if [[ -s /tmp/bflab_default_route6.txt ]]; then
    while read -r line; do ip -6 route add ${line#default } 2>>$LOG_FILE || true; done < /tmp/bflab_default_route6.txt
    rm -f /tmp/bflab_default_route6.txt
  fi
  # local IF; IF=$(primary_iface || true)    # Moved to within the dispatcher
  has nmcli && [[ -n "${IF:-}" ]] && nmcli device reapply "$IF" 2>>$LOG_FILE || true
  has dhclient && [[ -n "${IF:-}" ]] && { dhclient -r "$IF" 2>>$LOG_FILE || true; dhclient "$IF" 2>>$LOG_FILE || true; }
}

# ---------- local-connectivity (keep NIC up; block GW host) ----------
test_local_connectivity(){
  local gw; gw=$(default_gw)
  echo  "== Local connectivity: ping gateway host $gw ==" | tee -a $LOG_FILE
  [[ -z "${gw:-}" ]] && { lecho  "❌ $BLACK_ON_RED No default route"; return 1; }
  ping -c 2 -W 1 "$gw" >> $LOG_FILE  2>&1 && { lecho  "✅ $BLACK_ON_GREEN  Gateway $gw reachable on LAN" | tee -a $LOG_FILE; return 0; } || { lecho  "❌ $BLACK_ON_RED GW $gw not reachable" | tee -a $LOG_FILE; return 1; }
}
break_local_connectivity(){
  require_root;
  local gw; gw=$(default_gw)
  echo  "== Local connectivity break: blackhole GW host $gw ==" | tee -a $LOG_FILE
  [[ -z "${gw:-}" ]] && { echo  "No default route; nothing to do." | tee -a $LOG_FILE; return 0; }
  echo  "$gw" > /tmp/bflab_blackhole_gw
  ip route replace blackhole "$gw" || true
}
fix_local_connectivity(){
  require_root;
  local gw; gw=$(default_gw)
  echo  "== Local connectivity fix: remove GW blackhole $gw ==" | tee -a $LOG_FILE
  [[ -f /tmp/bflab_blackhole_gw ]] && { ip route del blackhole "$(cat /tmp/bflab_blackhole_gw)" 2>>$LOG_FILE || true; rm -f /tmp/bflab_blackhole_gw; } || true
}

# ---------- wifi (nmcli) ----------
test_wifi(){
  echo  "== Wi‑Fi test ==" | tee -a $LOG_FILE;
  has nmcli || { echo  "nmcli not available" | tee -a $LOG_FILE; return 2; };
  local s; s=$(nmcli -t -f WIFI g 2>>$LOG_FILE | tr '[:upper:]' '[:lower:]' || true);
  [[ "$s" == "enabled" ]] && { lecho  "✅ $BLACK_ON_GREEN  Wi‑Fi enabled" | tee -a $LOG_FILE; return 0; } || { lecho  "❌ $BLACK_ON_RED Wi‑Fi disabled" | tee -a $LOG_FILE; return 1; }
}
break_wifi(){
  require_root
  echo  "== Wi‑Fi break: radio off ==" | tee -a $LOG_FILE
  has nmcli && { nmcli radio wifi off || true; : > /tmp/bflab_wifi_disabled; } || echo  "nmcli not available" | tee -a $LOG_FILE;
}
fix_wifi(){
  require_root
  echo  "== Wi‑Fi fix: radio on ==" | tee -a $LOG_FILE
  [[ -f /tmp/bflab_wifi_disabled ]] && { has nmcli && nmcli radio wifi on || true; rm -f /tmp/bflab_wifi_disabled; } || true;
}

# ---------- nic (bring link down/up) ----------
#
# 🧭 VPN Advisory:
#   Many VPN clients (e.g., WireGuard, OpenVPN, strongSwan) bind their tunnel
#   to a specific *physical interface* when the VPN connects.
#   When that interface goes down (via `ip link set IF down` or a hardware event),
#   the kernel deletes the route(s) associated with that device.
#
#   Even though the kernel could theoretically reroute traffic through another
#   interface, the VPN software will *not* fail over automatically — its socket
#   remains bound to a dead device.
#
#   Symptoms:
#     - The VPN process still appears "connected"
#     - The tun/tap interface (e.g., tun0) still exists
#     - No traffic flows through the VPN tunnel
#
#   ✅ Lesson learned:
#     *Always turn off or disconnect the VPN before breaking a NIC.*
#     Otherwise, the VPN must be restarted after the NIC is restored.
#
#   Recovery example:
#       nmcli con down <vpn_name>
#       nmcli con up <vpn_name>
#
#   This behavior makes a good demonstration of OSI layer coupling:
#     Layer 3 (routing) can recover, but Layer 4 (VPN socket) cannot unless
#     the session is re-established.

#
#

test_nic(){
  echo  "== NIC counter test (using only kernel stats) ==" | tee -a "$LOG_FILE"

  # If we previously broke a NIC, test that same interface; otherwise use primary
  local ifc
  if [[ -f /tmp/bflab_nic_iface ]]; then
    ifc="$(cat /tmp/bflab_nic_iface)"
  else
    ifc="${IF:-$(primary_iface || true)}"
  fi

  if [[ -z "${ifc:-}" ]]; then
    lecho  "🌧 $WHITE_ON_RED  No interface to test (none recorded; no primary found)." | tee -a "$LOG_FILE"
    return 1
  fi
  echo  "Interface under test: $ifc." | tee -a "$LOG_FILE"

  _stat() { cat "/sys/class/net/$1/statistics/$2" 2>/dev/null || echo  0; }
  _uptime_secs() { awk '{print int($1)}' /proc/uptime 2>/dev/null || echo  0; }

  local rx1 tx1 rxerr1 txerr1 rxd1 txd1 coll1 carr1
  rx1=$(_stat "$ifc" rx_packets);  tx1=$(_stat "$ifc" tx_packets)
  rxerr1=$(_stat "$ifc" rx_errors); txerr1=$(_stat "$ifc" tx_errors)
  rxd1=$(_stat "$ifc" rx_dropped);  txd1=$(_stat "$ifc" tx_dropped)
  coll1=$(_stat "$ifc" collisions); carr1=$(_stat "$ifc" tx_carrier_errors)
  local up1; up1=$(_uptime_secs)

  local gw; gw=$(default_gw || true)
  [[ -n "${gw:-}" ]] && ping -c 3 -W 1 "$gw" >/dev/null 2>&1 || true

  local SLEEP_SEC=5; sleep "$SLEEP_SEC"

  local rx2 tx2 rxerr2 txerr2 rxd2 txd2 coll2 carr2
  rx2=$(_stat "$ifc" rx_packets);  tx2=$(_stat "$ifc" tx_packets)
  rxerr2=$(_stat "$ifc" rx_errors); txerr2=$(_stat "$ifc" tx_errors)
  rxd2=$(_stat "$ifc" rx_dropped);  txd2=$(_stat "$ifc" tx_dropped)
  coll2=$(_stat "$ifc" collisions); carr2=$(_stat "$ifc" tx_carrier_errors)
  local up2; up2=$(_uptime_secs)

  local drx=$((rx2-rx1)) dtx=$((tx2-tx1)) drxerr=$((rxerr2-rxerr1)) dtxerr=$((txerr2-txerr1))
  local drxd=$((rxd2-rxd1)) dtxd=$((txd2-txd1)) dcoll=$((coll2-coll1)) dcarr=$((carr2-carr1))
  local uph=$(( up2>0 ? (up2+3599)/3600 : 1 ))

  {
    echo  "Window: ${SLEEP_SEC}s"
    printf "RX pkts: %d -> %d  (Δ=%d)\n" "$rx1" "$rx2" "$drx"
    printf "TX pkts: %d -> %d  (Δ=%d)\n" "$tx1" "$tx2" "$dtx"
    printf "RX errors Δ=%d (total=%d), TX errors Δ=%d (total=%d)\n" "$drxerr" "$rxerr2" "$dtxerr" "$txerr2"
    printf "RX dropped Δ=%d (total=%d), TX dropped Δ=%d (total=%d)\n" "$drxd" "$rxd2" "$dtxd" "$txd2"
    printf "Collisions Δ=%d (total=%d), TX carrier errs Δ=%d (total=%d)\n" "$dcoll" "$coll2" "$dcarr" "$carr2"
    echo  "Uptime (hours, ceil): $uph  → “small” total threshold ≈ <$uph"
  } | tee -a "$LOG_FILE"

  local status=0
  if (( drx + dtx <= 0 )); then
    lecho  "⚠️ $BLACK_ON_YELLOW  $BLACK_ON_YELLOW   No packet movement in ${SLEEP_SEC}s — link may be idle/down." | tee -a "$LOG_FILE"
    status=1
  else
    lecho  "✅ Packet movement observed (ΔRX=$drx, ΔTX=$dtx)." | tee -a "$LOG_FILE"
  fi
  (( drxerr>0 || dtxerr>0 )) && lecho  "⚠️ $BLACK_ON_YELLOW  $BLACK_ON_YELLOW   Errors increased (Δrx_err=$drxerr, Δtx_err=$dtxerr)." | tee -a "$LOG_FILE"

  (( rxd2>uph || txd2>uph )) && lecho  "⚠️ $BLACK_ON_YELLOW  $BLACK_ON_YELLOW   Drops high for $uph h (rx_dropped=$rxd2, tx_dropped=$txd2)." | tee -a "$LOG_FILE"
  (( coll2>uph )) && lecho  "⚠️ $BLACK_ON_YELLOW  $BLACK_ON_YELLOW   Collisions high for $uph h (collisions=$coll2)." | tee -a "$LOG_FILE"
  (( carr2>uph )) && lecho  "⚠️ $BLACK_ON_YELLOW  $BLACK_ON_YELLOW   Carrier errs high for $uph h (tx_carrier_errors=$carr2)." | tee -a "$LOG_FILE"

  return "$status"
}


break_nic(){
  require_root
  local ifc="${IF:-$(primary_iface || true)}"
  [[ -z "$ifc" ]] && { echo  "No interface found." | tee -a "$LOG_FILE"; return 0; }
  echo  "$ifc" > /tmp/bflab_nic_iface
  echo  "== NIC break: '$ifc' down ==" | tee -a "$LOG_FILE"
  ip link set "$ifc" down
}




fix_nic(){
  require_root
  [[ -f /tmp/bflab_nic_iface ]] || return 0
  local ifc; ifc=$(cat /tmp/bflab_nic_iface)
  echo  "== NIC fix: '$ifc' up ==" | tee -a "$LOG_FILE"
  ip link set "$ifc" up || true
  has nmcli && nmcli device connect "$ifc" 2>>"$LOG_FILE" || true
  rm -f /tmp/bflab_nic_iface
}

test_nic_all(){
  # Test all NICs that are currently UP
  local iflist
  iflist=$(ip -o link show up | awk -F': ' '$2 !~ /lo|tun|tap|docker|veth|virbr|nm-|wg/ {print $2}')
  [[ -z "$iflist" ]] && { lecho  "🌧 $WHITE_ON_RED  No candidate interfaces up."; return 1; }
  local rc=0
  for ifc in $iflist; do
    echo  "----"; IF="$ifc" test_nic || rc=1
  done
  return $rc
}



# ---------- time of day -----------------------------
# This tests that the time of day is correct to within 10 seconds.
# It does it by changing the current time to be wrong by 30 seconds.
# That's not enough of an error to demonstrate an expired certificate, which is
# how time errors typically manifest themselves.  But it is enough of an error
# to verify that the time server, either ntpd or chronyd, is working properly
test_time(){
  # Does anybody know what time it is?
  # Does anybody really care?
  # No, I can't imagine why.
  # Chicago - 
  # https://www.youtube.com/watch?v=jgF_ycCmF18&list=RDjgF_ycCmF18&start_radio=1
  TIME_SERVER=time.google.com       # Actually, any public web server will do
  # DATE_HDR is GMT in RFC 2822 Format
  DATE_HDR=$(curl -sI "https://${TIME_SERVER}" | grep -i '^Date:' || true)
  if [[ -z "${DATE_HDR:-}" ]]; then
    lecho  "🌧 $WHITE_ON_RED  Could not read HTTP Date header from ${TIME_SERVER}" | tee -a "$LOG_FILE"
    return 1
  fi
  # Everything up to and including the colon is removed.  RFC 2616 says the header must be Date, RFCs RFC 7230 §3.2 → RFC 9110
  # say that Date is case insensitive, and HTTP/2 and HTTP/3 say that all headers should be lower case.
  # In the bash man page, look for ${parameter#word} — Remove the shortest match of word from the beginning of parameter.
  # %s means return the number of seconds since the epoch (January 1st, 1970). 
  REMOTE_TS=$(date -d "${DATE_HDR#[Dd]ate: }" +%s)
  LOCAL_TS=$(date +%s)
  OFFSET=$((LOCAL_TS - REMOTE_TS))
  ABS_OFFSET=${OFFSET#-}
  if (( ABS_OFFSET > 10 )); then
    lecho  "⚠️ $BLACK_ON_YELLOW  $BLACK_ON_YELLOW   Clock drift ${OFFSET}s exceeds ±10s."
    return 1
  else
    lecho  "✅ Clock within tolerance (${OFFSET}s)."
    return 0
  fi
}


break_time(){
  require_root; echo  "== Time skew time by 40 seconds (disable NTP) =="
  has timedatectl && timedatectl set-ntp false || true
  date -s "-40 seconds" >>$LOG_FILE
  : > /tmp/bflab_time_skewed
  echo  "Now: $(date)"
}

fix_time(){
  require_root; echo  "== time fix: restore time / enable NTP =="
  if [[ -f /tmp/bflab_time_skewed ]]; then
    has timedatectl && timedatectl set-ntp true || true
    has hwclock && hwclock -s || true
    rm -f /tmp/bflab_time_skewed
    if has timedatectl; then
      until timedatectl status | fgrep "System clock synchronized: yes"; do
        echo2 "Waiting 2 seconds for the system clock to synchronize"
        sleep 2
      done
    else
      echo2 "Waiting 10 seconds.  Hopefully, the system clock is synchronized"
    fi
  fi
  echo  "Now: $(date)"
}



# ---------- packet-loss (tc netem) ----------
test_packet_loss(){
  local DEF_ROUTES_FILE="/tmp/bflab_default_routes"
  local IF; # IF=$(cat /tmp/bflab_tc_iface)
  if [[ -n ${LOSS_IF:-} ]]; then
    IF=$LOSS_IF
  elif [[ -f /tmp/bflab_tc_iface ]]; then
    IF=$(cat /tmp/bflab_tc_iface) 
  else
    IF=$(primary_iface || true )
  fi
  ip route list | fgrep default > $DEF_ROUTES_FILE
  if [[ -z $IF ]]; then
    lecho  "🌧 $WHITE_ON_RED  Interface :$IF: is not set: the file /tmp/bflab_tc_iface didn't have it, neither did envar LOSS_IF, and primary_iface returned nothing"
    exit 1
  elif [[ $( wc -l <"$DEF_ROUTES_FILE" ) -ne 1 ]]; then
     lecho  "⚠️  $BLACK_ON_YELLOW  There are $(wc -l <$DEF_ROUTES_FILE) default routes,  There should be only one.  "
     cat $DEF_ROUTES_FILE
  fi  
  echo  "== Packet-loss test on interface :$IF: (ping $PUBLIC_TARGET, expect 0% when idle) =="  | tee -a $LOG_FILE
  if ip route list | egrep -q -E "$IF"; then
    echo2 "Interface :$IF: is connected to a default route"
  else
    lecho "🌧 $WHITE_ON_RED  Interface :$IF: is **not** connected to a default route, so the ping test will be meaningless"
    ip route list
  fi
  if ping -c 10 -W 1 $PUBLIC_TARGET | awk '/packets transmitted/ {loss=$6+0; print; if (loss>0) exit 1}'; then
    lecho  "✅ $BLACK_ON_GREEN  No significant loss observed" | tee -a $LOG_FILE; return 0
  else
    lecho  "⚠️ $BLACK_ON_YELLOW   Packet loss detected (may be induced)" | tee -a $LOG_FILE; return 1
  fi
  rm -f $DEF_ROUTES_FILE
}
break_packet_loss(){
  require_root
  local IF;     # IF=$(primary_iface || true); [[ -z "${IF:-}" ]] && { echo  "No primary interface."; exit 1; }
  if [[ -n ${LOSS_IF:-} ]]; then
    IF=$LOSS_IF
    echo  $IF > /tmp/bflab_tc_iface
  elif [[ -f /tmp/bflab_tc_iface ]]; then
    IF=$(cat /tmp/bflab_tc_iface) 
  else
    IF=$(primary_iface || true )
  fi
  if ip route list | egrep -q -E "$IF"; then
    echo2 "Interface $IF is connected to a default route"
  else
    echo1 "🌧 $WHITE_ON_RED  Interface :$IF: is **not** connected to a default route, so the ping test will probably fail"
    ip route list
  fi
  local PCT="${LOSS_PCT:-74}"; echo  "$IF" > /tmp/bflab_tc_iface
  echo  "== Packet-loss break: tc netem loss ${PCT}% on ${IF} =="
  tc qdisc del dev "$IF" root 2>>$LOG_FILE || true
  tc qdisc add dev "$IF" root netem loss "${PCT}%"
  tc qdisc show dev "$IF"
}
fix_packet_loss(){
  require_root; [[ -f /tmp/bflab_tc_iface ]] || return 0
  local IF; IF=$(cat /tmp/bflab_tc_iface)
  echo  "== Packet-loss fix: Setting the packet loss rate on ${IF} to 0% (should not be needed) ==" | tee -a $LOG_FILE  
  tc qdisc change dev "$IF" root netem loss 0%
  tc qdisc show dev "$IF"  
  echo  "== Packet-loss fix: remove tc netem on ${IF} ==" | tee -a $LOG_FILE
  tc qdisc del dev "$IF" root >> $LOG_FILE 2>>$LOG_FILE  || true
  tc qdisc show dev "$IF"
  rm -f /tmp/bflab_tc_iface
  
}

# --------------- Bad certificate ---------------------
# This creates a web server on the localhost.  It does it with a good certificate
# or with a bad certificate.
ssl_ca_prepare() {
  echo2 "Preparing the CA"
  mkdir -p "$SSL_CA_DIR" "$SSL_DEMO_DIR"
  cat /dev/null > $SSL_CA_IDX       # Make the index file empty but do not delete it
  SSL_CACNF="$(mktemp)"
  cat << EOF > $SSL_CACNF
[ ca ]
default_ca      = CA_default            # The default ca section

[ CA_default ]
serial = /tmp/bflab_ssl_ca/ca.srl
new_certs_dir = /tmp/bflab_ssl_demo/
database = /tmp/bflab_ssl_ca/index.txt        # index file.
default_md     = default               # md to use
policy         = policy_any            # default policy
email_in_dn    = no                    # Don't add the email into cert DN

name_opt       = ca_default            # Subject name display option
cert_opt       = ca_default            # Certificate display option
copy_extensions = none                 # Don't copy extensions from request

[ policy_any ]
countryName            = optional
stateOrProvinceName    = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = optional
emailAddress           = optional

EOF
  echo2 "Created a configuration file the openssl CA section"
  if $VERBOSE_FLAG; then cat $SSL_CACNF; fi
  # Unless both the Certificate Authority (CA) key and the CA cert exist, create them.
  if [[ ! -s "$SSL_CA_KEY" || ! -s "$SSL_CA_CRT" ]]; then
    echo  "== Creating local demo CA =="
#   OpenSSL isn’t a tool. It’s a choose-your-own-adventure book written in flags.  😆 
    openssl genrsa -out "$SSL_CA_KEY" 2048 >>$LOG_FILE 2>&1
    openssl req -x509 -new -key "$SSL_CA_KEY" -out "$SSL_CA_CRT" -days 3650 \
      -subj "/CN=BFLab Demo CA" >>$LOG_FILE 2>&1
  else
    echo  "The CA was already prepared"
  fi
  echo2 "The CA key is $SSL_CA_KEY and the CA cert is $SSL_CA_CRT"
  # Seed the CA serial number file.  This is an even number of hex digits.
  [[ -s "$SSL_CA_DIR/ca.srl" ]] || echo  "01" > "$SSL_CA_DIR/ca.srl"
  
}

ssl_make_csr() {
  # If both the server private key and the server certificate signing request
  # (CSR) exist, then skip this part.  The assumption is that the key and
  # the CSR, if they both exist, match.
  if [[ ! -s "$SSL_SRV_KEY" || -s "$SSL_SRV_CSR" ]]; then
    # Create server key + CSR with CN=localhost and SAN=DNS:localhost
    # -s means true if the file exists and has size greater than 0
    # If the server key does not exist, then create it
    if [[ ! -s "$SSL_SRV_KEY" ]]; then
      echo  "Creating the server private key"
      openssl genrsa -out "$SSL_SRV_KEY" 2048 >>$LOG_FILE 2>&1
    fi

    # Try -addext; if unsupported, fall back to a temp extfile
    echo2 "Creating the server Certificate Signing Request (CSR)"
    if openssl req -new -key "$SSL_SRV_KEY" -out "$SSL_SRV_CSR" \
        -subj "/CN=localhost" \
        -addext "subjectAltName=DNS:localhost" >>$LOG_FILE 2>&1; then
      :     # : is the shell no-op command
    else
      local REQCNF; REQCNF="$(mktemp)"
      cat >"$REQCNF" <<'EOF'
[ req ]
distinguished_name = dn
prompt = no
req_extensions = v3_req
[ dn ]
CN = localhost
[ v3_req ]
subjectAltName = @alt_names
[ alt_names ]
DNS.1 = localhost
EOF

      openssl req -new -key "$SSL_SRV_KEY" -out "$SSL_SRV_CSR" -config "$REQCNF" >>$LOG_FILE 2>&1
      rm -f "$REQCNF"
    fi
  else
    echo2 "The files $SSL_SRV_KEY and $SSL_SRV_CSR already exist"
  fi
}

ssl_sign_cert() {
  # $1 = "expired", then writes to $SSL_SRV_BAD_CRT else writes to $SSL_SRV_GOOD_CRT
  local mode="${1:-valid}"
  echo2 "Signing a $mode certificate"
  local EXTFILE; EXTFILE="$(mktemp)"
  printf "subjectAltName=DNS:localhost\nbasicConstraints=CA:FALSE\nkeyUsage=Digital Signature\nextendedKeyUsage=serverAuth\n" > "$EXTFILE"
  echo  -n "The CA serial number is: "; cat "$SSL_CA_DIR/ca.srl"
  if [[ "$mode" == "expired" ]]; then
# In the April 1st, 1992, A graduate student 🎓 named I. M. Virtual published a 
# paper in the Proceedings of the Association of Computing Machinery, in which
# they proved that the openssl program was incomprehensible.  That proof has not
# been refuted in any refereed journal to this day (Oct 23 2025)
    echo2 "Creating an expired certificate with external file $EXTFILE:"
    rm -f "$SSL_SRV_BAD_CRT"              # openssl won't overwrite an existing certificate file
    if $VERBOSE_FLAG; then cat $EXTFILE; fi
    # Using a negative number of days, as suggested by
    # https://unix.stackexchange.com/questions/359225/create-self-signed-certificate-with-end-date-in-the-past
    # no longer works.  There is an explicit test which rejects negative values
    #openssl x509 -req -in "$SSL_SRV_CSR" \
    #  -CA "$SSL_CA_CRT" -CAkey "$SSL_CA_KEY" -CAcreateserial \
    #  -extfile "$EXTFILE" \
    #  -out "$SSL_SRV_CRT" -sha256 >>$LOG_FILE 2>&1
    # Minimal CA-driven signing with explicit dates (using your CSR)
    # Note that the -CA option in the x509 subcommand is the same as -cert in the ca subcommand
    # and -CAkey and -keyfile are likewise equivalent.  I find this confusing.
    openssl ca -batch \
        -cert "$SSL_CA_CRT" -keyfile "$SSL_CA_KEY" -config $SSL_CACNF \
        -in "$SSL_SRV_CSR" \
        -out "$SSL_SRV_BAD_CRT" \
        -startdate 20230101000000Z \
        -enddate   20230401000000Z \
          >$LOG_FILE 2>&1
    # I had a couple of failures when openssl had a problem and yet it created
    # an empty cert file.
    if [[ ! -s "$SSL_SRV_BAD_CRT" ]]; then lecho  "🌧 $WHITE_ON_RED  SOMETHING WENT WRONG CREATING $SSL_SRV_BAD_CRT"; exit 1; fi
    local DATES; DATES="$(mktemp)"
    if openssl x509 -in "$SSL_SRV_BAD_CRT" -noout -dates | tee $DATES | fgrep 2023; then
      echo  "The certificate has dates in 2023"
      rm $DATES
    else
      echo  "The certificate does not have dates in 2023 - something is wrong"
      cat $DATES
      rm $DATES
      exit 1
    fi 
  else
    echo2 "Creating a valid certificate with external file $EXTFILE:"
    rm -f "$SSL_SRV_GOOD_CRT"       # openssl won't overwrite an existing certificate file
    # By default, the start date/time is now and the end date/time is however 
    # many days (367) after now.
    openssl x509 -req -in "$SSL_SRV_CSR" \
      -CA "$SSL_CA_CRT" -CAkey "$SSL_CA_KEY" -CAserial "$SSL_CA_DIR/ca.srl" \
      -extfile "$EXTFILE" \
      -days 367 \
      -out "$SSL_SRV_GOOD_CRT" -sha256 >$LOG_FILE 2>&1
    echo  "After creating a valid cert, openssl returned $?"
    # I had a couple of failures when openssl had a problem and yet it created
    # an empty cert file.
    if [[ ! -s "$SSL_SRV_GOOD_CRT" ]]; then lecho  "🌧 $WHITE_ON_RED  SOMETHING WENT WRONG CREATING $SSL_SRV_GOOD_CRT"; exit 1; fi
    echo  -n "The CA serial number is: "; cat "$SSL_CA_DIR/ca.srl"
  fi
  echo  "NOT DELETING $EXTFILE \!\!\!"
  # rm -f "$EXTFILE"
}

ssl_server_start() {
# What screams "insecure" ?
# HTTP://
#  🍼 
  local SSL_SRV_CRT
  if [[ $1 == "valid" ]]; then
    SSL_SRV_CRT=$SSL_SRV_GOOD_CRT
  elif [[ $1 == "expired" ]]; then
    SSL_SRV_CRT=$SSL_SRV_BAD_CRT
  else
    echo1 "🌧 $WHITE_ON_RED  .ssl_server_start was called with a bad value, $1"
    exit 1
  fi
  echo2 "Starting an HTTPS server on port $SSL_SRV_PORT with certificate $SSL_SRV_CRT and key $SSL_SRV_KEY"
  (openssl s_server -quiet -accept "$SSL_SRV_PORT" \
     -cert "$SSL_SRV_CRT" -key "$SSL_SRV_KEY" -www >/tmp/openssl_s_server_start_log.txt 2>&1 &
  echo  $! > "$SSL_SRV_PID")
  cat /tmp/openssl_s_server_start_log.txt >> $LOG_FILE
  rm -f /tmp/openssl_s_server_start_log.txt
  sleep 1
  if [[ -s "$SSL_SRV_PID" ]] && ps -p "$(cat "$SSL_SRV_PID")" -o comm= | grep -q openssl; then
    echo2 "✅ $BLACK_ON_GREEN  🗲 OpenSSL demo server: https://localhost:${SSL_SRV_PORT} (PID $(cat "$SSL_SRV_PID"))"
#   In Bash, 'trap' is like 'finally', except when it isn't.   😁
# The HTTPS server has been started and will continue to run until it stops.
# Whenever this script exits or generates an error, stop the HTTPS server.
# The alternative is to stop the server, if it is running, when the script starts
    trap ssl_server_stop EXIT ERR
  else
    echo2 "❌ $BLACK_ON_RED  Failed to start OpenSSL demo server."
    # Why ?
    openssl s_server -quiet -accept "$SSL_SRV_PORT" \
     -cert "$SSL_SRV_CRT" -key "$SSL_SRV_KEY" -www
    echo2 "openssl s_server -quiet -accept $SSL_SRV_PORT \
     -cert $SSL_SRV_CRT -key $SSL_SRV_KEY -www"
    echo2 "🌧 $WHITE_ON_RED "
    exit 1  
  fi
}

ssl_server_stop() {
# A network engineer was shipwrecked on an island with very few supplies.
# Taking an inventory, he tallied a pocketknife, a granola bar, and a scrap of
# fiber. He ate part of the granola bar and started looking for some food.
# Finding nothing, he figured he didn't need the fiber anymore, so he dug a 
# small hole and buried it.
#
# Half an hour later, a backhoe showed up, dug up the fiber, and rescued the
# network engineer.  🤣

  if [[ -f "$SSL_SRV_PID" ]]; then
    # pid=$(<FILE) is equivalent to pid=$(cat FILE) but faster, because running
    # cat means the shell has to fork a process and the process has to start.
    # pid=$(<FILE) makes the shell read the file and put it in the envar. 
    local pid; pid=$(<"$SSL_SRV_PID")
    # Look at the PID and verify it is running openssl, if it is, then kill it
    if ps -p "$pid" -o comm= | grep -q openssl; then
      kill -2 "$pid" 2>>$LOG_FILE || kill "$pid" 2>>$LOG_FILE || true
      sleep 1
      # If the process is still alive after 2 failed attempts to kill it,
      # beat the crap out of that process and make it die!
      ps -p "$pid" >>$LOG_FILE 2>&1 && kill -9 "$pid" 2>>$LOG_FILE || true
    fi
    rm -f "$SSL_SRV_PID"
  fi
}

test_openssl_expired() {
  echo  "== SSL-EXPIRED test =="
  if curl -fsS "https://localhost:${SSL_SRV_PORT}" --cacert "$SSL_CA_CRT" --connect-timeout 3 >>$LOG_FILE 2>&1; then
    lecho  "✅ $BLACK_ON_GREEN  TLS OK (time-valid cert in place)"
    return 0
  else
    lecho  "❌ $BLACK_ON_RED  TLS verify failed (expected if expired cert is active)"
    return 1
  fi
}

break_openssl_expired() {
  require_root
  echo  "== BREAK ssl-expired: start server with EXPIRED cert =="
  ssl_server_stop
  ssl_server_start expired
}

fix_openssl_expired() {
  require_root
  echo  "== FIX ssl-expired: swap to VALID cert =="
  ssl_server_stop
  ssl_server_start valid
}

if [[ ! -s $SSL_SRV_BAD_CRT || ! -s $SSL_SRV_GOOD_CRT ]]; then
  echo2 "One or both certificates do not exist - this might take a moment"
  ssl_ca_prepare
  ssl_make_csr
  ssl_sign_cert valid 
  ssl_sign_cert expired
  ls -l $SSL_SRV_BAD_CRT $SSL_SRV_GOOD_CRT
else
  echo2 "Both certificates already exist"
fi
if $VERBOSE_FLAG; then ls -l $SSL_DEMO_DIR/server*.crt; fi


# ------------------ openssl-bad-dns -----------------
# In this failure mode, for some reason, the website you want to go to isn't
# the website you think you want to go to.  There are a couple of possible 
# reasons why this might happen: 1) DNS is returning a wrong address or there
# is a bad entry in /etc/hosts 2) something weird is happening with routing.
# SSL will detect and prevent both of these scenarios.
# The test plan is to add an entry to /etc/hosts


test_openssl_bad_dns(){
  local STATUS
  echo2 "Testing ${HOST_TO_TEST}:443 using curl and IPv4 address $HOST_TO_TEST_IPv4_ADDR"
  curl -fsS "https://${HOST_TO_TEST}:443"  >>$LOG_FILE 2>&1;
  STATUS=$?
  if [[ $STATUS -eq 60 ]]; then
    lecho  "❌ $BLACK_ON_RED  TLS verify failed (expected if using evil hostname $HOST_TO_TEST )"
    return $STATUS
  elif [[ $STATUS -eq 6 ]]; then
    lecho  "❌ $BLACK_ON_RED  DNS failed to find $HOST_TO_TEST (expected if using bad hostname)"
    return $STATUS
  elif [[ $STATUS -ne 0 ]]; then
    lecho  "❌ $BLACK_ON_RED  curl failed for some other reason, refer to $LOG_FILE"
    return $STATUS
  else
    lecho  "✅ $BLACK_ON_GREEN  TLS OK (${HOST_TO_TEST}:443 using curl and IPv4 address $HOST_TO_TEST_IPv4_ADDR)"
    return 0
  fi
}

break_openssl_bad_dns(){
  # This simulates an evil (because this is deliberately malicious as opposed to merely stupid)
  # nameserver.  However, this is the precisely the threat that SSL/TLS was designed to detect and stop
  require_root
  HOST_TO_TEST=$DNS_TEST_FAKE_HOST
  # Intentionally map the FAKE hostname to a KNOWN GOOD real IP so TLS hostname mismatch is triggered.
  HOST_TO_TEST_IPv4_ADDR=$(dig +short $HOST_TO_TEST)
  cp /etc/hosts /tmp/hosts_SAVED
  # Avoid duplicate poison lines:
  grep -q "bflab poison" /etc/hosts || echo  "${HOST_TO_TEST_IPv4_ADDR}     ${HOST_TO_TEST}   # bflab poison" >> /etc/hosts
  echo  "$HOST_TO_TEST_IPv4_ADDR   $HOST_TO_TEST   # bflab poison" >> /etc/hosts
  if $VERBOSE_FLAG; then
    echo1 "Verifying that /etc/hosts was patched with $HOST_TO_TEST_IPv4_ADDR"
  fi
  fgrep "$HOST_TO_TEST_IPv4_ADDR" /etc/hosts | tee -a $LOG_FILE  
}

fix_openssl_bad_dns(){
  require_root
  if egrep -E "${HOST_TO_TEST_IPv4_ADDR}.*${HOST_TO_TEST}.*bflab poison" /etc/hosts; then
    if fgrep "bflab poison" /tmp/hosts_SAVED; then
      lecho  "⚠️   $BLACK_ON_YELLOW  NOT FIXING /etc/hosts with /tmp/hosts_SAVED has bflab poison"
      # This isn't a catastrophic failure because breaking /etc/hosts means
      # that there is a bad entry in it.  It would be bad if somebody actually
      # used that bad entry. But it does mean something may have gone wrong somwehere. 
    else
      cp -v /tmp/hosts_SAVED /etc/hosts
    fi
  else
    lecho  "⚠️   $BLACK_ON_YELLOW  NOT FIXING /etc/hosts because there is no bflab poison in it."
  fi
  HOST_TO_TEST=$DNS_TEST_REAL_HOST
  HOST_TO_TEST_IPv4_ADDR=$(dig +short $HOST_TO_TEST)
}
# ---------- dispatcher ----------
usage(){
  cat <<EOF
Usage: sudo ./bf.sh <operation> <subsystem> [verbose]

Operations: test | break | fix | all
Subsystems: dns | time | routing-isp | routing-local | local-connectivity | wifi | nic | nics | packet-loss | openssl-expired | openssl-bad-dns 
Add the word "verbose" if you want a more verbose output.

Examples:
  sudo ./bf.sh all dns
  sudo ./bf.sh test tls
  sudo LOSS_PCT=15 ./bf.sh all packet-loss
  sudo LOSS_IF=wlp1s0  ./bf.sh test packet-loss
  sudo PUBLIC_TARGET=8.8.8.8 ./bf.sh all routing-isp
EOF
}
map_sub(){
  local s=$(echo  "${1:-}" | tr '[:upper:]' '[:lower:]')
  case "$s" in
    dns) echo  dns ;;
    time) echo  time ;;
    routing-isp) echo  routing_isp ;;
    routing-local) echo  routing_local ;;
    local-connectivity) echo  local_connectivity ;;
    wifi) echo  wifi ;;
    nic) echo  nic ;;
    nics) echo  nics ;;
    packet-loss) echo  packet_loss ;;
    openssl-expired) echo  openssl_expired ;;
    openssl-bad-dns) echo  openssl_bad_dns ;;
    *) lecho  "🌧 $WHITE_ON_RED  $s wasn't one of dns, time, routing_ISP, routing_local, local_connectivity, wifi, nic, nics, packet-loss, openssl-expired, or openssl-bad-dns"; return 1; ;;
  esac
}


OP="${1:-}"; SUB="${2:-}" 
[[ -z "$OP" || -z "$SUB" ]] && { usage; exit 2; }
SUBN=$(map_sub "$SUB"); [[ -z "$SUBN" ]] && { lecho  "🌧 $WHITE_ON_RED Unknown subsystem: $SUB"; usage; exit 2; }
if [[ $SUBN == "nic" ]]; then
  IF=$(primary_iface || true)
elif [[ $SUBN == "nics" ]]; then
  echo1 "This tests all UP NICs, but does not attempt to break or fix them"
  test_nic_all
fi

do_test="test_${SUBN}"; do_break="break_${SUBN}"; do_fix="fix_${SUBN}"
echo  "Log file is on $LOG_FILE" | tee -a $LOG_FILE
case "$(echo  "$OP" | tr '[:upper:]' '[:lower:]')" in
  test) "$do_test" ;;
  break) "$do_break" ;;
  fix) "$do_fix" ;;
  all)
    echo  "== Phase: TEST (pre) ==" | tee -a $LOG_FILE
    # Whatever was under test is broken before the demonstration has begun!  Do not make a bad situation worse.
    echo  "SUBN = $SUBN %%%%%%%%%% %%%%%%   %%%%%"
    if ! "$do_test"; then lecho  "🌧 $WHITE_ON_RED  Pre-test failed. Aborting." | tee -a $LOG_FILE; exit 3; fi
    echo  "== Phase: BREAK ==" | tee -a $LOG_FILE; "$do_break"
    echo  "== Phase: TEST (mid) ==" | tee -a $LOG_FILE
    # This means either the break step didn't break whatever was under test or else the test can't detect that
    # whatever was under test is broken
    # or both!
    if "$do_test"; then lecho  "🌧 $WHITE_ON_RED  Mid-test unexpectedly succeeded; aborting." | tee -a $LOG_FILE; exit 4; fi
    echo  "== Phase: FIX ==" | tee -a $LOG_FILE; "$do_fix"
    echo  "== Phase: TEST (post) ==" | tee -a $LOG_FILE
    # Whatever was done to fix the test did not work.  It was working before we started, it stopped working when
    # we deliberately broke it, and now it is still broken!
    if ! "$do_test"; then lecho  "🌧 $WHITE_ON_RED  Post-test failed; aborting." | tee -a $LOG_FILE; exit 5; fi
    lecho  "✅ ✅ $BLACK_ON_GREEN  Completed all phases for '$SUB'." | tee -a $LOG_FILE
    ;;
  *) usage; exit 2 ;;
esac

######################### known problems/places for improvements ##################
# router-border is confusing.  Change to router-local everywhere (simple) ✔
#
# packet-loss test fails probablistically, so give it several chances before writing it off.
#
# Add an openssl-remote test which uses openssl s_client to test the certificate on a remote server (moderate)
#
# Add an nmap test.  Check on the following TCP ports: ftp-ftp-data ssh telnet smtp domain http pop3 sunrpc snmp snmp-trap xdmcp ldap https microsoft-ds 6000-6007 (X11) redis 
#
#
# Add a flag, BROKEN_IN_PROGRESS, which is true if we're in the BREAK phase, either false or not defined otherwise.
#
# HARD: Change the test-break-test-fix-test paradigm to setup-test-break-test-fix-test-teardown (hard)
#
# Ping sometimes returns an invalid argument in the packet-loss test.  I don't know why

