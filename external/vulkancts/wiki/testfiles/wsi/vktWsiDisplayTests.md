# vktWsiDisplayTests

## Overview

Coverage tests for the `VK_KHR_display` and `VK_KHR_get_display_properties2` instance extensions. Each test case exercises a single display-related Vulkan API query or operation, validating that the driver correctly populates output structures, returns appropriate VkResult codes, and respects array-size semantics. No shader programs are involved; all verification is performed through API query results, canary-based memory overwrite detection, and struct-field validation via `tcu::ResultCollector`.

**Role of file**: Implementation file

**Source**: [vktWsiDisplayTests.cpp](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp)

## Registration Hierarchy

```text
wsi.display
├── get_display_properties
├── get_display_plane_properties
├── get_display_plane_supported_displays
├── get_display_mode_properties
├── create_display_mode
├── get_display_plane_capabilities
├── create_display_plane_surface
├── surface_counters
├── get_display_properties2
├── get_display_plane_properties2
├── get_display_mode_properties2
└── get_display_plane_capabilities2
```

## Test Families

All 12 test cases share a single `DisplayCoverageTestInstance` class that dispatches via a switch on `m_testId` in `iterate()` ([vktWsiDisplayTests.cpp#L276-L311](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L276-L311)). Each case calls a dedicated private method performing one API query or operation. The tests are registered by `createDisplayCoverageTests()` ([vktWsiDisplayTests.cpp#L2199-L2228](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L2199-L2228)).

### VK_KHR_display tests (indices 1-8)

| Test Case | API Function | Description |
|---|---|---|
| `get_display_properties` | `vkGetPhysicalDeviceDisplayPropertiesKHR` | Enumerates display properties; validates handle uniqueness, field validity (planeReorderPossible, persistentContent, supportedTransforms, physicalResolution), and correct VK_SUCCESS/VK_INCOMPLETE returns for varying array sizes |
| `get_display_plane_properties` | `vkGetPhysicalDeviceDisplayPlanePropertiesKHR` | Enumerates display plane properties; validates currentStackIndex bounds and currentDisplay handle membership in the display set |
| `get_display_plane_supported_displays` | `vkGetDisplayPlaneSupportedDisplaysKHR` | Lists displays supported by each plane; validates returned handles against the known display set |
| `get_display_mode_properties` | `vkGetDisplayModePropertiesKHR` | Enumerates display mode properties per display; validates mode handle validity |
| `create_display_mode` | `vkCreateDisplayModeKHR` | Creates a custom display mode; includes negative tests passing zero refreshRate, zero visibleRegion width, and zero visibleRegion height, expecting `VK_ERROR_INITIALIZATION_FAILED`; verifies builtin mode count is unchanged after creation |
| `get_display_plane_capabilities` | `vkGetDisplayPlaneCapabilitiesKHR` | Queries plane capabilities per display/mode combination; validates supportedAlpha flags, position/extent range ordering (min <= max), and non-negative source positions |
| `create_display_plane_surface` | `vkCreateDisplayPlaneSurfaceKHR` | Creates a display plane surface using opaque alpha mode on full-display planes; validates surface handle is non-null |
| `surface_counters` | `vkGetPhysicalDeviceSurfaceCapabilities2EXT` + `vkGetPhysicalDeviceSurfaceCapabilitiesKHR` | Queries surface counters via `VK_EXT_display_surface_counter`; cross-validates `VkSurfaceCapabilities2EXT` against `VkSurfaceCapabilitiesKHR`; validates that only `VK_SURFACE_COUNTER_VBLANK_EXT` bits are set in supportedSurfaceCounters |

### VK_KHR_get_display_properties2 tests (indices 9-12)

| Test Case | API Function | Description |
|---|---|---|
| `get_display_properties2` | `vkGetPhysicalDeviceDisplayProperties2KHR` | Same as `get_display_properties` but using the pNext-chained `VkDisplayProperties2KHR` variant; additionally validates sType and pNext preservation |
| `get_display_plane_properties2` | `vkGetPhysicalDeviceDisplayPlaneProperties2KHR` | Same as `get_display_plane_properties` but using `VkDisplayPlaneProperties2KHR`; validates sType and pNext preservation |
| `get_display_mode_properties2` | `vkGetDisplayModeProperties2KHR` | Same as `get_display_mode_properties` but using `VkDisplayModeProperties2KHR`; validates sType and pNext preservation |
| `get_display_plane_capabilities2` | `vkGetDisplayPlaneCapabilities2KHR` | Same as `get_display_plane_capabilities` but using `VkDisplayPlaneCapabilities2KHR` and `VkDisplayPlaneInfo2KHR`; validates sType and pNext preservation |

## Parameter Dimensions

| Dimension | Values / Range | Notes |
|---|---|---|
| Test ID (enum `DisplayIndexTest`) | 12 values: `DISPLAY_TEST_INDEX_GET_DISPLAY_PROPERTIES` through `DISPLAY_TEST_INDEX_GET_DISPLAY_PLANE_CAPABILITIES2` | Selects the API function to exercise; each maps to one registered test case. Dispatched in `iterate()` ([vktWsiDisplayTests.cpp#L276-L311](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L276-L311)) |
| Display count | Runtime-dependent (capped at `MAX_TESTED_DISPLAY_COUNT = 16`) | Limits iteration over enumerated displays |
| Plane count | Runtime-dependent (capped at `MAX_TESTED_PLANE_COUNT = 16`) | Limits iteration over enumerated planes |
| Array size variation | 0 to count+1 | Each enumeration test iterates with varying requested array sizes to verify VK_SUCCESS/VK_INCOMPLETE behavior |

No shader-based or image-based parameterization. No `wsiType` parameter is consumed.

## Support / Feature Requirements

| Requirement | Applicable Tests | Check Location |
|---|---|---|
| `VK_KHR_display` instance extension | All 12 tests | Constructor throws `NotSupportedError` if missing ([vktWsiDisplayTests.cpp#L242-L245](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L242-L245)) |
| `VK_KHR_get_display_properties2` instance extension | `get_display_properties2`, `get_display_plane_properties2`, `get_display_mode_properties2`, `get_display_plane_capabilities2` | Constructor throws `NotSupportedError` if missing ([vktWsiDisplayTests.cpp#L249-L261](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L249-L261)) |
| `VK_EXT_display_surface_counter` instance extension | `surface_counters` | Checked at runtime in `testDisplaySurface()` ([vktWsiDisplayTests.cpp#L1508-L1511](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1508-L1511)) |
| At least one display available | All tests | `getDisplays()` / `getDisplays2()` throw `NotSupportedError` when no displays are reported |
| At least one plane available | Tests that enumerate planes or capabilities | Throws `ResourceError` or `NotSupportedError` when no planes are reported |

## Verification Methods

- **Canary-based memory overwrite detection**: Output structures are pre-filled with sentinel values (`INVALID_DISPLAY = 0xABCDEF11`, `INVALID_DISPLAY_MODE = 0xABCDEF11`); after the API call, the test verifies the driver has overwritten expected entries and not written beyond the requested count.
- **VkResult validation**: Enumeration queries are checked for `VK_SUCCESS` when the requested count >= reported count, and `VK_INCOMPLETE` when the requested count < reported count.
- **Struct field validation via `tcu::ResultCollector`**: Accumulates per-field failures for display properties, plane properties, mode properties, and capabilities without aborting on first error. Validated fields include handle validity, boolean range, flag recognition, position/extent ordering, and resolution non-zero.
- **Negative test** in `create_display_mode`: Passes zero refreshRate, zero visibleRegion width, and zero visibleRegion height; expects `VK_ERROR_INITIALIZATION_FAILED` and that the output handle remains `VK_NULL_HANDLE` ([vktWsiDisplayTests.cpp#L1267-L1302](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1267-L1302)).
- **Display handle uniqueness**: Verifies that enumerated display handles are unique (no duplicates in the returned set).
- **sType/pNext preservation** (KHR_get_display_properties2 variants): Confirms that the driver does not modify the `sType` or `pNext` fields of the 2-struct variants.
- **Surface counter cross-validation**: Compares `VkSurfaceCapabilities2EXT` fields against `VkSurfaceCapabilitiesKHR` for consistency; validates that only recognized counter bits (`VK_SURFACE_COUNTER_VBLANK_EXT`) are set.

## Notes / Uncertainties

- The `create_display_mode` negative test assumes the driver rejects invalid mode parameters with `VK_ERROR_INITIALIZATION_FAILED`; other error codes may be valid per the Vulkan spec but would cause a test failure.
- Tests 9-12 (the `*2` variants) are structurally identical to tests 1-4 but use the `VK_KHR_get_display_properties2` pNext-chained query variants. They share the same verification logic via shared `validate*` helper methods.
- The `surface_counters` test requires both `VK_EXT_display_surface_counter` and a display plane surface with opaque alpha support on a full-display plane; if no such combination exists, the test throws `NotSupportedError`.
- The `nextTestNumber()` helper ([vktWsiDisplayTests.cpp#L148-L158](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L148-L158)) skips middle indices in long mode-property enumeration loops, testing only the first 3 and last 3 modes when the count exceeds 6.
- No rendering or shader execution occurs in any test -- these are pure API query/validation tests.
- The `create_display_plane_surface` test only creates surfaces on planes where `minDstExtent` matches the mode's `visibleRegion` and opaque alpha is supported; other plane configurations are skipped.
