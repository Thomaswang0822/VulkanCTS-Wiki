# [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L1)

## Overview

This is the root registration file for the API category. It defines [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86) which assembles all 38 top-level groups into the `api` test tree. The file serves as the single entry point through which every API sub-test is registered with the CTS framework.

## Role of File

**Registration / Dispatcher** -- This file does not contain any test logic itself. It includes headers for each sub-module and attaches the resulting `tcu::TestCaseGroup` children to the root `api` group. The public entry point is [`createTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L146).

## Source Code

| File | Description |
|------|-------------|
| [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L1) | Root registration implementation |
| [`vktApiTests.hpp`](../../../modules/vulkan/api/vktApiTests.hpp#L1) | Public header declaring `createTests()` |

## Registration Path

```text
api
├── version_check
├── debug_utils
├── driver_properties
├── smoke                    [not in Vulkan SC]
├── info
├── device_drm_properties    [not in Vulkan SC]
├── device_init
├── object_management
├── buffer
├── buffer_marker            [not in Vulkan SC]
├── buffer_view
│   ├── create
│   └── access
├── command_buffers
├── copy_and_blit
├── ds_color_copy
├── image_clearing
├── fill_and_update_buffer
├── descriptor_pool
├── null_handle
├── granularity
├── get_memory_commitment
├── external                 [not in Vulkan SC]
├── maintenance3_check
├── descriptor_set
├── pipeline
├── invariance
├── tooling_info             [not in Vulkan SC]
├── format_feature_flags2    [not in Vulkan SC]
├── buffer_memory_requirements
├── image_compression_control [not in Vulkan SC]
├── get_device_proc_addr     [not in Vulkan SC]
├── maintenance6_check       [not in Vulkan SC]
├── frame_boundary           [not in Vulkan SC]
├── maintenance5             [not in Vulkan SC]
├── fragment_shader_output   [not in Vulkan SC]
├── maintenance7
├── device_address           [not in Vulkan SC]
├── extension_duplicates
└── performance_counters_by_region [not in Vulkan SC]
```

Source: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86), verified against mustpass [`api.txt`](../../../mustpass/main/vk-default/api.txt).

## Registered Subgroups

| Group Name | VKSC-only | Source |
|---|---|---|
| `version_check` | No | [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L1) |
| `debug_utils` | No | [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1) |
| `driver_properties` | No | [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1) |
| `smoke` | Yes | [`vktApiSmokeTests.cpp`](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L1) |
| `info` | No | [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1) |
| `device_drm_properties` | Yes | [`vktApiDeviceDrmPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1) |
| `device_init` | No | [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1) |
| `object_management` | No | [`vktApiObjectManagementTests.cpp`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1) |
| `buffer` | No | [`vktApiBufferTests.cpp`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L1) |
| `buffer_marker` | Yes | [`vktApiBufferMarkerTests.cpp`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1) |
| `buffer_view` | No | [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1), [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1) |
| `command_buffers` | No | [`vktApiCommandBuffersTests.cpp`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1) |
| `copy_and_blit` | No | [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1) |
| `ds_color_copy` | No | [`vktApiDSColorBitCopyTests.cpp`](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1) |
| `image_clearing` | No | [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1) |
| `fill_and_update_buffer` | No | [`vktApiFillBufferTests.cpp`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1) |
| `descriptor_pool` | No | [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1) |
| `null_handle` | No | [`vktApiNullHandleTests.cpp`](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1) |
| `granularity` | No | [`vktApiGranularityTests.cpp`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1) |
| `get_memory_commitment` | No | [`vktApiGetMemoryCommitment.cpp`](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1) |
| `external` | Yes | [`vktApiExternalMemoryTests.cpp`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1) |
| `maintenance3_check` | No | [`vktApiMaintenance3Check.cpp`](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1) |
| `descriptor_set` | No | [`vktApiDescriptorSetTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1) |
| `pipeline` | No | [`vktApiPipelineTests.cpp`](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1) |
| `invariance` | No | [`vktApiMemoryRequirementInvarianceTests.cpp`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1) |
| `tooling_info` | Yes | [`vktApiToolingInfoTests.cpp`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1) |
| `format_feature_flags2` | Yes | [`vktApiFormatPropertiesExtendedKHRtests.cpp`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1) |
| `buffer_memory_requirements` | No | [`vktApiBufferMemoryRequirementsTests.cpp`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1) |
| `image_compression_control` | Yes | [`vktApiImageCompressionControlTests.cpp`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1) |
| `get_device_proc_addr` | Yes | [`vktApiGetDeviceProcAddrTests.cpp`](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L1) |
| `maintenance6_check` | Yes | [`vktApiMaintenance6Check.cpp`](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1) |
| `frame_boundary` | Yes | [`vktApiFrameBoundaryTests.cpp`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1) |
| `maintenance5` | Yes | [`vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1) |
| `fragment_shader_output` | Yes | [`vktApiFragmentShaderOutputTests.cpp`](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1) |
| `maintenance7` | No | [`vktApiMaintenance7Tests.cpp`](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1) |
| `device_address` | Yes | [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) |
| `extension_duplicates` | No | [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1) |
| `performance_counters_by_region` | Yes | [`vktApiPerformanceCountersByRegionTests.cpp`](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1) |

## Notes / Uncertainties

- 18 of 38 group names differ from their factory symbol names. For example, `createMemoryRequirementInvarianceTests()` produces the group `invariance`, not `memory_requirement_invariance`. The full factory-symbol-to-group-name mapping is available in the internal tracker at [`api_tracker.md`](../../internal_doc/api_tracker.md).
- `buffer_view` is a composite group built by a local helper in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L78) that combines two sub-factories for `create` and `access` children.
- 16 of the 38 groups are guarded by `#ifndef CTS_USES_VULKANSC` and are only available in non-VulkanSC builds.
