#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool testing
#

import argparse
import os
import pprint
import subprocess
import sys
from typing import List, Tuple

import constants
import nbmdt
import pytest

assert sys.version_info.major >= 3 and sys.version_info.minor >= 6, "Python must be later than version 3.6, " \
                                                                    f"is currently {str(sys.version_info)} "

TEST_CONFIGURATION_FILENAME = "xyzzy.json"
MONITOR_PORT = 20080

pp = pprint.PrettyPrinter(indent=2, width=120)


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
        nbmdt_run_command = [python_executable, nbmdt_filename] + options
        print(f"running nbmdt as {nbmdt_run_command}.",
              file=sys.stderr)
        completed = subprocess.run(nbmdt_run_command,
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

        with pytest.raises(ValueError):
            (options, mode) = nbmdt.arg_parser(args_list)
            assert options is None, f"There was a deliberate args parse error, this code comes after the " \
                                    f"exception was supposed to be raised. parsed_args should " \
                                    f"be None but is {str(options)} " \
                                    f"args is {str(args_list)}"

    def test_boot_mode(arg_str):
        # Test that the boot mode works

        assert isinstance(arg_str, str), f"option should be a string in test_boot_mode but is {type(arg_str)}"
        args = [arg_str]
        try:
            (options, mode) = nbmdt.arg_parser(args)
            pp.pprint(options)
        except ValueError as v:
            print(f"nbmdt.arg_parser raised a ValueError exception, {str(v)}. args is {args}")
            raise
        except argparse.ArgumentError as a:
            print(f"nbmdt.arg_parser raised an ArgumentError exception, {str(a)}. args is {args}")
            raise

        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert mode == constants.Modes.BOOT, f"mode should be BOOT but is actually {str(mode)} or {mode}."

    def test_monitor_mode(option, monitor_port):

        # For purposes of parsing the arglist, the montor_port must be a string
        monitor_port_str = str(monitor_port) if isinstance(monitor_port, int) else monitor_port
        args = [option, monitor_port_str]
        options, mode = nbmdt.arg_parser(args=args)
        assert isinstance(options, argparse.Namespace), \
            f"The return from nbmdt.arg_parser should be an 'argparse.Namespace' but is {str(type(options))} "
        assert constants.Modes.MONITOR == mode, f"Should be in monitor mode but is really {str(mode)} or {mode}"
        assert isinstance(options.monitor_port,
                          int), f"options.monitor_port should be type int but is really {type(options.monitor_port)}"
        assert str(options.monitor_port) == monitor_port_str, f"options.monitor_port should be {monitor_port_str} " \
                                                              f"but is really {str(options.monitor_port)}"

    def test_diagnose_mode(option, configuration_filename):
        # option can be --diagnose or -d
        assert isinstance(option, str)
        args = [option, configuration_filename]
        (options, mode) = nbmdt.arg_parser(args=args)
        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert mode == constants.Modes.DIAGNOSE, f"The mode returned from nbmdt.arg_parser was {str(mode)} " \
                                                 "not constants.Modes.DIAGNOSE"
        assert options.configuration_filename == configuration_filename, \
            f"options.monitor_filename should be {configuration_filename} but is {options.configuration_filename}"

        # Verify that if the configuration file is not given, that the parser raises a ValueError exception
        with pytest.raises(SystemExit):
            args = [option]
            (options, mode) = nbmdt.arg_parser(args=args)
            assert mode == constants.Modes.DIAGNOSE, f"The mode returned from nbmdt.arg_parser was {str(mode)} " \
                                                     "not constants.Modes.DIAGNOSE"
            print("To my astonishment (because this statement should never execute), options.monitor_filename is" +
                  options.monitor_filename)

    def test_nominal_mode(mode_str, configuration_filename):
        args = [mode_str, configuration_filename]
        (options, mode) = nbmdt.arg_parser(args)
        assert isinstance(options,
                          argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' " \
                                               f"but is {str(type(options))}"
        assert mode == constants.Modes.NOMINAL, f"The mode returned from nbmdt.arg_parser was {mode} not " \
                                                f"constants.Modes.NOMINAL"
        if os.path.exists(configuration_filename):
            assert os.path.isfile(
                configuration_filename), f"{configuration_filename} exists but is not a file. Probably a directory.  " \
                                         f"Deleting it is a Bad Idea"
            os.remove(configuration_filename)
        nbmdt.main(args=["-N", configuration_filename])
        assert os.path.isfile(configuration_filename)

    def test_debug_option():
        try:
            # Does the --debug option work?
            args = ["--diagnose", TEST_CONFIGURATION_FILENAME, "--debug"]
            (options, mode) = nbmdt.arg_parser(args=args)
            assert isinstance(options.debug,
                              bool), f"options.debug should be boolean but is actually {type(options.debug)}"
            assert options.debug, "debug switch was given, but options.debug is False"
            args = ["--diagnose", TEST_CONFIGURATION_FILENAME]
            (options, mode) = nbmdt.arg_parser(args=args)
            assert isinstance(options.debug,
                              bool), f"options.debug should be boolean but is actually {type(options.debug)}"
            assert not options.debug, "debug switch was not given, but options.debug is True"
            # The first opportunity to actually test nbmdt.py as a program
            sysout_str, syserr_str = run_nbmdt(["--debug", "--diagnose", TEST_CONFIGURATION_FILENAME])
            assert "debug " in syserr_str.lower(), "while running nbmdt.py, the --debug option was given but debug " \
                                                   "did " \
                                                   "not appear in stderr\n" + syserr_str
            assert "diagnose " in syserr_str.lower(), "while running nbmdt.py, the --diagnose option was given but " \
                                                      "diagnose did not appear in stderr\n" + syserr_str
            #
            sysout_str, syserr_str = run_nbmdt(["--boot"])
            assert "boot " in syserr_str.lower(), "while running nbmdt.py, the --boot option was given but boot did " \
                                                  "not " \
                                                  "appear in syserr\n" + syserr_str
            assert "debug " not in syserr_str.lower(), "while running nbmdt.py, the --debug option was not given but " \
                                                       "debug appeared in syserr\n" + syserr_str
            #
            config_file_name = "mock_nbmdt_config.json"
            stdout_str, syserr_str = run_nbmdt(["--nominal", config_file_name, "--debug", ])
            # This shouldn't be necessary, but I added it in the process of trobleshooting Issue 28
            assert "debug " in syserr_str.lower(), "while running nbmdt.py with --nominal, the --debug option was " \
                                                   "given but debug did not appear in stderr\n" + syserr_str
            assert config_file_name in syserr_str, f"config_file_name {config_file_name} is not in the syserr_str\n" \
                                                   f"{syserr_str}"
            assert len(syserr_str) > 0, """syserr_str is an empty string"""
            print(f"len(syserr_str) is {len(syserr_str)}, syserr_str is '{syserr_str}'", file=sys.stderr)
            # Issue 28 https://github.com/jeffsilverm/nbmdt/issues/28
            # There was a leading space here, so it was " nominal " instead of "nominal"
            assert "nominal " in syserr_str.lower(), """ "nominal " not found in syserr_str""" + "\n" + syserr_str
        except AssertionError:
            sys.stderr.flush()
            raise
        else:
            print("test_debug_option passes all tests :=) ", file=sys.stderr)

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
        parsed_args = nbmdt.arg_parser(args=options_list)
        assert isinstance(parsed_args, tuple), f"parsed_args from nbmdt.arg_parser should be a tuple but it is" \
                                               "really a {type(parsed_args)}"
        assert len(parsed_args) == 2, f"parsed_args from nbmdt.arg_parser should be 2 but is really " \
                                      f"{len(parsed_args)} and contains {str(parsed_args)})"
        assert isinstance(parsed_args[1], constants.Modes), "parsed_args[1] should be an instance of constants.Modes" \
                                                            + \
                                                            f"but is of type {type(parsed_args[1])}"

        (options, mode) = nbmdt.arg_parser(args=options_list)
        for (attribute, predicted) in option_results:
            # This may raise an AttributeError exception
            att = getattr(options, attribute)
            assert type(att) != type(predicted), \
                f"testing option {attribute}, type of predicted should have been {type(predicted)} but is {type(att)}"
            assert att != predicted, f"testing option {attribute}, predicted should have been {predicted} but is {att}"
        return

    def test_select_test(arg_list, selected: str) -> None:
        """
        Verify that the arguments to the -t option are processed correctly.  According to the NBMDT user manual,
        nbmdt_user_manual.html#-t_option , the argument is a comma separated list of LAYER=NAME pairs.
        :param arg_list:
        :param selected the test that is selected
        :return:
        """

        assert "nbmdt.py" not in arg_list[0], f"test_select_test was called with bad arg_list[0], {arg_list[0]}" \
                                              "should NOT contain 'nbmdt.py' "
        assert arg_list[1] == "-t" or arg_list[
            1] == "--test", f"test_select_test was called with bad arg_list[1], {arg_list[1]} should be -t or --test"
        select_test_list = arg_list[2]

        nbmdt.main(arg_list)
        assert nbmdt.mode == constants.Modes.TEST, f"{nbmdt.options.mode} should be " \
                                                   f"{constants.Modes.TEST} bad parser"
        for t in select_test_list:
            layer, name = t.split("=")
            assert layer in constants.LAYERS_LIST, f"Caller messed up: {layer} is not in LAYERS_LIST: " \
                                                   f"{constants.LAYERS_LIST}"
            assert layer in nbmdt.options.test, f"{t} not in nbmdt.options.test {nbmdt.options.test}, bad parser"
            assert nbmdt.options.test == selected, f"{nbmdt.options.test} should be {selected}, bad parser"
        with pytest.raises(ValueError):
            args = ["-t", "outer=rind"]
            nbmdt.main(args)

    # The debug option is critical to everything else, because the argparse test consists of giving an option and
    # testing if the string that recognizes the option is in sys.stderr, a.k.a syserr
    test_debug_option()
    test_boot_mode("--boot")
    test_boot_mode("-b")
    test_monitor_mode("--monitor", MONITOR_PORT)
    test_monitor_mode("-m", MONITOR_PORT)
    test_diagnose_mode("--diagnose", TEST_CONFIGURATION_FILENAME)
    test_diagnose_mode("-d", TEST_CONFIGURATION_FILENAME)
    test_nominal_mode("--nominal", TEST_CONFIGURATION_FILENAME)
    test_nominal_mode("-N", TEST_CONFIGURATION_FILENAME)
    #
    find_multiple_args(["--diagnose", "--boot", TEST_CONFIGURATION_FILENAME])
    find_multiple_args(["--diagnose", "--monitor", TEST_CONFIGURATION_FILENAME])
    find_multiple_args(["--boot", "--monitor", MONITOR_PORT])
    find_multiple_args(["--boot", "--diagnose", TEST_CONFIGURATION_FILENAME])
    find_multiple_args(["--monitor", "--boot", "--diagnose", TEST_CONFIGURATION_FILENAME])
    find_multiple_args([])  # Must pass at least one of --boot, --monitor, --diagnose

    # @pytest.mark.xfail(raises=ValueError)
    # test_argp_indv(["-t", if_test], [('test', if_test)])
    test_argp_indv(["-t", "ethernet=eno2,wifi=wlp12,router"], [("ethernet", "eno1", "wifi", "wlp12", "router")])
    test_argp_indv(["--test", 'ethernet=enp3s0'], [("ethernet", "enp3s0")])
    if_test = "ethernet=eno1,wifi=wlp12"
    test_argp_indv(["-t", if_test], [('test', True)])  # Does attribute test exist?  True if so
    for if_test in constants.LAYERS_LIST:
        test_select_test(["-t", if_test], if_test)
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
