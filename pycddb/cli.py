from pycddb import *
from pycddb.util import cddb_path, write_map
from glob import glob
from pycddb.data import github
import os
from pycddb.dataset import Dataset
from lingpy import *
from pycddb.md import *


def parse_dash(dash, datatype, args, default):
    if dash in args:
        return datatype(args[args.index(dash)+1])
    return default

def main():

    from sys import argv
    
    dataset = parse_dash('-d', str, argv, None)
    family = parse_dash('-f', str, argv, 'sinitic')
    values = parse_dash('-v', lambda x: x.split(','), argv, '')
    idf = parse_dash('--id', str, argv, None)
    command = parse_dash('-c', str, argv, None)

    if 'show' in argv:
        pass

    if 'stats' in argv and not dataset:
        
        langs = load_languages()
        info = len(langs[list(langs.keys())[0]])
        groups = len(set([l['subgroup'] for l in langs.values()]))
        text = """Dataset contains
* {0} language varieties (distinct)
* {1} different values in the columns
* {2} genetic groups""".format(len(langs), info, groups)
        print(text)

    if 'open' in argv:
        if 'github' in argv:
            os.system('firefox --new-tab '+github)
    
    if 'prepare' in argv:
        dset = Dataset(argv[argv.index('prepare')+1])
        dset.prepare()
    if 'nexus' in argv:
        dset = Dataset(argv[argv.index('nexus')+1])
        dset._run_command('nexus')

    if 'map' in argv:
        write_map(cddb_path('varieties', 'languages.csv'), 
                cddb_path('varieties', 'languages.geojson'))

    if dataset:
        dset = Dataset(dataset)
        if 'languages' in argv:
            for language in dset.languages:
                print('{0:20}\t{1}'.format(
                    language,
                    '\t'.join([dset.languages[language][v] for v in values])))
        if 'prepare' in argv:
            dset.prepare()
        if 'tree' in argv:
            print(dset.get_path(['trees', idf]))
            tree = Tree(open(dset.get_path(['trees', idf])).read())
            print(tree.asciiArt())
        if 'stats' in argv:
            if dset.wordlist:
                print('Wordlist')
                print('Languages: {0}\nConcepts: {1}\nWords: {2}'.format(dset.wordlist.width,
                    dset.wordlist.height, len(dset.wordlist)))
        if 'check' in argv:
            dset._run_command('check')

        if command:
            dset._run_command(command)

    if 'list' in argv:
        if 'sources' in argv:
            l, w, c = set(), 0, set()
            sources = sorted(glob(cddb_path('datasets', '*', '__init__.py')))
            for i, s in enumerate(sources):
                src = os.path.split(os.path.split(s)[0])[1]
                dset = Dataset(src)
                words, concepts, chars = 0, 0, 0
                if dset.words:
                    words = len(dset.words)
                    concepts = len(dset.words.concepts)
                if dset.characters:
                    chars = dset.characters.height
                    c.update(dset.characters)
                print('{0:20}: {1:5} languages {2:6} words {3:6} characters'.format(src,
                    len(dset.languages), words, chars)) 
                l.update(dset.languages)
                w += words
            print( '{0:20}: {1:5} --------- {2:6} ----- {3:6} ----------'.format(
                18 * '-',
         '', '', ''))
            print('{0:20}: {1:5} languages {2:6} words {3:6} characters'.format(
                'TOTAL', len(l), w, len(c)))
    if 'markdown' in argv:
        md_sources()

    if 'master' in argv:
        if 'characters' in argv:
            from pycddb.commands import character_list
            character_list()
    
    if 'download' in argv:
        dset = Dataset(argv[argv.index('download')+1])
        dset._run_command('download')
