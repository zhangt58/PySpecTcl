# -*- coding: utf-8 -*-

import toml
import numpy as np
import pathlib
from requests.adapters import HTTPAdapter
from spectcl.contrib import to_image_tuple

CDIR_PATH = pathlib.Path(__file__).parent


DTYPE_MAP = {
    'short': np.dtype('i'),  # int8
    'word': np.dtype('i2'),  # int16
    'long': np.dtype('i4'),  # int32
}
STYPE_MAP = {
    '1' : '1D',
    '2' : '2D',
    's' : 's',
}

class MyAdapter(HTTPAdapter):
    pass
    # def init_poolmanager(self, connections, maxsize, block=False, **kws):
    #    self.pool


def make_response(r):
    if r.ok and r.json()['status'] == 'OK':
        return r.json()['detail']
    else:
        raise NotFoundSpecTclDataError


class NotFoundSpecTclDataError(Exception):
    def __init__(self):
        super(self.__class__, self).__init__()


class Spectrum(object):
    """Spectrum class, including:
    - configuration, or definition
    - parameters
    - type
    - axes
    - data, x, v or x, y, v
    """
    def __init__(self, name, conf, data, **kws):
        self.name = name
        self.data = data
        self.parameters = conf.Parameters
        self.axes = conf.Axes
        self.stype = conf.Type
        self.dtype = conf.ChanType

    @property
    def name(self):
        """str : Name of spectrum.
        """
        return self._name

    @name.setter
    def name(self, s):
        self._name = s

    @property
    def data(self):
        """DataFrame : Table of the spectral contents.
        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def parameters(self):
        """List : Parameters.
        """
        return self._parameters

    @parameters.setter
    def parameters(self, params):
        self._parameters = params

    @property
    def axes(self):
        """List : Axes.
        """
        return self._axes

    @axes.setter
    def axes(self, ax):
        self._axes = ax

    @property
    def stype(self):
        """str : Spectral type.
        """
        return self._stype

    @stype.setter
    def stype(self, s):
        self._stype = STYPE_MAP[s]

    @property
    def dtype(self):
        """dtype : Spectral channel type.
        """
        return self._dtype

    @dtype.setter
    def dtype(self, d: str):
        self._dtype = DTYPE_MAP[d]

    def __str__(self):
        return f"Spectrum '{self.name}': [{len(self.parameters)}] parameters, [{self.data.shape[0]}] entries."

    __repr__ = __str__
    def _repr_html_(self, *args, **kws):
        dfhtml = self._data._repr_html_(*args, **kws)
        return f'<h4>{str(self)}</h4>' + '<br>' + dfhtml

    def to_image_tuple(self):
        """Return spectral data as the tuple of x,y,z image.
        """
        return to_image_tuple(self.data)


ACTION_PARAMS = toml.load(CDIR_PATH.joinpath("action.toml"))

SPEC_NAME_MAP = {
    'name': 'Name',
    'type': 'Type',
    'parameters': 'Parameters',
    'axes': 'Axes',
    'chantype': 'ChanType'
}

GATE_NAME_MAP = {
    'name': 'Name',
    'type': 'Type',
    'parameters': 'Parameters',
    'low': 'Low',
    'high': 'High',
    'points': 'Points',
    'gates': 'Gates'
}

GATE_TYPE_MAP = {
    '+': 'Or',
    '-': 'Not',
    '*': 'And',
    's': 'Slice',
    'b': 'Band',
    'c': 'Contour',
    'gs': 'Gamma Slice',
    'gb': 'Gamma Band',
    'gc': 'Gamma Contour',
    'em': 'Equal Mask',
    'am': 'And Mask',
    'nm': 'Andnot Mask',
    'T': 'True',
    'F': 'False'
}
