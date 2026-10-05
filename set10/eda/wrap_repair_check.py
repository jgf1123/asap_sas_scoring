"""Check text_clean.repair on train text: join counts, random sample of joins, and declined in-zone splits."""
import random
import re
import sys

import pandas as pd

sys.path.insert(0, '.')
from common.text_clean import build_vocab, in_zone, repair, split_prefix

texts = pd.concat([pd.read_csv('data/set10/dev.csv'), pd.read_csv('data/set10/remainder.csv')]).text.tolist()
vocab = build_vocab(texts)
joins, declined, touched = [], [], 0
for t in texts:
    log = []
    repair(t, vocab, log)
    joins += log
    touched += bool(log)
    body = split_prefix(t)[1]
    for i, ch in enumerate(body):
        if ch == ' ' and in_zone(i) and 0 < i < len(body) - 1 and body[i - 1].isalpha() and body[i + 1].isalpha():
            left = re.search(r'[A-Za-z]+$', body[:i]).group()
            right = re.match(r'[A-Za-z]+', body[i + 1:]).group()
            if (left, right) not in log:
                declined.append((left, right))
print(f'vocab {len(vocab)} words | joins {len(joins)} in {touched}/{len(texts)} responses | in-zone letter-letter spaces declined {len(declined)}')
random.seed(0)
print('\nRandom 20 joins:', ', '.join(f'{a}|{b}' for a, b in random.sample(joins, 20)))
print('\nRandom 30 declined:', ', '.join(f'{a}|{b}' for a, b in random.sample(declined, 30)))
