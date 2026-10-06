"""Merge the blind-coding batches (dev_part*_codes.csv) into dev_codes.csv and validate against dev Ids.

Prints code and label frequencies only (no scores).
"""
import glob
import sys
from collections import Counter

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CODES = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'CS', 'CT']
parts = sorted(glob.glob('set1/eda/dev_part*_codes.csv'))
c = pd.concat([pd.read_csv(p, dtype={'other': str, 'flags': str, 'note': str}) for p in parts], ignore_index=True)
dev = pd.read_csv('data/set1/dev.csv', usecols=['Id'])
assert c.Id.is_unique, c.Id[c.Id.duplicated()].tolist()
assert set(c.Id) == set(dev.Id), (set(dev.Id) - set(c.Id), set(c.Id) - set(dev.Id))
assert c[CODES + ['seen']].isin([0, 1]).all().all()
c = c.fillna({'other': '', 'flags': '', 'note': ''}).sort_values('Id')
c.to_csv('set1/eda/dev_codes.csv', index=False)
print(f'{len(parts)} parts -> set1/eda/dev_codes.csv: {len(c)} responses, seen={int(c.seen.sum())}')

print('\nCode frequency (% of 300):', {k: f'{int(c[k].sum())} ({c[k].mean():.0%})' for k in CODES})
c['n_codes'] = c[CODES].sum(axis=1)
print('Distinct rubric codes per response:', c.n_codes.value_counts().sort_index().to_dict())
c['n_codes_container1'] = c.n_codes - (c.CS & c.CT)
print('  if CS and CT count once:', c.n_codes_container1.value_counts().sort_index().to_dict(), f'(both CS and CT: {int((c.CS & c.CT).sum())})')

flags = Counter(f for s in c['flags'] for f in s.split(';') if f)
print('\nFlags:', dict(flags.most_common()))
other = Counter(o.strip() for s in c.other for o in s.split(';') if o.strip())
print(f'\n"other" labels ({sum(other.values())} mentions, {len(other)} labels, in {int((c.other != "").sum())} responses):')
for k, v in other.most_common():
    print(f'  {v:3d}  {k}')
