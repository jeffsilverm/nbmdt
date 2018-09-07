#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This tests the physical layer, which is how the network interface cards (NICs)
# connect to the bus

import sys
# import subprocess
import constants
import utilities
import interface
from layer import Layer
import platform


class Physical(Layer):

    def __init__ (self, logical_name:str,
                  description:str = None,
                  product:str = None,
                  vendor:str = None,
                  bus_info:str = None,
                  version:str = None,
                  serial:str = None,
                  size:str = None,
                  capacity:str = None,
                  width:str = None,
                  clock:str = None,
                  capabiliities:str = None,
                  configuration:str = None,
                  resources:str = None
                  ):
        """
        Create a PhysicalAttributers object for this physical device.
        Inputs are from the lshw command in linux.  Other operating systems may vary
        :param logical_name:
        """

        """
        This is typical for a real ethernet:
        description: Ethernet interface
       product: 82579V Gigabit Network Connection
       vendor: Intel Corporation
       physical id: 19
       bus info: pci@0000:00:19.0
       logical name: eno1
       version: 04
       serial: 00:22:4d:7c:4d:d9
       size: 1Gbit/s
       capacity: 1Gbit/s
       width: 32 bits
       clock: 33MHz
       capabilities: pm msi bus_master cap_list ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
       configuration: autonegotiation=on broadcast=yes driver=e1000e driverversion=3.2.6-k duplex=full firmware=0.13-5 ip=192.168.0.3 latency=0 link=yes multicast=yes port=twisted pair speed=1Gbit/s
       resources: irq:29 memory:f7900000-f791ffff memory:f7939000-f7939fff ioport:f080(size=32)

        This is typical for a virtual ethernet, such as Docker:
        *-network
       description: Ethernet interface
       physical id: 1
       logical name: docker0
       serial: 02:42:51:b6:78:a2
       capabilities: ethernet physical
       configuration: broadcast=yes driver=bridge driverversion=2.3 firmware=N/A ip=172.17.0.1 link=no multicast=yes


        """
        self.logical_name: str = logical_name
        self.description: str = description
        self.product: str = product
        self.vendor: str = vendor
        self.bus_info: str = bus_info
        self.version: str = version
        self.serial: str = serial
        self.size: str = size
        self.capacity: str = capacity
        self.width: str = width
        self.clock: str = clock
        self.capabiliities: str = capabiliities
        self.configuration: str = configuration
        self.resources: str = resources


def physical_linux( ) -> constants.ErrorLevels :
    """
    Test the physical interfaces against known good interfaces
    :return:
    """
    print("In physical_linux", file=sys.stderr)
    # Execute the
    # Look in the nbmdt requirements document for the lshw - C network command and the
    # lspci -nnk | grep -iA2 net commands.That is a way to test the physical layer.Woot!
    command = ["lshw" "-C" "network" ]
    results = utilities.OsCliInter.run_command(command=command)
    for r in results.split("\n"):
        if "*-network" in r:
            continue
        key, value = r.split()
        key = re.sub(r"/\s+/_/")



        interface.PhysicalLink.physical_link_dict[if_name].physical_attributes.if_name = if_name
    return constants.ErrorLevels.UNKNOWN
    """
    If you want to diagnose just the network (in linux) try something like this:
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ sudo lshw -C network
[sudo] password for jeffs: 
  *-network                 
       description: Ethernet interface
       product: 82579V Gigabit Network Connection
       vendor: Intel Corporation
       physical id: 19
       bus info: pci@0000:00:19.0
       logical name: eno1
       version: 04
       serial: 00:22:4d:7c:4d:d9
       size: 1Gbit/s
       capacity: 1Gbit/s
       width: 32 bits
       clock: 33MHz
       capabilities: pm msi bus_master cap_list ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
       configuration: autonegotiation=on broadcast=yes driver=e1000e driverversion=3.2.6-k duplex=full firmware=0.13-5 ip=192.168.0.3 latency=0 link=yes multicast=yes port=twisted pair speed=1Gbit/s
       resources: irq:28 memory:f7900000-f791ffff memory:f7939000-f7939fff ioport:f080(size=32)
  *-network
       description: Ethernet interface
       product: NetXtreme BCM5722 Gigabit Ethernet PCI Express
       vendor: Broadcom Limited
       physical id: 0
       bus info: pci@0000:03:00.0
       logical name: enp3s0
       version: 00
       serial: 00:10:18:cc:9c:77
       size: 1Gbit/s
       capacity: 1Gbit/s
       width: 64 bits
       clock: 33MHz
       capabilities: pm vpd msi pciexpress bus_master cap_list ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt 1000bt-fd autonegotiation
       configuration: autonegotiation=on broadcast=yes driver=tg3 driverversion=3.137 duplex=full firmware=5722-v3.09 ip=192.168.0.12 latency=0 link=yes multicast=yes port=twisted pair speed=1Gbit/s
       resources: irq:33 memory:f7800000-f780ffff
  *-network
       description: Ethernet interface
       physical id: 1
       logical name: docker0
       serial: 02:42:5f:e9:a7:23
       capabilities: ethernet physical
       configuration: broadcast=yes driver=bridge driverversion=2.3 firmware=N/A ip=172.17.0.1 link=no multicast=yes
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ 

    
    In case you want to test the entire system, try something like:
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ sudo lshw -short
H/W path           Device      Class          Description
=========================================================
                               system         (To be filled by O.E.M.)
/0                             bus            DH77EB
/0/0                           memory         64KiB BIOS
/0/4                           memory         256KiB L1 cache
/0/5                           memory         1MiB L2 cache
/0/6                           memory         8MiB L3 cache
/0/7                           memory         16GiB System Memory
/0/7/0                         memory         4GiB DIMM DDR3 Synchronous 1600 MHz (0.6 ns)
/0/7/1                         memory         4GiB DIMM DDR3 Synchronous 1600 MHz (0.6 ns)
/0/7/2                         memory         4GiB DIMM DDR3 Synchronous 1600 MHz (0.6 ns)
/0/7/3                         memory         4GiB DIMM DDR3 Synchronous 1600 MHz (0.6 ns)
/0/2b                          processor      Intel(R) Core(TM) i7-3770 CPU @ 3.40GHz
/0/100                         bridge         Xeon E3-1200 v2/3rd Gen Core processor DRAM Controller
/0/100/1                       bridge         Xeon E3-1200 v2/3rd Gen Core processor PCI Express Root Port
/0/100/1/0                     display        GF108 [GeForce GT 430]
/0/100/1/0.1                   multimedia     GF108 High Definition Audio Controller
/0/100/2                       display        Xeon E3-1200 v2/3rd Gen Core processor Graphics Controller
/0/100/14                      bus            7 Series/C210 Series Chipset Family USB xHCI Host Controller
/0/100/14/0        usb3        bus            xHCI Host Controller
/0/100/14/0/3                  bus            USB hub
/0/100/14/0/3/2                multimedia     Logitech USB Headset
/0/100/14/0/4                  bus            2 Port Hub
/0/100/14/1        usb4        bus            xHCI Host Controller
/0/100/16                      communication  7 Series/C216 Chipset Family MEI Controller #1
/0/100/19          eno1        network        82579V Gigabit Network Connection
/0/100/1a                      bus            7 Series/C216 Chipset Family USB Enhanced Host Controller #2
/0/100/1a/1        usb1        bus            EHCI Host Controller
/0/100/1a/1/1                  bus            Integrated Rate Matching Hub
/0/100/1a/1/1/3                input          2.4G Receiver
/0/100/1a/1/1/4                bus            USB 2.0 Hub
/0/100/1a/1/1/4/1              multimedia     QuickCam Pro for Notebooks
/0/100/1b                      multimedia     7 Series/C216 Chipset Family High Definition Audio Controller
/0/100/1c                      bridge         7 Series/C216 Chipset Family PCI Express Root Port 1
/0/100/1c.2                    bridge         7 Series/C210 Series Chipset Family PCI Express Root Port 3
/0/100/1c.2/0      enp3s0      network        NetXtreme BCM5722 Gigabit Ethernet PCI Express
/0/100/1d                      bus            7 Series/C216 Chipset Family USB Enhanced Host Controller #1
/0/100/1d/1        usb2        bus            EHCI Host Controller
/0/100/1d/1/1                  bus            Integrated Rate Matching Hub
/0/100/1f                      bridge         H77 Express Chipset LPC Controller
/0/100/1f.2                    storage        7 Series/C210 Series Chipset Family 6-port SATA Controller [AHCI mode]
/0/100/1f.3                    bus            7 Series/C216 Chipset Family SMBus Controller
/0/1               scsi0       storage        
/0/1/0.0.0         /dev/sda    disk           120GB INTEL SSDSC2CT12
/0/1/0.0.0/1       /dev/sda1   volume         37GiB EXT4 volume
/0/1/0.0.0/3       /dev/sda3   volume         35GiB EXT4 volume
/0/1/0.0.0/4       /dev/sda4   volume         39GiB EXT4 volume
/0/2               scsi1       storage        
/0/2/0.0.0         /dev/sdb    disk           2TB ST2000DM001-9YN1
/0/2/0.0.0/1       /dev/sdb1   volume         1863GiB EXT4 volume
/0/3               scsi2       storage        
/0/3/0.0.0         /dev/cdrom  disk           CDDVDW SH-222BB
/1                 docker0     network        Ethernet interface
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ 

    """


def physical_windows() -> constants.ErrorLevels :
    print("In physical_windows", file=sys.stderr)
    if "Windows" == platform.system():
        raise NotImplementedError("Windows not implemented yet")
    return constants.ErrorLevels.OTHER


def physical_mac() -> constants.ErrorLevels :
    print("In physical_mac", file=sys.stderr)
    if "Mac" == platform.system():
        raise NotImplementedError("Mac OS X not implemented yet")
    return constants.ErrorLevels.OTHER


def physical_java() -> constants.ErrorLevels :
    print("In physical_java", file=sys.stderr)
    if "Java" == platform.system():
        raise NotImplementedError("java not implemented yet")
    return constants.ErrorLevels.OTHER


def physical() -> constants.ErrorLevels:
    """
    Test the NICs.  This is operating system independent
    :return:
    """

    if "linux" == utilities.OsCliInter.system:
        return physical_linux()
    elif "windows" == utilities.OsCliInter.system:
        return physical_windows()
    elif 'darwin' == utilities.OsCliInter.system:
        return physical_mac()
    elif 'java' == utilities.OsCliInter.system:
        return physical_java()
    else:
        raise ValueError("")



