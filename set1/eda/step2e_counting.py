"""Step 2e: counting questions. Do raters count several environment items, or container size + type, as one piece?

base = credited rubric codes without AMT (and without the items under test) + cover containers.
For each question, two predictions are compared with the scores where they differ:
  one piece  min(3, base + 1)        separate  min(3, base + n items)
Agreed cases (Score1 == Score2) are the evidence; disagreements are listed separately. Texts are printed so
that double-labelled single ideas (e.g. "environment, such as temperature") can be spotted.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CREDITED = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'CS', 'CT']
ENV = ['temperature', 'light', 'storage conditions']
c = pd.read_csv('set1/eda/dev_codes_v1.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('')
d = c.merge(pd.read_csv('data/set1/dev.csv'), on='Id', validate='one_to_one')
labels = d.other.map(lambda s: {o.strip() for o in s.split(';') if o.strip()})
d['n_env'] = labels.map(lambda s: len(s & set(ENV)))
d['cover'] = labels.map(lambda s: int('cover containers' in s))


def check(title, x, n_items, base):
    one, sep = (base + 1).clip(upper=3), (base + n_items).clip(upper=3)
    x = x.assign(one=one, sep=sep)
    differ = x[x.one != x.sep]
    print(f'\n===== {title}: {len(x)} responses, predictions differ for {len(differ)} =====')
    for name, g in (('agreed', differ[differ.Score1 == differ.Score2]), ('disagreed', differ[differ.Score1 != differ.Score2])):
        if len(g):
            print(f'-- {name} (n={len(g)}): Score1 matches one-piece {int((g.Score1 == g.one).sum())},'
                  f' separate {int((g.Score1 == g.sep).sum())}, neither {int(((g.Score1 != g.one) & (g.Score1 != g.sep)).sum())}')
        for r in g.sort_values('Id').to_dict('records'):
            print(f'  {r["Id"]} S1={r["Score1"]} S2={r["Score2"]} one={r["one"]} sep={r["sep"]} | other: {r["other"]}')
            print(f'      {r["text"].replace("^p", " ⏎ ")}')


env = d[d.n_env >= 2]
check('Q1 environment items (2+ distinct labels)', env, env.n_env, env[CREDITED].sum(axis=1) + env.cover)
cont = d[(d.CS == 1) & (d.CT == 1)]
check('Q2 container size and type', cont, 2, cont[[k for k in CREDITED if k not in ('CS', 'CT')]].sum(axis=1)
      + cont.cover + (cont.n_env > 0))
print(f'\n(n with exactly one environment label: {int((d.n_env == 1).sum())}; with 2+: {len(env)})')
