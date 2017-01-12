from functools import partial
import os
from glob import glob
from collections import OrderedDict, defaultdict

from clldutils.dsv import UnicodeReader
from clldutils.misc import slug
import unicodedata
from pybtex import database


from pyclpa.base import get_clpa
from pyconcepticon.api import Concepticon

from sinopy import sinopy
import geojson
import json

import lingpy as lp
from lingpy.compare.partial import _get_slices

from segments.tokenizer import Tokenizer


# modify lingpy settings
lp.settings.rcParams['morpheme_separator'] = '+'
clpa = get_clpa()

def cddb_path(*comps):
    return os.path.join(os.path.dirname(__file__), os.pardir, *comps)


def get_sources(src_type):
    return sorted([os.path.split(os.path.split(s)[0])[1] for s in glob(
                cddb_path('datasets', '*', src_type))])

def load_characters():
    return lp.Wordlist(cddb_path('datasets', 'characters.tsv'),
            row='character')

def load_languages(delimiter='\t', return_type='dict'):

    with UnicodeReader(cddb_path('varieties', 'languages.tsv'), delimiter='\t') as reader:
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
            if sinopy.iexpands_chinese(char):
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


def write_map(varieties, outfile):
    languages = lp.csv2list(varieties)
    colors = ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a",
            '#040404', '#F6E3CE', '#81F79F', '#8A0808', '#FA58F4', '#0489B1',
            '#088A08']
    points = []
    header = [x.strip() for x in languages[0]]
    nidx = header.index('NAME')
    latidx = header.index('LATITUDE')
    lonidx = header.index('LONGITUDE')
    pinidx = header.index('PINYIN')
    hanidx = header.index('HANZI')
    groupidx = header.index("SUBGROUP")
    pinidx = header.index("PINYIN")
    famidx = header.index('FAMILY')

    groups = sorted(set([line[groupidx] for line in languages[1:]]))
    for line in languages[1:]:
        name = line[nidx]
        pinyin = line[pinidx]
        hanzi = line[hanidx]
        lat, lon = line[latidx], line[lonidx]
        group = line[groupidx]
        family = line[famidx]
        if lat.strip() and lat != '?':
            lat, lon = float(lat), float(lon)
            if lat > 400 or lon > 400:
                raise ValueError("Coords for {0} are wrong.".format(name))
            point = geojson.Point((lon, lat))
            feature = geojson.Feature(geometry=point, 
                    properties = {
                        "Family" : family,
                        "Variety" : name,
                        "Pinyin" : pinyin,
                        "Chinese" : hanzi,
                        "Group" : group,
                        "marker-color" : colors[groups.index(group)]
                        })
            points += [feature]
    with open(outfile, 'w') as f:
        f.write(json.dumps(geojson.FeatureCollection(points)))

def get_inventories(wordlist, segments='tokens'):
    assert segments in wordlist.header
    D = {t : defaultdict(list) for t in wordlist.taxa}
    for taxon in wordlist.taxa:
        for idx in wordlist.get_list(taxon=taxon, flat=True):
            tokens = wordlist[idx, segments]
            print(' '.join(tokens))
            slices = _get_slices(tokens)
            for jdx, (sA, sB) in enumerate(slices):
                i, m, n, f, t = sinopy.parse_chinese_morphemes(tokens[sA:sB])
                pos = '{0}:{1}'.format(idx, jdx)
                if i != '-':
                    D[taxon]['initial', i] += [pos]
                if m != '-':
                    D[taxon]['medial', m] += [pos]
                if n != '-':
                    D[taxon]['nucleus', n] += [pos]
                if f != '-':
                    D[taxon]['final', f] += [pos]
                if t != '-': 
                    D[taxon]['tone', t] += [pos]
    I = [('ID', 'DOCULECT', 'CONTEXT', 'VALUE', 'OCCURRENCES', 'CROSSREF')]
    idx = 1
    for t in wordlist.taxa:
        for (s, v), occ in sorted(D[t].items(), key=lambda x: (x[0][0], x[0][1],
            len(x[1]))):
            I += [(str(idx), t, s, v, len(occ), ' '.join(occ))]
    return I

def normalize(string):
    norms = {'ˁ': 'ˤ', 'ɡ': 'g', "ε" : "ɛ"}
    return ''.join([norms.get(x, x) for x in string])

def get_transformer(profile, exception=None):
    
    profile = lp.csv2list(cddb_path('profiles', profile), strip_lines=False)
    for i, line in enumerate(profile):
        profile[i] = [unicodedata.normalize('NFD', clpa.normalize(x)) for x in line]
    tokenizer = Tokenizer(profile, errors_replace=lambda x: "«{0}»".format(x))
    
    return lambda x, y: unicodedata.normalize(
            'NFC',
            tokenizer.transform(clpa.normalize(x), column=y, separator=' + ')
            )

def get_bibliography():
    return database.parse_file(cddb_path('references', 'references.bib'))

def slice_word(word):
    for a, b in _get_slices(word):
        yield word[a:b]

def slice_characters(chars):

    out = []
    plus = False
    for char in chars:
        if plus:
            plus = False
            out[-1] += char
        elif char != '+':
            out += [char]
        elif char == '+':
            plus = True

    return out
        
