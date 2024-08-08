#!/usr/bin/env python3

from distutils.core import setup
from Cython.Build import cythonize
import numpy
setup(ext_modules=cythonize('network.pyx'), include_dirs=[numpy.get_include()])
setup(ext_modules=cythonize('result.pyx'), include_dirs=[numpy.get_include()])
