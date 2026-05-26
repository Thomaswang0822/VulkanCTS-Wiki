# [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)

## Overview

Dispatcher file for Vulkan copy and blit command tests. Does not contain test logic itself; instead it aggregates sub-files that implement image-to-image, buffer-to-buffer, image-to-buffer, buffer-to-image, depth/stencil copy, blitting, resolve, indirect copy, and reinterpretation tests under a single `copy_and_blit` group. The aggregate provides broad historical context for API test-plan copy/update themes across whole and partial ranges, small-to-large transfers, same-memory/object cases, compatible-format copies, and blits with or without scaling ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L683-L711)).

## Role of File

Registration/dispatcher. The [createCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L267) function creates the top-level group and delegates to sub-files via their respective `add*Tests` or `create*Tests` functions.

## Source Code

- Implementation: [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)
- Header: [vktApiCopiesAndBlittingTests.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L108)

## Registration Hierarchy

```text
api.copy_and_blit
├── core
├── dedicated_allocation
├── copy_commands2
├── sparse
├── multiplanar_xfer
├── dynamic_state (non-VulkanSC only)
├── copy_memory_indirect (non-VulkanSC only)
├── device_address (non-VulkanSC only)
└── reinterpret
```

## Test Families

### core — Suballocated copy and blit tests

[addCoreCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232) creates the `core` group with suballocated allocation kind and no extension flags. It delegates to [addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119) for the main copy/blit subgroups, then adds indirect copy tests via [addIndirectCopyTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74), buffer offset tests via `addCopyBufferToBufferOffsetTests()`, and use-after-copy tests via `createUseAfterXferGroup()`.

The subgroups created by `addCopiesAndBlittingTests()` under `core` include: image_to_image, image_to_buffer, buffer_to_image, buffer_to_depthstencil, depthstencil_to_buffer, buffer_to_buffer, blit_image, resolve_image, depth_stencil_msaa_copy, plus compute-queue and transfer-queue variants (buffer_to_depthstencil_compute_queue, depthstencil_to_buffer_compute_queue, buffer_to_depthstencil_transfer_queue, depthstencil_to_buffer_transfer_queue, image_to_buffer_transfer_queue, buffer_to_image_transfer_queue, buffer_to_buffer_transfer_queue, image_to_buffer_compute_queue, buffer_to_image_compute_queue). Because `core` uses suballocated allocation with no extensions, it also includes general-layout subgroups: image_to_image_general_layout, image_to_buffer_general_layout, buffer_to_image_general_layout. The indirect copy subgroups added are: memory_to_image_indirect, memory_to_depthstencil_indirect, image_to_buffer_indirect, and their transfer-queue and compute-queue variants. Additional subgroups: buffer_offset_tests, use_after_xfer.

### dedicated_allocation — Dedicated-allocation copy and blit tests

[addDedicatedAllocationCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L241) creates the `dedicated_allocation` group with dedicated allocation kind and no extension flags. It delegates to [addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119) for the main copy/blit subgroups, then adds indirect copy tests via [addIndirectCopyTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74).

The subgroups mirror those of `core` (image_to_image, image_to_buffer, buffer_to_image, buffer_to_depthstencil, depthstencil_to_buffer, buffer_to_buffer, blit_image, resolve_image, depth_stencil_msaa_copy, plus compute-queue and transfer-queue variants, plus indirect copy subgroups), but without the general-layout subgroups, buffer_offset_tests, and use_after_xfer that are exclusive to `core`.

### copy_commands2 — VK_KHR_copy_commands2 tests

The `copy_commands2` group uses [addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119) with dedicated allocation and the COPY_COMMANDS_2 extension flag. It includes the same subgroups as `dedicated_allocation` (image_to_image, image_to_buffer, buffer_to_image, buffer_to_depthstencil, depthstencil_to_buffer, buffer_to_buffer, blit_image, resolve_image, depth_stencil_msaa_copy, plus compute-queue and transfer-queue variants), and additionally adds image_to_image_transfer_queue, image_to_image_transfer_queue_secondary, and image_to_image_transfer_sparse subgroups that are specific to the COPY_COMMANDS_2 path.

### sparse — Sparse-binding copy tests

[addSparseCopyTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L57) creates the `sparse` group with dedicated allocation, COPY_COMMANDS_2 and SPARSE_BINDING flags. It contains a single image_to_image subgroup for sparse image-to-image copy tests.

### multiplanar_xfer — Multiplane image transfer-queue tests

Created by [createCopyMultiplaneImageTransferQueueTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L283), this group tests multiplane image copy operations on transfer queues. Its internal structure is defined in [vktApiCopyMultiplaneImageTransferQueueTests.cpp](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.cpp#L1) and covers multiple YCbCr and non-YCbCr multiplane formats with optimal and linear tiling, disjoint and non-disjoint images, and buffer-intermediated copies.

### dynamic_state — Dynamic-state meta-operations (non-VulkanSC only)

Created by [createDynamicStateMetaOperationsTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L286), this group tests copy operations combined with dynamic state meta-operations. Requires VK_KHR_maintenance5. Implementation is in [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1).

### copy_memory_indirect — Indirect copy commands (non-VulkanSC only)

Created by [createCopyMemoryIndirectTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L287), this group tests indirect copy memory commands. Implementation is in [vktApiCopyMemoryIndirectTests.cpp](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L1). Note: this is a separate top-level child of `copy_and_blit`, distinct from the indirect copy subgroups nested inside `core` and `dedicated_allocation` (which are added by [addIndirectCopyTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74)).

### device_address — Device-address copy commands (non-VulkanSC only)

[addDeviceAddressTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249) creates the `device_address` group using DEVICE_ADDRESS_COMMANDS. It contains subgroups: image_to_buffer, buffer_to_image, buffer_to_depthstencil, and buffer_to_buffer.

### reinterpret — Copy reinterpretation tests

Created by [createReinterpretationTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L290), this group tests copy reinterpretation between compatible formats. Implementation is in [vktApiCopiesAndBlittingReinterpretTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1).

### Delegated Sub-Files

The following sub-files provide the actual test implementations:

- [vktApiCopyImageToImageTests.hpp](../../../modules/vulkan/api/vktApiCopyImageToImageTests.hpp#L1)
- [vktApiCopyBufferToBufferTests.hpp](../../../modules/vulkan/api/vktApiCopyBufferToBufferTests.hpp#L1)
- [vktApiCopyImageToBufferTests.hpp](../../../modules/vulkan/api/vktApiCopyImageToBufferTests.hpp#L1)
- [vktApiCopyBufferToImageTests.hpp](../../../modules/vulkan/api/vktApiCopyBufferToImageTests.hpp#L1)
- [vktApiCopyBufferToDepthStencilTests.hpp](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.hpp#L1)
- [vktApiCopyDepthStencilToBufferTests.hpp](../../../modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.hpp#L1)
- [vktApiCopyDepthStencilMSAATests.hpp](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.hpp#L1)
- [vktApiBlittingTests.hpp](../../../modules/vulkan/api/vktApiBlittingTests.hpp#L1)
- [vktApiResolveTests.hpp](../../../modules/vulkan/api/vktApiResolveTests.hpp#L1)
- [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp#L1)
- [vktApiCopiesAndBlittingReinterpretTests.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.hpp#L1)
- [vktApiCopyMultiplaneImageTransferQueueTests.hpp](../../../modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.hpp#L1)
- [vktApiCopyMemoryIndirectTests.hpp](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.hpp#L1)
- [vktApiUseAfterCopyTests.hpp](../../../modules/vulkan/api/vktApiUseAfterCopyTests.hpp#L1)

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| AllocationKind | ALLOCATION_KIND_SUBALLOCATED, ALLOCATION_KIND_DEDICATED |
| Extension flags | 0, COPY_COMMANDS_2, SPARSE_BINDING, INDIRECT_COPY, DEVICE_ADDRESS_COMMANDS, MAINTENANCE_10 |
| QueueSelectionOptions | Universal, TransferOnly, ComputeOnly |
| Use secondary command buffer | true, false |
| Use sparse binding | true, false |
| General layout mode | true, false |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_copy_commands2 | copy_commands2 group |
| VK_KHR_maintenance10 | buffer_to_depthstencil_compute_queue, depthstencil_to_buffer_compute_queue, and transfer_queue variants |
| Sparse binding | sparse group |
| VK_KHR_maintenance5 | dynamic_state group (delegated) |
| Indirect copy extension | copy_memory_indirect group (non-SC) |
| Device address commands | device_address group (non-SC) |

## Verification Methods

Verification is delegated to the sub-files. Common patterns include:
- **Pixel comparison**: Copy results are read back and compared against source data
- **Buffer content comparison**: Buffer-to-buffer copies are verified by mapping and comparing memory
- **Format-specific thresholds**: Depth/stencil formats may use tolerance-based comparison

## Test Principles Observed

- Aggregation: this file serves as a single entry point for all copy/blit tests
- Parameterization: TestGroupParams struct carries allocation kind, extension flags, and queue selection through the hierarchy
- Queue coverage: tests are repeated across universal, compute-only, and transfer-only queues where applicable
- SC divergence: dynamic_state, copy_memory_indirect, and device_address groups are excluded for Vulkan SC

## Notes / Uncertainties

- The `core` group additionally includes indirect copy tests and use-after-copy tests that are not in `dedicated_allocation`
- The `copy_commands2` group uses dedicated allocation internally (hardcoded at [line 276](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L276))
- The `multiplanar_xfer` subgroup is created by [createCopyMultiplaneImageTransferQueueTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L283) and its internal structure is defined in a separate file
- The `dynamic_state`, `copy_memory_indirect`, and `device_address` groups are non-SC only
