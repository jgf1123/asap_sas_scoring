"""Step 0: Set 1 data format only (no score distributions, no agreement, no content reading).

1. Set 1 rows and columns in each Kaggle file
2. Release consistency: train vs train_rel_2, public_leaderboard vs rel_2, public texts vs labels
3. Shape of the text field: menu prefix, empty, whitespace, line breaks, non-ASCII, HTML entities, (TOKENS)
4. Three raw examples (repr, scores hidden)
"""
import re
import sys

import pandas as pd

SET = 1
sys.stdout.reconfigure(encoding='utf-8')

print('== 1. Files ==')
files = {'train.tsv': '\t', 'train_rel_2.tsv': '\t', 'public_leaderboard.tsv': '\t',
         'public_leaderboard_rel_2.tsv': '\t', 'public_leaderboard_solution.csv': ',',
         'private_leaderboard.tsv': '\t', 'test.csv': ','}
for f, sep in files.items():
    x = pd.read_csv(f'data/{f}', sep=sep)
    col = next((c for c in ('EssaySet', 'essay_set') if c in x), None)
    n = (x[col] == SET).sum() if col else '-'
    print(f'{f:32s} set{SET}={n!s:5s} cols={list(x.columns)}')

print('\n== 2. Release consistency ==')
a = pd.read_csv('data/train.tsv', sep='\t').query('EssaySet == @SET').set_index('Id')
b = pd.read_csv('data/train_rel_2.tsv', sep='\t').query('EssaySet == @SET').set_index('Id')
print(f'train vs train_rel_2: rows {len(a)} vs {len(b)} | same ids {a.index.equals(b.index)}')
common = a.index.intersection(b.index)
print(f'  on common ids: text differs {(a.EssayText[common] != b.EssayText[common]).sum()}, '
      f'Score1 differs {(a.Score1[common] != b.Score1[common]).sum()}, Score2 differs {(a.Score2[common] != b.Score2[common]).sum()}')
p1 = pd.read_csv('data/public_leaderboard.tsv', sep='\t').query('EssaySet == @SET').set_index('Id')
p2 = pd.read_csv('data/public_leaderboard_rel_2.tsv', sep='\t').query('EssaySet == @SET').set_index('Id')
print(f'public_leaderboard vs rel_2: rows {len(p1)} vs {len(p2)} | same ids {p1.index.equals(p2.index)}')
common = p1.index.intersection(p2.index)
diff = common[p1.EssayText[common] != p2.EssayText[common]]
print(f'  text differs on {len(diff)} common ids')
for i in diff[:3]:
    old, new = p1.EssayText[i], p2.EssayText[i]
    k = next((j for j in range(min(len(old), len(new))) if old[j] != new[j]), min(len(old), len(new)))
    print(f'  {i}: first difference at char {k}: {old[max(0, k - 20):k + 20]!r} -> {new[max(0, k - 20):k + 20]!r}')
sol = pd.read_csv('data/public_leaderboard_solution.csv').query('essay_set == @SET')
print(f'public labels: {len(sol)} | every rel_2 text has a label: {set(p2.index) == set(sol.id)} | Usage {sol.Usage.value_counts().to_dict()}')

print('\n== 3. Text field (train_rel_2 Set 1 train + public rel_2 test) ==')
for name, t in (('train', b.EssayText), ('test', p2.EssayText)):
    t = t.fillna('')
    print(f'-- {name} (n={len(t)})')
    print(f'  missing (NaN): {int(b.EssayText.isna().sum()) if name == "train" else int(p2.EssayText.isna().sum())}'
          f' | empty/whitespace-only: {int((t.str.strip() == "").sum())}')
    print(f'  contains "::": {int(t.str.contains("::", regex=False).sum())}'
          f' | leading space: {int(t.str.match(r"^\s").sum())} | trailing space: {int(t.str.contains(r"\s$").sum())}')
    print(f'  line breaks (\\n or \\r): {int(t.str.contains(r"[\r\n]").sum())} | tabs: {int(t.str.contains(chr(9)).sum())}'
          f' | double spaces: {int(t.str.contains("  ", regex=False).sum())}')
    nonascii = pd.Series([c for s in t for c in s if ord(c) > 127]).value_counts()
    print(f'  responses with non-ASCII: {int(t.map(lambda s: any(ord(c) > 127 for c in s)).sum())}'
          f' | chars: {dict((f"U+{ord(c):04X} {c}", n) for c, n in nonascii.head(8).items())}')
    ent = pd.Series(re.findall(r'&\w+;|&#\d+;', ' '.join(t))).value_counts()
    print(f'  HTML entities: {ent.head(8).to_dict()}')
    tok = pd.Series(re.findall(r'\([A-Z]{2,}\)|\[[^\]]{1,15}\]', ' '.join(t))).value_counts()
    print(f'  (UPPERCASE)/[bracket] tokens: {tok.head(10).to_dict()}')
    words = t.str.split().str.len()
    print(f'  words: median {words.median():.0f}, mean {words.mean():.0f}, min {words.min()}, max {words.max()}'
          f' | chars: median {t.str.len().median():.0f}, max {t.str.len().max()}')

print('\n== 4. Raw examples (train_rel_2, random seed 0, scores hidden) ==')
for i, s in b.EssayText.sample(3, random_state=0).items():
    print(f'{i}: {s!r}\n')

print('== 5. Markup and spacing (added after seeing "^p" in example 819) ==')
for name, t in (('train', b.EssayText), ('test', p2.EssayText)):
    carets = pd.Series(re.findall(r'\^\S{0,3}', ' '.join(t))).value_counts()
    print(f'-- {name}: responses with "^": {int(t.str.contains("^", regex=False).sum())} | caret tokens: {carets.head(8).to_dict()}')
    # where is "^p": position as a fraction of the response, and the text around it
    pos = [m.start() / len(s) for s in t for m in re.finditer(r'\^p', s)]
    if pos:
        print(f'  "^p" relative position: start(<10%) {sum(p < .1 for p in pos)}, middle {sum(.1 <= p <= .9 for p in pos)}, end(>90%) {sum(p > .9 for p in pos)}')
    runs = pd.Series([len(m.group()) for s in t for m in re.finditer(r' {2,}', s)]).value_counts().sort_index()
    print(f'  runs of 2+ spaces by length: {runs.to_dict()}')
    offs = pd.Series([m.start() for s in t for m in re.finditer(r' {2,}', s)])
    print(f'  char offset of 2+ space runs, deciles: {offs.quantile([.1, .3, .5, .7, .9]).round().astype(int).tolist()}')
