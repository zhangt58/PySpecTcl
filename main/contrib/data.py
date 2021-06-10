#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Data pre-processing functions.

2021-06-07 11:52:21 EDT
Tong Zhang <zhangt@frib.msu.edu>
"""

from pandas import DataFrame
import numpy as np


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

