#! /usr/bin/python3
#
# This is a vastly simplified version of the network monitor boot and diagnostic
# program, NBMDT
#
import sys
from colorama import Back, Style, Fore
import subprocess
import json
from typing import List
import re
import time

OK = (Back.GREEN + "OK" + Style.RESET_ALL)
FAIL = (Back.RED + "FAIL" + Style.RESET_ALL)
SLEEPING = ( Fore.YELLOW + "Sleeping" + Style.RESET_ALL)
pattern = re.compile( r"\$[A-Za-z0-9_]*")

def dereference ( cmd: str ) -> str:
    """ If there is a symbol in cmd (Introduced by a $ and ended by anything not in
    [A-Za-z0-9_], then do the substitution

    """
    mo = re.search(pattern=pattern, string=cmd, )
    if mo is None:          # There is no substitution needed
        return cmd
    key: str = mo.group(0)
    repl: str = symbol_table[key[1:]]
    expanded = pattern.sub(repl=repl, string=cmd )
    return expanded


if "__main__" == __name__:
    with open("network_description.json", "r") as fp:
        net_dscr = json.load(fp=fp)
    symbol_table = net_dscr["variables"]
    go = True
    while go:
        # Clear the screen
        print("\033[2J\033[H")
        print(time.ctime())
        for level in net_dscr["levels"]:
            sensor_keys: List[str] = net_dscr["levels"][level].keys()
            for sensor in sensor_keys:
                command: str = net_dscr["levels"][level][sensor]
                command: str = dereference ( command )
                cp = subprocess.run(args=command, shell=True, check=False,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                returncode = cp.returncode
                print(sensor, OK if returncode == 0 else FAIL)
        print(SLEEPING)
        time.sleep(10)

