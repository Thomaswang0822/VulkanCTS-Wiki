## Overview

**Core question:** When `VK_KHR_maintenance5` is enabled, do the `vkGetPhysicalDevice*FormatProperties*` queries return a zeroed or untouched output structure (and `VK_ERROR_FORMAT_NOT_SUPPORTED` for the `VkResult`-returning variants) when called with an unsupported format value or an unsupported image usage flag value?

- Covers the `api.maintenance5` test family, registered as `dEQP-VK.api.maintenance5.{format,flags}.*` in the default `api` mustpass.
- Implemented in [`vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1) for non-VulkanSC builds. The family has two intermediate nodes, `format` and `flags`, each expanded into the same set of API entry-point test case leaves.
- Each leaf sweeps five sentinel values near `VK_FORMAT_MAX_ENUM` (for the `format` node) or `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM` (for the `flags` node), calls one of six `vkGetPhysicalDevice*FormatProperties*` variants, and checks the output is zeroed or unchanged.
- The page explains what each intermediate node varies, how output is validated, what a failure means, and which cases are pruned by feature gating or by design.

## Background Knowledge

- `VK_KHR_maintenance5` promotes a stricter contract for the physical-device format-property queries: when a format or image usage flag is unsupported, the implementation must return `VK_ERROR_FORMAT_NOT_SUPPORTED` (for the `VkResult`-returning variants) and must not leave garbage in the caller-provided output structure. The CTS family checks that the host-visible output behaves this way across all six query entry points.
- The six query entry points pair up by struct-chain style and by what they query: `vkGetPhysicalDeviceFormatProperties` / `vkGetPhysicalDeviceFormatProperties2` (per-format feature flags), `vkGetPhysicalDeviceImageFormatProperties` / `vkGetPhysicalDeviceImageFormatProperties2` (per-format-per-usage image limits, returning `VkResult`), and `vkGetPhysicalDeviceSparseImageFormatProperties` / `vkGetPhysicalDeviceSparseImageFormatProperties2` (sparse-capability reporting via a counted array).
- `VK_FORMAT_MAX_ENUM` and `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM` are sentinel enum values used as upper bounds. The test treats values just below these maxima as guaranteed-unsupported inputs that exercise the maintenance5 error path.
- The `0xFF` pre-fill pattern is a CTS technique for distinguishing "implementation wrote zeros" from "implementation did not write at all". The output struct is first filled with `0xFF` bytes (via `makeInvalidVulkanStructure`), the API is called, and then the test accepts either an all-zero result or the unchanged `0xFF` pattern.

## Registration Hierarchy

```text
api.maintenance5
├── format
└── flags
```

The `maintenance5` group is created by [`createMaintenance5Tests()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L335-L361) and added under `api` only for non-VulkanSC builds via [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L128-L137). The two intermediate nodes (`format`, `flags`) each contain the same set of six test case leaves when both `HAS_FORMAT_PARAM` and `HAS_FLAGS_PARAM` apply; leaves with only one of the two bits set appear in just one node.

| Intermediate node | Registered test case leaves |
|---|---|
| `format` | `device_format_props`, `device_format_props2`, `image_format_props`, `image_format_props2`, `sparse_image_format_props`, `sparse_image_format_props2` |
| `flags` | `image_format_props`, `image_format_props2`, `sparse_image_format_props`, `sparse_image_format_props2` |

The `device_format_props` and `device_format_props2` leaves do not take an image usage flag, so their `FuncIDs` carry only `HAS_FORMAT_PARAM` and they are not registered under `flags`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `format`, `flags` | Selects whether the swept input is the format parameter or the image usage flag parameter. Each intermediate node sweeps a different invalid input across the same set of test case leaves. | [`createMaintenance5Tests()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L345-L347) |
| Test case leaf | `device_format_props`, `device_format_props2`, `image_format_props`, `image_format_props2`, `sparse_image_format_props`, `sparse_image_format_props2` | One leaf per `vkGetPhysicalDevice*FormatProperties*` variant. The `2` suffix denotes the `pNext`-chained `VkPhysicalDevice*Properties2` form. | [`funcs` array](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L337-L343) |
| Format sweep | `VK_FORMAT_MAX_ENUM - i` for `i` in `[0..4]` | Five sentinel format values near `VK_FORMAT_MAX_ENUM` fed into every `format`-group leaf. None of these are valid `VkFormat` values. | [`UnsupportedParametersMaintenance5FormatInstance::iterate()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L187-L189) |
| Usage flag sweep | `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i` for `i` in `[0..4]` | Five sentinel usage flag values near `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM` fed into every `flags`-group leaf. | [`UnsupportedParametersMaintenance5FlagsInstance::iterate()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L281-L283) |
| Image type | `VK_IMAGE_TYPE_2D` | Fixed image type used by image and sparse image format queries. | [format iterate](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L154), [flags iterate](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L251) |
| Tiling | `VK_IMAGE_TILING_OPTIMAL` | Fixed tiling used by image and sparse image format queries. | [format iterate](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L155), [flags iterate](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L252) |
| Sample count | `VK_SAMPLE_COUNT_1_BIT` | Fixed sample count used by sparse image format queries. | [format iterate](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L157), [flags iterate](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L254) |
| Valid format for `flags` tests | `VK_FORMAT_R8G8B8A8_UNORM` | A supported format used as the fixed `format` argument in `flags`-group leaves so only the usage flag is the invalid input. | [`UnsupportedParametersMaintenance5FlagsInstance::iterate()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L250) |

## Behavior Parameters

The primary behavioral axis is the intermediate node: `format` versus `flags`. Both intermediate nodes share the same set of test case leaves (where applicable) and the same six API entry points, but they target a different invalid input and exercise different parts of the maintenance5 contract.

### `format`: Invalid format sentinel sweep

Each `format`-group leaf sweeps five format values near `VK_FORMAT_MAX_ENUM`. For `device_format_props` and `device_format_props2`, the test pre-fills the output `VkFormatProperties` with `0xFF`, calls the query, and accepts either an all-zero result or the unchanged `0xFF` pattern. For `image_format_props` and `image_format_props2`, the test applies the same pre-fill/compare pattern to `VkImageFormatProperties`, and the returned `VkResult` is captured for the final assertion. For `sparse_image_format_props` and `sparse_image_format_props2`, the test passes a zero count and a null pointer, then verifies the implementation also returns zero. All six leaves are registered under this node because every entry point accepts a `VkFormat`.

### `flags`: Invalid usage flag sentinel sweep

Each `flags`-group leaf sweeps five image usage flag values near `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM`. The format is fixed to `VK_FORMAT_R8G8B8A8_UNORM` so that the usage flag is the only invalid input. Only the four entry points that accept a usage flag are registered here: the two `image_format_props` variants validate output pre-fill and `VkResult`; the two `sparse_image_format_props` variants always pass per design (see `## Runtime Execution and Result Checking` and `## Failure Meaning`). The `device_format_props` pair does not accept a usage flag and is therefore not registered under `flags`.

## Shader Analysis

No shader is involved in this test. Every test case leaf performs only host-side Vulkan property queries and never submits any pipeline work.

## Runtime Execution and Result Checking

Both intermediate nodes use the same overall shape, dispatched by `m_params.funcID` and the `HAS_FORMAT_PARAM` / `HAS_FLAGS_PARAM` selection bits. The host-side flow for one test case leaf is:

- Acquire the physical device and instance interface from the `Context`.
- Pre-fill the output structure with `0xFF` bytes via [`makeInvalidVulkanStructure()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L137-L145), and capture an `invalidProps` snapshot for the post-call comparison.
- Initialize `res = VK_ERROR_FORMAT_NOT_SUPPORTED`. The two sparse variants and the `device_format_props` variants return `void`, so `res` is only updated by the `image_format_props` variants' `VkResult` return.
- Loop `i` from `0` to `4`:
  - In the `format` node, compute `format = VkFormat(VK_FORMAT_MAX_ENUM - i)`.
  - In the `flags` node, fix `format = VK_FORMAT_R8G8B8A8_UNORM` and compute `usage = VkImageUsageFlags(VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i)`.
  - Dispatch on `m_params.funcID` and call the matching `vkGetPhysicalDevice*FormatProperties*` function.
  - For `VkFormatProperties` and `VkImageFormatProperties` outputs, set `verdicts[i] = (emptyProps == current || invalidProps == current)`. The implementation either wrote zeros or left the `0xFF` pattern untouched.
  - For sparse variants in the `format` node, set `verdicts[i] = (0 == propsCount)`. The implementation must report zero sparse image format entries for an unsupported format.
  - For sparse variants in the `flags` node, set `verdicts[i] = true` unconditionally. The source comment records that some implementations ignore wrong flags, so the test does not enforce the sparse-flag path.
- Final pass condition: `VK_ERROR_FORMAT_NOT_SUPPORTED == res` and `std::all_of(verdicts.begin(), verdicts.end(), ...)` returns `true` (the elided lambda returns each `verdicts[i]` unchanged). Any other `VkResult` from the `image_format_props` variants, or any `false` verdict, fails the leaf.

The `0xFF` pre-fill makes the output-structure check independent of any specific failure value the implementation might otherwise write: it accepts zeroed output (the maintenance5 contract) or untouched output (the conservative fallback), and rejects any partially-written structure that does not match either.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `format` | Implementation writes a partially-populated output structure for an unsupported format, returns a nonzero sparse image format count for an unsupported format, or returns a `VkResult` other than `VK_ERROR_FORMAT_NOT_SUPPORTED` from the image format queries. |
| `flags` | Implementation writes a partially-populated `VkImageFormatProperties` for an unsupported usage flag, or returns a `VkResult` other than `VK_ERROR_FORMAT_NOT_SUPPORTED` from the image format queries. The sparse-flag leaves always pass per design and cannot fail this family. |

A shared final assertion applies to both nodes: the `image_format_props` and `image_format_props2` leaves fail if `res != VK_ERROR_FORMAT_NOT_SUPPORTED`, regardless of the output-structure check.

### Cause Analysis

#### Output structure not zeroed or untouched for an unsupported format

**Possible failure symptoms:** In `format`-group leaves, after the API call `props1 != emptyProps && props1 != invalidProps` (for `VkFormatProperties`) or `imageProps1 != emptyImgProps && imageProps1 != invalidImgProps` (for `VkImageFormatProperties`). The leaf sets the corresponding `verdicts[i] = false`, which makes `std::all_of` return false, and the leaf returns `tcu::TestStatus::fail("")`.

**Possible implementation causes:** Per `VK_KHR_maintenance5`, the implementation must zero the output structure when returning `VK_ERROR_FORMAT_NOT_SUPPORTED` for an unsupported format. A failure means the implementation wrote a partial or nonzero set of fields into the caller-provided struct, violating the zeroing contract. Identifying which field is written incorrectly requires source-level inspection of the implementation's `vkGetPhysicalDevice*FormatProperties*` path; the CTS check does not isolate the failing field.

#### Nonzero sparse image format count for an unsupported format

**Possible failure symptoms:** In `format`-group sparse leaves (`sparse_image_format_props`, `sparse_image_format_props2`), `propsCount != 0` after the query. The leaf sets `verdicts[i] = false` and returns `tcu::TestStatus::fail("")`.

**Possible implementation causes:** Per `VK_KHR_maintenance5`, an unsupported format must report zero sparse image format entries. A nonzero count means the implementation claimed sparse support for a format that is, by construction, not supported. If the count is nonzero, isolating the cause requires source-level investigation; the test passes a null `pSparseImageFormatProperties` pointer and does not inspect the contents of any reported entries.

#### Wrong `VkResult` from the image format queries

**Possible failure symptoms:** In `format`-group and `flags`-group `image_format_props` and `image_format_props2` leaves, `res != VK_ERROR_FORMAT_NOT_SUPPORTED` after the call. The final assertion `VK_ERROR_FORMAT_NOT_SUPPORTED == res && std::all_of(...)` fails even when the output-structure check would have passed, and the leaf returns `tcu::TestStatus::fail("")`.

**Possible implementation causes:** Per `VK_KHR_maintenance5`, the image format queries must return `VK_ERROR_FORMAT_NOT_SUPPORTED` for an unsupported format or usage flag. Returning `VK_SUCCESS` would mean the implementation claimed support for an unsupported combination; returning another error code (such as `VK_ERROR_OUT_OF_HOST_MEMORY`) would mask the format-not-supported signal. Both outcomes violate the maintenance5 contract.

#### Output structure not zeroed or untouched for an unsupported usage flag

**Possible failure symptoms:** In `flags`-group image leaves (`image_format_props`, `image_format_props2`), `imageProps1 != emptyImgProps && imageProps1 != invalidImgProps` after the call. The leaf sets `verdicts[i] = false` and returns `tcu::TestStatus::fail("")`.

**Possible implementation causes:** The same maintenance5 zeroing contract applies; the difference is that the invalid input is the image usage flag rather than the format. Determining whether the implementation writes a partial subset of fields (for example, only `maxMipLevels` and not the rest) rather than zeroing the whole struct requires source-level investigation.

The sparse-flag leaves (`sparse_image_format_props` and `sparse_image_format_props2` under the `flags` node) always set `verdicts[i] = true` regardless of the implementation's response. They cannot contribute a failure to the leaf result; the source comment records that some implementations ignore wrong usage flags, so the test intentionally does not enforce the sparse-flag path.

## Case Pruning

### Requirement-based pruning

- The `maintenance5` group is registered only for non-VulkanSC builds: the parent `addChild(createMaintenance5Tests(testCtx))` call is wrapped in `#ifndef CTS_USES_VULKANSC` together with several sibling groups in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L128-L137).
- [`checkSupport()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L116-L123) requires the `VK_KHR_maintenance5` device functionality and the `maintenance5` feature being `VK_TRUE`. Implementations that do not expose the extension skip the case before any query runs.
- The sentinel values `VK_FORMAT_MAX_ENUM - i` and `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i` are intentionally outside the supported range. They are valid `uint32_t`/flag-bit values but are not valid `VkFormat` or supported usage combinations, which is the prerequisite for the maintenance5 error path.

### Design-based pruning

- The `device_format_props` and `device_format_props2` leaves are registered only under `format` because their `FuncIDs` carry `HAS_FORMAT_PARAM` but not `HAS_FLAGS_PARAM`. The `vkGetPhysicalDeviceFormatProperties` and `vkGetPhysicalDeviceFormatProperties2` functions do not take an image usage flag, so the `flags` node has no analogue for them.
- The sparse-flag leaves (`sparse_image_format_props` and `sparse_image_format_props2` under `flags`) are registered but always set `verdicts[i] = true` per the source comment that "some of the Implementations ignore wrong flags". The test intentionally does not enforce them.
- The format/usage sweep is fixed to five values (`i` in `[0..4]`). A larger sweep is not generated.
- Image type, tiling, sample count, and (for the `flags` node) the format are fixed to known-supported values so that only the targeted input is the invalid one. The matrix does not vary these dimensions.
- The sparse-flags path captures `VkPhysicalDeviceSparseImageFormatInfo2` and `VkPhysicalDeviceImageFormatInfo2` structs with the same fixed image type, tiling, and sample count as the format node, so the two nodes share a constant resource configuration.

## Key Takeaways

- The family verifies the `VK_KHR_maintenance5` guarantee that unsupported format and unsupported image usage flag inputs to the `vkGetPhysicalDevice*FormatProperties*` family produce a zeroed or untouched output structure, plus `VK_ERROR_FORMAT_NOT_SUPPORTED` for the `VkResult`-returning variants.
- The two intermediate nodes split the matrix by which input is invalid: `format` sweeps five sentinel formats, `flags` sweeps five sentinel usage flags. The same six test case leaves cover the same six API entry points where applicable.
- The `0xFF` pre-fill pattern makes the output check accept either zeroed output (the maintenance5 contract) or untouched output (a conservative fallback), and rejects any partially-written structure that matches neither.
- The sparse-flag leaves always pass per design; they do not contribute to the leaf result.
- See `## Failure Meaning` for how a partially-written output, a nonzero sparse count, or a wrong `VkResult` would manifest, and which ones require source-level investigation of the implementation's query path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createMaintenance5Tests()` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L335-L361](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L335-L361) | Public entry point that creates the `maintenance5` group and its `format` / `flags` intermediate nodes. |
| `funcs` array | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L337-L343](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L337-L343) | Maps test case leaf names to `FuncIDs`. Drives the per-leaf `HAS_FORMAT_PARAM` / `HAS_FLAGS_PARAM` registration logic. |
| `HAS_FORMAT_PARAM` / `HAS_FLAGS_PARAM` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L43-L44](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L43-L44) | Selection bits encoded into each `FuncIDs` value that determine which intermediate node(s) a leaf is added to. |
| `enum FuncIDs` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L45-L53](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L45-L53) | The six API entry-point identifiers, each tagged with the relevant selection bits. |
| `UnsupportedParametersMaintenance5FormatInstance::iterate()` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L147-L243](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L147-L243) | Host-side flow for the `format` node. Sweeps five format sentinels and validates output for all six `FuncIDs`. |
| `UnsupportedParametersMaintenance5FlagsInstance::iterate()` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L245-L331](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L245-L331) | Host-side flow for the `flags` node. Sweeps five usage flag sentinels and validates output for the four `FuncIDs` that accept a usage flag. |
| `checkSupport()` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L116-L123](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L116-L123) | Requires `VK_KHR_maintenance5` and `maintenance5 == VK_TRUE`. |
| `makeInvalidVulkanStructure()` | [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L137-L145](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L137-L145) | Pre-fills output structures with `0xFF` so a zeroed result and an untouched result are both detectable. |
| Parent registration | [vktApiTests.cpp#L128-L137](../../../modules/vulkan/api/vktApiTests.cpp#L128-L137) | Adds the `maintenance5` group under `api` only inside `#ifndef CTS_USES_VULKANSC`. |
| Mustpass entries | [api.txt#L327281-L327290](../../../mustpass/main/vk-default/api.txt#L327281-L327290) | Registers all ten `dEQP-VK.api.maintenance5.*` leaves in the default `api` mustpass. |
