import re
from sinopy import sinopy

def prepare(dataset):
    
    img_url = "http://kanji-database.sourceforge.net/dict/swjz/swjz-img/"

    with open(dataset.get_path('raw', 'swjz.xml')) as f:
        data = f.readlines()
    
    wordheads = {}
    blocks, chapter, idx = {}, '', 1
    blocks[idx] = ''
    for i, line in enumerate(data):
        if '<chaptertitle id' in line:
            chapter = re.findall('id="(.*?)"', line)[0]
        
        if blocks[idx]:
            blocks[idx]['text'] += '\n' + line.strip()

        if '<shuowen>' in line:
            blocks[idx] = dict(text = line.strip(), chapter=chapter)

        if '</shuowen>' in line:
            idx += 1
            blocks[idx] = False

    for i, block in [(a, b) for a, b in blocks.items() if b]:
        
        for line in block['text'].split('\n'):
            if 'wordhead' in line:
                wid, img, char = re.findall('id="(.*?)" img="(.*?)">(.*?)<',
                        line)[0]
                pinyin = sinopy.pinyin(char)
                if '?' in pinyin or sinopy.is_chinese(pinyin):
                    pinyin = ''
                wordheads[wid] = dict(explanations=[], char=char, notes=[],
                        img=img, block=i+1, pinyin=pinyin,
                        doculect='Old_Chinese', chapter=block['chapter'])
            if 'explanation>' in line:
                wordheads[wid]['explanations'] += [re.findall('>(.*?)<', line)[0]]
                structure = re.findall('从(.)。(.)聲', line)
                if structure:
                    wordheads[wid]['radical'] = structure[0][0]
                    wordheads[wid]['phonetic'] = structure[0][1]
            if 'duan_note>' in line:
                wordheads[wid]['notes'] += [re.findall('>(.*?)<',
                    line)[0]]
                fq = re.findall('>(..)切。', line)
                if fq and sinopy.is_chinese(fq[0]):
                    wordheads[wid]['fanqie'] = fq[0]
                bu = re.findall('(.)部。', line)
                if bu and sinopy.is_chinese(bu):
                    wordheads[wid]['rhyme'] = bu[0]

    with open(dataset.get_path('characters.tsv'), 'w') as f:
        f.write('ID\tCHARACTER_ID\tGROUP\tCHARACTER\tPINYIN\tDOCULECT\tRADICAL\tPHONETIC\tFANQIE\tRHYME\tCHAPTER\tIMAGE\n')
        idx = 1
        for k, vals in sorted(wordheads.items(), key=lambda x: x[0]):
            addons = []
            for key in ['block', 'char', 'pinyin', 'doculect', 'radical', 'phonetic', 'fanqie', 
                    'rhyme', 'chapter', 'img']:
                val = vals.get(key, '')
                if isinstance(val, list):
                    val = ' / '.join(val)
                addons += [str(val).replace('\t', ' ')]
            f.write(str(idx)+'\t'+k+'\t'+'\t'.join(addons)+'\n')  
            idx += 1
