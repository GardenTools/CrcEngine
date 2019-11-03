[![Build Status](https://travis-ci.com/GardenTools/crcpylib.svg?token=sQrmEU8kgQPPzaheXBfq&branch=master)](https://travis-ci.com/GardenTools/crcpylib)

CrcPyLib
========
A python library for CRC calculation providing table-based as well as
bit-bashing implementations (for reference).

Usage
-----
Use pre-defined algorithms such as CRC32 are available. Tailored algorithms can
be created by calling CrcEngine.create() and other related methods.

A calculation engine for a specific named algorithm can be obtained using
CrcEngine.new(). Algorithms which are not pre-defined can be created using
CrcEngine.create() 

A list of pre-defined algorithms can be obtained using CrcEngine.algorithms_available()

Examples
--------
Using a pre-defined algorithm
```python
from crcpylib import CrcEngine
crc_algorithm = CrcEngine.new('crc32-bzip2')
result = crc_algorithm(b'123456789')
print('CRC=0x{:08x}'.format(result))
```
Output:
> CRC=0xfc891918

Defining an algorithm
```python
from crcpylib import CrcEngine
crc_openpgp = CrcEngine.create(0x864cfb, 24, 0xb704ce, ref_in=False,
                               ref_out=False, xor_out=0, name='crc-24-openpgp')
```

Downloading
-----------
 * The source is available on [github](https://github.com/GardenTools/crcpylib).
 * Git clone [https://github.com/GardenTools/crcpylib.git](https://github.com/GardenTools/crcpylib.git)

---

With thanks to Greg Cook for providing such a thoroughly collated list of
[CRC definitions](http://reveng.sourceforge.net/crc-catalogue/all.htm)
