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
- `references/level3-template.md` for Level-3 output structure;
- `references/level2-template.md` for Level-2 output structure;
- `references/understanding-brief-template.md` when writing an Understanding Brief;
- `references/terminology-policy.md` before writing reader-facing hierarchy prose;
- `references/validation-checklist.md` before reporting completion;
- `references/pilot-examples.md` when a style or structure example is needed.

Keep template files as templates. Keep workflow decisions in this `SKILL.md`. Keep terminology and validation as separate concerns.

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

Use this outline template and fill it in place:

```md
# {category} Rewrite Outline

## Scope

- Category: `{category}`
- Old Level-2 page: `external/vulkancts/wiki/categories/{category}.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/{category}/`
- Source category directory: `external/vulkancts/modules/vulkan/{source_category_dir}/`

## Page Count

- Old Level-3 pages found: {old_level3_count}
- Registration-only dispatcher pages to fold into Level-2: {dispatcher_fold_count}
- Implementation-bearing Level-3 pages to rewrite: {implementation_level3_count}
- Counted rewrite files for batching: {total_counted_files}
  - {brief_count} Understanding Briefs
  - {rewrite_page_count} rewritten Level-3 pages

## Dispatcher Decision

- `{dispatcher_source}.cpp` should NOT be rewritten because it is registration-only.
- Fold category-specific dispatcher facts into the rewritten Level-2 `{category}` page:
  - direct category tree;
  - subgroup names: `{subgroup_1}`, `{subgroup_2}`, ...;
  - source-to-family routing.

If the dispatcher mixes registration with implementation, replace the first bullet with:

- `{dispatcher_source}.cpp` should be rewritten because it has implementation in addition to registration.

## Batch 1 — {description}

Counted files: {batch_counted_files}

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `{old_level3_page}.md` | Yes/No | {brief_required_or_direct_rewrite_reason}. |

## Batch 2 — {description}

Counted files: {batch_counted_files}

(same table)

...

## Batch N — {description}

Counted files: {batch_counted_files}

(same table)

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `{category}.md` as the compact Level-2 category gateway.
- Include folded dispatcher information when the dispatcher is registration-only.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating detailed shader walkthroughs, parameter matrices, and validation mechanics from Level-3 pages.
```

Batching rules:
- each easy direct-rewrite page counts as 1 file;
- each difficult page with an Understanding Brief counts as 2 files: brief plus page;
- group pages into batches with at most 8 counted files where possible;
- batch count is normally `ceil(total_counted_files / 8)`;
- if the whole category has fewer than 8 counted files, use a single smaller batch;
- do not split a page from its Understanding Brief across batches.

Do not record context-window or commit-boundary rationale in the outline. Keep the outline concise and actionable.

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

For Level-2 pages, wait until relevant Level-3 rewritten pages are stable when possible. Use Level-2 pages as compact category gateways, not smaller technical deep dives.

### 3. Decide whether an Understanding Brief is required

Create an Understanding Brief before the final Level-3 rewrite when any condition applies:
- shader-heavy behavior;
- generated GLSL, SPIR-V, HLSL, Amber, pipeline, resource-layout, or test-matrix artifacts;
- nontrivial host/device synchronization, resource lifetime, descriptor binding, queue, copyback, or validation behavior;
- a concept the user wants to learn or audit;
- inability to confidently summarize the core mechanism in a few sentences;
- direct rewriting risks producing source-navigation documentation.

Direct rewrite is allowed only for mechanical pages where the core property, execution flow, validation rule, important variants, and failure meaning are clear.

When a brief is required, write it from `references/understanding-brief-template.md`. Use the template as the document shape. Do not insert general workflow rationale into the brief itself.

After writing an Understanding Brief, stop only if the brief records unresolved risk points that affect final page semantics, representative walkthrough selection, or validation claims. If the brief's audit questions are resolved by inspected source, registration, mustpass, shader, or validation evidence, continue directly to the rewrite in the same task.

### 4. Rewrite Level-3 pages

Use the skeleton in `references/level3-template.md`. Scale sections by explanatory value:
- expand `Shader Analysis` for shader-heavy pages;
- expand `Runtime Execution and Result Checking` for host-behavior-heavy pages;
- expand resource explanations for resource-heavy pages;
- keep simple pages short;
- do not force tables, diagrams, or long prose when they do not clarify the specific test.

For `## Registration Hierarchy`, keep the fenced tree parseable and exactly one level deep below its root:
- use the category-qualified Level-3 root path as the first line;
- list only direct children of that root;
- do not include nested descendants, `...`, or descriptive placeholder lines inside the tree;
- explain deeper test case leaves, generated ranges, and large matrices in the structure, parameter, or prose sections instead.

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
- ensure the final walkthrough includes the mandatory collapsed `#### SPIR-V` subsection generated by `shader-disassembler`;
- do not hand-edit SPIR-V assembly or replace it with excerpts.

Use `shader-analyzer` auto mode only when the exact source file, builder function, target rewritten page, and insertion location are known. Otherwise use manual mode and stop at its confirmation checkpoint before continuing the Level-3 rewrite.

### 6. Rewrite Level-2 pages

Use the skeleton in `references/level2-template.md`.

Write Level-2 pages as category gateways:
- identify the shared testing theme;
- show the direct category hierarchy;
- explain how test families relate and differ at category level;
- route readers to rewritten Level-3 pages;
- avoid duplicating Level-3 matrices, shader walkthroughs, validation mechanics, feature gates, or source appendices.

### 7. Audit before completion

Apply `references/terminology-policy.md` to authored hierarchy prose.

Run `references/validation-checklist.md` before reporting completion. At minimum, check:
- semantic accuracy;
- registration/mustpass coverage;
- relative links;
- shader/SPIR-V handling when applicable;
- naming and title rules;
- obsolete-page preservation.

Report the new output file path and any unresolved risk points. Do not delete old pages.
