"""What-if on dev LLM codes: U overrides only responses that would not otherwise earn 2."""
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import load_run, qwk
from set10.score_from_codes import score

dev = pd.read_csv('data/set10/dev.csv')
grp = pd.read_csv('set10/eda/dev_codes.csv')[['Id', 'group']]
for run in ('r1', 'r2'):
    r = load_run(f'set10/results/dev_v1.1_{run}.jsonl').merge(dev, on='Id').merge(grp, on='Id')
    for name, cfgs in (('all-a', 'aaaaaa'), ('all-b', 'bbbbbb')):
        cfg = dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], cfgs))
        rows = r.to_dict('records')
        base = [score(x, cfg) for x in rows]
        scoped = [2 if x['U'] and score({**x, 'U': 0}, cfg) == 2 else s for x, s in zip(rows, base)]
        changed = sum(a != b for a, b in zip(base, scoped))
        print(f'{run} {name}: QWK v1.1 {qwk(r.Score1, base):.3f} -> U-scoped {qwk(r.Score1, scoped):.3f} ({changed} responses change)')
