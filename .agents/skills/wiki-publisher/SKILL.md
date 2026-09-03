---
name: wiki-publisher
description: Prepare translated VK-GL-CTS pages in the local GitLab Wiki publish-target checkout.
---

# Wiki Publish-Target Preparer

Prepare one VK-GL-CTS wiki category in the local GitLab Wiki publish-target checkout.

In this skill, **publish** means writing and validating the local files under `vkcts-wiki-pages/`. It does not mean remote
publication. This skill never stages, commits, or pushes either repository. A pipeline approval or waived hard stop authorizes the
local preparation workflow only; it does not authorize Git commit or push.

## Scope and Execution Model

Apply this skill one category at a time unless the user explicitly requests a narrower scope.

For normal category publishing, use Orchestrator mode to coordinate page-scoped workers with fixed roles:

- One Level-2 translation worker translates `external/vulkancts/wiki/categories/<category>.md`.
- One Level-3 translation worker translates exactly one canonical English page under
  `external/vulkancts/wiki/testfiles/<category>/`.
- Exclude Understanding Brief files from publisher inputs. Files matching
  `external/vulkancts/wiki/testfiles/<category>/*_brief.md` are internal English-only understanding notes for writing work; do not
  translate, publish, link-convert, or count them as Level-3 publish pages.
- Prepared Level-3 outputs live under the category directory,
  `vkcts-wiki-pages/categories/<category>/`, so GitLab Wiki can show a category page and its
  expandable child pages together in the sidebar.
- A category page list is a dispatch wave, not a multi-page worker assignment. Respect the runtime concurrency limit by using
  successive waves; never combine multiple Level-3 pages into one worker.
- One link-conversion worker runs the deterministic conversion script after all translation workers finish.

For rare narrower requests, such as publishing or repairing a single markdown file, the current agent may act as the worker directly
while still following this skill and its mandatory dependencies.

### Orchestrator worker dispatch

Before assigning any worker, read `references/worker-dispatch-templates.md`. This is mandatory, not optional. That reference is the sole canonical owner of the dispatch prompt and output-path templates for Level-2, Level-3, and link-conversion workers. Supply only the category name and assigned file list unless a specific request needs extra scope clarification; this `SKILL.md` remains the canonical source for workflow ordering, scope rules, and completion requirements.

## Mandatory Dependency

This skill is a publishing harness; it does not translate content. Before link conversion, every translation worker must read and
follow [`translate-doc`](../translate-doc/SKILL.md), which owns translation paths, protected content, terminology, language-skill
dependencies, and validation. Do not continue unless the worker confirms that skill and its checklist completed successfully.

## Workflow

### Translation Workers

1. Invoke [`translate-doc`](../translate-doc/SKILL.md) for the assigned files.
   - The Level-2 worker owns only `external/vulkancts/wiki/categories/<category>.md`.
   - Each Level-3 worker owns only its one assigned English source and one exact Chinese target.
   - Exclude `*_brief.md` internal notes and do not edit the canonical English wiki.
   - For each assigned page, load and apply `shuorenhua` followed by `humanizer-zh` inside the translation worker, as required by `translate-doc`. Do not dispatch a separate language-review agent or launch a separate chat, session, or process.
   - Complete all `translate-doc` dependency, output, and validation requirements before reporting completion.

2. Run a pre-publish-target translation guard for every assigned translated markdown file.
    - Fail the translation task if protected content appears translated or corrupted.
    - Check for Chinese characters inside inline-code identifiers, source filenames, URL path segments,
      and registered test names.
    - Check for excessive untranslated English prose outside protected technical terms.
    - Run the structural verification script for each translated file:
      ```bash
      python3 .agents/skills/wiki-publisher/scripts/verify_translation_structure.py \
        --source external/vulkancts/wiki/testfiles/<category>/<page>.md \
        --target vkcts-wiki-pages/categories/<category>/<page>.md
      ```
      This guard first runs the current canonical English Level-3 structure validator, then checks
      the corresponding fixed Chinese headings/phrases, walkthrough numbering and subsection order,
      parameter paths and canonical tables, SPIR-V metadata/details wrappers, multi-stage H5
      organization, cause-analysis labels, and per-section structural parity. A failure means the
      source is not canonical or the translation has a structural/fixed-language mismatch.
    - If any guard fails, fix the translation before reporting completion.
    - Rerun the guard after `shuorenhua` and `humanizer-zh`; language cleanup is not allowed to leave fixed headings, protected
      content, walkthrough structure, or SPIR-V artifacts invalid.

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
7. Confirm the local category path and child-page links use the layout expected to form one expandable category node after a user
   later commits and pushes the publish-target repository. Do not inspect or mutate the remote Wiki as part of this skill.

## Required Completion Report

The completion summary MUST include:

- The category name.
- The canonical source paths translated.
- The publish target paths written.
- A statement that `translate-doc` was invoked and its validation checklist passed.
- A statement that the mandatory `shuorenhua` and `humanizer-zh` language-skill passes were applied by the translation workers for the translated files, in that order.
- The link conversion commands or files processed.
- Any skipped files or unresolved validation warnings.
- Per-page canonical Chinese validator results for every Level-3 source/target pair.

If `translate-doc` was not invoked and validated, the task is incomplete and MUST be reported as failed.

## Check Mode

Use `--check` only for CI or manual preflight checks:

```bash
python3 .agents/skills/wiki-publisher/scripts/convert_markdown_links.py --check vkcts-wiki-pages/categories/<category>.md
```

A non-zero `--check` result means the file still needs conversion.

## Scope Notes

- Keep the markdown link conversion script as the deterministic implementation for publish-target links.
- `vkcts-wiki-pages/home.md` is preconfigured and remains untouched during local publish-target preparation.
- Do not add publish workflow state or temporary notes to user-facing wiki pages.
- Leave all prepared Chinese pages as local working-tree changes. Do not run `git add`, `git commit`, or `git push` in either the
  outer repository or the nested `vkcts-wiki-pages/` repository.
