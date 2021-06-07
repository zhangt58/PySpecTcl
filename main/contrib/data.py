#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Data pre-processing functions.

2021-06-07 11:52:21 EDT
Tong Zhang <zhangt@frib.msu.edu>
"""

import pandas as pd
import numpy as np


def to_image_tuple(df: DataFrame) -> tuple:
    """Process the spectrum data of x, y, v to three 2D array that
    could be visualized in `mpl4qt.MatplotlibImageWidget`.

    Parameters
    ----------
    df : DataFrame
        Data of spectrum with x, y, v columns.

    Returns
    -------
    r : tuple
        A tuple of ndarray for MatplotlibImageWidget, ``(xx, yy, zz)``,
        with the same shape, ``zz`` could be used to update the image,
        ``xx`` and ``yy`` are 2D array for extent.
    """
    x = np.arange(df.x.max() + 1)
    y = np.arange(df.y.max() + 1)
    xx, yy = np.meshgrid(x, y)
    zz = np.empty(xx.shape)
    zz.fill(np.nan)
    def _f(irow):
        zz[int(irow.y)][int(irow.x)] = irow.v
    df.apply(_f, axis=1)
    return xx, yy, zz

