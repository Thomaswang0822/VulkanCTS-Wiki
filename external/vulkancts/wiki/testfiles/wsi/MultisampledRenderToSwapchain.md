## Overview

**Core question:** Does the implementation render to a multisampled swapchain image and resolve it correctly for each supported WSI type?

- This page covers `wsi.<wsi_type>.multisampled_render_to_swapchain`, implemented in `vktWsiMultisampledRenderToSwapchainTests.cpp`.
- The generated leaves vary color-format combinations, sample counts, rendering mode, framebuffer scope, and a result index.
- A separate `supported_flags` branch checks the extension's reported support flags.

## Background Knowledge

For shared surface, swapchain, and presentation concepts, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- Multisampled rendering stores multiple samples per pixel and resolves them to a single-sample image.
- Render-pass and dynamic-rendering commands express attachment operations through different API structures while preserving the same rendering intent.
- The extension's supported flags describe which multisampled-render-to-single-sampled configurations a device can use.

## Registration Hierarchy

```text
wsi.android.multisampled_render_to_swapchain
├── b8g8r8a8_unorm_r16g16b16a16_sfloat_r16g16b16a16_sint
├── r8g8b8a8_unorm_r16g16b16a16_sfloat_r16g16b16a16_sint
├── r8g8b8a8_unorm_r16g16b16a16_sfloat_r32g32b32a32_uint
└── supported_flags
```

The same family is registered below the supported WSI type branches; deeper sample-count and rendering variants are kept in the parameter description.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Color-format combination | `b8g8r8a8_unorm...`, `r8g8b8a8_unorm...` | Selects swapchain and render-target formats. | [`vktWsiMultisampledRenderToSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp) |
| Sample count | `2x`, `4x`, `8x`, `16x` | Selects the multisample count. | [`vktWsiMultisampledRenderToSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp) |
| Rendering mode | `render_pass`, `dynamic_rendering` | Selects the command encoding for the render operation. | [`vktWsiMultisampledRenderToSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp) |
| Framebuffer scope | `whole_framebuffer`, `sub_framebuffer` | Selects the rendered region. | [`vktWsiMultisampledRenderToSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp) |
| Result index | `0`, `1` | Selects the generated result variant. | [`vktWsiMultisampledRenderToSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp) |

## Behavior Parameters

The primary behavioral axis is the generated render configuration: format, sample count, rendering mode, and framebuffer scope jointly determine the attachment and resolve path.

### Multisampled render configurations

The test creates the platform-specific surface and swapchain, configures the selected multisampled-render-to-single-sampled mode, renders, and checks the resulting image. Render-pass and dynamic-rendering leaves exercise separate API paths.

### Supported-flag queries

The `supported_flags` branch queries supported extension flags and checks that the returned structure is valid. It does not render a frame.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.wsi.android.multisampled_render_to_swapchain.b8g8r8a8_unorm_r16g16b16a16_sfloat_r16g16b16a16_sint
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `b8g8r8a8_unorm` | Swapchain color format. |
| `r16g16b16a16_sfloat` | Floating-point color attachment. |
| `r16g16b16a16_sint` | Integer color attachment. |
| `render_pass` | Uses `VkRenderPass` and `VkFramebuffer` attachment setup. |

#### Purpose

The graphics shader produces different values per sample. The host-side compute checks compare the resolved attachments with the expected sample average and also check pixels outside a sub-framebuffer render area.

#### Structural Design

| Stage | Operation | Check |
|---|---|---|
| Vertex | Draws a fullscreen triangle. | Covers the selected render area. |
| Fragment | Uses `gl_SampleID` to select per-sample float and integer values. | Confirms the requested sample count participated in rendering. |
| Compute | Reads the resolved images and increments verification counters. | Checks attachment values and untouched pixels. |

#### Shader Code

```glsl
#version 450
layout(location = 0) in vec4 in_position;
void main(void) { gl_Position = in_position; }
```

The fragment generator emits one branch for each selected sample count. Each branch writes distinct values to the three color attachments and sets `gl_FragDepth`.

#### Additional Info

- The render pass chains `VkMultisampledRenderToSingleSampledInfoEXT` with `multisampledRenderToSingleSampledEnable = VK_TRUE`.
- Dynamic-rendering cases use the equivalent `VkRenderingInfo` chain.
- The swapchain is created with `VK_SWAPCHAIN_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Format combination | Two swapchain formats, one float format, and two integer formats. | [`createMultisampledTestsInGroup`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp#L2461-L2529) |
| Sample count | `2x`, `4x`, `8x`, `16x` select the generated per-sample output. | [`sampleRange`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp#L2480-L2485) |
| Rendering mode | `render_pass` or `dynamic_rendering` selects command encoding. | [`dynamicRenderingGroup`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp#L2505-L2509) |
| Framebuffer scope | `whole_framebuffer` or `sub_framebuffer` selects the outside-area check. | [`renderToWholeFramebuffer`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp#L2510-L2514) |

#### SPIR-V

- Status: reconstructed from the source shader generator
- Source: `vktWsiMultisampledRenderToSwapchainTests.cpp#L1843-L2067`
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End
; The representative vertex shader passes the fullscreen-triangle position to gl_Position.
```

</details>

## Runtime Execution and Result Checking

Support checks select WSI types, extensions, formats, sample counts, and rendering modes that the device can use. The render cases submit the draw and validate the resolved output; the flag cases validate the reported support bits.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior | Possible cause |
|---|---|
| Render setup fails | Unsupported extension, format, sample count, surface capability, or attachment configuration. |
| Resolved output is wrong | Incorrect multisample resolve or swapchain image handling. |
| Supported flags are invalid | Incorrect extension feature or flag reporting. |

### Cause Analysis

#### Multisampled attachment execution

**Possible failure symptoms:** A supported configuration cannot create its swapchain, cannot submit rendering, or produces an incorrect resolved image.

**Possible implementation causes:** The implementation may mishandle multisample state, attachment usage, render-pass or dynamic-rendering setup, resolve operations, or swapchain image transitions. The exact lower-level cause requires implementation investigation.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the WSI platform, required extension, format, sample count, or surface capability is unavailable. Such skips are expected capability filtering, not conformance failures.

### Design-based pruning

The generated matrix keeps only configurations that exercise a distinct attachment or resolve path; unsupported or duplicate combinations are not executed.

## Key Takeaways

- The family adds multisampled-render-to-swapchain coverage below existing WSI type branches.
- Sample count, rendering mode, framebuffer scope, and format determine the tested attachment path.
- Support-flag queries are separate from rendered cases.

## Source Reference Appendix

- [`vktWsiMultisampledRenderToSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiMultisampledRenderToSwapchainTests.cpp)
- [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt)
