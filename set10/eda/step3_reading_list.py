"""Step 3: prior model (log words + color) on dev with 5-fold CV; build a surprise-ranked reading list.

Writes set10/eda/step3_reading_list.md. Dev only.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

SET = 10
dev = pd.read_csv(f'data/set{SET}/dev.csv')
parts = dev.text.str.split('::', n=1, expand=True)
dev['color'] = parts[0].str.strip().str.lower().replace('', '(blank)')
dev['body'] = parts[1].fillna('').str.strip()
dev['words'] = dev.body.str.split().str.len()

X = pd.get_dummies(dev.color, dtype=float).assign(log_words=np.log1p(dev.words))
cv = StratifiedKFold(5, shuffle=True, random_state=0)
P = cross_val_predict(LogisticRegression(max_iter=1000), X, dev.Score1, cv=cv, method='predict_proba')
dev[['p0', 'p1', 'p2']] = P
dev['surprise'] = -np.log(P[np.arange(len(dev)), dev.Score1])
argmax, expected = P.argmax(1), np.rint(P @ [0, 1, 2]).astype(int)
print('Prior model, 5-fold CV on dev:')
print(f'  QWK (most likely score):     {cohen_kappa_score(dev.Score1, argmax, weights="quadratic"):.3f}')
print(f'  QWK (rounded expected score): {cohen_kappa_score(dev.Score1, expected, weights="quadratic"):.3f}')
print('  Confusion (rows Score1, cols rounded expected):'); print(pd.crosstab(dev.Score1, expected))

def block(df, title):
    lines = [f'\n## {title} ({len(df)})\n', '| Id | S1 | S2 | words | P(0/1/2) | response |', '|---|---|---|---|---|---|']
    for r in df.itertuples():
        body = r.body.replace('|', '/').replace('\n', ' ')
        lines.append(f'| {r.Id} | {r.Score1} | {r.Score2} | {r.words} | {r.p0:.2f}/{r.p1:.2f}/{r.p2:.2f} | **{r.color}** :: {body} |')
    return lines

split = dev[dev.Score1 != dev.Score2].sort_values(['Score1', 'Score2'])
agree = dev[dev.Score1 == dev.Score2]
out = ['# Step 3 reading list: Set 10 dev', '',
       'P(0/1/2) = cross-validated prior from log(words) + color. Surprise = how unlikely S1 is under that prior.']
out += block(split, 'Raters split (Score1 != Score2)')
for s in (0, 1, 2):
    g = agree[agree.Score1 == s]
    out += block(g.nlargest(5, 'surprise'), f'Agreed score {s}: most surprising given priors')
    out += block(g.nsmallest(3, 'surprise'), f'Agreed score {s}: typical given priors')
open('set10/eda/step3_reading_list.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'\nRaters split: {len(split)} | reading list written: set10/eda/step3_reading_list.md')
