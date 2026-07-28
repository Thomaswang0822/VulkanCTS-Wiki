## Overview

**Core question:** when an image or swapchain is created with a `VkImageCompressionControlEXT` struct in the `pNext` chain, does the implementation report compression properties consistent with the requested control flags?

- This page covers the `image_compression_control` test family under the `api` test category, implemented in [`vktApiImageCompressionControlTests.cpp`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1) and attached to the `api` test category by [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L129).
- The test family is non-VulkanSC only; the parent registration is compiled out under `CTS_USES_VULKANSC`.
- It exercises `VK_EXT_image_compression_control` and `VK_EXT_image_compression_control_swapchain` across three image sources: regular image creation, Android Hardware Buffer external memory, and swapchain images.
- Five compression control flag values (`no_compression_control` for `create_image` only, plus `default`, `fixed_rate_default`, `disabled`, and `explicit` for all three image sources) drive five distinct validation rules in a shared `validate()` helper.
- The page explains what each flag value tests, how each image source sets up its target image, and what a failure implies.

## Background Knowledge

- **`VK_EXT_image_compression_control`.** An extension that lets an application pass a `VkImageCompressionControlEXT` struct in the `pNext` chain of `VkImageCreateInfo` (or related creation structs) to express a compression preference: `VK_IMAGE_COMPRESSION_DEFAULT_EXT`, `VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT`, `VK_IMAGE_COMPRESSION_DISABLED_EXT`, or `VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT` with per-plane fixed-rate flags. The implementation then reports the actual compression it applied through `VkImageCompressionPropertiesEXT`.
- **Compression property query.** `VkImageCompressionPropertiesEXT` can be chained to `vkGetImageSubresourceLayout2EXT` (per-image query) and to `VkImageFormatProperties2` returned by `vkGetPhysicalDeviceImageFormatProperties2` (per-format capability query). The test compares the two to ensure consistency.
- **Fixed-rate flag bits.** `VkImageCompressionFixedRateFlagsEXT` is a bitmask where each bit names a fixed bits-per-component rate. A higher bit position corresponds to a higher rate. The test converts a requested flag bit to a numeric rate via `1 << deCtz32(flag)` and compares requested versus actual rates as integers.

## Registration Hierarchy

```text
api.image_compression_control
├── create_image
├── android_hardware_buffer
└── swapchain
```

The factory [`createImageCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L736-L802) builds the three intermediate nodes shown above. Each node contains one intermediate level for the compression control flag, and the leaves under each flag depend on the image source:

- `create_image` exposes five flag intermediate nodes: `no_compression_control`, `default`, `fixed_rate_default`, `disabled`, `explicit`. Each flag leaf expands to one test case leaf per `VkFormat` swept over core formats, YCbCr formats, and YCbCr extended formats (compressed formats are skipped), for 168 leaves per flag and 840 leaves total. See [`addImageCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L423-L461).
- `android_hardware_buffer` exposes four flag intermediate nodes: `default`, `fixed_rate_default`, `disabled`, `explicit`. Each flag leaf expands to one test case leaf per format in a fixed list of 11 AHB-compatible formats, for 44 leaves total. See [`addAhbCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L712-L734).
- `swapchain` exposes one WSI-platform intermediate node per `vk::wsi::Type` value (`android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib`), and each WSI node has four test case leaves named `default`, `fixed_rate_default`, `disabled`, `explicit`, for 36 leaves total. See [`createImageCompressionControlTests()` swapchain branch](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L783-L797).

Total registered leaves: 920, verified against [`api.txt`](../../../mustpass/main/vk-default/api.txt#L318003-L318922).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image source (intermediate node) | `create_image`, `android_hardware_buffer`, `swapchain` | Selects which image-creation path is exercised: regular `VkImageCreateInfo`, AHB external-memory import, or WSI swapchain | [`createImageCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L736-L802) |
| Compression flag (intermediate node) | `no_compression_control` (create_image only), `default`, `fixed_rate_default`, `disabled`, `explicit` | Selects the value of `VkImageCompressionControlEXT::flags` and therefore which validation rule is applied | [`vktApiImageCompressionControlTests.cpp#L752-L761`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L752-L761) |
| Format (test case leaf, `create_image`) | 168 core, YCbCr, and YCbCr extended formats | Names the format of the created image; compressed formats are skipped | [`vktApiImageCompressionControlTests.cpp#L427-L460`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L427-L460) |
| Format (test case leaf, `android_hardware_buffer`) | 11 AHB-compatible formats (`R8G8B8A8_UNORM`, `R8G8B8_UNORM`, `R5G6B5_UNORM_PACK16`, `R16G16B16A16_SFLOAT`, `A2B10G10R10_UNORM_PACK32`, `D16_UNORM`, `X8_D24_UNORM_PACK32`, `D24_UNORM_S8_UINT`, `D32_SFLOAT`, `D32_SFLOAT_S8_UINT`, `S8_UINT`) | Names the AHB format imported into Vulkan | [`vktApiImageCompressionControlTests.cpp#L715-L725`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L715-L725) |
| WSI type (intermediate node under `swapchain`) | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` | Names the WSI platform whose surface and swapchain are created | [`vktApiImageCompressionControlTests.cpp#L784-L797`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L784-L797) |
| Swapchain surface format | queried from `vkGetPhysicalDeviceSurfaceFormats2KHR` per case | Determines the `VkFormat` used for the swapchain and validated image | [`vktApiImageCompressionControlTests.cpp#L625-L642`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L625-L642) |
| Fixed-rate plane flag sweep (for `explicit`) | 24 distinct combinations of `pFixedRateFlags[0..2]` built by XOR with shifted masks | Exercises many explicit-rate requests per format; AHB and swapchain only use plane 0 | [`vktApiImageCompressionControlTests.cpp#L315-L325`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L315-L325), [`vktApiImageCompressionControlTests.cpp#L379-L388`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L379-L388), [`vktApiImageCompressionControlTests.cpp#L604-L611`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L604-L611) |
| `compressionControlPlaneCount` | `numPlanes` for multi-planar YCbCr formats when `explicit`; `0` otherwise | Selects which plane the per-plane fixed-rate flags apply to | [`vktApiImageCompressionControlTests.cpp#L453-L454`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L453-L454) |

## Behavior Parameters

The primary behavioral axis is the compression flag, because the validation rules in [`validate()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L102-L217) are flag-driven. Each flag value tests a different clause of the compression-control contract: what the implementation may report when a particular preference was requested, or what it may report when no preference was requested at all. The same flag-driven validation runs across all three image source intermediate nodes through the shared `validate()` helper.

### `no_compression_control`: image created without the extension struct

`testParams.useExtension` is `false`, so [`imageCreateInfo.pNext`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L408-L411) is left unset. The image is created with no `VkImageCompressionControlEXT` in the chain. The validation rule asserts the implementation does not report any active fixed-rate compression: `imageCompressionFixedRateFlags` must be `VK_IMAGE_COMPRESSION_FIXED_RATE_NONE_EXT`, and `imageCompressionFlags` must be `VK_IMAGE_COMPRESSION_DEFAULT_EXT` or `VK_IMAGE_COMPRESSION_DISABLED_EXT` [`vktApiImageCompressionControlTests.cpp#L203-L215`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L203-L215). Registered only under `create_image` because AHB and swapchain tests always chain the control struct [`vktApiImageCompressionControlTests.cpp#L746`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L746).

### `default`: `VK_IMAGE_COMPRESSION_DEFAULT_EXT` requested

The control struct is chained with `flags = VK_IMAGE_COMPRESSION_DEFAULT_EXT`. The implementation is free to choose any compression mode, but the test asserts it does not report lossy (fixed-rate) compression in this case: `imageCompressionFixedRateFlags` must be `0` [`vktApiImageCompressionControlTests.cpp#L164-L168`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L164-L168).

### `fixed_rate_default`: `VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT` requested

The control struct is chained with `flags = VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT`. The implementation chooses a concrete compression mode, so the test asserts the reported `imageCompressionFlags` is one of `VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT`, `VK_IMAGE_COMPRESSION_DISABLED_EXT`, or `VK_IMAGE_COMPRESSION_DEFAULT_EXT` [`vktApiImageCompressionControlTests.cpp#L179-L186`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L179-L186). The implementation is not required to apply a fixed rate; it may fall back to `DEFAULT` or `DISABLED`.

### `disabled`: `VK_IMAGE_COMPRESSION_DISABLED_EXT` requested

The control struct is chained with `flags = VK_IMAGE_COMPRESSION_DISABLED_EXT`. The test asserts the implementation disables compression: `imageCompressionFlags` must be `VK_IMAGE_COMPRESSION_DISABLED_EXT`, and `imageCompressionFixedRateFlags` must be `0` [`vktApiImageCompressionControlTests.cpp#L169-L178`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L169-L178).

### `explicit`: `VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT` requested with per-plane rates

The control struct is chained with `flags = VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT`, `compressionControlPlaneCount` is set to the number of YCbCr planes (or `1` for non-YCbCr), and `pFixedRateFlags` is populated with 24 different combinations of plane flag bits across iterations. For each iteration, when the reported `imageCompressionFlags` is not `DISABLED` or `DEFAULT` (i.e., the implementation chose a fixed rate), the test asserts the reported rate is at least the minimum requested rate, compared as integer flag-bit values [`vktApiImageCompressionControlTests.cpp#L188-L201`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L188-L201).

## Shader Analysis

No shader is involved in this test family. No pipeline is built, no shader module is created, and no draw or dispatch is recorded. The test only creates images (or imports AHB, or creates swapchains), queries their compression properties through `vkGetImageSubresourceLayout2EXT` and `vkGetPhysicalDeviceImageFormatProperties2`, and validates the results on the host.

## Runtime Execution and Result Checking

All three image sources share the same final validation step, [`validate()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L102-L217), which:

- Iterates per plane for YCbCr formats and per image otherwise, choosing `VK_IMAGE_ASPECT_COLOR_BIT` or `VK_IMAGE_ASPECT_PLANE_0_BIT` / `_1_BIT` / `_2_BIT` accordingly [`vktApiImageCompressionControlTests.cpp#L105-L116`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L105-L116).
- Calls `vkGetImageSubresourceLayout2EXT` chained with `VkImageCompressionPropertiesEXT` to query the per-image compression properties [`vktApiImageCompressionControlTests.cpp#L118-L122`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L118-L122).
- Calls `vkGetPhysicalDeviceImageFormatProperties2` chained with a `VkImageCompressionControlEXT` mirror of the request and `VkImageCompressionPropertiesEXT` to query the per-format capability [`vktApiImageCompressionControlTests.cpp#L124-L146`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L124-L146).
- Applies the flag-driven rules described in `## Behavior Parameters` and records any violation through `tcu::ResultCollector::fail()` [`vktApiImageCompressionControlTests.cpp#L148-L215`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L148-L215).
- Returns `tcu::TestStatus(results.getResult(), results.getMessage())` so any collected failure becomes a non-passing case result.

The setup preceding `validate()` differs per image source:

- **`create_image`** ([`imageCreateTest()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L367-L421)). Calls `checkImageCompressionControlSupport()` to require `VK_EXT_image_compression_control` and the `imageCompressionControl` feature. For each of the 24 explicit-rate iterations (or a single iteration for other flags), builds a `VkImageCreateInfo` for a 16x16 `VK_IMAGE_TYPE_2D` optimal-tiling color-attachment image, optionally chains the control struct, calls `checkImageSupport()` to skip unsupported formats, creates the image, and calls `validate()`.
- **`android_hardware_buffer`** ([`ahbImageCreateTest()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L293-L365)). Requires `VK_ANDROID_external_memory_android_hardware_buffer` and `VK_EXT_image_compression_control`. For each of the 24 explicit-rate iterations, chains the control struct through a `VkExternalMemoryImageCreateInfo` with handle type `VK_EXTERNAL_MEMORY_HANDLE_TYPE_ANDROID_HARDWARE_BUFFER_BIT_ANDROID`, calls [`checkAhbImageSupport()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L219-L291) to verify the AHB format and external memory features are exportable and dedicated-only, creates the image, allocates exportable device memory, binds it, and calls `validate()`.
- **`swapchain`** ([`swapchainCreateTest()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L590-L710)). Calls `checkImageCompressionControlSupport(swapchain=true)` to also require `VK_EXT_image_compression_control_swapchain` and the `imageCompressionControlSwapchain` feature. Creates a custom instance and device through `InstanceHelper` and `DeviceHelper` with `VK_KHR_swapchain`, the WSI platform extension, and both compression-control extensions enabled. For each surface format returned by `vkGetPhysicalDeviceSurfaceFormats2KHR`, skips combinations whose supported compression mode or rate does not overlap the requested flag, creates a `VkSwapchainKHR` with the control struct chained, retrieves the swapchain images, and calls `validate()` against the first swapchain image.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| `VkImage` (`create_image`) | Yes | N/A (no descriptor) | None | Compression property query | Target image whose compression properties are validated. |
| `VkImage` + `VkDeviceMemory` (`android_hardware_buffer`) | Yes, with AHB export | Bound via `bindImageMemory` | None | Compression property query | AHB-backed image whose compression properties are validated. |
| `VkSwapchainKHR` + swapchain images (`swapchain`) | Yes | Owned by swapchain | None | Compression property query on `images[0]` | Swapchain image whose compression properties are validated. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_compression_control` | Implementation reports active fixed-rate or non-default compression for an image created without the control struct. |
| `default` | Implementation reports lossy (fixed-rate) compression when `VK_IMAGE_COMPRESSION_DEFAULT_EXT` was requested. |
| `fixed_rate_default` | Implementation reports a compression flag other than `EXPLICIT`, `DISABLED`, or `DEFAULT` when `VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT` was requested. |
| `disabled` | Implementation does not disable compression, or reports fixed-rate flags, when `VK_IMAGE_COMPRESSION_DISABLED_EXT` was requested. |
| `explicit` | Implementation reports an actual fixed rate lower than the minimum requested rate for a `VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT` request. |
| (all flags) | Per-image query and per-format capability query disagree, or reported flags are not a subset of supported flags. |

### Cause Analysis

#### Implementation reports active fixed-rate or non-default compression for an image created without the control struct

**Possible failure symptoms:** `validate()` records `"Fixed rate compression should not be enabled."` or `"Image compression should be default or not be enabled."` for the `no_compression_control` case [`vktApiImageCompressionControlTests.cpp#L203-L215`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L203-L215).

**Possible implementation causes:** When no `VkImageCompressionControlEXT` is chained, the spec lets the implementation apply default behavior. Reporting active fixed-rate compression in this case means the implementation exposed a non-default compression mode through `VkImageCompressionPropertiesEXT` without the application opting in. Source-level investigation is needed to distinguish a driver reporting an unintended flag from a CTS-side query setup issue; the test only verifies the reported flags are `DEFAULT` or `DISABLED` and the fixed-rate flags are `FIXED_RATE_NONE_EXT`.

#### Implementation reports lossy (fixed-rate) compression when `VK_IMAGE_COMPRESSION_DEFAULT_EXT` was requested

**Possible failure symptoms:** `validate()` records `"Got lossy compression when DEFAULT compression was requested."` [`vktApiImageCompressionControlTests.cpp#L164-L168`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L164-L168).

**Possible implementation causes:** `VK_IMAGE_COMPRESSION_DEFAULT_EXT` lets the implementation choose any mode, but the test asserts it does not pick a lossy fixed rate. A failure means the implementation chose fixed-rate lossy compression by default. Whether that is a spec violation depends on whether the extension permits lossy default compression for the format; source-level investigation against the `VK_EXT_image_compression_control` spec language is needed before attributing this to a driver bug.

#### Implementation reports a compression flag other than `EXPLICIT`, `DISABLED`, or `DEFAULT` when `VK_IMAGE_COMPRESSION_FIXED_RATE_DEFAULT_EXT` was requested

**Possible failure symptoms:** `validate()` records `"Explicit compression flags not returned for image creation with FIXED RATE DEFAULT."` [`vktApiImageCompressionControlTests.cpp#L179-L186`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L179-L186).

**Possible implementation causes:** The implementation returned a `imageCompressionFlags` value outside the three allowed values. The test accepts `EXPLICIT` (it applied a fixed rate), `DISABLED` (it fell back to no compression), or `DEFAULT` (it fell back to default). Any other flag is treated as a violation of the contract the test expects from `FIXED_RATE_DEFAULT`.

#### Implementation does not disable compression, or reports fixed-rate flags, when `VK_IMAGE_COMPRESSION_DISABLED_EXT` was requested

**Possible failure symptoms:** `validate()` records `"Image compression not disabled."` or `"Image compression disabled but got fixed rate flags."` [`vktApiImageCompressionControlTests.cpp#L169-L178`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L169-L178).

**Possible implementation causes:** `VK_IMAGE_COMPRESSION_DISABLED_EXT` requires the implementation to disable compression. Reporting any flag other than `DISABLED`, or reporting any fixed-rate flags, means the implementation did not honor the request. Source-level investigation is needed to determine whether the implementation silently applied a non-disabled mode or whether the queried properties are stale; the test only verifies the reported `imageCompressionFlags` and `imageCompressionFixedRateFlags`.

#### Implementation reports an actual fixed rate lower than the minimum requested rate for a `VK_IMAGE_COMPRESSION_FIXED_RATE_EXPLICIT_EXT` request

**Possible failure symptoms:** `validate()` records `"Image created with less bpc than requested."` [`vktApiImageCompressionControlTests.cpp#L188-L201`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L188-L201).

**Possible implementation causes:** The test computes `minRequestedRate = 1 << deCtz32(pFixedRateFlags[planeIndex])` and `actualRate = compressionProperties.imageCompressionFixedRateFlags` and asserts `minRequestedRate <= actualRate` when the reported `imageCompressionFlags` is not `DISABLED` or `DEFAULT`. A failure means the implementation chose a fixed rate with fewer bits per component than requested. Whether this is a spec violation depends on the extension's contract for `FIXED_RATE_EXPLICIT`; the test treats the requested rate as a minimum.

#### Per-image query and per-format capability query disagree, or reported flags are not a subset of supported flags

**Possible failure symptoms:** `validate()` records `"Got image with fixed rate flags that are not supported in image format properties."` or `"Got image with compression flags that are not supported in image format properties."` [`vktApiImageCompressionControlTests.cpp#L150-L163`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L150-L163).

**Possible implementation causes:** The compression properties reported through `vkGetImageSubresourceLayout2EXT` (per-image) must be a subset of those reported through `vkGetPhysicalDeviceImageFormatProperties2` (per-format) for the same control request. A failure means the two queries disagree: either the per-image query returned flags the per-format query said were unsupported, or the implementation reported different capabilities for the same format depending on which entry point was asked. Source-level investigation is needed to determine which query is wrong; the test only compares their results.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_EXT_image_compression_control` and the `imageCompressionControl` feature; unsupported devices skip the case via `NotSupportedError` from [`checkImageCompressionControlSupport()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L80-L100).
- Swapchain cases also require `VK_EXT_image_compression_control_swapchain` and the `imageCompressionControlSwapchain` feature, plus the WSI platform extension for the selected `vk::wsi::Type`. The custom device created by [`createDeviceWithWsi()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L507-L558) throws `NotSupportedError` if any required extension is missing.
- Android Hardware Buffer cases require `VK_ANDROID_external_memory_android_hardware_buffer`. [`checkAhbImageSupport()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L219-L291) also verifies the AHB format is allocatable, the external memory features include `EXPORTABLE_BIT` and `DEDICATED_ONLY_BIT`, the AHB usage bits cover the requested usage, and the supported compression flags overlap the requested flag.
- Swapchain cases skip surface formats whose supported compression mode or rate does not overlap the requested flag, except that `FIXED_RATE_DEFAULT` is allowed through when the surface reports any non-zero fixed-rate support [`vktApiImageCompressionControlTests.cpp#L657-L667`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L657-L667).
- `create_image` cases call `checkImageSupport()` after building `VkImageCreateInfo`, so any format unsupported by the implementation for the requested usage is skipped rather than failed [`vktApiImageCompressionControlTests.cpp#L413`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L413).

### Design-based pruning

- `create_image` sweeps three format ranges (core formats, YCbCr formats, and YCbCr extended formats) but explicitly skips compressed formats (`isCompressedFormat()` returns true for BC, ETC, ASTC, etc.) because the extension does not apply to already-compressed formats [`vktApiImageCompressionControlTests.cpp#L450-L451`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L450-L451).
- `android_hardware_buffer` uses a fixed list of 11 AHB-compatible formats instead of a format sweep, because only those formats are guaranteed to be allocatable as an AHB [`vktApiImageCompressionControlTests.cpp#L715-L725`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L715-L725).
- `swapchain` does not expand per-format leaves. Each WSI platform has exactly four test case leaves (`default`, `fixed_rate_default`, `disabled`, `explicit`) because the swapchain format is determined by the surface, not by the test.
- `no_compression_control` is registered only under `create_image`; AHB and swapchain tests always chain the control struct, so they have no `no_compression_control` variant [`vktApiImageCompressionControlTests.cpp#L746`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L746).
- For `explicit`, the test runs 24 iterations per format with distinct `pFixedRateFlags` combinations to exercise many requested rates. Other flag values run a single iteration per format [`vktApiImageCompressionControlTests.cpp#L315-L325`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L315-L325).

## Key Takeaways

- The `image_compression_control` test family checks reported compression properties against requested control flags, not rendered output. All validation lives in the shared `validate()` helper.
- The compression flag is the primary behavioral axis because it determines which validation rule runs; the image source intermediate node (`create_image`, `android_hardware_buffer`, `swapchain`) only changes how the target image is created and which extensions or features are required.
- `no_compression_control` is registered only under `create_image`; AHB and swapchain tests always chain the control struct.
- Compressed formats are skipped under `create_image` because the extension does not apply to already-compressed formats.
- See `## Failure Meaning` for the failure interpretation: a failing result means the implementation reported compression properties that disagree with the requested flag, with the per-format capability query, or with the no-control-struct baseline.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration | [`vktApiTests.cpp#L129`](../../../modules/vulkan/api/vktApiTests.cpp#L129) | Adds the `image_compression_control` test family to the `api` test category (non-VulkanSC only). |
| Factory | [`createImageCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L736-L802) | Builds the `create_image`, `android_hardware_buffer`, and `swapchain` intermediate nodes and their children. |
| Header declaration | [`vktApiImageCompressionControlTests.hpp#L36`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.hpp#L36) | Declares `createImageCompressionControlTests`. |
| `create_image` per-format registration | [`addImageCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L423-L461) | Adds one test case leaf per `VkFormat` under each flag intermediate node. |
| `android_hardware_buffer` per-format registration | [`addAhbCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L712-L734) | Adds one test case leaf per AHB-compatible format. |
| `create_image` test body | [`imageCreateTest()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L367-L421) | Creates a 16x16 optimal-tiling color-attachment image and calls `validate()`. |
| `android_hardware_buffer` test body | [`ahbImageCreateTest()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L293-L365) | Imports an AHB into a Vulkan image and calls `validate()`. |
| `swapchain` test body | [`swapchainCreateTest()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L590-L710) | Creates a custom instance/device with WSI, creates a swapchain, and calls `validate()` on the first swapchain image. |
| Shared validation | [`validate()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L102-L217) | Queries per-image and per-format compression properties and applies the flag-driven rules. |
| Compression-control support gate | [`checkImageCompressionControlSupport()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L80-L100) | Requires `VK_EXT_image_compression_control` and the `imageCompressionControl` feature; for swapchain also requires `VK_EXT_image_compression_control_swapchain` and `imageCompressionControlSwapchain`. |
| AHB support gate | [`checkAhbImageSupport()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L219-L291) | Verifies AHB format allocatability, external memory features, and compression flag overlap before creating an AHB-backed image. |
| Swapchain device creation | [`createDeviceWithWsi()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L507-L558) | Creates a custom device with `VK_KHR_swapchain`, the WSI platform extension, and both compression-control extensions. |
| Mustpass range | [`api.txt#L318003-L318922`](../../../mustpass/main/vk-default/api.txt#L318003-L318922) | All 920 `dEQP-VK.api.image_compression_control.*` entries. |
