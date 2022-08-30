#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import math


def weighted_stats(x: pd.Series, w: pd.Series, y: pd.Series = None ) -> dict:
    """Return a dict of weighted stats of input array *x* and *y*.

    Parameters
    ----------
    x : pd.Series
        Array of values.
    w : pd.Series
        Array of weights.
    y : pd.Series
        Another array of values.

    Returns
    -------
    r : dict
        Keys: 'sum' (sum of *w*), 'mean' (weighted average of *x*), 'std' (weighted std of *x*),
        'fwhm' (~2.355std, assuming Gaussian distribution).
    """
    def m(x, w):
        # weighted mean
        return (x * w).sum() / w.sum()
    def cov(x, y, w):
        # weighted covariance
        return (w * (x - m(x, w)) * (y - m(y, w))).sum() / w.sum()
    def corr(x, y, w):
        # weighted correlation
        return cov(x, y, w) / (cov(x, x, w) * cov(y, y, w)) ** 0.5

    # std to fwhm, assuming Gaussian distribution
    fac = 2 * (2 * math.log(2))**0.5

    xavg_w = m(x, w)
    # weighted standard deviation
    xstd_w = cov(x, x, w) ** 0.5
    fwhm_x = xstd_w * fac
        
    if y is not None:
        yavg_w = m(y, w)
        ystd_w = cov(y, y, w) ** 0.5
        fwhm_y = ystd_w * fac
        rho = corr(x, y, w)
        #
        return {
            'sum': w.sum(),
            'mean': (xavg_w, yavg_w),
            'std': (xstd_w, ystd_w),
            'fwhm': (fwhm_x, fwhm_y),
            'rho': rho
        }
    #
    return {
        'sum': w.sum(),
        'mean': xavg_w,
        'std': xstd_w,
        'fwhm': fwhm_x,
    }
