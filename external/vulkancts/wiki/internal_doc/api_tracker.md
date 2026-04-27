# api temporary tracker

## Scope

- Internal temporary coordination tracker for the Level-2 [`api`](../categories/api.md) page.
- Primary index is header/source filename, not inferred subgroup name.
- `Verified group name` is filled only when confirmed from mustpass TXT.
- Status values use `[x]`, `[-]`, `[ ]`.

## Tracker

| File | Kind | Factory symbol | Verified group name | VKSC | Status |
|---|---|---|---|---|---|
| `vktApiVersionCheck.hpp` | Header | `createVersionSanityCheckTests()` | `version_check` | No | [ ] |
| `vktApiDebugUtilsTests.hpp` | Header | `createDebugUtilsTests()` | `debug_utils` | No | [ ] |
| `vktApiDriverPropertiesTests.hpp` | Header | `createDriverPropertiesTests()` | `driver_properties` | No | [ ] |
| `vktApiSmokeTests.hpp` | Header | `createSmokeTests()` | `smoke` | Yes | [ ] |
| `vktApiFeatureInfo.hpp` | Header | `createFeatureInfoTests()` | `info` | No | [ ] |
| `vktApiDeviceDrmPropertiesTests.hpp` | Header | `createDeviceDrmPropertiesTests()` | `device_drm_properties` | Yes | [ ] |
| `vktApiDeviceInitializationTests.hpp` | Header | `createDeviceInitializationTests()` | `device_init` | No | [ ] |
| `vktApiObjectManagementTests.hpp` | Header | `createObjectManagementTests()` | `object_management` | No | [ ] |
| `vktApiBufferTests.hpp` | Header | `createBufferTests()` | `buffer` | No | [ ] |
| `vktApiBufferMarkerTests.hpp` | Header | `createBufferMarkerTests()` | `buffer_marker` | Yes | [ ] |
| `vktApiTests.cpp#L78` | Source | `createBufferViewTests()` | `buffer_view` | No | [ ] |
| `vktApiCommandBuffersTests.hpp` | Header | `createCommandBuffersTests()` | `command_buffers` | No | [ ] |
| `vktApiCopiesAndBlittingTests.hpp` | Header | `createCopiesAndBlittingTests()` | `copy_and_blit` | No | [ ] |
| `vktApiDSColorBitCopyTests.hpp` | Header | `createDSColorBitCopyTests()` | `ds_color_copy` | No | [ ] |
| `vktApiImageClearingTests.hpp` | Header | `createImageClearingTests()` | `image_clearing` | No | [ ] |
| `vktApiFillBufferTests.hpp` | Header | `createFillAndUpdateBufferTests()` | `fill_and_update_buffer` | No | [ ] |
| `vktApiDescriptorPoolTests.hpp` | Header | `createDescriptorPoolTests()` | `descriptor_pool` | No | [ ] |
| `vktApiNullHandleTests.hpp` | Header | `createNullHandleTests()` | `null_handle` | No | [ ] |
| `vktApiGranularityTests.hpp` | Header | `createGranularityQueryTests()` | `granularity` | No | [ ] |
| `vktApiGetMemoryCommitment.hpp` | Header | `createMemoryCommitmentTests()` | `get_memory_commitment` | No | [ ] |
| `vktApiExternalMemoryTests.hpp` | Header | `createExternalMemoryTests()` | `external` | Yes | [ ] |
| `vktApiMaintenance3Check.hpp` | Header | `createMaintenance3Tests()` | `maintenance3_check` | No | [ ] |
| `vktApiDescriptorSetTests.hpp` | Header | `createDescriptorSetTests()` | `descriptor_set` | No | [ ] |
| `vktApiPipelineTests.hpp` | Header | `createPipelineTests()` | `pipeline` | No | [ ] |
| `vktApiMemoryRequirementInvarianceTests.hpp` | Header | `createMemoryRequirementInvarianceTests()` | `invariance` | No | [ ] |
| `vktApiToolingInfoTests.hpp` | Header | `createToolingInfoTests()` | `tooling_info` | Yes | [ ] |
| `vktApiFormatPropertiesExtendedKHRtests.hpp` | Header | `createFormatPropertiesExtendedKHRTests()` | `format_feature_flags2` | Yes | [ ] |
| `vktApiBufferMemoryRequirementsTests.hpp` | Header | `createBufferMemoryRequirementsTests()` | `buffer_memory_requirements` | No | [ ] |
| `vktApiImageCompressionControlTests.hpp` | Header | `createImageCompressionControlTests()` | `image_compression_control` | Yes | [ ] |
| `vktApiGetDeviceProcAddrTests.hpp` | Header | `createGetDeviceProcAddrTests()` | `get_device_proc_addr` | Yes | [ ] |
| `vktApiMaintenance6Check.hpp` | Header | `createMaintenance6Tests()` | `maintenance6_check` | Yes | [ ] |
| `vktApiFrameBoundaryTests.hpp` | Header | `createFrameBoundaryTests()` | `frame_boundary` | Yes | [ ] |
| `vktApiPhysicalDeviceFormatPropertiesMaint5Tests.hpp` | Header | `createMaintenance5Tests()` | `maintenance5` | Yes | [ ] |
| `vktApiFragmentShaderOutputTests.hpp` | Header | `createFragmentShaderOutputTests()` | `fragment_shader_output` | Yes | [ ] |
| `vktApiMaintenance7Tests.hpp` | Header | `createMaintenance7Tests()` | `maintenance7` | No | [ ] |
| `vktApiDeviceAddressCommandsTests.hpp` | Header | `createDeviceAddressCommandsTests()` | `device_address` | Yes | [ ] |
| `vktApiExtensionDuplicatesTests.hpp` | Header | `createExtensionDuplicatesTests()` | `extension_duplicates` | No | [ ] |
| `vktApiPerformanceCountersByRegionTests.hpp` | Header | `createRenderPassPerformanceCountersByRegionApiTests()` | `performance_counters_by_region` | Yes | [ ] |

## Nested subgroup files under copy_and_blit

These files register subgroups within `copy_and_blit` and need Level-3 docs:

| File | Verified subgroup names (from mustpass) | Status |
|---|---|---|
| `vktApiCopyImageToImageTests.cpp` | `core.image_to_image`, `dedicated_allocation.image_to_image`, `copy_commands2.image_to_image`, etc. | [ ] |
| `vktApiCopyBufferToBufferTests.cpp` | `core.buffer_to_buffer`, `dedicated_allocation.buffer_to_buffer`, `copy_commands2.buffer_to_buffer`, etc. | [ ] |
| `vktApiCopyImageToBufferTests.cpp` | `core.image_to_buffer`, `dedicated_allocation.image_to_buffer`, etc. | [ ] |
| `vktApiCopyBufferToImageTests.cpp` | `core.buffer_to_image`, `dedicated_allocation.buffer_to_image`, etc. | [ ] |
| `vktApiCopyBufferToDepthStencilTests.cpp` | `core.buffer_to_depthstencil`, `dedicated_allocation.buffer_to_depthstencil`, etc. | [ ] |
| `vktApiCopyDepthStencilToBufferTests.cpp` | `core.depthstencil_to_buffer`, `dedicated_allocation.depthstencil_to_buffer`, etc. | [ ] |
| `vktApiCopyDepthStencilMSAATests.cpp` | `core.depth_stencil_msaa_copy`, `dedicated_allocation.depth_stencil_msaa_copy` | [ ] |
| `vktApiBlittingTests.cpp` | `core.blit_image`, `dedicated_allocation.blit_image`, `copy_commands2.blit_image`, etc. | [ ] |
| `vktApiResolveTests.cpp` | `core.resolve_image`, `dedicated_allocation.resolve_image`, `copy_commands2.resolve_image`, etc. | [ ] |
| `vktApiCopyMemoryIndirectTests.cpp` | `copy_memory_indirect` | [ ] |
| `vktApiCopyMultiplaneImageTransferQueueTests.cpp` | `multiplane_transfer_queue` | [ ] |
| `vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp` | `dynamic_state_meta_ops` | [ ] |
| `vktApiCopiesAndBlittingReinterpretTests.cpp` | `reinterpret` | [ ] |
| `vktApiUseAfterCopyTests.cpp` | `core.use_after_copy` | [ ] |

## Utility files (NO Level-3 docs needed)

These files do not register tests and should NOT have Level-3 wiki pages:

| File | Reason |
|---|---|
| `vktApiBufferAndImageAllocationUtil.cpp` | Utility: allocation strategy classes |
| `vktApiBufferComputeInstance.cpp` | Utility: compute instance helpers |
| `vktApiComputeInstanceResultBuffer.cpp` | Utility: result buffer helpers |
| `vktApiCopiesAndBlittingUtil.cpp` | Utility: shared test infrastructure |

## Summary

- Total top-level groups: 38
- Nested subgroup files under copy_and_blit: 14
- Utility files (no wiki needed): 4
- Total Level-3 docs needed: 53 (38 top-level + 14 nested + 1 root registration)
- Existing Level-3 docs to delete: 4 (utility files)
