# -*- coding: utf-8 -*-

from requests.adapters import HTTPAdapter


class MyAdapter(HTTPAdapter):
    pass
    #def init_poolmanager(self, connections, maxsize, block=False, **kws):
    #    self.pool


def make_response(r):
    if r.ok and r.json()['status'] == 'OK':
        return r.json()['detail']
    else:
        raise NotFoundSpecTclDataError


class NotFoundSpecTclDataError(Exception):
    def __init__(self):
        super(self.__class__, self).__init__()


ACTION_PARAMS = {
    'spectrum': {
        'contents': ('name',),
        'list': ('filter',),
        'delete': ('name', ),
        'create': ('name', 'type', 'parameters', 'axes', 'chantype'),
        'clear': ('pattern',),
    },
}


