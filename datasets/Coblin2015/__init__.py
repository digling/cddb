from pycddb.dataset import Dataset
from lingpy import *
import re

def _clean_html(line):
    return re.sub('<.*?>', '', line).strip()

def check(dataset):
    
    D, idx, errors = [], 1, 1
    with open(dataset.get_path(['raw', '08-Gan Appendix.html'])) as f:
        stack = ''
        qys, cdc = False, True
        page = 360
        for line in f:
            if 'QYS' in line and cdc:
                stack += _clean_html(line)
                qys = True
                cdc = False
            elif 'CDC' in line and qys:
                stack += ' '+_clean_html(line)
                cdc = True
                qys = False
                tmp = re.split(r'\s*', stack)
                try:
                    py, ch, _qy, qy, _cc, cc = tmp
                    D += [[str(idx), ch, py, qy, cc, str(page+1)]]
                    idx += 1
                except ValueError:
                    print(errors, page+1, len(tmp), stack)
                    errors += 1
                stack = ''
            elif not cdc and qys:
                stack += ' '+_clean_html(line)

            pagex = re.findall('>([3-6][0-9][0-9])<', line)
            if pagex:
                page = int(pagex[0])

    with open(dataset.get_path(['characters.tsv']), 'w') as f:
        f.write('ID\tCHARACTER\tPINYIN\tQIEYUN\tCOMMON_CHINESE\tPAGE\n')
        for line in D:
            f.write('\t'.join(line)+'\n')
