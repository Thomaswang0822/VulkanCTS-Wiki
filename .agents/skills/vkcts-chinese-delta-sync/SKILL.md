---
name: vkcts-chinese-delta-sync
description: Use when syncing Class A English VKCTS Wiki deltas into published Chinese pages. Guides lead-agent classification consumption, one-page worker dispatch, review, validation, and tracker updates.
---

# VKCTS Chinese Delta Sync

Use this temporary orchestration skill only for **Class A — localized delta sync** pages in the completed English Wiki repair. It guides the lead agent; page workers receive a narrow prompt derived from this workflow.

This skill does not classify pages and does not handle Class B clean republishing. The lead classification already exists in the tracker.

## Fixed repositories and tracker

Source repository:

```text
/home/wanghaoxuan/Documents/repos/VK-GL-CTS
```

Published Chinese Wiki repository:

```text
/home/wanghaoxuan/Documents/repos/VK-GL-CTS/vkcts-wiki-pages
```

Always begin by reading:

```text
external/vulkancts/wiki/internal_doc/chinese_pages_requiring_republish.md
```

Treat its Class A checkboxes as the complete work queue and progress record:

- `[ ]` means pending Class A sync;
- `[x]` means lead-reviewed and validated;
- do not dispatch Class B or Class C pages;
- workers must not edit the tracker;
- the lead updates checkboxes and aggregate counts only after verification.

## Input and output contract

For each selected Class A page:

```text
English input:
external/vulkancts/wiki/testfiles/<category>/<Page>.md

Chinese output:
vkcts-wiki-pages/categories/<category>/<Page>.md
```

The authoritative semantic input is the direct tree-to-tree net diff:

```bash
git diff before_repair_reference..vkcts-wiki -- \
  external/vulkancts/wiki/testfiles/<category>/<Page>.md
```

Use `..`, not `...`. The branches have non-linear merge history, so merge-base diff is not authoritative.

Every worker must also read:

```bash
git show before_repair_reference:external/vulkancts/wiki/testfiles/<category>/<Page>.md
```

and the current English and Chinese files. The diff says what changed; the full files supply context and existing Chinese terminology.

## Lead-agent workflow

### 1. Preflight

Before dispatching:

1. Read the tracker and select only unchecked Class A pages.
2. Confirm both repositories' status.
3. Preserve unrelated user changes and the Git index.
4. Confirm each English page and corresponding Chinese page exist.
5. Assign one worker to one Chinese page. Never give two live workers the same page.
6. Run at most five independent workers concurrently.

Do not ask workers to classify pages. Classification is already complete and belongs to the lead.

### 2. Dispatch exact page-scoped workers

Give every worker the shared instruction below, replacing `<English page>` and `<Chinese page>` with exact paths.

```text
Repository: /home/wanghaoxuan/Documents/repos/VK-GL-CTS. English source repo is the outer repository; published Chinese Wiki is the nested repository at /home/wanghaoxuan/Documents/repos/VK-GL-CTS/vkcts-wiki-pages.

This page is already classified by the lead as Class A (localized delta sync). Do not reclassify it. Work only on `<Chinese page>`. Do not edit the English source, CTS source, mustpass files, tracker, Git index, any skill, or any other Chinese page. Do not commit or push.

Read all four inputs before editing:
1. `git diff before_repair_reference..vkcts-wiki -- <English page>`
2. `git show before_repair_reference:<English page>`
3. the current English file `<English page>`
4. the current Chinese file `<Chinese page>`

Apply only the semantic or structural delta visible in the authoritative English net diff. Do not retranslate, rewrite, or reformat unaffected Chinese content. Preserve exact identifiers, registration paths, code, shader/SPIR-V artifacts, source links, filenames, and technical meaning. Match terminology and fixed Chinese wording from `.agents/skills/translate-doc/references/terminology.zh.md` and the existing category style. In particular, preserve the canonical fixed headings, labels, and table headers enforced by the Chinese validator.

Use a targeted edit. Then inspect the page-specific Chinese diff and run from the source repository:

`python3 .agents/skills/wiki-publisher/scripts/verify_translation_structure.py --source <English page> --target <Chinese page>`

`python3 .agents/skills/wiki-publisher/scripts/convert_markdown_links.py --check <Chinese page>`

Also run `git diff --check` inside `vkcts-wiki-pages`.

Return:
- exact Chinese file changed;
- concise list of synchronized deltas;
- page-specific diff stat;
- validator, link-check, and diff-check results;
- confirmation that no other file was edited.
```

The worker's role is mechanical delta application. It may report a blocker, but it must not broaden scope, rewrite the page, switch to full republish, or modify the tracker.

### 3. Lead review each returned page

Worker summaries are not proof. For every page, the lead independently reads:

```bash
git diff before_repair_reference..vkcts-wiki -- <English page>
git -C vkcts-wiki-pages diff -- <published relative Chinese path>
```

Confirm:

- every semantic English delta has a corresponding Chinese delta;
- no unrelated Chinese prose was rewritten;
- exact protected content stayed unchanged unless the English diff changed it;
- full representative paths retain `dEQP-VK.`;
- fixed Chinese headings, labels, and table headers follow `terminology.zh.md`;
- terminology and capitalization match neighboring Chinese content;
- links remain in already-converted published form;
- the worker changed only its assigned page.

If a worker introduces a small style inconsistency, make the smallest lead correction and rerun validation. Do not turn the review into a broader rewrite.

### 4. Run exact validation

For every modified page, run from the source repository:

```bash
python3 .agents/skills/wiki-publisher/scripts/verify_translation_structure.py \
  --source external/vulkancts/wiki/testfiles/<category>/<Page>.md \
  --target vkcts-wiki-pages/categories/<category>/<Page>.md \
  --verbose
```

This validator:

- first runs the current canonical English Level-3 validator;
- checks fixed Chinese headings and phrases;
- checks walkthrough numbering, subsection order, representative paths, canonical tables, SPIR-V wrappers/metadata, cause labels, and multi-stage H5 alignment;
- compares stable per-section structures between source and target.

Then run:

```bash
python3 .agents/skills/wiki-publisher/scripts/convert_markdown_links.py \
  --check vkcts-wiki-pages/categories/<category>/<Page>.md

git -C vkcts-wiki-pages diff --check
```

A page is incomplete until all commands pass.

### 5. Update tracker progress

After lead review and validation pass, change only that page's Class A checkbox from `[ ]` to `[x]`.

Recompute, rather than estimate, aggregate progress:

- Class A total;
- checked Class A count;
- remaining Class A count.

Update the tracker summary accordingly. Do not mark a worker-completed but unreviewed page done.

### 6. Report a batch

Report:

- category and pages completed;
- exact Chinese files modified;
- concise delta summary per page;
- validator/link/diff-check results;
- Class A completed and remaining totals;
- blockers or pages deliberately left unchanged.

Do not commit or push unless the user explicitly requests it.

## Scope boundaries

This skill handles only localized Chinese deltas:

- no Class B deletion or clean republish;
- no Class C edits;
- no English page modifications;
- no source, mustpass, brief, or Level-2 edits;
- no global-skill creation or modification by workers;
- no Git index/history operations;
- no automatic publishing.

If a Class A worker discovers that the target cannot be safely patched locally, stop that page and report the evidence to the lead. Do not silently reclassify it or invoke `wiki-publisher`.

## Temporary lifecycle

This is a temporary repository-local orchestration skill. Keep it until every Class A checkbox is complete and the user confirms the delta-sync phase is finished. At that point, review references to this skill and ask/confirm before deleting it. Do not delete the tracker or this skill merely because one category or batch is complete.
