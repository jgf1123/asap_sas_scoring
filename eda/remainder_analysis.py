"""Pre-registered remainder analysis (eda/prereg_remainder.md): 3 configs, all 1340 and excluding the 60 blind-coded."""
import sys

import pandas as pd

sys.path.insert(0, '.')
from evaluate import load_run, paired_qwk_diff_ci, qwk, report
from score_from_codes import score

CONFIGS = {'all-a': 'aaaaaa', 'majority': 'aaaabb', 'all-b': 'bbbbbb'}
RULES = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']

raw = [l for l in open('results/remainder_v1.2.jsonl', encoding='utf-8')]
r = load_run('results/remainder_v1.2.jsonl')
assert len(raw) == len(r) == 1340 and set(r.prompt_hash) == {'34e06a141c41'}, 'run incomplete or wrong prompt'
m = r.merge(pd.read_csv('data/set10/remainder.csv'), on='Id')
m['group'] = m.text.str.split('::').str[0].str.contains('gray').map({True: 'gray', False: 'white/black'})
for name, c in CONFIGS.items():
    cfg = dict(zip(RULES, c))
    m[name] = [score(row, cfg) for row in m.to_dict('records')]
print(f'LLM own score == all-a from its codes (prompt used all-a): {(m.score == m["all-a"]).mean():.3f}')

seen = set(pd.read_csv('eda/remainder_sample_ids.csv').Id)
for label, d in (('ALL 1340', m), ('EXCLUDING 60 blind-coded (n=%d)' % (~m.Id.isin(seen)).sum(), m[~m.Id.isin(seen)])):
    hh = qwk(d.Score1, d.Score2)
    print(f'\n=== {label} ===')
    rows = [report(d.Score1, d[n], f'{n} ({c})', hh) for n, c in CONFIGS.items()]
    rows.append(report(d.Score1, d.Score2, 'Score2 (human reference)'))
    print(pd.DataFrame(rows).to_string(index=False))
    for n in ('majority', 'all-b'):
        diff, lo, hi = paired_qwk_diff_ci(d.Score1, d[n], d['all-a'])
        print(f'  QWK({n}) - QWK(all-a) = {diff:+.3f}, paired 95% CI [{lo:+.3f}, {hi:+.3f}]')

best = max(CONFIGS, key=lambda n: qwk(m.Score1, m[n]))
print(f'\nSELECTED by pre-registered rule (highest QWK, all 1340): {best} ({CONFIGS[best]})')
for n in CONFIGS:
    print(f'\nConfusion {n} (rows Score1):'); print(pd.crosstab(m.Score1, m[n]))
