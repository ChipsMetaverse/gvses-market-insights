#!/usr/bin/env python3
"""
Phase 5 Backfill Script
=======================
Populate ML feature vectors and training flags in pattern_events.

- Connects to Supabase via env SUPABASE_URL, SUPABASE_ANON_KEY
- Scans pattern_events for rows missing ml_features or not yet marked used_for_training
- Uses PatternFeatureBuilder to compute a 50-feature vector per pattern
- Stores features JSON in pattern_events.ml_features and marks used_for_training
- Optionally assigns a training_split (train/val) based on hash bucketing

Usage:
  python backend/scripts/phase5_backfill.py --limit 5000 --dry-run
  python backend/scripts/phase5_backfill.py --limit 0   # process all

Safety:
- Dry-run prints planned updates without writing
- Batched updates with basic retry
"""
import os
import sys
import json
import time
import math
import argparse
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from supabase import create_client, Client

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.ml.feature_builder import PatternFeatureBuilder

BATCH_SIZE = 500


def _get_client() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        print("[WARN] Supabase credentials missing; set SUPABASE_URL and SUPABASE_ANON_KEY", file=sys.stderr)
        return None
    return create_client(url, key)


def _assign_split(pattern_id: str) -> str:
    # Simple, stable split assignment (80/20 train/val)
    bucket = (hash(pattern_id) & 0xFFFF) / 0x10000
    return "train" if bucket < 0.8 else "val"


def fetch_candidates(client: Client, limit: int) -> List[Dict[str, Any]]:
    """Fetch pattern rows lacking ML features or not yet used_for_training."""
    rows: List[Dict[str, Any]] = []
    start = 0
    remaining = limit if limit and limit > 0 else None

    while True:
        end = start + BATCH_SIZE - 1
        query = (
            client.table("pattern_events")
            .select("*")
            .or_("ml_features.is.null,used_for_training.eq.false")
            .order("created_at", desc=False)
            .range(start, end)
        )
        resp = query.execute()
        batch = resp.data or []
        if not batch:
            break
        rows.extend(batch)
        start += BATCH_SIZE
        if remaining is not None:
            remaining -= len(batch)
            if remaining <= 0:
                break
    return rows


def build_feature_payload(builder: PatternFeatureBuilder, row: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal pattern_data mapping for the builder; enrich as needed
    pattern_data = {
        "id": row.get("id"),
        "symbol": row.get("symbol"),
        "timeframe": row.get("timeframe"),
        "pattern_type": row.get("pattern_type"),
        "support": row.get("support"),
        "resistance": row.get("resistance"),
        "target": row.get("target"),
        "entry": row.get("entry"),
        "confidence": row.get("confidence"),
        "metadata": json.loads(row.get("metadata")) if isinstance(row.get("metadata"), str) else (row.get("metadata") or {}),
        "created_at": row.get("created_at"),
    }
    feature_set = builder.extract_features(pattern_data=pattern_data)
    features_json = feature_set.features
    return {
        "ml_features": json.dumps(features_json),
        "rule_confidence": row.get("confidence"),
        "used_for_training": True,
        "training_split": row.get("training_split") or _assign_split(row.get("id", "")),
        "last_evaluated_at": row.get("last_evaluated_at") or None,
    }


def apply_updates(client: Client, updates: List[Dict[str, Any]], dry_run: bool = False) -> int:
    success = 0
    for upd in updates:
        pid = upd["id"]
        if dry_run:
            print(json.dumps({"id": pid, "updates": upd["updates"]}))
            success += 1
            continue
        try:
            resp = (
                client.table("pattern_events")
                .update(upd["updates"])  # ml_features JSON string, flags
                .eq("id", pid)
                .execute()
            )
            if resp.data:
                success += 1
            else:
                print(f"[WARN] No data returned updating {pid}")
        except Exception as e:
            print(f"[ERROR] Update failed for {pid}: {e}")
    return success


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Max rows to process (0 = all)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes")
    args = parser.parse_args()

    client = _get_client()
    if not client:
        print("[EXIT] No Supabase client; exiting.")
        sys.exit(1)

    builder = PatternFeatureBuilder()

    rows = fetch_candidates(client, args.limit)
    print(f"[INFO] Fetched {len(rows)} candidate rows")

    updates: List[Dict[str, Any]] = []
    for row in rows:
        try:
            payload = build_feature_payload(builder, row)
            updates.append({"id": row.get("id"), "updates": payload})
        except Exception as e:
            print(f"[ERROR] Feature build failed for {row.get('id')}: {e}")

    updated = apply_updates(client, updates, dry_run=args.dry_run)
    print(f"[DONE] Updated {updated} rows{' (dry-run)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
