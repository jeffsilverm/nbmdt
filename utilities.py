#!

# This file has utility functions that will be generally useful


from enum import Enum
import json

class Source(Enum):
    FILE = 1                # populate the object from a file.  This is "nominal"
    RUNNING = 2             # populate the object by querying the system.  This is "current"

class Comparison(Enum):
    NOMINAL = 1001
    OTHER = 1002



class SystemConfigurationFile(object):
    """This class handles interfacing between the program and the configuration file.  Thus, when the system is in its
    'nominal' state, then that's a good time to write the configuration file.  When the state of the system is
    questionable, then that's a good time to read the configuration file"""

    def __init__ (self, filename ):
        """Create a SystemConfigurationFile object which has all of the information in a system configuration file"""

        with open(filename, "r") as json_fp:
            self.system_description = json.load(json_fp)


    def save_state (self, filename ):
        with open(filename, "w") as json_fp:
            json.dump(self, json_fp, ensure_ascii=False )


    def compare_state (self, the_other ):
        """This method compares the 'nominal' state, which is in self, with another state, 'the_other'.  The output is
    a dictionary which is keyed by field.  The values of the dictionary are a dictionary with three keys:
    Comparison.NOMINAL, Comparison.OTHER.  The values of these dictonaries will be objects
    appropriate for what is being compared.  If something is not in Comparison.NOMINAL and not in Comparison.DIFFERENT,
     then there is no change.  
    
        """
        pass






