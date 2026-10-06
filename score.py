"""Score ASAP-SAS responses with Claude, using a set's prompt and schema from set{N}/config.py.

Responses are scored one at a time (single process, sequential) and appended to
set{N}/results/<run>.jsonl, so an interrupted run resumes where it stopped.
Set-specific options (e.g. Set 10's --cfg, --s-tier) are added by the set's config.

Usage (from the repo root):
  python score.py --set 10 --split dev --n 20 --run pilot1
  python score.py --set 10 --split dev --run v1 --model claude-opus-5-5 --effort medium --cfg aaaaaa
"""
import argparse
import hashlib
import importlib
import json
import sys
import time
from pathlib import Path

import anthropic
import pandas as pd

def main():
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument('--set', type=int, required=True)
    conf = importlib.import_module(f'set{pre.parse_known_args()[0].set}.config')

    ap = argparse.ArgumentParser(parents=[pre])
    ap.add_argument('--split', choices=['dev', 'remainder', 'test'], required=True)
    ap.add_argument('--n', type=int, help='score only the first N responses (pilot)')
    ap.add_argument('--run', required=True, help='run name; output goes to set{N}/results/<run>.jsonl')
    ap.add_argument('--model', default='claude-opus-5-5')
    ap.add_argument('--effort', default='medium', choices=['low', 'medium', 'high', 'xhigh', 'max'])
    ap.add_argument('--show-prompt', action='store_true', help='print the system prompt and exit')
    ap.add_argument('--expect-hash', help='refuse to run unless the assembled prompt has this hash')
    conf.add_args(ap)
    args = ap.parse_args()

    system_text, cfg = conf.system_prompt(args)
    if args.show_prompt:
        sys.stdout.reconfigure(encoding='utf-8')  # the codebook has non-cp1252 characters (→)
        print(system_text)
        return
    prompt_hash = hashlib.sha256(system_text.encode()).hexdigest()[:12]
    if args.expect_hash and args.expect_hash != prompt_hash:
        raise SystemExit(f'Prompt hash {prompt_hash} != expected {args.expect_hash}. Did the rubric change?')

    data = pd.read_csv(f'data/set{args.set}/{args.split}.csv')
    if args.n:
        data = data.head(args.n)
    out = Path(f'set{args.set}/results/{args.run}.jsonl')
    out.parent.mkdir(exist_ok=True)
    prior = [json.loads(line) for line in out.open(encoding='utf-8')] if out.exists() else []
    old = {(r['prompt_hash'], r['model'], r['effort'], r['cfg']) for r in prior}
    if old - {(prompt_hash, args.model, args.effort, cfg)}:
        raise SystemExit(f'Refusing to resume {out}: it was scored with {old}, but this run would use '
                         f'{(prompt_hash, args.model, args.effort, cfg)}. Did the rubric change?')
    out.with_suffix('.prompt.txt').write_text(system_text, encoding='utf-8')
    done = {r['Id'] for r in prior if 'error' not in r}
    todo = data[~data.Id.isin(done)]
    print(f'{args.run}: {len(todo)} to score ({len(done)} already done) | model={args.model} '
          f'effort={args.effort} cfg={cfg} prompt={prompt_hash}')

    prepare = getattr(conf, 'prepare', lambda t: t)  # optional per-set text preparation (Set 1: ^p -> line break)
    client = anthropic.Anthropic(max_retries=5)
    for i, row in enumerate(todo.itertuples(), 1):
        t0 = time.time()
        rec = {'Id': row.Id, 'split': args.split, 'model': args.model, 'effort': args.effort,
               'cfg': cfg, 'prompt_hash': prompt_hash}
        try:
            resp = client.messages.create(
                model=args.model,
                max_tokens=16000,
                system=[{'type': 'text', 'text': system_text, 'cache_control': {'type': 'ephemeral'}}],
                messages=[{'role': 'user', 'content': f'<response>\n{prepare(row.text)}\n</response>'}],
                output_config={'effort': args.effort, 'format': {'type': 'json_schema', 'schema': conf.SCHEMA}},
            )
            rec['stop_reason'] = resp.stop_reason
            rec['usage'] = {k: getattr(resp.usage, k, None) for k in
                            ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')}
            if resp.stop_reason == 'end_turn':
                rec.update(json.loads(next(b.text for b in resp.content if b.type == 'text')))
            else:
                rec['error'] = f'stop_reason={resp.stop_reason}'
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as e:
            raise SystemExit(f'Authentication/permission error (check ANTHROPIC_API_KEY): {e.message}')
        except anthropic.BadRequestError as e:
            raise SystemExit(f'Bad request (fix before continuing): {e}')
        except anthropic.APIStatusError as e:
            rec['error'] = f'API {e.status_code}: {e.message}'
        except anthropic.APIConnectionError as e:
            rec['error'] = f'connection: {e}'
        rec['seconds'] = round(time.time() - t0, 1)
        with out.open('a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        status = rec['error'] if 'error' in rec else (f'score={rec["score"]}' if 'score' in rec else 'coded')
        print(f'  [{i}/{len(todo)}] {row.Id}: {status}')


if __name__ == '__main__':
    main()
