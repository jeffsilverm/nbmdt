#!

# This file has utility functions that will be generally useful


import json
import platform
import subprocess
from sys import stderr
from typing import List

from constants import OperatingSystems

"""
>>> platform.system()
'Linux'
>>> 
>>> platform.linux_distribution()
('Ubuntu', '18.04', 'bionic')
>>> platform.dist()
('Ubuntu', '18.04', 'bionic')
>>> 

>>> platform.mac_ver()
('', ('', '', ''), '')
>>> 
>>> platform.win32_ver()
('', '', '', '')
>>> 
>>> platform.mac_ver()
('', ('', '', ''), '')
>>> 


"""


class SystemConfigurationFile(object):
    """This class handles interfacing between the program and the configuration file.  Thus, when the system is in its
    'nominal' state, then that's a good time to write the configuration file.  When the state of the system is
    questionable, then that's a good time to read the configuration file"""

    def __init__(self, filename):
        """Create a SystemConfigurationFile object which has all of the information in a system configuration file"""

        with open(filename, "r") as json_fp:
            self.system_description = json.load(json_fp)

    def save_state(self, filename):
        with open(filename, "w") as json_fp:
            json.dump(self, json_fp, ensure_ascii=False)

    def compare_state(self, the_other):
        """This method compares the 'nominal' state, which is in self, with another state, 'the_other'.  The output is
    a dictionary which is keyed by field.  The values of the dictionary are a dictionary with three keys:
    Comparison.NOMINAL, Comparison.OTHER.  The values of these dictonaries will be objects
    appropriate for what is being compared.  If something is not in Comparison.NOMINAL and not in Comparison.DIFFERENT,
     then there is no change.  
    
        """
        pass


class OsCliInter(object):
    """
    A collection of methods for running CLI commands.
    """

    # Since the system is going to be the same across the entire program, populate it when the OsCliInter object is
    # imported for the first time and then make it available to any object in class OsCliInter (which should not need
    # to be instantiated.  See https://docs.python.org/3/library/platform.html
    # possible values are: 'Linux', 'Windows', or 'Java'  (what about Mac?)
    system: str = platform.system().lower()
    assert "linux" == system or "windows" == system or "java" == system, \
        f"platform.system returned an unknown (not unimplemented, that's different) value: {system}"

    @classmethod
    def run_command(cls, command: List[str]) -> str:
        """
        Run the command on the CLI

        :param command: a list of strings.  Element 0 is the name of the executable. The rest of the list are args to
        the command
        :return: A string which is the output of the program in ASCII
        """

        completed: subprocess.CompletedProcess = subprocess.run(command,
                                                                stdin=None,
                                                                input=None,
                                                                stdout=subprocess.PIPE, stderr=None, shell=False,
                                                                timeout=None,
                                                                check=False)
        completed_str = completed.stdout.decode('ascii')
        return completed_str


try:
    print("Testing the __file__ special variable: " + __file__, file=stderr)  # sys.stderr
except Exception as e:  # if anything goes wrong
    print("Testing the __file__ special variable FAILED, exception is " + str(e), file=stderr)  # sys.stderr

# Globally note the operating system name.  Note that this section of the code *must* follow the definition
# of class OsCliInter or else the compiler will raise a NameError exception at compile time
# Access the_os using utilities.the_os  The variable is so named to avoid confusion with the os package name
os_name: str = OsCliInter.system.lower()
the_os = OperatingSystems.UNKNOWN
if 'linux' == os_name:
    the_os = OperatingSystems.LINUX
elif 'windows' == os_name:
    the_os = OperatingSystems.WINDOWS
elif 'darwin' == os_name:
    the_os = OperatingSystems.MAC_OS_X
else:
    raise ValueError(f"System is {os_name} and I don't recognize it")

if "__main__" == __name__:
    print(f"System is {os_name} A.K.A. {the_os}")
