#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from time import sleep


INET="-4"
INET6="-6"


BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"


def main():
  default_gateway_4 = get_default_gateway(INET)
  ldr4 = len(default_gateway_4)
  report("Found default IPv4 gateway", green=(ldr4 == 1), red=(ldr4 == 0), yellow=(ldr4 > 1) )
  default_gateway_6 = get_default_gateway(INET6)
  ldr6 = len(default_gateway_6)
  report("Found default IPv6 gateway", green=(ldr6 == 1), red=(ldr6 == 0), yellow=(ldr6 > 1 ) )
  verify_ping_4 = ping(default_gateway_4, INET)
  report("IPv4 default gateway pingable", green=(verify_ping_4 == 1.0), yellow=(verify_ping_4 < 1.0 and verify_ping_4 > 0.0), red = (verify_ping_4 == 0.0) )
  verify_ping_6 = ping(default_gateway_6, INET6`)
  report("IPv6 default gateway pingable", green=(verify_ping_6 == 1.0), yellow=(verify_ping_6 < 1.0 and verify_ping_4 > 0.0), red = (verify_ping_4 == 0.0) )

def ping(host, protocol):

def report(explanation: str="Not specified", red: bool =False, yellow: 
        bool =False, green: bool =False):
  """
  explanation: str  A descriptive string
  red: bool True if status should be red
  yellow: bool  True if status should be yellow.  If not specified, the default
                is False so the answer must be RED or GREEN
  green: bool True if status should be green
  This is done this way to shift complexity to the subroutine
  """
  if int(red) + int(yellow) + int(green) > 1:
      raise ValueError("More than one of red, yellow, or green was set to True")  status = ("RED" if red else ("YELLOW" if yellow else ("GREEN" if green else \
              "UNKNOWN") ) )
  print(f"{explanation}: {status}")

def ping(


if "__main__" == __name__:
  while True do:
    main()
    time.sleep(10)

