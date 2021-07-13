# -*- coding: utf-8 -*-

import toml
import matplotlib.pyplot as plt
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
    """Class for spectrum configuration and data.

    Parameters
    ----------
    name : str
        Name of the spectrum.
    conf : DataFrame
        Spectrum definition, columns: Type, Parameters, Axes, ChanType.
    data : DataFrame
        Spectrum contents, columns of x, v or x, y, v.

    Keyword Arguments
    -----------------
    map : bool
        If do coordinate mapping from channel to world, by default is True.
    client : SpecTclClient
        SpecTclClient instance.
    """
    def __init__(self, name, conf, data, **kws):
        self._axes_values_channel = [] # list of arrays for all axes in channel coordinate
        self._axes_values_world = []   # list of arrays for all axes in world coordinate
        self._axes_map_fn = []         # list of func to map channel to world
        self.name = name # == conf.index.values[0]
        self.data = data
        self.parameters = conf.Parameters
        self.axes = conf.Axes
        self.stype = conf.Type
        self.dtype = conf.ChanType
        # map axes?
        if kws.get('map', True):
            self.map_data()
        # client
        self.client = kws.get('client', None)

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
        """DataFrame : Table of the spectral contents (channel coordinate).
        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        if 'x' in data:
            _x = np.arange(data.x.max() + 1)
            self._axes_values_channel.append(_x)
        if 'y' in data:
            _y = np.arange(data.y.max() + 1)
            self._axes_values_channel.append(_y)

    def get_axes_values(self, map=True):
        """Return a list of value of array for all axes.
        """
        if map:
            return self._axes_values_world
        else:
            return self._axes_values_channel

    def get_data(self, map=True, with_label=True):
        """Return the table of spectral data.

        Parameters
        ----------
        map : bool
            If do coordinate mapping from channel to world, by default is True.
        with_label : bool
            If set, return the table with expected column names, by default is True.
        """
        if map:
            _d = self._data.copy()
            for ax_name, fn in zip(('x', 'y'), self._axes_map_fn):
                _d[ax_name] = _d[ax_name].apply(fn)
            r = _d
        else:
            r = self._data
        if with_label:
            r.rename(columns=dict(zip(('x', 'y'), self.parameters)), inplace=True)
            r.rename(columns={'v': 'count'}, inplace=True)
        return r

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

    def to_image_tuple(self, **kws):
        """Return spectral data as the tuple of x,y,z image.

        Parameters
        ----------
        nan_as_num : float
            Fill empty with nan (default) or a defined number.
        map : bool
            If do coordinate mapping from channel to world, by default is True.

        Returns
        -------
        r : tuple
            A tuple of ndarray for MatplotlibImageWidget, ``(xx, yy, zz)``,
            with the same shape, ``zz`` could be used to update the image,
            ``xx`` and ``yy`` are 2D array for extent, or None.

        See Also
        --------
        :func:`~spectcl.to_image_tuple`
        """
        if self.stype != '2D':
            print(f"Spectrum {self.name} is not 2D type.")
            return None
        if kws.pop('map', True):
            _x, _y = self._axes_values_world
        else:
            _x, _y = self._axes_values_channel
        return to_image_tuple(self.data, x=_x, y=_y, **kws)

    def map_data(self, **kws):
        """Map data from channel coordinate to world coordinate.

        Keyword Arguments
        -----------------
        force : bool
            If set, refresh the world coordinate values, otherwise override the existing one.
        """
        if kws.get('force', False):
            return self._axes_values_world
        self._axes_values_world = []
        self._axes_map_fn = []
        for ax, v in zip(self.axes, self._axes_values_channel):
            low, high, bins = ax['low'], ax['high'], ax['bins']
            self._axes_values_world.append(low + v * (high - low) / bins)
            self._axes_map_fn.append(lambda ch: low + ch * (high - low) / bins)

    def del_gate(self):
        pass

    def set_gate(self, gate: str):
        """Set/update with *gate*.
        """
        if self.client is None:
            print(f"Cannot apply '{gate}'")
            return None
        self.client._apply_client.apply(self.name, gate)

    def get_gate(self):
        """Return applied gate.
        """
        if self.client is None:
            return None
        applied_gate = self.client._apply_client.list().loc[self._name].gate
        if applied_gate == '-TRUE-':
            return None
        return self.client._gate_client.list().loc[applied_gate]

    gate = property(get_gate, set_gate, del_gate, "Gate")

    def plot(self, ax=None, **kws):
        """Plot spectrum data.
        """
        if ax is None:
            _, ax = plt.subplots()
        figsize = kws.pop('figsize', (10, 8))
        fontsize = kws.pop('fontsize', 12)
        if self.stype == '2D':
            xcol, ycol = self.parameters
            r = self.get_data().plot(kind='scatter', x=xcol, y=ycol,
                                     c='count', s=kws.pop('s', 4), cmap=kws.pop('cmap', 'jet'),
                                     ax=ax, figsize=figsize, **kws)
            ax.set_xlabel(xcol, fontsize=fontsize)
            ax.set_ylabel(ycol, fontsize=fontsize)
            ax.set_title(self.name, fontsize=fontsize + 2)
            return r
        elif self.stype == '1D':
            xcol, = self.parameters
            r = self.get_data().plot(kind='line', x=xcol, y='count', ax=ax, figsize=figsize,
                                     legend=kws.pop('legend', False), **kws)
            ax.set_xlabel(xcol, fontsize=fontsize)
            ax.set_ylabel('Count', fontsize=fontsize)
            ax.set_title(self.name, fontsize=fontsize + 2)
            ax.lines[0].set_drawstyle(kws.get('ds', 'steps'))
            return r
        else:
            return None


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
