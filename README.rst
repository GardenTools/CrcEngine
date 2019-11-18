.. image:: https://img.shields.io/pypi/v/crcengine.svg
        :target: https://pypi.python.org/pypi/crcengine
.. image:: https://img.shields.io/travis/GardenTools/crcengine.svg
        :target: https://travis-ci.org/GardenTools/crcengine
.. image:: https://readthedocs.org/projects/crcengine/badge/?version=latest
        :target: https://crcengine.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://pyup.io/repos/github/GardenTools/crcengine/shield.svg
     :target: https://pyup.io/repos/github/GardenTools/crcengine/
     :alt: Updates

=========
CrcEngine
=========
A python library for CRC calculation providing table-based as well as
bit-bashing implementations (for reference).

* Free software: GNU General Public License v3
* Documentation: https://crcengine.readthedocs.io.

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

.. code-block::

  import crcengine
  crc_algorithm = crcengine.new('crc32-bzip2')
  result = crc_algorithm(b'123456789')
  print('CRC=0x{:08x}'.format(result))

Output:
> CRC=0xfc891918

Defining an algorithm
.. code-block::

  import crcengine
  crc_openpgp = crcengine.create(0x864cfb, 24, 0xb704ce, ref_in=False,
                                 ref_out=False, xor_out=0, name='crc-24-openpgp')


Code Generation
---------------
The library can generate C code for a given table-algorithm. The code produced
is intended to be a reasonable compromise between size, complexity and speed
without requiring allocation of memory for table generation at runtime.

Faster implementations of specific algorithms can be achived in software which
unroll loops and pipeline the operations different bytes to introduce
parallelism in the calculation see intel_soft_src_ for example. Some processors
also include instructions specifically for crc calculation.

.. _intel_soft_src: https://github.com/intel/soft-crc

Downloading
-----------
- The source is available on github_
- Git clone crcengine.git_

.. _github: https://github.com/GardenTools/crcengine
.. _crcengine.git: https://github.com/GardenTools/crcengine.git

----

With thanks to Greg Cook for providing such a thoroughly collated list of
`CRC definitions`_

.. _CRC definitions: http://reveng.sourceforge.net/crc-catalogue/all.htm
