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

Before translating, read the required reference files under `.agents/skills/translate-doc/references/`.

Always read:

- `references/terminology.zh.md`

Also read according to page type:

- Level-2 category page: `references/level2-template.zh.md`
- Level-3 page: `references/level3-template.zh.md`

Rules:

- Treat the reference files as the canonical Chinese structural and terminology guide.
- Do not copy English template guideline prose into Chinese output.
- Use reference templates only for fixed elements: headings, fixed labels, fixed opening sentence
  shapes, fixed table headers, and fixed tree-comment translations.
- If a source heading exactly matches a reference heading, use the reference Chinese heading exactly.
- If a source heading begins with a protected identifier or registered path component, preserve that
  identifier and translate only the explanatory suffix.
- For Level-3 `## Shader Analysis`, apply the dedicated shader-walkthrough heading and terminology
  mappings in `references/level3-template.zh.md` and `references/terminology.zh.md`. These mappings
  cover the current `shader-analyzer` output contract.

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

## Content That Must Remain Unchanged

Do not translate these elements:

1. **Code blocks** fenced by triple backticks — preserve code tokens exactly, including `glsl`, `mermaid`, `drawio`, and `text` fences. The only allowed content translation inside code blocks is wiki-authored explanatory `///` comments in reconstructed GLSL.
2. **Inline code** inside backticks — preserve exactly.
3. **File paths and URL targets** — preserve exactly.
4. **Markdown link target paths before `#`** — preserve exactly; only translate `#fragment` heading
   references when their target headings are translated.
5. **Function names, class names, enum names, struct names, variables, constants, macros, CLI flags**.
6. **Registered test paths and test case names**, such as `dEQP-VK.memory_model.shared.16bit.arrays_of_arrays.3`.
7. **Source filenames and wiki filenames**, such as `vktMemoryModelMessagePassing.cpp` and
   `vktMemoryModelMessagePassing.md`.
8. **Directory names**, such as `categories/`, `testfiles/`, `modules/vulkan/`, `mustpass/`.
9. **YAML frontmatter** — preserve exactly.
10. **Markdown table structure** — translate cell prose while preserving `|` and separator rows.
11. **ASCII diagrams and registration trees** — preserve registered path components exactly.
12. **HTML comments or machine markers** — preserve exactly.
13. **Source-generated comments inside code blocks** — preserve exact `//` comments from generated shader source. Translate wiki-authored explanatory `///` GLSL comments while preserving the `///` marker, indentation, and referenced identifiers.

Allowed tree-comment translation:

- Translate explanatory comments in registration trees when they are not registered path components.
- Example: `(registration only)` becomes `(仅注册)`.

## VK-GL-CTS Terminology Policy

Use `references/terminology.zh.md` as the authoritative terminology reference.

Core rules:

- Translate ordinary explanatory prose naturally into Mandarin Chinese.
- Preserve exact registered path components, filenames, identifiers, inline code, and code blocks.
- Use the redesigned wiki hierarchy terminology consistently:
  - `test category` → `测试类别`.
  - `test family` → `测试子族`.
  - `intermediate node` → `中间节点`.
  - `test case` / `test case leaf` → `单个测试`.
- Do not use `节点` for a test category or a page-scope test family.
- Preserve technical Vulkan/GLSL terms such as `subgroup`, `workgroup`, and `shader` when translating them would be less familiar
  or would confuse technical meaning.
- Preserve singular/plural distinctions when they affect technical scope:
  - If a technical term is kept in English, keep its English singular or plural form, for example `race instance` vs
    `race instances`.
  - If a plural term is translated into Chinese and plurality matters, add a natural scope marker such as `多个`, `一组`,
    `一系列`, `这些`, `若干`, `集合`, or use a context-specific rephrasing.
  - Do not mechanically mark every English plural; apply this only when plurality affects scope, behavior, or interpretation.
- Preserve exact test paths, for example `memory_model.shared.16bit.arrays_of_arrays.3`.

Use natural Chinese sentence structure around preserved English terms.

Good:

```markdown
`memory_model` 测试类别包含五个注册测试子族。
```

Bad:

```markdown
`memory_model` test category 包含 five registered test families。
```

## Heading Translation Rules

- Translate Markdown headings to Mandarin Chinese for readability.
- Preserve heading levels and numbering.
- Use the relevant reference template for fixed headings:
  - `references/level2-template.zh.md` for Level-2 pages.
  - `references/level3-template.zh.md` for Level-3 pages.
- Same-page links should target the translated heading anchor directly.
- Cross-page links with a `#fragment` should preserve everything before `#` and translate only the
  heading fragment when it points to a translated heading.
- Do not keep English headings merely to preserve old English anchors.
- Do not add compatibility HTML anchors unless the user explicitly asks.

### Heading Details

- If a heading has a numeric prefix, preserve the prefix and translate the heading text.
- If a heading begins with a protected identifier, registered path component, source filename, or test
  family name, preserve that identifier and translate only the explanatory suffix.
  - Example: `### basic_arrays — Arrays of basic types` becomes
    `### basic_arrays — 基本类型数组`.
- If a markdown link points to a canonical heading, update only the `#fragment` to the translated
  Chinese heading anchor.

## Translation Quality Requirements

- Preserve Markdown formatting: headings, lists, tables, links, emphasis, code fences.
- Use natural Mandarin Chinese for explanatory prose.
- Avoid excessive English-Chinese mixing for ordinary explanatory terms.
- Keep domain terms in English when translating them would be less familiar to Vulkan/CTS readers.
- Translate table cell prose, list descriptions, and category explanations unless they are identifiers
  or domain terms that should remain English.
- Keep left-side category names, path components, and filenames unchanged; translate right-side explanations.
- Preserve `shader-analyzer` factual precision in `## Shader Analysis`: translate surrounding prose, table prose,
  bullets, and wiki-authored `///` GLSL comments, but do not simplify, remove, or re-interpret annotated GLSL,
  resource facts, synchronization semantics, validation meaning, parameter-variation coverage, or source-evidence links.
- In `#### SPIR-V` sections, keep the `spirv-dis` assembly inside `llvm` code fences exactly unchanged. Translate only
  fixed header fields and HTML summary text using the reference mapping, for example `Status` -> `状态`,
  `Source` -> `来源`, `Stage` -> `阶段`, and `Target SPIRV version` -> `目标 SPIRV 版本`.
- Do not introduce a separate translated `SPIR-V version` field; `Target SPIRV version` is the single version metadata field.
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
8. Write or overwrite the publish target file.
9. Report source file, target file, reference files used, and any translated heading-fragment links.

### Category Mode

1. Resolve the category to:
   - `external/vulkancts/wiki/categories/<category>.md`
   - all `external/vulkancts/wiki/testfiles/<category>/*.md`
2. Translate each file to the corresponding path under `vkcts-wiki-pages/`.
3. For the Level-2 page, use `references/level2-template.zh.md` plus `references/terminology.zh.md`.
4. For each Level-3 page, use `references/level3-template.zh.md` plus `references/terminology.zh.md`.
5. Preserve filenames.
6. Preserve canonical directory identity at the category level, but note the publish-tree transformation:
   - Level-2 page -> `vkcts-wiki-pages/categories/<category>.md`
   - Level-3 page -> `vkcts-wiki-pages/categories/<category>/<page>.md`
7. Translate heading fragments after `#` in markdown links when their target headings are translated.
8. Report translated file count, skipped files, reference files used, and any unresolved warnings.

### Directory Mode

1. Scan the requested canonical source directory for `.md` files.
2. Exclude `internal_doc/` and existing generated/temporary files.
3. Translate files to matching relative paths under `vkcts-wiki-pages/`.
4. Preserve filenames. Preserve the canonical category identity, but allow the publish-tree layout transformation where Level-3 pages move under `vkcts-wiki-pages/categories/<category>/`.
5. Translate heading fragments after `#` in markdown links when their target headings are translated.
6. Report translated file count, skipped files, reference files used, and any unresolved warnings.

## Validation Checklist

After translation, verify:

- Output is under `vkcts-wiki-pages/`, not under `external/vulkancts/wiki/`.
- Filename and relative directory path are preserved, except `README.md` → `home.md`.
- Required reference files were read and applied.
- Code tokens, inline code, and source-generated code comments are unchanged; wiki-authored `///` GLSL comments may be translated.
- Markdown links still exist.
- Markdown link paths before `#` are preserved, including `.md` suffixes.
- Source-code and mustpass/source-adjacent links were not accidentally rewritten unless explicitly requested.
- Headings are translated using the relevant reference template, and same-page or cross-page heading
  links use translated `#fragment` anchors.
- Category names, registered paths, filenames, and symbols remain unchanged.
- Registration-tree path components remain unchanged; only explanatory comments such as
  `(registration only)` may be translated.
- Redesigned hierarchy terminology follows `references/terminology.zh.md`.
- `## Shader Analysis` preserves all `shader-analyzer` code fences and code tokens exactly, while translating
  the surrounding walkthrough headings, purpose, structural-design prose, additional-info bullets, variation tables,
  and wiki-authored `///` GLSL comments.
- No obsolete version-1 heading assumptions were introduced.
- Explanatory prose is readable Mandarin Chinese with limited, intentional English technical terms.
