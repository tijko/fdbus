#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, Extension, find_packages
except ImportError:
    from disutils.core import setup, Extension


setup(
    name='fdbus',
    version='0.0.1',
    author='Tim Konick',
    author_email='konick781@gmail.com',
    url='',
    description='Bus for passing file descriptors',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    packages=['fdbus', 'fdbus/client', 'fdbus/server', 
              'fdbus/exceptions', 'fdbus/fdobjects']
)
