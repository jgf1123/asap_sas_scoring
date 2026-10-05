"""Compare two scoring runs response by response: score and code differences.

Usage: python eda/compare_runs.py results/a.jsonl results/b.jsonl
"""
import json
import sys

import pandas as pd

CODES = ['E', 'J', 'D', 'N', 'P', 'L', 'U']
load = lambda p: pd.DataFrame([json.loads(l) for l in open(p, encoding='utf-8')]).set_index('Id')
a, b = load(sys.argv[1]), load(sys.argv[2])
ids = a.index.intersection(b.index)
print(f'{len(ids)} common responses | score changed: {(a.loc[ids, "score"] != b.loc[ids, "score"]).sum()}')
for i in ids:
    diffs = [f'{c}:{a.at[i, c]}->{b.at[i, c]}' for c in CODES if a.at[i, c] != b.at[i, c]]
    fa, fb = sorted(a.at[i, 'flags']), sorted(b.at[i, 'flags'])
    if fa != fb:
        diffs.append(f'flags:{fa}->{fb}')
    if diffs or a.at[i, 'score'] != b.at[i, 'score']:
        print(f'\n{i}: score {a.at[i, "score"]}->{b.at[i, "score"]} | {", ".join(diffs)}')
        print(f'  A: {a.at[i, "rationale"]}\n  B: {b.at[i, "rationale"]}')
