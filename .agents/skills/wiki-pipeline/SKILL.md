---
name: wiki-pipeline
description: Use for end-to-end VK-GL-CTS wiki category work. Follow the rewrite outline, dispatch one page per subagent per phase, then run rewrite, audit, and publish with page-level recovery and final verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, pipeline, orchestration, rewrite, audit, publish]
    related_skills: []
---

# Wiki Pipeline

## Purpose

Orchestrate one complete project-local wiki category lifecycle:

`outline → rewrite → Level-2 synthesis → audit → Chinese publish → final verification → checklist`

This is a **lead-agent orchestration skill**. Load and follow the project-local primary skills instead of duplicating their page-writing, auditing, translation, shader, or link-conversion rules:

- `.agents/skills/wiki-rewriter/SKILL.md`
- `.agents/skills/wiki-auditor/SKILL.md`
- `.agents/skills/wiki-publisher/SKILL.md`

Read their required references and helper skills as those primary skills direct.

## Non-negotiable workflow

1. Run wiki-rewriter Step 0 yourself as lead agent: inspect category state and create or resume `external/vulkancts/wiki/internal_doc/<category>_rewrite_outline.md`.
2. **Hard stop 1 for user approval:** when Step 0 creates a new outline for a new category, stop and ask the user to approve it before inspecting, briefing, or rewriting pages. Resume only after approval or an explicit request to continue. A resumed category with an existing approved outline skips only this checkpoint.
3. Follow the approved outline's batches exactly for rewrite dispatch.
4. Rewrite all assigned Level-3 pages. A page stabilizes only after the canonical English structure, registration hierarchy, and
   wiki-link validators pass. Then synthesize the Level-2 page after every Level-3 page is stable.
5. Stage the changes produced by the rewrite phase, preserving unrelated pre-existing work, and continue directly into audit without stopping.
6. Audit the Level-2 page and every rewritten Level-3 page. Re-run the same three English Level-3 validators after any audit edit;
   validator success is necessary but does not replace the semantic audit.
7. **Hard stop 2 for user approval:** after audit repairs, Level-2 audit, category validation, and audit-summary finalization pass, stop before publish and ask the user to review and approve the audited result. Do not translate, publish, or convert links before approval.
8. After approval, freeze the audited English source set, then translate and publish every Level-2 and Level-3 page. Each translated
   Level-3 page must pass the canonical Chinese structure/fixed-language validator before link conversion.
9. Convert links only after every translation worker has completed.
10. Verify the fully published category.
11. **Final mandatory update:** only after all publication and verification gates pass, update `external/vulkancts/wiki/internal_doc/wiki_rewrite_checklist.md`, then report.
    - Mark the category done.
    - Count rewritten Level-3 pages only: exclude `_brief.md`, legacy `vkt*.md`, and dispatcher pages folded into Level-2.
    - Set `UB` from the category's `*_brief.md` count.
    - Recount checked and unchecked rows and update the summary.

## Dispatch invariant

For **rewrite, audit, and publish**:

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
- confirmation that audited English sources remain frozen throughout publish;
- Chinese structure/fixed-language verification for every translated Level-3 source/target pair;
- link conversion and idempotency checks;
- the final checklist update;
- final counts and completion report.

Workers own only their assigned page in their assigned phase. They must not edit shared summaries, enter a later phase, translate during rewrite/audit, or run link conversion during translation.

## Phase contracts and recovery

Before dispatching each phase, read `references/phase-input-contracts.md`. For batching, barriers, retry policy, and verification, read `references/orchestration-and-batching.md` and `references/recovery-and-verification.md`.

Use the filesystem and validators as evidence, not worker claims alone. Classify HTTP 429 responses from the provider payload: retry transient concurrency/short-window rate-limit failures with bounded, page-level retries; treat token-usage, quota, billing, or other account-limit 429s as terminal blockers and stop without retrying. For ordinary failed or missing pages, enumerate missing or suspect outputs and retry only those pages with fresh single-page workers. Preserve successful pages and unrelated pre-existing index state.

## Completion gate

Do not report completion until every outline page is accounted for; English structure, registration hierarchy, wiki-link, semantic
audit, Chinese structure/fixed-language, target-language, and category gates pass in their owning phases; all links are converted and
idempotent; the final checklist update matches filesystem evidence; audited English pages remain unchanged during publish; and
unauthorized paths and the Git index remain untouched except for the explicit rewrite staging checkpoint.

Use `references/completion-report.md` for the final report shape.
