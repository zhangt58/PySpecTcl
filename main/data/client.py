# -*- coding: utf-8 -*-

import pandas as pd
import requests
from simplejson import JSONDecodeError

from .utils import make_response
from .utils import ACTION_PARAMS


DEFAULT_APP_NAME = 'spectcl'
DEFAULT_BASE_URL = 'http://127.0.0.1'
DEFAULT_PORT_NUMBER = 8000
DEFAULT_GROUP_NAME = 'spectrum'

JSON_HEADERS = {"Content-Type": "application/json"}


class SpecTclDataClient(object):
    """Client for data retrieval.

    Parameters
    ----------
    base_url : str
        Base url for data retrieval API, default is 'http://127.0.0.1'.
    port : int
        Port number for service, default is 8000.
    group : str
        Service group name, default is 'spectrum'.
    """
    def __init__(self, base_url=DEFAULT_BASE_URL,
                 port=DEFAULT_PORT_NUMBER, group=DEFAULT_GROUP_NAME,
                 name=DEFAULT_APP_NAME):
        self.name = name
        self._base_url = base_url
        self._port = port
        self._group = group
        self.update_base_uri()
        #
        self._vlist_cache = self.list()

    @property
    def name(self):
        return self._name  # default is spectcl

    @name.setter
    def name(self, s):
        if s is None:
            self._name = DEFAULT_APP_NAME
        else:
            self._name = s

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, i):
        self._port = i
        self.update_base_uri()

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, s):
        self._group = s
        self.update_base_uri()

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, s):
        self._base_url = s
        self.update_base_uri()

    def update_base_uri(self):
        """Update base uri.
        """
        self._base_uri = f"{self.base_url}:{self.port}/{self.name}/{self.group}"

    def get(self, action, **action_params):
        """Retrieve data from SpecTcl service, return as a dict.

        Parameters
        ----------
        action : str
            Action name.

        Keyword Argumetns
        -----------------
        action_params : str
            Supported action parameter configs.

        Returns
        -------
        r : dict
            Pack retrieval as dict.
        """
        is_valid = self.validate_action(action, action_params)
        if not is_valid:
            return
        url = self._base_uri + '/' + action
        r = requests.get(url, params=action_params, verify=False)
        return make_response(r)

    def list(self, **kws):
        """List defined spectra.

        Keyword Arguments
        -----------------
        filter : str
            Unix wildcard pattern as the name filter.
        update_cache : bool
            If set, update the cached value for spectrum configurations.

        Returns
        -------
        r : DataFrame
            Table of spectrum configurations.
        """
        r = self.get("list", **kws)
        df = pd.DataFrame(columns=['Name', 'Type', 'Parameters', 'Axes', 'ChanType'])
        for i, v in enumerate(r):
            df.loc[i] = v['name'], v['type'], v['parameters'], v['axes'], v['chantype']
        df.set_index('Name', inplace=True)
        if kws.get('update_cache', False):
            self._vlist_cache = df
        return df

    def contents(self, name, **kws):
        """Return the data of spectrum named *name*.

        Parameters
        ----------
        name : str
            Name of the spectrum.

        Keyword Arguments
        -----------------
        refresh_cache : bool
            If set, refresh the cache of spectra info.
        """
        try:
            data = self.get("contents", name=name, **kws)
        except JSONDecodeError:
            return None
        else:
            df = pd.DataFrame.from_dict(data['channels'])
            if kws.get('refresh_cache', False):
                self.list()
            spec_conf = self._vlist_cache.loc[name]
            params = spec_conf.Parameters
            if len(params) == 1: # type '1'
                df.rename(columns={'x': params[0], 'v': 'count'}, inplace=True)
            elif len(params) == 2: # type '2'
                df.rename(columns={'x': params[0], 'y': params[1], 'v': 'count'}, inplace=True)
            return df

    def validate_action(self, action, action_params):
        params = ACTION_PARAMS[self._group][action]
        for i in action_params:
            if i not in params:
                print('-- {} is not a valid action parameter.'.format(i))
                print("-- Valid action Parameters of {}: {}".format(self._group, ','.join(params)))
                return False
        return True


    def __repr__(self):
        return "[Data Client] SpecTcl REST Service on: {}:{}/spectcl".format(self._base_url, self._port)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    c = SpecTclDataClient()
    print(c)

    data1 = c.get('contents', name='s1')
    df = DataFrame.from_dict(data1['channels'])
    df.plot(x='x', y='v')

    data2 = c.get('contents', name='s2')
    df = DataFrame.from_dict(data2['channels'])
    df.plot()

    plt.show()
