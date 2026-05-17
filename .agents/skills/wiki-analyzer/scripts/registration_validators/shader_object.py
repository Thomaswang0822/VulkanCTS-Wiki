import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple

MUSTPASS_EXCLUDED_PREFIXES = (
    'shader_object.performance',
)


def extract_group_paths(
    wiki_dir: Path,
    category: str,
    get_wiki_candidate_files: Callable[[Path, str], Tuple[Path, List[Path]]],
    extract_canonical_hierarchy_paths: Callable[[Path, str], Dict[str, List[Tuple[Path, int]]]],
) -> Dict[str, List[Tuple[Path, int]]]:
    """
    Extract verifiable paths for the shader_object category.

    The `performance` branch is source-registered but explicitly excluded from
    mustpass by excluded-tests.txt (glob dEQP-VK.shader_object.performance.*).
    Paths under that branch are omitted from the returned dict so the validator
    does not report false failures.
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

    for md_file in candidate_files:
        canonical_paths = extract_canonical_hierarchy_paths(md_file, category)
        for full_path, locs in canonical_paths.items():
            if any(full_path.startswith(prefix) for prefix in MUSTPASS_EXCLUDED_PREFIXES):
                continue
            for source_file, line_num in locs:
                add_path(source_file, line_num, full_path)

    if not paths:
        print(
            f"Error: No canonical '## Registration Hierarchy' data found for category '{category}'. "
            f"Normalize existing wiki files first.",
            file=sys.stderr,
        )
        sys.exit(2)

    return paths
