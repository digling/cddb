from lingpy import *
import geojson
import json

def write_map(varieties, outfile):
    languages = csv2list(varieties)
    colors = ["#a6cee3","#1f78b4","#b2df8a","#33a02c","#fb9a99","#e31a1c","#fdbf6f","#ff7f00","#cab2d6","#6a3d9a", '#040404']
    points = []
    header = [x.strip() for x in languages[0]]
    # get the indices
    nidx = header.index('NAME')
    latidx = header.index('LATITUDE')
    lonidx = header.index('LONGITUDE')
    pinidx = header.index('PINYIN')
    hanidx = header.index('HANZI')
    groupidx = header.index("GROUP")
    srcidx = header.index("LEXICON")
    pinidx = header.index("PINYIN")

    groups = sorted(set([line[groupidx] for line in languages[1:]]))
    for line in languages[1:]:
        name = line[nidx]
        pinyin = line[pinidx]
        hanzi = line[hanidx]
        lat, lon = line[latidx], line[lonidx]
        group = line[groupidx]
        sources = line[srcidx].split(', ')
        if lat.strip() and lat != '?':
            lat, lon = float(lat), float(lon)
            if lat > 400 or lon > 400:
                raise ValueError("Coords for {0} are wrong.".format(name))
            point = geojson.Point((lon, lat))
            feature = geojson.Feature(geometry=point, 
                    properties = {
                        "Variety" : name,
                        "Pinyin" : pinyin,
                        "Chinese" : hanzi,
                        "Sources" : ','.join(sources),
                        "Group" : group,
                        "marker-color" : colors[groups.index(group)]
                        })
            points += [feature]
    with open(outfile, 'w') as f:
        f.write(json.dumps(geojson.FeatureCollection(points)))

if __name__ == "__main__":
    from glob import glob
    files = glob('../varieties/*.csv')
    for f in files:
        print(f, )
        write_map(f, f.replace('.csv', '.geojson'))
