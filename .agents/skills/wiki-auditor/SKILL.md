---
name: wiki-auditor
description: Audits explanation-first Vulkan CTS wiki pages produced by wiki-rewriter, corrects confirmed technical and explanatory defects in place, validates the edited pages, and writes a compact page-centered category audit summary. This skill should be used after Level-3 rewrites stabilize, before or after Level-2 synthesis, or whenever rewritten pages need low-burden expert review in sequential or parallel mode.
---

# Wiki Auditor

Audit rewritten Vulkan CTS wiki pages as an expert technical-writing professor. Verify technical truth and explanatory sufficiency, correct confirmed meaningful defects directly in the rewritten pages, and leave the user a compact findings summary rather than a transcript of the review reasoning.

Optimize for reducing human review burden. Treat rewritten pages as generally strong. Find consequential defects; do not perform another broad rewrite or optional polishing pass.

## Scope

Use this skill for:

- one rewritten Level-3 page;
- all rewritten Level-3 pages in one test category;
- a rewritten Level-2 category page after its Level-3 pages stabilize;
- a full rewritten category audit in sequential or orchestrated parallel mode;
- re-auditing pages after source or documentation changes.

Target explanation-first outputs created under [`wiki-rewriter`](../wiki-rewriter/SKILL.md), not first-version source-navigation pages created by the old wiki-analysis workflow.

Do not treat Understanding Briefs, obsolete navigation-style originals, rewrite outlines, or other internal tracking files as user-facing audit targets unless explicitly requested. Never delete obsolete originals.

If a requested page is still navigation-first rather than a rewritten output, stop and route it through `wiki-rewriter` instead of adapting this audit to the old page shape.

## Required Inputs

Resolve before auditing:

- target page or test category;
- rewritten Level-2 and/or Level-3 scope;
- implementation source cited by each page;
- registration and mustpass evidence;
- relevant Vulkan specification chapters for semantic claims;
- applicable rewrite templates and validation policy.

For a category audit, enumerate the complete target set before assigning work. Include every rewritten Level-3 page and the rewritten Level-2 page when present. Exclude files ending in `_brief.md` and files under `wiki/internal_doc/` from user-facing page ownership.

## References

Load these resources as needed:

- [`references/review-protocol.md`](references/review-protocol.md) for the professor model, meaningful-defect threshold, internal worksheet, editing policy, worker contract, and category summary template;
- [`../shader-analyzer/SKILL.md`](../shader-analyzer/SKILL.md) when a shader walkthrough's source-level reconstruction or explanation is defective;
- [`../shader-disassembler/SKILL.md`](../shader-disassembler/SKILL.md) for the canonical `#### SPIR-V` output contract whenever a page contains generated SPIR-V;
- [`../wiki-rewriter/references/level3-template.md`](../wiki-rewriter/references/level3-template.md) for Level-3 structure and section semantics;
- [`../wiki-rewriter/references/level2-template.md`](../wiki-rewriter/references/level2-template.md) for Level-2 gateway semantics;
- [`../wiki-rewriter/references/terminology-policy.md`](../wiki-rewriter/references/terminology-policy.md) for hierarchy terminology;
- [`../wiki-rewriter/references/validation-checklist.md`](../wiki-rewriter/references/validation-checklist.md) for mechanical and semantic completion gates.

Keep detailed review procedure in `references/review-protocol.md`. Keep orchestration and mandatory workflow decisions in this file.

## Core Review Rule

Apply two internal judgments to every load-bearing point:

1. Determine whether the point is technically true, properly scoped, and supported.
2. Determine whether the page itself explains the point clearly enough for a graphics/GPU-literate reader who understands general pipeline and shader concepts but may lack raw-Vulkan programming experience, Vulkan-specific API knowledge, and CTS internals.

Use the full target-reader definition in `references/review-protocol.md`. Require brief, page-specific explanations of Vulkan concepts needed for this test; do not require a general Vulkan tutorial.

Use all available expert knowledge. Do not pretend to forget Vulkan or CTS knowledge. Never treat the ability to infer an intended argument as proof that the page made that argument.

Do not expose the complete internal worksheet in normal results. Report only confirmed corrections, unresolved findings, validation failures, and requested audit coverage.

## Workflow

### 1. Resolve the target and execution mode

For one page, use page mode.

For a category, select:

- **Sequential mode:** process each Level-3 page one at a time when the category is small, only one agent is available, or source knowledge is strongly shared.
- **Orchestrated parallel mode:** assign non-overlapping Level-3 pages to workers when multi-agent execution is available and parallelism reduces elapsed work.

In parallel mode:

- assign each Level-3 page to exactly one worker;
- permit each worker to edit only its assigned page;
- prohibit workers from editing the combined audit summary;
- reserve Level-2 review, category validation, and summary ownership for the orchestrator;
- require workers to return the compact result contract from `references/review-protocol.md`.

Do not let convenience sampling replace the declared category audit. Audit every rewritten page in scope, varying depth according to complexity while preserving the same meaningful-defect threshold.

### 2. Run the mechanical gate

Before semantic edits, check the page against the applicable rewrite template and terminology policy.

At minimum verify:

- naming and title rules;
- required section order and applicable sections;
- mandatory `## Background Knowledge`, using the Level-3 no-prerequisite sentence or Level-2 no-common-concepts sentence when no
  bullets are needed;
- canonical registration hierarchy shape;
- exact registered identifiers;
- behavior parameter and failure mapping alignment;
- exact `shader-disassembler` output shape and target/header agreement when generated SPIR-V is present;
- local relative source links and GitHub `#L` fragments;
- absence of stale workflow text;
- preservation of obsolete originals.

Run the canonical page-scoped registration and link validators from `../wiki-rewriter/references/validation-checklist.md` for each
Level-3 page. Treat validator success as necessary but insufficient. Continue to professor review.

### 3. Audit category-shared Background Knowledge ownership

For a category audit where a rewritten Level-2 page exists, audit the Level-2 `## Background Knowledge` section before auditing
Level-3 BGK sections. Verify that it:
- contains the mandatory heading;
- explains repeated category-shared prerequisites needed by multiple Level-3 pages;
- uses the canonical no-common-concepts sentence from the Level-2 template when no shared prerequisite explanation is needed;
- preserves concise realistic examples when they materially improve the category-level mental model;
- avoids Level-3 setup, parameter matrices, validation mechanics, expected results, and failure meaning.

Then audit each Level-3 BGK section against that shared owner:
- verify local sufficiency from the Level-3 page alone when the Level-2 BGK uses the no-common-concepts sentence, or from the
  Level-3 page plus the linked Level-2 BGK when an upward link exists;
- identify repeated shared concepts that should be consolidated upward instead of patched independently on many pages;
- preserve definitely page-local BGK bullets, including titles and wording, unless a confirmed meaningful defect requires a minimal
  edit;
- for mixed shared/local bullets, shorten only the shared explanation and preserve the local consequence;
- do not rewrite a Level-3 `## Background Knowledge` section wholesale during audit.

If the Level-2 page is not in the audit scope yet, audit Level-3 BGK for local sufficiency only and record repeated shared concepts
as a category-level follow-up rather than forcing cross-page consolidation prematurely.

### 4. Build the evidence-derived reference model

Read the page and inspect authoritative evidence near cited ranges and relevant surrounding control flow.

Derive the compact reference model defined in `references/review-protocol.md`. Focus on:

- core purpose and registered scope;
- required knowledge prerequisites relative to the target-reader baseline;
- primary behavioral axis or groups;
- parameter-to-mechanism relationships;
- generated artifacts and bound resources;
- host/device execution;
- observable result and actual pass condition;
- support checks and pruning;
- failure-localization limits;
- representative walkthrough coverage.

Use current source and registration/mustpass evidence as authoritative. Use relevant Vulkan specification chapters for Vulkan semantic and implementation-cause claims. Treat existing wiki prose and historical test plans as non-authoritative context.

Keep this reference model transient. Do not write it into the page or category summary.

### 5. Review load-bearing claims and knowledge prerequisites

Apply the truth, exposition, and knowledge prerequisite tests from `references/review-protocol.md`.

Audit `## Background Knowledge` first in both directions:

1. **Completeness:** derive the prerequisites needed by later behavior, shader, runtime, validation, pruning, or failure explanations;
   compare them with the target-reader baseline; and verify that each missing concept is explained with enough brief relevance to
   support the later reasoning.
2. **Responsibility boundary:** classify each existing item and remove or relocate content that has become concrete test setup,
   parameters, execution, expected results, correctness contracts, conclusions, failure meaning, unused tutorial material, or
   substantive duplication of `## Overview` and `## Key Takeaways`.

Preserve concise realistic examples that materially improve the required mental model. Also preserve a bounded ordinary-use versus
unconventional-test-use contrast when the ordinary concept would otherwise mislead the reader, but require it to stop after the
unusual relationship and its interpretive consequence. Do not reject content merely because it uses an example or briefly mentions
this test. Follow the detailed classification and editing rules in `references/review-protocol.md`.

Then check whether necessary concepts are explained adequately near first use elsewhere. A syntax form, API name, or dictionary
definition is insufficient when it leaves the causal role unclear. Do not duplicate adequate explanations or add general Vulkan
teaching material.

Prioritize claims and prerequisite gaps whose failure would change the reader’s mental model. Pay particular attention to:

- broad words such as `all`, `every`, `only`, `always`, `exactly`, and `required`;
- conditional support or generated subsets;
- behavior parameters mislabeled as configuration dimensions;
- comparison tolerances, masks, aggregation, and pass/fail strength;
- host/device chronology and resource roles;
- failure causes stated more strongly than validation can localize;
- representative walkthroughs presented beyond their actual coverage;
- explanations understandable only by opening source links;
- contradictions between behavior, runtime, failure, pruning, and takeaway sections.

Apply the meaningful-defect threshold. Ignore optional improvements that do not materially affect correctness or comprehension.

### 6. Correct confirmed defects in place

Edit the rewritten target page directly.

- Make the smallest evidence-backed correction, except where the generated-shader boundary below requires complete regeneration.
- Preserve exact identifiers, links, code fences, registered paths, and generated artifacts that are not being regenerated through their owning skill.
- Avoid broad restructuring and added tutorial material.
- Keep the established natural technical voice.
- Do not reopen already completed language-worker wording merely for stylistic preference.
- If a defect requires substantial re-analysis or broad rewriting rather than a surgical correction, report it as unresolved and route the page back through `wiki-rewriter`.
- If evidence remains uncertain after reasonable inspection, leave the point unchanged and record an unresolved finding.

Treat each shader walkthrough as a generated unit. Follow the mandatory `Generated shader boundary` decision table in
`references/review-protocol.md`; it determines whether to edit prose, regenerate a complete walkthrough, regenerate only the SPIR-V
subsection, or leave the artifact unchanged as unresolved. Never hand-edit generated or CTS-authored SPIR-V assembly.

After each edit or complete generated-unit replacement, reread dependent sections and correct any inconsistency introduced or exposed
by the change.

### 7. Revalidate the page

Rerun the page-scoped registration and link validators after edits. Fix validator failures only when the correction remains semantically accurate.

Return compact findings using the worker contract when operating under an orchestrator. Report `no-confirmed-issues` when no meaningful defect was found.

### 8. Aggregate category-level patterns

After all Level-3 pages finish, inspect worker results or sequential findings for repeated patterns.

Before writing page-specific findings for a recurring issue, first check whether the same root-cause defect appears across multiple pages and should be treated as a category-level pattern. If the same defect appears on 3 or more pages with the same evidence-backed Mistake and Correction, consolidate it into the category summary instead of repeating it page by page.

Check whether a finding indicates:

- a shared helper was misunderstood across pages;
- one comparison or support rule was repeatedly overstated;
- repeated behavior/failure mapping defects;
- a Level-2 synthesis assumption is now wrong;
- a generated-artifact or shader-target convention was misapplied across pages;
- further pages require re-audit.

Expand or repeat affected page reviews when a shared defect pattern is confirmed. Do not merely mention a systemic problem while leaving known affected pages uncorrected.

### 9. Audit the Level-2 page

Audit Level-2 only after Level-3 pages in scope stabilize.

Verify that it:

- represents the direct category hierarchy accurately;
- includes the mandatory `## Background Knowledge` section with either shared prerequisites or the canonical no-common-concepts
  sentence;
- routes each family or conceptual area to the correct rewritten Level-3 page;
- explains family relationships at category level;
- reflects corrected Level-3 meanings;
- avoids duplicating Level-3 mechanisms, matrices, validation details, or shader walkthroughs.

Edit confirmed defects in place and validate its links.

### 10. Run category validation

After all page edits, run the canonical category-scoped registration and link validators from
`../wiki-rewriter/references/validation-checklist.md`. Exclude Understanding Briefs from semantic target accounting even when a
glob includes them in link validation.

Rerun until validation passes or record the remaining limitation compactly.

### 11. Write the combined audit summary

For a category audit, write:

```text
external/vulkancts/wiki/internal_doc/<category>_audit_summary.md
```

Make the orchestrator or sequential lead the sole writer.

Use the exact page-centered structure in `references/review-protocol.md`:

- create one `## <page>.md` section for each page with resolved or unresolved findings;
- place all findings under that page;
- append `(UNRESOLVED)` to unresolved finding headings;
- consolidate defects recurring across 3 or more pages into `## Recurring Defect Patterns` before the page-specific sections, and list pages whose only finding is a recurring pattern under `## Pages With Only Recurring Findings`;
- collect all pages without confirmed issues under `## Pages With No Confirmed Issues`;
- do not create separate global resolved and unresolved sections;
- omit internal worksheets, passed claim inventories, severity, confidence, and verbose validator logs.

For a single-page audit, do not create a category summary unless requested. Return compact findings directly.

## Completion Criteria

Complete a page audit only when:

- mechanical checks have been applied;
- load-bearing claims have undergone truth and exposition review;
- confirmed meaningful defects have been edited in place;
- uncertain points remain unchanged and are reported as unresolved;
- page-scoped validators pass or their limitation is reported.

Complete a category audit only when:

- every rewritten Level-3 page in declared scope has one completed owner result;
- repeated defect patterns have been handled;
- the Level-2 page has been audited when present;
- category validators pass or remaining limitations are recorded;
- the page-centered audit summary has been written by one owner.

## Final Report

Keep the task completion response brief. Report only:

- audited scope;
- paths edited;
- category audit summary path, when applicable;
- validator result;
- unresolved findings, if any.

Do not repeat the summary contents or narrate the full review process.
