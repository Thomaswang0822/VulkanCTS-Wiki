# [vktApiImageClearingTests.cpp](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1)

## Overview

[`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.image_clearing` subtree. It covers Vulkan image clearing through [`vkCmdClearColorImage`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2531-L2838), [`vkCmdClearDepthStencilImage`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2840-L2954), and [`vkCmdClearAttachments`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2956-L3187), with one top-level branch for suballocated memory and one for dedicated allocation. Within those branches, the generator expands image type, tiling, layer configuration, dimensions, format families, clear-value variants, separate depth/stencil layout modes, partial-clear modes, and selected multisample variants.

## Role of File

- **Role:** implementation-heavy test file.
- **Primary source:** [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1).
- **Registration context inspected:**
  - [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L110) for placement under the top-level `api` category.
  - [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204-L3214) for the Level-3 root `api.image_clearing` and its exact direct children.
  - [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224-L3190) for the deeper subgroup structure shared by `core` and `dedicated_allocation`.

## Source Code

- Implementation: [vktApiImageClearingTests.cpp](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1)
- Header: [vktApiImageClearingTests.hpp](../../../modules/vulkan/api/vktApiImageClearingTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L110)

## Registration Hierarchy

```text
api.image_clearing
├── core
└── dedicated_allocation
```

The confirmed Level-3 root is `api.image_clearing`, created by [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204-L3214) and registered under `api` in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L110). The exact direct children are `core` and `dedicated_allocation`; both delegate to the same generator in [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224-L3190) with different [`AllocationKind`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224-L2225) values.

## Test Families

### core — Suballocated image-clearing matrix

Covers the `core` direct child registered by [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3208-L3212). This branch calls [`createCoreImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3192-L3195), which forwards [`ALLOCATION_KIND_SUBALLOCATED`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3194) into [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224-L3190).

Observed deeper descendants under `core` are the exact subgroup names created in [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2227-L2235): `clear_color_image`, `clear_depth_stencil_image`, `clear_color_attachment`, `clear_depth_stencil_attachment`, `partial_clear_color_attachment`, and `partial_clear_depth_stencil_attachment`. Those subgroups then expand further through nested loops over image types, tilings, layer configurations, dimensions, formats, clear-color parameter sets, and a few special-case suffix generators such as `_multiple_subresourcerange`, `_separate_layouts_depth`, `_separate_layouts_stencil`, and multisample suffixes from [`getSampleCountName()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2703-L2734).

### dedicated_allocation — Dedicated-memory mirror of the same clearing matrix

Covers the `dedicated_allocation` direct child registered by [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3210-L3212). This branch calls [`createDedicatedAllocationImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3197-L3200), which reuses the same generator but passes [`ALLOCATION_KIND_DEDICATED`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3199).

The deeper subgroup structure under `dedicated_allocation` is therefore the same six-way branch described for `core`, because both children are built from the same subgroup creation code in [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2227-L2235). The distinction is allocation strategy rather than separate registration names or different command coverage.

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Level-3 direct child | `core`, `dedicated_allocation` | [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204-L3214) |
| Shared deeper subgroup names | `clear_color_image`, `clear_depth_stencil_image`, `clear_color_attachment`, `clear_depth_stencil_attachment`, `partial_clear_color_attachment`, `partial_clear_depth_stencil_attachment` | [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2227-L2235) |
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | [`createCoreImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3192-L3195), [`createDedicatedAllocationImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3197-L3200) |
| Color-image image type | `VK_IMAGE_TYPE_1D`, `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TYPE_3D` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2533-L2534) |
| Depth/stencil-image image type | `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TYPE_3D` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2842-L2843) |
| Image tiling | `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_TILING_LINEAR` for clear-color-image cases; attachment clears use optimal tiling | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2536-L2540), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3027-L3030), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3145-L3148) |
| Color formats | Explicit table from `VK_FORMAT_R4G4_UNORM_PACK8` through `VK_FORMAT_A4B4G4R4_UNORM_PACK16_EXT`, with several compressed and some 64-bit float formats commented out | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2237-L2425) |
| Depth/stencil formats | `VK_FORMAT_D16_UNORM`, `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_S8_UINT`, `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2428-L2431) |
| Clear-color parameter set | default pair with no suffix and unsigned-fixed-point clamp-input pair with `_clamp_input` suffix | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2433-L2465) |
| Layer configuration names | `single_layer`, `multiple_layers`, `cube_layers`, `remaining_array_layers`, `remaining_array_layers_twostep` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2471-L2519) |
| Attachment-layer subset | excludes the last two `VK_REMAINING_ARRAY_LAYERS` configurations for attachment clears | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2521-L2525) |
| Image dimensions | `256x1x1`, `256x256x1`, `256x256x16`, `200x1x1`, `200x180x1`, `200x180x16`, `71x1x1`, `1x33x1`, `55x21x11`, `64x11x1`, `33x128x1`, `32x29x3` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2527-L2529) |
| Separate depth/stencil layout mode | none for pure depth or pure stencil formats; none, depth-only, stencil-only for combined depth/stencil formats | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2875-L2891), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3125-L3141) |
| 3D image 2D-array-compatible flag | `false`, `true` on selected 3D clear-color-image cases | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2662-L2672) |
| General-layout mode | `false`, `true` on selected 2D clear-color-image and color-attachment cases | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2674-L2682), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3056-L3059) |
| Multisample counts | `VK_SAMPLE_COUNT_4_BIT` for selected clear-color-image cases; `VK_SAMPLE_COUNT_2_BIT`, `4_BIT`, `8_BIT`, `16_BIT`, `32_BIT`, `64_BIT` for selected color-attachment clears | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2467-L2469), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2703-L2734), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3071-L3086) |
| Generated suffix patterns | `_clamp_input`, `_multiple_subresourcerange`, `_separate_layouts_depth`, `_separate_layouts_stencil`, sample-count suffixes such as `_4_samples` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2453-L2456), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2692-L2700), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2884-L2891), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3076-L3079) |

## Support / Feature Requirements

Observed support gates and extension-dependent coverage include:

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `VK_EXT_separate_depth_stencil_layouts` | cases using non-default separate depth/stencil layout modes | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2878-L2891), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3128-L3141) |
| `VK_KHR_maintenance1`-style 2D-array-compatible 3D image behavior | selected 3D clear-color-image cases that set `create2DArrayCompatible = true` | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2662-L2672) |
| `VK_EXT_4444_formats` | extension-only `VK_FORMAT_A4R4G4B4_UNORM_PACK16_EXT` and `VK_FORMAT_A4B4G4R4_UNORM_PACK16_EXT` color formats in the explicit format table | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2423-L2424) |

The inspected generator code clearly exposes these dependencies through the registered parameter space, but this normalization pass did not re-audit every runtime `checkSupport()` branch elsewhere in the file beyond the registration-relevant construction loops requested for hierarchy normalization.

## Verification Methods

- **Image-content comparison after clear:** the generated cases construct expected clear values directly from the same parameters used to create the commands, including alternative expected values for clamp-input cases in [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2442-L2465).
- **Multiple-subresource-range validation:** dedicated `_multiple_subresourcerange` branches are registered for both color and combined depth/stencil image clears when the generator enables that path in [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2689-L2700) and [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2927-L2937).
- **Two-step `VK_REMAINING_ARRAY_LAYERS` coverage:** the `remaining_array_layers_twostep` layer configuration drives alternate test-instance classes for both color and depth/stencil image clears in [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2737-L2743) and [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2939-L2945).
- **Partial-clear attachment validation:** partial render-pass clears are registered separately through [`PartialClearAttachmentTestInstance`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3065-L3069) and [`PartialClearAttachmentTestInstance`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3173-L3177).

## Test Principles Observed

- **Allocation strategy is treated as a first-class axis at the Level-3 root.** The exact direct children are split into `core` and `dedicated_allocation`, while deeper subgroup names remain the same through the shared generator in [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204-L3214) and [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2224-L3190).
- **Command coverage is organized by clearing mechanism, not by format family alone.** The generator creates separate roots for image clears, attachment clears, and partial attachment clears in [`createImageClearingTestsCommon()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2227-L2235).
- **Generated names encode behavioral variants rather than duplicating structural nodes in the registration tree.** Examples include `_clamp_input`, `_multiple_subresourcerange`, separate-layout suffixes, and sample-count suffixes from [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2453-L2456), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2692-L2700), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2884-L2891), and [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3076-L3079).
- **The generator deliberately prunes invalid shape combinations.** Examples include skipping multi-layer 3D clear-color-image cases, skipping cube-image clear-image cases, filtering dimensions that do not match the selected image type, and restricting attachment clears to 2D-compatible dimensions in [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2555-L2562), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2574-L2580), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2853-L2870), [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2974-L2978), and [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3116-L3120).

## Notes / Uncertainties

- This normalization confirms the Level-3 root as `api.image_clearing`, not just `api -> image_clearing`, because the canonical contract requires the category-qualified root from [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L3204-L3214).
- The exact direct children are only `core` and `dedicated_allocation`; subgroup names such as `clear_color_image` and `clear_depth_stencil_image` are deeper descendants described in prose rather than expanded in the parseable tree.
- Several compressed and larger 64-bit formats are present only as commented-out candidates in the explicit format table because of noted `tcu::TextureFormat` limitations in [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L2237-L2425).
- This pass intentionally normalized only [`vktApiImageClearingTests.md`](vktApiImageClearingTests.md) and did not modify adjacent files.
