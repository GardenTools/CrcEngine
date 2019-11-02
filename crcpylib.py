
# Table of bit-reversed bits for fast bit reversal, initialised on loading
_REV8BITS = None

MAX_UINT32 = ((1<<32) - 1)
CRC32_POLY = 0x04C11DB7


def _no_op(*args, **kwargs):
    return None


class Crc:
    def __init__(self, poly, width=32, seed=0xFFFFFFFF, xor_out=0xFFFFFF,
                 ref_in=True, ref_out=True, name=''):
        self.name = name
        self.poly = poly
        self.seed = seed
        self.xor_out = xor_out
        self.width = width
        self.ref_in = ref_in
        self.ref_out = ref_out
        self._msbit = 1 << (self.width - 1)
        self._msb_lshift = self.width - 8
        self._result_mask = (1 << self.width) - 1
        self._table = None
        self.log = _no_op

    def __call__(self, data, seed=None):
        return self.calculate(data, seed)

    def set_printing(self, enable):
        if enable:
            self.log = print
        else:
            self.log = _no_op

    def calculate(self, data, seed=None):
        if seed is None:
            seed = self.seed
        # reflected calculations are more efficiently performed with the little endian algorithm
        if self.ref_in and self.ref_out:
            remainder = self.calc_raw_lsb(data, bit_reverse_n(self.poly, self.width), seed)
        else:
            remainder = self.calc_raw_msb(data, self.poly, seed)
        return remainder ^ self.xor_out

    def calculate_msb(self, data, seed=None):
        if seed is None:
            seed = self.seed
        remainder = self.calc_raw_msb(data, self.poly, seed)
        return remainder

    def calculate_lsb(self, data, seed=None):
        if seed is None:
            seed = self.seed
        if self.ref_in:
            poly = bit_reverse_n(self.poly, self.width)
        else:
            poly = self.poly
        remainder = self.calc_raw_lsb(data, poly, seed)
        return remainder ^ self.xor_out

    def calc_raw_msb(self, data, poly, remainder):
        self.log('')
        for byte in data:
            self.log('Start iteration %x %x %x' % (byte, remainder, bit_reverse_n(remainder, 32)))
            if self.ref_in:
                reflect_byte = _REV8BITS[byte]
                self.log("Reflect %x -> %x" % (byte, reflect_byte))
                byte = reflect_byte
            remainder ^= (byte << self._msb_lshift)
            self.log('After Xor input byte %x %x' % (remainder, bit_reverse_n(remainder, 32)))
            for j in range(8):
                if remainder & self._msbit:
                    remainder = (remainder << 1) ^ poly
                else:
                    remainder <<= 1
                self.log('Iteration %d %08x %08x' % (j, remainder, bit_reverse_n(remainder, 32)))
            remainder &= self._result_mask
        if self.ref_out:
            remainder = bit_reverse_n(remainder, self.width)
        self.log('Post-reflect %x %x' % (remainder, bit_reverse_n(remainder, 32)))
        return remainder ^ self.xor_out

    def calc_raw_lsb(self, data, poly, remainder):
        result_mask = (1 << self.width) - 1
        for byte in data:
            self.log('Start LE iteration %x %x %x' % (byte, remainder, bit_reverse_n(remainder, 32)))
            remainder ^= byte
            self.log('After Xor input byte %x %x' % (remainder, bit_reverse_n(remainder, 32)))
            for j in range(8):
                if remainder & 1:
                    remainder = (remainder >> 1) ^ poly
                else:
                    remainder >>= 1
                self.log('Iteration %d %x %x' % (j, remainder, bit_reverse_n(remainder, 32)))
        self.log('Post-reflect %x %x' % (remainder, bit_reverse_n(remainder, 32)))
        return remainder & result_mask

    def generate_msb_table(self):
        self._table = self.calculate_msb_table()

    def calculate_msb_table_individual(self):
        """ Generate a CRC table calculating each entry.
            Mainly for demonstration and test, since calculate_msb_table() is
            much more efficient to calculate
        :return: Generated table
        """
        table = 256 * [0]
        for n in range(1, 256):
            crc = n << self._msb_lshift
            for j in range(8):
                if crc & self._msbit:
                    crc = (crc << 1) ^ self.poly
                else:
                    crc <<= 1
                self.log('Iteration %d %08x %08x' % (j, crc, bit_reverse_n(crc, 32)))
            table[n] = crc & self._result_mask
        return table

    def calculate_msb_table(self):
        """ Calculate a CRC lookup table for the selected algorithm definition
        :return: list of CRC values
        """
        # Preallocate entries to 0
        table = 256 * [0]
        # this is essentially the '1' shifted left by the number of
        # bits necessary for it to reach the msbit of the remainder value
        crc = self._msbit
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
            if crc & self._msbit:
                crc = (crc << 1) ^ self.poly
            else:
                crc <<= 1
            crc &= self._result_mask
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
    for n in range(num_bytes):
        result <<= 8
        result |= _REV8BITS[value & 0xFF]
        value >>= 8
    return result


def _init_bit8rev_table():
    global _REV8BITS
    _REV8BITS = [bit_reverse_byte(n) for n in range(256)]


# Table initialisation on loading
_init_bit8rev_table()

crc32 = Crc(name='CRC32', poly=CRC32_POLY, seed=MAX_UINT32, xor_out=MAX_UINT32,
            width=32, ref_in=True, ref_out=True)

