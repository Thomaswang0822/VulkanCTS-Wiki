---
name: db-lookup-updater
description: Use after a Wiki category stabilizes to update lookup DB.
---

# DB Lookup Updater

Add one writing/audit-stable Vulkan CTS Wiki category to the registration-path lookup index. Keep complex ownership construction local and supervised; SQLite is intermediate, while `case_lookup/site/mappings.json` is the tracked runtime artifact.

## Scope

Use this skill after a category's canonical English Level-3 pages pass writing and audit gates.

This skill owns:

- enabling the category's mustpass inputs;
- making its ownership build pass without hiding page defects;
- updating source-backed category projections when genuinely required;
- regenerating and reviewing the tracked runtime JSON;
- lookup tests and coverage verification.

It does not translate, publish, audit prose, or modify CTS source/mustpass files.

## Required context

Read before editing:

```text
external/vulkancts/wiki/case_lookup/README.md
external/vulkancts/wiki/case_lookup/build_helper/tree_and_handler_spec.md
external/vulkancts/wiki/case_lookup/build_helper/category_inputs.py
external/vulkancts/wiki/case_lookup/build_helper/category_handlers.py
external/vulkancts/wiki/case_lookup/build_helper/ownership_aliases.py
external/vulkancts/wiki/case_lookup/tests/test_builder.py
external/vulkancts/wiki/internal_doc/wiki_rewrite_checklist.md
```

Confirm the category's Level-3 English pages already pass:

```bash
python3 .agents/skills/wiki-writer/scripts/verify_english_structure.py <category>
python3 .agents/skills/wiki-writer/scripts/verify_registration_paths.py <category>
```

Use the category-scoped link command from
`.agents/skills/wiki-writer/references/validation-checklist.md` as the third precondition.

## Procedure

### 1. Capture the baseline

Before changing lookup files, record from `site/mappings.json`:

- `category_count`;
- `mapping_count`;
- ordered category set derived from mappings;
- current file hash.

Also record both Git repositories' status. Preserve the user's index and unrelated work.

### 2. Resolve exact mustpass inputs

Inspect `external/vulkancts/mustpass/main/vk-default/` and identify every file that belongs to the category. Do not guess from filename alone when the category uses split directories or construction variants.

Add the category to `CATEGORY_MUSTPASS_FILES` in the category-checklist order. Keep unsupported future categories commented.

Update `test_only_validated_categories_are_enabled` in `tests/test_builder.py` so its expected registry order matches exactly.

### 3. Run an isolated category build

Use temporary intermediate paths first:

```bash
python3 external/vulkancts/wiki/case_lookup/build.py \
  --mode categories \
  --categories <category> \
  --db-dir /tmp/vkcts-case-lookup-<category>-db
```

Do not run the full build until this category succeeds.

### 4. Diagnose failures by evidence class

#### Page ownership/tree defect

Examples:

- missing concrete root or direct child;
- wrong page owner;
- `registration only` used on an implemented family;
- overlapping or incomplete ownership;
- page prose and tree disagree.

Inspect current source registration, all relevant mustpass paths, the complete English page, and sibling page ownership before editing. Make the smallest evidence-backed English page correction, then rerun English structure, registration, and link validators.

Do not modify a page merely to silence the builder.

#### Legitimate namespace projection

Use `category_handlers.py` only when source and mustpass prove that different namespaces represent the same page-owned behavior, such as:

- construction variants;
- generated family expansion too large for literal tree enumeration;
- shared category/page directories.

Projection rules must be explicit, category-specific, deterministic, and covered by tests. They may generate only real current mustpass prefixes and may not change the owner.

#### Unsupported fallback

Never make a formal build pass through:

- `OWNERSHIP_ALIASES`;
- generic anchor fallback;
- suffix guessing;
- broad nearest-prefix ownership.

`OWNERSHIP_ALIASES` should remain empty. A fallback hit is a diagnosis, not accepted coverage.

#### Source or mustpass defect

Do not edit CTS C/C++ source or mustpass. Report the blocker with the exact path and evidence.

### 5. Add regression coverage

Not every category needs a dedicated test. Add a focused category-scoped regression test ONLY when this category's ownership required a repair or special handling:

- an ownership repair to an English page (tree defect fix, owner correction, excluded-branch change);
- a new category-specific projection/handler in `category_handlers.py`.

Do not add one merely because a category was added with an uneventful, first-pass build.

The test must prove:

- the representative executable leaf resolves to the expected page;
- component-boundary longest-prefix behavior remains intact;
- the category registry/count is correct;
- unsupported aliases are not required.

Rerun the isolated category build after each repair.

### 6. Regenerate the final runtime index

Only after the category build passes, run the complete supervised build:

```bash
python3 external/vulkancts/wiki/case_lookup/build.py
```

This rebuilds all enabled category intermediates, the ignored final SQLite DB, and the tracked:

```text
external/vulkancts/wiki/case_lookup/site/mappings.json
```

Do not commit `db/` or `vkcts_lookup.sqlite3`.

### 7. Review the JSON delta

Programmatically verify:

- `category_count` increased by the expected amount;
- the new category appears;
- `mapping_count` equals `len(mappings)`;
- every new mapping has the expected category, page, and Wiki URL;
- pre-existing prefixes did not change owner unexpectedly;
- output ordering and serialization are deterministic.

Review the actual Git diff for `site/mappings.json`. Any unrelated owner change requires investigation before completion.

Update hard-coded current category/count statements in `case_lookup/README.md` when applicable.

### 8. Run completion verification

```bash
python3 -m unittest discover \
  -s external/vulkancts/wiki/case_lookup/tests \
  -p 'test_*.py' -v

python3 -m py_compile \
  external/vulkancts/wiki/case_lookup/build.py \
  external/vulkancts/wiki/case_lookup/lookup.py \
  external/vulkancts/wiki/case_lookup/build_helper/*.py

git diff --check
```

Run runtime coverage against every configured mustpass input for the new category:

```bash
python3 external/vulkancts/wiki/case_lookup/lookup.py validate \
  <mustpass-file-1> [<mustpass-file-2> ...]
```

For changes that affect runtime data shape or frontend behavior, also run the static Chromium E2E documented in `case_lookup/README.md`. A normal category-only data addition does not require frontend changes.

## Completion report

Report:

```text
Category: <category>
Mustpass inputs: <exact files>
Level-3 owner pages: <count>
Executable leaves: <count>
Mappings added: <count>
Page repairs: <paths or none>
Handler changes: <files/rules or none>
Runtime JSON: <old count> -> <new count>
Tests: <result>
Coverage: <passed>/<total>
Remaining blockers: <none or exact evidence>
```

Do not commit or push unless explicitly authorized.

## Pitfalls

- A successful registration validator does not prove full mustpass leaf coverage; the builder does.
- A failed build does not automatically mean the page tree is wrong; construction namespaces may need an explicit handler.
- A large generated family does not justify a generic alias.
- `--mode categories` does not update the tracked runtime JSON; the final full build does.
- CI publishes committed `site/` files and intentionally does not run this supervised build.
