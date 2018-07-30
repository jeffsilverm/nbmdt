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
            parsed_args = nbmdt.arg_parser()
            assert parsed_args is None, f"There was a deliberate args parse error, this code comes after the " \
                                        f"exception was supposed to be raised. parsed_args should " \
                                        f"be None but is {str(parsed_args)} " \
                                 f"args_list is {str(args_list)}"

    def test_boot_mode(option):
        # Test that the boot mode works

        sys.argv = ["nbmdt.py", option]
        try:
            args = nbmdt.arg_parser()
        except ValueError as v:
            print(f"nbmdt.main raised a ValueError exception. option is {option}")
        assert isinstance(args, tuple), f"The return from nbmdt.arg_parser should be a tuple but is {str(type(args))}"
        assert len(args)==2, f"The return from nbmdt.arg_parser should be a length 2 but is {len(args)}"
        assert args.boot, "args.boot is False when it should be True"
        assert not args.monitor, "the --monitor switch is True when it should be False"
        assert not args.diagnose, "the --diagnose switch is True when it should be False"

    def test_monitor_mode(option):
        sys.argv = ["nbmdt.py", option]
        args = nbmdt.arg_parser()
        assert isinstance(args, tuple), f"The return from nbmdt.arg_parser should be a tuple but is {str(type(args))}"
        assert len(args)==2, f"The return from nbmdt.arg_parser should be a length 2 but is {len(args)}"
        assert not args.boot, "args.boot is True when it should be False"
        assert args.monitor, "args.monitor is False when it should be True"
        assert not args.diagnose, "args.diagnose switch is False when it should be True"

    def test_diagnose_mode(option):
        sys.argv = ["nbmdt.py", option]
        args = nbmdt.arg_parser()
        assert isinstance(args, tuple), f"The return from nbmdt.arg_parser should be a tuple but is {str(type(args))}"
        assert len(args)==2, f"The return from nbmdt.arg_parser should be a length 2 but is {len(args)}"
        assert not args.boot, "args.boot is True when it should be False"
        assert not args.monitor, "args.monitor is True when it should be False"
        assert args.diagnose, "args.diagnose is False when it should be True"

    def test_debug_option():
        # Does the --debug option work?
        sys.argv = ["nbmdt.py", "--diagnose", "--debug"]
        args = nbmdt.arg_parser()
        assert isinstance(args.debug, bool), f"args.debug should be boolean but is actually {type(args.debug)}"
        assert args.debug, "debug switch was given, but args.debug is False"
        sys.argv = ["nbmdt.py", "--diagnose"]
        args = nbmdt.arg_parser()
        assert isinstance(args.debug, bool), f"args.debug should be boolean but is actually {type(args.debug)}"
        assert not args.debug, "debug switch was not given, but args.debug is True"
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
