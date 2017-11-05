# coding=utf-8
"""
Handles configuration items pertaining to routing
"""

import shlex, subprocess

class Routes():
    """This class stores all of the routes from (in linux) the ip route command """

    def __init__(self):

        # /usr/sbin/ip should be a configuration item, but at the moment, I am using the ip command to create the
        # .ini file, so this is here to avoid a subtle infinite loop
        cmd = '/usr/sbin/ip route list'
        # cmd = raw_input("shell:")
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE)
        stdout = result.stdout
        default_gateway_str = stdout[0]
        route_words = default_gateway_str.split()
        assert route_words[0] == "default", f"route_words[0] should be 'default', is actually {route_words[0]}"\
            "route_words is {route_words} the defaut_gateway_str is {default_gateway_str}"
        self.default_gateway = route_words[2]

if __name__ == "__main__" :

    route = Routes()
    print(f"Default gateway is {route.default_gateway}")
    cmd = "ping -c 4 " + route.default_gateway
    result = subprocess.run(cmd)
    print(result.stdout())


