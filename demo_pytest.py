import pytest

import interface

# See https://gist.githubusercontent.com/alysivji/a2535eae67a5569fa0169766c228f818/raw/d166e13401f6a2eb01719074dd7b80a67bfcc300/test_interface_pytest.py
# and https://gist.github.com/alysivji/a2535eae67a5569fa0169766c228f818
# and https://disqus.com/home/discussion/siv-scripts/adding_function_arguments_to_pytest_fixtures/?utm_source=reply&utm_medium=email&utm_content=read_more#comment-3865338855


@pytest.fixture(scope='session')
def run_command_mock(mocker):
    def _create_run_command_mock(mock_return_value):
        mock_run = mocker.MagicMock(name='run command mock')
        mock_run.return_value = "foo"
        run_command_patch = mocker.patch('interface.run_command', new=mock_run)
        return run_command_patch

    return _create_run_command_mock


def test_interface_run_command(ifname : str) -> boolean :

    eno1_obj = interface.Interface(ifname)
    assert isinstance(eno1_obj.mtu, "str"), f"mtu should be a string"
    assert eno1_obj.mtu == "1500", f"The MTU should be 1500 but is really {eno1_obj}"
