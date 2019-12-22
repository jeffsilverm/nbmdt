import pytest
from unittest import mock
import sys

HELP_MSG = """
Enter -h or --help for help
Enter -g or --good for known good routing tables
Enter -c or --current for the current actual routing tables
Enter -b FAILURE or --bad FAILURE to simulate a failed route.
FAILURE can be (comma separated):
NODEF   no default gateway
TWODEF  two default gateways
DEFNOPING   The default gateway is not pingable
    """

#####
# READ https://www.thedigitalcatonline.com/blog/2016/03/06/python-mocks-a-gentle-introduction-part-1/
####
@pytest.fixture
def cmdopt(request):
    return request.config.getoption("--seltest")

def pytest_addoption(parser):
    parser.addoption(
        "--seltest", action="store", default=None, help=HELP_MSG)
    return None

def test_routing_table(seltest):
    if seltest == "-h" or seltest == "--help":
        print(HELP_MSG, file=sys.stderr)
        sys.exit(0)

    assert False, "This should be False"
    assert True, "This should be True which means you will never see it"



if __name__ == '__main__':
    pytest.main()
