#!/usr/bin/env python3
"""
Build a structured patterns.json dataset from processed text using a YAML index.

Steps:
1) Read config/pattern_index.yaml (copy from config/pattern_index_template.yaml)
2) For each pattern, locate text via start/end markers (in processed/<doc>.txt)
3) Populate schema fields (with optional overrides) and validate against schema
4) Write patterns.json

This is designed to be re-runnable.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml  # type: ignore
from jsonschema import Draft7Validator  # type: ignore


@dataclass
class BuilderPaths:
    root: Path
    processed: Path
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
            f"Index file not found: {index_path}. Copy the template and fill entries."
        )
    return yaml.safe_load(index_path.read_text(encoding="utf-8")) or {"patterns": []}


def read_processed_text(processed_dir: Path, doc_name: str) -> str:
    text_path = processed_dir / (Path(doc_name).stem + ".txt")
    if not text_path.exists():
        raise FileNotFoundError(
            f"Processed text for {doc_name} not found at {text_path}. Run extract_text.py first."
        )
    return text_path.read_text(encoding="utf-8")


def slice_between_markers(text: str, start_marker: str, end_marker: Optional[str]) -> str:
    # Use case-insensitive search; allow some fuzz around markers
    start_match = re.search(re.escape(start_marker), text, flags=re.IGNORECASE)
    if not start_match:
        return ""
    start_idx = start_match.end()
    end_idx = len(text)
    if end_marker:
        end_match = re.search(re.escape(end_marker), text, flags=re.IGNORECASE)
        if end_match and end_match.start() > start_idx:
            end_idx = end_match.start()
    snippet = text[start_idx:end_idx].strip()
    # Trim to a reasonable length by paragraph if extremely long
    paragraphs = [p.strip() for p in snippet.split("\n\n") if p.strip()]
    if len("\n\n".join(paragraphs)) > 8000:  # safety cap
        snippet = "\n\n".join(paragraphs[:8])
    return snippet


def build_entry_from_index_item(item: Dict[str, Any], processed_dir: Path, allow_placeholders: bool) -> Dict[str, Any]:
    pattern_id: str = item["pattern_id"]
    display_name: str = item.get("display_name", pattern_id.replace("_", " ").title())
    category: str = item.get("category", "price_action")
    aliases: List[str] = list(item.get("aliases", []) or [])
    overrides: Dict[str, Any] = item.get("overrides", {}) or {}

    # Gather snippets from sources
    description_override: Optional[str] = overrides.get("description")
    description_parts: List[str] = []
    sources_meta: List[Dict[str, Any]] = []
    for src in item.get("sources", []) or []:
        doc = src["doc"]
        start_marker: Optional[str] = src.get("start_marker")
        end_marker: Optional[str] = src.get("end_marker")
        page_hint: Optional[int] = src.get("page_hint")

        text = read_processed_text(processed_dir, doc)
        snippet = ""
        if start_marker:
            snippet = slice_between_markers(text, start_marker, end_marker)
        # Fallback: if no markers or not found, take first paragraphs near page_hint
        if not snippet:
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            if page_hint and 0 < page_hint < len(paragraphs):
                snippet = "\n\n".join(paragraphs[page_hint - 1 : page_hint + 2])
            elif paragraphs:
                snippet = paragraphs[0]

        if snippet:
            description_parts.append(snippet)
        sources_meta.append({"doc": doc, "page": page_hint})

    if description_override:
        description = description_override.strip()
    else:
        description = "\n\n".join(description_parts).strip()

    # Defaults, optionally overridden
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

    # Strip whitespace from string fields for cleanliness
    for key, value in list(recognition_rules.items()):
        if isinstance(value, str):
            recognition_rules[key] = value.strip()
    for key, value in list(trading_playbook.items()):
        if isinstance(value, str):
            trading_playbook[key] = value.strip()

    # If description is empty, optionally set a minimal placeholder to pass validation
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
    for i, entry in enumerate(entries):
        errs = sorted(validator.iter_errors(entry), key=lambda e: e.path)
        for err in errs:
            errors.append((i, err.message))
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build structured patterns.json from processed text and YAML index")
    parser.add_argument("--root", default=str(Path(__file__).parent), help="Training root (default: script directory)")
    parser.add_argument("--allow-placeholders", action="store_true", help="Fill minimal TBD values to pass validation")
    parser.add_argument("--output", default="patterns.json", help="Output filename (written under training root)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    paths = BuilderPaths(
        root=root,
        processed=root / "processed",
        config=root / "config",
        schema_file=root / "schema" / "pattern_schema.json",
        index_file=root / "config" / "pattern_index.yaml",
        output_file=root / args.output,
    )

    validator = load_schema(paths.schema_file)
    index = load_index(paths.index_file)

    raw_patterns: List[Dict[str, Any]] = []
    for item in index.get("patterns", []) or []:
        try:
            entry = build_entry_from_index_item(item, paths.processed, allow_placeholders=args.allow_placeholders)
            raw_patterns.append(entry)
        except Exception as exc:
            print(f"Error building {item.get('pattern_id')}: {exc}")

    errors = validate_entries(raw_patterns, validator)
    if errors:
        print("Validation errors:")
        for i, msg in errors:
            print(f"  - [#{i}] {msg}")
        print("Aborting write due to validation errors.")
        return 2

    paths.output_file.write_text(json.dumps(raw_patterns, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(raw_patterns)} pattern(s) to {paths.output_file}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
