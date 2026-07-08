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

### Orchestrator Worker Dispatch Templates

Keep dispatch prompts intentionally minimal. The category name and assigned file list are the variable
inputs; this skill remains the canonical source for workflow details. Do not duplicate the workflow in a
dispatch prompt unless a specific request needs extra scope clarification.

#### Level-2 Translation Worker

```text
Translate the Level-2 `<category>` category page using `.agents/skills/wiki-publisher/SKILL.md`.

Input:
- `external/vulkancts/wiki/categories/<category>.md`

Output:
- `vkcts-wiki-pages/categories/<category>.md`

Strictly follow the skill's translation-worker requirements. Do not run link conversion. When complete, use `attempt_completion`.
```

#### Level-3 Translation Worker

```text
Translate this `<category>` Level-3 page batch using `.agents/skills/wiki-publisher/SKILL.md`.

Inputs:
- `external/vulkancts/wiki/testfiles/<category>/<file1>.md`
- `external/vulkancts/wiki/testfiles/<category>/<file2>.md`
- `external/vulkancts/wiki/testfiles/<category>/<file3>.md`

Input rule:
- Do not include `*_brief.md` files; Understanding Briefs are internal English-only audit notes and must not be published.

Outputs:
- `vkcts-wiki-pages/categories/<category>/<file1>.md`
- `vkcts-wiki-pages/categories/<category>/<file2>.md`
- `vkcts-wiki-pages/categories/<category>/<file3>.md`

Strictly follow the skill's translation-worker requirements. Do not run link conversion. When complete, use `attempt_completion`.
```

#### Link-Conversion Worker

```text
Run the publish link-conversion phase for the completed `<category>` translations using `.agents/skills/wiki-publisher/SKILL.md`.

Inputs:
- `vkcts-wiki-pages/categories/<category>.md`
- all `vkcts-wiki-pages/categories/<category>/*.md`

Script:
- `.agents/skills/wiki-publisher/scripts/convert_markdown_links.py`

Strictly follow the skill's link-conversion requirements. Do not translate content. When complete, use `attempt_completion`.
```

## Mandatory Dependency

This skill is only a publishing harness. It MUST NOT translate content by itself.

Before any link conversion, the worker MUST explicitly invoke and follow the
[`translate-doc`](../translate-doc/SKILL.md) skill for the requested category.

Hard requirements:

- Read the full `../translate-doc/SKILL.md` file before translating.
- Treat every rule in `translate-doc` as part of this skill's required workflow.
- Confirm the mandatory Chinese language worker skills required by `translate-doc` are installed globally under `~/.agents/skills/`:
  - `shuorenhua`
  - `humanizer-zh`
- If either Chinese language worker skill is missing, STOP before translating and ask the user to install the missing skill globally:

  ```bash
  npx skills add MrGeDiao/shuorenhua -g
  npx skills add op7418/humanizer-zh -g
  ```

- Translate only from the canonical English source under `external/vulkancts/wiki/`.
- Write translated output only under `vkcts-wiki-pages/`.
- Do not perform generic or ad-hoc translation.
- Do not run link conversion until the `translate-doc` validation checklist passes, including the mandatory `shuorenhua` and
  `humanizer-zh` worker passes.
- If the worker cannot confirm `translate-doc` was applied, STOP and report failure instead of publishing.

## Workflow

### Translation Workers

1. Invoke the [`translate-doc`](../translate-doc/SKILL.md) skill first. This step is mandatory.
   - Level-2 translation workers translate only `external/vulkancts/wiki/categories/<category>.md`.
   - Level-3 translation workers translate only their assigned publishable batch under
     `external/vulkancts/wiki/testfiles/<category>/`.
   - Skip `*_brief.md` files. Understanding Briefs are internal rewrite/audit notes, must remain English-only, and are not
     publisher inputs.
   - Write translated output to the corresponding path under `vkcts-wiki-pages/`.
   - Do not edit the English canonical wiki during publishing.
   - Preserve code blocks, inline code, identifiers, filenames, directory names, markdown link targets,
     URL targets, registered test paths, and YAML/machine markers exactly as required by `translate-doc`.
   - Use the heading and terminology rules from `translate-doc`; do not invent a separate translation style.
   - Invoke the mandatory Chinese language worker skills through the `translate-doc` workflow, in the order required there:
     `shuorenhua` first, then `humanizer-zh`.
   - Complete the `translate-doc` validation checklist for the assigned files before reporting completion.

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
