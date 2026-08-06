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

`outline → rewrite → Level-2 synthesis → audit → Chinese publish → final verification`

This is a **lead-agent orchestration skill**. Load and follow the project-local primary skills instead of duplicating their page-writing, auditing, translation, shader, or link-conversion rules:

- `.agents/skills/wiki-rewriter/SKILL.md`
- `.agents/skills/wiki-auditor/SKILL.md`
- `.agents/skills/wiki-publisher/SKILL.md`

Read their required references and helper skills as those primary skills direct.

## Non-negotiable workflow

1. Run wiki-rewriter Step 0 yourself as lead agent: inspect category state and create or resume `external/vulkancts/wiki/internal_doc/<category>_rewrite_outline.md`.
2. **Hard stop 1 for user approval:** when Step 0 creates a new outline for a new category, stop and ask the user to approve it before inspecting, briefing, or rewriting pages. Resume only after approval or an explicit request to continue. A resumed category with an existing approved outline skips only this checkpoint.
3. Follow the approved outline's batches exactly for rewrite dispatch.
4. Rewrite all assigned Level-3 pages, then synthesize the Level-2 page after Level-3 pages stabilize.
5. Stage the changes produced by the rewrite phase, preserving unrelated pre-existing work, and continue directly into audit without stopping.
6. Audit the Level-2 page and every rewritten Level-3 page.
7. **Hard stop 2 for user approval:** after audit repairs, Level-2 audit, category validation, and audit-summary finalization pass, stop before publish and ask the user to review and approve the audited result. Do not translate, publish, convert links, or update publish indexes before approval.
8. After approval, translate and publish every Level-2 and Level-3 page.
9. Convert links only after every translation worker has completed.
10. Verify the final category, update `home.md` and the rewrite checklist, then report.

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
- link conversion and idempotency checks;
- `home.md` and checklist updates;
- final counts and completion report.

Workers own only their assigned page in their assigned phase. They must not edit shared summaries, enter a later phase, translate during rewrite/audit, or run link conversion during translation.

## Phase contracts and recovery

Before dispatching each phase, read `references/phase-input-contracts.md`. For batching, barriers, retry policy, and verification, read `references/orchestration-and-batching.md` and `references/recovery-and-verification.md`.

Use the filesystem and validators as evidence, not worker claims alone. Classify HTTP 429 responses from the provider payload: retry transient concurrency/short-window rate-limit failures with bounded, page-level retries; treat token-usage, quota, billing, or other account-limit 429s as terminal blockers and stop without retrying. For ordinary failed or missing pages, enumerate missing or suspect outputs and retry only those pages with fresh single-page workers. Preserve successful pages and unrelated pre-existing index state.

## Completion gate

Do not report completion until every outline page is accounted for; rewrite, audit, translation, structural, registration/link, and category validations pass; all links are converted and idempotent; `home.md` is correct; checklist counts match filesystem evidence; and canonical English pages, unauthorized paths, and the Git index remain untouched.

Use `references/completion-report.md` for the final report shape.
