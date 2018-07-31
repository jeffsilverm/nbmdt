#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool testing
#

import sys
from typing import List
import subprocess
import pytest
import nbmdt
import argparse

assert sys.version_info.major >= 3 and sys.version_info.minor >= 6, "Python must be later than version 3.6, " \
                                                                    f"is currently {str(sys.version_info)} "


def test_argparse():
    """Verify that the argparser accepts one and only one of --boot, --monitor, --diagnose"""

    def find_multiple_args(args_list: List[str]):
        """
        Test the ability of nbmdt.py to detect invalid combinations of options
        :param args_list:   list of strings
        :return:
        """
        sys.argv = ["nbmdt.py"] + args_list
        with pytest.raises(ValueError):
            (parsed_args, mode) = nbmdt.arg_parser()
            assert parsed_args is None, f"There was a deliberate args parse error, this code comes after the " \
                                        f"exception was supposed to be raised. parsed_args should " \
                                        f"be None but is {str(parsed_args)} " \
                                 f"args_list is {str(options_list)}"

    def test_boot_mode(option):
        # Test that the boot mode works

        sys.argv = ["nbmdt.py", option]
        try:
            (options, mode) = nbmdt.arg_parser()
        except ValueError as v:
            print(f"nbmdt.main raised a ValueError exception. option is {option}")
        assert isinstance(options, argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' but is {str(type(options))}"
        assert options.boot, "options.boot is False when it should be True"
        assert not options.monitor, "the --monitor switch is True when it should be False"
        assert not options.diagnose, "the --diagnose switch is True when it should be False"

    def test_monitor_mode(option):
        sys.argv = ["nbmdt.py", option]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options, argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' but is {str(type(options))}"
        assert not options.boot, "options.boot is True when it should be False"
        assert options.monitor, "options.monitor is False when it should be True"
        assert not options.diagnose, "options.diagnose switch is False when it should be True"

    def test_diagnose_mode(option):
        sys.argv = ["nbmdt.py", option]
        (options, mode) = nbmdt.arg_parser()
        assert isinstance(options, argparse.Namespace), f"The return from nbmdt.arg_parser should be a 'argparse.Namespace' but is {str(type(options))}"
        assert not options.boot, "options.boot is True when it should be False"
        assert not options.monitor, "options.monitor is True when it should be False"
        assert options.diagnose, "options.diagnose is False when it should be True"

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
        stdout_str, stderr_str = run_nbmdt("--debug", "--diagnose")
        assert "debug" in stderr_str.lower(), "while running nbmdt.py, the --debug option was given but debug did not appear in stderr"
        assert "diagnose" in stderr_str.lower(), "while running nbmdt.py, the --diagnose option was given but diagnose did not appear in stderr"
        stdout_str, stderr_str = run_nbmdt("--boot")
        assert "debug" not in stderr_str.lower(), "while running nbmdt.py, the --debug option was not given but debug appeared in stderr"
        assert "boot" in stderr_str.lower(), "while running nbmdt.py, the --boot option was given but boot did not appear in stderr"

    def test_nominal_mode():
        raise NotImplemented


    # There should be a bug report here: utilities.py should be able to handle this use case.  It
    # doesn't, and rather than fix it now and fix anything that calls it, I am duplicating it here.
    def run_nbmdt( options : List[str]):
        """
        :param options:  A list of strings that are options to the nbmdt program
        :return: a tuple of 2 strings, the first of which is stdout, and the second is stderr
        """
        python_executable = sys.executable
        completed = subprocess.run([python_executable, "nbmdt.py"] + options,
                                   stdin=None,
                                   input=None,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, timeout=None,
                                   check=False)
        stdout_str : str = completed.stdout.decode('ascii')
        stderr_str : str = completed.stderr.decode('ascii')
        return ( stdout_str, stderr_str )


    test_boot_mode("--boot")
    test_boot_mode("-b")
    test_monitor_mode("--monitor")
    test_monitor_mode("-m")
    test_diagnose_mode("--diagnose")
    test_diagnose_mode("-d")
    test_nominal_mode("--nominal")
    test_nominal_mode("-N")

#
    with pytest.raises(NotImplemented):
        test_nominal_mode("--nominal")
        test_nominal_mode("-N")


    find_multiple_args(["--diagnose", "--boot"])
    find_multiple_args(["--diagnose", "--monitor"])
    find_multiple_args(["--boot", "--monitor"])
    find_multiple_args(["--boot", "--diagnose"])
    find_multiple_args(["--monitor", "--boot", "--diagnose"])
    find_multiple_args([])      # Must pass at least one of --boot, --monitor, --diagnose

    with pytest.raises(FileNotFoundError):
        sys.argv = ["nbmdt.py", "--file", "xyzzy.txt"]
        nbmdt.main()

    test_debug_option()





if __name__ == "__main__":
    pytest.main()
