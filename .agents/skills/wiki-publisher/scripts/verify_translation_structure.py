#!/usr/bin/env python3
"""Verify structural consistency between an English source wiki page and its
Chinese translation.

This is a sanity check, not a quality check. It compares structural element
counts per markdown section to catch omissions, dropped rows, or missing code
blocks introduced during translation. Passing never means "perfectly
translated"; failing always means "something is structurally wrong".

Usage:
    python3 verify_translation_structure.py \\
        --source external/vulkancts/wiki/testfiles/<category>/<page>.md \\
        --target vkcts-wiki-pages/categories/<category>/<page>.md

Exit codes:
    0 - All structural checks passed
    1 - One or more structural mismatches found
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Lightweight markdown section parser
# ---------------------------------------------------------------------------

@dataclass
class Section:
    """One ## section (or the pre-first-section header) with its structural counts."""
    heading: str = ""
    level: int = 0
    list_items: int = 0
    ordered_list_items: int = 0
    table_rows: int = 0
    table_max_cols: int = 0
    code_blocks: int = 0
    code_languages: List[str] = field(default_factory=list)
    tree_children: int = 0  # ├── and └── lines inside ```text fences


@dataclass
class FileStructure:
    sections: List[Section] = field(default_factory=list)

    def section_by_index(self, idx: int) -> Optional[Section]:
        if 0 <= idx < len(self.sections):
            return self.sections
        return None


def parse_markdown_structure(content: str) -> FileStructure:
    """Parse markdown into a list of sections with structural element counts."""
    lines = content.split('\n')
    structure = FileStructure()

    # Pre-section content (frontmatter, title, etc.) goes into a synthetic section
    current = Section(heading="(header)", level=0)
    structure.sections.append(current)

    in_fence = False
    fence_lang = ""
    current_text_fence = False  # track ```text fences for tree children

    for line in lines:
        stripped = line.strip()

        # Handle code fence boundaries
        if stripped.startswith('```'):
            if not in_fence:
                in_fence = True
                fence_lang = stripped[3:].strip()
                current.code_blocks += 1
                current.code_languages.append(fence_lang)
                current_text_fence = (fence_lang == 'text')
            else:
                in_fence = False
                fence_lang = ""
                current_text_fence = False
            continue

        # Inside code fence: only count tree children in text fences
        if in_fence:
            if current_text_fence:
                if stripped.startswith('├──') or stripped.startswith('└──'):
                    current.tree_children += 1
            continue

        # Section headings (## or deeper, but not inside code)
        if stripped.startswith('#'):
            # Count heading level
            level = 0
            for ch in stripped:
                if ch == '#':
                    level += 1
                else:
                    break
            heading_text = stripped[level:].strip()
            # Only track ## level for section comparison
            if level == 2:
                current = Section(heading=heading_text, level=level)
                structure.sections.append(current)
            continue

        # Table rows (lines with | that are not separator-only)
        if '|' in stripped and not stripped.startswith('```'):
            # Check if it's a separator row like |---|---|
            if re.match(r'^\|[\s:|-]+\|$', stripped):
                continue
            # Count as a table row
            current.table_rows += 1
            # Count columns
            cols = stripped.count('|') - 1  # approximate
            if cols > current.table_max_cols:
                current.table_max_cols = cols
            continue

        # Unordered list items
        if re.match(r'^[-*+]\s', stripped):
            current.list_items += 1
            continue

        # Ordered list items
        if re.match(r'^\d+\.\s', stripped):
            current.ordered_list_items += 1
            continue

    return structure


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------

@dataclass
class Mismatch:
    section_label: str
    check: str
    source_value: int
    target_value: int
    detail: str = ""


def compare_structures(
    source: FileStructure,
    target: FileStructure,
) -> List[Mismatch]:
    """Compare two parsed structures and return a list of mismatches."""
    mismatches: List[Mismatch] = []

    # Match sections by position (## headings)
    # The first section is always the synthetic "(header)"
    source_sections = source.sections
    target_sections = target.sections

    max_sections = max(len(source_sections), len(target_sections))

    for i in range(max_sections):
        src = source_sections[i] if i < len(source_sections) else None
        tgt = target_sections[i] if i < len(target_sections) else None

        if src is None:
            mismatches.append(Mismatch(
                section_label=f"section #{i}",
                check="section_exists",
                source_value=0,
                target_value=1,
                detail=f"Target has extra section: {tgt.heading}" if tgt else "",
            ))
            continue

        if tgt is None:
            mismatches.append(Mismatch(
                section_label=f"section #{i} ({src.heading})",
                check="section_exists",
                source_value=1,
                target_value=0,
                detail=f"Source section missing in target: {src.heading}",
            ))
            continue

        label = f"section #{i} ({src.heading})"

        # Compare list items
        if src.list_items != tgt.list_items:
            mismatches.append(Mismatch(
                section_label=label,
                check="list_items",
                source_value=src.list_items,
                target_value=tgt.list_items,
            ))

        # Compare ordered list items
        if src.ordered_list_items != tgt.ordered_list_items:
            mismatches.append(Mismatch(
                section_label=label,
                check="ordered_list_items",
                source_value=src.ordered_list_items,
                target_value=tgt.ordered_list_items,
            ))

        # Compare table rows
        if src.table_rows != tgt.table_rows:
            mismatches.append(Mismatch(
                section_label=label,
                check="table_rows",
                source_value=src.table_rows,
                target_value=tgt.table_rows,
            ))

        # Compare code blocks
        if src.code_blocks != tgt.code_blocks:
            mismatches.append(Mismatch(
                section_label=label,
                check="code_blocks",
                source_value=src.code_blocks,
                target_value=tgt.code_blocks,
            ))

        # Compare code languages (only if code block count matches)
        if src.code_blocks == tgt.code_blocks:
            for j, (sl, tl) in enumerate(zip(src.code_languages, tgt.code_languages)):
                if sl != tl:
                    mismatches.append(Mismatch(
                        section_label=label,
                        check=f"code_language[{j}]",
                        source_value=0,
                        target_value=0,
                        detail=f"Source fence: '{sl}', target fence: '{tl}'",
                    ))

        # Compare tree children in Registration Hierarchy
        if src.tree_children != tgt.tree_children:
            mismatches.append(Mismatch(
                section_label=label,
                check="tree_children",
                source_value=src.tree_children,
                target_value=tgt.tree_children,
            ))

    return mismatches


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_mismatch(m: Mismatch) -> str:
    parts = [
        f"  {m.section_label}:",
        f"    {m.check}: source={m.source_value}, target={m.target_value}",
    ]
    if m.detail:
        parts.append(f"    {m.detail}")
    return '\n'.join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify structural consistency between source and translated wiki pages."
    )
    parser.add_argument('--source', type=str, required=True,
                        help='Path to the English source markdown file')
    parser.add_argument('--target', type=str, required=True,
                        help='Path to the translated target markdown file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print per-section details even on pass')

    args = parser.parse_args()

    source_path = Path(args.source)
    target_path = Path(args.target)

    if not source_path.is_file():
        print(f"Error: source file not found: {source_path}", file=sys.stderr)
        return 2
    if not target_path.is_file():
        print(f"Error: target file not found: {target_path}", file=sys.stderr)
        return 2

    source_content = source_path.read_text(encoding='utf-8')
    target_content = target_path.read_text(encoding='utf-8')

    source_struct = parse_markdown_structure(source_content)
    target_struct = parse_markdown_structure(target_content)

    mismatches = compare_structures(source_struct, target_struct)

    if args.verbose:
        # Print summary counts
        src_sections = len(source_struct.sections)
        tgt_sections = len(target_struct.sections)
        src_lists = sum(s.list_items for s in source_struct.sections)
        tgt_lists = sum(s.list_items for s in target_struct.sections)
        src_tables = sum(s.table_rows for s in source_struct.sections)
        tgt_tables = sum(s.table_rows for s in target_struct.sections)
        src_code = sum(s.code_blocks for s in source_struct.sections)
        tgt_code = sum(s.code_blocks for s in target_struct.sections)
        print(f"Source: {src_sections} sections, {src_lists} list items, "
              f"{src_tables} table rows, {src_code} code blocks")
        print(f"Target: {tgt_sections} sections, {tgt_lists} list items, "
              f"{tgt_tables} table rows, {tgt_code} code blocks")
        print()

    if mismatches:
        print(f"FAIL: {len(mismatches)} structural mismatch(es) found:\n")
        for m in mismatches:
            print(format_mismatch(m))
        return 1

    print("PASS: structural check passed")
    return 0


if __name__ == '__main__':
    sys.exit(main())
