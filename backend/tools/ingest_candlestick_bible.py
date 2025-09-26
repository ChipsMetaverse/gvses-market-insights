#!/usr/bin/env python3
"""
Ingest "The Candlestick Trading Bible" training JSON into knowledge_base.json.

Usage:
  python3 backend/tools/ingest_candlestick_bible.py \
      --source backend/training/json_docs/the_candlestick_trading_bible.json \
      --output backend/knowledge_base.json --append

Then embed with:
  python3 -m backend.services.knowledge_embedder
"""

import argparse
import json
from pathlib import Path


def infer_topic(text: str) -> str:
    tl = text.lower()
    topics = [
        'doji','gravestone doji','dragonfly doji','marubozu','spinning top',
        'hammer','hanging man','shooting star','inverted hammer',
        'bullish engulfing','bearish engulfing','harami','harami cross',
        'morning star','evening star',
        'three white soldiers','three black crows',
        'piercing line','dark cloud cover'
    ]
    for key in topics:
        if key in tl:
            return f"candlestick:{key}"
    return 'candlestick:general'


def load_chunks(source_file: Path):
    data = json.loads(source_file.read_text(encoding='utf-8'))
    chunks = data.get('chunks', [])
    out = []
    for ch in chunks:
        text = ch.get('text', '').strip()
        if not text:
            continue
        out.append({
            'id': ch.get('chunk_id', ''),
            'text': text,
            'source': 'The Candlestick Trading Bible',
            'source_file': source_file.name,
            'topic': infer_topic(text)
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='Path to the_candlestick_trading_bible.json')
    ap.add_argument('--output', required=True, help='Path to knowledge_base.json to write/append')
    ap.add_argument('--append', action='store_true', help='Append to existing file instead of overwrite')
    args = ap.parse_args()

    src = Path(args.source)
    out = Path(args.output)

    if not src.exists():
        raise SystemExit(f"Source file not found: {src}")

    new_chunks = load_chunks(src)
    print(f"Loaded {len(new_chunks)} chunks from {src}")

    existing = []
    if args.append and out.exists():
        try:
            existing = json.loads(out.read_text(encoding='utf-8'))
        except Exception:
            existing = []

    merged = existing + new_chunks
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(merged)} total chunks to {out}")
    print("Next: embed with backend/services/knowledge_embedder.py to update the vector index.")


if __name__ == '__main__':
    main()

