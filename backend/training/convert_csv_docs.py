#!/usr/bin/env python3
"""Convert CSV knowledge exports into json_docs entries.

Each CSV file under knowledge/csv/ is assumed to contain one text column
exported from a PDF or image OCR pass. We join the rows, normalize blank
lines, and emit the same JSON structure produced by convert_docs.py so that
the downstream knowledge builders can consume them consistently.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable, List, Optional


def slugify(name: str) -> str:
    return name.replace(" ", "_").replace("/", "_").lower()


def chunk_paragraphs(paragraphs: List[str], max_chars: int) -> List[str]:
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


def load_csv_paragraphs(csv_path: Path) -> List[str]:
    paragraphs: List[str] = []
    buffer: List[str] = []

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            text = " ".join(cell.strip() for cell in row if cell.strip())
            text = text.replace("\f", "").strip()
            if not text:
                if buffer:
                    paragraphs.append(" ".join(buffer).strip())
                    buffer = []
                continue
            buffer.append(text)

    if buffer:
        paragraphs.append(" ".join(buffer).strip())

    # Remove empty entries
    return [p for p in paragraphs if p]


def convert_csv_file(csv_path: Path, output_dir: Path, *, max_chars: int) -> Path:
    paragraphs = load_csv_paragraphs(csv_path)
    chunks = chunk_paragraphs(paragraphs, max_chars=max_chars)

    stem = csv_path.stem
    doc_id = slugify(stem)
    payload = {
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
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Convert CSV knowledge documents into json_docs format")
    parser.add_argument("--root", default=str(Path(__file__).parent), help="Training root directory")
    parser.add_argument("--csv-dir", default=None, help="Override CSV source directory")
    parser.add_argument("--output", default=None, help="Output directory for JSON docs")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximum characters per chunk (0 keeps paragraphs)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    csv_dir = Path(args.csv_dir) if args.csv_dir else root / "knowledge" / "csv"
    output_dir = Path(args.output) if args.output else root / "json_docs"

    if not csv_dir.exists():
        raise SystemExit(f"CSV directory not found: {csv_dir}")

    csv_files = sorted(p for p in csv_dir.glob("*.csv") if p.is_file())
    if not csv_files:
        print(f"No CSV files found in {csv_dir}")
        return 0

    written = []
    for csv_path in csv_files:
        out_path = convert_csv_file(csv_path, output_dir, max_chars=args.max_chars)
        written.append(out_path)

    print(f"Converted {len(written)} CSV document(s) to JSON under {output_dir}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
