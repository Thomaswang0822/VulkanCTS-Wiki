from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify_translation_structure.py")
SPEC = importlib.util.spec_from_file_location("verify_translation_structure", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

ENGLISH_PAGE = """## Overview

**Core question:** Does the test work?

## Background Knowledge

No additional prerequisite concepts are needed for this page.

## Registration Hierarchy

```text
memory.sample
└── first
```

## Parameter Dimensions and Observed Values

None.

## Behavior Parameters

No meaningful behavioral axis.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.sample.first
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `first` | Selects the representative shader path. |

#### Purpose

Exercise the representative shader.

#### Structural Design

| Phase | Role |
|-------|------|
| Write | The shader writes one value. |

#### Shader Code

```glsl
#version 450
void main() {}
```

#### Additional Info

- Fixed case.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Case | Other cases change the value. | [Source](source.cpp#L1) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
OpCapability Shader
```

</details>

## Runtime Execution and Result Checking

- The host checks the result.

## Failure Meaning

### Failure Cause Mapping

A failure means the result differed.

### Cause Analysis

#### Result mismatch

**Possible failure symptoms:** The result differs.

**Possible implementation causes:** The implementation returned the wrong result.

## Case Pruning

### Requirement-based pruning

None.

### Design-based pruning

None.

## Key Takeaways

- The result must match.

## Source Reference Appendix

- Source.
"""

CHINESE_PAGE = """## 概览

**核心问题：** 测试能否正常工作？

## 背景知识

本页不需要额外的前置概念。

## 注册层级

```text
memory.sample
└── first
```

## 参数维度与可确认取值

无。

## 行为参数

没有有意义的行为轴。

## Shader 分析

### 代表性 shader 讲解 1

#### 所选参数值

代表性路径：

```text
dEQP-VK.memory.sample.first
```

| 参数选择 | 在此代表性用例中的含义 |
|----------|------------------------|
| `first` | 选择代表性 shader 路径。 |

#### 目的

执行代表性 shader。

#### 结构设计

| 阶段 | 作用 |
|------|------|
| 写入 | shader 写入一个值。 |

#### Shader 代码

```glsl
#version 450
void main() {}
```

#### 补充信息

- 固定用例。

#### 参数变化总结

| 参数维度 | 相对此 shader 的 shader 层面变化 | 证据 |
|----------|--------------------------------|------|
| 用例 | 其他用例会改变写入值。 | [源码](source.cpp#L1) |

#### SPIR-V

- 状态：已生成并验证
- 来源：本讲解中的重构 GLSL
- 阶段：`comp`
- 目标 SPIRV 版本：`spirv1.0`

<details>
<summary>点击展开 SPIRV asm 代码</summary>

```llvm
; SPIR-V
; Version: 1.0
OpCapability Shader
```

</details>

## runtime 执行逻辑与结果检查

- host 检查结果。

## 失败含义

### 失败原因映射

失败表示结果不同。

### 原因分析

#### 结果不匹配

**可能的失败表现：** 结果不同。

**可能的实现原因：** 实现返回了错误结果。

## 用例裁剪

### 基于要求的裁剪

无。

### 基于设计的裁剪

无。

## 要点总结

- 结果必须匹配。

## 源码参考附录

- 源码。
"""


class TranslationStructureValidatorTests(unittest.TestCase):
    def validate(self, target: str):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Sample.md"
            translated = root / "Sample.zh.md"
            source.write_text(ENGLISH_PAGE, encoding="utf-8")
            translated.write_text(target, encoding="utf-8")
            english_issues, target_issues = validator.validate_translation(source, translated)
            self.assertEqual(english_issues, [])
            return target_issues

    def test_accepts_canonical_chinese_translation(self) -> None:
        self.assertEqual(self.validate(CHINESE_PAGE), [])

    def test_rejects_noncanonical_english_source_before_translation_check(self) -> None:
        source = ENGLISH_PAGE.replace("## Key Takeaways", "## key takeaways")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "Sample.md"
            target_path = root / "Sample.zh.md"
            source_path.write_text(source, encoding="utf-8")
            target_path.write_text(CHINESE_PAGE, encoding="utf-8")
            english_issues, target_issues = validator.validate_translation(
                source_path, target_path
            )
        self.assertIn("heading-case", {issue.rule for issue in english_issues})
        self.assertTrue(target_issues)

    def test_requires_fixed_chinese_section_titles(self) -> None:
        issues = self.validate(CHINESE_PAGE.replace("## 要点总结", "## 要点"))
        self.assertIn("translated-section-contract", {issue.rule for issue in issues})

    def test_requires_fixed_walkthrough_titles_and_order(self) -> None:
        content = CHINESE_PAGE.replace("#### 目的", "#### 讲解目的")
        issues = self.validate(content)
        self.assertIn("shader-walkthrough-subsections", {issue.rule for issue in issues})

    def test_requires_full_deqp_path_and_fixed_parameter_table(self) -> None:
        content = CHINESE_PAGE.replace("dEQP-VK.memory.sample.first", "memory.sample.first")
        content = content.replace("| 参数选择 | 在此代表性用例中的含义 |", "| 选择 | 含义 |")
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-parameter-path", rules)
        self.assertIn("shader-walkthrough-parameter-table", rules)

    def test_requires_fixed_variation_table_and_evidence_link(self) -> None:
        content = CHINESE_PAGE.replace(
            "| 参数维度 | 相对此 shader 的 shader 层面变化 | 证据 |",
            "| 参数维度 | GLSL 变化 | 证据 |",
        ).replace("[源码](source.cpp#L1)", "源码")
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-variation-table", rules)

    def test_requires_chinese_spirv_metadata_and_summary(self) -> None:
        content = CHINESE_PAGE.replace("- 状态：", "- Status:").replace(
            "<summary>点击展开 SPIRV asm 代码</summary>",
            "<summary>Click to expand SPIRV asm code</summary>",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-spirv-metadata", rules)
        self.assertIn("shader-walkthrough-spirv-details", rules)

    def test_requires_fixed_cause_analysis_labels(self) -> None:
        content = CHINESE_PAGE.replace("**可能的失败表现：**", "**失败表现：**")
        issues = self.validate(content)
        self.assertIn("cause-analysis-label", {issue.rule for issue in issues})

    def test_detects_structural_omission(self) -> None:
        content = CHINESE_PAGE.replace("- host 检查结果。", "host 检查结果。")
        issues = self.validate(content)
        self.assertIn("translated-section-structure", {issue.rule for issue in issues})

    def test_requires_fixed_no_prerequisite_sentence(self) -> None:
        content = CHINESE_PAGE.replace(
            "本页不需要额外的前置概念。", "本页面无需额外背景。"
        )
        issues = self.validate(content)
        self.assertIn("no-prerequisite-sentence", {issue.rule for issue in issues})

    def test_requires_matching_multishader_h5_stage_identity(self) -> None:
        source = ENGLISH_PAGE.replace(
            "#### Shader Code\n\n```glsl",
            "#### Shader Code\n\n##### Compute Shader\n\n```glsl",
        ).replace(
            "#### SPIR-V\n\n- Status:",
            "#### SPIR-V\n\n##### Compute SPIR-V\n\n- Status:",
        )
        target = CHINESE_PAGE.replace(
            "#### Shader 代码\n\n```glsl",
            "#### Shader 代码\n\n##### Fragment Shader\n\n```glsl",
        ).replace(
            "#### SPIR-V\n\n- 状态：",
            "#### SPIR-V\n\n##### Fragment SPIR-V\n\n- 状态：",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "Sample.md"
            target_path = root / "Sample.zh.md"
            source_path.write_text(source, encoding="utf-8")
            target_path.write_text(target, encoding="utf-8")
            english_issues, issues = validator.validate_translation(
                source_path, target_path
            )
        self.assertEqual(english_issues, [])
        self.assertIn("translated-multishader-h5", {issue.rule for issue in issues})


class TranslationStructureValidatorCliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_accepts_multiple_categories_and_matches_english_summary_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wiki_dir = root / "english"
            target_dir = root / "chinese"
            for category in ("api", "compute"):
                source = wiki_dir / "testfiles" / category / "Sample.md"
                target = target_dir / category / "Sample.md"
                source.parent.mkdir(parents=True)
                target.parent.mkdir(parents=True)
                source.write_text(ENGLISH_PAGE, encoding="utf-8")
                target.write_text(CHINESE_PAGE, encoding="utf-8")

            result = self.run_cli(
                "api",
                "compute",
                "--wiki-dir",
                str(wiki_dir),
                "--target-dir",
                str(target_dir),
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"PASS {wiki_dir / 'testfiles' / 'api'}", result.stdout)
        self.assertIn(f"PASS {wiki_dir / 'testfiles' / 'compute'}", result.stdout)
        self.assertIn("Total checked category count 2, page count 2.", result.stdout)
        self.assertIn(
            "Failure category count 0, page count 0, finding count 0.",
            result.stdout,
        )

    def test_reports_category_page_and_findings_like_english_validator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wiki_dir = root / "english"
            target_dir = root / "chinese"
            source = wiki_dir / "testfiles" / "api" / "Sample.md"
            target = target_dir / "api" / "Sample.md"
            source.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            source.write_text(ENGLISH_PAGE, encoding="utf-8")
            target.write_text(
                CHINESE_PAGE.replace("## 要点总结", "## 要点"),
                encoding="utf-8",
            )

            result = self.run_cli(
                "api",
                "--wiki-dir",
                str(wiki_dir),
                "--target-dir",
                str(target_dir),
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(f"FAIL {wiki_dir / 'testfiles' / 'api'}", result.stdout)
        self.assertIn("     Sample.md:", result.stdout)
        self.assertIn("     - [translated-section-contract]", result.stdout)
        self.assertIn("Total checked category count 1, page count 1.", result.stdout)
        self.assertIn(
            "Failure category count 1, page count 1, finding count 1.",
            result.stdout,
        )

    def test_files_mode_infers_matching_chinese_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wiki_dir = root / "english"
            target_dir = root / "chinese"
            source = wiki_dir / "testfiles" / "api" / "Sample.md"
            target = target_dir / "api" / "Sample.md"
            source.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            source.write_text(ENGLISH_PAGE, encoding="utf-8")
            target.write_text(CHINESE_PAGE, encoding="utf-8")

            result = self.run_cli(
                "--files",
                str(source),
                "--wiki-dir",
                str(wiki_dir),
                "--target-dir",
                str(target_dir),
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"PASS {wiki_dir / 'testfiles' / 'api'}", result.stdout)
        self.assertIn("Total checked category count 1, page count 1.", result.stdout)

    def test_reports_empty_category_without_treating_it_as_an_invocation_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wiki_dir = root / "english"
            target_dir = root / "chinese"
            (wiki_dir / "testfiles" / "empty").mkdir(parents=True)
            (target_dir / "empty").mkdir(parents=True)

            result = self.run_cli(
                "empty",
                "--wiki-dir",
                str(wiki_dir),
                "--target-dir",
                str(target_dir),
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"PASS {wiki_dir / 'testfiles' / 'empty'}", result.stdout)
        self.assertIn("Total checked category count 1, page count 0.", result.stdout)

    def test_rejects_unknown_category_with_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wiki_dir = root / "english"
            target_dir = root / "chinese"
            (wiki_dir / "testfiles").mkdir(parents=True)

            result = self.run_cli(
                "missing",
                "--wiki-dir",
                str(wiki_dir),
                "--target-dir",
                str(target_dir),
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Error: category directory not found:", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
