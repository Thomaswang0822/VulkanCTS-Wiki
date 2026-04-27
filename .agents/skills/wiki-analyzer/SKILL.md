---
name: "wiki-analyzer"
description: "Analyzes Vulkan CTS tests and generates evidence-backed hierarchical wiki documentation. Invoke when user wants to document test categories, test families, or understand test structure from code."
---

# Vulkan CTS Wiki Analyzer

This skill analyzes Vulkan CTS tests and generates structured wiki documentation derived from code and test-plan evidence.

## When to Invoke

Invoke this skill when:
- User wants to document a test category
- User wants to understand the structure of tests
- User wants to create or regenerate documentation for a category
- User wants evidence-backed summaries of test families, parameters, support gates, or verification methods

## Primary Goal

Build a navigable and extensible knowledge system that answers the questions in [`Objectives.md`](../../../external/vulkancts/wiki/Objectives.md) using verifiable repository evidence.

The skill is not just a template filler. It must derive claims from:
- source registration paths
- test creation functions
- parameter structs, enums, arrays, and loops
- support checks and feature requirements
- verification logic
- the official test plan when relevant

## Required Reading Before Starting

**CRITICAL**: Before starting documentation work, you MUST read:

1. [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md)
   - Check progress tracking
   - Confirm whether the category is already documented
   - Avoid duplicating or conflicting with existing work
   - Follow the category order in the Progress Tracking table unless the user explicitly requests a different category

2. [`external/vulkancts/wiki/Objectives.md`](../../../external/vulkancts/wiki/Objectives.md)
   - Defines the questions the documentation must answer
   - Defines the allowed scope

3. [`doc/testspecs/VK/apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc)
   - Use when it contains relevant authoritative purpose/context for the category
   - Do not force it into docs if the category is better explained directly from code

4. Relevant framework files when making framework-level claims
   - [`external/vulkancts/modules/vulkan/vktTestCase.hpp`](../../../external/vulkancts/modules/vulkan/vktTestCase.hpp)
   - [`framework/common/tcuTestCase.hpp`](../../../framework/common/tcuTestCase.hpp)

## Scope Rules

Per [`Objectives.md`](../../../external/vulkancts/wiki/Objectives.md), documentation may rely on:
- [`external/vulkancts/`](../../../external/vulkancts/)
- [`doc/testspecs/VK/apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc)

Do not rely on sources outside this scope for factual claims.

## Evidence Rules

1. **Evidence first**
   - Every nontrivial claim must be supported by inspected source or test-plan evidence.

2. **Code links are mandatory**
   - Link all important claims to concrete files and lines.
   - Registration claims must point to the function that registers the group or test family.
   - Verification claims must point to the code that performs the check or comparison.

3. **Do not overclaim**
   - Do not say "all features" unless the inspected code justifies that wording.
   - Do not infer parameter ranges unless they are visible in enums, arrays, loops, helper builders, or explicit generated names.
   - Do not claim a verification method unless it is visible in code or directly stated in authoritative documentation.

4. **Handle uncertainty explicitly**
   - If something is plausible but not proven from inspected files, say so.
   - Use wording such as "observed in inspected files" or "not confirmed from inspected files".

5. **Prefer code over existing wiki text**
   - Existing wiki pages can help with structure, but regenerated content must be derived from source again.

## Execution Model

### Preferred Unit of Work

Default target:

```text
One Run = 1 Category = 1 Level-2 Document + N Level-3 Documents
```

However, this is a workflow preference, not a hard constraint. Large categories may be handled in stages:
- analyze source files first
- draft/review Level-3 documents
- synthesize the Level-2 category document afterward

### Registration vs Implementation Files

Do not treat all `vkt*Tests.cpp` files the same.

There are at least two common Level-3 subtypes:

1. **Registration / dispatcher files**
   - Main value: subgroup structure, delegation, included source files, registration hierarchy

2. **Implementation-heavy test files**
   - Main value: test families, parameter dimensions, support requirements, verification methods, principles

Document them differently according to their role.

### Parallel Execution

If orchestration is available:
1. Identify the category registration file and all relevant implementation files
2. Split the category by top-level registered groups from the category root registration file
3. Launch workers per top-level group when helpful
4. Allow workers to create additional Level-3 pages for nested registered subgroup files under their assigned top-level group
5. Review worker output for unsupported claims and broken links
6. Create or update the Level-2 summary only after Level-3 evidence is stable

### Completion

After documentation is complete:
- update [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md) if the workflow uses progress tracking
- ensure links are correct relative to each document location
- ensure the category summary matches the actual registration tree

## Wiki Structure

```text
external/vulkancts/wiki/
├── README.md
├── Vulkan_CTS_Framework_and_Mechanism.md
├── categories/
│   ├── api.md
│   ├── geometry.md
│   └── ...
├── internal_doc/
│   ├── api_progress.md
│   ├── geometry_progress.md
│   └── ...
└── testfiles/
    ├── api/
    ├── geometry/
    └── ...
```

Do not hardcode category or file counts in generated docs unless you derive them from the current tree.

## Documentation Levels

## Level 2: Category Documentation

**Purpose**: Document one top-level Vulkan test category as a navigable summary backed by code.

**Naming**: `external/vulkancts/wiki/categories/{category_name}.md`

**Required contents**:
- H1 title
- Brief overview of what the category verifies
- Registration entry point with source link
- Subgroup structure derived from the registration file and verified implementation files
- File inventory, clearly distinguishing registration files from implementation files where useful
- Cross-file recurring test families or themes
- Cross-file recurring parameter dimensions
- Cross-file recurring support requirements or feature gates
- Cross-file recurring verification methods
- Links to Level-3 docs
- Notes on scope/uncertainty when appropriate

**Important**:
- The category doc must answer the category-level questions from [`Objectives.md`](../../../external/vulkancts/wiki/Objectives.md#L15).
- Keep it concise, but not so compressed that it loses traceability.
- Level-2 pages are user-facing wiki documents. Do not place temporary worker-coordination material or internal progress tables in them.
- Avoid using factory-symbol names such as `create*Tests()` as displayed subgroup identifiers in Level-2 pages unless the symbol itself is the subject of a code-reference claim. The user-facing identifier should be the verified registered group name.

## Internal Category Progress Trackers

**Purpose**: Support temporary master/worker coordination while a category is being documented.

**Location**: `external/vulkancts/wiki/internal_doc/{category}_progress.md`

**Lifecycle**:
- Create when active coordination is needed for a category
- Update during analysis and writing
- Remove after the category work is complete, if the tracker is no longer useful

**Indexing rule**:
- Use header/source filenames as the initial tracker index because they are easy and robust to enumerate from the category root file includes.
- Do not use inferred subgroup names derived from factory symbols as the initial tracker key.
- After inspecting the implementation file, record the verified registered group name separately if needed.

**Important**:
- These internal trackers are not user-facing documentation.
- Keep temporary planning notes, worker assignment notes, and partial verification state here rather than in Level-2 category docs.

## Level 3: CPP Test File Documentation

**Purpose**: Document the tests represented by one source file.

**Which files get Level-3 docs**: Create Level-3 wiki for a file **if and only if** it registers tests (has a registration path in the test tree). Pure utility/helper files that provide infrastructure without registering any tests do not get their own Level-3 pages.

**Naming**: `external/vulkancts/wiki/testfiles/{category}/{cpp_filename}.md`

**Required contents**:
- H1 title
- Overview
- Role of file: registration file or implementation file
- Source code link
- Other inspected related files if relevant
- Registration path
- Test hierarchy as observed from creation/registration code
- Test families with evidence-backed descriptions
- Parameter dimensions and observed values/ranges
- Support/feature requirements
- Verification methods
- Test principles observed in the file
- Notes / uncertainties

**Formatting guidance**:
- Use ASCII trees for hierarchies
- Use tables for parameters when appropriate
- Stop at meaningful test-family granularity
- Do not explode to every generated test unless the file is small and the expansion helps understanding

Note: the workflow rules in this section are primarily about Level-2 category production. Level-3 standardization may follow different or additional rules later.

## Progress Counting Policy

Use two different concepts and do not mix them:

1. **Tracker count**
   - For [`README.md`](../../../external/vulkancts/wiki/README.md), count only the top-level groups registered directly by the category root registration file.
   - This is the official progress number.
   - Do not count nested subgroup files in this tracker number.

2. **Writing scope**
   - When documenting the category, create Level-3 pages for any separately meaningful registered group file, including nested subgroup files when they exist as their own registration/documentation units.
   - In other words, writing may be broader than the official tracker count.

### How to identify top-level groups for counting

For a category, start from its root registration file and count the groups added directly there.

- Example for `api`: inspect [`createApiTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiTests.cpp#L86).
- Example for `geometry`: inspect [`createChildren()`](../../../external/vulkancts/modules/vulkan/geometry/vktGeometryTests.cpp#L41).
- Example for `info`: inspect [`createInfoTests()`](../../../external/vulkancts/modules/vulkan/vktInfoTests.cpp#L260).

This counting step is about how many top-level registered children the category has, not about how to name them in user-facing text.

### How to determine the correct group name

Do not assume the displayed group name from the factory symbol passed to `addChild()`. The common 1-to-1-to-1 correspondence between factory symbol, filename, and group name is only a heuristic, not a guarantee.

**Step-by-step discovery process:**

1. **Start from the category root registration file** (e.g., `vktGeometryTests.cpp`)
2. **Examine the include section** — identify headers that register test groups (exclude the file's own `.hpp` and utility headers)
3. **Navigate to each header file** — find the factory function declaration (e.g., `createVaryingGeometryShaderTests()`)
4. **Navigate to the corresponding `.cpp` file** — find the factory function definition
5. **Locate the group name** — look for `TestCaseGroup` construction with the string name:
   ```cpp
   MovePtr<TestCaseGroup> varyingGroup(new TestCaseGroup(testCtx, "varying"));
   ```
   The group name is `"varying"`.

**Optimization tip:** Factory function definitions are typically at the **end of the `.cpp` file**. When only extracting the group name, read from the end rather than loading the entire file (some files have thousands of lines).

**Verification via mustpass TXT files:**

After determining a group name, verify it against the mustpass definition files:

1. Locate the corresponding TXT file: `external/vulkancts/mustpass/main/vk-default/{category}.txt`
   - Note: Some categories map to multiple TXT files (e.g., `renderpass` and `renderpasses`)
2. Use [`scripts/verify_registration_paths.py`](scripts/verify_registration_paths.py) to check if the full registration path exists
3. The script searches for patterns like `api.copy_and_blit.core.blit_image` without loading the entire TXT file
4. Parent paths are verified incrementally: when verifying `blit_image`, assume `api.copy_and_blit.core` was already verified

**Important:** This verification is mandatory whenever documenting a group name in wiki pages.

### What not to use for tracker counts

Do **not** use any of the following as the official Level-3 count source:
- raw `.cpp` counts from the directory
- CMake source lists
- counts of all existing wiki pages under `testfiles/`
- counts of nested subgroup pages created during detailed documentation

Those sources can help discover material to inspect, but they are not the tracker rule.

### Worker-dispatch rule

When a category is large:
- use top-level branches from the category root registration file as the dispatch unit for worker sessions;
- in internal trackers, use filenames as the early indexing aid before the precise group names are verified;
- allow each worker to inspect and document nested subgroup files inside its assigned top-level branch;
- keep the official category count aligned only to the top-level registration structure so progress tracking stays simple and stable.

## Analysis Process

### Step 1: Read Prerequisites

1. Read [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md)
2. Read [`external/vulkancts/wiki/Objectives.md`](../../../external/vulkancts/wiki/Objectives.md)
3. Read [`doc/testspecs/VK/apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc) if relevant
4. Read framework files if making framework-level statements

### Step 2: Identify Category

Determine the target category from the user request or the test path.

### Step 3: Discover Source Files

Inspect the category directory under:

```text
external/vulkancts/modules/vulkan/{category}/
```

Identify:
- registration/aggregator files
- implementation files
- helper/util files that materially affect understanding

### Step 4: Trace Registration

Start from the category registration file and trace:
- top-level group creation
- subgroup creation functions
- delegation to implementation files

Use this step to identify the counted top-level branches. Do not finalize displayed group names until the corresponding implementation files are verified.

### Step 5: Build Internal Tracker if Needed

If the category is large or uses worker coordination:
1. create [`external/vulkancts/wiki/internal_doc/{category}_progress.md`](../../../external/vulkancts/wiki/internal_doc/)
2. list candidate top-level branches using filenames as the initial index
3. add verified group names only after checking the implementation file
4. keep temporary worker notes in this internal tracker, not in the Level-2 page

### Step 6: Analyze Implementation Files

For each implementation file:
1. identify major test families
2. extract parameter dimensions from enums, arrays, structs, loops, and generated names
3. identify support checks and feature requirements
4. identify verification logic and result criteria
5. record uncertainties instead of guessing
6. verify the actual registered group names when the file constructs and returns subgroup objects

### Step 7: Write Level-3 Docs

Generate evidence-backed per-file documentation.

### Step 8: Write Level-2 Doc

Synthesize the category-level summary only after the Level-3 understanding is stable.
Use only verified group names in user-facing subgroup trees and navigation text.

### Step 9: Consistency Review

Before marking work complete, verify:
- all relative links are correct (run [`scripts/validate_wiki_links.py`](scripts/validate_wiki_links.py))
- all group names are verified (run [`scripts/verify_registration_paths.py`](scripts/verify_registration_paths.py))
- category docs match registration code
- displayed group names are verified from implementation where needed
- no temporary coordination material leaked into Level-2 pages
- no unsupported claims remain
- repeated statements are deduplicated
- wording matches inspected evidence strength

### Step 10: Update Progress Tracking

If the project is using [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md) as a tracker, update it after the consistency review.
When updating its `Level-3 Files` column, use the official top-level-group count and only fill it once the category is `✅ Done`.

## Key Principles

1. **CPP files are the primary anchor for Level-3 docs**
2. **Registration path matters**
3. **Evidence beats intuition**
4. **Level-3 docs are for files that register tests** — utility/helper files without registration paths do not get their own Level-3 pages
5. **Top-level-group counts are for tracking, not for limiting writing**
6. **Factory-symbol names are heuristics, not authoritative user-facing identifiers**
7. **Avoid factory function names in wiki content** — do not expose factory symbols like `createXxxTests()` in registration trees, tables, or hierarchy sections unless the symbol itself is the subject of a specific code-reference claim. Users who need to trace call stacks should use an IDE, not a wiki. Naming discrepancies between factory symbols and verified group names belong in Notes sections, not in primary tables or trees.
8. **Internal coordination belongs in temporary files, not in Level-2 wiki pages**
9. **No parameter explosion**
10. **Concise but traceable**
11. **Distinguish observed fact from interpretation**
12. **Use correct relative links from the current document location**
13. **Prefer regeneration from source over editing around old wiki mistakes**

## Quality Checklist

Before finishing a category, confirm:
- every important claim has a source link
- registration file and subgroup tree are documented correctly
- user-facing Level-2 pages use verified subgroup names rather than inferred factory-symbol names
- temporary coordination material is stored only in [`wiki/internal_doc/`](../../../external/vulkancts/wiki/internal_doc/)
- parameter tables come from observable code constructs
- support gates are documented when present
- verification methods are documented only when evidenced
- links to Level-3 docs are correct from the category doc
- links to source files are correct from each Level-3 doc
- wording avoids unsupported universal claims
- [`scripts/validate_wiki_links.py`](scripts/validate_wiki_links.py) reports no broken links
- [`scripts/verify_registration_paths.py`](scripts/verify_registration_paths.py) confirms all group names
