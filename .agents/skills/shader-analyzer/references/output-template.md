# Shader Analyzer Output Template

The final walkthrough output is markdown that can be:
- inserted directly under `## Shader Analysis` in auto mode; or
- written/appended to a Level-3 sidecar shader-analysis file in manual mode.

## Manual Mode Confirmation Step

Use this checkpoint before full reconstruction.

### Resolved Input Case

```text
dEQP-VK.<full CTS registration path>
```

### Candidate Builder Selection

- Source file: `<relative source path>`
- Builder function: `<function name>` in `<relative source path>#L<line>`
- Supporting construction entrypoint: `<function name>` in `<relative source path>#L<line>`
- Target Level-3 wiki page: `<external/vulkancts/wiki/testfiles/<category>/<wiki-page>.md>`
- Manual sidecar output: `<external/vulkancts/wiki/testfiles/<category>/<wiki-page>_shader_analysis.md>`
- Why this builder matches:
  - <short reason>
  - <short reason>

Confirmation prompt:

1. Proceed with this builder and sidecar output.
2. Use a different source file/function: `<file/function>`.
3. Stop here.

## Final Output Template

### Representative Shader Walkthrough <N>

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.<full CTS registration path>
```

Use one complete executable registration path beginning with `dEQP-VK.`. Do not use a category-relative path, a group prefix, or
placeholder shorthand in final output.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `<choice>` | <why this selected parameter matters here> |
| `<combined choice>` | <why the combination matters for shader structure, resources, execution, or validation> |

#### Purpose

<One or two concise sentences describing the property tested by this shader.>

#### Structural Design

<Use a compact table, Mermaid flowchart, mapping, decision tree, short diagram, or another compact non-plain-text form to show the shader logic before code. Avoid raw ASCII flowcharts; use Mermaid when the structure is flowchart-like or tree-like, but do not force Mermaid when a table or other format is clearer.>

#### Shader Code

Use `glsl` fences for GLSL and `hlsl` fences for HLSL. Preserve source-generated `//` comments and apply the annotation
procedure and examples in [`workflow-notes.md`](workflow-notes.md) for added wiki-authored `///` comments.

For a single-stage walkthrough:

```<glsl-or-hlsl>
<primary shader code with preserved source-generated // comments and added /// wiki comments>
```

For a multi-shader walkthrough, use stage-specific headings and include only stages that are part of the tested property,
dataflow, validation signal, or reader mental model:

##### <Primary Stage> Shader

```<glsl-or-hlsl>
<primary shader code with preserved source-generated // comments and added /// wiki comments>
```

##### <Secondary Stage> Shader

```<glsl-or-hlsl>
<secondary shader code with preserved source-generated // comments and added /// wiki comments>
```

For a direct-SPIR-V stage, keep the stage-specific H5 in source order and state explicitly under that H5 that this case uses
direct SPIR-V and does not use GLSL or HLSL. Do not fabricate a source-language fence. Its authoritative assembly belongs under the
matching H5 in `#### SPIR-V`.

#### Additional Info

Keep the heading. Leave it empty when there is no high-value exact-case information. When non-empty, use Markdown list items; do not
use a plain paragraph or impose an artificial bullet-count cap.

For multi-shader walkthroughs, this subsection must include at least one bullet for each non-primary shader shown under
`#### Shader Code`. Each such bullet should state whether that stage varies across the page's cases or stays fixed, and why
it matters to the selected representative case.

Good content:
- <Exact source evidence for a non-obvious reconstruction branch, generator rule, or exactness claim.>
- <Host/runtime fact needed to interpret this shader, but too long or nonlocal for inline shader comments.>
- <Representative-case caveat, feature assumption, deterministic-generation note, runtime-dependent value, or readability normalization.>

Do not include:
- mustpass line proof unless it resolves ambiguity about the selected case;
- generic CTS/mustpass mechanics, source inventory, or facts that belong in the Source Reference Appendix;
- repeated parameter meanings, inline resource comments, or page-level runtime/pruning content;
- SPIR-V generation status or assembly text; those belong only in the final `#### SPIR-V` subsection.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `<dimension>` | <how this dimension changes declarations, resources, control flow, synchronization, or validation> | <source link> |

#### SPIR-V

This must be the final walkthrough subsection.

For a single SPIR-V artifact, insert the complete `#### SPIR-V` subsection returned by `shader-disassembler` unchanged. See
[`../../shader-disassembler/SKILL.md`](../../shader-disassembler/SKILL.md) and strictly preserve its output format.

For multiple source stages or any stage-qualified Shader Code layout, compose one `#### SPIR-V` subsection and organize generated
artifacts with H5 stage headings:

```markdown
#### SPIR-V

##### <Primary Stage> SPIR-V

<one complete metadata + details + llvm artifact body returned by shader-disassembler>

##### <Secondary Stage> SPIR-V

<one complete metadata + details + llvm artifact body returned by shader-disassembler>
```

Composition rules:

- Keep H5 stages in the same relative order as their matching H5s under `#### Shader Code`.
- Every SPIR-V H5 owns exactly one complete artifact: one metadata set, one collapsed `<details>` wrapper, and one non-empty `llvm` fence.
- Use a stage-qualified H5 even when only one selected stage from a multi-stage walkthrough receives SPIR-V.
- It is valid to omit SPIR-V for secondary source stages when their assembly does not materially help audit the tested property; do
  not add an unmatched artifact.
- A mixed direct-SPIR-V stage uses a matching H5 and its authoritative artifact without a fabricated GLSL/HLSL fence.
- Strip only the repeated outer `#### SPIR-V` heading when combining individual disassembler results. Do not edit their metadata,
  details summaries, or assembly.
