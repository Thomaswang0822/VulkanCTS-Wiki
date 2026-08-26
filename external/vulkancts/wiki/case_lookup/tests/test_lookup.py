from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL_ROOT = HERE.parent
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from lookup import InvalidPathError, LookupIndex, validate_mustpass  # noqa: E402


MAPPINGS = {
    "dEQP-VK.api.buffer": [
        "Buffer",
        "api",
        "https://example.test/-/wikis/categories/api/Buffer",
    ],
    "dEQP-VK.api.copy_and_blit.core.use_after_copy": [
        "UseAfterCopy",
        "api",
        "https://example.test/-/wikis/categories/api/UseAfterCopy",
    ],
    "dEQP-VK.api.copy_and_blit.copy_commands2.buffer_to_image": [
        "CopyBufferToImage",
        "api",
        "https://example.test/-/wikis/categories/api/CopyBufferToImage",
    ],
    "dEQP-VK.rasterization.fill_rules_multisample_16_bit": [
        "Core",
        "rasterization",
        "https://example.test/-/wikis/categories/rasterization/Core",
    ],
}


def write_index(path: Path, mappings: dict[str, list[str]]) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "category_count": len({row[1] for row in mappings.values()}),
                "mapping_count": len(mappings),
                "mappings": mappings,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


class LookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.json_path = Path(self.tmp.name) / "mappings.json"
        write_index(self.json_path, MAPPINGS)
        self.index = LookupIndex(self.json_path)

    def tearDown(self) -> None:
        self.index.close()
        self.tmp.cleanup()

    def test_shortest_prefix_owns_descendant(self) -> None:
        result = self.index.lookup("dEQP-VK.api.buffer.basic.max_size")
        self.assertEqual(result.page, "Buffer")
        self.assertEqual(result.matched_prefix, "dEQP-VK.api.buffer")

    def test_normalized_dispatcher_path_is_an_ordinary_prefix(self) -> None:
        result = self.index.lookup(
            "dEQP-VK.api.copy_and_blit.copy_commands2.buffer_to_image.2d_images.array"
        )
        self.assertEqual(result.page, "CopyBufferToImage")
        self.assertEqual(
            result.matched_prefix,
            "dEQP-VK.api.copy_and_blit.copy_commands2.buffer_to_image",
        )

    def test_longest_prefix_wins(self) -> None:
        result = self.index.lookup(
            "dEQP-VK.api.copy_and_blit.core.use_after_copy.r8_unorm.general.32x32x1"
        )
        self.assertEqual(result.page, "UseAfterCopy")

    def test_rejects_non_full_path(self) -> None:
        with self.assertRaises(InvalidPathError):
            self.index.lookup("api.buffer.basic.max_size")

    def test_accepts_numeric_components_with_leading_minus(self) -> None:
        self.assertEqual(
            self.index.validate_path("dEQP-VK.pipeline.family.clear_value_-3"),
            "dEQP-VK.pipeline.family.clear_value_-3",
        )

    def test_accepts_category_level_leaf(self) -> None:
        self.assertEqual(
            self.index.validate_path("dEQP-VK.info.build"),
            "dEQP-VK.info.build",
        )

    def test_component_boundary_prevents_raw_prefix_match(self) -> None:
        self.assertIsNone(self.index.lookup("dEQP-VK.api.buffer2.max_size"))

    def test_runtime_has_no_suffix_fallback(self) -> None:
        self.assertIsNone(
            self.index.lookup("dEQP-VK.rasterization.fill_rules_other.basic_quad")
        )


class CoverageTests(unittest.TestCase):
    def test_reports_every_case_and_failure_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_path = root / "mappings.json"
            mustpass = root / "api.txt"
            write_index(
                index_path,
                {
                    "dEQP-VK.api.buffer": [
                        "Buffer",
                        "api",
                        "https://example.test/-/wikis/categories/api/Buffer",
                    ]
                },
            )
            mustpass.write_text(
                "dEQP-VK.api.buffer.basic.max_size\n"
                "dEQP-VK.api.unknown.case\n",
                encoding="utf-8",
            )
            report = validate_mustpass(index_path, (mustpass,))

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["failure_samples"], ["dEQP-VK.api.unknown.case"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
