import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('check_line_refs.py')
spec = importlib.util.spec_from_file_location('line_refs', SCRIPT)
assert spec is not None and spec.loader is not None
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


class ReferenceTests(unittest.TestCase):
    def check(self, source, label, start, end):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'test.cpp').write_text(source)
            page = root / 'page.md'
            page.write_text(f'[`{label}`](test.cpp#L{start}-L{end})')
            return list(validator.iter_links(page, root, {}, {}))

    def test_unknown_symbol_is_bounds_only(self):
        self.assertEqual(self.check('void f() {\n work();\n}\n', 'unknown', 1, 3), [])

    def test_function_subrange_is_allowed(self):
        self.assertEqual(self.check('void f() {\n a();\n b();\n c();\n}\n', 'f', 2, 4), [])

    def test_bounds_errors_remain_detected(self):
        found = self.check('void f() {\n a();\n}\n', 'f', 1, 5)
        self.assertEqual(found[0].rule, 'RANGE_OUT_OF_BOUNDS')


if __name__ == '__main__':
    unittest.main()
