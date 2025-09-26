#!/usr/bin/env python3
"""
Ingest Encyclopedia of Chart Patterns into knowledge_base.json format.

Usage:
  python3 backend/tools/ingest_chart_encyclopedia.py \
      --source backend/training/json_docs/encyclopedia_of_chart_patterns.json \
      --output backend/knowledge_base.json --append

This converts each chunk in the training JSON into a knowledge chunk
with fields: text, source, source_file, topic (heuristically inferred).
After ingestion, run the embedder to update embeddings:
  python3 -m backend.services.knowledge_embedder
"""

import argparse
import json
from pathlib import Path
import re


def infer_topic(text: str) -> str:
    tl = text.lower()
    topics = [
        'head and shoulders','inverse head and shoulders',
        'double top','double bottom','triple top','triple bottom',
        'ascending triangle','descending triangle','symmetrical triangle',
        'flag','pennant','rising wedge','falling wedge','wedge',
        'rectangle','broadening','diamond','rounding bottom','cup and handle',
        'doji','gravestone doji','dragonfly doji','hammer','shooting star',
        'harami','engulfing','marubozu','piercing line','dark cloud cover',
    ]
    for key in topics:
        if key in tl:
            return f"pattern:{key}"
    return 'chart_patterns:encyclopedia'


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
            'source': 'Encyclopedia of Chart Patterns (Bulkowski)',
            'source_file': source_file.name,
            'topic': infer_topic(text)
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='Path to encyclopedia_of_chart_patterns.json')
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

