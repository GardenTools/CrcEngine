#!/usr/bin/env python
"""
This file is part of CrcEngine, a python library for CRC calculation

Copyright 2019 Garden Tools software

crcengine is free software: you can redistribute it an d /or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

crcengine is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with crcengine.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import generator_stop

# Some of these polynomials are used for many algorithms, so they are collected
# here
_CRC16_CCITT_POLY = 0x1021
_CRC32_POLY = 0x04C11DB7

_U8_MAX = 255
_U16_MAX = ((1 << 16) - 1)
_U32_MAX = ((1 << 32) - 1)

_FIELDS = ('poly', 'width', 'seed', 'ref_in', 'ref_out', 'xor_out', 'check')

_ALGORITHMS = {
    # =========================  8-bit ========================================
    'crc8': (0xD5, 8, 0, False, False, 0, 0xbc),
    'crc8-autosar': (0x2f, 8, _U8_MAX, False, False, _U8_MAX, 0xdf),
    'crc8-bluetooth': (0xa7, 8, 0, True, True, 0, 0x26),
    # ITU I.432.1 https://www.itu.int/rec/T-REC-I.432.1-199902-I/en
    'crc8-ccitt': (0x07, 8, 0, False, False, 0x55, 0xa1),
    # https://www.etsi.org/deliver/etsi_ts/100900_100999/100909/08.09.00_60/ts_100909v080900p.pdf
    'crc8-gsm-b': (0x49, 8, 0, False, False, _U8_MAX, 0x94),
    'crc8-sae-j1850': (0x1d, 8, _U8_MAX, False, False, _U8_MAX, 0x4b),
    # ========================= 15-bit ========================================
    'crc15-can': (0x4599, 15, 0, False, False, 0, 0x059e),
    # ========================= 16-bit ========================================
    # From  KERMIT PROTOCOL MANUAL Sixth Edition 1986 Three-character 16-bit
    # CRC-CCITT. The CRC calculation treats  the  data  it operates  upon  as
    # a  string  of  bits with the low order bit of the first character first
    # and the high order bit of the last character last.  The initial value of
    # the CRC is taken as 0; the 16-bit CRC is the remainder after 16  12  5
    # dividing the data bit string by the polynomial X  +X  +X +1 (this
    # calculation  can  actually  be  done  a  character at a time, using a
    # simple table lookup algorithm).
    # http://www.columbia.edu/kermit/ftp/e/kproto.doc
    # The Kermit protocol describes the algorithm applied to bits down the wire
    # and UARTs transmit least-significant-bit first
    'crc16-kermit': (_CRC16_CCITT_POLY, 16, 0, True, True, 0, 0x2189),
    'crc16-ccitt-true': (_CRC16_CCITT_POLY, 16, 0, True, True, 0, 0x2189),
    # https://www.itu.int/rec/T-REC-V.41/en
    'crc16-xmodem': (_CRC16_CCITT_POLY, 16, 0, False, False, 0, 0x31c3),
    # AKA CRC16-CCITT-FALSE
    # Reference https://www.autosar.org/fileadmin/Releases_TEMP/Classic_Platform_4.4.0/Libraries.zip
    'crc16-autosar': (_CRC16_CCITT_POLY, 16, _U16_MAX, False, False, 0, 0x29b1),
    #  crc16-ccitt-false is an alias of crc16-autosar
    'crc16-ccitt-false': (_CRC16_CCITT_POLY, 16, _U16_MAX, False, False, 0, 0x29b1),
    'crc16-cdma2000': (0xC867, 16, _U16_MAX, False, False, 0, 0x4c06),
    # Algorithms normally called "CRC16"
    'crc16-ibm': (0x8005, 16, 0, True, True, 0, 0xbb3d),
    'crc16-modbus': (0x8005, 16, _U16_MAX, True, True, 0, 0x4b37),
    'crc16-profibus': (0x1dcf, 16, _U16_MAX, False, False, _U16_MAX, 0xa819),
    # ========================= 24-bit ========================================
    'crc24-flexray16-a': (0x5d6dcb, 24, 0xfedcba, False, False, 0, 0x7979bd),
    'crc24-flexray16-b': (0x5d6dcb, 24, 0xabcdef, False, False, 0, 0x1f23b8),
    # ========================= 32-bit ========================================
    # Ethernet CRC32
    # https://www.ecma-international.org/publications/files/ECMA-ST/Ecma-130.pdf
    'crc32': (_CRC32_POLY, 32, _U32_MAX, True, True, _U32_MAX, 0xCBF43926),
    # CRC32 as implemented in BZIP, same polynomial but no reflection
    'crc32-bzip2': (_CRC32_POLY, 32, _U32_MAX, False, False, _U32_MAX, 0xfc891918),
    # Castagnoli CRC used in iSCSi SSE4, ext4
    'crc32-c': (0x1edc6f41, 32, _U32_MAX, True, True, _U32_MAX, 0xe3069283),
    # ========================= 64-bit ========================================
    'crc64-ecma': (0x42F0E1EBA9EA3693, 64, 0, False, False, 0, 0x6c40df5f0b497347),
}


class AlgorithmNotFoundError(Exception):
    """Exception raised when an algorithm is requested that doesn't exist in
     the table"""


def get_algorithm_params(name, include_check=False):
    """ Obtain the parameters for a named CRC algorithm
    Optionally the 'check' field can be included, this field is not part of the
    definition of the algorithm and so is omitted by default

    :param name: Name of algorithm (lowercase)
    :param include_check: if True include the 'check' field in the output
    :return: dict of algorithm parameters
    """
    try:
        raw_params = _ALGORITHMS[name]
    except KeyError as e:
        raise AlgorithmNotFoundError(name) from e
    final = None if include_check else -1
    param_dict = dict(zip(_FIELDS[:final], raw_params[:final]))
    param_dict['name'] = name
    return param_dict


def algorithms_available():
    """Obtain a list of available named CRC algorithms"""
    return _ALGORITHMS.keys()
