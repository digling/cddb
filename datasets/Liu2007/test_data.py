from lingpy import *
from glob import glob
import re
from collections import defaultdict
files = glob('chinese-*.tsv')

tone_converter = dict(zip('012345-', '⁰¹²³⁴⁵¯'))
tone_converter['_'] = ''
converter = [
        ('E', 'ɛ'),
        ]


concepts = defaultdict(set)
for f in files:
    data = csv2list(f)
    for i, line in enumerate(data):
        if len(line) != 4:
            print(i, line)
            raise ValueError('wrong line number')
        concept, page, char, sampas = line
        concepts[concept].add(page)
        if sampas.startswith('!'):
            pass
        else:
            sampas = sampas.split(', ')
            for sampa in sampas:
                if sampa.startswith('('):
                    sampa = sampa[sampa.index(' '):]

                morphemes = sampa.split(' ')
                for morpheme in morphemes:
                    #print(f, concept, page, char, sampa, line)
                    morph = re.sub(r'([012345\-_]+)$', r'<\1>',
                            morpheme) 
                    # get all tone combis
                    tones = re.findall('<.*?>', morph)
                    for tone in tones:
                        newtone = ''.join([tone_converter.get(x, x) for x in tone])
                        morph = morph.replace(tone, newtone[1:-1])
                    print(concept, page, sampas, morph)
                    ipa = sampa2uni(morph)
                    print('\t',morph, ipa)
for i, concept in enumerate(sorted(concepts)):
    print(i+1, concept, concepts[concept])
