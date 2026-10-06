"""Candidates for the v0.1 coding-principle re-read (codebook §3), printed WITHOUT scores.

Candidates: responses with at least one code in v1 AND (flag `change`, OR an equipment-type "other" label,
OR a coding note saying assumed / inferred / ambiguous / equipment). Defined by rule, not by score comparison.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CODES = ['VA', 'VT', 'MAT', 'MATV', 'MATK', 'SIZE', 'AMT', 'RT', 'DRY', 'CS', 'CT']
EQUIP = {'materials list', 'handling tool', 'timer', 'safety', 'labelling'}
c = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
labels = c.other.map(lambda s: {o.strip() for o in s.split(';') if o.strip()})
cand = (c[CODES].sum(axis=1) > 0) & (c['flags'].str.contains('change') | labels.map(lambda s: bool(s & EQUIP))
                                     | c.note.str.contains('assum|inferr|ambig|equipment', case=False))
x = c[cand].merge(pd.read_csv('data/set1/dev.csv', usecols=['Id', 'text']), on='Id')
print(f'{len(x)} candidates')
for r in x.sort_values('Id').to_dict('records'):
    codes = ','.join(k for k in CODES if r[k])
    print(f'{r["Id"]} | {codes} | other: {r["other"] or "-"} | flags: {r["flags"] or "-"} | note: {r["note"] or "-"}')
    print(f'    {r["text"].replace("^p", " ⏎ ")}')
