import crcengine
if __name__ == '__main__':
    params = crcengine.get_algorithm_params('crc32')
    crcengine.generate_code(params, 'out/')

    crcengine.generate_code('crc16-xmodem', 'out/')
