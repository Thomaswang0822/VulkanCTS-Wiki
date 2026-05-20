---
name: wiki-auditor
description: Performs skeptical semantic audits of generated Vulkan CTS wiki documentation against repository evidence. This skill should be used after wiki pages are generated or modified, especially for category-level and per-test-file documentation, to find false claims, overclaims, stale statements, hierarchy mistakes, unsupported parameter claims, and source-link evidence mismatches beyond what validators can catch.
---

# Wiki Auditor

## Overview

Perform evidence-first semantic audits of Vulkan CTS wiki documentation by comparing each generated wiki claim against the corresponding source files, test-plan text, mustpass registration paths, and validation scripts.

Use this skill to answer the question: "Does the wiki say anything that the inspected source does not actually prove?" Treat link validation and registration validation as necessary but insufficient; the core work is skeptical source-vs-wiki reading.

## Relationship to Other Skills

Use this skill after wiki authoring skill [`wiki-analyzer`](../wiki-analyzer/SKILL.md) has generated or updated documentation. This skill does not replace generation; it audits finished or draft wiki pages for semantic correctness.

When auditing Vulkan CTS wiki pages, preserve the factual scope used by `wiki-analyzer`:

- Rely on `external/vulkancts/` and `doc/testspecs/VK/apitests.adoc` for factual claims.
- Prefer inspected code over existing wiki prose.
- Require source links for important claims.
- Use GitHub fragment syntax in wiki source links: `file.cpp#L82` or `file.cpp#L82-L95`.
- Treat colon-style source line links in wiki pages as invalid: `file.cpp:82` is not acceptable.

## Core Principle

Audit meaning, not presentation.

Do not stop after checking broken links, duplicate headings, or validator output. Those checks are useful final guards, but semantic audit requires reading generated wiki files beside their corresponding source files and identifying statements such as:

- "The page claims X, but source line Y shows Z."
- "The page implies all cases do X, but the loop/guard only applies to a subset."
- "The registration tree says child A exists here, but source constructs child B or places A under a different root."
- "The page says this feature is required, but the code only checks it conditionally."
- "The page says verification compares every byte, but source masks selected low bits before comparison."
- "The page still contains stale workflow text that became false after later generated files were added."

## Audit Triggers

Apply this skill when asked to:

- Review generated wiki documentation for correctness.
- Audit a category after workers or another agent generated Level-2 and Level-3 pages.
- Check whether wiki claims are source-backed.
- Find actual documentation errors rather than only run validators.
- Verify that documentation follows a harness after generation.
- Perform a skeptical source-vs-wiki review before marking a category complete.

## Required Inputs

Identify or derive these inputs before starting:

1. Target wiki scope: one page, one test-file directory, or one full category.
2. Source scope: the source files cited by the wiki pages and registration files that define hierarchy.
3. Harness rules: applicable wiki conventions, especially hierarchy, link, evidence, and validation requirements.
4. Validation commands: category-scoped link and registration validators when available.

If scope is ambiguous and cannot be inferred from files or the user's request, ask for the target category or wiki paths before auditing.

## Workflow

### Step 1: Enumerate the Complete Audit Set

List every wiki file in scope before reading details. For a category audit, include:

- The Level-2 category page.
- Every Level-3 page under the category's `testfiles/{category}/` directory.
- Relevant tracker or README rows only if the task includes progress tracking.

Do not sample only representative files unless the user explicitly requests sampling. For a full category audit, every generated Level-3 page and the Level-2 page must be audited.

### Step 2: Map Wiki Pages to Source Evidence

For each wiki page, map major sections to source evidence:

- Overview and role → registration source, file comments, test-plan references.
- Registration hierarchy → factory functions, `TestCaseGroup` construction, `addChild()` calls, loops, guards, and mustpass paths.
- Test families → direct children in the hierarchy tree plus deeper generated cases.
- Parameter dimensions → enums, arrays, structs, vectors, loops, name builders, skip conditions.
- Support requirements → `checkSupport()` methods, runtime `NotSupportedError` branches, feature/extension checks, queue/device creation helpers.
- Verification methods → pass/fail checks, comparisons, shader result validation, buffer/image copy readbacks, fences, semaphores, metadata/property checks.
- Notes and uncertainties → statements about omissions, generated scope, helper files, device-group roots, or incomplete work.

Open source files at cited lines and nearby context. If a source link points to a broad range, inspect enough surrounding code to verify the claim, not just the linked line.

### Step 3: Audit Registration Semantics

Verify the documented tree against actual registration code.

Check:

- Root group name from `TestCaseGroup(testCtx, "name")`, `createTestGroup(...)`, or equivalent.
- Direct child names from one level below the documented root.
- Conditional children guarded by preprocessor macros or runtime conditions.
- Device-group roots that reuse common builders.
- Nested subgroup files that may deserve separate Level-3 pages under the documentation harness.

For Level-3 hierarchy trees, enforce one canonical parseable root unless the active harness explicitly allows more. If one source file registers multiple top-level roots, document one canonical tree and describe the additional roots in prose or tables, or follow the project-specific convention for multi-root files.

### Step 4: Audit Parameter Claims

Trace every parameter claim to code constructs.

Verify:

- Image types, buffer types, formats, sizes, sample counts, operations, flags, operands, queue counts, semaphore counts, and device-group variants.
- Skip logic, such as YCbCr alignment filters, Vulkan SC guards, unsupported image types, feature gates, or conditional extra formats.
- Claims using words like `all`, `every`, `only`, `same`, `always`, `fully`, `strict`, `exactly`, and `required`.

Treat broad wording as suspicious. Rewrite broad statements to narrower statements when the source only proves a subset.

### Step 5: Audit Support and Feature Gates

Compare support sections against `checkSupport()` and runtime checks.

Distinguish:

- Compile-time or registration guards.
- Static per-case support checks.
- Runtime checks inside `iterate()` or helper setup.
- Conditional feature checks for specific formats, operands, sample counts, queue families, device groups, or memory types.
- Shared helper requirements inherited from base classes.

Avoid writing that a feature is required for the whole page when the code requires it only for a format, operand, or branch.

### Step 6: Audit Verification Claims

Inspect the actual pass/fail logic.

Check whether verification is:

- Host-visible byte comparison.
- Masked byte comparison rather than exact comparison.
- Integer, fixed-point, or floating-point comparison with tolerances.
- Shader output or rendered-image comparison.
- Fence or semaphore wait result.
- Property/metadata comparison.
- Conditional on strict sparse-residency behavior.

Ensure the wiki does not claim verification happens when the source only prepares resources, logs images, or relies on successful API calls.

### Step 7: Audit Stale or Workflow-Derived Text

Look for statements created during earlier drafting stages that may have become false after later work, such as:

- "The Level-2 summary is not created yet."
- "This is an initial page."
- "Other files are not complete."
- "The full category has not been audited."
- Temporary worker coordination notes in user-facing docs.

Remove or update stale text before completion.

### Step 8: Fix Confirmed Errors

Edit only confirmed issues. For each fix, preserve evidence links or add better links.

Prefer precise wording such as:

- "Observed in the inspected source..."
- "The regular root documents...; the device-group root is registered separately with the same direct children..."
- "The code requests N generic queues, then filters duplicate sparse-queue handles, so distinct non-sparse queues can be fewer than N."
- "The comparison masks selected low bits before comparing."

Do not invent missing source evidence to support a claim. If a plausible behavior is not proven, say it is not confirmed from inspected files or omit it.

### Step 9: Run Validators After Semantic Fixes

Run validators only after manual semantic auditing and fixes. Use category-scoped validation when possible.

Typical Vulkan CTS wiki commands:

```bash
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose

python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category>
```

If validators fail, fix validation problems only after checking that the fix remains semantically accurate.

### Step 10: Report Audit Results

Report the audit as a source-backed review, not as a validator run.

Include:

- The complete list of audited pages.
- Confirmed false or unsupported claims found.
- For each correction: the previous claim, the source evidence, and the new corrected meaning.
- Pages where no confirmed semantic errors were found after source comparison.
- Validator results as secondary confirmation.

Avoid vague summaries like "I checked the files." Show concrete audit coverage and concrete findings.

## Error Categories

Use these categories when recording findings:

| Category | Meaning |
|---|---|
| False claim | Wiki states something contradicted by source. |
| Overclaim | Wiki uses broader wording than source proves. |
| Conditionality error | Wiki omits guards, skip logic, or feature conditions. |
| Registration mismatch | Wiki hierarchy/root/child does not match registration code or harness contract. |
| Verification mismatch | Wiki describes the wrong pass/fail mechanism or comparison strength. |
| Parameter mismatch | Wiki lists wrong values, counts, formats, sizes, operations, or generated names. |
| Stale workflow text | Wiki contains temporary or outdated drafting statements. |
| Unsupported claim | Wiki claim lacks inspected source/test-plan evidence. |

## Completion Criteria

Consider the audit complete only when:

- Every page in the declared scope has been compared against source evidence.
- Every major nontrivial claim has either source support, narrower wording, or removal.
- Registration trees match the harness contract and source registration semantics.
- Support/verification/parameter claims reflect conditional code paths.
- Temporary coordination text is absent from user-facing pages.
- Category-scoped link validation passes, unless a documented external issue is out of scope.
- Registration-path validation passes for documented trees, unless a documented validator limitation is out of scope.
- Final report distinguishes semantic audit findings from automated validation results.
