# api

## Overview

The [`api`](../../../modules/vulkan/api/vktApiTests.cpp#L86) category is the main Vulkan API conformance bucket registered by [`createTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L146) and populated by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86). It covers foundational object-lifetime and buffer-contract validation, a large copy/blit subtree, and many additional API-focused subgroups.

## Registration Entry Point

The category is rooted in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86), which adds 38 top-level children. Group names below are verified against [`api.txt`](../../../external/vulkancts/mustpass/main/vk-default/api.txt).

```text
api
├── version_check
├── debug_utils
├── driver_properties
├── smoke                                  (not in Vulkan SC)
├── info
├── device_drm_properties                  (not in Vulkan SC)
├── device_init
├── object_management
├── buffer
├── buffer_marker                          (not in Vulkan SC)
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
├── external                              (not in Vulkan SC)
├── maintenance3_check
├── descriptor_set
├── pipeline
├── invariance
├── tooling_info                           (not in Vulkan SC)
├── format_feature_flags2                  (not in Vulkan SC)
├── buffer_memory_requirements
├── image_compression_control              (not in Vulkan SC)
├── get_device_proc_addr                   (not in Vulkan SC)
├── maintenance6_check                     (not in Vulkan SC)
├── frame_boundary                         (not in Vulkan SC)
├── maintenance5                           (not in Vulkan SC)
├── fragment_shader_output                 (not in Vulkan SC)
├── maintenance7
├── device_address                         (not in Vulkan SC)
├── extension_duplicates
└── performance_counters_by_region         (not in Vulkan SC)
```

Source: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86), verified against mustpass [`api.txt`](../../../external/vulkancts/mustpass/main/vk-default/api.txt).

## File Inventory

| File | Role | Verified group name | Level-3 doc |
|---|---|---|---|
| [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L1) | Registration / dispatcher | (root) | [`vktApiTests.md`](../testfiles/api/vktApiTests.md) |
| [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L1) | Implementation | `version_check` | [`vktApiVersionCheck.md`](../testfiles/api/vktApiVersionCheck.md) |
| [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1) | Implementation | `debug_utils` | [`vktApiDebugUtilsTests.md`](../testfiles/api/vktApiDebugUtilsTests.md) |
| [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1) | Implementation | `driver_properties` | [`vktApiDriverPropertiesTests.md`](../testfiles/api/vktApiDriverPropertiesTests.md) |
| [`vktApiSmokeTests.cpp`](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L1) | Implementation | `smoke` | [`vktApiSmokeTests.md`](../testfiles/api/vktApiSmokeTests.md) |
| [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1) | Implementation | `info` | [`vktApiFeatureInfo.md`](../testfiles/api/vktApiFeatureInfo.md) |
| [`vktApiDeviceDrmPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1) | Implementation | `device_drm_properties` | [`vktApiDeviceDrmPropertiesTests.md`](../testfiles/api/vktApiDeviceDrmPropertiesTests.md) |
| [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1) | Implementation | `device_init` | [`vktApiDeviceInitializationTests.md`](../testfiles/api/vktApiDeviceInitializationTests.md) |
| [`vktApiObjectManagementTests.cpp`](../../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1) | Implementation | `object_management` | [`vktApiObjectManagementTests.md`](../testfiles/api/vktApiObjectManagementTests.md) |
| [`vktApiBufferTests.cpp`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L1) | Implementation | `buffer` | [`vktApiBufferTests.md`](../testfiles/api/vktApiBufferTests.md) |
| [`vktApiBufferMarkerTests.cpp`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1) | Implementation | `buffer_marker` | [`vktApiBufferMarkerTests.md`](../testfiles/api/vktApiBufferMarkerTests.md) |
| [`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1) | Implementation | `buffer_view.create` | [`vktApiBufferViewCreateTests.md`](../testfiles/api/vktApiBufferViewCreateTests.md) |
| [`vktApiBufferViewAccessTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1) | Implementation | `buffer_view.access` | [`vktApiBufferViewAccessTests.md`](../testfiles/api/vktApiBufferViewAccessTests.md) |
| [`vktApiCommandBuffersTests.cpp`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1) | Implementation | `command_buffers` | [`vktApiCommandBuffersTests.md`](../testfiles/api/vktApiCommandBuffersTests.md) |
| [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1) | Registration / dispatcher | `copy_and_blit` | [`vktApiCopiesAndBlittingTests.md`](../testfiles/api/vktApiCopiesAndBlittingTests.md) |
| [`vktApiDSColorBitCopyTests.cpp`](../../../modules/vulkan/api/vktApiDSColorBitCopyTests.cpp#L1) | Implementation | `ds_color_copy` | [`vktApiDSColorBitCopyTests.md`](../testfiles/api/vktApiDSColorBitCopyTests.md) |
| [`vktApiImageClearingTests.cpp`](../../../modules/vulkan/api/vktApiImageClearingTests.cpp#L1) | Implementation | `image_clearing` | [`vktApiImageClearingTests.md`](../testfiles/api/vktApiImageClearingTests.md) |
| [`vktApiFillBufferTests.cpp`](../../../modules/vulkan/api/vktApiFillBufferTests.cpp#L1) | Implementation | `fill_and_update_buffer` | [`vktApiFillBufferTests.md`](../testfiles/api/vktApiFillBufferTests.md) |
| [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1) | Implementation | `descriptor_pool` | [`vktApiDescriptorPoolTests.md`](../testfiles/api/vktApiDescriptorPoolTests.md) |
| [`vktApiNullHandleTests.cpp`](../../../modules/vulkan/api/vktApiNullHandleTests.cpp#L1) | Implementation | `null_handle` | [`vktApiNullHandleTests.md`](../testfiles/api/vktApiNullHandleTests.md) |
| [`vktApiGranularityTests.cpp`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1) | Implementation | `granularity` | [`vktApiGranularityTests.md`](../testfiles/api/vktApiGranularityTests.md) |
| [`vktApiGetMemoryCommitment.cpp`](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1) | Implementation | `get_memory_commitment` | [`vktApiGetMemoryCommitment.md`](../testfiles/api/vktApiGetMemoryCommitment.md) |
| [`vktApiExternalMemoryTests.cpp`](../../../modules/vulkan/api/vktApiExternalMemoryTests.cpp#L1) | Implementation | `external` | [`vktApiExternalMemoryTests.md`](../testfiles/api/vktApiExternalMemoryTests.md) |
| [`vktApiMaintenance3Check.cpp`](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L1) | Implementation | `maintenance3_check` | [`vktApiMaintenance3Check.md`](../testfiles/api/vktApiMaintenance3Check.md) |
| [`vktApiDescriptorSetTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1) | Implementation | `descriptor_set` | [`vktApiDescriptorSetTests.md`](../testfiles/api/vktApiDescriptorSetTests.md) |
| [`vktApiPipelineTests.cpp`](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1) | Implementation | `pipeline` | [`vktApiPipelineTests.md`](../testfiles/api/vktApiPipelineTests.md) |
| [`vktApiMemoryRequirementInvarianceTests.cpp`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1) | Implementation | `invariance` | [`vktApiMemoryRequirementInvarianceTests.md`](../testfiles/api/vktApiMemoryRequirementInvarianceTests.md) |
| [`vktApiToolingInfoTests.cpp`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1) | Implementation | `tooling_info` | [`vktApiToolingInfoTests.md`](../testfiles/api/vktApiToolingInfoTests.md) |
| [`vktApiFormatPropertiesExtendedKHRtests.cpp`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1) | Implementation | `format_feature_flags2` | [`vktApiFormatPropertiesExtendedKHRtests.md`](../testfiles/api/vktApiFormatPropertiesExtendedKHRtests.md) |
| [`vktApiBufferMemoryRequirementsTests.cpp`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1) | Implementation | `buffer_memory_requirements` | [`vktApiBufferMemoryRequirementsTests.md`](../testfiles/api/vktApiBufferMemoryRequirementsTests.md) |
| [`vktApiImageCompressionControlTests.cpp`](../../../modules/vulkan/api/vktApiImageCompressionControlTests.cpp#L1) | Implementation | `image_compression_control` | [`vktApiImageCompressionControlTests.md`](../testfiles/api/vktApiImageCompressionControlTests.md) |
| [`vktApiGetDeviceProcAddrTests.cpp`](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L1) | Implementation | `get_device_proc_addr` | [`vktApiGetDeviceProcAddrTests.md`](../testfiles/api/vktApiGetDeviceProcAddrTests.md) |
| [`vktApiMaintenance6Check.cpp`](../../../modules/vulkan/api/vktApiMaintenance6Check.cpp#L1) | Implementation | `maintenance6_check` | [`vktApiMaintenance6Check.md`](../testfiles/api/vktApiMaintenance6Check.md) |
| [`vktApiFrameBoundaryTests.cpp`](../../../modules/vulkan/api/vktApiFrameBoundaryTests.cpp#L1) | Implementation | `frame_boundary` | [`vktApiFrameBoundaryTests.md`](../testfiles/api/vktApiFrameBoundaryTests.md) |
| [`vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp`](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1) | Implementation | `maintenance5` | [`vktApiPhysicalDeviceFormatPropertiesMaint5Tests.md`](../testfiles/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.md) |
| [`vktApiFragmentShaderOutputTests.cpp`](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1) | Implementation | `fragment_shader_output` | [`vktApiFragmentShaderOutputTests.md`](../testfiles/api/vktApiFragmentShaderOutputTests.md) |
| [`vktApiMaintenance7Tests.cpp`](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1) | Implementation | `maintenance7` | [`vktApiMaintenance7Tests.md`](../testfiles/api/vktApiMaintenance7Tests.md) |
| [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) | Implementation | `device_address` | [`vktApiDeviceAddressCommandsTests.md`](../testfiles/api/vktApiDeviceAddressCommandsTests.md) |
| [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1) | Implementation | `extension_duplicates` | [`vktApiExtensionDuplicatesTests.md`](../testfiles/api/vktApiExtensionDuplicatesTests.md) |
| [`vktApiPerformanceCountersByRegionTests.cpp`](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1) | Implementation | `performance_counters_by_region` | [`vktApiPerformanceCountersByRegionTests.md`](../testfiles/api/vktApiPerformanceCountersByRegionTests.md) |

### Nested subgroup files under copy_and_blit

| File | Subgroups | Level-3 doc |
|---|---|---|
| [`vktApiCopyImageToImageTests.cpp`](../../../modules/vulkan/api/vktApiCopyImageToImageTests.cpp#L1) | `core.image_to_image`, etc. | [`vktApiCopyImageToImageTests.md`](../testfiles/api/vktApiCopyImageToImageTests.md) |
| [`vktApiCopyBufferToBufferTests.cpp`](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.cpp#L1) | `core.buffer_to_buffer`, etc. | [`vktApiCopyBufferToBufferTests.md`](../testfiles/api/vktApiCopyBufferToBufferTests.md) |
| [`vktApiCopyImageToBufferTests.cpp`](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.cpp#L1) | `core.image_to_buffer`, etc. | [`vktApiCopyImageToBufferTests.md`](../testfiles/api/vktApiCopyImageToBufferTests.md) |
| [`vktApiCopyBufferToImageTests.cpp`](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.cpp#L1) | `core.buffer_to_image`, etc. | [`vktApiCopyBufferToImageTests.md`](../testfiles/api/vktApiCopyBufferToImageTests.md) |
| [`vktApiCopyBufferToDepthStencilTests.cpp`](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L1) | `core.buffer_to_depthstencil`, etc. | [`vktApiCopyBufferToDepthStencilTests.md`](../testfiles/api/vktApiCopyBufferToDepthStencilTests.md) |
| [`vktApiCopyDepthStencilToBufferTests.cpp`](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.cpp#L1) | `core.depthstencil_to_buffer`, etc. | [`vktApiCopyDepthStencilToBufferTests.md`](../testfiles/api/vktApiCopyDepthStencilToBufferTests.md) |
| [`vktApiCopyDepthStencilMSAATests.cpp`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1) | `core.depth_stencil_msaa_copy`, etc. | [`vktApiCopyDepthStencilMSAATests.md`](../testfiles/api/vktApiCopyDepthStencilMSAATests.md) |
| [`vktApiBlittingTests.cpp`](../../../modules/vulkan/api/vktApiBlittingTests.cpp#L1) | `core.blit_image`, etc. | [`vktApiBlittingTests.md`](../testfiles/api/vktApiBlittingTests.md) |
| [`vktApiResolveTests.cpp`](../../../modules/vulkan/api/vktApiResolveTests.cpp#L1) | `core.resolve_image`, etc. | [`vktApiResolveTests.md`](../testfiles/api/vktApiResolveTests.md) |
| [`vktApiCopyMemoryIndirectTests.cpp`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1) | `copy_memory_indirect` | [`vktApiCopyMemoryIndirectTests.md`](../testfiles/api/vktApiCopyMemoryIndirectTests.md) |
| [`vktApiCopyMultiplaneImageTransferQueueTests.cpp`](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L1) | `multiplane_transfer_queue` | [`vktApiCopyMultiplaneImageTransferQueueTests.md`](../testfiles/api/vktApiCopyMultiplaneImageTransferQueueTests.md) |
| [`vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1) | `dynamic_state_meta_ops` | [`vktApiCopiesAndBlittingDynamicStateMetaOpsTests.md`](../testfiles/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.md) |
| [`vktApiCopiesAndBlittingReinterpretTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1) | `reinterpret` | [`vktApiCopiesAndBlittingReinterpretTests.md`](../testfiles/api/vktApiCopiesAndBlittingReinterpretTests.md) |
| [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1) | `core.use_after_copy` | [`vktApiUseAfterCopyTests.md`](../testfiles/api/vktApiUseAfterCopyTests.md) |

## Cross-file Recurring Themes

### Allocation strategy as a primary parameter dimension

Many API test files distinguish suballocated vs dedicated allocation paths. This is visible in:
- `buffer` (suballocated vs dedicated)
- `copy_and_blit` (core vs dedicated_allocation branches)
- `image_clearing` (core vs dedicated_allocation branches)
- `fill_and_update_buffer` (suballocation vs dedicated allocation)

### Queue family coverage

Universal, compute-only, and transfer-only queue paths recur across:
- `copy_and_blit` (transfer_queue and compute_queue subgroups)
- `ds_color_copy` (queue type parameterization)
- `fill_and_update_buffer` (transfer-only queue variants)

### Extension-gated feature coverage

Many subgroups are conditional on extensions:
- `buffer_marker` requires `VK_AMD_buffer_marker`
- `format_feature_flags2` requires `VK_KHR_format_feature_flags2`
- `frame_boundary` requires `VK_EXT_frame_boundary`
- `device_address` requires `VK_KHR_device_address_commands`
- `copy_memory_indirect` requires `VK_KHR_copy_memory_indirect`
- `image_compression_control` requires `VK_EXT_image_compression_control`

### VKSC divergence

16 of 38 top-level groups are excluded from Vulkan SC builds, guarded by `#ifndef CTS_USES_VULKANSC` in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L93).

## Cross-file Recurring Verification Methods

- **Structural success/failure**: object creation, allocation, binding, destruction checks (e.g., `object_management`, `buffer`, `null_handle`)
- **CPU reference image comparison**: thresholded framebuffer comparison via `tcu::floatThresholdCompare()` or `tcu::fuzzyCompare()` (e.g., `copy_and_blit` subgroups, `image_clearing`)
- **Property/value validation**: checking reported properties against expected values (e.g., `driver_properties`, `maintenance3_check`, `maintenance7`)
- **Negative API-contract validation**: expected error codes, callback accounting, null-handle behavior (e.g., `object_management`, `null_handle`)
- **Indirect semantic validation**: verifying correctness through later consumption rather than immediate readback (e.g., `use_after_copy`)

## Notes / Uncertainties

- Many group names differ significantly from their factory symbol names. For example, `createMemoryRequirementInvarianceTests()` produces the group `invariance`, not `memory_requirement_invariance`. All group names in this document are verified against mustpass [`api.txt`](../../../external/vulkancts/mustpass/main/vk-default/api.txt).
- The `buffer_view` group is a composite created locally in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L78) rather than through an external factory function.
- The `copy_and_blit` subtree is by far the largest single group, with 14+ nested implementation files and multiple allocation/queue/command-variant branches.
