from distutils.extension import Extension
from Cython.Distutils import build_ext
import sdss3tools
import os.path
import numpy

ac62kusb = Extension(
    'ac62kusb',
    ['ac62kusb/cython/ac62kusb.pyx'],
    library_dirs = ['ac62kusb/c'],
    libraries = ['minicamera'],
    include_dirs = [
        'ac62kusb/c',
        'ac62kusb/cython',
        numpy.get_include(),
    ],
)

sdss3tools.setup(
    name = 'fcc',
    description = "Field center camera actor.",
    cmdclass = {"build_ext": build_ext},
    ext_modules = [ac62kusb],
)

