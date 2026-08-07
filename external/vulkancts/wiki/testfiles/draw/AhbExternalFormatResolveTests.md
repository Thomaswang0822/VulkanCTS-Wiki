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

The implementation generates a pass-through vertex shader and format-dependent fragment shaders in `initPrograms`. The base fragment variants write float, signed-integer, or unsigned-integer output matching the implementation-selected resolve color-attachment format. Input-attachment variants read either the external image or the separate color attachment selected by `nullColorAttachmentWithExternalFormatResolve`, then apply an RGB/BGR component order selected for the format. Shader source is generated at runtime; this page does not claim a single fixed SPIR-V module or reproduce generated assembly.

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
