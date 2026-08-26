# Recovery and Verification

## Page-level truth

Treat worker summaries as claims to verify. For each assigned page, independently confirm:

- expected output path exists;
- it is the assigned page and phase output;
- the worker stayed within its write scope;
- required page and category validators pass;
- translation output contains CJK text during publish;
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

## Rewrite checks

For every Level-3 rewrite:

- expected new page and required brief exist;
- obsolete `vkt*.md` source remains untouched;
- output follows the page classification and filename in the approved outline;
- registration and wiki-link validators pass;
- required English language-quality passes were applied by the page worker;
- no forbidden publication output was written.

For Level-2:

- navigation covers every rewritten Level-3 family;
- dispatcher-only facts are folded according to the outline;
- shared Background Knowledge consolidation and Level-3 upward links are complete;
- category validation passes.

## Audit checks

- every rewritten Level-3 page has one worker result;
- every failed worker is retried;
- every edited page revalidates;
- Level-2 has an explicit audit result;
- combined summary is lead-owned and finalized;
- counts come from the actual summary and files, not memory or worker count;
- recurring-pattern classification matches the auditor contract.

## Publish checks

Before conversion:

- all Level-2/Level-3 target files exist;
- every target contains CJK text;
- translation structure verifier passes for every source/target pair;
- no worker ran link conversion early;
- English sources and internal briefs are unchanged.

After conversion:

- converter succeeds separately for every published page;
- check mode reports no remaining changes;
- source-code and mustpass links resolve to the expected publication URLs without translated path segments.

## Checklist reconciliation

Derive values from disk:

- rewritten Level-3 count excludes obsolete `vkt*.md` files and `*_brief.md`;
- UB count includes only `*_brief.md` Understanding Briefs;
- update the category checkbox and `(UB: N)` annotation;
- recompute done/todo category counts and L3/UB totals arithmetically;
- ensure spoken counts match the file and final report exactly.

## Rewrite staging checkpoint

After rewrite and Level-2 synthesis validate, the lead agent stages the paths produced by the rewrite phase before starting audit. Preserve unrelated pre-existing staged or unstaged work; do not stage broad globs that could capture it. This staging checkpoint is not a user-approval stop. Audit continues immediately.

## Repository safety

Before final reporting, compare Git status and index state with the initial state. The pipeline's explicit rewrite staging checkpoint authorizes staging rewrite-produced paths only; do not stage unrelated work. Never unstage, restore, commit, push, or rewrite history unless separately authorized. Report any unauthorized-path write instead of silently deleting or repairing it.
