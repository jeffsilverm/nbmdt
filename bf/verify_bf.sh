#! /bin/bash
#
# bash script to check the bf.sh script
require_root() { [[ $EUID -eq 0 ]] || { echo "🌧 Please run as root (sudo)."; exit 1; }; }
require_root

for SCENARIO in nic wifi local-connectivity routing-border routing-isp dns time openssl-expired openssl-bad-dns packet-loss ; do
  echo $SCENARIO
  if ./bf.sh all $SCENARIO ; then
    echo "----------$SCENARIO passed"
  else
    echo "----------$SCENARIO **~~~~~~~~~~ FAILED ***********";
  fi
done
exit 0
