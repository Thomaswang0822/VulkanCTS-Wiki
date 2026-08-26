## Overview

**Core question:** Can a render pass sample one aspect of a combined depth/stencil image in its fragment shader while framebuffer operations write the other aspect?

- [`vktImageDepthStencilSeparateTests.cpp`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp) implements `image.depth_stencil_separate_access`.
- Each leaf draws 256 one-pixel points into a 16 x 16 framebuffer. It samples the read-only depth or stencil aspect at the same pixel and writes that sampled value to a storage image.
- The other aspect receives a clear, `DONT_CARE`, test-and-store, or multisample test-and-resolve attachment operation.

## Background Knowledge

For the shared concepts image views, aspects, layouts, and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Aspect-specific views.** A combined depth/stencil format contains depth and stencil aspects. The test attaches a view containing both aspects and samples a second view whose subresource range contains only the aspect that the attachment must preserve.
- **Concurrent framebuffer and shader access.** The property `separateDepthStencilAttachmentAccess` supports the arrangement under test: fragment sampling accesses one aspect while attachment operations access the other. The fragment shader copies the sampled texel into a typed storage image for host observation.
- **Combined and separate layouts.** Ordinary leaves use `VK_IMAGE_LAYOUT_GENERAL`, `VK_IMAGE_LAYOUT_DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL`, or `VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL`. Separate-layout leaves give depth and stencil independently selected attachment/read-only layouts through render-pass-2 depth/stencil-layout structures.

## Registration Hierarchy

```text
image.depth_stencil_separate_access
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
└── d32_sfloat_s8_uint
```

Every format group receives the same write-aspect and mechanism matrix. The factory appends `_general_layout`, `_separate_layouts`, and, for eligible stencil-test leaves, `_dynamic_stencil_ref` suffixes. [`createImageDepthStencilSeparateTests()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1415-L1485) registers the hierarchy.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Effect |
|-----------|-------------------|--------|
| Depth/stencil format | `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint` | Selects depth precision and the combined depth/stencil attachment format. |
| Write aspect | `write_depth`, `write_stencil` | Selects the framebuffer-written aspect. The other aspect becomes the fragment-sampled aspect. |
| Write mechanism | `render_pass_clears`, `render_pass_dont_care`, `test_and_store`, `test_and_resolve` | Selects attachment load/store behavior or fragment-test and resolve behavior. |
| Layout mode | default combined layout, `_general_layout`, `_separate_layouts` | Selects combined access-specific layout, `GENERAL`, or individual depth/stencil layouts. |
| Stencil-reference mode | ordinary dynamic command state, `_dynamic_stencil_ref` | Selects host-set per-point stencil reference or fragment-shader export. The suffix exists only for stencil test/resolve cases. |

## Behavior Parameters

The primary behavioral axis is **write mechanism**. It changes the way the attachment updates the selected aspect while the same render pass samples the other aspect.

| Value | Attachment behavior | Defined attachment result checked by host? |
|-------|---------------------|--------------------------------------------|
| `render_pass_clears` | The selected aspect uses `VK_ATTACHMENT_LOAD_OP_CLEAR` and `STORE`. | Yes. The expected selected aspect is zero. |
| `render_pass_dont_care` | The selected aspect uses `DONT_CARE` for load and store. | No. `DONT_CARE` leaves its resulting contents undefined. |
| `test_and_store` | The selected aspect loads, then an always-passing depth or stencil test writes it and stores the result. | Yes. The expected selected aspect is the generated per-pixel value. |
| `test_and_resolve` | A four-sample attachment runs the selected test and resolves into the single-sample depth/stencil image with `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT`. | Yes. The expected resolved selected aspect is the generated per-pixel value. |

### `render_pass_clears`: clear the written aspect

The render pass clears the selected write aspect and stores it, while the fragment shader samples the opposite aspect. The host expects zero in the defined written aspect and the prefilled values in the sampled-aspect storage image.

### `render_pass_dont_care`: leave the written result undefined

The selected write aspect uses `DONT_CARE` load and store operations while the opposite aspect remains readable through `LOAD` and `STORE`. The host checks color and the sampled-aspect storage image but deliberately does not compare the written aspect.

### `test_and_store`: test and retain the generated value

An always-passing depth or stencil test writes the selected aspect and stores the generated per-pixel value. The other aspect remains read-only to the attachment and is copied by the fragment shader into its storage image.

### `test_and_resolve`: test with four samples, then resolve

The selected aspect is written in a four-sample attachment and resolved into the single-sample depth/stencil image using `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT`. The resolved image provides both the sampled opposite aspect and the defined written result for readback.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.depth_stencil_separate_access.d24_unorm_s8_uint.write_depth_test_and_store_separate_layouts
```

| Parameter choice | Meaning in this representative case |
|---|---|
| Format: `VK_FORMAT_D24_UNORM_S8_UINT` | The attachment has 24-bit normalized depth and 8-bit unsigned stencil. |
| Write aspect: depth | Depth test/write is enabled; stencil test/write is disabled. |
| Mechanism: `test_and_store` | Depth uses `LOAD` and `STORE`; generated point depth passes `VK_COMPARE_OP_ALWAYS`. |
| Layout mode: `separate_layouts` | Depth uses `DEPTH_ATTACHMENT_OPTIMAL`; stencil uses `STENCIL_READ_ONLY_OPTIMAL`. |
| Sampled aspect: stencil | Binding 0 is a `usampler2D` view with `VK_IMAGE_ASPECT_STENCIL_BIT`. |
| Storage result: `R32_UINT` | Binding 1 records the sampled unsigned stencil value. |

#### Purpose

This walkthrough isolates the shader behavior exercised by the selected representative case.

#### Structural Design

- Vertex stage transports point position, color, and the auxiliary stencil-reference value.
- Fragment stage writes color, samples the read-only stencil aspect, and stores it to the R32_UINT image.
- Fixed-function depth testing writes the selected depth aspect while the shader observes the opposite aspect.

#### Shader Code

[`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) emits these common vertex operations and the selected stencil-read fragment path.

##### Vertex Shader

```glsl
// Vertex shader: one input point represents one framebuffer pixel.
#version 460
layout (location=0) in vec4 inPos;
layout (location=1) in vec4 inColor;
layout (location=2) in ivec4 inExtra;

layout (location=0) out vec4 outColor;
layout (location=1) out flat ivec4 outExtra;

void main (void)
{
    gl_Position  = inPos;
    gl_PointSize = 1.0;
    outColor = inColor;
    outExtra = inExtra;
}
```

##### Fragment Shader

```glsl
// Fragment shader generated when the sampled aspect is stencil.
#version 460
layout (location=0) in vec4 inColor;
layout (location=1) in flat ivec4 inExtra;
layout (location=0) out vec4 outColor;

layout (set=0, binding=0) uniform usampler2D stencilSampler;
layout (r32ui, set=0, binding=1) uniform uimage2D stencilCopy;

void main (void)
{
    outColor = inColor;
    const ivec2 texCoords = ivec2(gl_FragCoord.xy);
    imageStore(stencilCopy, texCoords, texelFetch(stencilSampler, texCoords, 0));
}
```

The depth/stencil pipeline state enables depth test and depth write for this leaf, with `VK_COMPARE_OP_ALWAYS`. The host prefills depth with zero for a writable depth test, so every generated point depth in `[0.5, 1.0)` passes. It prefills stencil from each vertex and uses `LOAD`/`STORE` for that read-only aspect. The shader's unsigned fetch must therefore reproduce each prefilled stencil value.

#### Additional Info

- ``write_depth``: Fragment shader uses `usampler2D` and `r32ui uimage2D` to fetch/store stencil. The pipeline enables depth test/write.
- ``write_stencil``: Fragment shader uses `sampler2D` and `r32f image2D` to fetch/store depth. The pipeline enables stencil test/write with `REPLACE` on pass.
- ``_dynamic_stencil_ref``: Fragment shader enables `GL_ARB_shader_stencil_export` and assigns `gl_FragStencilRefARB = inExtra.x`.
- `Ordinary stencil test leaves`: The host uses `cmdSetStencilReference` before a one-point draw for every generated vertex.
- `Clear or `DONT_CARE` leaves`: Neither depth nor stencil fragment test writes through pipeline state. The fragment shader still samples and stores the opposite aspect.
- `Resolve leaves`: The graphics pipeline uses four samples. A render-pass-2 depth/stencil resolve attachment receives sample-zero resolve results.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| ``write_depth`` | Fragment shader uses `usampler2D` and `r32ui uimage2D` to fetch/store stencil. The pipeline enables depth test/write. | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) |
| ``write_stencil`` | Fragment shader uses `sampler2D` and `r32f image2D` to fetch/store depth. The pipeline enables stencil test/write with `REPLACE` on pass. | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) |
| ``_dynamic_stencil_ref`` | Fragment shader enables `GL_ARB_shader_stencil_export` and assigns `gl_FragStencilRefARB = inExtra.x`. | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) |
| `Ordinary stencil test leaves` | The host uses `cmdSetStencilReference` before a one-point draw for every generated vertex. | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) |
| `Clear or `DONT_CARE` leaves` | Neither depth nor stencil fragment test writes through pipeline state. The fragment shader still samples and stores the opposite aspect. | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) |
| `Resolve leaves` | The graphics pipeline uses four samples. A render-pass-2 depth/stencil resolve attachment receives sample-zero resolve results. | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) |

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
; Bound: 34
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos %outColor %inColor %outExtra %inExtra
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpName %outExtra "outExtra"
               OpName %inExtra "inExtra"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 1
               OpDecorate %outExtra Flat
               OpDecorate %outExtra Location 1
               OpDecorate %inExtra Location 2
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
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %inColor = OpVariable %_ptr_Input_v4float Input
      %v4int = OpTypeVector %int 4
%_ptr_Output_v4int = OpTypePointer Output %v4int
   %outExtra = OpVariable %_ptr_Output_v4int Output
%_ptr_Input_v4int = OpTypePointer Input %v4int
    %inExtra = OpVariable %_ptr_Input_v4int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPos
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %24 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %24 %float_1
         %27 = OpLoad %v4float %inColor
               OpStore %outColor %27
         %33 = OpLoad %v4int %inExtra
               OpStore %outExtra %33
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
; Bound: 41
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %inColor %gl_FragCoord %inExtra
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpName %texCoords "texCoords"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %stencilCopy "stencilCopy"
               OpName %stencilSampler "stencilSampler"
               OpName %inExtra "inExtra"
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 0
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %stencilCopy Binding 1
               OpDecorate %stencilCopy DescriptorSet 0
               OpDecorate %stencilSampler Binding 0
               OpDecorate %stencilSampler DescriptorSet 0
               OpDecorate %inExtra Flat
               OpDecorate %inExtra Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %inColor = OpVariable %_ptr_Input_v4float Input
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
    %v2float = OpTypeVector %float 2
       %uint = OpTypeInt 32 0
         %23 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_23 = OpTypePointer UniformConstant %23
%stencilCopy = OpVariable %_ptr_UniformConstant_23 UniformConstant
         %28 = OpTypeImage %uint 2D 0 0 0 1 Unknown
         %29 = OpTypeSampledImage %28
%_ptr_UniformConstant_29 = OpTypePointer UniformConstant %29
%stencilSampler = OpVariable %_ptr_UniformConstant_29 UniformConstant
      %int_0 = OpConstant %int 0
     %v4uint = OpTypeVector %uint 4
      %v4int = OpTypeVector %int 4
%_ptr_Input_v4int = OpTypePointer Input %v4int
    %inExtra = OpVariable %_ptr_Input_v4int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
  %texCoords = OpVariable %_ptr_Function_v2int Function
         %12 = OpLoad %v4float %inColor
               OpStore %outColor %12
         %19 = OpLoad %v4float %gl_FragCoord
         %20 = OpVectorShuffle %v2float %19 %19 0 1
         %21 = OpConvertFToS %v2int %20
               OpStore %texCoords %21
         %26 = OpLoad %23 %stencilCopy
         %27 = OpLoad %v2int %texCoords
         %32 = OpLoad %29 %stencilSampler
         %33 = OpLoad %v2int %texCoords
         %35 = OpImage %28 %32
         %37 = OpImageFetch %v4uint %35 %33 Lod %int_0
               OpImageWrite %26 %27 %37
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Resource setup and prefill

The test creates a 16 x 16 single-sample depth/stencil image with attachment and sampled usage. Non-resolve leaves also give it transfer source/destination usage. A full image view serves as the depth/stencil attachment, while a depth-only or stencil-only view serves binding 0. The test creates an `R32_SFLOAT` storage image when sampling depth and an `R32_UINT` storage image when sampling stencil.

The host generates 256 vertices, one at the center of each pixel. Each vertex includes pseudorandom color, depth in `[0.5, 1.0)`, and stencil reference in `[1, 255]`. It copies generated depth and stencil planes from separate host-visible buffers into their corresponding aspects before rendering.

For `test_and_resolve`, the test also creates four-sample color and depth/stencil attachments. The single-sample images remain the resolve targets and the source sampled by the fragment shader.

### Layout transitions and draw

Before the render pass, the test transitions the depth/stencil image from transfer-destination or general layout into the selected layout mode:

- Combined leaves transition both aspects together to the ordinary access-specific layout or `GENERAL`.
- Separate-layout leaves submit one barrier for depth and one for stencil, each with its own final layout and access/stage masks.
- Resolve leaves prepare the multisample attachment as well as the prefilled single-sample resolve target.

[`makeSeparateRenderPass()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L558-L797) assigns `LOAD` and `STORE` to the read-only aspect. It assigns the selected clear, `DONT_CARE`, or load/store mechanism to the written aspect. The command buffer binds the graphics pipeline and descriptors, then draws all 256 points at once except ordinary stencil-test leaves, which set a distinct dynamic reference and draw one point at a time.

### Readback and reference images

After rendering, barriers make color-attachment, fragment-storage, and depth/stencil writes available to transfer commands. The test copies:

1. color attachment to its readback buffer;
2. storage image to its readback buffer;
3. depth aspect to a depth verification buffer; and
4. stencil aspect to a stencil verification buffer.

The host builds four reference images from the same vertex data. For a clear of the written depth or stencil aspect it expects zero. For other defined writes it expects the generated per-pixel depth or stencil value. The sampled-aspect storage reference always contains its original generated data, because that aspect used `LOAD` and `STORE`.

| Result | Comparison | Pass rule |
|--------|------------|-----------|
| Color | `floatThresholdCompare` | Each generated RGBA color must match within `0.005`. |
| Sampled depth storage | `floatThresholdCompare` | Each sampled depth must match within the format-specific threshold. |
| Sampled stencil storage | `intThresholdCompare` | Each sampled stencil value must match exactly. |
| Written depth/stencil attachment | `dsThresholdCompare` | Compare only when it is not the sampled aspect and its mechanism defines stored contents. |

Depth thresholds are `1.5 / 65535` for D16, `1.5 / 16777215` for D24, and `1.0 / 33554431` for D32. The stencil threshold is zero.

### Support requirements

| Requirement | Reason |
|-------------|--------|
| `VK_KHR_get_physical_device_properties2` | Queries the Maintenance7 property path. |
| `VK_KHR_maintenance7` | Provides the separate depth/stencil attachment-access capability under test. |
| `VK_KHR_format_feature_flags2` | Provides the format-feature query path. |
| `separateDepthStencilAttachmentAccess` | Must be true on non-Vulkan-SC builds. |
| Image-format properties and sample count | The selected format must support the requested single-sample or four-sample image usage. |
| Depth/stencil attachment, sampled image, transfer source, and transfer destination format features | Required on non-Vulkan-SC builds for the selected combined format. |
| `VK_EXT_shader_stencil_export` | Required for `_dynamic_stencil_ref` leaves. |
| `VK_KHR_depth_stencil_resolve` | Required for `test_and_resolve` leaves. |
| `VK_KHR_separate_depth_stencil_layouts` | Required for `_separate_layouts` leaves. |

Unsupported prerequisites raise `NotSupportedError`; an executed leaf has passed its support checks.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `render_pass_clears` | Depth/stencil attachment clearing, preservation and sampling of the opposite aspect, or readback synchronization. |
| `render_pass_dont_care` | Access to the preserved sampled aspect, the `DONT_CARE` attachment path, or color/storage readback. The test does not diagnose a resulting value for the written aspect. |
| `test_and_store` | Depth/stencil test and write behavior, sampled opposite-aspect preservation, dynamic state/reference handling, or result comparison. |
| `test_and_resolve` | Multisample attachment access, sample-zero depth/stencil resolve, sampled resolve-target aspect preservation, or result readback. |

### Cause Analysis

#### Attachment operation, aspect preservation, and readback

**Possible failure symptoms:** Clear and `DONT_CARE` leaves can report a color or sampled-aspect storage mismatch; clear leaves can also report a mismatch in the defined written aspect.

**Possible implementation causes:** The render pass may apply the selected depth/stencil load or store operation to the wrong aspect, fail to preserve the opposite `LOAD`/`STORE` aspect during fragment sampling, or fail to make color or storage writes available before readback.

#### Depth/stencil test, reference, and storage path

**Possible failure symptoms:** `test_and_store` leaves can mismatch in the written depth or stencil verification image, or in the storage image that captures the opposite aspect.

**Possible implementation causes:** Depth/stencil test state, per-point stencil-reference state, shader stencil export, aspect-only image views, or the result-comparison path may use the wrong generated value or aspect.

#### Multisample resolve path

**Possible failure symptoms:** `test_and_resolve` leaves can mismatch in the resolved written aspect or the storage image sampled from the resolve target.

**Possible implementation causes:** The four-sample attachment, render-pass-2 depth/stencil resolve attachment, or `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` result may not preserve the expected selected aspect before readback.

#### Failure clusters by variant

**Possible failure symptoms:** A cluster limited to one write aspect, layout mode, or dynamic-reference variant narrows the mismatch to that variant's color, storage, or depth/stencil readback.

**Possible implementation causes:** `write_depth` clusters point to depth attachment access or the stencil-only view; `write_stencil` clusters point to stencil operations, reference values, or the depth-only view. `_separate_layouts` clusters point to per-aspect barriers and depth/stencil-layout structures; dynamic-reference clusters also cover shader stencil export.

## Case Pruning

### Requirement-based pruning

- A dynamic stencil-reference suffix is registered only when the test writes stencil through `test_and_store` or `test_and_resolve`, and those leaves require `VK_EXT_shader_stencil_export`.
- `test_and_resolve` leaves require `VK_KHR_depth_stencil_resolve`; `_separate_layouts` leaves require `VK_KHR_separate_depth_stencil_layouts`. Unsupported prerequisites report `NotSupportedError` before execution.

### Design-based pruning

- The factory excludes the meaningless combination of `_general_layout` with `_separate_layouts`.
- The factory excludes `_separate_layouts` for resolve leaves to bound the matrix.

## Key Takeaways

- One combined image supplies both the framebuffer attachment and an aspect-only sampled view.
- The generated storage image observes the aspect the render pass must leave readable and preserved.
- Clear, `DONT_CARE`, test/store, and test/resolve paths isolate different depth/stencil attachment operations.
- Layout and stencil-reference variants extend the same core access pattern without changing the validation contract.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters | [`TestParams`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L83-L185) | Chooses read/write aspect, layouts, sample count, and storage result format. |
| Support checks | [`DepthStencilSeparateCase::checkSupport()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L316-L399) | Validates functionality, property, formats, sample counts, and selected extensions. |
| Generated shaders | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) | Builds the vertex path and depth/stencil sampling fragment variants. |
| Render-pass construction | [`makeSeparateRenderPass()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L558-L797) | Selects load/store operations, layouts, and resolve configuration. |
| Execution and checking | [`DepthStencilSeparateInstance::iterate()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L833-L1411) | Creates resources, records transitions/draws/copies, and compares output buffers. |
| Registration factory | [`createImageDepthStencilSeparateTests()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1415-L1485) | Generates formats, mechanism/layout/reference variants, and pruning rules. |
