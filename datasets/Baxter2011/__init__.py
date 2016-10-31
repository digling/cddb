from lingpy import csv2list, Wordlist

def get_bracket(string, b='()'):
    bropen = False
    out1 = ''
    out2 = ''
    chars = list(string)
    while chars:
        char = chars.pop(0)
        if char == b[0]:
            bropen = True
        if bropen:
            out2 += char
        else:
            out1 += char
        if char == b[1]:
            bropen = False
    return out1.strip(), out2.strip()

def prepare(ds):
    data = csv2list(ds.raw('Baxter2011.tsv'))
    data = data[1:]
    C = {0 : [
        'character',
        'simplified_character',
        'pinyin',
        'doculect',
        'doculect_in_source',
        'reading',
        'segments',
        'context',
        'gloss', 'cognate_class']}
    idx = 1
    for i, line in enumerate(data):
        l, s, p = line[0:3]
        mch = ds.transform(line[3], 'clpa')
        if '«' in mch:
            print(mch, line[3])
        struc = ds.transform(line[3], 'structure')
        assert len(mch.split(' ')) == len(struc.split(' '))
        C[idx] = [
                l, s, p, 'Middle_Chinese', 'MC', 
                line[3], mch, struc, 
                ds.gloss(line[-1]), str(i+1)]
        idx += 1
        och1, och2 = get_bracket(line[-2], '{}')
        och1, note = get_bracket(och1, '()')
        och1 = och1.split(' ')[0]
        och, struc = ds.och(och1)
        try:
            assert len(och.split(' ')) == len(struc.split(' '))
        except AssertionError:
            print(och, struc)
            och = False
        if '«' in och:
            print(och, och1)
            och = False
        if och:
            C[idx] = [l, s, p, 'Old_Chinese', 'OC', line[-2], och, struc,
                    ds.gloss(line[-1]), str(i+1)]
            idx += 1

    ds.write_wordlist(Wordlist(C, row='character'), 'characters')

