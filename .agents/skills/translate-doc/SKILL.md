---
name: translate-doc
description: Translate redesigned VK-GL-CTS wiki markdown from canonical English local wiki pages into Mandarin Chinese GitLab Wiki publish-target pages while preserving formatting, links, code, and Vulkan/CTS terminology
adapted from: <https://mcpmarket.com/en/tools/skills/markdown-doc-translator>
---

# Translate Doc

Translate redesigned VK-GL-CTS wiki documentation from the canonical English local wiki under
`external/vulkancts/wiki/` into Mandarin Chinese pages under the GitLab Wiki repo clone
`vkcts-wiki-pages/`.

This project-scoped skill is specialized for the Vulkan CTS wiki publishing workflow. It is not a
generic documentation translator.

## Primary Goal

Produce readable Mandarin Chinese wiki pages for internal readers while preserving:

- Markdown structure.
- Source evidence links.
- File names and directory layout.
- Code blocks and inline code.
- Registered test paths and identifiers.
- Vulkan/CTS terminology that readers normally understand in English.

The English local wiki remains canonical and read-only during translation. Translated output is a
generated publish artifact in `vkcts-wiki-pages/`.

## Scope

This skill targets the redesigned wiki pages only.

Supported canonical sources:

- Level-2 category pages under `external/vulkancts/wiki/categories/` following the redesigned
  Level-2 structure.
- Level-3 pages under `external/vulkancts/wiki/testfiles/<category>/` following the redesigned
  Level-3 structure.
- Other explicitly requested redesigned user-facing wiki pages under `external/vulkancts/wiki/`.

Do not optimize for old version-1 source-navigation pages. Old headings such as `File Inventory`,
`Subgroup Structure`, `Source Code`, and old `testfile`-style structures are not compatibility
requirements.

Exclude `external/vulkancts/wiki/internal_doc/` from translation and publishing.

## Translation References

Before translating any page, read all reference files under `.agents/skills/translate-doc/references/`. This is mandatory; do not skip a reference based on expected relevance:

- `references/terminology.zh.md` — canonical Chinese terminology and protection rules.
- `references/level2-template.zh.md` — canonical Level-2 Chinese output shape.
- `references/level3-template.zh.md` — canonical Level-3 Chinese output shape, including shader-walkthrough heading mappings.

The reference files are the sole canonical owners of Chinese structural shapes, fixed labels, terminology choices, and protection rules. This `SKILL.md` owns workflow, phase ordering, path mapping, dependency gating, and reporting; it does not restate the detailed reference contracts.

## Mandatory Language Worker Dependencies

This skill invokes two global language workers as mandatory quality gates for every translated page:

| Worker skill | Purpose in this workflow |
|---|---|
| `shuorenhua` | Primary Chinese technical-doc naturalness and translationese cleanup pass. |
| `humanizer-zh` | Secondary Chinese residual AI-pattern pass. |

Before translating, confirm both exist under `~/.agents/skills/`. If either is missing, stop and ask the user to install it:

```bash
npx skills add MrGeDiao/shuorenhua -g
npx skills add op7418/humanizer-zh -g
```

Run `shuorenhua` before `humanizer-zh`. These workers may improve language only; preserve factual claims, links, paths, identifiers,
code, shader assembly, filenames, mustpass references, and exact Vulkan/CTS terminology.

## Trigger

```text
/translate-doc <target>
/translate-doc <target> --to zh
```

`<target>` can be:

- A single canonical wiki file, such as `external/vulkancts/wiki/categories/memory_model.md`.
- A canonical wiki directory, such as `external/vulkancts/wiki/testfiles/memory_model/`.
- A category name, such as `memory_model`, meaning:
  - `external/vulkancts/wiki/categories/memory_model.md`
  - all `external/vulkancts/wiki/testfiles/memory_model/*.md`

Default direction for VK-GL-CTS wiki publishing is English to Mandarin Chinese. Do not translate the
Chinese publish target back into English unless the user explicitly asks.

## Project-Specific Input and Output Paths

### Canonical Input Root

```text
external/vulkancts/wiki/
```

This tree is the English canonical source. Do not edit it during translation.

### Publish Output Root

```text
vkcts-wiki-pages/
```

This tree is the GitLab Wiki repo clone. Translation output is written here in place.

### Output Path Mapping

Preserve relative paths and filenames from `external/vulkancts/wiki/` to `vkcts-wiki-pages/`, with
one landing-page exception and one publish-layout transformation.

| Canonical English source | Chinese publish target |
|--------------------------|------------------------|
| `external/vulkancts/wiki/README.md` | `vkcts-wiki-pages/home.md` |
| `external/vulkancts/wiki/CTS_Framework.md` | `vkcts-wiki-pages/CTS_Framework.md` |
| `external/vulkancts/wiki/Objectives.md` | `vkcts-wiki-pages/Objectives.md` |
| `external/vulkancts/wiki/categories/memory_model.md` | `vkcts-wiki-pages/categories/memory_model.md` |
| `external/vulkancts/wiki/testfiles/memory_model/vktMemoryModelMessagePassing.md` | `vkcts-wiki-pages/categories/memory_model/vktMemoryModelMessagePassing.md` |

Rules:

- Do **not** add `.zh.md` suffixes.
- Do **not** translate filenames.
- Do **not** translate directory names.
- Do **not** place translated files next to the English canonical files.
- Create missing output directories under `vkcts-wiki-pages/` as needed.
- Exclude `external/vulkancts/wiki/internal_doc/` from translation and publishing.
- Level-2 category pages still publish to `vkcts-wiki-pages/categories/<category>.md`.
- Level-3 pages publish under the matching category directory, `vkcts-wiki-pages/categories/<category>/<page>.md`, so GitLab Wiki can show one category page plus its expandable child pages together in the sidebar.

## Markdown Link Rules

Translation should preserve markdown link targets, including relative paths and `.md` suffixes. The
translator is **not** responsible for converting GitLab Wiki page links such as
`categories/memory_model.md` to `categories/memory_model`; that belongs to the `wiki-publisher` link
conversion phase.

The only markdown-link change this skill should make is for `#fragment` section-heading references
whose target heading is translated.

Rules:

- Preserve everything before `#` exactly, including relative paths and `.md` extensions.
- Translate only the section-heading fragment after `#` when the referenced heading is translated.
- This applies to same-page links and cross-page links.
- Do not add compatibility HTML anchors such as `<a id="category-index"></a>` unless there is a
  specific verified need.

## Content Protection and Terminology

`references/terminology.zh.md` is the sole canonical owner of the protection rules (what must remain unchanged), the hierarchy terminology mappings, the singular/plural preservation rules, and the allowed tree-comment translations. Apply it directly; this workflow does not restate those contracts.

`references/level2-template.zh.md` and `references/level3-template.zh.md` are the sole canonical owners of fixed Chinese headings, heading translation rules, and heading-detail examples. Apply the relevant template directly.

Workflow-specific protection notes not restated in the references:
- In `#### SPIR-V` sections, keep the `spirv-dis` assembly inside `llvm` code fences exactly unchanged. Translate only fixed header fields and HTML summary text using the reference mapping.
- Do not introduce a separate translated `SPIR-V version` field; `Target SPIRV version` is the single version metadata field.
- Preserve `shader-analyzer` factual precision in `## Shader Analysis`: translate surrounding prose, table prose, bullets, and wiki-authored `///` GLSL comments, but do not simplify, remove, or re-interpret annotated GLSL, resource facts, synchronization semantics, validation meaning, parameter-variation coverage, or source-evidence links.
- Do not introduce new factual claims while translating.
- Do not remove source links, mustpass links, or evidence links.
- Do not change code examples.
- Do not translate `external/vulkancts/wiki/internal_doc/` documents.

## Workflow

### Single File Mode

1. Read the canonical English source file under `external/vulkancts/wiki/`.
2. Determine whether it is a Level-2 category page, Level-3 page, or other redesigned user-facing page.
3. Read `references/terminology.zh.md` and the relevant template reference.
4. Determine the publish target under `vkcts-wiki-pages/` using the mapping rules.
5. Translate prose to Mandarin Chinese using the terminology and template references.
6. Preserve protected content.
7. Translate `#fragment` section-heading references when their target headings are translated, while
   preserving link paths before `#` exactly.
8. Write the translation incrementally, never the whole file in one action:
   1. Create the empty publish target file at the path determined in step 4.
   2. Append the translation one section at a time, where a section is one `##` block together with
      its subsections, tables, and fenced code.
   3. After the final section, re-read the assembled file once to verify section boundaries and
      ordering before running the language workers.
9. Invoke the required Chinese language worker skills on the written target file in this exact order:
   1. `shuorenhua`
   2. `humanizer-zh`
10. Run the validation checklist below.
11. Report source file, target file, reference files used, language worker passes completed, and any translated heading-fragment
    links.

### Category Mode

1. Resolve the category to:
   - `external/vulkancts/wiki/categories/<category>.md`
   - all `external/vulkancts/wiki/testfiles/<category>/*.md`
2. Translate each file to the corresponding path under `vkcts-wiki-pages/`, following the Single File
   Mode procedure: read the whole source first, then write incrementally section by section.
3. For the Level-2 page, use `references/level2-template.zh.md` plus `references/terminology.zh.md`.
4. For each Level-3 page, use `references/level3-template.zh.md` plus `references/terminology.zh.md`.
5. Preserve filenames.
6. Preserve canonical directory identity at the category level, but note the publish-tree transformation:
   - Level-2 page -> `vkcts-wiki-pages/categories/<category>.md`
   - Level-3 page -> `vkcts-wiki-pages/categories/<category>/<page>.md`
7. Translate heading fragments after `#` in markdown links when their target headings are translated.
8. Invoke the required Chinese language worker skills on every translated output file in this exact order:
   1. `shuorenhua`
   2. `humanizer-zh`
9. Run the validation checklist below for every translated output file.
10. Report translated file count, skipped files, reference files used, language worker passes completed, and any unresolved warnings.

### Directory Mode

1. Scan the requested canonical source directory for `.md` files.
2. Exclude `internal_doc/` and existing generated/temporary files.
3. Translate files to matching relative paths under `vkcts-wiki-pages/`.
4. Preserve filenames. Preserve the canonical category identity, but allow the publish-tree layout transformation where Level-3 pages move under `vkcts-wiki-pages/categories/<category>/`.
5. Translate heading fragments after `#` in markdown links when their target headings are translated.
6. Invoke the required Chinese language worker skills on every translated output file in this exact order:
   1. `shuorenhua`
   2. `humanizer-zh`
7. Run the validation checklist below for every translated output file.
8. Report translated file count, skipped files, reference files used, language worker passes completed, and any unresolved warnings.

## Validation Checklist

After translation, verify:

- Output follows the canonical-to-publish path mapping, including the `README.md` → `home.md` exception.
- Required terminology and page-type references were applied.
- Every rule in `Content That Must Remain Unchanged` passes, including the special handling for wiki-authored `///` comments and
  registration-tree annotations.
- Markdown paths before `#` remain unchanged and translated heading fragments resolve to translated headings.
- `## Shader Analysis` preserves generated code and SPIR-V while translating only the permitted explanatory content.
- No obsolete version-1 structure was introduced.
- Explanatory prose is readable Mandarin Chinese with limited, intentional English technical terms.
- `shuorenhua` and `humanizer-zh` completed in that order after translation.
