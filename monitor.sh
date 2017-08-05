#! /bin/bash

TEST_HOST="f5.com"
TEST_HOST_IP="104.219.111.168"
DEFAULT_ROUTER="192.168.0.1"		# This assumes the default router is also a name server, true for home networks, false for businesses

# This script creates colors for any bash script that invokes it
BLACK='\033[0;30m'
DARKGRAY='\033[1;30m'
RED='\033[0;31m'
LIGHTRED='\033[1;31m'
GREEN='\033[0;32m'
LIGHTGREEN='\033[1;32m'
BROWN='\033[0;33m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
LIGHTBLUE='\033[1;34m'
PURPLE='\033[0;35m'
LIGHTPURPLE='\033[1;35m'
CYAN='\033[0;36m'
LIGHTCYAN='\033[1;36m'
LIGHTGRAY='\033[0;37m'     
WHITE='\033[1;37m'
NC='\033[0m'
# This script creates colors for any bash script that invokes it
BLACK_BG='\033[0;49m'
DARKGRAY_BG='\033[1;40m'
RED_BG='\033[0;41m'
LIGHTRED_BG='\033[1;41m'
GREEN_BG='\033[0;42m'
LIGHTGREEN_BG='\033[1;42m'
BROWN_BG='\033[0;43m' 
YELLOW_BG='\033[1;43m'
BLUE_BG='\033[0;44m'
LIGHTBLUE_BG='\033[1;44m'
PURPLE_BG='\033[0;45m'
LIGHTPURPLE_BG='\033[1;45m'
CYAN_BG='\033[0;46m'
LIGHTCYAN_BG='\033[1;46m'
LIGHTGRAY_BG='\033[0;47m'     
WHITE_BG='\033[1;47m'
echo -e -n "${PURPLE}"
date
echo -e -n "${NC}"
exitstatus=0
if ping -c 4 $DEFAULT_ROUTER  > /dev/null; then
  echo -e  "${GREEN_BG}Path to router is UP${NC}"
else
  echo -e  "${RED_BG}Path to router is DOWN${NC}"
  exitstatus=1
fi
if ping -c 4 $TEST_HOST_IP > /dev/null ; then
  echo -e  "${GREEN_BG}Path to F5.com without using DNS is UP${NC}"
else
  echo -e  "${RED_BG}Path to F5.com without using DNS is DOWN${NC}"
  exitstatus=1
fi
if ping -c 4 $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}Path to F5.com using DNS is UP${NC}"
else
  echo -e  "${RED_BG}Path to F5.com using DNS is DOWN${NC}"
  exitstatus=1
fi
if dig @$DEFAULT_ROUTER desktop > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on router to desktop (tests internal configuration) is UP${NC}"
else
  echo -e  "${RED_BG} on router is DOWN${NC}"
  exitstatus=1
fi
if dig @$DEFAULT_ROUTER $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on router to $TEST_HOST (tests external confguration) is UP${NC}"
else
  echo -e  "${RED_BG}DNS on router to $TEST_HOST nis DOWN${NC}"
  exitstatus=1
fi
if dig @8.8.8.8 $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on Google's name server to F5.com is UP${NC}"
else
  echo -e  "${RED_BG}DNS on Google's name server to F5.com is DOWN${NC}"
  exitstatus=1
fi
if dig $TEST_HOST | fgrep $TEST_HOST_IP > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on the default name server to F5.com is UP${NC}"
else
  echo -e  "${RED_BG}DNS on the default name server to F5.com is DOWN${NC}"
  exitstatus=1
fi
if curl -s http://$TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}HTTP on F5.com is UP${NC}"
else
  echo -e  "${RED_BG}HTTP on F5.com is ${RED_BG}DOWN${NC}"
  exitstatus=1
fi
exit $exitstatus


