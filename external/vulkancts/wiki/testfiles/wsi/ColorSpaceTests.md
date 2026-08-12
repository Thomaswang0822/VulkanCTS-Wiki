## Overview

**Core question:** Can every advertised surface color-space choice be used without changing the raw rendered pixel value for a fixed image format?

- This page covers the `colorspace` and `colorspace_compare` test families implemented by [vktWsiColorSpaceTests.cpp](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp).
- `colorspace` checks extension advertisement, renders with each queried surface format and color-space pair, and repeats the rendering path with HDR metadata.
- `colorspace_compare` fixes one of six image formats, creates a swapchain for each supported color space, and compares pixel `(128, 128)` exactly across the resulting images. The current source [performs each readback after presenting the image without reacquiring it](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L530-L545), contrary to the [presentable-image reacquisition rule](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7419-L7426), so this comparison cannot serve as a conformance oracle as implemented.
- The source owns both families because they share instance, device, swapchain, renderer, presentation, and readback setup. The WSI dispatcher registers them separately under each platform type.

## Background Knowledge

For the shared concepts surface queries and swapchain presentation, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- A `VkSurfaceFormatKHR` pairs a `VkFormat` with a `VkColorSpaceKHR`. The format controls stored component representation. The color space tells the presentation system how to interpret those values.
- `VK_EXT_swapchain_colorspace` adds color-space choices beyond `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR`. The test enables the extension when the implementation advertises it before using those choices in `VkSwapchainCreateInfoKHR`.
- HDR metadata describes display primaries and luminance ranges for presentation. It does not add a shader resource or rewrite the shader output.

## Registration Hierarchy

The same two families are registered under each WSI platform type. `headless` is the representative platform below.

```text
wsi.headless
├── colorspace
└── colorspace_compare
```

The WSI dispatcher registers both families for all nine platform types in [createTypeSpecificTests](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74). The direct test case leaves are listed under `## Behavior Parameters`, and the [default WSI mustpass file](../../../mustpass/main/vk-default/wsi.txt) contains their executable paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform type | `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, `direct` | Selects native display, window, surface extension, and platform swapchain rules. | [WSI names](../../../framework/vulkan/vkWsiUtil.cpp#L64-L80) |
| `colorspace` test case leaf | `extensions`, `basic`, `hdr` | Selects enumeration-only checking, rendered swapchain coverage, or rendered coverage with HDR metadata. | [createColorSpaceTests](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L755-L763) |
| `colorspace_compare` format leaf | `b8g8r8a8_unorm`, `r8g8b8a8_unorm`, `r8g8b8a8_srgb`, `r5g6b5_unorm_pack16`, `a2b10g10r10_unorm_pack32`, `r16g16b16a16_sfloat` | Fixes image storage format while the test varies the queried color space. | [format list and registration](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L765-L779) |
| Surface format and color space | Every `VkSurfaceFormatKHR` returned for the surface | Drives swapchain creation in `basic` and `hdr`; comparison cases keep only entries matching their registered format. | [format iteration](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L696-L739), [comparison filtering](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L438-L452) |
| Frame index | `0` through `59` for `basic` and `hdr`; `0` for each comparison swapchain | The vertex shader derives triangle rotation from this push constant. | [60-frame loop](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L608-L680), [recordFrame](../../../framework/vulkan/vkWsiUtil.cpp#L1019-L1069) |
| HDR metadata | absent in `basic`; source-defined `VkHdrMetadataEXT` in `hdr` | Adds the `setHdrMetadataEXT` call without changing shader code. | [HDR setup](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L660-L676) |

## Behavior Parameters

The primary behavioral axis is the registered test family and its direct test case leaves. Each value selects a different correctness check.

### `extensions`

This test case requires `VK_EXT_swapchain_colorspace`, queries the surface formats, and looks for at least one entry whose color space differs from `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR`. It performs no rendering. If the extension is advertised but the query exposes no extended color space, the case reports not supported rather than pass.

### `basic`

This test case visits every queried `VkSurfaceFormatKHR`. For each pair, it creates a swapchain and renders 60 acquired images with the common triangle renderer. It checks whether swapchain creation, image acquisition, queue submission, and presentation complete without an unexpected Vulkan result. It does not compare pixels.

### `hdr`

This test case follows the `basic` rendering sequence and requires `VK_EXT_hdr_metadata`. Before submitting each rendered frame, it calls `setHdrMetadataEXT` with the source-defined display primaries, white point, and luminance values. Its result checks API and presentation completion, not the compositor's visible HDR output.

### `b8g8r8a8_unorm`

This leaf fixes `VK_FORMAT_B8G8R8A8_UNORM`. It requires at least two queried color spaces for that format and compares the same readback pixel across one swapchain per color space.

### `r8g8b8a8_unorm`

This leaf applies the same comparison to `VK_FORMAT_R8G8B8A8_UNORM`.

### `r8g8b8a8_srgb`

This leaf applies the same comparison to `VK_FORMAT_R8G8B8A8_SRGB`, so the fixed storage format uses sRGB encoding while `VkColorSpaceKHR` remains the varied field.

### `r5g6b5_unorm_pack16`

This leaf applies the comparison to the packed 16-bit `VK_FORMAT_R5G6B5_UNORM_PACK16` format.

### `a2b10g10r10_unorm_pack32`

This leaf applies the comparison to `VK_FORMAT_A2B10G10R10_UNORM_PACK32`, which has ten bits for each color component and two alpha bits.

### `r16g16b16a16_sfloat`

This leaf applies the comparison to the four-component half-float `VK_FORMAT_R16G16B16A16_SFLOAT` format.

For all six format leaves, the first supported color space supplies the reference `tcu::Vec4`; every later value must compare equal to it. This is intended to compare raw swapchain-image values rather than displayed compositor output. However, the source reads each image after `vkQueuePresentKHR` without reacquiring it; the Vulkan WSI rules prohibit using a presented image again before reacquisition, so the observed equality or inequality is not a valid conformance result.

## Shader Analysis

The rendering cases use the shared `WsiTriangleRenderer`. One walkthrough is enough because the source generates the same vertex and fragment shaders for every format, color space, and HDR choice. The vertex shader is primary because `frameNdx` changes its transform; the fragment shader provides the fixed magenta output used by every case.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.wsi.headless.colorspace_compare.b8g8r8a8_unorm
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `headless` | Uses the headless WSI registration as a representative of the repeated per-platform family. |
| `colorspace_compare` | Selects one rendered frame and exact pixel readback for each supported color space. |
| `b8g8r8a8_unorm` | Fixes `VK_FORMAT_B8G8R8A8_UNORM`; only `VkColorSpaceKHR` varies between swapchains. |
| `frameNdx = 0` | Produces an identity rotation in the vertex shader for each comparison image. |

#### Purpose

The shaders render identical content into each color-space swapchain. The selected color space never reaches either shader, so a host readback difference comes from another part of the rendering, swapchain, or readback path.

#### Structural Design

| Stage | Input | Operation | Output |
|-------|-------|-----------|--------|
| Vertex | Three `vec4` positions and the `frameNdx` push constant | Builds a two-dimensional rotation matrix and transforms each vertex | `gl_Position` |
| Fragment | Rasterized triangle coverage | Writes one fixed magenta value | `o_color = vec4(1.0, 0.0, 1.0, 1.0)` |

#### Shader Code

##### Vertex Shader

```glsl
#version 310 es
/// Location 0 reads one of three host-populated vec4 positions from the renderer's vertex buffer.
layout(location = 0) in highp vec4 a_position;
/// The host writes one uint32 frame index before each draw. No descriptor sets are used.
layout(push_constant) uniform FrameData
{
    highp uint frameNdx;
} frameData;
void main (void)
{
    /// Build a two-dimensional rotation. The comparison path passes zero, so this is the identity transform.
    highp float angle = float(frameData.frameNdx) / 100.0;
    highp float c     = cos(angle);
    highp float s     = sin(angle);
    highp mat4  t     = mat4( c, -s,  0,  0,
                              s,  c,  0,  0,
                              0,  0,  1,  0,
                              0,  0,  0,  1);
    gl_Position = t * a_position;
}
```

##### Fragment Shader

```glsl
#version 310 es
/// The sole color attachment receives the same magenta value for every format and color-space choice.
layout(location = 0) out lowp vec4 o_color;
void main (void) { o_color = vec4(1.0, 0.0, 1.0, 1.0); }
```

#### Additional Info

- The fragment shader stays fixed across this page and supplies the value written inside the triangle; the render pass also clears the attachment to `(0.125, 0.25, 0.75, 1.0)` before drawing.
- `WsiTriangleRenderer::getPrograms` emits both stages without explicit `ShaderBuildOptions`, so the source collection baseline target is SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Color space | None. `VkColorSpaceKHR` is used in swapchain creation and is not passed to a shader. | [getBasicSwapchainParameters](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L250-L307) |
| Image format | No GLSL source change. It changes the render-pass attachment, image view, pipeline compatibility, and host readback interpretation. | [renderer construction](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L467-L486) |
| HDR metadata | None. The host calls `setHdrMetadataEXT` on the swapchain. | [HDR metadata call](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L660-L676) |
| Frame index | Changes the vertex rotation angle; comparison cases use `0`, while `basic` and `hdr` use `0` through `59`. | [shader generation](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194) |
| WSI platform type | None in shader source. It changes surface and swapchain setup. | [platform properties](../../../framework/vulkan/vkWsiUtil.cpp#L83-L159) |

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
; Bound: 53
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %a_position
               OpSource ESSL 310
               OpName %main "main"
               OpName %angle "angle"
               OpName %FrameData "FrameData"
               OpMemberName %FrameData 0 "frameNdx"
               OpName %frameData "frameData"
               OpName %c "c"
               OpName %s "s"
               OpName %t "t"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %a_position "a_position"
               OpDecorate %FrameData Block
               OpMemberDecorate %FrameData 0 Offset 0
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %a_position Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
       %uint = OpTypeInt 32 0
  %FrameData = OpTypeStruct %uint
%_ptr_PushConstant_FrameData = OpTypePointer PushConstant %FrameData
  %frameData = OpVariable %_ptr_PushConstant_FrameData PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
  %float_100 = OpConstant %float 100
    %v4float = OpTypeVector %float 4
%mat4v4float = OpTypeMatrix %v4float 4
%_ptr_Function_mat4v4float = OpTypePointer Function %mat4v4float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %a_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
      %angle = OpVariable %_ptr_Function_float Function
          %c = OpVariable %_ptr_Function_float Function
          %s = OpVariable %_ptr_Function_float Function
          %t = OpVariable %_ptr_Function_mat4v4float Function
         %16 = OpAccessChain %_ptr_PushConstant_uint %frameData %int_0
         %17 = OpLoad %uint %16
         %18 = OpConvertUToF %float %17
         %20 = OpFDiv %float %18 %float_100
               OpStore %angle %20
         %22 = OpLoad %float %angle
         %23 = OpExtInst %float %1 Cos %22
               OpStore %c %23
         %25 = OpLoad %float %angle
         %26 = OpExtInst %float %1 Sin %25
               OpStore %s %26
         %31 = OpLoad %float %c
         %32 = OpLoad %float %s
         %33 = OpFNegate %float %32
         %35 = OpLoad %float %s
         %36 = OpLoad %float %c
         %38 = OpCompositeConstruct %v4float %31 %33 %float_0 %float_0
         %39 = OpCompositeConstruct %v4float %35 %36 %float_0 %float_0
         %40 = OpCompositeConstruct %v4float %float_0 %float_0 %float_1 %float_0
         %41 = OpCompositeConstruct %v4float %float_0 %float_0 %float_0 %float_1
         %42 = OpCompositeConstruct %mat4v4float %38 %39 %40 %41
               OpStore %t %42
         %46 = OpLoad %mat4v4float %t
         %49 = OpLoad %v4float %a_position
         %50 = OpMatrixTimesVector %v4float %46 %49
         %52 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %52 %50
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a WSI instance and enables `VK_KHR_surface`, the platform surface extension, and `VK_EXT_swapchain_colorspace` when advertised. Device creation requires `VK_KHR_swapchain` and enables `VK_EXT_hdr_metadata` when available.
- Swapchains use two requested images, `VK_PRESENT_MODE_FIFO_KHR`, `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, and the chosen `VkSurfaceFormatKHR`. Comparison cases override only `imageColorSpace` while keeping their registered `VkFormat` fixed.
- `basic` and `hdr` construct a renderer for one queried surface format, then render 60 frames. Fences cap the number of queued frames at twice the swapchain image count. Each iteration acquires an image, records the draw, submits it, and presents it.
- The `hdr` path calls `setHdrMetadataEXT` on the swapchain before submitting each frame.
- A comparison leaf gathers all color spaces reported with its fixed format and requires at least two. For each color space, it creates a swapchain, acquires one image, records frame `0`, submits, and presents.
- After `queuePresentKHR`, `getPixel` copies the selected image from `VK_IMAGE_LAYOUT_PRESENT_SRC_KHR` into a host-visible buffer, invalidates the mapped memory range, and returns pixel `(128, 128)` as a `tcu::Vec4`. The source does not reacquire that image first, despite the specification rule that presented images must not be used again before `vkAcquireNextImageKHR` reacquires them.
- The first comparison value becomes the reference. The case returns fail on the first exact inequality; otherwise it waits for the device and returns pass. Because the readback uses a released image, neither outcome is a valid conformance judgment for the intended cross-color-space comparison.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `extensions` | An unexpected Vulkan error during instance, surface, device, or surface-format query setup. Missing required extension support or finding no extended color space produces `NotSupported`, not failure. |
| `basic` | Failure to create, acquire, render, submit, or present a swapchain for one queried surface format and color space. |
| `hdr` | The basic WSI rendering path fails, or a supported `VK_EXT_hdr_metadata` path rejects the metadata call. Extension unavailability produces `NotSupported`, not failure. |
| `b8g8r8a8_unorm`, `r8g8b8a8_unorm`, `r8g8b8a8_srgb`, `r5g6b5_unorm_pack16`, `a2b10g10r10_unorm_pack32`, `r16g16b16a16_sfloat` | An unexpected Vulkan error occurs, or the exact pixel readback differs between color-space swapchains. Fewer than two color spaces produces `NotSupported`, not failure. |

Missing a required extension, finding no extended color space, and finding fewer than two color spaces for a comparison format are `NotSupported` outcomes rather than test failures. All families also construct `DeviceHelper`, so missing `VK_KHR_swapchain` produces `NotSupported` even for the non-rendering `extensions` case. The actual failures are unexpected Vulkan errors in the exercised setup or rendering path, plus the comparison mismatch result subject to the invalid-readback limitation below.

### Cause Analysis

#### Extended color-space enumeration failure

**Possible failure symptoms:** `extensions` cannot find a non-`VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` entry after confirming the extension is available, so the case does not report pass.

**Possible implementation causes:** This is not a test failure: CTS reports `NotSupported` both when `VK_EXT_swapchain_colorspace` is unavailable and when the queried surface has no non-`VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` entry. No implementation defect can be inferred from this outcome alone.

#### Surface-format rendering or presentation failure

**Possible failure symptoms:** `basic` or `hdr` receives an unexpected result while creating the swapchain, acquiring an image, submitting rendering, presenting, or waiting for completion. The CTS exception identifies the Vulkan call; these cases do not produce a pixel mismatch result.

**Possible implementation causes:** The implementation may report a `VkSurfaceFormatKHR` pair that it cannot use in a swapchain, mishandle the selected attachment format, or fail the required acquire, layout, submission, and presentation sequence. The precise call result is needed to narrow the cause.

#### HDR metadata path failure

**Possible failure symptoms:** `hdr` reports unsupported when `VK_EXT_hdr_metadata` is absent, or a device/API error occurs in the rendering loop that includes `setHdrMetadataEXT`.

**Possible implementation causes:** Extension absence is a `NotSupported` outcome, not a failure. If the supported path returns an unexpected error, the implementation may fail to accept or associate the source-defined `VkHdrMetadataEXT` with the active swapchain. The test does not inspect displayed luminance or colorimetry.

#### Raw pixel mismatch across color spaces

**Possible failure symptoms:** A comparison-format leaf copies pixel `(128, 128)` from each presented swapchain image and obtains a `tcu::Vec4` that differs from the first color-space result.

**Possible implementation causes:** No implementation defect can be inferred from this mismatch as the source stands. `queuePresentKHR` releases the image acquisition, but `getPixel` uses the image without reacquiring it; the Vulkan specification requires reacquisition before any further use. The test must first be corrected to perform valid image access before a mismatch can localize a rendering, transfer, or color-space defect.

## Case Pruning

### Requirement-based pruning

- All families require the WSI surface extensions for the selected platform and `VK_KHR_swapchain`. Even `extensions` constructs `DeviceHelper`, whose device creation rejects implementations without `VK_KHR_swapchain`, before it performs its enumeration-only check.
- `extensions`, `basic`, `hdr`, and all comparison leaves require `VK_EXT_swapchain_colorspace`. Missing support produces a not-supported result.
- `hdr` requires `VK_EXT_hdr_metadata`.
- A comparison leaf needs at least two color spaces for its fixed format. With fewer than two, CTS reports the format as unsupported because no cross-color-space comparison is possible.
- Surface capabilities decide image count, extent, transform, and composite alpha. The helper reports not supported if it finds no composite-alpha mode.

### Design-based pruning

- `colorspace_compare` registers six formats chosen in source rather than generating cases for every `VkFormat`.
- Comparison leaves vary only color space after fixing the format. They do not compare different storage formats with each other.
- Pixel checking uses only `(128, 128)` and exact `tcu::Vec4` equality. The design does not sample the full image or validate compositor output.
- `basic` and `hdr` rely on successful execution rather than image comparison. Their purpose is broad usability coverage for every reported surface format and color-space pair.

## Key Takeaways

- The file owns two related families: `colorspace` covers enumeration and repeated rendering, while `colorspace_compare` checks raw pixel stability for six fixed formats.
- The selected color space affects swapchain creation and presentation interpretation. It never becomes a shader parameter.
- `basic` and `hdr` pass on successful 60-frame API execution; only the comparison family reads a pixel. Its current post-present readback lacks the required reacquisition, so its pass/fail result is not a valid conformance judgment.
- The HDR case checks that metadata can be attached to the swapchain rendering path. It does not validate visible HDR output.
- See `## Failure Meaning` for the difference between extension enumeration, rendering/presentation, HDR metadata, and pixel-mismatch failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| WSI family routing | [createTypeSpecificTests](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Registers `colorspace` and `colorspace_compare` under every WSI platform type. |
| Instance and device setup | [createInstanceWithWsi and createDeviceWithWsi](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L96-L165) | Enables the surface, swapchain color-space, swapchain, and HDR metadata extensions. |
| Swapchain configuration | [getBasicSwapchainParameters](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L250-L307) | Selects image format, color space, usage, extent, transform, alpha, and present mode. |
| Pixel copy and readback | [getPixel](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L346-L383) | Copies a presentable image to host-visible memory and reads `(128, 128)`. |
| Extension enumeration check | [basicExtensionTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L385-L416) | Defines the non-default color-space requirement. |
| Per-format comparison | [colorspaceCompareTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L425-L563) | Filters color spaces, renders one image per choice, and performs exact equality. |
| 60-frame render and HDR path | [surfaceFormatRenderTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L565-L693) | Defines acquisition, synchronization, HDR metadata, submission, and presentation. |
| Registrations and fixed formats | [createColorSpaceTests and createColorspaceCompareTests](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L755-L779) | Provides all direct child names and the six comparison formats. |
| Shared shader generator | [WsiTriangleRenderer::getPrograms](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194) | Emits the exact vertex and fragment GLSL used by rendering cases. |
| Shared renderer commands | [WsiTriangleRenderer::recordFrame](../../../framework/vulkan/vkWsiUtil.cpp#L1019-L1069) | Records layout transitions, clear, push constant, draw, and presentation transition. |
| Mustpass evidence | [wsi.txt](../../../mustpass/main/vk-default/wsi.txt) | Lists executable WSI color-space paths. |
| Vulkan surface semantics | [VK_KHR_surface/wsi.adoc](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc) | Defines surface-format query and WSI behavior used to interpret the tests. |
| Presentable-image use rule | [Present release and reacquisition requirement](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7419-L7426) | States that `vkQueuePresentKHR` releases image acquisition and that a presented image must not be used again before reacquisition. |
