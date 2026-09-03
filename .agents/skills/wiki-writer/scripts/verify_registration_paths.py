#!/usr/bin/env python3
"""
Verify documented registration hierarchy prefixes against mustpass TXT files.

This script verifies registration path prefixes documented in the Vulkan CTS wiki
against the actual registration paths in the mustpass definition files.

For regular categories, the extraction source is the canonical
`## Registration Hierarchy` section in Level-3 wiki pages. The hierarchy contract
is intentionally strict: one `text` fence may contain one or more independent
trees, each beginning with a category-qualified root and expanding exactly one
level below that root. The validator reconstructs full prefixes internally from
the tree set.

This script validates wiki content written to the canonical Level-3 hierarchy
contract.

MUSTPASS TXT FILE FORMAT:
    The mustpass TXT files contain test names in the format:
        dEQP-VK.{category}.{group_path}.{test_name}

    For example, geometry.txt contains lines like:
        dEQP-VK.geometry.basic.output_10
        dEQP-VK.geometry.input.basic_primitive.points

    When verifying a path like "geometry.basic", the script searches for
    lines starting with "dEQP-VK.geometry.basic." in geometry.txt.

USAGE:
    python verify_registration_paths.py <category>
    python verify_registration_paths.py --wiki-file <path-to-level3-md>

    Category mode validates all registration paths extracted from the category
    wiki pages. The legacy --check-all flag is accepted as a no-op alias for
    category mode for compatibility with older workflow notes.

EXIT CODES:
    0 - All paths verified successfully
    1 - One or more paths not found in mustpass files
    2 - Error (file not found, malformed wiki input, etc.)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


CANONICAL_HIERARCHY_HEADING = '## Registration Hierarchy'
PATH_COMPONENT_PATTERN = r'[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*'
TREE_CHILD_PATTERN = re.compile(rf'^(?P<marker>├──|└──)\s+(?P<name>{PATH_COMPONENT_PATTERN}(?:\s*\([^)]*\))?)\s*$')
TRAILING_PAREN_NOTE_PATTERN = re.compile(r'\s*\([^)]*\)\s*$')
SIMPLE_GROUP_PATTERN = re.compile(rf'^{PATH_COMPONENT_PATTERN}(?:\.{PATH_COMPONENT_PATTERN})*$')
TREE_MARKER_PATTERN = re.compile(r'[├└│]')
PLACEHOLDER_PATTERN = re.compile(r'<[^>]+>|\.\.\.')
HIERARCHY_ERRORS: List[Tuple[Path, int, str]] = []


class PrefixTreeNode:
    """One node in the dot-separated mustpass registration prefix tree."""

    __slots__ = ('children', 'first_location')

    def __init__(self) -> None:
        self.children: Dict[str, 'PrefixTreeNode'] = {}
        self.first_location: Optional[Tuple[Path, int]] = None


class MustpassPrefixTree:
    """Index all prefixes from one mustpass TXT file in a single pass."""

    def __init__(self) -> None:
        self.root = PrefixTreeNode()

    def add(self, entry: str, location: Tuple[Path, int]) -> None:
        node = self.root
        for component in entry.split('.'):
            node = node.children.setdefault(component, PrefixTreeNode())
            if node.first_location is None:
                node.first_location = location

    def find(self, path: str) -> Tuple[bool, Optional[Tuple[Path, int]]]:
        node = self.root
        for component in path.split('.'):
            node = node.children.get(component)
            if node is None:
                return False, None
        return True, node.first_location


def build_mustpass_prefix_tree(txt_file: Path) -> MustpassPrefixTree:
    """Build a prefix tree by reading one mustpass file exactly once."""
    tree = MustpassPrefixTree()
    try:
        with open(txt_file, 'r', encoding='utf-8') as handle:
            for line_num, line in enumerate(handle, start=1):
                entry = line.strip()
                if entry.startswith('dEQP-VK.'):
                    tree.add(entry, (txt_file, line_num))
    except Exception as e:
        print(f"Error reading {txt_file}: {e}", file=sys.stderr)
    return tree


def find_mustpass_files(category: str, mustpass_dir: Path) -> List[Path]:
    """
    Find mustpass TXT files for a given category.

    Handles both traditional layouts where category TXT files live directly under
    the mustpass root (for example, `geometry.txt`), categories whose wiki names
    use underscores while mustpass filenames use hyphens (for example,
    `binding_model` -> `binding-model.txt`), and split layouts where a category
    owns a subdirectory of variant TXT files (for example,
    `pipeline/monolithic.txt`, `pipeline/pipeline-library.txt`, etc.).

    Also handles cases where multiple TXT files may correspond to one category
    (e.g., renderpass and renderpasses).
    """
    txt_files: List[Path] = []

    def add_if_exists(path: Path) -> None:
        if path.exists() and path.is_file() and path not in txt_files:
            txt_files.append(path)

    category_variants = [category]
    hyphenated_category = category.replace('_', '-')
    if hyphenated_category != category:
        category_variants.append(hyphenated_category)

    for category_variant in category_variants:
        add_if_exists(mustpass_dir / f"{category_variant}.txt")
        add_if_exists(mustpass_dir / f"{category_variant}s.txt")

    hyphenated_branch_file = mustpass_dir / hyphenated_category / f"{hyphenated_category}.txt"
    add_if_exists(hyphenated_branch_file)
    underscored_branch_file = mustpass_dir / hyphenated_category / f"{category}.txt"
    add_if_exists(underscored_branch_file)

    variations = [
        f"{category}es.txt",
        f"{hyphenated_category}es.txt",
    ]
    for var in variations:
        add_if_exists(mustpass_dir / var)

    category_dir = mustpass_dir / category
    if category_dir.exists() and category_dir.is_dir():
        for txt_file in sorted(category_dir.rglob("*.txt")):
            add_if_exists(txt_file)

    hyphenated_dir = mustpass_dir / hyphenated_category
    if hyphenated_dir.exists() and hyphenated_dir.is_dir():
        for txt_file in sorted(hyphenated_dir.rglob("*.txt")):
            add_if_exists(txt_file)

    return txt_files


def verify_path_in_txt(group_path: str, txt_file: Path) -> Tuple[bool, Optional[int]]:
    """
    Verify that a group path exists in a mustpass TXT file.

    Uses efficient line-by-line search without loading entire file.

    Returns (found, line_number) tuple.
    """
    pattern = re.compile(rf'^{re.escape(group_path)}(\.|$)')

    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                if pattern.match(line.strip()):
                    return (True, line_num)
    except Exception as e:
        print(f"Error reading {txt_file}: {e}", file=sys.stderr)
        return (False, None)

    return (False, None)


def verify_registration_path(category: str, group_path: str,
                             mustpass_dir: Path,
                             prefix_trees: Optional[Dict[Path, MustpassPrefixTree]] = None,
                             txt_files: Optional[Sequence[Path]] = None) -> Tuple[bool, str]:
    """
    Verify a registration path against mustpass files.

    Returns (success, message) tuple.
    """
    if txt_files is None:
        txt_files = find_mustpass_files(category, mustpass_dir)

    if not txt_files:
        return (False, f"No mustpass TXT file found for category '{category}'")

    full_path = f"dEQP-VK.{category}.{group_path}" if group_path else f"dEQP-VK.{category}"

    for txt_file in txt_files:
        if prefix_trees is None:
            found, line_num = verify_path_in_txt(full_path, txt_file)
        else:
            found, location = prefix_trees[txt_file].find(full_path)
            line_num = location[1] if location is not None else None
        if found:
            rel = txt_file.relative_to(mustpass_dir.parent) if mustpass_dir.parent in txt_file.parents else txt_file.name
            return (True, f"Found in {rel}:{line_num}")

    return (False, f"Path '{full_path}' not found in any mustpass file")


def get_wiki_candidate_files(wiki_dir: Path, category: str) -> Tuple[Path, List[Path]]:
    """Return the category document and candidate wiki files for extraction."""
    category_testfiles_dir = wiki_dir / 'testfiles' / category
    category_doc = wiki_dir / 'categories' / f'{category}.md'
    candidate_files: List[Path] = []

    if category_doc.exists():
        candidate_files.append(category_doc)

    if category_testfiles_dir.exists():
        candidate_files.extend(sorted(category_testfiles_dir.rglob('*.md')))

    return category_doc, candidate_files


def strip_trailing_note(node_text: str) -> str:
    """Remove one trailing parenthesized note from a hierarchy node line."""
    return TRAILING_PAREN_NOTE_PATTERN.sub('', node_text).strip()


def extract_canonical_hierarchy_paths(md_file: Path, category: str) -> Dict[str, List[Tuple[Path, int]]]:
    """Extract prefixes from one canonical, single-level hierarchy tree set."""
    paths: Dict[str, List[Tuple[Path, int]]] = {}
    initial_error_count = len(HIERARCHY_ERRORS)

    def add_error(line_num: int, message: str) -> None:
        HIERARCHY_ERRORS.append((md_file, line_num, message))

    def add_path(line_num: int, full_path: str) -> None:
        loc = (md_file, line_num)
        if full_path not in paths:
            paths[full_path] = [loc]
        elif loc not in paths[full_path]:
            paths[full_path].append(loc)

    try:
        lines = md_file.read_text(encoding='utf-8').split('\n')
    except Exception:
        return paths

    heading_index: Optional[int] = None
    for idx, line in enumerate(lines):
        if line.strip() == CANONICAL_HIERARCHY_HEADING:
            heading_index = idx
            break

    if heading_index is None:
        return paths

    section_end = len(lines)
    for idx in range(heading_index + 1, len(lines)):
        if lines[idx].strip().startswith('## '):
            section_end = idx
            break

    fences: List[Tuple[int, int, str]] = []
    idx = heading_index + 1
    while idx < section_end:
        stripped = lines[idx].strip()
        if not stripped.startswith('```'):
            idx += 1
            continue
        fence_start = idx
        fence_language = stripped[3:].strip()
        idx += 1
        while idx < section_end and lines[idx].strip() != '```':
            idx += 1
        if idx >= section_end:
            add_error(fence_start + 1, "Unclosed fenced block in Registration Hierarchy")
            return {}
        fences.append((fence_start, idx, fence_language))
        idx += 1

    if len(fences) != 1 or fences[0][2] != 'text':
        add_error(
            heading_index + 1,
            "Registration Hierarchy must contain exactly one text fenced block with one or more trees",
        )
        return {}

    fence_start, fence_end, _language = fences[0]
    content = [(idx, lines[idx]) for idx in range(fence_start + 1, fence_end)]
    if not any(text.strip() for _idx, text in content):
        add_error(fence_start + 1, "Registration Hierarchy tree must not be empty")
        return {}

    roots: List[Tuple[int, str, List[Tuple[int, str]]]] = []
    current_root: Optional[Tuple[int, str, List[Tuple[int, str]]]] = None
    separated = True

    def finish_tree() -> None:
        nonlocal current_root
        if current_root is not None:
            roots.append(current_root)
            current_root = None

    for line_idx, line in content:
        bare_line = line.strip()
        if not bare_line:
            if current_root is not None:
                separated = True
            continue

        child_match = TREE_CHILD_PATTERN.fullmatch(bare_line)
        if current_root is None:
            current_root = (line_idx, bare_line, [])
            separated = False
            continue

        child_like = bool(
            child_match
            or TREE_MARKER_PATTERN.search(bare_line)
            or PLACEHOLDER_PATTERN.search(bare_line)
            or '#' in bare_line
        )
        if child_like and not separated:
            current_root[2].append((line_idx, bare_line))
            continue

        if child_like:
            add_error(line_idx + 1, "Registration Hierarchy child must follow a tree root")
            continue

        if not separated:
            add_error(line_idx + 1, "Registration Hierarchy trees must be separated by a blank line")
            continue

        finish_tree()
        current_root = (line_idx, bare_line, [])
        separated = False

    finish_tree()

    for root_idx, root_text, children in roots:
        if root_text.startswith('dEQP-VK.'):
            add_error(root_idx + 1, "Registration Hierarchy root must not include the dEQP-VK. package prefix")
            continue
        if not SIMPLE_GROUP_PATTERN.fullmatch(root_text):
            add_error(root_idx + 1, "Registration Hierarchy root must be a concrete category-qualified path")
            continue
        if root_text != category and not root_text.startswith(f'{category}.'):
            add_error(root_idx + 1, f"Registration Hierarchy root must belong to category '{category}'")
            continue

        add_path(root_idx + 1, root_text)
        seen_children: set[str] = set()
        for line_idx, node in children:
            if PLACEHOLDER_PATTERN.search(node):
                add_error(line_idx + 1, "Registration Hierarchy tree must not contain placeholders or ...")
                continue
            if '#' in node:
                add_error(line_idx + 1, "Registration Hierarchy comments must use a trailing parenthesized note, not #")
                continue
            match = TREE_CHILD_PATTERN.fullmatch(node)
            if not match:
                if TREE_MARKER_PATTERN.search(node):
                    add_error(
                        line_idx + 1,
                        "Malformed or nested Registration Hierarchy line; "
                        "only direct children using '├── name' or '└── name' are allowed",
                    )
                else:
                    add_error(line_idx + 1, "Unexpected non-empty line in Registration Hierarchy tree block")
                continue
            child_name = strip_trailing_note(match.group('name'))
            if child_name in seen_children:
                add_error(line_idx + 1, f"duplicate direct child in Registration Hierarchy tree: {child_name}")
                continue
            seen_children.add(child_name)
            add_path(line_idx + 1, f'{root_text}.{child_name}')

    root_names = [root for _line, root, _children in roots]
    for index, root in enumerate(root_names):
        if root_names.count(root) > 1:
            add_error(roots[index][0] + 1, f"duplicate Registration Hierarchy root: {root}")
        for other_index in range(index + 1, len(root_names)):
            other = root_names[other_index]
            if root.startswith(f'{other}.') or other.startswith(f'{root}.'):
                add_error(
                    roots[index][0] + 1,
                    f"Registration Hierarchy roots must not overlap as ancestor and descendant: {root}, {other}",
                )

    if len(HIERARCHY_ERRORS) != initial_error_count:
        return {}
    return paths


def extract_default_group_paths_from_wiki(wiki_dir: Path, category: str) -> Dict[str, List[Tuple[Path, int]]]:
    """
    Extract group paths from wiki markdown files for a regular category.

    Returns dict mapping each unique full_path to a list of (md_file, line_num)
    source locations where it appears.
    """
    paths: Dict[str, List[Tuple[Path, int]]] = {}

    _category_doc, candidate_files = get_wiki_candidate_files(wiki_dir, category)
    if not candidate_files:
        return paths

    def add_path(md_file: Path, line_num: int, full_path: str) -> None:
        loc = (md_file, line_num)
        if full_path not in paths:
            paths[full_path] = [loc]
        elif loc not in paths[full_path]:
            paths[full_path].append(loc)

    canonical_found = False

    for md_file in candidate_files:
        canonical_paths = extract_canonical_hierarchy_paths(md_file, category)
        if canonical_paths:
            canonical_found = True
            for full_path, locs in canonical_paths.items():
                for source_file, line_num in locs:
                    add_path(source_file, line_num, full_path)

    if canonical_found:
        return paths

    print(
        f"Error: No canonical '## Registration Hierarchy' data found for category '{category}'. "
        f"Normalize existing wiki files first.",
        file=sys.stderr,
    )
    sys.exit(2)


def extract_group_paths_from_wiki(wiki_dir: Path, category: str) -> Dict[str, List[Tuple[Path, int]]]:
    """Dispatch to a category-specific extractor when needed."""
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)

    if category == 'pipeline':
        from registration_validators import pipeline
        return pipeline.extract_group_paths(
            wiki_dir, get_wiki_candidate_files, extract_canonical_hierarchy_paths)

    if category in ('synchronization', 'synchronization2'):
        from registration_validators import synchronization
        return synchronization.extract_group_paths(
            wiki_dir, category, get_wiki_candidate_files, extract_canonical_hierarchy_paths)

    if category == 'shader_object':
        from registration_validators import shader_object
        return shader_object.extract_group_paths(
            wiki_dir, category, get_wiki_candidate_files, extract_canonical_hierarchy_paths)

    return extract_default_group_paths_from_wiki(wiki_dir, category)


def validate_paths(paths: Dict[str, List[Tuple[Path, int]]],
                    category: str, mustpass_dir: Path) -> int:
    """Validate paths and print compact results grouped by documenting page."""
    txt_files = find_mustpass_files(category, mustpass_dir)
    prefix_trees = {
        txt_file: build_mustpass_prefix_tree(txt_file)
        for txt_file in txt_files
    }

    loaded_files = [
        str(txt_file.relative_to(mustpass_dir.parent))
        if mustpass_dir.parent in txt_file.parents
        else txt_file.name
        for txt_file in txt_files
    ]
    if len(loaded_files) == 1:
        print(f"Loaded mustpass file: {loaded_files[0]}")
    else:
        print("Loaded mustpass files: [")
        for loaded_file in loaded_files:
            print(f"     {loaded_file}")
        print("]")

    pages = {
        md_file
        for sources in paths.values()
        for md_file, _line_num in sources
    }
    findings_by_page: Dict[Path, List[str]] = {}

    seen_hierarchy_errors = set()
    for md_file, line_num, message in HIERARCHY_ERRORS:
        error_key = (md_file, line_num, message)
        if error_key in seen_hierarchy_errors:
            continue
        seen_hierarchy_errors.add(error_key)
        pages.add(md_file)
        findings_by_page.setdefault(md_file, []).append(
            f"line {line_num}: {message}"
        )

    for full_path, sources in paths.items():
        parts = full_path.split('.', 1)
        group_path = parts[1] if len(parts) > 1 else ''

        success, message = verify_registration_path(
            category,
            group_path,
            mustpass_dir,
            prefix_trees,
            txt_files,
        )

        if not success:
            for md_file, line_num in sources:
                findings_by_page.setdefault(md_file, []).append(
                    f"{full_path}:{line_num}: {message}"
                )

    for md_file in sorted(pages, key=lambda path: (path.name, str(path))):
        findings = findings_by_page.get(md_file, [])
        if not findings:
            print(f"PASS {md_file.name}")
            continue
        print(f"FAIL {md_file.name}")
        for finding in findings:
            print(f"     - {finding}")

    return sum(len(findings) for findings in findings_by_page.values())


def main():
    parser = argparse.ArgumentParser(description='Verify registration paths in mustpass files')
    parser.add_argument('category', nargs='?', help='Category name (e.g., api, geometry)')
    parser.add_argument('--wiki-file', type=str,
                        help='Path to a single Level-3 wiki file to validate')
    parser.add_argument('--mustpass-dir', type=str,
                        default='external/vulkancts/mustpass/main/vk-default',
                        help='Path to mustpass directory')
    parser.add_argument('--wiki-dir', type=str,
                        default='external/vulkancts/wiki',
                        help='Path to wiki directory')
    parser.add_argument('--check-all', action='store_true',
                        help='Deprecated no-op; category mode already validates all extracted paths')

    args = parser.parse_args()

    mustpass_dir = (Path.cwd() / args.mustpass_dir).resolve()
    wiki_dir = (Path.cwd() / args.wiki_dir).resolve()

    if not mustpass_dir.exists():
        print(f"Error: Mustpass directory not found: {mustpass_dir}", file=sys.stderr)
        sys.exit(2)

    if args.wiki_file:
        wiki_file = Path(args.wiki_file)
        if not wiki_file.is_absolute():
            wiki_file = (Path.cwd() / wiki_file).resolve()
        if not wiki_file.exists():
            print(f"Error: Wiki file not found: {wiki_file}", file=sys.stderr)
            sys.exit(2)

        category = wiki_file.parent.name

        HIERARCHY_ERRORS.clear()
        paths = extract_canonical_hierarchy_paths(wiki_file, category)
        if not paths:
            print(f"No canonical hierarchy data found in {wiki_file}", file=sys.stderr)
            sys.exit(2)

        category_dir = wiki_dir / 'testfiles' / category
        try:
            display_dir = category_dir.relative_to(Path.cwd())
        except ValueError:
            display_dir = category_dir
        print(f"Collected {len(paths)} paths from {display_dir}")

        failed = validate_paths(paths, category, mustpass_dir)

        print()
        if failed > 0:
            print(f"Verification failed: {failed} hierarchy or path issue(s) found")
            sys.exit(1)
        else:
            print("All paths verified successfully")
            sys.exit(0)

    elif args.category:
        HIERARCHY_ERRORS.clear()
        paths = extract_group_paths_from_wiki(wiki_dir, args.category)
        if not paths:
            print(f"No registration paths found in wiki for category '{args.category}'")
            sys.exit(0)

        category_dir = wiki_dir / 'testfiles' / args.category
        try:
            display_dir = category_dir.relative_to(Path.cwd())
        except ValueError:
            display_dir = category_dir
        print(f"Collected {len(paths)} paths from {display_dir}")

        failed = validate_paths(paths, args.category, mustpass_dir)

        print()
        if failed > 0:
            print(f"Verification failed: {failed} hierarchy or path issue(s) found")
            sys.exit(1)
        else:
            print("All paths verified successfully")
            sys.exit(0)

    else:
        print("Error: provide a category argument or --wiki-file", file=sys.stderr)
        parser.print_help()
        sys.exit(2)


if __name__ == '__main__':
    main()
