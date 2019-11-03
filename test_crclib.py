import struct
from crcpylib import *


def test_reverse_poly():
    assert bit_reverse_n(0, 32) == 0
    assert bit_reverse_n(1, 8) == 0x80
    assert bit_reverse_n(1, 16) == 0x8000
    assert bit_reverse_n(1, 17) == 0x10000
    assert bit_reverse_n(1, 32) == 0x80000000
    assert bit_reverse_n(CRC32_POLY, 32) == 0xEDB88320


def test_crc32_generic():
    """Test the generic calculation engine with a CRC32"""
    crc32_generic = CrcEngine.create_generic(CRC32_POLY, 32, UINT32_MAX,
                                             ref_in=True, ref_out=True,
                                             xor_out=UINT32_MAX)
    assert crc32_generic(b'123456789') == 0xCBF43926
    assert crc32_generic(b'A') == 0xD3D99E8B


def test_crc32_generic_lsb():
    poly = bit_reverse_n(CRC32_POLY, 32)
    assert poly == 0xEDB88320
    crc32_generic = CrcEngine.create_generic_lsbf(
        poly, 32, UINT32_MAX, ref_in=False, ref_out=False, xor_out=UINT32_MAX)
    assert crc32_generic.calculate(b'A') == 0xD3D99E8B
    assert crc32_generic.calculate(b'123456789') == 0xCBF43926


def test_generate_crc32_table_individual():
    table = CrcEngine.create_msb_table_individual(CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_generate_crc32_msb_table():
    table = CrcEngine.create_msb_table(CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[2] == 0x09823B6E
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_generate_crc32_lsb_table():
    table = CrcEngine.create_lsb_table(CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x77073096
    assert table[2] == 0xEE0E612C
    assert table[7] == 0x9E6495A3
    assert table[255] == 0x2D02EF8D


def test_generate_crc32_msb_table_individual():
    table = CrcEngine.create_msb_table_individual(CRC32_POLY, 32)
    assert table[0] == 0
    # the table entry of 1 should always be the polynomial
    assert table[1] == 0x04C11DB7
    assert table[2] == 0x09823B6E
    assert table[7] == 0x1E475005
    assert table[255] == 0xB1F740B4


def test_crc32_table_driven():
    assert CRC32(b'A') == 0xD3D99E8B
    assert CRC32(b'123456789') == 0xCBF43926
    # The values below are from the AUTOSAR spec.
    assert CRC32(b'\x00\x00\x00\x00') == 0x2144DF1C
    assert CRC32(b'\x0F\xAA\x00\x55') == 0xB6C9B287
    assert CRC32(b'\x00\xFF\x55\x11') == 0x32A06212
    assert CRC32(b'\x92\x6B\x55') == 0x9CDEA29B
    assert CRC32(b'\xFF\xFF\xFF\xFF') == 0xFFFFFFFF


def test_crc32_bzip2():
    assert CRC32_BZIP2(b'A') == 0x81B02D8B
    assert CRC32_BZIP2(b'123456789') == 0xFC891918


def test_tables_crosscheck():
    table1 = CrcEngine.create_msb_table_individual(CRC32_POLY, 32)
    table2 = CrcEngine.create_msb_table(CRC32_POLY, 32)
    for n, (val1, val2) in enumerate(zip(table1, table2)):
        assert val1 == val2, 'Mismatch for entry {}'.format(n)


def test_crc16_kermit():
    assert CRC16_KERMIT(b'123456789') == 0x2189
    # confirm that this does behave as a CRC should this is an LSB-first CRC
    # The CRC value needs to be packed as little endian
    data = b'123456789' + struct.pack('<H', 0x2189)
    assert CRC16_KERMIT.calculate(data) == 0


def test_crc16_xmodem():
    assert CRC16_XMODEM(b'123456789') == 0x31c3
    # confirm that this does behave as a CRC should, the CRC value needs to
    # be packed as big-endian
    data = b'123456789' + struct.pack('>H', 0x31c3)
    assert CRC16_XMODEM.calculate(data) == 0


def test_crc16_lsb_autosar():
    assert CRC16_AUTOSAR(b'123456789') == 0x29B1
    # confirm that this does behave as a CRC should this is an LSB-first CRC
    # The CRC value needs to be packed as little endian
    data = b'123456789' + struct.pack('>H', 0x29B1)
    assert CRC16_AUTOSAR(data) == 0


def test_crc16_autosar_results():
    # Reference values from AUTOSAR_SWS_CRCLibrary.pdf 4.4
    assert CRC16_AUTOSAR(b'\x00\x00\x00\x00') == 0x84C0
    assert CRC16_AUTOSAR(b'\xF2\x01\x83') == 0xD374
    assert CRC16_AUTOSAR(b'\x0F\xAA\x00\x55') == 0x2023
    assert CRC16_AUTOSAR(b'\x00\xFF\x55\x11') == 0xB8F9
    assert CRC16_AUTOSAR(b'3"U\xAA\xBB\xCC\xDD\xEE\xFF') == 0xF53F
    assert CRC16_AUTOSAR(b'\x92\x6B\x55') == 0x0745
    assert CRC16_AUTOSAR(b'\xFF\xFF\xFF\xFF') == 0x1D0F
