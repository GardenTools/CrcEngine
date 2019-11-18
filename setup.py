#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

import crcengine._version

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['jinja2>=2.7']  # ['pytest-runner', ]

test_requirements = ['pytest>=3', 'tox>=3']

setup(
    author="Garden Tools",
    author_email='gardensofdorwinion@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A library for CRC calculation",
    entry_points={
        'console_scripts': [
            'crcengine=crcengine.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n',  # + history,
    include_package_data=True,
    keywords='crcengine',
    name='crcengine',
    packages=find_packages(include=['crcengine', 'crcengine.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/GardenTools/crcengine',
    version=crcengine.__version__,
    zip_safe=False,
)
