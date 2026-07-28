## Overview

**Core question:** Does the implementation's reported `maxCombinedImageSamplerDescriptorCount` from `VK_KHR_maintenance6` bound every per-format `combinedImageSamplerDescriptorCount` reported for YCbCr and related formats?

- [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp) implements the `api.maintenance6_check` test family, registered under the `api` test category by [vktApiTests.cpp#L131](../../../modules/vulkan/api/vktApiTests.cpp#L131).
- The test family registers exactly one CTS test case leaf, `maintenance6_properties`, behind `#ifndef CTS_USES_VULKANSC`.
- The test queries two device properties and compares them: `VkPhysicalDeviceMaintenance6PropertiesKHR::maxCombinedImageSamplerDescriptorCount`, and the per-format `VkSamplerYcbcrConversionImageFormatProperties::combinedImageSamplerDescriptorCount` for every format in three YCbCr-related format ranges.
- Passing requires every per-format value to be less than or equal to the maintenance6 limit. The test is purely host-side; no shaders, pipelines, or GPU work are involved.

## Background Knowledge

- **`maxCombinedImageSamplerDescriptorCount`.** `VK_KHR_maintenance6` adds `VkPhysicalDeviceMaintenance6PropertiesKHR`, whose `maxCombinedImageSamplerDescriptorCount` field reports an implementation-wide upper bound on the descriptor count that any single combined image sampler can consume. Applications can size descriptor set layouts against this single limit instead of scanning per-format values.
- **Per-format `combinedImageSamplerDescriptorCount`.** `VK_KHR_sampler_ycbcr_conversion` (core in Vulkan 1.1) exposes `VkSamplerYcbcrConversionImageFormatProperties`, which is queried through `getPhysicalDeviceImageFormatProperties2` and reports, for a specific image format, how many descriptor slots a combined image sampler using a `VkSamplerYcbcrConversion` on that format occupies. Multi-planar YCbCr formats typically report a count greater than one.
- **The maintenance6 consistency contract.** The maintenance6 limit is useful as a single sizing bound only if it is at least as large as every per-format value the implementation can report. This test verifies that contract across the format set CTS treats as YCbCr-capable.

## Registration Hierarchy

```text
api.maintenance6_check
└── maintenance6_properties (non-VulkanSC only)
```

The hierarchy is small: one test case leaf directly under the `maintenance6_check` test family, with no intermediate nodes. The leaf is registered only on non-VulkanSC builds; the entire source file is guarded by `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

This page has no generated parameter matrix. The values below are fixed inputs to the single `maintenance6_properties` case; the path has no intermediate nodes between the `maintenance6_check` test family and the final test case leaf.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format ranges | YCbCr formats, YCbCr extended formats, `VK_FORMAT_R16G16_S10_5_NV` | Each range contributes formats whose per-format `combinedImageSamplerDescriptorCount` must be bounded by the maintenance6 limit. | [s_formatRanges](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L68-L81) |
| Image type | `VK_IMAGE_TYPE_2D` | Fixed `VkPhysicalDeviceImageFormatInfo2` input; per-format descriptor count is queried only for 2D images. | [imageInfo](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L96) |
| Tiling | `VK_IMAGE_TILING_OPTIMAL` | Fixed; only optimal-tiling 2D images are queried for the per-format descriptor count. | [imageInfo](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L97) |
| Usage | `VK_IMAGE_USAGE_TRANSFER_DST_BIT` | Fixed usage flag passed to `getPhysicalDeviceImageFormatProperties2`. | [imageInfo](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L98) |
| Flags | `0U` | No creation flags; the query reflects the base format properties. | [imageInfo](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L98) |

The three format ranges are:

- YCbCr formats: `VK_FORMAT_G8B8G8R8_422_UNORM` through `VK_FORMAT_G16_B16_R16_3PLANE_444_UNORM`.
- YCbCr extended formats: `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM` through `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM`.
- `VK_FORMAT_R16G16_S10_5_NV` as a single-format range.

Each range is half-open: the loop iterates from `begin` up to but not including `end`, where `end` is the format after the last one to test.

## Behavior Parameters

There is no multi-value behavioral axis under the `maintenance6_check` test family. The registered path goes directly from `api.maintenance6_check` to the single `maintenance6_properties` case leaf, so the behavior parameter is the fixed leaf.

The `maintenance6_properties` case performs one property comparison repeated across the three format ranges listed above. For each format, it queries `VkSamplerYcbcrConversionImageFormatProperties::combinedImageSamplerDescriptorCount` through `getPhysicalDeviceImageFormatProperties2` using a fixed `VkPhysicalDeviceImageFormatInfo2` of `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_USAGE_TRANSFER_DST_BIT`, and no creation flags. It compares the per-format value against `VkPhysicalDeviceMaintenance6PropertiesKHR::maxCombinedImageSamplerDescriptorCount`, which it queried once at the start of the iteration through `getPhysicalDeviceProperties2`.

## Shader Analysis

No shader is involved in this test family. The case is a host-side property consistency check between two reported values from `getPhysicalDeviceProperties2` and `getPhysicalDeviceImageFormatProperties2`.

## Runtime Execution and Result Checking

- The test instance queries `VkPhysicalDeviceMaintenance6PropertiesKHR` through the `pNext` chain of `VkPhysicalDeviceProperties2` via `getPhysicalDeviceProperties2`, reading `maxCombinedImageSamplerDescriptorCount` once at the start of the iteration [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L60-L66).
- It then iterates three format ranges defined as begin/end pairs. For each format in each range, it chains `VkSamplerYcbcrConversionImageFormatProperties` into `VkImageFormatProperties2` and calls `getPhysicalDeviceImageFormatProperties2` with the fixed image type, tiling, usage, and flags described above [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L83-L99).
- The pass/fail condition is evaluated per format: if `conversionImageFormatProps.combinedImageSamplerDescriptorCount` exceeds `maintProp6.maxCombinedImageSamplerDescriptorCount`, the test returns `tcu::TestStatus::fail` immediately, with a message naming the offending format and reporting both values [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L100-L109).
- If the loop completes without any format exceeding the bound, the test returns `tcu::TestStatus::pass("Pass")` [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L113).
- The first offending format terminates the test, so a single failure log entry is produced per failing run.

The test does not create any images, samplers, descriptor sets, or GPU work. It relies solely on the implementation's reported property values.

## Failure Meaning

### Failure Cause Mapping

Because `api.maintenance6_check.maintenance6_properties` is a single fixed case with no multi-value behavioral axis, any failure points to the same property comparison: a per-format descriptor count exceeded the maintenance6 limit.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `maintenance6_properties` | A per-format `combinedImageSamplerDescriptorCount` exceeded `maxCombinedImageSamplerDescriptorCount`, indicating the maintenance6 limit is reported too low or a per-format descriptor count is reported too high. |

### Cause Analysis

#### Per-format descriptor count exceeds the maintenance6 limit

**Possible failure symptoms:** The test returns `tcu::TestStatus::fail` with a message of the form `Fail: format <name> requires a larger combinedImageSamplerDescriptorCount=<per-format value> than maxCombinedImageSamplerDescriptorCount=<limit>`, naming the first offending format and both values [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L103-L108). The loop exits on the first offending format, so only one format is reported per failing run.

**Possible implementation causes:** A failure indicates the implementation's reported maintenance6 limit is not large enough to bound the per-format descriptor count for at least one YCbCr or related format. This is a property-consistency violation between two values the implementation reports independently. Grounded investigation should compare the reported `maxCombinedImageSamplerDescriptorCount` against every per-format `combinedImageSamplerDescriptorCount` the implementation reports for the formats enumerated by the test, and confirm that the `VkSamplerYcbcrConversionImageFormatProperties` struct in the `pNext` chain of `VkImageFormatProperties2` was populated rather than silently ignored. The test does not verify pNext-chain support: if the implementation ignored the chain, the field would remain at its `initVulkanStructure()` zero value, which would not by itself trigger a failure. A failure therefore implies the chain was populated and the per-format value exceeded the maintenance6 limit.

## Case Pruning

### Requirement-based pruning

- The case requires the `VK_KHR_maintenance6` extension through `checkSupport`, so it is reported as unsupported rather than failed when the extension is absent [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L128-L131).
- The entire source file is guarded by `#ifndef CTS_USES_VULKANSC`, so the case is not registered on VulkanSC builds [vktApiMaintenance6Check.cpp](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L39).

### Design-based pruning

- The format scan is limited to three ranges: YCbCr formats, YCbCr extended formats, and `VK_FORMAT_R16G16_S10_5_NV`. Formats that do not accept a `VkSamplerYcbcrConversion` are not enumerated, because their `combinedImageSamplerDescriptorCount` is not relevant to the maintenance6 bound.
- The image type, tiling, usage, and flags are fixed to `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_USAGE_TRANSFER_DST_BIT`, and `0U`. Other configurations are not tested, because the maintenance6 limit applies to the per-format descriptor count independently of these dimensions.
- The loop exits on the first offending format rather than accumulating all violations. This is a reporting choice, not a coverage restriction: every format is examined until the first failure.

## Key Takeaways

- `api.maintenance6_check.maintenance6_properties` is a single fixed case checking that the maintenance6 `maxCombinedImageSamplerDescriptorCount` is at least as large as every per-format `combinedImageSamplerDescriptorCount` reported for the YCbCr formats, YCbCr extended formats, and `VK_FORMAT_R16G16_S10_5_NV`.
- The test is non-VulkanSC only and requires `VK_KHR_maintenance6`.
- The test is purely host-side: it queries two property structs through `getPhysicalDeviceProperties2` and `getPhysicalDeviceImageFormatProperties2` and compares their values, with no shader, pipeline, or GPU work.
- See `## Failure Meaning` for the failure interpretation: a failure means a property-consistency violation between the maintenance6 limit and a per-format descriptor count, with the first offending format named in the failure message.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [vktApiTests.cpp#L131](../../../modules/vulkan/api/vktApiTests.cpp#L131) | Attaches `maintenance6_check` as a child of the `api` test category. |
| Test family factory | [vktApiMaintenance6Check.cpp#L142-L149](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L142-L149) | Creates the `maintenance6_check` group and adds the `maintenance6_properties` test case leaf. |
| Header declaration | [vktApiMaintenance6Check.hpp#L38](../../../modules/vulkan/api/vktApiMaintenance6Check.hpp#L38) | Declares `createMaintenance6Tests`. |
| Test case leaf class | [vktApiMaintenance6Check.cpp#L117-L138](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L117-L138) | `Maintenance6MaxCombinedImageSamplerDescriptorCountTestCase` registers the `maintenance6_properties` name and gates support on `VK_KHR_maintenance6`. |
| Test instance | [vktApiMaintenance6Check.cpp#L52-L115](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L52-L115) | Queries the maintenance6 properties, iterates the format ranges, and applies the pass/fail rule. |
| Maintenance6 limit query | [vktApiMaintenance6Check.cpp#L63-L66](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L63-L66) | Reads `maxCombinedImageSamplerDescriptorCount` through `getPhysicalDeviceProperties2`. |
| Format ranges | [vktApiMaintenance6Check.cpp#L68-L81](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L68-L81) | Defines the three YCbCr-related format ranges scanned by the test. |
| Per-format descriptor count query | [vktApiMaintenance6Check.cpp#L90-L99](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L90-L99) | Chains `VkSamplerYcbcrConversionImageFormatProperties` and calls `getPhysicalDeviceImageFormatProperties2` per format. |
| Pass/fail comparison | [vktApiMaintenance6Check.cpp#L100-L113](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L100-L113) | Fails on the first per-format value exceeding the limit, otherwise passes. |
| Non-VulkanSC guard | [vktApiMaintenance6Check.cpp#L39](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L39) | The file is compiled only when `CTS_USES_VULKANSC` is not defined. |
| Mustpass entry | [api.txt#L327291](../../../mustpass/main/vk-default/api.txt#L327291) | The single `dEQP-VK.api.maintenance6_check.maintenance6_properties` line. |
