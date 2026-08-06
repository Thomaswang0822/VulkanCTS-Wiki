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

For HTTP 429, timeout, interrupted worker, missing output, validator failure, or uncertain provenance:

1. Enumerate expected outputs and compare them with disk state.
2. Preserve verified successful pages.
3. Retry each failed, missing, or suspect page with a fresh single-page worker for the same phase.
4. Re-run that phase's validators after the retry.
5. Do not compensate by assigning multiple pages to one worker.
6. Do not cross the phase barrier while retries remain unresolved.

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
- source-code and mustpass links resolve to the expected publication URLs without translated path segments;
- `home.md` has the correct extensionless category link and was not passed through the converter.

## Checklist reconciliation

Derive values from disk:

- rewritten Level-3 count excludes obsolete `vkt*.md` files and `*_brief.md`;
- UB count includes only `*_brief.md` Understanding Briefs;
- update the category checkbox and `(UB: N)` annotation;
- recompute done/todo category counts and L3/UB totals arithmetically;
- ensure spoken counts match the file and final report exactly.

## Repository safety

Before final reporting, compare Git status and index state with the initial state. Never stage, unstage, restore, commit, push, or rewrite history unless separately authorized. Report any unauthorized-path write instead of silently deleting or repairing it.
