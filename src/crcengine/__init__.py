"""
This file is part of crcengine, a python library for CRC calculation

Copyright 2019 Garden Tools software

crcengine is free software: you can redistribute it an d /or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

crcengine is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with crcengine.  If not, see <https://www.gnu.org/licenses/>.
"""
from .version import __version__
from .crcengine import *
from .algorithms import get_algorithm_params, algorithms_available
from .codegen import generate_code
