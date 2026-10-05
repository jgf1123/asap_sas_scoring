"""Score1 vs Score2 confusion matrix (counts and row %) for the given sets."""
import sys
import pandas as pd

d = pd.read_csv('data/train.tsv', sep='\t')
for s in map(int, sys.argv[1:]):
    g = d[d.EssaySet == s]
    ct = pd.crosstab(g.Score1, g.Score2, margins=True, margins_name='total')
    pct = (pd.crosstab(g.Score1, g.Score2, normalize='index') * 100).round(0).astype(int)
    gap = (g.Score1 - g.Score2).abs().value_counts().sort_index()
    print(f'===== SET {s} (n={len(g)}) =====')
    print('Counts (rows = Score1, cols = Score2):')
    print(ct)
    print('Row %:')
    print(pct)
    print('|Score1 - Score2| counts:', gap.to_dict(), '\n')
