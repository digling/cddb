import re
from sinopy import sinopy

def prepare(dataset):

    with open(dataset.get_path('raw', 'wikibooks.txt')) as f:
        data = f.readlines()
    out = []
    for i, line in enumerate(data):
        line = line.strip().replace('\t', ' ')
        if line.startswith('*'):
            if not line[1] == ' ':
                line = line.replace('*', '* ')
            elms = line.split(' ')
            if elms and len(elms) > 1:
                kgsc = elms[1].split('/')
                if len(kgsc) == 1:
                    schuessler = ''
                    karlgren = kgsc[0]
                elif len(kgsc) == 2:
                    karlgren = kgsc[1]
                    schuessler = kgsc[0]
                else:
                    print('[ERROR:schuessler/karlgren] {0}'.format(line))
                
                try:
                    char = elms[2].split('|')[-1][0]
                except IndexError:
                    print('[ERROR:character] {0}'.format(line))
                    char = ''
                
                mch = [x[:-1] if x.endswith(',') else x for x in elms[3:]]
                if len(karlgren) not in [4, 5, 6]:
                    print('[ERROR:karlgren] {0}'.format(line, karlgren))
                elif not sinopy.is_chinese(char):
                    print('[ERROR:char] {0}'.format(line))
                elif char:
                    pinyin = sinopy.pinyin(char)
                    if '?' in pinyin or sinopy.is_chinese(pinyin):
                        pinyin = ''
                    out += [(
                        char,
                        pinyin,
                        'Old_Chinese',
                        karlgren[:4],
                        karlgren,
                        '',
                        'Karlgren1954'
                        )]
                    for reading in mch:
                        out += [(
                            char, pinyin, 'Middle_Chinese', '', karlgren, reading,
                            'Wikibooks2016a')]
    with open(dataset.get_path('characters.tsv'), 'w') as f:
        f.write('ID\tCHARACTER\tPINYIN\tDOCULECT\tPHONETIC_CLASS\tKARLGREN_ID\tREADING\tSOURCE\n')
        for i, line in enumerate(out):
            f.write(str(i+1)+'\t'+'\t'.join(line)+'\n')

                    
                    

