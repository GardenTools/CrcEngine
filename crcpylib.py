#!/usr/bin/env python
"""
A python library for CRC calculation
"""
# This file is part of crcpylib.
#
# crcpylib is free software: you can redistribute it an d /or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# crcpylib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with crcpylib.  If not, see <https://www.gnu.org/licenses/>.

UINT8_MAX = 255
UINT16_MAX = ((1 << 16) - 1)
UINT32_MAX = ((1 << 32) - 1)


CRC16_CCITT_POLY = 0x1021
CRC32_POLY = 0x04C11DB7


class CrcLsbf:
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
        crc = self._seed
        for byte in data:
            crc = ((crc >> 8) ^
                   self._table[(crc & 0xFF) ^ byte])
            crc &= self._result_mask
        if self._reverse_result:
            # This is a weird corner case where the output is reflected bu the
            # input isn't
            crc = bit_reverse_n(crc, self._width)
        return crc ^ self._xor_out

    def __call__(self, data):
        return self.calculate(data)


class CrcMsbf:
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


class CrcGeneric:
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


class CrcGenericLsbf:
    """
    General purpose CRC calculation using LSB algorithm. Mainly here for
     reference, since the other algorithms cover all useful calculation
      combinations
    """
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


class CrcEngine:
    """Factory for creating CRC calculators"""
    @classmethod
    def create(cls, poly, width, seed, ref_in=True, ref_out=True, name='',
               xor_out=0xFFFFFF):
        """Create a table-driven CRC calculation engine"""
        if ref_in:
            table = cls.create_lsb_table(poly, width)
            algorithm = CrcLsbf(table, width, seed,
                                reverse_result=(ref_in != ref_out),
                                xor_out=xor_out,
                                name=name)
        else:
            table = cls.create_msb_table(poly, width)
            algorithm = CrcMsbf(table, width, seed,
                                reverse_result=ref_out,
                                xor_out=xor_out, name=name)
        return algorithm

    @classmethod
    def create_generic(cls, poly, width, seed, ref_in=True, ref_out=True,
                       name='', xor_out=0xFFFFFF):
        return CrcGeneric(poly, width, seed, ref_in=ref_in, ref_out=ref_out,
                          xor_out=xor_out, name=name)

    @classmethod
    def create_generic_lsbf(cls, poly, width, seed, ref_in=True, ref_out=True,
                            name='', xor_out=0xFFFFFF):
        """Create a CRC calculation engine that uses the Least-significant first
        algorithm, but does not reflect the polynomial. If you use this, reflect
        the polynomial before passing it in"""
        return CrcGenericLsbf(poly, width, seed, ref_in=ref_in, ref_out=ref_out,
                              xor_out=xor_out, name=name)

    @classmethod
    def create_msb_table_individual(cls, poly, width):
        """ Generate a CRC table calculating each entry.
            Mainly for demonstration and test, since calculate_msb_table() is
            much more efficient to calculate
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

    @classmethod
    def create_msb_table(cls, poly, width):
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

    @classmethod
    def create_lsb_table(cls, poly, width):
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
        more = True
        # On iteration we compute index positions 128, 64, 32 ...
        # this can be done with a single application of the polynomial bit test
        # since we know only one bit is set. We re-use the value of index 2n to
        # calculate n
        while more:
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
            more = i > 0
        return table


def bit_reverse_byte(byte):
    """Noddy bit reversal of a byte"""
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


# Table of bit-reversed bits for fast bit reversal, initialised on loading
_REV8BITS = [bit_reverse_byte(n) for n in range(256)]

# Ethernet CRC32
CRC32 = CrcEngine.create(poly=CRC32_POLY, width=32, seed=UINT32_MAX,
                         ref_in=True, ref_out=True, xor_out=UINT32_MAX,
                         name='CRC32')

# BZIP2 CRC32 - like the Ethernet CRC32 but no bit reversal
CRC32_BZIP2 = CrcEngine.create(poly=CRC32_POLY, width=32, seed=UINT32_MAX,
                               ref_in=False, ref_out=False, xor_out=UINT32_MAX,
                               name='CRC32-BZIP2')

# From  KERMIT PROTOCOL MANUAL Sixth Edition 1986
# Three-character 16-bit CRC-CCITT. The CRC calculation treats  the  data  it
# operates  upon  as  a  string  of  bits with the low order bit of the first
# character first and the high order bit of the last character last.  The in-
# itial value of the CRC is taken as 0; the 16-bit CRC is the remainder after
#                                                  16  12  5
# dividing the data bit string by the polynomial X  +X  +X +1 (this  calcula-
# tion  can  actually  be  done  a  character at a time, using a simple table
# lookup algorithm).
# http://www.columbia.edu/kermit/ftp/e/kproto.doc
CRC16_KERMIT = CrcEngine.create(name='CRC16-KERMIT', poly=CRC16_CCITT_POLY,
                                width=16, seed=0, ref_in=True, ref_out=True,
                                xor_out=0)
# XMODEM CRC, see ITU-T V.41 Code-Independent Error-Control System 1988, 1993
# https://www.itu.int/rec/T-REC-V.41/en
CRC16_XMODEM = CrcEngine.create(name='CRC16-XMODEM', poly=CRC16_CCITT_POLY,
                                width=16, seed=0, ref_in=False, ref_out=False,
                                xor_out=0)

# AKA CRC16-CCITT-FALSE
# Reference https://www.autosar.org/fileadmin/Releases_TEMP/Classic_Platform_4.4.0/Libraries.zip
CRC16_AUTOSAR = CrcEngine.create(name='CRC16-AUTOSAR', poly=CRC16_CCITT_POLY,
                                 width=16, seed=UINT16_MAX, ref_in=False,
                                 ref_out=False, xor_out=0)
