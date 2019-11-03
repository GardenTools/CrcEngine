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

A list of pre-defined algorithms can be obtained using

Example
-------
```python
from crcpylib import CrcEngine
crc_algorithm = CrcEngine.new('crc32-bzip2')
result = crc_algorithm(b'123456789')
print('CRC=0x{:08x}'.format(result))
```
Output:
> CRC=0xfc891918

---

With thanks to Greg Cook for providing such a thoroughly collated list of
[CRC definitions](http://reveng.sourceforge.net/crc-catalogue/all.htm)
