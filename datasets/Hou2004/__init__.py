from pycddb.dataset import Dataset
from sinopy import sinopy
from collections import defaultdict
from lingpy import Wordlist

rhymebook = sinopy._cd.GY
rhymebook['yun']['譚'] = 'om'
rhymebook['yun']['祃'] = rhymebook['yun']['禡']
rhymebook['yun']['狝'] = rhymebook['yun']['獮']
rhymebook['yun']['麇'] = rhymebook['yun']['真']
rhymebook['yun']['襇'] = rhymebook['yun']['襉']
rhymebook['yun']['恩'] = rhymebook['yun']['痕']
rhymebook['yun']['殷'] = rhymebook['yun']['真']
rhymebook['yun']['誌'] = rhymebook['yun']['志']
rhymebook['yun']['槨'] = rhymebook['yun']['鐸']
rhymebook['yun']['鹹'] = rhymebook['yun']['咸']
rhymebook['yun']['闞'] = rhymebook['yun']['蒸']
rhymebook['yun']['稱'] = rhymebook['yun']['蒸']

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
                zgyy = sinopy.sixtuple2baxter(v, rhymebook=rhymebook)
            except ValueError:
                print(sinopy.sixtuple2baxter(v, debug=True, rhymebook=rhymebook))
                input()
                errors += [(v, k)]
                zgyy = None
            if zgyy:
                ipa = ''.join(zgyy).replace('P', '').replace('R','')
                if ipa != k:
                    print(count, g, k, ipa)
                    count += 1
    count = 1
    for a, b in errors:
        print(count, a, b)
        count += 1

        
