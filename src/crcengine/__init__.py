"""
Package exports
"""
# This file is part of crcengine, a python library for CRC calculation
#
# Copyright 2021 Garden Tools software
#
# crcengine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# crcengine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with crcengine.  If not, see <https://www.gnu.org/licenses/>.

import importlib_metadata

__version__ = importlib_metadata.version('crcengine')

from .algorithms import (
    AlgorithmNotFoundError,
    algorithms_available,
    get_algorithm_params,
    register_algorithm,
    unregister_algorithm,
)
from .calc import (
    bit_reverse_byte,
    bit_reverse_n,
    create,
    create_generic,
    create_lsb_table,
    create_msb_table,
    get_bits_max_value,
    new,
)
from .codegen import generate_code, generate_test

__all__ = [
    AlgorithmNotFoundError,
    algorithms_available,
    bit_reverse_byte,
    bit_reverse_n,
    create,
    create_generic,
    create_lsb_table,
    create_msb_table,
    get_algorithm_params,
    get_bits_max_value,
    new,
    register_algorithm,
    unregister_algorithm,
]
