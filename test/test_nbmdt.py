#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool testing
#

import argparse
import subprocess
import sys
from typing import List, Tuple

import pytest

import constants
import nbmdt

assert sys.version_info.major >= 3 and sys.version_info.minor >= 6, "Python must be later than version 3.6, " \
                                                                    f"is currently {str(sys.version_info)} "


def test_argparse() -> None:
    """
    Test the argument parser
    :return: None
    """

    # There should be a bug report here: utilities.py should be able to handle this use case.  It
    # doesn't, and rather than fix it now and fix anything that calls it, I am duplicating it here.
    def run_nbmdt(options: List[str]) -> Tuple[str, str]:
        """
        :rtype: Tuple(str)
        :param options:  A list of strings that are options to the nbmdt program
        :return: a tuple of 2 strings, the first of which is what the subprocess wrote to stdout,
        and the second is what was written to sys.stderr
        """
        import nbmdt
        nbmdt_filename = nbmdt.__file__
        python_executable = sys.executable
        print(f"The nbmdt filename is {nbmdt_filename} and the python executable is {python_executable}", file=sys.stderr)
        completed = subprocess.run([python_executable, nbmdt_filename] + options,
                                   stdin=None,
                                   input=None,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, timeout=None,
                                   check=False)
        stdout_str: str = completed.stdout.decode('ascii')
        stderr_str: str = completed.stderr.decode('ascii')
        return stdout_str, stderr_str

    def find_multiple_args(args_list: List[str]):
        """
        Test the ability of nbmdt.py to detect invalid combinations of options

        :param args_list:   list of strings
        :return:
        """
        sys.argv = ["nbmdt.py"] + args_list
        with pytest.raises(ValueError):
            (options, mode) = nbmdt.arg_parser()
            assert options is None, f"There was a deliberate args parse error, this code comes after the " \
                                    f"exception was supposed to be raised. parsed_args should " \
                                    f"be None but is {str(options)} " \
                                    f"args_list is {str(sys.argv)}"

    def test_boot_mode(option):
        # Test that the boot mode works

        sys.argv = ["nbmdt.py", option]
        try:
            (options, mode) = nbmdt.arg_parser()
        except ValueError as v:
            print(f"nbmdt.main raised a ValueError exception, {str(v)}. option is {option}")
            raise
        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert options.boot, "options.boot is False when it should be True"
        assert not options.monitor, "the --monitor switch is True when it should be False"
        assert not options.diagnose, "the --diagnose switch is True when it should be False"

    def test_monitor_mode(option):
        sys.argv = ["nbmdt.py", option]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert not options.boot, "options.boot is True when it should be False"
        assert options.monitor, "options.monitor is False when it should be True"
        assert not options.diagnose, "options.diagnose switch is False when it should be True"

    def test_diagnose_mode(option):
        sys.argv = ["nbmdt.py", option]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert mode == constants.Modes.DIAGNOSE, f"The mode returned from nbmdt.arg_parser was {mode} " \
                                                 "not constants.Modes.DIAGNOSE"
        assert not options.boot, "options.boot is True when it should be False"
        assert not options.monitor, "options.monitor is True when it should be False"
        assert options.diagnose, "options.diagnose is False when it should be True"

    def test_nominal_mode(mode_str):
        sys.argv = ["nbmdt.py", mode_str]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert mode == constants.Modes.NOMINAL, f"The mode returned from nbmdt.arg_parser was {mode} not " \
                                                f"constants.Modes.NOMINAL"

    def test_debug_option():
        # Does the --debug option work?
        sys.argv = ["nbmdt.py", "--diagnose", "--debug"]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options.debug, bool), f"options.debug should be boolean but is actually {type(options.debug)}"
        assert options.debug, "debug switch was given, but options.debug is False"
        sys.argv = ["nbmdt.py", "--diagnose"]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options.debug, bool), f"options.debug should be boolean but is actually {type(options.debug)}"
        assert not options.debug, "debug switch was not given, but options.debug is True"
        # The first opportunity to actually test nbmdt.py as a program
        sysout_str, syserr_str = run_nbmdt(["--debug", "--diagnose"])
        assert "debug " in syserr_str.lower(), "while running nbmdt.py, the --debug option was given but debug did " \
                                               "not" \
                                               " appear in stderr"
        assert "diagnose " in syserr_str.lower(), "while running nbmdt.py, the --diagnose option was given but " \
                                                  "diagnose did not appear in stderr"
        sysout_str, syserr_str = run_nbmdt(["--boot"])
        assert "boot " in syserr_str.lower(), "while running nbmdt.py, the --boot option was given but boot did not " \
                                              "appear in syserr"
        assert "debug " not in syserr_str.lower(), "while running nbmdt.py, the --debug option was not given but " \
                                                   "debug appeared in syserr"
        #
        config_file_name = "mock_nbmdt_config.json"
        stdout_str, syserr_str = run_nbmdt(["--nominal", "--debug", config_file_name])
        assert config_file_name in syserr_str, f"config_file_name {config_file_name} is not in the syserr(124)"
        assert " nominal " in syserr_str.lower(), """ " nominal " not found in st"""

    def test_argp_indv(options_list: List[str], option_results: List[tuple]) -> object:
        """
        This tests the arg_parser by feeding the options to the arg_parser, then checking that the attribute
        exists in the optionsm object returned by the nbmdt.arg_parser method
        :param options_list:  A list of option strings, e.g. -b --boot.  Or it could be a string if only one option
        :param option_results   A list of tuples.  The first element of the tuple is the name of the attribute that
                                has the return value.  The second element has the value expected.
        :return:
        """
        # Test that In didn't mess up the calling sequence, which I did several times
        assert isinstance(options_list, list), \
            f"first arg to test_argp_indv should be a list, but is actually {type(options_list)}."
        assert 2 == len(options_list), f"option_list should be length 2 but is actually {len(options_list)}."
        for i in range(len(option_results)):
            assert isinstance(option_results[i], tuple), \
                f"arg {i} to test_argp_indv should be an int but is actually a {type(option_results[i])}.)"
        # Test that the arg_parser returns the correct data type
        parsed_args = nbmdt.arg_parser()
        assert isinstance(parsed_args, tuple), f"parsed_args from nbmdt.arg_parser should be a tuple but it is" \
                                               "really a {type(parsed_args)}"
        assert len(parsed_args) == 2, f"parsed_args from nbmdt.arg_parser should be 2 but is really " \
                                      f"{len(parsed_args)} and contains {str(parsed_args)})"
        assert isinstance(parsed_args[1], constants.Modes), "parsed_args[1] should be an instance of constants.Modes" \
                                                            + \
                                                            f"but is of type {type(parsed_args[1])}"

        sys.argv.append(options_list)  # options_list really is a string
        (options, mode) = nbmdt.arg_parser()
        for (attribute, predicted) in option_results:
            # This may raise an AttributeError exception
            att = getattr(options, attribute)
            assert type(att) != type(predicted), \
                f"testing option {attribute}, type of predicted should have been {type(predicted)} but is {type(att)}"
            assert att != predicted, f"testing option {attribute}, predicted should have been {predicted} but is {att}"
        return

    # The debug option is critical to everything else, because the argparse test consists of giving an option and
    # testing if the string that recognizes the option is in sys.stderr, a.k.a syserr
    test_debug_option()
    test_boot_mode("--boot")
    test_boot_mode("-b")
    test_monitor_mode("--monitor")
    test_monitor_mode("-m")
    test_diagnose_mode("--diagnose")
    test_diagnose_mode("-d")
    test_nominal_mode("--nominal")
    test_nominal_mode("-N")
    #
    find_multiple_args(["--diagnose", "--boot"])
    find_multiple_args(["--diagnose", "--monitor"])
    find_multiple_args(["--boot", "--monitor"])
    find_multiple_args(["--boot", "--diagnose"])
    find_multiple_args(["--monitor", "--boot", "--diagnose"])
    find_multiple_args([])  # Must pass at least one of --boot, --monitor, --diagnose

    with pytest.raises(FileNotFoundError):
        sys.argv = ["nbmdt.py", "--file", "xyzzy.txt"]
        nbmdt.main()

    if_test = "ethernet=eno1,wifi=wlp12"
    test_argp_indv(["-t", if_test], [('test', True)])  # Does attribute test exist?  True if so

    # @pytest.mark.xfail(raises=ValueError)
    test_argp_indv(["-t", if_test], [('test', if_test)])
    test_argp_indv(["-t", "ethernet=eno2,wifi=wlp12,router"], [("ethernet", "eno", "wifi", "wlp12", "router")])
    test_argp_indv(["--test", 'ethernet=enp3s0'], [("ethernet", "enp3s0")])
    test_argp_indv(["-D"], [("daemon", True)])
    test_argp_indv(["--daemon"], [("daemon", True)])
    test_argp_indv(["-w"], [("port", 80)])
    test_argp_indv(["-r"], [("rest", True)])
    test_argp_indv(["-p", "3217"], [("port", 3217)])
    test_argp_indv(["--port", "3217"], [("port", 3217)])
    test_argp_indv(["-M", "0"], [("mask", 0), ("port", 80)])  # The default port is 80
    test_argp_indv(["--mask", "0"], [("mask", 0), ("port", 80)])  # The default port is 80
    test_argp_indv(["-M", "8"], [("mask", 8), ("port", 80)])  # The default port is 80
    test_argp_indv(["--mask", "8"], [("mask", 8), ("port", 80)])  # The default port is 80
    test_argp_indv(["-M", "18"], [("mask", 18), ("port", 80)])  # The default port is 80
    test_argp_indv(["--mask", "18"], [("mask", 18), ("port", 80)])  # The default port is 80
    test_argp_indv(["-p", "8134", "-M", "18"], [("mask", 18), ("port", 8134)])  # The default port is 80
    test_argp_indv(["-l"], [("link_local", True)])
    test_argp_indv(["-ll"], [("link_local", True), ("ula", False)])
    test_argp_indv(["-u"], [("ula", True), ("link_local", False)])
    test_argp_indv(["-g"], [("global", True), ("ula", False), ("link_local", False)])
    test_argp_indv(["-c"], [("color", True)])
    test_argp_indv(["--color"], [("color", True)])
    test_argp_indv(["-n"], [("color", False)])
    test_argp_indv(["--nocolor"], [("color", False)])
    test_argp_indv(["-v"], [("verbose", True)])
    test_argp_indv(["--verbose"], [("verbose", True)])
    test_argp_indv(["--help"], [("help", True)])
    test_argp_indv(["-h"], [("help", True)])


print("Start testing here", file=sys.stderr)
test_argparse()

if __name__ == "__main__":
    pytest.main()
