"""Exploratory rule-level analysis of the code->score rules (OT-style: rules are ranked; first applicable rule decides).

Run on LLM codes from a frozen run (default: remainder; also test). No API calls; nothing here changes
reported results. Three analyses:
  1. QWK lost to each rule's decisions (oracle fix of the responses that rule decided)
  2. Tier ablations: O -> O+C -> O+C+B -> +S, and leave-one-out / add-one
  3. Re-ranking: all orderings of the ranked rules; adjacent swaps of the current ranking

Usage: python set10/eda/rule_analysis.py remainder|test
"""
import itertools
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, '.')
from common.evaluate import load_run, paired_qwk_diff_ci, qwk
from set10.score_from_codes import score

SPLIT = sys.argv[1] if len(sys.argv) > 1 else 'remainder'
RUN = {'remainder': 'set10/results/remainder_v1.2.jsonl', 'test': 'set10/results/test_v1.2.jsonl'}[SPLIT]

m = load_run(RUN).merge(pd.read_csv(f'data/set10/{SPLIT}.csv'), on='Id')
m['group'] = m.text.str.split('::').str[0].str.contains('gray').map({True: 'gray', False: 'white/black'})
y = m.Score1.to_numpy()
c = {k: m[k].astype(bool).to_numpy() for k in ['E', 'J', 'D', 'N', 'P', 'L', 'U']}
f = {k: m['flags'].str.split(';').apply(lambda s: k in s).to_numpy() for k in ['hyp', 'vague', 'consistency', 'mismatch', 'physics']}
gray = (m.group == 'gray').to_numpy()

# Default variant settings = v1.2 with all-b boundary outcomes (the pre-registered selection).
DEFAULT = dict(B3='b', B4='b', B1='b', B2='b', B5='b', B6='b', C2=True, C3=True, O4b=True,
               present={'B5', 'FULL', 'C1', 'B1', 'B2', 'O2', 'B6'})
ORDER = ['B5', 'FULL', 'C1', 'B1', 'B2', 'S1', 'O2', 'B6']   # v1.2 ranking; O3 (-> 0) is always last
TIER = {'FULL': 'O', 'O2': 'O', 'C1': 'C', 'B1': 'B', 'B2': 'B', 'B5': 'B', 'B6': 'B', 'S1': 'S'}


def rules(v):
    """Condition and outcome arrays for each ranked rule under variant settings v."""
    n = c['N'] & ~(f['hyp'] & (v['B3'] == 'a')) & ~(f['vague'] & (v['B4'] == 'a'))
    p = c['P'] & n
    effect = c['E'] | (c['J'] & v['C3'])
    full = np.where(gray, (p if v['O4b'] else n) & effect, n & (c['E'] | (c['D'] & v['C2'])))
    ones, zeros = np.ones(len(y), int), np.zeros(len(y), int)
    return {
        'B5': (f['mismatch'] & full, ones if v['B5'] == 'b' else 2 * ones),
        'FULL': (full, 2 * ones),
        'C1': (c['U'], zeros),
        'B1': (f['consistency'] & ~p, effect.astype(int) if v['B1'] == 'b' else zeros),
        'B2': (c['L'] & n & ~p, effect.astype(int) if v['B2'] == 'b' else zeros),
        'S1': ((c['E'] | c['J']) & ~c['D'] & ~n & ~f['physics'], zeros),   # approx: bare effect, no reason
        'O2': (effect | n, ones),
        'B6': (f['physics'] | c['D'], ones if v['B6'] == 'b' else zeros),
    }


def predict(v, order=ORDER):
    """First applicable present rule decides; O3 (0) if none. Returns scores and the deciding rule."""
    rs = rules(v)
    pred, who = np.zeros(len(y), int), np.full(len(y), 'O3', dtype=object)
    open_ = np.ones(len(y), bool)
    for name in order:
        if name not in v['present']:
            continue
        cond, out = rs[name]
        hit = open_ & cond
        pred[hit], who[hit] = out[hit], name
        open_ &= ~hit
    return pred, who


def with_(**kw):
    v = {**DEFAULT, 'present': set(DEFAULT['present'])}
    for k, val in kw.items():
        v[k] = val
    return v


# --- Check: the ranked-list scorer reproduces score_from_codes.py for both pre-registered configs ---
recs = m.to_dict('records')
for cfg in ('aaaaaa', 'bbbbbb'):
    ref = np.array([score(r, dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], cfg))) for r in recs])
    v = with_(**dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], cfg)))
    assert (predict(v)[0] == ref).all(), f'ranked scorer differs from score_from_codes for {cfg}'
print(f'[{SPLIT}, n={len(y)}] ranked-list scorer reproduces score_from_codes.py for aaaaaa and bbbbbb')

base_pred, base_who = predict(DEFAULT)
base = qwk(y, base_pred)
print(f'Selected config (v1.2, all-b): QWK {base:.3f}\n')

# --- 1. QWK lost to each rule's decisions ---
print('1. QWK lost to each rule (oracle: give the responses this rule decided their human score)')
rows = []
for name in ORDER + ['O3']:
    hit = base_who == name
    if not hit.any():
        continue
    fixed = np.where(hit, y, base_pred)
    rows.append({'rule': name, 'tier': TIER.get(name, 'O'), 'decided': int(hit.sum()),
                 'wrong': int((base_pred[hit] != y[hit]).sum()),
                 'error rate': round(float((base_pred[hit] != y[hit]).mean()), 3),
                 'QWK lost': round(qwk(y, fixed) - base, 3)})
print(pd.DataFrame(rows).sort_values('QWK lost', ascending=False).to_string(index=False))

# --- 2. Tier ablations ---
print('\n2. Tiers (cumulative), then leave-one-out / add-one from the selected config')
O_ONLY = with_(C2=False, C3=False, B3='b', B4='b', B5='a', present={'FULL', 'O2'})
O_C = with_(C2=True, C3=True, B3='b', B4='b', B5='a', present={'FULL', 'O2', 'C1'})
variants = {
    'O only (official text literal)': O_ONLY,
    'O + C': O_C,
    'O + C + B (all-a)': with_(**dict(zip(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], 'aaaaaa'))),
    'O + C + B (all-b) = selected': DEFAULT,
    'O + C + B (all-b) + S1': with_(present=DEFAULT['present'] | {'S1'}),
    '  - C1 (U ignored)': with_(present=DEFAULT['present'] - {'C1'}),
    '  - C2 (white/black need explicit E)': with_(C2=False),
    '  - C3 (gray J not an effect)': with_(C3=False),
    '  - O4b placement (gray needs N, not P)': with_(O4b=False),
    '  - B1': with_(present=DEFAULT['present'] - {'B1'}),
    '  - B2': with_(present=DEFAULT['present'] - {'B2'}),
    '  B3 a (hyp -> N=0)': with_(B3='a'),
    '  B4 a (vague -> N=0)': with_(B4='a'),
    '  - B5': with_(present=DEFAULT['present'] - {'B5'}),
    '  - B6': with_(present=DEFAULT['present'] - {'B6'}),
}
rows = []
for label, v in variants.items():
    pred = predict(v)[0]
    d, lo, hi = paired_qwk_diff_ci(y, pred, base_pred, n_boot=1000)
    rows.append({'variant': label, 'QWK': round(qwk(y, pred), 3), 'vs selected': f'{d:+.3f} [{lo:+.3f}, {hi:+.3f}]',
                 'changed': int((pred != base_pred).sum())})
print(pd.DataFrame(rows).to_string(index=False))

# --- 3. Re-ranking ---
print('\n3. Re-ranking the 7 rules of the selected config (S1 excluded; O3 last)')
ranked = [r for r in ORDER if r != 'S1']
results = []
for perm in itertools.permutations(ranked):
    results.append((perm, qwk(y, predict(DEFAULT, perm)[0])))
q = np.array([r[1] for r in results])
print(f'{len(results)} rankings: QWK min {q.min():.3f}, median {np.median(q):.3f}, max {q.max():.3f}; '
      f'current {base:.3f} (rank {int((q > base).sum()) + 1} of {len(q)}); '
      f'distinct outcomes {len(set(np.round(q, 6)))}')
best = max(results, key=lambda r: r[1])
print('best ranking :', ' >> '.join(best[0]), f'({best[1]:.3f})')
worst = min(results, key=lambda r: r[1])
print('worst ranking:', ' >> '.join(worst[0]), f'({worst[1]:.3f})')

print('\nPairwise ranking arguments: mean QWK over all rankings with X >> Y minus Y >> X')
pos = {perm: {r: i for i, r in enumerate(perm)} for perm, _ in results}
rows = []
for a, b in itertools.combinations(ranked, 2):
    ab = np.array([pos[perm][a] < pos[perm][b] for perm, _ in results])
    rows.append({'X >> Y': f'{a} >> {b}', 'mean diff': round(q[ab].mean() - q[~ab].mean(), 4)})
pw = pd.DataFrame(rows)
print(pw[pw['mean diff'].abs() >= 0.001].sort_values('mean diff', key=abs, ascending=False).to_string(index=False))
print(f'({(pw["mean diff"].abs() < 0.001).sum()} of {len(pw)} pairs: |diff| < 0.001, ranking irrelevant)')

print('\nAdjacent swaps of the current ranking (single re-rankings), paired 95% CI')
for i in range(len(ranked) - 1):
    perm = ranked[:i] + [ranked[i + 1], ranked[i]] + ranked[i + 2:]
    pred = predict(DEFAULT, perm)[0]
    changed = int((pred != base_pred).sum())
    if changed:
        d, lo, hi = paired_qwk_diff_ci(y, pred, base_pred, n_boot=1000)
        print(f'  {ranked[i + 1]} >> {ranked[i]}: {d:+.3f} [{lo:+.3f}, {hi:+.3f}], {changed} responses change')
    else:
        print(f'  {ranked[i + 1]} >> {ranked[i]}: no responses change')
