from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

pxds = Extension("Mark3/*",["Mark3/*.pxd"])
pyxs = Extension("Mark3/*",["Mark3/*.pyx"])
exts = [pyxs, pxds]

setup(ext_modules = cythonize(exts))