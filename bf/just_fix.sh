#! /bin/bash
#
# bash script to check the bf.sh script
require_root() { [[ $EUID -eq 0 ]] || { echo "🌧 Please run as root (sudo)."; exit 1; }; }
require_root

for SCENARIO in nic wifi local-connectivity routing-local routing-isp dns time openssl-expired openssl-bad-dns packet-loss ; do
  echo $SCENARIO
  if ./bf.sh fix $SCENARIO ; then
    echo "✅ ----------$SCENARIO fixed"
  else
    echo "❌ ----------$SCENARIO **~~~~~~~~~~ was NOT fixed ***********";
  fi
  if ./bf.sh test $SCENARIO ; then
    echo "✅ ----------$SCENARIO tested: fixed"
  else
    echo "❌ ----------$SCENARIO tested: ~~~~~~~~~~ was NOT fixed ***********";
  fi

done
exit 0
