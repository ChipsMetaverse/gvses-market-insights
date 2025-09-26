#!/usr/bin/env python3
"""Convert processed knowledge documents into JSON payloads.

Each processed text file under ``processed/`` is transformed into a JSON file
under ``json_docs/`` that contains lightly-structured paragraphs. This makes it
easy to ingest the raw knowledge into vector stores or other pipelines that
expect JSON input.

Example usage::

    python convert_docs.py --root backend/training --max-paragraph 1200

Options allow overriding the processed/input directories and adjusting how
paragraphs are chunked.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class Paths:
    root: Path
    processed_dir: Path
    output_dir: Path


def iter_paragraphs(text: str) -> Iterable[str]:
    """Yield cleaned paragraphs from processed text."""
    for block in text.split("\n\n"):
        cleaned = block.strip()
        if cleaned:
            yield cleaned


def chunk_paragraphs(paragraphs: List[str], max_chars: int) -> List[str]:
    """Group adjacent paragraphs into chunks below ``max_chars``."""
    if max_chars <= 0:
        return paragraphs

    chunks: List[str] = []
    buffer: List[str] = []
    buffer_len = 0

    for para in paragraphs:
        para_len = len(para)
        if buffer and (buffer_len + 2 + para_len) > max_chars:
            chunks.append("\n\n".join(buffer))
            buffer = [para]
            buffer_len = para_len
        else:
            buffer.append(para)
            buffer_len = buffer_len + (2 if buffer_len else 0) + para_len

    if buffer:
        chunks.append("\n\n".join(buffer))

    return chunks


def slugify(name: str) -> str:
    return name.replace(" ", "_").replace("/", "_").lower()


def convert_file(processed_path: Path, output_dir: Path, *, max_chars: int) -> Path:
    text = processed_path.read_text(encoding="utf-8")
    paragraphs = list(iter_paragraphs(text))
    chunks = chunk_paragraphs(paragraphs, max_chars=max_chars)

    stem = processed_path.stem
    doc_id = slugify(stem)
    metadata = {
        "doc_id": doc_id,
        "source_file": stem,
        "chunk_count": len(chunks),
        "paragraph_count": len(paragraphs),
        "chunks": [
            {"chunk_id": f"{doc_id}__{idx}", "text": chunk}
            for idx, chunk in enumerate(chunks, start=1)
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{doc_id}.json"
    out_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Convert processed knowledge documents into per-doc JSON")
    parser.add_argument("--root", default=str(Path(__file__).parent), help="Training root directory")
    parser.add_argument("--processed", default=None, help="Override processed text directory")
    parser.add_argument("--output", default=None, help="Output directory for JSON docs")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximum characters per chunk (0 disables chunking)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    processed_dir = Path(args.processed) if args.processed else root / "processed"
    output_dir = Path(args.output) if args.output else root / "json_docs"

    if not processed_dir.exists():
        raise SystemExit(f"Processed directory not found: {processed_dir}")

    processed_files = sorted(processed_dir.glob("*.txt"))
    if not processed_files:
        print(f"No processed text files found in {processed_dir}")
        return 0

    written = []
    for processed_file in processed_files:
        out_path = convert_file(processed_file, output_dir, max_chars=args.max_chars)
        written.append(out_path)

    print(f"Converted {len(written)} document(s) to JSON under {output_dir}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
