---
name: shader-analyzer
description: Reconstructs and analyzes one exact Vulkan CTS generated GLSL or HLSL shader case from source, annotates shader-visible resources and test logic, and emits a wiki-ready Representative Shader Walkthrough. This skill should be used for direct requests for concrete shader analysis from a CTS path or by wiki-writing workflows that need source-grounded shader walkthrough material.
---

# Shader Analyzer

Reconstruct and analyze one concrete generated GLSL or HLSL shader case from Vulkan CTS source by walking the actual shader-generator logic.

Support two usage modes:
- manual mode for direct human requests, with a required confirmation stop after resolving the candidate builder function;
- auto mode for upstream skill callers, with the exact file/function entrypoint and target wiki page supplied.

## When To Use This Skill

Use this skill when the task requires any of the following:
- turn one exact CTS path into reconstructed and annotated GLSL or HLSL;
- map a CTS path to the correct shader-generation function before deep analysis;
- produce a wiki-ready `Representative Shader Walkthrough N` subsection;
- annotate important shader variables, resource declarations, code phases, synchronization, and validation logic;
- place the generated walkthrough in the target Level-3 wiki page or sidecar analysis file;
- invoke `shader-disassembler` to generate the mandatory final `#### SPIR-V` subsection from the reconstructed GLSL or HLSL.

## Required Inputs

Require:
- one exact CTS case;
- one implementation entrypoint;
- one Level-3 wiki page target or enough source mapping to resolve it.

Interpret that contract by mode and phase.

### Manual mode

Manual mode is a required two-phase workflow. Keep the phases separate.

#### Manual Phase 1: Resolve Builder Checkpoint

Use this phase when the caller provides an exact CTS path without an explicitly confirmed source file and shader-generation function.

Require:
- an exact CTS path, such as a full `dEQP-VK...` case name or an exact path below the category root;
- optionally a source-area hint when the user already knows the likely implementation file.

Output only the confirmation checkpoint:
- resolved case;
- candidate shader-generation source file;
- candidate shader-generation function;
- supporting case-construction source file/function when different;
- target Level-3 wiki page when resolvable;
- manual sidecar path when the target page is resolvable;
- short reason for the mapping;
- confirmation prompt with 2-4 suggested answers.

Hard stop after Phase 1.

#### Manual Phase 2: Reconstruct After Confirmation

Use this phase after receiving explicit positive confirmation of the source file and shader-generation function.

Require:
- exact CTS path;
- confirmed shader-generation source file;
- confirmed shader-generation function;
- target Level-3 wiki page, or enough source mapping to resolve it.

Write the generated walkthrough to the sidecar file next to the Level-3 wiki page:

```text
<level3-wiki-stem>_shader_analysis.md
```

Append later manual analyses for the same Level-3 wiki page to the same sidecar file. Number walkthrough headings sequentially from existing sidecar content.

### Auto mode

Auto mode is for upstream skill callers that already resolved and confirmed the entrypoint and target page.

Require the caller to provide:
- the exact CTS path;
- the exact source file;
- the exact builder function;
- the target Level-3 wiki page;
- the target walkthrough heading number, or instruction to use the next available heading number under `## Shader Analysis`.

Insert one generated walkthrough directly under `## Shader Analysis` in the target Level-3 wiki page, at the requested heading number/location.

## Output Contract

Apply the exact output shapes, heading structure, section-level content rules, and formatting requirements in the mandatory
[`references/output-template.md`](references/output-template.md). Do not reproduce or improvise a parallel output contract here.

Workflow-level selection rules for multi-shader walkthroughs:
- Default to the stage whose logic is central to the selected CTS case as the one primary shader.
- Select a secondary shader only when it is part of the tested property, dataflow, validation signal, or reader mental model; do
  not select boilerplate stages merely for completeness.
- Keep the primary shader first unless producer-before-consumer order is clearer for the tested dataflow.
- Generate SPIR-V for the primary shader by default. Select secondary stages for SPIR-V only when their assembly materially aids
  audit of the tested property.

The final `#### SPIR-V` subsection is mandatory, must remain last, and must be produced by `shader-disassembler` from the
reconstructed GLSL or HLSL. Its ownership and safety rules are defined under "Generate SPIR-V assembly" below.

## Manual Mode Confirmation Checkpoint

Before full reconstruction in manual mode:
1. run Manual Phase 1 when only the CTS case is available;
2. parse the exact CTS path;
3. resolve the likely source file and candidate builder function;
4. resolve the target Level-3 wiki page and sidecar path when possible;
5. present the resolved case, source file, builder function, target page, sidecar path, and short reason for the choice;
6. stop and wait for user confirmation;
7. run Manual Phase 2 after explicit positive confirmation.

When case construction and shader text generation use different files or functions, include both in the checkpoint. Mark the shader-generation function as the primary reconstruction entrypoint.

### Confirmation Mechanism

Use the host environment's interactive `ask_followup_question` tool when available, with 2-4 clickable suggested answers.

If the interactive tool is not exposed in the current session, return the checkpoint and confirmation prompt text to the parent orchestrator or user.

## Reconstruction Workflow

Follow this workflow in order.

### 1. Normalize the input case

Parse the exact CTS path into a concrete case object.

Tasks:
- split the registered path into dimensions;
- preserve exact registered identifiers;
- map each dimension to its source-controlled meaning.

When a checked rewritten wiki page already contains a trustworthy parameter interpretation table, use it as a convenience aid. Treat source code and mustpass evidence as authoritative.

### 2. Resolve the owning builder path

Find the exact implementation path that owns shader generation for the case.

Tasks:
- identify the implementation file;
- identify the candidate shader-generation function;
- distinguish separate builders when one source file has multiple shader-generation paths;
- identify the corresponding Level-3 wiki page under `external/vulkancts/wiki/testfiles/`.

Examples include files with a regular builder and a separate transitive builder.

### 3. Confirm the builder path in manual mode

In manual mode:
- show the candidate source file;
- show the candidate builder function;
- show the target Level-3 wiki page and sidecar path;
- give a short explanation of why the case maps there;
- wait for confirmation.

### 4. Walk the generator branches deterministically

Reconstruct by tracing actual source branches.

Trace branches that affect:
- shader header and extensions;
- specialization constants or fixed compile-time constants;
- data type selection;
- resource declaration forms;
- descriptor, location, push-constant, or shader-local transport;
- image formats, scalar/vector types, and storage classes;
- size or extent rules;
- coordinate calculation and addressing;
- synchronization form;
- stage-specific structure;
- validation and fail-write logic.

Assemble the shader from branch outcomes grounded in the implementation.

### 5. Expand non-local helper behavior

Before finalizing reconstructed shader source, list every non-local helper, utility wrapper, or generated-code printer that can
change emitted shader text or semantics. Use the already-loaded
[`references/shader-utility-index.md`](references/shader-utility-index.md) for canonical lookup and navigation content.

For each helper, inspect its source definition or explicitly establish that it is irrelevant to emitted GLSL or HLSL. Never infer
behavior from a call-site name or treat the index as factual evidence replacing source inspection.

### 6. Build the resource annotation facts

Inspect host/runtime setup together with shader declarations.

For important resources and shader-visible objects, derive:
- role in the selected test;
- shader-side declaration form;
- host-side resource kind or shader-local status;
- descriptor binding, location, push-constant transport, or local declaration site;
- storage class;
- image format or scalar/vector type;
- exact size or extent rule when derivable;
- read/write direction when central to the test.

Use exact static facts when source proves them. Use a size or extent rule when the exact value is runtime-dependent.

### 7. Annotate reconstructed GLSL or HLSL

Use two passes:
1. Reconstruct faithful GLSL or HLSL while preserving every source-generated `//` comment.
2. After the full shader or stage set is known, add concise wiki-authored `///` comments.

Put declaration facts next to the declarations they explain and block-level comments before semantic phases. Declarations before
`main()` must explain enough shader-visible context for a reader without prior knowledge of the specific stage, including relevant
inputs, outputs, descriptor resources, execution layouts, built-in blocks, and stage-to-stage transport. For example, annotate a
geometry shader's `layout(...) in` and `layout(..., max_vertices = ...) out` declarations when primitive shape, invocation count,
or emitted-vertex budget participates in the tested behavior.

For annotation examples and review cues, see [`references/workflow-notes.md`](references/workflow-notes.md).

### 8. Compose the walkthrough

Apply the already-loaded [`references/output-template.md`](references/output-template.md) as the final reader-facing order, not as
the drafting order.

Draft in this order:
1. keep the representative path as the anchor input;
2. collect exact source branch facts;
3. choose the primary shader stage and decide whether secondary shader blocks are necessary;
4. reconstruct faithful GLSL or HLSL for the primary shader and any required secondary shaders without wiki comments;
5. derive resource/interface and semantic facts across all shown stages;
6. add compact `///` comments to the reconstructed GLSL or HLSL;
7. choose and draft `Structural Design` using the smallest compact form that exposes what the reader must understand before code;
8. draft `Purpose` in one or two concise sentences;
9. refine `Parameter Values Chosen` into the final representative path and parameter table;
10. draft `Parameter Variation Summary` from nearby variant effects;
11. draft `Additional Info` as the final overflow/filter section with required bullets for any non-primary shaders plus 0-3 other high-value exact-case facts;
12. assemble the non-SPIR-V walkthrough material in template order;
13. invoke `shader-disassembler` with the primary reconstructed GLSL or HLSL, source language, shader stage, target SPIR-V environment, and output destination; invoke it for secondary stages only when their SPIR-V is explicitly justified;
14. append the resulting `#### SPIR-V` subsection as the final subsection of `Representative Shader Walkthrough N`.

Structural Design rule:
- choose the format after reconstructing and annotating the shader;
- use a compact table, flow, mapping, decision tree, or short diagram according to what the reader must understand before code;
- when the structure is flowchart-like, a decision tree, or another visual control-flow sketch, use Mermaid rather than raw ASCII text;
- when using a Mermaid `flowchart`, always use top-down direction with `flowchart TD` for consistent, readable wiki rendering;
- do not use horizontal Mermaid directions such as `flowchart LR` in shader walkthroughs, even for short flows;
- do not default to a phase table when another concise form better exposes the shader's core mental model;
- do not force Mermaid when a table, mapping, or other structured non-text format explains the shader better.

The exact `Additional Info` inclusion, exclusion, and multi-shader content contract is owned by the mandatory output template.
Apply it without adding a parallel filter here.

### 9. Place the walkthrough

Apply the mode-specific destination rule:
- auto mode: insert the walkthrough into the target Level-3 wiki page under `## Shader Analysis`;
- manual mode: write or append the walkthrough in the sidecar file next to the target Level-3 wiki page.

For multiple walkthroughs in the same destination, use sequential human-facing heading numbers starting at 1.

### 10. Generate SPIR-V assembly

Treat SPIR-V assembly as mandatory final walkthrough output.

`shader-disassembler` owns the complete `#### SPIR-V` subsection and its exact format. Delegate generation after reconstructed GLSL
or HLSL is complete. Provide:
- the primary reconstructed GLSL or HLSL from `#### Shader Code`, or a specific stage subsection under it when multiple shader blocks are present;
- the source language, `GLSL` or `HLSL`, derived from the CTS source collection and selected code block;
- the shader stage derived from the exact CTS case and selected code block, such as `comp`, `vert`, `geom`, or `frag`;
- the target SPIR-V environment derived from CTS shader build options, such as `spirv1.0` or `spirv1.3`;
- the target `#### SPIR-V` subsection destination.

For multi-shader walkthroughs, generate SPIR-V for the primary shader by default. Generate additional collapsed SPIR-V blocks for secondary shaders only when their generated assembly materially helps audit the tested property; otherwise describe the secondary stages in `#### Shader Code`, `#### Structural Design`, and required `#### Additional Info` bullets.

Choose the target from the shader insertion path:

1. Explicit `vk::ShaderBuildOptions` -> use its `targetVersion`.
2. No explicit build options -> use the `vk::SourceCollections` default from `vk::getBaselineSpirvVersion()` (currently SPIR-V 1.0).

Do not use the Vulkan runtime version or `vk::getMaxSpirvVersionForVulkan()`. Pass `spirv1.X`, never `vulkan1.X`.

Insert the complete `shader-disassembler` result unchanged. Do not reformat its fields, add generation prose, or edit its assembly.

If `shader-disassembler` fails, do not treat the failure as only a final-output status. Return to shader reconstruction and perform
the detailed reconstruction-failure audit in the already-loaded
[`references/workflow-notes.md`](references/workflow-notes.md) before accepting the failure as final.

## Output Formatting Rules

Apply the exact, canonical formatting contract in the mandatory
[`references/output-template.md`](references/output-template.md). Preserve exact CTS identifiers and do not introduce local
formatting variants in this workflow file.

## Suggested Tool Strategy

Prefer this tool order inside the VK-GL-CTS repository:
1. inspect mustpass or exact test path evidence;
2. inspect the owning source file and builder function;
3. identify the corresponding Level-3 wiki page;
4. inspect nearby runtime/resource setup code;
5. reconstruct GLSL or HLSL;
6. annotate resource declarations and semantic blocks;
7. compose the non-SPIR-V walkthrough sections;
8. call `shader-disassembler` for mandatory `#### SPIR-V` output;
9. write or insert the complete walkthrough.

## Scope Boundary

Keep the scope to one exact case at a time. When multiple representative shaders are needed, run this skill separately for each selected case.
