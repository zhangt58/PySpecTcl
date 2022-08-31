# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

class Gate:
    """Class for gate configuration and data.
    
    Parameters
    ----------
    conf : pd.Series
        Gate configuration, referenced from `client.list('gate')`,
        including the value of attributes of 'Type', 'Gates', 'Parameters', 'Points', 'Desc'.
    """
    def __init__(self, conf: pd.Series):
        self.name = conf.name
        self._type = conf.Type  # raw type string
        self.type = conf.Desc   # interpret raw string
        self.gates = None if _is_nan(conf.Gates) else conf.Gates # a list of related gate names
        self.parameters = None if _is_nan(conf.Parameters) else conf.Parameters
        self.points = None if _is_nan(conf.Points) else conf.Points
    
    def __str__(self):
        if self.gates is None: 
            s = f"Gate '{self.name}': '{self.type}' on parameters {self.parameters}"
            if self.type == 'Contour':
                s += f" of ({len(self.points)}) points"
            return s
        else:
            return f"Gate '{self.name}': '{self.type}' on gates {self.gates}"
    __repr__ = __str__
    

def _is_nan(x):
    # test if *x* is nan once when x is a float number.
    if not isinstance(x, float):
        return False
    return np.isnan(x)
    
