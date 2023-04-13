import pytest
import crcengine
from crcengine.calc import _calc_end_mask
from crcengine import algorithms as alg

def test_end_bit_mask():
    """ Test calculation of final bit mask, counting MSbit first
    """
    # Bit 0 is MSbit only 1 bit set
    assert _calc_end_mask(0) == 0b1000_0000
    assert _calc_end_mask(1) == 0b1100_0000
    assert _calc_end_mask(2) == 0b1110_0000
    assert _calc_end_mask(3) == 0b1111_0000
    assert _calc_end_mask(4) == 0b1111_1000
    assert _calc_end_mask(5) == 0b1111_1100
    assert _calc_end_mask(6) == 0b1111_1110
    # Bit 7 is least significant bit, all bits set
    assert _calc_end_mask(7) == 0b1111_1111


@pytest.mark.parametrize(
    "start_bit, check_stream", [
        (0, 0b1001010110000000),
        (1, 0b1100101011000000),
        (2, 0b1110010101100000),
        (3, 0b1111001010110000),
        (4, 0b1111100101011000),
        (5, 0b1111110010101100),
        (6, 0b1111111001010110),
        (7, 0b1111111100101011),
    ]
)
def test_crc5_range_window(start_bit, check_stream):
    """Checksum a stream of 9 bits using a 5 bit CRC shifting the window of
    checked bits along the underlying two bytes.

    Note this isn't the same CRC5 listed in the algorithms table, just a plain
    MSB-first one with no bit reflection
    """
    params = {
        "poly": 0b00101,
        "width": 5,
        "seed": 0,
        "ref_in": False,
        "ref_out": False,
        "xor_out": 0,
    }
    crc_alg = crcengine.calc.windowed_crc(alg.params_from_dict(params))
    # Compare with hand-calculated result
    assert crc_alg.calculate(check_stream.to_bytes(2, byteorder='big'), start_bit=start_bit,
                             length_bits=9) == 0b01111
