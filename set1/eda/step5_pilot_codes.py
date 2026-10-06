"""Step 5: pilot coding agreement, model codes vs my v0.1 dev codes (NOT vs human scores).

Usage: python set1/eda/step5_pilot_codes.py set1/results/<run>.jsonl
Per code: both 1, model only, mine only. Flags likewise. Derived score (rubric §5) from each code set.
Disagreements are listed with text, model rationale and "other", to judge whether the codebook or my
coding is unclear. Also reports tokens and cost.
"""
import json
import sys

import pandas as pd

sys.path.insert(0, '.')
from set1.config import CODES, FLAGS
from set1.score_from_codes import score

sys.stdout.reconfigure(encoding='utf-8')
run = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
m = pd.DataFrame([r for r in run if 'error' not in r]).set_index('Id')
mine = pd.read_csv('set1/eda/dev_codes_v01.csv', dtype={'other': str, 'flags': str, 'note': str}).fillna('').set_index('Id').loc[m.index]
text = pd.read_csv('data/set1/dev.csv', usecols=['Id', 'text']).set_index('Id').text

print(f'{len(m)} responses coded, {sum("error" in r for r in run)} errors')
rows = []
for c in CODES:
    a, b = m[c].astype(int), mine[c].astype(int)
    rows.append({'code': c, 'both': int((a & b).sum()), 'model only': int((a & ~b & 1).sum()),
                 'mine only': int((~a & 1 & b).sum()), 'agree': int((a == b).sum())})
for f in FLAGS:
    a = m['flags'].map(lambda x: int(f in x))
    b = mine['flags'].map(lambda x: int(f in x.split(';')))
    rows.append({'code': f'flag:{f}', 'both': int((a & b).sum()), 'model only': int((a & ~b & 1).sum()),
                 'mine only': int((~a & 1 & b).sum()), 'agree': int((a == b).sum())})
t = pd.DataFrame(rows)
print(t[(t['model only'] + t['mine only'] + t['both']) > 0].to_string(index=False))
cells = len(m) * len(CODES)
dis = int(t[~t.code.str.startswith('flag')][['model only', 'mine only']].sum().sum())
print(f'code cells: {cells}, disagreements: {dis} ({dis / cells:.1%})')

m['s_model'] = [score(r) for r in m.to_dict('records')]
mine['s_mine'] = [score(r) for r in mine.to_dict('records')]
print(f'derived score equal: {int((m.s_model == mine.s_mine).sum())}/{len(m)}')

u = pd.DataFrame([r['usage'] for r in run])
cost = (u.input_tokens * 4 + u.cache_creation_input_tokens.fillna(0) * 5 + u.cache_read_input_tokens.fillna(0) * 0.4
        + u.output_tokens * 20) / 1e6
print(f'tokens: output mean {u.output_tokens.mean():.0f} | cost ${cost.sum():.2f} (${cost.mean():.4f}/response)')

print('\n== Responses with any code disagreement ==')
for i in m.index:
    diff = [f'{c}: model {int(m.at[i, c])} mine {int(mine.at[i, c])}' for c in CODES if int(m.at[i, c]) != int(mine.at[i, c])]
    if diff:
        print(f'{i} | {"; ".join(diff)} | score model {m.at[i, "s_model"]} mine {mine.at[i, "s_mine"]}')
        print(f'    text: {text[i].replace("^p", " / ")}')
        print(f'    model other: {m.at[i, "other"]} | flags: {m.at[i, "flags"]} | rationale: {m.at[i, "rationale"]}')
        print(f'    my other: {mine.at[i, "other"] or "-"} | note: {mine.at[i, "note"] or "-"}')
