import re
from sinopy import sinopy

def prepare(dataset):
    
    img_url = "http://kanji-database.sourceforge.net/dict/swjz/swjz-img/"

    with open(dataset.get_path(['raw', 'swjz.xml'])) as f:
        data = f.read()
    
    wordheads = {}
    blocks = re.findall('<shuowen>(.*?)</shuowen>', data, re.DOTALL)
    for i, block in enumerate(blocks):
        
        for line in block.split('\n'):
            if 'wordhead' in line:
                wid, img, char = re.findall('id="(.*?)" img="(.*?)">(.*?)<',
                        line)[0]
                pinyin = sinopy.pinyin(char)
                if '?' in pinyin or sinopy.is_chinese(pinyin):
                    pinyin = ''
                wordheads[wid] = dict(explanations=[], char=char, notes=[],
                        img=img, block=i+1, pinyin=pinyin,
                        doculect='Old_Chinese')
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

    with open(dataset.get_path(['characters.tsv']), 'w') as f:
        f.write('ID\tGROUP\tCHARACTER\tPINYIN\tDOCULECT\tRADICAL\tPHONETIC\tFANQIE\tRHYME\tIMAGE\n')
        for k, vals in sorted(wordheads.items(), key=lambda x: x[0]):
            addons = []
            for key in ['block', 'char', 'pinyin', 'doculect', 'radical', 'phonetic', 'fanqie', 
                    'rhyme', 'img']:
                val = vals.get(key, '')
                if isinstance(val, list):
                    val = ' / '.join(val)
                addons += [str(val)]
            f.write(k+'\t'+'\t'.join(addons)+'\n')  
