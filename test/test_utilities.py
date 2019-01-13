#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Tests utilities.py


import pytest

import utilities
from pprint import PrettyPrinter
# class test_SystemConfigurationFile(object):

TEST_CONFIGURATION_FILE = "nominal_test_nbmt_configuration.json"
pp = PrettyPrinter(indent=4)

sd_obj = utilities.SystemDescriptionFile( TEST_CONFIGURATION_FILE )
assert isinstance( sd_obj, utilities.SystemDescription ), f"sd_obj is not an instance of SystemDescription, it's {type(sd_obj)}"
pp.pprint( sd_obj)
assert isinstance(sd_obj["version"], str), f'sd_obj["version"] should be a string, but it\'s really a {type(sd_obj["version"])}'
assert sd_obj.version == "0.01"
assert sd_obj.timestamp == "Sat Jan 12 18:39:16 PST 2019", f'sd_obj["timestamp"] should be ' \
    f'"Sat Jan 12 18:39:16 PST 2019" but is really {sd_obj["timestamp"]}'

# "version": 0.01,
#   "timestamp": "Sat Jan 12 18:39:16 PST 2019",
#   "remote": {
#     "commercialventvac.com": {
#       "protocol": "http"
#     },
#     "google.com": {
#       "protocol": "https"
#     }
#   },
#   "applications": {
#     "ssh": {
#       "protocol": "tcp",
#       "port": 22
#     },
#    "services": {
#      "comment1": "On my machine, dig 127.0.0.1 fails.  I don't have a DNS Masquerader.",
#      "dns": ["127.0.0.1", "8.8.8.8", "8.8.4.4", "::1", "2001:4860:4860::8888", "2001:4860:4860::8844", "gateway6", "gateway4" ],
#      "ntp": ["0.ubuntu.pool.ntp.org", "1.ubuntu.pool.ntp.org", "2.ubuntu.pool.ntp.org", "3.ubuntu.pool.ntp.org" ]
#    },
#     "presentations": {},
#     "local_services": {
#       "ssh": {
#         "protocol": "ssh",
#         "port": [22, 22022]
#       }
#     },
#     "transport": {},
#     "network": {
#       "IPv4" : {
#         "gateway": "192.168.0.1",
#         "neighbors": [
#           {"10.1.1.160": "8a:78:b5:08:99:ac"},
#           {"192.168.0.1": "04:bf:6d:d9:8a:b4"}
#           ]
#         },
#       "IPv6" : {
#         "gateway" : "fe80::6bf:6dff:fed9:8ab4" },
#         "neighbors": [
#           {"fe80::6bf:6dff:fed9:8ab4": "04:bf:6d:d9:8a:b4"}
#         ]
#       },
#     "datalink": [
#       {
#         "eno1": {
#           "MAC": "04:bf:6d:d9:8a:b4"
#         },
#         "enp3s0": {
#           "MAC": "00:10:18:cc:9c:77"
#         }
#       }
#     ]
#   },
#     "physical": {
#         "eno1": {
#           "comment1": "I don't know what the proper nomenclature is for this value",
#           "class": "link/ether",
#           "MAC": "04:bf:6d:d9:8a:b4"
#         },
#         "enp3s0": {
#           "class": "link/ether",
#           "MAC": "00:10:18:cc:9c:77"
#         },
#         "ttyUSB0": {
#           "comment1": "HIGHLY EXPERIMENTAL - as of January 12th, it doesn't work at all",
#           "class": "serial",
#           "usb": "Bus 001 Device 006: ID 067b:2303"
#         }
#     }
# }


