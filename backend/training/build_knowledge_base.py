#!/usr/bin/env python3
"""Build consolidated knowledge_base.json from json_docs outputs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional


def detect_topic(text: str) -> str:
    """Heuristic topic detection using keyword triggers (mirrors extract_knowledge)."""
    text_lower = text.lower()
    patterns = {
        "head_and_shoulders": ["head and shoulders", "h&s pattern", "neckline"],
        "double_bottom": ["double bottom", "w pattern", "twin valleys"],
        "double_top": ["double top", "m pattern", "twin peaks"],
        "triangle": ["triangle", "ascending triangle", "descending triangle", "symmetrical"],
        "flag": ["flag pattern", "bull flag", "bear flag", "pennant"],
        "wedge": ["wedge", "rising wedge", "falling wedge"],
        "cup_and_handle": ["cup and handle", "cup with handle", "c&h"],
        "engulfing": ["engulfing", "bullish engulfing", "bearish engulfing"],
        "doji": ["doji", "dragonfly", "gravestone", "long-legged"],
        "hammer": ["hammer", "inverted hammer", "hanging man"],
        "shooting_star": ["shooting star", "evening star", "morning star"],
        "support_resistance": ["support", "resistance", "key level", "price level"],
        "trend": ["trend", "uptrend", "downtrend", "trend line"],
        "volume": ["volume", "volume analysis", "volume spike", "volume pattern"],
        "rsi": ["rsi", "relative strength", "overbought", "oversold"],
        "macd": ["macd", "signal line", "histogram", "convergence divergence"],
        "moving_average": ["moving average", "ma ", "sma", "ema", "golden cross", "death cross"],
        "bollinger": ["bollinger", "bands", "squeeze", "expansion"],
        "risk_management": ["risk", "stop loss", "position size", "risk reward"],
        "strategy": ["strategy", "trading plan", "entry", "exit", "setup"],
    }

    topic_scores = {}
    for topic, keywords in patterns.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            topic_scores[topic] = score

    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    return "general_ta"


def approximate_tokens(text: str) -> int:
    words = max(len(text.split()), 1)
    return int(math.ceil(words * 1.3))


def build_chunks(doc_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    doc_id = doc_json.get("doc_id", "unknown_doc")
    source = doc_json.get("source_file", doc_id)
    chunks: List[Dict[str, Any]] = []

    for chunk in doc_json.get("chunks", []):
        text = (chunk.get("text") or "").strip()
        if not text:
            continue
        chunk_id = chunk.get("chunk_id") or f"{doc_id}__{len(chunks)+1}"
        tokens = approximate_tokens(text)
        chunks.append(
            {
                "text": text,
                "doc_id": doc_id,
                "source": source,
                "chunk_id": chunk_id,
                "topic": detect_topic(text),
                "tokens": tokens,
            }
        )

    return chunks


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build knowledge_base.json from json_docs outputs")
    parser.add_argument("--root", default=str(Path(__file__).parent.parent), help="Project root (default: backend/)")
    parser.add_argument("--json-docs", default=None, help="Directory with per-doc JSON files")
    parser.add_argument("--output", default=None, help="Output knowledge base JSON path")
    args = parser.parse_args(argv)

    root = Path(args.root)
    docs_dir = Path(args.json_docs) if args.json_docs else root / "training" / "json_docs"
    output_path = Path(args.output) if args.output else root / "knowledge_base.json"

    if not docs_dir.exists():
        raise SystemExit(f"json_docs directory not found: {docs_dir}")

    doc_files = sorted(docs_dir.glob("*.json"))
    if not doc_files:
        print(f"No JSON documents found in {docs_dir}")
        return 0

    all_chunks: List[Dict[str, Any]] = []
    for doc_file in doc_files:
        data = json.loads(doc_file.read_text(encoding="utf-8"))
        chunks = build_chunks(data)
        all_chunks.extend(chunks)

    output_path.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(all_chunks)} chunks to {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
