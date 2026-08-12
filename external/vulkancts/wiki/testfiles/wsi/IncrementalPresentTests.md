## Overview

**Core question:** Can the presentation engine accept correct incremental-present damage regions while swapchain images accumulate partial updates across many frames?

- This page covers the `incremental_present` test family implemented in `vktWsiIncrementalPresentTests.cpp` and registered below each supported WSI platform branch.
- Each generated swapchain configuration renders 300 frame updates into a sequence of acquired swapchain images. The test catches each image up with the updates it missed since its prior use.
- The `reference` leaf presents without region metadata. The `incremental_present` leaf attaches matching `VkPresentRegionsKHR` rectangles to `VkPresentInfoKHR`.
- Scaling, present mode, surface transform, composite alpha, and selected surface formats exercise the same two presentation paths under different swapchain configurations.
- The verdict comes from Vulkan call results and retry limits. The test does not read pixels back or compare displayed images.

## Background Knowledge

For the shared concepts swapchain images and asynchronous presentation, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- `VkPresentRegionsKHR` carries an optimization hint. Its `VkRectLayerKHR` entries identify image pixels changed since the last presentation to the same swapchain. The presentation engine may ignore the hint, so the application must provide complete desired content in every image.
- Each swapchain image has its own history. Acquisition may return an image that missed several global frames, so partial rendering must apply every update that this image missed.
- Incremental-present rectangle offsets and extents name pixels in the swapchain image, and layer 0 selects its only layer. The rectangles are specified relative to the surface's `currentTransform`, regardless of the swapchain's `preTransform`; the presentation engine then applies `preTransform` to the rectangles together with the image content.

## Registration Hierarchy

```text
wsi.headless.incremental_present
└── scale_none
```

The dispatcher registers `incremental_present` below nine platform branches: `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, and `direct`. `scale_none` exists for each branch in the mustpass list. The source registers `scale_up` and `scale_down` when the platform declares `SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE`, except for Wayland; current mustpass evidence contains those scaled paths for Android and Metal.

Below each scaling intermediate node, the hierarchy continues through present mode, transform, and composite-alpha intermediate nodes before ending in the `reference` and `incremental_present` test case leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform | `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, `direct` | Selects the native surface integration and platform scaling policy. | [`createWsiTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L90) |
| Scaling | `scale_none`, conditional `scale_up`, conditional `scale_down` | Chooses an image extent that matches, is smaller than, or is larger than the surface extent. | [`generateSwapchainConfigs`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L618-L643), [`createIncrementalPresentTests`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1116-L1124) |
| Present mode | `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `fifo_latest_ready` | Changes how the presentation engine processes and queues present requests. Unsupported modes cause a skip. | [`presentModes`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1085-L1093) |
| Surface transform | `identity`, `rotate_90`, `rotate_180`, `rotate_270`, `horizontal_mirror`, `horizontal_mirror_rotate_90`, `horizontal_mirror_rotate_180`, `horizontal_mirror_rotate_270`, `inherit` | Chooses the swapchain `preTransform`; incremental regions must remain valid when the presentation engine transforms them with the image. | [`transforms`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1094-L1106) |
| Composite alpha | `opaque`, `pre_multiplied`, `post_multiplied`, `inherit` | Chooses how the surface alpha participates in window-system composition. Unsupported values cause a skip. | [`alphas`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1107-L1114) |
| Test case leaf | `reference`, `incremental_present` | Selects a plain `VkPresentInfoKHR` or one whose `pNext` chain contains `VkPresentRegionsKHR`. | [`leaf registration`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1146-L1162) |

For each supported combination, `selectRepresentativeFormats` chooses at most one `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` format and one non-SRGB format. `generateSwapchainConfigs` adds the test extent and a minimum-sized extent for each chosen format, and the instance runs every generated configuration.

## Behavior Parameters

The primary behavioral axis is the test case leaf. The rest of the registered dimensions change the environment in which the selected presentation path runs.

### `reference` - Present without region metadata

The test renders the same per-image catch-up updates as the incremental path, but `VkPresentInfoKHR::pNext` is null. This leaf checks the shared surface, swapchain, rendering, synchronization, acquisition, and presentation path without requiring `VK_KHR_incremental_present` at device creation.

### `incremental_present` - Present the matching updated-region list

After rendering every update missed by the acquired image, the test creates one `VkRectLayerKHR` for each frame in that same range. It places the list in a `VkPresentRegionKHR`, chains a one-swapchain `VkPresentRegionsKHR` to `VkPresentInfoKHR`, and presents the image. Device creation enables `VK_KHR_incremental_present` for this leaf.

## Shader Analysis

The fragment shader gives each update rectangle frame-dependent content. Shader output helps exercise partial rendering, but the host does not read or compare the pixels. One walkthrough is enough because every registration dimension uses the same shader programs.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.wsi.headless.incremental_present.scale_none.fifo.identity.opaque.incremental_present
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `headless`, `scale_none` | Uses a headless surface and a swapchain extent selected without scaling. |
| `fifo`, `identity`, `opaque` | Uses guaranteed FIFO presentation with no image transform and opaque composition. |
| `incremental_present` | Attaches the rectangles that match the acquired image's rendered catch-up range. |

#### Purpose

The fragment shader writes a deterministic RGB pattern that changes with the frame index and pixel coordinate. A dynamic scissor confines each draw to the update rectangle reported for that frame.

#### Structural Design

| Input or state | Shader use | Result |
|----------------|------------|--------|
| Four-byte frame-index push constant | XOR with integer `gl_FragCoord` components | Changes the selected color bits across frames and pixels. |
| Dynamic scissor | Limits fragment coverage before the shader writes | Restricts each draw to `getRenderFrameRect(frameNdx, ...)`. |
| Location 0 color output | Stores normalized RGB and alpha 1.0 | Updates the acquired swapchain image inside the scissor. |

#### Shader Code

```glsl
#version 310 es
layout(location = 0) out highp vec4 o_color;
/// The host supplies the global frame index through this four-byte fragment-stage push constant.
layout(push_constant) uniform PushConstant {
    highp uint mask;
} pushConstants;
void main (void)
{
    highp uint mask = pushConstants.mask;
    highp uint x = mask ^ uint(gl_FragCoord.x);
    highp uint y = mask ^ uint(gl_FragCoord.y);
    highp uint r = 128u * bitfieldExtract(x, 0, 1)
                  +  64u * bitfieldExtract(y, 1, 1)
                  +  32u * bitfieldExtract(x, 3, 1);
    highp uint g = 128u * bitfieldExtract(y, 0, 1)
                  +  64u * bitfieldExtract(x, 2, 1)
                  +  32u * bitfieldExtract(y, 3, 1);
    highp uint b = 128u * bitfieldExtract(x, 1, 1)
                  +  64u * bitfieldExtract(y, 2, 1)
                  +  32u * bitfieldExtract(x, 4, 1);
    /// The dynamic scissor limits this write to the current update rectangle.
    o_color = vec4(float(r) / 255.0, float(g) / 255.0, float(b) / 255.0, 1.0);
}
```

#### Additional Info

- The fixed vertex shader emits six vertices for a full-screen two-triangle quad. It does not vary across cases and leaves the dynamic scissor to define the updated area.
- Frame 0 clears and draws across the full image. This initializes a swapchain image on its first acquisition before later partial updates.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| WSI platform, scaling, present mode, transform, composite alpha, test case leaf | None. These dimensions change host-side surface, swapchain, or presentation behavior. | [`Programs::init` and registration`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1037-L1176) |
| Frame index | The host changes the push-constant `mask`; the shader combines it with fragment coordinates. | [`cmdRenderFrame`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L260-L284) |
| Update rectangle | The host changes the dynamic scissor; shader source stays fixed. | [`cmdRenderFrame`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L277-L284) |

#### SPIR-V

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
; Bound: 93
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %mask "mask"
               OpName %PushConstant "PushConstant"
               OpMemberName %PushConstant 0 "mask"
               OpName %pushConstants "pushConstants"
               OpName %x "x"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %y "y"
               OpName %r "r"
               OpName %g "g"
               OpName %b "b"
               OpName %o_color "o_color"
               OpDecorate %PushConstant Block
               OpMemberDecorate %PushConstant 0 Offset 0
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %o_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%PushConstant = OpTypeStruct %uint
%_ptr_PushConstant_PushConstant = OpTypePointer PushConstant %PushConstant
%pushConstants = OpVariable %_ptr_PushConstant_PushConstant PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
   %uint_128 = OpConstant %uint 128
      %int_1 = OpConstant %int 1
    %uint_64 = OpConstant %uint 64
    %uint_32 = OpConstant %uint 32
      %int_3 = OpConstant %int 3
      %int_2 = OpConstant %int 2
      %int_4 = OpConstant %int 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
  %float_255 = OpConstant %float 255
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %mask = OpVariable %_ptr_Function_uint Function
          %x = OpVariable %_ptr_Function_uint Function
          %y = OpVariable %_ptr_Function_uint Function
          %r = OpVariable %_ptr_Function_uint Function
          %g = OpVariable %_ptr_Function_uint Function
          %b = OpVariable %_ptr_Function_uint Function
         %15 = OpAccessChain %_ptr_PushConstant_uint %pushConstants %int_0
         %16 = OpLoad %uint %15
               OpStore %mask %16
         %18 = OpLoad %uint %mask
         %25 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %26 = OpLoad %float %25
         %27 = OpConvertFToU %uint %26
         %28 = OpBitwiseXor %uint %18 %27
               OpStore %x %28
         %30 = OpLoad %uint %mask
         %32 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %33 = OpLoad %float %32
         %34 = OpConvertFToU %uint %33
         %35 = OpBitwiseXor %uint %30 %34
               OpStore %y %35
         %38 = OpLoad %uint %x
         %40 = OpBitFieldUExtract %uint %38 %int_0 %int_1
         %41 = OpIMul %uint %uint_128 %40
         %43 = OpLoad %uint %y
         %44 = OpBitFieldUExtract %uint %43 %int_1 %int_1
         %45 = OpIMul %uint %uint_64 %44
         %46 = OpIAdd %uint %41 %45
         %48 = OpLoad %uint %x
         %50 = OpBitFieldUExtract %uint %48 %int_3 %int_1
         %51 = OpIMul %uint %uint_32 %50
         %52 = OpIAdd %uint %46 %51
               OpStore %r %52
         %54 = OpLoad %uint %y
         %55 = OpBitFieldUExtract %uint %54 %int_0 %int_1
         %56 = OpIMul %uint %uint_128 %55
         %57 = OpLoad %uint %x
         %59 = OpBitFieldUExtract %uint %57 %int_2 %int_1
         %60 = OpIMul %uint %uint_64 %59
         %61 = OpIAdd %uint %56 %60
         %62 = OpLoad %uint %y
         %63 = OpBitFieldUExtract %uint %62 %int_3 %int_1
         %64 = OpIMul %uint %uint_32 %63
         %65 = OpIAdd %uint %61 %64
               OpStore %g %65
         %67 = OpLoad %uint %x
         %68 = OpBitFieldUExtract %uint %67 %int_1 %int_1
         %69 = OpIMul %uint %uint_128 %68
         %70 = OpLoad %uint %y
         %71 = OpBitFieldUExtract %uint %70 %int_2 %int_1
         %72 = OpIMul %uint %uint_64 %71
         %73 = OpIAdd %uint %69 %72
         %74 = OpLoad %uint %x
         %76 = OpBitFieldUExtract %uint %74 %int_4 %int_1
         %77 = OpIMul %uint %uint_32 %76
         %78 = OpIAdd %uint %73 %77
               OpStore %b %78
         %81 = OpLoad %uint %r
         %82 = OpConvertUToF %float %81
         %84 = OpFDiv %float %82 %float_255
         %85 = OpLoad %uint %g
         %86 = OpConvertUToF %float %85
         %87 = OpFDiv %float %86 %float_255
         %88 = OpLoad %uint %b
         %89 = OpConvertUToF %float %88
         %90 = OpFDiv %float %89 %float_255
         %92 = OpCompositeConstruct %v4float %84 %87 %90 %float_1
               OpStore %o_color %92
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a surface and chooses a presentation-capable queue family. Device creation always enables `VK_KHR_swapchain`; the `incremental_present` leaf also requires `VK_KHR_incremental_present`.
- `generateSwapchainConfigs` rejects unsupported present modes, transforms, and composite-alpha modes. It selects representative formats and produces two extent configurations for each one.
- Swapchain setup creates image views, framebuffers, a load-preserving render pass, the fixed graphics pipeline, semaphores, six fences, and six rotating command-buffer slots.
- Each frame acquires one image. `m_imageNextFrames[imageIndex]` identifies the first update that image has not received. The command buffer draws every rectangle through the current global frame and then advances that image's next-frame marker.
- Frame 0 clears and draws the full image. Later frames use a smaller moving rectangle. Reacquiring an image after several frames causes one command buffer to replay the full missed range.
- Rendering waits on the acquire semaphore and signals the render semaphore. Presentation waits on the render semaphore, and the host checks both the `vkQueuePresentKHR` return value and its per-swapchain result.
- The incremental leaf reports rectangles for the same frame range rendered into the image. The reference leaf uses a null `pNext` chain.
- The host waits for the queue after each present, rotates semaphores by image, and runs 300 frames for each generated swapchain configuration.
- `VK_ERROR_OUT_OF_DATE_KHR` or `VK_SUBOPTIMAL_KHR` causes swapchain-resource recreation and restarts the frame sequence. More than 20 such results fail that configuration. Other Vulkan errors also enter the result collector as failures.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `reference` | Baseline surface, swapchain, rendering, synchronization, acquisition, or presentation failure under the selected configuration. |
| `incremental_present` | Baseline presentation failure, or incorrect support for `VK_KHR_incremental_present` structures and updated-region handling under the selected configuration. |

A failure caused only by exceeding the out-of-date/suboptimal retry limit points to unstable surface/swapchain compatibility during the run rather than to a pixel-comparison mismatch.

### Cause Analysis

#### Baseline WSI or rendering path failure

**Possible failure symptoms:** the `reference` leaf records an acquire, submit, present, or per-swapchain result error, or it exceeds the retry limit before completing 300 frames for a configuration.

**Possible implementation causes:** source and Vulkan WSI semantics support investigation of surface capability handling, swapchain creation, image acquisition, image-layout transitions, queue synchronization, or presentation for the selected extent, format, present mode, transform, and alpha mode. The CTS result alone does not isolate one of these mechanisms.

#### Incremental-present metadata or region handling failure

**Possible failure symptoms:** the `incremental_present` leaf reports a present error for rectangle metadata that matches the updates rendered since the acquired image's previous use, while a corresponding reference configuration may complete.

**Possible implementation causes:** investigation should cover `VkPresentRegionsKHR` processing, per-swapchain region association, rectangle bounds and layer handling, transform application, and preservation of unchanged presented content. The extension defines the regions as hints, so ignoring a hint is valid; rejecting valid metadata or mishandling the required presentation operation is not. This test has no pixel oracle, so a visually wrong result that still returns success may escape detection.

#### Repeated swapchain incompatibility

**Possible failure symptoms:** one generated configuration produces `VK_ERROR_OUT_OF_DATE_KHR` or `VK_SUBOPTIMAL_KHR` more than 20 times and never completes its frame sequence.

**Possible implementation causes:** the surface may keep changing in a way that prevents the chosen swapchain extent or other surface-dependent configuration from remaining usable. Source-level investigation must compare live surface capabilities and returned results because the CTS retry count does not identify the changing property.

## Case Pruning

### Requirement-based pruning

- Device creation requires `VK_KHR_swapchain`; the `incremental_present` leaf also requires `VK_KHR_incremental_present`.
- A present-mode case skips when the surface does not report that mode. `fifo_latest_ready` also depends on `VK_EXT_present_mode_fifo_latest_ready` and its feature.
- Transform and composite-alpha cases skip when the surface capability bits do not include the requested value.
- Instance creation requires `VK_KHR_surface` and the selected platform surface extension. Display-backed and direct-DRM paths add their required instance extensions.

### Design-based pruning

- The source omits `scale_up` and `scale_down` unless platform properties declare window-size scaling. Wayland omits them in all cases.
- Format coverage uses a representative subset rather than every advertised format: one sRGB nonlinear color space and one non-sRGB color space when present, with the first available format as a fallback.
- The fixed shader, one image layer, exclusive queue sharing, and color-attachment-only usage keep the matrix focused on presentation-region behavior rather than shader or resource-layout variants.

## Key Takeaways

- The test tracks missed updates per swapchain image. Its rendered catch-up range and incremental-present rectangle range use the same frame indices.
- `reference` and `incremental_present` share rendering and synchronization; the leaf changes device-extension requirements and the `VkPresentInfoKHR::pNext` chain.
- Scaling, transform, alpha, present mode, format, and extent broaden WSI coverage without changing shader source.
- Success proves that the configured sequence completes and that the presentation engine accepts the supplied region metadata. It does not prove visual equivalence because CTS performs no pixel comparison.
- See `## Failure Meaning` for the limits of diagnosis from each failing leaf.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Damage rectangles and partial rendering | [`getRenderFrameRect`, `getUpdatedRects`, and `cmdRenderFrame`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L227-L285) | Defines frame 0, later rectangles, push constants, scissors, and draws. |
| Per-image catch-up command recording | [`createCommandBuffer`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L287-L330) | Replays all updates missed by one acquired image. |
| Format and extent configurations | [`selectRepresentativeFormats` and `generateSwapchainConfigs`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L576-L719) | Selects formats, checks supported parameters, and creates the configurations under test. |
| Swapchain resource lifetime | [`initSwapchainResources` and `deinitSwapchainResources`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L780-L849) | Owns per-configuration rendering and synchronization resources. |
| Acquire, submit, and present paths | [`IncrementalPresentTestInstance::render`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L851-L953) | Implements per-image state, region chaining, result checks, and semaphore rotation. |
| Frame count and retry logic | [`IncrementalPresentTestInstance::iterate`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L955-L1035) | Runs each configuration and handles out-of-date or suboptimal results. |
| Shader source | [`Programs::init`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1037-L1074) | Supplies the fixed quad vertex shader and frame-dependent fragment shader. |
| Family registration | [`createIncrementalPresentTests`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1078-L1176) | Defines every registered dimension and conditional scaling branch. |
| WSI dispatcher | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Registers the test family under each platform branch. |
| Platform properties | [`getPlatformProperties`](../../../framework/vulkan/vkWsiUtil.cpp#L83-L158) | Defines which platforms use window-size scaling. |
| Incremental-present specification | [`VkPresentRegionsKHR`, `VkPresentRegionKHR`, and `VkRectLayerKHR`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7584-L7685) | Defines hint semantics, region association, coordinates, transforms, and bounds. |
| Mustpass registration | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L11542) | Confirms the platform-qualified executable paths. |
