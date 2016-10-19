from pycddb.dataset import Dataset
from sinopy import sinopy
from collections import defaultdict
from lingpy import Wordlist

def check(dataset):

    wl = Wordlist(dataset.get_path(['raw', 'Hou2004-characters.tsv']))
    tmp = defaultdict(set)
    for k in wl:
        
        tmp[wl[k, 'gloss'], wl[k, 'baxter']].add(wl[k, 'zgyy'])
    
    errors = []
    count = 1
    for (g, k), vals in tmp.items():
        for v in vals:
            try:
                zgyy = sinopy.sixtuple2baxter(v)
            except:
                errors += [v]
                zgyy = None
            if zgyy:
                ipa = ''.join(zgyy).replace('P', '').replace('R','')
                if ipa != k:
                    print(count, g, k, ipa)
                    count += 1


        
