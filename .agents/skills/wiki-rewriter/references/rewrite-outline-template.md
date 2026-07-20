# Category Rewrite Outline Template

Load this reference when starting a new category rewrite. Fill the template in place at
`external/vulkancts/wiki/internal_doc/{category_name}_rewrite_outline.md`.

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
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.
```

Batching rules:

- Count each easy direct-rewrite page as 1 file.
- Count each difficult page with an Understanding Brief as 2 files: brief plus page.
- Group pages into batches with at most 8 counted files where possible.
- Use `ceil(total_counted_files / 8)` batches normally.
- If the whole category has fewer than 8 counted files, use a single smaller batch.
- Do not split a page from its Understanding Brief across batches.

Keep the outline concise and actionable. Do not record context-window or commit-boundary rationale.
