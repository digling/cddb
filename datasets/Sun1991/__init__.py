from lingpy import *
import re

def prepare(dataset):

    wl = Wordlist(dataset.get_path('raw', 'ZMYYC.csv'), row='gloss',
            col='language')
    glosses = set()
    out = {}
    for l in dataset.lid2lang:
        idxs = wl.get_list(language=l, flat=True)
        for idx in idxs:
            stedt_id = wl[idx, 'rn']
            gid = wl[idx, 'srcid'].split('.')[0]
            gloss = wl[idx, 'gloss']
            word = wl[idx, 'reflex']
            words = re.split('([¹²³⁴⁵]+)', word)
            for i, w in enumerate(words):
                if w:
                    t = ' '.join(ipa2tokens(w, semi_diacritics='sɕʑzʒʃ̢ʂʐh',
                        merge_vowels=False, expand_nasals=True))
                    words[i] = t
            segments = ' '.join(words)
            glosses.add((gid, gloss))
            if not word == '*':
                out[int(stedt_id)] = [dataset.lid2lang[l], l, gloss, '', stedt_id,
                    word, segments,
                        'Sun1991']
    out[0] = ['doculect', 'doculect_in_source', 'concept', 'concepticon_id',
        'stedt_id', 'value', 'segments', 'source']
    dataset.write_wordlist(Wordlist(out), 'words')
    with open(dataset.get_path('concepts.tsv'), 'w') as f:
        f.write('NUMBER\tENGLISH\n')
        for a, b in sorted(glosses, key=lambda x: int(x[0])):
            f.write(a+'\t'+b+'\n')


