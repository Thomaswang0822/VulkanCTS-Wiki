## Overview

**Core question:** Does `gl_PointSize` clamp an oversized point to the device's advertised maximum point size?

- This page covers `vktDrawPointClampTests.cpp`, which implements the `draw.renderpass.point_size_clamp` test family.
- Its only registered test case, `point_size_clamp_max`, supplies a point size above `pointSizeRange[1]` and checks the rendered extent.
- The test uses a one-row color attachment, a vertex push constant, a point-list draw, image-to-buffer readback, and an exact pixel comparison.
- The source entry points and registration evidence are collected in the [Source Reference Appendix](#source-reference-appendix).

## Background Knowledge

- Vulkan exposes the supported point-size interval through `VkPhysicalDeviceLimits::pointSizeRange`. The upper endpoint limits the rasterized size when a vertex shader writes `gl_PointSize`.
- A render pass writes the color attachment, while the test later copies that image into a host-visible buffer. The comparison therefore checks the complete path from point-size handling through rasterization, attachment writes, and readback.

## Registration Hierarchy

```text
draw.renderpass.point_size_clamp
└── point_size_clamp_max
```

`vktDrawTests.cpp` adds `point_size_clamp` directly to the `renderpass` group. The dispatcher creates a separate `dynamic_rendering` branch, but this family is not added there. The same leaf appears in both the Vulkan and Vulkan SC mustpass files.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case | `point_size_clamp_max` | Exercises the upper point-size limit with one fixed oversized input | [`createDrawPointClampTests`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L393-L400) |
| Point size | `floor(maxPointSizeRange * 2.0)` | Supplies a value intended to exceed `pointSizeRange[1]` | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L105-L114) |
| Render size | `ceil(maxPointSizeRange * 0.5) + 1` by `1` pixel | Provides horizontal space for the clamped point and keeps the vertical extent to one row | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L107-L124) |
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_POINT_LIST` | Makes the draw contain one point primitive | [`makeGraphicsPipeline`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L263-L278) |
| Point position | `x = 2 * (fbWidthSize - 0.25) / fbWidthSize - 1`, `y = 0` | Places the point near the right edge while its center lies on the single framebuffer row | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L120-L124) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Defines the attachment and readback pixel format | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L102-L104), [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L366-L370) |

## Behavior Parameters

The primary behavioral axis is the single registered test case. The source does not generate a broader matrix; the fixed case targets the maximum point-size clamp.

### `point_size_clamp_max`: upper point-size clamp

The test reads the device's maximum point size, doubles it, and floors the result before passing it to the vertex shader through a push constant. The vertex shader assigns that value to `gl_PointSize`. The draw then uses `VK_PRIMITIVE_TOPOLOGY_POINT_LIST`, so the observed coverage depends on the implementation applying the device limit rather than accepting the oversized value unchanged.

## Shader Analysis

The source builds a vertex and fragment program in `createPointSizeClampProgs`. The walkthrough below follows the only registered path and uses the vertex shader as the primary stage because its `gl_PointSize` write establishes the shader-to-rasterizer contract under test.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.point_size_clamp.point_size_clamp_max
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `point_size_clamp_max` | Selects the sole registered case, which requests a point larger than the advertised maximum. |
| `psize = floor(pointSizeRange[1] * 2.0)` | Deliberately exceeds the upper point-size limit and is delivered to the vertex stage through four push-constant bytes. |
| `VK_PRIMITIVE_TOPOLOGY_POINT_LIST`, one vertex | Makes the vertex shader's `gl_PointSize` output control the rasterization of one point primitive. |
| One-row `R8G8B8A8_UNORM` target | Reduces the observed result to horizontal point coverage: black covered pixels replace the green clear color. |

#### Purpose

The shaders request an oversized point and carry a contrasting color to the attachment. The test checks that fixed-function rasterization clamps the vertex shader's `gl_PointSize` to `pointSizeRange[1]` rather than rasterizing the unbounded request.

#### Structural Design

| Stage or interface | Value flow | Role in the check |
|--------------------|------------|-------------------|
| Vertex inputs | Location `0` position; location `1` black color | Supplies the single point's center and distinguishable output color. |
| Vertex push constant | `in_pointSize.psize = floor(pointSizeRange[1] * 2.0)` | Carries the deliberately oversized requested point size. |
| Vertex built-ins | Position -> `gl_Position`; `psize` -> `gl_PointSize` | Establishes point placement and the size value that must be clamped. |
| Location `0` varying | Vertex `out_color` -> fragment `in_color` | Carries black through the graphics pipeline. |
| Fragment output | `in_color` -> location `0` attachment output | Replaces the green clear color wherever the clamped point covers the target. |

#### Shader Code

##### Vertex Shader

```glsl
#version 450
/// Vertex location 0 supplies the single point position as a 32-bit float vector.
layout(location = 0) in vec4 in_position;
/// Vertex location 1 supplies the point color; the host uses R8G8B8A8_UNORM and black.
layout(location = 1) in vec4 in_color;
/// Four vertex-stage push-constant bytes carry floor(pointSizeRange[1] * 2.0).
layout(push_constant) uniform pointSizeBlk {
    float psize;
} in_pointSize;
/// Location 0 transports the point color to the fragment shader.
layout(location = 0) out vec4 out_color;

out gl_PerVertex {
    vec4  gl_Position;
    float gl_PointSize;
};
void main() {
    /// Request the deliberately oversized point; fixed-function rasterization must clamp it.
    gl_PointSize = in_pointSize.psize;
    /// Place the point near the right edge of the one-row framebuffer.
    gl_Position  = in_position;
    /// Forward black so covered samples differ from the green clear color.
    out_color    = in_color;
}
```

##### Fragment Shader

```glsl
#version 450
/// Flat location 0 receives the point color without interpolation.
layout(location = 0) flat in vec4 in_color;
/// Location 0 writes to the R8G8B8A8_UNORM color attachment.
layout(location = 0) out vec4 out_color;
void main()
{
    /// Store black at every fragment covered by the clamped point.
    out_color = in_color;
}
```

#### Additional Info

- The fragment shader stays fixed because this family has one case. It matters as the final shader stage that turns point coverage into black attachment pixels for host comparison.
- The pipeline layout exposes no descriptor sets; its only shader-visible non-vertex-buffer resource is the four-byte vertex-stage push-constant range ([source](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L115-L118), [pipeline layout](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L205-L215)).
- No explicit `ShaderBuildOptions` are attached when the GLSL sources are added, so the walkthrough uses the `SourceCollections` baseline target, SPIR-V 1.0 ([source](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L89-L90)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Registered case | There is no nearby shader variant: the group registers only `point_size_clamp_max` with this shared builder. | [`createDrawPointClampTests`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L393-L400) |
| Device maximum point size | The GLSL declaration and control flow remain fixed, while the host-derived float placed in `in_pointSize.psize` changes with `pointSizeRange[1]`. | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L105-L118) |

#### SPIR-V

##### Vertex Shader

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
; Bound: 30
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %out_color %in_color
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %pointSizeBlk "pointSizeBlk"
               OpMemberName %pointSizeBlk 0 "psize"
               OpName %in_pointSize "in_pointSize"
               OpName %in_position "in_position"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %pointSizeBlk Block
               OpMemberDecorate %pointSizeBlk 0 Offset 0
               OpDecorate %in_position Location 0
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
%pointSizeBlk = OpTypeStruct %float
%_ptr_PushConstant_pointSizeBlk = OpTypePointer PushConstant %pointSizeBlk
%in_pointSize = OpVariable %_ptr_PushConstant_pointSizeBlk PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
%_ptr_Output_float = OpTypePointer Output %float
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_PushConstant_float %in_pointSize %int_0
         %19 = OpLoad %float %18
         %21 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %21 %19
         %24 = OpLoad %v4float %in_position
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
         %29 = OpLoad %v4float %in_color
               OpStore %out_color %29
               OpReturn
               OpFunctionEnd
```

</details>

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
; Bound: 13
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %out_color %in_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %out_color Location 0
               OpDecorate %in_color Flat
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %in_color
               OpStore %out_color %12
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test creates an `R8G8B8A8_UNORM` image and a one-row framebuffer whose width is derived from the device limit. It also creates a host-visible vertex buffer and a host-visible readback buffer.
- It builds a graphics pipeline with the generated vertex and fragment shaders, a push-constant range for one vertex-stage float, and `VK_PRIMITIVE_TOPOLOGY_POINT_LIST`.
- Before drawing, it records a host-write-to-vertex-read memory barrier and transitions the color image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`.
- The command buffer begins a render pass with green as the clear color, binds the pipeline and vertex buffer, pushes `testPointSize`, and draws one vertex. The test then copies the image to the readback buffer and waits for completion.
- The reference image is black except for pixel `(0, 0)`, which is set to green. The host compares the reference and result with `tcu::floatThresholdCompare` using a zero threshold. A mismatch returns `fail`; an exact match returns `pass("Rendering succeeded")`.

The complete draw, synchronization, copyback, and comparison path is in [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L93-L385).

## Failure Meaning

### Failure Cause Mapping

Because this page has one fixed behavioral value, the failure mapping is a direct statement rather than a multi-row matrix.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `point_size_clamp_max` | Incorrect point-size clamping or rasterized coverage; vertex input, push-constant handling, shader compilation, render-pass execution, image copyback, or result comparison errors can also produce the observed mismatch. |

### Cause Analysis

#### Point-size handling and rasterized coverage

**Possible failure symptoms:** The result buffer differs from the reference at one or more pixels. The test expects black point coverage with green at `(0, 0)`; any other value fails the zero-threshold comparison.

**Possible implementation causes:** The implementation may apply the maximum point-size limit incorrectly, rasterize the clamped point with the wrong coverage, or mishandle the oversized `gl_PointSize` value. The source establishes the input and expected coverage, but it does not isolate which pipeline stage caused a mismatch.

#### Command, resource, or comparison path

**Possible failure symptoms:** The same exact pixel mismatch can arise even when point-size rasterization is correct if the vertex buffer, push constant, attachment contents, image-to-buffer copy, host invalidation, or format interpretation is wrong.

**Possible implementation causes:** The inspected test source does not distinguish these causes after the readback. Investigating the test log and the implementation's handling of the relevant Vulkan commands would be required to identify the failing stage.

## Case Pruning

### Requirement-based pruning

`checkSupport` rejects the case when the device does not advertise `largePoints`. Such a device receives `NotSupportedError("Large points not supported")`, so the test does not run and does not report a rendering failure. The support check is at [`checkSupport`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L387-L391).

### Design-based pruning

The source registers one fixed maximum-clamp case. It does not generate point-size, topology, format, or rendering-mode variants. The one-row framebuffer and fixed colors keep the check focused on the horizontal extent and the selected reference pixel.

## Key Takeaways

- `point_size_clamp_max` pushes `floor(pointSizeRange[1] * 2.0)` into the vertex shader, then relies on the implementation to clamp `gl_PointSize`.
- The case runs under `draw.renderpass.point_size_clamp` and is not registered under the dispatcher's `dynamic_rendering` branch.
- A zero-threshold image comparison checks the final attachment contents after draw, copyback, and host readback, so a failure identifies an incorrect result but does not by itself localize the responsible stage.
- Devices without `largePoints` are skipped as unsupported rather than marked as failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Shader construction | [`createPointSizeClampProgs`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L59-L91) | Defines the vertex push constant, `gl_PointSize` assignment, and fragment output. |
| Test execution and comparison | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L93-L385) | Defines limits, resources, pipeline, draw, synchronization, readback, reference image, and pass/fail logic. |
| Support gate and registration | [`checkSupport` and `createDrawPointClampTests`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L387-L400) | Checks `largePoints` and registers the sole test case. |
| Renderpass dispatcher | [`createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L142) | Places `point_size_clamp` under `draw.renderpass`. |
| Vulkan mustpass evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28976) | Lists `dEQP-VK.draw.renderpass.point_size_clamp.point_size_clamp_max`. |
| Vulkan SC mustpass evidence | [`draw.txt`](../../../mustpass/main/vksc-default/draw.txt#L1528) | Lists `dEQP-VKSC.draw.renderpass.point_size_clamp.point_size_clamp_max`. |
| Source declaration | [`vktDrawPointClampTests.hpp`](../../../modules/vulkan/draw/vktDrawPointClampTests.hpp#L35) | Declares the registration factory used by the dispatcher. |
