"""Repair line-wrap artifacts in ASAP-SAS response text.

Digitizing handwritten lines inserted a space at each line wrap, often splitting a word ("dogho use").
Wraps fall near fixed offsets in the student's text (after the "color ::" prefix): 45, then about
every 73 characters, wobbling by a character or two (eda/space_artifact.py, eda/wrap_artifact_check.py).

Repair rule: at a space within TOL characters of an expected wrap offset, with letters on both sides,
join the two fragments if the joined word is in the corpus vocabulary and either a fragment is not, or the
joined word is at least as frequent as the rarer fragment ("be|cause" -> "because"; "of|the" stays).
The vocabulary is built only from tokens away from wrap zones, so it is not polluted by fragments;
single letters other than "a" and "i" are excluded from it.
"""
import re
from collections import Counter

FIRST, PERIOD, TOL, MIN_COUNT = 45, 73, 3, 2
WORD = re.compile(r'[A-Za-z]+')


def split_prefix(text):
    color, _, body = text.partition('::')
    lead = len(body) - len(body.lstrip())
    return color + '::' + body[:lead], body[lead:]


def in_zone(i):
    if i < FIRST - TOL:
        return False
    k = round((i - FIRST) / PERIOD)
    return abs(i - (FIRST + PERIOD * k)) <= TOL


def build_vocab(texts):
    counts = Counter()
    for t in texts:
        body = split_prefix(t)[1]
        for m in WORD.finditer(body):
            if not any(in_zone(i) for i in range(m.start() - 1, m.end() + 1)):
                counts[m.group().lower()] += 1
    return {w: c for w, c in counts.items() if c >= MIN_COUNT and (len(w) > 1 or w in ('a', 'i'))}


def repair(text, vocab, log=None):
    """Return text with wrap-split words rejoined. If log is a list, append (left, right) for each join."""
    prefix, body = split_prefix(text)
    drop = []
    for i, ch in enumerate(body):
        if ch != ' ' or not in_zone(i) or i == 0 or i + 1 >= len(body):
            continue
        if not (body[i - 1].isalpha() and body[i + 1].isalpha()):
            continue
        left = re.search(r'[A-Za-z]+$', body[:i]).group()
        right = re.match(r'[A-Za-z]+', body[i + 1:]).group()
        joined = (left + right).lower()
        lw, rw = left.lower(), right.lower()
        if joined in vocab and (lw not in vocab or rw not in vocab or vocab[joined] >= min(vocab[lw], vocab[rw])):
            drop.append(i)
            if log is not None:
                log.append((left, right))
    for i in reversed(drop):
        body = body[:i] + body[i + 1:]
    return prefix + body
