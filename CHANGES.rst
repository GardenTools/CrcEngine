=======
History
=======

0.3.2 (2021-04-10)
------------------
Correcting issue relating to module import order for version.py

0.3.1 (2021-04-09)
------------------
* Correcting metadata for python version in setup.cfg

0.3.0 (2021-04-05)
------------------
* Fixed code generation for algorithms whose result doesn't wholly fill a data-type
* Added unit tests for generated C, run using Ceedling_
* Added command-line entry point
* Added support for invoking as a module via python -m
* Switched over to using setup.cfg rather than setup.py
* Python 3.9 support added

.. _Ceedling: https://github.com/ThrowTheSwitch/Ceedling

0.2.0  (2020-01-30)
-------------------
Added Sphinx documentation

0.1.1 (2019-11-19)
------------------
Addressing dependency issues when installing package in some environments

0.1.0 (2019-11-18)
------------------

* First experimental release on PyPI. Code generation support is incomplete and
  API is prone to change
