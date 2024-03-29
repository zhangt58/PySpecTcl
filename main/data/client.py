# -*- coding: utf-8 -*-

import pandas as pd
import requests
from simplejson import JSONDecodeError

from .gate import Gate
from .spectrum import Spectrum
from .utils import ACTION_PARAMS
from .utils import make_response
from .utils import GATE_NAME_MAP
from .utils import GATE_TYPE_MAP
from .utils import SPEC_NAME_MAP
from .utils import GATE_APPLY_MAP
from .utils import DTYPE_MAP_
from .utils import STYPE_MAP_

DEFAULT_APP_NAME = 'spectcl'
DEFAULT_BASE_URL = 'http://127.0.0.1'
DEFAULT_PORT_NUMBER = 8000
DEFAULT_GROUP_NAME = 'spectrum'

VALID_GROUP_LIST = ['spectrum', 'gate', 'apply']

JSON_HEADERS = {"Content-Type": "application/json"}


class _BaseClient(object):
    """BaseClient

    Parameters
    ----------
    base_url : str
        Base url for data retrieval API, default is 'http://127.0.0.1'.
    port : int
        Port number for service, default is 8000.
    """
    def __init__(self,
                 base_url=DEFAULT_BASE_URL,
                 port=DEFAULT_PORT_NUMBER,
                 name=DEFAULT_APP_NAME,
                 group=DEFAULT_GROUP_NAME):
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
    def group(self):
        return self._group

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, i):
        self._port = i
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

    def get(self, action, raw=False, **action_params):
        """Retrieve data from SpecTcl service, return as a dict.

        Parameters
        ----------
        action : str
            Action name.
        raw : bool
            if set returns raw response.

        Keyword Argumetns
        -----------------
        action_params : str
            Supported action parameter configs.

        Returns
        -------
        r : dict
            Pack retrieval as dict.
        """
        p = {
            k: v
            for k, v in action_params.items() if k not in ('refresh_cache', )
        }
        is_valid = self.validate_action(action, p)
        if not is_valid:
            return
        url = self._base_uri + '/' + action
        r = requests.get(url, params=action_params, verify=False)
        if raw:
            return r
        else:
            return make_response(r)

    def validate_action(self, action, action_params):
        params = ACTION_PARAMS[self._group][action]
        for i in action_params:
            if i not in params['arg']:
                print('-- {} is not a valid action parameter.'.format(i))
                print("-- Valid action Parameters of {}: {}".format(
                    self._group, ','.join(params)))
                return False
        return True

    def __repr__(self):
        return f"[Data Client] SpecTcl REST Service on: {self._base_uri}"


class SpecTclSpectrumClient(_BaseClient):
    """Client for spectrum API.
    """
    def __init__(self,
                 base_url=DEFAULT_BASE_URL,
                 port=DEFAULT_PORT_NUMBER,
                 name=DEFAULT_APP_NAME):
        super(self.__class__, self).__init__(base_url, port, name, "spectrum")

    def list(self, **kws):
        """List defined spectra.

        Keyword Arguments
        -----------------
        filter : str
            Unix wildcard pattern as the name filter.
        refresh_cache : bool
            If set, update the cached value for spectrum configurations.

        Returns
        -------
        r : DataFrame
            Table of spectrum configurations.
        """
        r = self.get("list", **kws)
        if r == []:
            return None
        df = pd.DataFrame.from_records(r)
        df.rename(columns=SPEC_NAME_MAP, inplace=True)
        df.set_index('Name', inplace=True)
        if kws.get('refresh_cache', False):
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
        as_raw : bool
            If set, return data with original column names.
        refresh_cache : bool
            If set, refresh the cache of spectra info.
        Other arguments that client.get('contents') supports.
        """
        as_raw = kws.pop('as_raw', False)
        refresh_cache = kws.pop('refresh_cache', False)
        try:
            data = self.get("contents", name=name, **kws)
        except JSONDecodeError:
            return None
        else:
            df = pd.DataFrame.from_dict(data['channels'])
            self.list(refresh_cache=refresh_cache)
            spec_conf = self._vlist_cache.loc[name]
            if not as_raw:
                params = spec_conf.Parameters
                if len(params) == 1:  # type '1'
                    df.rename(columns={
                        'x': params[0],
                        'v': 'count'
                    },
                              inplace=True)
                elif len(params) == 2:  # type '2'
                    df.rename(columns={
                        'x': params[0],
                        'y': params[1],
                        'v': 'count'
                    },
                              inplace=True)
            return df

    def parameters(self, name):
        """Convenient method to return the parameters of a spectrum defined
        by *name*.

        Parameters
        ----------
        name : str
            Name of spectrum configuration.

        Returns
        -------
        r : list
            A list of parameters, return None for non-existing spectrum.
        """
        try:
            conf = self._vlist_cache.loc[name]
        except KeyError:
            return None
        else:
            return conf.Parameters

    def create(self, name, type, parameters, axes, **kws):
        """Create a new spectrum.

        Parameters
        ----------
        name : str
            The name of the new spectrum.
        type : str
            Spectrum type.
        parameters : list
            A list of parameters.
        axes : str
            Axes definition.
        
        Keyword Arguments
        -----------------
        chantype : str
            Channel type, default is long.
        """
        params = {
            'name': name,
            'type': type,
            'parameters': parameters,
            'axes': axes,
            'chantype': kws.get('chantype', 'long')
        }
        r = self.get("create", **params)
        if r != 'OK but no details':
            return None
        else:
            # refresh cache
            self.list(refresh_cache=True)
            return r


class SpecTclGateClient(_BaseClient):
    """Client for gate service group.
    """
    def __init__(self,
                 base_url=DEFAULT_BASE_URL,
                 port=DEFAULT_PORT_NUMBER,
                 name=DEFAULT_APP_NAME):
        super(self.__class__, self).__init__(base_url, port, name, "gate")

    def list(self, **kws):
        """List defined gates.

        Keyword Arguments
        -----------------
        pattern : str
            Unix wildcard pattern as the name filter.
        refresh_cache : bool
            If set, update the cached value for gate configurations.

        Returns
        -------
        r : DataFrame
            Table of gate configurations.
        """
        r = self.get("list", **kws)
        if r == []:
            return None
        df = pd.DataFrame.from_records(r)
        df['Desc'] = df['type'].apply(lambda i: GATE_TYPE_MAP[i])
        df.rename(columns=GATE_NAME_MAP, inplace=True)
        df.set_index('Name', inplace=True)
        if kws.get('refresh_cache', False):
            self._vlist_cache = df
        return df


class SpecTclApplyClient(_BaseClient):
    """Client for apply service group. (gate application)
    """
    def __init__(self,
                 base_url=DEFAULT_BASE_URL,
                 port=DEFAULT_PORT_NUMBER,
                 name=DEFAULT_APP_NAME):
        super(self.__class__, self).__init__(base_url, port, name, "apply")

    def list(self, only_gated=False, **kws):
        """List gate applying status to a spectrum

        Parameters
        ----------
        only_gated : bool
            If set, only show gated spectra.

        Keyword Arguments
        -----------------
        pattern : str
            Unix wildcard pattern as the name filter.
        refresh_cache : bool
            If set, update the cached value for gate applications.

        Returns
        -------
        r : DataFrame
            Table of gate configurations.
        """
        r = self.get("list", **kws)
        df = pd.DataFrame.from_records(r)
        df['desc'] = df['gate'].apply(lambda i: GATE_APPLY_MAP.get(i, i))
        #df.rename(columns=GATE_NAME_MAP, inplace=True)
        df.set_index('spectrum', inplace=True)
        if kws.get('refresh_cache', False):
            self._vlist_cache = df
        if only_gated:
            return df.loc[df['gate'] != '-TRUE-']
        else:
            return df

    def apply(self, spectrum, gate, **kws):
        """Apply *spectrum* with *gate*.

        Returns
        r : bool
            True if applied, otherwise False.
        """
        r = self.get("apply", raw=True, spectrum=spectrum, gate=gate, **kws)
        if r.json()['status'] == 'OK':
            print(f"Applied {gate} to {spectrum}")
            return True
        print(f"Failed to apply {gate} to {spectrum}")
        return False


class SpecTclClient(object):
    """Data interface for data of spectrum, gate, apply info.

    Examples
    --------
    >>> from spectcl.client import Client
    >>> client = Client()
    >>> client.list("spectrum")
    >>> sp = client.get_spectrum("pid::fp.pin.dE_vs_tof.rf2!FPslits")
    >>> sp.gate
    >>> sp.gate = <gate name>
    """
    def __init__(self,
                 base_url=DEFAULT_BASE_URL,
                 port=DEFAULT_PORT_NUMBER,
                 name=DEFAULT_APP_NAME):
        self.name = name
        self._base_url = base_url
        self._port = port
        #
        self._spectrum_client = SpecTclSpectrumClient(base_url, port, name)
        self._gate_client = SpecTclGateClient(base_url, port, name)
        self._apply_client = SpecTclApplyClient(base_url, port, name)
        #
        self.__list_map = {
            'spectrum': self._spectrum_client,
            'gate': self._gate_client,
            'apply': self._apply_client
        }

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, i):
        self._port = i
        for c in (self._spectrum_client, self._gate_client,
                  self._apply_client):
            c.port = i

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, s):
        self._base_url = s
        for c in (self._spectrum_client, self._gate_client,
                  self._apply_client):
            c.base_url = s

    def __repr__(self):
        return f"[SpecTcl Client] to {self.base_url}:{self.port}/{self.name}"

    def list(self, group, **kws):
        """List resources as a table.

        Parameters
        ----------
        group : str
            spectrum, gate.
        
        Keyword Arguments
        -----------------
        filter : str
            Search pattern.
        clean : str
            Only work with group of 'gate', default is True.
        """
        clean_gate = kws.pop('clean', True)
        if group not in VALID_GROUP_LIST:
            print(
                f"'{group}' is not one of the supported: {VALID_GROUP_LIST}.")
            return None
        else:
            r = self.__list_map.get(group).list(**kws)
            if r is None:
                return None
            if group == 'spectrum':
                # append gated column
                gate_apply_data = self._apply_client.list()
                r['Gate'] = r.apply(lambda i: gate_apply_data.loc[i.name].desc,
                                    axis=1)
                r.drop(columns=['gate'], inplace=True)
                # append a column '_gate_viz': the name of gate which matches the Parameters, which is for drawing gate
                # with the spectrum.
                _df_gate = self.list('gate')
                r['_params_str'] = r.apply(lambda i: str(i.Parameters), axis=1)
                _df_gate['_params_str'] = _df_gate.apply(
                    lambda i: str(i.Parameters), axis=1)
                _df_gate1 = _df_gate.reset_index().set_index('_params_str')
                _df_sp1 = r.reset_index().set_index('_params_str')
                _idx = _df_sp1.index.intersection(_df_gate1.index)
                _df_sp = _df_gate1.loc[_idx]['Name'].to_frame().rename(
                    columns={
                        'Name': 'ShowGate'
                    }).join(_df_sp1.loc[_idx]).set_index('Name')
                r['ShowGate'] = _df_sp['ShowGate']
                r.drop(columns=['_params_str'], inplace=True)
                return r
            elif group == 'gate':
                # remove gates with not-defined Parameters, but keep the ones with defined Gates
                if clean_gate:
                    r.drop(r[r.Parameters.isna() & r.Gates.isna()].index,
                           inplace=True)
                return r

    def add_spectrum(self, sp: Spectrum):
        """Create a new spectrum.

        Returns
        -------
        r : Spectrum
            New added Spectrum object.
        """
        # test if the name is existing
        if sp.name in self.list('spectrum').index:
            print(
                "The spectrum is already defined, please give a different name."
            )
            return None
        _axes = ' '.join([
            str([int(j) for j in i.values()]) for i in sp.axes
        ]).replace('[', '{').replace(']', '}').replace(',', '')
        r = self._spectrum_client.create(
            sp.name,
            STYPE_MAP_[sp.stype],
            sp.parameters,
            _axes,
            chantype=DTYPE_MAP_[sp.dtype],
        )
        if r is not None:
            # return the new created spectrum as a Spectrum object.
            return self.get_spectrum(sp.name)

    def get_spectrum(self, name, **kws):
        """Return a instance of Spectrum for spectrum of the name defined by *name*.

        Parameters
        ----------
        name : str
            Name of the spectrum.

        Keyword Arguments
        -----------------
        refresh_cache : bool
            If set, refresh the cache of spectra info.

        Returns
        -------
        r : Spectrum
            Spectrum instance.
        """
        kws.pop('as_raw', None)
        refresh_cache = kws.pop('refresh_cache', False)
        for c in (self._spectrum_client, self._gate_client,
                  self._apply_client):
            c.list(refresh_cache=refresh_cache)
        _spectrum_df = self.list('spectrum')
        data = self._spectrum_client.contents(name, as_raw=True, **kws)
        conf = _spectrum_df.loc[name]
        return Spectrum(name, conf, data, client=self)

    def get_gate(self, name: str):
        """Return a instance of Gate for gate of the name defined by *name*.
        
        Parameters
        ----------
        name : str
            Name of the gate.
        
        Returns
        -------
        r : Gate
            Gate instance.
        """
        df_gate = self.list('gate')
        if name in df_gate.index:
            return Gate(df_gate.loc[name])
        else:
            return None


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from pandas import DataFrame

    c = SpecTclSpectrumClient()
    print(c)

    data1 = c.get('contents', name='s1')
    df = DataFrame.from_dict(data1['channels'])
    df.plot(x='x', y='v')

    data2 = c.get('contents', name='s2')
    df = DataFrame.from_dict(data2['channels'])
    df.plot()

    plt.show()
