# [vktApiDeviceDrmPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1)

## Overview

Tests VK_EXT_physical_device_drm by querying `VkPhysicalDeviceDrmPropertiesEXT` and verifying that DRM device files corresponding to the reported primary and render major/minor node numbers exist on the system.

## Role of File

Implementation-heavy. Contains test logic, DRM library integration, and registration.

## Source Code

| File | Description |
|------|-------------|
| [vktApiDeviceDrmPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1) | Test implementation and registration |
| [vktApiDeviceDrmPropertiesTests.hpp](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.hpp#L1) | Declares `createDeviceDrmPropertiesTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L98) | Parent registration: `apiTests->addChild(createDeviceDrmPropertiesTests(testCtx))` |

## Registration Path

```
api
  +-- device_drm_properties
       +-- drm_files_exist
```

## Test Hierarchy

```
device_drm_properties
  +-- drm_files_exist
       Queries VkPhysicalDeviceDrmPropertiesEXT and verifies
       that DRM device nodes exist for reported major/minor numbers
```

## Test Families

### device_drm_properties

Group name verified at [vktApiDeviceDrmPropertiesTests.cpp:120](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L120): `createTestGroup(testCtx, "device_drm_properties", createTestCases)`.

Single test case `drm_files_exist` at [line 113](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L113).

The test function `testDeviceDrmProperties` at [line 80](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L80):
1. Pre-fills `VkPhysicalDeviceDrmPropertiesEXT` with zeros and `VkPhysicalDeviceProperties2` with 0xAA pattern ([lines 86-94](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L86))
2. Chains `VkPhysicalDeviceDrmPropertiesEXT` into `VkPhysicalDeviceProperties2.pNext` ([line 94](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L94))
3. Calls `getPhysicalDeviceProperties2` ([line 96](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L96))
4. Calls `testFilesExist` which checks DRM device nodes ([line 101](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L101))

The `testFilesExist` function at [line 53](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53):
- If `hasPrimary` is true, searches for a DRM device node matching `primaryMajor`/`primaryMinor`
- If `hasRender` is true, searches for a DRM device node matching `renderMajor`/`renderMinor`
- Uses `tcu::LibDrm` to enumerate DRM devices when `DEQP_SUPPORT_DRM` is defined ([line 58](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58))
- Throws `NotSupportedError` if neither primary nor render device files are found ([lines 74-77](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L74))

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Test type | TEST_FILES_EXIST | Only one test type defined |
| DRM node type | Primary, Render | Both checked if hasPrimary/hasRender is true |

## Support / Feature Requirements

- `VK_EXT_physical_device_drm` required via `checkSupport` at [line 50](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L50)
- `DEQP_SUPPORT_DRM` must be defined at compile time for actual DRM device node lookup ([line 58](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58))
- `CTS_USES_VULKANSC` must not be defined for DRM lookup ([line 58](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L58))

## Verification Methods

- **DRM node existence**: Uses `tcu::LibDrm::findDeviceNode` to search for DRM device nodes matching the major/minor numbers reported in `VkPhysicalDeviceDrmPropertiesEXT` ([lines 64-69](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L64))
- **Pre-fill pattern**: The `VkPhysicalDeviceProperties2` structure is pre-filled with 0xAA to detect if the implementation writes to it correctly ([line 85](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L85))

## Test Principles Observed

- Platform integration: verifies that Vulkan DRM properties correspond to actual system DRM devices
- Property validation: checks that reported DRM node numbers are usable

## Notes / Uncertainties

- Without `DEQP_SUPPORT_DRM`, the test always passes as long as at least one of `hasPrimary` or `hasRender` is false, because `primaryFound`/`renderFound` default to true when the corresponding `has*` flag is false ([line 55](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L55))
- The test does not verify the content of `VkPhysicalDeviceProperties2.properties` beyond the DRM extension; the 0xAA pre-fill is not checked after the query
- This test is Linux-specific due to its dependency on DRM
