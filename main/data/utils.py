# -*- coding: utf-8 -*-

import toml
import numpy as np
import pathlib
from requests.adapters import HTTPAdapter

CDIR_PATH = pathlib.Path(__file__).parent

DTYPE_MAP = {
    'short': np.dtype('i'),  # int8
    'word': np.dtype('i2'),  # int16
    'long': np.dtype('i4'),  # int32
}
STYPE_MAP = {
    '1': '1D',
    '2': '2D',
    's': 's',
}
STYPE_MAP_ = {v: k for k, v in STYPE_MAP.items()}
DTYPE_MAP_ = {v: k for k, v in DTYPE_MAP.items()}


class MyAdapter(HTTPAdapter):
    pass
    # def init_poolmanager(self, connections, maxsize, block=False, **kws):
    #    self.pool


def make_response(r):
    if r.ok and r.json()['status'] == 'OK':
        return r.json().get('detail', 'OK but no details')
    else:
        raise NotFoundSpecTclDataError


class NotFoundSpecTclDataError(Exception):
    def __init__(self):
        super(self.__class__, self).__init__()


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

GATE_APPLY_MAP = {
    '-TRUE-': 'ungated'  # ungated
}


def is_nan(x):
    # test if *x* is nan once when x is a float number.
    if not isinstance(x, float):
        return False
    return np.isnan(x)