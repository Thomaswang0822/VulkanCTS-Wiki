# vktApiResolveTests

## Overview

Tests for `vkCmdResolveImage` and `vkCmdResolveImage2` (via `VK_KHR_copy_commands2`).
Resolving converts a multisampled image to a non-multisampled image by averaging sample values.
This file (~2600 lines) also tests intermediate copy operations on multisampled images before resolving.

## Role

- **Implementation-heavy test file**: contains test instance class, test case registration, and verification logic.

## Source Code

- [`vktApiResolveTests.cpp`](../../../modules/vulkan/api/vktApiResolveTests.cpp)
- [`vktApiResolveTests.hpp`](../../../modules/vulkan/api/vktApiResolveTests.hpp)
- [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp)

## Registration Hierarchy

```text
api.copy_and_blit.core.resolve_image
├── whole
├── partial
├── with_regions
├── whole_copy_before_resolving
├── whole_copy_before_resolving_no_cab
├── whole_copy_before_resolving_compute
├── whole_copy_before_resolving_transfer
├── diff_layout_copy_before_resolving
├── layer_copy_before_resolving
├── copy_with_regions_before_resolving
├── whole_array_image
├── whole_array_image_one_region
└── diff_image_size
```

Registered from [`addCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L121-L170),
which adds the direct `resolve_image` subgroup under variant roots such as `core`,
`dedicated_allocation`, and `copy_commands2` via
[`addTestGroup(group, "resolve_image", addResolveImageTests, ...)`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L137).
Within that Level-3 group, [`addResolveImageTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2588-L2608)
registers the exact direct child subgroups shown in the tree above. The queue-specific children are
registered as separate direct children in mustpass as `whole_copy_before_resolving_compute` and
`whole_copy_before_resolving_transfer`, rather than as a literal `compute_and_transfer_queue`
path component.

## Test Families

### whole — Whole-image resolve

Covers direct full-image resolves registered through
[`addResolveImageWholeTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2590).

### partial — Partial resolve regions

Covers partial resolve operations registered through
[`addResolveImagePartialTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2591).

### with_regions — Multi-region resolve

Covers region-based resolve variants registered through
[`addResolveImageWithRegionsTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2592).

### whole_copy_before_resolving — Full multisample copy before resolve

Covers cases that copy a multisampled image to another multisampled image before resolving,
registered through
[`addResolveImageWholeCopyBeforeResolvingTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2593-L2594).

### whole_copy_before_resolving_no_cab — Full multisample copy before resolve without CAB

Covers the no-concurrent-access-bit copy-before-resolve path registered through
[`addResolveImageWholeCopyWithoutCabBeforeResolvingTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2595-L2596).

### whole_copy_before_resolving_compute — Compute-queue copy before resolve

Covers compute-queue variants. Although the implementation calls
[`addComputeAndTransferQueueTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2597),
mustpass registration exposes a direct child subgroup named
`whole_copy_before_resolving_compute`.

### whole_copy_before_resolving_transfer — Transfer-queue copy before resolve

Covers transfer-queue variants added through the same queue-specialized registration path as the
compute cases. Mustpass registration exposes this direct child as
`whole_copy_before_resolving_transfer`.

### diff_layout_copy_before_resolving — Copy-before-resolve with different layouts

Covers variants registered through
[`addResolveImageWholeCopyDiffLayoutsBeforeResolvingTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2598-L2599)
that exercise layout differences before the resolve.

### layer_copy_before_resolving — Layer copy before resolve

Covers layer-specific multisample copy-before-resolve cases registered through
[`addResolveImageLayerCopyBeforeResolvingTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2600-L2601).

### copy_with_regions_before_resolving — Region-based copy before resolve

Covers copy-with-regions variants registered through
[`addResolveCopyImageWithRegionsTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2602-L2603).

### whole_array_image — Whole array-image resolve

Covers whole-array-image resolve cases registered through
[`addResolveImageWholeArrayImageTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2604).

### whole_array_image_one_region — Whole array-image resolve with one region

Covers single-region array-image resolve cases registered through
[`addResolveImageWholeArrayImageSingleRegionTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2605-L2606).

### diff_image_size — Resolve between different image sizes

Covers different-image-size resolve cases registered through
[`addResolveImageDiffImageSizeTests()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L2607).

### ResolveImageToImage — Core test implementation

- Inherits [`CopiesAndBlittingTestInstanceWithSparseSemaphore`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L474)
- Creates a multisampled source image, a non-multisampled destination, and optionally
  intermediate multisampled copy images
- Controlled by [`ResolveImageToImageOptions`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L36) enum:

| Option | Description |
|--------|-------------|
| `NO_OPTIONAL_OPERATION` | Simple resolve only |
| `COPY_MS_IMAGE_TO_MS_IMAGE` | Copy MS->MS before resolve |
| `COPY_MS_IMAGE_TO_ARRAY_MS_IMAGE` | Copy MS->array MS before resolve |
| `COPY_MS_IMAGE_LAYER_TO_MS_IMAGE` | Copy single layer MS->MS before resolve |
| `COPY_MS_IMAGE_TO_MS_IMAGE_MULTIREGION` | Multi-region MS->MS copy before resolve |
| `COPY_MS_IMAGE_TO_MS_IMAGE_NO_CAB` | MS->MS copy without concurrent access bit |
| `COPY_MS_IMAGE_TO_MS_IMAGE_COMPUTE` | MS->MS copy on compute queue |
| `COPY_MS_IMAGE_TO_MS_IMAGE_TRANSFER` | MS->MS copy on transfer queue |

### copyMSImageToMSImage — Intermediate copy helper

- Performs an intermediate copy between multisampled images before resolving
- Verifiable via [`checkIntermediateCopy()`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L63)

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Sample count | `VK_SAMPLE_COUNT_2_BIT`, `VK_SAMPLE_COUNT_4_BIT`, `VK_SAMPLE_COUNT_8_BIT`, `VK_SAMPLE_COUNT_16_BIT`, `VK_SAMPLE_COUNT_32_BIT`, `VK_SAMPLE_COUNT_64_BIT` |
| Image formats | Color formats supporting MSAA |
| Resolve regions | Whole, partial, multi-region |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2` |
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` |
| Queue type | Universal, compute-only, transfer-only |
| Array layers | Single layer, multi-layer, array image |
| Image sizes | Same size, different sizes |

## Support / Feature Requirements

- Multisampled image support for the chosen format and sample count
- `COPY_COMMANDS_2`: `VK_KHR_copy_commands2` or Vulkan 1.3
- Compute/transfer queue resolve requires appropriate queue family with support
- Checked via `checkExtensionSupport()` and format property queries

## Verification Methods

- CPU-side reference generated by averaging multisampled pixel values
  (via `FILL_MODE_MULTISAMPLE`)
- Result compared using `tcu::floatThresholdCompare()` or similar threshold-based comparison
- Intermediate copy verification via `checkIntermediateCopy()` when
  `shouldVerifyIntermediateResults()` returns true

## Test Principles

- Verify that `vkCmdResolveImage` correctly averages multisampled pixels into a
  non-multisampled destination
- Verify whole-image, partial, and multi-region resolves
- Verify resolve after intermediate MS->MS copy operations
  (testing concurrent access bit)
- Verify resolve on compute and transfer queues
- Verify array image resolve (whole and single-region)
- Verify resolve between images of different sizes
- Verify resolve with different image layouts before/after

## Notes / Uncertainties

- This page normalizes the `core` variant root because that registration path is directly present in
  mustpass and matches the canonical Level-3 hierarchy contract used by the validator. The same
  implementation also participates in sibling variant roots such as `dedicated_allocation` and
  `copy_commands2`.
- The exact sample counts tested vary per sub-function and were not exhaustively
  enumerated from the inspected code.
- The `copyMSImageToMSImage` path creates additional multisampled images and may use
  `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`; this was not fully inspected.
- The `diff_image_size` tests were not fully inspected beyond the registration function
  signature.
