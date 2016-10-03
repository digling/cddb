from lingpy import *
from glob import glob
import re
files = glob('chinese-*.tsv')

tone_converter = dict(zip('012345-', '⁰¹²³⁴⁵¯'))
tone_converter['_'] = ''
converter = [
        ('E', 'ɛ'),
        ]


for f in files:
    data = csv2list(f)
    for i, line in enumerate(data):
        if len(line) != 4:
            print(i, line)
            raise ValueError('wrong line number')
        concept, page, char, sampas = line
        sampas = sampas.split(', ')
        for sampa in sampas:
            if sampa.startswith('('):
                sampa = sampa[sampa.index(' '):]
            print(f, concept, page, char, sampa, line)
            sampa = re.sub(r'([012345\-_]+)$|([012345\-_]+) ', r'<\1>', sampa) 
            # get all tone combis
            tones = re.findall('<.*?>', sampa)
            for tone in tones:
                newtone = ''.join([tone_converter.get(x, x) for x in tone])
                sampa = sampa.replace(tone, newtone[1:-1])
            print(sampa)
            ipa = sampa2uni(sampa)
            print('\t',sampa, ipa)
        
