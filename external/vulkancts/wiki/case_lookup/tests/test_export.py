from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL_ROOT = HERE.parent
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from build_helper.export import export_lookup_json  # noqa: E402


class LookupExportTests(unittest.TestCase):
    def test_site_frontend_uses_tracked_mapping_data(self) -> None:
        index = (TOOL_ROOT / "site/index.html").read_text(encoding="utf-8")
        self.assertIn("fetch('./mappings.json')", index)
        self.assertIn("findLongestPrefix", index)
        self.assertNotIn("/api/lookup", index)

    def test_exports_deterministic_reviewable_lookup_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "lookup.sqlite3"
            output = root / "mappings.json"
            with sqlite3.connect(database) as connection:
                connection.executescript(
                    """
                    CREATE TABLE mappings (
                        prefix TEXT PRIMARY KEY,
                        page TEXT NOT NULL,
                        category TEXT NOT NULL,
                        wiki_url TEXT NOT NULL
                    );
                    CREATE TABLE metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                    INSERT INTO mappings VALUES (
                        'dEQP-VK.image.qualifiers', 'Qualifiers', 'image',
                        'https://example.test/-/wikis/categories/image/Qualifiers'
                    );
                    INSERT INTO mappings VALUES (
                        'dEQP-VK.api.buffer', 'Buffer', 'api',
                        'https://example.test/-/wikis/categories/api/Buffer'
                    );
                    INSERT INTO metadata VALUES ('kind', 'final');
                    INSERT INTO metadata VALUES ('categories', 'api,image');
                    INSERT INTO metadata VALUES ('mapping_count', '2');
                    """
                )

            first = export_lookup_json(database, output)
            first_bytes = output.read_bytes()
            second = export_lookup_json(database, output)
            second_bytes = output.read_bytes()
            payload = json.loads(first_bytes)

        self.assertEqual(first, second)
        self.assertEqual(first_bytes, second_bytes)
        self.assertTrue(first_bytes.endswith(b"\n"))
        self.assertGreater(first_bytes.count(b"\n"), 5)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["category_count"], 2)
        self.assertEqual(payload["mapping_count"], 2)
        self.assertEqual(
            list(payload["mappings"]),
            ["dEQP-VK.api.buffer", "dEQP-VK.image.qualifiers"],
        )
        self.assertEqual(
            payload["mappings"]["dEQP-VK.api.buffer"],
            ["Buffer", "api", "https://example.test/-/wikis/categories/api/Buffer"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
