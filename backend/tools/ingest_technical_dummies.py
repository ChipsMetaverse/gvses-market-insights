#!/usr/bin/env python3
"""
Ingest "Technical Analysis for Dummies (2nd Edition)" training JSON into the knowledge base.

Usage:
  python3 backend/tools/ingest_technical_dummies.py \
      --source backend/training/json_docs/technical_analysis_for_dummies_2nd_edition.json \
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
        # Core concepts
        'trend', 'support', 'resistance', 'breakout', 'pullback', 'volume', 'volatility',
        # Indicators
        'moving average', 'sma', 'ema', 'wma',
        'rsi', 'macd', 'bollinger', 'stochastic', 'adx', 'atr', 'cci',
        'vwap', 'ichimoku', 'parabolic sar',
        # Chart patterns
        'triangle', 'flag', 'pennant', 'wedge', 'head and shoulders', 'double top', 'double bottom',
        # Risk/position
        'risk', 'stop loss', 'position sizing', 'risk management',
    ]
    for key in topics:
        if key in tl:
            # Normalize topic label
            lbl = key.replace(' ', '_')
            return f"ta_dummies:{lbl}"
    return 'ta_dummies:general'


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
            'source': 'Technical Analysis for Dummies (2nd ed.)',
            'source_file': source_file.name,
            'topic': infer_topic(text)
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='Path to technical_analysis_for_dummies_2nd_edition.json')
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

