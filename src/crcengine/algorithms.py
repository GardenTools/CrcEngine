#!/usr/bin/env python
"""CRC Algorithm parametrisation
"""

# This file is part of CrcEngine, a python library for CRC calculation
#
# Copyright 2021 Garden Tools software
#
# crcengine is free software: you can redistribute it and/or modify
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

from __future__ import generator_stop
from collections import namedtuple as _namedtuple
from typing import Iterable
# Some of these polynomials are used for many algorithms, so they are collected
# here
_CRC16_CCITT_POLY = 0x1021
_CRC32_POLY = 0x04C11DB7

_U8_MAX = 255
_U16_MAX = (1 << 16) - 1
_U32_MAX = (1 << 32) - 1

_FIELDS = ("poly", "width", "seed", "ref_in", "ref_out", "xor_out", "check")

CrcParams = _namedtuple("CrcParams", (
    "polynomial", "width", "seed", "reflect_in", "reflect_out", "xor_out"
))

# All algorithms specified in this table have their polynomials specified with
# the high order coefficients in the most significant bit and the low order in
# the least significant bits.
_ALGORITHMS = {
    # pylint: disable=line-too-long
    # ======================== sub-byte =======================================
    # Token CRC in USB https://web.archive.org/web/20160326215031/http://www.usb.org/developers/whitepapers/crcdes.pdf
    "crc5-usb": (0x05, 5, 0x1f, True, True,  0x1f,  0x19),
    # =========================  8-bit ========================================
    "crc8": (0xD5, 8, 0, False, False, 0, 0xBC),
    "crc8-autosar": (0x2F, 8, _U8_MAX, False, False, _U8_MAX, 0xDF),
    "crc8-bluetooth": (0xA7, 8, 0, True, True, 0, 0x26),
    # ITU I.432.1 https://www.itu.int/rec/T-REC-I.432.1-199902-I/en
    "crc8-ccitt": (0x07, 8, 0, False, False, 0x55, 0xA1),
    # https://www.etsi.org/deliver/etsi_ts/100900_100999/100909/08.09.00_60/ts_100909v080900p.pdf
    "crc8-gsm-b": (0x49, 8, 0, False, False, _U8_MAX, 0x94),
    "crc8-sae-j1850": (0x1D, 8, _U8_MAX, False, False, _U8_MAX, 0x4B),
    # ========================= 15-bit ========================================
    "crc15-can": (0x4599, 15, 0, False, False, 0, 0x059E),
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
    "crc16-kermit": (_CRC16_CCITT_POLY, 16, 0, True, True, 0, 0x2189),
    "crc16-ccitt-true": (_CRC16_CCITT_POLY, 16, 0, True, True, 0, 0x2189),
    # https://www.itu.int/rec/T-REC-V.41/en
    "crc16-xmodem": (_CRC16_CCITT_POLY, 16, 0, False, False, 0, 0x31C3),
    # AKA CRC16-CCITT-FALSE
    # Reference https://www.autosar.org/fileadmin/Releases_TEMP/Classic_Platform_4.4.0/Libraries.zip
    "crc16-autosar": (_CRC16_CCITT_POLY, 16, _U16_MAX, False, False, 0, 0x29B1),
    #  crc16-ccitt-false is an alias of crc16-autosar
    "crc16-ccitt-false": (_CRC16_CCITT_POLY, 16, _U16_MAX, False, False, 0, 0x29B1),
    "crc16-cdma2000": (0xC867, 16, _U16_MAX, False, False, 0, 0x4C06),
    # Algorithms normally called "CRC16"
    "crc16-ibm": (0x8005, 16, 0, True, True, 0, 0xBB3D),
    "crc16-modbus": (0x8005, 16, _U16_MAX, True, True, 0, 0x4B37),
    "crc16-profibus": (0x1DCF, 16, _U16_MAX, False, False, _U16_MAX, 0xA819),
    # ========================= 24-bit ========================================
    "crc24-flexray16-a": (0x5D6DCB, 24, 0xFEDCBA, False, False, 0, 0x7979BD),
    "crc24-flexray16-b": (0x5D6DCB, 24, 0xABCDEF, False, False, 0, 0x1F23B8),
    # ========================= 32-bit ========================================
    # Ethernet CRC32
    # https://www.ecma-international.org/publications/files/ECMA-ST/Ecma-130.pdf
    "crc32": (_CRC32_POLY, 32, _U32_MAX, True, True, _U32_MAX, 0xCBF43926),
    # CRC32 as implemented in BZIP, same polynomial but no reflection
    "crc32-bzip2": (_CRC32_POLY, 32, _U32_MAX, False, False, _U32_MAX, 0xFC891918),
    # Castagnoli CRC used in iSCSi SSE4, ext4
    "crc32-c": (0x1EDC6F41, 32, _U32_MAX, True, True, _U32_MAX, 0xE3069283),
    # ========================= 64-bit ========================================
    "crc64-ecma": (0x42F0E1EBA9EA3693, 64, 0, False, False, 0, 0x6C40DF5F0B497347),
}

_registered_algorithms = {}


class AlgorithmNotFoundError(Exception):
    """Exception raised when an unrecognized algorithm is requested.
    """


def get_algorithm_params(name: str, include_check=False):
    """Obtain the parameters for a named CRC algorithm
    Optionally the 'check' field can be included, this field is not part of the
    definition of the algorithm and so is omitted by default

    :param name: Name of algorithm (lowercase)
    :param include_check: if True include the 'check' field in the output
    :return: dict of algorithm parameters
    :raises: AlgorithmNotFoundError if algorithm with `name` cannot be found
    """
    raw_params = _lookup_named_params(name)
    final = None if include_check else -1
    param_dict = dict(zip(_FIELDS[:final], raw_params[:final]))
    param_dict["name"] = name
    return param_dict


def _lookup_named_params(name: str) -> dict:
    """Look up the defined raw parameters for algorithm `name`
    """
    try:
        raw_params = _ALGORITHMS[name]
    except KeyError:
        try:
            raw_params = _registered_algorithms[name]
        except KeyError as excep:
            raise AlgorithmNotFoundError(name) from excep
    return raw_params


def lookup_params(name: str) -> CrcParams:
    """Look up CRC parameters given an algorithm name.
    A list of algorithms can be obtained using algorithms_available()

    :param name: name of CRC algorithm
    :raises AlgorithmNotFoundError: if algorithm `name` cannot be found
    """
    raw_params = _lookup_named_params(name)
    return CrcParams(*raw_params[:6])


def params_from_dict(params: dict) -> CrcParams:
    """Turn a dict of CRC parameters into a CrcParams

    :param params: dictionary of parameters as returned by get_algorithm_params
    :return: corresponding CrcParams namedtuple
    """
    return CrcParams(
        polynomial=params["poly"],
        width=params["width"],
        seed=params["seed"],
        reflect_in=params["ref_in"],
        reflect_out=params["ref_out"],
        xor_out=params["xor_out"],
    )


def algorithms_available() -> Iterable[str]:
    """Obtain an iterable of available named CRC algorithms"""
    yield from _ALGORITHMS.keys()
    yield from _registered_algorithms.keys()


def register_algorithm(name: str, polynomial: int, width: int, seed: int, reflect_in: bool,
                       reflect_out: bool,  xor_out: int, check: int = None) -> None:
    """Register a CRC algorithm with custom parameters"""
    poly_mask = (1 << width) - 1
    _registered_algorithms[name] = (
        polynomial & poly_mask,
        width,
        seed & poly_mask,
        reflect_in,
        reflect_out,
        xor_out & poly_mask,
        check,
    )


def unregister_algorithm(name: str) -> None:
    """ Remove an algorithm registration"""
    try:
        del _registered_algorithms[name]
    except KeyError as excep:
        raise AlgorithmNotFoundError from excep
