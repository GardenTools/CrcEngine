"""Unit tests for the crcengine module"""
# This file is part of crcengine.
#
# crcengine is free software: you can redistribute it an d /or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# crcengine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with crcengine.  If not, see <https://www.gnu.org/licenses/>.
import struct
import pytest
import crcengine
from crcengine import get_algorithm_params, bit_reverse_n

# pylint: disable=missing-function-docstring,redefined-outer-name
_CRC32_POLY = get_algorithm_params('crc32')['poly']
_U32_MAX = crcengine.get_maximum_value(32)


@pytest.fixture
def crc32():
    return crcengine.new('crc32')


@pytest.fixture
def crc16_kermit():
    return crcengine.new('crc16-kermit')


@pytest.fixture
def crc16_xmodem():
    return crcengine.new('crc16-xmodem')


@pytest.fixture
def crc16_autosar():
    return crcengine.new('crc16-autosar')


def test_reverse_poly():
    assert bit_reverse_n(0, 32) == 0
    assert bit_reverse_n(1, 8) == 0x80
    assert bit_reverse_n(1, 16) == 0x8000
    assert bit_reverse_n(1, 17) == 0x10000
    assert bit_reverse_n(1, 32) == 0x80000000
    assert bit_reverse_n(_CRC32_POLY, 32) == 0xEDB88320


def test_crc8():
    crc8 = crcengine.new('crc8')
    assert crc8(b'123456789') == 0xbc


def test_crc8_autosar():
    crc8 = crcengine.new('crc8-autosar')
    assert crc8(b'123456789') == 0xdf


def test_crc8_bluetooth():
    crc8 = crcengine.new('crc8-bluetooth')
    assert crc8(b'123456789') == 0x26


def test_crc32_generic():
    """Test the generic calculation engine with a CRC32"""
    crc32_generic = crcengine.create_generic(_CRC32_POLY, 32, _U32_MAX,
                                       ref_in=True, ref_out=True,
                                       xor_out=_U32_MAX)
    assert crc32_generic(b'123456789') == 0xCBF43926
    assert crc32_generic(b'A') == 0xD3D99E8B


def test_crc32_generic_lsb():
    poly = crcengine.bit_reverse_n(_CRC32_POLY, 32)
    assert poly == 0xEDB88320
    crc32_generic = crcengine.create_generic_lsbf(
        poly, 32, _U32_MAX, ref_in=False, ref_out=False,
        xor_out=_U32_MAX)
    assert crc32_generic.calculate(b'A') == 0xD3D99E8B
    assert crc32_generic.calculate(b'123456789') == 0xCBF43926


def test_generate_crc32_table_individual():
    table = crcengine.create_msb_table_individual(_CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_generate_crc32_msb_table():
    table = crcengine.create_msb_table(_CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[2] == 0x09823B6E
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_generate_crc32_lsb_table():
    table = crcengine.create_lsb_table(_CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x77073096
    assert table[2] == 0xEE0E612C
    assert table[7] == 0x9E6495A3
    assert table[255] == 0x2D02EF8D


def test_generate_crc32_msb_table_individual():
    table = crcengine.create_msb_table_individual(_CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[2] == 0x09823B6E
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_crc32_table_driven(crc32):
    assert crc32(b'A') == 0xD3D99E8B
    assert crc32(b'123456789') == 0xCBF43926
    # The values below are from the AUTOSAR spec.
    assert crc32(b'\x00\x00\x00\x00') == 0x2144DF1C
    assert crc32(b'\x0F\xAA\x00\x55') == 0xB6C9B287
    assert crc32(b'\x00\xFF\x55\x11') == 0x32A06212
    assert crc32(b'\x92\x6B\x55') == 0x9CDEA29B
    assert crc32(b'\xFF\xFF\xFF\xFF') == 0xFFFFFFFF


def test_crc32_bzip2():
    crc32_bzip2 = crcengine.new('crc32-bzip2')
    assert crc32_bzip2(b'A') == 0x81B02D8B
    assert crc32_bzip2(b'123456789') == 0xFC891918


def test_tables_crosscheck():
    table1 = crcengine.create_msb_table_individual(_CRC32_POLY, 32)
    table2 = crcengine.create_msb_table(_CRC32_POLY, 32)
    for n, (val1, val2) in enumerate(zip(table1, table2)):
        assert val1 == val2, 'Mismatch for entry {}'.format(n)


def test_crc16_kermit(crc16_kermit):
    assert crc16_kermit(b'123456789') == 0x2189
    # confirm that this does behave as a CRC should this is an LSB-first CRC
    # The CRC value needs to be packed as little endian
    data = b'123456789' + struct.pack('<H', 0x2189)
    assert crc16_kermit.calculate(data) == 0


def test_crc16_xmodem(crc16_xmodem):
    assert crc16_xmodem(b'123456789') == 0x31c3
    # confirm that this does behave as a CRC should, the CRC value needs to
    # be packed as big-endian
    data = b'123456789' + struct.pack('>H', 0x31c3)
    assert crc16_xmodem.calculate(data) == 0


def test_crc16_lsb_autosar(crc16_autosar):
    assert crc16_autosar(b'123456789') == 0x29B1
    # confirm that this does behave as a CRC should this is an LSB-first CRC
    # The CRC value needs to be packed as little endian
    data = b'123456789' + struct.pack('>H', 0x29B1)
    assert crc16_autosar(data) == 0


def test_crc16_autosar_results(crc16_autosar):
    # Reference values from AUTOSAR_SWS_CRCLibrary.pdf 4.4
    assert crc16_autosar(b'\x00\x00\x00\x00') == 0x84C0
    assert crc16_autosar(b'\xF2\x01\x83') == 0xD374
    assert crc16_autosar(b'\x0F\xAA\x00\x55') == 0x2023
    assert crc16_autosar(b'\x00\xFF\x55\x11') == 0xB8F9
    assert crc16_autosar(b'3"U\xAA\xBB\xCC\xDD\xEE\xFF') == 0xF53F
    assert crc16_autosar(b'\x92\x6B\x55') == 0x0745
    assert crc16_autosar(b'\xFF\xFF\xFF\xFF') == 0x1D0F


def test_available_algorithms():
    available = crcengine.algorithms_available()
    assert 'crc32' in available
    assert 'crc16-xmodem' in available
    assert 'crc-womble' not in available


@pytest.mark.parametrize("algorithm_name", crcengine.algorithms_available())
def test_algorithm_checks(algorithm_name):
    """Check the result of every algorithm against its recorded check-word"""
    check_word = crcengine.get_algorithm_params(algorithm_name, True)['check']
    crc_alg = crcengine.new(algorithm_name)
    assert crc_alg(b'123456789') == check_word,\
        'Check CRC mismatch for {}'.format(algorithm_name)
