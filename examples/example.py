import crcengine
if __name__ == '__main__':
    params = crcengine.get_algorithm_params('crc32')
    crcengine.generate(params, 'out/')

    crcengine.generate('crc16-xmodem', 'out/')
