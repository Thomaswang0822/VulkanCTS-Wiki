## Overview

**Core question:** Does `VK_KHR_maintenance10` produce the expected single-sample color, depth, or stencil result when a four-sample image is resolved through command, render-pass, or dynamic-rendering operations?

[`vktPipelineMultisampleResolveMaint10Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1) implements the `m10_resolve` test family below `multisample`. It renders deterministic per-sample values, resolves selected image regions, copies the resolved image to host-visible buffers, and compares every checked layer with a host-generated reference.

The split pipeline mustpass files register 2,916 leaves for this family: 1,000 each in `monolithic` and `fast-linked-library`, plus 916 in `shader-object-unlinked-spirv`. The command intermediate node accounts for 832 leaves in each construction root. The render-pass intermediate node has 84 leaves in the first two roots and is absent from the shader-object root; dynamic rendering has 84 leaves in every registered root.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Multisample resolve.** A multisample image retains several samples per pixel; resolve writes one value to a single-sample image. The relevant [command-resolve rules](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) define source and destination image regions, while `VkResolveImageModeInfoKHR` selects the resolve mode for non-stencil and stencil values.
- **Maintenance10 extensions.** The [maintenance10 feature](../../../../vulkan-docs/src/chapters/features.adoc#features-maintenance10) adds command-resolve modes and depth/stencil support, and permits control of sRGB transfer-function behavior. The command rules require `average` for non-integer color and `sample_zero` for integer color when a resolve-mode structure is present.
- **Aspect-specific output.** Color, depth, and stencil use separate image aspects. The source checks device-advertised depth and stencil resolve modes before running an applicable case, then reads each selected aspect back independently.

## Registration Hierarchy

```text
pipeline.monolithic.multisample.m10_resolve
├── resolve_cmd
├── render_pass_resolve
└── dynamic_render_resolve
```

[`createMultisampleResolveMaint10Tests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1586-L1810) creates these direct intermediate nodes. [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7787-L7791) registers the family only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction, and excludes the fragment-shading-rate root. `render_pass_resolve` is pruned for shader-object construction.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Resolve intermediate node | `resolve_cmd`, `render_pass_resolve`, `dynamic_render_resolve` | Selects the API mechanism that performs the resolve. | [method registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1591-L1597) |
| Format class | UNORM, UINT, SINT, SFLOAT, sRGB, depth, stencil, and combined depth/stencil entries | Determines output representation, legal aspects, reference calculation, and comparison tolerance. | [format list](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1599-L1660) |
| Resolve aspect | `color`, `depth`, `stencil`, `depth_stencil` | Selects the attachment usage, shader output, resolve properties, copyback buffer, and reference path. | [aspect registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1662-L1671) |
| Resolve mode | `average`, `sample_zero`, `min`, `max` | Selects the host operation used to calculate the expected value for the selected aspect. | [mode registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1673-L1682) |
| Resolve area | `full`, `full_multilayer`, `full_multilayer_rem`, `full_multilayer_rem_single`, `full_3d`, `region`, `regions_multilayer`, `regions_multilayer_rem` | Selects full, layered, 3D, or subregion source-to-destination mapping. | [area registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1684-L1697) |
| sRGB flags | `no_flags`, `enable_transfer`, `skip_transfer` | Selects default behavior or the maintenance10 transfer-function override for applicable sRGB average resolves. | [flag registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1699-L1707) |
| Construction type | `monolithic`, `fast_linked_library`, `shader_object_unlinked_spirv` | Selects a supported pipeline-construction implementation; shader objects omit render-pass cases. | [dispatcher condition](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7787-L7791) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below `m10_resolve`. Each value selects a different mechanism that must produce the same class of resolved data for its legal parameter combinations.

### resolve_cmd: command-buffer image resolve

This intermediate node records `vkCmdResolveImage2` with one or more `VkImageResolve2` regions and a chained `VkResolveImageModeInfoKHR`. It covers the complete area matrix, including 3D destination slices and subregions. The source uses transfer layouts and explicit barriers before resolving, then copies the destination image to verification buffers.

### render_pass_resolve: render-pass attachment resolve

This intermediate node resolves the multisample attachment through render-pass attachment state. It restricts the matrix to sRGB formats and area forms that fit this path. Shader-object construction cannot use this render-pass path, so registration omits it for that construction type.

### dynamic_render_resolve: dynamic-rendering attachment resolve

This intermediate node supplies the resolve through dynamic-rendering attachment state. It uses the same sRGB-focused scope as the render-pass path, but it remains registered for shader-object construction. The checked result is still a copied single-sample image compared with the host reference.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.multisample.m10_resolve.resolve_cmd.r8_unorm.color.average.full.no_flags
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `resolve_cmd` | The four-sample color image is resolved by `vkCmdResolveImage2`; the shader only populates the multisample source image. |
| `r8_unorm`, `color`, `average` | The fragment output is a normalized `vec4`, and the host reference expects the average of the four per-sample values for each pixel. |
| `full`, `no_flags` | A single 16x16 layer is resolved over the complete image, with no sRGB transfer-function override. The generated index therefore has no layer offset and uses a fixed sample multiplier of 4. |

#### Purpose

The shaders make every multisample value deterministic by loading a distinct `PixelData` record for each fragment sample. This lets the maintenance10 resolve operation—not shader-side filtering—be tested for full-image color averaging.

#### Structural Design

| Stage/phase | Dataflow for this representative case |
|------------|----------------------------------------|
| Vertex | Select one of three vertices forming a full-screen triangle; write `gl_Position`. |
| Fragment coordinates | Convert `gl_FragCoord` to integer pixel coordinates and flatten `(x, y)` into `pixelIndex = y * width + x`. |
| Sample selection | Compute `sampleIndex = pixelIndex * 4 + gl_SampleID`, selecting one record from the host-filled storage buffer for each of the four rasterized samples. |
| Attachment write | Load `colorValue` and write it to `outColor`; the multisample attachment resolve is performed later by the selected API path. |

#### Shader Code

##### Vertex Shader

```glsl
#version 460

/// Three vertices cover the viewport as a full-screen triangle.
const vec4 vertices[] = vec4[](
    vec4(-1.0, -1.0, 0.0, 1.0),
    vec4(-1.0,  3.0, 0.0, 1.0),
    vec4( 3.0, -1.0, 0.0, 1.0)
);

void main (void) {
    /// The draw uses the vertex index directly; no inter-stage data is needed.
    gl_Position = vertices[gl_VertexIndex % 3];
}
```

##### Fragment Shader

```glsl
#version 460

/// The selected r8_unorm color aspect is represented by a floating-point vector output.
layout (location=0) out vec4 outColor;

struct PixelData {
    vec4 colorValue;
    vec4 dsValue; // .x = depth, .y = stencil (as float)
};

/// Host-populated, read-only records contain one color value per pixel and sample.
layout (set=0, binding=0) readonly buffer PixelValuesBlock {
    PixelData values[];
} pixels;

/// The host supplies the two-dimensional image width and height.
layout (push_constant, std430) uniform PushConstantBlock {
    float width;
    float height;
} pc;

void main (void) {
    /// This non-layered representative has no preceding-layer offset.
    const uint prevPixels = 0u;
    /// Flatten the fragment coordinate into the 16x16 host-buffer pixel order.
    const uint pixelIndex = uint(floor(gl_FragCoord.y) * pc.width + floor(gl_FragCoord.x)) + prevPixels;
    /// Four records belong to each pixel; gl_SampleID selects this fragment's record.
    const uint sampleIndex = pixelIndex * 4 + uint(gl_SampleID);
    /// The resolve command, rather than this shader, combines the four samples.
    outColor = pixels.values[sampleIndex].colorValue;
}
```

#### Additional Info

- The exact source generator emits the depth/stencil member and its source comment even though this color-only case does not read `dsValue`; the output type and writes are controlled by `TestParams::getGLSLFragOutType()` and the selected aspects ([`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L378-L420)).
- `PixelValuesBlock` is a storage buffer at set 0/binding 0, while `width` and `height` are push constants. The host fills the records in the same four-sample order used by `sampleIndex` before the draw ([resource setup and draw](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L535-L790)).
- The vertex stage stays structurally fixed for non-layered cases; layered variants add `GL_ARB_shader_viewport_layer_array` and `gl_Layer = gl_InstanceIndex` ([vertex generation](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L380-L395)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Resolve aspect and format class | Color formats select `vec4`, `uvec4`, or `ivec4` output and matching `PixelData.colorValue` type; depth/stencil-only cases omit the color output and write built-ins instead. | [`getGLSLFragOutType` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L141-L155) (../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L396-L419) |
| Layered resolve area | Multi-slice areas add the viewport-layer extension, assign `gl_Layer`, and add `uint(pc.width * pc.height) * uint(gl_Layer)` to `prevPixels`. | [`isMultiSlice` and shader generation](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L61-L76) (../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L382-L415) |
| Sample count | The generator embeds `m_params.getSampleCount()` in the `sampleIndex` multiplier; this family fixes it at four samples. | [`getSampleCount` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L136-L139) (../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L414-L415) |
| Resolve method, mode, and sRGB flags | These parameters change the host-side resolve operation, attachment/command setup, or `VkResolveImageModeInfoKHR`; they do not change this representative shader's indexing algorithm. | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L85-L155) and [`iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L535-L1581) |

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
; Bound: 38
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %gl_VertexIndex
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %indexable "indexable"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
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
     %uint_3 = OpConstant %uint 3
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
   %float_n1 = OpConstant %float -1
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %21 = OpConstantComposite %v4float %float_n1 %float_n1 %float_0 %float_1
    %float_3 = OpConstant %float 3
         %23 = OpConstantComposite %v4float %float_n1 %float_3 %float_0 %float_1
         %24 = OpConstantComposite %v4float %float_3 %float_n1 %float_0 %float_1
         %25 = OpConstantComposite %_arr_v4float_uint_3 %21 %23 %24
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_3 = OpConstant %int 3
%_ptr_Function__arr_v4float_uint_3 = OpTypePointer Function %_arr_v4float_uint_3
%_ptr_Function_v4float = OpTypePointer Function %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
  %indexable = OpVariable %_ptr_Function__arr_v4float_uint_3 Function
         %28 = OpLoad %int %gl_VertexIndex
         %30 = OpSMod %int %28 %int_3
               OpStore %indexable %25
         %34 = OpAccessChain %_ptr_Function_v4float %indexable %30
         %35 = OpLoad %v4float %34
         %37 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %37 %35
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
; Bound: 54
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %gl_SampleID %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %pixelIndex "pixelIndex"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "width"
               OpMemberName %PushConstantBlock 1 "height"
               OpName %pc "pc"
               OpName %sampleIndex "sampleIndex"
               OpName %gl_SampleID "gl_SampleID"
               OpName %outColor "outColor"
               OpName %PixelData "PixelData"
               OpMemberName %PixelData 0 "colorValue"
               OpMemberName %PixelData 1 "dsValue"
               OpName %PixelValuesBlock "PixelValuesBlock"
               OpMemberName %PixelValuesBlock 0 "values"
               OpName %pixels "pixels"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpDecorate %gl_SampleID BuiltIn SampleId
               OpDecorate %gl_SampleID Flat
               OpDecorate %outColor Location 0
               OpMemberDecorate %PixelData 0 Offset 0
               OpMemberDecorate %PixelData 1 Offset 16
               OpDecorate %_runtimearr_PixelData ArrayStride 32
               OpDecorate %PixelValuesBlock BufferBlock
               OpMemberDecorate %PixelValuesBlock 0 NonWritable
               OpMemberDecorate %PixelValuesBlock 0 Offset 0
               OpDecorate %pixels NonWritable
               OpDecorate %pixels Binding 0
               OpDecorate %pixels DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_float = OpTypePointer Input %float
%PushConstantBlock = OpTypeStruct %float %float
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
     %uint_0 = OpConstant %uint 0
     %uint_4 = OpConstant %uint 4
%_ptr_Input_int = OpTypePointer Input %int
%gl_SampleID = OpVariable %_ptr_Input_int Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
  %PixelData = OpTypeStruct %v4float %v4float
%_runtimearr_PixelData = OpTypeRuntimeArray %PixelData
%PixelValuesBlock = OpTypeStruct %_runtimearr_PixelData
%_ptr_Uniform_PixelValuesBlock = OpTypePointer Uniform %PixelValuesBlock
     %pixels = OpVariable %_ptr_Uniform_PixelValuesBlock Uniform
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
 %pixelIndex = OpVariable %_ptr_Function_uint Function
%sampleIndex = OpVariable %_ptr_Function_uint Function
         %15 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %16 = OpLoad %float %15
         %17 = OpExtInst %float %1 Floor %16
         %24 = OpAccessChain %_ptr_PushConstant_float %pc %int_0
         %25 = OpLoad %float %24
         %26 = OpFMul %float %17 %25
         %28 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %29 = OpLoad %float %28
         %30 = OpExtInst %float %1 Floor %29
         %31 = OpFAdd %float %26 %30
         %32 = OpConvertFToU %uint %31
         %33 = OpIAdd %uint %32 %uint_0
               OpStore %pixelIndex %33
         %35 = OpLoad %uint %pixelIndex
         %37 = OpIMul %uint %35 %uint_4
         %40 = OpLoad %int %gl_SampleID
         %41 = OpBitcast %uint %40
         %42 = OpIAdd %uint %37 %41
               OpStore %sampleIndex %42
         %50 = OpLoad %uint %sampleIndex
         %52 = OpAccessChain %_ptr_Uniform_v4float %pixels %int_0 %50 %int_0
         %53 = OpLoad %v4float %52
               OpStore %outColor %53
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host checks `VK_KHR_maintenance10`, the method-specific extension, pipeline-construction support, image format support, and depth/stencil resolve properties. Layered paths require Vulkan 1.2 plus `shaderOutputLayer`; sRGB transfer flags require the device property `resolveSrgbFormatSupportsTransferFunctionControl`.
- CTS creates a four-sample 2D source image and a single-sample destination image. A `full_3d` case changes the destination to a 3D image. It fills a host-visible storage buffer with deterministic random per-sample `PixelData`, flushes it, and draws into the multisample attachment.
- The selected area builds one or more `ResolveRegion` mappings. Full-area cases may use explicit layer counts or `VK_REMAINING_ARRAY_LAYERS`; regional command cases move quadrants within or across layers.
- For `resolve_cmd`, CTS transitions the images, builds `VkImageResolve2` entries, chains `VkResolveImageModeInfoKHR`, and calls `vkCmdResolveImage2`. The render-pass and dynamic-rendering paths resolve through their attachment configuration.
- CTS transitions the resolved image to transfer source, copies color, depth, and stencil aspects to separate verification buffers, waits for submission completion, and invalidates host allocations.
- The host reference maps each destination pixel through the first matching resolve region. It selects sample zero, minimum, maximum, or an average as appropriate. It compares integer color and stencil exactly, floating-point color with a format-derived threshold, and depth with a format-specific threshold.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `resolve_cmd` | `vkCmdResolveImage2` region, mode, aspect, layout, or sRGB control is mishandled; source or destination image state may also be wrong. |
| `render_pass_resolve` | Render-pass attachment resolve state or its integration with maintenance10 mode and sRGB control is mishandled. |
| `dynamic_render_resolve` | Dynamic-rendering resolve attachment state or its integration with maintenance10 mode and sRGB control is mishandled. |

### Cause Analysis

#### Command resolve state or region mapping

**Possible failure symptoms:** `resolve_cmd` leaves show mismatches in covered pixels, layers, or moved quadrants, while pixels outside a selected region should retain the zero reference. A mismatch can be limited to `full_3d`, `VK_REMAINING_ARRAY_LAYERS`, or one aspect.

**Possible implementation causes:** The implementation may apply `VkImageResolve2` offsets, extents, base layers, layer counts, image layouts, or resolve modes incorrectly. The final image also includes multisample attachment writes, barriers, the command resolve, copyback, and host comparison, so one mismatch does not identify an exclusive failing stage.

#### Attachment resolve integration

**Possible failure symptoms:** `render_pass_resolve` or `dynamic_render_resolve` differs from the reference for an sRGB leaf, or only one attachment-based mechanism fails while command resolve passes.

**Possible implementation causes:** Render-pass or dynamic-rendering attachment resolve configuration may select the wrong resolve image, mode, aspect, or layout. The source-generated data and final copyback remain shared dependencies, so the result localizes the operation shape rather than proving that attachment resolve alone caused the error.

#### sRGB transfer-function or numerical result

**Possible failure symptoms:** A mismatch is confined to `enable_transfer` or `skip_transfer`, or it occurs only for averaged sRGB or floating-point color. Exact integer color and stencil cases can pass while tolerant color cases fail.

**Possible implementation causes:** The implementation may ignore the maintenance10 transfer flags, use the wrong default from `resolveSrgbFormatAppliesTransferFunction`, convert at the wrong point in averaging, or produce a value beyond the format-derived tolerance. The [resolve rules](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) permit implementation-defined numerical precision for calculations over multiple samples, which is why CTS uses format-aware thresholds.

## Case Pruning

### Requirement-based pruning

The source reports not supported when `VK_KHR_maintenance10`, the method-specific extension, format support, sample count, or required depth/stencil resolve modes are unavailable. Depth/stencil cases require `VK_KHR_depth_stencil_resolve`; stencil cases also require `VK_EXT_shader_stencil_export`. A selected sRGB transfer flag requires `resolveSrgbFormatSupportsTransferFunctionControl`. Layered cases require Vulkan 1.2 and `shaderOutputLayer`.

### Design-based pruning

The registration loop rejects aspect and format pairs that do not match, such as color resolve for a depth/stencil format. Integer color retains only `sample_zero`, while floating-point and normalized color retains `average`. Stencil excludes `average`. `full_3d`, `region`, and multi-region areas only apply to `resolve_cmd`; render-pass and dynamic-rendering paths retain sRGB formats because they concentrate on the new transfer flags. `render_pass_resolve` is omitted for shader-object construction.

## Key Takeaways

- `m10_resolve` compares resolved image data with a host model that includes region routing, aspect semantics, resolve mode, and sRGB transfer handling.
- `resolve_cmd` covers the broadest geometry matrix; render-pass and dynamic-rendering paths focus on sRGB transfer-flag behavior.
- The final readback exposes incorrect results, but the shared draw, synchronization, resolve, copyback, and reference path limit fault localization. See [Failure Meaning](#failure-meaning) for operation-shape-specific causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L51-L226) | Defines image shape, sample count, aspects, and image uses. |
| Support checks | [`Maint10ResolveCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L273-L390) | Checks extension, property, format, layered-rendering, and resolve-mode requirements. |
| Shader generation | [`Maint10ResolveCase::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L392-L418) | Generates per-sample color, depth, and stencil writes. |
| Execution and readback | [`Maint10ResolveInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L535-L1581) | Creates resources, resolves images, generates references, and compares results. |
| Matrix registration | [`createMultisampleResolveMaint10Tests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1586-L1810) | Creates methods, formats, aspects, modes, areas, and sRGB flags. |
| Parent registration | [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7787-L7791) | Limits supported construction types and fragment-shading-rate use. |
| Maintenance10 contract | [Maintenance10 feature](../../../../vulkan-docs/src/chapters/features.adoc#features-maintenance10) | Defines the feature's resolve additions. |
| Resolve command contract | [Resolve image commands](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) | Defines `VkResolveImageInfo2`, modes, aspects, sRGB control, and valid usage. |
