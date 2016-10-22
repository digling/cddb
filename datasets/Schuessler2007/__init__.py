import re

def prepare(dataset):
    with open(dataset.get_path(['raw', '__private__schuessler.txt'])) as f:
        data = f.readlines()

    D = [('ID', 'CHARACTER', 'PINYIN', 'DOCULECT', 'WORD_FAMILY',
        'GLOSS', 'READING', 'SOURCE')]
    idf = ''
    idx = 1
    for line in data:
        if line.startswith('ENTRY'):
            if idf:
                if mch:
                    D += [(idx, char, pinyin, 'Middle_Chinese', '', gloss, mch, 
                        'Schuessler2007')]
                    idx += 1
                if ocb:
                    D += [(idx, char, pinyin, 'Old_Chinese', '', gloss, ocb, 
                        'Baxter1992')]
                    idx += 1
                if ocm:
                    D += [(idx, char, pinyin, 'Old_Chinese', anc, gloss, ocm, 
                        'Schuessler2007')]
                    idx += 1
                if lhc:
                    D += [(idx, char, pinyin, 'Late_Han_Chinese', '', gloss, lhc, 
                        'Schuessler2007')]
                    idx += 1


            idf = line[6:].strip()
            gloss, pinyin, anc, char, mch, ocb, ocm, lhc = ('', '', '', '', '', '',
                    '', '')
        if line.startswith('HEAD'):
            if '⪤' in line:
                anc, line = line[5:].split('⪤')
                anc = '⪤ '+anc
            elif '~' in line:
                anc, line = line[5:].split('~')
                anc = '~ ' + anc
            elif '=' in line:
                anc, line = line[5:].split('=')
                anc = '= '+anc
            else:
                anc, line = '', line[5:]
            line = line.strip()
            anc = anc.strip()
            if line.count(' ') == 1:
                pinyin, char = line.split(' ')
            else:
                idf = ''
                print('[Problem]: {0}'.format(line))
        if line.startswith('LH'):
            lhc = line[14:].strip()
        if line.startswith('GLOSS'):
            if gloss:
                gloss += '/' + line[6:].strip()
            else:
                gloss = line[6:].strip()
        if line.startswith('MC'):
            mch = line[18:].strip()
        if line.startswith('OCB'):
            ocb = line[25:].strip()
        if line.startswith('OCM'):
            ocm = line[26:].strip()
    
    with open(dataset.get_path(['characters.tsv']), 'w') as f:
        for i, line in enumerate(D):
            f.write('\t'.join([str(x) for x in line])+'\n')
