"""Candidate error-analysis cases: test disagreements under the selected config (all-b), tagged by deciding rule.

Writes set10/eda/error_candidates.md (git-ignored: quotes student responses).
"""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import load_run
from set10.score_from_codes import has, score

CODES = ['E', 'J', 'D', 'N', 'P', 'L', 'U']
A, B = (dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], c)) for c in ('aaaaaa', 'bbbbbb'))


def deciding_rule(r, cfg):
    """Which rule set the score (mirrors score_from_codes.score)."""
    n = bool(r['N']) and not (has(r['flags'], 'hyp') and cfg['B3'] == 'a') and not (has(r['flags'], 'vague') and cfg['B4'] == 'a')
    p, effect = bool(r['P']) and n, bool(r['E'] or r['J'])
    full = (p and effect) if r['group'] == 'gray' else (n and bool(r['E'] or r['D']))
    if full:
        return 'B5 mismatch' if has(r['flags'], 'mismatch') and cfg['B5'] == 'b' else 'full credit (O4)'
    if r['U']:
        return 'C1 U->0'
    if has(r['flags'], 'consistency') and not p:
        return 'B1 consistency'
    if r['L'] and n and not p:
        return 'B2 literal'
    if effect or n:
        return 'O2 partial'
    if has(r['flags'], 'physics') or r['D']:
        return 'B6 physics'
    return 'O3 nothing'


m = load_run('set10/results/test_v1.2.jsonl').merge(pd.read_csv('data/set10/test.csv'), on='Id')
m['group'] = m.text.str.split('::').str[0].str.contains('gray').map({True: 'gray', False: 'white/black'})
recs = m.to_dict('records')
m['b'] = [score(x, B) for x in recs]
m['a'] = [score(x, A) for x in recs]
m['rule'] = [deciding_rule(x, B) for x in recs]
e = m[m.b != m.Score1].copy()
e['cell'] = e.Score1.astype(str) + '->' + e.b.astype(str)
e['config_effect'] = e.a == e.Score1
print('Disagreements by cell and deciding rule (all-b):')
print(pd.crosstab(e.rule, e.cell, margins=True))
print('\nFixed by all-a (config effect):', e.config_effect.groupby(e.cell).sum().to_dict())

picks = []
for cell, g in e.groupby('cell'):
    g = g.sample(frac=1, random_state=0)
    k = 2 if abs(int(cell[0]) - int(cell[-1])) == 2 else 3
    picks.append(g.drop_duplicates('rule').head(k) if g.rule.nunique() >= k else g.head(k))
picks = pd.concat(picks)
lines = ['# Error-analysis candidates (test, config all-b)', '',
         'Codes are the LLM\'s. Student text quoted for review only: paraphrase before publishing.', '']
for r in picks.itertuples():
    codes = ' '.join(f'{c}={getattr(r, c)}' for c in CODES)
    lines += [f'## {r.Id}: Score1 {r.Score1} -> LLM {r.b} ({r.cell}); rule: {r.rule}; all-a gives {r.a}',
              f'- **Codes:** {codes}; flags: {r.flags or "none"}', f'- **LLM rationale:** {r.rationale}',
              f'- **Response:** {r.text}', '']
open('set10/eda/error_candidates.md', 'w', encoding='utf-8').write('\n'.join(lines))
print(f'\n{len(picks)} candidates written to set10/eda/error_candidates.md')
