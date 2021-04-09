"""Unit tests for version number reporting"""
# This file is part of crcengine.
#
# crcengine is free software: you can redistribute it an d /or modify
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

import packaging.version

import crcengine

def test_version():
    pkg_ver = packaging.version.parse(crcengine.__version__)
    ref_ver = packaging.version.parse("0.3.0")
    print(pkg_ver)
    print(ref_ver)
    assert pkg_ver > ref_ver
