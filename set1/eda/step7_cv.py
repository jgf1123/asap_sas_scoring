"""Step 7: rule reliability by cross-validation on fixed model codes (pre-registered in set1/eda/prereg_cv.md).

Usage: python set1/eda/step7_cv.py RUN.jsonl [RUN.jsonl ...] [--subset remainder] [--exclude-seen] [--save PATH]
  RUN files: model v0.2 coding runs (e.g. set1/results/dev_v0.2.jsonl set1/results/remainder_v0.2.jsonl).
  --subset remainder  use only remainder responses (sensitivity analysis)
  --exclude-seen      drop the remainder responses already read (set1/eda/remainder_seen_ids.csv)
  --save PATH         write the configuration selected on all training responses to PATH (JSON)

Knobs (prereg §4): 15 per-code knobs with settings off / present / borderline (= present or borderline);
a pooled borderline knob (all credited codes: borderline vs present only); two counting knobs.
Folds: StratifiedKFold(5) on Score1, seeds 0-19. Responses flagged `unfinished` are excluded from every set
used for selection; held-out results are reported with and without them.
"responses changed by alternatives": how many training responses each non-best-guess setting would rescore;
0 means the data cannot distinguish the settings (a tie, resolved to the best guess).
"""
import argparse
import json
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

sys.stdout.reconfigure(encoding='utf-8')

GROUPS = {'VA': ['VA'], 'VT': ['VT'], 'MAT': ['MAT'], 'SIZE': ['SIZE'], 'RT': ['RT'], 'DRY': ['DRY'],
          'container': ['CS', 'CT'], 'surroundings': ['ENVT', 'ENVL', 'ENVP'], 'COVER': ['COVER'],
          'MATV': ['MATV'], 'AMT': ['AMT'], 'MATK': ['MATK'], 'MASS': ['MASS'], 'RINSE': ['RINSE'],
          'DESIGN': ['DESIGN']}
OFFICIAL = ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'container']
LEVEL = {'off': None, 'present': 2, 'borderline': 1}
KNOBS = {**{g: ['off', 'present', 'borderline'] for g in GROUPS},
         'pooled_borderline': ['per-code', 'present'],
         'surroundings_count': ['once', 'separate'], 'container_count': ['once', 'separate']}
BEST = {**{g: 'borderline' for g in ['VA', 'VT', 'MAT', 'SIZE', 'RT', 'DRY', 'container', 'surroundings', 'COVER']},
        **{g: 'off' for g in ['MATV', 'AMT', 'MATK', 'MASS', 'RINSE', 'DESIGN']},
        'pooled_borderline': 'per-code', 'surroundings_count': 'once', 'container_count': 'once'}
ORDER = list(KNOBS)  # search order = prereg §4 order


def scores(L, cfg):
    """Scores for all rows of L (dict code -> int array of levels 0/1/2) under configuration cfg."""
    n = np.zeros(len(next(iter(L.values()))), dtype=int)
    for g, codes in GROUPS.items():
        setting = cfg[g]
        if setting == 'off':
            continue
        if setting == 'borderline' and cfg['pooled_borderline'] == 'present':
            setting = 'present'
        hits = [L[c] >= LEVEL[setting] for c in codes]
        separate = (g == 'surroundings' and cfg['surroundings_count'] == 'separate') or \
                   (g == 'container' and cfg['container_count'] == 'separate')
        n += np.sum(hits, axis=0) if separate else np.any(hits, axis=0)
    return np.minimum(n, 3)


def qwk(a, b, k=4):
    """Quadratic weighted kappa (same as sklearn cohen_kappa_score(weights='quadratic')), vectorized."""
    o = np.zeros((k, k))
    np.add.at(o, (a, b), 1)
    w = (np.arange(k)[:, None] - np.arange(k)[None, :]) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    return 1 - (w * o).sum() / (w * e).sum()


def select(L, y, idx, cfg, knob):
    """Setting of `knob` with the highest QWK on rows idx (others as in cfg); ties go to cfg's setting."""
    best_s, best_q = cfg[knob], qwk(y[idx], scores(L, cfg)[idx])
    for s in KNOBS[knob]:
        if s != best_s:
            q = qwk(y[idx], scores(L, {**cfg, knob: s})[idx])
            if q > best_q:
                best_s, best_q = s, q
    return best_s


def search(L, y, idx):
    """Prereg §6: from the best guess, one knob at a time in ORDER, repeat passes until nothing changes."""
    cfg = dict(BEST)
    for _ in range(20):
        changed = False
        for knob in ORDER:
            s = select(L, y, idx, cfg, knob)
            if s != cfg[knob]:
                cfg[knob], changed = s, True
        if not changed:
            break
    return cfg


def load(paths):
    recs = [json.loads(l) for p in paths for l in open(p, encoding='utf-8')]
    m = pd.DataFrame([r for r in recs if 'error' not in r]).drop_duplicates('Id', keep='last').drop(columns='split')
    split = pd.concat([pd.read_csv(f'data/set1/{s}.csv', usecols=['Id', 'Score1']).assign(split=s)
                       for s in ('dev', 'remainder')])
    return m.merge(split, on='Id', validate='one_to_one')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--subset', choices=['remainder'])
    ap.add_argument('--exclude-seen', action='store_true')
    ap.add_argument('--save')
    args = ap.parse_args()

    m = load(args.runs)
    if args.subset:
        m = m[m.split == args.subset]
    if args.exclude_seen:
        m = m[~m.Id.isin(pd.read_csv('set1/eda/remainder_seen_ids.csv').Id)]
    m = m.reset_index(drop=True)
    L = {c: m[c].astype(int).to_numpy() for codes in GROUPS.values() for c in codes}
    y = m.Score1.to_numpy()
    unf = m['flags'].map(lambda f: 'unfinished' in f).to_numpy()
    print(f'n={len(m)} ({m.split.value_counts().to_dict()}) | unfinished {int(unf.sum())} (excluded from selection)')
    best_all = scores(L, BEST)
    print(f'best guess on all training responses: QWK {qwk(y, best_all):.3f} (all), {qwk(y[~unf], best_all[~unf]):.3f} (without unfinished)')

    splits = [(r, tr, te) for r in range(20)
              for tr, te in StratifiedKFold(5, shuffle=True, random_state=r).split(np.zeros(len(y)), y)]

    # Per-knob reliability (prereg §5)
    rows = []
    for knob in ORDER:
        sel, opt, gain_rep, gain_rep_nu = [], [], [], []
        for r in range(20):
            pred_sel, pred_best = np.empty(len(y), int), np.empty(len(y), int)
            for rr, tr, te in splits:
                if rr != r:
                    continue
                tr_sel = tr[~unf[tr]]
                s = select(L, y, tr_sel, BEST, knob)
                sel.append(s)
                ps, pb = scores(L, {**BEST, knob: s}), scores(L, BEST)
                pred_sel[te], pred_best[te] = ps[te], pb[te]
                opt.append((qwk(y[tr_sel], ps[tr_sel]) - qwk(y[tr_sel], pb[tr_sel]))
                           - (qwk(y[te], ps[te]) - qwk(y[te], pb[te])))
            gain_rep.append(qwk(y, pred_sel) - qwk(y, pred_best))
            gain_rep_nu.append(qwk(y[~unf], pred_sel[~unf]) - qwk(y[~unf], pred_best[~unf]))
        cnt = pd.Series(sel).value_counts()
        modal, top = cnt.index[0], int(cnt.iloc[0])
        g = np.array(gain_rep)
        if top < 80:
            label = 'unstable'
        elif modal == BEST[knob]:
            label = 'stable: supports best guess'
        elif (g > 0).sum() >= 16:
            label = 'stable: contradicts best guess'
        else:
            label = 'stable at another setting, gain not consistent'
        base = scores(L, BEST)
        changes = {s: int((scores(L, {**BEST, knob: s}) != base).sum()) for s in KNOBS[knob] if s != BEST[knob]}
        rows.append({'knob': knob, 'best guess': BEST[knob], 'selected (of 100)': {k: int(v) for k, v in cnt.items()},
                     'responses changed by alternatives': changes,
                     'oof gain mean': round(g.mean(), 4), 'oof gain range': f'[{g.min():+.4f}, {g.max():+.4f}]',
                     'gain>0 repeats': int((g > 0).sum()), 'oof gain w/o unfinished': round(np.mean(gain_rep_nu), 4),
                     'optimism': round(np.mean(opt), 4), 'label': label})
    t = pd.DataFrame(rows)
    with pd.option_context('display.width', 250, 'display.max_colwidth', 60):
        print('\n== Per-knob reliability (other knobs at best guess) ==')
        print(t.to_string(index=False))

    credited = {k: int(sum(t.loc[t.knob == k, 'selected (of 100)'].iloc[0].get(s, 0) for s in ('present', 'borderline')))
                for k in OFFICIAL}
    ok = all(v >= 80 for v in credited.values())
    print(f'\nPositive control (official codes credited in >= 80 of 100): {credited} -> {"PASS" if ok else "FAIL"}')

    # Nested CV of the search procedure (prereg §6)
    gain, gain_nu, chosen = [], [], []
    for r in range(20):
        pred, pred_best = np.empty(len(y), int), np.empty(len(y), int)
        for rr, tr, te in splits:
            if rr != r:
                continue
            cfg = search(L, y, tr[~unf[tr]])
            chosen.append(json.dumps({k: v for k, v in cfg.items() if v != BEST[k]}, sort_keys=True))
            pred[te], pred_best[te] = scores(L, cfg)[te], scores(L, BEST)[te]
        gain.append(qwk(y, pred) - qwk(y, pred_best))
        gain_nu.append(qwk(y[~unf], pred[~unf]) - qwk(y[~unf], pred_best[~unf]))
    g = np.array(gain)
    print(f'\n== Search procedure, nested CV: out-of-fold QWK minus best guess: mean {g.mean():+.4f},'
          f' range [{g.min():+.4f}, {g.max():+.4f}], > 0 in {int((g > 0).sum())}/20 repeats;'
          f' without unfinished mean {np.mean(gain_nu):+.4f}')
    print('changes from best guess chosen in the 100 outer training sets (count):')
    for k, v in pd.Series(chosen).value_counts().head(10).items():
        print(f'  {v:3d}  {k}')

    final = search(L, y, np.where(~unf)[0])
    diff = {k: v for k, v in final.items() if v != BEST[k]}
    print(f'\n== Configuration selected on all training responses: changes from best guess: {diff or "none"}')
    if args.save:
        json.dump(final, open(args.save, 'w'), indent=1)
        print(f'saved to {args.save}')


if __name__ == '__main__':
    main()
