# [vktApiDeviceDrmPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1)

## Overview

[`vktApiDeviceDrmPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.device_drm_properties` subtree. It registers one direct child, `drm_files_exist`, and that leaf verifies that the DRM major/minor node numbers reported through `VK_EXT_physical_device_drm` correspond to device nodes visible on the system.

## Role of File

Implementation-heavy test file for the `api.device_drm_properties` subgroup. The public entry point is [`createDeviceDrmPropertiesTests()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L118-L121).

## Source Code

- Primary source: [vktApiDeviceDrmPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1)
- Header: [vktApiDeviceDrmPropertiesTests.hpp](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L100-L140)

## Registration Hierarchy

```text
api.device_drm_properties
└── drm_files_exist
```

The confirmed Level-3 root is `api.device_drm_properties`, created by [`createDeviceDrmPropertiesTests()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L118-L121) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L136-L136). The exact direct child confirmed from [`createTestCases()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L110-L114) is `drm_files_exist`, added through [`addFunctionCase(group, "drm_files_exist", ...)`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L113-L113).

## Test Families

### drm_files_exist — DRM node existence validation

Covers the only direct child registered by [`createTestCases()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L110-L114). The leaf executes [`testDeviceDrmProperties()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L80-L108), which queries [`VkPhysicalDeviceDrmPropertiesEXT`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L86-L96) through [`getPhysicalDeviceProperties2()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L96-L96) and then dispatches to [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78).

The execution flow observed in [`testDeviceDrmProperties()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L80-L108) is:

1. Zero-initialize [`VkPhysicalDeviceDrmPropertiesEXT`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L88-L90).
2. Fill [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L84-L94) with the `0xaa` pattern before setting the required `sType` and `pNext` fields.
3. Chain the DRM extension struct through `pNext` and call [`getPhysicalDeviceProperties2()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L94-L96).
4. For `TEST_FILES_EXIST`, pass the queried DRM properties to [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L98-L102).

Within [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78), the test:

- Treats a missing primary or render requirement as already satisfied by initializing `primaryFound` from `!hasPrimary` and `renderFound` from `!hasRender` in [`vktApiDeviceDrmPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L55-L56).
- When DRM support is compiled in and Vulkan SC is not in use, enumerates DRM devices through [`tcu::LibDrm`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58-L71).
- Uses [`findDeviceNode()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L64-L69) to look up both the primary and render major/minor pairs reported by the driver.
- Throws [`NotSupportedError`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L74-L77) if neither reported DRM node can be resolved to an existing device file.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child subgroup | `drm_files_exist` from [`createTestCases()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L110-L114) |
| Test type enum | `TEST_FILES_EXIST` in [`enum TestType`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L42-L45) |
| DRM node categories | `primary` and `render` from the `hasPrimary` / `hasRender` flags and corresponding major/minor fields consumed in [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L55-L69) |
| Property-query fill pattern | `0xaa` stored in `memsetPattern` before the query in [`testDeviceDrmProperties()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L84-L94) |

## Support / Feature Requirements

- `VK_EXT_physical_device_drm` is required for the leaf by [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L47-L51).
- Actual DRM device enumeration requires the `DEQP_SUPPORT_DRM` build flag and excludes Vulkan SC builds through the preprocessor guard in [`vktApiDeviceDrmPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58-L72).
- The validation is effectively Linux/DRM-platform-specific because it depends on DRM device discovery via [`tcu::LibDrm`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58-L71).

## Verification Methods

- **DRM node existence**: [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78) resolves the primary and render major/minor values against enumerated DRM devices using [`findDeviceNode()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L64-L69).
- **Failure condition**: the test reports failure by throwing [`NotSupportedError`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L74-L77) when neither expected DRM node is found.
- **Property query initialization guard**: [`testDeviceDrmProperties()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L84-L96) pre-fills [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L84-L94) with `0xaa` before invoking the Vulkan query.

## Test Principles Observed

- Cross-check extension-reported DRM metadata against actual platform-visible DRM device nodes.
- Use the Vulkan `pNext` chain to request extension-specific physical-device properties.
- Treat primary and render DRM nodes as separate validation targets while allowing platforms to report only one of them.

## Notes / Uncertainties

- The canonical normalization for this page confirms the Level-3 root as `api.device_drm_properties` and the only direct child as `drm_files_exist`.
- If `DEQP_SUPPORT_DRM` is not enabled, the DRM enumeration block is compiled out, so success depends only on the initial `hasPrimary` / `hasRender` state handled in [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L55-L56).
- The inspected code does not explicitly validate the non-DRM members of [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L84-L96) after the query.
