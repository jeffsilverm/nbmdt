# nbmdt
network boot, monitor, and diagnostic tool (NBMDT).

This tool will do fault isolation and diagnostics on a linux network.  It runs in several different but similar modes:
* boot.  In this mode, NBMDT reads its nominal network configuration file and nominal values of the IP protocol stack, from bottom to top, with a Pass/Fail indication.
    + Verify hardware: cable is connected
    + Verify that all of the network interface cards have proper IPv4 and IPv6 addresses either from DHCP, DHCP6, automatic configuration (IPv6 only), or static configuration.
    + ping the nearby routers and gateway nodes.  The routers come from the normal system routing tables.
    + Verify ARP table (IPv4) or neighbor table (IPv6).
    + Verify that DNS is working by querying all of the nameservers listed in /etc/resolv.conf
    + Verify that the remote machines specified by the sysadmin in the persistent configuration file and the nominal configuration file are reachable using the protocol/port specified.
    + Verify that local services are listening on their given ports, as given by the sysadmin in the persistent configuration file and the nominal configuration file
* monitor.  In this mode, NBMDT monitors the network using its predefined configuration and the configuration it has auto-discovered.  Each of the tests in boot mode are run, but in no particular sequence, and with frequecy specified by the system administrator in the persistent configuration file
* monitor.  In this mode, NBMDT watches over the network periodically, and alerts on any important change.
* discovery.  In this mode, NBMDT assumes that the network is correct and goes through the auto discovery process.  It makes a new nominal configuration file.  This file can be compared with an earlier nominal configuration file to see what changed.


The roadmap for MBMDT is:

1 Use a bash script to implement the NBMDT.  Output is to a flat ASCII file, and changes are detected using the diff command
2 Use a python program that invokes other programs to examine the state of the network.  Output is to a JSON file, and changes are detected using 
3 Use a python program that reads files in the /proc and /system pseudo file systems to examine the state of the network.
4 Use nagios plugins to do the same things if unavailable by other means.

See also [How to test and repair local area networks using linux tools] by Jeff Silverman




