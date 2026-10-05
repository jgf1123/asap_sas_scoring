"""Two repeat LLM runs on dev: agreement with Score1, run-to-run noise, LLM vs hand codes, config sweep.

Usage: python set10/eda/dev_runs_analysis.py set10/results/dev_v1.1_r1.jsonl set10/results/dev_v1.1_r2.jsonl
"""
import itertools
import sys

import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, '.')
from common.evaluate import load_run, paired_qwk_diff_ci, qwk, report
from set10.score_from_codes import score

CODES = ['E', 'J', 'D', 'N', 'P', 'L', 'U']
RULES = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
PREREG = {'all-a': 'aaaaaa', 'dev-best (hand codes)': 'bababb', 'all-b': 'bbbbbb'}

dev = pd.read_csv('data/set10/dev.csv')
hand = pd.read_csv('set10/eda/dev_codes.csv').fillna({'flags': ''})
runs = [load_run(p).merge(dev, on='Id').merge(hand[['Id', 'group']], on='Id') for p in sys.argv[1:3]]
ids = sorted(set(runs[0].Id) & set(runs[1].Id))
r1, r2 = (r.set_index('Id').loc[ids] for r in runs)
hh = qwk(r1.Score1, r1.Score2)
print(f'{len(ids)} responses scored in both runs\n')

print('1. LLM score vs Score1')
rows = [report(r1.Score1, r1.score, 'run 1', hh), report(r1.Score1, r2.score, 'run 2', hh),
        report(r1.Score1, r1.Score2, 'Score2 (human reference)')]
print(pd.DataFrame(rows).to_string(index=False))
d, lo, hi = paired_qwk_diff_ci(r1.Score1, r1.score, r2.score)
print(f'QWK(run1) - QWK(run2) = {d:+.3f}, paired 95% CI [{lo:+.3f}, {hi:+.3f}]')
print('Confusion run 1 (rows Score1):'); print(pd.crosstab(r1.Score1, r1.score))

print('\n2. Run-to-run noise')
print(f'score identical: {(r1.score == r2.score).mean():.3f} | QWK(run1, run2): {qwk(r1.score, r2.score):.3f}')
print('code identical:', {c: round((r1[c] == r2[c]).mean(), 3) for c in CODES})
print(f'any code or flag differs: {((r1[CODES] != r2[CODES]).any(axis=1) | (r1.flags != r2.flags)).mean():.3f}')

print('\n3. LLM codes vs hand codes (dev_codes.csv; hand codes fitted to dev)')
h = hand.set_index('Id').loc[ids]
rows = []
for c in CODES:
    rows.append({'code': c, 'hand rate': round(h[c].mean(), 2), 'LLM rate r1': round(r1[c].mean(), 2),
                 'agree r1': round((r1[c] == h[c]).mean(), 3), 'kappa r1': round(cohen_kappa_score(h[c], r1[c]), 3),
                 'kappa r2': round(cohen_kappa_score(h[c], r2[c]), 3), 'kappa r1 vs r2': round(cohen_kappa_score(r1[c], r2[c]), 3)})
print(pd.DataFrame(rows).to_string(index=False))

print('\n4. Config sweep: QWK vs Score1 from LLM codes (run 1, run 2) and from hand codes')
def sweep_qwk(frame, cfg):
    return qwk(frame.Score1, [score(row, cfg) for row in frame.reset_index().to_dict('records')])
hf = h.assign(Score1=r1.Score1)
res = []
for variants in itertools.product('ab', repeat=6):
    cfg = dict(zip(RULES, variants))
    res.append({'cfg': ''.join(variants), 'run1': sweep_qwk(r1, cfg), 'run2': sweep_qwk(r2, cfg), 'hand': sweep_qwk(hf, cfg)})
res = pd.DataFrame(res).round(3)
res['mean_llm'] = ((res.run1 + res.run2) / 2).round(3)
print('Pre-registered configs:')
print(res[res.cfg.isin(PREREG.values())].assign(name=lambda x: x.cfg.map({v: k for k, v in PREREG.items()})).to_string(index=False))
print(f'Spread across 64 configs (mean of runs): min {res.mean_llm.min():.3f}, max {res.mean_llm.max():.3f}')
print(f'Run-to-run gap for the same config: mean |run1-run2| = {(res.run1 - res.run2).abs().mean():.3f}, max {(res.run1 - res.run2).abs().max():.3f}')
print('Top 5 by mean of runs:'); print(res.sort_values('mean_llm', ascending=False).head(5).to_string(index=False))
print('\nToggle effects (mean over other settings, mean of runs):')
for i, b in enumerate(RULES):
    print(f'  {b}: a={res[res.cfg.str[i] == "a"].mean_llm.mean():.3f}  b={res[res.cfg.str[i] == "b"].mean_llm.mean():.3f}')
