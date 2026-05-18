---
name: "wiki-analyzer"
description: "Analyzes Vulkan CTS tests and generates evidence-backed hierarchical wiki documentation. Invoke when user wants to document test categories, create or regenerate category documentation, understand test structure from code, or get evidence-backed summaries of test families, parameters, support gates, or verification methods."
---

# Vulkan CTS Wiki Analyzer

This skill analyzes Vulkan CTS tests and generates structured wiki documentation derived from code and test-plan evidence.

## Primary Goal

Build a navigable and extensible knowledge system that answers the questions in [`Objectives.md`](../../../external/vulkancts/wiki/Objectives.md) using verifiable repository evidence.

The skill is not just a template filler. It must derive claims from:
- source registration paths
- test creation functions
- parameter structs, enums, arrays, and loops
- support checks and feature requirements
- verification logic
- the official test plan when relevant

**Scope**: Rely only on [`external/vulkancts/`](../../../external/vulkancts/) and [`doc/testspecs/VK/apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc) for factual claims.

## Evidence Rules

1. **Evidence first**
   - Every nontrivial claim must be supported by inspected source or test-plan evidence.

2. **Code links are mandatory**
   - Link all important claims to concrete files and lines.
   - Registration claims must point to the function that registers the group or test family.
   - Verification claims must point to the code that performs the check or comparison.
   - **Source-code line references MUST use GitHub fragment syntax in link targets**: `file.cpp#L82` for a single line and `file.cpp#L82-L95` for a range.
   - **Colon-style line references are forbidden in wiki links**: do not use `file.cpp:82` or `file.cpp:82-95` for `.cpp`, `.hpp`, `.h`, `.c`, or any other source file targets.

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
1. Identify the category registration file and inspect its `#include` section first
2. Follow the group-name discovery process (see Progress Counting Policy) to index top-level branches and verify group names
3. Launch workers per verified top-level branch when helpful
4. Allow workers to create additional Level-3 pages for nested registered subgroup files under their assigned top-level group
5. Review worker output for unsupported claims and broken links
6. Create or update the Level-2 summary only after Level-3 evidence is stable

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
- **Remove after the category work is complete**. These are temporary artifacts and should not be committed to the repository.

**Indexing rule**:
- Use header/source filenames as the initial tracker index because they are easy and robust to enumerate from the category root file includes.
- Do not use inferred subgroup names derived from factory symbols as the initial tracker key.
- After inspecting the implementation file, record the verified registered group name separately if needed.

**Important**:
- These internal trackers are not user-facing documentation.
- Keep temporary planning notes, worker assignment notes, and partial verification state here rather than in Level-2 category docs.
- **Cleanup requirement**: All files in `internal_doc/` must be removed before committing wiki documentation changes. This includes progress trackers (`{category}_progress.md`) and validation error logs (`error_paths_{category}.txt`, `error_urls_{category}.txt`).

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
- Registration hierarchy
- Test families with evidence-backed descriptions
- Parameter dimensions and observed values/ranges
- Support/feature requirements
- Verification methods
- Test principles observed in the file
- Notes / uncertainties

### Level-3 Registration Hierarchy Contract

Use one canonical user-facing section, `## Registration Hierarchy`, instead of separate duplicated
`Registration Path` and `Test Hierarchy` sections.

The section must contain one fenced `text` tree block that is both readable for users and parseable by
[`verify_registration_paths.py`](.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py).
The tree is the source from which the validator derives registration-prefix candidates.

Rules:
- The first line is the category-qualified Level-3 root path, without the global `dEQP-VK` prefix.
  - Example: `dynamic_state.general_state`
  - Example: `geometry.input`
- The tree expands exactly one level below that Level-3 root.
  - If the page documents a top-level category child, list that group's direct children only.
  - If the page documents a lower-level registered subgroup, list that subgroup's direct children only.
- Fully expand every direct child at that one-level-down depth, even when the child list is large.
- Use Unicode tree markers only:
  - `├──` for non-final children
  - `└──` for the final child
- Each child line contains exactly one registered path component, optionally followed by a trailing
  parenthesized note for users.
  - Allowed: `├── state_switch_mesh (non-VulkanSC only)`
  - The validator ignores the trailing parenthesized note.
- Do not include deeper descendants in the parseable hierarchy tree.
- Do not use shorthand or non-parseable notation in the tree:
  - no `...`
  - no `[_suffix]`
  - no `same test names as ...`
  - no trailing `/`
  - no inline prose unless it is a trailing parenthesized note
  - no factory-symbol call stacks such as `createApiTests -> createBufferTests -> buffer`

Example:

```text
dynamic_state.general_state
├── state_switch
├── state_switch_mesh (non-VulkanSC only)
├── bind_order
├── bind_order_mesh (non-VulkanSC only)
├── state_persistence (non-mesh only)
├── static_stencil_mask_zero
└── double_static_bind (non-shader-object only)
```

### Relationship Between Registration Hierarchy and Test Families

Do not remove `## Test Families`. Use it to explain the direct children listed in `## Registration Hierarchy`.

Rules:
- Each `Test Families` subsection should begin with the exact registered child name from the hierarchy tree.
- Add a human-readable description after the exact name when useful.
- Use this section for deeper descendants, generated cases, parameter matrices, and evidence-backed semantics.

Recommended subsection heading pattern:

```markdown
### basic_primitive — Basic primitive expansion
### triangle_strip_adjacency — Triangle-strip-adjacency vertex-count sweep
### conversion — Primitive-type conversion
```

**Formatting guidance**:
- Use the canonical registration hierarchy tree style above.
- Use tables for parameters when appropriate.
- Stop at meaningful test-family granularity in prose.
- Put deeper generated cases in `Test Families` rather than the parseable hierarchy tree.

Note: the workflow rules in this section are primarily about Level-2 category production. Level-3 standardization may follow different or additional rules later.

## Progress Counting Policy

Use two different concepts and do not mix them:

1. **README tracker count**
   - For [`README.md`](../../../external/vulkancts/wiki/README.md), keep the per-category `Level-3 Files` column for categories that are already `✅ Done`.
   - Leave the `Level-3 Files` field blank for categories that are not yet complete, because the final Level-3 writing scope is not reliable until category analysis is finished.
   - Do not maintain aggregate README progress metrics based on Level-3 file totals; category completion status is the only reliable global progress signal.
   - For categories that share a wiki folder with another category (e.g., `synchronization` and `synchronization2` share `testfiles/synchronization/`), the primary category gets the actual file count, and the secondary category uses `(shared with {primary_category})` instead of a number.

2. **Writing scope**
   - When documenting the category, create Level-3 pages for any separately meaningful registered group file, including nested subgroup files when they exist as their own registration/documentation units.
   - Writing scope is evidence-driven and may expand during analysis as additional registered subgroup files are discovered.

### How to identify top-level groups for counting

For a category, start from the root registration file's `#include` section. Use included `.hpp` files as the primary initial index for top-level branches, excluding:

- the root category header (`vkt{Category}Tests.hpp` or equivalent)
- shared utilities and helper-only headers
- headers included only by implementation files rather than the root registration file

For each candidate top-level header, follow the group-name discovery process below to verify the group and its displayed name.

### How to determine the correct group name

Do not assume the displayed group name from the factory symbol passed to `addChild()`. The common 1-to-1-to-1 correspondence between factory symbol, filename, and group name is only a heuristic, not a guarantee.

**Step-by-step discovery process:**

1. **Start from the category root registration file** (e.g., `vktGeometryTests.cpp`)
2. **Examine the include section first** — identify included headers that correspond to root-level test groups (exclude the file's own `.hpp` and utility/helper-only headers)
3. **Use those headers as the primary branch index** — do not primarily count by following factory-symbol calls in `createChildren()`
4. **Cross-check root registration calls** — use `createChildren()` or equivalent to confirm the included header is registered directly at the root and to note conditional registration guards
5. **Navigate to each header file** — find the factory function declaration only as a navigation aid, not as the authoritative group name
6. **Navigate to the corresponding `.cpp` file** — find the factory function definition or group-building function
7. **Locate the group name** — look for `TestCaseGroup` construction with the string name:
   ```cpp
   MovePtr<TestCaseGroup> varyingGroup(new TestCaseGroup(testCtx, "varying"));
   ```
   The group name is `"varying"`.

**Optimization tip:** Factory function definitions are typically at the **end of the `.cpp` file**. When only extracting the group name, read from the end rather than loading the entire file (some files have thousands of lines).

**Verification via mustpass TXT files:**

After determining a group name, verify it against the mustpass definition files using the registration path verifier.

## Registration Path Validation

**Purpose:** Confirm that documented registration paths and group names are backed by mustpass coverage before considering a category complete.

**Script:** [`verify_registration_paths.py`](.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py)

**How to run:** Run from the repository root.

```bash
# Check all extracted paths for a category
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category> --check-all

# Check a single path
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category> <group_path>

# Save category results for review
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category> --check-all \
  > external/vulkancts/wiki/internal_doc/error_paths_<category>.txt 2>&1
```

Use category-wide verification as the default before marking documentation complete. Use single-path verification while investigating one suspicious or newly added registration path.

The intended input for nested validation is the canonical `## Registration Hierarchy` tree in Level-3 pages. Avoid adding script-only explicit-prefix snippets to user-facing wiki pages.

The current validator behavior for regular categories is:
- canonical `## Registration Hierarchy` extraction in Level-3 pages is the only supported source of validation prefixes
- the validator reconstructs the Level-3 root path and its direct-child prefixes internally from the tree
- trailing parenthesized notes on child lines are ignored by the parser
- legacy, non-normalized wiki pages are expected to work only after they have been normalized to the canonical Level-3 contract

### Special cases

- **Regular categories** use the default extractor automatically.
- **Special categories** such as `pipeline` may dispatch to category-specific adapters under [`registration_validators/`](.agents/skills/wiki-analyzer/scripts/registration_validators/).
- Mustpass discovery handles direct matches, hyphenated names such as `binding_model` → `binding-model.txt`, plural forms such as `renderpass` → `renderpasses.txt`, and split-category directories such as `pipeline/`.

**Important:** This validation is mandatory whenever documenting group names or registration paths in wiki pages.

## Wiki Link Validation

**Purpose:** Confirm that markdown links in the wiki resolve correctly and that source-code line links use GitHub `#L...` fragment syntax.

**Script:** [`validate_wiki_links.py`](.agents/skills/wiki-analyzer/scripts/validate_wiki_links.py)

**How to run:** Run from the repository root.

```bash
# Check the entire wiki tree
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --repo-root . \
  --verbose

# Check one category scope only (recommended during active work)
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose

# Save category results for review
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose \
  > external/vulkancts/wiki/internal_doc/error_urls_<category>.txt 2>&1
```

Use category-scoped validation as the default while writing or repairing one category. Whole-wiki validation is mainly for global cleanup and may report expected false positives from tracker links in [`README.md`](../../../external/vulkancts/wiki/README.md) that point to not-yet-created category pages.

### Notes

- Links are resolved relative to the owning markdown file's directory, not relative to `wiki/`.
- The validator ignores external URLs, URI schemes, and anchor-only links.
- `--auto-fix` only rewrites colon-style source references such as `file.cpp:82` to `file.cpp#L82`; it does not repair broken relative paths or wrong filenames.

**Important:** Re-run category-scoped wiki-link validation until it passes cleanly before marking a category documentation batch complete.

## Analysis Process

### Step 1: Read Prerequisites

**CRITICAL**: Read these before starting any documentation work:

1. [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md) — check progress tracking, confirm whether the category is already documented, avoid duplicating existing work, follow the category order in the Progress Tracking table unless the user explicitly requests otherwise
2. [`external/vulkancts/wiki/Objectives.md`](../../../external/vulkancts/wiki/Objectives.md) — defines the questions the documentation must answer and the allowed scope
3. [`doc/testspecs/VK/apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc) — use when it contains relevant authoritative purpose/context; do not force it into docs if the category is better explained directly from code
4. Relevant framework files when making framework-level claims: [`vktTestCase.hpp`](../../../external/vulkancts/modules/vulkan/vktTestCase.hpp), [`tcuTestCase.hpp`](../../../framework/common/tcuTestCase.hpp)

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

Start from the category root registration file's `#include` section and follow the group-name discovery process (see Progress Counting Policy) to:
- identify the counted top-level branches
- verify displayed group names from implementation files
- note conditional registration guards

Do not finalize displayed group names until the corresponding implementation files are verified.

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
- every important claim has a source link
- registration file and subgroup tree are documented correctly
- user-facing Level-2 pages use verified subgroup names rather than inferred factory-symbol names
- temporary coordination material is stored only in [`wiki/internal_doc/`](../../../external/vulkancts/wiki/internal_doc/)
- parameter tables come from observable code constructs
- support gates are documented when present
- verification methods are documented only when evidenced
- all relative links are correct (run [`scripts/validate_wiki_links.py`](scripts/validate_wiki_links.py))
- links to Level-3 docs are correct from the category doc
- links to source files are correct from each Level-3 doc
- all group names are verified (run [`verify_registration_paths.py`](.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) with `--check-all`; redirect output to `external/vulkancts/wiki/internal_doc/error_paths_<category>.txt`)
- category docs match registration code
- no unsupported claims remain; wording avoids universal claims not justified by evidence
- repeated statements are deduplicated
- wording matches inspected evidence strength

### Step 10: Update Progress Tracking

If the project is using [`external/vulkancts/wiki/README.md`](../../../external/vulkancts/wiki/README.md) as a tracker, update it after the consistency review.
When a category reaches `✅ Done`, update its `Level-3 Files` cell with the actual number of `.md` files under `testfiles/{category}/`, but do not add or maintain aggregate README statistics based on total Level-3 file counts.
