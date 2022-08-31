# -*- coding: utf-8 -*-
import numpy as np


def is_nan(x):
    # test if *x* is nan once when x is a float number.
    if not isinstance(x, float):
        return False
    return np.isnan(x)