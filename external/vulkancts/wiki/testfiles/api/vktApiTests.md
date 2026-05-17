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

## Registration Hierarchy

```text
api
├── version_check
├── debug_utils
├── driver_properties
├── smoke (not in Vulkan SC)
├── info
├── device_drm_properties (not in Vulkan SC)
├── device_init
├── object_management
├── buffer
├── buffer_marker (not in Vulkan SC)
├── buffer_view
├── command_buffers
├── copy_and_blit
├── ds_color_copy
├── image_clearing
├── fill_and_update_buffer
├── descriptor_pool
├── null_handle
├── granularity
├── get_memory_commitment
├── external (not in Vulkan SC)
├── maintenance3_check
├── descriptor_set
├── pipeline
├── invariance
├── tooling_info (not in Vulkan SC)
├── format_feature_flags2 (not in Vulkan SC)
├── buffer_memory_requirements
├── image_compression_control (not in Vulkan SC)
├── get_device_proc_addr (not in Vulkan SC)
├── maintenance6_check (not in Vulkan SC)
├── frame_boundary (not in Vulkan SC)
├── maintenance5 (not in Vulkan SC)
├── fragment_shader_output (not in Vulkan SC)
├── maintenance7 (not in Vulkan SC)
├── device_address (not in Vulkan SC)
├── extension_duplicates
└── performance_counters_by_region (not in Vulkan SC)
```

Evidence:
- root registration in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86)
- verified against mustpass [`api.txt`](../../../mustpass/main/vk-default/api.txt)

## Test Families

### version_check — Version sanity check

Registered by [`createVersionSanityCheckTests()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L1). See [`vktApiVersionCheck.md`](vktApiVersionCheck.md).

### debug_utils — Debug utilities

Registered by [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1). See [`vktApiDebugUtilsTests.md`](vktApiDebugUtilsTests.md).

### driver_properties — Driver properties

Registered by [`createDriverPropertiesTests()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1). See [`vktApiDriverPropertiesTests.md`](vktApiDriverPropertiesTests.md).

### smoke — Smoke tests (not in Vulkan SC)

Registered by [`createSmokeTests()`](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L1). See [`vktApiSmokeTests.md`](vktApiSmokeTests.md).

### info — Feature info queries

Registered by [`api::createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1). See [`vktApiFeatureInfo.md`](vktApiFeatureInfo.md).

### device_drm_properties — Device DRM properties (not in Vulkan SC)

Registered by [`createDeviceDrmPropertiesTests()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1). See [`vktApiDeviceDrmPropertiesTests.md`](vktApiDeviceDrmPropertiesTests.md).

### device_init — Device initialization

Registered by [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1). See [`vktApiDeviceInitializationTests.md`](vktApiDeviceInitializationTests.md).

### object_management — Object lifecycle management

Registered by [`createObjectManagementTests()`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1). See [`vktApiObjectManagementTests.md`](vktApiObjectManagementTests.md).

### buffer — Buffer creation and properties

Registered by [`createBufferTests()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L1). See [`vktApiBufferTests.md`](vktApiBufferTests.md).

### buffer_marker — Buffer marker tests (not in Vulkan SC)

Registered by [`createBufferMarkerTests()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1). See [`vktApiBufferMarkerTests.md`](vktApiBufferMarkerTests.md).

### buffer_view — Buffer view creation and access

Composite group registered by the local helper [`createBufferViewTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L78), which combines two sub-factories:
- `create` from [`createBufferViewCreateTests()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1)
- `access` from [`createBufferViewAccessTests()`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1)

See [`vktApiBufferViewCreateTests.md`](vktApiBufferViewCreateTests.md) and [`vktApiBufferViewAccessTests.md`](vktApiBufferViewAccessTests.md).

### command_buffers — Command buffer tests

Registered by [`createCommandBuffersTests()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1). See [`vktApiCommandBuffersTests.md`](vktApiCommandBuffersTests.md).

### copy_and_blit — Copy and blit operations

Registered by [`createCopiesAndBlittingTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1). See [`vktApiCopiesAndBlittingTests.md`](vktApiCopiesAndBlittingTests.md).

### ds_color_copy — Depth-stencil and color bit copy

Registered by [`createDSColorBitCopyTests()`](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1). See [`vktApiDSColorBitCopyTests.md`](vktApiDSColorBitCopyTests.md).

### image_clearing — Image clearing operations

Registered by [`createImageClearingTests()`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1). See [`vktApiImageClearingTests.md`](vktApiImageClearingTests.md).

### fill_and_update_buffer — Fill and update buffer

Registered by [`createFillAndUpdateBufferTests()`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1). See [`vktApiFillBufferTests.md`](vktApiFillBufferTests.md).

### descriptor_pool — Descriptor pool

Registered by [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1). See [`vktApiDescriptorPoolTests.md`](vktApiDescriptorPoolTests.md).

### null_handle — Null handle tests

Registered by [`createNullHandleTests()`](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1). See [`vktApiNullHandleTests.md`](vktApiNullHandleTests.md).

### granularity — Granularity query

Registered by [`createGranularityQueryTests()`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1). See [`vktApiGranularityTests.md`](vktApiGranularityTests.md).

### get_memory_commitment — Memory commitment query

Registered by [`createMemoryCommitmentTests()`](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1). See [`vktApiGetMemoryCommitment.md`](vktApiGetMemoryCommitment.md).

### external — External memory (not in Vulkan SC)

Registered by [`createExternalMemoryTests()`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1). See [`vktApiExternalMemoryTests.md`](vktApiExternalMemoryTests.md).

### maintenance3_check — Maintenance3 check

Registered by [`createMaintenance3Tests()`](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1). See [`vktApiMaintenance3Check.md`](vktApiMaintenance3Check.md).

### descriptor_set — Descriptor set

Registered by [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1). See [`vktApiDescriptorSetTests.md`](vktApiDescriptorSetTests.md).

### pipeline — Pipeline tests

Registered by [`createPipelineTests()`](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1). See [`vktApiPipelineTests.md`](vktApiPipelineTests.md).

### invariance — Memory requirement invariance

Registered by [`createMemoryRequirementInvarianceTests()`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1). See [`vktApiMemoryRequirementInvarianceTests.md`](vktApiMemoryRequirementInvarianceTests.md).

### tooling_info — Tooling information (not in Vulkan SC)

Registered by [`createToolingInfoTests()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1). See [`vktApiToolingInfoTests.md`](vktApiToolingInfoTests.md).

### format_feature_flags2 — Extended format feature flags (not in Vulkan SC)

Registered by [`createFormatPropertiesExtendedKHRTests()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1). See [`vktApiFormatPropertiesExtendedKHRtests.md`](vktApiFormatPropertiesExtendedKHRtests.md).

### buffer_memory_requirements — Buffer memory requirements

Registered by [`createBufferMemoryRequirementsTests()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1). See [`vktApiBufferMemoryRequirementsTests.md`](vktApiBufferMemoryRequirementsTests.md).

### image_compression_control — Image compression control (not in Vulkan SC)

Registered by [`createImageCompressionControlTests()`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1). See [`vktApiImageCompressionControlTests.md`](vktApiImageCompressionControlTests.md).

### get_device_proc_addr — Get device procedure address (not in Vulkan SC)

Registered by [`createGetDeviceProcAddrTests()`](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L1). See [`vktApiGetDeviceProcAddrTests.md`](vktApiGetDeviceProcAddrTests.md).

### maintenance6_check — Maintenance6 check (not in Vulkan SC)

Registered by [`createMaintenance6Games()`](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1). See [`vktApiMaintenance6Check.md`](vktApiMaintenance6Check.md).

### frame_boundary — Frame boundary (not in Vulkan SC)

Registered by [`createFrameBoundaryTests()`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1). See [`vktApiFrameBoundaryTests.md`](vktApiFrameBoundaryTests.md).

### maintenance5 — Maintenance5 format properties (not in Vulkan SC)

Registered by [`createMaintenance5Tests()`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1). See [`vktApiPhysicalDeviceFormatPropertiesMaint5Tests.md`](vktApiPhysicalDeviceFormatPropertiesMaint5Tests.md).

### fragment_shader_output — Fragment shader output (not in Vulkan SC)

Registered by [`createFragmentShaderOutputTests()`](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1). See [`vktApiFragmentShaderOutputTests.md`](vktApiFragmentShaderOutputTests.md).

### maintenance7 — Maintenance7 (not in Vulkan SC)

Registered by [`createMaintenance7Tests()`](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1). See [`vktApiMaintenance7Tests.md`](vktApiMaintenance7Tests.md).

### device_address — Device address commands (not in Vulkan SC)

Registered by [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1). See [`vktApiDeviceAddressCommandsTests.md`](vktApiDeviceAddressCommandsTests.md).

### extension_duplicates — Extension duplicates

Registered by [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1). See [`vktApiExtensionDuplicatesTests.md`](vktApiExtensionDuplicatesTests.md).

### performance_counters_by_region — Performance counters by region (not in Vulkan SC)

Registered by [`createRenderPassPerformanceCountersByRegionApiTests()`](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1). See [`vktApiPerformanceCountersByRegionTests.md`](vktApiPerformanceCountersByRegionTests.md).

## Notes / Uncertainties

- 18 of 38 group names differ from their factory symbol names. For example, `createMemoryRequirementInvarianceTests()` produces the group `invariance`, not `memory_requirement_invariance`. The full factory-symbol-to-group-name mapping was recorded during analysis in an internal tracker, but that tracker is not currently part of the committed wiki tree.
- `buffer_view` is a composite group built by a local helper in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L78) that combines two sub-factories for `create` and `access` children.
- 15 of the 38 groups are guarded by `#ifndef CTS_USES_VULKANSC` and are only available in non-VulkanSC builds.
