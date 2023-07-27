#!/usr/bin/env python3

from setuptools import setup

PACKAGE_NAME = 'fill'

setup(name=PACKAGE_NAME,
      version='0.0.1',
      packages=['fill'],
      description='Fills clicked fields with strings from file or stdin',
      install_requires=['pynput==1.7.6'],
      entry_points={'console_scripts': ['fill = fill:run_default']})
