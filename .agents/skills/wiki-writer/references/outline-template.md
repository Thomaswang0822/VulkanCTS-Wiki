# Category Writing Outline Template

Load this reference when starting a fresh category. Fill it in at
`external/vulkancts/wiki/internal_doc/{category}_outline.md`.

```md
# {category} Writing Outline

## Scope

- Category: `{category}`
- Source category directory: `external/vulkancts/modules/vulkan/{source_category_dir}/`
- Root registration file: `{root_registration_file}`
- Mustpass source: `{mustpass_files}`
- Level-2 output: `external/vulkancts/wiki/categories/{category}.md`
- Level-3 output directory: `external/vulkancts/wiki/testfiles/{category}/`

## Discovery Summary

- Verified registered category path: `{category}`
- Root registration entry point: `{registration_entrypoint}`
- Registered direct branches: `{branch_1}`, `{branch_2}`, ...
- Category-specific mapping or conditional guards: `{mapping_or_none}`

## Page Classification

| Source scope | Registered group/path | Classification | Level-3 page | Reason |
|---|---|---|---|---|
| `{source_file}` | `{registered_path}` | implementation-bearing / hybrid / registration-only / helper | `{page_or_none}` | `{evidence-backed reason}` |

Registration-only dispatchers and helper-only files must be listed for completeness but do not receive Level-3 pages.

## Page Count

- Implementation-bearing or hybrid Level-3 pages: `{implementation_level3_count}`
- Registration-only/helper files with no page: `{no_page_count}`
- Counted writing files for batching: `{total_counted_files}`
  - `{brief_count}` Understanding Briefs
  - `{page_count}` final Level-3 pages

## Batch 1 — {description}

Counted files: {batch_counted_files}

| Level-3 page | Brief? | Reason |
|---|---:|---|
| `{page}.md` | Yes/No | {brief_required_or_direct_write_reason}. |

## Batch 2 — {description}

Counted files: {batch_counted_files}

|(same table)|
|---|

...

## Batch N — {description}

Counted files: {batch_counted_files}

|(same table)|
|---|

## Level-2 Synthesis

After all planned Level-3 pages stabilize:

- Write `{category}.md` as the compact Level-2 category gateway.
- Include verified root structure and registration-only routing where useful.
- Link concrete families and reader goals to final Level-3 pages.
- Avoid duplicating detailed shader walkthroughs, parameter matrices, runtime mechanics, and failure analysis.
- Consolidate repeated category-shared Background Knowledge into Level-2.
```

Batching rules:

- Count each direct-write Level-3 page as 1 file.
- Count each page with an Understanding Brief as 2 files: brief plus page.
- Group pages into batches with at most 8 counted files where possible.
- Use `ceil(total_counted_files / 8)` batches normally.
- If the whole category has fewer than 8 counted files, use a single smaller batch.
- Never split a page from its Understanding Brief across batches.

Keep the outline concise and actionable. Do not create a separate progress tracker.
