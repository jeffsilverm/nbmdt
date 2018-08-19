#!

# This file has utility functions that will be generally useful


import json
import subprocess
from enum import Enum
from typing import List

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


class OSILevels(Enum):
    PHYSICAL = 1
    MEDIAACCESSCONTROL = 2
    NETWORK = 3
    TRANSPORT = 4
    SESSION = 5
    PRESENTATION = 6
    APPLICATION = 7


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
                                              stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
                                              check=False)
        completed_str = completed.stdout.decode('ascii')
        return completed_str


