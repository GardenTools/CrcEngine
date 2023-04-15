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

.PHONY: clean clean-test clean-pyc clean-build clean-all
clean-all: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean: clean-build

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
dist: clean-build ## builds source and wheel package
	poetry build
	ls -l dist

.PHONY: install
install: clean ## install the package to the active Python's site-packages
	poetry install

# The sed command is needed because poetry seems to muddle the version marker,
# if one dependency says it doesn't need a package at a specific version of
# python it sets the limit globally even when the package is specified as
# required in project.toml
docs/requirements.txt: poetry.lock Makefile
	poetry export --format requirements.txt --only docs --without-hashes | sed 's/;.*//' > $@

