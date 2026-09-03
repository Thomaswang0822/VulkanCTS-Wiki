from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify_registration_paths.py")
SPEC = importlib.util.spec_from_file_location("verify_registration_paths", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class RegistrationExtractionTests(unittest.TestCase):
    def extract(self, content: str, category: str = "memory"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Sample.md"
            path.write_text(content, encoding="utf-8")
            validator.HIERARCHY_ERRORS.clear()
            paths = validator.extract_canonical_hierarchy_paths(path, category)
            errors = [message for _path, _line, message in validator.HIERARCHY_ERRORS]
            return paths, errors

    def test_accepts_one_root_and_direct_children(self) -> None:
        content = """## Registration Hierarchy

```text
memory_model
├── message_passing
├── padding (registration only)
└── shared
```
"""
        paths, errors = self.extract(content, "memory_model")
        self.assertEqual(
            set(paths),
            {
                "memory_model",
                "memory_model.message_passing",
                "memory_model.padding",
                "memory_model.shared",
            },
        )
        self.assertEqual(errors, [])

    def test_accepts_root_only_tree(self) -> None:
        content = """## Registration Hierarchy

```text
memory.generated_family
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(set(paths), {"memory.generated_family"})
        self.assertEqual(errors, [])

    def test_rejects_second_text_snippet(self) -> None:
        content = """## Registration Hierarchy

```text
synchronization.basic
└── fence
```

```text
synchronization2.basic
└── fence
```
"""
        paths, errors = self.extract(content, "synchronization")
        self.assertEqual(paths, {})
        self.assertTrue(any("exactly one text fenced block" in error for error in errors))

    def test_accepts_multiple_trees_in_one_snippet(self) -> None:
        content = """## Registration Hierarchy

```text
memory.first
└── child

memory.second
└── child
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(
            set(paths),
            {
                "memory.first",
                "memory.first.child",
                "memory.second",
                "memory.second.child",
            },
        )
        self.assertEqual(errors, [])

    def test_accepts_mixed_root_only_and_expanded_trees(self) -> None:
        content = """## Registration Hierarchy

```text
memory.first
├── alpha
└── beta

memory.second

memory.third
└── gamma (registration only)
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(
            set(paths),
            {
                "memory.first",
                "memory.first.alpha",
                "memory.first.beta",
                "memory.second",
                "memory.third",
                "memory.third.gamma",
            },
        )
        self.assertEqual(errors, [])

    def test_rejects_trees_without_blank_separator(self) -> None:
        content = """## Registration Hierarchy

```text
memory.first
└── child
memory.second
└── child
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(paths, {})
        self.assertTrue(any("separated by a blank line" in error for error in errors))

    def test_rejects_duplicate_root_and_ancestor_overlap(self) -> None:
        duplicate = """## Registration Hierarchy

```text
memory.first

memory.first
```
"""
        overlap = """## Registration Hierarchy

```text
memory

memory.first
```
"""
        duplicate_paths, duplicate_errors = self.extract(duplicate)
        overlap_paths, overlap_errors = self.extract(overlap)
        self.assertEqual(duplicate_paths, {})
        self.assertTrue(any("duplicate Registration Hierarchy root" in error for error in duplicate_errors))
        self.assertEqual(overlap_paths, {})
        self.assertTrue(any("ancestor and descendant" in error for error in overlap_errors))

    def test_rejects_duplicate_direct_child(self) -> None:
        content = """## Registration Hierarchy

```text
memory.first
├── child
└── child
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(paths, {})
        self.assertTrue(any("duplicate direct child" in error for error in errors))

    def test_rejects_child_after_blank_line(self) -> None:
        content = """## Registration Hierarchy

```text
memory.first
├── alpha

└── beta
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(paths, {})
        self.assertTrue(any("child must follow a tree root" in error for error in errors))

    def test_rejects_wrong_category_in_later_tree(self) -> None:
        content = """## Registration Hierarchy

```text
memory.first
└── alpha

api.second
└── beta
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(paths, {})
        self.assertTrue(any("belong to category" in error for error in errors))

    def test_rejects_nested_tree_placeholder_and_hash_comment(self) -> None:
        content = """## Registration Hierarchy

```text
memory.sample
├── <type>
│   └── nested
└── child # comment
```
"""
        _paths, errors = self.extract(content)
        combined = "\n".join(errors)
        self.assertIn("placeholder", combined.lower())
        self.assertIn("nested", combined.lower())
        self.assertIn("#", combined)

    def test_rejects_package_prefix_and_wrong_category_root(self) -> None:
        package_content = """## Registration Hierarchy

```text
dEQP-VK.memory.sample
└── child
```
"""
        wrong_content = """## Registration Hierarchy

```text
memory_model.sample
└── child
```
"""
        package_paths, package_errors = self.extract(package_content)
        wrong_paths, wrong_errors = self.extract(wrong_content)
        self.assertEqual(package_paths, {})
        self.assertTrue(any("dEQP-VK" in error for error in package_errors))
        self.assertEqual(wrong_paths, {})
        self.assertTrue(any("belong to category" in error for error in wrong_errors))

    def test_rejects_non_text_fence(self) -> None:
        content = """## Registration Hierarchy

```markdown
memory.sample
└── child
```
"""
        paths, errors = self.extract(content)
        self.assertEqual(paths, {})
        self.assertTrue(any("exactly one text fenced block" in error for error in errors))

    def test_prefix_tree_matches_entries_and_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text(
                "dEQP-VK.api.external.memory.allocate.case_a\n"
                "dEQP-VK.api.external.pipeline.case_b\n",
                encoding="utf-8",
            )
            tree = validator.build_mustpass_prefix_tree(path)

            found, location = tree.find("dEQP-VK.api.external.memory")
            self.assertTrue(found)
            self.assertEqual(location, (path, 1))
            found, location = tree.find("dEQP-VK.api.external.memory.allocate.case_a")
            self.assertTrue(found)
            self.assertEqual(location, (path, 1))
            self.assertFalse(tree.find("dEQP-VK.api.external.mem")[0])
            self.assertFalse(tree.find("dEQP-VK.api.other")[0])

    def test_validation_output_is_grouped_by_page_and_omits_passed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mustpass_dir = root / "vk-default"
            mustpass_dir.mkdir()
            (mustpass_dir / "api.txt").write_text(
                "dEQP-VK.api.good.case_a\n",
                encoding="utf-8",
            )
            paths = {
                "api.good": [(root / "Good.md", 10)],
                "api.missing": [(root / "Bad.md", 20)],
            }

            validator.HIERARCHY_ERRORS.clear()
            output = io.StringIO()
            with redirect_stdout(output):
                failed = validator.validate_paths(paths, "api", mustpass_dir)

            self.assertEqual(failed, 1)
            self.assertIn(
                "Loaded mustpass file: vk-default/api.txt", output.getvalue()
            )
            self.assertIn("FAIL Bad.md", output.getvalue())
            self.assertIn("PASS Good.md", output.getvalue())
            self.assertIn("     - api.missing:20:", output.getvalue())
            self.assertNotIn("OK: api.good", output.getvalue())

    def test_multiple_mustpass_files_use_multiline_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mustpass_dir = root / "vk-default"
            category_dir = mustpass_dir / "pipeline"
            category_dir.mkdir(parents=True)
            (category_dir / "first.txt").write_text(
                "dEQP-VK.pipeline.good.case_a\n", encoding="utf-8"
            )
            (category_dir / "second.txt").write_text(
                "dEQP-VK.pipeline.other.case_b\n", encoding="utf-8"
            )
            paths = {"pipeline.good": [(root / "Good.md", 10)]}

            validator.HIERARCHY_ERRORS.clear()
            output = io.StringIO()
            with redirect_stdout(output):
                failed = validator.validate_paths(paths, "pipeline", mustpass_dir)

            self.assertEqual(failed, 0)
            self.assertIn(
                "Loaded mustpass files: [\n"
                "     vk-default/pipeline/first.txt\n"
                "     vk-default/pipeline/second.txt\n"
                "]",
                output.getvalue(),
            )
            self.assertNotIn("'", output.getvalue())


if __name__ == "__main__":
    unittest.main()
