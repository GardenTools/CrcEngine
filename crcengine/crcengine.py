#!/usr/bin/env python
"""
A python library for CRC calculation

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

from .algorithms import get_algorithm_params


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
    # The algorithm starts from this value because in an lsb-first VRV the poly
    #  will only be applied to it once, so we can compute it without iteration
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


# Table of bit-reversed bytes, initialised on loading
_REV8BITS = [bit_reverse_byte(n) for n in range(256)]
