# Understanding Brief: wsi.<platform>.surface / vktWsiSurfaceTests.cpp

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation creates, destroys, and reports the properties of a `VkSurfaceKHR` correctly for each CTS WSI platform, including allocation-failure, extended-query, surfaceless-query, device-group, and native-window-size paths.

## Background Knowledge

### A surface connects Vulkan to a native presentation target

`VkSurfaceKHR` is an opaque Vulkan handle that represents a native window or display target. `VK_KHR_surface` defines the handle and its destruction function, while each platform extension supplies the matching creation function. Surface queries report the intersection of physical-device, native-target, and WSI-platform capabilities that an application needs before creating a swapchain.

Why it matters here:

- The same `surface` test family runs under nine WSI platform paths, but `createSurface()` selects a platform-specific creation entry point.
- Most cases create a native display and window, create a surface, and query every physical device that can present to it.
- Destroying a Vulkan surface disconnects Vulkan from the native target; it does not destroy the native window.

### Count-then-fill enumeration and `VK_INCOMPLETE`

Vulkan enumeration queries commonly use two calls. The first call passes a null output pointer to obtain a count. The second supplies storage for that many results. If the caller supplies too little storage, the query writes only the available elements, updates the count, and returns `VK_INCOMPLETE`.

Why it matters here:

- Format, present-mode, and present-rectangle cases check the normal count-and-fill path.
- They also make deliberately undersized calls and check both the `VK_INCOMPLETE` result and the untouched part of the output buffer.
- KHR2 and EXT query forms must agree with their base KHR counterparts where they report the same information.

### Application allocation callbacks

`VkAllocationCallbacks` lets an application provide host-memory allocation functions to Vulkan. Each callback reports an allocation scope, such as `VK_SYSTEM_ALLOCATION_SCOPE_OBJECT` or `VK_SYSTEM_ALLOCATION_SCOPE_INSTANCE`. If an allocation callback returns null and Vulkan cannot continue, the command reports `VK_ERROR_OUT_OF_HOST_MEMORY`.

Why it matters here:

- `create_custom_allocator` records callbacks and checks their scopes and lifetime.
- `create_simulate_oom` fails each allocation point in turn, accepts the resulting out-of-memory exception, and checks that cleanup leaves no recorded allocations.
- The test does not inject failures into `VkInstance` creation; it starts failure counting before native-object and surface creation.

## One Concrete Example

Consider `dEQP-VK.wsi.xcb.surface.query_formats2`, a registered XCB case in [wsi.txt](../../../mustpass/main/vk-default/wsi.txt#L31928).

1. The host enables `VK_KHR_surface`, `VK_KHR_xcb_surface`, and `VK_KHR_get_surface_capabilities2`.
2. It creates the native XCB display/window objects and a `VkSurfaceKHR`.
3. For each physical device with at least one queue family that supports the surface, it obtains a reference list through `vkGetPhysicalDeviceSurfaceFormatsKHR`.
4. It obtains the KHR2 count through `vkGetPhysicalDeviceSurfaceFormats2KHR`.
5. It initializes every `VkSurfaceFormat2KHR` with the required `sType` and a null `pNext`, then fetches the KHR2 list.
6. It checks the count, `sType`/`pNext` preservation, and coverage of every base-query format pair.
7. It repeats the KHR2 query with capacity for half the list. The expected result is `VK_INCOMPLETE`, and bytes beyond the returned range must keep the CTS fill pattern.

The case does not render or present an image. It checks API query behavior and the returned metadata.

## End-to-End Test Flow

```text
1. [host] select one of the nine WSI platform types
2. [host] create a Vulkan instance with VK_KHR_surface and the platform surface extension
3. [host] create native display/window objects when the selected case needs a real surface
4. [host] create a VkSurfaceKHR, or use VK_NULL_HANDLE for the tested surfaceless query
5. [host] run one behavior path
   5.1 create/destroy and allocation-callback checks
   5.2 queue-family presentation-support checks
   5.3 capability, format, or present-mode queries
   5.4 device-group capability and present-rectangle checks
   5.5 native-window initial-size or resize checks
6. [host] compare returned values with spec constraints, a base query, a real-surface query, or the requested window size
7. [host] destroy RAII-owned Vulkan and native objects and verify allocation records when applicable
8. [host] report pass, fail, quality warning, or not-supported
```

No case in this file submits GPU work. The device appears only through physical-device, queue-family, surface, and device-group queries; the host performs all validation.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

This file generates no shaders, pipelines, command buffers, or rendered reference images. Registration binds each test case leaf to a C++ function and a `vk::wsi::Type` value. The main generated data are host-side test inputs:

- the nine platform types routed by `vktWsiTests.cpp`;
- the three window sizes `(64, 64)`, `(124, 119)`, and `(256, 512)`;
- deliberately short enumeration arrays;
- `0xcd` guard/fill bytes for output-overrun detection;
- deterministic allocation-failure positions from 0 through 1024 allowed allocations.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Native display and window | Yes | No | No | Host retains them | Supply the platform object wrapped by `VkSurfaceKHR`; size-aware cases create or resize the window. |
| `VkSurfaceKHR` | Yes | No | No | Queried by host API calls | Object under test for lifecycle, support, capability, format, and present-mode behavior. |
| `VkInstance` | Yes | No | No | Used by host | Owns the surface and exposes instance-level WSI commands. |
| Physical-device and queue-family records | Enumerated by host | No | No | Inspected by host | Determine whether a device/queue can present and which surface queries are applicable. |
| Device-group `VkDevice` | Yes, in two cases | No commands submitted | No | Queried by host | Exposes device-group present masks and mode flags. |
| Enumeration vectors | Yes | No | No | Host checks them in place | Hold formats, present modes, or rectangles and expose count, overflow, and `VK_INCOMPLETE` defects. |
| Allocation recorder/failing allocator | Yes | No | No | Host inspects records | Checks allocator use, allocation scopes, OOM cleanup, and leaks. |

## What Is Checked

| Behavior area | Host-side pass condition |
|---------------|--------------------------|
| Surface creation and destruction | Creation returns a managed surface; custom allocation records use allowed scopes and are empty after cleanup; each injected OOM path cleans up; destroying `VK_NULL_HANDLE` makes no allocation or free callback. |
| Presentation support | Android reports support for every physical-device queue family; other platforms log the result. Where a native platform query exists, its answer matches `vkGetPhysicalDeviceSurfaceSupportKHR`. |
| Capabilities | Counts, extents, transforms, alpha flags, array-layer limits, and usage flags satisfy source checks; KHR2 and EXT base fields match KHR1; chained structures retain their expected `sType` and `pNext`. |
| Formats and present modes | Counts remain consistent, required platform values exist, format pairs contain no duplicates, short arrays return `VK_INCOMPLETE`, and query variants agree with their reference form. |
| Surfaceless queries | Null-surface results obey the enabled `VK_GOOGLE_surfaceless_query` version rules and match real-surface results where the source requires equality. |
| Device groups | Present masks permit each represented device to present on itself, local presentation is supported, flags stay in the accepted mask, guard bytes remain unchanged, rectangles do not overlap, and short rectangle arrays return `VK_INCOMPLETE`. |
| Native-window size | `currentExtent` equals each requested initial or resized window size. |

The individual C++ functions return `tcu::TestStatus`; `tcu::ResultCollector` aggregates multiple field failures in cases that continue checking after one mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group (the test case leaves grouped by the property they exercise)
>
> **Candidate values:** `surface lifecycle and allocation`, `presentation support`, `surface capability reporting`, `format and present-mode enumeration`, `surfaceless enumeration`, `device-group presentation`, `native-window extent tracking`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `surface lifecycle and allocation` | Surface creation/destruction, allocation-callback routing, allocation scope, OOM unwinding, or null-handle destruction does not match the tested contract. |
| `presentation support` | Queue-family surface support is wrong for the platform, or the native presentation-support query disagrees with the surface-specific query. |
| `surface capability reporting` | A capability field violates its required range or bit constraints, an extended query disagrees with the base query, or chained input/output structures are mishandled. |
| `format and present-mode enumeration` | Enumeration counts, required values, duplicate handling, KHR2/EXT agreement, `VK_INCOMPLETE`, or output bounds are wrong. |
| `surfaceless enumeration` | `VK_GOOGLE_surfaceless_query` returns a disallowed present mode or results inconsistent with the real-surface query required by the tested extension version. |
| `device-group presentation` | Present masks or mode flags are invalid, present rectangles overlap, an incomplete rectangle query returns the wrong status, or a query writes beyond its output object. |
| `native-window extent tracking` | `VkSurfaceCapabilitiesKHR::currentExtent` does not follow a supported initial-size or resize operation. |

## Important Variations and Special Cases

### Platform replication and conditional leaves

`createWsiTests()` registers the `surface` test family under `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, and `direct`. The common source registers 20 leaves on every platform. `initial_size` appears only when `FEATURE_INITIAL_WINDOW_SIZE` is set, and `resize` appears only when `FEATURE_RESIZE_WINDOW` is set. The inspected default mustpass contains 189 surface cases: 20 for each platform, plus five `initial_size` leaves and four `resize` leaves.

The direct and direct-DRM paths still contain the registered `query_presentation_support` leaf, but the test function reports not-supported because no matching native presentation-support query exists.

### Base, KHR2, and EXT queries

- `query_capabilities2` and `query_formats2` exercise extensible KHR2 structures and compare their base payloads with KHR1 results.
- `query_protected_capabilities` adds `VkSurfaceProtectedCapabilitiesKHR` to the output chain.
- `query_surface_counters` uses `vkGetPhysicalDeviceSurfaceCapabilities2EXT` and requires zero supported counters for non-display surfaces.
- `query_present_modes2` uses `vkGetPhysicalDeviceSurfacePresentModes2EXT` and requires `VK_EXT_full_screen_exclusive` on each queried device.

### Surfaceless extension versions

`query_present_modes_surfaceless` supports two rules. Extension version 1 checks that each null-surface mode also occurs in the real-surface list. Version 2 or later permits only `VK_PRESENT_MODE_FIFO_KHR`, `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR`, and `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR`. `query_present_modes2_surfaceless` requires version 2 or later.

### Allocation outcomes

A custom allocator that receives no calls produces a quality warning rather than a failure. The OOM loop also returns a quality warning if surface creation never succeeds by the 1024-allocation limit. These results distinguish a conformance failure from a path that could not exercise allocation callbacks as intended.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Per-platform routing | [createTypeSpecificTests()](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Registers `surface` beneath each WSI platform path. |
| Shared instance and surface setup | [createInstanceWithWsi() and `InstanceHelper`](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L173-L221) | Enables required surface extensions and builds the instance used by most cases. |
| Lifecycle and allocation paths | [surface creation, custom allocator, and OOM tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L223-L351) | Implements the creation and allocation-failure behavior. |
| Support queries | [surface and native presentation support](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L353-L442) | Checks queue-family support and cross-query agreement. |
| Capability validation | [`validateSurfaceCapabilities()` and capability queries](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L444-L638) | Defines field checks and KHR2/protected-chain validation. |
| Format queries | [base, surfaceless, and KHR2 format tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L640-L878) | Implements format requirements, consistency, and incomplete-array checks. |
| Present-mode queries | [base, EXT, and surfaceless present-mode tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L880-L1307) | Implements required-mode, extension-version, and comparison rules. |
| Device-group queries | [device-group capabilities and modes](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1309-L1576) | Checks masks, flags, guard bytes, rectangles, and incomplete results. |
| Window size and null destruction | [initial size, resize, and null-handle tests](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1578-L1690) | Implements extent tracking and the null-handle no-op check. |
| Case registration | [createSurfaceTests()](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1694-L1748) | Lists all leaves and both feature-conditional registrations. |
| Platform feature table | [getPlatformProperties() table](../../../framework/vulkan/vkWsiUtil.cpp#L90-L158) | Determines which platform paths receive size-related leaves. |
| Default mustpass example | [XCB surface entries](../../../mustpass/main/vk-default/wsi.txt#L31918-L31939) | Shows all 22 possible leaves on a platform with both window-size features. |
| WSI surface semantics | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L53-L82) | Defines the surface abstraction and platform-specific creation model. |
| Surface query semantics | [Vulkan surface-query chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2860-L2997) | Defines capability meaning and constraints. |
| Allocation callback semantics | [Vulkan memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc#L27-L178) | Defines host allocation callbacks and out-of-host-memory behavior. |

## Questions / Risk Points for User Audit

- [x] The source, dispatcher, platform feature table, and default mustpass agree on nine platform copies and 22 possible leaves.
- [x] The behavioral axis uses seven behavior groups because the 22 leaves test related variants of seven mechanisms; treating the platform type as primary would hide the failure distinctions.
- [x] Shader analysis is unnecessary because the file creates no shader program and submits no device work.
- [x] The direct and direct-DRM `query_presentation_support` leaves remain registered even though execution reports not-supported.
- [x] The final page should use XCB as the complete one-level registration example, then state the platform-dependent omissions in prose.
- [ ] The default mustpass snapshot proves registration in `vk-default`; profiles with different feature or extension filters may omit executable coverage.

## Conversion Notes for Final Wiki Rewrite

- Keep the seven behavioral groups as the `## Behavior Parameters` subsections.
- Copy the `### Failure Cause Mapping` table without changes.
- Omit a representative shader walkthrough and state that the family is host API behavior only.
- Keep the count-then-fill model, allocation callback model, and surface/native-window distinction as concise prerequisites.
- Use the full XCB leaf set for the parseable hierarchy. Explain the nine platform copies and conditional `initial_size`/`resize` registration outside the tree.
- Compress the resource table into runtime prose because no GPU-bound resource graph exists.
- Keep source navigation in the final appendix.
