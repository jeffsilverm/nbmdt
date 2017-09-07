#! /bin/bash

TEST_HOST="www.commercialventvac.com"
TEST_HOST_IP="208.97.189.29"
DEFAULT_ROUTER_IP="192.168.0.1"		# This assumes the default router is also a name server, true for home networks, false for businesses
ISPS_ROUTER="tukw-dsl-gw67.tukw.qwest.net"
ISPS_ROUTER_IP="63.231.10.67"


# For more information about putting colors in scripts, see for example
# http://misc.flogisoft.com/bash/tip_colors_and_formatting
source ./colors.sh
echo -e "\033[1m\033[37;40m$(date)\033[0m"
exitstatus=0
if ping -c 4 $DEFAULT_ROUTER_IP  > /dev/null 2>/dev/null; then
  echo -e  "${GREEN_BG}ping to LAN router is UP${NC}"
else
  echo -e  "${RED_BG}ping to LAN router is DOWN${NC}"
  exitstatus=1
  spd-say -w  "The local router is not pingable"
fi
if ping -c 4 $ISPS_ROUTER_IP > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}ping to ISP's router ${ISPS_ROUTER_IP} is UP${NC}"
else
  echo -e  "${RED_BG}ping to ISP's router ${ISPS_ROUTER_IP} is DOWN${NC}"
  exitstatus=1
  spd-say -w  "The ISP's router is not pingable"
fi
if ping -c 4 $TEST_HOST_IP > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}ping to ${TEST_HOST} without using DNS is UP${NC}"
else
  echo -e  "${RED_BG}ping to ${TEST_HOST} without using DNS is DOWN${NC}"
  exitstatus=1
  spd-say -w  "The test host $TEST_HOST_IP is not pingable"
fi
if ping -c 4 $TEST_HOST > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}ping to ${TEST_HOST} using DNS is UP${NC}"
else
  echo -e  "${RED_BG}ping to ${TEST_HOST} using DNS is DOWN${NC}"
  exitstatus=1
  spd-say -w  "The test host $TEST_HOST is not pingable"
fi
if ping -c 4 8.8.8.8 > /dev/null  2>/dev/null; then
  echo -e  "${GREEN_BG}ping to Google's name server  is UP${NC}"
else
  echo -e  "${RED_BG}ping to Google's name server  is DOWN${NC}"
  exitstatus=1
  spd-say -w  "Google's name server is not pingable"
fi
if dig @${DEFAULT_ROUTER_IP} desktop > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on router to desktop (tests internal configuration) is UP${NC}"
else
  echo -e  "${RED_BG}DNS on router to desktop is DOWN${NC}"
  exitstatus=1
  spd-say -w  "The name server on the local router fails to answer DNS queries for desktop"
fi
if dig @${DEFAULT_ROUTER_IP} $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on router to $TEST_HOST (tests external confguration) is UP${NC}"
else
  echo -e  "${RED_BG}DNS on router to $TEST_HOST is DOWN${NC}"
  exitstatus=1
  spd-say -w  "The name server on the local router fails to answer DNS queries for $TEST_HOST "
fi
if dig @8.8.8.8 $TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on Google's name server to ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}DNS on Google's name server to ${TEST_HOST} is DOWN${NC}"
  exitstatus=1
  spd-say -w  "Google's name server fails to answer queries for ${TEST_HOST} "
fi
if dig $TEST_HOST | fgrep $TEST_HOST_IP > /dev/null ; then
  echo -e  "${GREEN_BG}DNS on the default name server to ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}DNS on the default name server to ${TEST_HOST} is DOWN${NC}"
  exitstatus=1
  spd-say -w  "Default name server fails to answer queries for ${TEST_HOST} "
fi
if nc -z ${TEST_HOST} 22 > /dev/null ; then
  echo -e  "${GREEN_BG}SSH on ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}SSH on ${TEST_HOST} is ${RED_BG}DOWN${NC}"
  exitstatus=1
  spd-say -w  "SSH on ${TEST_HOST} fails"
fi
if curl -s http://$TEST_HOST > /dev/null ; then
  echo -e  "${GREEN_BG}HTTP on ${TEST_HOST} is UP${NC}"
else
  echo -e  "${RED_BG}HTTP on ${TEST_HOST} is ${RED_BG}DOWN${NC}"
  exitstatus=1
  spd-say -w  "HTTP on ${TEST_HOST} fails"
fi

if ping -c 4 jeffsilverman.ddns.net > /dev/null; then
  echo -e "${GREEN_BG}jeffsilverman.ddns.net DNS lookup is UP${NC}"
elif [ $? -eq 2 ] ; then
  echo -e "${RED_BG}jeffsilverman.ddns.net DNS lookup is not resolving${NC}"
  exitstatus=1
elif [ $? -eq 1 ]; then
  echo -e "${YELLOW_BG}jeffsilverman.ddns.net DNS lookup is resolving but the external address is not pingable${NC}"
  exitstatus=1
  if [[ "$(host jeffsilverman.ddns.net)" == *75.172.110.119 ]]; then
    echo -e "${YELLOW_BG}jeffsilverman.ddns.net DNS lookup is resolving to ${GREEN_BG}75.172.110.119${NC}, but it is  ${RED_BG}not pingable${NC}" 
  else
    echo -e "${YELLOW_BG}jeffsilverman.ddns.net DNS lookup is resolving to ${RED_BG}$(host jeffsilverman.ddns.net)${YELLOW_BG}, not ${GREEN_BG}75.172.110.119${NC}"
  fi 
fi

if ping -c 4 jeffsilverm.ddns.net > /dev/null; then
  echo -e "${GREEN_BG}jeffsilverm.ddns.net DNS lookup is UP${NC}"
elif [ $? -eq 2 ] ; then
  echo -e "${RED_BG}jeffsilverm.ddns.net DNS lookup is not resolving${NC}"
  exitstatus=1
elif [ $? -eq 1 ]; then
  host_ipv4=`host jeffsilverm.ddns.net|fgrep -v IPv6`
  echo -e "${YELLOW_BG}jeffsilverm.ddns.net DNS lookup is resolving but the external address ${host_ipv4} is not pingable${NC}"
  exitstatus=1
  if [[ "$()" == *75.172.110.119 ]]; then
    echo -e "${YELLOW_BG}jeffsilverm.ddns.net DNS lookup is resolving to ${GREEN_BG}75.172.110.119${NC}, but it is  ${RED_BG}not pingable${NC}" 
  else
    echo -e "${YELLOW_BG}${host_ipv4}, not ${GREEN_BG}75.172.110.119${NC}"
  fi 
fi

exit 


