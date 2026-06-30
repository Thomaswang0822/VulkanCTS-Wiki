# Shader Analyzer Workflow Notes

Use this reference to keep reconstruction, annotation, and placement stable.

## Core Principles

- Reconstruct one exact case at a time.
- Prefer source-controlled branch tracing over prose extrapolation.
- Keep registered identifiers exact.
- Treat source code and mustpass evidence as authoritative.
- Emit one complete `Representative Shader Walkthrough N` per invocation.
- Treat `#### SPIR-V` as mandatory final walkthrough output produced by `shader-disassembler`.
- Inspect non-local helper definitions before relying on their shader-emission behavior.
- Default to one primary shader per walkthrough, but include secondary shader code blocks when producer/consumer stages are part of the tested property or necessary to understand the validation signal.

## Manual Mode

- Accept one exact CTS path.
- Resolve the likely implementation file and builder function.
- Resolve the corresponding Level-3 wiki page.
- Present the candidate builder selection and sidecar path.
- Wait for confirmation before deep reconstruction.
- Write or append to `<level3-wiki-stem>_shader_analysis.md` next to the Level-3 wiki page.

## Auto Mode

- Require the caller to supply the exact file, builder function, target Level-3 wiki page, and insertion heading number or next-heading instruction.
- Insert one walkthrough under `## Shader Analysis` in the target page.
- Use the same heading depth as the final wiki page.

## Walkthrough Numbering

- Use `### Representative Shader Walkthrough 1` for the first walkthrough.
- Use `### Representative Shader Walkthrough 2` and `### Representative Shader Walkthrough 3` for additional walkthroughs.
- Determine the next human-facing heading number from existing headings in the target destination.
- Keep subsection headings at `####` depth.

## What To Trace In Source

Trace branches that affect:
- preamble and shader extensions;
- specialization constants and local-size settings;
- data-type declarations and casts;
- resource declarations and transport;
- descriptor bindings, locations, push constants, and shader-local objects;
- image formats, scalar/vector types, and storage classes;
- size and extent rules;
- coordinate, lane, primitive, texel, or index mapping;
- synchronization primitives and semantics;
- stage-specific control flow;
- pass/fail checks.

## Helper Expansion Checkpoint

Before finalizing reconstructed GLSL or HLSL, identify non-local helper functions, utility wrappers, and code-printer functions that affect shader text or shader-semantic facts. Inspect their definitions rather than inferring behavior from names or call-site context.

Pay special attention to helpers that affect:
- type spelling and precision qualifiers;
- declaration printers for structs, arrays, resources, and interfaces;
- extension and feature gating;
- literal generation, casts, comparison helpers, and validation expressions;
- generated source comments or formatting artifacts.

Use `shader-utility-index.md` only as a lookup aid for likely helper locations. Source code remains the authority, and the index must not replace reading the helper implementation.

## Resource Annotation Facts

For each important resource or shader-visible object, derive:
- test role;
- shader-side declaration form;
- host-created resource kind or shader-local status;
- binding, location, push-constant transport, or local declaration site;
- storage class;
- image format or scalar/vector type;
- exact size or size rule;
- read/write direction when central to the test.

Place compact facts as `///` comments near declarations.

Examples:

```glsl
/// Binding 0 is an r32ui storage image whose extent matches the generated invocation grid; each texel stores
/// one payload value that must become visible through the selected synchronization chain.
layout(set=0, binding=0, r32ui) uniform nonprivate uimage2D payload;
```

```glsl
/// Binding 0 is the only host-created GPU resource in this case: a std140 storage buffer containing one uint
/// pass counter. The shader increments it only if every generated shared-memory field check succeeds.
layout(std140, binding = 0) buffer block { highp uint passed; };
```

```glsl
/// These generated shared objects live in workgroup shared memory. Their nested structs, arrays, and 16-bit
/// fields are the layout/access data being tested.
shared sG s1;
shared sN s2;
shared sAL s3;
```

## GLSL/HLSL Annotation Workflow

1. Reconstruct faithful GLSL or HLSL from source-controlled branches.
2. Decide whether the walkthrough is single-stage or multi-shader:
   - use one primary shader when other stages are boilerplate;
   - add secondary shader blocks when another stage creates, transforms, consumes, or validates the tested value.
3. Preserve generated `//` comments.
4. Add custom `///` comments after seeing the full shader or stage set.
5. Comment semantic blocks and key declarations.
6. Keep comments concise and source-grounded.

Comment categories:
- execution shape and runtime knobs;
- shader-visible interface roles;
- resource type, binding/location, format/type, and size/extent rules;
- data layout or addressing model;
- control-flow phases;
- synchronization and ordering semantics;
- validation and failure recording;
- generated-code artifact or deliberate oddity;
- variant-sensitive block.

## Additional Info Content

Use `Additional Info` for 0-3 high-value bullets that help interpret the exact reconstructed shader but do not belong naturally in
`Parameter Values Chosen`, `Structural Design`, compact GLSL comments, `Parameter Variation Summary`, or page-level runtime/pruning
sections.

Good candidates:
- exact source evidence for a non-obvious reconstruction branch or generator rule;
- host/runtime facts needed to interpret this shader but too long or nonlocal for inline comments;
- feature/support assumptions specific to this selected shader;
- caveats about representative exactness, deterministic random generation, runtime-dependent values, or readability normalizations;
- short clarifications that prevent a likely misunderstanding of the shown shader;
- for multi-shader walkthroughs, one required bullet per non-primary shader explaining whether that stage varies across the page's cases or stays fixed, and why it matters to the representative case.

Do not include:
- mustpass line proof unless it resolves ambiguity about the selected case;
- generic CTS or mustpass mechanics covered by framework/reader-guide pages;
- repeated parameter meanings without new audit value;
- resource facts already clear from inline comments or page resource tables, except required non-primary shader bullets in multi-shader walkthroughs;
- host execution details better handled by `Runtime Execution and Result Checking`;
- source inventory links that do not explain the reconstructed shader;
- SPIR-V generation details, which belong only in the final `#### SPIR-V` subsection generated by `shader-disassembler`.

## SPIR-V Target Environment

Resolve the SPIR-V target environment from CTS shader build options, not from Vulkan runtime API version.

Rules:
- if the shader is inserted with an explicit `vk::ShaderBuildOptions`, use its `targetVersion`;
- if the shader has no explicit `vk::ShaderBuildOptions`, follow the `vk::SourceCollections` default, which is constructed from `vk::getBaselineSpirvVersion()` and currently defaults GLSL/HLSL shaders to SPIR-V 1.0;
- do not use `vk::getMaxSpirvVersionForVulkan()` to choose the emitted SPIR-V target; it describes the maximum SPIR-V version supported by a Vulkan version without extension;
- pass `shader-disassembler` a SPIR-V target environment such as `spirv1.0` or `spirv1.3`, not a Vulkan target environment such as `vulkan1.1`.

`shader-disassembler` compiles and validates with the same SPIR-V target version. It uses `spirv1.X` spelling for `glslangValidator` and the matching `spv1.X` spelling for `spirv-val`. The `#### SPIR-V` output uses `Target SPIRV version` as the single version metadata field; do not add a duplicate `SPIR-V version` field from the `spirv-dis` header.

If SPIR-V generation fails, audit reconstructed GLSL or HLSL against generator helpers before accepting the failure as final. Common suspects are non-local helper behavior, declaration printing, source-language flags, entry point, extension emission, type aliases, precision qualifiers, feature gates, casts, and validation helper generation.

## Suggested VK-GL-CTS Inputs

Useful evidence often lives in:
- mustpass entries under `external/vulkancts/mustpass/`
- implementation sources under `external/vulkancts/modules/vulkan/`
- rewritten wiki pages under `external/vulkancts/wiki/testfiles/` when a checked explanation already exists
- temporary planning docs under `external/vulkancts/wiki/internal_doc/` for internal templates only
