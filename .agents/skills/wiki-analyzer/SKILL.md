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
2. Launch workers for Level-3 file analysis
3. Review worker output for unsupported claims and broken links
4. Create the Level-2 summary only after Level-3 evidence is stable

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
- Subgroup structure derived from the registration file
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

## Level 3: CPP Test File Documentation

**Purpose**: Document the tests represented by one source file.

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

This establishes the documentation skeleton.

### Step 5: Analyze Implementation Files

For each implementation file:
1. identify major test families
2. extract parameter dimensions from enums, arrays, structs, loops, and generated names
3. identify support checks and feature requirements
4. identify verification logic and result criteria
5. record uncertainties instead of guessing

### Step 6: Write Level-3 Docs

Generate evidence-backed per-file documentation.

### Step 7: Write Level-2 Doc

Synthesize the category-level summary only after the Level-3 understanding is stable.

### Step 8: Consistency Review

Before marking work complete, verify:
- all relative links are correct
- category docs match registration code
- no unsupported claims remain
- repeated statements are deduplicated
- wording matches inspected evidence strength

### Step 9: Update Progress Tracking

If the project is using [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md) as a tracker, update it after the consistency review.

## Key Principles

1. **CPP files are the primary anchor for Level-3 docs**
2. **Registration path matters**
3. **Evidence beats intuition**
4. **No parameter explosion**
5. **Concise but traceable**
6. **Distinguish observed fact from interpretation**
7. **Use correct relative links from the current document location**
8. **Prefer regeneration from source over editing around old wiki mistakes**

## Quality Checklist

Before finishing a category, confirm:
- every important claim has a source link
- registration file and subgroup tree are documented correctly
- parameter tables come from observable code constructs
- support gates are documented when present
- verification methods are documented only when evidenced
- links to Level-3 docs are correct from the category doc
- links to source files are correct from each Level-3 doc
- wording avoids unsupported universal claims
