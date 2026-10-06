"""Step 0b: is there a line-wrap artifact in Set 1, like Set 10's? (all train text, no labels)

Set 10's artifact: digitizing inserted a space at each handwritten line wrap, splitting words
("dogho use") at near-fixed character offsets (45, then about every 73). Two tests, each run on Set 10 too
as a positive control:
  (a) offset test: share of responses with a space at each character offset; Set 10 shows peaks
  (b) split-word test: spaces between letters where the joined word is a known word and a fragment is not
      ("be cause" -> "because"), counted per 100 responses and located by offset. Offset-free, so it would
      also catch wraps that do not fall at fixed offsets. Offsets restart after a "^p" paragraph mark.
"""
import re
import sys
from collections import Counter

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
train = pd.read_csv('data/train.tsv', sep='\t')
WORD = re.compile(r'[A-Za-z]+')


def bodies(s):
    t = train.query('EssaySet == @s').EssayText
    return t.str.split('::', n=1).str[1].str.lstrip() if s == 10 else t


def offset_peaks(body, L=400):
    rate = pd.Series([body[body.str.len() > i].str[i].eq(' ').mean() for i in range(L)])
    return rate.mean(), rate.nlargest(6).round(2).sort_index().to_dict()


def split_words(body):
    vocab = Counter(w.lower() for t in body for w in WORD.findall(t))
    found = []
    for t in body:
        line_start = 0
        for m in re.finditer(r'(?<=[A-Za-z]) (?=[A-Za-z])', t):
            i = m.start()
            p = t.rfind('^p', 0, i)
            line_start = p + 3 if p >= 0 else 0
            left = re.search(r'[A-Za-z]+$', t[:i]).group().lower()
            right = re.match(r'[A-Za-z]+', t[i + 1:]).group().lower()
            joined = left + right
            # joined is a reasonably common word, and at least one fragment is rare (< 2 uses) on its own
            if vocab[joined] >= 3 and min(vocab[left], vocab[right]) < 2:
                found.append((i - line_start, left, right))
    return found


for s in (10, 1):
    body = bodies(s)
    mean, peaks = offset_peaks(body)
    sw = split_words(body)
    print(f'===== Set {s} (n={len(body)}) =====')
    print(f'(a) mean space rate {mean:.3f} | top offsets: {peaks}')
    print(f'(b) split-word candidates: {len(sw)} ({100 * len(sw) / len(body):.1f} per 100 responses)')
    if sw:
        offs = pd.Series([o for o, _, _ in sw])
        print(f'    offset deciles: {offs.quantile([.1, .3, .5, .7, .9]).round().astype(int).tolist()}')
        print(f'    all/first 25: {", ".join(f"{a}|{b}@{o}" for o, a, b in sw[:25])}')
