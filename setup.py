#!/usr/bin/env python

import os
import sys
import subprocess as sub
from setuptools import setup
from wheel.pep425tags import get_platform

from getdlls import getDLLs


# Get the necessary SDL2 DLLs for the platform

getDLLs(get_platform())


# Install the package

setup(
	name='sdl2dll',
	version='2.0.10',
	description='A package containing pre-built SDL binaries for PySDL2',
	author='Austin Hurst',
	author_email='mynameisaustinhurst@gmail.com',
	packages=['sdl2dll'],
	include_package_data=True,
	install_requires=[]
)
