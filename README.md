# nbmdt
network boot, monitor, and diagnostic (NBMT) tool.

This tool will do fault isolation and diagnostics on a linux network.  It runs in three different but similar modes:
* boot or diagnostic.  In this mode, nbmt goes through its network  configuration through the IP protocol stack, from bottom to top, with a Pass/Fail indication.
    + Verify hardware: cable is connected
    + ping the nearby routers and gateway nodes.  The routers come from the normal system routing tables.
    + Verify ARP table.
    + Verify that DNS is working by querying all of the nameservers listed in /etc/resolv.conf
    + Verify that the remote machines specified by the sysadmin in the persistent configuration file and the nominal configuration file are reachable using the protocol/port specified.
    + Verify that local services are listening on their given ports, as given by the sysadmin in the persistent configuration file and the nominal configuration file
* monitor.  In this mode, nbmt monitors the network using its predefined configuration and the configuration it has auto-discovered.  Each of the tests in boot mode are run, but in no particular sequence, and with frequecy specified by the system administrator in the persistent configuration file
* nominal.  In this mode, nbmt assumes that the network is correct and goes through the auto discovery process.  It makes a new nominal configuration file.  This file can be compared with an earlier nominal configuration file to see what changed.




The NBMT is very specific to linux and probably would require a lot of work to port.  However, one of the things on the roadmap is to be able to nagios plugins.

