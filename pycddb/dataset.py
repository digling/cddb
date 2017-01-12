from clldutils.dsv import UnicodeReader
from clldutils.misc import cached_property
from pycddb.util import cddb_path, load_languages, get_transformer
import json
from collections import OrderedDict
import os
#from pylexibank.util import with_sys_path
from pyconcepticon.api import Concepticon, Conceptlist 
from clldutils.path import Path, import_module
from lingpy import *
from sinopy import sinopy

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

def csv2list(path):
    with UnicodeReader(path, delimiter='\t') as reader:
        data = list(reader)
    header = [h.lower() for h in data[0]]
    return [dict(zip(header,line)) for line in data[1:]]

def json2dict(path):
    with open(path) as f:
        return json.load(f)


def data_path(path):
    return lambda *x: cddb_path('datasets', path, *x)

class Dataset(object):

    def __init__(self, name, data_path=data_path, base='cddb', 
            _languages=_languages, _path=cddb_path):
        self.id = name
        self.get_path = data_path(name)
        self.path = self.get_path('')
        self._data = {}

        # get the languages
        self.languages = csv2dict(self.get_path('languages.csv'), key=base,
                prefix=self.id)
        self.lid2lang = dict([(self.languages[x][self.id+'_id'], x) for x in
            self.languages])
        for k in self.languages:
            for h, v in _languages[k].items():
                self.languages[k][h.lower()] = v

        self.metadata = json2dict(self.get_path('metadata.json'))
        #with with_sys_path(Path(_path('datasets'))) as f:
        self.commands = import_module(Path(_path('datasets', self.id)))
        
        # try to get a concept list
        clist = False
        if os.path.isfile(self.get_path('concepts.csv')):
            clist = Conceptlist.from_file(self.get_path('concepts.csv'))
        elif 'concepts' in self.metadata:
            clist = Concepticon().conceptlists[self.metadata['concepts']]
        if clist:
            self.concepts = {c.gloss or c.english : c for c in
                    clist.concepts.values()}

        if 'profile' in self.metadata:
            self.transform = get_transformer(self.metadata['profile'])

    def raw(self, *comps):
        return self.get_path('raw', *comps)

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
    def structures(self):
        if os.path.exists(self.get_path('structures.tsv')):
            return Wordlist(self.get_path('structures.tsv'), row='structure')
        return None
    
    def write_characters(self, data):
        with open(self.get_path('characters.tsv'), 'w') as f:
            for line in data:
                f.write('\t'.join([str(x) for x in line])+'\n')


    def write_wordlist(self, wordlist, *path):
        wordlist.output('tsv', filename=self.get_path(*path, 'words'), ignore='all',
                prettify=False)
        print(self.get_path(*path))
   
    def pinyin(self, chars):
        py = []
        for char in chars:
            p = sinopy.pinyin(char)
            if '?' in p or sinopy.is_chinese(p):
                p = ''
            py += [p]
        return ' '.join(py)

    def sixtuple(self, chars, debug=False):
        assert len(chars) == 6
        if not debug:
            mch =''.join(sinopy.sixtuple2baxter(chars))
            return mch
        else:
            return sinopy.sixtuple2baxter(chars, debug=True)

    def structure(self, string):
        ct = sinopy.parse_chinese_morphemes(string)
        return ' '.join([b for a, b in zip(ct, 'imnft') if a != '-'])
    
    def chinese(self, string):
        return sinopy.is_chinese(string)

    def gbk_and_big5(self, chars):
        out1, out2 = '', ''
        for char in chars:
            if sinopy.is_chinese(char):
                idx1, idx2 = sinopy._cd.GBK.find(char), sinopy._cd.BIG5.find(char)
                if idx1 > -1:
                    out1 += char
                    out2 += sinopy._cd.BIG5[idx1]
                elif idx2 > -1:
                    out1 += sinopy._cd.GBK[idx2]
                    out2 += char
                else:
                    out1 += char
                    out2 += char
            
        return out1, out2
    
    @cached_property()
    def mch(self):
        t = get_transformer(self._path('profiles', 'Baxter1992.prf'))
        return lambda x: (t(x, 'clpa'), t(x, 'structure'))
    
    @cached_property()
    def och(self):
        t = get_transformer(self._path('profiles', 'Baxter2014.prf'))
        return lambda x: (t(x, 'clpa'), 
                t(x, 'structure'), 
               )
    
    def gloss(self, string):
        reps = {'"': '“'}
        return ''.join([reps.get(x, x) for x in string])

    
    def csv2list(self, path):
        return csv2list(path)

    def split_initial_final(self, string):

        tokens = ipa2tokens(string, merge_vowels=False)
        cv = ''.join([x.lower() for x in tokens2class(tokens, 'cv')])
        vidx = cv.find('v')
        tidx = cv.find('t')
        if tidx != -1 and vidx != -1:
            return (
                    ''.join(tokens[:vidx]), ''.join(tokens[vidx:tidx]),
                    ''.join(tokens[tidx:]))
        if vidx != -1:
            return (''.join(tokens[:vidx]), ''.join(tokens[vidx:]), '')
        return (
                ''.join(tokens), '', '')

    def write_profile(self, path, profile):
        with open(path, 'w') as f:
            f.write('GRAPHEMES\tSOURCE\tTYPE\tCLPA'
                    '\tSTRUCTURE\tDOCULECT\tFREQUENCY\n')
            for (s, t), vals in sorted(
                    profile.items(), key=lambda x: (x[0][1], sum(x[1].values())),
                    reverse=True):
                f.write('\t'.join([
                    s.replace(' ', ''), s, t, s, '', ','.join(sorted(vals)),
                    str(sum(vals.values()))])+'\n')


