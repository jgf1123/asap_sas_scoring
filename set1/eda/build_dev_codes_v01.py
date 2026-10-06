"""Build dev_codes_v01.csv: dev codes in the codebook v0.1 code set (rubric.md §4).

1. Start from dev_codes_v1.csv (blind codes + SIZE/MAT split overrides).
2. Mechanical mapping of "other" labels to the new v0.1 codes (labels consumed are removed from `other`):
     RINSE  rinse water amount, rinse method, rinse count     COVER  cover containers
     ENVT   temperature    ENVL light    ENVP storage conditions
     MASS   mass tool, mass method, mass units                DESIGN control, number of trials
     MATV   materials list (when not already MATV)
   Flag `labelled` is dropped (not in v0.1).
3. dev_overrides_v01.csv: the §3 coding principle (equipment lists, substitutions, catch-alls, unstated
   referents) applied to a rule-defined candidate set (set1/eda/dump_v01_candidates.py) without consulting
   scores, plus two cases found in step 3. `score_seen` = 1 where that response's scores had been seen
   (steps 1b-3), so the change is not blind.
"""
import pandas as pd

MAP = {'RINSE': {'rinse water amount', 'rinse method', 'rinse count'}, 'COVER': {'cover containers'},
       'ENVT': {'temperature'}, 'ENVL': {'light'}, 'ENVP': {'storage conditions'},
       'MASS': {'mass tool', 'mass method', 'mass units'}, 'DESIGN': {'control', 'number of trials'},
       'MATV': {'materials list'}}
CODES = ['VA', 'VT', 'MAT', 'MATV', 'MATK', 'SIZE', 'AMT', 'RT', 'RINSE', 'DRY', 'CS', 'CT', 'COVER',
         'ENVT', 'ENVL', 'ENVP', 'MASS', 'DESIGN']

c = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('').set_index('Id')
labels = c.other.map(lambda s: [o.strip() for o in s.split(';') if o.strip()])
for code, labs in MAP.items():
    hit = labels.map(lambda ls: int(any(l in labs for l in ls)))
    c[code] = (c[code] | hit) if code in c else hit
used = set().union(*MAP.values())
c['other'] = labels.map(lambda ls: ';'.join(l for l in ls if l not in used))
c['flags'] = c['flags'].map(lambda s: ';'.join(f for f in s.split(';') if f and f != 'labelled'))

o = pd.read_csv('set1/eda/dev_overrides_v01.csv', dtype={'old': str, 'new': str}).fillna('')
for r in o.itertuples():
    cur = c.at[r.Id, r.column]
    if r.column == 'flags':
        assert cur == r.old, (r.Id, cur, r.old)
        c.at[r.Id, 'flags'] = r.new
    else:
        assert int(cur) == int(r.old), (r.Id, r.column, cur, r.old)
        c.at[r.Id, r.column] = int(r.new)
c = c[['seen'] + CODES + ['other', 'flags', 'note']].reset_index()
c.to_csv('set1/eda/dev_codes_v01.csv', index=False)
print(f'{len(o)} v0.1 overrides ({int(o.score_seen.sum())} score-seen) -> set1/eda/dev_codes_v01.csv')
print('code counts:', {k: int(c[k].sum()) for k in CODES})
