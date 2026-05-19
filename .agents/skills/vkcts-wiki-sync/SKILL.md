---
name: vkcts-wiki-sync
description: This skill should be used when maintaining the Vulkan CTS wiki after periodically merging official Khronos Vulkan-GL-CTS upstream changes into a fork. It guides init, category refresh, validation, merge-log updates, and final merge instructions for external/vulkancts/wiki/ after the user has already created a date-stamped merge_main integration branch.
---

# VKCTS Wiki Sync

## Overview

Maintain [external/vulkancts/wiki/](../../../external/vulkancts/wiki/) after periodic upstream Vulkan-GL-CTS syncs.

Use this skill only after the user has created and checked out a merge-specific integration branch such as
`merge_main_YYYY-MM-DD`. The purpose is to compare the current integration branch against previous upstream/wiki state,
identify affected completed wiki categories, refresh stale wiki facts from current source and mustpass evidence, validate
the result, update the durable merge log, and guide the user through the final merge back to `vkcts-wiki`.

This skill complements [wiki-analyzer](../wiki-analyzer/SKILL.md). Use `wiki-analyzer` evidence rules for all factual wiki
claims and validation expectations.

## Non-Negotiable Git Safety Rules

- Run read-only Git commands freely when needed to inspect state, history, diffs, merge bases, commit parents, changed
  paths, and validation evidence.
- Treat these as read-only examples: `git status`, `git branch`, `git log`, `git show`, `git diff`, `git merge-base`,
  `git rev-parse`, `git ls-files`, `git name-status`, `git diff-tree`.
- Do not run editing/history-changing Git commands. This includes `git merge`, `git rebase`, `git reset`, `git checkout`,
  `git switch`, `git cherry-pick`, `git commit`, `git push`, `git tag`, `git stash`, `git clean`, or commands that write
  Git metadata.
- When an editing Git command is needed, present the exact command, explain what it does, explain expected outcomes, and
  ask the user to run it manually.
- Never assume branch names or commit IDs. Read them from Git or from user-provided context.

## Core Evidence Sources

Use only repository evidence for factual wiki updates:

- Vulkan CTS source under [external/vulkancts/](../../../external/vulkancts/), especially
  [modules/vulkan/](../../../external/vulkancts/modules/vulkan/).
- Mustpass files under [external/vulkancts/mustpass/main/](../../../external/vulkancts/mustpass/main/), especially
  `vk-default` and relevant `vksc-default` files.
- [doc/testspecs/VK/apitests.adoc](../../../doc/testspecs/VK/apitests.adoc) when relevant.
- Existing durable sync context in [merge_update_log.md](../../../external/vulkancts/wiki/internal_doc/merge_update_log.md).
- Current temporary per-merge tracker if present, commonly
  [TODOs_after_merge.md](../../../external/vulkancts/wiki/internal_doc/TODOs_after_merge.md).

Prefer current source and mustpass evidence over existing wiki text. Existing wiki pages can guide structure but must not
be treated as authoritative when upstream source changed.

## Phase 1: Init Phase

Goal: produce a temporary, evidence-backed TODO tracker for the current integration branch.

### 1. Confirm Initial State

Run read-only checks:

```bash
git status --short --branch
git branch --show-current
git log --oneline --decorate --max-count=20
git rev-parse HEAD
```

Confirm:
- current branch is a merge-specific integration branch, typically `merge_main_<date>`;
- there are no unresolved conflicts;
- the user has already performed the upstream merge or asks for instructions to do so.

If the upstream merge has not happened, do not perform it. Provide the exact `git merge` command for the user to run.

### 2. Recover Previous Sync Context

Read [merge_update_log.md](../../../external/vulkancts/wiki/internal_doc/merge_update_log.md) if present. Extract:

- last integrated upstream commit/range;
- prior integration branch and merge commit;
- known validator/tooling decisions;
- recurring mustpass layout issues;
- durable merge policy decisions.

Use this to avoid rediscovering past decisions.

### 3. Establish Git Baseline

Use read-only Git commands to identify:

- current integration branch name;
- current HEAD;
- merge commit parents if HEAD is a merge commit or if a recent merge commit exists;
- local wiki parent;
- upstream main parent;
- original common base between local wiki parent and upstream parent;
- changed files from base to upstream parent;
- changed files introduced by local wiki work if needed.

Typical commands:

```bash
git show --stat --summary --format=fuller HEAD
git rev-list --parents -n 1 HEAD
git merge-base <local-wiki-parent> <upstream-main-parent>
git diff --name-status <base>..<upstream-main-parent> -- external/vulkancts/modules/vulkan external/vulkancts/mustpass/main
git diff --name-only --diff-filter=U
```

If HEAD is not the merge commit, use read-only log inspection to find the relevant upstream merge commit.

### 4. Identify Completed Wiki Categories

Read [README.md](../../../external/vulkancts/wiki/README.md) and determine which categories are already marked done.

Rules:
- Only completed categories require immediate post-merge refresh.
- Not-started categories affected by upstream changes should be recorded for future work, but do not refresh their wiki
  pages now unless the user explicitly asks.
- Categories sharing a wiki folder must be considered together. Example: `synchronization` and `synchronization2` share
  [testfiles/synchronization](../../../external/vulkancts/wiki/testfiles/synchronization/).

### 5. Map Changed Source and Mustpass Files to Wiki Impact

For changed upstream files:

- group `external/vulkancts/modules/vulkan/<category>/...` paths by category;
- map source category names to wiki category names when they differ, e.g. `renderpass` → `renderpasses`,
  `device_generated_commands` → `dgc`, `ray_tracing` → `ray_tracing_pipeline` if relevant;
- record changed mustpass files under `mustpass/main/vk-default` and relevant `vksc-default` files;
- flag deleted, renamed, or nested mustpass files as validator risk.

### 6. Create Temporary TODO Tracker

Create a concise but complete tracker at
`external/vulkancts/wiki/internal_doc/TODOs_after_merge.md` unless the user requests a different file name.

Include:

- evidence baseline with branch, commits, parents, merge base, conflict status;
- immediate cleanup work list;
- mustpass layout changes needing validator attention;
- completed categories requiring review with exact changed source/mustpass files;
- completed categories not touched by upstream source changes;
- affected not-started categories for future scope;
- new files inside not-started categories;
- recommended execution order.

Keep the tracker actionable, not verbose prose. It is temporary working material unless the user says otherwise.

## Phase 2: Refresh Phase

Goal: refresh affected completed wiki categories against current source and mustpass evidence.

### 1. Work in Category-Sized Batches

Default to one category at a time. If the user asks, batch several small low-risk categories together.

For each batch:

1. Read the TODO tracker section for the category.
2. Inspect upstream diffs for listed changed source/mustpass files.
3. Read current wiki category and Level-3 pages.
4. Decide whether the diff changes documented facts.
5. Edit only stale facts proven by current source or mustpass evidence.
6. Run category-scoped validation.
7. Update the TODO tracker with review result.
8. Stop for user review unless the user explicitly asks to continue.

### 2. Decide Whether Wiki Updates Are Needed

Update wiki pages only when current source or mustpass files show stale:

- registration paths or hierarchy;
- test families;
- generated parameter dimensions;
- support checks, extensions, features, Vulkan SC guards;
- verification logic;
- scope notes or mustpass mapping;
- source line links or broken local links.

Do not update user-facing wiki for purely mechanical changes, such as:

- helper signature changes with no behavior change;
- removed validation-layer command-line plumbing;
- formatting-only diffs;
- local helper refactors with no documented behavior impact;
- compile-guard adjustments that do not change documented behavior.

Still record the no-update decision in the TODO tracker.

### 3. Follow Wiki Analyzer Evidence Rules

For user-facing docs:

- Use GitHub fragment syntax for source line links, e.g. `file.cpp#L123` or `file.cpp#L123-L140`.
- Do not use colon-style source line links in wiki docs.
- Link registration claims to registration functions.
- Link verification claims to check/comparison code.
- Avoid overclaiming; state uncertainty when evidence is incomplete.
- Preserve the canonical `## Registration Hierarchy` contract used by
  [verify_registration_paths.py](../wiki-analyzer/scripts/verify_registration_paths.py).

### 4. Validate Each Category Batch

Run category-scoped link validation:

```bash
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose
```

Run registration validation:

```bash
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category>
```

If a category shares wiki files with another category, validate both relevant category pages and shared Level-3 files.

### 5. Produce a Concise Commit Message for Each Batch

After each category or small category batch, provide a concise commit message summarizing:

- what changed in wiki files;
- what changed upstream but required no wiki edit;
- validation performed;
- any validator/tooling change.

Use this shape:

```text
docs(vulkancts): refresh <category> wiki after upstream sync

<Short summary of source/mustpass changes and wiki updates.>

No wiki update was needed for <files/categories> because <reason>.

Validation:
- link validation passed for <scope>
- registration validation passed for <category>, <N> paths checked
```

Do not commit unless the user explicitly asks and permits editing Git commands.

## Phase 3: Wrap-Up Phase

Goal: validate the full user-facing wiki state, update durable process memory, and guide the final merge.

### 1. Confirm TODO Tracker Completion

Search the temporary tracker for unchecked items:

```bash
grep -n "\\[ \\]" external/vulkancts/wiki/internal_doc/TODOs_after_merge.md
```

Complete written actionable items when they are in scope. If an item is a policy decision, ask the user.

### 2. Run Final Validation Sweep

Run a practical user-facing link sweep over completed category and testfile docs:

```bash
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --repo-root . \
  --files $(find external/vulkancts/wiki/categories external/vulkancts/wiki/testfiles -name '*.md' | sort) \
  --verbose
```

Also consider whole-wiki validation:

```bash
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --repo-root . \
  --verbose
```

Interpret whole-wiki failures carefully. Expected non-actionable failures may include:

- [README.md](../../../external/vulkancts/wiki/README.md) links to not-yet-created category pages;
- temporary/internal tracker links to deleted mustpass files preserved as evidence;
- temporary/internal tracker links whose relative paths are not intended as user-facing docs.

Do not silently ignore new failures in user-facing category/testfile docs.

### 3. Update Merge Update Log

Update [merge_update_log.md](../../../external/vulkancts/wiki/internal_doc/merge_update_log.md) with a concise new entry.

Include:

- integration branch and target branch;
- upstream range handled;
- merge commit and parents;
- conflict summary;
- scope decisions;
- mustpass/validator notes;
- completed categories reviewed;
- notable user-facing updates;
- validation summary;
- merge policy decisions or changes.

Keep this log durable and short. Do not copy the full TODO tracker into it.

### 4. Decide Temporary Tracker Handling

Discuss temporary tracker cleanup with the user before final commit.

Default recommendation:
- keep `merge_update_log.md` as durable process memory;
- remove `TODOs_after_merge.md` before final commit if the commit should contain no temporary coordination artifacts;
- keep `TODOs_after_merge.md` during review if the user is still using it.

Do not delete files without user approval.

### 5. Guide Final Merge Back to `vkcts-wiki`

Recommend regular merge, not squash merge, for integration branches that contain upstream history.

Rationale:
- preserves official upstream commits as ancestors of `vkcts-wiki`;
- lets future quarterly syncs compute the correct merge base;
- avoids reprocessing old upstream commits as if they were new;
- improves auditability of what upstream range was integrated.

When ready, present commands for the user to run manually. Example only; adjust branch names from read-only Git state:

```bash
git switch vkcts-wiki
git merge --no-ff merge_main_YYYY-MM-DD
git status --short --branch
```

Explain what each command does. Do not run these commands directly.

## Common Risk Patterns

- Deleted mustpass files that were formerly assumed by docs or validators.
- Mustpass files moved into nested directories.
- Split category names where source directory and wiki category differ.
- Categories sharing one Level-3 folder.
- Mechanical upstream refactors that do not require wiki edits but still shift source line numbers.
- Descriptor/mustpass expansions that add many paths under existing registration roots.
- Vulkan SC compile guards that may or may not change documented behavior.

## Completion Criteria

A sync is ready for final user review when:

- every written TODO item in the temporary tracker is complete or explicitly deferred by user decision;
- affected completed categories have documented review results;
- edited category/testfile docs pass link validation;
- edited/reviewed categories pass registration validation;
- a practical user-facing global link sweep passes;
- [merge_update_log.md](../../../external/vulkancts/wiki/internal_doc/merge_update_log.md) has a concise entry for the sync;
- the user has clear manual Git commands for any remaining merge/commit steps.
