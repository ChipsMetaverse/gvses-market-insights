#!/usr/bin/env python3
"""Supabase schema diagnostic helper.

Run this script to inspect the sessions/conversations tables and perform a
lightweight insert/delete round trip to confirm constraints. Requires
`SUPABASE_URL` and `SUPABASE_ANON_KEY` in the environment.
"""

import os
import sys
import uuid
from typing import Any

from supabase import Client, create_client


def _print(title: str, payload: Any) -> None:
    print(f"\n=== {title} ===")
    if isinstance(payload, list):
        for item in payload:
            print(item)
    else:
        print(payload)


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise SystemExit("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
    return create_client(url, key)


def fetch_columns(client: Client, table_name: str) -> None:
    try:
        response = client.table("information_schema.columns").select(
            "column_name,data_type,is_nullable"
        ).eq("table_name", table_name).execute()
        _print(f"Columns for {table_name}", response.data or [])
    except Exception as exc:  # pragma: no cover
        _print(f"Failed to fetch columns for {table_name}", exc)


def sanity_round_trip(client: Client) -> None:
    session_id = f"diag_{uuid.uuid4().hex[:12]}"
    try:
        insert_payload = {"id": session_id, "created_at": None}
        client.table("sessions").insert(insert_payload).execute()
        client.table("conversations").insert(
            {
                "session_id": session_id,
                "role": "diagnostic",
                "content": "schema connectivity check",
            }
        ).execute()
        _print("Insert status", "success")
    except Exception as exc:
        _print("Insert status", f"failed: {exc}")
    finally:
        try:
            client.table("conversations").delete().eq("session_id", session_id).execute()
            client.table("sessions").delete().eq("id", session_id).execute()
        except Exception as cleanup_error:  # pragma: no cover
            _print("Cleanup warning", cleanup_error)


def main() -> None:
    client = get_client()
    fetch_columns(client, "sessions")
    fetch_columns(client, "conversations")
    sanity_round_trip(client)


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except SystemExit as exc:
        print(exc)
        sys.exit(1)
