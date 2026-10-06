"""Set 1 ("Acid Rain") configuration. Interface: see set10/config.py.

Work in progress: only what common/baselines.py needs is defined so far. The prompt, schema and
codes_score() will be added once the codebook is drafted.
"""
WRAP_REPAIR = False  # no line-wrap artifact in Set 1 (set1/eda/step0b_wrap_artifact.py)


def body(text: str) -> str:
    """Student's text; "^p" paragraph marks become line breaks (no menu prefix in Set 1)."""
    return text.replace('^p', '\n')
