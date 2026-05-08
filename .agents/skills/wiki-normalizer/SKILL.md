---
name: "wiki-normalizer"
description: "Normalizes existing Vulkan CTS Level-3 wiki pages to the canonical registration-hierarchy contract. Invoke together with [`wiki-analyzer`](../wiki-analyzer/SKILL.md) when migrating finished categories, removing duplicated hierarchy sections, restructuring `Test Families`, and preparing pages for parser-driven registration-path validation."
---

# Vulkan CTS Wiki Normalizer

This skill normalizes existing Level-3 Vulkan CTS wiki pages so they conform to the canonical documentation contract defined by [`wiki-analyzer`](../wiki-analyzer/SKILL.md).

It is a **companion skill**, not a replacement for [`wiki-analyzer`](../wiki-analyzer/SKILL.md).

## Primary Goal

Migrate existing user-facing Level-3 wiki pages under [`external/vulkancts/wiki/testfiles/`](../../../external/vulkancts/wiki/testfiles/) to the canonical structure required for Phase 2 of the registration-path refactor:
- one canonical `## Registration Hierarchy` section
- one-level-down, fully expanded hierarchy tree
- no duplicated `Registration Path` / `Test Hierarchy` structural content
- `Test Families` subsections aligned with the direct children from the hierarchy tree
- no script-only registration-prefix snippets in user-facing pages

The end state should leave the wiki corpus ready for parser-driven nested validation by [`verify_registration_paths.py`](../wiki-analyzer/scripts/verify_registration_paths.py).

## Relationship with [`wiki-analyzer`](../wiki-analyzer/SKILL.md)

### Division of responsibilities

[`wiki-analyzer`](../wiki-analyzer/SKILL.md) remains responsible for:
- source-backed factual understanding
- evidence rules and wording strength
- verified registration roots and group names
- category context and documentation intent
- support/verification/parameter analysis from code

This skill, `wiki-normalizer`, is responsible for:
- restructuring existing Level-3 wiki files to match the canonical contract
- removing duplicated legacy hierarchy sections
- rewriting hierarchy blocks into the canonical parseable form
- aligning `Test Families` headings with exact registered subgroup names
- preserving evidence-backed prose while improving structural consistency

### Required operating model

Use this skill **together with** [`wiki-analyzer`](../wiki-analyzer/SKILL.md).

Do not use this skill to invent new factual claims from source code independently when [`wiki-analyzer`](../wiki-analyzer/SKILL.md) has not already established the relevant registration structure and semantics.

If direct registered child names needed for the canonical `Registration Hierarchy` are unresolved from the currently available context, this skill must escalate that specific Level-3 page back to [`wiki-analyzer`](../wiki-analyzer/SKILL.md) for deeper source inspection.

If [`wiki-analyzer`](../wiki-analyzer/SKILL.md) still cannot confirm the direct child names after deeper re-analysis, stop normalization of that page and ask the user for manual intervention. Do not invent placeholder child names, semantic pseudo-nodes, or non-registered parseable tree entries just to satisfy the hierarchy contract.

## Scope

### In scope

- Existing Level-3 wiki pages under [`external/vulkancts/wiki/testfiles/`](../../../external/vulkancts/wiki/testfiles/)
- Finished categories only, following the order in [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md)
- Markdown structure normalization
- Canonical hierarchy-tree formatting
- `Test Families` subsection renaming and reshaping
- Relocating deeper hierarchy detail from parseable tree blocks into prose
- Removing validator-only explicit-prefix snippets from user-facing pages
- File-by-file migration discipline and review consistency

### Out of scope

- Writing new Level-2 category documents from scratch
- Refactoring [`verify_registration_paths.py`](../wiki-analyzer/scripts/verify_registration_paths.py)
- Changing mustpass semantics or validation policy
- Re-analyzing source files from zero when [`wiki-analyzer`](../wiki-analyzer/SKILL.md) has not been applied
- Adding unsupported claims or rewriting correct evidence-backed prose without need

## Required Inputs

Before normalizing a Level-3 page, confirm or obtain from [`wiki-analyzer`](../wiki-analyzer/SKILL.md):
- target file path
- category name
- confirmed Level-3 root registration path
- confirmed direct child subgroup names for the canonical hierarchy
- whether the file is a root-level branch page or a deeper registered subgroup page
- any category-specific or file-specific caveats
- any dual-category behavior or registration peculiarities

If these are not known, stop and use [`wiki-analyzer`](../wiki-analyzer/SKILL.md) first.

If the page can be partially understood but the exact direct child names remain unresolved, escalate that page to [`wiki-analyzer`](../wiki-analyzer/SKILL.md) for deeper inspection rather than proceeding with an approximate hierarchy.

## Canonical Level-3 Normalization Contract

This skill enforces the Level-3 contract documented in [`wiki-analyzer`](../wiki-analyzer/SKILL.md).

### Canonical hierarchy section

Each Level-3 page must contain exactly one canonical user-facing section:

```markdown
## Registration Hierarchy
```

This section replaces duplicated structural use of legacy `Registration Path` and `Test Hierarchy` sections.

### Canonical tree rules

The `Registration Hierarchy` section must contain one fenced `text` block with these rules:

1. The first line is the category-qualified Level-3 root path.
   - Example: `dynamic_state.general_state`
   - Example: `geometry.input`

2. The tree expands exactly one level below that root.
   - Show the direct children of the Level-3 root only.
   - Do not include grandchildren or deeper descendants in the parseable tree.

3. Fully expand every direct child at that depth.
   - No omissions.
   - No summary placeholders.

4. Use Unicode tree markers only.
   - `├──`
   - `└──`

5. Each child line contains the exact registered child name, optionally followed by a trailing note in `()`.
   - Example: `├── state_switch_mesh (non-VulkanSC only)`
   - Parenthesized notes are for users and should be ignored by the validator.

6. The global `dEQP-VK` prefix does not appear in wiki hierarchy trees.

### Forbidden hierarchy-tree content

Do not allow these inside the parseable hierarchy tree:
- `...`
- `[_suffix]`
- `same test names as ...`
- trailing `/`
- deeper-than-one-level expansion
- call-stack or factory-symbol narrative such as `createApiTests -> createBufferTests -> buffer`
- category-qualified flat path lists used instead of a real tree
- inline explanatory prose unless it is a trailing parenthesized note

## Relationship Between `Registration Hierarchy` and `Test Families`

Do not remove `## Test Families`.

Instead, use it as the place where each direct child from the canonical hierarchy is explained in detail.

### Required `Test Families` rules

- Each direct child from `Registration Hierarchy` must be represented in `Test Families`.
- Each subsection heading must begin with the **exact registered child name**.
- A human-readable description may follow after a separator.
- Deeper descendants, generated leaves, matrices, and semantic explanations belong here rather than in the parseable hierarchy tree.

Recommended heading pattern:

```markdown
### basic_primitive — Basic primitive expansion
### triangle_strip_adjacency — Triangle-strip-adjacency vertex-count sweep
### conversion — Primitive-type conversion
```

## Preservation Rules

This skill restructures pages, but must preserve valuable documentation content whenever it is valid.

Preserve unless correction is required:
- evidence-backed claims
- source links
- parameter tables
- support/feature requirement descriptions
- verification-method descriptions
- meaningful uncertainty notes
- file role descriptions

The goal is normalization, not simplification by deletion.

## Migration Strategy

### Required order

Migrate finished categories in the order defined in [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md):

1. `info`
2. `api`
3. `memory`
4. `synchronization`
5. `synchronization2`
6. `query_pool`
7. `binding_model`
8. `pipeline`
9. `shader_object`
10. `renderpasses`
11. `dynamic_state`
12. `geometry`

### Preferred unit of work

Default unit:

```text
One Run = 1 Level-3 wiki file normalization
```

For consistency-sensitive cases, a larger unit may be used:

```text
One Run = 1 finished category review + N coordinated Level-3 normalizations
```

## Normalization Workflow

### Step 1: Confirm prerequisites

Confirm the inputs listed above from [`wiki-analyzer`](../wiki-analyzer/SKILL.md).

### Step 2: Audit current page structure

Inspect the target page and identify:
- whether both `Registration Path` and `Test Hierarchy` exist
- whether they duplicate each other structurally
- whether the tree uses non-canonical markers or shorthand
- whether the root is unqualified or overly narrative
- whether deeper descendants are embedded in the parseable tree
- whether validator-only explicit-prefix snippets are present
- whether `Test Families` headings already map to direct children cleanly

### Step 3: Plan the transformation

Decide explicitly:
- which hierarchy sections will be merged or replaced
- what the canonical root path should be
- what the direct child list should be
- what deeper descendants should be moved into `Test Families`
- which subsection headings must be renamed
- what prose should remain unchanged

### Step 4: Normalize the page

Perform the structural migration:
- replace duplicated hierarchy sections with one canonical `Registration Hierarchy`
- rewrite the tree into the canonical one-level-down format
- remove unsupported shorthand from the parseable tree
- remove script-only prefix snippets from user-facing content
- rename `Test Families` subsections to begin with exact subgroup names
- move deeper hierarchy detail into prose where needed

If direct child names are unresolved at this step:
- pause normalization of that page
- invoke [`wiki-analyzer`](../wiki-analyzer/SKILL.md) for deeper source inspection of the specific file
- resume only if exact direct child names are confirmed
- otherwise stop and report that the page needs user intervention

### Step 5: Review the normalized page

Check that:
- the root path is correct
- direct children are complete and exact
- no forbidden shorthand remains in the parseable tree
- every direct child has a corresponding `Test Families` subsection
- evidence-backed prose was preserved
- the page still reads naturally for users
- relative links remain valid

## Review Checklist

Before considering a normalized Level-3 page complete, verify:
- one canonical `## Registration Hierarchy` section exists
- legacy duplicated structural hierarchy sections are removed or merged
- the root is category-qualified
- the hierarchy tree goes exactly one level down
- all direct children are present
- only `├──` and `└──` markers are used
- parser-ignored notes use trailing `()` only
- no invented semantic placeholders or non-registered parseable nodes remain in the hierarchy tree
- no `...`, `[_suffix]`, trailing `/`, or `same test names as ...` remains in the parseable tree
- any unresolved-child-name case was escalated to [`wiki-analyzer`](../wiki-analyzer/SKILL.md) before declaring the page complete
- `Test Families` mirrors the direct children with exact subgroup-name headings
- deeper descendants are explained in prose rather than kept in the parseable tree
- links remain valid
- no factual evidence was lost

## Common Anti-Patterns

Do not leave or introduce:
- both `Registration Path` and `Test Hierarchy` as parallel structural sections
- explicit validator-only prefix blocks in user-facing pages
- deep tree expansions inside the parseable hierarchy block
- shorthand placeholders in the hierarchy block
- human-friendly subsection headings that omit the exact subgroup name
- prose rewrites that weaken or distort evidence-backed claims
- file-local formatting experiments that diverge from the canonical contract

## Quality Gate

A normalized Level-3 page is successful when:
- it satisfies the canonical hierarchy contract from [`wiki-analyzer`](../wiki-analyzer/SKILL.md)
- it preserves user-facing clarity
- it preserves evidence-backed content
- it is structurally consistent with other migrated Level-3 pages
- it is ready for later parser-driven path extraction by [`verify_registration_paths.py`](../wiki-analyzer/scripts/verify_registration_paths.py)

## When to Escalate Back to [`wiki-analyzer`](../wiki-analyzer/SKILL.md)

Stop normalization and return to [`wiki-analyzer`](../wiki-analyzer/SKILL.md) when:
- the true Level-3 root path is uncertain
- the direct child list is uncertain
- existing prose appears factually unsupported or contradictory
- category-specific registration semantics are unclear
- the page may actually represent a different registration unit than currently documented

## Example Use Cases

This skill is particularly useful for legacy pages such as:
- [`vktApiBufferTests.md`](../../../external/vulkancts/wiki/testfiles/api/vktApiBufferTests.md)
- [`vktMemoryAllocationTests.md`](../../../external/vulkancts/wiki/testfiles/memory/vktMemoryAllocationTests.md)
- [`vktSynchronizationBasicSemaphoreTests.md`](../../../external/vulkancts/wiki/testfiles/synchronization/vktSynchronizationBasicSemaphoreTests.md)
- [`vktRenderPassTests.md`](../../../external/vulkancts/wiki/testfiles/renderpasses/vktRenderPassTests.md)
- [`vktGeometryInputGeometryShaderTests.md`](../../../external/vulkancts/wiki/testfiles/geometry/vktGeometryInputGeometryShaderTests.md)

These are exactly the kinds of pages where structural normalization and careful preservation must work together.
