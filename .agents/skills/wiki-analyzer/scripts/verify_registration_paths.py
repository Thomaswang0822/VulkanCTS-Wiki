#!/usr/bin/env python3
"""
Verify literal registration path prefixes against mustpass TXT files.

This script verifies intentionally documented registration path prefixes
against the actual registration paths in the mustpass definition files.
It does not try to prove that every human-facing group label in a wiki
page is a complete registration path. The default wiki extractor is
conservative by design: it extracts explicit category-prefixed paths and
simple root-tree entries, but does not infer paths from arbitrary tables.

MUSTPASS TXT FILE FORMAT:
    The mustpass TXT files contain test names in the format:
        dEQP-VK.{category}.{group_path}.{test_name}

    For example, geometry.txt contains lines like:
        dEQP-VK.geometry.basic.output_10
        dEQP-VK.geometry.input.basic_primitive.points

    When verifying a path like "geometry.basic", the script searches for
    lines starting with "dEQP-VK.geometry.basic." in geometry.txt.

USAGE:
    python verify_registration_paths.py <category> <group_path>
    python verify_registration_paths.py api copy_and_blit.core.blit_image
    python verify_registration_paths.py geometry --check-all

EXIT CODES:
    0 - Path verified successfully
    1 - Path not found in mustpass files
    2 - Error (file not found, etc.)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


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

    variations = [
        f"{category}es.txt",
        f"{hyphenated_category}es.txt",
    ]
    for var in variations:
        add_if_exists(mustpass_dir / var)

    category_dir = mustpass_dir / category
    if category_dir.exists() and category_dir.is_dir():
        for txt_file in sorted(category_dir.glob("*.txt")):
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


def extract_default_group_paths_from_wiki(wiki_dir: Path, category: str) -> Dict[str, List[Tuple[Path, int]]]:
    """
    Extract group paths from wiki markdown files for a regular category.

    Returns dict mapping each unique full_path to a list of (md_file, line_num)
    source locations where it appears.
    """
    paths: Dict[str, List[Tuple[Path, int]]] = {}

    category_doc, candidate_files = get_wiki_candidate_files(wiki_dir, category)
    if not candidate_files:
        return paths

    def add_path(md_file: Path, line_num: int, full_path: str) -> None:
        loc = (md_file, line_num)
        if full_path not in paths:
            paths[full_path] = [loc]
        elif loc not in paths[full_path]:
            paths[full_path].append(loc)

    full_path_pattern = re.compile(rf'`({re.escape(category)}\.(?!txt`)[a-zA-Z0-9_.]+)`')
    simple_group_pattern = re.compile(r'^[a-z0-9]+(?:_[a-z0-9]+)*(?:\.[a-z0-9]+(?:_[a-z0-9]+)*)*$')

    for md_file in candidate_files:
        try:
            lines = md_file.read_text(encoding='utf-8').split('\n')
        except Exception:
            continue

        for line_num, line in enumerate(lines, start=1):
            for match in full_path_pattern.finditer(line):
                add_path(md_file, line_num, match.group(1))

            if md_file == category_doc:
                stripped = line.strip()
                if stripped.startswith('├──') or stripped.startswith('└──'):
                    group = stripped[3:].strip().split()[0]
                    if simple_group_pattern.match(group):
                        add_path(md_file, line_num, f'{category}.{group}')

    return paths


def extract_group_paths_from_wiki(wiki_dir: Path, category: str) -> Dict[str, List[Tuple[Path, int]]]:
    """Dispatch to a category-specific extractor when needed."""
    if category == 'pipeline':
        _scripts_dir = str(Path(__file__).resolve().parent)
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from registration_validators import pipeline
        return pipeline.extract_group_paths(wiki_dir, get_wiki_candidate_files)
    return extract_default_group_paths_from_wiki(wiki_dir, category)


def main():
    parser = argparse.ArgumentParser(description='Verify registration paths in mustpass files')
    parser.add_argument('category', nargs='?', help='Category name (e.g., api, geometry)')
    parser.add_argument('group_path', nargs='?', help='Group path (e.g., copy_and_blit.core.blit_image)')
    parser.add_argument('--mustpass-dir', type=str,
                        default='external/vulkancts/mustpass/main/vk-default',
                        help='Path to mustpass directory')
    parser.add_argument('--repo-root', type=str,
                        default='.',
                        help='Path to repository root')
    parser.add_argument('--wiki-dir', type=str,
                        default='external/vulkancts/wiki',
                        help='Path to wiki directory')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose output')
    parser.add_argument('--check-all', action='store_true',
                        help='Check all paths found in wiki files for the category')

    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    mustpass_dir = (repo_root / args.mustpass_dir).resolve()
    wiki_dir = (repo_root / args.wiki_dir).resolve()

    if not mustpass_dir.exists():
        print(f"Error: Mustpass directory not found: {mustpass_dir}", file=sys.stderr)
        sys.exit(2)

    if args.check_all:
        if not args.category:
            print("Error: --check-all requires a category argument", file=sys.stderr)
            sys.exit(2)

        paths = extract_group_paths_from_wiki(wiki_dir, args.category)
        if not paths:
            print(f"No registration paths found in wiki for category '{args.category}'")
            sys.exit(0)

        print(f"Checking {len(paths)} registration paths...\n")

        failed = 0
        for full_path, sources in paths.items():
            parts = full_path.split('.', 1)
            group_path = parts[1] if len(parts) > 1 else ''

            success, message = verify_registration_path(
                args.category, group_path, mustpass_dir, args.verbose)

            if success:
                print(f"  OK: {full_path}")
                if args.verbose:
                    print(f"      ({message})")
            else:
                primary_md, primary_line = sources[0]
                rel_md = primary_md.relative_to(repo_root)
                print(f"  FAIL: {full_path}")
                print(f"        Source: {rel_md}:{primary_line}")
                if len(sources) > 1:
                    extra = ', '.join(
                        f"{s[0].relative_to(repo_root)}:{s[1]}" for s in sources[1:]
                    )
                    print(f"        Also at: {extra}")
                print(f"        {message}")
                failed += 1

        print()
        if failed > 0:
            print(f"Verification failed: {failed} path(s) not found")
            sys.exit(1)
        else:
            print("All paths verified successfully")
            sys.exit(0)

    else:
        if not args.category:
            print("Error: category argument required", file=sys.stderr)
            parser.print_help()
            sys.exit(2)

        success, message = verify_registration_path(
            args.category, args.group_path or '', mustpass_dir, args.verbose)

        if success:
            print(f"Verified: {message}")
            sys.exit(0)
        else:
            print(f"Verification failed: {message}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
