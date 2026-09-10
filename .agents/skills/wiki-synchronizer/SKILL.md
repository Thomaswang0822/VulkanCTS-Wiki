---
name: wiki-synchronizer
description: Use when syncing the VK-GL-CTS wiki after an upstream merge. Classify upstream changes, update English categories, validate and rebuild the lookup DB, then synchronize Chinese pages when authorized.
---

# Wiki Synchronizer

Synchronize the repository's wiki with an upstream VK-GL-CTS range. Follow six steps: establish the baseline, classify changes, resolve indirect impact, update categories, validate English and the DB, then synchronize Chinese. Keep this skill an orchestrator, not another page template or validator specification.

## Boundaries and dependencies

- Preserve existing work and the Git index. Ask the user to perform branch creation, merge, commit, and push unless separately authorized; this workflow does not authorize those operations by itself. Do not reset, stash, clean, or rewrite history.
- CTS source, specifications, and MUSTPASS are evidence, not documentation repair targets. Report source defects without changing them. Never delete repository files automatically.
- Keep all workflow changes repository-local. Do not create or modify global skills.
- Load [wiki-writer](../wiki-writer/SKILL.md) and its required references for page contracts and validation. Existing-page maintenance belongs here; use writer's scratch workflow only for newly authorized pages/categories. Load [wiki-auditor](../wiki-auditor/SKILL.md) for semantic review.
- Load [db-lookup-updater](../db-lookup-updater/SKILL.md) before DB work, and [wiki-publisher](../wiki-publisher/SKILL.md) plus [translate-doc](../translate-doc/SKILL.md) before Chinese work. Those skills own detailed commands and output rules.
- English/DB approval is not translation approval. Stop at the English completion boundary unless Chinese synchronization was explicitly authorized. Do not even inspect `vkcts-wiki-pages/` before that authorization. Local Chinese preparation is not permission to publish remotely.
- Continue through the authorized batch without intermediate confirmation or progress-only replies unless a real blocker or explicit checkpoint requires it.

## 1. Establish the branch and upstream range

Read Git status, branch, first-parent history, merge parents, and the previous [merge log](../../../external/vulkancts/wiki/internal_doc/merge_update_log.md). If needed, provide the user with branch-creation and merge commands using `merge_main_<YY-MM-DD>` and verified refs; otherwise resume the existing integration branch.

Record the integration and target branches, merge commit, local wiki parent, upstream parent, previous integrated upstream commit (`START`), and new upstream commit (`END`). Verify the merge base separately: it need not be identical to the last integrated upstream commit. Locate the actual merge in history rather than assuming HEAD is the merge.

Capture the repository-wide upstream delta, including additions, renames, and deletions:

```bash
git diff --stat START..END
git diff --name-status --find-renames START..END
```

Resolve the placeholders before running. Save the commands, exact commits, and output in `external/vulkancts/wiki/internal_doc/git_diff_stat.txt` or another agreed artifact; preserve an existing input rather than overwriting it blindly. Read targeted full diffs as needed. The upstream delta is not the accumulated integration-branch wiki diff.

Use one compact `internal_doc/TODOs_after_merge.md` tracker for the baseline, classified files, category decisions, and remaining work. Do not build a second tracking system.

## 2. Classify every changed path: A / B / C

| Class | Meaning | Treatment |
|---|---|---|
| A | Clearly unrelated to Vulkan CTS wiki, such as GL-only tests | Record the exclusion and reason. |
| B | Indirect/shared impact that needs the actual diff inspected | Review root dispatchers, framework, utilities, build configuration, global MUSTPASS/exclusions, and tools before assigning category work. |
| C | Direct test-category source or MUSTPASS change | Map to the owning wiki category and queue it for English refresh. |

Do not classify shared build/framework changes as A just because they are outside a category directory. Account for both sides of renames and deleted files. Source, wiki, and MUSTPASS names may differ (`renderpass` / `renderpasses`, `device_generated_commands` / `dgc`, hyphenated names); verify mappings rather than guessing.

## 3. Resolve B-class impact first

Read each actual diff and trace callers, package registration, and existing documentation claims. Record `no wiki update`, `update <owners>`, `validator-only`, `DB-only`, or `unresolved source issue`, with concise evidence.

Feed affected categories into C, including categories with no direct upstream changes. Shared helpers such as Amber may affect several owners without warranting a standalone page. Handle nested MUSTPASS layouts and package namespaces before category workers rely on them.

Fix a proven tooling defect within the authorized scope, with regression tests; do not alter source or page ownership to disguise a tool failure. A previously expected failure is not a permanent exemption: verify it against the current implementation.

## 4. Update C-class English categories

For each category, compare its upstream delta with current source, registration, MUSTPASS, and relevant specification evidence. Maintain the gateway, affected Level-3 pages, and related briefs where their evidence became stale. New implementation-bearing families may need new pages; dispatchers and helper-only files do not.

Preserve explanation depth and canonical structure. Change source-proven facts and dependent references, not unrelated prose. Do not replace real shader walkthroughs with exceptions. Use writer's shader helpers when required; keep host-only/setup-only explanations short and factual, without workflow filenames in published prose.

Use category-sized maintenance batches. When splitting substantial writing or audit work, assign exactly one canonical page (and its related brief if needed) to a worker. The lead owns the gateway, shared files, and final category verification. Supply each worker the exact local skills/references to read, baseline, evidence, writable paths, and validation commands. Never run two writers on the same file or re-dispatch it while its worker is live.

Apply the writer's English language gates and auditor's source-vs-page review. After edits, run the category checks below. Record `update` or `no wiki update`, evidence, affected paths, and actual results. A checked box follows verified work; it never substitutes for it.

## 5. Validate English and rebuild the lookup DB

Use the current commands in [writer's validation checklist](../wiki-writer/references/validation-checklist.md): English structure, registration paths, and local links. Run the source line-reference checker as well, after inspecting its current CLI. Use category identifiers, not `.md` filenames; resolve shared physical page directories explicitly. Include briefs in link/reference checks but not canonical Level-3 structure counts.

Then follow [db-lookup-updater](../db-lookup-updater/SKILL.md): inspect configured inputs and current mappings, build affected categories in isolation, diagnose ownership or namespace failures, rebuild the full runtime index, and run lookup tests/coverage. Updating an already-enabled category need not change category counts. Preserve tree-first ownership; no generic aliases or suffix guesses to force a successful build.

```
English edits → validators → DB build/lookup → diagnose → minimal owning-page/tool repair → rerun
```

Before accepting the phase, the lead runs the global English structure/registration checks, category/testfile link and line-reference sweeps, relevant tool tests, full DB build and configured coverage validation, and `git diff --check`. Keep logs in `/tmp` and record concise results in the tracker. Inspect diagnostics and collected counts, not just exit codes: zero extracted paths is not coverage, and line-reference candidates are not automatically confirmed semantic defects.

Separate genuine page defects, tool limitations, namespace projections, and source/MUSTPASS omissions. Resolve failures or record explicit scoped deferrals; do not report a deferred gate as PASS. Recheck after all workers finish, and do not let delayed results overwrite newer work.

## 6. Synchronize Chinese changes by category

After English and DB acceptance and explicit translation authorization, freeze the accepted English revision. Derive the Chinese work list from the English delta since the last synchronized wiki revision, including added pages and B-class/global repairs, not merely the upstream source delta. Exclude briefs and internal documents.

For this merge-maintenance phase, use **one worker per test category** as requested by the user. This overrides publisher's normal page-worker dispatch granularity only; all publisher/translate-doc content, path, terminology, language, and validation rules still apply. Each worker processes its affected pages sequentially. Group shared physical outputs into one non-overlapping assignment. Handle changed global pages with explicit separate ownership.

Each worker reads publisher and translate-doc requirements, updates its exact Chinese targets from canonical English, preserves unaffected explanations and protected code/SPIR-V/identifiers, and applies `shuorenhua` then `humanizer-zh` per page. Use the publisher's Chinese structural guard for every source/target pair.

Translation and link conversion remain separate: workers hand back pre-conversion output as required by translate-doc; after translations finish, the lead runs publisher's deterministic link conversion and final guards. Avoid mixing already-converted URLs into pre-conversion text. Missing Chinese pages use the complete translation procedure. Renamed/deleted outputs require an explicit plan; do not remove files automatically.

Do not change English, DB, source, or MUSTPASS in this phase. If Chinese checks reveal an English defect, return it to the English owner, rerun affected English/DB gates, and refresh the translation. Leave both repositories unstaged and uncommitted; publishing remotely remains a separate user action.

## Close the sync

Update the durable merge log with verified commit IDs, range, major scope decisions, English/DB results, unresolved issues, and Chinese status. Keep the tracker for review unless the user chooses otherwise. Mark only verified or explicitly deferred items accordingly.

Report what changed, what was actually checked, and what remains. Provide manual final merge commands using verified branch names; prefer a regular merge rather than squash so upstream ancestry remains available for the next sync. Do not claim Chinese synchronization, DB regeneration, or remote publication merely because English validators passed.
