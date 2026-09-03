---
name: wiki-writer
description: Writes source-backed Vulkan CTS wiki pages from scratch for clean test categories, including Level-2 gateways, Level-3 explanations, briefs, shader walkthroughs, and validation.
---

# Wiki Writer

Write high-quality, reader-facing Vulkan CTS wiki documentation from a fresh category. Build the page scope and every factual claim from current source, registration, mustpass, and—when relevant—Vulkan specification evidence. The final pages follow the explanation-first contracts in this skill's references.

This skill supports **scratch writing only**. The input category is clean: do not expect, require, inspect, rewrite, or preserve legacy wiki pages as source material. Existing repository navigation files may be read only to resolve naming or navigation context; they are never evidence for current test behavior.

## Scope

Use this skill to:

- document one fresh Vulkan CTS test category as one Level-2 gateway and its implementation-bearing Level-3 pages;
- discover the category's registration hierarchy and page boundaries directly from C++ source and mustpass files;
- prepare Understanding Briefs for complex pages;
- coordinate `shader-analyzer` and `shader-disassembler` for representative shader walkthroughs;
- apply the mandatory English language-quality passes;
- validate structure, links, registration coverage, and semantics before completion.

Do not create Level-3 pages for pure registration-only dispatchers or helper/utility files unless a file also contains meaningful implementation-bearing test behavior. Do not use this skill for legacy-page rewriting or repair.

## Required References

Before writing any page, read every file under `references/`:

- `references/outline-template.md` — category scope, page classification, and batching contract.
- `references/level3-template.md` — canonical Level-3 structure and Background Knowledge ownership.
- `references/level2-template.md` — canonical Level-2 gateway structure.
- `references/understanding-brief-template.md` — complex-page learning and risk-review shape.
- `references/terminology-policy.md` — hierarchy terminology and exact identifier rules.
- `references/validation-checklist.md` — completion assertions and validator commands.
- `references/pilot-examples.md` — accepted style and structure examples.

Each reference owns its detailed contract. This file owns scope, evidence, discovery, phase ordering, decisions, and completion gates.

## Evidence Contract

- Derive every nontrivial claim from inspected current source, registration/mustpass evidence, or directly relevant Vulkan specification text.
- Link important claims to concrete repository files and GitHub-style source fragments such as `file.cpp#L82` or `file.cpp#L82-L95`.
- Link registration claims to the registration function or construction site, and verification claims to the code that performs the check.
- Treat current source and mustpass as authoritative for exact registration paths, generated parameters, support gates, feature requirements, and verification behavior.
- Use `doc/testspecs/VK/apitests.adoc` only for relevant historical objective-level context. Never use it as evidence for current registration, parameters, support gates, or verification logic.
- Do not infer parameter ranges, universal coverage, or implementation causes beyond the inspected evidence. State uncertainty when a claim is plausible but unconfirmed.
- Preserve exact registered identifiers and technical Vulkan/GLSL terms.

## Mandatory Dependencies

For every user-facing English page, the current writing worker must load and apply these global language skills in order:

1. `humanizer`
2. `stop-slop`

They are prose-quality passes only. They must not alter evidence-backed facts, source links, registered paths, identifiers, code blocks, shader assembly, mustpass references, filenames, or required Vulkan/CTS terminology.

Use these helper skills when applicable:

- `shader-analyzer` for every selected representative shader walkthrough;
- `shader-disassembler` for the mandatory SPIR-V artifact under each walkthrough;
- `wiki-auditor` for the final source-vs-page semantic audit.

## Workflow

### 1. Resolve the fresh category

Confirm the category name, source directory, mustpass location, and target output directory. Read the user-facing `README.md` and `Objectives.md` for navigation and documentation scope, but do not use any existing wiki page as a content reference. Read relevant framework files only when making framework-level claims.

If the category is not clean or the task asks to rewrite an existing page, stop: this skill is scratch-only.

### 2. Discover the complete source and registration scope

Do not start from an old wiki inventory. Use the source-discovery process below so the page set is complete and registered names are exact:

1. Locate the category root registration file, usually `vkt{Category}Tests.cpp` or its verified equivalent.
2. Inspect its `#include` section first. Use included non-root, non-helper headers as the initial top-level branch index.
3. Inspect the root `createChildren()` or equivalent to confirm direct registration and conditional guards.
4. Follow each branch header to its factory declaration, then to the corresponding `.cpp` definition.
5. Find the actual registered group string in `TestCaseGroup` construction. Never treat a factory symbol or filename as the authoritative displayed name.
6. Trace nested registered subgroup files and their implementation-bearing behavior.
7. Inspect mustpass TXT files to confirm registered roots, direct children, variants, and category naming mappings.
8. Classify every discovered source file as implementation-bearing, hybrid, registration-only, or helper/utility.
9. Create a Level-3 page only for an implementation-bearing or hybrid scope that is meaningful to readers. Fold registration-only routing into Level-2; do not create helper-only pages.
10. Record the complete discovered scope in the outline before drafting pages.

Extract from implementation files:

- test families and meaningful intermediate nodes;
- all observable parameter dimensions and registered values;
- support checks, feature requirements, limits, and pruning;
- generated artifacts, resources, synchronization, execution flow, and result checking;
- exact failure symptoms and evidence-backed possible causes.

### 3. Create and approve the category outline

Write the temporary outline to:

```text
external/vulkancts/wiki/internal_doc/{category}_outline.md
```

Use `references/outline-template.md`. Preserve its batching rules: count each direct page as one file, count each page with an Understanding Brief as two files, keep batches at most eight counted files where practical, and never separate a brief from its page.

The outline must list:

- the verified root registration file and category mapping;
- every discovered branch and registered group name;
- every implementation-bearing/hybrid Level-3 page to write;
- every registration-only/helper file explicitly marked as no-page;
- the reason each Brief is or is not required;
- the planned batches and later Level-2 synthesis.

After creating a new outline, stop for user review. Do not write Level-3 or Level-2 pages until the user approves the outline or explicitly asks to continue.

Do not create progress trackers. `*_outline.md` is the only temporary coordination artifact; remove it, along with any temporary validator logs, after the category is complete.

### 4. Prepare Understanding Briefs when needed

Before a complex Level-3 page, read the relevant chapters under `external/vulkan-docs/src/chapters/` and write `<Level3PageName>_brief.md` beside the target page using `references/understanding-brief-template.md`.

Use a Brief for shader-heavy, generated-artifact, resource-layout, synchronization, descriptor, pipeline, or otherwise nontrivial behavior, or whenever the behavior axis and failure mapping are not yet clear. A direct write is appropriate only when intent, execution, primary behavior axis, validation, pruning, and failure meaning are already unambiguous.

Resolve Brief risk points before final writing. Distill its teaching material into the final page; carry its confirmed behavior-axis conclusion and `Failure Cause Mapping` table, but write `Cause Analysis` fresh.

### 5. Write Level-3 pages

Use `references/level3-template.md` exactly. Start with `## Overview`; omit a top-level H1. Keep the page explanation-first and use source links as evidence rather than as the main narrative.

Use the final shortened CamelCase Level-3 filename convention established by the template and repository workflow. Do not use source extensions in wiki filenames. For hybrid files, explain implementation behavior and mark delegated registration-only branches accurately.

When `## Shader Analysis` requires walkthroughs:

- choose an exact registered path or parameter case;
- invoke `shader-analyzer` immediately and insert only its final output;
- use auto mode only when source file, builder, target page, and insertion location are confirmed; otherwise use manual mode and its confirmation checkpoint;
- include at most three materially distinct walkthroughs, each ending in the generated `#### SPIR-V` subsection;
- use the reviewed exception registry only for source-confirmed pages where shader code is absent or irrelevant.

### 6. Write the Level-2 gateway

After the planned Level-3 pages are stable, write `external/vulkancts/wiki/categories/{category}.md` using `references/level2-template.md`.

Use verified registered group names, fold registration-only dispatcher routing into the category structure, and link each concrete reader goal to a Level-3 page. Keep Level-2 concise: do not duplicate Level-3 shader walkthroughs, parameter matrices, runtime mechanics, or failure analysis.

Then perform the category Background Knowledge consolidation pass: move repeated prerequisites shared by multiple Level-3 pages into Level-2 and replace affected Level-3 material with the canonical upward-link sentence while preserving page-local prerequisites.

### 7. Apply language passes and validate

Once each page is technically complete, apply `humanizer` and then `stop-slop` in the current worker. Afterwards run all applicable validators from the repository root:

```bash
python3 .agents/skills/wiki-writer/scripts/verify_english_structure.py <category>
python3 .agents/skills/wiki-writer/scripts/verify_registration_paths.py <category>
python3 .agents/skills/wiki-writer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . --verbose
```

Use single-page variants while drafting. Fix failures at their actual scope and rerun. Then invoke `wiki-auditor` over the complete generated category scope, compare every claim against its cited source, correct confirmed semantic errors, and rerun registration and link validation.

### 8. Complete the category

Before reporting completion, verify that:

- every discovered implementation-bearing/hybrid page is present and every registration-only/helper file has no page;
- all pages follow the canonical templates and naming rules;
- source, registration, mustpass, and relevant spec evidence support the claims;
- the English language passes were applied in order;
- structure, registration, and link validators pass;
- the semantic audit is complete and any findings are reported as `claimed X, source showed Y, fixed to Z`;
- no internal outline, progress tracker, or temporary validator log remains;
- only then, if needed, user-facing README navigation is updated.

Report output paths, validator results, semantic findings, and unresolved risks. Do not claim completion on partial coverage.
