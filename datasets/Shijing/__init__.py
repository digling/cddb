from clldutils.dsv import UnicodeReader
from sinopy import sinopy

def prepare(dataset):
    with UnicodeReader(dataset.get_path('raw', 'O_shijing.tsv'), delimiter='\t') as reader:
        data = list(reader)
    header = [h.lower() for h in data[0]]
    C = [('ID', 'CHARACTER', 'PINYIN', 'DOCULECT', 'SHIJING_NAME',
        'SHJING_NUMBER', 'STANZA', 'VERSE', 'RHYME_CLASS', 'POSITION', 'TEXT',
        'ORDER', 'SOURCE'
        )]
    for line in data[1:]:
        tmp = dict([(a, b.strip()) for a, b in zip(header, line)])
        
        poem = '·'.join((tmp['block'], tmp['chapter'], tmp['title']))
        poem_number = tmp['number']
        stanza = tmp['stanza']
        verse = tmp['verse']
        char = tmp['character']
        
        # get the position
        pos = str(tmp['raw_section'].index(char))
        text = tmp['raw_section'] + tmp['endchar']
        rhymeid = tmp['rhyme']
        pinyin = sinopy.pinyin(char)
        order = tmp['section_number']
        if '?' in pinyin or sinopy.is_chinese(pinyin):
            pinyin = ''

        C += [[tmp['id'], char, pinyin, 'Old_Chinese', poem, poem_number, stanza,
            verse, rhymeid, pos, text, order, 'Baxter1992']]

    with open(dataset.get_path('characters.tsv'), 'w') as f:
        for line in C:
            f.write('\t'.join(line)+'\n')
