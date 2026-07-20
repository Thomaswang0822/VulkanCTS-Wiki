# Shader Analyzer Output Template

Use this reference when producing final `shader-analyzer` output.

The output should be markdown that can be:
- inserted directly under `## Shader Analysis` in auto mode; or
- written/appended to a Level-3 sidecar shader-analysis file in manual mode.

## Manual Mode Confirmation Step

Use this checkpoint before full reconstruction.

### Resolved Input Case

```text
<full CTS path>
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
<full CTS path>
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `<choice>` | <why this selected parameter matters here> |
| `<combined choice>` | <why the combination matters for shader structure, resources, execution, or validation> |

#### Purpose

<One or two concise sentences describing the property tested by this shader.>

#### Structural Design

<Use a compact table, Mermaid flowchart, mapping, decision tree, short diagram, or another compact non-plain-text form to show the shader logic before code. Avoid raw ASCII flowcharts; use Mermaid when the structure is flowchart-like or tree-like, but do not force Mermaid when a table or other format is clearer.>

#### Shader Code

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

Comment targets:
- runtime constants, stage shape, dispatch/draw shape, or specialization constants;
- resource declarations, bindings/locations, host-created or shader-local status, format/type, and size/extent rule;
- generated structs, shared objects, or address/reference forms;
- coordinate, index, lane, primitive, texel, or invocation mapping;
- synchronization, ordering, availability, visibility, and scope semantics;
- validation checks, skip conditions, fail writes, and pass counters;
- generated-code artifacts or variant-sensitive branches.

#### Additional Info

Use 0-3 high-value bullets for ordinary single-stage walkthroughs. Keep the heading, but do not force filler content.

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

Insert the complete `#### SPIR-V` subsection returned by `shader-disassembler` unchanged.
See `shader-disassembler/SKILL.md` and strictly follow the output format.

## Destination Rules

Auto mode:
- write one walkthrough into the target Level-3 wiki page under `## Shader Analysis`;
- use the caller-provided human-facing heading number or the next available `Representative Shader Walkthrough N` heading number.

Manual mode:
- write to `<level3-wiki-stem>_shader_analysis.md` next to the target Level-3 wiki page;
- append additional walkthroughs for the same Level-3 wiki page to the same sidecar file;
- use the next available `Representative Shader Walkthrough N` heading number in that sidecar file.
