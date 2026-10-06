"""Non-LLM baselines: length-only and bag-of-words logistic regression.

Both are fit on all train responses of the set (dev + remainder; 1640 for Set 10). By default this
reports nested 5-fold cross-validation on train only. --test fits on all of train and evaluates on the
official test set; run it once, alongside the LLM's single test run (set10/eda/prereg_remainder.md).

Text variant for the final bag-of-words baseline: wraps repaired if its CV QWK >= raw (decided on train CV).

--dev fits on the remainder only and predicts the dev set (dev labels unseen), saving predictions to
set{N}/results/baselines_dev_predictions.csv for comparison with codebook scores on dev.

Usage (from the repo root):
  python common/baselines.py --set 10          # nested CV on train
  python common/baselines.py --set 10 --test   # final test evaluation
  python common/baselines.py --set 1 --dev     # fit on remainder, predict dev
"""
import argparse
import importlib
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

sys.path.insert(0, '.')
from common.evaluate import report
from common.text_clean import build_vocab, repair

conf = None  # set{N}.config, loaded in main()


def body_words(texts):
    """log(1 + number of words in the student's own text, without any menu prefix)."""
    bodies = pd.Series([conf.body(t) for t in texts])
    return np.log1p(bodies.str.split().str.len().to_numpy()).reshape(-1, 1)


def bow_model(vocab=None):
    """Unigram+bigram counts -> logistic regression, C by inner CV. With vocab, repair wrap-split words first."""
    steps = [FunctionTransformer(lambda xs: [repair(x, vocab) for x in xs])] if vocab is not None else []
    steps += [CountVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2), LogisticRegression(max_iter=5000)]
    return GridSearchCV(make_pipeline(*steps), {'logisticregression__C': [0.01, 0.03, 0.1, 0.3, 1, 3]},
                        scoring='accuracy', cv=StratifiedKFold(5, shuffle=True, random_state=1), n_jobs=1)


def models(vocab):
    m = {'length-only': make_pipeline(FunctionTransformer(body_words), LogisticRegression(max_iter=1000)),
         'bag-of-words (raw text)': bow_model()}
    if vocab is not None:
        m['bag-of-words (wraps repaired)'] = bow_model(vocab)
    return m


def main():
    global conf
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', type=int, required=True)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--test', action='store_true', help='fit on all train and evaluate on the test set (run once)')
    mode.add_argument('--dev', action='store_true', help='fit on the remainder only and predict the dev set')
    args = ap.parse_args()
    conf = importlib.import_module(f'set{args.set}.config')
    SET = args.set

    train = pd.concat([pd.read_csv(f'data/set{SET}/dev.csv'), pd.read_csv(f'data/set{SET}/remainder.csv')])
    X, y = train.text.to_numpy(), train.Score1.to_numpy()
    vocab = build_vocab(train.text) if conf.WRAP_REPAIR else None  # unsupervised: train text only, no labels
    rows = []
    if args.dev:
        rem, dev = pd.read_csv(f'data/set{SET}/remainder.csv'), pd.read_csv(f'data/set{SET}/dev.csv')
        if vocab is not None:
            vocab = build_vocab(rem.text)
        out = dev[['Id']].copy()
        for name, model in models(vocab).items():
            model.fit(rem.text.to_numpy(), rem.Score1.to_numpy())
            out[name] = model.predict(dev.text.to_numpy())
            rows.append(report(dev.Score1, out[name], f'{name} (fit remainder, dev)'))
        rows.append(report(dev.Score1, dev.Score2, 'Score2 (human reference, dev)'))
        out.to_csv(f'set{SET}/results/baselines_dev_predictions.csv', index=False)
    elif not args.test:
        outer = StratifiedKFold(5, shuffle=True, random_state=0)
        for name, model in models(vocab).items():
            pred = cross_val_predict(model, X, y, cv=outer, n_jobs=1)
            rows.append(report(y, pred, f'{name} (nested 5-fold CV, train)'))
        rows.append(report(y, train.Score2.to_numpy(), 'Score2 (human reference, train)'))
    else:
        test = pd.read_csv(f'data/set{SET}/test.csv')
        out = test[['Id']].copy()
        for name, model in models(vocab).items():
            model.fit(X, y)
            out[name] = model.predict(test.text.to_numpy())
            rows.append(report(test.Score1, out[name], f'{name} (test)'))
            if name.startswith('bag-of-words'):
                print(name, 'chosen C:', model.best_params_)
        out.to_csv(f'set{SET}/results/baselines_test_predictions.csv', index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
    main()
