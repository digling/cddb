from pycddb.dataset import Dataset
from lingpy import *
import re
from sinopy import sinopy

def _clean_html(line):
    return re.sub('<.*?>', '', line).strip()

def check(dataset):
    
    D, idx, errors = [], 1, 1
    with open(dataset.get_path('raw', '08-Gan Appendix.html')) as f:
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
                    if sinopy.is_chinese(ch):
                        if qy:
                            D += [[str(idx), ch, py, 'Middle_Chinese', qy, str(page+1)]]
                            idx += 1
                        if cc:
                            D += [[str(idx), ch, py, 'Common_Chinese', cc, str(page+1)]]
                            idx += 1
                    else:
                        raise ValueError
                except ValueError:
                    print(errors, page+1, len(tmp), stack)
                    errors += 1
                stack = ''
            elif not cdc and qys:
                stack += ' '+_clean_html(line)

            pagex = re.findall('>([3-6][0-9][0-9])<', line)
            if pagex:
                page = int(pagex[0])

    with open(dataset.get_path('characters.tsv'), 'w') as f:
        f.write('ID\tCHARACTER\tPINYIN\tDOCULECT\tREADING\tPAGE\n')
        for line in D:
            f.write('\t'.join(line)+'\n')
