#!/usr/bin/env python
"""
Implementation of CRC calculation in pure python
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

from typing import Iterable

from .algorithms import CrcParams, lookup_params

_BYTEBITS = 8
_DEFAULT_ENGINE = "table"


class _ReflectedTableCrc:
    """Least-significant-bit first calculation of a CRC. Implies a ref_in
    calculations was specified with new data being shifted in from the MSB end
    of the calculation register.

    The seed parameter is still specified with high-order polynomial elements
    in the most significant bit, which means this is not a "pure" LSB-first
    CRC
    """

    def __init__(self, table, width, seed, xor_out=0, reverse_result=False, name=""):
        """Initialize a table-based CRC instead of a specified polynomial,
        the information comes from a precomputed table of values


        :param table: 256 entry lookup-table for calculation
        :param width: width in bits of CRC polynomial
        :param seed: initial seed for calculation
        :param xor_out:
        :param reverse_result: reflect the bits of the result. Note that
                               although this is the same action as reflect_out
                               this is considered logically distinct since the
                               LSBit-first algorithm implements the practical
                               effect of `reflect_out` by default
        :param name:
        """
        self._table = table
        self._default_seed = seed
        self._width = width
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._reverse_result = reverse_result
        self.name = name

    def calculate(self, data: bytes):
        """Perform CRC calculation on data

        :param data: a string of bytes
        :return: integer calculated CRC
        """
        # For the parameters to make sense in the normal usage, the seed has to
        # be reflected here because this algorithm corresponds to a reflection
        # of the input data, which is implemented by a reflection of the lookup
        # table for performance improvement i.e. all the intermediate CRC values
        # are reflected so the same has to be done for the seed
        crc = bit_reverse_n(self._default_seed, self._width)
        for byte in data:
            crc = (crc >> 8) ^ self._table[(crc & 0xFF) ^ byte]
            crc &= self._result_mask
        if self._reverse_result:
            # This is a weird corner case where the output is reflected but the
            # input isn't
            crc = bit_reverse_n(crc, self._width)
        return crc ^ self._xor_out

    def __call__(self, data):
        """calculate CRC"""
        return self.calculate(data)


class _CrcMsbfTable:
    """Most-significant-bit-first table-driven CRC calculation"""

    def __init__(self, table, width, seed, xor_out=0, reverse_result=False, name=""):
        self._table = table
        self._seed = seed
        self._width = width
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._msb_lshift = width - 8
        self._reverse_result = reverse_result
        self.name = name

    def calculate(self, data):
        """Calculate a CRC on data

        :param data: bytes string
        :return: calculated CRC
        """
        remainder = self._seed
        for value in data:
            remainder = (remainder << 8) ^ self._table[
                (remainder >> self._msb_lshift) ^ value
                ]
            remainder &= self._result_mask
        if self._reverse_result:
            remainder = bit_reverse_n(remainder, self._width)
        return remainder ^ self._xor_out

    def __call__(self, data):
        return self.calculate(data)


class _CrcGeneric:
    """Generic most-significant-bit-first table-driven CRC calculation, allows
    unusual (and probably not useful) combinations of parameters such as
    reflecting the input without reflecting the output
    """
    def __init__(self, poly: int, width: int, seed: int, ref_in: bool, ref_out: bool, xor_out=0,
                 name=""):
        """

        :param poly: polynomial representation, has implicit leading 1 bit
        :param width:
        :param seed:
        :param ref_in:
        :param ref_out:
        :param xor_out:
        :param name:
        """
        self._poly = poly
        self._width = width
        self._default_seed = seed
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1

        # If the width is less than 8 bits, the CRC poly needs
        # to be shifted to meet the most significant bit. This allows whole
        # bytes to be loaded into the calculation, even though the result is
        # less than 8 bits wide
        if width < 8:
            self._crc_lshift = 8 - width
            self._msb_lshift = 0
        else:
            self._msb_lshift = width - 8
            self._crc_lshift = 0
        # Bit mask that can be used to test whether the most significant bit
        # of the intermediate CRC is set
        self._msbit_mask = 1 << (width + self._crc_lshift - 1)
        # Mask that can be used to remove bits shifted off the left hand edge
        # of the calculation register
        self._crc_mask = (1 << (width + self._crc_lshift)) - 1
        self._ref_in = ref_in
        self._ref_out = ref_out
        self.name = name

    def calculate(self, data, seed=None):
        """Calculate CRC of data

        :param data: byte string
        :param seed: optional seed value
        :return: calculated CRC

        The fundamental logic of the algorithm is to read each byte from the
        input stream, and xor with the pol
        """
        crc = seed if seed is not None else self._default_seed
        # if the poly is less than 8 bits wide, the calculation is performed
        # at the top end of the byte, so that whole bytes can be loaded
        crc <<= self._crc_lshift
        poly = self._poly << self._crc_lshift
        for byte in data:
            if self._ref_in:
                byte = _REV8BITS[byte]
            crc ^= byte << self._msb_lshift
            for _ in range(_BYTEBITS):
                if crc & self._msbit_mask:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
            crc &= self._crc_mask
        crc >>= self._crc_lshift
        if self._ref_out:
            crc = bit_reverse_n(crc, self._width)
        return crc ^ self._xor_out

    def __call__(self, data):
        return self.calculate(data)


class _WindowedCrc:
    """Generic most-significant-bit-first table-driven CRC calculation with
    an optional range of bit positions on the input to process.
    Allows unusual (and probably not very useful) combinations of parameters such as
    reflecting the input without reflecting the output or ignoring whole bytes
    of the specified input data.
    """
    def __init__(self, params: CrcParams, name="") -> None:
        self._width = params.width
        self._default_seed = params.seed
        self._params = params
        self._result_mask = (1 << params.width) - 1

        # If the width is less than 8 bits, the CRC poly needs
        # to be shifted to meet the most significant bit. This allows whole
        # bytes to be loaded into the calculation, even though the result is
        # less than 8 bits wide
        if params.width < 8:
            self._crc_lshift = 8 - params.width
            self._msb_lshift = 0
        else:
            self._msb_lshift = params.width - 8
            self._crc_lshift = 0
        # Bit mask that can be used to test whether the most significant bit
        # of the intermediate CRC is set
        self._msbit_mask = 1 << (params.width + self._crc_lshift - 1)
        # Mask that can be used to remove bits shifted off the left hand edge
        # of the calculation register
        self._crc_mask = (1 << (params.width + self._crc_lshift)) - 1
        self._ref_in = params.reflect_in
        self._ref_out = params.reflect_out
        self.name = name

    def calculate(self, data: bytes, start_bit=0, length_bits=None, seed=None) -> int:
        """Calculate CRC of data including only `length_bits` of `data` after
        `start_bit`

        :param start_bit: bit number in `data` bytes at which checksum should
                          start. Most significant bit of the first byte in
                          `data` is bit 0
        :param length_bits: number of bits (starting at `start_bit`) to checksum
        :param data: byte string of data to checksum
        :param seed: optional seed value
        :return: calculated CRC
        """
        # pylint: disable=too-many-locals
        residual = seed if seed is not None else self._default_seed
        num_input_bits = _BYTEBITS * len(data)

        if length_bits is None:
            length_bits = num_input_bits - start_bit

        if (start_bit >= num_input_bits) or (start_bit < 0):
            raise ValueError(f"Start bit {start_bit} is out of range.")
        if length_bits < 0:
            raise ValueError(f"Checksum length must be non-negative (value {length_bits}).")
        if start_bit + length_bits > num_input_bits:
            raise ValueError(f"Parameter length_bits {length_bits} is out of range.")

        first_byte, first_bit = divmod(start_bit, _BYTEBITS)
        last_byte, last_bit = divmod(start_bit + length_bits - 1, 8)

        check_range = range(first_byte, last_byte + 1)
        # if the poly is less than 8 bits wide, the calculation is performed
        # at the top end of the byte, so that whole bytes can be loaded
        residual <<= self._crc_lshift
        poly = self._params.polynomial << self._crc_lshift
        # Since we are checking a slice of the byte stream, it's clearer to
        # iterate over the index of the list  rather than the data itself
        for index in check_range:
            input_bits, input_width = self._get_input_bits(
                data, index, first_byte, first_bit, last_byte, last_bit
            )
            # Shift the input data to align with the top bit of the rolling
            # CRC value
            residual ^= input_bits << self._msb_lshift
            # XOR the poly, this is usually 8 bits, unless it is a partial first
            # or last byte
            for _ in range(input_width):
                if residual & self._msbit_mask:
                    residual = (residual << 1) ^ poly
                else:
                    residual <<= 1
                residual &= self._crc_mask
        # For small polynomials undo any shift we did at the start
        assert residual & ((1 << self._crc_lshift) - 1) == 0
        residual >>= self._crc_lshift
        if self._ref_out:
            residual = bit_reverse_n(residual, self._width)
        return residual ^ self._params.xor_out

    def _get_input_bits(self, data, index, first_byte, first_bit, last_byte, last_bit):
        input_byte = data[index]
        if self._ref_in:
            input_byte = _REV8BITS[input_byte]
        # if this is the last byte in the calculation, we want to mask out
        # any extraneous trailing set bits
        # the position of the final bit determines the length of the block
        # that needs to be checked
        if index == last_byte:
            end_mask = _calc_end_mask(last_bit)
            input_byte &= end_mask
            block_width = last_bit + 1
        else:
            block_width = _BYTEBITS
        if index == first_byte:
            # This is the first byte to be checked, shift the bit stream
            # left until the first interesting bit is aligned with the msb
            input_byte <<= first_bit
            block_width -= first_bit
        return input_byte, block_width

    def __call__(self, data):
        return self.calculate(data)


class _GenericLsbfCrc:
    """General purpose CRC calculation using LSB algorithm. Mainly here for
    reference, since the other algorithms cover all useful calculation combinations
    """

    def __init__(self, lsb_poly, width, lsb_seed, ref_in, ref_out, xor_out, name=""):
        self._poly = lsb_poly
        self._width = width
        self._seed = lsb_seed
        self._xor_out = xor_out
        self._result_mask = (1 << width) - 1
        self._msbit = 1 << (width - 1)
        self._msb_lshift = width - 8
        self._ref_in = ref_in
        self._ref_out = ref_out
        self.name = name

    def calculate(self, data, seed=None):
        """Calculate a CRC on data

        :param data: bytes string whose CRC will be calculated
        :param seed: Optional seed
        :return: calculated CRC
        """
        if seed is not None:
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


def new(name, calc_engine=_DEFAULT_ENGINE):
    """Create a new CRC calculation instance"""
    params = lookup_params(name)
    # the check field is not part of the definition, remove it before
    # creating the algorithm
    return create_from_params(params, calc_engine)


def table_crc(params: CrcParams):
    """Return a table-based CRC algorithm corresponding to `params`
    """
    if params.reflect_in:
        table = create_lsb_table(params.polynomial, params.width)
        crc_class = _ReflectedTableCrc
    else:
        table = create_msb_table(params.polynomial, params.width)
        crc_class = _CrcMsbfTable

    reverse_result = params.reflect_in != params.reflect_out
    algorithm = crc_class(table, params.width, params.seed, xor_out=params.xor_out,
                          reverse_result=reverse_result)
    return algorithm


def create(poly: int, width: int, seed: int, ref_in: bool, ref_out: bool,
           xor_out: int, calc_engine="table"):
    """Create a table-driven CRC calculation engine

    :param poly: polynomial binary representation
    :param width: polynomial width in bits
    :param seed: seed value for the CRC calculation to use
    :param ref_in:  reflect input bits
    :param ref_out: reflect output bits
    :param xor_out:  exclusive-or the output with this value
    :return:
    """
    creator_fun = _CREATOR_FUNCS[calc_engine]
    params = CrcParams(poly, width, seed, ref_in, ref_out, xor_out)
    algorithm = creator_fun(params)
    return algorithm


def create_from_params(params: CrcParams, calc_engine=_DEFAULT_ENGINE):
    """Create a CRC calculation algorithm instance based on `params` using
    calculation engine `calc_engine` as the back end

    :param params:
    :param calc_engine:
    :return:
    """
    creator_fun = _CREATOR_FUNCS[calc_engine]
    return creator_fun(params)


def create_generic(poly: int, width: int, seed: int, ref_in: bool, ref_out: bool,
                   xor_out: int, name=""):
    """Create generic non-table-driven CRC calculator

    :param poly: Polynomial
    :param width: calculator width in bits e.g. 32
    :param seed: calculation seed value
    :param ref_in: reflect incoming bits
    :param ref_out: reflect result bits
    :param name: name to assign to calculator
    :param xor_out: pattern to XOR into result
    :return: A CRC calculation engine
    """
    return _CrcGeneric(
        poly, width, seed, ref_in=ref_in, ref_out=ref_out, xor_out=xor_out, name=name
    )


def windowed_crc(params: CrcParams):
    """Create generic non-table-driven CRC calculator that allows a start-bit
    and bit-length window to be specified on the CRC calculation

    :return: A CRC calculation engine
    """
    return _WindowedCrc(params)


def generic_lsb_first(
        lsb_poly, width, lsb_seed, ref_in=False, ref_out=False, xor_out=0xFFFFFF, name=""
):
    """Create a CRC calculation engine that uses the Least-significant first
    algorithm, but does not reflect the polynomial or seed value. If you use
    this, reflect the polynomial before passing it in"""
    return _GenericLsbfCrc(
        lsb_poly, width, lsb_seed, ref_in=ref_in, ref_out=ref_out, xor_out=xor_out, name=name
    )


def create_msb_table_individual(poly, width):
    """Generate a CRC table calculating each entry.
    Mainly for demonstration and test, since calculate_msb_table() is
    much more efficient at calculating the same information
    :return: Generated table
    """
    msb_lshift = width - 8
    ms_bit = 1 << (width - 1)
    result_mask = (1 << width) - 1
    table = 256 * [0]
    for index in range(1, 256):
        crc = index << msb_lshift
        for _ in range(8):
            if crc & ms_bit:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
        table[index] = crc & result_mask
    return table


_CREATOR_FUNCS = {
    "table": table_crc,
    "generic": create_generic,
    "generic_msbf": create_generic,
    "generic_lsbf": generic_lsb_first,
    "windowed": windowed_crc,
}


def available_calculation_engines() -> Iterable[str]:
    """Return the list of available calculation back-ends. These can be used
    with :meth:`crcengine.create()`
    """
    return _CREATOR_FUNCS.keys()


def create_msb_table(poly, width):
    """Calculate a CRC lookup table for the selected algorithm definition
    :return: list of CRC values
    """
    ms_bit = 1 << (width - 1)
    result_mask = (1 << width) - 1
    # Preallocate entries to 0
    table = 256 * [0]
    # this is essentially the '1' shifted left by the number of
    # bits necessary for it to reach the msbit of the remainder value
    crc = ms_bit
    # `i` is the index of the table that is being computed this loop
    i = 1
    while i <= 128:
        # Each (1<<n) must have the polynomial applied to it n+1 times
        # since 1 must be shifted left 7 times before a non-zero bit is in
        # the msb, there are no more shifts to be done
        # 2 requires 6 shifts for a non-zero bit in the msbit, so the msbit
        # test (and conditional polynomial xor) is applied once more
        # 4 requires 5 shifts for a non-zero bit in the msbit, so the
        # msb test is applied three times.
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
    """Calculate a CRC lookup table for the selected algorithm definition
    producing a table that can be used for the lsbit algorithm

    :return: table of reflected
    """
    table = 256 * [0]
    crc = 1
    # `i` is the index of the table that is being computed this loop
    # the lsb table contains an implicit reflection of the data byte so
    # '1' is a reflected 128
    # The algorithm starts from this value because in an lsb-first CRC the poly
    #  will only be applied to it once, so we can compute it without iteration
    i = 0x80
    poly = bit_reverse_n(poly, width)
    # On iteration, we compute index positions 128, 64, 32 ...
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


def bit_reverse_byte(byte: int) -> int:
    """Bit-bashing reversal of a byte"""
    result = 0
    for i in range(8):
        if byte & (1 << i):
            result |= 1 << (7 - i)
    return result & 0xFF


def bit_reverse_n(value: int, num_bits: int) -> int:
    """Mirror the bits in an integer

    :param value: the integer to reverse
    :param num_bits: the number of bits  to reverse
    :return: mirrored value
    """
    # This left shift will introduce zeroes in the least-significant bits, which
    # will be ignored as 0 most sig bits once we bit reverse
    value <<= (8 - num_bits) & 7
    num_bytes = (num_bits + 7) >> 3
    result = 0
    for _ in range(num_bytes):
        result <<= 8
        result |= _REV8BITS[value & 0xFF]
        value >>= 8
    return result


def get_bits_max_value(nbits):
    """Convenience function returning largest unsigned integer for a given
    number of bits"""
    return (1 << nbits) - 1


# Table of bit-reversed bytes, initialised on loading
_REV8BITS = [bit_reverse_byte(_n) for _n in range(256)]


def _calc_end_mask(last_bit: int):
    """Calculate the mask required to mask IN the bits of the final byte of
    data. Bits are counted most-significant-bit first

    :param last_bit: position of final bit 0=most significant, 7 = least
                     significant
    :return:
    """
    return ~((1 << (7 - last_bit)) - 1) & 0xFF


def bytes_to_bit_string(value: bytes, sep="_", prefix=""):
    """Convert a bytes into a binary string representation

    :param value: bytes value to convert
    :param sep: separator for output octets
    :param prefix: optional additional prefix e.g. 0b
    :return: binary representation string of `value`
    """
    output = sep.join([f"{x:08b}" for x in value])
    return prefix + output
