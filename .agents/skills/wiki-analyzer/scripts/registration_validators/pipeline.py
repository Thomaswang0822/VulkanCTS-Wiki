import re
from pathlib import Path
from typing import Callable, Dict, List, Tuple

PIPELINE_VARIANT_ROOTS = {
    'monolithic',
    'pipeline_library',
    'fast_linked_library',
    'shader_object_unlinked_spirv',
    'shader_object_unlinked_binary',
    'shader_object_linked_spirv',
    'shader_object_linked_binary',
    'no_queues',
}


def extract_group_paths(
    wiki_dir: Path,
    get_wiki_candidate_files: Callable[[Path, str], Tuple[Path, List[Path]]],
    extract_canonical_hierarchy_paths: Callable[[Path, str], Dict[str, List[Tuple[Path, int]]]],
) -> Dict[str, List[Tuple[Path, int]]]:
    """
    Extract verifiable pipeline paths.

    Pipeline is structurally special: topic groups such as `blend` and `stencil`
    are registered below construction-variant roots, not directly below
    `pipeline`. This extractor therefore verifies:

    1. Variant root entries from the category document's tree.
    2. Full paths extracted from canonical ``## Registration Hierarchy`` sections
       in Level-3 wiki pages (post-normalization).

    Returns dict mapping each unique full_path to a list of (md_file, line_num)
    source locations where it appears.
    """
    category = 'pipeline'
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

    simple_group_pattern = re.compile(r'^[a-z0-9]+(?:_[a-z0-9]+)*$')

    if category_doc.exists():
        try:
            lines = category_doc.read_text(encoding='utf-8').split('\n')
        except Exception:
            lines = []

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith('├──') or stripped.startswith('└──'):
                group = stripped[3:].strip().split()[0]
                if simple_group_pattern.match(group) and group in PIPELINE_VARIANT_ROOTS:
                    add_path(category_doc, line_num, f'pipeline.{group}')

    for md_file in candidate_files:
        if md_file == category_doc:
            continue
        canonical_paths = extract_canonical_hierarchy_paths(md_file, category)
        for full_path, locs in canonical_paths.items():
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
