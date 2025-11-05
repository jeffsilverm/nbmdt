# Browser/Network Failure Lab — Controller‑First Bundle

This bundle provides a single **controller** script (`bf.sh`) for running *test → break → test → fix → test* across common networking subsystems that affect web browsing.


## Files
- `bf.sh` — the controller (run with `sudo`)
- 'verify.sh' - a script that runs the controller in a "bottom up" sequence
- `README.md` — this file

## Usage
```bash
sudo ./bf.sh <operation> <subsystem>
```
**Operations:** `test | break | fix | all`  
**Subsystems:** `dns | time | routing-isp | routing-border | local-connectivity | wifi | nic | packet-loss | openssl-expired | openssl-bad-dns`

### Examples
```bash
sudo ./bf.sh all dns
sudo ./bf.sh all nic
sudo LOSS_PCT=15 ./bf.sh all packet-loss
sudo PUBLIC_TARGET=8.8.8.8 ./bf.sh all routing-isp
```

If you know that you don't know what you are doing (which is *never* a bad thought to have), then try this:
````bash
sudo ./verify_bf.sh
````

I wrote this script to help me test bf.sh automatically, and then I realized that it would actually be useful if something went wrong and you didn't know what it was.

CAUTION: the packet-loss test is not reliable on machines with more than one default route.  Yet.

## Safety & cleanup
- Script stores breadcrumbs in `/tmp/bflab_*` and `/etc/hosts` and removes only what it created.
- Manual cleanup if needed:
  - `sudo nft delete table inet bflab_dns`
  - `sudo iptables -D OUTPUT -j BFLAB ; sudo iptables -F BFLAB ; sudo iptables -X BFLAB`
  - `tc qdisc del dev <iface> root`  where <iface> is the interface that the primary_iface function identified.
  - `timedatectl set-ntp true` (if available), `hwclock -s`
  - `sudo sed -i.bak '/\# bflab poison/d' hosts
  
## Requirements
- Root privileges for break/fix and some tests
- `curl`, `iproute2` (`ip`, `tc`), optionally `dig`, `nmcli`
- Modern Linux (nftables preferred; iptables works as fallback)
