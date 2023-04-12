#This file is part of CrcEngine, a python library for CRC calculation
#
#crcengine is free software: you can redistribute it an d /or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#crcengine is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with crcengine.  If not, see <https://www.gnu.org/licenses/>.

.DEFAULT_GOAL := help

ifeq ($(OS),Windows_NT)
    SYS_PY3:=py -3
    TESTENV_BIN:=testenv/Scripts
    FIX_WIN_VENV=scripts/fix_win_bash_venv $(1)
else
    SYS_PY3:=python3
    TESTENV_BIN:=testenv/bin
    FIX_WIN_VENV=:
endif

PYTHON?=python

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
      target, help = match.groups()
      print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean clean-test clean-pyc clean-build
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	-find . -name '*.egg-info' -exec rm -rf {} +
	-find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	pylint src
test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

# Use make -B testenv to force an update
testenv: requirements.txt ## Build test virtualenv
	echo $@
	$(SYS_PY3) -m venv testenv ; \
	$(call FIX_WIN_VENV, $@) ; \
	. $(TESTENV_BIN)/activate ; \
	python -m pip install --upgrade pip; \
	pip install -r requirements.txt

.PHONY: coverage-text
coverage-text: ## Run tests with coverage text output
	pytest --cov=crcengine --cov-report term tests

.PHONY: coverage
coverage: ## Run tests with coverage html output
	pytest --cov=crcengine --cov-report html tests
	$(BROWSER) htmlcov/index.html

.PHONY: release
release: dist ## package and upload a release
	twine upload dist/*

# testpypi is expected to point to https://test.pypi.org/legacy/ 

.PHONY: release-test
release-test: dist ## package and upload a release
	twine upload --repository testpypi dist/*

.PHONY: dist
dist: clean ## builds source and wheel package
	python -m build
	ls -l dist

.PHONY: install
install: clean ## install the package to the active Python's site-packages
	python setup.py install

UPDATE_REQS=pip-compile -q -U --resolver=backtracking --output-file=requirements.txt requirements.in

.PHONY: update-deps
update-deps: ## Update dependencies in requirements.txt
	$(PYTHON) -m pip install --upgrade pip
	$(call UPDATE_REQS)

requirements.txt: requirements.in
	$(call UPDATE_REQS)
