## Objectives

- Establish one canonical, user-facing hierarchy format for Level-3 wiki pages so nested registration paths can be derived reliably.
- Remove the need for script-only prefix snippets in user-facing documents.
- Use the hierarchy tree as the source from which [`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) derives the prefixes it validates.
- Track the migration and script refactor in a fixed, reviewable order.

## Agreed Direction

- [x] Use a single canonical hierarchy section in Level-3 wiki pages instead of keeping both `Registration Path` and `Test Hierarchy` with overlapping content.
- [x] Keep the source of truth user-facing rather than embedding script-only prefix lists in Level-3 pages.
- [x] Make the validator parse a documented hierarchy contract instead of inferring paths from arbitrary prose or inconsistent historical tree styles.
- [x] Migrate finished categories first, following the order in [`README.md`](../README.md).
- [x] Use a single-level-down hierarchy in each Level-3 page.
- [x] Make [`Test Families`](../testfiles/geometry/vktGeometryInputGeometryShaderTests.md) mirror each direct child from the hierarchy tree using exact registered subgroup names in subsection headers.

## Recommended Execution Order

1. Update the documentation contract first
   - Adjust the skill guidance in [`SKILL.md`](../../../.agents/skills/wiki-analyzer/SKILL.md).
   - Define exactly how the canonical Level-3 hierarchy section must look.
   - Clarify what is allowed, what is forbidden, and what depth is required for validation.

2. Normalize existing finished wiki pages next
   - Go through finished categories in the progress order defined in [`README.md`](../README.md).
   - Update Level-3 pages to the canonical hierarchy format.
   - Remove duplicated hierarchy sections and remove script-only prefix snippets.

3. Refactor the validator after the documentation corpus is ready
   - Refactor [`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) so it derives explicit validation prefixes internally from the canonical hierarchy tree.
   - Keep the parser conservative and diagnostics strong.

## Why This Order

- The script should target a stable contract, not a moving or inconsistent corpus.
- Refactoring the script first would either force temporary heuristics or require continued support for non-uniform legacy formats.
- Normalizing the docs first creates a clean input model and makes the validator implementation simpler, safer, and easier to maintain.

## Problem Summary

### Current wiki problems

- Many older Level-3 pages contain both a `Registration Path` section and a `Test Hierarchy` section with duplicated or overlapping information.
- Tree syntax is inconsistent across finished pages.
- Existing trees use mixed styles such as `+--`, `|--`, arrows, slashes, flat path forms, and prose-heavy hybrid structures.
- Many pages use shorthand that is human-friendly but not machine-reliable, such as:
  - `...`
  - optional suffix notation such as `[_rebind]`
  - phrases such as `same test names as ...`
  - category-qualified path lists instead of real tree structure
- Recent pages sometimes added explicit prefix snippets only for the validator, which works technically but pollutes user-facing documentation.

### Current script limitation

[`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) currently works best when it can find:
- explicit backticked full paths such as `category.subgroup.subgroup`
- simple root-tree entries in category pages
- category-specific extractor logic such as [`pipeline.py`](../../../.agents/skills/wiki-analyzer/scripts/registration_validators/pipeline.py)

This is sufficient for top-level validation and for some recent pages, but not for reliable nested validation across older finished categories.

## Canonical Level-3 Hierarchy Contract

### Intended source of truth

Each Level-3 page should have one canonical hierarchy section that is both:
- readable to humans
- parseable by the validator

Suggested heading:
- `## Registration Hierarchy`

Suggested content form:
- one fenced `text` block containing the canonical tree

### Core decisions currently agreed

- The tree root line includes the category-qualified Level-3 root path, for example `dynamic_state.general_state` or `geometry.input`.
- The `dEQP-VK` prefix is omitted because it is globally constant and not needed in wiki trees.
- The tree expands exactly one level below the Level-3 root.
  - If the Level-3 page documents a top-level group, the tree shows that root and its direct children.
  - If the Level-3 page documents a lower-level registered subgroup, the tree still shows that root and its direct children only.
- Additional user-facing notes may appear in trailing `()` on the same line, and the validator will ignore that parenthesized suffix.
- The tree must be fully expanded at that one-level-down depth; no omissions are allowed at that depth.
- Deeper structure is not represented in the canonical tree. Instead, it is explained in [`Test Families`](../testfiles/geometry/vktGeometryInputGeometryShaderTests.md) with subsection headers that begin with the exact registered child name.

### Required structural rules

- Use one tree style only.
- Prefer Unicode tree markers:
  - `├──`
  - `└──`
- Use consistent indentation for nesting.
- Each parseable node line should contain one registered node name only, optionally followed by a human-facing note in `()`.
- Node names should correspond to actual registered path components.
- The tree should be sufficient for the intended validation depth.

### Forbidden or unsupported shorthand inside the parseable tree

- `...`
- `[_suffix]`
- `same test names as ...`
- trailing `/`
- inline prose after the node name unless it is enclosed in trailing `()`
- mixed narrative stacks such as `api -> createApiTests -> createBufferTests -> buffer`
- category-qualified flat-path lists used as a substitute for a tree
- deeper-than-one-level expansion in the canonical hierarchy block

### Relationship with `Test Families`

`Registration Hierarchy` and `Test Families` work together:

- `Registration Hierarchy` gives the exact Level-3 root and its direct children only.
- `Test Families` is not removed.
- `Test Families` should mirror each direct child node from the hierarchy tree.
- Each subsection header in `Test Families` should begin with the exact registered subgroup name, followed by an optional human-readable description.

Recommended pattern:
- `### basic_primitive — Basic primitive expansion`
- `### triangle_strip_adjacency — Triangle-strip-adjacency vertex-count sweep`
- `### conversion — Primitive-type conversion`

This keeps the tree compact and parseable while still giving readers the deeper semantic explanation they need.

### Handling human explanation

Human explanation is still welcome, but it should live outside the parseable tree block except for brief trailing notes in `()`.
Examples:
- short notes below the tree
- prose describing conditional registration
- prose describing repeated generation patterns
- evidence links pointing to source code
- deeper subgroup discussion in `Test Families`

### Handling large or generated trees

Even when a subtree is very large, the canonical hierarchy rule remains:
- fully expand the direct children of the Level-3 root
- do not compress or omit any direct child at that depth
- move deeper expansion and semantic explanation into `Test Families`

## Observations From Sampled Finished Pages

### More parseable example

[`vktDynamicStateGeneralTests.md`](../testfiles/dynamic_state/vktDynamicStateGeneralTests.md) is relatively close to the target style because the tree is compact and explicit.

### Examples showing duplication or style drift

- [`vktApiBufferTests.md`](../testfiles/api/vktApiBufferTests.md)
- [`vktMemoryAllocationTests.md`](../testfiles/memory/vktMemoryAllocationTests.md)
- [`vktSynchronizationBasicSemaphoreTests.md`](../testfiles/synchronization/vktSynchronizationBasicSemaphoreTests.md)
- [`vktRenderPassTests.md`](../testfiles/renderpasses/vktRenderPassTests.md)
- [`vktGeometryInputGeometryShaderTests.md`](../testfiles/geometry/vktGeometryInputGeometryShaderTests.md)
- [`vktGeometryBasicGeometryShaderTests.md`](../testfiles/geometry/vktGeometryBasicGeometryShaderTests.md)
- [`vktGeometryEmitGeometryShaderTests.md`](../testfiles/geometry/vktGeometryEmitGeometryShaderTests.md)
- [`vktGeometryBuiltinVariableGeometryShaderTests.md`](../testfiles/geometry/vktGeometryBuiltinVariableGeometryShaderTests.md)

These examples confirm that the corpus must be normalized before the validator should rely on hierarchy parsing.

## Validator Refactor Goals

After documentation normalization, refactor [`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) with these goals:

- parse only the canonical hierarchy contract
- derive explicit validation prefixes internally
- remain conservative rather than guessing from arbitrary prose
- produce strong diagnostics for malformed or unsupported hierarchy blocks
- preserve category-specific extraction hooks only where semantics differ structurally, not where formatting was historically inconsistent

## Validator Refactor Shape

### Internal responsibilities to separate

- mustpass file discovery
- candidate wiki file discovery
- hierarchy section extraction
- tree parsing into path prefixes
- validation against mustpass TXT files
- diagnostics and CLI reporting

### Expected diagnostics

- missing canonical hierarchy section
- malformed tree indentation
- unsupported shorthand token in parseable tree
- ambiguous or invalid node line
- extracted prefix list in verbose mode
- verification failures with source file and line references when possible

### Compatibility stance

A temporary compatibility layer may be acceptable during migration, but the desired end state is:
- canonical hierarchy tree as the primary source
- old explicit-path or ad hoc extraction logic retired where possible

## Migration Scope and Order

Follow the finished-category order from [`README.md`](../README.md):

- [ ] `info`
- [ ] `api`
- [ ] `memory`
- [ ] `synchronization`
- [ ] `synchronization2`
- [ ] `query_pool`
- [ ] `binding_model`
- [ ] `pipeline`
- [ ] `shader_object`
- [ ] `renderpasses`
- [ ] `dynamic_state`
- [x] `geometry`

For each finished category:
- [ ] review all Level-3 pages in the category
- [ ] merge duplicated `Registration Path` and `Test Hierarchy` content into one canonical hierarchy section
- [ ] normalize tree markers, indentation, root qualification, and node-line rules
- [ ] keep the tree single-level-down and fully expanded at that depth
- [ ] adjust `Test Families` so subsection headers mirror the exact child names from the tree
- [ ] move deeper expansion and explanatory prose into `Test Families`
- [ ] remove script-only prefix snippets from user-facing pages
- [ ] note any category-specific structural edge cases for the validator refactor

Geometry test-set result:
- [x] reviewed all geometry Level-3 pages
- [x] merged duplicated hierarchy sections into canonical `Registration Hierarchy`
- [x] normalized geometry tree roots and one-level-down child lists
- [x] aligned `Test Families` headings with exact direct child names
- [x] resolved the layered-registration edge case by escalating back to [`wiki-analyzer`](../../../.agents/skills/wiki-analyzer/SKILL.md) and confirming child names from [`createLayeredRenderingTests()`](../../../external/vulkancts/modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1996-L2079)
- [x] used geometry as the Phase-2 test set for validating the `wiki-normalizer` harness

## Planned Work Breakdown

### Phase 1: Contract definition

- [x] Update [`SKILL.md`](../../../.agents/skills/wiki-analyzer/SKILL.md) to define the canonical Level-3 hierarchy section
- [x] Record allowed syntax, forbidden syntax, and expected validation depth
- [x] Align related workflow documentation with the new contract in the skill guidance

### Phase 2: Wiki normalization of finished categories

- [ ] Normalize finished categories in [`README.md`](../README.md) order
- [ ] Keep user-facing readability while enforcing parseable structure
- [ ] Track exceptions or special cases discovered during migration

### Phase 3: Validator refactor

- [ ] Refactor [`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) around canonical hierarchy parsing
- [ ] Reduce reliance on explicit inline path extraction from prose
- [ ] Retain category-specific handlers only where structurally justified
- [ ] Improve diagnostics and verbose reporting

### Phase 4: Verification and cleanup

- [ ] Run the refactored validator on all finished categories
- [ ] Fix any remaining malformed hierarchy pages
- [ ] Remove transitional compatibility logic if no longer needed
- [ ] Confirm the final workflow is documented clearly for future category work

## Open Questions To Resolve During Implementation

- [x] Final heading name for the canonical section: `## Registration Hierarchy`
- [x] Expected validation depth: exactly one level below the Level-3 root
- [x] Parenthesized note handling: trailing `()` notes are user-facing and ignored by the parser
- [ ] Exact indentation contract for parser implementation details
- [ ] Exact allowed character set for registered node names in parseable lines
- [ ] Whether any dual-category file patterns need a documented exception strategy
- [ ] Whether some category-specific structures still justify adapters like [`pipeline.py`](../../../.agents/skills/wiki-analyzer/scripts/registration_validators/pipeline.py)
- [ ] How to map parser diagnostics back to exact markdown line numbers most usefully

## Progress

- [x] Initial analysis of current validator behavior completed
- [x] Confirmed nested-path validation gap in older finished pages
- [x] Confirmed explicit validator-only snippets are undesirable in user-facing docs
- [x] Agreed on the strategy of deriving validation prefixes internally from a standardized user-facing hierarchy tree
- [x] Agreed that the canonical tree is category-qualified, single-level-down, and fully expanded at that depth
- [x] Agreed that `Test Families` mirrors each direct child with exact subgroup-name subsection headers
- [x] Detailed internal refactor plan documented in this file
- [x] Phase 1 contract update completed in [`SKILL.md`](../../../.agents/skills/wiki-analyzer/SKILL.md)
- [x] Finished-category migration started
- [ ] Validator refactor started
- [ ] End-to-end validation across finished categories completed
- [x] Geometry finished as the Phase-2 normalization test set
- [x] `wiki-normalizer` fallback-to-`wiki-analyzer` rule added and validated against the layered-registration case
