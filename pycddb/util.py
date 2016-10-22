from functools import partial
from clldutils.dsv import UnicodeReader
import os
from clldutils.misc import slug
from pyconcepticon.api import Concepticon
from collections import OrderedDict
from sinopy import sinopy
import geojson
import json
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


