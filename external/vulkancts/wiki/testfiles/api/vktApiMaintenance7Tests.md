# [vktApiMaintenance7Tests.cpp](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1)

## Overview

Tests VK_KHR_maintenance7 by verifying two properties: (1) `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` is correctly populated for layered Vulkan implementations, including deviceID/vendorID consistency and zero-filling of limits/sparseProperties, and (2) `VkPhysicalDeviceMaintenance7PropertiesKHR` dynamic buffer descriptor limits are consistent with existing Vulkan 1.0 and Vulkan 1.2 limits.

## Role of File

Implementation-heavy. Contains two test instance classes and registration logic.

## Source Code

| File | Description |
|------|-------------|
| [vktApiMaintenance7Tests.cpp](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1) | Test implementation and registration |
| [vktApiMaintenance7Tests.hpp](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.hpp#L1) | Declares `createMaintenance7Tests` |
| [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L135) | Parent registration: `apiTests->addChild(createMaintenance7Tests(testCtx))` |

## Registration Path

```
api
  +-- maintenance7
       +-- layered_api_vulkan_properties
       +-- total_dynamic_buffers_properties
```

## Test Hierarchy

```
maintenance7
  +-- layered_api_vulkan_properties
  |    Verifies VkPhysicalDeviceLayeredApiVulkanPropertiesKHR:
  |    - deviceID/vendorID match between layered and base properties
  |    - limits/sparseProperties are zero-filled for Vulkan layered APIs
  |    - limits/sparseProperties are ignored for non-Vulkan layered APIs
  +-- total_dynamic_buffers_properties
       Verifies VkPhysicalDeviceMaintenance7PropertiesKHR:
       - maxDescriptorSetTotalUniformBuffersDynamic >= maxDescriptorSetUniformBuffersDynamic
       - maxDescriptorSetTotalStorageBuffersDynamic >= maxDescriptorSetStorageBuffersDynamic
       - maxDescriptorSetTotalBuffersDynamic >= sum of uniform + storage dynamic
       - Same checks for update-after-bind variants
```

## Test Families

### maintenance7

Group name verified at [vktApiMaintenance7Tests.cpp:310](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L310): `new tcu::TestCaseGroup(testCtx, "maintenance7", "Maintenance7 Tests")`.

Two test cases added at [lines 312-314](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L312):

**layered_api_vulkan_properties** - `Maintenance7LayeredApiVulkanPropertiesTestInstance` at [line 37](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L37):
1. Queries `VkPhysicalDeviceLayeredApiPropertiesListKHR` via `getPhysicalDeviceProperties2` ([line 65](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L65))
2. If layered APIs are reported, allocates `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` chains with pre-filled 0xFF in limits/sparseProperties ([lines 78-81](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L78))
3. Re-queries and verifies: for Vulkan layered APIs, deviceID/vendorID must match, and limits/sparseProperties must be zero-filled ([lines 93-173](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L93))
4. For non-Vulkan layered APIs, limits/sparseProperties must remain at 0xFF (ignored) ([lines 130-172](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L130))

**total_dynamic_buffers_properties** - `Maintenance7TotalDynamicBuffersPropertiesTestInstance` at [line 200](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L200):
1. Queries `VkPhysicalDeviceMaintenance7PropertiesKHR` ([line 213](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L213))
2. Verifies 6 inequalities against Vulkan 1.0 and 1.2 device limits ([lines 221-284](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221))

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Layered API count | Implementation-dependent | Queried at runtime |
| Buffer limit type | Uniform, Storage, Total | Both regular and update-after-bind |

## Support / Feature Requirements

- `VK_KHR_maintenance7` required by both test cases via `checkSupport` at [line 190](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L190) and [line 299](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L299)
- Entire file is guarded by `#ifndef CTS_USES_VULKANSC` at [line 30](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L30)

## Verification Methods

- **deviceID/vendorID consistency**: For each Vulkan layered API, `VkPhysicalDeviceLayeredApiPropertiesKHR::deviceID` must equal `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR::properties::properties::deviceID` (same for vendorID) ([lines 95-110](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L95))
- **Zero-fill verification**: Byte-by-byte check that limits and sparseProperties are all zeros for Vulkan layered APIs ([lines 113-128](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L113))
- **Ignore verification**: Byte-by-byte check that limits and sparseProperties remain 0xFF for non-Vulkan layered APIs ([lines 130-172](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L130))
- **Descriptor limit inequalities**: 6 separate inequality checks between maintenance7 properties and existing device limits ([lines 221-284](../../../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221))

## Test Principles Observed

- Property consistency: layered API properties must be consistent with base device properties
- Limit monotonicity: total dynamic buffer limits must be at least as large as their component limits
- Robustness: pre-fills structures with 0xFF to detect whether the implementation writes to them

## Notes / Uncertainties

- The layered_api_vulkan_properties test passes trivially if no layered APIs are reported (layeredApiCount == 0)
- The total_dynamic_buffers_properties test relies on `getDeviceVulkan12Properties()` for update-after-bind limits, which may not be available on all implementations
