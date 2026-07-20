# Validation Checklist

Run this checklist before reporting a rewritten page as complete.

## Naming And Output

- [ ] Rewritten output is in a new file.
- [ ] Obsolete original page remains untouched.
- [ ] Level-2 filename keeps snake_case category style, such as `memory_model.md`.
- [ ] Level-3 filename is shortened CamelCase family/source suffix style, such as `MessagePassing.md`.
- [ ] Rewritten output page omits the top `#` title and starts at `## Overview`.

## Structural Audit

- [ ] Section order matches the Level-3 template: Overview → Background Knowledge → Registration Hierarchy → Parameter Dimensions and Observed Values → Behavior Parameters → Shader Analysis → Runtime Execution and Result Checking → Failure Meaning → Case Pruning → Key Takeaways → Source Reference Appendix.
- [ ] `## Parameter Dimensions and Observed Values` appears before `## Behavior Parameters`.
- [ ] `## Failure Meaning` appears between `## Runtime Execution and Result Checking` and `## Case Pruning`.

## Semantic Audit

- [ ] Core question or category purpose is clear.
- [ ] Test intent matches source behavior.
- [ ] Execution flow is understandable without source reading as the main path.
- [ ] Validation and pass/fail conditions are explicit.
- [ ] `## Background Knowledge` is present in every Level-3 page.
- [ ] Each Background Knowledge item is a necessary prerequisite outside the target-reader baseline and is consumed later.
- [ ] Background Knowledge stops before concrete setup, registered values, parameters, execution, expected results, correctness
  contracts, conclusions, and failure meaning.
- [ ] Background Knowledge has minimal substantive overlap with `## Overview` and `## Key Takeaways`.
- [ ] Realistic examples are concise, technically faithful, clearly illustrative, and materially improve the required mental model.
- [ ] Test-specific contrasts are used only when ordinary usage would otherwise mislead, and stop after the unusual relationship
  and its interpretive consequence.
- [ ] General tutorial material and unused prerequisites are absent.
- [ ] The canonical no-prerequisite sentence is used when no Background Knowledge bullets are needed.
- [ ] `## Behavior Parameters` identifies the primary behavioral axis with subsections for each value.
- [ ] `## Failure Meaning` exists with `### Failure Cause Mapping` and `### Cause Analysis`.
- [ ] Failure cause mapping table aligns with the behavior parameter values.
- [ ] Cause analysis states possible failure symptoms for every cause (derived from test validation logic).
- [ ] Each `####` cause uses the bold lead-in labels `**Possible failure symptoms:**` and `**Possible implementation causes:**`.
- [ ] Implementation causes are grounded in spec, architecture, or source; unverified causes are flagged as needing investigation.
- [ ] No preconceived bug-location assumptions (GPU hardware, driver, host) are present; analysis is derived case by case.
- [ ] C++ details support understanding instead of dominating it.
- [ ] No speculative hardware, driver, or Vulkan implementation claims are presented as facts.

## Registration And Mustpass Audit

- [ ] Registered identifiers are exact.
- [ ] Hierarchy shape matches source/mustpass evidence.
- [ ] Implemented test families are not omitted.
- [ ] Delegated or registration-only areas are marked accurately.
- [ ] Pure registration-only source files are not turned into unnecessary Level-3 technical pages.
- [ ] Parameter values and test case names are exact.
- [ ] Registration validation script passes for the rewritten page or active category.

### Registration validation script

Use the existing wiki-analyzer validator from the repository root.

```bash
# Check one rewritten Level-3 wiki file.
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py \
  --wiki-file external/vulkancts/wiki/testfiles/<category>/<rewritten_page>.md

# Check all extracted paths for a category.
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category>
```

Redirect a command's output to an internal review file only when persistent diagnostics are needed.

Notes:

- Use single-file validation while rewriting one Level-3 page.
- Use category validation before considering a Level-2 + Level-3 category batch stable.
- The script reads the canonical `## Registration Hierarchy` tree in Level-3 pages.
- Trailing parenthesized notes on child lines are intended to be ignored by the parser.
- Special categories may dispatch to adapters under `registration_validators/`.

## Link Audit

- [ ] Wiki link validation script passes for the rewritten page or active category.
- [ ] Source-code line references use GitHub fragment syntax, such as `file.cpp#L82` or `file.cpp#L82-L95`.
- [ ] Colon-style source line references such as `file.cpp:82` are not present in wiki links.
- [ ] Relative links resolve from the owning markdown file's directory.
- [ ] Level-2 navigation links point to rewritten Level-3 pages when available.
- [ ] Links are attached to meaningful source functions, ranges, or purpose labels.
- [ ] Old source-inventory links were either used as evidence or deliberately omitted as irrelevant.

### Wiki link validation script

Use the existing wiki-analyzer validator from the repository root.

```bash
# Check one rewritten page.
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/testfiles/<category>/<rewritten_page>.md \
  --repo-root . \
  --verbose

# Check one active category scope.
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose
```

Redirect a command's output to an internal review file only when persistent diagnostics are needed.

Notes:

- Prefer category-scoped validation during active rewrite work.
- Whole-wiki validation is mainly for global cleanup after category pages are expected to resolve cleanly.
- The validator ignores external URLs, URI schemes, and anchor-only links.
- `--auto-fix` only rewrites colon-style source references to `#L` form; it does not repair broken relative paths or wrong filenames.

## Shader And SPIR-V Audit

Use when the page includes shader analysis.

- [ ] `## Shader Analysis` exists.
- [ ] No walkthrough is created when shader code is irrelevant.
- [ ] Each walkthrough corresponds to an exact CTS case or parameter path.
- [ ] No more than three representative walkthroughs are used.
- [ ] `shader-analyzer` produced the walkthrough material.
- [ ] Reconstructed GLSL/HLSL preserves source-generated `//` comments and uses concise wiki-authored `///` comments.
- [ ] Important resource facts appear near shader declarations when concise.
- [ ] Every walkthrough ends with a complete `#### SPIR-V` subsection in the exact generated-output shape from
  `../../shader-disassembler/SKILL.md`; its fields are not renamed, reordered, augmented, or replaced by prose.
- [ ] `shader-disassembler` generated the subsection from reconstructed GLSL or HLSL; the target comes from CTS shader build options,
  and `Target SPIRV version: spirv1.X` matches the assembly `; Version: 1.X` header.
- [ ] SPIR-V assembly is full, collapsed, fenced as `llvm`, and unmodified.

## Brief-to-Page Audit

Use when an Understanding Brief was created.

- [ ] Final page distills the brief rather than copying beginner scaffolding verbatim.
- [ ] Final Background Knowledge retains only necessary prerequisites, useful bounded examples, and necessary ordinary-to-special
  contrast bridges; detailed application is moved to the appropriate section.
- [ ] Brief's `### Failure Cause Mapping` table is copied directly into the final page's `### Failure Cause Mapping`.
- [ ] Brief's `## Behavior Parameter Identification` conclusion is carried into `## Behavior Parameters`.
- [ ] `### Cause Analysis` is written fresh during the rewrite, not carried from the brief.
- [ ] Brief source mapping becomes a focused source appendix.
- [ ] Important concrete examples become formal walkthroughs, tables, or concise explanations.
- [ ] Relevant Vulkan spec chapters were read before writing the brief.
- [ ] Risk points are resolved or reported.
