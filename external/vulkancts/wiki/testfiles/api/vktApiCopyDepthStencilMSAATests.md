# [vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1)

## Overview

Tests Vulkan image-to-image copy operations on multisampled depth/stencil images. The file validates `vkCmdCopyImage` and `vkCmdCopyImage2` when both source and destination are multisampled depth/stencil images, ensuring all samples are correctly preserved during the copy. Verification is performed via a GPU-based shader comparison rather than CPU readback.

## Role of File

Implementation-heavy. Contains the `DepthStencilMSAA` test instance with a two-phase approach (render a triangle to the source image, then copy and verify), the `DepthStencilMSAATestCase` with shader generation and support checks, and the `addCopyDepthStencilMSAATests` / `addDepthStencilCopyMSAATest` registration functions.

## Source Code

- Implementation: [vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1)
- Header: [vktApiCopyDepthStencilMSAATests.hpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.hpp#L1)
- Parent registration: [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)

## Registration Hierarchy

```text
api.copy_and_blit.core.depth_stencil_msaa_copy
├── whole
├── partial
└── array_to_array
```

## Test Families

### whole — Full-image multisampled depth/stencil copies

Covers the `whole` subgroup registered by [`addCopyDepthStencilMSAATests()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1274). This branch uses `COPY_WHOLE_IMAGE` and generates cases that vary format, source layout, destination layout, copied aspect, sample count, and optional bind-offset handling through [`addDepthStencilCopyMSAATest()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1172-L1257).

Observed generated case patterns include:

- `<format>_<srcLayout>_<dstLayout>_D_<samples>`
- `<format>_<srcLayout>_<dstLayout>_D_<samples>_bind_offset`
- `<format>_<srcLayout>_<dstLayout>_S_<samples>`
- `<format>_<srcLayout>_<dstLayout>_S_<samples>_bind_offset`

Within the implementation, the source image is populated by rendering a triangle before the copy command is issued, and verification then compares multisample values from source and destination images sample-by-sample using shader-written storage buffers ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L226-L257), [vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L564-L659), [vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L999)).

### partial — Subregion multisampled depth/stencil copies

Covers the `partial` subgroup registered by [`addCopyDepthStencilMSAATests()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1274). This branch uses `COPY_PARTIAL` and generates partial-copy cases over depth or stencil aspects, sample counts, formats, and optional bind offsets via [`addDepthStencilCopyMSAATest()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1172-L1257).

Observed generated case patterns include:

- `<format>_D_<samples>`
- `<format>_D_<samples>_bind_offset`
- `<format>_S_<samples>`
- `<format>_S_<samples>_bind_offset`

The implementation copies two subregions of the multisampled image and additionally checks that uncopied destination regions remain at the clear value, which is explicitly handled in the verification logic for partial copies ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L980-L999)).

### array_to_array — Multisampled array-layer copies

Covers the `array_to_array` subgroup registered by [`addCopyDepthStencilMSAATests()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1274). This branch uses `COPY_ARRAY_TO_ARRAY` and generates cases across depth/stencil aspects, sample counts, formats, and optional bind offsets via [`addDepthStencilCopyMSAATest()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1172-L1257).

Observed generated case patterns include:

- `<format>_D_<samples>`
- `<format>_D_<samples>_bind_offset`
- `<format>_S_<samples>`
- `<format>_S_<samples>_bind_offset`

This mode copies between specific layers of a five-layer image (source layer 2 to destination layer 3) and verifies that non-target destination layers remain at the clear value ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1107-L1134)).

### DepthStencilMSAA — Common execution model

Test instance inheriting directly from `vkt::TestInstance` ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L35-L999)), not from the `CopiesAndBlittingTestInstance` hierarchy. Uses a two-phase approach:

1. **Render phase**: Creates a multisampled depth/stencil source image, renders a triangle to it via a graphics pipeline, producing known depth/stencil values per sample ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L226-L257))
2. **Copy phase**: Issues `vkCmdCopyImage` or `vkCmdCopyImage2` to copy from source to destination image ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L564-L659))
3. **Verify phase**: Uses a verification shader that reads both source and destination images as input attachments, writes sample values to storage buffers, then CPU-compares the buffer contents sample-by-sample ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L999))

Three copy options are defined in the implementation enum ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L38-L43)):
- `COPY_WHOLE_IMAGE`: Full image copy with layout variations
- `COPY_ARRAY_TO_ARRAY`: Copies between specific array layers in a 5-layer image
- `COPY_PARTIAL`: Copies two subregions of the image

### DepthStencilMSAATestCase — Case construction and shader generation

`DepthStencilMSAATestCase` is a `TestCase` subclass ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1003-L1169)) that generates verification shaders via [`DepthStencilMSAATestCase::initPrograms()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1137-L1167). The verification shader reads multisampled input attachments and writes per-sample values to storage buffers. For depth aspects, it uses `subpassInputMS`; for stencil aspects, `usubpassInputMS` ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1080-L1135)).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Format | VK_FORMAT_D32_SFLOAT, VK_FORMAT_S8_UINT, VK_FORMAT_D16_UNORM_S8_UINT, VK_FORMAT_D24_UNORM_S8_UINT ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1179-L1185)) |
| Sample count | 2, 4, 8, 16, 32, 64 ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170)) |
| Copy aspect | VK_IMAGE_ASPECT_DEPTH_BIT, VK_IMAGE_ASPECT_STENCIL_BIT |
| Copy option | COPY_WHOLE_IMAGE, COPY_PARTIAL, COPY_ARRAY_TO_ARRAY |
| Image offset | `false` (no bind offset), `true` (bind image with alignment offset) |
| Src image layout | VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL (whole copy only) |
| Dst image layout | VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL (whole copy only) |
| extensionFlags | From `testGroupParams`: NONE, COPY_COMMANDS_2 |
| allocationKind | From `testGroupParams`: ALLOCATION_KIND_SUBALLOCATION, ALLOCATION_KIND_DEDICATED |

## Support / Feature Requirements

- `fragmentStoresAndAtomics` device feature required ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1027-L1028))
- `framebufferDepthSampleCounts` must include the requested sample count for depth aspects ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1030-L1032))
- `framebufferStencilSampleCounts` must include the requested sample count for stencil aspects ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1033-L1034))
- Image format must support `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1037-L1045))
- `_bind_offset` variant only generated when `allocationKind != ALLOCATION_KIND_DEDICATED` ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1219-L1224))

## Verification Methods

- GPU-based verification: A fragment shader reads source and destination images as multisampled input attachments, writes per-sample values to storage buffers ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L957))
- CPU comparison: After GPU verification pass, CPU reads back storage buffers and compares source vs. destination sample values coordinate-by-coordinate and sample-by-sample ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L958-L999))
- Partial copy: Additionally verifies that uncopied regions (top half) remain at the clear value (0) ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L980-L999))
- Array-to-array: Verifies that non-target layers in the destination contain only the clear value ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1107-L1134))

## Test Principles Observed

- Per-sample verification: Ensures every individual sample is correctly copied, not just the resolved value
- Subregion testing: Validates partial copies and array-layer copies, not just whole-image copies
- Layout variation: Tests both optimal transfer layouts and GENERAL layout for whole-image copies
- Bind offset: Tests images bound with a memory offset (alignment-based) to catch alignment-related bugs
- Shader-based verification: Avoids the complexity of reading back multisampled depth/stencil images on the CPU

## Notes / Uncertainties

- The `addCopyDepthStencilMSAATests` function signature differs from the other files: it takes `AllocationKind` and `uint32_t extensionFlags` directly rather than `TestGroupParamsPtr` ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1274))
- Layout variations (GENERAL vs. TRANSFER_SRC/DST_OPTIMAL) are only tested for `COPY_WHOLE_IMAGE` to limit test count; partial and array copies use only optimal layouts ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1251-L1257))
- The `checkSupport()` method checks `framebufferDepthSampleCounts` for both depth and stencil aspects, which may be a minor oversight since stencil should check `framebufferStencilSampleCounts` ([vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1033-L1034))
- The source image is initialized by rendering a triangle, not by uploading buffer data, which means the depth/stencil values are determined by the rendering pipeline rather than being precisely controlled

