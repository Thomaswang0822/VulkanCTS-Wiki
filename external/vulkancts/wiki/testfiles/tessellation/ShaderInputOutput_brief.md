# Understanding Brief: `tessellation.shader_input_output`

## One-Sentence Test Purpose

This test family checks whether a tessellation pipeline preserves patch shape, built-in values, stage interfaces, and cross-invocation data while the tessellation control shader changes an input patch into an output patch.

## Background Knowledge

### Input patches, output patches, and tessellation control invocations

A draw supplies input control points in patches. The pipeline's patch-control-point state sets the input patch size, while the tessellation shader's `OutputVertices` execution mode sets the output patch size. Vulkan invokes the tessellation control shader at least once per output control point. `InvocationId` identifies the output control point owned by the current invocation.

The two patch sizes describe different interfaces. In a tessellation control shader, `PatchVertices` reports the pipeline input patch size. In a tessellation evaluation shader, it reports the tessellation control output patch size. A correct implementation must not substitute one count for the other.

### Per-vertex data, per-patch data, and execution phases

Per-vertex arrays hold one element per control point. A tessellation control invocation can read any incoming control point and can write an output element. A `patch` output instead belongs to the whole patch.

Invocations for one patch execute in parallel with no defined relative order. `OpControlBarrier`, emitted for GLSL `barrier()`, divides execution into phases. Reading another invocation's output in the phase that writes it yields an undefined value. The synchronization cases place barriers between those writes and reads so that the values have a defined producer-to-consumer relationship.

### Stage interfaces and tessellation built-ins

User-defined shader inputs and outputs connect through matching `Location` decorations. Built-in variables connect shader stages to the execution environment through `BuiltIn` decorations. This family exercises both forms:

- `Position` carries the current vertex position and, as an input, receives the preceding stage's `Position` output.
- `PrimitiveId` identifies the patch in tessellation control and evaluation shaders.
- `TessLevelInner` and `TessLevelOuter` are written by the tessellation control shader, drive tessellation, and can be read by the tessellation evaluation shader.

## One Concrete Example

Use the synchronization case:

```text
dEQP-VK.tessellation.shader_input_output.barrier
```

The test creates one 32-control-point input patch and a 32-control-point output patch. All tessellation control invocations first write their own per-vertex element and initialize one shared per-patch float. After a barrier, invocation 5 writes `0.5` to the patch float. A second barrier makes that phase complete before every invocation reads the value. Later phases publish per-vertex results, read the next invocation's result, and replace the shared patch float with `31.0` from invocation 31.

The tessellation evaluation shader uses the final per-vertex values as a curve and turns an incorrect final patch value into a blue-channel difference. The host compares the rendered image against `barrier_ref.png`. A synchronization or cross-invocation visibility error therefore changes geometry, color, or both.

## End-to-End Test Flow

```text
[host] require tessellationShader support
[host] generate vertex, tessellation-control, tessellation-evaluation, and fragment shaders for one test case
[host] create the vertex buffer, RGBA8 color image, render pass, framebuffer, and graphics pipeline
[host] set the input patch size in pipeline state and the output patch size in generated tessellation shader code
[host] draw numPrimitives * inputPatchSize vertices as patches
[device] vertex shader forwards the supplied control-point data
[device] tessellation control invocations transform or communicate control-point and patch data
[device] fixed-function tessellator generates coordinates from the written tessellation levels
[device] tessellation evaluation shader converts tested values into position and/or color
[device] fragment shader writes the final color attachment
[host] copy the color image to a host-visible buffer
[host] fuzzy-compare the result with a PNG or generated all-white reference at threshold 0.002
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

Every test case generates four GLSL ES 3.10 stages. The vertex and fragment shaders usually forward one value. The tessellation control and evaluation shaders carry the tested behavior. Each case uses the default CTS shader build target, SPIR-V 1.0.

The host loads PNG references for the two patch-count cases, both `PrimitiveId` cases, all three `Position` routing cases, and `barrier`. It generates a 256 by 256 all-white reference for the `PatchVertices`, tessellation-level, and cross-invocation cases.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes, as location 0 vertex input | vertex shader reads it | no | Supplies control-point values or packed `vec4` position/color data. |
| TCS/TES stage interfaces | generated shader variables | yes, through `Location` or `BuiltIn` decorations | tessellation stages read and write them | no | Carry the values being tested. |
| Tessellation levels | generated built-in outputs | yes | TCS writes; tessellator and some TES cases read | no | Set generated tessellation and expose built-in propagation. |
| RGBA8 color attachment | yes | yes | fragment output writes it | copied to a buffer | Converts shader-visible errors into pixels. |
| Host-visible color buffer | yes | transfer destination | image copy writes it | yes | Supplies the final image to `tcu::fuzzyCompare`. |
| PNG or generated reference image | yes, host-side | no | no | host reads it | Defines the expected geometry and color. |

The pipeline uses no descriptor sets, push constants, storage buffers, or sampled images.

## What Is Checked

- `patch_vertices_5_in_10_out` and `patch_vertices_10_in_5_out` check resampling between unequal input and output patch sizes.
- `primitive_id_tcs` and `primitive_id_tes` check the patch index through a TCS patch output or directly in the TES.
- `patch_vertices_in_tcs` expects `10`; `patch_vertices_in_tes` expects `5`.
- Six tessellation-level cases expect the TES to read the TCS values `inner = {9, 8}` and `outer = {7, 6, 5, 4}`.
- Three `gl_position` cases route the same packed control-point values through user-defined variables, `Position`, or both. All must reproduce one reference triangle and its color.
- `barrier` checks several ordered phases of per-patch and per-vertex communication across 32 TCS invocations.
- Twelve `cross_invocation` cases check per-vertex versus per-patch arrays across `int`, `uint`, `float`, `vec3`, `vec4`, and `mat4x3`. Each invocation writes its ID, waits, and adds the next invocation's value; the TES requires every output to match.
- The host applies `tcu::fuzzyCompare` with threshold `0.002`. Any image mismatch fails the case with `Failure`; a match returns `OK`.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group selected by the test case leaf
>
> **Candidate values:** `patch vertex count`, `built-in and per-patch data`, `Position routing`, `multi-phase barrier`, `typed cross-invocation communication`

The executable leaves are flat under `shader_input_output`, but five source-level groups change what property is tested. Data type and per-vertex/per-patch storage refine the typed cross-invocation group; they do not replace the group as the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `patch vertex count` | Incorrect input/output patch sizing, `InvocationId` handling, per-control-point indexing, or TCS-to-TES array transport. |
| `built-in and per-patch data` | Incorrect `PrimitiveId`, `PatchVertices`, or tessellation-level values; wrong patch storage transport; or a TCS-to-TES built-in propagation error. |
| `Position routing` | Incorrect `Position` input/output interface handling at the vertex-to-TCS or TCS-to-TES boundary, or corruption of the corresponding user-defined interface. |
| `multi-phase barrier` | Incorrect TCS control-barrier execution, per-patch/per-vertex output visibility between phases, cross-invocation indexing, or final TCS-to-TES transport. |
| `typed cross-invocation communication` | Incorrect barrier-ordered reads of another TCS invocation's output, per-vertex versus patch array layout/transport, or type-dependent interface lowering. |

All groups also share graphics-pipeline setup, draw, rasterization, image copy, and fuzzy-comparison infrastructure. A broad failure across unrelated groups can point to that common path rather than one tessellation interface rule.

## Important Variations and Special Cases

- The family registers 28 leaves in both Vulkan and Vulkan SC default tessellation mustpass lists.
- Input/output patch pairs are `5 -> 10` and `10 -> 5`. Other groups use fixed pairs: `10 -> 5`, `3 -> 3`, or `32 -> 32`.
- `PrimitiveId` cases draw eight patches but test whether the fourth patch has ID 3; their PNGs encode which horizontal slice should be white.
- Integer cross-invocation varyings use `mediump` declarations, as do the floating, vector, and matrix variants. `mat4x3` consumes four locations per value and makes the patch-array location jump much larger.
- Every cross-invocation case draws eight patches. Geometry selects a horizontal slice from the first input value, while shader success selects white versus black.
- `requireFeatures(... FEATURE_TESSELLATION_SHADER)` is the only explicit runtime feature gate in this source. Pipeline creation and Vulkan limits still enforce legal patch sizes and interfaces.
- The tests do not read shader values back directly. They encode values into rendered geometry or color, then compare pixels.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shared host execution and image comparison | [runTest](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L68-L197) | Builds the pipeline, draws patches, copies the image, and defines pass/fail. |
| Unequal patch-size generator and input data | [PatchVertexCount](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L215-L333) | Defines the two resampling cases. |
| Built-in and per-patch generator | [PerPatchData](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L335-L518) | Tests `PrimitiveId`, `PatchVertices`, and tessellation levels. |
| `Position` routing generator | [GLPosition](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L520-L643) | Selects built-in or user-defined transport at each stage boundary. |
| Multi-phase synchronization generator | [Barrier](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L645-L790) | Defines the barrier-ordered per-patch and per-vertex exchange. |
| Typed communication generator | [CrossInvocation](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L792-L967) | Expands storage class and data type dimensions. |
| Registration | [createShaderInputOutputTests](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L971-L1085) | Registers all 29 executable leaves. |
| TCS/TES execution model | [Vulkan shader stages](../../../../vulkan-docs/src/chapters/shaders.adoc#L2634-L2685) | Defines patch sizes, parallel TCS invocations, barriers, and TES invocation behavior. |
| Relevant built-in semantics | [Vulkan shader interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#L3459-L3488) | Defines `InvocationId`; nearby linked ranges define `PatchVertices`, `Position`, `PrimitiveId`, and tessellation levels. |
| Default Vulkan mustpass entries | [tessellation mustpass list](../../../mustpass/main/vk-default/tessellation.txt#L388-L415) | Confirms the registered Vulkan paths. |

## Questions / Risk Points for User Audit

- The behavioral axis uses five behavior groups rather than listing 29 flat leaves. Each group corresponds to a distinct generator and failure mechanism in the source.
- The representative walkthrough should use `barrier` because it exposes the TCS execution model and the strongest synchronization contract in one shader. The walkthrough must come from `shader-analyzer`, with SPIR-V generated by `shader-disassembler`.
- Image comparison can report a failure caused by common rendering or copyback infrastructure. The final page should keep that shared cause separate from group-specific tessellation causes.
- Source, mustpass, local Vulkan specification chapters, and the generated SPIR-V agree. No unresolved semantic risk blocks the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Use the five behavioral groups as `## Behavior Parameters` subsections.
- Copy the `### Failure Cause Mapping` table unchanged.
- Keep one representative walkthrough for `dEQP-VK.tessellation.shader_input_output.barrier`, centered on the tessellation control shader.
- Distill patch-size and TCS phase rules into `Background Knowledge`; leave concrete constants and checks in later sections.
- Explain the common image-comparison path once in the runtime and failure sections.
