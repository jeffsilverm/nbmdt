#! /bin/bash

# ---------- helpers ---------- (from bf.sh, do not include when merging into bf.sh)
LOG_FILE="/tmp/$0_${DATE}.log"

require_root() { [[ $EUID -eq 0 ]] || { echo "🌧 Please run as root (sudo)."; exit 1; }; }
has(){ command -v "$1" >>$LOG_FILE 2>&1; }
has_nft(){ has nft; } ; has_ipt(){ has iptables; } ; has_ip6t(){ has ip6tables; }


primary_iface() {
  local dev; dev=$(ip route show default 2>>$LOG_FILE | awk '/default/ {print $5; exit}')
  [[ -n "${dev:-}" ]] && { echo "$dev"; return; }
  ip -o link show up | awk -F': ' '$2 !~ /lo/ {print $2; exit}'
}
default_gw(){ ip route show default 2>>$LOG_FILE | awk '/default via/ {print $3; exit}'; }

# echo1 I actually thought of second, but I didn't want to call it echo3.
# Write the arguments both the stdout and the log file unconditionally.
echo1() { echo $@ | tee -a $LOG_FILE ; }

VERBOSE_FLAG=$([[ "${3-}" == "verbose" ]] && echo true || echo false)    # If $3 is unset, then expand to empty string

# echo2 is a good idea, I just thought of it too late.  But if I ever refactor this bash script....
echo2() {
# If the verbose flag is set, then log the arguments to both stdout and the log file, otherwise
# just the log file
  if $VERBOSE_FLAG; then
    echo1 $@
  else
    echo $@ >> $LOG_FILE
  fi
}
# ------------------------- end of helpers 

# ---------- nic (counter-based; DNS-independent) ----------
test_nic(){
  echo "== NIC counter test (kernel stats; no DNS required) ==" | tee -a "$LOG_FILE"

  local IF; IF=$(primary_iface || true)
  if [[ -z "${IF:-}" ]]; then
    echo "❌ No active interface detected." | tee -a "$LOG_FILE"
    return 1
  fi
  echo "Interface under test: $IF" | tee -a "$LOG_FILE"

  # Helpers to read integer counters from sysfs safely
  _stat() { cat "/sys/class/net/$1/statistics/$2" 2>/dev/null || echo 0; }
  _uptime_secs() { awk '{print int($1)}' /proc/uptime 2>/dev/null || echo 0; }

  # Snapshot #1
  local rx1 tx1 rxerr1 txerr1 rxd1 txd1 coll1 carr1
  rx1=$(_stat "$IF" rx_packets)
  tx1=$(_stat "$IF" tx_packets)
  rxerr1=$(_stat "$IF" rx_errors)
  txerr1=$(_stat "$IF" tx_errors)
  rxd1=$(_stat "$IF" rx_dropped)
  txd1=$(_stat "$IF" tx_dropped)
  coll1=$(_stat "$IF" collisions)
  carr1=$(_stat "$IF" tx_carrier_errors)
  local up1; up1=$(_uptime_secs)

  # Create a tiny burst of local traffic so counters should move
  # — gateway ping (no DNS), but don't fail the test if it doesn't reply.
  local gw; gw=$(default_gw || true)
  if [[ -n "${gw:-}" ]]; then
    ping -c 3 -W 1 "$gw" >/dev/null 2>&1 || true
  fi

  # Wait a few seconds to let counters advance
  local SLEEP_SEC=5
  sleep "$SLEEP_SEC"

  # Snapshot #2
  local rx2 tx2 rxerr2 txerr2 rxd2 txd2 coll2 carr2
  rx2=$(_stat "$IF" rx_packets)
  tx2=$(_stat "$IF" tx_packets)
  rxerr2=$(_stat "$IF" rx_errors)
  txerr2=$(_stat "$IF" tx_errors)
  rxd2=$(_stat "$IF" rx_dropped)
  txd2=$(_stat "$IF" tx_dropped)
  coll2=$(_stat "$IF" collisions)
  carr2=$(_stat "$IF" tx_carrier_errors)
  local up2; up2=$(_uptime_secs)

  # Deltas over the short window
  local drx=$((rx2 - rx1))
  local dtx=$((tx2 - tx1))
  local drxerr=$((rxerr2 - rxerr1))
  local dtxerr=$((txerr2 - txerr1))
  local drxd=$((rxd2 - rxd1))
  local dtxd=$((txd2 - txd1))
  local dcoll=$((coll2 - coll1))
  local dcarr=$((carr2 - carr1))

  # Totals (since boot) for rate analysis
  local rx_total="$rx2" tx_total="$tx2"
  local rxerr_total="$rxerr2" txerr_total="$txerr2"
  local rxd_total="$rxd2" txd_total="$txd2"
  local coll_total="$coll2" carr_total="$carr2"

  # Uptime in hours (avoid div-by-zero)
  local uph=1
  if (( up2 > 0 )); then
    uph=$(( (up2 + 3599) / 3600 ))  # ceil to nearest hour
  fi

  # Thresholds: errors must not increase; other “bad” counters should be ~< 1/hour of uptime
  local per_hour_thresh=$uph

  # Report
  {
    echo "Window: ${SLEEP_SEC}s"
    printf "RX pkts: %d -> %d  (Δ=%d)\n" "$rx1" "$rx2" "$drx"
    printf "TX pkts: %d -> %d  (Δ=%d)\n" "$tx1" "$tx2" "$dtx"
    printf "RX errors Δ=%d (total=%d), TX errors Δ=%d (total=%d)\n" "$drxerr" "$rxerr_total" "$dtxerr" "$txerr_total"
    printf "RX dropped Δ=%d (total=%d), TX dropped Δ=%d (total=%d)\n" "$drxd" "$rxd_total" "$dtxd" "$txd_total"
    printf "Collisions Δ=%d (total=%d), TX carrier errs Δ=%d (total=%d)\n" "$dcoll" "$coll_total" "$dcarr" "$carr_total"
    echo "Uptime (hours, ceil): $uph  → “small” total threshold ≈ <$per_hour_thresh"
  } | tee -a "$LOG_FILE"

  local status=0

  # Pass/fail on packet movement
  if (( drx + dtx <= 0 )); then
    echo "❌ No packet movement detected over ${SLEEP_SEC}s — link may be down or idle." | tee -a "$LOG_FILE"
    status=1
  else
    echo "✅ Packet movement observed (ΔRX=$drx, ΔTX=$dtx)." | tee -a "$LOG_FILE"
  fi

  # Warnings per your criteria
  if (( drxerr > 0 || dtxerr > 0 )); then
    echo "⚠️  Errors increased in the last ${SLEEP_SEC}s (Δrx_err=$drxerr, Δtx_err=$dtxerr)." | tee -a "$LOG_FILE"
  fi

  # “Very small”: totals less than ~1 per hour of uptime
  if (( rxd_total > per_hour_thresh || txd_total > per_hour_thresh )); then
    echo "⚠️  Drops seem high for $uph h uptime (rx_dropped=$rxd_total, tx_dropped=$txd_total)." | tee -a "$LOG_FILE"
  fi
  if (( coll_total > per_hour_thresh )); then
    echo "⚠️  Collisions seem high for $uph h uptime (collisions=$coll_total)." | tee -a "$LOG_FILE"
  fi
  if (( carr_total > per_hour_thresh )); then
    echo "⚠️  TX carrier errors seem high for $uph h uptime (tx_carrier_errors=$carr_total)." | tee -a "$LOG_FILE"
  fi

  return "$status"
}

test_nic
break_nic
test_nic
fix_nic
test_nic
if curl -fsS -I https://google.com; then echo "Google can be reached using HTTPS"; else "Googgle cannot be reached using curl and HTTPS\!\!\!"; fi

