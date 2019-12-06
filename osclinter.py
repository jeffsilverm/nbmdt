#!

# This file has utility functions that will be generally useful


import json
import os
import platform
import subprocess
import sys
from typing import List, Tuple

import constants
from constants import ErrorLevels
from constants import OperatingSystems
from constants import type_application_dict, type_presentation_dict, type_session_dict, \
    type_transport_dict, type_network_4_dict, type_network_6_dict, type_datalink_dict, \
    type_physical_dict

class OsCliInter(object):
    """
    A collection of methods for running CLI commands.
    """
    # This causes compilation of utilities.py to fail.  See issue #29, https://github.com/jeffsilverm/nbmdt/issues/29
    # Since the system is going to be the same across the entire program, populate it when the OsCliInter object is
    # imported for the first time and then make it available to any object in class OsCliInter (which should not need
    # to be instantiated.  See https://docs.python.org/3/library/platform.html
    # possible values are: 'Linux', 'Windows', or 'Java'  (what about Mac?)
    system: str = platform.system().lower()
    assert "linux" == system or "windows" == system or "java" == system, \
        f"platform.system returned an unknown (not unimplemented, that's different) value: {system}"

    @classmethod
    def run_command(cls, command: List[str]) -> Tuple[str, str, int]:
        """
        Run the command on the CLI.  This is here to make it easy to mock

        :param command: a list of strings.  Element 0 is the name of the executable. The rest of the list are args to
        the command
        :return: A string which is the output of the program in ASCII
        """

        assert isinstance(command, list), f"command should be a list of strings but is actually a string {command}"
        completed: subprocess.CompletedProcess = subprocess.run(command,
                                                                stdin=None,
                                                                input=None,
                                                                stdout=subprocess.PIPE, stderr=None, shell=False,
                                                                timeout=None,
                                                                check=False)
        # Issue #36 - return stdout, stderr, and the return status code.
        stdout_str: stdout_str = completed.stdout.decode('ascii')
        # Why the following isn't the default behavior, I'll never know
        stderr_str str = ( "" if completed.stderr is Null else \
                completed.stderr.decode('ascii') )
        status: int = completed.returncode
        return stdout_str, stderr_str, status


try:
    print("Testing the __file__ special variable: " + __file__, file=sys.stderr)
except Exception as e:  # if anything goes wrong
    print("Testing the __file__ special variable FAILED, exception is " + str(e), file=sys.stderr)

# Globally note the operating system name.  Note that this section of the code *must* follow the definition
# of class OsCliInter or else the compiler will raise a NameError exception at compile time
# Access the_os using utilities.the_os  The variable is so named to avoid confusion with the os package name
print("About to import osCliInter", file=sys.stderr)
os_name: str = OsCliInter.system.lower()
the_os = constants.OperatingSystems.UNKNOWN
if 'linux' == os_name:
    the_os = constants.OperatingSystems.LINUX
elif 'windows' == os_name:
    the_os = constants.OperatingSystems.WINDOWS
elif 'darwin' == os_name:
    the_os = constants.OperatingSystems.MAC_OS_X
else:
    raise ValueError(f"System is {os_name} and I don't recognize it")

if "__main__" == __name__:
    print(f"System is {os_name} A.K.A. {the_os}")
    if OperatingSystems.LINUX == the_os:
        print(f"In linux, the uname -a command output is \n{OsCliInter.run_command(['uname', '-a'])}\n.")
    else:
        raise NotImplemented("This program ONLY runs on linux at this time")
