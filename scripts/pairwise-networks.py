from lingpy import *
import networkx as nx
from collections import defaultdict
from itertools import combinations, product
from util import *
import pickle
from lingpy.algorithm.cython.misc import squareform
from sys import argv


def threshold_from_tlen(tlen):
    return len(list(combinations(range(tlen), r=2)))

def distance(graph):
    possible = sum([len(val) for val in graph.values()])
    reduction = len(graph)
    soundsA, soundsB = set([k[0] for k in graph]), set([k[1] for k in graph])
    return reduction / len(list(product(soundsA, soundsB)))

def compatibility(tax1, tax2, pos, wordlist):
    graph = defaultdict(list)
    idxs1 = wordlist.get_list(language=tax1, flat=False)
    idxs2 = wordlist.get_list(language=tax2, flat=False)
    for idx1, idx2 in zip(idxs1, idxs2):
        if 0 not in (idx1, idx2):
            cog1, cog2 = wordlist[idx1, 'cogid'], wordlist[idx2, 'cogid']
            if cog1 == cog2:
                alm1, alm2 = [wordlist[x, 'alignment'] for x in [idx1, idx2]]
                char1, char2 = alm1[pos], alm2[pos]
                graph[char1, char2] += [cog1]
    return graph

def splits_and_mergers(graph):
    splits, mergers = defaultdict(set), defaultdict(set)
    for (a, b), sets in graph.items():
        if len(sets) > 1:
            splits[a].add(b)
            mergers[b].add(a)
    return splits, mergers

def largest_cliques(graph, iterate=2):
    clens = defaultdict(int)
    for n, d in graph.nodes(data=True):
        clens[d['clique']] += 1
    for n in graph.nodes():
        if graph.node[n]['clique'] != 0:
            graph.node[n]['clen'] = clens[graph.node[n]['clique']]

    for i, clique in enumerate(nx.find_cliques(graph)):
        clen = len(clique)
        for node in clique:
            if clen > graph.node[node].get('clen', 0):
                graph.node[node]['clique'] = i+1
                graph.node[node]['clen'] = clen

def reduce_edges(graph, threshold, key='weight'):
    badlist = []
    for a, b, c in graph.edges(data=True):
        if c[key] < threshold:
            badlist += [(a, b)]
    graph.remove_edges_from(badlist)

def compute_pairwise_network(alms, taxa):
    G = nx.Graph()
    for cogid, msa in alms.msa['cogid'].items():
        pattern = []
        for idx, tax in zip(msa['ID'], msa['taxa']):
            if tax not in alms.taxa:
                pattern += ['Ø']
            else:
                pattern += [alms[idx, 'alignment'][0]]
    
        G.add_node(str(cogid), 
                proto=alms[msa['ID'][0], 'proto'], 
                protoclass=alms[msa['ID'][0], 'proto_tokens'].split(' ')[0],
                pattern=' '.join(pattern),
                color=color_from_sound(alms[msa['ID'][0], 'proto_tokens'].split(' ')[0]),
                clique=0,
                clen=0
                )
    matrix = []
    for taxA, taxB in combinations(taxa, r=2):
        print("Computing {0} and {1}".format(taxA, taxB))
        corrs = compatibility(taxA, taxB, 0, alms)
        # threshold XXX 
        for val in corrs.values():
            if len(val) > 3:
                for a, b in combinations(val, r=2):
                    add_edge(G, str(a), str(b), weight=1)
        matrix += [distance(corrs)]
    return G, matrix

alms = load_alignments()
_t = int(argv[1]) if len(argv) > 1 else 10
_taxa = argv[2].split(',') if len(argv) > 2 else alms.taxa
try:
    G, matrix = pickle.load(open('pairdata.bin', 'rb'))
except:
    G, matrix = compute_pairwise_network(alms, _taxa)
    pickle.dump([G, matrix], open('pairdata.bin', 'wb')) 
reduce_edges(G, threshold_from_tlen(_t))

for i in range(5):
    print('computing cliques {0}'.format(i+1))
    largest_cliques(G)

save_network('../output/pair-sound-graph.gml', G)

# test for purity in cliques
groups = defaultdict(list)
for n, d in G.nodes(data=True):
    groups[d['clique']] += [n]
bads = []
purities = []
sounds = []
for clique, group in groups.items():
    if len(group) > 2:
        protos = [G.node[g]['protoclass'] for g in group]
        sprotos = sorted(set(protos), key=lambda x: protos.count(x),
                reverse=True)
        print(clique, '\t', len(group),
                ' '.join(sorted(set(protos), key=lambda x: protos.count(x),
                    reverse=True)))
        print('---')
        for p in sorted(set(protos), key=lambda x: protos.count(x),
                reverse=True):
            print('   ', '{0:5}'.format(p), '\t', protos.count(p))
        purity = protos.count(sprotos[0]) / len(protos)
        print('purity: {0:.2f}\n'.format(protos.count(sprotos[0]) / len(protos)))
        purities += [purity]
        sounds += [(sprotos, purity)]
    else:
        bads += [len(group)]
print('BADNESS: {0:.2f} ({1})'.format(sum(bads) / len(alms.msa['cogid']), sum(bads)), 
        'PURITY: {0:.2f}'.format(sum(purities) / len(purities)), 
        'CLUSTERS: {0}'.format(len(purities))
        )
for sound, purity in sorted(sounds, key=lambda x: x[0][0]):
    print(','.join(['{0:4}'.format(x) for x in sound]), '\t', '\t',
            '{0:.2f}'.format(purity).rjust(20))

tree = neighbor(squareform(matrix), _taxa)
with open('../output/nj-pw-tree.tre', 'w') as f: f.write(tree)
