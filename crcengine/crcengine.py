#!/usr/bin/env python
"""
A python library for CRC calculation
"""
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
from __future__ import generator_stop

import os
import pathlib
import textwrap

from ._version import __version__ as crcengine_version

_U8_MAX = 255
_U16_MAX = ((1 << 16) - 1)
_U32_MAX = ((1 << 32) - 1)
# Some of these polynomials are used for many algorithms, so they are collected
# here
_CRC16_CCITT_POLY = 0x1021
_CRC32_POLY = 0x04C11DB7

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


class _CrcLsbf:
    """Least-significant-bit first calculation of a CRC. Implies a ref_in
    calculations was specified with new data being shifted in from the MSB end
     of the calculation register"""
    def __init__(self, table, width, seed, xor_out=0, reverse_result=False,
                 name=''):
        self._table = table
        self._seed = seed
        self._width = width
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._reverse_result = reverse_result
        self.name = name

    def calculate(self, data):
        """ Perform CRC calculation on data

        :param data: a string of bytes
        :return: integer calculated CRC
        """
        crc = self._seed
        for byte in data:
            crc = ((crc >> 8) ^
                   self._table[(crc & 0xFF) ^ byte])
            crc &= self._result_mask
        if self._reverse_result:
            # This is a weird corner case where the output is reflected but the
            # input isn't
            crc = bit_reverse_n(crc, self._width)
        return crc ^ self._xor_out

    def __call__(self, data):
        """calculate CRC"""
        return self.calculate(data)


class _CrcMsbf:
    """Most-significant-bit-first table-driven CRC calculation"""
    def __init__(self, table, width, seed, xor_out=0, reverse_result=False,
                 name=''):
        self._table = table
        self._seed = seed
        self._width = width
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._msb_lshift = width - 8
        self._reverse_result = reverse_result
        self.name = name

    def calculate(self, data):
        """ Calculate a CRC on data

        :param data: bytes string
        :return: calculated CRC
        """
        remainder = self._seed
        for value in data:
            remainder = ((remainder << 8) ^
                         self._table[(remainder >> self._msb_lshift) ^ value])
            remainder &= self._result_mask
        if self._reverse_result:
            remainder = bit_reverse_n(remainder, self._width)
        return remainder ^ self._xor_out

    def __call__(self, data):
        return self.calculate(data)


class _CrcGeneric:
    """Generic most-significant-bit-first table-driven CRC calculation"""
    def __init__(self, poly, width, seed, ref_in, ref_out, xor_out=0,
                 name=''):
        self._poly = poly
        self._width = width
        self._seed = seed
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._msbit = 1 << (width - 1)
        self._msb_lshift = width - 8
        self._ref_in = ref_in
        self._ref_out = ref_out
        self.name = name

    def calculate(self, data, seed=None):
        """ Calculate CRC of data

        :param data: byte string
        :param seed: optional seed value
        :return: calculated CRC
        """
        if seed:
            crc = seed
        else:
            crc = self._seed
        for byte in data:
            if self._ref_in:
                reflect_byte = _REV8BITS[byte]
                byte = reflect_byte
            crc ^= (byte << self._msb_lshift)
            for _ in range(8):
                if crc & self._msbit:
                    crc = (crc << 1) ^ self._poly
                else:
                    crc <<= 1
            crc &= self._result_mask
        if self._ref_out:
            crc = bit_reverse_n(crc, self._width)
        return crc ^ self._xor_out

    def __call__(self, data):
        return self.calculate(data)


class _CrcGenericLsbf:
    """
    General purpose CRC calculation using LSB algorithm. Mainly here for
     reference, since the other algorithms cover all useful calculation
      combinations
    """
    def __init__(self, poly, width, seed, ref_in, ref_out, xor_out=0, name=''):
        self._poly = poly
        self._width = width
        self._seed = seed
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._msbit = 1 << (width - 1)
        self._msb_lshift = width - 8
        self._ref_in = ref_in
        self._ref_out = ref_out
        self.name = name

    def calculate(self, data, seed=None):
        """ Calculate a CRC on data

        :param data: bytes string whose CRC will be calculated
        :param seed: Optional seed
        :return: calculated CRC
        """
        if seed:
            crc = seed
        else:
            crc = self._seed
        if self._ref_in:
            poly = bit_reverse_n(self._poly, self._width)
        else:
            poly = self._poly
        for byte in data:
            if self._ref_in:
                byte = _REV8BITS[byte]
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
            crc &= self._result_mask
        if self._ref_out:
            crc = bit_reverse_n(crc, self._width)
        return crc ^ self._xor_out

    def __call__(self, data):
        """Calculate CRC for data"""
        return self.calculate(data)


def new(name):
    """Create a new CRC calculation instance"""
    params = get_algorithm_params(name.lower())
    # the check field is not part of the definition, remove it before
    # creating the algorithm
    return create(**params)


class AlgorithmNotFoundError(Exception):
    pass


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
        import sys
        tb = sys.exc_info()[2]
        raise AlgorithmNotFoundError(name) from e
    final = None if include_check else -1
    param_dict = dict(zip(_FIELDS[:final], raw_params[:final]))
    param_dict['name'] = name
    return param_dict


def algorithms_available():
    """Obtain a list of available named CRC algorithms"""
    return _ALGORITHMS.keys()


def create(poly, width, seed, ref_in=True, ref_out=True, name='',
           xor_out=0xFFFFFF):
    """ Create a table-driven CRC calculation engine

    :param poly: polynomial
    :param width: polynomial width in bits
    :param seed: seed value for the CRC calculation to use
    :param ref_in:  reflect input bits
    :param ref_out: reflect output bits
    :param name: associate a name with this algorithm
    :param xor_out:  exclusive-or the output with this value
    :return:
    """
    if ref_in:
        table = create_lsb_table(poly, width)
        algorithm = _CrcLsbf(table, width, seed,
                             reverse_result=(ref_in != ref_out),
                             xor_out=xor_out,
                             name=name)
    else:
        table = create_msb_table(poly, width)
        algorithm = _CrcMsbf(table, width, seed,
                             reverse_result=ref_out,
                             xor_out=xor_out, name=name)
    return algorithm


def create_generic(poly, width, seed, ref_in=True, ref_out=True,
                   name='', xor_out=0xFFFFFF):
    """ Create generic non-table-driven CRC calculator

    :param poly: Polynomial
    :param width: calculator width in bits e.g. 32
    :param seed: calculation seed value
    :param ref_in: reflect incoming bits
    :param ref_out: reflect result bits
    :param name: name to assign to calculator
    :param xor_out: pattern to XOR into result
    :return: A CRC calculation engine
    """
    return _CrcGeneric(poly, width, seed, ref_in=ref_in, ref_out=ref_out,
                       xor_out=xor_out, name=name)


def create_generic_lsbf(poly, width, seed, ref_in=True, ref_out=True,
                        name='', xor_out=0xFFFFFF):
    """Create a CRC calculation engine that uses the Least-significant first
    algorithm, but does not reflect the polynomial. If you use this, reflect
    the polynomial before passing it in"""
    return _CrcGenericLsbf(poly, width, seed, ref_in=ref_in, ref_out=ref_out,
                           xor_out=xor_out, name=name)


def create_msb_table_individual(poly, width):
    """ Generate a CRC table calculating each entry.
        Mainly for demonstration and test, since calculate_msb_table() is
        much more efficient at calculating the same information
    :return: Generated table
    """
    msb_lshift = width - 8
    ms_bit = 1 << (width - 1)
    result_mask = (1 << width) - 1
    table = 256 * [0]
    for n in range(1, 256):
        crc = n << msb_lshift
        for _ in range(8):
            if crc & ms_bit:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
        table[n] = crc & result_mask
    return table


def create_msb_table(poly, width):
    """ Calculate a CRC lookup table for the selected algorithm definition
    :return: list of CRC values
    """
    ms_bit = 1 << (width - 1)
    result_mask = (1 << width) - 1
    # Preallocate entries to 0
    table = 256 * [0]
    # this is essentially the '1' shifted left by the number of
    # bits necessary for it to reach the msbit of the remainder value
    crc = ms_bit
    # i is the index of the table that is being computed this loop
    i = 1
    while i <= 128:
        # Each (1<<n) must have the polynomial applied to it n+1 times
        # since 1 must be shifted left 7 times before a non-zero bit is in
        # the msb, there are no more shifts to be done
        # 2 requires 6 shifts for a non-zero bit in the msbit, so the msbit
        # test (and conditional polynomial xor) is applied once more
        # 4 requires 5 shifts for a non-zero bit in the msbit, so the
        # the msb test is applied three times.
        # We take advantage of this property by reusing the result for n
        # in the calculation of the result for 2n
        if crc & ms_bit:
            crc = (crc << 1) ^ poly
        else:
            crc <<= 1
        crc &= result_mask
        # because all operations are xors the following holds:
        # table[i ^ j] == table[i] ^ table[j]
        # The result for n can be combined with all the results for 0..(n-1)
        # to determine the (n+1)..(2n-1) th entries without any further
        # calculation
        # since i is a power of 2 and always larger than j
        # i + j == i ^ j
        for j in range(0, i):
            table[i + j] = table[j] ^ crc
        i <<= 1
    return table


def create_lsb_table(poly, width):
    """ Calculate a CRC lookup table for the selected algorithm definition
    producing a table that can be used for the lsbit algorithm

    :return: table of reflected
    """
    table = 256 * [0]
    crc = 1
    # i is the index of the table that is being computed this loop
    # the lsb table contains an implicit reflection of the data byte so
    # '1' is a reflected 128
    i = 0x80
    poly = bit_reverse_n(poly, width)
    # On iteration we compute index positions 128, 64, 32 ...
    # this can be done with a single application of the polynomial bit test
    # since we know only one bit is set. We re-use the value of index 2n to
    # calculate n
    while i > 0:
        # Apply the test for lsb set and the (reflected) polynomial
        # to bits shifting in from the left
        # so the first tests 0x80 >> 7, the second iteration re-uses this to
        # represent application 0x40 >> 6 and then applies the test again
        # for the remaining shift etc.
        if crc & 1:
            crc = (crc >> 1) ^ poly
        else:
            crc >>= 1
        # Having computed the value of a power of 2 entry, we can combine
        # it with the values from the (larger) power of 2 entries that have
        # been already calculated, this can be done because
        #  table[i + j] == table[i] ^ table[j]
        for j in range(0, 256, 2 * i):
            table[i + j] = crc ^ table[j]
        i >>= 1
    return table


def generate(crc_params, output_dir='out/'):
    if isinstance(crc_params, str):
        # crc_params is an algorithm name, so replace it with the algorithm
        # parameters
        crc_params = get_algorithm_params(crc_params)
    # only support consistent combinations for now
    assert crc_params['ref_in'] == crc_params['ref_out'], \
        'Code generation only supported with ref_in==ref_out'
    if crc_params['ref_in']:
        table = create_lsb_table(crc_params['poly'], crc_params['width'])
    else:
        table = create_msb_table(crc_params['poly'], crc_params['width'])

    width =  crc_params['width']
    datatype_bits = (64 if width > 32 else 32 if width > 16 else
                     16 if width > 8 else 8)

    value_rows = _generate_table_text(table, value_width=datatype_bits//4)
    from jinja2 import Environment, FileSystemLoader
    package_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(package_dir, 'templates')

    env = Environment(loader=FileSystemLoader(templates_dir),
                      trim_blocks=True)
    c_template = env.get_template('c_template')
    h_template = env.get_template('h_template')

    crc_id = crc_params['name'].replace('-', '_')
    c_output_filename = f'{crc_id}.c'
    h_output_filename = f'{crc_id}.h'

    seed_parameter = False
    template_params = {
        'after_table': '',
        'crc_datatype': f'uint{datatype_bits}_t',
        'before_table': '',
        'byte_type': 'uint8_t',
        'function_name': crc_id,
        'table_name': f'{crc_id}_table',
        'value_rows': value_rows,
        'reflect': crc_params['ref_in'],
        'includes': ['#include <stdint.h>'],
        'c_includes': [],
        'preamble': f'/* Auto-generated by CrcEngine {crcengine_version},'
                    ' do not hand edit */',
        'header_macro': '{}_H'.format(crc_id.upper()),
        'header_file': h_output_filename,
        'msb_shift': crc_params['width'] - 8,
    }
    if not seed_parameter:
        template_params['seed'] = '0x{:0x}u'.format(crc_params['seed'])

    if crc_params['xor_out']:
        template_params['xor_out'] = '0x{:0x}u'.format(crc_params['xor_out'])

    _ensure_directory(output_dir)
    c_output = c_template.render(template_params)
    c_file_path = os.path.join(output_dir, c_output_filename)
    with open(c_file_path, 'w') as f:
        f.write(c_output)

    h_output = h_template.render(template_params)
    h_file_path = os.path.join(output_dir, h_output_filename)
    with open(h_file_path, 'w') as f:
        f.write(h_output)


def _ensure_directory(output_dir):
    newpath = pathlib.Path(output_dir)
    newpath.mkdir(parents=True, exist_ok=True)


def _generate_table_text(table, max_width=79, value_width=8, indent_width=4,
                         number_prefix='0x', number_suffix='u'):
    """ Generate the text values for a CRC lookup table

    :param table:
    :return: list of rows of table entry strings
    """
    spacer = ', '
    indent = indent_width * ' '
    elements = [f'{number_prefix}{value:0{value_width}x}{number_suffix}'
                for value in table]
    txt = spacer.join(elements)
    wrapper = textwrap.TextWrapper(width=max_width, initial_indent=indent,
                                   subsequent_indent=indent,
                                   break_long_words=False)
    wt = wrapper.wrap(txt)
    return wt


def bit_reverse_byte(byte):
    """Bit-bashing reversal of a byte"""
    result = 0
    for i in range(8):
        if byte & (1 << i):
            result |= 1 << (7 - i)
    return result & 0xFF


def bit_reverse_n(value, num_bits):
    """ Mirror the bits in an integer

    :param value: the integer to reverse
    :param num_bits: the number of bits  to reverse
    :return: mirrored value
    """
    # This left shift will introduce zeroes in the least-significant bits, which
    # will be ignored 0 ms bits once we bit reverse
    value <<= (8 - num_bits) & 7
    num_bytes = (num_bits + 7) >> 3
    result = 0
    for _ in range(num_bytes):
        result <<= 8
        result |= _REV8BITS[value & 0xFF]
        value >>= 8
    return result


def get_maximum_value(nbits):
    """Convenience function returning largest unsigned integer for a given
     number of bits"""
    return (1 << nbits) - 1


# Table of bit-reversed bits for fast bit reversal, initialised on loading
_REV8BITS = [bit_reverse_byte(n) for n in range(256)]
