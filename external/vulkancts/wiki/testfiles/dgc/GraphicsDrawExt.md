## Overview

**Core question:** Do EXT generated draw actions consume the selected draw records and state, then produce the expected pixels for non-indexed and indexed graphics paths?

- [vktDGCGraphicsDrawTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1) implements the `dgc.ext.graphics.draw` test category. Its registration function creates the `token_draw` and `token_draw_indexed` test families.
- The tests exercise `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` and `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_EXT`, including simple paths without generated buffer-binding tokens and a supplemental indexed path with a host-bound index buffer.
- The matrix combines monolithic pipelines, shader objects, graphics pipeline libraries, optional tessellation or geometry stages, execution sets, explicit preprocessing, unordered sequences, and draw-parameter checks.
- Each main case renders a small image, copies it to host memory, and compares it with a reference derived from the generated commands.

## Background Knowledge

- A `VkIndirectCommandsLayoutEXT` has state tokens followed by one action token. The action token must be last. `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` consumes a `VkDrawIndirectCommand`; `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_EXT` consumes a `VkDrawIndexedIndirectCommand`.
- An execution set lets generated sequences select pipelines or shader objects. Explicit preprocessing runs `vkCmdPreprocessGeneratedCommandsEXT` before execution. `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT` permits implementation-dependent sequence order.
- With separate-state preprocessing, the test records state into a separate command buffer and passes that command buffer only as the state source to `vkCmdPreprocessGeneratedCommandsEXT`. Preprocessing and generated execution remain in the main command buffer, with a preprocess-to-execute barrier before execution.

## Registration Hierarchy

```text
dgc.ext.graphics.draw
├── token_draw
└── token_draw_indexed
```

The `indexed_draw_without_index_buffer_token` test cases are registered under `token_draw_indexed` by the same implementation file.

## Parameter Dimensions and Observed Values

The registration matrix is formed by nested loops in [`createDGCGraphicsDrawTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2071-L2157). The values below are exact registered suffixes or test-name components.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw action | `token_draw`, `token_draw_indexed`, plus `indexed_draw_without_index_buffer_token` cases | Selects non-indexed, indexed, or supplemental indexed execution. | [`TestType` and registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L212-L222), [registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2146-L2152) |
| Pipeline or shader state | `monolithic`, `shader_objects`, `gpl_fast`, `gpl_optimized`, `gpl_mix_base_fast`, `gpl_mix_base_opt` | Selects ordinary pipelines, `VkShaderEXT` objects, or graphics pipeline library construction. | [`pipelineTypeCases`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2089-L2100) |
| Extra stages | no suffix, `_with_tess`, `_with_geom` | Adds no stage, tessellation control/evaluation stages, or a geometry stage. | [`extraStageCases`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2079-L2087) |
| Execution set | no suffix, `_with_execution_set` | Uses one pipeline or per-stage shader-object selection per generated sequence. | [execution-set layout](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1032-L1038), [indices](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1249-L1267) |
| Draw-parameter check | no suffix, `_check_draw_params` | Checks `gl_DrawID`, `gl_BaseVertex`, and `gl_BaseInstance` in shader output. | [shader checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L479-L508) |
| Preprocessing | no suffix, `_preprocess_same_state_cmd_buffer`, `_preprocess_separate_state_cmd_buffer` | Chooses no explicit preprocessing, same-state preprocessing, or separate-state preprocessing. | [`preprocessCases`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2102-L2110) |
| Sequence order | no suffix, `_unordered` | Sets `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`. | [layout flags](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1025-L1030) |
| Simple and DX index forms | `_simple`, `_dx_index` | Omits generated buffer binding for `DRAW_SIMPLE`; uses `VK_INDIRECT_COMMANDS_INPUT_MODE_DXGI_INDEX_BUFFER_EXT` for `DRAW_INDEXED_DX`. | [`TestType` and input mode](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L212-L327), [test-name construction](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2132-L2137) |

## Behavior Parameters

The primary behavioral axis is the draw action test family. The other dimensions change how the action receives state or which graphics path executes it.

### `token_draw` | Non-indexed generated draw

`token_draw` ends each sequence with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT`. The regular form supplies a generated vertex-buffer binding before the action. The generated `VkDrawIndirectCommand` records vary `vertexCount`, `instanceCount`, `firstVertex`, and `firstInstance`; the simple form pre-binds one vertex buffer and omits the vertex-buffer token.

The main case creates three sequences over four triangles in a 2x2 attachment. The first sequence draws one triangle, the second uses a wider-stride buffer for two triangles, and the third starts at the final triangle and uses two instances. Push constants and shader outputs make these differences visible in the reference image.

### `token_draw_indexed` | Indexed generated draw

`token_draw_indexed` ends each sequence with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_INDEXED_EXT`. The regular indexed forms supply an index-buffer binding token. The records vary `indexCount`, `instanceCount`, `firstIndex`, `vertexOffset`, and `firstInstance`. The third index buffer uses `VK_INDEX_TYPE_UINT16`; the `_dx_index` form supplies the DXGI index-buffer input mode.

The separately registered `indexed_draw_without_index_buffer_token` cases keep the index buffer bound by the host and test the indexed action with and without a push-constant token. They use a 4x4 point render and compare a fixed color or push-constant gradient.

## Shader Analysis

The source generates GLSL strings in `DGCDrawCase::initPrograms()` rather than loading checked-in shader files. The vertex and fragment shaders encode instance and draw parameters in the color output. Execution-set cases add normal and alternative shader variants; tessellation and geometry cases pass the triangle-flip choice through their extra stage.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.graphics.draw.token_draw.monolithic_with_execution_set_check_draw_params
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `token_draw` | Uses `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DRAW_EXT` with generated vertex-buffer state. |
| `monolithic` | Binds graphics pipelines selected by the execution set. |
| `_with_execution_set` | Selects a normal or alternate pipeline for each sequence. |
| `_check_draw_params` | Checks `gl_DrawID`, `gl_BaseVertex`, and `gl_BaseInstance` in the fragment output. |

#### Purpose

This path checks whether generated non-indexed draws use both the per-sequence vertex state and the pipeline selected by the execution-set token, while the shader reports the draw built-ins for host comparison.

#### Structural Design

| Step | Generated or shader action | Observable result |
|------|----------------------------|-------------------|
| 1 | The stream selects a pipeline and vertex-buffer binding for the sequence. | The sequence reads its own vertex data and shader pair. |
| 2 | The draw action consumes a `VkDrawIndirectCommand`. | Counts and starting values choose the covered triangle. |
| 3 | The vertex shader forwards instance and draw values. | The fragment stage receives values derived from the generated record. |
| 4 | The fragment shader writes encoded values to the color attachment. | The host can compare pipeline selection and draw parameters in pixels. |

#### Shader Code

Reconstructed GLSL for the relevant generated behavior:

```glsl
#version 460
layout (location=0) in vec4 inPos;
layout (location=0) out flat int instanceIndex;
layout (location=3) out flat int drawIndex;
layout (location=4) out flat int baseVertex;
layout (location=5) out flat int baseInstance;
void main (void)
{
    gl_Position = inPos;
    instanceIndex = gl_InstanceIndex;
    drawIndex = gl_DrawID;
    baseVertex = gl_BaseVertex;
    baseInstance = gl_BaseInstance;
}
```

#### Additional Info

- The source also generates an alternate vertex shader that flips selected X coordinates and an alternate fragment shader that changes the blue channel for execution-set cases.
- Tessellation and geometry variants carry the flip choice through the extra stage before the fragment shader performs the same color check.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Execution set | Selects normal or alternate vertex and fragment shader variants. | [shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L414-L508) |
| Draw parameters | Adds `gl_DrawID`, `gl_BaseVertex`, and `gl_BaseInstance` outputs and fragment comparisons. | [draw-parameter shader checks](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L429-L506) |
| Extra stages | Adds tessellation or geometry shader stages when the corresponding suffix is selected. | [extra-stage shader generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L511-L650) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 35
; Schema: 0
               OpCapability Shader
               OpCapability DrawParameters
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos %instanceIndex %gl_InstanceIndex %drawIndex %gl_DrawID %baseVertex %gl_BaseVertex %baseInstance %gl_BaseInstance
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %instanceIndex "instanceIndex"
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpName %drawIndex "drawIndex"
               OpName %gl_DrawID "gl_DrawID"
               OpName %baseVertex "baseVertex"
               OpName %gl_BaseVertex "gl_BaseVertex"
               OpName %baseInstance "baseInstance"
               OpName %gl_BaseInstance "gl_BaseInstance"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
               OpDecorate %instanceIndex Flat
               OpDecorate %instanceIndex Location 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
               OpDecorate %drawIndex Flat
               OpDecorate %drawIndex Location 3
               OpDecorate %gl_DrawID BuiltIn DrawIndex
               OpDecorate %baseVertex Flat
               OpDecorate %baseVertex Location 4
               OpDecorate %gl_BaseVertex BuiltIn BaseVertex
               OpDecorate %baseInstance Flat
               OpDecorate %baseInstance Location 5
               OpDecorate %gl_BaseInstance BuiltIn BaseInstance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %inPos = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_int = OpTypePointer Output %int
%instanceIndex = OpVariable %_ptr_Output_int Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
  %drawIndex = OpVariable %_ptr_Output_int Output
  %gl_DrawID = OpVariable %_ptr_Input_int Input
 %baseVertex = OpVariable %_ptr_Output_int Output
%gl_BaseVertex = OpVariable %_ptr_Input_int Input
%baseInstance = OpVariable %_ptr_Output_int Output
%gl_BaseInstance = OpVariable %_ptr_Input_int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPos
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %25 = OpLoad %int %gl_InstanceIndex
               OpStore %instanceIndex %25
         %28 = OpLoad %int %gl_DrawID
               OpStore %drawIndex %28
         %31 = OpLoad %int %gl_BaseVertex
               OpStore %baseVertex %31
         %34 = OpLoad %int %gl_BaseInstance
               OpStore %baseInstance %34
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a 2x2 `VK_FORMAT_R8G8B8A8_UNORM` color image and a transfer destination, then generates triangle vertices and the per-sequence vertex or index buffers.
- The host creates a `VkIndirectCommandsLayoutEXT`. Depending on the case, its stream contains an execution-set token, push-constant token, vertex-buffer or index-buffer token, and one final draw action token. The push-constant and buffer-binding tokens can appear in either supported order around the binding token.
- Monolithic cases bind a graphics pipeline. Shader-object cases bind `VkShaderEXT` objects. GPL cases construct pipeline-library variants and use an execution set.
- Tessellation and geometry cases add the required shader stages. The source checks `DEVICE_CORE_FEATURE_TESSELLATION_SHADER` or `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`; draw-parameter cases require `VK_KHR_shader_draw_parameters`.
- Explicit-preprocess cases call `vkCmdPreprocessGeneratedCommandsEXT` and pass the preprocess buffer to generated execution. In separate-state cases, the main command buffer preprocesses using state captured in the separate command buffer; that state command buffer is not submitted for execution.
- The render pass clears the attachment. The device processes three sequences, runs the selected draw action, and writes encoded values to the color attachment. The host copies the image to a buffer after submission completes.
- The host builds the expected four pixels. Execution-set cases account for the selected fragment shader and horizontal triangle flip. The host calls `tcu::floatThresholdCompare` with a `0.005` threshold and fails the case when the result differs.
- The supplemental indexed path binds a vertex buffer, index buffer, and ordinary pipeline before executing the generated indexed action. It checks either a fixed blue color or a blue gradient and reports `Unexpected color in result buffer; check log for details` on mismatch.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `token_draw` | The implementation may consume the wrong `VkDrawIndirectCommand` fields, apply the wrong generated vertex-buffer binding, select the wrong graphics state, or produce incorrect rasterization or color-buffer data. |
| `token_draw_indexed` | The implementation may consume the wrong `VkDrawIndexedIndirectCommand` fields, apply the wrong index-buffer address, size, type, or vertex offset, mishandle the Vulkan or DXGI index mode, or produce incorrect rasterization or color-buffer data. |

### Cause Analysis

#### Non-indexed draw action and generated vertex state

**Possible failure symptoms:** The four-pixel result has the wrong covered pixel, color channel, instance value, or alpha draw-parameter status. The comparison reports `Unexpected results in color buffer; check log for details`.

**Possible implementation causes:** The implementation may read a draw record at the wrong stream offset, ignore a `VkDrawIndirectCommand` field, or fail to apply a generated vertex-buffer address, size, or stride. It may also bind or execute the wrong pipeline or shader-object state.

#### Indexed draw action and generated index state

**Possible failure symptoms:** The indexed result has the wrong triangle location, index-selected vertex, color, or draw-parameter status. The comparison fails against the reference image or buffer.

**Possible implementation causes:** The implementation may mishandle `firstIndex`, `vertexOffset`, `indexCount`, or `firstInstance`, use the wrong index type or device address, or interpret `VK_INDIRECT_COMMANDS_INPUT_MODE_DXGI_INDEX_BUFFER_EXT` incorrectly. Host-side generated stream construction or image checking also needs investigation when the observed result does not isolate the device behavior.

#### Pipeline selection, preprocessing, or sequence ordering

**Possible failure symptoms:** A case with execution sets uses the normal shader where the reference expects the alternative shader, fails to flip selected triangles, or produces inconsistent output in an unordered case. An explicit-preprocess case fails before or during generated execution.

**Possible implementation causes:** The implementation may use the wrong execution-set index, fail to preserve per-stage shader-object selection, mishandle explicit-preprocess state, or process the generated stream with an invalid synchronization relationship. The observed symptom alone does not identify whether the cause is in the driver, compiler, hardware, or host setup.

## Case Pruning

### Requirement-based pruning

- Cases with tessellation require `DEVICE_CORE_FEATURE_TESSELLATION_SHADER`.
- Cases with geometry require `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`.
- `_check_draw_params` cases require `VK_KHR_shader_draw_parameters`.
- GPL cases require `VK_EXT_graphics_pipeline_library` and the source asserts that an execution set is present.
- Shader-object cases require `VK_EXT_shader_object`. An execution-set shader-object case also needs a nonzero `maxIndirectShaderObjectCount`.
- The common DGC support check gates the selected graphics stages and indexed input mode. Unsupported cases are skipped or reported as unsupported rather than treated as functional failures.

### Design-based pruning

- The registration loop skips GPL cases without `_with_execution_set` because this implementation only prepares GPL cases for execution-set use.
- The test does not create separate walkthroughs for every pipeline, shader-stage, preprocess, ordering, or draw-parameter combination. The source uses the same generated behavior with suffix-controlled state, so those combinations remain matrix dimensions.
- Simple and supplemental indexed cases omit generated buffer-binding tokens by design. They check the action token against host-bound state rather than duplicate the regular binding-token path.

## Key Takeaways

- `token_draw` and `token_draw_indexed` test the two EXT generated graphics draw action families. Their records expose the fields that affect non-indexed and indexed execution.
- Execution sets, shader objects, GPL construction, extra stages, preprocessing, unordered sequences, and draw-parameter checks vary the surrounding state without changing the final rendered-output contract.
- The test validates the complete path through pixels copied back to the host. A failure means that the action, its state, its shaders, its synchronization, or the host-side result path needs investigation.

## Source Reference Appendix

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters and feature gates | [`DrawTestParams` and `DGCDrawCase::checkSupport`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L212-L412) | Defines draw type, extra stages, pipeline type, preprocessing, draw-parameter checks, execution sets, and support requirements. |
| Generated shaders | [`DGCDrawCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L414-L652) | Generates vertex, fragment, tessellation, and geometry variants and encodes observed values in color. |
| Vertex and index data | [`makeVertexBuffers` and `makeIndexBuffers`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L728-L956) | Creates per-sequence buffer layouts, index types, and vertex offsets. |
| Main draw setup and DGC stream | [`DGCDrawInstance::iterate` layout and command data](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L959-L1290) | Builds the render target, token layout, draw records, bindings, and execution-set indices. |
| Execution and result checking | [`DGCDrawInstance::iterate` execution and comparison](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1302-L1827) | Records state, preprocessing, generated execution, copyback, reference image, and pass/fail comparison. |
| Supplemental indexed path | [`indexedDrawWithoutIndexTokenRun`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1860-L2067) | Covers direct index-buffer binding and the optional push-constant token. |
| Registration | [`createDGCGraphicsDrawTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2071-L2157) | Registers the two draw action test families and the full generated matrix. |
| EXT command-layout rules | [device-generated command layout](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#indirectmdslayout) | Defines action-token placement, explicit preprocessing, and unordered sequence semantics. |
