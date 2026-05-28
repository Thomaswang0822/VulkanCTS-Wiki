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

The graphics subgroup creates three pipeline-construction branches from the `constructionTypes[]` table:

| Registered branch | Pipeline construction type | Block-matching content |
|---|---|---|
| `monolithic` | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` at [`vktImageProcessingTests.cpp#L54`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L54) | `block_matching` with `basic` plus the monolithic-only extended graphics groups guarded at [`vktImageProcessingBlockMatchingTests.cpp#L2004-L2006`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2006). |
| `fast_lib` | `PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY` at [`vktImageProcessingTests.cpp#L55`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L55) | `block_matching` with the `basic` group; the extended graphics groups are skipped by the monolithic guard. |
| `shader_objects` | `PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_UNLINKED_SPIRV` at [`vktImageProcessingTests.cpp#L56`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L56) | `block_matching` with the `basic` group; the extended graphics groups are skipped by the monolithic guard. |

Each branch receives a `block_matching` child through [`createImageProcessingBlockMatchingGraphicsTests()`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L61-L62), and that factory creates the group named `block_matching` at [`vktImageProcessingBlockMatchingTests.cpp#L1885`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1885).

### [`api`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L139)

The API subgroup registers one `properties` test at [`vktImageProcessingApiTests.cpp#L141`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L141). It queries `VkPhysicalDeviceImageProcessingPropertiesQCOM` and checks minimum values for `maxWeightFilterPhases`, `maxWeightFilterDimension`, `maxBoxFilterBlockSize`, and `maxBlockMatchRegion` at [`vktImageProcessingApiTests.cpp#L101-L124`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L101-L124).

### [`compute`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L75)

The compute subgroup adds `block_matching` through [`createImageProcessingBlockMatchingComputeTests()`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L76). In the common block-matching factory, compute cases always get the `basic` group at [`vktImageProcessingBlockMatchingTests.cpp#L1958-L2001`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1958-L2001), and the compute-only `self` group is added under the `testCompute` branch at [`vktImageProcessingBlockMatchingTests.cpp#L2221-L2248`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248).

## Parameter Dimensions and Registration Names

| Dimension | Source-backed values / names |
|---|---|
| Operations | `sad` and `ssd`, registered from `ImageProcOp::IMAGE_PROC_OP_BLOCK_MATCH_SAD` and `ImageProcOp::IMAGE_PROC_OP_BLOCK_MATCH_SSD` at [`vktImageProcessingBlockMatchingTests.cpp#L1893-L1898`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1893-L1898). |
| Pipeline construction branches | `monolithic`, `fast_lib`, and `shader_objects` from the graphics dispatcher table at [`vktImageProcessingTests.cpp#L54-L56`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L54-L56). |
| Basic-case names | `{format}_same`, `{format}_diff`, optional `_random`, and `_constdiff` suffixes are assembled at [`vktImageProcessingBlockMatchingTests.cpp#L1967-L1982`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1967-L1982). |
| Default target/reference image setup | `IMAGE_TYPE_2D`, `64x64`, selected format, `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`, identity components, `VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE`, and `SAMPLER_REDUCTION_MODE_NONE` at [`vktImageProcessingBlockMatchingTests.cpp#L1662-L1675`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1662-L1675). |
| Default block-match coordinates and block size | `targetCoord = 0,0`, `referenceCoord = 0,0`, and `blockSize = 32x32` at [`vktImageProcessingBlockMatchingTests.cpp#L1677-L1682`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1677-L1682). |
| `block_sizes` graphics cases | `params0` through `params4`, generated from non-zero coordinates, `1x1`, `64x64`, and `1x64` block-size entries at [`vktImageProcessingBlockMatchingTests.cpp#L1817-L1874`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1817-L1874). |
| `address_modes` graphics cases | `clamp_to_edge` and `clamp_to_border`, the actual registered name prefixes in `addressModes[]` at [`vktImageProcessingBlockMatchingTests.cpp#L1900-L1906`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1900-L1906); address-mode parameter variants include the `40x40`, `16x16` target / `32x32` reference, and `targetCoord = 64,64` cases at [`vktImageProcessingBlockMatchingTests.cpp#L1699-L1740`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1699-L1740). |
| `reduction_modes` graphics cases | Registered prefixes `weighted_average`, `min`, and `max` from `reductionModes[]` at [`vktImageProcessingBlockMatchingTests.cpp#L1908-L1914`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1908-L1914). Each reference reduction mode is combined with target reduction modes from `SAMPLER_REDUCTION_MODE_NONE` through `SAMPLER_REDUCTION_MODE_MAX` at [`vktImageProcessingBlockMatchingTests.cpp#L1743-L1761`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1743-L1761). |
| `tiling` graphics cases | Registered prefixes `optimal` and `linear` from `tilingTypes[]` at [`vktImageProcessingBlockMatchingTests.cpp#L1916-L1920`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1916-L1920). The generator skips the both-optimal case because basic tests already cover it at [`vktImageProcessingBlockMatchingTests.cpp#L1775-L1785`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1775-L1785). |
| `layouts` graphics cases | Registered prefixes `rdonly_optimal` and `general` from `layouts[]` at [`vktImageProcessingBlockMatchingTests.cpp#L1922-L1926`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1922-L1926). The generator skips the both-`VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` case because basic tests already cover it at [`vktImageProcessingBlockMatchingTests.cpp#L1800-L1811`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1800-L1811). |
| `swizzles` graphics cases | Registered names `bgra`, `g01a`, and `rbg1` from `swizzles[]` at [`vktImageProcessingBlockMatchingTests.cpp#L1928-L1943`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1928-L1943). |
| `shader_stages` graphics cases | `vertex` is the additional graphics shader-stage case; the source notes that fragment-stage coverage is already in basic tests at [`vktImageProcessingBlockMatchingTests.cpp#L1945-L1949`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1945-L1949). |
| `descriptors` graphics cases | `updateAfterBind_same`, `updateAfterBind_diff`, and optional `_random` suffixes are generated from the descriptor loop at [`vktImageProcessingBlockMatchingTests.cpp#L2192-L2216`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2192-L2216). |
| `self` compute cases | `same`, `diff`, and optional `_random` suffixes are generated for compute self-tests at [`vktImageProcessingBlockMatchingTests.cpp#L2221-L2248`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248). |
| Block-matching formats | `getOpSupportedFormats()` returns `VK_FORMAT_R8_UNORM`, `VK_FORMAT_R8G8_UNORM`, `VK_FORMAT_R8G8B8_UNORM`, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_A8B8G8R8_UNORM_PACK32`, and `VK_FORMAT_A2B10G10R10_UNORM_PACK32` for `sad` / `ssd` at [`vktImageProcessingTestsUtil.cpp#L408-L435`](../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435). |

## Support / Feature Requirements by Code Path

| Scope | Support gates / checks |
|---|---|
| API `properties` test | If the API version is below Vulkan 1.3, the test requires `VK_KHR_format_feature_flags2`; it also requires `VK_QCOM_image_processing` at [`vktImageProcessingApiTests.cpp#L66-L72`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L66-L72). |
| Shared image-processing test base | Block-matching tests use `ImageProcessingTest::checkSupport()`, which requires `VK_KHR_format_feature_flags2` below Vulkan 1.3 and `VK_QCOM_image_processing` at [`vktImageProcessingBase.cpp#L92-L100`](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L92-L100). |
| `sad` / `ssd` block-matching operation | The shared base checks `textureBlockMatch` and `VK_FORMAT_FEATURE_2_BLOCK_MATCHING_BIT_QCOM` for the sampled/reference image format and selected tiling at [`vktImageProcessingBase.cpp#L108-L123`](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L108-L123). |
| Target image in block-matching tests | `ImageProcessingBlockMatchTest::checkSupport()` also checks `VK_FORMAT_FEATURE_2_BLOCK_MATCHING_BIT_QCOM` for the target image format and selected tiling at [`vktImageProcessingBlockMatchingTests.cpp#L165-L177`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L165-L177). |
| Graphics output image | Graphics block-matching cases require `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT`, successful `vkGetPhysicalDeviceImageFormatProperties()` for transfer-source plus color-attachment usage, and pipeline-construction requirements at [`vktImageProcessingBlockMatchingTests.cpp#L240-L272`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L240-L272). |
| Compute output image | Compute block-matching cases require `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT`, successful `vkGetPhysicalDeviceImageFormatProperties()` for transfer-source plus storage-image usage, and output dimensions within `maxComputeWorkGroupCount` at [`vktImageProcessingBlockMatchingTests.cpp#L1160-L1193`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1160-L1193). |
| Descriptor update-after-bind cases | Cases that set `updateAfterBind` require `VK_EXT_descriptor_indexing` and `descriptorBindingSampledImageUpdateAfterBind` in the shared base at [`vktImageProcessingBase.cpp#L163-L168`](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L163-L168); those cases are generated in the `descriptors` group at [`vktImageProcessingBlockMatchingTests.cpp#L2192-L2216`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2192-L2216). |

## Verification Methods

- API `properties` verifies `VkPhysicalDeviceImageProcessingPropertiesQCOM` minimums and fails if any inspected property is below the coded threshold at [`vktImageProcessingApiTests.cpp#L93-L127`](../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L93-L127).
- Block-matching tests compare the GPU result image against a CPU-built reference image with exact image threshold `(0,0,0,0)` and compare the computed error metric against `errorThreshold` in [`ImageProcessingTestInstance::verifyResult()`](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L237-L272).

## Notes / Uncertainties

- The inspected category currently registers only block-matching operations (`sad` and `ssd`) even though the shared base has support branches for sample-weighted and box-filter operations at [`vktImageProcessingBase.cpp#L125-L157`](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L125-L157).
- Extended graphics groups (`block_sizes`, `address_modes`, `reduction_modes`, `tiling`, `swizzles`, `layouts`, `shader_stages`, and `descriptors`) are generated only when `testCompute` is false and the pipeline construction type is `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` at [`vktImageProcessingBlockMatchingTests.cpp#L2004-L2006`](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2006).
- Per-device format support is checked at runtime even though `getOpSupportedFormats()` supplies a fixed candidate format list at [`vktImageProcessingTestsUtil.cpp#L408-L435`](../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435).
