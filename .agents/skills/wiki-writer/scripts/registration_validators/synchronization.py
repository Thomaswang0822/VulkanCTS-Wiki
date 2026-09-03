import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple

SYNC_CATEGORIES = ('synchronization', 'synchronization2')
SHARED_WIKI_DIR = 'synchronization'

SYNC2_ONLY_PATTERN = re.compile(r'\(sync2\s+only', re.IGNORECASE)
LEGACY_ONLY_PATTERN = re.compile(r'\(LEGACY\s+only', re.IGNORECASE)


def extract_group_paths(
    wiki_dir: Path,
    category: str,
    get_wiki_candidate_files: Callable[[Path, str], Tuple[Path, List[Path]]],
    extract_canonical_hierarchy_paths: Callable[[Path, str], Dict[str, List[Tuple[Path, int]]]],
) -> Dict[str, List[Tuple[Path, int]]]:
    """
    Extract verifiable paths for synchronization and/or synchronization2.

    These two categories share the same wiki directory (testfiles/synchronization/)
    and the same source directory, but are registered as separate top-level
    categories in the test package. The canonical hierarchy trees in the wiki
    files use the correct root prefix (synchronization.xxx or synchronization2.xxx),
    so we scan the shared directory and extract paths for the requested category.

    Children annotated with (sync2 only) are excluded when validating the
    synchronization category, and children annotated with (LEGACY only) are
    excluded when validating the synchronization2 category.
    """
    paths: Dict[str, List[Tuple[Path, int]]] = {}

    shared_testfiles_dir = wiki_dir / 'testfiles' / SHARED_WIKI_DIR

    candidate_files: List[Path] = []
    for cat in SYNC_CATEGORIES:
        category_doc = wiki_dir / 'categories' / f'{cat}.md'
        if category_doc.exists() and category_doc not in candidate_files:
            candidate_files.append(category_doc)

    if shared_testfiles_dir.exists():
        candidate_files.extend(sorted(shared_testfiles_dir.rglob('*.md')))

    if not candidate_files:
        return paths

    def add_path(md_file: Path, line_num: int, full_path: str) -> None:
        loc = (md_file, line_num)
        if full_path not in paths:
            paths[full_path] = [loc]
        elif loc not in paths[full_path]:
            paths[full_path].append(loc)

    for md_file in candidate_files:
        canonical_paths = extract_canonical_hierarchy_paths(md_file, category)
        for full_path, locs in canonical_paths.items():
            for source_file, line_num in locs:
                if _is_cross_category_child(source_file, line_num, category):
                    continue
                add_path(source_file, line_num, full_path)

    if not paths:
        print(
            f"Error: No canonical '## Registration Hierarchy' data found for category '{category}'. "
            f"Normalize existing wiki files first.",
            file=sys.stderr,
        )
        sys.exit(2)

    return paths


def _is_cross_category_child(md_file: Path, line_num: int, category: str) -> bool:
    """Check if a hierarchy child line is annotated as belonging to the other category."""
    try:
        lines = md_file.read_text(encoding='utf-8').split('\n')
    except Exception:
        return False

    if line_num < 1 or line_num > len(lines):
        return False

    line = lines[line_num - 1]

    if category == 'synchronization' and SYNC2_ONLY_PATTERN.search(line):
        return True

    if category == 'synchronization2' and LEGACY_ONLY_PATTERN.search(line):
        return True

    return False
