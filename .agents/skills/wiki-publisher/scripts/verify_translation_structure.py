#!/usr/bin/env python3
"""Validate canonical Chinese Level-3 pages against current English sources.

This validator has two layers:

1. run the canonical English structure validator on the source page;
2. enforce the equivalent Chinese heading, walkthrough, table, SPIR-V, and
   failure-analysis contracts while also comparing source/target structures.

It is a structural and fixed-language guard, not a translation-quality or
semantic audit.

Exit codes:
    0 - all selected pages passed
    1 - one or more structural issues were found
    2 - invocation or input error
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[4]
ENGLISH_VALIDATOR_PATH = REPO_ROOT / ".agents/skills/wiki-writer/scripts/verify_english_structure.py"

H2_TRANSLATIONS = {
    "Overview": "概览",
    "Background Knowledge": "背景知识",
    "Registration Hierarchy": "注册层级",
    "Parameter Dimensions and Observed Values": "参数维度与可确认取值",
    "Behavior Parameters": "行为参数",
    "Shader Analysis": "Shader 分析",
    "Runtime Execution and Result Checking": "runtime 执行逻辑与结果检查",
    "Failure Meaning": "失败含义",
    "Case Pruning": "用例裁剪",
    "Key Takeaways": "要点总结",
    "Source Reference Appendix": "源码参考附录",
}
H3_TRANSLATIONS = {
    "Failure Cause Mapping": "失败原因映射",
    "Cause Analysis": "原因分析",
    "Requirement-based pruning": "基于要求的裁剪",
    "Design-based pruning": "基于设计的裁剪",
}
WALKTHROUGH_SOURCE_PREFIX = "Representative Shader Walkthrough"
WALKTHROUGH_TARGET_PREFIX = "代表性 shader 讲解"
WALKTHROUGH_TARGET_RE = re.compile(r"^代表性 shader 讲解 (?P<number>[1-3])$")
H4_TRANSLATIONS = {
    "Parameter Values Chosen": "所选参数值",
    "Purpose": "目的",
    "Structural Design": "结构设计",
    "Shader Code": "Shader 代码",
    "Additional Info": "补充信息",
    "Parameter Variation Summary": "参数变化总结",
    "SPIR-V": "SPIR-V",
}
TARGET_WALKTHROUGH_SUBSECTIONS = tuple(H4_TRANSLATIONS.values())
SOURCE_CORE_LABEL = "**Core question:**"
TARGET_CORE_LABEL = "**核心问题：**"
TARGET_CAUSE_LABELS = ("**可能的失败表现：**", "**可能的实现原因：**")
TARGET_PATH_LABEL = "代表性路径："
TARGET_PARAMETER_HEADER = ["参数选择", "在此代表性用例中的含义"]
TARGET_VARIATION_HEADER = ["参数维度", "相对此 shader 的 shader 层面变化", "证据"]
TARGET_SPIRV_METADATA_LABELS = ("状态", "来源", "阶段", "目标 SPIRV 版本")
TARGET_SPIRV_SUMMARY = "<summary>点击展开 SPIRV asm 代码</summary>"
SOURCE_NO_PREREQUISITES = "No additional prerequisite concepts are needed for this page."
TARGET_NO_PREREQUISITES = "本页不需要额外的前置概念。"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+\S")


@dataclass(frozen=True)
class Mismatch:
    line: int
    rule: str
    message: str


def _load_english_validator() -> ModuleType:
    scripts_dir = str(ENGLISH_VALIDATOR_PATH.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(
        "canonical_english_structure_validator", ENGLISH_VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load English validator: {ENGLISH_VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGLISH = _load_english_validator()


def _issue(line: int, rule: str, message: str) -> Mismatch:
    return Mismatch(line=line, rule=rule, message=message)


def _body(lines: Sequence[str], start: int, end: int) -> str:
    return "\n".join(lines[start:end])


def _nonblank(lines: Sequence[str], start: int, end: int) -> list[str]:
    return [line for line in lines[start:end] if line.strip()]


def _headings_at(headings: Sequence[object], level: int) -> list[object]:
    return [heading for heading in headings if heading.level == level]


def _section_bounds_by_index(
    headings: Sequence[object], index: int, line_count: int
) -> tuple[int, int]:
    heading = headings[index]
    end = headings[index + 1].line - 1 if index + 1 < len(headings) else line_count
    return heading.line, end


def _validate_heading_spacing(lines: Sequence[str], headings: Sequence[object]) -> list[Mismatch]:
    issues: list[Mismatch] = []
    for heading in headings:
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
                    heading.line,
                    "heading-spacing",
                    f"{'#' * heading.level} {heading.title} 前必须恰好有一个空行；实际为 {blank_count}",
                )
            )
    return issues


def _validate_section_alignment(
    source_headings: Sequence[object], target_headings: Sequence[object]
) -> list[Mismatch]:
    issues: list[Mismatch] = []
    source_h2 = _headings_at(source_headings, 2)
    target_h2 = _headings_at(target_headings, 2)
    expected = [H2_TRANSLATIONS.get(heading.title, heading.title) for heading in source_h2]
    actual = [heading.title for heading in target_h2]
    if actual != expected:
        line = target_h2[0].line if target_h2 else 1
        issues.append(
            _issue(
                line,
                "translated-section-contract",
                f"中文 ## 标题必须与 English source 一一对应且顺序一致；expected={expected}, actual={actual}",
            )
        )
    if _headings_at(target_headings, 1):
        issues.append(_issue(_headings_at(target_headings, 1)[0].line, "no-h1-title", "Level-3 中文页面不得包含 # 标题"))
    return issues


def _compare_structural_counts(
    source_lines: Sequence[str],
    target_lines: Sequence[str],
    source_headings: Sequence[object],
    target_headings: Sequence[object],
    source_fences: Sequence[object],
    target_fences: Sequence[object],
) -> list[Mismatch]:
    """Compare stable Markdown structures per aligned H2 section."""
    issues: list[Mismatch] = []
    source_h2 = _headings_at(source_headings, 2)
    target_h2 = _headings_at(target_headings, 2)
    if len(source_h2) != len(target_h2):
        return issues

    def counts(lines: Sequence[str], headings: Sequence[object], fences: Sequence[object], start: int, end: int) -> tuple[int, int, int, int, tuple[str, ...]]:
        block = lines[start:end]
        lists = sum(bool(LIST_ITEM_RE.match(line)) for line in block)
        tables = len(ENGLISH._table_rows(lines, start, end))
        section_fences = ENGLISH._fences_inside(fences, start, end)
        tree_children = sum(
            line.strip().startswith(("├──", "└──"))
            for fence in section_fences
            if fence.language == "text"
            for _, line in fence.lines
        )
        return lists, tables, len(section_fences), tree_children, tuple(f.language for f in section_fences)

    for index, (source_h2_heading, target_h2_heading) in enumerate(zip(source_h2, target_h2)):
        source_start, source_end = _section_bounds_by_index(source_h2, index, len(source_lines))
        target_start, target_end = _section_bounds_by_index(target_h2, index, len(target_lines))
        source_counts = counts(source_lines, source_headings, source_fences, source_start, source_end)
        target_counts = counts(target_lines, target_headings, target_fences, target_start, target_end)
        if source_counts != target_counts:
            issues.append(
                _issue(
                    target_h2_heading.line,
                    "translated-section-structure",
                    f"## {target_h2_heading.title} 的 list/table/fence/tree 结构必须匹配 source；source={source_counts}, target={target_counts}",
                )
            )
    return issues


def _validate_fixed_sections(
    lines: Sequence[str], headings: Sequence[object]
) -> list[Mismatch]:
    issues: list[Mismatch] = []
    h2 = _headings_at(headings, 2)
    by_title = {heading.title: heading for heading in h2}

    overview = by_title.get("概览")
    if overview is not None:
        start, end = ENGLISH._section_bounds(overview, h2, len(lines))
        core = [line for line in lines[start:end] if line.startswith(TARGET_CORE_LABEL)]
        if len(core) != 1:
            issues.append(_issue(overview.line, "core-question", f"概览必须恰好包含一行 {TARGET_CORE_LABEL}"))

    checks = (
        ("失败含义", ("失败原因映射", "原因分析"), "failure-subsections"),
        ("用例裁剪", ("基于要求的裁剪", "基于设计的裁剪"), "pruning-subsections"),
    )
    for section_name, expected, rule in checks:
        section = by_title.get(section_name)
        if section is None:
            continue
        start, end = ENGLISH._section_bounds(section, h2, len(lines))
        actual = [h.title for h in ENGLISH._headings_inside(headings, start, end, 3)]
        if actual != list(expected):
            issues.append(_issue(section.line, rule, f"## {section_name} 必须依次包含：{', '.join(expected)}"))

    failure = by_title.get("失败含义")
    if failure is not None:
        failure_start, failure_end = ENGLISH._section_bounds(failure, h2, len(lines))
        cause = next(
            (
                heading
                for heading in headings
                if heading.level == 3
                and heading.title == "原因分析"
                and failure_start < heading.line <= failure_end
            ),
            None,
        )
        if cause is not None:
            causes = [
                heading
                for heading in headings
                if heading.level == 4 and cause.line < heading.line <= failure_end
            ]
            if not causes:
                issues.append(_issue(cause.line, "cause-analysis", "原因分析至少需要一个 #### 原因小节"))
            for index, heading in enumerate(causes):
                end = causes[index + 1].line - 1 if index + 1 < len(causes) else failure_end
                block = _body(lines, heading.line, end)
                for label in TARGET_CAUSE_LABELS:
                    if label not in block:
                        issues.append(_issue(heading.line, "cause-analysis-label", f"#### {heading.title} 缺少 {label}"))
    return issues


def _validate_walkthrough_content(
    lines: Sequence[str],
    headings: Sequence[object],
    fences: Sequence[object],
    walkthrough: object,
    walkthrough_end: int,
    subsections: Sequence[object],
) -> list[Mismatch]:
    issues: list[Mismatch] = []
    subsection_map = {heading.title: heading for heading in subsections}
    bounds = {
        title: (heading.line, ENGLISH._heading_end(heading, headings, walkthrough_end))
        for title, heading in subsection_map.items()
    }
    if subsections and any(line.strip() for line in lines[walkthrough.line : subsections[0].line - 1]):
        issues.append(_issue(subsections[0].line, "shader-walkthrough-first-subsection", "代表性 shader 讲解后必须直接进入 #### 所选参数值，中间只能有空行"))

    for title in TARGET_WALKTHROUGH_SUBSECTIONS:
        if title == "补充信息" or title not in bounds:
            continue
        if not _nonblank(lines, *bounds[title]):
            issues.append(_issue(subsection_map[title].line, "shader-walkthrough-empty-subsection", f"#### {title} 不得为空"))

    parameters = subsection_map.get("所选参数值")
    if parameters is not None:
        start, end = bounds[parameters.title]
        block = _body(lines, start, end)
        path_fences = [
            fence
            for fence in ENGLISH._fences_inside(fences, start, end)
            if fence.language == "text" and any(line.strip().startswith("dEQP-VK.") for _, line in fence.lines)
        ]
        if TARGET_PATH_LABEL not in block or len(path_fences) != 1:
            issues.append(_issue(parameters.line, "shader-walkthrough-parameter-path", "#### 所选参数值必须包含“代表性路径：”及唯一的 ```text dEQP-VK... 路径块"))
        table = ENGLISH._table_rows(lines, start, end)
        if not table or table[0][1] != TARGET_PARAMETER_HEADER or len(table) < 2:
            issues.append(_issue(parameters.line, "shader-walkthrough-parameter-table", "#### 所选参数值必须包含固定两列表头及至少一个数据行"))

    structural = subsection_map.get("结构设计")
    if structural is not None:
        start, end = bounds[structural.title]
        has_table = bool(ENGLISH._table_rows(lines, start, end))
        has_mermaid = any(f.language == "mermaid" for f in ENGLISH._fences_inside(fences, start, end))
        has_list = any(LIST_ITEM_RE.match(line) for line in lines[start:end])
        if not (has_table or has_mermaid or has_list):
            issues.append(_issue(structural.line, "shader-walkthrough-structural-design-format", "#### 结构设计必须使用表格、Mermaid 或 Markdown 列表"))

    shader_code = subsection_map.get("Shader 代码")
    if shader_code is not None:
        start, end = bounds[shader_code.title]
        code_fences = ENGLISH._fences_inside(fences, start, end)
        source_fences = [f for f in code_fences if f.language in {"glsl", "hlsl"}]
        llvm_fences = [f for f in code_fences if f.language == "llvm"]
        if llvm_fences:
            issues.append(_issue(llvm_fences[0].start, "shader-walkthrough-shader-code-assembly", "#### Shader 代码不得包含 SPIR-V assembly"))
        # Direct-SPIR-V pages can legitimately have no GLSL/HLSL fence. The source
        # validator proves that exception; translation parity proves no fence was lost.
        if source_fences and any(not any(line.strip() for _, line in fence.lines) for fence in source_fences):
            issues.append(_issue(shader_code.line, "shader-walkthrough-shader-code-empty", "GLSL/HLSL fenced block 不得为空"))

    additional = subsection_map.get("补充信息")
    if additional is not None:
        start, end = bounds[additional.title]
        body = _nonblank(lines, start, end)
        if body and not any(LIST_ITEM_RE.match(line) for line in body):
            issues.append(_issue(additional.line, "shader-walkthrough-additional-info-format", "非空 #### 补充信息必须使用 Markdown 列表"))

    variations = subsection_map.get("参数变化总结")
    if variations is not None:
        start, end = bounds[variations.title]
        table = ENGLISH._table_rows(lines, start, end)
        if not table or table[0][1] != TARGET_VARIATION_HEADER or len(table) < 2:
            issues.append(_issue(variations.line, "shader-walkthrough-variation-table", "#### 参数变化总结必须包含固定三列表头及至少一个数据行"))
        elif any(not MARKDOWN_LINK_RE.search(row[2]) for _, row in table[1:]):
            issues.append(_issue(table[1][0], "shader-walkthrough-variation-evidence", "参数变化总结的每个数据行都必须在证据列包含 Markdown source link"))

    spirv = subsection_map.get("SPIR-V")
    if spirv is not None:
        start, end = bounds[spirv.title]
        block = _body(lines, start, end)
        llvm = [f for f in ENGLISH._fences_inside(fences, start, end) if f.language == "llvm"]
        for fence in llvm:
            assembly = [line for _, line in fence.lines]
            if not assembly or assembly[0].strip() != "; SPIR-V" or not any(re.fullmatch(r"; Version: 1\.[0-6]", line.strip()) for line in assembly[:5]):
                issues.append(_issue(fence.start, "shader-walkthrough-spirv-header", "llvm artifact 必须以标准 '; SPIR-V' 和 '; Version: 1.x' header 开始"))
        if llvm:
            details = len(re.findall(r"^<details>\s*$", block, re.MULTILINE))
            closings = len(re.findall(r"^</details>\s*$", block, re.MULTILINE))
            summaries = len(re.findall(rf"^{re.escape(TARGET_SPIRV_SUMMARY)}\s*$", block, re.MULTILINE))
            if not (details == closings == summaries == len(llvm)):
                issues.append(_issue(spirv.line, "shader-walkthrough-spirv-details", "每个 SPIR-V llvm block 必须有一个固定中文 summary 的 collapsed <details> wrapper"))
            for label in TARGET_SPIRV_METADATA_LABELS:
                if len(re.findall(rf"^- {re.escape(label)}：\s*\S", block, re.MULTILINE)) != len(llvm):
                    issues.append(_issue(spirv.line, "shader-walkthrough-spirv-metadata", f"每个 SPIR-V artifact 必须恰好包含一个 '- {label}：' metadata 行"))
    return issues


def _validate_walkthroughs(
    lines: Sequence[str], headings: Sequence[object], fences: Sequence[object]
) -> list[Mismatch]:
    issues: list[Mismatch] = []
    h2 = _headings_at(headings, 2)
    shader = next((h for h in h2 if h.title == "Shader 分析"), None)
    if shader is None:
        return issues
    start, end = ENGLISH._section_bounds(shader, h2, len(lines))
    section_headings = [h for h in headings if start < h.line <= end]
    walkthroughs = [h for h in section_headings if h.level == 3 and h.title.startswith(WALKTHROUGH_TARGET_PREFIX)]
    malformed = [h for h in section_headings if h.level == 3 and ("讲解" in h.title or "walkthrough" in h.title.casefold()) and h not in walkthroughs]
    for heading in malformed:
        issues.append(_issue(heading.line, "shader-walkthrough-heading", f"讲解标题必须严格匹配：### {WALKTHROUGH_TARGET_PREFIX} <1-3>"))
    if not walkthroughs:
        if any(h.level == 4 for h in section_headings):
            issues.append(_issue(shader.line, "shader-walkthrough-orphan-subsection", "没有代表性 shader 讲解时，Shader 分析中不得出现 #### 小节"))
        return issues
    if len(walkthroughs) > 3:
        issues.append(_issue(walkthroughs[3].line, "shader-walkthrough-count", "最多允许三个代表性 shader 讲解"))
    numbers=[]
    for walkthrough in walkthroughs:
        match=WALKTHROUGH_TARGET_RE.fullmatch(walkthrough.title)
        if match is None:
            issues.append(_issue(walkthrough.line, "shader-walkthrough-heading", f"讲解标题必须严格匹配：### {WALKTHROUGH_TARGET_PREFIX} <1-3>"))
        else:
            numbers.append(int(match.group("number")))
    if numbers != list(range(1,len(walkthroughs)+1)):
        issues.append(_issue(walkthroughs[0].line, "shader-walkthrough-numbering", "讲解编号必须从 1 开始连续递增"))

    owned_h4:set[int]=set(); all_h3=[h for h in section_headings if h.level==3]
    for walkthrough in walkthroughs:
        next_h3=next((h for h in all_h3 if h.line>walkthrough.line),None)
        walkthrough_end=next_h3.line-1 if next_h3 else end
        subsections=ENGLISH._headings_inside(section_headings,walkthrough.line,walkthrough_end,4)
        owned_h4.update(h.line for h in subsections)
        actual=[h.title for h in subsections]
        if actual != list(TARGET_WALKTHROUGH_SUBSECTIONS):
            issues.append(_issue(walkthrough.line,"shader-walkthrough-subsections","讲解必须依次且仅包含："+", ".join(TARGET_WALKTHROUGH_SUBSECTIONS)))
        issues.extend(_validate_walkthrough_content(lines,headings,fences,walkthrough,walkthrough_end,subsections))
        spirv=[h for h in subsections if h.title=='SPIR-V']
        if len(spirv)!=1:
            issues.append(_issue(walkthrough.line,"shader-walkthrough-spirv",f"每个讲解必须恰好有一个 #### SPIR-V 小节；实际为 {len(spirv)}"))
        else:
            block=_body(lines,spirv[0].line,walkthrough_end)
            llvm=re.findall(r"```llvm\s*\n(?P<body>.*?)\n```",block,re.DOTALL)
            if not llvm or not all(body.strip() for body in llvm):
                issues.append(_issue(spirv[0].line,"shader-walkthrough-spirv-format","#### SPIR-V 必须包含非空 ```llvm assembly block"))
    for heading in section_headings:
        if heading.level==4 and heading.line not in owned_h4:
            issues.append(_issue(heading.line,"shader-walkthrough-orphan-subsection",f"#### {heading.title} 位于代表性 shader 讲解之外"))
    return issues


def _validate_walkthrough_alignment(
    source_lines: Sequence[str],
    target_lines: Sequence[str],
    source_headings: Sequence[object],
    target_headings: Sequence[object],
) -> list[Mismatch]:
    """Require source/target walkthrough and per-stage H5 ownership to align."""
    issues: list[Mismatch] = []

    def walkthroughs(
        lines: Sequence[str],
        headings: Sequence[object],
        section_title: str,
        prefix: str,
    ) -> tuple[list[object], int]:
        h2 = _headings_at(headings, 2)
        section = next((h for h in h2 if h.title == section_title), None)
        if section is None:
            return [], 0
        start, end = ENGLISH._section_bounds(section, h2, len(lines))
        return [
            h
            for h in headings
            if h.level == 3 and start < h.line <= end and h.title.startswith(prefix)
        ], end

    source_walkthroughs, source_shader_end = walkthroughs(
        source_lines, source_headings, "Shader Analysis", WALKTHROUGH_SOURCE_PREFIX
    )
    target_walkthroughs, target_shader_end = walkthroughs(
        target_lines, target_headings, "Shader 分析", WALKTHROUGH_TARGET_PREFIX
    )
    if len(source_walkthroughs) != len(target_walkthroughs):
        line = target_walkthroughs[0].line if target_walkthroughs else 1
        issues.append(
            _issue(
                line,
                "translated-walkthrough-count",
                f"中文页必须保留 source 的 walkthrough 数量；source={len(source_walkthroughs)}, target={len(target_walkthroughs)}",
            )
        )
        return issues

    for index, (source_walkthrough, target_walkthrough) in enumerate(
        zip(source_walkthroughs, target_walkthroughs)
    ):
        source_end = (
            source_walkthroughs[index + 1].line - 1
            if index + 1 < len(source_walkthroughs)
            else source_shader_end
        )
        target_end = (
            target_walkthroughs[index + 1].line - 1
            if index + 1 < len(target_walkthroughs)
            else target_shader_end
        )

        def stage_keys(
            headings: Sequence[object],
            walkthrough: object,
            end: int,
            code_title: str,
        ) -> tuple[list[str], list[str], list[object]]:
            h4 = ENGLISH._headings_inside(headings, walkthrough.line, end, 4)
            by_title = {h.title: h for h in h4}
            result: list[list[str]] = []
            owned: list[object] = []
            for title in (code_title, "SPIR-V"):
                section = by_title.get(title)
                if section is None:
                    result.append([])
                    continue
                section_end = ENGLISH._heading_end(section, headings, end)
                h5 = ENGLISH._headings_inside(headings, section.line, section_end, 5)
                owned.extend(h5)
                result.append([ENGLISH._shader_stage_key(h.title) for h in h5])
            all_h5 = ENGLISH._headings_inside(headings, walkthrough.line, end, 5)
            return result[0], result[1], [h for h in all_h5 if h not in owned]

        source_code, source_spirv, _ = stage_keys(
            source_headings, source_walkthrough, source_end, "Shader Code"
        )
        target_code, target_spirv, target_orphans = stage_keys(
            target_headings, target_walkthrough, target_end, "Shader 代码"
        )
        if target_orphans:
            issues.append(
                _issue(
                    target_orphans[0].line,
                    "shader-walkthrough-h5-location",
                    "walkthrough 的 ##### stage 标题只能位于 #### Shader 代码或 #### SPIR-V 下",
                )
            )
        if (source_code, source_spirv) != (target_code, target_spirv):
            issues.append(
                _issue(
                    target_walkthrough.line,
                    "translated-multishader-h5",
                    "中文页必须保留 source 在 Shader Code/SPIR-V 下的 H5 stage identity 和顺序；"
                    f"source={(source_code, source_spirv)}, target={(target_code, target_spirv)}",
                )
            )
    return issues


def validate_translation(source_path: Path, target_path: Path) -> tuple[list[Any], list[Mismatch]]:
    source_lines=source_path.read_text(encoding='utf-8').splitlines()
    target_lines=target_path.read_text(encoding='utf-8').splitlines()
    source_headings,source_fences,source_parse=ENGLISH._parse_headings_and_fences(source_path,source_lines)
    target_headings,target_fences,target_parse=ENGLISH._parse_headings_and_fences(target_path,target_lines)
    category=source_path.parent.name
    english_issues=ENGLISH.validate_page(source_path,category)
    issues=[_issue(issue.line,issue.rule,issue.message) for issue in target_parse]
    issues.extend(_validate_heading_spacing(target_lines,target_headings))
    issues.extend(_validate_section_alignment(source_headings,target_headings))
    issues.extend(_compare_structural_counts(source_lines,target_lines,source_headings,target_headings,source_fences,target_fences))
    issues.extend(_validate_fixed_sections(target_lines,target_headings))
    issues.extend(_validate_walkthroughs(target_lines,target_headings,target_fences))
    issues.extend(
        _validate_walkthrough_alignment(
            source_lines, target_lines, source_headings, target_headings
        )
    )
    if SOURCE_NO_PREREQUISITES in source_path.read_text(encoding='utf-8') and TARGET_NO_PREREQUISITES not in target_path.read_text(encoding='utf-8'):
        background=next((h for h in target_headings if h.level==2 and h.title=='背景知识'),None)
        issues.append(_issue(background.line if background else 1,'no-prerequisite-sentence',f'固定句式必须为：{TARGET_NO_PREREQUISITES}'))
    return english_issues,sorted(issues,key=lambda x:(x.line,x.rule,x.message))


def discover_category_pairs(
    wiki_dir: Path, target_dir: Path, category: str
) -> list[tuple[Path, Path]]:
    sources = ENGLISH.discover_category_pages(wiki_dir, category)
    pairs = [(source, target_dir / category / source.name) for source in sources]
    missing = [target for _source, target in pairs if not target.is_file()]
    if missing:
        raise FileNotFoundError(f"translated page not found: {missing[0]}")
    return pairs


def _category_for_explicit_page(wiki_dir: Path, path: Path) -> str:
    try:
        relative = path.resolve().relative_to((wiki_dir / "testfiles").resolve())
    except ValueError as error:
        raise ValueError(f"file is not below {wiki_dir / 'testfiles'}: {path}") from error
    if len(relative.parts) < 2:
        raise ValueError(f"cannot infer category from path: {path}")
    return relative.parts[0]


def _print_results(
    selected: Sequence[tuple[str, Path, Path]],
    results: Sequence[tuple[list[Any], list[Mismatch]]],
    wiki_dir: Path,
    category_order: Sequence[str],
) -> int:
    """Print the same compact category-oriented shape as the English validator."""
    category_pages: dict[
        str, list[tuple[Path, list[Any], list[Mismatch]]]
    ] = {}
    for (category, _source, target), (english_issues, target_issues) in zip(
        selected, results
    ):
        category_pages.setdefault(category, []).append(
            (target, english_issues, target_issues)
        )

    for category in category_order:
        category_pages.setdefault(category, [])

    total_issues = 0
    failing_pages = 0
    failing_categories = 0
    for category, pages in category_pages.items():
        category_path = wiki_dir / "testfiles" / category
        failed = [
            (path, english_issues, target_issues)
            for path, english_issues, target_issues in pages
            if english_issues or target_issues
        ]
        if not failed:
            print(f"PASS {category_path}")
            continue

        failing_categories += 1
        print(f"FAIL {category_path}")
        for path, english_issues, target_issues in failed:
            all_issues = [*english_issues, *target_issues]
            print(f"     {path.name}:{all_issues[0].line}:")
            for issue in english_issues:
                print(
                    f"     - [english:{issue.rule}] "
                    f"English source: {issue.message}"
                )
            for issue in target_issues:
                print(f"     - [{issue.rule}] {issue.message}")
            failing_pages += 1
            total_issues += len(all_issues)

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


def _run_legacy_pair(source: Path, target: Path, verbose: bool) -> int:
    """Preserve the original one-pair CLI for existing worker commands."""
    if not source.is_file() or not target.is_file():
        print("Error: source and target must both exist", file=sys.stderr)
        return 2
    english_issues, issues = validate_translation(source, target)
    if english_issues:
        print(
            f"FAIL: English source has {len(english_issues)} canonical structure "
            "issue(s); repair source first:"
        )
        for issue in english_issues:
            print(f"  {source}:{issue.line}: [{issue.rule}] {issue.message}")
        return 1
    if issues:
        print(f"FAIL: {len(issues)} Chinese structure/fixed-language mismatch(es) found:")
        for issue in issues:
            print(f"  {target}:{issue.line}: [{issue.rule}] {issue.message}")
        return 1
    if verbose:
        print(f"English source validated with current canonical validator: {source}")
    print("PASS: canonical Chinese structure and fixed-language checks passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("categories", nargs="*", help="Level-3 categories to validate")
    parser.add_argument(
        "--files", nargs="+", type=Path, help="specific English Level-3 files to validate"
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=Path("external/vulkancts/wiki"),
        help="canonical English Wiki root",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=Path("vkcts-wiki-pages/categories"),
        help="published Chinese Level-3 category root",
    )
    # Backward-compatible one-pair mode used by existing publisher workers.
    parser.add_argument("--source", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.source is not None or args.target is not None:
        if args.source is None or args.target is None:
            parser.error("--source and --target must be used together")
        if args.categories or args.files:
            parser.error("legacy --source/--target mode cannot be combined with categories or --files")
        return _run_legacy_pair(args.source, args.target, args.verbose)

    if not args.categories and not args.files:
        parser.error("provide at least one category or --files")
    if args.categories and args.files:
        parser.error("use categories or --files, not both")

    selected: list[tuple[str, Path, Path]] = []
    try:
        if args.files:
            for source in args.files:
                if not source.is_file():
                    raise FileNotFoundError(f"file not found: {source}")
                category = _category_for_explicit_page(args.wiki_dir, source)
                target = args.target_dir / category / source.name
                if not target.is_file():
                    raise FileNotFoundError(f"translated page not found: {target}")
                selected.append((category, source, target))
        else:
            for category in args.categories:
                selected.extend(
                    (category, source, target)
                    for source, target in discover_category_pairs(
                        args.wiki_dir, args.target_dir, category
                    )
                )
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    results = [
        validate_translation(source, target)
        for _category, source, target in selected
    ]
    category_order = (
        list(args.categories)
        if args.categories
        else [category for category, _source, _target in selected]
    )
    return _print_results(selected, results, args.wiki_dir, category_order)


if __name__=='__main__':
    raise SystemExit(main())
