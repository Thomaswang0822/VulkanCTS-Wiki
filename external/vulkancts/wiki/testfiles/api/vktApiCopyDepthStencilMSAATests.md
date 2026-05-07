# [vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1)

## Overview

Tests Vulkan image-to-image copy operations on multisampled depth/stencil images. The file validates `vkCmdCopyImage` and `vkCmdCopyImage2` when both source and destination are multisampled depth/stencil images, ensuring all samples are correctly preserved during the copy. Verification is performed via a GPU-based shader comparison rather than CPU readback.

## Role of File

Implementation-heavy. Contains the `DepthStencilMSAA` test instance with a two-phase approach (render a triangle to the source image, then copy and verify), the `DepthStencilMSAATestCase` with shader generation and support checks, and the `addCopyDepthStencilMSAATests` / `addDepthStencilCopyMSAATest` registration functions.

## Source Code

- Implementation: [vktApiCopyDepthStencilMSAATests.cpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1)
- Header: [vktApiCopyDepthStencilMSAATests.hpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.hpp#L1)
- Parent registration: [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)

## Registration Path

```
api
  copy_and_blit
    core / dedicated_allocation
      depth_stencil_msaa_copy
```

## Test Hierarchy

```
depth_stencil_msaa_copy
  +-- whole
  |     +-- <format>_<srcLayout>_<dstLayout>_D_<samples>
  |     +-- <format>_<srcLayout>_<dstLayout>_D_<samples>_bind_offset
  |     +-- <format>_<srcLayout>_<dstLayout>_S_<samples>
  |     +-- <format>_<srcLayout>_<dstLayout>_S_<samples>_bind_offset
  +-- partial
  |     +-- <format>_D_<samples>
  |     +-- <format>_D_<samples>_bind_offset
  |     +-- <format>_S_<samples>
  |     +-- <format>_S_<samples>_bind_offset
  +-- array_to_array
        +-- <format>_D_<samples>
        +-- <format>_D_<samples>_bind_offset
        +-- <format>_S_<samples>
        +-- <format>_S_<samples>_bind_offset
```

## Test Families

### DepthStencilMSAA (instance)

Test instance inheriting directly from `vkt::TestInstance` ([line 35](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L35)), not from the `CopiesAndBlittingTestInstance` hierarchy. Uses a two-phase approach:

1. **Render phase**: Creates a multisampled depth/stencil source image, renders a triangle to it via a graphics pipeline, producing known depth/stencil values per sample ([line 226](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L226))
2. **Copy phase**: Issues `vkCmdCopyImage` or `vkCmdCopyImage2` to copy from source to destination image ([line 564](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L564))
3. **Verify phase**: Uses a verification shader that reads both source and destination images as input attachments, writes sample values to storage buffers, then CPU-compares the buffer contents sample-by-sample ([line 661](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661))

Three copy options are defined ([line 38](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L38)):
- `COPY_WHOLE_IMAGE`: Full image copy with layout variations
- `COPY_ARRAY_TO_ARRAY`: Copies between specific array layers (layer 2 to layer 3) in a 5-layer image
- `COPY_PARTIAL`: Copies two subregions (bottom-right to bottom-left, top-right to bottom-right) of the image

### DepthStencilMSAATestCase (case)

TestCase subclass ([line 1003](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1003)) that generates verification shaders via `initPrograms` ([line 1137](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1137)). The verification shader reads multisampled input attachments and writes per-sample values to storage buffers. For depth aspects, it uses `subpassInputMS`; for stencil, `usubpassInputMS` ([line 1080](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1080)).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Format | VK_FORMAT_D32_SFLOAT, VK_FORMAT_S8_UINT, VK_FORMAT_D16_UNORM_S8_UINT, VK_FORMAT_D24_UNORM_S8_UINT ([line 1179](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1179)) |
| Sample count | 2, 4, 8, 16, 32, 64 ([line 1169](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1169)) |
| Copy aspect | VK_IMAGE_ASPECT_DEPTH_BIT, VK_IMAGE_ASPECT_STENCIL_BIT |
| Copy option | COPY_WHOLE_IMAGE, COPY_PARTIAL, COPY_ARRAY_TO_ARRAY |
| Image offset | `false` (no bind offset), `true` (bind image with alignment offset) |
| Src image layout | VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL (whole copy only) |
| Dst image layout | VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL (whole copy only) |
| extensionFlags | From `testGroupParams`: NONE, COPY_COMMANDS_2 |
| allocationKind | From `testGroupParams`: ALLOCATION_KIND_SUBALLOCATION, ALLOCATION_KIND_DEDICATED |

## Support / Feature Requirements

- `fragmentStoresAndAtomics` device feature required ([line 1027](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1027))
- `framebufferDepthSampleCounts` must include the requested sample count for depth aspects ([line 1030](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1030))
- `framebufferStencilSampleCounts` must include the requested sample count for stencil aspects ([line 1034](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1034))
- Image format must support `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` ([line 1037](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1037))
- `_bind_offset` variant only generated when `allocationKind != ALLOCATION_KIND_DEDICATED` ([line 1219](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1219))

## Verification Methods

- GPU-based verification: A fragment shader reads source and destination images as multisampled input attachments, writes per-sample values to storage buffers ([line 661](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661))
- CPU comparison: After GPU verification pass, CPU reads back storage buffers and compares source vs. destination sample values coordinate-by-coordinate and sample-by-sample ([line 958](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L958))
- Partial copy: Additionally verifies that uncopied regions (top half) remain at the clear value (0) ([line 979](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L979))
- Array-to-array: Verifies that non-target layers in the destination contain only the clear value ([line 1113](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1113))

## Test Principles Observed

- Per-sample verification: Ensures every individual sample is correctly copied, not just the resolved value
- Subregion testing: Validates partial copies and array-layer copies, not just whole-image copies
- Layout variation: Tests both optimal transfer layouts and GENERAL layout for whole-image copies
- Bind offset: Tests images bound with a memory offset (alignment-based) to catch alignment-related bugs
- Shader-based verification: Avoids the complexity of reading back multisampled depth/stencil images on the CPU

## Notes / Uncertainties

- The `addCopyDepthStencilMSAATests` function signature differs from the other files: it takes `AllocationKind` and `uint32_t extensionFlags` directly rather than `TestGroupParamsPtr` ([line 1260](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260))
- Layout variations (GENERAL vs. TRANSFER_SRC/DST_OPTIMAL) are only tested for COPY_WHOLE_IMAGE to limit test count; partial and array copies use only optimal layouts ([line 1251](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1251))
- The `checkSupport` method checks `framebufferDepthSampleCounts` for both depth and stencil aspects, which may be a minor oversight since stencil should check `framebufferStencilSampleCounts` ([line 1034](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1034))
- The source image is initialized by rendering a triangle, not by uploading buffer data, which means the depth/stencil values are determined by the rendering pipeline rather than being precisely controlled
