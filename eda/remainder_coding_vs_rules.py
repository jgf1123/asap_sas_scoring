"""Exploratory: on the 60 blind-coded remainder responses, v1.2 rules applied to hand codes vs LLM codes."""
import sys

import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, '.')
from evaluate import load_run, qwk
from score_from_codes import score

CODES = ['E', 'J', 'D', 'N', 'P', 'L', 'U']
hand = pd.read_csv('eda/remainder_blind_codes.csv').fillna({'flags': ''})
llm = load_run('results/remainder_v1.2.jsonl').merge(hand[['Id', 'group']], on='Id')
rem = pd.read_csv('data/set10/remainder.csv').set_index('Id')
h, l = hand.set_index('Id'), llm.set_index('Id').loc[hand.Id]
s1, s2 = rem.loc[hand.Id, 'Score1'], rem.loc[hand.Id, 'Score2']
print(f'n={len(hand)} | human Score2 vs Score1 QWK {qwk(s1, s2):.3f}')
for c in ('aaaaaa', 'bbbbbb'):
    cfg = dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], c))
    ph = [score(r, cfg) for r in h.reset_index().to_dict('records')]
    pl = [score(r, cfg) for r in l.reset_index().to_dict('records')]
    print(f'{c}: v1.2 rules on hand codes QWK {qwk(s1, ph):.3f} | on LLM codes QWK {qwk(s1, pl):.3f} | '
          f'hand vs LLM rule scores identical {sum(a == b for a, b in zip(ph, pl))}/{len(ph)}')
print('Per-code kappa, hand vs LLM:', {c: round(cohen_kappa_score(h[c], l[c]), 2) for c in CODES})
