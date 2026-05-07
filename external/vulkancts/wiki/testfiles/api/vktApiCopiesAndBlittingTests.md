# [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)

## Overview

Dispatcher file for Vulkan copy and blit command tests. Does not contain test logic itself; instead it aggregates sub-files that implement image-to-image, buffer-to-buffer, image-to-buffer, buffer-to-image, depth/stencil copy, blitting, resolve, indirect copy, and reinterpretation tests under a single `copy_and_blit` group.

## Role of File

Registration/dispatcher. The [createCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L267) function creates the top-level group and delegates to sub-files via their respective `add*Tests` or `create*Tests` functions.

## Source Code

- Implementation: [vktApiCopiesAndBlittingTests.cpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1)
- Header: [vktApiCopiesAndBlittingTests.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L108)

## Registration Path

```
api
  +-- copy_and_blit
```

## Test Hierarchy

```
copy_and_blit
  +-- core
  |     +-- image_to_image
  |     +-- image_to_buffer
  |     +-- buffer_to_image
  |     +-- buffer_to_depthstencil
  |     +-- depthstencil_to_buffer
  |     +-- buffer_to_buffer
  |     +-- blit_image
  |     +-- resolve_image
  |     +-- depth_stencil_msaa_copy
  |     +-- buffer_to_depthstencil_compute_queue
  |     +-- depthstencil_to_buffer_compute_queue
  |     +-- buffer_to_depthstencil_transfer_queue
  |     +-- depthstencil_to_buffer_transfer_queue
  |     +-- image_to_buffer_transfer_queue
  |     +-- buffer_to_image_transfer_queue
  |     +-- buffer_to_buffer_transfer_queue
  |     +-- image_to_buffer_compute_queue
  |     +-- buffer_to_image_compute_queue
  |     +-- image_to_image_general_layout        [suballocated, no extensions only]
  |     +-- image_to_buffer_general_layout        [suballocated, no extensions only]
  |     +-- buffer_to_image_general_layout        [suballocated, no extensions only]
  |     +-- memory_to_image_indirect              [non-SC]
  |     +-- memory_to_depthstencil_indirect       [non-SC]
  |     +-- image_to_buffer_indirect              [non-SC]
  |     +-- memory_to_image_indirect_transfer_queue  [non-SC]
  |     +-- image_to_buffer_indirect_transfer_queue  [non-SC]
  |     +-- memory_to_image_indirect_compute_queue   [non-SC]
  |     +-- image_to_buffer_indirect_compute_queue   [non-SC]
  |     +-- buffer_offset_tests
  |     +-- use_after_xfer
  +-- dedicated_allocation
  |     +-- image_to_image
  |     +-- image_to_buffer
  |     +-- buffer_to_image
  |     +-- buffer_to_depthstencil
  |     +-- depthstencil_to_buffer
  |     +-- buffer_to_buffer
  |     +-- blit_image
  |     +-- resolve_image
  |     +-- depth_stencil_msaa_copy
  |     +-- buffer_to_depthstencil_compute_queue
  |     +-- depthstencil_to_buffer_compute_queue
  |     +-- buffer_to_depthstencil_transfer_queue
  |     +-- depthstencil_to_buffer_transfer_queue
  |     +-- image_to_buffer_transfer_queue
  |     +-- buffer_to_image_transfer_queue
  |     +-- buffer_to_buffer_transfer_queue
  |     +-- image_to_buffer_compute_queue
  |     +-- buffer_to_image_compute_queue
  |     +-- memory_to_image_indirect              [non-SC]
  |     +-- memory_to_depthstencil_indirect       [non-SC]
  |     +-- image_to_buffer_indirect              [non-SC]
  |     +-- memory_to_image_indirect_transfer_queue  [non-SC]
  |     +-- image_to_buffer_indirect_transfer_queue  [non-SC]
  |     +-- memory_to_image_indirect_compute_queue   [non-SC]
  |     +-- image_to_buffer_indirect_compute_queue   [non-SC]
  +-- copy_commands2
  |     +-- image_to_image
  |     +-- image_to_buffer
  |     +-- buffer_to_image
  |     +-- buffer_to_depthstencil
  |     +-- depthstencil_to_buffer
  |     +-- buffer_to_buffer
  |     +-- blit_image
  |     +-- resolve_image
  |     +-- depth_stencil_msaa_copy
  |     +-- buffer_to_depthstencil_compute_queue
  |     +-- depthstencil_to_buffer_compute_queue
  |     +-- buffer_to_depthstencil_transfer_queue
  |     +-- depthstencil_to_buffer_transfer_queue
  |     +-- image_to_buffer_transfer_queue
  |     +-- buffer_to_image_transfer_queue
  |     +-- buffer_to_buffer_transfer_queue
  |     +-- image_to_buffer_compute_queue
  |     +-- buffer_to_image_compute_queue
  |     +-- image_to_image_transfer_queue
  |     +-- image_to_image_transfer_queue_secondary
  |     +-- image_to_image_transfer_sparse
  +-- sparse
  |     +-- image_to_image
  +-- multiplane
  +-- dynamic_state_meta_ops                   [non-SC]
  +-- indirect                                 [non-SC]
  +-- device_address                           [non-SC]
  |     +-- image_to_buffer
  |     +-- buffer_to_image
  |     +-- buffer_to_depthstencil
  |     +-- buffer_to_buffer
  +-- reinterpretation
```

## Test Families

### Core and Dedicated Allocation

[addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119) creates subgroups for each copy/blit type under both `core` (suballocated) and `dedicated_allocation` groups. Each subgroup delegates to a sub-file: image_to_image, image_to_buffer, buffer_to_image, buffer_to_depthstencil, depthstencil_to_buffer, buffer_to_buffer, blit_image, resolve_image, depth_stencil_msaa_copy. Additional subgroups for compute-only and transfer-only queues are added.

### Copy Commands2

The `copy_commands2` group uses the same [addCopiesAndBlittingTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119) but with the COPY_COMMANDS_2 extension flag, adding image_to_image_transfer_queue, image_to_image_transfer_queue_secondary, and image_to_image_transfer_sparse subgroups.

### Sparse

[addSparseCopyTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L57) adds a sparse image_to_image subgroup using COPY_COMMANDS_2 and SPARSE_BINDING flags.

### Indirect Copy (non-SC)

[addIndirectCopyTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74) adds memory_to_image_indirect, memory_to_depthstencil_indirect, and image_to_buffer_indirect subgroups for universal, transfer-only, and compute-only queues.

### Device Address (non-SC)

[addDeviceAddressTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L249) adds image_to_buffer, buffer_to_image, buffer_to_depthstencil, and buffer_to_buffer subgroups using DEVICE_ADDRESS_COMMANDS.

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
| VK_KHR_maintenance5 | dynamic_state_meta_ops (delegated) |
| Indirect copy extension | indirect group (non-SC) |
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
- SC divergence: indirect copy and device address groups are excluded for Vulkan SC

## Notes / Uncertainties

- The `core` group additionally includes indirect copy tests and use-after-copy tests that are not in `dedicated_allocation`
- The `copy_commands2` group uses dedicated allocation internally (hardcoded at [line 276](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L276))
- The `multiplane` subgroup is created by [createCopyMultiplaneImageTransferQueueTests()](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L283) and its internal structure is defined in a separate file
- The `dynamic_state_meta_ops`, `indirect`, and `device_address` groups are non-SC only
