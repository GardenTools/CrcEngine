import crcengine

if __name__ == '__main__':
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
