#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='cache_toolbar',
    version='1.0.0',
    description='',
    author='Rick van Hattem',
    author_email='Rick.van.Hattem@Fawo.nl',
    url='http://github.com/WoLpH/cache-debug-panel',
    packages=find_packages(exclude=('examples', 'examples.demo', 'test')),
    provides=['cache_toolbar'],
    requires=['Django', 'debug_toolbar'],
    include_package_data=True,
    zip_safe=False,
)
