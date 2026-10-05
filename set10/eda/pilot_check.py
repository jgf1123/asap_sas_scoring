"""Pilot check: well-formedness, cost, LLM vs Score1, LLM score vs its own codes, LLM codes vs hand codes.

Usage: python set10/eda/pilot_check.py set10/results/pilot1.jsonl
"""
import json
import sys

import pandas as pd

sys.path.insert(0, '.')
from set10.score_from_codes import score

PRICE = {'claude-opus-5-5': (4.00, 20.00, 0.20, 5.00), 'claude-sonnet-5-5': (2.00, 10.00, 0.20, 2.50)}  # in, out, cache read, cache write ($/MTok)
CODES = ['E', 'J', 'D', 'N', 'P', 'L', 'U']

recs = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
r = pd.DataFrame(recs)
print(f'records {len(r)} | errors {r.get("error", pd.Series(dtype=str)).notna().sum()} | stop_reasons {r.stop_reason.value_counts().to_dict()}')

u = pd.json_normalize(r.usage)
p_in, p_out, p_cr, p_cw = PRICE[r.model.iloc[0]]
cost = (u.input_tokens * p_in + u.output_tokens * p_out + u.cache_read_input_tokens.fillna(0) * p_cr
        + u.cache_creation_input_tokens.fillna(0) * p_cw) / 1e6
print(f'tokens/resp: input {u.input_tokens.mean():.0f}, cache read {u.cache_read_input_tokens.mean():.0f}, '
      f'cache write {u.cache_creation_input_tokens.mean():.0f}, output {u.output_tokens.mean():.0f}')
print(f'cost: ${cost.sum():.3f} total, ${cost.mean():.4f}/response | {r.seconds.mean():.1f} s/response')

cfg = dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], r.cfg.iloc[0]))
r['flags'] = r['flags'].apply(';'.join)  # r.flags is DataFrame metadata, not the column
dev = pd.read_csv('data/set10/dev.csv').merge(pd.read_csv('set10/eda/dev_codes.csv'), on='Id', suffixes=('', '_hand'))
m = r.merge(dev, on='Id', suffixes=('_llm', '_hand'))
m['from_codes'] = m.apply(lambda x: score({**{c: x[f'{c}_llm'] for c in CODES}, 'flags': x['flags_llm'], 'group': x['group']}, cfg), axis=1)

print('\nLLM score vs Score1 (rows Score1):'); print(pd.crosstab(m.Score1, m.score))
print(f'LLM score == score computed from its own codes: {(m.score == m.from_codes).mean():.2f}')
print('Per-code agreement, LLM vs hand codes:', {c: round((m[f"{c}_llm"] == m[f"{c}_hand"]).mean(), 2) for c in CODES})

cols = ['Id', 'Score1', 'Score2', 'score', 'from_codes'] + [f'{c}_llm' for c in CODES] + ['flags_llm', 'rationale']
print('\nDisagreements with Score1:')
pd.set_option('display.max_colwidth', 160)
print(m[m.score != m.Score1][cols].to_string(index=False))
