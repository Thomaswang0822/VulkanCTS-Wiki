## Overview

**Core question:** Does each WSI platform create a usable `VkSurfaceKHR` and satisfy the value, structure, enumeration, and extent checks implemented for the tested WSI queries?

- This page covers the `surface` test family implemented by `vktWsiSurfaceTests.cpp`.
- CTS registers the family under nine platform paths: `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, and `direct`.
- The test case leaves cover surface lifecycle, allocation callbacks and injected OOM, presentation support, surface metadata, surfaceless queries, device-group properties, and native-window extent tracking.
- All checks run on the host. These tests create no shaders, submit no command buffers, and present no images.

## Background Knowledge

For the shared concepts Vulkan surfaces and surface capability queries, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- Enumeration queries use a count-then-fill pattern. A short output array must receive only the entries that fit, and the function returns `VK_INCOMPLETE`; storage outside the written range must remain untouched.
- `VkAllocationCallbacks` routes implementation host-memory operations through application callbacks. The callback reports an allocation scope, and a failed allocation can produce `VK_ERROR_OUT_OF_HOST_MEMORY` when the implementation cannot continue.

## Registration Hierarchy

XCB has both native-window-size features, so its hierarchy shows all 22 possible test case leaves:

```text
wsi.xcb.surface
├── create
├── create_custom_allocator
├── create_simulate_oom
├── query_support
├── query_presentation_support
├── query_capabilities
├── query_capabilities2
├── query_protected_capabilities
├── query_surface_counters
├── query_formats
├── query_formats2
├── query_present_modes
├── query_present_modes2
├── query_devgroup_present_capabilities
├── query_devgroup_present_modes
├── destroy_null_handle
├── initial_size
├── resize
├── query_formats_surfaceless
├── query_present_modes_surfaceless
├── query_present_modes2_surfaceless
└── query_formats2_surfaceless
```

The same `surface` test family appears under all nine WSI platform paths. Each path has the 20 unconditional leaves. `initial_size` is also registered for `xlib`, `xcb`, `android`, `win32`, and `metal`; `resize` is registered for `xlib`, `xcb`, `win32`, and `metal`. The default mustpass contains 189 surface cases across the nine platforms.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform path | `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, `direct` | Selects the native objects, platform surface extension, creation command, and platform-specific rules. | [Platform registration](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L83) |
| Behavior leaf | 20 unconditional leaves; `initial_size` and `resize` when their platform features exist | Selects which lifecycle, support, query, enumeration, device-group, or extent contract the case checks. | [Surface registration](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1694-L1748) |
| Window size | `(64, 64)`, `(124, 119)`, `(256, 512)` | Exercises both square and nonsquare extents for initial-size and resize tracking. | [Size-aware tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1578-L1669) |
| Surface query form | base KHR, KHR2, EXT, or null-surface extension path | Checks base results, extensible structures, extension-specific data, and `VK_GOOGLE_surfaceless_query`. | [Capability and format queries](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L499-L1121) |
| Enumeration capacity | full count or a reduced count, usually one-third or one-half | Every implemented reduced-capacity call must produce `VK_INCOMPLETE`; the base format/mode and KHR2 format paths also check that unwritten storage remains untouched. | [`CheckIncompleteResult`](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L117-L169), [KHR2 short-format check](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L849-L870), [other short calls](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L953-L960) |
| OOM injection position | 0 through 1024 allowed allocations | Moves the deterministic failure point until surface creation succeeds or the bound is reached. | [`createSurfaceSimulateOOMTest()`](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L298-L351) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group** formed by related test case leaves. Grouping the 22 leaves this way keeps variants of one API contract together while separating failures that point to different mechanisms.

### `surface lifecycle and allocation`: create, destroy, and unwind host allocations

`create` verifies that the platform helper returns a managed `VkSurfaceKHR`. `create_custom_allocator` records allocation callbacks during instance and surface lifetime, permits only object and instance scopes, and requires no live records after cleanup. `create_simulate_oom` advances a deterministic failure point through surface creation and checks cleanup after each out-of-memory exception. `destroy_null_handle` calls `vkDestroySurfaceKHR` with `VK_NULL_HANDLE` using default and custom allocators; the custom allocator must record no allocation or free.

### `presentation support`: report whether queue families can present

`query_support` calls `vkGetPhysicalDeviceSurfaceSupportKHR` for each physical device and queue family. Android requires every result to be true. `query_presentation_support` compares the platform-specific presentation-support query with the surface-specific query. The direct and direct-DRM paths have no platform query, so their registered cases report not-supported.

### `surface capability reporting`: return valid base and chained properties

`query_capabilities` checks image counts and extents, array-layer limits, color-attachment usage, transforms, and composite-alpha support. `query_capabilities2` compares `VkSurfaceCapabilities2KHR::surfaceCapabilities` with the base KHR result and checks that the implementation preserves input bytes, `sType`, and `pNext`. `query_protected_capabilities` extends the output chain with `VkSurfaceProtectedCapabilitiesKHR`. `query_surface_counters` compares EXT and KHR base fields and requires zero surface-counter bits for non-display surfaces.

### `format and present-mode enumeration`: return complete, bounded lists

`query_formats` and `query_present_modes` perform count-and-fill queries, check required platform values, and make short-array calls that must return `VK_INCOMPLETE`. Format results must contain no duplicates. Android has additional required formats and requires `VK_PRESENT_MODE_MAILBOX_KHR`; every platform must expose `VK_PRESENT_MODE_FIFO_KHR`. The KHR2 format leaf requires the same count as the base query and coverage of every base format, then checks extensible structures and a guarded short-array call. The EXT present-mode leaf compares only its count with the base query, checks required modes, and requires `VK_INCOMPLETE` from its short-array call.

### `surfaceless enumeration`: query without a `VkSurfaceKHR`

Four leaves exercise `VK_GOOGLE_surfaceless_query`. The format leaves compare null-surface results with real-surface results through base and KHR2 APIs. Present-mode handling depends on the extension version: version 1 checks that null-surface modes also occur for the real surface, while version 2 or later permits only `VK_PRESENT_MODE_FIFO_KHR`, `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR`, and `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR`. The EXT present-mode leaf requires version 2 or later.

### `device-group presentation`: validate masks, flags, and present rectangles

`query_devgroup_present_capabilities` creates a device group and checks that each represented device can present on itself, `VK_DEVICE_GROUP_PRESENT_MODE_LOCAL_BIT_KHR` is set, and no write reaches the guard bytes after `VkDeviceGroupPresentCapabilitiesKHR`. `query_devgroup_present_modes` checks the mode-flag mask and guard bytes. If local multi-device presentation is supported, it also checks that present rectangles do not overlap and that a short rectangle array returns `VK_INCOMPLETE`.

### `native-window extent tracking`: follow requested window dimensions

`initial_size` creates a new native window and surface for each of the three sizes, then compares `VkSurfaceCapabilitiesKHR::currentExtent` with the requested size. `resize` keeps one surface, resizes its native window through the same values, and repeats the capability check. CTS registers these leaves only when the platform feature table says the operation is supported.

## Shader Analysis

This test family has no shader code. It validates host API calls, returned structures, allocator records, and native-window state without creating a graphics or compute pipeline.

## Runtime Execution and Result Checking

- The dispatcher selects a `vk::wsi::Type`. `createInstanceWithWsi()` enables `VK_KHR_surface`, the platform surface extension, `VK_KHR_display` for display surfaces, and any extension required by the chosen leaf.
- Most leaves create `NativeObjects`, create a `VkSurfaceKHR`, enumerate physical devices, and skip a device-specific surface query when no queue family supports that surface.
- Support and property cases call one or more WSI queries. `tcu::ResultCollector` lets a case record several field mismatches before returning its final status.
- Base-versus-extended cases fetch both forms and compare the shared fields, format coverage, or count selected by that leaf. KHR2 cases initialize `sType` and `pNext`; capability cases also copy the input structure and compare its bytes after the call.
- The base format and present-mode leaves and the KHR2 format leaf query a full list and then issue a guarded reduced-capacity call, requiring `VK_INCOMPLETE` without changes to unwritten storage. The EXT present-mode and device-group rectangle leaves also require `VK_INCOMPLETE` from reduced-capacity calls, but do not apply the same unwritten-storage check to those calls.
- Device-group cases create a logical device with `VK_KHR_swapchain` and device-group support, query presentation data, and inspect both values and adjacent `0xcd` guard bytes. They submit no device work.
- Size-aware cases create or resize native windows, then compare `currentExtent` against the requested dimensions for each surface-supported physical device.
- Allocation cases inspect the callback recorder after scoped objects have been destroyed. An unused custom allocator or an OOM loop that does not reach success by 1024 allowed allocations produces a quality warning rather than a conformance failure.

A case passes when all checks in its selected path hold. A thrown `NotSupportedError` or an explicit not-supported status excludes a path whose required extension, device functionality, or native operation is unavailable.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `surface lifecycle and allocation` | Surface creation/destruction, allocation-callback routing, allocation scope, OOM unwinding, or null-handle destruction does not match the tested contract. |
| `presentation support` | Queue-family surface support is wrong for the platform, or the native presentation-support query disagrees with the surface-specific query. |
| `surface capability reporting` | A capability field violates its required range or bit constraints, an extended query disagrees with the base query, or chained input/output structures are mishandled. |
| `format and present-mode enumeration` | Enumeration counts, required values, duplicate handling, KHR2 format coverage, EXT present-mode count agreement, `VK_INCOMPLETE`, or the guarded output bounds are wrong. |
| `surfaceless enumeration` | `VK_GOOGLE_surfaceless_query` returns a disallowed present mode or results inconsistent with the real-surface query required by the tested extension version. |
| `device-group presentation` | Present masks or mode flags are invalid, present rectangles overlap, an incomplete rectangle query returns the wrong status, or a query writes beyond its output object. |
| `native-window extent tracking` | `VkSurfaceCapabilitiesKHR::currentExtent` does not follow a supported initial-size or resize operation. |

### Cause Analysis

#### Surface lifecycle or allocation handling

**Possible failure symptoms:** Surface creation throws or returns no managed handle; callback records use a disallowed scope, remain live after destruction, or appear during null-handle destruction; an injected OOM path leaks a recorded allocation or fails outside the accepted outcome.

**Possible implementation causes:** The implementation may route surface host allocations through the wrong callback set, report the wrong `VkSystemAllocationScope`, omit cleanup on a partially completed platform-surface creation, or perform work for `vkDestroySurfaceKHR(VK_NULL_HANDLE)`. Vulkan requires failed callback allocation to become `VK_ERROR_OUT_OF_HOST_MEMORY` when the command cannot continue, and requires compatible callbacks across object creation and destruction.

#### Presentation-support reporting

**Possible failure symptoms:** Android reports false for a device or queue family, or a platform-specific presentation query differs from `vkGetPhysicalDeviceSurfaceSupportKHR` for the same physical device and queue family.

**Possible implementation causes:** The platform WSI support path may map the physical device, queue family, native display, or surface incorrectly. For Android, the Vulkan WSI rules require all physical devices and queue families to support presentation to native windows.

#### Capability and structure handling

**Possible failure symptoms:** Counts or extents violate their tested bounds, required usage/transform/alpha bits are absent, a KHR2 or EXT result differs from its KHR base data, `supportsProtected` is not boolean, or the implementation changes input bytes, `sType`, or `pNext`.

**Possible implementation causes:** The surface-capability implementation may derive inconsistent limits from the native target and physical device, populate a base and extended path from different state, or walk extensible structures incorrectly. The Vulkan WSI chapter defines the field bounds and requires `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT`, at least one transform, and at least one composite-alpha mode.

#### Enumeration count, value, or bounds handling

**Possible failure symptoms:** The count changes between the count and fill calls, a required format or present mode is missing, a format pair is duplicated, a KHR2 format list omits a base format, an EXT present-mode count differs from the base count, a short call fails to return `VK_INCOMPLETE`, or a guarded call changes bytes outside its returned range.

**Possible implementation causes:** The implementation may mishandle the two-call enumeration contract, write using the available-result count instead of caller capacity, or generate inconsistent KHR2 format results or present-mode counts across related entry points. Platform-specific required values can also be absent from the WSI backend's advertised list.

#### Surfaceless-query handling

**Possible failure symptoms:** Null-surface format lists differ from the corresponding real-surface list, version 1 present modes are absent from the real-surface list, version 2 returns a present mode outside the three permitted values, or the EXT path accepts an unsupported extension version.

**Possible implementation causes:** The `VK_GOOGLE_surfaceless_query` path may retain surface-dependent filtering where the extension requires physical-device-wide format results, apply the wrong version rule, or pass `VK_NULL_HANDLE` through a query path that still assumes a live surface.

#### Device-group query handling

**Possible failure symptoms:** A present mask excludes a represented device from itself, local presentation is absent, mode flags exceed the accepted set, rectangles overlap, a short rectangle query returns the wrong result, or guard bytes change.

**Possible implementation causes:** The device-group WSI implementation may encode physical-device indices or mode bits incorrectly, generate an invalid local multi-device partition, ignore the caller's rectangle capacity, or write the wrong structure size.

#### Native-window extent propagation

**Possible failure symptoms:** `currentExtent` differs from the initial window size or remains stale after a successful native resize.

**Possible implementation causes:** The platform surface backend may cache native dimensions without observing the supported window operation, convert dimensions incorrectly, or report a swapchain-selected extent on a platform path where CTS expects the native window to determine the current extent.

## Case Pruning

### Requirement-based pruning

- Every case needs `VK_KHR_surface` and the selected platform surface extension. Display surface types also enable `VK_KHR_display`; direct DRM adds `VK_EXT_direct_mode_display`.
- KHR2 capability and format leaves need `VK_KHR_get_surface_capabilities2`. Protected capabilities also need `VK_KHR_surface_protected_capabilities`.
- Surface counters explicitly enable both `VK_KHR_display` and `VK_EXT_display_surface_counter`. EXT present-mode leaves need `VK_EXT_full_screen_exclusive` on the queried device.
- Surfaceless leaves need `VK_GOOGLE_surfaceless_query`; `query_present_modes2_surfaceless` requires extension version 2 or later.
- Device-group leaves need `VK_KHR_device_group_creation`, device-group functionality, and `VK_KHR_swapchain`.
- The direct and direct-DRM cases for `query_presentation_support` report not-supported because CTS has no native presentation-support adapter for them.
- A physical-device-specific real-surface query runs only when at least one queue family supports the surface.

### Design-based pruning

- CTS registers `initial_size` only for platform types with `FEATURE_INITIAL_WINDOW_SIZE`, and `resize` only for types with `FEATURE_RESIZE_WINDOW`. This avoids asking a native-window adapter to perform an operation outside its declared CTS support.
- The OOM loop stops at the first successful creation. The upper bound of 1024 prevents an unbounded test when the implementation keeps requesting host allocations.
- Surfaceless tests still create a real surface when the validation rule requires a reference list. They pass `VK_NULL_HANDLE` only to the query being tested.

## Key Takeaways

- The family tests the host-visible contract around `VkSurfaceKHR`; it does not test rendering or presentation.
- One implementation file supplies the same 20 core leaves to nine platform paths, while the platform feature table adds `initial_size` and `resize` where CTS can perform those native operations.
- Where a leaf cross-checks a base query, capability fields, KHR2 format coverage, or EXT present-mode counts must agree; surfaceless queries follow their extension-version-specific value rules. A successful return code alone does not pass the case.
- Every implemented reduced-capacity query must return `VK_INCOMPLETE`; guard patterns add output-bound checks to the base format/mode, KHR2 format, and full device-group output paths.
- Allocation tests cover callback selection, scope, lifetime, and cleanup across injected failure points. See `Failure Meaning` for the diagnostic split among these mechanisms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Per-platform routing | [createTypeSpecificTests()](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Places `surface` beneath every WSI platform path. |
| Instance and extension setup | [createInstanceWithWsi() and `InstanceHelper`](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L173-L221) | Creates the instance used by the surface cases and checks required extensions. |
| Lifecycle and allocator tests | [surface creation, custom allocator, and OOM paths](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L223-L351) | Implements creation, callback validation, injected failure, and cleanup. |
| Presentation support | [surface and native support queries](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L353-L442) | Queries queue-family support and compares platform and surface answers. |
| Capability checks | [`validateSurfaceCapabilities()` and capability variants](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L444-L638) | Defines field constraints and extensible-structure checks. |
| Format enumeration | [base, surfaceless, and KHR2 format tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L640-L878) | Checks required formats, duplicates, query agreement, and short arrays. |
| Present-mode enumeration | [base, EXT, and surfaceless present-mode tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L880-L1307) | Checks required modes and extension-version rules. |
| Device-group checks | [present capabilities, modes, and rectangles](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1309-L1576) | Validates masks, flags, guard bytes, rectangle partitioning, and `VK_INCOMPLETE`. |
| Extent and null-destruction checks | [initial size, resize, and null-handle tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1578-L1690) | Connects native-window operations to surface capability and lifecycle checks. |
| Complete leaf registration | [createSurfaceTests()](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1694-L1748) | Registers the 20 common leaves and two conditional leaves. |
| Platform feature ownership | [getPlatformProperties()](../../../framework/vulkan/vkWsiUtil.cpp#L90-L158) | Controls conditional initial-size and resize registration. |
| Mustpass coverage | [XCB surface entries](../../../mustpass/main/vk-default/wsi.txt#L31918-L31939) | Shows one platform path with all 22 possible leaves. |
| Surface and query rules | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2508-L2997) | Defines presentation support, surface capabilities, and their required values. |
| Enumeration and surfaceless rules | [Vulkan format and present-mode queries](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L3870-L3991), [present-mode queries](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L4222-L4315) | Defines `VK_INCOMPLETE`, KHR2 behavior, and null-surface result rules. |
| Allocation callback rules | [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L27-L178) | Defines application allocation callbacks and allocation failure behavior. |
