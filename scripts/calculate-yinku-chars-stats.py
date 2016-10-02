from lingpy import *
from collections import defaultdict
from itertools import combinations
from lingpy.sequence.sound_classes import token2class
from lingpy.thirdparty.cogent import LoadTree
from matplotlib import pyplot as plt
import networkx as nx
import html
from sys import argv
alms = Alignments('../yinku-chars/yinku.tsv')

# calculate essential diversity of sounds in the initials
color = Model('color')
tree = Tree(open('../trees/sagart-yinku.tre').read())
print([t for t in tree.taxa if t not in alms.taxa])
print('')
print([t for t in alms.taxa if t not in tree.taxa])

paps = []
cols = []
dols = []
protos = []
symbols = defaultdict(int)
for cogid, msa in alms.msa['cogid'].items():
    
    proto = alms[msa['ID'][0], 'proto_tokens'].split(' ')
    col1 = [line[0] for line in msa['alignment']]
    cols1 = [token2class(x, color) for x in col1]
    dol1 = [token2class(x, 'dolgo') for x in col1]
    
    col_new, cols_new, dols_new = [], [], []
    for i, tax in enumerate(alms.taxa):
        if tax in msa['taxa']:
            idx = msa['taxa'].index(tax)
        else:
            idx = -1
        if idx != -1:
            col_new += [col1[idx]]
            cols_new += [cols1[idx]]
            dols_new += [dol1[idx]]
        else:
            col_new += ['Ø']
            cols_new += ['#ffffff']
            dols_new += ['Ø']
        

    paps += [[str(cogid)] + col_new]
    protos += [proto[0]]
    for x in col_new:
        symbols[x] += 1
    
    cols += [cols_new]
    dols += [dols_new]

with open('../output/paps-yinku-chars.tsv', 'w') as f:
    f.write('COGNATESET\t'+'\t'.join(alms.taxa)+'\n')
    for line in paps:
        f.write('\t'.join(line)+'\n')

def compatible(col1, col2):
    comps = 0
    incomps = 0
    for a, b in zip(col1, col2):
        if 'Ø' in (a, b): 
            pass
        elif a == b:
            comps += 1
        elif a != b:
            incomps +=1
    if incomps > int(argv[1]):
        return -1
    return comps

def cons_color(pat):

    if type(pat) == str:
        pat = pat.split(' ')
    best = sorted(set(pat), key=lambda x: pat.count(x), reverse=True)
    best = [x for x in best if x != 'Ø']
    best = best[0]
    
    this_color = token2class(best, color)
    return this_color

patterns = defaultdict(list)
for i, pattern in enumerate(paps):
    patterns[' '.join(pattern[1:])] += [pattern[0]]

S = nx.Graph()
for cog, *pat in paps:
    for s1, s2 in combinations(sorted([x for x in set(pat) if x != 'Ø']), r=2):
        try:
            S.edge[s1][s2]['weight'] += 1
        except KeyError:
            S.add_edge(s1, s2, weight=1)
with open('../output/sounds.gml', 'w') as f:
    f.write(html.unescape('\n'.join(nx.generate_gml(S))))

G = nx.Graph()
count = 0
for (i,p1), (j,p2) in combinations(enumerate(paps), r=2):
    pat1 = p1[1:]
    pat2 = p2[1:]

    if not count % 1000:
        print('counted {0}'.format(count))
    count += 1
    if pat1 not in G:
        G.add_node(p1[0], proto=protos[i], pattern=' '.join(pat1), color=cons_color(pat1))
    if pat2 not in G:
        G.add_node(p2[0], proto=protos[j], pattern=' '.join(pat2), color=cons_color(pat2))
    comp = compatible(pat1, pat2)
    if comp != -1:
        try:
            G.edge[p1[0]][p2[0]]['weight'] += comp
        except KeyError:
            G.add_edge(p1[0], p2[0], weight=comp)

def escapo(string):
    out = ''
    for x in string:
        out += '&#'+str(hex(ord(x))).lstrip('0')+';'
    return out

comps = defaultdict(int)
blocks = []
compos = []
idx = 1
for comp in nx.connected_components(G):
    comps[len(comp)] += 1
    if len(comp) > 1:
        for c in comp:
            blocks += [[str(idx), str(c)]+[escapo(x) for x in
                G.node[c]['pattern'].split(' ')]]
        idx += 1
    compos += [len(comp)]

plt.clf()
plt.hist(compos, bins=30)
plt.ylim(0,500)
plt.savefig('compos-'+argv[1]+'.png')
with open('../output/blocked_data.tsv', 'w') as f:
    f.write('BLOCK\tCOGID\t'+'\t'.join(alms.taxa)+'\n')
    for line in blocks:
        f.write('\t'.join(line)+'\n')

sumx = 0
for i,(idx, c) in enumerate(sorted(comps.items(), key=lambda x: x[0],
    reverse=True)):
    print(i+1, idx, c)
    sumx += c
print(sumx)
input('done')
with open('../output/sound-graph.gml', 'w') as f:
    f.write(html.unescape('\n'.join(nx.generate_gml(G))))

#with open('../output/symbols-yinku.tsv', 'w') as f:
#    for sym, count in sorted(symbols.items(), key=lambda x: x[1], reverse=True):
#        f.write('{0}\t{1}\n'.format(sym, count))


plt.figure(figsize=(40, 10))
for i, row in enumerate(cols):
    for j, cell in enumerate(row):
        circle = plt.Rectangle((i, j), 0.8, 0.8, color=cell)
        plt.gca().add_patch(circle)
plt.axes().set_aspect(4)
plt.ylim(0, j)
plt.xlim(0, i)
plt.savefig('../output/patterns.pdf')
