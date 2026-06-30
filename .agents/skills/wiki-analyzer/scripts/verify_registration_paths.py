#!/usr/bin/env python3
"""
Verify documented registration hierarchy prefixes against mustpass TXT files.

This script verifies registration path prefixes documented in the Vulkan CTS wiki
against the actual registration paths in the mustpass definition files.

For regular categories, the extraction source is the canonical
`## Registration Hierarchy` section in Level-3 wiki pages. The hierarchy contract
is intentionally strict: the tree root is a category-qualified Level-3 root path
and the tree expands exactly one level below that root. The validator reconstructs
full prefixes internally from that tree.

This script is intended for post-normalization wiki content. Existing legacy wiki
files are expected to work with the validator after they have been normalized to
that canonical Level-3 contract.

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
from typing import Dict, List, Optional, Tuple


CANONICAL_HIERARCHY_HEADING = '## Registration Hierarchy'
PATH_COMPONENT_PATTERN = r'[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*'
TREE_CHILD_PATTERN = re.compile(rf'^(?P<marker>├──|└──)\s+(?P<name>{PATH_COMPONENT_PATTERN}(?:\s*\([^)]*\))?)\s*$')
TRAILING_PAREN_NOTE_PATTERN = re.compile(r'\s*\([^)]*\)\s*$')
SIMPLE_GROUP_PATTERN = re.compile(rf'^{PATH_COMPONENT_PATTERN}(?:\.{PATH_COMPONENT_PATTERN})*$')
TREE_MARKER_PATTERN = re.compile(r'[├└│]')
HIERARCHY_ERRORS: List[Tuple[Path, int, str]] = []


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
                             mustpass_dir: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Verify a registration path against mustpass files.

    Returns (success, message) tuple.
    """
    txt_files = find_mustpass_files(category, mustpass_dir)

    if not txt_files:
        return (False, f"No mustpass TXT file found for category '{category}'")

    if verbose:
        print(
            f"Checking mustpass files: "
            f"{[str(f.relative_to(mustpass_dir.parent)) if mustpass_dir.parent in f.parents else str(f.name) for f in txt_files]}"
        )

    full_path = f"dEQP-VK.{category}.{group_path}" if group_path else f"dEQP-VK.{category}"

    for txt_file in txt_files:
        found, line_num = verify_path_in_txt(full_path, txt_file)
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
    """Extract full registration prefixes from a canonical Registration Hierarchy section."""
    paths: Dict[str, List[Tuple[Path, int]]] = {}

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

    fence_start: Optional[int] = None
    for idx in range(heading_index + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith('## '):
            return paths
        if stripped == '```text':
            fence_start = idx
            break

    if fence_start is None:
        return paths

    fence_end: Optional[int] = None
    for idx in range(fence_start + 1, len(lines)):
        if lines[idx].strip() == '```':
            fence_end = idx
            break

    if fence_end is None or fence_end <= fence_start + 1:
        return paths

    root_line_num = fence_start + 2
    root_text = lines[fence_start + 1].strip()
    if (root_text == category or root_text.startswith(f'{category}.')) and SIMPLE_GROUP_PATTERN.match(root_text):
        add_path(root_line_num, root_text)
    else:
        return paths

    for idx in range(fence_start + 2, fence_end):
        stripped = lines[idx].rstrip()
        if not stripped.strip():
            continue

        # Support multiple roots in a single fence block: a bare line that
        # matches the category-qualified group pattern becomes the new root.
        bare_line = stripped.strip()
        if (bare_line == category or bare_line.startswith(f'{category}.')) and SIMPLE_GROUP_PATTERN.match(bare_line):
            root_text = bare_line
            add_path(idx + 1, root_text)
            continue

        match = TREE_CHILD_PATTERN.match(bare_line)
        if not match:
            if TREE_MARKER_PATTERN.search(bare_line):
                add_error(
                    idx + 1,
                    "Malformed or nested Registration Hierarchy line; "
                    "only direct children using '├── name' or '└── name' are allowed")
            else:
                add_error(idx + 1, "Unexpected non-empty line in Registration Hierarchy tree block")
            continue

        child_name = strip_trailing_note(match.group('name'))
        if not child_name or not re.fullmatch(PATH_COMPONENT_PATTERN, child_name):
            add_error(idx + 1, "Invalid Registration Hierarchy child name")
            continue

        add_path(idx + 1, f'{root_text}.{child_name}')

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
                    category: str, mustpass_dir: Path, verbose: bool = False) -> int:
    """Validate extracted paths against mustpass files. Returns number of failures."""
    failed = 0

    malformed_files = set()
    for md_file, line_num, _message in HIERARCHY_ERRORS:
        if md_file in malformed_files:
            continue
        malformed_files.add(md_file)
        try:
            rel_md = md_file.relative_to(Path.cwd())
        except ValueError:
            rel_md = md_file
        print("  FAIL: malformed or nested Registration Hierarchy line; "
              "only direct children using '├── name' or '└── name' are allowed")
        print(f"        Source: {rel_md}:{line_num}")
        failed += 1

    for full_path, sources in paths.items():
        parts = full_path.split('.', 1)
        group_path = parts[1] if len(parts) > 1 else ''

        success, message = verify_registration_path(
            category, group_path, mustpass_dir, verbose)

        if success:
            print(f"  OK: {full_path}")
            if verbose:
                print(f"      ({message})")
        else:
            primary_md, primary_line = sources[0]
            try:
                rel_md = primary_md.relative_to(Path.cwd())
            except ValueError:
                rel_md = primary_md
            print(f"  FAIL: {full_path}")
            print(f"        Source: {rel_md}:{primary_line}")
            if len(sources) > 1:
                extra = ', '.join(
                    f"{s[0].relative_to(Path.cwd())}:{s[1]}" for s in sources[1:]
                )
                print(f"        Also at: {extra}")
            print(f"        {message}")
            failed += 1

    return failed


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
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose output')
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

        print(f"Checking {len(paths)} registration paths from {wiki_file.name}...\n")

        failed = validate_paths(paths, category, mustpass_dir, args.verbose)

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

        print(f"Checking {len(paths)} registration paths...\n")

        failed = validate_paths(paths, args.category, mustpass_dir, args.verbose)

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
