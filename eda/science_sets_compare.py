"""Per-set label distribution and human-human agreement for the science sets."""
import pandas as pd
from sklearn.metrics import cohen_kappa_score

d = pd.read_csv('data/train.tsv', sep='\t')
rows = []
for s in (1, 2, 5, 6, 10):
    g = d[d.EssaySet == s]
    dist = g.Score1.value_counts(normalize=True).sort_index().mul(100).round(0).astype(int)
    rows.append({'set': s, 'n': len(g), 'range': f'0-{g.Score1.max()}',
                 'Score1 % by level': '/'.join(map(str, dist)),
                 'exact agree': round((g.Score1 == g.Score2).mean(), 3),
                 'human QWK': round(cohen_kappa_score(g.Score1, g.Score2, weights='quadratic'), 3),
                 'median words': int(g.EssayText.str.split().str.len().median())})
print(pd.DataFrame(rows).to_string(index=False))
