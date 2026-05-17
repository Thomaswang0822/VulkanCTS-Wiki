# image_processing

## Overview

The [`image_processing`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L1) category documents Vulkan image processing tests registered by [`createTests()`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L83). In the inspected files, this category covers the `VK_QCOM_image_processing` extension, which provides hardware-accelerated block matching for both graphics and compute pipelines.

## Registration Entry Point

The category is rooted in [`createChildren()`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43), which adds three subgroups:

```text
image_processing
├── graphics
├── api
└── compute
```

Source: [`vktImageProcessingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktImageProcessingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L1) | Registration | Top-level image_processing category registration |
| [`vktImageProcessingApiTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L1) | Implementation | API property limit validation tests |
| [`vktImageProcessingBlockMatchingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1) | Implementation | Block matching tests for graphics and compute |
| [`vktImageProcessingBase.cpp`](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L1) | Helper | Shared base class for image processing tests |
| [`vktImageProcessingTestsUtil.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L1) | Helper | Format lists and utility functions |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktImageProcessingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L1) | [`vktImageProcessingTests.md`](../testfiles/image_processing/vktImageProcessingTests.md) |
| [`vktImageProcessingApiTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L1) | [`vktImageProcessingApiTests.md`](../testfiles/image_processing/vktImageProcessingApiTests.md) |
| [`vktImageProcessingBlockMatchingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1) | [`vktImageProcessingBlockMatchingTests.md`](../testfiles/image_processing/vktImageProcessingBlockMatchingTests.md) |

## Subgroup Structure and Major Themes

### [`graphics`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L48)

The graphics subgroup is further split by pipeline construction type:
- [`monolithic`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L54) — Full block matching test suite (basic, block_sizes, address_modes, reduction_modes, tiling, swizzles, layouts, shader_stages, descriptors)
- [`fast_lib`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L54) — Basic block matching only
- [`shader_objects`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L56) — Basic block matching only

Each pipeline variant contains a `block_matching` child group.

### [`api`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L139)

API property validation tests that verify `VkPhysicalDeviceImageProcessingPropertiesQCOM` minimum values against implementation-reported limits.

### [`compute`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L75)

Compute pipeline block matching tests with `basic` and `self` sub-groups.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Pipeline construction type | Monolithic, fast linked library, shader objects |
| Block matching target/reference sizes | 64x64, 32x32, 16x16, 8x8 |
| Block size | 4x4, 8x8, 16x16, 32x32 |
| Address mode | Clamp to edge, repeat, mirror |
| Reduction mode | Min, max, min/max |
| Tiling | Optimal, linear |
| Shader stages | Vertex, fragment |

## Recurring Support Requirements

- `VK_QCOM_image_processing` extension
- Vulkan 1.3+ or `VK_KHR_format_feature_flags2`
- `shaderStorageImageReadWithoutFormat` for compute path
- `shaderImageGatherExtended` for graphics path

## Recurring Verification Methods

- CPU reference computation vs GPU result comparison with error threshold
- Property limit validation against spec-defined minimums

## Notes / Uncertainties

- Format lists are determined at runtime by `getOpSupportedFormats()` in [`vktImageProcessingTestsUtil.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L1), so exact format coverage varies by implementation.
- Extended graphics sub-groups (block_sizes, address_modes, etc.) are only generated for the monolithic pipeline construction type.
