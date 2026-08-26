## Overview

**Core question:** Does Vulkan preserve the intended pixel values when rendering, clearing, and reading Android Hardware Buffer (AHB) external formats through the external-format-resolve path?

- This page covers `vktDrawAhbExternalFormatResolveTests.cpp`, which implements `draw.renderpass.ahb_external_format_resolve` and is reused by the dispatcher for the supported draw variants.
- Each case allocates a 64x64 AHB and queries its Vulkan format properties. Cases that require external-format testing then import the AHB as a Vulkan image, execute a clear or checkerboard draw, and validate the final bytes through AHB CPU readback or a Vulkan buffer copy.
- If the reported Vulkan format already supports native color- or depth/stencil-attachment use, the case passes before importing or rendering because external-format resolve is not required.
- The same implementation handles the render-pass path and the primary, partial-secondary, and complete-secondary dynamic-rendering paths. The input-attachment family is render-pass-only.

## Background Knowledge

- An AHB external format is identified by Android rather than by a normal Vulkan `VkFormat`. Vulkan uses the `VK_ANDROID_external_format_resolve` machinery and implementation-reported resolve properties to connect that image to a renderable color-attachment format.
- Importing external memory only makes its storage accessible to Vulkan; it does not establish that format conversion or rendered values are correct. Correctness must be established from an observable representation.
- YUV and packed raw formats can have subsampling or byte packing that differs from ordinary RGBA images. CPU validation therefore needs format-aware conversion, including raw decompression and chroma downsampling.
- An input attachment exposes attachment contents to a fragment shader through `subpassLoad` in a subpass where that attachment is declared for input use. Attachment load and store operations determine whether existing contents are retained across separate render-pass executions.

## Registration Hierarchy

```text
draw.renderpass.ahb_external_format_resolve
├── clear
├── draw
└── input_attachment
```

The dispatcher attaches this group under the non-VulkanSC draw registration. In addition to the render-pass path shown above, it is registered under `dynamic_rendering.primary_cmd_buff`, `dynamic_rendering.partial_secondary_cmd_buff`, and `dynamic_rendering.complete_secondary_cmd_buff`; it is absent from both nested-secondary paths. `draw` and `clear` use AHB usage `GPU_FRAMEBUFFER | CPU_READ`; `input_attachment` uses `GPU_FRAMEBUFFER | GPU_SAMPLED` and is omitted for dynamic rendering.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Operation family | `clear`, `draw`, `input_attachment` | Selects whether the test only clears, draws directly to the external image, or reads that image in a later subpass. | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1687-L1771) |
| AHB format | Color/raw AHB formats other than `IMPLEMENTATION_DEFINED`; `draw` and `clear` additionally require a valid CTS texture mapping, while `input_attachment` also registers `AHARDWAREBUFFER_FORMAT_RAW_OPAQUE`. | Changes the external representation, Vulkan resolve format, CPU decoder when applicable, alpha behavior, and comparison tolerance. | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1690-L1765) |
| Render area | `full_render_area`; `partial_render_area_0` through `partial_render_area_9` for `draw` and `input_attachment` | Full cases cover every texel. Partial cases leave the clear value outside an even-aligned random rectangle. | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1672-L1682), [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1710-L1724) |
| Image size | 64x64, one layer | Fixed target dimensions used for allocation and reference generation. | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1659-L1669) |
| Rendering mode | Render pass; dynamic rendering with primary, partial-secondary, or complete-secondary command buffers | Exercises the attachment setup and command-buffer inheritance selected by the shared draw dispatcher. Nested-secondary variants do not register this family. | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L121) |
| Secondary-buffer condition | Clear is registered only for a primary-buffer path or the complete-secondary dynamic-rendering path. | Restricts where clear-only leaves appear; the clear operation itself is recorded in a separate primary command buffer. | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1754-L1765), [`renderToExternalFormat`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L315-L331) |

## Behavior Parameters

The primary behavioral axis is the registered operation family.

### `clear`: Clear-only external-format resolve

The case loads the AHB-backed attachment with a fixed clear color and performs no geometry draw. It reads the resulting AHB representation and compares every decoded component with the clear-color reference. This isolates attachment load/clear, external-format resolve, memory import, and final-byte readback.

### `draw`: Direct checkerboard draw

The case first clears the complete 64x64 target, then draws a full-screen quad over either the complete image or an even-aligned random render area. The fragment shader emits a coordinate-derived checkerboard of black, red, green, and half-intensity blue. For a partial case, pixels outside the render area must retain the clear value, so the comparison checks both render-area coverage and preservation of the previously cleared contents.

### `input_attachment`: External image consumed by a later subpass

After the full-image clear, one render-pass execution draws in subpass 0 and advances through subpass 1 without a consumer draw. A second execution skips the draw in subpass 0, then reads the preserved attachment through `subpassLoad` in subpass 1 and writes a normal Vulkan color image for buffer copyback. For YUV, the reference omits software downsampling when a separate color attachment is the input, but applies the device-reported chroma-location downsampling when the implementation exposes the external image directly as the input attachment. This family is registered only for render-pass variants because dynamic rendering has no subpass equivalent.

## Shader Analysis

The implementation generates a pass-through vertex shader and format-dependent fragment shaders in `initPrograms`. The representative case selects the floating-point base fragment variant for `AHARDWAREBUFFER_FORMAT_B8G8R8A8_UNORM`; because this format has alpha, the black entry uses alpha 0.0 and the other entries use alpha 1.0. The shader indexes four fixed colors with the integer pixel coordinates from `gl_FragCoord`: black, red, green, and half-intensity blue. Input-attachment variants are separate generated shaders and are not part of this direct-draw representative case.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.ahb_external_format_resolve.draw.AHARDWAREBUFFER_FORMAT_B8G8R8A8_UNORM.full_render_area
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `draw` | Selects the direct checkerboard draw path rather than clear-only or input-attachment consumption. |
| `AHARDWAREBUFFER_FORMAT_B8G8R8A8_UNORM` | Selects a color format with alpha and the floating-point resolve attachment type for this walkthrough. |
| `full_render_area` | The full-screen quad is rasterized over the complete 64x64 target, so no outside-area clear-preservation branch is exercised. |

#### Purpose

The shaders produce a deterministic full-screen checkerboard whose four colors are selected from integer fragment coordinates. The vertex stage supplies clip-space positions, while the fragment stage provides the pixel values that the external-format resolve and final readback compare against the generated reference.

#### Structural Design

| Stage | Inputs and operations | Output role |
|-------|-----------------------|-------------|
| Vertex | Read `in_position` at location 0 and construct `vec4(in_position, 0.0f, 1.0f)`. | Write `gl_Position` for the full-screen quad. |
| Fragment | Convert `gl_FragCoord` to `uvec4`; compute `(x & 1) + ((y & 1) << 1)`; index four constant `vec4` colors. | Write the selected color to location 0. |

#### Shader Code

##### Vertex Shader

```glsl
#version 430
layout(location = 0) in vec2 in_position;

/// Pass the quad's 2D clip-space position through to the vertex position.
void main() {
    gl_Position  = vec4(in_position, 0.0f, 1.0f);
}
```

##### Fragment Shader

```glsl
#version 430
layout(location = 0) out vec4 out_color;

/// The selected AHB format has alpha; black is opaque only where the generated
/// reference specifies it, while the other checkerboard entries use alpha 1.
const vec4 reference_colors[] =
{
    vec4(0.0f, 0.0f, 0.0f, 0.0f),
    vec4(1.0f, 0.0f, 0.0f, 1.0f),
    vec4(0.0f, 1.0f, 0.0f, 1.0f),
    vec4(0.0f, 0.0f, 1.0f * 0.5, 1.0f),
};
void main()
{
    /// Integer fragment coordinates select one of the four checkerboard cells.
    uvec4 fragmentPosition = uvec4(gl_FragCoord);
    uint color_index = (fragmentPosition.x & 1u) + ((fragmentPosition.y & 1u) << 1u);
    out_color = reference_colors[color_index];
}
```

#### Additional Info

- The vertex stage is fixed across the operation, format, and render-area variants; it only establishes the full-screen primitive position.
- The direct `draw` path uses the base fragment shader. The separate `frag_input_*` family is generated only when `m_isInputAttachment` is true and is therefore not needed for this selected case.
- The source collection uses its default SPIR-V target because this `initPrograms` path supplies no explicit shader build options; the canonical disassembly below is generated for SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| AHB format | The base fragment shader selects `float`, `int`, or `uint` output according to the implementation-selected resolve color-attachment format; alpha presence changes the first color's alpha initializer. | [`AhbExternalFormatResolveTestCase::initPrograms`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1552-L1587) |
| Operation family | `clear` does not require the draw fragment shader; `draw` uses `frag_vec4`; `input_attachment` adds typed `subpassInput` shaders and RGB/BGR swizzle variants for YUV formats. | [`AhbExternalFormatResolveTestCase::initPrograms`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1590-L1633) |
| Render area | Full and partial cases use the same shader; the render area changes rasterization coverage and therefore which pixels retain the prior clear value. | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1672-L1682) |

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
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpName %_ ""
               OpName %in_position "in_position"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpDecorate %in_position Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
%in_position = OpVariable %_ptr_Input_v2float Input
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpLoad %v2float %in_position
         %22 = OpCompositeExtract %float %19 0
         %23 = OpCompositeExtract %float %19 1
         %24 = OpCompositeConstruct %v4float %22 %23 %float_0 %float_1
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
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
; Bound: 46
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %out_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 430
               OpName %main "main"
               OpName %fragmentPosition "fragmentPosition"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %color_index "color_index"
               OpName %out_color "out_color"
               OpName %indexable "indexable"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %out_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
    %float_0 = OpConstant %float 0
         %33 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_0
    %float_1 = OpConstant %float 1
         %35 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
         %36 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
  %float_0_5 = OpConstant %float 0.5
         %38 = OpConstantComposite %v4float %float_0 %float_0 %float_0_5 %float_1
         %39 = OpConstantComposite %_arr_v4float_uint_4 %33 %35 %36 %38
%_ptr_Function__arr_v4float_uint_4 = OpTypePointer Function %_arr_v4float_uint_4
%_ptr_Function_v4float = OpTypePointer Function %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
%fragmentPosition = OpVariable %_ptr_Function_v4uint Function
%color_index = OpVariable %_ptr_Function_uint Function
  %indexable = OpVariable %_ptr_Function__arr_v4float_uint_4 Function
         %14 = OpLoad %v4float %gl_FragCoord
         %15 = OpConvertFToU %v4uint %14
               OpStore %fragmentPosition %15
         %19 = OpAccessChain %_ptr_Function_uint %fragmentPosition %uint_0
         %20 = OpLoad %uint %19
         %22 = OpBitwiseAnd %uint %20 %uint_1
         %23 = OpAccessChain %_ptr_Function_uint %fragmentPosition %uint_1
         %24 = OpLoad %uint %23
         %25 = OpBitwiseAnd %uint %24 %uint_1
         %26 = OpShiftLeftLogical %uint %25 %uint_1
         %27 = OpIAdd %uint %22 %26
               OpStore %color_index %27
         %40 = OpLoad %uint %color_index
               OpStore %indexable %39
         %44 = OpAccessChain %_ptr_Function_v4float %indexable %40
         %45 = OpLoad %v4float %44
               OpStore %out_color %45
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `iterate` allocates the AHB with one of two usage combinations, checks whether external-format testing is required, and then creates the imported Vulkan image, views, attachment images where `nullColorAttachment` is false, render pass/framebuffer or dynamic-rendering state, descriptors, pipelines, and a four-vertex full-screen quad.
- The command sequence transitions attachments, clears the complete image with attachment load, and submits the clear work before the draw work. Input-attachment cases use one render-pass execution to produce and preserve the pattern and a second execution to consume it as an input attachment, then copy the conventional result image to a host-visible buffer.
- Direct draw and clear cases explicitly invoke the `m_resources` destructor before locking the AHB for `CPU_READ`, then decode the final bytes into a `tcu::TextureLevel`. RAW10 and RAW12 are unpacked through the CTS compressed-texture path; RAW16 is treated as an ordinary UINT16 representation. Because the ordinary data member is not reconstructed before the test instance is later destroyed, the resulting resource-lifetime behavior requires source-level investigation.
- The reference is generated procedurally from the render area and checkerboard colors. For formats without alpha, the expected alpha uses the format's maximum value. YUV references are downsampled according to the device-reported chroma locations when the result is read directly from the AHB or when a null color attachment is used.
- The final comparison is `tcu::intThresholdCompare`. `YCbCr_P010` uses `tcu::UVec4(4)` to accommodate reduced-range implementations; other formats use `tcu::UVec4(1, 0, 1, 0)`. A mismatch returns `fail`; successful comparison returns `pass`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `clear` | AHB image import, attachment clear/load, external-format resolve, format decoding, or final-byte readback mismatch. |
| `draw` | Full-screen shader or render-area coverage, clear preservation outside a partial area, resolve conversion, AHB byte layout, format decoding, or final image comparison mismatch. |
| `input_attachment` | Resolve preservation and attachment loading across the two render-pass executions, input-attachment descriptor/layout, format swizzle or chroma handling, intermediate-image copyback, or final comparison mismatch. |

### Cause Analysis

#### External image property query and import

**Possible failure symptoms:** An unexpected Vulkan error during the AHB property query or image import prevents the case from reaching rendering or comparison. A missing extension/API or failed AHB allocation instead reports the case as unsupported, not as a failed pixel comparison.

**Possible implementation causes:** A failure while querying AHB properties, creating the external image and view, allocating dedicated imported memory, or binding that memory can terminate the case before it produces an image.

#### Attachment clear and resolve

**Possible failure symptoms:** A clear case differs from the clear reference, or a partial draw contains unexpected values outside its render area.

**Possible implementation causes:** Attachment load/clear semantics, resolve attachment selection, image layout transitions, or preservation of the initial clear value may not match the required behavior. The test's two-command submission also makes completion and resource lifetime part of the observable path.

#### Shader, coverage, and format conversion

**Possible failure symptoms:** Checkerboard colors, alpha values, YUV components, packed raw values, or only particular render-area cases differ from the reference.

**Possible implementation causes:** The selected generated shader may write the wrong type or component order; rasterization may cover the wrong pixels; or conversion may mishandle alpha defaults, chroma location, reduced range, or packed raw bytes. The exact layer requiring investigation depends on which format and operation fail.

#### Input-attachment consumption and readback

**Possible failure symptoms:** Direct AHB cases pass but `input_attachment` fails, or the copied conventional Vulkan image differs from the expected checkerboard.

**Possible implementation causes:** The first render-pass execution may not preserve the resolved contents for the second execution's attachment load and input read, the descriptor/layout may be wrong, or the input shader's RGB/BGR handling may not match the selected format. A failure may also be in the result-image transition or host-visible buffer invalidation.

## Case Pruning

### Requirement-based pruning

- The group is excluded from VulkanSC registration. The device must support `VK_ANDROID_external_format_resolve`; an AHB external API instance must be available.
- Dynamic-rendering variants require `VK_KHR_dynamic_rendering`. Input-attachment cases are omitted from dynamic rendering because they require subpasses.
- Cases whose AHB allocation fails are reported as unsupported. Formats whose reported Vulkan format already supports native color- or depth/stencil-attachment use pass early because they do not require external-format resolve.
- Formats without a valid CTS texture mapping are excluded from the CPU-readback `draw` and `clear` families. `input_attachment` uses Vulkan buffer readback and also registers the raw format `AHARDWAREBUFFER_FORMAT_RAW_OPAQUE`; non-color/non-raw formats and `IMPLEMENTATION_DEFINED` remain excluded.

### Design-based pruning

- Partial render areas are generated as even-aligned rectangles so subsampled formats do not depend on undefined reduction values.
- Clear leaves are omitted from the partial-secondary dynamic-rendering path; the complete-secondary path retains them even though the standalone clear operation is recorded in a primary command buffer.
- The target is fixed at 64x64 and one layer because the behavior under test is external-format resolve and representation conversion, not image sizing or array-layer rendering.

## Key Takeaways

- Direct `clear` and `draw` cases validate decoded AHB bytes, while `input_attachment` validates the conventional Vulkan image copied by the consumer pass; neither path is merely a command-success or image-creation check.
- Partial draws are meaningful preservation checks: the complete-image clear establishes known contents, and pixels outside the draw rectangle must remain unchanged.
- The input-attachment family adds a distinct render-pass producer/consumer path and validates the conventional Vulkan image produced from the external attachment.
- Format-aware readback is essential: YUV chroma placement, alpha defaults, reduced-range P010, and RAW10/RAW12 packing are all part of the expected result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test instance and final comparison | [`AhbExternalFormatResolveTestInstance::iterate`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L170-L269) | Allocates, executes, reads back, builds the reference, and returns CTS status. |
| External-format rendering | [`AhbExternalFormatResolveTestInstance::renderToExternalFormat`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L271-L347) | Shows resource setup, clear submission, draw submission, and input-attachment sequencing. |
| Reference generation | [`AhbExternalFormatResolveTestInstance::buildReferenceImage`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L682-L730) | Defines checkerboard, clear preservation, alpha, and YUV reference rules. |
| Support gates | [`AhbExternalFormatResolveTestCase::checkSupport`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1641-L1650) | Defines extension, AHB API, and dynamic-rendering prerequisites. |
| Registration and case matrix | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1652-L1771) | Defines operation groups, formats, render areas, usage flags, and pruning. |
| Dispatcher attachment | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L121) | Places the family in the draw registration and preserves the VulkanSC boundary. |
