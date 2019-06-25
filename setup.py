from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize



#pxds = Extension("cgt/*", ["cgt/*.pxd"])
pyxs = Extension("cgt/*", ["cgt/*.pyx"])
exts = [pyxs]#, pxds]

setup(ext_modules=cythonize(exts))
