"""Step 1b: truncated transcriptions. Short responses with high scores, and how common unfinished endings are.

Part 1 prints the train responses with Score1 >= 2 and <= 10 words (all six are in the remainder; their Ids
are recorded in remainder_seen_ids.csv so remainder results can be reported with and without them).
Part 2 counts, from text only, responses that end without . ! ? and those whose last word is also rare in
the Set 1 corpus (a noisy mid-word-cut signal), by split; for train, their Score1 distribution and length.
"""
import re
import sys
from collections import Counter

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
d = pd.concat([pd.read_csv(f'data/set1/{s}.csv').assign(split=s) for s in ('dev', 'remainder', 'test')])
d['words'] = d.text.str.replace('^p', ' ', regex=False).str.split().str.len()

print('== 1. Score1 >= 2 with <= 10 words (train) ==')
tr = d[d.split != 'test']
x = tr[(tr.Score1 >= 2) & (tr.words <= 10)].sort_values('words')
for r in x.itertuples():
    print(f'{r.Id} [{r.split}] S1={r.Score1:.0f} S2={r.Score2:.0f} words={r.words}: {r.text!r}')
raw = pd.read_csv('data/train.tsv', sep='\t').set_index('Id')
print('identical to raw train.tsv:', all(raw.EssayText[i] == t for i, t in zip(x.Id, x.text)))

print('\n== 2. Unfinished endings (text only) ==')
toks = [re.findall(r'[A-Za-z]+', t.lower()) for t in d.text]
vocab = Counter(w for ts in toks for w in ts)
d['last'] = [ts[-1] if ts else '' for ts in toks]
d['no_end_punct'] = ~d.text.str.rstrip().str[-1].isin(list('.!?'))
d['rare_last'] = [vocab[w] < 3 for w in d['last']]  # < 3 in total = used fewer than 2 times elsewhere
d['midword'] = d.no_end_punct & d.rare_last
print('ends without . ! ? :', d.groupby('split').no_end_punct.agg(['sum', 'mean']).round(3).to_dict('index'))
print('likely mid-word cut :', d.groupby('split').midword.agg(['sum', 'mean']).round(3).to_dict('index'))
print('last tokens of likely mid-word cuts:', sorted(d[d.midword]['last'].tolist()))

tr = d[d.split != 'test']
pct = lambda x: x.Score1.value_counts(normalize=True).sort_index().mul(100).round(0).astype(int).to_dict()
for name, m in (('likely mid-word cut', tr.midword), ('no end punctuation', tr.no_end_punct), ('all train', tr.Score1 >= 0)):
    x = tr[m]
    print(f'{name:20s} n={len(x):4d} Score1 %={pct(x)} | mean words {x.words.mean():.0f}'
          f' | mean words at Score1>=2: {x[x.Score1 >= 2].words.mean():.0f}')
