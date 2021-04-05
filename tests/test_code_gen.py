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

import crcengine
from os.path import join
import subprocess
import os
import sys

import pytest

C_TEST_HOME = join(os.path.dirname(__file__), "c_tests")


@pytest.fixture(autouse=True)
def _generate_algorithms():
    algorithms = crcengine.algorithms_available()
    for alg in algorithms:
        print("Generating code for", alg)
        crcengine.generate_code(alg, join(C_TEST_HOME, "src"))


def generate_tests():
    """Generate the test files for generated code, normally these are checked
    in so that the introduction of a regression in enumeration of algorithms
    (for example) won't affect the tests run unless they are explicitly
     regenerated"""
    algorithms = crcengine.algorithms_available()
    for alg in algorithms:
        print("Generating code for", alg)
        crcengine.generate_code(alg, join(C_TEST_HOME, "src"))
        crcengine.codegen.generate_test(alg, join(C_TEST_HOME, "test"))


@pytest.mark.needs_ceedling
def test_code_gen():
    completed = subprocess.run(
        ["ceedling", "test:all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=C_TEST_HOME,
        universal_newlines=True,
    )
    print(completed.returncode)
    print(completed.stdout)
    print(completed.stderr, file=sys.stderr)
    assert completed.returncode == 0
