from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL_ROOT = HERE.parent
REPO_ROOT = TOOL_ROOT.parents[3]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from build import (  # noqa: E402
    MappingBuildError,
    build_category_databases,
    build_database,
    extract_page_ownership,
    iter_mustpass_leaves,
    merge_category_databases,
    merge_selected_category_databases,
)
from build_helper import CATEGORY_MUSTPASS_FILES  # noqa: E402
from lookup import LookupIndex  # noqa: E402


class ExtractionTests(unittest.TestCase):
    def test_extracts_roots_and_direct_children(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "Example.md"
            page.write_text(
                """## Registration Hierarchy

```text
api.alpha
├── first
└── second (registration only)

api.beta
```
""",
                encoding="utf-8",
            )
            trees = extract_page_ownership(page, "api")

        self.assertEqual(
            [(tree.root, tree.children) for tree in trees],
            [("api.alpha", ("first",)), ("api.beta", ())],
        )
        self.assertEqual(trees[0].children, ("first",))

    def test_requires_blank_line_between_trees(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "Example.md"
            page.write_text(
                """## Registration Hierarchy

```text
api.alpha
api.beta
```
""",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(MappingBuildError, "之间必须有空行"):
                extract_page_ownership(page, "api")

    def test_shared_sync_pages_select_requested_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "Example.md"
            page.write_text(
                """## Registration Hierarchy

```text
synchronization.basic
└── fence
```

```text
synchronization2.basic
└── fence
```
""",
                encoding="utf-8",
            )
            trees = extract_page_ownership(page, "synchronization2")

        self.assertEqual(
            [(tree.root, tree.children) for tree in trees],
            [
                ("synchronization.basic", ("fence",)),
                ("synchronization2.basic", ("fence",)),
            ],
        )


class MustpassInputTests(unittest.TestCase):
    def test_only_validated_categories_are_enabled(self) -> None:
        self.assertEqual(
            list(CATEGORY_MUSTPASS_FILES),
            [
                "info",
                "api",
                "memory",
                "pipeline",
                "binding_model",
                "spirv_assembly",
                "glsl",
                "renderpasses",
                "ubo",
                "dynamic_state",
                "ssbo",
                "query_pool",
                "draw",
                "compute",
                "image",
                "image_processing",
                "wsi",
                "synchronization",
                "synchronization2",
                "sparse_resources",
                "tessellation",
                "rasterization",
                "clipping",
                "fragment_operations",
                "texture",
                "geometry",
                "robustness",
                "multiview",
                "subgroups",
                "ycbcr",
                "protected_memory",
                "device_group",
                "memory_model",
                "conditional_rendering",
                "graphicsfuzz",
                "imageless_framebuffer",
                "transform_feedback",
                "descriptor_indexing",
                "fragment_shader_interlock",
                "fragment_shading_barycentric",
                "fragment_shading_rate",
                "drm_format_modifiers",
                "ray_tracing_pipeline",
                "ray_query",
                "reconvergence",
                "shader_object",
                "dgc",
            ],
        )

    def test_reads_multiple_configured_files_and_rejects_cross_file_duplicates(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.txt"
            second = root / "second.txt"
            first.write_text("dEQP-VK.api.alpha.one\n", encoding="utf-8")
            second.write_text("dEQP-VK.api.beta.one\n", encoding="utf-8")
            self.assertEqual(
                list(iter_mustpass_leaves((first, second), "api")),
                ["dEQP-VK.api.alpha.one", "dEQP-VK.api.beta.one"],
            )
            second.write_text("dEQP-VK.api.alpha.one\n", encoding="utf-8")
            with self.assertRaisesRegex(MappingBuildError, "重复 path"):
                list(iter_mustpass_leaves((first, second), "api"))

    def test_projects_multiview_rendering_wrapper(self) -> None:
        from build_helper.category_handlers import project_category_mappings

        owner = object()
        projected = project_category_mappings(
            {"dEQP-VK.multiview.renderpass2": owner},
            ("dEQP-VK.multiview.renderpass2.masks.no_queries.15",),
            "multiview",
        )
        self.assertIs(projected["dEQP-VK.multiview.renderpass2.masks"], owner)

    def test_projects_graphicsfuzz_generated_leaf(self) -> None:
        from build_helper.category_handlers import project_category_mappings

        owner = object()
        path = "dEQP-VK.graphicsfuzz.access-new-vector-inside-if-condition"
        projected = project_category_mappings(
            {"dEQP-VK.graphicsfuzz": owner}, (path,), "graphicsfuzz"
        )
        self.assertIs(projected[path], owner)

    def test_accepts_newly_enabled_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stats = build_category_databases(
                REPO_ROOT,
                ("multiview",),
                "https://example.test/-/wikis",
                root / "db",
            )
            self.assertEqual(stats["multiview"]["leaves"], 694)


class BuildDatabaseTests(unittest.TestCase):
    def test_category_build_and_final_merge_can_run_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_dir = root / "db"
            final_database = root / "lookup.sqlite3"

            category_stats = build_category_databases(
                REPO_ROOT,
                ("rasterization",),
                "https://example.test/-/wikis",
                db_dir,
            )

            self.assertEqual(category_stats["rasterization"]["leaves"], 15079)
            self.assertTrue((db_dir / "rasterization.sqlite3").is_file())
            self.assertFalse(final_database.exists())

            merge_stats = merge_selected_category_databases(
                final_database,
                ("rasterization",),
                db_dir,
            )

            self.assertEqual(merge_stats["category_count"], 1)
            self.assertEqual(merge_stats["categories"], ["rasterization"])
            self.assertEqual(merge_stats["mappings"], 46)
            self.assertTrue(final_database.is_file())

    def test_builds_category_databases_and_deterministic_final_database(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "lookup.sqlite3"
            db_dir = root / "db"
            stats = build_database(
                repo_root=REPO_ROOT,
                database_path=database,
                categories=("api", "rasterization"),
                wiki_base_url="https://example.test/-/wikis",
                category_db_dir=db_dir,
                json_path=root / "mappings.json",
            )
            first_bytes = database.read_bytes()
            first_json_bytes = (root / "mappings.json").read_bytes()
            first_api_bytes = (db_dir / "api.sqlite3").read_bytes()
            rebuilt_stats = build_database(
                repo_root=REPO_ROOT,
                database_path=database,
                categories=("rasterization", "api"),
                wiki_base_url="https://example.test/-/wikis",
                category_db_dir=db_dir,
                json_path=root / "mappings.json",
            )
            index = LookupIndex(root / "mappings.json")
            try:
                api = index.lookup("dEQP-VK.api.buffer.basic.max_size")
                rasterization = index.lookup("dEQP-VK.rasterization.culling.front_cw")
                indirect_copy = index.lookup(
                    "dEQP-VK.api.copy_and_blit.core.memory_to_image_indirect.2d_images.array"
                )
                shader_tile = index.lookup(
                    "dEQP-VK.rasterization.shader_tile_image.coherent.color"
                )
            finally:
                index.close()
            rebuilt_bytes = database.read_bytes()
            rebuilt_json_bytes = (root / "mappings.json").read_bytes()
            rebuilt_api_bytes = (db_dir / "api.sqlite3").read_bytes()

        self.assertEqual(stats, rebuilt_stats)
        self.assertEqual(list(stats["categories"]), ["api", "rasterization"])
        self.assertEqual(stats["final"]["category_count"], 2)
        self.assertEqual(first_bytes, rebuilt_bytes)
        self.assertEqual(first_json_bytes, rebuilt_json_bytes)
        self.assertEqual(first_api_bytes, rebuilt_api_bytes)
        self.assertEqual(stats["categories"]["api"]["leaves"], 327795)
        self.assertEqual(stats["categories"]["rasterization"]["leaves"], 15079)
        self.assertEqual(stats["final"]["mappings"], 535)
        self.assertEqual(api.page, "Buffer")
        self.assertEqual(api.matched_prefix, "dEQP-VK.api.buffer.basic")
        self.assertEqual(rasterization.page, "Core")
        self.assertEqual(indirect_copy.page, "CopyMemoryIndirect")
        self.assertEqual(
            indirect_copy.matched_prefix,
            "dEQP-VK.api.copy_and_blit.core.memory_to_image_indirect",
        )
        self.assertEqual(shader_tile.page, "ShaderTileImage")
        self.assertEqual(
            shader_tile.matched_prefix, "dEQP-VK.rasterization.shader_tile_image.coherent"
        )
        self.assertTrue(api.wiki_url.endswith("/categories/api/Buffer"))

    def test_merge_rejects_duplicate_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "lookup.sqlite3"
            db_dir = root / "db"
            build_database(
                REPO_ROOT,
                database,
                ("rasterization",),
                "https://example.test/-/wikis",
                db_dir,
            )
            with self.assertRaisesRegex(MappingBuildError, "重复 category DB"):
                merge_category_databases(
                    (db_dir / "rasterization.sqlite3", db_dir / "rasterization.sqlite3"),
                    root / "invalid.sqlite3",
                )

    def test_category_database_is_self_describing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_database(
                REPO_ROOT,
                root / "final.sqlite3",
                ("rasterization",),
                "https://example.test/-/wikis",
                root / "db",
            )
            connection = sqlite3.connect(root / "db/rasterization.sqlite3")
            try:
                with connection:
                    metadata = dict(
                        connection.execute("SELECT key, value FROM metadata")
                    )
                    table_names = {
                        row[0]
                        for row in connection.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
            finally:
                connection.close()

        self.assertEqual(metadata["category"], "rasterization")
        self.assertEqual(metadata["kind"], "category")
        self.assertEqual(metadata["schema_version"], "2")
        self.assertEqual(metadata["mapping_count"], "46")
        self.assertIn("source_manifest", metadata)
        self.assertEqual(table_names, {"mappings", "metadata"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
