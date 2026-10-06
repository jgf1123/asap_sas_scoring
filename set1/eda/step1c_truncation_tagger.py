"""Step 1c: rule-based tagger for unfinished endings (text only), and Score1 by tag.

An unfinished ending can mean the student stopped (the rater saw the same text: expect low scores) or the
transcription was cut (the rater saw more: scores can be high). Tags, from the text alone:
  complete  ends with . ! ? ) or a quote
  dangling  no end punctuation; last word cannot end a sentence (article, preposition, conjunction,
            auxiliary, subject pronoun, need/know/how/what/much...)
  fragment  no end punctuation; last word is rare in Set 1 (< 3 uses in total): possible mid-word cut
  open      no end punctuation; ends on an ordinary content word (often just a missing period)
Score1 by tag and by length is aggregated over all train responses; texts are printed for dev only.
"""
import re
import sys
from collections import Counter

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
CANNOT_END = set('''a an the of to in into on onto for with by from at about as than
and or but because so if that which who whose when where while
is are was were be been being am do does did would will should could can may might must shall have has had
i you we they he she it its their your my our his her
need needs know knows how what much many each every also more very use put make
another other some any this these those there'''.split())

d = pd.concat([pd.read_csv(f'data/set1/{s}.csv').assign(split=s) for s in ('dev', 'remainder')], ignore_index=True)
d['words'] = d.text.str.replace('^p', ' ', regex=False).str.split().str.len()
vocab = Counter(w for t in d.text for w in re.findall(r'[a-z]+', t.lower()))


def tag(text):
    t = re.sub(r'(\s|\^p)+$', '', text)
    if t[-1:] in set('.!?)"\''):
        return 'complete'
    last = (re.findall(r'[A-Za-z]+', t) or [''])[-1].lower()
    if last in CANNOT_END:
        return 'dangling'
    if vocab[last] < 3:
        return 'fragment'
    return 'open'


d['tag'] = d.text.map(tag)
d['length'] = pd.cut(d.words, [0, 15, 1000], labels=['<=15 words', '>15 words'])
order = ['complete', 'open', 'fragment', 'dangling']
pct = lambda g: g.value_counts(normalize=True).reindex(range(4), fill_value=0).mul(100).round(0).astype(int)

print(f'== 1. Score1 % by tag (train n={len(d)}) ==')
t1 = d.groupby('tag').Score1.apply(pct).unstack().reindex(order)
t1['n'] = d.tag.value_counts().reindex(order)
t1['mean words'] = d.groupby('tag').words.mean().reindex(order).round(0)
t1['mean Score1'] = d.groupby('tag').Score1.mean().reindex(order).round(2)
print(t1.to_string())

print('\n== 2. Score1 % by tag and length ==')
t2 = d.groupby(['tag', 'length'], observed=True).Score1.apply(pct).unstack()
t2.columns = list(range(4))
t2['n'] = d.groupby(['tag', 'length'], observed=True).size()
print(t2.reindex(order, level=0).to_string())

print('\n== 3. Dev responses tagged dangling or fragment (for checking the tagger) ==')
for r in d[(d.split == 'dev') & d.tag.isin(['dangling', 'fragment'])].sort_values(['tag', 'words']).itertuples():
    print(f'{r.Id} [{r.tag}] S1={r.Score1} S2={r.Score2} words={r.words}: ...{r.text[-90:]!r}')
