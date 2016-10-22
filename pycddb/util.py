from functools import partial
from clldutils.dsv import UnicodeReader
import os
from clldutils.misc import slug
from pyconcepticon.api import Concepticon
from collections import OrderedDict
from sinopy import sinopy

import lingpy as lp

# modify lingpy settings
lp.settings.rcParams['morpheme_separator'] = '+'

def cddb_path(*comps):
    return os.path.join(os.path.dirname(__file__), os.pardir, *comps)

def load_languages(delimiter='\t', return_type='dict'):

    with UnicodeReader(cddb_path('varieties', 'languages.csv'), delimiter='\t') as reader:
        data = list(reader)
        
    if return_type == 'dict':
        out = {}
        for line in data[1:]:
            out[line[0]] = OrderedDict(zip(
                [h.lower() for h in data[0]],
                line))
        return out
    else:
        return data

def renumber_partial(wordlist, name='cogids', partial_cognates='value'):
    # renumber for partial cognates
    pcogs, idx = {}, 1
    converter = {}
    for k in wordlist:
        chars = sinopy.gbk2big5(wordlist[k, partial_cognates])
        concept = wordlist[k, 'concept']
        cogids = []
        for char in chars:
            if sinopy.is_chinese(char):
                if char not in pcogs:
                    pcogs[char] = idx
                    idx += 1
                cchar = concept + ':' + str(pcogs[char])
                if cchar not in pcogs:
                    pcogs[cchar] = pcogs[char]
            else:
                cchar = concept + ':' + char
                if cchar not in pcogs:
                    pcogs[cchar] = idx
                    idx += 1
            cogids += [pcogs[cchar]]
        converter[k] = ' '.join([str(x) for x in cogids])
    wordlist.add_entries(name, converter, lambda x: x)

