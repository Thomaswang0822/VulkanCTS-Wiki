## Overview

**Core question:** Does indexed vertex fetch remain correct when the index type, base vertex, bound-buffer offset, draw command, and rendering command-buffer mode change?

- `vktDrawIndexedTest.cpp` implements the `indexed_draw` test family under the draw test category.
- The file covers ordinary and instanced `vkCmdDrawIndexed`, maintenance6 null-index-buffer paths, 8-bit multi-bind draws, and index-buffer updates performed after binding.
- The generated cases compare rendered pixels, and selected maintenance6 cases also count fragment invocations in an SSBO.

## Background Knowledge

- An indexed draw reads an index from the bound index buffer, adds `vertexOffset`, and uses the resulting vertex index for vertex fetch. The byte offset passed when binding the index buffer selects where the index sequence begins; it is separate from a memory-allocation offset.
- Instancing repeats the indexed primitive sequence. `firstInstance` changes the instance ID visible to the vertex shader, while the index and vertex-offset rules remain the same.
- Indirect and multi-draw commands obtain draw parameters from device-visible memory. A count form executes the smaller of the available draw count and its maximum, so the command path has both an index-fetch and an indirect-parameter contract.

## Registration Hierarchy

The tree below expands the registered `renderpass` instance of `indexed_draw`; the same implementation is registered under dynamic-rendering primary, partial/complete secondary-command-buffer, and nested partial/complete secondary-command-buffer variants by `vktDrawTests.cpp`.

```text
draw.renderpass.indexed_draw
├── draw_indexed_bindindexbuffer2_maintenance6
├── draw_indexed_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_bindindexbuffer2_maintenance6
├── draw_indexed_count_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_count_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_count_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_indirect_bindindexbuffer2_maintenance6
├── draw_indexed_count_indirect_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_count_indirect_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_count_indirect_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_indirect_count_bindindexbuffer2_maintenance6
├── draw_indexed_count_indirect_count_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_count_indirect_count_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_count_indirect_count_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_indirect_count_maintenance6
├── draw_indexed_count_indirect_count_maintenance_5_maintenance6
├── draw_indexed_count_indirect_count_nulldescriptor_maintenance6
├── draw_indexed_count_indirect_count_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_indirect_maintenance6
├── draw_indexed_count_indirect_maintenance_5_maintenance6
├── draw_indexed_count_indirect_nulldescriptor_maintenance6
├── draw_indexed_count_indirect_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_maintenance6
├── draw_indexed_count_maintenance_5_maintenance6
├── draw_indexed_count_multi_bindindexbuffer2_maintenance6
├── draw_indexed_count_multi_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_count_multi_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_count_multi_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_multi_maintenance6
├── draw_indexed_count_multi_maintenance_5_maintenance6
├── draw_indexed_count_multi_nulldescriptor_maintenance6
├── draw_indexed_count_multi_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_count_nulldescriptor_maintenance6
├── draw_indexed_count_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_indirect_bindindexbuffer2_maintenance6
├── draw_indexed_indirect_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_indirect_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_indirect_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_indirect_count_bindindexbuffer2_maintenance6
├── draw_indexed_indirect_count_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_indirect_count_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_indirect_count_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_indirect_count_maintenance6
├── draw_indexed_indirect_count_maintenance_5_maintenance6
├── draw_indexed_indirect_count_nulldescriptor_maintenance6
├── draw_indexed_indirect_count_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_indirect_maintenance6
├── draw_indexed_indirect_maintenance_5_maintenance6
├── draw_indexed_indirect_nulldescriptor_maintenance6
├── draw_indexed_indirect_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_maintenance6
├── draw_indexed_maintenance_5_maintenance6
├── draw_indexed_multi_bindindexbuffer2_maintenance6
├── draw_indexed_multi_bindindexbuffer2_maintenance_5_maintenance6
├── draw_indexed_multi_bindindexbuffer2_nulldescriptor_maintenance6
├── draw_indexed_multi_bindindexbuffer2_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_multi_maintenance6
├── draw_indexed_multi_maintenance_5_maintenance6
├── draw_indexed_multi_nulldescriptor_maintenance6
├── draw_indexed_multi_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_nulldescriptor_maintenance6
├── draw_indexed_nulldescriptor_maintenance_5_maintenance6
├── draw_indexed_triangle_list
├── draw_indexed_triangle_list_maintenance_5
├── draw_indexed_triangle_list_offset_minus_one
├── draw_indexed_triangle_list_offset_minus_one_maintenance_5
├── draw_indexed_triangle_list_offset_minus_one_with_alloc_offset
├── draw_indexed_triangle_list_offset_minus_one_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_list_offset_minus_one_with_bind_offset
├── draw_indexed_triangle_list_offset_minus_one_with_bind_offset_maintenance_5
├── draw_indexed_triangle_list_offset_minus_one_with_bind_offset_with_alloc_offset
├── draw_indexed_triangle_list_offset_minus_one_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_list_offset_negative_large
├── draw_indexed_triangle_list_offset_negative_large_maintenance_5
├── draw_indexed_triangle_list_offset_negative_large_with_alloc_offset
├── draw_indexed_triangle_list_offset_negative_large_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_list_offset_negative_large_with_bind_offset
├── draw_indexed_triangle_list_offset_negative_large_with_bind_offset_maintenance_5
├── draw_indexed_triangle_list_offset_negative_large_with_bind_offset_with_alloc_offset
├── draw_indexed_triangle_list_offset_negative_large_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_list_with_alloc_offset
├── draw_indexed_triangle_list_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_list_with_bind_offset
├── draw_indexed_triangle_list_with_bind_offset_maintenance_5
├── draw_indexed_triangle_list_with_bind_offset_with_alloc_offset
├── draw_indexed_triangle_list_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_strip
├── draw_indexed_triangle_strip_maintenance_5
├── draw_indexed_triangle_strip_offset_minus_one
├── draw_indexed_triangle_strip_offset_minus_one_maintenance_5
├── draw_indexed_triangle_strip_offset_minus_one_with_alloc_offset
├── draw_indexed_triangle_strip_offset_minus_one_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_strip_offset_minus_one_with_bind_offset
├── draw_indexed_triangle_strip_offset_minus_one_with_bind_offset_maintenance_5
├── draw_indexed_triangle_strip_offset_minus_one_with_bind_offset_with_alloc_offset
├── draw_indexed_triangle_strip_offset_minus_one_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_strip_offset_negative_large
├── draw_indexed_triangle_strip_offset_negative_large_maintenance_5
├── draw_indexed_triangle_strip_offset_negative_large_with_alloc_offset
├── draw_indexed_triangle_strip_offset_negative_large_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_strip_offset_negative_large_with_bind_offset
├── draw_indexed_triangle_strip_offset_negative_large_with_bind_offset_maintenance_5
├── draw_indexed_triangle_strip_offset_negative_large_with_bind_offset_with_alloc_offset
├── draw_indexed_triangle_strip_offset_negative_large_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_strip_with_alloc_offset
├── draw_indexed_triangle_strip_with_alloc_offset_maintenance_5
├── draw_indexed_triangle_strip_with_bind_offset
├── draw_indexed_triangle_strip_with_bind_offset_maintenance_5
├── draw_indexed_triangle_strip_with_bind_offset_with_alloc_offset
├── draw_indexed_triangle_strip_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_list
├── draw_instanced_indexed_triangle_list_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_minus_one
├── draw_instanced_indexed_triangle_list_offset_minus_one_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_minus_one_with_alloc_offset
├── draw_instanced_indexed_triangle_list_offset_minus_one_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_minus_one_with_bind_offset
├── draw_instanced_indexed_triangle_list_offset_minus_one_with_bind_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_minus_one_with_bind_offset_with_alloc_offset
├── draw_instanced_indexed_triangle_list_offset_minus_one_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_negative_large
├── draw_instanced_indexed_triangle_list_offset_negative_large_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_negative_large_with_alloc_offset
├── draw_instanced_indexed_triangle_list_offset_negative_large_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_negative_large_with_bind_offset
├── draw_instanced_indexed_triangle_list_offset_negative_large_with_bind_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_offset_negative_large_with_bind_offset_with_alloc_offset
├── draw_instanced_indexed_triangle_list_offset_negative_large_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_with_alloc_offset
├── draw_instanced_indexed_triangle_list_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_with_bind_offset
├── draw_instanced_indexed_triangle_list_with_bind_offset_maintenance_5
├── draw_instanced_indexed_triangle_list_with_bind_offset_with_alloc_offset
├── draw_instanced_indexed_triangle_list_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip
├── draw_instanced_indexed_triangle_strip_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_minus_one
├── draw_instanced_indexed_triangle_strip_offset_minus_one_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_minus_one_with_alloc_offset
├── draw_instanced_indexed_triangle_strip_offset_minus_one_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_minus_one_with_bind_offset
├── draw_instanced_indexed_triangle_strip_offset_minus_one_with_bind_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_minus_one_with_bind_offset_with_alloc_offset
├── draw_instanced_indexed_triangle_strip_offset_minus_one_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_negative_large
├── draw_instanced_indexed_triangle_strip_offset_negative_large_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_negative_large_with_alloc_offset
├── draw_instanced_indexed_triangle_strip_offset_negative_large_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_negative_large_with_bind_offset
├── draw_instanced_indexed_triangle_strip_offset_negative_large_with_bind_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_offset_negative_large_with_bind_offset_with_alloc_offset
├── draw_instanced_indexed_triangle_strip_offset_negative_large_with_bind_offset_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_with_alloc_offset
├── draw_instanced_indexed_triangle_strip_with_alloc_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_with_bind_offset
├── draw_instanced_indexed_triangle_strip_with_bind_offset_maintenance_5
├── draw_instanced_indexed_triangle_strip_with_bind_offset_with_alloc_offset
├── draw_instanced_indexed_triangle_strip_with_bind_offset_with_alloc_offset_maintenance_5
├── multibind_8bit_case_0
├── multibind_8bit_case_0_sorted
├── multibind_8bit_case_1
├── multibind_8bit_case_10
├── multibind_8bit_case_10_sorted
├── multibind_8bit_case_11
├── multibind_8bit_case_11_sorted
├── multibind_8bit_case_12
├── multibind_8bit_case_12_sorted
├── multibind_8bit_case_13
├── multibind_8bit_case_13_sorted
├── multibind_8bit_case_14
├── multibind_8bit_case_14_sorted
├── multibind_8bit_case_15
├── multibind_8bit_case_15_sorted
├── multibind_8bit_case_16
├── multibind_8bit_case_16_sorted
├── multibind_8bit_case_17
├── multibind_8bit_case_17_sorted
├── multibind_8bit_case_18
├── multibind_8bit_case_18_sorted
├── multibind_8bit_case_19
├── multibind_8bit_case_19_sorted
├── multibind_8bit_case_1_sorted
├── multibind_8bit_case_2
├── multibind_8bit_case_2_sorted
├── multibind_8bit_case_3
├── multibind_8bit_case_3_sorted
├── multibind_8bit_case_4
├── multibind_8bit_case_4_sorted
├── multibind_8bit_case_5
├── multibind_8bit_case_5_sorted
├── multibind_8bit_case_6
├── multibind_8bit_case_6_sorted
├── multibind_8bit_case_7
├── multibind_8bit_case_7_sorted
├── multibind_8bit_case_8
├── multibind_8bit_case_8_sorted
├── multibind_8bit_case_9
├── multibind_8bit_case_9_sorted
├── update_index_buffer_before_draw_16
├── update_index_buffer_before_draw_32
└── update_index_buffer_before_draw_8
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Ordinary topology | `triangle_list`, `triangle_strip` | Changes primitive assembly and the index count used by the draw. | [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1712) |
| `vertexOffset` | `13`, `-1`, `-13` | Exercises positive and negative base-vertex adjustment. | [`OffsetCases`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1727) |
| Index bind offset | `0`, `16` | Moves the index sequence within the bound buffer. | [`IndexBindOffsetCases`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1739) |
| Memory allocation offset | `0`, `16` | Moves the allocation-backed buffer start; the implementation rounds it to alignment. | [`MemoryBindOffsetCases`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1749) |
| Maintenance5 binding | absent, `_maintenance_5` | Selects `vkCmdBindIndexBuffer` or `vkCmdBindIndexBuffer2`. | [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1614) |
| Indexed behavior family | `draw_indexed_*`, `draw_instanced_indexed_*`, `draw_indexed*_*maintenance6`, `multibind_8bit_case_*`, `update_index_buffer_before_draw_*` | Selects the command and resource behavior under test. | [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1771) |
| Maintenance6 command | indexed, `_indirect`, `_indirect_count`, `_multi` | Selects direct, indirect, indirect-count, or `vkCmdDrawMultiIndexedEXT` execution. | [`Maintenance6Cases`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1807) |
| Maintenance6 switches | `_bindindexbuffer2`, `_nulldescriptor`, `_count` | Selects null-descriptor/bind2 behavior and fragment-count validation. | [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1820) |
| 8-bit case | `0`-`19`, with optional `_sorted` | Selects the pseudorandom block layout and its sorted counterpart. | [`Multibind8BitInstance`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1032) |
| Update index type | `8`, `16`, `32` | Selects `VK_INDEX_TYPE_UINT8`, `VK_INDEX_TYPE_UINT16`, or `VK_INDEX_TYPE_UINT32`. | [`indexTypeCases`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1868) |
| Rendering mode | `renderpass`, `dynamic_rendering`, `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Reuses the family with the command-recording mode selected by `SharedGroupParams`. | [`createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family changes the operation whose indexed-input contract is checked.

### `draw_indexed_*`: Base vertex and buffer offsets

The test writes a known index sequence and vertex data, binds the index buffer at the requested offset, then calls `vkCmdDrawIndexed` with `indexCount` 6. For negative offsets, initialization shifts the stored indices upward so that adding the negative `vertexOffset` addresses the intended vertices. Positive offsets are covered by leading vertex padding. Both topologies must produce the blue reference rectangle.

### `draw_instanced_indexed_*`: Instanced indexed fetch

`DrawInstancedIndexed` inherits the ordinary setup and issues four instances with `firstInstance = 2`. `VertexFetchInstancedFirstInstance.vert` checks the instance-coordinate path while the same topology, base-vertex, bind-offset, allocation-offset, and maintenance5 dimensions remain active.

### `draw_indexed*_*maintenance6`: Null descriptors and indexed command variants

`DrawIndexedMaintenance6` uses point-list draws on a 1x1 target. It covers direct, indirect, indirect-count, and (when not building VulkanSC) multi-indexed commands. The loops combine bind2, null-descriptor, and fragment-count switches. Null-descriptor cases bind `VK_NULL_HANDLE`; bind2 cases use `vkCmdBindIndexBuffer2` and exercise the maintenance6 API behavior.

### `multibind_8bit_case_*`: Repeated 8-bit binds

Each case divides a 16x16 target into eight pseudorandom blocks and binds a separate `VK_INDEX_TYPE_UINT8` index buffer before each indexed draw. The 20 seeds are generated in unsorted and sorted forms. This family is excluded for dynamic rendering, secondary command buffers, and the maintenance5-extension pass.

### `update_index_buffer_before_draw_*`: Update after binding

The test binds a device-local index buffer, copies the selected index data from a staging buffer with `cmdCopyBuffer`, inserts the required transfer-to-vertex-input barrier, and then draws. The leaves select `VK_INDEX_TYPE_UINT8`, `VK_INDEX_TYPE_UINT16`, or `VK_INDEX_TYPE_UINT32`.

## Shader Analysis

The ordinary path uses the repository shaders `VertexFetch.vert` and `VertexFetch.frag`. The representative vertex shader below is compiled from the exact repository source for the ordinary indexed path. It forwards the fetched position, compares the built-in `gl_VertexIndex` with the reference index stored in vertex data, and colors a matching vertex with its expected color. The fragment shader simply forwards that color. Maintenance6 count cases instead use `VertexFetchCount.vert` and `VertexFetchCount.frag`; the latter atomically increments `ssbo.counter` for every fragment.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.indexed_draw.draw_indexed_triangle_list
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` |
| `vertexOffset` | `13` |
| Index bind offset | `0` |
| Allocation offset | `0` |

#### Purpose

The shader makes an indexing mistake visible: the expected vertex writes its input color, while another fetched vertex writes red.

#### Structural Design

| Shader value | Source | Role |
|---|---|---|
| `in_position` | vertex attribute location 0 | Position fetched using the indexed vertex. |
| `in_color` | vertex attribute location 1 | Expected color for the referenced vertex. |
| `in_refVertexIndex` | vertex attribute location 2 | Reference index compared with `gl_VertexIndex`. |
| `gl_VertexIndex` | Vulkan vertex built-in | Effective indexed vertex number after the draw's index and base-vertex processing. |
| `out_color` | vertex output / fragment input | Pixel color used by the image comparison. |

#### Shader Code

```glsl
#version 430

layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 2) in int in_refVertexIndex;

layout(location = 0) out vec4 out_color;

out gl_PerVertex {
    vec4 gl_Position;
};

void main() {
    gl_Position = in_position;
    if (gl_VertexIndex == in_refVertexIndex)
        out_color = in_color;
    else
        out_color = vec4(1.0, 0.0, 0.0, 1.0);
}
```

#### Additional Info

- The fragment stage is a pass-through stage: `VertexFetch.frag` writes its input `in_color` to the color attachment.
- The shader source is [`VertexFetch.vert`](../../../data/vulkan/draw/VertexFetch.vert); the companion fragment source is [`VertexFetch.frag`](../../../data/vulkan/draw/VertexFetch.frag).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `vertexOffset` | Changes the effective `gl_VertexIndex` without changing the shader source. | [`VertexFetch.vert`](../../../data/vulkan/draw/VertexFetch.vert), [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1771-L1784) |
| Index bind and allocation offsets | Move the same index bytes through different buffer-address calculations without changing the shader source. | [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1739-L1784) |
| Instanced indexed family | Replaces the vertex shader with `VertexFetchInstancedFirstInstance.vert`, which adds a per-instance position selected by `gl_InstanceIndex`; the fragment shader remains `VertexFetch.frag`. | [`VertexFetchInstancedFirstInstance.vert`](../../../data/vulkan/draw/VertexFetchInstancedFirstInstance.vert), [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1787-L1795) |
| Maintenance6 fragment-count mode | Replaces the ordinary pair with `VertexFetchCount.vert` and `VertexFetchCount.frag`; the vertex shader uses fixed point positions and colors, and the fragment shader atomically increments the counter SSBO. | [`VertexFetchCount.vert`](../../../data/vulkan/draw/VertexFetchCount.vert), [`VertexFetchCount.frag`](../../../data/vulkan/draw/VertexFetchCount.frag), [`DrawIndexedTests::init`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1832-L1844) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 34
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %gl_VertexIndex %in_refVertexIndex %out_color %in_color
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %in_refVertexIndex "in_refVertexIndex"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %in_position Location 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %in_refVertexIndex Location 2
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
%in_refVertexIndex = OpVariable %_ptr_Input_int Input
       %bool = OpTypeBool
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
         %33 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %in_position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %20 = OpLoad %int %gl_VertexIndex
         %22 = OpLoad %int %in_refVertexIndex
         %24 = OpIEqual %bool %20 %22
               OpSelectionMerge %26 None
               OpBranchConditional %24 %25 %30
         %25 = OpLabel
         %29 = OpLoad %v4float %in_color
               OpStore %out_color %29
               OpBranch %26
         %30 = OpLabel
               OpStore %out_color %33
               OpBranch %26
         %26 = OpLabel
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- `DrawIndexed::initialize` creates the pipeline layout, color target, render pass or dynamic-rendering state, framebuffer when needed, vertex buffer, and index buffer. `iterate` records the selected command-buffer path, binds the index buffer and vertex data, and issues the indexed draw.
- Ordinary and instanced families use `tcu::fuzzyCompare` with threshold `0.05` against the expected blue rectangle. Instancing uses the same image contract.
- Maintenance6 count cases use `tcu::intThresholdCompare` with zero threshold and then check that the SSBO counter equals `indexCount`. Null-descriptor cases without the count path compare against an `rr::Renderer`-generated reference with `tcu::intThresholdPositionDeviationCompare`.
- The 8-bit multi-bind and update-before-draw families read back the color buffer and use exact `tcu::floatThresholdCompare` against an all-blue image.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `draw_indexed_*` | Incorrect index fetch, base-vertex addition, index-buffer bind offset, allocation offset, or primitive assembly. |
| `draw_instanced_indexed_*` | Incorrect indexed instance repetition, `firstInstance` handling, or inherited vertex/index fetch. |
| `draw_indexed*_*maintenance6` | Incorrect maintenance6 null-descriptor, bind2, indirect parameter, multi-draw, or fragment-count behavior. |
| `multibind_8bit_case_*` | Incorrect `VK_INDEX_TYPE_UINT8` decoding or state replacement across repeated binds. |
| `update_index_buffer_before_draw_*` | Missing visibility/order between `cmdCopyBuffer` and vertex-input index reads, or incorrect index-type decoding. |

### Cause Analysis

#### Indexed address calculation and primitive assembly

**Possible failure symptoms:** The ordinary image differs from the blue reference, often with red pixels from the vertex shader's mismatch branch or with a displaced primitive.

**Possible implementation causes:** The implementation may apply `vertexOffset` at the wrong stage, calculate the index-buffer address incorrectly, or fail to assemble the selected triangle list/strip from the fetched indices. Vulkan specifies that primitive-restart comparison occurs before adding `vertexOffset`; these cases do not enable restart, but the ordering explains why index and base-vertex responsibilities are separate.

#### Instancing and first-instance state

**Possible failure symptoms:** The four-instance image differs while a single-instance case passes, or the instance-coordinate shader receives the wrong first instance.

**Possible implementation causes:** The driver may mishandle instance repetition or the `firstInstance = 2` value used by `DrawInstancedIndexed`, or may combine instance state with vertex-index arithmetic incorrectly.

#### Maintenance6, indirect, and null-descriptor behavior

**Possible failure symptoms:** A null-descriptor case produces unexpected fragments, an indirect variant uses the wrong parameters, a multi-draw variant executes the wrong number of draws, or the SSBO counter differs from `indexCount`.

**Possible implementation causes:** The implementation may mishandle `vkCmdBindIndexBuffer2`, null index-buffer semantics, indirect/count parameter fetch, or the maintenance6 command rules. A counter mismatch specifically indicates that the observed fragment count did not match the test's expected indexed point draw.

#### 8-bit decoding and copy-before-draw visibility

**Possible failure symptoms:** A multi-bind or update-before-draw case produces a non-blue pixel or a result that changes with `VK_INDEX_TYPE_UINT8` versus the wider index types.

**Possible implementation causes:** The driver may decode 8-bit indices with the wrong element width, fail to replace index-buffer state between draws, or omit the transfer-write to vertex-input-read synchronization needed after `cmdCopyBuffer`.

## Case Pruning

### Requirement-based pruning

- Maintenance6 leaves require `VK_KHR_maintenance6`; bind2 paths also require the maintenance5 capability used by the source. Null-descriptor leaves require `VK_EXT_robustness2` and its `nullDescriptor` feature. Count leaves require `fragmentStoresAndAtomics`; indirect-count leaves require draw-indirect-count support; multi leaves require `VK_EXT_multi_draw` and are excluded from VulkanSC builds.
- 8-bit cases and update-before-draw `8` require the index-type-uint8 feature. The support checks reject unsupported feature combinations before execution.

### Design-based pruning

- Standard generation uses only triangle list and triangle strip, so adjacency and other topologies do not appear in this family.
- The 8-bit and update-before-draw families are registered only for the ordinary render-pass configuration, not dynamic rendering, secondary command buffers, or the maintenance5-extension pass. The source deliberately avoids multiplying these specialized cases across modes where they are not implemented.

## Key Takeaways

- Indexed correctness depends on two separate address adjustments: the index-buffer bind/allocation offsets locate the index data, while `vertexOffset` adjusts the fetched vertex index.
- Instanced cases keep the same index path and add four instances beginning at `firstInstance = 2`.
- Maintenance6 cases test command and descriptor variants; count leaves add an independent SSBO observation.
- The 8-bit and copy-before-draw families target index decoding and resource-state transitions rather than ordinary image geometry alone.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Registration and generated names | [`vktDrawIndexedTest.cpp`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1603-L1885) |
| Public registration class | [`vktDrawIndexedTest.hpp`](../../../modules/vulkan/draw/vktDrawIndexedTest.hpp#L34-L48) |
| Rendering-mode registration | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) |
| Ordinary indexed setup and draw | [`DrawIndexed::initialize` / `iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L146-L511) |
| Instanced indexed draw | [`DrawInstancedIndexed::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L514-L640) |
| Maintenance6 path | [`DrawIndexedMaintenance6::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L642-L957) |
| 8-bit multi-bind | [`Multibind8BitInstance::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1032-L1390) |
| Update before draw | [`UpdateBeforeDrawInstance::iterate`](../../../modules/vulkan/draw/vktDrawIndexedTest.cpp#L1402-L1598) |
| Mustpass registration evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L18050-L18252) |
| Indexed draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L37-L89) |
