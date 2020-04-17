"""
@author:
        Mohammad Kabajah
@Contact:
        kabajah.mohammad@gmail.com
@date:
        April 28, 2019
@Purpose:
    setup script
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='testparams',
    version='0.0.1',
    author='Mohammad Kabajah',
    author_email='kabajah.mohammad@gmail.com',
    maintainer='Mohammad Kabajah',
    description='Test parameters plugin for pytest.',
    long_description=read('README_SPIRATEST.md'),
    py_modules=['test_parameters_pytest'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=['pytest>=3.5.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points={
        'pytest11': [
            'testparams = testparams',
        ],
    },
)
