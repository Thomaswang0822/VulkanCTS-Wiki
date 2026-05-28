---
name: translate-doc
description: Translate VK-GL-CTS wiki markdown from canonical English local wiki pages into Mandarin Chinese GitLab Wiki publish-target pages while preserving formatting, links, code, and Vulkan/CTS terminology
adapted from: <https://mcpmarket.com/en/tools/skills/markdown-doc-translator>
---

# Translate Doc

Translate VK-GL-CTS wiki documentation from the canonical English local wiki under
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
- Vulkan/CTS identifiers and domain terms that are normally read in English.

The English local wiki remains canonical and read-only during translation. Translated output is a
generated publish artifact in `vkcts-wiki-pages/`.

## Trigger

```text
/translate-doc <target>
/translate-doc <target> --to zh
```

`<target>` can be:

- A single canonical wiki file, such as `external/vulkancts/wiki/categories/api.md`.
- A canonical wiki directory, such as `external/vulkancts/wiki/testfiles/api/`.
- A category name, such as `api`, meaning:
  - `external/vulkancts/wiki/categories/api.md`
  - all `external/vulkancts/wiki/testfiles/api/*.md`

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
one landing-page exception.

| Canonical English source | Chinese publish target |
|--------------------------|------------------------|
| `external/vulkancts/wiki/README.md` | `vkcts-wiki-pages/home.md` |
| `external/vulkancts/wiki/Vulkan_CTS_Framework_and_Mechanism.md` | `vkcts-wiki-pages/Vulkan_CTS_Framework_and_Mechanism.md` |
| `external/vulkancts/wiki/Objectives.md` | `vkcts-wiki-pages/Objectives.md` |
| `external/vulkancts/wiki/categories/api.md` | `vkcts-wiki-pages/categories/api.md` |
| `external/vulkancts/wiki/testfiles/api/vktApiBufferTests.md` | `vkcts-wiki-pages/testfiles/api/vktApiBufferTests.md` |

Rules:

- Do **not** add `.zh.md` suffixes.
- Do **not** translate filenames.
- Do **not** translate directory names.
- Do **not** place translated files next to the English canonical files.
- Create missing output directories under `vkcts-wiki-pages/` as needed.
- Exclude `external/vulkancts/wiki/internal_doc/` from translation and publishing.

## Markdown Link Rules

Translation should preserve markdown link targets, including relative paths and `.md` suffixes. The
translator is **not** responsible for converting GitLab Wiki page links such as
`categories/info.md` to `categories/info`; that belongs to the future `wiki-publisher` link
transformation script.

The only markdown-link change this skill should make is for `#fragment` section-heading references
whose target heading is translated.

Rules:

- Preserve everything before `#` exactly, including relative paths and `.md` extensions.
- Translate only the section-heading fragment after `#` when the referenced heading is translated.
- This applies to same-page links and cross-page links.
- Do not add compatibility HTML anchors such as `<a id="category-index"></a>` unless there is a
  specific verified need.

Examples:

| English source link | Chinese translated link |
|---------------------|-------------------------|
| `[Category Index](#category-index)` | `[类别索引](#类别索引)` |
| `[Category Naming Notes](#category-naming-notes)` | `[类别命名说明](#类别命名说明)` |
| `[details](categories/api.md#test-families)` | `[详细信息](categories/api.md#测试族)` |
| `[details](../categories/api.md#support-requirements)` | `[详细信息](../categories/api.md#支持条件)` |

Important: source-code links, mustpass links, source-adjacent documentation links, and inter-wiki
`.md` suffix removal have not been fully validated or implemented in this skill. Preserve those link
target paths for the later `wiki-publisher` link-transformation step unless the user explicitly asks
otherwise.

## Content That Must Remain Unchanged

Do not translate these elements:

1. **Code blocks** fenced by triple backticks — preserve exactly.
2. **Inline code** inside backticks — preserve exactly.
3. **File paths and URL targets** — preserve exactly.
4. **Markdown link target paths before `#`** — preserve exactly; only translate `#fragment` heading
   references when their target headings are translated.
5. **Function names, class names, enum names, struct names, variables, constants, macros, CLI flags**.
6. **Registered test paths and test case names**, such as `dEQP-VK.api.buffer.create.destroy`.
7. **Source filenames and wiki filenames**, such as `vktApiBufferTests.cpp` and `vktApiBufferTests.md`.
8. **Directory names**, such as `categories/`, `testfiles/`, `modules/vulkan/`, `mustpass/`.
9. **YAML frontmatter** — preserve exactly.
10. **Markdown table structure** — translate cell prose while preserving `|` and separator rows.
11. **ASCII diagrams and directory trees** — preserve exactly unless the user explicitly asks to
    translate comments in them.
12. **HTML comments or machine markers** — preserve exactly.

## VK-GL-CTS Terminology Policy

Translate naturally into Mandarin Chinese, but avoid awkward translation of terms that Vulkan/CTS
readers usually understand in English.

### Usually Keep in English

Keep these terms in English in most contexts:

- Vulkan, Vulkan CTS, Vulkan SC, CTS, dEQP, API, SPIR-V, GLSL, HLSL, YCbCr, DRM.
- GPU, CPU, shader, Vertex Shader, Fragment Shader, Compute Shader, Mesh Shader, Ray Tracing,
  Ray Query.
- device, queue, pipeline, descriptor, descriptor set, render pass, framebuffer, image, buffer,
  sampler, command buffer, query pool, subpass.
- mustpass, waiver, conformance, extension, feature, limit, format, layout, tiling.
- test, test case, test group, test family when used as CTS concepts; translate surrounding prose
  instead of forcing every occurrence into Chinese.
- Level-2 and Level-3 when referring to this wiki's documentation levels.
- testfile when referring to this wiki's Level-3 page type.
- category only when it is part of a protected identifier, path, filename, registered name, table key,
  or when the sentence explicitly discusses the fixed English documentation term itself. In ordinary
  prose, translate category-related phrases to Chinese.

### Usually Translate to Chinese

Translate ordinary explanatory words and non-identifier phrases:

| English phrase | Preferred Chinese |
|----------------|-------------------|
| source evidence | 源码证据 |
| implementation evidence | 实现证据 |
| category | 类别 |
| test category | 测试类别 |
| category page | 类别页面 |
| category summary | 类别概览 |
| category index | 类别索引 |
| category naming notes | 类别命名说明 |
| per-source-file notes | 按源文件整理的说明 |
| source-file-level behavior | 源文件级别的行为 |
| registration hierarchy | 注册层级 |
| parameter dimensions | 参数维度 |
| support requirements | 支持条件 |
| verification methods | 验证方法 |
| top-level category | 顶层类别 |
| directory hierarchy | 目录层级 |
| entry point | 入口点 |
| overview | 概览 |
| purpose | 目的 |
| structure | 结构 |
| generation | 生成 |
| build and execution | 构建与执行 |
| result reporting | 结果报告 |
| factory declaration | 工厂函数声明 |

### Mixed-Term Style

Use natural Chinese sentence structure around preserved English terms.

Good:

```markdown
测试会验证 Vulkan state 是否被正确更新。
```

Bad:

```markdown
Tests verify that Vulkan state is correctly updated。
```

Good:

```markdown
类别页面和 testfile 页面会基于已检查过的源码证据，总结注册层级、测试族、参数维度、支持条件以及验证方法。
```

Bad:

```markdown
Category pages 和 testfile pages 使用 source-code evidence 来 summarize registration hierarchy。
```

## Heading Translation Rules

- Translate Markdown headings to Mandarin Chinese for readability.
- Preserve heading levels and numbering.
- If a heading exactly matches an entry in the canonical heading translation map below, use the mapped
  Chinese heading exactly.
- Same-page links should target the translated heading anchor directly.
- Cross-page links with a `#fragment` should preserve everything before `#` and translate only the
  heading fragment when it points to a translated heading.
- Do not keep English headings merely to preserve old English anchors.
- Do not add compatibility HTML anchors unless the user explicitly asks.

### Canonical Heading Translation Map

Use this map for fixed headings generated by the VK-GL-CTS wiki workflow. This keeps translated wiki
pages consistent and makes heading-anchor fragments predictable.

#### Level-2 Category Page Headings

| English heading | Chinese heading |
|-----------------|-----------------|
| Overview | 概览 |
| Registration Entry Point | 注册入口点 |
| Subgroup Structure | 子组结构 |
| File Inventory | 文件清单 |
| Recurring Test Families | 反复出现的测试族 |
| Recurring Parameter Dimensions | 反复出现的参数维度 |
| Recurring Support Requirements | 反复出现的支持条件 |
| Recurring Feature Gates | 反复出现的 feature gate |
| Recurring Verification Methods | 反复出现的验证方法 |
| Level-3 Testfile Pages | Level-3 testfile 页面 |
| Notes and Uncertainties | 说明与不确定性 |
| Scope and Uncertainty | 范围与不确定性 |

#### Level-3 Testfile Page Headings

| English heading | Chinese heading |
|-----------------|-----------------|
| Overview | 概览 |
| File Role | 文件角色 |
| Source Code | 源码 |
| Related Files | 相关文件 |
| Registration Hierarchy | 注册层级 |
| Test Families | 测试族 |
| Parameter Dimensions | 参数维度 |
| Support / Feature Requirements | 支持与 feature 要求 |
| Verification Methods | 验证方法 |
| Test Principles | 测试原则 |
| Notes and Uncertainties | 说明与不确定性 |
| Notes / Uncertainties | 说明与不确定性 |

#### Shared Wiki Page Headings

| English heading | Chinese heading |
|-----------------|-----------------|
| Where to Start | 从哪里开始 |
| How the Wiki Is Organized | Wiki 的组织方式 |
| Scope and Evidence | 范围与证据 |
| Category Index | 类别索引 |
| Category Naming Notes | 类别命名说明 |

### Heading Translation Details

- Preserve heading levels, numbering, and Markdown heading syntax.
- If a heading has a numeric prefix, preserve the prefix and translate the heading text.
- If a heading begins with a protected identifier or registered child name, preserve that identifier.
  Translate only the explanatory suffix.
  - Example: `### basic_primitive — Basic primitive expansion` becomes
    `### basic_primitive — 基本图元展开`.
- If a markdown link points to a canonical heading, update only the `#fragment` to the translated
  Chinese heading anchor.
- Do not add English compatibility headings or HTML anchors unless a specific GitLab Wiki rendering
  problem has been verified.

Example:

```markdown
## Category Naming Notes
```

becomes:

```markdown
## 类别命名说明
```

and same-page links should use:

```markdown
[类别命名说明](#类别命名说明)
```

## Translation Quality Requirements

- Preserve Markdown formatting: headings, lists, tables, links, emphasis, code fences.
- Use natural Mandarin Chinese for explanatory prose.
- Avoid excessive English-Chinese mixing for ordinary explanatory terms.
- Keep domain terms in English when translating them would be less familiar to Vulkan/CTS readers.
- Translate table cell prose, list descriptions, and category explanations unless they are identifiers
  or domain terms that should remain English.
- Keep left-side category names and filenames unchanged; translate right-side explanations.
- Do not introduce new factual claims while translating.
- Do not remove source links or evidence links.
- Do not change code examples.

## Workflow

### Single File Mode

1. Read the canonical English source file under `external/vulkancts/wiki/`.
2. Determine the publish target under `vkcts-wiki-pages/` using the mapping rules.
3. Translate prose to Mandarin Chinese using the terminology policy.
4. Preserve protected content.
5. Translate `#fragment` section-heading references when their target headings are translated, while
   preserving link paths before `#` exactly.
6. Write or overwrite the publish target file.
7. Report source file, target file, and any translated heading-fragment links.

### Category Mode

1. Resolve the category to:
   - `external/vulkancts/wiki/categories/<category>.md`
   - `external/vulkancts/wiki/testfiles/<category>/*.md`
2. Translate each file to the corresponding path under `vkcts-wiki-pages/`.
3. Preserve filenames and directory layout.
4. Translate heading fragments after `#` in markdown links when their target headings are translated.
5. Report translated file count and skipped files.

### Directory Mode

1. Scan the requested canonical source directory for `.md` files.
2. Exclude `internal_doc/` and existing generated/temporary files.
3. Translate files to matching relative paths under `vkcts-wiki-pages/`.
4. Preserve directory layout and filenames.
5. Translate heading fragments after `#` in markdown links when their target headings are translated.
6. Report translated file count and skipped files.

## Validation Checklist

After translation, verify:

- Output is under `vkcts-wiki-pages/`, not under `external/vulkancts/wiki/`.
- Filename and relative directory path are preserved, except `README.md` → `home.md`.
- Code blocks and inline code are unchanged.
- Markdown links still exist.
- Markdown link paths before `#` are preserved, including `.md` suffixes.
- Source-code and mustpass/source-adjacent links were not accidentally rewritten unless explicitly requested.
- Headings are translated and same-page or cross-page heading links use translated `#fragment` anchors.
- Category names, registered paths, filenames, and symbols remain unchanged.
- Explanatory prose is readable Mandarin Chinese with limited, intentional English technical terms.
