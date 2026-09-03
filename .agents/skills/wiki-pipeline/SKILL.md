---
name: wiki-pipeline
description: Use for end-to-end VK-GL-CTS wiki category work. Follow the writing outline, dispatch one page per subagent per phase, then run writing, audit, and local Chinese publish-target preparation with page-level recovery and final verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, pipeline, orchestration, writing, audit, publish]
    related_skills: []
---

# Wiki Pipeline

## Purpose

Orchestrate one complete project-local wiki category lifecycle:

`outline → Level-3 writing → Level-2 synthesis → audit → Chinese publish-target preparation → lookup DB update → final verification → checklist`

This is a **lead-agent orchestration skill**. Load and follow the project-local primary skills instead of duplicating their page-writing, auditing, translation, shader, or link-conversion rules:

- `.agents/skills/wiki-writer/SKILL.md`
- `.agents/skills/wiki-auditor/SKILL.md`
- `.agents/skills/wiki-publisher/SKILL.md`
- `.agents/skills/db-lookup-updater/SKILL.md`

Read their required references and helper skills as those primary skills direct.

## Non-negotiable workflow

1. Run wiki-writer's outline/discovery step yourself as lead agent: inspect the clean category source and create or resume `external/vulkancts/wiki/internal_doc/<category>_outline.md`.
2. **Hard stop 1 for user approval:** when the outline is new, stop and ask the user to approve it before briefing or writing pages. Resume only after approval or an explicit request to continue. The outline is the only temporary coordination artifact; do not create a progress tracker.
3. Follow the approved outline's batches exactly for page-writing dispatch.
4. Write all assigned Level-3 pages. A page stabilizes only after the canonical English structure, registration hierarchy, and
   wiki-link validators pass. Then synthesize the Level-2 page after every Level-3 page is stable.
5. Stage the changes produced by the writing phase, preserving unrelated pre-existing work, and continue directly into audit without stopping.
6. Audit the Level-2 page and every final Level-3 page. Re-run the same three English Level-3 validators after any audit edit;
   validator success is necessary but does not replace the semantic audit.
7. **Hard stop 2 for user approval:** after audit repairs, Level-2 audit, category validation, and audit-summary finalization pass, stop before local Chinese publish-target preparation and ask the user to review and approve the audited result. Do not translate, write Chinese targets, or convert links before approval.
8. After approval, freeze the audited English source set, then translate and prepare the local Chinese publish target for every Level-2 and Level-3 page. Each translated
   Level-3 page must pass the canonical Chinese structure/fixed-language validator before link conversion.
9. Convert links only after every translation worker has completed.
10. Verify the complete local Chinese publish-target file set. Do not commit or push it.
11. Continue directly into `.agents/skills/db-lookup-updater/SKILL.md`; there is no third hard stop. Add the audit-stable English
    category to the lookup builder, resolve ownership or source-backed projection findings under that skill's boundaries, run the
    complete supervised lookup build, and review the tracked `case_lookup/site/mappings.json` delta.
12. Verify the lookup category build, full runtime index, tests, and mustpass coverage.
13. **Final mandatory update:** only after local publish-target preparation and lookup DB verification both pass, update `external/vulkancts/wiki/internal_doc/wiki_rewrite_checklist.md`, then report.
    - Mark the category done.
    - Count final Level-3 pages only: exclude `_brief.md`, source/dispatcher pages folded into Level-2, and helper-only files.
    - Set `UB` from the category's `*_brief.md` count.
    - Recount checked and unchecked rows and update the summary.

## Dispatch invariant

For **writing, audit, and local publish-target preparation**:

> **one subagent = one page = one phase**

An outline batch is a dispatch wave, not a multi-page assignment. Preserve page membership and ordering from the outline. If a wave exceeds the runtime concurrency limit, split it into multiple waves without combining pages into one worker. Never use a multi-page worker as a workaround for rate limits or timeouts.

## Lead-owned responsibilities

The lead agent owns:

- Step 0 and outline creation or resumption;
- user approval hard stop;
- outline interpretation and page-level dispatch prompts;
- Level-2 synthesis and category Background Knowledge consolidation;
- audit-summary creation, incremental aggregation, and finalization;
- category-wide validation;
- page- and category-scoped English structure, registration hierarchy, and wiki-link gate verification;
- confirmation that audited English sources remain frozen throughout local publish-target preparation;
- Chinese structure/fixed-language verification for every translated Level-3 source/target pair;
- link conversion and idempotency checks;
- invocation and verification of `db-lookup-updater` after local publish-target preparation completes;
- review of lookup ownership findings, category coverage, and the tracked `case_lookup/site/mappings.json` delta;
- the final checklist update;
- final counts and completion report.

Workers own only their assigned page in their assigned phase. They must not edit shared summaries, enter a later phase, translate during writing/audit, or run link conversion during translation.

## Final lookup DB phase

Hard stop 2 is the final approval boundary: it separates audited English output from local Chinese publish-target preparation. Once the user approves this phase, complete
the local Chinese publish target and then run `db-lookup-updater` without another approval stop. Do not parallelize publish-target preparation
and DB integration; the order is:

```text
prepare all local Chinese target pages
→ convert and verify publish-target links
→ update and fully verify lookup DB/runtime JSON
→ update final checklist
→ report category completion
```

The lookup phase remains locally supervised because build failures may expose English page ownership defects or require an explicit,
source-backed category projection. Follow `db-lookup-updater` rather than weakening the builder or accepting fallback ownership.
If lookup diagnosis requires an English ownership repair after initial Chinese target preparation, rerun that page's English validators,
regenerate and reconvert the affected local Chinese page, rerun its Chinese validator, then rebuild lookup. This repair loop has no
approval stop, but the category cannot complete while the local Chinese target and final lookup JSON lag behind repaired English evidence.

## Phase contracts and recovery

Before dispatching each phase, read `references/phase-input-contracts.md`. For batching, barriers, retry policy, and verification, read `references/orchestration-and-batching.md` and `references/recovery-and-verification.md`.

Use the filesystem and validators as evidence, not worker claims alone. Classify HTTP 429 responses from the provider payload: retry transient concurrency/short-window rate-limit failures with bounded, page-level retries; treat token-usage, quota, billing, or other account-limit 429s as terminal blockers and stop without retrying. For ordinary failed or missing pages, enumerate missing or suspect outputs and retry only those pages with fresh single-page workers. Preserve successful pages and unrelated pre-existing index state.

## Completion gate

Do not report completion until every outline page is accounted for; English structure, registration hierarchy, wiki-link, semantic
audit, Chinese structure/fixed-language, target-language, local publish-target, and lookup DB gates pass in their owning phases; all publish-target
links are converted and idempotent; the category is covered by the verified runtime lookup index; the tracked mappings JSON and final
checklist match filesystem evidence; audited English pages remain unchanged during local publish-target preparation except for any later evidence-backed
ownership repair required by `db-lookup-updater`; and unauthorized paths and the Git index remain untouched except for the explicit
writing staging checkpoint.

Use `references/completion-report.md` for the final report shape.
