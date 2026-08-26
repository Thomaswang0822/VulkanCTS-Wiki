# Orchestration and Batching

## Step 0: lead-owned outline

The lead agent performs wiki-rewriter Step 0 directly. Never delegate outline creation.

1. Inspect category state and the old Level-2/Level-3 inventory.
2. If an outline exists, treat the task as resumed work and establish which entries are unfinished.
3. If no outline exists and the category is new, create the canonical outline under `external/vulkancts/wiki/internal_doc/` using wiki-rewriter's outline template.
4. If a new outline was created, hard stop 1 for user approval. Do not inspect page implementations deeply, create briefs, or rewrite pages before approval. A resumed category with an existing approved outline skips this checkpoint.
5. Once approved, retain the outline as the batching and page-classification authority for rewrite.

The lead writes the outline because its category-wide survey is required context for later coordination. This reason need not be exposed in worker prompts.

## Batch semantics

An approved outline batch defines:

- which pages belong to the same logical wave;
- page order;
- brief/direct-rewrite decisions;
- dispatcher and Level-2 synthesis notes.

It does not define worker granularity. For a batch containing pages A, B, and C, dispatch three workers: one for A, one for B, and one for C.

If the runtime permits fewer workers than the batch contains, preserve outline order and split the batch into successive dispatch waves. Do not move pages between outline batches merely to fill concurrency slots.

## Rewrite phase

For each approved outline batch:

1. Resolve one input contract per page.
2. Dispatch one rewrite worker per page.
3. Wait for the complete wave result.
4. Check each expected brief/output on disk. For each Level-3 output, run the page-scoped English structure, registration hierarchy,
   and wiki-link validators from `wiki-rewriter/references/validation-checklist.md`.
5. Retry missing, failed, or provenance-suspect pages individually.
6. Mark the outline batch stable only when every page passes.

After all Level-3 batches stabilize, rerun the English structure and registration validators in category mode. Then perform
lead-owned Level-2 synthesis and category Background Knowledge consolidation. Only after Level-2 exists, run the category wiki-link
command and revalidate affected Level-3 upward links. Stage the changes produced by this rewrite (without staging unrelated
pre-existing work), and continue into audit without stopping.

## Audit phase

1. Enumerate the full rewritten Level-3 set and Level-2 page; exclude briefs and internal documentation.
2. Audit Level-2 Background Knowledge first so workers have the correct shared-concept ownership model.
3. Create the combined audit summary before dispatching Level-3 workers.
4. Dispatch one audit worker per Level-3 page. Concurrency waves may differ from rewrite batches, but page granularity never changes.
5. After each wave, verify edits and immediately append page findings/no-issue entries to the lead-owned summary.
6. Retry failed pages individually.
7. Reconcile recurring patterns, audit the rest of Level-2, rerun category-scoped English structure, registration hierarchy, and
   wiki-link validation, and finalize the summary.
8. **Hard stop 2:** stop before any publish translation or link conversion and ask the user to review and approve the complete audit result.

## Publish phase

1. Confirm every English page is audit-stable.
2. Dispatch one translation worker per Level-3 page and one worker for the Level-2 page.
3. Check every target file for existence and target-language text. For each Level-3 source/target pair, run the canonical Chinese
   structure/fixed-language validator after the language passes.
4. Retry only missing, failed, or suspect translations.
5. After all translations pass, run link conversion per file.
6. Run link-conversion check mode to prove idempotency.
7. Run final category checks.

## Phase barriers

Do not cross a barrier until its condition is true:

- **Outline barrier:** when a new outline was created, it has explicit user approval.
- **Rewrite barrier:** all outline-assigned Level-3 outputs/briefs and Level-2 synthesis exist; every Level-3 page and the category
  pass English structure, registration hierarchy, and applicable wiki-link gates.
- **Rewrite staging checkpoint:** the rewrite-produced paths are staged, unrelated pre-existing work is preserved, and the lead continues into audit without stopping.
- **Audit barrier:** every Level-3 page and Level-2 page has an audit outcome; repaired Level-3 pages and the category pass English
  structure, registration hierarchy, and wiki-link gates; summary is final.
- **Publish-approval barrier:** the user has explicitly approved the completed audit result.
- **Publish barrier:** every translation exists and contains target-language text; every Level-3 source/target pair passes the
  canonical Chinese structure/fixed-language validator; audited English sources remain unchanged.
- **Lookup barrier:** after publish, `db-lookup-updater` completes the isolated category build and full supervised build; mustpass
  runtime coverage and tests pass; tracked `site/mappings.json` is reviewed. Any English ownership repair is revalidated and its
  Chinese page is republished/reconverted before rebuilding lookup.
- **Completion barrier:** publication and lookup barriers pass, conversion is idempotent after any repair loop, the checklist is
  correct, counts are reconciled, and safety checks pass.
