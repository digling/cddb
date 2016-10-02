import networkx as nx
import html
import lingpy

_color = lingpy.Model('color')
def save_network(filename, graph):
    with open(filename, 'w') as f:
        for line in nx.generate_gml(graph):
            f.write(html.unescape(line)+'\n')

def color_from_sound(sound, color=_color):
    return lingpy.sequence.sound_classes.token2class(sound, color)

def load_alignments():
    return lingpy.Alignments('../yinku-chars/yinku.tsv')

def add_edge(G, source, target, **values):
    try:
        for a, b in values.items():
            G.edge[source][target][a] += b
    except KeyError:
        G.add_edge(source, target, **values)
