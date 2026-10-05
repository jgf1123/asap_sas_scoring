"""Evaluation metrics for automated scores vs human scores.

Metrics follow the automated-scoring framework of Williamson, Xi & Breyer (2012):
QWK (>= 0.70), degradation vs human-human QWK (<= 0.10), standardized mean difference (|SMD| <= 0.15).

Usage (from the repo root): python common/evaluate.py --set 10 set10/results/<run>.jsonl [--cfg aaaaaa]
  Scores the run against Score1 using the LLM's own score and the score computed from its codes
  (set{N}/config.py codes_score).
"""
import argparse
import importlib
import json

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score


def qwk(a, b):
    return cohen_kappa_score(a, b, weights='quadratic')


def qwk_ci(a, b, n_boot=2000, seed=0):
    """Point QWK and a percentile bootstrap 95% CI (resampling responses)."""
    a, b = np.asarray(a), np.asarray(b)
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        i = rng.integers(0, len(a), len(a))
        if len(set(a[i])) > 1 and len(set(b[i])) > 1:
            stats.append(qwk(a[i], b[i]))
    return qwk(a, b), np.percentile(stats, 2.5), np.percentile(stats, 97.5)


def paired_qwk_diff_ci(human, a, b, n_boot=2000, seed=0):
    """QWK(human, a) - QWK(human, b) with a paired bootstrap 95% CI (same resampled responses)."""
    human, a, b = map(np.asarray, (human, a, b))
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(human), len(human))
        diffs.append(qwk(human[i], a[i]) - qwk(human[i], b[i]))
    return qwk(human, a) - qwk(human, b), np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)


def smd(machine, human):
    """Standardized mean difference: (mean machine - mean human) / pooled SD."""
    m, h = np.asarray(machine, float), np.asarray(human, float)
    return (m.mean() - h.mean()) / np.sqrt((m.var() + h.var()) / 2)


def report(human, machine, label, human_human_qwk=None):
    """One-row summary of machine vs human agreement."""
    q, lo, hi = qwk_ci(human, machine)
    row = {'scorer': label, 'n': len(human), 'QWK': round(q, 3), 'CI95': f'[{lo:.3f}, {hi:.3f}]',
           'exact': round(float(np.mean(np.asarray(human) == np.asarray(machine))), 3),
           'SMD': round(smd(machine, human), 3)}
    if human_human_qwk is not None:
        row['degradation'] = round(human_human_qwk - q, 3)
    return row


def load_run(path):
    r = pd.DataFrame([json.loads(line) for line in open(path, encoding='utf-8')])
    r = r[r.get('error', pd.Series(index=r.index, dtype=object)).isna()].copy()
    r['flags'] = r['flags'].apply(';'.join)  # r.flags would be pandas metadata, not the column
    return r


def main():
    import sys
    sys.path.insert(0, '.')

    ap = argparse.ArgumentParser()
    ap.add_argument('--set', type=int, required=True)
    ap.add_argument('run')
    ap.add_argument('--cfg', help='boundary config for code-derived scores (default: the run\'s own)')
    args = ap.parse_args()

    conf = importlib.import_module(f'set{args.set}.config')
    r = load_run(args.run)
    split = r.split.iloc[0]
    data = pd.read_csv(f'data/set{args.set}/{split}.csv')
    m = r.merge(data, on='Id')
    cfg = args.cfg or r.cfg.iloc[0]
    m['from_codes'] = [conf.codes_score(row, cfg) for row in m.to_dict('records')]

    hh = qwk(m.Score1, m.Score2) if 'Score2' in m else None
    rows = [report(m.Score1, m.score, 'LLM score', hh), report(m.Score1, m.from_codes, f'codes->rules ({cfg})', hh)]
    if 'Score2' in m:
        rows.append(report(m.Score1, m.Score2, 'Score2 (human reference)'))
    print(f'{args.run}: {len(m)} scored responses ({split})')
    print(pd.DataFrame(rows).to_string(index=False))
    print('\nConfusion, LLM score (rows Score1):')
    print(pd.crosstab(m.Score1, m.score))


if __name__ == '__main__':
    main()
