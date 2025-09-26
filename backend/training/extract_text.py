#!/usr/bin/env python3
"""
Extract text from training knowledge sources into processed .txt files.

Supported formats:
- PDF (PyMuPDF text first; OCR fallback with Tesseract when text is empty/very short)
- Images (OCR via Tesseract)

Outputs are written to backend/training/processed/<basename>.txt
This script is idempotent by default and will skip files that already have outputs,
unless --force is specified.
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyMuPDF (fitz) is required. Please install PyMuPDF.") from exc

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Pillow is required. Please install Pillow.") from exc

"""
Note: OCR via Tesseract is optional. If Tesseract or pytesseract are not available,
the script will still extract text from PDFs that have a text layer, and skip OCR.
"""


RE_HYPHEN_LINEBREAK = re.compile(r"(\w)-\n(\w)")
RE_MULTI_SPACES = re.compile(r"[ \t]{2,}")
RE_MULTI_NEWLINES = re.compile(r"\n{3,}")


@dataclass
class ExtractionConfig:
    knowledge_dir: Path
    processed_dir: Path
    ocr_when_chars_below: int = 32
    dpi_for_ocr: int = 220
    max_pages: Optional[int] = None


def normalize_text(text: str) -> str:
    """Clean common PDF artifacts and normalize whitespace while preserving paragraphs."""
    if not text:
        return ""
    # Join hyphenated line breaks like "engi-\nneering" -> "engineering"
    text = RE_HYPHEN_LINEBREAK.sub(r"\\1\\2", text)
    # Replace Windows line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse >2 blank lines
    text = RE_MULTI_NEWLINES.sub("\n\n", text)
    # Collapse long spaces but keep single spaces
    text = RE_MULTI_SPACES.sub(" ", text)
    return text.strip()


def ensure_dirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_source_files(knowledge_dir: Path) -> List[Path]:
    exts = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff"}
    files: List[Path] = []
    for entry in sorted(knowledge_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() in exts:
            files.append(entry)
    return files


def render_page_to_image(page: "fitz.Page", dpi: int) -> Image.Image:
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return img


def ocr_image(image: Image.Image) -> str:
    try:
        import pytesseract  # Lazy import to avoid hard dependency when OCR is not needed
    except Exception:
        return ""
    try:
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def extract_text_from_pdf(pdf_path: Path, cfg: ExtractionConfig) -> str:
    doc = fitz.open(pdf_path)
    texts: List[str] = []
    num_pages = len(doc)
    pages_to_process = range(num_pages)
    if cfg.max_pages is not None:
        pages_to_process = range(min(num_pages, cfg.max_pages))
    for page_index in pages_to_process:
        page = doc.load_page(page_index)
        text = page.get_text("text") or ""
        # Fallback to OCR if the text layer is too short (likely scanned PDF)
        if len(text.strip()) < cfg.ocr_when_chars_below:
            image = render_page_to_image(page, cfg.dpi_for_ocr)
            text = ocr_image(image)
        texts.append(text)
    joined = "\n\n".join(texts)
    return normalize_text(joined)


def extract_text_from_image(image_path: Path) -> str:
    img = Image.open(image_path)
    text = ocr_image(img)
    return normalize_text(text)


def write_output(processed_dir: Path, source_file: Path, text: str) -> Path:
    ensure_dirs(processed_dir)
    out_path = processed_dir / (source_file.stem + ".txt")
    out_path.write_text(text, encoding="utf-8")
    return out_path


def process_file(source_file: Path, cfg: ExtractionConfig, force: bool) -> Optional[Path]:
    out_path = cfg.processed_dir / (source_file.stem + ".txt")
    if out_path.exists() and not force:
        return None
    if source_file.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(source_file, cfg)
    else:
        text = extract_text_from_image(source_file)
    return write_output(cfg.processed_dir, source_file, text)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Extract & normalize text from training knowledge sources")
    parser.add_argument("--knowledge-dir", default=str(Path(__file__).parent / "knowledge"), help="Path to knowledge sources directory")
    parser.add_argument("--processed-dir", default=str(Path(__file__).parent / "processed"), help="Output directory for processed text files")
    parser.add_argument("--force", action="store_true", help="Rebuild outputs even if they already exist")
    parser.add_argument("--max-pages", type=int, default=None, help="Optional max pages per PDF (for quick iteration)")
    args = parser.parse_args(argv)

    cfg = ExtractionConfig(
        knowledge_dir=Path(args.knowledge_dir),
        processed_dir=Path(args.processed_dir),
        max_pages=args.max_pages,
    )

    ensure_dirs(cfg.processed_dir)
    sources = list_source_files(cfg.knowledge_dir)
    if not sources:
        print(f"No source files found in {cfg.knowledge_dir}")
        return 0

    written: List[Path] = []
    skipped = 0
    for src in sources:
        out = process_file(src, cfg, force=args.force)
        if out is None:
            skipped += 1
        else:
            written.append(out)

    print(f"Processed {len(written)} file(s); skipped {skipped} existing.")
    if written:
        for p in written:
            print(f"  - {p}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


