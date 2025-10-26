#!/usr/bin/env python3
"""
Generate a consolidated trading pattern library from the processed knowledge corpus.

This script reads `config/pattern_index.yaml` to understand which pattern definitions we
care about, extracts supporting text from the JSON knowledge dumps under
`json_docs/`, merges the result with any structured overrides, validates the final
objects against the JSON schema, and writes a `patterns.generated.json` artifact.

The generated file becomes the single source of truth that the runtime
`PatternLibrary` consumes. Run this script whenever knowledge docs are updated or
new patterns are curated.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml  # type: ignore
from jsonschema import Draft7Validator  # type: ignore


@dataclass
class GeneratorPaths:
    """Filesystem locations required to build the pattern library."""

    root: Path
    json_docs: Path
    config: Path
    schema_file: Path
    index_file: Path
    output_file: Path


def load_schema(schema_path: Path) -> Draft7Validator:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return Draft7Validator(schema)


def load_index(index_path: Path) -> Dict[str, Any]:
    if not index_path.exists():
        raise FileNotFoundError(
            f"Pattern index not found at {index_path}. Copy the template and populate entries."
        )
    return yaml.safe_load(index_path.read_text(encoding="utf-8")) or {"patterns": []}


def load_json_docs(json_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load all JSON knowledge documents into memory keyed by useful identifiers."""

    docs: Dict[str, Dict[str, Any]] = {}
    for path in json_dir.glob("*.json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - knowledge artifacts must be valid
            raise RuntimeError(f"Malformed JSON doc at {path}: {exc}") from exc

        stem = path.stem.lower()
        if "doc_id" in doc:
            docs[doc["doc_id"].lower()] = doc
        if "source_file" in doc:
            docs[str(doc["source_file"]).lower()] = doc
        docs[stem] = doc
    return docs


def slugify(value: str) -> str:
    """Normalize a document identifier for lookup."""

    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug


def iter_doc_candidates(doc_name: str) -> Iterable[str]:
    base = Path(doc_name).stem.lower()
    yield base
    yield slugify(base)
    yield base.replace(" ", "_").replace("-", "_")
    yield base.replace("_", "-")


def resolve_doc(doc_name: str, json_docs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    for candidate in iter_doc_candidates(doc_name):
        if candidate in json_docs:
            return json_docs[candidate]
    raise FileNotFoundError(
        f"No JSON knowledge document found for '{doc_name}'. Expected one of: {set(json_docs.keys())}"
    )


def flatten_doc_text(doc: Dict[str, Any]) -> str:
    chunks = doc.get("chunks") or []
    parts: List[str] = []
    for chunk in chunks:
        text = (chunk.get("text") or "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def slice_between_markers(text: str, start_marker: Optional[str], end_marker: Optional[str]) -> str:
    if not start_marker:
        return ""

    pattern = re.compile(re.escape(start_marker), flags=re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""

    start_idx = match.end()
    end_idx = len(text)
    if end_marker:
        end_pattern = re.compile(re.escape(end_marker), flags=re.IGNORECASE)
        end_match = end_pattern.search(text, pos=start_idx)
        if end_match:
            end_idx = end_match.start()

    snippet = text[start_idx:end_idx].strip()
    if not snippet:
        return ""
    # Trim excessively long snippets by paragraph blocks
    paragraphs = [p.strip() for p in snippet.split("\n\n") if p.strip()]
    if len("\n\n".join(paragraphs)) > 8000:
        snippet = "\n\n".join(paragraphs[:8])
    return snippet


def snippet_from_doc(
    doc: Dict[str, Any],
    start_marker: Optional[str],
    end_marker: Optional[str],
    page_hint: Optional[int],
) -> str:
    text = flatten_doc_text(doc)
    snippet = slice_between_markers(text, start_marker, end_marker)
    if snippet:
        return snippet

    if page_hint is not None:
        # Approximate page selection by paragraph index
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if paragraphs:
            index = max(0, min(len(paragraphs) - 1, page_hint - 1))
            window = paragraphs[index : index + 3]
            if window:
                return "\n\n".join(window)

    # Fallback: return the opening paragraphs to avoid empty description
    fallback_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()][:3]
    return "\n\n".join(fallback_paragraphs)


def build_entry_from_index_item(
    item: Dict[str, Any],
    json_docs: Dict[str, Dict[str, Any]],
    allow_placeholders: bool,
) -> Dict[str, Any]:
    pattern_id: str = item["pattern_id"]
    display_name: str = item.get("display_name", pattern_id.replace("_", " ").title())
    category: str = item.get("category", "price_action")
    aliases: List[str] = list(item.get("aliases", []) or [])
    overrides: Dict[str, Any] = item.get("overrides", {}) or {}

    description_override: Optional[str] = overrides.get("description")
    description_parts: List[str] = []
    sources_meta: List[Dict[str, Any]] = []

    for src in item.get("sources", []) or []:
        doc_name = src["doc"]
        start_marker: Optional[str] = src.get("start_marker")
        end_marker: Optional[str] = src.get("end_marker")
        page_hint: Optional[int] = src.get("page_hint")

        doc = resolve_doc(doc_name, json_docs)
        snippet = snippet_from_doc(doc, start_marker, end_marker, page_hint)
        if snippet:
            description_parts.append(snippet)
        sources_meta.append({
            "doc": doc.get("source_file", doc.get("doc_id", doc_name)),
            "page": page_hint,
        })

    if description_override:
        description = description_override.strip()
    else:
        description = "\n\n".join(description_parts).strip()

    recognition_rules = {
        "candle_structure": "",
        "trend_context": "",
        "volume_confirmation": None,
        "invalidations": [],
    }
    recognition_rules.update(overrides.get("recognition_rules", {}))

    trading_overrides = overrides.get("trading_playbook", {}) or {}
    trading_playbook = {
        "signal": trading_overrides.get("signal", "neutral"),
        "entry": trading_overrides.get("entry", ""),
        "stop_loss": trading_overrides.get("stop_loss", ""),
        "targets": trading_overrides.get("targets", []),
        "risk_notes": trading_overrides.get("risk_notes", None),
        "timeframe_bias": trading_overrides.get("timeframe_bias", None),
    }

    for key, value in list(recognition_rules.items()):
        if isinstance(value, str):
            recognition_rules[key] = value.strip()
    for key, value in list(trading_playbook.items()):
        if isinstance(value, str):
            trading_playbook[key] = value.strip()

    if not description and allow_placeholders:
        description = f"Summary for {display_name} to be curated."
    if allow_placeholders:
        if not recognition_rules["candle_structure"]:
            recognition_rules["candle_structure"] = "TBD"
        if not recognition_rules["trend_context"]:
            recognition_rules["trend_context"] = "TBD"
        if not trading_playbook["entry"]:
            trading_playbook["entry"] = "TBD"
        if not trading_playbook["stop_loss"]:
            trading_playbook["stop_loss"] = "TBD"

    entry: Dict[str, Any] = {
        "pattern_id": pattern_id,
        "category": category,
        "display_name": display_name,
        "aliases": aliases,
        "description": description,
        "recognition_rules": recognition_rules,
        "trading_playbook": trading_playbook,
        "statistics": overrides.get("statistics", {}),
        "visual_examples": overrides.get("visual_examples", []),
        "sources": sources_meta,
    }
    return entry


def validate_entries(entries: List[Dict[str, Any]], validator: Draft7Validator) -> List[Tuple[int, str]]:
    errors: List[Tuple[int, str]] = []
    for index, entry in enumerate(entries):
        for error in sorted(validator.iter_errors(entry), key=lambda e: e.path):
            errors.append((index, error.message))
    return errors


def build_pattern_library(paths: GeneratorPaths, allow_placeholders: bool) -> List[Dict[str, Any]]:
    validator = load_schema(paths.schema_file)
    index = load_index(paths.index_file)
    json_docs = load_json_docs(paths.json_docs)

    patterns: List[Dict[str, Any]] = []
    for item in index.get("patterns", []) or []:
        try:
            entry = build_entry_from_index_item(item, json_docs, allow_placeholders)
        except Exception as exc:
            raise RuntimeError(f"Failed to build pattern '{item.get('pattern_id')}': {exc}") from exc
        patterns.append(entry)

    errors = validate_entries(patterns, validator)
    if errors:
        formatted = "\n".join(f"  - [#{idx}] {msg}" for idx, msg in errors)
        raise ValueError(f"Pattern schema validation failed:\n{formatted}")

    return patterns


def write_output(patterns: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.write_text(json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate patterns.generated.json from knowledge docs")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).parent),
        help="Training directory root (defaults to script directory)",
    )
    parser.add_argument(
        "--output",
        default="patterns.generated.json",
        help="Output filename (written under training root)",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Fill minimal placeholder text when knowledge snippets are missing",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    root = Path(args.root).resolve()
    paths = GeneratorPaths(
        root=root,
        json_docs=root / "json_docs",
        config=root / "config",
        schema_file=root / "schema" / "pattern_schema.json",
        index_file=root / "config" / "pattern_index.yaml",
        output_file=root / args.output,
    )

    if not paths.json_docs.exists():
        raise FileNotFoundError(f"Knowledge JSON docs not found at {paths.json_docs}. Run acquisition pipeline first.")

    patterns = build_pattern_library(paths, allow_placeholders=args.allow_placeholders)
    write_output(patterns, paths.output_file)
    print(f"Wrote {len(patterns)} pattern(s) to {paths.output_file}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
