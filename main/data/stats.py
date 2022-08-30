#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import math


def weighted_stats(x: pd.Series, w: pd.Series, ddof: int = 0) -> dict:
    """Return a dict of weighted stats of input array *x*.

    Parameters
    ----------
    x : pd.Series
        Array of values.
    w : pd.Series
        Array of weights.
    ddof : int
        Delta degrees of freedom, see `numpy.std()`.

    Returns
    -------
    r : dict
        Keys: 'sum' (sum of *w*), 'mean' (weighted average of *x*), 'std' (weighted std of *x*),
        'fwhm' (~2.355std, assuming Gaussian distribution).
    """
    n = x.size
    # weighted average
    xavg_w = (x * w).sum() / w.sum()
    # weighted standard deviation
    xstd_w = ((w * (x - xavg_w)**2).sum() / (w.sum() * (n - ddof) / n))**0.5
    #
    return {
        'sum': w.sum(),
        'mean': xavg_w,
        'std': xstd_w,
        'fwhm': xstd_w * 2 * (2 * math.log(2))**0.5
    }
