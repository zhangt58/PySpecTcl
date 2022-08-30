# -*- coding: utf-8 -*-

import toml
import matplotlib.pyplot as plt
import numpy as np
import pathlib
from functools import partial
from requests.adapters import HTTPAdapter
from spectcl.contrib import to_image_tuple
from .stats import weighted_stats
from .plot import plot_image

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
    client : SpecTclClient
        SpecTclClient instance.
    """
    def __init__(self, name, conf, data, **kws):
        self._axes_values_channel = [
        ]  # list of arrays for all axes in channel coordinate
        self._axes_values_world = [
        ]  # list of arrays for all axes in world coordinate
        self._axes_map_fn = []  # list of func to map channel to world
        self.name = name  # == conf.index.values[0]
        self.data = data  # update self._axes_values_channel
        self.parameters = conf.Parameters
        self.axes = conf.Axes
        self.stype = conf.Type
        self.dtype = conf.ChanType
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

    def get_data(self, map=True):
        """Return the table of spectral data.

        Parameters
        ----------
        map : bool
            If True, return mapped coordinate from channel to world.

        Returns
        -------
        df : DataFrame
        """
        if map:
            # return a dataframe with mapped data (world coordinate), name column with parameter
            return self._data[self.parameters + ['count']]
        else:
            # return x, [y], count columns of channel coordinate
            df = self._data.loc[:, ~self._data.columns.isin(self.parameters)]
            count_col = df.pop('count')
            df.insert(len(df.columns), 'count', count_col)
            return df

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

    def map_data(self):
        """Map data from channel coordinate to world coordinate, add as new columns.
        """
        self._axes_values_world = []
        self._axes_map_fn = []
        for ax, v in zip(self.axes, self._axes_values_channel):
            low, high, bins = ax['low'], ax['high'], ax['bins']
            self._axes_values_world.append(low + v * (high - low) / bins)
            self._axes_map_fn.append(partial(_map_fn, low, high, bins))

        # add column(s) for world coordinate data.
        for u, p, fn in zip(('x', 'y'), self.parameters, self._axes_map_fn):
            self._data[p] = self._data[u].apply(fn)
        #
        self._data.rename(columns={'v': 'count'}, inplace=True)
        self._data.index.name = 'id'

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

    def plot(self,
             ax=None,
             show_colorbar=True,
             show_profile=True,
             show_grid=True,
             fillna=True,
             mapped=True,
             **kws):
        """Plot spectrum data.

        Parameters
        ----------
        ax : Axes
            Axes object (1D only)
        show_colorbar : bool
            If show colorbar or not.
        show_profile : bool
            If show x,y profile or not.
        show_grid : bool
            If show grid on x,y profile plots (1D plot) or not.
        fillna : bool
            If fill empty count as nan, otherwise fill with zero.
        mapped : bool
            If show data in mapped coordinate (world), otherwise show in channel coordinate.

        Keyword Arguments
        -----------------
        xlim : tuple
            Limit range along x axis.
        ylim : tuple
            Limit range along y axis.
        figsize : tuple
            Tuple of figure width and height, default is (10, 8).
        fontsize : int
            Font size, default is 12 (1D only).
        cmap : str
            Colormap name for 2D plot, default is 'viridis'.
        legend : bool
            If show legend or not for 1D plot, default is False.
        ds : str
            Draw line style for 1D plot, default is 'steps'.
        and other matplotlib.pyplot.plot() arguments.

        Returns
        -------
        r : Axes, List[Axes]
            Axes for 1D, and (ax_image, ax_xprofile, ax_yprofile) for 2D spectrum.
        """
        figsize = kws.pop('figsize', (10, 8))
        fontsize = kws.pop('fontsize', 12)
        xlim = kws.pop('xlim', None)
        ylim = kws.pop('ylim', None)
        if self.stype == '2D':
            _, (ax_im, ax_xprof,
                ax_yprof) = plot_image(self,
                                       show_profile,
                                       show_colorbar,
                                       show_grid,
                                       fillna,
                                       mapped,
                                       figsize=figsize,
                                       cmap=kws.pop('cmap', 'viridis'),
                                       **kws)
            ax_im.set_xlim(xlim)
            ax_im.set_ylim(ylim)
            return (ax_im, ax_xprof, ax_yprof)
        elif self.stype == '1D':
            if ax is None:
                _, ax = plt.subplots()
            xcol, = self.parameters
            r = self.get_data().plot(kind='line',
                                     x=xcol,
                                     y='count',
                                     ax=ax,
                                     grid=show_grid,
                                     figsize=figsize,
                                     legend=kws.pop('legend', False),
                                     **kws)
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.set_xlabel(xcol, fontsize=fontsize)
            ax.set_ylabel('Count', fontsize=fontsize)
            ax.set_title(self.name, fontsize=fontsize + 2)
            ax.lines[0].set_drawstyle(kws.get('ds', 'steps'))
            return r
        else:
            return None


def _map_fn(low, high, bins, ch):
    return low + ch * (high - low) / bins


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
