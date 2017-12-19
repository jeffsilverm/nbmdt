# coding=utf-8
"""
Handles configuration items pertaining to routing
"""

import shlex, subprocess
from collections import OrderedDict

class Routes_4():
    """This class stores all of the routes from (in linux) the ip route command """

    def __init__(self):

        # /usr/sbin/ip should be a configuration item, but at the moment, I am using the ip command to create the
        # .ini file, so this is here to avoid a subtle infinite loop
        cmd = '/usr/sbin/ip -4 route list'
        # cmd = raw_input("shell:")
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE)
        stdout = result.stdout
        stdout_list=stdout.split(b"\n")
        # I don't assume that the default route will be first, and in fact, there might not be a default route at all.
        # Furthermore, if name resolution isn't working, then the default route might be 0.0.0.0
        self.routing_table=OrderedDict()
        # The ip command also returns a spurious blank line at the end of its output.  Skip it.
        for route_line in stdout_list[:-1]:
            route_words = route_line.split()
            destination = route_words[0]
            if destination == b"default" or destination == b"0.0.0.0" :
                raise NotImplemented("Why are you using the routing module?  Use routes instead")
                self.default_gateway = destination
            self.routing_table[destination] = route_words[1:]

if __name__ == "__main__" :

    route = Routes_4()
    print(f"Default gateway is {route.default_gateway}")
    cmd = b"ping -c 4 " + bytes(route.default_gateway, encoding="ascii")
    result = subprocess.run(cmd)
    print(result.stdout())
    for destination in route.routing_table.keys():
        print(route.routing_table[destination])


