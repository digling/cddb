from pycddb import *
from pycddb.data import github
import os
from pycddb.dataset import Dataset
from lingpy import *


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

    if 'show' in argv:
        pass

    if 'stats' in argv and not dataset:
        
        langs = load_languages()
        info = len(langs[list(langs.keys())[0]])
        groups = len(set([l['group'] for l in langs.values()]))
        text = """Dataset contains
* {0} language varieties (distinct)
* {1} different values in the columns
* {2} genetic groups""".format(len(langs), info, groups)
        print(text)

    if 'open' in argv:
        if 'github' in argv:
            os.system('firefox --new-tab '+github)

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




    
