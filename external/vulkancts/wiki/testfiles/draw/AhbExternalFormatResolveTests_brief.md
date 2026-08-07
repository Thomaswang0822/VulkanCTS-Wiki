# Understanding Brief: AhbExternalFormatResolveTests

## One-Sentence Test Purpose

This test checks that Vulkan external-format resolve preserves the expected final pixel values when a 64x64 Android Hardware Buffer is cleared, drawn, read as an input attachment, and decoded back into host-visible bytes.

## Background Knowledge

- Android Hardware Buffer formats are external representations. Vulkan imports the buffer as an external image and uses `VK_ANDROID_external_format_resolve` plus implementation-reported properties to select the renderable resolve path.
- A pixel comparison must account for representation details. YUV formats may subsample chroma, RAW10/RAW12 use packed bytes, and formats without alpha need a defined maximum alpha value when decoded into a four-component reference.
- A render-pass input attachment is consumed by a later subpass. The later subpass can therefore test not only the producing attachment write but also the availability, layout, descriptor, and format conversion used by the consumer.

## One Concrete Example

A `draw.<format>.partial_render_area_N` case clears the complete AHB-backed image, draws the checkerboard only inside one even-aligned random rectangle, locks the AHB for CPU read, decodes its bytes, and compares them with a reference containing checkerboard colors inside the rectangle and the clear color everywhere else. The case therefore checks both rendered bytes and preservation of the obsolete contents outside the render area.

## End-to-End Test Flow

1. Registration creates `draw.renderpass.ahb_external_format_resolve` with `clear`, `draw`, and `input_attachment` families. The format loop retains valid color/raw formats that have a valid CTS texture mapping.
2. The instance allocates a one-layer 64x64 AHB with either `GPU_FRAMEBUFFER | CPU_READ` or `GPU_FRAMEBUFFER | GPU_SAMPLED` usage. Unsupported allocation and missing extension/API support stop the case as unsupported.
3. Vulkan imports the AHB, creates an external image/view, and, when required, creates a separate Vulkan color attachment. It builds the selected render-pass or dynamic-rendering resources and generated pipelines.
4. The command sequence transitions attachments and clears the whole image. Non-clear cases then draw a full-screen quad; input-attachment cases run a producer subpass followed by a consumer subpass that writes a conventional Vulkan image.
5. Direct AHB cases destroy Vulkan resources retaining the AHB, lock it for CPU read, and decode final bytes. RAW10 and RAW12 are decompressed; RAW16 follows its UINT16 representation. Input-attachment cases invalidate a host-visible result buffer after image-to-buffer copy.
6. The host builds the expected image from clear color, checkerboard coverage, format alpha rules, and device chroma-location properties. It compares the result with `tcu::intThresholdCompare`: P010 uses threshold `(4,4,4,4)` and other formats use `(1,0,1,0)`.
7. A comparison mismatch returns a failing CTS status; a matching final image returns pass.

## Generated Test Artifacts and Bound Resources

| Artifact/resource | Role |
|---|---|
| AHB allocation | Owns the external pixel storage and supplies the final CPU-readable representation for direct cases. |
| Imported external Vulkan image and view | Exposes AHB storage to Vulkan attachment operations. |
| Optional Vulkan color attachment | Provides the intermediate renderable format when `nullColorAttachment` is false. |
| Generated vertex/fragment shader modules | Draw a full-screen quad and write typed or swizzled color components for the selected resolve format. |
| Render pass/framebuffer or dynamic-rendering state | Defines attachment load, resolve, and (for input cases) subpass transitions. |
| Result image and host-visible buffer | Used only by input-attachment cases to copy and inspect the conventional Vulkan output. |

## What Is Checked

The source checks the final decoded image bytes against an independently generated reference. For full draws, every pixel should contain the checkerboard result. For partial draws, the initial clear must remain outside the render rectangle. For clear-only cases, the entire image must contain the clear result. Input-attachment cases compare the later subpass's conventional Vulkan image, while direct cases compare decoded AHB bytes.

This is not a registration-only or command-success check: the test can pass Vulkan submission and still fail because the externally represented bytes, conversion, swizzle, chroma placement, alpha, or preserved clear pixels are wrong.

## Behavior Parameter Identification

The primary behavioral axis is the operation family:

- `clear`: attachment-load clear followed by direct AHB-byte validation.
- `draw`: full-screen checkerboard draw, with full or partial render area and direct AHB-byte validation.
- `input_attachment`: external-format producer followed by input-attachment consumer and conventional Vulkan buffer validation.

The format and render-area dimensions modify the representation and coverage being validated, but the operation family determines the distinct correctness mechanism.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `clear` | AHB allocation/import, attachment clear/load, external-format resolve, format decoding, or final-byte readback mismatch. |
| `draw` | Full-screen shader or render-area coverage, clear preservation outside a partial area, resolve conversion, AHB byte layout, format decoding, or final image comparison mismatch. |
| `input_attachment` | External-image producer/consumer subpass dependency, input-attachment descriptor/layout, format swizzle or chroma handling, intermediate-image copyback, or final comparison mismatch. |

### Cause Analysis

#### External allocation and import

**Possible failure symptoms:** The case is skipped as unsupported, or no valid output reaches comparison.

**Possible implementation causes:** The platform can reject an AHB allocation with the requested format and usage, or required external-format-resolve/AHB functionality may be absent. The source checks these prerequisites explicitly.

#### Final-byte conversion and preservation

**Possible failure symptoms:** Clear-only output is wrong, checkerboard pixels differ, or pixels outside a partial render area no longer equal the clear value.

**Possible implementation causes:** The attachment clear, resolve selection, image transitions, raster coverage, or external byte conversion may be incorrect. Format-specific causes include packed RAW decoding, YUV chroma placement, reduced-range P010, and alpha defaults.

#### Input-attachment path

**Possible failure symptoms:** Direct `draw` passes but `input_attachment` fails, or the result copied from the conventional Vulkan image differs from the expected image.

**Possible implementation causes:** The producing subpass may not make the external image available to the consumer, the descriptor/layout or generated swizzle may be wrong, or the result image/buffer copyback may expose stale or misconverted data. Source-level investigation is needed to distinguish these possibilities for a particular failure.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Iteration, readback, reference, and threshold | [`iterate`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L170-L269) | Defines the final-byte validation contract. |
| Resource and command sequencing | [`renderToExternalFormat`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L271-L347) | Shows clear-before-draw and input-attachment execution. |
| Registration | [`createAhbExternalFormatResolveDrawTests`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1652-L1771) | Defines exact families, formats, leaves, usage, and pruning. |
| Support gates and dispatcher link | [`checkSupport`](../../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L1641-L1650), [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L121) | Defines required functionality and the non-VulkanSC registration boundary. |
| External-format resolve semantics | [`VK_ANDROID_external_format_resolve`](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/chap47.html#VK_ANDROID_external_format_resolve) | Normative extension behavior for external images and resolve attachments. |
