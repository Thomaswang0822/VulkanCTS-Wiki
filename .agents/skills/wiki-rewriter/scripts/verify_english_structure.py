#!/usr/bin/env python3
"""Mechanically validate canonical English Level-3 Wiki page structure.

This is a structural guard, not a semantic or source-backed audit. It checks the
page-level section and heading contract from ``references/level3-template.md``.
Registration Hierarchy tree semantics are owned by ``verify_registration_paths.py``.

Exit codes:
    0 - all selected pages passed
    1 - one or more structural issues were found
    2 - invocation or input error
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from walkthrough_exceptions import PAGES_WITHOUT_WALKTHROUGH


REQUIRED_SECTIONS = (
    "Overview",
    "Background Knowledge",
    "Registration Hierarchy",
    "Behavior Parameters",
    "Shader Analysis",
    "Runtime Execution and Result Checking",
    "Failure Meaning",
    "Case Pruning",
    "Key Takeaways",
    "Source Reference Appendix",
)
OPTIONAL_SECTIONS = ("Parameter Dimensions and Observed Values",)
CANONICAL_SECTION_ORDER = (
    "Overview",
    "Background Knowledge",
    "Registration Hierarchy",
    "Parameter Dimensions and Observed Values",
    "Behavior Parameters",
    "Shader Analysis",
    "Runtime Execution and Result Checking",
    "Failure Meaning",
    "Case Pruning",
    "Key Takeaways",
    "Source Reference Appendix",
)
ALLOWED_SECTIONS = frozenset(CANONICAL_SECTION_ORDER)
FAILURE_SUBSECTIONS = ("Failure Cause Mapping", "Cause Analysis")
PRUNING_SUBSECTIONS = ("Requirement-based pruning", "Design-based pruning")
WALKTHROUGH_PREFIX = "Representative Shader Walkthrough"
WALKTHROUGH_RE = re.compile(r"^Representative Shader Walkthrough (?P<number>[1-3])$")
WALKTHROUGH_SUBSECTIONS = (
    "Parameter Values Chosen",
    "Purpose",
    "Structural Design",
    "Shader Code",
    "Additional Info",
    "Parameter Variation Summary",
    "SPIR-V",
)
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+\S")
TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")
SPIRV_METADATA_LABELS = (
    "Status",
    "Source",
    "Stage",
    "Target SPIRV version",
)


@dataclass(frozen=True)
class Heading:
    line: int
    level: int
    title: str


@dataclass(frozen=True)
class Fence:
    start: int
    end: int
    language: str
    lines: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    rule: str
    message: str


def _issue(path: Path, line: int, rule: str, message: str) -> Issue:
    return Issue(path=path, line=line, rule=rule, message=message)


def _parse_headings_and_fences(
    path: Path, lines: Sequence[str]
) -> tuple[list[Heading], list[Fence], list[Issue]]:
    headings: list[Heading] = []
    fences: list[Fence] = []
    issues: list[Issue] = []
    fence_start: int | None = None
    fence_language = ""
    fence_lines: list[tuple[int, str]] = []

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if fence_start is None:
                fence_start = line_number
                fence_language = stripped[3:].strip()
                fence_lines = []
            elif stripped == "```":
                fences.append(
                    Fence(
                        start=fence_start,
                        end=line_number,
                        language=fence_language,
                        lines=tuple(fence_lines),
                    )
                )
                fence_start = None
                fence_language = ""
                fence_lines = []
            else:
                issues.append(
                    _issue(
                        path,
                        line_number,
                        "code-fence",
                        "a fenced block must close with exactly ```",
                    )
                )
            continue

        if fence_start is not None:
            fence_lines.append((line_number, line))
            continue

        match = HEADING_RE.match(line)
        if match:
            headings.append(
                Heading(
                    line=line_number,
                    level=len(match.group("marks")),
                    title=match.group("title"),
                )
            )

    if fence_start is not None:
        issues.append(
            _issue(path, fence_start, "code-fence", "unclosed fenced code block")
        )

    return headings, fences, issues


def _validate_heading_spacing(
    path: Path, lines: Sequence[str], headings: Sequence[Heading]
) -> list[Issue]:
    """Enforce the repository's markdownlint-style blank line before headings."""
    issues: list[Issue] = []
    for heading in headings:
        # A heading at the beginning of the file has no preceding line to check.
        if heading.line == 1:
            continue

        blank_count = 0
        cursor = heading.line - 2
        while cursor >= 0 and not lines[cursor].strip():
            blank_count += 1
            cursor -= 1
        if blank_count != 1:
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "heading-spacing",
                    f"{heading.level * '#'} {heading.title} must be preceded by exactly one blank line; found {blank_count}",
                )
            )
    return issues


def _section_bounds(
    heading: Heading, h2_headings: Sequence[Heading], line_count: int
) -> tuple[int, int]:
    index = h2_headings.index(heading)
    end = h2_headings[index + 1].line - 1 if index + 1 < len(h2_headings) else line_count
    return heading.line, end


def _headings_inside(
    headings: Iterable[Heading], start: int, end: int, level: int
) -> list[Heading]:
    return [h for h in headings if h.level == level and start < h.line <= end]


def _heading_end(heading: Heading, headings: Sequence[Heading], fallback_end: int) -> int:
    """Return the line before the next heading at the same or higher level."""
    following = [
        candidate
        for candidate in headings
        if candidate.line > heading.line and candidate.level <= heading.level
    ]
    return min((candidate.line for candidate in following), default=fallback_end + 1) - 1


def _fences_inside(fences: Sequence[Fence], start: int, end: int) -> list[Fence]:
    return [fence for fence in fences if start < fence.start and fence.end <= end]


def _nonblank_body_lines(lines: Sequence[str], start: int, end: int) -> list[str]:
    return [line for line in lines[start:end] if line.strip()]


def _table_rows(lines: Sequence[str], start: int, end: int) -> list[tuple[int, list[str]]]:
    """Return simple pipe-table rows whose next row is a Markdown separator."""
    rows: list[tuple[int, list[str]]] = []

    def cells(line: str) -> list[str]:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            return []
        return [cell.strip() for cell in stripped[1:-1].split("|")]

    index = start
    while index + 1 < end:
        header = cells(lines[index])
        separator = cells(lines[index + 1])
        if (
            header
            and len(header) == len(separator)
            and all(TABLE_SEPARATOR_CELL_RE.fullmatch(cell) for cell in separator)
        ):
            table: list[tuple[int, list[str]]] = [(index + 1, header)]
            cursor = index + 2
            while cursor < end:
                row = cells(lines[cursor])
                if len(row) != len(header):
                    break
                table.append((cursor + 1, row))
                cursor += 1
            return table
        index += 1
    return rows


def _normalized_stage_label(title: str) -> str:
    label = re.sub(r"\bSPIR-V\b", "", title, flags=re.IGNORECASE)
    label = re.sub(r"\bShader\b", "", label, flags=re.IGNORECASE)
    return " ".join(label.casefold().split())


def _shader_stage_key(title: str) -> str:
    """Normalize stage-role wording without treating source/artifact labels as stages."""
    value = title.casefold()
    if (
        "ray generation" in value
        or "ray-generation" in value
        or "raygen" in value
        or "rgen" in value
        or "wr-asb" in value
    ):
        return "rgen"
    if "callable" in value:
        return "callable"
    if "any-hit" in value or "any hit" in value or "ahit" in value:
        return "any-hit"
    if "closest-hit" in value or "closest hit" in value or "chit" in value:
        return "closest-hit"
    if "intersection" in value or "isec" in value or "rint" in value:
        return "intersection"
    if "miss" in value or "rmiss" in value:
        return "miss"
    if "vertex" in value or re.search(r"\bvert\b", value):
        return "vertex"
    if "fragment" in value or re.search(r"\bfrag\b", value):
        return "fragment"
    if "compute" in value or re.search(r"\bcomp\b", value):
        return "compute"
    if "producer" in value and re.search(r"\bcomp\d*\b", value):
        return "compute"
    if "consumer" in value and re.search(r"\bcomp\d*\b", value):
        return "compute"
    if "tessellation control" in value or "tess control" in value or re.search(r"\btesc\b", value):
        return "tessellation-control"
    if "tessellation evaluation" in value or "tess evaluation" in value or re.search(r"\btese\b", value):
        return "tessellation-evaluation"
    if "geometry" in value or re.search(r"\bgeom\b", value):
        return "geometry"
    if "pixel" in value or "fragment" in value:
        return "fragment"
    return ""


def _validate_walkthrough_content_structure(
    path: Path,
    lines: Sequence[str],
    headings: Sequence[Heading],
    fences: Sequence[Fence],
    walkthrough: Heading,
    walkthrough_end: int,
    subsections: Sequence[Heading],
) -> list[Issue]:
    """Validate template shapes without judging shader meaning or prose quality."""
    issues: list[Issue] = []
    subsection_map = {heading.title: heading for heading in subsections}
    bounds = {
        title: (
            heading.line,
            _heading_end(heading, headings, walkthrough_end),
        )
        for title, heading in subsection_map.items()
    }

    if subsections and any(
        line.strip()
        for line in lines[walkthrough.line : subsections[0].line - 1]
    ):
        issues.append(
            _issue(
                path,
                subsections[0].line,
                "shader-walkthrough-first-subsection",
                "the walkthrough H3 must be followed directly by #### Parameter Values Chosen, separated only by blank lines",
            )
        )

    # Every canonical subsection except Additional Info must carry content. The
    # template explicitly allows Additional Info to be empty rather than padded.
    for title in WALKTHROUGH_SUBSECTIONS:
        if title == "Additional Info" or title not in bounds:
            continue
        heading = subsection_map[title]
        body = _nonblank_body_lines(lines, *bounds[title])
        if not body:
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "shader-walkthrough-empty-subsection",
                    f"#### {title} must not be empty",
                )
            )

    parameters = subsection_map.get("Parameter Values Chosen")
    if parameters is not None:
        parameter_start, parameter_end = bounds[parameters.title]
        parameter_block = "\n".join(lines[parameter_start:parameter_end])
        path_fences = [
            fence
            for fence in _fences_inside(fences, parameter_start, parameter_end)
            if fence.language == "text"
            and any(line.strip().startswith("dEQP-VK.") for _, line in fence.lines)
        ]
        if "Representative path:" not in parameter_block or len(path_fences) != 1:
            issues.append(
                _issue(
                    path,
                    parameters.line,
                    "shader-walkthrough-parameter-path",
                    "#### Parameter Values Chosen must contain Representative path: followed by exactly one ```text dEQP-VK... path block",
                )
            )
        table = _table_rows(lines, parameter_start, parameter_end)
        expected_header = [
            "Parameter choice",
            "Meaning in this representative case",
        ]
        if not table or table[0][1] != expected_header or len(table) < 2:
            issues.append(
                _issue(
                    path,
                    parameters.line,
                    "shader-walkthrough-parameter-table",
                    "#### Parameter Values Chosen must contain the canonical two-column parameter table with at least one data row",
                )
            )

    structural = subsection_map.get("Structural Design")
    if structural is not None:
        structural_start, structural_end = bounds[structural.title]
        has_table = bool(_table_rows(lines, structural_start, structural_end))
        has_mermaid = any(
            fence.language == "mermaid"
            for fence in _fences_inside(fences, structural_start, structural_end)
        )
        has_list = any(
            LIST_ITEM_RE.match(line)
            for line in lines[structural_start:structural_end]
        )
        if not (has_table or has_mermaid or has_list):
            issues.append(
                _issue(
                    path,
                    structural.line,
                    "shader-walkthrough-structural-design-format",
                    "#### Structural Design must use a table, Mermaid block, or Markdown list rather than plain text only",
                )
            )

    shader_code = subsection_map.get("Shader Code")
    source_fences: list[Fence] = []
    direct_spirv_marker = False
    if shader_code is not None:
        code_start, code_end = bounds[shader_code.title]
        code_fences = _fences_inside(fences, code_start, code_end)
        source_fences = [fence for fence in code_fences if fence.language in {"glsl", "hlsl"}]
        llvm_fences = [fence for fence in code_fences if fence.language == "llvm"]
        code_block = "\n".join(lines[code_start:code_end])
        direct_spirv_marker = (
            "SPIR-V" in code_block
            and "GLSL" in code_block
            and "HLSL" in code_block
            and re.search(
                r"\b(?:no|not|without|rather than|does not|isn't|is not)\b",
                code_block,
                re.IGNORECASE,
            )
            is not None
        )
        if llvm_fences:
            issues.append(
                _issue(
                    path,
                    llvm_fences[0].start,
                    "shader-walkthrough-shader-code-assembly",
                    "#### Shader Code must not contain SPIR-V assembly; place complete assembly in the final #### SPIR-V subsection",
                )
            )
        if not source_fences and not direct_spirv_marker:
            issues.append(
                _issue(
                    path,
                    shader_code.line,
                    "shader-walkthrough-shader-code-format",
                    "#### Shader Code must contain GLSL/HLSL source fences or explicitly state that the direct-SPIR-V case does not use GLSL or HLSL",
                )
            )
        if source_fences and any(
            not any(line.strip() for _, line in fence.lines) for fence in source_fences
        ):
            issues.append(
                _issue(
                    path,
                    shader_code.line,
                    "shader-walkthrough-shader-code-empty",
                    "GLSL/HLSL source fences in #### Shader Code must be non-empty",
                )
            )

    additional = subsection_map.get("Additional Info")
    if additional is not None:
        additional_start, additional_end = bounds[additional.title]
        body = _nonblank_body_lines(lines, additional_start, additional_end)
        bullets = [line for line in body if LIST_ITEM_RE.match(line)]
        if body and not bullets:
            issues.append(
                _issue(
                    path,
                    additional.line,
                    "shader-walkthrough-additional-info-format",
                    "non-empty #### Additional Info must use Markdown list items",
                )
            )

    variations = subsection_map.get("Parameter Variation Summary")
    if variations is not None:
        variation_start, variation_end = bounds[variations.title]
        table = _table_rows(lines, variation_start, variation_end)
        expected_header = [
            "Parameter dimension",
            "Shader-level variation from this shader",
            "Evidence",
        ]
        if not table or table[0][1] != expected_header or len(table) < 2:
            issues.append(
                _issue(
                    path,
                    variations.line,
                    "shader-walkthrough-variation-table",
                    "#### Parameter Variation Summary must contain the canonical three-column table with at least one data row",
                )
            )
        elif any(not MARKDOWN_LINK_RE.search(row[2]) for _, row in table[1:]):
            issues.append(
                _issue(
                    path,
                    table[1][0],
                    "shader-walkthrough-variation-evidence",
                    "every Parameter Variation Summary data row must contain a Markdown source link in Evidence",
                )
            )

    spirv = subsection_map.get("SPIR-V")
    if spirv is not None:
        spirv_start, spirv_end = bounds[spirv.title]
        spirv_block = "\n".join(lines[spirv_start:spirv_end])
        spirv_fences = [
            fence
            for fence in _fences_inside(fences, spirv_start, spirv_end)
            if fence.language == "llvm"
        ]
        if spirv_fences:
            for fence in spirv_fences:
                assembly_lines = [line for _, line in fence.lines]
                if (
                    not assembly_lines
                    or assembly_lines[0].strip() != "; SPIR-V"
                    or not any(
                        re.fullmatch(r"; Version: 1\.[0-6]", line.strip())
                        for line in assembly_lines[:5]
                    )
                ):
                    issues.append(
                        _issue(
                            path,
                            fence.start,
                            "shader-walkthrough-spirv-header",
                            "each llvm artifact must begin with the canonical spirv-dis '; SPIR-V' and '; Version: 1.x' header",
                        )
                    )
            details_count = len(re.findall(r"^<details>\s*$", spirv_block, re.MULTILINE))
            closing_count = len(re.findall(r"^</details>\s*$", spirv_block, re.MULTILINE))
            summary_count = len(
                re.findall(
                    r"^<summary>Click to expand SPIRV asm code</summary>\s*$",
                    spirv_block,
                    re.MULTILINE,
                )
            )
            if not (
                details_count == closing_count == summary_count == len(spirv_fences)
            ):
                issues.append(
                    _issue(
                        path,
                        spirv.line,
                        "shader-walkthrough-spirv-details",
                        "each SPIR-V llvm block must have one canonical collapsed <details> wrapper and summary",
                    )
                )
            for label in SPIRV_METADATA_LABELS:
                if len(re.findall(rf"^- {re.escape(label)}:\s*\S", spirv_block, re.MULTILINE)) != len(spirv_fences):
                    issues.append(
                        _issue(
                            path,
                            spirv.line,
                            "shader-walkthrough-spirv-metadata",
                            f"each SPIR-V artifact must contain exactly one '- {label}:' metadata line",
                        )
                    )

        # The newly agreed multi-shader rule is intentionally implemented here
        # only, not written into shader-analyzer's skill definition yet.
        code_h5 = []
        spirv_h5 = []
        if shader_code is not None:
            code_start, code_end = bounds[shader_code.title]
            code_h5 = _headings_inside(headings, code_start, code_end, 5)
        spirv_h5 = _headings_inside(headings, spirv_start, spirv_end, 5)
        if len(source_fences) > 1 or len(spirv_fences) > 1 or code_h5 or spirv_h5:
            code_labels = [_normalized_stage_label(heading.title) for heading in code_h5]
            spirv_labels = [_normalized_stage_label(heading.title) for heading in spirv_h5]
            code_stage_keys = [_shader_stage_key(heading.title) for heading in code_h5]
            spirv_stage_keys = [_shader_stage_key(heading.title) for heading in spirv_h5]
            ordinary_mismatch = (
                len(code_h5) < 1
                or len(spirv_h5) < 1
                or any(not key for key in code_stage_keys)
                or any(not key for key in spirv_stage_keys)
                or any(key not in code_stage_keys for key in spirv_stage_keys)
                or spirv_stage_keys != [key for key in code_stage_keys if key in spirv_stage_keys]
                or len(spirv_h5) != len(spirv_fences)
                or len(code_h5) != len(source_fences)
            )
            # When both sections contain the same ordered, stage-qualified
            # artifact list, the labels are valid even if prose/source uses a
            # different descriptive spelling for a stage.
            canonical_full_pair_ok = (
                len(code_h5) == len(source_fences) == len(spirv_h5) == len(spirv_fences)
                and code_stage_keys == spirv_stage_keys
                and all(code_stage_keys)
            )
            # A single SPIR-V artifact may be a source-backed representative
            # subset of a multi-stage source walkthrough. Its H5 must still
            # match the artifact's declared stage, while source H5s remain
            # independently checked for meaningful stage roles.
            direct_single_stage_ok = (
                len(spirv_h5) == len(spirv_fences) == 1
                and len(spirv_stage_keys) == 1
                and bool(spirv_stage_keys[0])
                and spirv_stage_keys[0] in code_stage_keys
            )
            # A mixed-source walkthrough may pair ordinary GLSL/HLSL stages
            # with a CTS-authored direct-SPIR-V stage.  The direct stage has an
            # explanatory H5 under Shader Code rather than a source fence, and
            # only that stage needs a matching SPIR-V artifact.  Keep the
            # direct-stage labels in source order and require every SPIR-V H5
            # to correspond to one of the Shader Code H5 labels.
            mixed_direct_selective_ok = (
                bool(spirv_h5)
                and len(spirv_h5) == len(spirv_fences)
                and len(code_h5) == len(source_fences) + len(spirv_h5)
                and all(key and key in code_stage_keys for key in spirv_stage_keys)
                and spirv_stage_keys == [key for key in code_stage_keys if key in spirv_stage_keys]
            )
            mixed_direct_full_ok = (
                spirv_stage_keys == [key for key in code_stage_keys if key in spirv_stage_keys]
                and len(spirv_h5) == len(spirv_fences)
            )
            mixed_direct_mismatch = (
                len(code_h5) < 1
                or not (mixed_direct_selective_ok or mixed_direct_full_ok)
            )
            if (direct_spirv_marker and mixed_direct_mismatch) or (
                not direct_spirv_marker
                and ordinary_mismatch
                and not direct_single_stage_ok
                and not canonical_full_pair_ok
            ):
                issues.append(
                    _issue(
                        path,
                        walkthrough.line,
                        "shader-walkthrough-multishader-h5",
                        "multi-shader walkthroughs must use matching stage H5 headings under Shader Code and SPIR-V, with one llvm artifact per SPIR-V stage",
                    )
                )

    # H5 headings are reserved for per-stage organization in the two shader
    # artifact subsections. This is purely a heading ownership check.
    allowed_h5_ranges = [
        bounds[title]
        for title in ("Shader Code", "SPIR-V")
        if title in bounds
    ]
    for heading in _headings_inside(headings, walkthrough.line, walkthrough_end, 5):
        if not any(start < heading.line <= end for start, end in allowed_h5_ranges):
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "shader-walkthrough-h5-location",
                    "walkthrough H5 headings are allowed only under #### Shader Code or #### SPIR-V",
                )
            )

    return issues


def _casefold_match(title: str, canonical: str) -> bool:
    return title.casefold() == canonical.casefold()


def _validate_fixed_heading_case(
    path: Path, lines: Sequence[str], headings: Sequence[Heading]
) -> list[Issue]:
    """Require exact case only for headings owned by the canonical templates."""
    issues: list[Issue] = []
    h2 = [heading for heading in headings if heading.level == 2]

    for heading in h2:
        canonical = next(
            (
                title
                for title in CANONICAL_SECTION_ORDER
                if _casefold_match(heading.title, title)
            ),
            None,
        )
        if canonical is not None and heading.title != canonical:
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "heading-case",
                    f"fixed heading must use exact spelling and case: ## {canonical}",
                )
            )

    contextual_subsections = (
        ("Failure Meaning", 3, FAILURE_SUBSECTIONS),
        ("Case Pruning", 3, PRUNING_SUBSECTIONS),
    )
    for section_name, level, canonical_titles in contextual_subsections:
        section = next(
            (heading for heading in h2 if _casefold_match(heading.title, section_name)),
            None,
        )
        if section is None:
            continue
        start, end = _section_bounds(section, h2, len(lines))
        for heading in _headings_inside(headings, start, end, level):
            canonical = next(
                (
                    title
                    for title in canonical_titles
                    if _casefold_match(heading.title, title)
                ),
                None,
            )
            if canonical is not None and heading.title != canonical:
                issues.append(
                    _issue(
                        path,
                        heading.line,
                        "heading-case",
                        f"fixed heading must use exact spelling and case: "
                        f"{'#' * level} {canonical}",
                    )
                )

    shader = next(
        (heading for heading in h2 if _casefold_match(heading.title, "Shader Analysis")),
        None,
    )
    if shader is None:
        return issues
    start, end = _section_bounds(shader, h2, len(lines))
    shader_headings = [heading for heading in headings if start < heading.line <= end]
    walkthroughs = [
        heading
        for heading in shader_headings
        if heading.level == 3
        and heading.title.casefold().startswith(WALKTHROUGH_PREFIX.casefold())
    ]
    for walkthrough in walkthroughs:
        if not walkthrough.title.startswith(WALKTHROUGH_PREFIX):
            issues.append(
                _issue(
                    path,
                    walkthrough.line,
                    "heading-case",
                    f"fixed heading prefix must use exact spelling and case: "
                    f"### {WALKTHROUGH_PREFIX}",
                )
            )
        next_walkthrough = next(
            (candidate for candidate in walkthroughs if candidate.line > walkthrough.line),
            None,
        )
        walkthrough_end = next_walkthrough.line - 1 if next_walkthrough else end
        for heading in _headings_inside(
            shader_headings, walkthrough.line, walkthrough_end, 4
        ):
            canonical = next(
                (
                    title
                    for title in WALKTHROUGH_SUBSECTIONS
                    if _casefold_match(heading.title, title)
                ),
                None,
            )
            if canonical is not None and heading.title != canonical:
                issues.append(
                    _issue(
                        path,
                        heading.line,
                        "heading-case",
                        f"fixed heading must use exact spelling and case: #### {canonical}",
                    )
                )
    return issues


def _validate_section_contract(
    path: Path, lines: Sequence[str], headings: Sequence[Heading]
) -> list[Issue]:
    issues: list[Issue] = []
    h1 = [heading for heading in headings if heading.level == 1]
    for heading in h1:
        issues.append(
            _issue(path, heading.line, "no-h1-title", "Level-3 pages must omit a top-level # title")
        )

    h2 = [heading for heading in headings if heading.level == 2]
    titles = [heading.title for heading in h2]
    if not h2:
        return [_issue(path, 1, "sections", "page has no ## sections")]
    if h2[0].title != "Overview":
        issues.append(
            _issue(path, h2[0].line, "section-order", "first ## section must be Overview")
        )

    for heading in h2:
        if heading.title not in ALLOWED_SECTIONS:
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "section-name",
                    f"non-canonical ## section: {heading.title}",
                )
            )

    for title in REQUIRED_SECTIONS:
        count = titles.count(title)
        if count == 0:
            issues.append(_issue(path, 1, "required-section", f"missing ## {title}"))
        elif count > 1:
            first = next(heading for heading in h2 if heading.title == title)
            issues.append(
                _issue(path, first.line, "duplicate-section", f"duplicate ## {title}")
            )
    for title in OPTIONAL_SECTIONS:
        if titles.count(title) > 1:
            first = next(heading for heading in h2 if heading.title == title)
            issues.append(
                _issue(path, first.line, "duplicate-section", f"duplicate ## {title}")
            )

    canonical_positions = {title: index for index, title in enumerate(CANONICAL_SECTION_ORDER)}
    known = [heading for heading in h2 if heading.title in canonical_positions]
    for previous, current in zip(known, known[1:]):
        if canonical_positions[current.title] <= canonical_positions[previous.title]:
            issues.append(
                _issue(
                    path,
                    current.line,
                    "section-order",
                    f"## {current.title} is out of canonical order",
                )
            )

    overview = next((heading for heading in h2 if heading.title == "Overview"), None)
    if overview is not None:
        start, end = _section_bounds(overview, h2, len(lines))
        core_lines = [
            number
            for number in range(start + 1, end + 1)
            if lines[number - 1].startswith("**Core question:**")
        ]
        if len(core_lines) != 1:
            issues.append(
                _issue(
                    path,
                    overview.line,
                    "core-question",
                    "Overview must contain exactly one **Core question:** line",
                )
            )

    return issues


def _validate_fixed_subsections(
    path: Path, lines: Sequence[str], headings: Sequence[Heading]
) -> list[Issue]:
    issues: list[Issue] = []
    h2 = [heading for heading in headings if heading.level == 2]
    checks = (
        ("Failure Meaning", FAILURE_SUBSECTIONS, "failure-subsections"),
        ("Case Pruning", PRUNING_SUBSECTIONS, "pruning-subsections"),
    )
    for section_name, expected, rule in checks:
        section = next((heading for heading in h2 if heading.title == section_name), None)
        if section is None:
            continue
        start, end = _section_bounds(section, h2, len(lines))
        actual = [heading.title for heading in _headings_inside(headings, start, end, 3)]
        if actual != list(expected):
            issues.append(
                _issue(
                    path,
                    section.line,
                    rule,
                    f"## {section_name} must contain exactly these ### subsections in order: "
                    + ", ".join(expected),
                )
            )
    return issues


def _validate_cause_analysis(
    path: Path, lines: Sequence[str], headings: Sequence[Heading]
) -> list[Issue]:
    issues: list[Issue] = []
    h2 = [heading for heading in headings if heading.level == 2]
    failure = next((heading for heading in h2 if heading.title == "Failure Meaning"), None)
    if failure is None:
        return issues
    failure_start, failure_end = _section_bounds(failure, h2, len(lines))
    cause = next(
        (
            heading
            for heading in headings
            if heading.level == 3
            and heading.title == "Cause Analysis"
            and failure_start < heading.line <= failure_end
        ),
        None,
    )
    if cause is None:
        return issues
    causes = [
        heading
        for heading in headings
        if heading.level == 4 and cause.line < heading.line <= failure_end
    ]
    if not causes:
        issues.append(
            _issue(
                path,
                cause.line,
                "cause-analysis",
                "Cause Analysis needs at least one #### cause subsection",
            )
        )
        return issues
    for index, heading in enumerate(causes):
        end = causes[index + 1].line - 1 if index + 1 < len(causes) else failure_end
        block = "\n".join(lines[heading.line:end])
        for label in (
            "**Possible failure symptoms:**",
            "**Possible implementation causes:**",
        ):
            if label not in block:
                issues.append(
                    _issue(
                        path,
                        heading.line,
                        "cause-analysis-label",
                        f"#### {heading.title} is missing {label}",
                    )
                )
    return issues


def _validate_shader_walkthroughs(
    path: Path,
    lines: Sequence[str],
    headings: Sequence[Heading],
    fences: Sequence[Fence],
    category: str,
) -> list[Issue]:
    issues: list[Issue] = []
    h2 = [heading for heading in headings if heading.level == 2]
    section = next((heading for heading in h2 if heading.title == "Shader Analysis"), None)
    if section is None:
        return issues
    start, end = _section_bounds(section, h2, len(lines))
    section_headings = [h for h in headings if start < h.line <= end]
    walkthroughs = [
        h
        for h in section_headings
        if h.level == 3 and h.title.casefold().startswith(WALKTHROUGH_PREFIX.casefold())
    ]
    malformed_walkthroughs = [
        h
        for h in section_headings
        if h.level == 3
        and "walkthrough" in h.title.casefold()
        and h not in walkthroughs
    ]
    for heading in malformed_walkthroughs:
        issues.append(
            _issue(
                path,
                heading.line,
                "shader-walkthrough-heading",
                f"walkthrough heading must match exactly: ### {WALKTHROUGH_PREFIX} <1-3>",
            )
        )

    if not walkthroughs:
        if path.name not in PAGES_WITHOUT_WALKTHROUGH.get(category, set()):
            issues.append(
                _issue(
                    path,
                    section.line,
                    "shader-walkthrough-required",
                    "page has no Representative Shader Walkthrough and is not listed in "
                    "PAGES_WITHOUT_WALKTHROUGH",
                )
            )
        orphan_h4 = [heading for heading in section_headings if heading.level == 4]
        for heading in orphan_h4:
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "shader-walkthrough-orphan-subsection",
                    f"#### {heading.title} is outside a Representative Shader Walkthrough",
                )
            )
        return issues

    if len(walkthroughs) > 3:
        issues.append(
            _issue(path, walkthroughs[3].line, "shader-walkthrough-count", "at most three walkthroughs are allowed")
        )

    numbers: list[int] = []
    for walkthrough in walkthroughs:
        match = WALKTHROUGH_RE.fullmatch(walkthrough.title)
        if match is None:
            issues.append(
                _issue(
                    path,
                    walkthrough.line,
                    "shader-walkthrough-heading",
                    f"walkthrough heading must match exactly: ### {WALKTHROUGH_PREFIX} <1-3>",
                )
            )
        else:
            numbers.append(int(match.group("number")))
    if numbers != list(range(1, len(walkthroughs) + 1)):
        issues.append(
            _issue(
                path,
                walkthroughs[0].line,
                "shader-walkthrough-numbering",
                "walkthrough numbers must start at 1 and be consecutive",
            )
        )

    owned_h4_lines: set[int] = set()
    all_h3 = [heading for heading in section_headings if heading.level == 3]
    for walkthrough in walkthroughs:
        next_h3 = next(
            (heading for heading in all_h3 if heading.line > walkthrough.line),
            None,
        )
        walkthrough_end = next_h3.line - 1 if next_h3 else end
        subsections = _headings_inside(
            section_headings, walkthrough.line, walkthrough_end, 4
        )
        owned_h4_lines.update(heading.line for heading in subsections)
        actual = [heading.title for heading in subsections]
        if actual != list(WALKTHROUGH_SUBSECTIONS):
            issues.append(
                _issue(
                    path,
                    walkthrough.line,
                    "shader-walkthrough-subsections",
                    "walkthrough must contain exactly these #### subsections in order: "
                    + ", ".join(WALKTHROUGH_SUBSECTIONS),
                )
            )

        issues.extend(
            _validate_walkthrough_content_structure(
                path,
                lines,
                headings,
                fences,
                walkthrough,
                walkthrough_end,
                subsections,
            )
        )

        spirv = [heading for heading in subsections if heading.title == "SPIR-V"]
        if len(spirv) != 1:
            issues.append(
                _issue(
                    path,
                    walkthrough.line,
                    "shader-walkthrough-spirv",
                    f"walkthrough must contain exactly one #### SPIR-V subsection; found {len(spirv)}",
                )
            )
            continue

        spirv_heading = spirv[0]
        spirv_end = walkthrough_end
        block = "\n".join(lines[spirv_heading.line:spirv_end])
        llvm_blocks = re.findall(r"```llvm\s*\n(?P<body>.*?)\n```", block, re.DOTALL)
        if not llvm_blocks or not all(body.strip() for body in llvm_blocks):
            issues.append(
                _issue(
                    path,
                    spirv_heading.line,
                    "shader-walkthrough-spirv-format",
                    "#### SPIR-V must contain a non-empty ```llvm fenced assembly block",
                )
            )

    for heading in section_headings:
        if heading.level == 4 and heading.line not in owned_h4_lines:
            issues.append(
                _issue(
                    path,
                    heading.line,
                    "shader-walkthrough-orphan-subsection",
                    f"#### {heading.title} is outside a Representative Shader Walkthrough",
                )
            )
    return issues


def validate_page(path: Path, category: str) -> list[Issue]:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    headings, fences, issues = _parse_headings_and_fences(path, lines)
    issues.extend(_validate_heading_spacing(path, lines, headings))
    issues.extend(_validate_fixed_heading_case(path, lines, headings))
    issues.extend(_validate_section_contract(path, lines, headings))
    issues.extend(_validate_fixed_subsections(path, lines, headings))
    issues.extend(_validate_cause_analysis(path, lines, headings))

    issues.extend(_validate_shader_walkthroughs(path, lines, headings, fences, category))
    return sorted(issues, key=lambda issue: (issue.line, issue.rule, issue.message))


def discover_category_pages(wiki_dir: Path, category: str) -> list[Path]:
    directory = wiki_dir / "testfiles" / category
    if not directory.is_dir():
        raise FileNotFoundError(f"category directory not found: {directory}")
    return [
        page
        for page in sorted(directory.glob("*.md"))
        if not page.name.startswith("vkt") and not page.stem.endswith("_brief")
    ]


def _category_for_explicit_page(wiki_dir: Path, path: Path) -> str:
    try:
        relative = path.resolve().relative_to((wiki_dir / "testfiles").resolve())
    except ValueError as error:
        raise ValueError(f"file is not below {wiki_dir / 'testfiles'}: {path}") from error
    if len(relative.parts) < 2:
        raise ValueError(f"cannot infer category from path: {path}")
    return relative.parts[0]


def _print_results(
    selected: Sequence[tuple[str, Path]],
    results: Sequence[tuple[Path, list[Issue]]],
    wiki_dir: Path,
) -> int:
    """Print compact category-oriented results and return the process status."""
    category_pages: dict[str, list[tuple[Path, list[Issue]]]] = {}
    for (category, _selected_path), (path, issues) in zip(selected, results):
        category_pages.setdefault(category, []).append((path, issues))

    total_issues = 0
    failing_pages = 0
    failing_categories = 0
    for category, pages in category_pages.items():
        category_path = wiki_dir / "testfiles" / category
        failed = [(path, issues) for path, issues in pages if issues]
        if not failed:
            print(f"PASS {category_path}")
            continue

        failing_categories += 1
        print(f"FAIL {category_path}")
        for path, issues in failed:
            print(f"     {path.name}:{issues[0].line}:")
            for issue in issues:
                print(f"     - [{issue.rule}] {issue.message}")
            failing_pages += 1
            total_issues += len(issues)

    print()
    print(
        f"Total checked category count {len(category_pages)}, "
        f"page count {len(results)}."
    )
    print(
        f"Failure category count {failing_categories}, "
        f"page count {failing_pages}, finding count {total_issues}."
    )
    return 1 if total_issues else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("categories", nargs="*", help="Level-3 categories to validate")
    parser.add_argument("--files", nargs="+", type=Path, help="specific Level-3 files to validate")
    parser.add_argument(
        "--wiki-dir", type=Path, default=Path("external/vulkancts/wiki"), help="canonical English Wiki root"
    )
    args = parser.parse_args()

    if not args.categories and not args.files:
        parser.error("provide at least one category or --files")
    if args.categories and args.files:
        parser.error("use categories or --files, not both")

    selected: list[tuple[str, Path]] = []
    try:
        if args.files:
            for path in args.files:
                if not path.is_file():
                    raise FileNotFoundError(f"file not found: {path}")
                selected.append((_category_for_explicit_page(args.wiki_dir, path), path))
        else:
            for category in args.categories:
                selected.extend(
                    (category, path) for path in discover_category_pages(args.wiki_dir, category)
                )
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    results: list[tuple[Path, list[Issue]]] = []
    for category, path in selected:
        issues = validate_page(path, category)
        results.append((path, issues))

    return _print_results(selected, results, args.wiki_dir)


if __name__ == "__main__":
    raise SystemExit(main())
