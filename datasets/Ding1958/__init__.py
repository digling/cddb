from lingpy import *
from sinopy import sinopy

def prepare(ds):

    data = csv2list(ds.raw('gujinduiyinduizhaoshouce.csv'), strip_lines=False)
    header = data[0]
    data = data[1:]
    C = {0: ['character', 'pinyin', 'doculect', 'reading', 'context']}
    idx = 1
    errors = set()
    for line in data:
        char, bj, fq, st = [''.join(x) for x in (
            line[1], line[2:5], line[5:7], line[7:])]
        if char.strip() and ds.chinese(char):
            py = ds.pinyin(char)

            bjr = ds.transform(bj, 'source')
            ct = ds.transform(bj, 'context')
            try:
                _i = ds.sixtuple(st)
                print(char, _i)
                mc, st = ds.mch(_i)

                C[idx] = [char, py, 'Middle_Chinese', mc, st]
                C[idx+1] = [char, py, 'Beijing', bjr, ct]
                idx += 2
            except ValueError:
                for tup, v in zip(ds.sixtuple(st, debug=True), 'imnft'):
                    if tup[1] == '?':
                        errors.add((v, tup[0]))
    ds.write_wordlist(Wordlist(C, row='character'), 'characters')
    for i, (e1, e2) in enumerate(errors):
        print(i, e1, e2)
        

