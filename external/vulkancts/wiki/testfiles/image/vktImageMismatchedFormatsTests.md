# [vktImageMismatchedFormatsTests.cpp](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L1)

## Overview

[`vktImageMismatchedFormatsTests.cpp`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L1) is an implementation-heavy Level-3 file for the `image.mismatched_formats` subtree. It covers Vulkan image load/store operations where the Vulkan format differs from the SPIR-V image format representation. The tests validate that implementations correctly handle format mismatches that are compatible in terms of vector width, byte size, and channel class.

## Role of File

- **Role:** implementation-heavy test file.
- **Primary source:** [`vktImageMismatchedFormatsTests.cpp`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L1).
- **Registration context inspected:**
  - [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp) for placement under the top-level `image` category.
  - [`createImageMismatchedFormatsTests()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L478-L524) for the Level-3 root `image.mismatched_formats` and its exact direct children.

## Source Code

- Implementation: [vktImageMismatchedFormatsTests.cpp](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L1)
- Parent registration: [vktImageTests.cpp](../../../modules/vulkan/image/vktImageTests.cpp)

## Registration Hierarchy

```text
image.mismatched_formats
├── image_read
├── image_write
└── sparse_image_read (non-VulkanSC only)
```

The confirmed Level-3 root is `image.mismatched_formats`, created by [`createImageMismatchedFormatsTests()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L478-L524). The exact direct children are `image_read`, `image_write`, and `sparse_image_read` (the latter is excluded for VulkanSC builds via preprocessor).

## Test Families

### image_read — OpImageRead with mismatched formats

Covers the `image_read` direct child registered by [`createImageMismatchedFormatsTests()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L483-L484). This group tests the [`imageLoad()`](https://www.khronos.org/registry/vulkan/specs/1.3-extensions/man/html/imageLoad.html) GLSL builtin with SPIR-V image formats that differ from the underlying Vulkan image format.

The test class [`MismatchedFormatTest`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L231-L245) with `TestType::READ` generates GLSL shaders that perform [`imageLoad()`](https://www.khronos.org/registry/vulkan/specs/1.3-extensions/man/html/imageLoad.html) operations.

### image_write — OpImageWrite with mismatched formats

Covers the `image_write` direct child registered by [`createImageMismatchedFormatsTests()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L484). This group tests the [`imageStore()`](https://www.khronos.org/registry/vulkan/specs/1.3-extensions/man/html/imageStore.html) GLSL builtin with mismatched formats.

The test class [`MismatchedFormatTest`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L231-L245) with `TestType::WRITE` generates GLSL shaders that perform [`imageStore()`](https://www.khronos.org/registry/vulkan/specs/1.3-extensions/man/html/imageStore.html) operations.

### sparse_image_read — Sparse OpImageRead with mismatched formats (non-VulkanSC)

Covers the `sparse_image_read` direct child registered by [`createImageMismatchedFormatsTests()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L486-L487). This group tests sparse texture read operations with mismatched formats using the [`GL_ARB_sparse_texture2`](https://www.opengl.org/registry/specs/ARB/sparse_texture2.txt) extension.

The test class [`MismatchedFormatTest`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L231-L245) with `TestType::SPARSE_READ` generates GLSL shaders using `sparseImageLoadARB()`.

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Level-3 direct children | `image_read`, `image_write`, `sparse_image_read` | [`createImageMismatchedFormatsTests()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L478-L524) |
| Vulkan formats tested | All non-compressed Vulkan formats from `VK_FORMAT_R4G4_UNORM_PACK8` to `VK_CORE_FORMAT_LAST` | [`for loop`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L489-L490) |
| SPIR-V formats tested | 46 formats in `SpirvFormats` map | [`SpirvFormats`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L129-L168) |
| Format matching criteria | Same vector width, same bytes per pixel, same channel class | [`matching()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L179-L194) |
| SPIR-V format categories | Floating-point, unsigned fixed-point, signed fixed-point, signed integer, unsigned integer | [`SpirvFormats`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L129-L168) |
| Image type | 2D only | [`VK_IMAGE_TYPE_2D`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L213) |
| Image extent | 8x8x1 | [`makeExtent3D(8, 8, 1)``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L215) |
| Image usage | `VK_IMAGE_USAGE_STORAGE_BIT`, `VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, `VK_IMAGE_USAGE_TRANSFER_DST_BIT` | [`fillImageCreateInfo()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L220-L221) |
| Dispatch dimensions | 8x8x1 workgroups | [`vk.cmdDispatch(*cmdBuffer, 8, 8, 1)``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L457) |
| GLSL image types | `image2D`, `uimage2D`, `iimage2D` | [`ChannelClassToImageType()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L90-L100) |
| GLSL vector types | `vec4`, `uvec4`, `ivec4` | [`ChannelClassToVecType()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L103-L113) |

## Support / Feature Requirements

Observed support gates and extension-dependent coverage include:

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `DEVICE_CORE_FEATURE_SPARSE_BINDING` | Required for `TestType::SPARSE_READ` | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L264-L266) |
| `sparseResidencyBuffer` | Required for sparse read tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L266-L267) |
| `shaderResourceResidency` | Required for sparse read tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L278-L281) |
| Sparse format support | Checked via `checkSparseImageFormatSupport()` | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L273-L276) |
| `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` | Required for all tests | [`checkSupport()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L288-L291) |
| `GL_ARB_sparse_texture2` | Required for sparse read shader compilation | [`initPrograms()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L328) |

## Verification Methods

- **Shader compilation success:** Tests verify that SPIR-V shaders with mismatched formats compile successfully.
- **Pipeline creation success:** Tests verify that compute pipelines with mismatched format descriptors can be created.
- **Dispatch execution:** Tests execute a single `vkCmdDispatch` call with the mismatched format configuration.
- **Pass criteria:** Tests return `tcu::TestStatus::pass("Passed")` if dispatch completes without error.

## Test Principles Observed

- **Format matching considers multiple dimensions.** The [`matching()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L179-L194) function checks three criteria: vector width (number of components), bytes per pixel, and channel class (float, signed integer, unsigned integer, etc.).
- **Tests iterate all Vulkan format/SPIR-V format combinations.** For each Vulkan format, all SPIR-V formats are checked for compatibility, and test cases are created for matching pairs.
- **Sparse tests require additional feature checks.** Sparse read tests require sparse binding, sparse residency buffer, and shader resource residency features, plus explicit format support validation.
- **Compressed formats are excluded.** The test loop explicitly skips compressed formats with [`isCompressedFormat()``](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L492-L493).

## Notes / Uncertainties

- The `SpirvFormats` map contains 46 SPIR-V format definitions covering floating-point, fixed-point, and integer channel classes.
- Test names are generated from format names, e.g., `rgba32f_with_rgba32f` for matching formats.
- The `sparse_image_read` group is excluded for VulkanSC builds via `#ifndef CTS_USES_VULKANSC`.
- Sparse image allocation uses `allocateAndBindSparseImage()` helper which handles semaphore creation and memory binding.
