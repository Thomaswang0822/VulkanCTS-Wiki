"""Export a validated final SQLite build database as runtime lookup JSON."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

STATIC_SCHEMA_VERSION = 1


def load_lookup_payload(database_path: Path) -> dict[str, object]:
    """Read and validate a final build DB into the browser runtime schema."""
    database_path = database_path.resolve()
    # Close explicitly: the sqlite3 context manager only commits, and an open
    # read-only handle blocks later replace/unlink of the database on Windows.
    connection = sqlite3.connect(
        f"file:{database_path.as_posix()}?mode=ro", uri=True
    )
    try:
        with connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            if {"mappings", "metadata"} - tables:
                raise sqlite3.DatabaseError("database 缺少 mappings 或 metadata 表")
            metadata = dict(connection.execute("SELECT key, value FROM metadata"))
            if metadata.get("kind") != "final":
                raise sqlite3.DatabaseError("JSON export 需要 final database")
            rows = list(
                connection.execute(
                    "SELECT prefix, page, category, wiki_url "
                    "FROM mappings ORDER BY prefix"
                )
            )
    finally:
        connection.close()

    expected_count = int(metadata.get("mapping_count", "-1"))
    if expected_count != len(rows):
        raise sqlite3.DatabaseError("mapping count metadata 不一致")
    categories = [value for value in metadata.get("categories", "").split(",") if value]
    return {
        "schema_version": STATIC_SCHEMA_VERSION,
        "category_count": len(categories),
        "mapping_count": len(rows),
        "mappings": {
            prefix: [page, category, wiki_url]
            for prefix, page, category, wiki_url in rows
        },
    }


def serialize_lookup_payload(payload: dict[str, object]) -> bytes:
    """Serialize stable, line-oriented JSON suitable for Git review."""
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def export_lookup_json(
    database_path: Path, output_path: Path
) -> dict[str, int | str]:
    """Atomically replace the tracked runtime JSON from one final build DB."""
    payload = load_lookup_payload(database_path)
    content = serialize_lookup_payload(payload)
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.unlink(missing_ok=True)
    try:
        temporary_path.write_bytes(content)
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    category_count = payload["category_count"]
    mapping_count = payload["mapping_count"]
    if not isinstance(category_count, int) or not isinstance(mapping_count, int):
        raise TypeError("lookup payload counts must be integers")
    return {
        "output": str(output_path),
        "category_count": category_count,
        "mapping_count": mapping_count,
    }
