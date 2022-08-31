# -*- coding: utf-8 -*-

import pandas as pd
from matplotlib.patches import Polygon

from .utils import is_nan


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
        self.gates = None if is_nan(conf.Gates) else conf.Gates # a list of related gate names
        self.parameters = None if is_nan(conf.Parameters) else conf.Parameters
        self.points = None if is_nan(conf.Points) else conf.Points
    
    def __str__(self):
        if self.gates is None: 
            s = f"Gate '{self.name}': '{self.type}' on parameters {self.parameters}"
            if self.type == 'Contour':
                s += f" of ({len(self.points)}) points"
            return s
        else:
            return f"Gate '{self.name}': '{self.type}' on gates {self.gates}"
    __repr__ = __str__

    def draw(self, ax, color='r', **kws):
        """Draw the gate onto *ax*.

        Keyword Arguments
        -----------------
        color : str
            Edge color.
        alpha : float
            Alpha of drawing.
        ls : str
            Line style.
        lw : str
            Line width.
        
        Returns
        -------
        o :
            A drawing artist object.
        """
        if self.type == "Contour":
            pts = [list(p.values()) for p in self.points]
            polygon1 = Polygon(pts, fill=False, ec=color,
                       alpha=kws.get('alpha', 0.8), ls=kws.get('ls', '--'),
                       lw=kws.get('lw', 1.0))
            ax.add_patch(polygon1)
            return polygon1