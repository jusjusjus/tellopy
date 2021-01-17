from tellopy import utils
from .conftest import is_valid_ip


def test_get_own_ip():
    """test that utils.get_own_ip return url"""
    ip = utils.get_own_ip()
    assert is_valid_ip(ip), ip
