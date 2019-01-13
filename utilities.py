#!

# This file has utility functions that will be generally useful


import json
import platform
import subprocess
from sys import stderr
from typing import List

from constants import OperatingSystems
from nbmdt import SystemDescription


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


class SystemDescription(object):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including devices, datalinks, IPv4 and IPv6 addresses and routes, TCP and UDP, sessions,
     presentations, applications.  Each of these objects have a test associated with them"""

    # Issue 13
    #    CURRENT = None

    def __init__(self, applications: type_application_dict = None,
                 presentations: type_presentation_dict = None,
                 sessions: type_session_dict = None,
                 transports: type_transport_dict = None,
                 networks: type_network_dict = None,
                 # interfaces: type_interface_dict = None,          # Issue 25
                 datalinks: type_datalink_dict = None,
                 physicals: type_physical_dict = None,
                 # Removed mode - it's not part of the system description, it's how nbmdt processes a system description
                 configuration_filename: str = None,
                 system_name: str = platform.node()
                 ) -> None:
        """
        Populate a description of the system.  Note that this method is
        a constructor, and all it does is create a SystemDescription object.

        :param applications:
        :param presentations:
        :param sessions:
        :param transports:
        :param networks:
        :param datalinks:
        :param configuration_filename:
        :param system_name: str The name of this computer
        """
        self.applications = applications
        self.presentations = presentations
        self.sessions = sessions
        self.transports = transports  # TCP, UDP
        self.networks = networks  # IPv4, IPv6
        self.datalinks = datalinks  # MAC address
        self.physicals = physicals
        self.configuration_filename: str = configuration_filename
        self.system_name = system_name

    @classmethod
    def system_description_from_file(cls, filename: str) -> 'SystemDescription':
        """
        Read a system description from a file and create a SystemDescription object.
        I couldn't figure out how to return a SystemDescription object, so I return an object
        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} does not exist")
        with open(filename, "r") as f:
            so = json.load(f)

        return SystemDescription(
            applications=so.applications,
            presentations=so.presentations,
            sessions=so.presentations,
            transports=so.transports,
            networks=so.networks,
            datalinks=so.datalinks,
            physicals=so.physicals,
            configuration_filename=filename,
            system_name=so.system_name
        )

    @classmethod
    def discover(cls) -> object:
        """

        :return: a SystemDescription object.
        """

        applications: typing.Dict = application.Application.discover()
        presentations = presentation.Presentation.discover()
        sessions = session.Session.discover()
        transports = transport.Transport.discover()
        networks = network.Network.discover()
        # interfaces = interface.Interface.discover()
        datalinks = datalink.DataLink.discover()
        physicals = physical.Physical.discover()
        name: str = platform.node()

        my_system: object = SystemDescription(
            applications=applications,
            presentations=presentations,
            sessions=sessions,
            transports=transports,
            networks=networks,
            datalinks=datalinks,
            physicals=physicals,
            system_name=name
        )
        return my_system

    def file_from_system_description(self, filename: str) -> None:
        """Write a system description to a file
        :param  filename
        :return:
        """
        # In the future, detect if a configuration file already exists, and if so, create
        # a new version.
        with open(filename, "w") as f:
            json.dump(self, f)

    """
        def __init__(self, configuration_file: str = None, description: Descriptions = None) -> None:

            if configuration_file is None:
                # This is what the system is currently is

                # Create a dictionary, keyed by link name, of the physical interfaces
                self.phys_db = interfaces.PhysicalInterface.get_all_physical_interfaces()
                # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
                self.data_link_db = interfaces.LogicalInterface.get_all_logical_interfaces()
                # Create lists, sorted from smallest netmask to largest netmask of IPv4 and IPv6 routes
                self.ipv4_routes = network.IPv4Route.find_ipv4_routes()
                self.default_ipv4_gateway : network.IPv4Address = network.IPv4Route.get_default_ipv4_gateway()
                self.ipv6_routes = network.IPv6Route.find_ipv6_routes()
                self.default_ipv6_gateway : network.IPv6Address = network.IPv6Route.get_default_ipv6_gateway()
                # Create something... what?  to track transports (OSI layer 4)
                self.transports_4 = transports.ipv4
                self.transports_6 = transports.ipv6
                # Issue 13
                if description is None or description == self.Descriptions.CURRENT:
                    # Assume current
                    self.description = self.Descriptions.CURRENT


            else:
                raise NotImplemented("configuration file is not implemented yet")

            if not hasattr(self, "IP_COMMAND"):
                self.IP_COMMAND = configuration.Configuration.find_executable('ip')
            if not hasattr(self, "PING4_COMMAND"):
                self.PING4_COMMAND = configuration.Configuration.find_executable('ping')
            if not hasattr(self, "PING6_COMMAND"):
                self.PING6_COMMAND = configuration.Configuration.find_executable('ping6')
            if DEBUG:
                import os
                assert os.stat.S_IXUSR & os.stat(os.path)[os.stat.ST_MODE]
                assert os.stat.S_IXUSR & os.stat(os.path)[os.stat.ST_MODE]
                self.applications: dict = {}  # For now

                #        self.name_servers = nameservers.nameservers()
                #        self.applications = applications
                # To find all IPv4 machines on an ethernet, use arp -a     See ipv4_neighbors.txt

                # To find all IPv6 machines on an ethernet, use ip -6 neigh show
                #        self.networks = networks
                #        self.name = name
            else:
                y = yaml.safe_load(configuration_file)
                self.interfaces = y['interfaces']
                for interface in self.interfaces:
                    self.ipv4_address = interfaces

    """
    """
        @staticmethod
        def describe_current_state():
            "This method goes through a system that is nominally configured and operating and records the configuration
            "

            #        applications = Applications.find_applications()
            #        applications = None
            #        ipv4_routes = IPv4_route.find_ipv4_routes()
            #        ipv6_routes = IPv6_route.find_ipv6_routes()
            #        ipv6_addresses = interfaces.LogicalInterface.find_ipv6_addresses()
            #        ipv4_addresses = interfaces.LogicalInterface.find_ipv4_addresses()
            #        networks = Networks.find_networks()
            #        networks = None

            # nominal = SystemDescription.describe_current_state()
            pass

        #        return (applications, ipv4_routes, ipv6_routes, ipv4_addresses, ipv6_addresses, networks)
    """

    @property
    def __str__(self):
        """This generates a nicely formatted report of the state of this system
        This method is probably most useful in BOOT mode.

        The classes should be re-written with __str__ methods which are sensitive to the mode
        """
        result = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(str(self.applications), str(self.presentations),
                                                       str(self.sessions), str(self.transports), str(self.networks),
                                                       str(self.datalinks))
        return result

    def nominal(self, filename) -> None:
        print(f"The nominal configuration file is going to be {filename}", file=sys.stderr)
        self.file_from_system_description(filename)

    def boot(self) -> constants.ErrorLevels:
        print("Going to test in boot mode", file=sys.stderr)
        raise NotImplementedError

    def monitor(self, port) -> None:
        print(f"going to monitor on port {port}", file=sys.stderr)
        raise NotImplementedError

    def diagnose(self, filename) -> constants.ErrorLevels:
        print(f"In diagnostic mode, nomminal filename is {filename}", file=sys.stderr)
        nominal_system: SystemDescription = SystemDescription.system_description_from_file(filename)
        raise NotImplementedError
        return constants.ErrorLevels.UNKNOWN

    def test(self, test_specification) -> constants.ErrorLevels:
        print(f"The test_specification is {test_specification}", file=sys.stderr)
        raise NotImplementedError
        return constants.ErrorLevels.UNKNOWN

class SystemDescriptionFile(SystemDescription):
    """This class handles interfacing between the program and the configuration file.  Thus, when the system is in its
    'nominal' state, then that's a good time to write the configuration file.  When the state of the system is
    questionable, then that's a good time to read the configuration file"""

    def __init__(self, configuration_filename):
        """Create a SystemDescription object which has all of the information in a system configuration file"""

        with open(configuration_filename, "r") as json_fp:
            c_dict = json.load(json_fp)         # Configuration dictionary
        super(SystemDescriptionFile, self).__init__(applications=c_dict["applications"],
                                                    presentations=c_dict["presentations"],
                                                    sessions=c_dict["sessions"],
                                                    transports=c_dict["networks"],
                                                    datalinks=c_dict["datalinks"],
                                                    physicals=c_dict["physicals"],
                                                    configuration_filename=configuration_filename,
                                                    system_name=None    # for now.
                                                    )
        self.version = c_dict['version']
        self.timestamp = c_dict['timestamp']

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

        assert isinstance(command, list), f"command should be a list of strings but is actually a string {command}"
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
    if OperatingSystems.LINUX == the_os:
        print(f"In linux, the uname -a command output is \n{OsCliInter.run_command(['uname', '-a'])}\n.")
