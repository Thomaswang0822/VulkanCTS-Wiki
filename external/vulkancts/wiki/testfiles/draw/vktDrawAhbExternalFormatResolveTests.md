# ahb_external_format_resolve

## Overview

Android Hardware Buffer external format resolve draw tests that verify correct rendering to and from AHB images with external formats that require format resolution. These tests exercise the `VK_ANDROID_external_format_resolve` extension, which enables rendering to AHB images whose formats are not natively supported as Vulkan color attachments by resolving through an intermediate color attachment format.

## Role

Validates the external format resolve pipeline: rendering to an AHB-backed image with an external format via a resolve attachment, reading back the result (either directly from AHB CPU read or via an input attachment subpass), and comparing against a reference image. Covers three modes: direct draw to external format, input attachment read-back from external format (renderpass-only), and clear-only operations.

## Source Code

- [vktDrawAhbExternalFormatResolveTests.cpp](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.ahb_external_format_resolve
├── clear
├── draw
└── input_attachment
```

## Test Families

### clear — Clear-only AHB external format resolve tests

Tests that clearing an AHB-backed external format image via `VK_ATTACHMENT_LOAD_OP_CLEAR` produces the expected clear color values. Each test case clears the image and validates the result without drawing any geometry.

Leaf test cases are named by AHB format (e.g., `R8G8B8A8_UNORM`, `R5G6B5_UNORM`, `Y8Cb8Cr8_420`, etc.). Only formats with a valid `tcu::TextureFormat` and that are color or raw formats are included.

Source: [vktDrawAhbExternalFormatResolveTests.cpp#L1756-L1766](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1756-L1766)

### draw — Draw to AHB external format resolve

Tests rendering a checkerboard pattern to an AHB-backed external format image via the resolve attachment mechanism. Each format has a `full_render_area` test and 10 `partial_render_area_N` tests with randomly generated render areas.

Per-format sub-groups are named by AHB format. Only formats with a valid `tcu::TextureFormat` and that are color or raw formats are included. Each format sub-group contains:

| Test Case | Description |
|-----------|-------------|
| full_render_area | Renders to the entire image (64x64) |
| partial_render_area_0 through partial_render_area_9 | Renders to a randomly generated sub-region of the image |

Source: [vktDrawAhbExternalFormatResolveTests.cpp#L1687-L1725](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1687-L1725)

### input_attachment — Input attachment read from AHB external format (renderpass-only)

Tests a two-subpass render pass where the first subpass draws to the external format image, and the second subpass reads from it as an input attachment and renders to a standard Vulkan format image. The result is read back from the Vulkan image and compared against a reference.

Per-format sub-groups are named by AHB format. Only available in renderpass variants (not dynamic rendering) because subpasses cannot be translated to dynamic rendering. Each format sub-group contains the same `full_render_area` and `partial_render_area_N` tests as the draw group.

Source: [vktDrawAhbExternalFormatResolveTests.cpp#L1727-L1752](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1727-L1752)

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| AHB Format | R8G8B8A8_UNORM, R8G8B8X8_UNORM, R8G8B8_UNORM, R5G6B5_UNORM, R16G16B16A16_FLOAT, R10G10B10A2_UNORM, Y8Cb8Cr8_420, YCbCr_P010, R8_UNORM, R16_UINT, R16G16_UINT, R10G10B10A10_UNORM, B8G8R8A8_UNORM, YV12, Y8, Y16, RAW10, RAW12, RAW16, NV16, NV21, YUY2 | AHB format enum (IMPLEMENTATION_DEFINED, BLOB, depth/stencil, RAW_OPAQUE, and D32_FLOAT_S8_UINT excluded) |
| Render area | full (64x64), partial (10 random sub-regions) | The render area within the image |
| Test mode | draw, input_attachment, clear | Whether to draw, read as input attachment, or only clear |
| AHB usage | GPU_FRAMEBUFFER \| CPU_READ (draw/clear), GPU_FRAMEBUFFER \| GPU_SAMPLED (input_attachment) | AHB usage flags |
| Partial draw | true, false | Whether the render area is a sub-region of the full image |
| Image dimensions | 64x64 | Fixed render target size |

## Support / Feature Requirements

| Requirement | Condition | Details |
|-------------|-----------|---------|
| Vulkan only | `!CTS_USES_VULKANSC` | Registered under `#ifndef CTS_USES_VULKANSC` in the parent module ([vktDrawTests.cpp#L103](../../../modules/vulkan/draw/vktDrawTests.cpp#L103)) |
| All variants | Both renderpass and dynamic rendering | Added to all variant groups including dynamic rendering ([vktDrawTests.cpp#L119](../../../modules/vulkan/draw/vktDrawTests.cpp#L119)) |
| External format resolve | `VK_ANDROID_external_format_resolve` | Required device functionality checked in `checkSupport` ([vktDrawAhbExternalFormatResolveTests.cpp#L1643](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1643)) |
| AHB API availability | `AndroidHardwareBufferExternalApi::getInstance()` | Platform must support AHB ([vktDrawAhbExternalFormatResolveTests.cpp#L1645-L1646](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1645-L1646)) |
| Dynamic rendering | `VK_KHR_dynamic_rendering` | Required when using dynamic rendering variant ([vktDrawAhbExternalFormatResolveTests.cpp#L1648-L1649](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1648-L1649)) |
| AHB allocation | Successful allocation | Throws `NotSupportedError` if the AHB cannot be allocated with the requested format and dimensions ([vktDrawAhbExternalFormatResolveTests.cpp#L176-L187](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L176-L187)) |
| External format testing required | Format not natively renderable | Skips (passes) if the format is already natively supported as a color attachment ([vktDrawAhbExternalFormatResolveTests.cpp#L617-L627](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L617-L627)) |
| Input attachment format support | `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` | When `nullColorAttachment` is VK_FALSE and format lacks color attachment bit, input attachment tests throw `NotSupportedError` ([vktDrawAhbExternalFormatResolveTests.cpp#L668-L671](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L668-L671)) |
| Input attachment variant | Renderpass only | The `input_attachment` sub-group is only added when `!useDynamicRendering` ([vktDrawAhbExternalFormatResolveTests.cpp#L1727](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1727)) |
| Clear variant | Primary or complete secondary cmd buffer | Clear tests are only added when not using a partial secondary command buffer ([vktDrawAhbExternalFormatResolveTests.cpp#L1754-L1755](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1754-L1755)) |

## Verification Methods

| Method | Description |
|--------|-------------|
| Integer threshold comparison | Uses `tcu::intThresholdCompare` with a per-format threshold to compare rendered output against a procedurally generated reference image. For YCbCr_P010 format, the threshold is `tcu::UVec4(4)`; for all other formats it is `tcu::UVec4(1, 0, 1, 0)` ([vktDrawAhbExternalFormatResolveTests.cpp#L259-L261](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L259-L261)) |
| CPU readback (draw/clear) | For draw and clear tests, the AHB is locked for CPU read and the pixel data is copied to a `tcu::TextureLevel` for comparison. Compressed RAW formats (RAW10, RAW12) are decompressed first ([vktDrawAhbExternalFormatResolveTests.cpp#L211-L238](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L211-L238)) |
| Vulkan buffer readback (input_attachment) | For input attachment tests, the result is read from a host-visible buffer via `vkCmdCopyImageToBuffer` ([vktDrawAhbExternalFormatResolveTests.cpp#L197-L204](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L197-L204)) |
| YUV chroma downsampling | For YUV formats, the reference image is downsampled according to the device's chroma location properties (`externalFormatResolveChromaOffsetX/Y`) when the test reads directly from the AHB or when `nullColorAttachment` is VK_TRUE ([vktDrawAhbExternalFormatResolveTests.cpp#L721-L729](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L721-L729)) |

## Notes

- This test exercises the `VK_ANDROID_external_format_resolve` extension, which provides a mechanism to render to AHB images with external formats that are not natively supported as Vulkan color attachments. The extension queries `VkAndroidHardwareBufferFormatResolvePropertiesANDROID` to determine the resolve color attachment format and `VkPhysicalDeviceExternalFormatResolvePropertiesANDROID` to determine whether a null color attachment can be used.
- The `nullColorAttachment` property determines whether a separate Vulkan color attachment image is needed alongside the external format image. When VK_TRUE, the external format image is used directly as the resolve attachment without a separate color attachment.
- The input attachment tests use a two-subpass render pass: subpass 0 draws to the external format, and subpass 1 reads from it as an input attachment. This is why input_attachment tests are renderpass-only.
- The clear tests only run when using a primary command buffer or a secondary command buffer that completely contains the dynamic renderpass, because clearing requires full control over the render pass lifecycle.
- The reference image is built procedurally using a checkerboard pattern of four colors (black, red, green, blue) based on fragment coordinates, with clear color applied outside the render area for partial draws.
- Alpha channel handling differs between AHB formats that have alpha and those that do not. For formats without alpha, the reference image uses the format's maximum value for the alpha component.
- Shader generation produces three fragment shader variants (float, int, uint output types) for the base draw pipeline, and additional input attachment variants with RGB/BGR swizzle orders for YUV formats.
