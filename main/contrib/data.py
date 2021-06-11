#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Data pre-processing functions.

2021-06-07 11:52:21 EDT
Tong Zhang <zhangt@frib.msu.edu>
"""

from getpass import getuser
from pandas import DataFrame
import numpy as np
import pathlib
import json

CDIR_PATH = pathlib.Path(__file__).parent
with open(CDIR_PATH.joinpath("template.json"), "r") as fp:
    TEMP_AS_JSON_DATA = json.load(fp)


def to_image_tuple(df: DataFrame, nan_as_num: float=None, **kws) -> tuple:
    """Process the spectrum data of x, y, v to three 2D array that
    could be visualized in `mpl4qt.MatplotlibImageWidget`.

    Parameters
    ----------
    df : DataFrame
        Data of spectrum with x, y, v columns.
    nan_as_num : float
        Fill empty with nan (default) or a defined number.

    Keyword Arguments
    -----------------
    x : ndarray
        1D array for x axis, use df.x to build by default.
    y : ndarray
        1D array for y axes, use df.y to build by default.

    Returns
    -------
    r : tuple
        A tuple of ndarray for MatplotlibImageWidget, ``(xx, yy, zz)``,
        with the same shape, ``zz`` could be used to update the image,
        ``xx`` and ``yy`` are 2D array for extent.
    """
    if nan_as_num is None:
        vfill = np.nan
    else:
        vfill = nan_as_num
    x = kws.get('x', np.arange(df.x.max() + 1))
    y = kws.get('y', np.arange(df.y.max() + 1))
    xx, yy = np.meshgrid(x, y)
    zz = np.empty(xx.shape)
    zz.fill(vfill)
    def _f(irow):
        zz[int(irow.y)][int(irow.x)] = irow.v
    df.apply(_f, axis=1)
    return xx, yy, zz


def export_spectrum_for_allison(filepath, spectrum, energy : float=1.022487) -> None:
    """Generate a json data file from 2D spectrum of transverse phase space for Allison scanner
    app to calculate the emittance and Twiss parameter.

    Parameters
    ----------
    filepath : str
        File path for the output json data file.
    spectrum : Spectrum
        Spectrum object retrieved by DataClient.get_spectrum().
    energy : float
        Particle energy in keV.
    """
    xx, yy, zz = spectrum.to_image_tuple(nan_as_num=0)
    ek = energy
    ek0 = 1022.487 # [eV], where 1 mrad -> 1V
    # xx in mm
    xstep = (xx[0,:][-1] - xx[0,:][0]) / (len(xx[0,:]) - 1)
    # yy in mrad --> in volt (1 mrad --> 1 V)
    vv = yy * (ek * 1000.0 / ek0)
    vstep = (vv[:,0][-1] - vv[:,0][0]) / (len(vv[:, 0]) - 1)
    # update data
    data = TEMP_AS_JSON_DATA.copy()
    data['position'] = {'end': xx.max(), 'begin': xx.min(), 'step': xstep}
    data['voltage'] = {'end': vv.max(), 'begin': vv.min(), 'step': vstep}
    data['data']['shape'] = zz.shape
    data['data']['array'] = zz.tolist()
    data['Beam Source'] = {'Ek': ek * 1000, 'Ion Name': 'Ar', 'A': 40, 'Q': 9}
    path = pathlib.Path(filepath)
    data['info']['user'] = getuser()
    data['note'] = f"Generated phase space data from {spectrum.name} spectrum, the voltage array is created from xp with the spec of FRIB allison scanner device, only for interfacing purpose."
    try:
        fullpath = path.expanduser().resolve()
        with open(fullpath, 'w') as fp:
            json.dump(data, fp, indent=2)
    except:
        print("Failed to export.")
    else:
        print(f"Exported spectrum to {fullpath}.")
