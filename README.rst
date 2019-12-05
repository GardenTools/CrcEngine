.. image:: https://img.shields.io/pypi/v/crcengine.svg
        :target: https://pypi.python.org/pypi/crcengine

.. image:: https://travis-ci.com/GardenTools/CrcEngine.svg?branch=master
        :target: https://travis-ci.com/GardenTools/crcengine

.. image:: https://readthedocs.org/projects/crcengine/badge/?version=latest
        :target: https://crcengine.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/GardenTools/CrcEngine/shield.svg
     :target: https://pyup.io/repos/github/GardenTools/CrcEngine/
     :alt: Updates

=========
CrcEngine
=========
A python library for CRC calculation providing table-based as well as
bit-bashing implementations (for reference).

* Free software: GNU General Public License v3
* Documentation: https://crcengine.readthedocs.io.

Installing
----------
CrcEngine can be installing using pip with

.. code-block::

    pip install crcengine

Usage
-----
Pre-defined algorithms such as CRC32 are available. Tailored algorithms can
be created by calling CrcEngine.create() and other related methods.

A calculation engine for a specific named algorithm can be obtained using
CrcEngine.new(). Algorithms which are not pre-defined can be created using
CrcEngine.create() 

A list of pre-defined algorithms can be obtained using crcengine.algorithms_available()

.. code-block::

   >>> list(crcengine.algorithms_available())
   ['crc8', 'crc8-autosar', 'crc8-bluetooth', 'crc8-ccitt', 'crc8-gsm-b', 'crc8-sae-j1850', 'crc15-can', 'crc16-kermit', 'crc16-ccitt-true', 'crc16-xmodem', 'crc16-autosar', 'crc16-ccitt-false', 'crc16-cdma2000', 'crc16-ibm', 'crc16-modbus', 'crc16-profibus', 'crc24-flexray16-a', 'crc24-flexray16-b', 'crc32', 'crc32-bzip2', 'crc32-c', 'crc64-ecma']

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

Faster implementations of specific algorithms can be achieved in software which
unroll loops and pipeline the operations different bytes to introduce
parallelism in the calculation see intel_soft_src_ for example. Some processors
also include instructions specifically for crc calculation.

.. _intel_soft_src: https://github.com/intel/soft-crc

Code Generation Example usage:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generating code into a directory named "out" by passing CRC parameters

.. code-block::

    params = crcengine.get_algorithm_params('crc32')
    crcengine.generate_code(params, 'out/')

or referencing the algorithm by name

.. code-block::

    crcengine.generate_code('crc16-xmodem', 'out/')


Downloading
-----------
- The source is available on github_
- Git clone crcengine.git_
- On pypi.org_

.. _github: https://github.com/GardenTools/crcengine
.. _crcengine.git: https://github.com/GardenTools/crcengine.git
.. _pypi.org: https://pypi.org/project/crcengine/

--------

With thanks to Greg Cook for providing such a thoroughly collated list of
`CRC definitions`_

.. _CRC definitions: http://reveng.sourceforge.net/crc-catalogue/all.htm
