# [vktApiMaintenance7Tests.cpp](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1)

## Overview

Tests the VK_KHR_maintenance7 extension by validating layered API Vulkan properties (deviceID/vendorID consistency and limits zero-fill behavior) and total dynamic buffer property constraints (ensuring aggregate dynamic buffer limits are at least as large as their individual counterparts from Vulkan 1.0 and 1.2 properties).

## Role of File

Implementation-heavy. Contains two test instance/case pairs and the registration entry point. The entire file is wrapped in a `#ifndef CTS_USES_VULKANSC` guard, making it non-VKSC only.

## Source Code

- Implementation: [vktApiMaintenance7Tests.cpp](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1)
- Header: [vktApiMaintenance7Tests.hpp](../../modules/vulkan/api/vktApiMaintenance7Tests.hpp#L1)
- Registration function: [createMaintenance7Tests()](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L307)
- Registered under: api -> maintenance7

## Registration Path

```
api
+-- maintenance7
    +-- maintenance7
```

## Test Hierarchy

```
maintenance7
+-- layered_api_vulkan_properties
+-- total_dynamic_buffers_properties
```

## Test Families

### layered_api_vulkan_properties

Queries VkPhysicalDeviceLayeredApiPropertiesListKHR to discover layered APIs, then for each layered API entry verifies two things: (1) if the layered API is VK_PHYSICAL_DEVICE_LAYERED_API_VULKAN_KHR, the deviceID and vendorID in VkPhysicalDeviceLayeredApiPropertiesKHR must match those in VkPhysicalDeviceLayeredApiVulkanPropertiesKHR; (2) the limits and sparseProperties structures in VkPhysicalDeviceLayeredApiVulkanPropertiesKHR must be zero-filled for Vulkan layers and must remain untouched (still 0xFF-filled) for non-Vulkan layers. The test pre-fills limits and sparseProperties with 0xFF to detect whether the implementation writes to them.

- Instance: [Maintenance7LayeredApiVulkanPropertiesTestInstance](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L37)
- Case: [Maintenance7LayeredApiVulkanPropertiesTestCase](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L180)
- Support gate: [VK_KHR_maintenance7](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L190)
- Two-pass query: First query gets layeredApiCount ([L65-L66](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L65)), second query fills properties ([L88](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L88))
- deviceID/vendorID check: [L93-L110](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L93)
- Limits zero-fill check: [L113-L142](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L113)
- SparseProperties zero-fill check: [L143-L173](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L143)

### total_dynamic_buffers_properties

Queries VkPhysicalDeviceMaintenance7PropertiesKHR and validates that the new aggregate dynamic buffer limits are consistent with existing limits: maxDescriptorSetTotalUniformBuffersDynamic >= maxDescriptorSetUniformBuffersDynamic, maxDescriptorSetTotalStorageBuffersDynamic >= maxDescriptorSetStorageBuffersDynamic, maxDescriptorSetTotalBuffersDynamic >= sum of uniform + storage dynamic, and the same three checks for the update-after-bind variants using Vulkan 1.2 properties.

- Instance: [Maintenance7TotalDynamicBuffersPropertiesTestInstance](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L200)
- Case: [Maintenance7TotalDynamicBuffersPropertiesTestCase](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L289)
- Support gate: [VK_KHR_maintenance7](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L299)
- Vulkan 1.0 dynamic buffer checks: [L221-L249](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221)
- Vulkan 1.2 update-after-bind dynamic buffer checks: [L252-L284](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L252)

## Parameter Dimensions

This file has no parameterized dimensions. Each test family consists of a single test case.

## Support / Feature Requirements

| Requirement | Where | Context |
|---|---|---|
| VK_KHR_maintenance7 | [L190](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L190), [L299](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L299) | Both test families |
| Non-VKSC build | [L30](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L30) | Entire file guarded |

## Verification Methods

- **ID consistency**: Compares deviceID and vendorID between VkPhysicalDeviceLayeredApiPropertiesKHR and VkPhysicalDeviceLayeredApiVulkanPropertiesKHR for Vulkan-layered APIs ([L95-L109](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L95))
- **Zero-fill detection**: Pre-fills limits/sparseProperties with 0xFF, then checks they are zeroed for Vulkan layers and untouched for non-Vulkan layers ([L78-L79](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L78), [L113-L173](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L113))
- **Property inequality**: Verifies that maintenance7 aggregate dynamic buffer limits are >= individual limits from VkPhysicalDeviceProperties and VkPhysicalDeviceVulkan12Properties ([L221-L284](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221))

## Test Principles Observed

- **Sentinel pre-fill**: Uses 0xFF memset to detect whether the implementation writes to output structures ([L78-L79](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L78))
- **Cross-property consistency**: Validates that new aggregate limits are consistent with existing per-category limits ([L221-L284](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221))
- **Two-pass query pattern**: First queries count, allocates, then queries data for layered API properties ([L65-L88](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L65))

## Notes / Uncertainties

- The layered_api_vulkan_properties test has a likely copy-paste error in its log messages: when the layeredAPI is not VK_PHYSICAL_DEVICE_LAYERED_API_VULKAN_KHR, the log message still says "is VK_PHYSICAL_DEVICE_LAYERED_API_VULKAN_KHR" at [L133-L138](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L133) and [L165-L170](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L165). The logic itself is correct (it checks for non-Vulkan), but the message is misleading.
- The test does not cover other VK_KHR_maintenance7 properties such as maxFragmentShadingRateAttachmentSize, maxMeshWorkGroupTotalCount, etc.
- The total_dynamic_buffers_properties test relies on getDeviceVulkan12Properties() at [L252](../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L252), which may throw if Vulkan 1.2 is not available. The VK_KHR_maintenance7 requirement likely implies Vulkan 1.1+ but the test does not explicitly check for Vulkan 1.2.
