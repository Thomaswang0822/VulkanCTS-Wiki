# Recovery and Verification

## Page-level truth

Treat worker summaries as claims to verify. For each assigned page, independently confirm:

- expected output path exists;
- it is the assigned page and phase output;
- the worker stayed within its write scope;
- required page and category validators pass;
- translation output contains CJK text during local publish-target preparation;
- protected paths/identifiers and canonical English sources remain intact;
- the Git index has not changed.

Use the filesystem and validator output to determine completion. A delegation marked `completed` can still contain a rate-limit failure or partial result.

## Failure and retry policy

First classify the provider failure. HTTP status `429` alone is not enough to choose a recovery path.

### Retryable transient 429

If the provider payload indicates temporary concurrency pressure, a short rate window, `Too Many Requests`, or an explicit retry-after condition, use the existing accurate page-level recovery:

1. Enumerate expected outputs and compare them with disk state.
2. Preserve verified successful pages.
3. Retry only the failed, missing, or suspect page with a fresh single-page worker.
4. Keep the retry budget bounded; do not loop indefinitely.
5. Re-run that phase's validators after the retry.

### Terminal usage/quota 429

If the provider payload indicates token usage, quota, billing, credit, account, daily/monthly/long-window limit, or usage reset, treat it as a terminal external blocker:

1. Preserve completed work and verified successful pages.
2. Do not retry or re-dispatch the affected page.
3. Do not advance the phase or cross a phase barrier.
4. Report the provider error and current page-level completion state to the user, then stop for the user to resolve the model/provider limit.

### Ambiguous provider failure

If a `429` payload does not provide enough information to distinguish a transient window from an account usage limit, do not start an unbounded retry loop. Make at most the explicitly supported bounded diagnostic retry; if classification remains unclear, stop and report the blocker.

For non-429 ordinary interruptions, missing outputs, validator failures, or uncertain provenance, enumerate expected outputs, retry only the affected page with a fresh single-page worker, and revalidate before crossing the phase barrier. Never compensate by assigning multiple pages to one worker.

If an erroneous multi-page worker was accidentally dispatched, its outputs are untrusted. Re-run every affected page through the correct single-page worker and verify the final on-disk version after all competing workers finish.

## Writing checks

For every Level-3 page:

- expected final page and required brief exist;
- output follows the page classification and filename in the approved outline;
- the canonical English structure validator passes, including headings/spacing, fixed subsections, walkthrough tables, SPIR-V
  artifacts, and multi-stage H5 organization;
- the strict Registration Hierarchy/mustpass validator passes; a visually plausible tree is not enough;
- the wiki-link validator passes;
- a no-walkthrough page has source-reviewed justification and an approved entry in `walkthrough_exceptions.py`; a worker has not
  added an exception merely to silence validation;
- required English language-quality passes were applied by the page worker;
- no forbidden publish-target output was written.

For Level-2:

- navigation covers every final Level-3 family;
- dispatcher-only facts are folded according to the outline;
- shared Background Knowledge consolidation and Level-3 upward links are complete;
- category validation passes.

## Audit checks

- every final Level-3 page has one worker result;
- every failed worker is retried;
- every edited page revalidates;
- English structure, registration hierarchy, and wiki-link validators are rerun after every audit edit and at category completion;
- Level-2 has an explicit audit result;
- combined summary is lead-owned and finalized;
- counts come from the actual summary and files, not memory or worker count;
- recurring-pattern classification matches the auditor contract.

## Publish checks

Before conversion:

- all Level-2/Level-3 target files exist;
- every target contains CJK text;
- the canonical Chinese structure/fixed-language validator passes for every Level-3 source/target pair after language-quality passes;
- validator output confirms the English source itself is canonical before accepting the Chinese result;
- no worker ran link conversion early;
- English sources and internal briefs are unchanged.
- audited English source hashes/diffs remain unchanged throughout local publish-target preparation.

After conversion:

- converter succeeds separately for every prepared Chinese target page;
- check mode reports no remaining changes;
- source-code and mustpass links have the expected publication URL forms without translated path segments;
- the Chinese target files remain local working-tree changes, and neither repository was staged, committed, or pushed.

## Lookup DB checks

After local publish-target verification, run `db-lookup-updater` and confirm:

- the category is enabled with exact mustpass inputs;
- isolated category ownership build passes without aliases or generic fallback;
- the complete supervised build passes for every enabled category;
- `site/mappings.json` includes the category with reviewed owner/page/URL mappings;
- unit tests, Python compile, runtime mustpass coverage, and `git diff --check` pass;
- ignored SQLite intermediates are not staged or committed.

If lookup diagnosis repairs an English page, the previous publish-target verification for that page is invalidated. Re-run its three English
validators, regenerate the local Chinese page through the one-page publisher, reconvert links, rerun the Chinese validator,
and only then accept the rebuilt runtime JSON. This bounded repair loop adds no user hard stop.

## Checklist reconciliation

Derive values from disk:

- final Level-3 count excludes `*_brief.md` files and source scopes classified as registration-only or helper-only;
- UB count includes only `*_brief.md` Understanding Briefs;
- update the category checkbox and `(UB: N)` annotation;
- recompute done/todo category counts and L3/UB totals arithmetically;
- ensure spoken counts match the file and final report exactly.

## Writing staging checkpoint

After writing and Level-2 synthesis validate, the lead agent stages the paths produced by the writing phase before starting audit. Preserve unrelated pre-existing staged or unstaged work; do not stage broad globs that could capture it. This staging checkpoint is not a user-approval stop. Audit continues immediately.

## Repository safety

Before final reporting, compare Git status and index state with the initial state. The pipeline's explicit writing staging checkpoint authorizes `git add` for writing-phase paths only; do not stage unrelated work or any Chinese publish-target path. Never commit or push. Do not unstage, restore, or rewrite history unless separately authorized. Report any unauthorized-path write instead of silently deleting or repairing it.
