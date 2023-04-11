"""
Test the functionality in crcengine.algorithms
"""
from crcengine import algorithms as alg


def test_lookup_params():
    params = alg.lookup_params("crc16-xmodem")
    assert params.polynomial == 0x1021
    assert params.width == 16
    assert params.seed == 0
    assert not params.reflect_in
    assert not params.reflect_out
