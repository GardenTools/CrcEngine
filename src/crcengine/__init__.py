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

try:
    # python 3.8 onwards
    from importlib import metadata as importlib_metadata
except ImportError:
    # python 3.7 support
    import importlib_metadata

__version__ = importlib_metadata.version('crcengine')

from .algorithms import (
    AlgorithmNotFoundError,
    algorithms_available,
    CrcParams,
    get_algorithm_params,
    lookup_params,
    register_algorithm,
    unregister_algorithm,
)
from .calc import (
    available_calculation_engines,
    bit_reverse_byte,
    bit_reverse_n,
    create,
    create_from_params,
    create_generic,
    create_lsb_table,
    create_msb_table,
    get_bits_max_value,
    new,
    table_crc,
)

from .import codegen

__all__ = [
    "AlgorithmNotFoundError",
    "algorithms_available",
    "available_calculation_engines",
    "bit_reverse_byte",
    "bit_reverse_n",
    "codegen",
    "CrcParams",
    "create",
    "create_from_params",
    "create_generic",
    "create_lsb_table",
    "create_msb_table",
    "get_algorithm_params",
    "get_bits_max_value",
    "lookup_params",
    "new",
    "register_algorithm",
    "table_crc",
    "unregister_algorithm",
]
