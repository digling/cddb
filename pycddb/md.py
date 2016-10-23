from pycddb.dataset import *
from pycddb.util import cddb_path
from glob import glob
import os

def md_sources():
    sources = sorted(glob(cddb_path('datasets', '*', '__init__.py')))
    text = '# Datasets in the CDDB\n'
    text += ' | ' .join(['DATASET', 'LANGUAGES', 'WORDS', 'CHARACTERS', 
            'STRUCTURES', 'TREES', 'INVENTORIES']) + '\n'
    text += ' | '.join(7 * ['---'])+'\n'
    for i, s in enumerate(sources):
        src = os.path.split(os.path.split(s)[0])[1]
        dset = Dataset(src)
        words = len(dset.words) if dset.words else 0
        words_langs = dset.words.height if dset.words else 0
        chars = dset.characters.height if dset.characters else 0
        chars_langs = dset.characters.width if dset.characters else 0
        concepts = dset.words.height if dset.words else 0
        structs = dset.structures.height if dset.structures else 0
        structs_langs = dset.structures.height if dset.structures else 0
        
        text += ' | '.join([
            '[{0}](http://bibliography.lingpy.org?key={0})'.format(src),
            str(len(dset.languages)),
            '{0} words, {1} conc., {2} lngs'.format(words, concepts, words_langs),
            '{0} chars, {1} lngs.'.format(chars, chars_langs),
            '{0} feat., {1} lngs.'.format(structs, structs_langs),
            '',
            ''])+'\n'
    text += '\n'
    with open(cddb_path('datasets/README.md'), 'w') as f:
        f.write(text)
