#! /bin/bash
#
# bash script to check the bf.sh script

# Colors for VT-100 (ANSI X3.64) escape sequences.  This will also work on a linux console
WHITE_ON_RED='\033[37;41m'
BLACK_ON_RED='\033[30;41m'
WHITE_ON_BLUE='\033[30;44m'
BLACK_ON_YELLOW='\033[30;43m'
WHITE_ON_GREEN='\033[37;42m'
BLACK_ON_GREEN='\033[30;42m'
BLACK_ON_CYAN='\033[30;46m'

RESET='\033[0m'

echo -e "$BLACK_ON_CYAN Running all of the test in bf.sh${RESET}"

require_root() { [[ $EUID -eq 0 ]] || { echo "🌧 Please run as root (sudo)."; exit 1; }; }
require_root


for SCENARIO in nic wifi local-connectivity routing-local routing-isp dns time openssl-expired openssl-bad-dns packet-loss ; do
  echo -e "${BLACK_ON_CYAN}      $SCENARIO $RESET"
  if ./bf.sh all $SCENARIO ; then
    echo -e "${WHITE_ON_GREEN} ----------$SCENARIO passed $RESET"
  else
    echo -e"${WHITE_ON_RED} ----------$SCENARIO **~~~~~~~~~~ FAILED ***********${RESET}";
  fi
done

echo "Special cases"
PUBLIC_TARGET=f5.com ./bf.sh all routing-isp

exit 0
