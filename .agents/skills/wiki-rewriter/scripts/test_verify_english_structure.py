from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify_english_structure.py")
SPEC = importlib.util.spec_from_file_location("verify_english_structure", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


STANDARD_SECTIONS = """## Overview

**Core question:** Does the test work?

## Background Knowledge

No additional prerequisite concepts are needed for this page.

## Registration Hierarchy

```text
memory.sample
├── first
└── second (registration only)
```

## Parameter Dimensions and Observed Values

None.

## Behavior Parameters

No meaningful behavioral axis.

## Shader Analysis

No shader is used.

## Runtime Execution and Result Checking

The host checks the result.

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

The result must match.

## Source Reference Appendix

- Source.
"""

VALID_WALKTHROUGH = """### Representative Shader Walkthrough 1

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

- The value is fixed for this representative case.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Case | Other cases change the written value. | [Source](source.cpp#L1) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
OpCapability Shader
OpMemoryModel Logical GLSL450
```

</details>"""


class EnglishStructureValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        validator.PAGES_WITHOUT_WALKTHROUGH.clear()
        validator.PAGES_WITHOUT_WALKTHROUGH["memory"] = {"Sample.md"}

    def tearDown(self) -> None:
        validator.PAGES_WITHOUT_WALKTHROUGH.clear()

    def validate(self, content: str, category: str = "memory"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Sample.md"
            path.write_text(content, encoding="utf-8")
            return validator.validate_page(path, category)

    def test_accepts_standard_level3_page(self) -> None:
        self.assertEqual(self.validate(STANDARD_SECTIONS), [])

    def test_requires_walkthrough_when_page_is_not_exempt(self) -> None:
        validator.PAGES_WITHOUT_WALKTHROUGH.clear()
        rules = {issue.rule for issue in self.validate(STANDARD_SECTIONS)}
        self.assertIn("shader-walkthrough-required", rules)

    def test_accepts_complete_walkthrough_when_page_is_not_exempt(self) -> None:
        validator.PAGES_WITHOUT_WALKTHROUGH.clear()
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        self.assertEqual(self.validate(content), [])

    def test_parameter_dimensions_section_is_optional(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "## Parameter Dimensions and Observed Values\n\nNone.\n\n", ""
        )
        self.assertEqual(self.validate(content), [])

    def test_rejects_title_unknown_heading_and_wrong_order(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "## Overview", "# Sample\n\n## Overview"
        ).replace(
            "## Background Knowledge", "## Custom Section\n\nText.\n\n## Background Knowledge"
        ).replace(
            "## Behavior Parameters\n\nNo meaningful behavioral axis.\n\n## Shader Analysis",
            "## Shader Analysis\n\nNo shader is used.\n\n## Behavior Parameters",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("no-h1-title", rules)
        self.assertIn("section-name", rules)
        self.assertIn("section-order", rules)

    def test_requires_failure_and_pruning_subsections(self) -> None:
        content = STANDARD_SECTIONS.replace("### Cause Analysis\n\n", "").replace(
            "### Design-based pruning\n\n", ""
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("failure-subsections", rules)
        self.assertIn("pruning-subsections", rules)

    def test_requires_cause_analysis_labels(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "**Possible implementation causes:** The implementation returned the wrong result.\n",
            "",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("cause-analysis-label", rules)

    def test_does_not_validate_registration_tree_semantics(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "memory.sample\n├── first\n└── second (registration only)",
            "not-a-category-root\n├── <placeholder>\n│   └── nested # comment",
        )
        self.assertEqual(self.validate(content), [])


    def test_walkthrough_requires_matching_spirv_subsection(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "No shader is used.",
            "### Representative Shader Walkthrough 1\n\nExplanation only.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-spirv", rules)

    def test_walkthrough_requires_exact_subsections_in_order(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "#### Purpose\n\nExercise the representative shader.\n\n"
            "#### Structural Design\n\n| Phase | Role |\n|-------|------|\n"
            "| Write | The shader writes one value. |",
            "#### Structural Design\n\n| Phase | Role |\n|-------|------|\n"
            "| Write | The shader writes one value. |\n\n"
            "#### Purpose\n\nExercise the representative shader.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-subsections", rules)

    def test_walkthrough_rejects_missing_and_duplicate_subsections(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "#### Additional Info\n\n- The value is fixed for this representative case.\n\n",
            "#### Purpose\n\nDuplicated purpose.\n\n",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-subsections", rules)

    def test_walkthrough_numbers_must_be_consecutive(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "No shader is used.",
            VALID_WALKTHROUGH.replace(
                "Representative Shader Walkthrough 1",
                "Representative Shader Walkthrough 2",
            ),
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-numbering", rules)

    def test_walkthrough_rejects_orphan_subsection(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "No shader is used.",
            "#### SPIR-V\n\nOrphan subsection.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-orphan-subsection", rules)

    def test_walkthrough_rejects_malformed_heading(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "No shader is used.",
            VALID_WALKTHROUGH.replace(
                "Representative Shader Walkthrough 1",
                "Shader Walkthrough 1",
            ),
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-heading", rules)

    def test_spirv_requires_disassembler_output_shape(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "<details>\n<summary>Click to expand SPIRV asm code</summary>\n\n"
            "```llvm\n; SPIR-V\n; Version: 1.0\n"
            "OpCapability Shader\nOpMemoryModel Logical GLSL450\n```\n\n"
            "</details>",
            "Assembly omitted.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-spirv-format", rules)

    def test_requires_parameter_path_and_canonical_parameter_table(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "Representative path:\n\n```text\ndEQP-VK.memory.sample.first\n```\n\n"
            "| Parameter choice | Meaning in this representative case |\n"
            "|------------------|-------------------------------------|\n"
            "| `first` | Selects the representative shader path. |",
            "Representative case: `memory.sample.first`.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-parameter-path", rules)
        self.assertIn("shader-walkthrough-parameter-table", rules)

    def test_all_headings_require_exactly_one_preceding_blank_line(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "No meaningful behavioral axis.\n\n## Shader Analysis\n\n"
            "### Representative Shader Walkthrough 1\n\n#### Parameter Values Chosen",
            "No meaningful behavioral axis.\n## Shader Analysis\n"
            "### Representative Shader Walkthrough 1\n\n\n#### Parameter Values Chosen",
        ).replace(
            "Exercise the representative shader.\n\n#### Structural Design",
            "Exercise the representative shader.\n\n\n#### Structural Design",
        )
        issues = self.validate(content)
        spacing_issues = [issue for issue in issues if issue.rule == "heading-spacing"]
        # Missing separators before the H2 and H3, plus two blank lines before
        # the first H4 and Structural Design, produce four independent findings.
        self.assertEqual(len(spacing_issues), 4)
        self.assertEqual(
            {issue.message.rsplit("; found ", 1)[-1] for issue in spacing_issues},
            {"0", "2"},
        )

    def test_heading_at_start_of_file_does_not_require_preceding_blank_line(self) -> None:
        self.assertNotIn(
            "heading-spacing",
            {issue.rule for issue in self.validate(STANDARD_SECTIONS)},
        )

    def test_first_walkthrough_subsection_rejects_intervening_prose(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "### Representative Shader Walkthrough 1\n\n#### Parameter Values Chosen",
            "### Representative Shader Walkthrough 1\n\nIntervening prose.\n\n"
            "#### Parameter Values Chosen",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-first-subsection", rules)

    def test_structural_design_rejects_plain_text_only(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "| Phase | Role |\n|-------|------|\n| Write | The shader writes one value. |",
            "The shader writes one value.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-structural-design-format", rules)

    def test_shader_code_accepts_direct_spirv_explanation(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "```glsl\n#version 450\nvoid main() {}\n```",
            "This direct SPIR-V case does not use GLSL or HLSL. CTS authors the module as SPIR-V assembly.",
        )
        self.assertEqual(self.validate(content), [])

    def test_shader_code_rejects_assembly_and_untyped_prose(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "```glsl\n#version 450\nvoid main() {}\n```",
            "```llvm\nOpCapability Shader\n```",
            1,
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-shader-code-assembly", rules)
        self.assertIn("shader-walkthrough-shader-code-format", rules)

    def test_additional_info_must_be_empty_or_use_bullets(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "- The value is fixed for this representative case.",
            "This is plain prose rather than a bullet.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-additional-info-format", rules)

    def test_additional_info_allows_more_than_three_bullets(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "- The value is fixed for this representative case.",
            "- Fact one.\n"
            "- Fact two.\n"
            "- Fact three.\n"
            "- Fact four for an unusually complex case.",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertNotIn("shader-walkthrough-additional-info-format", rules)

    def test_variation_summary_requires_canonical_linked_table(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace("[Source](source.cpp#L1)", "Source evidence")
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-variation-evidence", rules)

    def test_spirv_requires_metadata_and_details_wrapper(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace("- Stage: `comp`\n", "").replace(
            "<details>\n<summary>Click to expand SPIRV asm code</summary>\n\n",
            "",
        ).replace("\n\n</details>", "")
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-spirv-metadata", rules)
        self.assertIn("shader-walkthrough-spirv-details", rules)

    def test_spirv_requires_fresh_disassembly_header_shape(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace("; SPIR-V\n; Version: 1.0\n", "")
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-spirv-header", rules)

    def test_multishader_requires_matching_h5_stage_structure(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "```glsl\n#version 450\nvoid main() {}\n```",
            "##### Vertex Shader\n\n```glsl\n#version 450\nvoid main() {}\n```\n\n"
            "##### Fragment Shader\n\n```glsl\n#version 450\nvoid main() {}\n```",
        ).replace(
            "```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\nOpMemoryModel Logical GLSL450\n```",
            "##### Vertex Shader\n\n```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\nOpMemoryModel Logical GLSL450\n```\n\n"
            "##### Compute Shader\n\n```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\nOpMemoryModel Logical GLSL450\n```",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("shader-walkthrough-multishader-h5", rules)

    def test_multishader_accepts_mixed_glsl_and_direct_spirv_stages(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "```glsl\n#version 450\nvoid main() {}\n```",
            "##### Vertex Shader\n\n"
            "```glsl\n#version 450\nvoid main() {}\n```\n\n"
            "##### Fragment Shader\n\n"
            "This CTS fragment stage is generated directly as SPIR-V assembly "
            "and does not use GLSL or HLSL source.",
        ).replace(
            "```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\nOpMemoryModel Logical GLSL450\n```",
            "##### Fragment Shader\n\n"
            "```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\n"
            "OpMemoryModel Logical GLSL450\n```",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertNotIn("shader-walkthrough-multishader-h5", rules)

    def test_multishader_accepts_artifacts_for_all_mixed_source_stages(self) -> None:
        content = STANDARD_SECTIONS.replace("No shader is used.", VALID_WALKTHROUGH)
        content = content.replace(
            "```glsl\n#version 450\nvoid main() {}\n```",
            "##### Vertex Shader\n\n"
            "```glsl\n#version 450\nvoid main() {}\n```\n\n"
            "##### Fragment Shader\n\n"
            "This CTS fragment stage is generated directly as SPIR-V assembly "
            "and does not use GLSL or HLSL source.",
        ).replace(
            "```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\nOpMemoryModel Logical GLSL450\n```",
            "##### Vertex Shader\n\n"
            "```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\n"
            "OpMemoryModel Logical GLSL450\n```\n\n"
            "##### Fragment Shader\n\n"
            "```llvm\n; SPIR-V\n; Version: 1.0\nOpCapability Shader\n"
            "OpMemoryModel Logical GLSL450\n```",
        )
        rules = {issue.rule for issue in self.validate(content)}
        self.assertNotIn("shader-walkthrough-multishader-h5", rules)

    def test_rejects_wrong_case_for_fixed_headings(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "## Background Knowledge", "## Background knowledge"
        ).replace(
            "### Failure Cause Mapping", "### Failure cause mapping"
        ).replace(
            "No shader is used.",
            "### Representative Shader Walkthrough 1\n\n"
            "#### Parameter Values Chosen\n\nText.\n\n"
            "#### Purpose\n\nText.\n\n"
            "#### Structural Design\n\nText.\n\n"
            "#### Shader Code\n\nText.\n\n"
            "#### Additional Info\n\nText.\n\n"
            "#### Parameter Variation Summary\n\nText.\n\n"
            "#### Spir-v\n\nText.",
        )
        issues = self.validate(content)
        heading_case_messages = [
            issue.message for issue in issues if issue.rule == "heading-case"
        ]
        self.assertIn(
            "fixed heading must use exact spelling and case: ## Background Knowledge",
            heading_case_messages,
        )
        self.assertIn(
            "fixed heading must use exact spelling and case: ### Failure Cause Mapping",
            heading_case_messages,
        )
        self.assertIn(
            "fixed heading must use exact spelling and case: #### SPIR-V",
            heading_case_messages,
        )

    def test_rejects_wrong_case_for_walkthrough_heading_prefix(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "No shader is used.",
            "### Representative shader walkthrough 1\n\n"
            "#### Parameter values chosen\n\nText.\n\n"
            "#### Purpose\n\nText.\n\n"
            "#### Structural design\n\nText.\n\n"
            "#### Shader code\n\nText.\n\n"
            "#### Additional info\n\nText.\n\n"
            "#### Parameter variation summary\n\nText.\n\n"
            "#### SPIR-V\n\nText.",
        )
        issues = self.validate(content)
        rules = {issue.rule for issue in issues}
        self.assertIn("heading-case", rules)
        self.assertNotIn("shader-walkthrough-spirv", rules)

    def test_does_not_case_check_behavior_parameter_headings(self) -> None:
        content = STANDARD_SECTIONS.replace(
            "No meaningful behavioral axis.",
            "### opsdotkhr: signed dot product\n\nText.",
        )
        self.assertEqual(self.validate(content), [])

    def test_rejects_unclosed_fence(self) -> None:
        content = STANDARD_SECTIONS.rsplit("```", 1)[0]
        rules = {issue.rule for issue in self.validate(content)}
        self.assertIn("code-fence", rules)


if __name__ == "__main__":
    unittest.main()
