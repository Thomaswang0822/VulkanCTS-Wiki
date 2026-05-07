from pathlib import Path
import re
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
) -> Dict[str, List[Tuple[Path, int]]]:
    """
    Extract verifiable pipeline paths.

    Pipeline is structurally special: topic groups such as `blend` and `stencil`
    are registered below construction-variant roots, not directly below
    `pipeline`. This extractor therefore verifies only root variants from the
    category tree and explicit full paths whose first component is a known
    variant root.

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

    variant_pattern = '|'.join(
        re.escape(root) for root in sorted(PIPELINE_VARIANT_ROOTS, key=len, reverse=True)
    )
    full_path_pattern = re.compile(
        rf'`(pipeline\.(?:{variant_pattern})(?:\.[a-zA-Z0-9_.]+)?)`'
    )
    simple_group_pattern = re.compile(r'^[a-z0-9]+(?:_[a-z0-9]+)*$')

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
                    if simple_group_pattern.match(group) and group in PIPELINE_VARIANT_ROOTS:
                        add_path(md_file, line_num, f'pipeline.{group}')

    return paths
