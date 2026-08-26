## Overview

**Core question:** When a render pass instance captures per-region performance counters via `VK_ARM_performance_counters_by_region`, does the implementation write counter values into the correct tile regions of the capture buffer, and do those values match the expected value for each region?

- This page covers the `performance_counters_by_region` test family in [`vktRenderPassPerformanceCountersByRegionTests.cpp`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp). The family is created by [`createRenderPassPerformanceCountersByRegionTests()`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1610-L1614) and attached under each rendering variant root (`renderpass1`, `renderpass2`, `dynamic_rendering`) at the rendering-type level.
- It registers a small matrix of test case leaves that combine one color format (`R8G8B8A8_UNORM`) with one or two attachment layers, each capturing a single counter named "Fragment warps".
- The core idea is to render a full-screen blue quad into a color attachment whose render pass instance has per-region performance counters enabled, then read back the counter buffer and check that each tile region's counter value matches the expected value for a complete region (or falls within `[1, expectedMax]` for a partial region), where the expected value scales with the layer index.
- The test also writes per-pixel device timestamps into an SSBO via `clockRealtimeEXT()` and checks that timestamps from different logical devices do not overlap, as a side-channel consistency check.

## Background Knowledge

- **Per-region performance counters.** `VK_ARM_performance_counters_by_region` lets an application request that the implementation capture performance counters per tile region during a render pass instance. The framebuffer is divided into regions of a fixed size reported by `VkPhysicalDevicePerformanceCounterPropertiesPerRegionARM`, and the implementation writes the requested counter values into a host-visible buffer laid out region-by-region ([VK_ARM_performance_counters_by_region.adoc](../../../../vulkan-docs/src/appendices/VK_ARM_performance_counters_by_region.adoc)).
- **Region layout.** The capture buffer is organized as a 2D grid of regions, with each region holding `maxPerRegionPerformanceCounters` uint32 values padded to `regionAlignment`. Rows are padded to `rowStrideAlignment`. This layout is reconstructed during verification to locate each region's counter values.
- **Complete vs partial regions.** The last row or column of regions may be partial if the framebuffer dimensions are not a multiple of the region size. The expected counter range differs for partial regions because they cover fewer pixels and therefore trigger fewer fragment invocations.

## Registration Hierarchy

```text
renderpasses.renderpass1.performance_counters_by_region
└── r8g8b8a8_unorm
```

The tree shows the `renderpass1` representative root. The same family is registered under `renderpasses.renderpass2.performance_counters_by_region` and under each `renderpasses.dynamic_rendering.*.performance_counters_by_region` root. Under each root, the single `r8g8b8a8_unorm` format node holds two leaves: `layers_1` and `layers_2` ([registration loop](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1581-L1606)). The family is non-SC and is guarded by `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Color format | `R8G8B8A8_UNORM` | The only format the test uses. It is a common UNORM color format sufficient to produce a full-screen blue quad. | [formats array](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1575-L1577) |
| Layer count | `1`, `2` | The number of attachment layers. Two layers add a geometry shader that routes draws to a second layer via `gl_Layer`, doubling the expected fragment work for the "Fragment warps" counter. | [layer loop](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1598-L1607) |
| Counter | "Fragment warps", regionMin=0, regionMax=0, fragment=256 | The single counter captured per region. Because both `regionMin` and `regionMax` are `0` and are offset by the same `fragment` value, the expected counter for a complete region is an exact value, not a range. | [counter config](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1587) |

## Behavior Parameters

The primary behavioral axis is the layer count. For each layer index, the host issues a separate draw of `3 * (layerIdx + 1)` vertices ([draw commands](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L951-L966)). Both the expected minimum and maximum for a complete region are set to `fragment * (layerIdx + 1)`, so complete regions are checked against an exact value — `256` for layer 0 and `512` for layer 1. Partial regions use a minimum of `1` and the same maximum.

The counter is fixed to "Fragment warps" across all leaves, so the layer count is the only value that changes the expected counter value.

### layers_1: single-layer counter capture

The render pass instance has one color attachment layer. The fragment shader runs once per covered pixel, writes blue to the color attachment, and writes a device timestamp to the SSBO. Because both `regionMin` and `regionMax` are `0` and are offset by the same `fragment` value, the expected "Fragment warps" counter per complete region is an exact value of `256` ([counter range computation](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1248-L1262)).

### layers_2: two-layer counter capture with geometry shader routing

A geometry shader sets `gl_Layer` from the push constant to route the triangle to a chosen layer ([geometry shader](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1386-L1407)). The host issues a separate draw per layer index with `3 * (layerIdx + 1)` vertices ([draw commands](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L951-L966)), so layer 1 produces twice the fragment work of layer 0. The expected "Fragment warps" counter per complete region is an exact value of `512`, because the `fragment` value (256) is scaled by `layerIdx + 1`.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.renderpass1.performance_counters_by_region.r8g8b8a8_unorm.layers_2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass1` | Uses the legacy render-pass path; the shader interfaces and draw behavior are shared with the `renderpass2` and dynamic-rendering variants. |
| `R8G8B8A8_UNORM`, `layers_2` | The two-layer case enables the geometry shader. The host submits one three-vertex draw for each layer and changes the push-constant `layer`, so this case exercises both the full-screen producer and layer routing while the fragment shader records the timestamp side channel. |

#### Purpose

The shaders generate the full-screen fragment workload whose per-region counter values are captured by the render pass. The fragment shader also records one realtime device-clock value per pixel and writes blue to the color attachment, while the geometry shader routes the triangle to the layer selected by the host.

#### Structural Design

| Stage | Input/control | Device-side work | Observable result |
|-------|---------------|------------------|-------------------|
| Vertex | `gl_VertexIndex`; no vertex buffer | Select one of three clip-space positions for a full-screen triangle. | Rasterization covers the attachment. |
| Geometry (`layers_2`) | `pc.layer`; three vertices from `gl_in` | Copy the input triangle and set `gl_Layer` before emitting three vertices. | The draw targets exactly the selected array layer. |
| Fragment | `gl_FragCoord`, `pc.width`, SSBO binding 0 | Compute `x + y * width`, store `clockRealtimeEXT()` at that index, then output `(0, 0, 1, 1)`. | Host reads timestamps and a blue image; the implementation's region counter measures the resulting fragment work. |

#### Shader Code

##### Fragment Shader

```glsl
#version 450
#extension GL_EXT_shader_realtime_clock : require
#extension GL_ARB_gpu_shader_int64 : require
precision highp float;
/// Set 0, binding 0 is the host-created storage buffer used as a per-pixel
/// timestamp array. Its extent is `width * height` uint64 values.
layout(set=0, binding=0, std430) buffer SSBO
{
	uint64_t time_stamps[];
} ssbo;
/// The host pushes the attachment dimensions and selected layer at offset 0.
/// The fragment stage uses `width` for row-major timestamp addressing; the
/// `layer` member is part of the shared push-constant layout but is unused here.
layout(push_constant, std140) uniform PC
{
	float width;
	float height;
	uint layer;
} pc;
/// The fixed color output is checked after the image is copied back to the host.
layout(location = 0) out vec4 out_color;
void main()
{
	/// Convert the fragment coordinates and pushed width into the row-major
	/// linear index used by the host-side timestamp collection.
	int time_stamp_idx = int(gl_FragCoord.x) + int(gl_FragCoord.y) * int(pc.width);
	ssbo.time_stamps[time_stamp_idx] = clockRealtimeEXT();
	out_color = vec4(0,0,1,1);
}
```

##### Geometry Shader

```glsl
#version 450
/// One invocation receives the triangle generated by the vertex shader and
/// emits one triangle strip with exactly three vertices.
layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;
/// The host writes the selected array-layer index into the same 12-byte push
/// constant range used by the fragment stage. `width` and `height` are unused
/// in this stage but preserve the generated block layout.
layout(push_constant, std140) uniform PC
{
	float width;
	float height;
	int  layer;
} pc;
void main()
{
	gl_Layer = pc.layer;
	gl_Position = gl_in[0].gl_Position;
	EmitVertex();
	gl_Position = gl_in[1].gl_Position;
	EmitVertex();
	gl_Position = gl_in[2].gl_Position;
	EmitVertex();
	EndPrimitive();
}
```

#### Additional Info

- The vertex shader is fixed across all leaves and is intentionally not expanded here: it has no resources or variant-dependent control flow beyond selecting the three full-screen triangle positions from `gl_VertexIndex` ([generator](../../../modules/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1341-L1351)).
- The geometry stage is emitted only when `config.layerCount > 1`; `layers_1` binds only the vertex and fragment stages, while `layers_2` binds this geometry stage ([stage branch](../../../modules/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1379-L1403), [pipeline selection](../../../modules/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L704-L710)).
- The storage buffer is allocated as `width * height * sizeof(uint64_t)` and bound at set 0, binding 0; the host later invalidates that memory and reduces the per-pixel values into per-region timestamp intervals ([buffer setup](../../../modules/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L639-L642), [descriptor setup](../../../modules/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L329-L396), [timestamp collection](../../../modules/vulkancts/modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1268-L1294)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `layers_1` vs `layers_2` | `layers_1` omits the geometry shader and draws the full-screen triangle directly to layer 0. `layers_2` adds a geometry stage, and the host performs one draw per layer while pushing the selected layer index; the fragment shader remains unchanged. | [shader branch](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1379-L1403), [draw loop](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L951-L966) |
| `renderpass1`, `renderpass2`, and dynamic rendering | No GLSL source changes: the same `vert`, `frag`, and conditional `geom` collections are used. The rendering type changes host-side pass or dynamic-rendering setup, not shader-visible interfaces. | [build dispatch](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L812-L821), [pipeline setup](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L763-L809) |
| `R8G8B8A8_UNORM` | The only registered color format; it changes the attachment format used by the pipeline, but not the generated shader text. | [format registration](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1572-L1576) |

#### SPIR-V

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 47
; Schema: 0
               OpCapability Shader
               OpCapability Int64
               OpCapability ShaderClockKHR
               OpExtension "SPV_KHR_shader_clock"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %out_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_ARB_gpu_shader_int64"
               OpSourceExtension "GL_EXT_shader_realtime_clock"
               OpName %main "main"
               OpName %time_stamp_idx "time_stamp_idx"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %PC "PC"
               OpMemberName %PC 0 "width"
               OpMemberName %PC 1 "height"
               OpMemberName %PC 2 "layer"
               OpName %pc "pc"
               OpName %SSBO "SSBO"
               OpMemberName %SSBO 0 "time_stamps"
               OpName %ssbo "ssbo"
               OpName %out_color "out_color"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %PC Block
               OpMemberDecorate %PC 0 Offset 0
               OpMemberDecorate %PC 1 Offset 4
               OpMemberDecorate %PC 2 Offset 8
               OpDecorate %_runtimearr_ulong ArrayStride 8
               OpDecorate %SSBO BufferBlock
               OpMemberDecorate %SSBO 0 Offset 0
               OpDecorate %ssbo Binding 0
               OpDecorate %ssbo DescriptorSet 0
               OpDecorate %out_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
         %PC = OpTypeStruct %float %float %uint
%_ptr_PushConstant_PC = OpTypePointer PushConstant %PC
         %pc = OpVariable %_ptr_PushConstant_PC PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
      %ulong = OpTypeInt 64 0
%_runtimearr_ulong = OpTypeRuntimeArray %ulong
       %SSBO = OpTypeStruct %_runtimearr_ulong
%_ptr_Uniform_SSBO = OpTypePointer Uniform %SSBO
       %ssbo = OpVariable %_ptr_Uniform_SSBO Uniform
%_ptr_Uniform_ulong = OpTypePointer Uniform %ulong
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %46 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%time_stamp_idx = OpVariable %_ptr_Function_int Function
         %16 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %17 = OpLoad %float %16
         %18 = OpConvertFToS %int %17
         %20 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %21 = OpLoad %float %20
         %22 = OpConvertFToS %int %21
         %28 = OpAccessChain %_ptr_PushConstant_float %pc %int_0
         %29 = OpLoad %float %28
         %30 = OpConvertFToS %int %29
         %31 = OpIMul %int %22 %30
         %32 = OpIAdd %int %18 %31
               OpStore %time_stamp_idx %32
         %38 = OpLoad %int %time_stamp_idx
         %39 = OpReadClockKHR %ulong %uint_1
         %41 = OpAccessChain %_ptr_Uniform_ulong %ssbo %int_0 %38
               OpStore %41 %39
               OpStore %out_color %46
               OpReturn
               OpFunctionEnd
```

</details>

##### Geometry Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 42
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_Layer %_ %gl_in
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_Layer "gl_Layer"
               OpName %PC "PC"
               OpMemberName %PC 0 "width"
               OpMemberName %PC 1 "height"
               OpMemberName %PC 2 "layer"
               OpName %pc "pc"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpDecorate %gl_Layer BuiltIn Layer
               OpDecorate %PC Block
               OpMemberDecorate %PC 0 Offset 0
               OpMemberDecorate %PC 1 Offset 4
               OpMemberDecorate %PC 2 Offset 8
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Output_int = OpTypePointer Output %int
   %gl_Layer = OpVariable %_ptr_Output_int Output
      %float = OpTypeFloat 32
         %PC = OpTypeStruct %float %float %int
%_ptr_PushConstant_PC = OpTypePointer PushConstant %PC
         %pc = OpVariable %_ptr_PushConstant_PC PushConstant
      %int_2 = OpConstant %int 2
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_PushConstant_int %pc %int_2
         %16 = OpLoad %int %15
               OpStore %gl_Layer %16
         %31 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %32 = OpLoad %v4float %31
         %34 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %34 %32
               OpEmitVertex
         %36 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %37 = OpLoad %v4float %36
         %38 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %38 %37
               OpEmitVertex
         %39 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %40 = OpLoad %v4float %39
         %41 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %41 %40
               OpEmitVertex
               OpEndPrimitive
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

Each test case creates three `PerformanceCountersByRegionContainer` instances (one per logical device used for the timestamp overlap check), sets up a color attachment in the selected format and layer count, records a render pass instance with per-region counters enabled, renders the full-screen quad, and reads back the counter buffer and color attachment.

Counter verification walks the region grid and computes the expected value for each region based on whether it is complete or partial and on the layer index ([counter verification](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1223-L1275)). For complete regions the minimum and maximum are both `fragment * (layerIdx + 1)`, so the check is exact. Partial regions use a minimum of at least `1` and the same scaled maximum.

Attachment verification checks that every pixel of every layer is blue `(0, 0, 1, 1)` within a `0.01` tolerance ([attachment check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1313-L1344)).

Timestamp verification gathers per-region start and end timestamps from the SSBO and checks that timestamps from different logical devices do not overlap ([timestamp check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1445-L1478)). All failures are collected in a `tcu::ResultCollector` and aggregated into the final pass/fail.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layers_1` leaves | The single-layer counter value per region did not match the expected value `256` for a complete region (or fell outside `[1, 256]` for a partial region), meaning the implementation miscounted fragment warps or wrote the counter to the wrong region. |
| `layers_2` leaves | The two-layer counter value per region did not match the expected value `512` for a complete region (or fell outside `[1, 512]` for a partial region), meaning the per-layer draw routing or scaling was wrong. |
| Attachment check (any leaf) | The color attachment is not blue within tolerance, meaning the render did not cover the framebuffer or the color write was corrupted independent of the counter path. |
| Timestamp overlap check (any leaf) | Device timestamps from different logical devices overlapped, violating the extension's security model for concurrent workloads. |
| Any leaf (common cause) | Counter buffer layout, region stride, alignment, or mapping was wrong, so counter values were read from the wrong offsets. |

### Cause Analysis

#### Counter value outside expected range per region

**Possible failure symptoms:** A region's "Fragment warps" counter differs from the expected exact value for a complete region (256 for layer 0, 512 for layer 1), or falls outside `[1, expectedMax]` for a partial region. The failure is reported per layer via the result collector.

**Possible implementation causes:** The extension requires the implementation to divide the framebuffer into regions of the reported size and write each region's counter values into the capture buffer at the correct stride and alignment. A driver that uses the wrong region size, skips partial regions, or does not scale the counter by the actual fragment work can produce an out-of-range value. The layer-count scaling isolates whether the counter reflects the total fragment work across all layers or only one layer.

#### Counter buffer layout or region mapping wrong

**Possible failure symptoms:** Counter values appear shifted, duplicated, or zeroed across regions in a pattern that does not track framebuffer location.

**Possible implementation causes:** The capture buffer uses `regionAlignment` per region and `rowStrideAlignment` per row, both reported by the implementation. A driver that pads differently from what it reports, or that maps regions in a different order than row-major, produces a shifted layout. Source-level investigation is needed to distinguish a layout bug from a counter-value bug, since both manifest as out-of-range reads.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_ARM_performance_counters_by_region` with the `performanceCountersByRegion` feature enabled ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1537-L1569)).
- `VK_KHR_buffer_device_address`, `VK_EXT_separate_stencil_usage`, and `VK_KHR_get_physical_device_properties2` are always required ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1535-L1538)).
- `VK_KHR_shader_clock` with the `shaderDeviceClock` feature is required for the timestamp SSBO writes ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1555-L1558)).
- The `renderpass2` root requires `VK_KHR_create_renderpass2`; the `dynamic_rendering` root requires `VK_KHR_dynamic_rendering` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1540-L1544)).
- The graphics pipeline library variant requires `VK_KHR_pipeline_library` or `VK_EXT_graphics_pipeline_library` with the `graphicsPipelineLibrary` feature ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1546-L1552)).

### Design-based pruning

- Only `R8G8B8A8_UNORM` is tested because the counter capture is independent of the color format; one common UNORM format is sufficient to produce fragment work.
- Layer counts are limited to 1 and 2 because the layer count's only role is to scale the expected counter range; two values confirm the scaling.
- The counter is fixed to "Fragment warps" because it is a representative fragment-work counter available on the target implementation.

## Key Takeaways

- The test verifies that `VK_ARM_performance_counters_by_region` writes per-region counter values into the capture buffer at the correct layout and matching the expected value for each region.
- The layer count is the behavioral axis: two layers double the expected counter value via per-layer draws with increasing vertex counts.
- Complete and partial regions have different expected minima, because partial regions cover fewer pixels.
- A side-channel timestamp check verifies that device timestamps from different logical devices do not overlap, supporting the extension's concurrent-workload security model.
- See [Failure Meaning](#failure-meaning) for how counter range, buffer layout, and timestamp overlap map to distinct failure symptoms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [`createRenderPassPerformanceCountersByRegionTests`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1610-L1614) | Creates the group and dispatches to `initTests`. |
| Registration loop | [`initTests`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1581-L1606) | Generates the `r8g8b8a8_unorm.layers_{1,2}` leaves. |
| Counter verification | [per-region range check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1223-L1275) | Walks the region grid and checks each counter value against the expected min/max. |
| Attachment verification | [color check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1313-L1344) | Checks every pixel is blue within `0.01` tolerance. |
| Timestamp verification | [timestamp overlap check](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1445-L1478) | Gathers per-region timestamps and checks cross-device non-overlap. |
| Shader generation | [`Programs::init`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1334-L1410) | Emits the vertex, fragment (with `clockRealtimeEXT`), and geometry (for `layers_2`) shaders. |
| Support checks | [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1535-L1569) | Requires the extension, its feature, buffer device address, shader clock, and rendering-type extensions. |
| Vulkan spec: per-region counters | [VK_ARM_performance_counters_by_region.adoc](../../../../vulkan-docs/src/appendices/VK_ARM_performance_counters_by_region.adoc) | Defines per-region performance counter capture, region layout, and the security model. |
