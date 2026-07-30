## Overview

The `api` test category collects tests that check foundational Vulkan API contracts: device initialization and property reporting, object and resource lifetime, buffer/image copy and clear commands, descriptor management, command buffer lifecycle, pipeline creation, and extension-gated feature queries.

## Background Knowledge

No common prerequisite concepts need category-level explanation for this test category.

## Category Structure

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
├── maintenance7                           (not in Vulkan SC)
├── device_address                         (not in Vulkan SC)
├── extension_duplicates
└── performance_counters_by_region         (not in Vulkan SC)
```

The category has 38 direct children registered by [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L86), verified against mustpass [`api.txt`](../../mustpass/main/vk-default/api.txt). Two registration-only dispatcher files are folded into this Level-2 page rather than getting their own Level-3 pages:

- [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L1) assembles the 38 top-level groups into the `api` tree and contains no test logic.
- [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1) dispatches the `copy_and_blit` family to 14 delegated implementation files via `addCopiesAndBlittingTests()` and friends.

The `buffer_view` group is a composite created locally in `vktApiTests.cpp` from two implementation files (`vktApiBufferViewCreateTests.cpp` for `create`, `vktApiBufferViewAccessTests.cpp` for `access`) rather than through a single external factory. The 52 rewritten Level-3 pages exceed the 38 direct children because `copy_and_blit` produces 14 Level-3 pages from its delegated files and `buffer_view` produces 2 (`create` and `access`). Fifteen of the 38 groups are excluded from Vulkan SC builds via `#ifndef CTS_USES_VULKANSC` in `vktApiTests.cpp`.

## How the Families Fit Together

- Most families validate a single API contract: property reporting, object lifetime, buffer or view creation, descriptor management, or command buffer behavior. Each family probes one API surface area with its own parameter matrix and pass or fail condition.
- The `copy_and_blit` family is the largest subtree. Its registration-only dispatcher delegates to 14 implementation files covering buffer-to-buffer, image-to-image, image-to-buffer, depth or stencil, blit, resolve, multiplane, reinterpret, and use-after-copy paths. Each delegated file registers under shared variant intermediate nodes (`core`, `dedicated_allocation`, `copy_commands2`, `device_address`, and per-queue siblings) that change allocation strategy, command extension, or queue family without altering the copy semantics under test.
- `image_clearing` and `fill_and_update_buffer` exercise clear and fill commands with their own allocation and queue variants, separate from the `copy_and_blit` dispatcher but using the same verification pattern of host-computed reference comparison.
- Extension-gated families (`buffer_marker`, `frame_boundary`, `device_address`, `image_compression_control`, `format_feature_flags2`, `fragment_shader_output`, `performance_counters_by_region`, `copy_memory_indirect`) are excluded from Vulkan SC builds and require their respective extensions before their cases execute.

## Level-3 Pages Navigation

### Property, version, and maintenance checks

| Registered test family | Level-3 page | What to read there |
|---|---|---|
| `version_check` | [VersionCheck.md](../testfiles/api/VersionCheck.md) | API version reporting against the CTS build maximum, and `vkGetInstanceProcAddr` / `vkGetDeviceProcAddr` resolution for core, extension, and unavailable functions. |
| `driver_properties` | [DriverProperties.md](../testfiles/api/DriverProperties.md) | Physical device property reporting against spec minimums and limits. |
| `info` | [FeatureInfo.md](../testfiles/api/FeatureInfo.md) | Feature and property query reporting for the device and platform. |
| `device_drm_properties` | [DeviceDrmProperties.md](../testfiles/api/DeviceDrmProperties.md) | DRM property reporting checks. |
| `device_init` | [DeviceInitialization.md](../testfiles/api/DeviceInitialization.md) | Device creation configuration matrix across queues, extensions, and feature requests. |
| `tooling_info` | [ToolingInfo.md](../testfiles/api/ToolingInfo.md) | `VK_EXT_tooling_info` physical device tooling property query. |
| `extension_duplicates` | [ExtensionDuplicates.md](../testfiles/api/ExtensionDuplicates.md) | Extension deduplication contract when duplicate names are present in the enabled list. |
| `get_device_proc_addr` | [GetDeviceProcAddr.md](../testfiles/api/GetDeviceProcAddr.md) | `vkGetDeviceProcAddr` resolution contract for core and extension device functions. |
| `maintenance3_check` | [Maintenance3Check.md](../testfiles/api/Maintenance3Check.md) | Maintenance3 property minimums and descriptor set layout support query. |
| `maintenance6_check` | [Maintenance6Check.md](../testfiles/api/Maintenance6Check.md) | Maintenance6 property checks. |
| `maintenance7` | [Maintenance7.md](../testfiles/api/Maintenance7.md) | Maintenance7 property checks. |
| `format_feature_flags2` | [FormatPropertiesExtendedKHR.md](../testfiles/api/FormatPropertiesExtendedKHR.md) | Extended `VkFormatProperties3` feature flags2 reporting. |
| `maintenance5` | [PhysicalDeviceFormatPropertiesMaint5.md](../testfiles/api/PhysicalDeviceFormatPropertiesMaint5.md) | Maintenance5 format properties and `VK_REMAINING_ARRAY_LAYERS` query path. |
| `get_memory_commitment` | [GetMemoryCommitment.md](../testfiles/api/GetMemoryCommitment.md) | `vkGetDeviceMemoryCommitment` query for sparse memory. |
| `granularity` | [Granularity.md](../testfiles/api/Granularity.md) | `VkQueueFamilyProperties::minImageTransferGranularity` submission granularity query. |
| `image_compression_control` | [ImageCompressionControl.md](../testfiles/api/ImageCompressionControl.md) | `VK_EXT_image_compression_control` fixed-rate compression property reporting. |

### Object, buffer, and descriptor management

| Registered test family | Level-3 page | What to read there |
|---|---|---|
| `object_management` | [ObjectManagement.md](../testfiles/api/ObjectManagement.md) | `vkCreate*` / `vkDestroy*` lifecycle across 11 intermediate nodes including multithreaded contention, allocation callback validation, deterministic allocation failure, and `VK_EXT_private_data` storage. |
| `buffer` | [Buffer.md](../testfiles/api/Buffer.md) | Buffer creation, usage flags, size, sparse binding, and `VkMemoryRequirements` consistency across suballocated and dedicated allocations. |
| `buffer_marker` | [BufferMarker.md](../testfiles/api/BufferMarker.md) | `vkCmdWriteBufferMarkerAMD` ordering at chosen pipeline stages, with `memory_dep` slot ownership transfer and external host memory variants. |
| `buffer_view.create` | [BufferViewCreate.md](../testfiles/api/BufferViewCreate.md) | `VkBufferView` creation matrix across formats, buffer sizes, and usage flags. |
| `buffer_view.access` | [BufferViewAccess.md](../testfiles/api/BufferViewAccess.md) | `VkBufferView` access pattern validation through shader reads. |
| `buffer_memory_requirements` | [BufferMemoryRequirements.md](../testfiles/api/BufferMemoryRequirements.md) | `vkGetBufferMemoryRequirements` and `vkGetBufferMemoryRequirements2` query consistency. |
| `invariance` | [MemoryRequirementInvariance.md](../testfiles/api/MemoryRequirementInvariance.md) | Invariance of memory requirements across repeated queries and query APIs. |
| `fill_and_update_buffer` | [FillBuffer.md](../testfiles/api/FillBuffer.md) | `vkCmdFillBuffer`, `vkCmdUpdateBuffer`, and `VK_KHR_device_address_commands` counterparts across whole, partial, and `VK_WHOLE_SIZE` ranges. |
| `null_handle` | [NullHandle.md](../testfiles/api/NullHandle.md) | Null-handle API contract for object creation, destruction, and query paths. |
| `descriptor_pool` | [DescriptorPool.md](../testfiles/api/DescriptorPool.md) | Descriptor pool allocation and free contract, including fragmentation and reset behavior. |
| `descriptor_set` | [DescriptorSet.md](../testfiles/api/DescriptorSet.md) | `VkDescriptorSetLayout` lifetime, legally empty layouts, and `vkUpdateDescriptorSets` writes spanning multiple bindings. |
| `pipeline` | [Pipeline.md](../testfiles/api/Pipeline.md) | `VkPipeline` creation, cache, and derivative contract at the API level. |
| `external` | [ExternalMemory.md](../testfiles/api/ExternalMemory.md) | External memory handle import and export contract across handle types. |

### Command buffer and execution

| Registered test family | Level-3 page | What to read there |
|---|---|---|
| `command_buffers` | [CommandBuffers.md](../testfiles/api/CommandBuffers.md) | Command buffer lifecycle, recording, submission, secondary buffers, state transitions, and pool reset or trim behavior. |
| `frame_boundary` | [FrameBoundary.md](../testfiles/api/FrameBoundary.md) | `VK_EXT_frame_boundary` frame boundary signaling and image ownership transfer contract. |

### Copy and blit operations

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `copy_and_blit.core.buffer_to_buffer` and variants | [CopyBufferToBuffer.md](../testfiles/api/CopyBufferToBuffer.md) | Bit-exact `vkCmdCopyBuffer`, `vkCmdCopyBuffer2`, and `vkCmdCopyMemoryKHR` byte comparison across offsets, regions, and allocation strategies. |
| `copy_and_blit.core.image_to_buffer` and variants | [CopyImageToBuffer.md](../testfiles/api/CopyImageToBuffer.md) | `VkBufferImageCopy` region layout for image-to-buffer copies across image types, formats, tiling, and compressed block handling. |
| `copy_and_blit.core.buffer_to_image` and variants | [CopyBufferToImage.md](../testfiles/api/CopyBufferToImage.md) | `VkBufferImageCopy` region layout for buffer-to-image copies across formats, tiling, `VK_REMAINING_ARRAY_LAYERS`, and transfer queue granularity. |
| `copy_and_blit.core.depthstencil_to_buffer` and variants | [CopyDepthStencilToBuffer.md](../testfiles/api/CopyDepthStencilToBuffer.md) | Depth and stencil aspect selection and ordering for image-to-buffer copies, including `VK_KHR_maintenance10` per-queue copy feature bits. |
| `copy_and_blit.copy_memory_indirect` | [CopyMemoryIndirect.md](../testfiles/api/CopyMemoryIndirect.md) | `vkCmdCopyMemoryIndirectKHR` buffer-to-buffer indirect copy and mandatory format feature compliance for `VK_KHR_copy_memory_indirect`. |
| `copy_and_blit.dynamic_state_meta_ops` | [CopiesAndBlittingDynamicStateMetaOps.md](../testfiles/api/CopiesAndBlittingDynamicStateMetaOps.md) | Copy commands combined with dynamic state meta operations. |
| `ds_color_copy` | [DSColorBitCopy.md](../testfiles/api/DSColorBitCopy.md) | Depth or stencil color-bit copy contract between depth or stencil and color formats. |
| `copy_and_blit.core.image_to_image` and variants | [CopyImageToImage.md](../testfiles/api/CopyImageToImage.md) | Size-compatible format copying, compressed block scaling, layout transitions, depth or stencil aspect separation, and `VK_REMAINING_ARRAY_LAYERS` for `vkCmdCopyImage`. |
| `copy_and_blit.core.buffer_to_depthstencil` and variants | [CopyBufferToDepthStencil.md](../testfiles/api/CopyBufferToDepthStencil.md) | Separate aspect selection, stencil bias, and dual-source layout rules for buffer-to-depth or stencil copies. |
| `copy_and_blit.core.depth_stencil_msaa_copy` and variants | [CopyDepthStencilMSAA.md](../testfiles/api/CopyDepthStencilMSAA.md) | MSAA sample-resolve copy logic with per-sample aspect handling and `fragmentStoresAndAtomics` verification path. |
| `copy_and_blit.core.blit_image` and variants | [Blitting.md](../testfiles/api/Blitting.md) | Scaling, filtering, and format-compatibility matrix for `vkCmdBlitImage`, including mirror mode, compressed source, and mipmap generation. |
| `copy_and_blit.core.resolve_image` and variants | [Resolve.md](../testfiles/api/Resolve.md) | Multisample resolve with format and sample-count matrix for `vkCmdResolveImage`. |
| `copy_and_blit.multiplane_transfer_queue` | [CopyMultiplaneImageTransferQueue.md](../testfiles/api/CopyMultiplaneImageTransferQueue.md) | Multiplane YCbCr format plane-by-plane copy on transfer queues with `minImageTransferGranularity` alignment and LSB don't-care tolerance. |
| `copy_and_blit.reinterpret` | [CopiesAndBlittingReinterpret.md](../testfiles/api/CopiesAndBlittingReinterpret.md) | Format reinterpretation between size-compatible formats via `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` and `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT`. |
| `copy_and_blit.core.use_after_copy` | [UseAfterCopy.md](../testfiles/api/UseAfterCopy.md) | Indirect semantic validation by consuming copied data in later shader or draw work. |
| `image_clearing` | [ImageClearing.md](../testfiles/api/ImageClearing.md) | `vkCmdClearColorImage`, `vkCmdClearDepthStencilImage`, and `vkCmdClearAttachments` across formats, tilings, layers, separate depth or stencil layouts, partial clears, and multisample resolve. |

### Smoke, shader output, device address, and performance

| Registered test family | Level-3 page | What to read there |
|---|---|---|
| `smoke` | [Smoke.md](../testfiles/api/Smoke.md) | Smoke test coverage of core API paths for quick implementation sanity checks. |
| `fragment_shader_output` | [FragmentShaderOutput.md](../testfiles/api/FragmentShaderOutput.md) | Fragment shader output interface validation across formats and write modes. |
| `device_address` | [DeviceAddressCommands.md](../testfiles/api/DeviceAddressCommands.md) | `VK_KHR_device_address_commands` buffer and image device-address command contract. |
| `performance_counters_by_region` | [PerformanceCountersByRegion.md](../testfiles/api/PerformanceCountersByRegion.md) | Performance counter by region query and reporting contract. |
| `debug_utils` | [DebugUtils.md](../testfiles/api/DebugUtils.md) | `VK_EXT_debug_utils` messenger and callback contract, including message severity and type filtering. |

## Category Notes

- The `copy_and_blit` subtree uses a two-level dispatcher structure: `vktApiCopiesAndBlittingTests.cpp` routes to 14 delegated implementation files, each registering under shared variant intermediate nodes (`core`, `dedicated_allocation`, `copy_commands2`, `device_address`, and per-queue siblings). The variant intermediate nodes change allocation strategy, command extension, or queue family, not the copy semantics under test.
- Many group names differ from their factory symbol names. For example, `createMemoryRequirementInvarianceTests()` produces the group `invariance`, not `memory_requirement_invariance`. All group names in the tree above are verified against mustpass [`api.txt`](../../mustpass/main/vk-default/api.txt).
- The historical Vulkan API test plan in [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc) frames api testing around object creation and destruction, multithreaded object management, configurable device initialization, buffer corner cases, command buffer lifecycle, and copy or blit coverage. Treat it as objective-level context only; current source files and mustpass lists remain the evidence for exact registration, parameters, support gates, and verification behavior.
