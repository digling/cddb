from importlib import import_module
from clldutils.dsv import UnicodeReader
from clldutils.misc import cached_property
from pycddb.util import cddb_path, load_languages
import json
from collections import OrderedDict
import os
from pylexibank.util import with_sys_path
from clldutils.path import Path
from lingpy import *

_languages = load_languages(return_type='dict')


def csv2dict(path, key='id', prefix=''):
    d = {}
    with UnicodeReader(path, delimiter='\t') as reader:
        data = list(reader)
    
    idx = 0
    header = [h.lower() for h in data[0]]
    if key in header:
        idx = header.index(key.lower())
    for line in data[1:]:
        d[line[idx]] = OrderedDict(zip(
            [prefix+'_'+h if prefix else h for h in header],
            line))
    return d


def json2dict(path):
    with open(path) as f:
        return json.load(f)


def data_path(path):
    return lambda *x: cddb_path('datasets', path, *x)

class Dataset(object):

    def __init__(self, name):
        self.id = name
        self.get_path = data_path(name)
        self.path = self.get_path('')
        self._data = {}

        # get the languages
        self.languages = csv2dict(self.get_path('languages.csv'), key='cddb',
                prefix=self.id)
        self.lid2lang = dict([(self.languages[x][self.id+'_id'], x) for x in
            self.languages])
        for k in self.languages:
            for h, v in _languages[k].items():
                self.languages[k][h.lower()] = v

        self.metadata = json2dict(self.get_path('metadata.json'))
        with with_sys_path(Path(cddb_path('datasets'))) as f:
            self.commands = import_module(name)
    
    def _run_command(self, name, *args, **kw):
        if not hasattr(self.commands, name):
            print('command "%s" not available for dataset %s' % (name, self.id))
        else:
            getattr(self.commands, name)(self, *args, **kw)

    def prepare(self, **kw):
        self._run_command('prepare')

    @cached_property()
    def words(self):
        if os.path.exists(self.get_path('words.tsv')):
            return Wordlist(self.get_path('words.tsv'))
        return None
    
    @cached_property()
    def characters(self):
        if os.path.exists(self.get_path('characters.tsv')):
            return Wordlist(self.get_path('characters.tsv'), row='character')
        return None

    @cached_property()
    def structure(self):
        if os.path.exists(self.get_path('structures.tsv')):
            return Wordlist(self.get_path('structures.tsv'), row='structure')
        return None
