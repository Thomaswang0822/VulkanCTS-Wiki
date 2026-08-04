## Overview

**Core question:** When a vertex buffer is bound at different byte offsets, does Vulkan still fetch the intended `vec2` or `vec4` attribute bytes for packed, padded, and overlapping layouts under static and dynamic vertex-input state?

[`vktPipelineInputAttributeOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L1) creates the `input_attribute_offset` group for the requested pipeline-construction type; the monolithic invocation is `pipeline.monolithic.input_attribute_offset`. The test renders vertex data to a 4×4 opaque-blue image, then checks every pixel with zero tolerance.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

A vertex-input binding supplies the buffer-binding offset (through `vkCmdBindVertexBuffers`) and the per-vertex stride. An attribute description supplies a binding, format, and offset relative to that binding. For vertex index *i*, the fetch address therefore includes the bound buffer offset, the attribute offset, and *i* times the stride. The test chooses `attributeOffset()` to compensate for `bindingOffset`, so the first attribute begins at the next attribute-size-aligned byte location. A `vec2` attribute is 8 bytes and a `vec4` attribute is 16 bytes. [Vulkan vertex-input rules](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L370-L405) define these address and format fields.

`PACKED` places adjacent attributes together. `PADDED` inserts one attribute-size of unused bytes between records, doubling the stride. `OVERLAPPING` applies only to `vec2`: the buffer retains adjacent `vec2` records while the shader declares `vec4`. The shader uses `.xy` for position and consumes `.zw`, so an incorrect four-component fetch changes the output.

Static cases put `VkVertexInputBindingDescription` and `VkVertexInputAttributeDescription` in the pipeline. Dynamic cases enable `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` and issue `cmdSetVertexInputEXT` with equivalent `VkVertexInputBindingDescription2EXT` and `VkVertexInputAttributeDescription2EXT` before the draw. Both paths use the same shader source.

## Registration Hierarchy

```text
pipeline.monolithic.input_attribute_offset
├── vec2
└── vec4
```

[`createInputAttributeOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L511-L563) creates these families for each construction type. Each family then expands by `offset_N`, stride case, memory-offset choice, and static or dynamic state.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Data type | `TYPE_FLOAT_VEC2`, `TYPE_FLOAT_VEC4` | Selects attribute size and Vulkan format. | [`getTypeSize()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L101-L115) |
| `bindingOffset` | `0` through `typeSize - 1` | Selects every possible byte offset for the vertex-buffer binding. | [`offset` loop](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L517-L525) |
| `strideCase` | `PACKED`, `PADDED`, `OVERLAPPING` | Selects record stride and buffer layout; `OVERLAPPING` is `vec2` only. | [`StrideCase`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L53-L99) |
| `useMemoryOffset` | `false`, `true` | Selects zero or aligned nonzero buffer-memory binding offset. | [`memoryOffset` calculation](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L370-L391) |
| Vertex-input state | `static`, `dynamic` | Selects pipeline creation state or command-buffer state. | [`dynamic` setup](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L407-L435) |
| Pipeline construction | `PipelineConstructionType` | Selects the pipeline construction path. | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L117-L124) |

`vec2` has 8 byte-offset values. Each combines 3 layouts, 2 memory-offset choices, and 2 state modes for 96 leaves. `vec4` has 16 offsets and omits `OVERLAPPING`, producing 128 leaves. Each construction root therefore has 224 leaves. `monolithic.txt` contains 224 `dEQP-VK.pipeline.monolithic.input_attribute_offset.` paths.

## Behavior Parameters

### `PACKED`: adjacent records

`vertexDataPadding()` returns zero and `bindingStride()` equals the attribute size. `buildVertexBufferData()` writes each record at `bindingOffset + attributeOffset()`. This variant checks the combined binding offset, attribute offset, format, and compact stride calculation.

### `PADDED`: records with unused bytes

`vertexDataPadding()` returns the attribute size, so binding stride is twice the attribute size. The host skips padding after each attribute. Vertex fetch must advance by the declared stride rather than attribute width.

### `OVERLAPPING`: `vec2` storage with a `vec4` fetch

This variant is limited to `TYPE_FLOAT_VEC2`. `attributeFormat()` selects `VK_FORMAT_R32G32B32A32_SFLOAT`, and the shader input becomes `vec4` while the buffer remains a sequence of `vec2` records. The host appends a zero `vec2` so the last four-component fetch remains inside the buffer. The shader uses `.xy` for position and evaluates `.zw`, preventing an implementation from reading only two components.

## Shader Analysis

[`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L329-L358) generates both GLSL programs. The vertex shader reads location 0 and writes `gl_Position`. The fragment shader does not consume vertex input; it writes default blue. Fixed-function vertex-input state performs the behavior under test.

### Representative Shader Walkthrough 1: overlapping dynamic leaf

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.input_attribute_offset.vec2.offset_0.overlapping.no_memory_offset.dynamic
```

| Parameter choice | Meaning in this case |
|---|---|
| `TYPE_FLOAT_VEC2` | Each source record has 8 bytes. |
| `bindingOffset = 0` | The buffer binding begins at the allocation start. |
| `OVERLAPPING` | The shader fetches `vec4` from adjacent `vec2` records. |
| `no_memory_offset` | Buffer memory binds at offset zero. |
| `dynamic` | The command buffer supplies the vertex-input descriptions. |

#### Purpose

This case checks that dynamic vertex-input state supplies the correct format, stride, and attribute offset for a four-component fetch from adjacent `vec2` records.

#### Structural Design

The host generates one triangle per pixel in the 4×4 framebuffer. For overlap storage it appends `vec2(0.0f, 0.0f)` after the original vertices, keeping the final `vec4` fetch in bounds. The vertex shader forms position from `.xy` and evaluates `.zw`. The fragment shader writes opaque blue to covered pixels.

#### Shader Code

```glsl
#version 460
layout (location=0) in vec4 inPos;
void main (void) { gl_Position = vec4(inPos.xy, floor(abs(inPos.z) / 1000.0), (floor(abs(inPos.w) / 2500.0) + 1.0)); }
```

#### Additional Info

`dynamic` changes where the host submits descriptions, not the shader or vertex bytes. The corresponding static leaf supplies the same descriptions during pipeline construction.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level change from this shader | Evidence |
|---|---|---|
| `dynamic` | None; only the description-submission path changes. | [`dynamic` branch](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L407-L435) |
| `bindingOffset` | None; host buffer address and compensated attribute offset change. | [`attributeOffset()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L152-L158) |
| `useMemoryOffset` | None; allocation memory-binding offset changes. | [`memoryOffset` calculation](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L376-L390) |
| `strideCase` | Only `OVERLAPPING` uses this `vec4` shader. `PACKED` and `PADDED` use a `vec2` input. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L339-L356) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 43
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
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
    %v2float = OpTypeVector %float 2
     %uint_2 = OpConstant %uint 2
%_ptr_Input_float = OpTypePointer Input %float
 %float_1000 = OpConstant %float 1000
     %uint_3 = OpConstant %uint 3
 %float_2500 = OpConstant %float 2500
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpLoad %v4float %inPos
         %20 = OpVectorShuffle %v2float %19 %19 0 1
         %23 = OpAccessChain %_ptr_Input_float %inPos %uint_2
         %24 = OpLoad %float %23
         %25 = OpExtInst %float %1 FAbs %24
         %27 = OpFDiv %float %25 %float_1000
         %28 = OpExtInst %float %1 Floor %27
         %30 = OpAccessChain %_ptr_Input_float %inPos %uint_3
         %31 = OpLoad %float %30
         %32 = OpExtInst %float %1 FAbs %31
         %34 = OpFDiv %float %32 %float_2500
         %35 = OpExtInst %float %1 Floor %34
         %37 = OpFAdd %float %35 %float_1
         %38 = OpCompositeExtract %float %20 0
         %39 = OpCompositeExtract %float %20 1
         %40 = OpCompositeConstruct %v4float %38 %39 %28 %37
         %42 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %42 %40
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. `generateVertices()` makes triangles that cover the 4×4 framebuffer. `buildVertexBufferData()` writes bytes using the binding offset, compensated attribute offset, stride, and padding; overlap storage adds one `vec2`.
2. The test creates a `VK_BUFFER_USAGE_VERTEX_BUFFER_BIT` buffer in host-visible memory. With `useMemoryOffset`, it adds `lcm(vertexBufferReqs.alignment, attributeSize())` to the allocation and binds memory at that offset.
3. It creates a `VK_FORMAT_R8G8B8A8_UNORM` color image, render pass, framebuffer, pipeline layout, and graphics pipeline. Dynamic leaves enable `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT`.
4. The command buffer binds the pipeline and vertex buffer. Dynamic leaves call `cmdSetVertexInputEXT`, then all leaves call `cmdDraw`. The test copies the color image to a buffer, submits, and waits.
5. The host invalidates the allocation and compares it with `getDefaultColor()` using `tcu::floatThresholdCompare` and `tcu::Vec4(0.0f)`. Any non-blue result fails.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `PACKED` | Attribute address computation, bound-buffer offset handling, format interpretation, or static/dynamic state setup selects the wrong bytes. |
| `PADDED` | Stride calculation or padding skip is wrong, or the implementation uses attribute width rather than declared stride for a later vertex. |
| `OVERLAPPING` | A four-component fetch from adjacent `vec2` records is incomplete, reads the wrong neighboring bytes, or the `.zw` validation path receives unexpected values. |

### Cause Analysis

#### Binding and attribute offset error

**Possible failure symptoms:** `PACKED` cases fail at particular `offset_N` values, or multiple layouts fail at the same offsets. The result has pixels other than opaque blue.

**Possible implementation causes:** The implementation may add binding and attribute offsets incorrectly, ignore the vertex-buffer bind offset, or misinterpret format width. The source computes `attributeOffset()` as `((attributeSize - bindingOffset) % attributeSize)`, so losing either term fetches the wrong address.

#### Stride and padding error

**Possible failure symptoms:** `PADDED` cases fail while matching `PACKED` cases pass, often after the first vertex.

**Possible implementation causes:** Vertex fetch may advance by attribute size rather than declared binding stride, or apply padding twice. Inspect `bindingStride()` and the bytes from `buildVertexBufferData()`.

#### Overlapping fetch error

**Possible failure symptoms:** `OVERLAPPING` cases fail while ordinary `vec2` cases pass, potentially only on later vertices where `.zw` comes from the next record.

**Possible implementation causes:** The implementation may fetch only two components, interpret `VK_FORMAT_R32G32B32A32_SFLOAT` incorrectly, or read the wrong neighboring bytes. Check the appended final `vec2` and `.zw` expression before investigating rasterization.

#### Dynamic state or memory-offset error

**Possible failure symptoms:** Dynamic leaves fail while static leaves pass, or `with_memory_offset` differs from `no_memory_offset`.

**Possible implementation causes:** `cmdSetVertexInputEXT` may not establish the supplied descriptions, or memory binding and buffer binding offsets may combine incorrectly. Dynamic leaves require `VK_EXT_vertex_input_dynamic_state`.

## Case Pruning

### Requirement-based pruning

- Every case checks the selected pipeline-construction requirements.
- Dynamic cases require `VK_EXT_vertex_input_dynamic_state`.
- When `VK_KHR_portability_subset` is available, `checkSupport()` skips strides below or not divisible by `minVertexInputBindingStrideAlignment`.

### Design-based pruning

- `vec2` covers offsets `0` through `7`; `vec4` covers offsets `0` through `15`.
- `OVERLAPPING` is omitted for `vec4` because it models a `vec4` fetch from `vec2` storage.
- Every offset has both memory-binding choices and both state modes. The monolithic mustpass file contains all 224 leaves.

## Key Takeaways

- The matrix separates buffer binding offset, compensated attribute offset, optional memory-binding offset, and binding stride.
- `PACKED`, `PADDED`, and `OVERLAPPING` exercise distinct byte layouts. `OVERLAPPING` exposes adjacent-record fetches through `.zw` use.
- Static and dynamic vertex-input descriptions must produce identical opaque-blue output.
- The zero-threshold image comparison exposes fetch, state, and layout defects.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Parameters and layout helpers | [`TestParams`, `attributeOffset()`, and `bindingStride()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L117-L173) | Defines dimensions and byte layout. |
| Vertex-buffer construction | [`buildVertexBufferData()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L178-L220) | Shows padding, overlap tail, and byte placement. |
| Generated programs | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L329-L358) | Defines vertex input types and blue fragment output. |
| Runtime and comparison | [`InputAttributeOffsetInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L360-L507) | Shows setup, draw, readback, and oracle. |
| Registration | [`createInputAttributeOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L511-L563) | Defines the 224-leaf matrix per construction root. |
| Specification context | [Vertex input](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L14-L38) | Describes vertex input bindings and attributes. |
| Mustpass evidence | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) | Confirms monolithic coverage. |
