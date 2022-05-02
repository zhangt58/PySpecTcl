from spectcl.client import *
from spectcl.contrib import *
from spectcl.data import Spectrum

__version__ = '0.3.2'
__author__ = 'Tong Zhang <zhangt@frib.msu.edu>'
__name__ = "PySpecTcl"
__doc__ ="""Python interface to SpecTcl REST server."""

def info():
    print(f"{__name__} (v{__version__}): {__doc__}\nContact: {__author__}")
