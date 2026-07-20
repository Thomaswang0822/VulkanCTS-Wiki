---
name: wiki-rewriter
description: Rewrites existing Vulkan CTS wiki pages from source-navigation notes into explanation-first technical documentation. This skill should be used when an old Level-2 category page or old Level-3 test-family page already exists and needs a new rewritten output page grounded in source links, mustpass/registration evidence, optional Understanding Briefs, and shader-analyzer/shader-disassembler walkthroughs.
---

# Wiki Rewriter

Rewrite existing Vulkan CTS wiki pages into reader-facing technical documentation that explains test intent, execution, validation, and failure meaning. Treat the old wiki page as a required source-navigation aid: use its links and inventory during study, but write the new page as explanation-first documentation.

## Scope

Use this skill for:
- rewriting an existing Level-3 test-family wiki page into a new shortened output file;
- rewriting an existing Level-2 test-category wiki page after related Level-3 rewrites stabilize;
- preparing an Understanding Brief before a complex Level-3 rewrite;
- coordinating `shader-analyzer` and `shader-disassembler` for representative shader walkthroughs;
- auditing rewritten English Vulkan CTS wiki pages for semantics, links, registration coverage, and naming.

Do not use this skill to create a wiki page from scratch for a new category or family. Require the old navigation-style page to exist first. Future scratch generation belongs to a later combined analyzer/rewriter workflow, not this skill.

## Required Inputs

Require or resolve:
- the existing wiki page to rewrite;
- the rewrite level: Level-2 category page or Level-3 test-family page;
- source links and related source files referenced by the old page;
- mustpass or registration evidence for the relevant test hierarchy;
- target output filename and destination directory.

If the old page is missing, stop and request the old wiki page or use the separate wiki-analysis workflow first.

## Reference Files

Load references as needed:
- `references/rewrite-outline-template.md` when starting a category rewrite;
- `references/level3-template.md` for Level-3 output structure;
- `references/level2-template.md` for Level-2 output structure;
- `references/understanding-brief-template.md` when writing an Understanding Brief;
- `references/terminology-policy.md` before writing reader-facing hierarchy prose;
- `references/validation-checklist.md` before reporting completion;
- `references/pilot-examples.md` when a style or structure example is needed.

Keep template files as templates. Keep workflow decisions in this `SKILL.md`. Keep terminology and validation as separate concerns.

## Mandatory Language Worker Dependencies

This skill invokes the English language worker skills as mandatory quality gates for rewritten wiki prose.

Required global worker skills:

| Worker skill | Global install source | Purpose in this workflow |
|---|---|---|
| `humanizer` | `blader/humanizer` | Main English naturalness audit for rewritten wiki prose. |
| `stop-slop` | `hardikpandya/stop-slop` | Final English directness and residual AI-pattern pass. |

Before rewriting any user-facing page, confirm both worker skills are installed globally under `~/.agents/skills/`. Accept either
of these checks:

```bash
npx skills ls -g
```

or direct presence of:

```text
~/.agents/skills/humanizer/SKILL.md
~/.agents/skills/stop-slop/SKILL.md
```

If any required worker skill is missing, STOP before rewriting and ask the user to install the missing skill globally:

```bash
npx skills add blader/humanizer -g
npx skills add hardikpandya/stop-slop -g
```

The language workers are mandatory for every rewritten Level-2 and Level-3 user-facing English wiki page. 
They are language-quality passes only. 
They must not change factual claims, evidence scope, source links, registered paths, identifiers, code blocks, shader assembly, mustpass references, filenames, or Vulkan/CTS terminology that must remain exact.

## Output File Rules

Write rewritten output to a new file. Do not overwrite or delete the obsolete original page.

Naming:
- Level-2 output: keep snake_case category filename, for example `memory_model.md`.
- Level-3 output: shorten from source-style names such as `vktMemoryModelMessagePassing.md` to the useful family/source suffix, preserving CamelCase, for example `MessagePassing.md`.

Title:
- Omit the top `# File Title` in new rewritten pages. GitLab Wiki supplies a page title from the filename.
- Start rewritten Level-2 and Level-3 pages with `## Overview`.

Deletion boundary:
- Never remove obsolete original pages. User deletion is the final approval signal for that page.

## Workflow

### 0. Resolve category state and prepare rewrite outline

When the user asks to apply this skill to a category, first determine whether the category work is new, continued, or already rewritten.

State resolution:
- Check whether `external/vulkancts/wiki/internal_doc/{category_name}_rewrite_outline.md` exists.
  - If it exists, treat the request as continued work and proceed from the next unfinished page in the next planned batch.
- If no outline exists, inspect one or two representative Level-3 pages to see whether rewritten output pages already exist.
  - If rewritten pages already exist, report that the category appears to have been fully rewritten or previously started, and stop for user confirmation.
- If no outline exists and representative rewritten pages are absent, treat it as a new category and draft the outline before rewriting any page.

Write the outline under `external/vulkancts/wiki/internal_doc/` as `{category_name}_rewrite_outline.md`. Treat it as temporary internal documentation; remove it after the entire category rewrite finishes.

After drafting a new category rewrite outline, stop and report the outline path for user review. Do not inspect, brief, rewrite, or otherwise start work on any Level-3 page until the user approves the outline or explicitly asks to continue.

Load `references/rewrite-outline-template.md` and fill it in place. Follow its batching rules exactly; they keep difficult pages with
their Understanding Briefs and make category progress reviewable without embedding coordination rationale in user-facing work.

### 1. Inspect existing page and evidence

Read the old wiki page first. Extract:
- source files and source ranges already linked by the old page;
- registered category, test families, intermediate nodes, and test case leaves;
- parameter tables, generated artifact notes, shader/pipeline/resource clues, and validation clues;
- gaps where the old page lists files but does not explain behavior.

Then inspect source and mustpass evidence directly. Treat source and registration/mustpass evidence as authoritative; treat the old page as a navigation aid, not as final truth.

### 2. Classify the rewrite

For Level-3 pages, identify whether the old page covers:
- one implementation-bearing test family;
- multiple implemented test families owned by one source file;
- one family with meaningful intermediate nodes;
- a hybrid implementation plus registration file;
- a mechanical/simple delegated behavior.

Do not make ordinary rewritten Level-3 pages for pure registration-only category files. If the old page is registration-only, report that it should be represented by Level-2 navigation unless the user explicitly asks for a manual exception.

When a Level-3 page covers multiple test families, state the structural reason for grouping them: they are rooted in the same implementation file, or one is in-place while others are delegated to separate files. Do not describe the grouping using shader-content qualifiers such as "shader-heavy", because that conflates "uses shaders" with "is the primary implementation file" and creates ambiguity in translation.

For Level-2 pages, wait until relevant Level-3 rewritten pages are stable when possible. Use Level-2 pages as compact test category gateways, not smaller technical deep dives.

### 3. Decide whether an Understanding Brief is required

Create an Understanding Brief before the final Level-3 rewrite when any condition applies:
- shader-heavy behavior;
- generated GLSL, SPIR-V, HLSL, Amber, pipeline, resource-layout, or test-matrix artifacts;
- nontrivial host/device synchronization, resource lifetime, descriptor binding, queue, copyback, or validation behavior;
- a concept the user wants to learn or audit;
- inability to confidently summarize the core mechanism in a few sentences;
- direct rewriting risks producing source-navigation documentation.

Direct rewrite is allowed only for mechanical pages where the core property, execution flow, validation rule, important variants,
and failure meaning are clear. When a brief is written, its `## Behavior Parameter Identification` and `### Failure Cause Mapping`
table are prepared for user confirmation and later copy into the final page.

When a brief is required, write it from `references/understanding-brief-template.md`. Use the template as the document shape. Do not insert general workflow rationale into the brief itself.

Write the brief to the same directory as the target Level-3 page, using the naming convention `<Level3PageName>_brief.md`. For example, a brief for `testfiles/memory_model/MessagePassing.md` is written to `testfiles/memory_model/MessagePassing_brief.md`.

Before writing the brief, read the relevant Vulkan spec chapters at `external/vulkan-docs/src/chapters/` for the domain the test
exercises. This ensures the brief's Background Knowledge and Failure Cause Mapping are grounded in spec semantics, not just CTS
source structure.

After writing an Understanding Brief, stop only if the brief records unresolved risk points that affect final page semantics, representative walkthrough selection, or validation claims. If the brief's audit questions are resolved by inspected source, registration, mustpass, shader, or validation evidence, continue directly to the rewrite in the same task.

### 4. Rewrite Level-3 pages

Use the skeleton in `references/level3-template.md`. Scale sections by explanatory value:
- expand `Shader Analysis` for shader-heavy pages;
- expand `Runtime Execution and Result Checking` for host-behavior-heavy pages;
- expand `Failure Meaning` for pages with multiple distinct failure mechanisms;
- expand resource explanations for resource-heavy pages;
- keep simple pages short;
- do not force tables, diagrams, or long prose when they do not clarify the specific test.

For `## Background Knowledge` during initial Level-3 drafting:
- follow the prerequisite and section-boundary rules in `references/level3-template.md`;
- keep each page self-contained until the later category consolidation pass;
- distill any Understanding Brief teaching material instead of copying it verbatim;
- keep the heading and use the template's canonical no-prerequisite sentence when no bullets are needed.

For `## Registration Hierarchy`, keep the fenced tree parseable and exactly one level deep below its root:
- use the category-qualified Level-3 root path as the first line;
- list only direct children of that root;
- do not include nested descendants, `...`, or descriptive placeholder lines inside the tree;
- explain deeper test case leaves, generated ranges, and large matrices in the structure, parameter, or prose sections instead.

For `## Behavior Parameters`:
- identify the primary behavioral axis — the registered dimension whose values change what is being tested;
- use `### <parameter value name> — <very brief description>` subsections for each value of that axis;
- if an Understanding Brief exists, carry its `## Behavior Parameter Identification` conclusion into this section;
- configuration dimensions (data type, size, count, format, etc.) belong in `## Parameter Dimensions and Observed Values`, not here.

For `## Failure Meaning`:
- if an Understanding Brief exists, copy its `### Failure Cause Mapping` table directly into `### Failure Cause Mapping`; do not
  craft a new table from scratch;
- write `### Cause Analysis` fresh during the rewrite — it is not carried from the brief;
- for each cause, state what specifically could go wrong (derived from the test's validation logic) and what could cause it in the
  implementation (only when grounded in Vulkan spec semantics, GPU architecture knowledge, or CTS source inspection);
- derive each page's failure analysis case by case from what that specific test exercises; do not apply preconceived assumptions
  about where bugs live (GPU hardware, driver, host);
- if not confident about an implementation-level claim, search the relevant Vulkan spec chapter at
  `external/vulkan-docs/src/chapters/` to verify before stating it; if still unverified, state that source-level investigation is
  needed rather than inventing a cause;
- scale the depth of `### Cause Analysis` to the number of distinct mechanisms; do not pad with empty subsections.

Focus every section on test behavior. Keep C++ details as supporting evidence. Move source-navigation material to the final source appendix.

### 5. Integrate shader walkthroughs

Keep `## Shader Analysis` in every Level-3 page.

When drafting a Level-3 page, handle `## Shader Analysis` in-place at the moment the section is reached:
- first decide whether shader code is part of the tested behavior;
- if shader code is not part of the tested behavior, state that briefly and do not create walkthrough subsections;
- if shader code is part of the tested behavior, select the representative CTS case or parameter path before drafting the section body;
- invoke `shader-analyzer` immediately for each selected walkthrough and insert its final output directly under `## Shader Analysis`;
- do not draft a placeholder walkthrough, hand-written shader reconstruction, or temporary shader explanation to be replaced later.

For representative shader walkthroughs:
- select exact CTS cases or parameter paths;
- use at most three walkthroughs, with one as the default;
- add a second or third only when materially different and central to the test;
- invoke `shader-analyzer` for each walkthrough;
- ensure each walkthrough's `#### Structural Design` uses a structured non-plain-text format: use Mermaid for flowchart-like or decision-tree logic, but allow tables, mappings, or other compact formats when they are clearer;
- ensure the final walkthrough contains the complete `#### SPIR-V` subsection returned by `shader-disassembler` unchanged;
- do not author, reformat, or replace SPIR-V output with prose or excerpts.

Use `shader-analyzer` auto mode only when the exact source file, builder function, target rewritten page, and insertion location are known. Otherwise use manual mode and stop at its confirmation checkpoint before continuing the Level-3 rewrite.

### 6. Rewrite Level-2 pages

Use the skeleton in `references/level2-template.md`.

Write Level-2 pages as category gateways:
- identify the shared testing theme;
- include the mandatory `## Background Knowledge` section;
- show the direct category hierarchy;
- explain how test families relate and differ at category level;
- route readers to rewritten Level-3 pages;
- avoid duplicating Level-3 matrices, shader walkthroughs, validation mechanics, feature gates, or source appendices.

Draft the ordinary gateway sections first, using the stabilized Level-3 pages to form the category-level view. After those sections
are drafted, run the category Background Knowledge consolidation pass:
- inspect the `## Background Knowledge` sections of all rewritten Level-3 pages in the category;
- identify repeated category-shared prerequisite concepts that are needed by multiple Level-3 pages;
- explain those shared concepts in the Level-2 `## Background Knowledge` section, following the same prerequisite boundaries used
  for Level-3 pages;
- preserve concise realistic examples when they materially improve the shared mental model;
- if no repeated category-shared prerequisites need explanation, write exactly:
  `No common prerequisite concepts need category-level explanation for this test category.`
- in Level-3 pages, add an upward link to the Level-2 background when shared concepts were consolidated;
- compact only the shared portion of Level-3 BGK items;
- preserve definitely page-local BGK bullets, including their titles and wording, unless a confirmed meaningful defect requires a
  minimal edit;
- for mixed shared/local bullets, remove or shorten only the shared explanation and keep the local consequence;
- do not rewrite a Level-3 `## Background Knowledge` section wholesale during consolidation.

### 7. Mandatory English language-worker pass

After the rewritten English page is technically complete and before final validation, invoke the required language worker skills in
this exact order:

1. `humanizer`
2. `stop-slop`

Use `humanizer` for the main naturalness audit. Use `stop-slop` as the final directness and residual AI-pattern pass. Follow each
worker skill's own instructions for how to perform its pass; this master skill only defines when the passes are required and the
project-specific boundaries below.

Project boundaries for both worker passes:
- Treat the target voice as plain, natural, professional technical English.
- Do not add personal voice, promotional tone, humor, rhetorical flourishes, or unsupported explanation.
- Preserve all protected technical content exactly: inline code, code fences, registered paths, source links, filenames, function
  names, shader identifiers, SPIR-V assembly, mustpass references, Vulkan/CTS terms, and evidence-backed claims.
- Prefer conservative edits when a wording change could alter technical meaning or traceability.
- If a worker-suggested wording conflicts with source evidence, registration evidence, shader/SPIR-V facts, or validation logic,
  reject that wording and keep the technically safer version.

The page is not complete until both worker passes have been applied.

### 8. Audit before completion

Apply `references/terminology-policy.md` to authored hierarchy prose.

Run `references/validation-checklist.md` before reporting completion. At minimum, check:
- semantic accuracy;
- behavior parameter identification is correct and matches the behavioral axis;
- failure cause mapping table aligns with behavior parameters;
- cause analysis states what could go wrong for every cause; implementation causes are grounded or flagged as needing investigation;
- no preconceived bug-location assumptions are present;
- registration/mustpass coverage;
- relative links;
- shader/SPIR-V handling when applicable;
- naming and title rules;
- obsolete-page preservation;
- mandatory `humanizer` and `stop-slop` passes completed.

For registration/mustpass coverage and relative links, run the canonical page- or category-scoped commands in
`references/validation-checklist.md`; manual inspection alone is insufficient. Re-run the relevant validator until it passes or
report the remaining failure explicitly.

Report the new output file path and any unresolved risk points. Do not delete old pages.
