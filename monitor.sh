#! /bin/bash

TEST_HOST="www.commercialventvac.com"
TEST_HOST_IP="208.97.189.29"
DEFAULT_ROUTER="192.168.0.1"		# This assumes the default router is also a name server, true for home networks, false for businesses
ISPS_ROUTER="tukw-dsl-gw67.tukw.qwest.net"


# For more information about putting colors in scripts, see for example
# http://misc.flogisoft.com/bash/tip_colors_and_formatting
source ./colors.sh
echo -e -n "${WHITE}"
date
echo -e -n "${NC}"
exitstatus=0
if ping -c 4 $DEFAULT_ROUTER  > /dev/null 2>/dev/null; then
  echo -e  "${GREEN_BG}Path to router is UP${NC}"
else
  echo -e  "${RED_BG}Path to router is DOWN${NC}"
  exitstatus=1
fi
if ping -c 4 $ISPS_ROUTER > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}Path to ISP's router ${ISPS_ROUTER} is UP${NC}"
else
  echo -e  "${RED_BG}Path to ISP's router ${ISPS_ROUTER} is DOWN${NC}"
  exitstatus=1
fi
if ping -c 4 $TEST_HOST_IP > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}Path to ${TEST_HOST} without using DNS is UP${NC}"
else
  echo -e  "${RED_BG}Path to ${TEST_HOST} without using DNS is DOWN${NC}"
  exitstatus=1
fi
if ping -c 4 $TEST_HOST > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}Path to ${TEST_HOST} using DNS is UP${NC}"
else
  echo -e  "${RED_BG}Path to ${TEST_HOST} using DNS is DOWN${NC}"
  exitstatus=1
fi
if ping -c 4 8.8.8.8 > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}Path to Google's name server  is UP${NC}"
else
  echo -e  "${RED_BG}Path to Google's name server  is DOWN${NC}"
  exitstatus=1
fi
if dig @$DEFAULT_ROUTER desktop > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on router to desktop (tests internal configuration) is UP${NC}"
else
  echo -e  "${RED_BG}DNS on router is DOWN${NC}"
  exitstatus=1
fi
if dig @$DEFAULT_ROUTER $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on router to $TEST_HOST (tests external confguration) is UP${NC}"
else
  echo -e  "${RED_BG}DNS on router to $TEST_HOST is DOWN${NC}"
  exitstatus=1
fi
if dig @8.8.8.8 $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on Google's name server to ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}DNS on Google's name server to ${TEST_HOST} is DOWN${NC}"
  exitstatus=1
fi
if dig $TEST_HOST | fgrep $TEST_HOST_IP > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on the default name server to ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}DNS on the default name server to ${TEST_HOST} is DOWN${NC}"
  exitstatus=1
fi
if nc -z ${TEST_HOST} 22 > /dev/null ; then
  echo -e  "${GREEN_BG}SSH on ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}SSH on ${TEST_HOST} is ${RED_BG}DOWN${NC}"
  exitstatus=1
fi
if curl -s http://$TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}HTTP on ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}HTTP on ${TEST_HOST} is ${RED_BG}DOWN${NC}"
  exitstatus=1
fi
exit $exitstatus


