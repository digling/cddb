from functools import partial
from clldutils.dsv import UnicodeReader
import os
from clldutils.misc import slug
from pyconcepticon.api import Concepticon
from collections import OrderedDict

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

def query_languages(family, column):
    pass
    
