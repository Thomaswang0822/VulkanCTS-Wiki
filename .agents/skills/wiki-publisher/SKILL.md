---
name: wiki-publisher
description: This skill should be used when publishing translated VK-GL-CTS wiki pages for a category from the canonical English wiki into the GitLab Wiki publish target.
---

# Wiki Publisher

Publish one VK-GL-CTS wiki category to the GitLab Wiki publish target.

## Scope and Execution Model

Apply this skill one category at a time unless the user explicitly requests a narrower scope.

For normal category publishing, use Orchestrator mode to coordinate multiple Code-mode workers with fixed
roles:

- One Level-2 translation worker translates `external/vulkancts/wiki/categories/<category>.md`.
- One or more Level-3 translation workers translate publishable rewritten pages under
  `external/vulkancts/wiki/testfiles/<category>/*.md` in batches of at most 5 files per worker.
- Exclude Understanding Brief files from publisher inputs. Files matching
  `external/vulkancts/wiki/testfiles/<category>/*_brief.md` are internal English-only audit notes for rewrite work; do not
  translate, publish, link-convert, or count them in Level-3 batches.
- Published Level-3 outputs live under the published category directory,
  `vkcts-wiki-pages/categories/<category>/`, so GitLab Wiki can show a category page and its
  expandable child pages together in the sidebar.
- Use smaller Level-3 batches for unusually long or complex pages.
- Do not exceed the 5-file Level-3 batch cap.
- One link-conversion worker runs the deterministic conversion script after all translation workers finish.

For rare narrower requests, such as publishing or repairing a single markdown file, the current agent may
act as the worker directly while still following this skill and its mandatory dependencies.

### Orchestrator worker dispatch

Load `references/worker-dispatch-templates.md` before assigning workers. Supply only the category name and assigned file list unless a
specific request needs extra scope clarification; this skill remains the canonical source for workflow details.

## Mandatory Dependency

This skill is a publishing harness; it does not translate content. Before link conversion, every translation worker must read and
follow [`translate-doc`](../translate-doc/SKILL.md), which owns translation paths, protected content, terminology, language-worker
dependencies, and validation. Do not continue unless the worker confirms that skill and its checklist completed successfully.

## Workflow

### Translation Workers

1. Invoke [`translate-doc`](../translate-doc/SKILL.md) for the assigned files.
   - The Level-2 worker owns only `external/vulkancts/wiki/categories/<category>.md`.
   - Each Level-3 worker owns only its assigned publishable batch under `external/vulkancts/wiki/testfiles/<category>/`.
   - Exclude `*_brief.md` internal notes and do not edit the canonical English wiki.
   - Complete all `translate-doc` dependency, output, and validation requirements before reporting completion.

2. Run a pre-publish translation guard for every assigned translated markdown file.
   - Fail the translation task if protected content appears translated or corrupted.
   - Check for Chinese characters inside inline-code identifiers, source filenames, URL path segments,
     and registered test names.
   - Check for excessive untranslated English prose outside protected technical terms.
   - If any guard fails, fix the translation before reporting completion.

3. Translation workers must not run link conversion.
   - Leave markdown link targets in the pre-conversion form required by `translate-doc`.
   - Report the source files translated and publish target files written.

### Link-Conversion Worker

1. Run only after all Level-2 and Level-3 translation workers for the category have completed.
2. Do not translate content.
3. Convert links in every translated markdown file for that category.
   - Run the link conversion script once per translated markdown file.
   - Convert the Level-2 category page:

     ```bash
     python3 .agents/skills/wiki-publisher/scripts/convert_markdown_links.py vkcts-wiki-pages/categories/<category>.md
     ```

   - Enumerate Level-3 testfile pages under `vkcts-wiki-pages/categories/<category>/`.
   - Invoke the script separately for each discovered `.md` file. Do not pass shell globs to the script.

     ```bash
     python3 .agents/skills/wiki-publisher/scripts/convert_markdown_links.py vkcts-wiki-pages/categories/<category>/<page>.md
     ```

4. Confirm source-code and mustpass links converted to GitLab blob URLs without translated path segments.
5. Confirm wiki-page links have the expected GitLab Wiki form.
6. For links from `vkcts-wiki-pages/categories/<category>.md` to child Level-3 pages under the same category,
   prefer the GitLab-tested form `./<category>/<page>` rather than an unprefixed relative path.
7. Confirm the category page and its child Level-3 pages appear under the same expandable category node in the GitLab Wiki sidebar.

### Orchestrator Finalization

After the link-conversion worker completes successfully, update the category row in
`vkcts-wiki-pages/home.md` under the category index table:

- Find the `文档` column link for the published category.
- Remove only the `.md` suffix from that link target, for example `categories/<category>.md` becomes
  `categories/<category>`.
- Do not run the markdown link conversion script on `vkcts-wiki-pages/home.md`.
- Do not change rows for unpublished categories.

## Required Completion Report

The completion summary MUST include:

- The category name.
- The canonical source paths translated.
- The publish target paths written.
- A statement that `translate-doc` was invoked and its validation checklist passed.
- A statement that the mandatory `shuorenhua` and `humanizer-zh` language worker passes were invoked for the translated files.
- The link conversion commands or files processed.
- Confirmation that the `vkcts-wiki-pages/home.md` category-index link was updated for the published category.
- Any skipped files or unresolved validation warnings.

If `translate-doc` was not invoked and validated, the task is incomplete and MUST be reported as failed.

## Check Mode

Use `--check` only for CI or manual preflight checks:

```bash
python3 .agents/skills/wiki-publisher/scripts/convert_markdown_links.py --check vkcts-wiki-pages/categories/<category>.md
```

A non-zero `--check` result means the file still needs conversion.

## Scope Notes

- Keep the markdown link conversion script as the deterministic implementation for publish-target links.
- Do not add publish workflow state or temporary notes to user-facing wiki pages.
