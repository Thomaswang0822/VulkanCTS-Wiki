# [vktApiDeviceDrmPropertiesTests.cpp](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1)

## Overview

Tests for the `VK_EXT_physical_device_drm` extension, which exposes DRM (Direct Rendering Manager) device properties such as primary and render node major/minor numbers. The file verifies that the DRM device file nodes reported by the Vulkan implementation actually exist on the system by cross-referencing them with the DRM subsystem via `libdrm`.

## Role of File

Implementation-heavy. Contains the test logic, support check, and registration function. Uses a single `TestType` enum and a free-function test pattern via `addFunctionCase`.

## Source Code

| File | Path |
|------|------|
| Source | [vktApiDeviceDrmPropertiesTests.cpp](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1) |
| Header | [vktApiDeviceDrmPropertiesTests.hpp](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.hpp#L1) |
| Parent registration | [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L98) |

## Registration Path

```
api
└── device_drm_properties            (non-VKSC only, vktApiTests.cpp#L98)
    └── drm_files_exist
```

## Test Hierarchy

```
device_drm_properties
└── drm_files_exist
```

## Test Families

### drm_files_exist

Queries `VkPhysicalDeviceDrmPropertiesEXT` via `vkGetPhysicalDeviceProperties2` ([line 96](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L96)), then verifies that at least one of the reported DRM device nodes (primary or render) actually exists on the system. When `DEQP_SUPPORT_DRM` is defined and the build is not VulkanSC, the test uses `tcu::LibDrm` to enumerate DRM devices and match them by major/minor numbers ([line 58-71](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58)). If neither the primary nor render node is found, the test throws `NotSupportedError` rather than failing, since the absence may be environment-dependent ([line 75-77](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L75)).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| TestType | TEST_FILES_EXIST | [line 43-45](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L43) |

Only one test type exists. The enum appears to be structured for potential future expansion but currently has a single value.

## Support / Feature Requirements

| Requirement | Source |
|-------------|--------|
| VK_EXT_physical_device_drm | [line 50](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L50) |
| DEQP_SUPPORT_DRM (compile-time) | [line 58](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58) |
| Not CTS_USES_VULKANSC (compile-time) | [line 58](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58) |

Note: The `DEQP_SUPPORT_DRM` and `CTS_USES_VULKANSC` guards are compile-time conditions, not runtime checks. When DRM is not supported at compile time, the test still runs but can only verify that at least one of `hasPrimary` or `hasRender` is false (i.e., the Vulkan implementation reports no DRM nodes), otherwise it passes trivially since `primaryFound`/`renderFound` default to true when the corresponding `hasPrimary`/`hasRender` flags are false ([line 55-56](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L55)).

## Verification Methods

- **DRM node existence**: The test retrieves `VkPhysicalDeviceDrmPropertiesEXT` and, when libdrm is available, calls `libDrm.findDeviceNode()` for both primary and render major/minor pairs ([line 64-68](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L64)). If neither node is found, `NotSupportedError` is thrown ([line 76](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L76)). If at least one is found, the test passes.
- **Structure pre-fill check**: The `VkPhysicalDeviceProperties2` struct is pre-filled with `0xaa` bytes before the query call ([line 85-92](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L85)), which can help detect uninitialized fields, though no explicit verification of this is performed in the current code.

## Test Principles Observed

- **Environment-aware graceful degradation**: Uses `NotSupportedError` rather than `fail` when DRM nodes are not found, acknowledging this may be environment-dependent ([line 76](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L76)).
- **Compile-time platform gating**: The libdrm integration is conditionally compiled based on `DEQP_SUPPORT_DRM` and `CTS_USES_VULKANSC` ([line 58](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58)).
- **Extension requirement**: Explicitly checks for `VK_EXT_physical_device_drm` before running ([line 50](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L50)).

## Notes / Uncertainties

- The header file comment says "VK_KHR_driver_properties tests" ([vktApiDeviceDrmPropertiesTests.hpp#L25](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.hpp#L25)), which appears to be a copy-paste error; the actual extension tested is `VK_EXT_physical_device_drm`.
- The `TestType` enum has only one value (`TEST_FILES_EXIST`), suggesting the framework was designed for additional test types that were never added or are planned for the future.
- When `DEQP_SUPPORT_DRM` is not defined, the test logic in `testFilesExist` reduces to checking if `hasPrimary` or `hasRender` are false (in which case the corresponding "found" variable defaults to true), meaning the test effectively always passes on non-DRM platforms as long as the extension is supported.
- The `checkSupport` function does not use its `config` parameter ([line 49](../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L49)).
