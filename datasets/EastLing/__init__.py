from collections import defaultdict

def prepare(ds):
    print('prep')
    idx = 1
    D = {0: ['characters', 'pinyin', 'doculect', 'reading', 'segments',
             'structure', 'source']}
    profile = defaultdict(lambda : defaultdict(int))
    for d in ds.csv2list(ds.raw('eastling-data-excerpt.tsv')):
        for reading in ['li1971', 'pan2000', 'wang1980',
                        'zhengzhang2003', 'karlgren1954']:
            if d[reading].strip():
                i, f, t = ds.split_initial_final(d[reading].replace(' ',
                    '').replace("'", '‘'))
                if f:
                    profile[i, 'i'][reading] += 1
                    profile[f, 'f'][reading] += 1
                else:
                    print(reading, '\t', d[reading])
                    profile[i, 's'][reading] += 1
    ds.write_profile(ds.raw('eastling.prf'), profile)
        
    
