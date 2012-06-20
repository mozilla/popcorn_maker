#!/usr/bin/env python
import os

from setuptools import setup, find_packages


setup(name='popcorn_gallery',
      version='0.1',
      description='Popcorn Gallery',
      long_description='',
      author='',
      author_email='',
      license='BSD License',
      url='',
      include_package_data=True,
      classifiers = [],
      packages=find_packages(exclude=['tests']),
      install_requires=[])
