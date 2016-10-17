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
D = {}
D[0] = ['doculect', 'concept', 'hanzi_in_source', 'ipa_in_source', 'page']
blocks = []
cc = ''
for f in files:
    data = csv2list(f)
    idx = 0
    for i, line in enumerate(data):
        if len(line) != 4:
            print(i, line)
            raise ValueError('wrong line number')
        concept, page, char, sampas = line
        if cc != concept:
            blocks += [[]]
        cc = concept

        concepts[concept].add(page)
        
        if sampas.startswith('!'):
            print(sampas)
            input()
        else:
            sampas = sampas.split(', ')
            idx += 1
            all_morphs = []
            for sampa in sampas:
                if sampa.startswith('('):
                    sampa = sampa[sampa.index(' '):]

                morphemes = sampa.split(' ')
                mymorphs = []
                for morpheme in morphemes:
                    #print(f, concept, page, char, sampa, line)
                    morph = re.sub(r'([012345\-_]+)$', r'<\1>',
                            morpheme) 
                    # get all tone combis
                    tones = re.findall('<.*?>', morph)
                    for tone in tones:
                        newtone = ''.join([tone_converter.get(x, x) for x in tone])
                        morph = morph.replace(tone, newtone[1:-1])
                    print(i, f, concept, page, sampas, morph)
                    ipa = sampa2uni(morph)
                    print('\t',morph, ipa)
                    mymorphs += [ipa]
                all_morphs += ['+'.join(mymorphs)]
            blocks[-1] += [[idx, concept, page, char,all_morphs]]
            if idx == 19:
                print(len(blocks[-1]), blocks[-1])
                assert len(blocks[-1]) == 19
                idx = 0

for i, concept in enumerate(sorted(concepts)):
    print(i+1, concept, concepts[concept])
