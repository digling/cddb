from pycddb.dataset import Dataset
from lingpy._plugins.chinese import sinopy

def prepare():
    wl = Wordlist(dataset.get_path('raw', 'bds.tsv'))
    wl.output('tsv', filename=dataset.get_path('words'))
