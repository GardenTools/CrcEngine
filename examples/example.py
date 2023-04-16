import crcengine


def main():
    params = crcengine.get_algorithm_params('crc32')
    crcengine.generate_code(params, 'out/')
    crcengine.generate_code('crc16-xmodem', 'out/')
    filename = "out/crc16_xmodem.c"
    print("Created {} with the following content:")
    with open(filename, "r") as f:
        file = f.read()
        print(file)
    available = crcengine.algorithms_available()
    print("\nThe following algorithms are available")
    print(", ".join(available))

    data = b"123456789"
    crc16x = crcengine.new("crc16-xmodem")
    result = crc16x.calculate(data)
    print("\nThe crc16-xmodem of {} is 0x{:x}".format(data.decode("ascii"), result))

    defining_an_algorithm()


def defining_an_algorithm():
    params = crcengine.CrcParams(0x864cfb, 24, 0xb704ce, reflect_in=False, reflect_out=False, xor_out=0)
    crc_openpgp = crcengine.create_from_params(params, calc_engine='table')
    result = crc_openpgp(b'123456789')
    # or
    crc_openpgp = crcengine.create(params=params, name='crc-24-openpgp')
    result = crc_openpgp(b'123456789')
    print(f'CRC=0x{result:08x}')


if __name__ == '__main__':
    main()


