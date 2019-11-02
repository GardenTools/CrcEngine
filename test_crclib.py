import unittest
import pytest
from crcpylib import *


def test_reverse_poly():
    assert bit_reverse_n(0, 32) == 0
    assert bit_reverse_n(1, 8) == 0x80
    assert bit_reverse_n(1, 16) == 0x8000
    assert bit_reverse_n(1, 17) == 0x10000
    assert bit_reverse_n(1, 32) == 0x80000000
    assert bit_reverse_n(CRC32_POLY, 32) == 0xEDB88320


@pytest.mark.skip()
def test_crc32_base():
    assert crc32(b'123456789') == 0xCBF43926
    assert crc32(b'A') == 0xD3D99E8B


def test_crc32_msb():
    crc32.set_printing(True)
    assert crc32.calculate_msb(b'A') == 0xD3D99E8B
    crc32.set_printing(False)
    assert crc32.calculate_msb(b'123456789') == 0xCBF43926


def test_crc32_lsb():
    assert crc32.calculate_lsb(b'A') == 0xD3D99E8B
    assert crc32.calculate_lsb(b'123456789') == 0xCBF43926


def test_generate_crc32_table_individual():
    table = crc32.calculate_msb_table_individual()
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_generate_crc32_msb_table():
    table = crc32.calculate_msb_table()
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[2] == 0x09823B6E
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_generate_crc32_msb_table_individual():
    table = crc32.calculate_msb_table_individual()
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[2] == 0x09823B6E
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_tables_crosscheck():
    table1 = crc32.calculate_msb_table_individual()
    table2 = crc32.calculate_msb_table()
    for n, (v1, v2) in enumerate(zip(table1, table2)):
        assert v1 == v2, 'Mismatch for entry {}'.format(n)
