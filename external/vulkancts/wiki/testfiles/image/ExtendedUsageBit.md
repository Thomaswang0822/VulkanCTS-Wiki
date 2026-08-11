## Overview

**Core question:** Does an image-format-properties query accept an image format, tiling, and usage when `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` and `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` permit that usage through a compatible view format?

- [`vktImageExtendedUsageBitTests.cpp`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L43-L356) implements `image.extended_usage_bit_compatibility` in the `image` test category.
- For each generated case, the test first searches the core format range for a compatible format that supports the requested usage without image-create flags. It then queries the selected image format with the two image-create flags and requires the same result.
- The three direct test families use the legacy format-properties query, the `VkPhysicalDeviceImageFormatInfo2` query, or the latter with `VkImageFormatListCreateInfo`. The test creates no image and runs no shader.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Extended usage with mutable formats.** `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` allows an image's usage flags to be supported by a compatible view format rather than by the image format alone. This source combines it with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` in every tested query.
- **Image-format-properties queries.** `vkGetPhysicalDeviceImageFormatProperties` and `vkGetPhysicalDeviceImageFormatProperties2` report whether an image configuration is supported. The `image_format_list` family uses the v2 form with an explicit image-format list in its `pNext` chain.
- **Source compatibility predicate.** The test treats identical formats as compatible. It also admits uncompressed, non-depth/stencil formats with equal pixel sizes and a fixed set of compressed format pairs: UNORM/SRGB pairs for BC, ETC2, and ASTC, plus UNORM/SNORM pairs for BC4, BC5, and EAC.

## Registration Hierarchy

```text
image.extended_usage_bit_compatibility
├── image_format_properties
└── image_format_properties2
```

[`createImageExtendedUsageBitTests()`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L282-L356) registers all three direct source families and one generated test case leaf for each selected format, tiling, and usage combination. The canonical tree above follows the active Vulkan-default mustpass inventory. The checked-in default mustpass inventories do not have the same family inventory:

| Default inventory | `image_format_properties` | `image_format_properties2` | `image_format_list` | Total leaves |
|-------------------|--------------------------:|---------------------------:|--------------------:|-------------:|
| [Vulkan](../../../mustpass/main/vk-default/image/extended-usage-bit-compatibility.txt) | 6,624 | 6,624 | 0 | 13,248 |
| [Vulkan SC](../../../mustpass/main/vksc-default/image/extended-usage-bit-compatibility.txt) | 2,944 | 2,944 | 2,944 | 8,832 |

Thus `image_format_list` is source-registered in both build variants and present in the Vulkan SC default inventory, but intentionally absent from the Vulkan default inventory. [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L26-L27) excludes the Vulkan `image_format_list` subtree as Issue 4894, and the Vulkan default mustpass configuration applies that exclusion list while the Vulkan SC configuration does not ([mustpass configuration](../../../scripts/build_mustpass.py#L56-L79)). Commit `3ec4d5909` introduced the exclusion because these cases exposed under-specified specification corners that were still under working-group discussion. The per-family counts match the source matrices: 184 core formats × 2 tilings × 18 Vulkan usages, or × 8 Vulkan SC usages. [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) adds the group to the `image` test category.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct test family | `image_format_properties`, `image_format_properties2`, `image_format_list` | Selects the query form and whether the v2 query receives a one-format `VkImageFormatListCreateInfo` chain. | [Query wrappers](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L135-L198), [factory](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L282-L356) |
| Image format | Every core format from the value after `VK_FORMAT_UNDEFINED` to the value before `VK_CORE_FORMAT_LAST` | Selects the image format passed to the flagged query and the set against which compatible view formats are searched. | [Compatibility search](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L200-L242), [factory loop](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L330-L351) |
| Tiling | `linear`, `optimal` | Selects the tiling argument for both the unflagged compatible-view query and the flagged image-format query. | [Tiling table](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L323-L328) |
| Image usage | `TRANSFER_SRC`, `TRANSFER_DST`, `SAMPLED`, `STORAGE`, `COLOR_ATTACHMENT`, `DEPTH_STENCIL_ATTACHMENT`, `TRANSIENT_ATTACHMENT`, `INPUT_ATTACHMENT`; non-Vulkan-SC builds also add video decode, video encode, fragment density map, fragment shading rate, invocation mask, and NV shading-rate-image usages | Selects the usage whose support must be found in at least one compatible format. | [Usage table](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L293-L321) |
| Image type | `VK_IMAGE_TYPE_2D` | Fixes the queried image type so the matrix isolates format, tiling, usage, and query-interface differences. | [All three query wrappers](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L142-L198) |
| Test case leaf name | `<format>_<linear|optimal>_<usage>` | Encodes the selected image format, tiling, and lowercased usage-bit suffix. | [Leaf-name construction](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L337-L348) |

## Behavior Parameters

The primary behavioral axis is the direct **test family**. Each family asks the same compatibility question through a different image-format-properties interface. Format, tiling, and usage select the configuration under that interface.

### `image_format_properties` - Legacy format-properties query

This family calls `vkGetPhysicalDeviceImageFormatProperties` for each candidate compatible view format, then calls it again for the selected image format with `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT | VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`. The two calls establish the expected and observed results.

### `image_format_properties2` - Version-2 format-properties query

This family performs the same comparison through `vkGetPhysicalDeviceImageFormatProperties2`. It fills `VkPhysicalDeviceImageFormatInfo2` with the selected 2D type, tiling, usage, and create flags, while leaving its `pNext` pointer null.

### `image_format_list` - Version-2 query with an image-format list

This family uses `vkGetPhysicalDeviceImageFormatProperties2` with a `VkImageFormatListCreateInfo` in the input `pNext` chain. Each query wrapper places its queried format in the one-entry list. The expected-result search therefore lists each candidate compatible format, and the flagged query lists the selected image format.

## Shader Analysis

This test has no shader code. It compares results returned by physical-device image-format-properties queries and does not create an image, bind descriptors, or submit GPU work.

## Runtime Execution and Result Checking

- The support callback requires `VK_KHR_maintenance2`, obtains `VkFormatProperties` for the selected image format, and skips the leaf if the selected linear or optimal tiling has no format features. Outside Vulkan SC, it requests corresponding device functionality for video decode, video encode, fragment density map, fragment shading rate attachment, and invocation mask usages. The registered NV shading-rate-image usage has no additional functionality check in this callback. [Support checks](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L244-L278)
- The test scans every core format and retains only formats accepted by the source compatibility predicate. For each candidate, the selected family queries support for the requested tiling and usage with no image-create flags. The first `VK_SUCCESS` sets the expected result. [Compatibility search and expected result](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L200-L220)
- If no compatible format succeeds, the case reports `NotSupportedError` rather than testing a negative extended-usage result. Otherwise, it queries the selected image format with both `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` and `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`. [Unsupported branch and flagged query](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L222-L232)
- The case passes only if the flagged query result equals the successful expected result. A difference returns `fail` and names the compatible view format that established the expectation. [Comparison and status](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L234-L242)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `image_format_properties` | Legacy image-format-properties handling of compatible view formats, extended-usage and mutable-format create flags, or the selected format, tiling, and usage combination. |
| `image_format_properties2` | `VkPhysicalDeviceImageFormatInfo2` handling of the same compatibility and create-flag condition. |
| `image_format_list` | `VkImageFormatListCreateInfo` chaining or view-format-list handling in addition to the v2 compatibility and create-flag condition. |

### Cause Analysis

#### Image-format-properties compatibility result

**Possible failure symptoms:** The case returns `Fail: view format <format>` because the flagged query did not return `VK_SUCCESS` after an unflagged query for that compatible view format did. The log identifies the first compatible view format that supplied the expected result but does not identify the internal stage that produced the different query result.

**Possible implementation causes:** The source derives the expected result by querying the selected tiling and usage against a compatible view format, then requests the same configuration for the image format with both create flags. A failure can involve the implementation's compatibility evaluation, the requested usage or tiling, or recognition of `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`. The test's source-defined compatibility predicate also bounds the formats used to establish an expectation, so diagnosis of a specific result requires the queried formats and runtime log.

#### Version-2 input structure or format-list handling

**Possible failure symptoms:** A failure confined to `image_format_properties2` or `image_format_list` indicates that the corresponding v2 query form returned a result different from the successful compatible-view query. A failure confined to `image_format_list` further narrows the differing input to the `VkImageFormatListCreateInfo` chain.

**Possible implementation causes:** The v2 families populate `VkPhysicalDeviceImageFormatInfo2` with the same type, tiling, usage, and flags as the legacy family. The format-list family attaches a one-entry list containing the format passed to that individual query: each candidate during the expected-result search and the selected image format during the flagged query. Incorrect interpretation of that structure, its `pNext` chain, the format-list entry, or the shared extended-usage condition can produce the mismatch. The source result comparison cannot distinguish among those inputs without additional implementation diagnostics.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_maintenance2`.
- The support callback skips an image format when its selected linear or optimal tiling has no format features.
- Outside Vulkan SC, video-decode usage values require `VK_KHR_video_decode_queue`; video-encode values require `VK_KHR_video_encode_queue`; fragment-density-map, fragment-shading-rate, and invocation-mask values each require their matching extension. [Requirement checks](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L244-L278)
- If no source-compatible view format supports the requested usage, the executor reports the leaf unsupported. That case has no successful compatible-view query from which to derive the test's expected success result.

### Design-based pruning

- The factory fixes the image type at 2D and varies only core image formats, two tilings, and one usage bit per leaf. It does not cover multi-bit usage combinations or image creation.
- The executor considers only the source-defined compatibility set: identical formats, equal-pixel-size uncompressed non-depth/stencil formats, and listed compressed pairs. It does not treat arbitrary format pairs as compatible. [Compatibility predicates](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L43-L126)
- Vulkan SC builds omit the extension-specific usage values guarded by `CTS_USES_VULKANSC`. [Usage registration](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L299-L320)

## Key Takeaways

- The family tests a query-time compatibility rule rather than image allocation, image-view creation, or image data access.
- A successful compatible-view query supplies the expected result for the selected image format queried with both extended-usage and mutable-format create flags.
- The legacy, v2, and format-list families use the same matrix and result comparison while covering three input interfaces.
- Unsupported tilings, missing extension functionality, and configurations with no successful compatible-view query leave the test unsupported instead of producing a failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Format compatibility predicates | [`isCompatibleCompressedFormat()` and `isCompatibleFormat()`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L43-L126) | Defines the source's compatible-view-format set. |
| Query-interface wrappers | [`PhysicalDeviceImageFormatProperties`, `PhysicalDeviceImageFormatProperties2`, and `PhysicalDeviceImageFormatList`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L135-L198) | Defines the legacy, v2, and one-entry format-list query forms. |
| Expected-result search and comparison | [`testExtendedUsageBitCompatiblity()`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L200-L242) | Finds a successful compatible view format, runs the flagged query, and decides pass or fail. |
| Support callback | [`checkSupport()`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L244-L278) | Applies maintenance, tiling-feature, and extension requirements. |
| Test registration | [`createImageExtendedUsageBitTests()`](../../../modules/vulkan/image/vktImageExtendedUsageBitTests.cpp#L282-L356) | Registers exact test-family names and the format, tiling, and usage matrix. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) | Adds `extended_usage_bit_compatibility` to the `image` test category. |
| Mustpass inventories | [`vk-default`](../../../mustpass/main/vk-default/image/extended-usage-bit-compatibility.txt) and [`vksc-default`](../../../mustpass/main/vksc-default/image/extended-usage-bit-compatibility.txt) | Confirm default `image_format_properties` and `image_format_properties2` leaves for Vulkan, and all three direct-family leaf sets for Vulkan SC. |
