from spectcl.client import *

__version__ = '0.0.3'
__author__ = 'Tong Zhang <zhangt@frib.msu.edu>'
__name__ = "PySpecTcl"
__doc__ ="""Python interface to SpecTcl REST server."""

def info():
    print(f"{__name__} (v{__version__}): {__doc__}\nDeveloped by: {__author__}")
