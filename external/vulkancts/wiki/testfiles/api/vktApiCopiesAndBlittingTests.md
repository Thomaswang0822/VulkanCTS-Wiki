# vktApiCopiesAndBlittingTests

## Overview

This is the **registration/dispatcher file** for the `copy_and_blit` subtree within the Vulkan API test category. It does not contain test instance logic itself; instead it creates the top-level `copy_and_blit` group and delegates to 14 included implementation files that provide the actual test families.

## Role

- **Registration / dispatcher file** — creates the `copy_and_blit` test group and populates it with subgroups.

## Source Code

- [`vktApiCopiesAndBlittingTests.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp)
- [`vktApiCopiesAndBlittingTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.hpp)

## Registration Path

```
api → copy_and_blit
```

Registered at [`vktApiTests.cpp:108`](../../../external/vulkancts/modules/vulkan/api/vktApiTests.cpp:108) via `createCopiesAndBlittingTests(testCtx)`.

## Included Implementation Files

| Include | Delegated Subgroup(s) |
|---------|----------------------|
| [`vktApiCopyImageToImageTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToImageTests.hpp) | `image_to_image`, variants |
| [`vktApiCopyBufferToBufferTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToBufferTests.hpp) | `buffer_to_buffer`, variants |
| [`vktApiCopyImageToBufferTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyImageToBufferTests.hpp) | `image_to_buffer`, variants |
| [`vktApiCopyBufferToImageTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToImageTests.hpp) | `buffer_to_image`, variants |
| [`vktApiCopyBufferToDepthStencilTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.hpp) | `buffer_to_depthstencil`, variants |
| [`vktApiCopyDepthStencilToBufferTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyDepthStencilToBufferTests.hpp) | `depthstencil_to_buffer`, variants |
| [`vktApiCopyDepthStencilMSAATests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyDepthStencilMSAATests.hpp) | `depth_stencil_msaa_copy` |
| [`vktApiBlittingTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiBlittingTests.hpp) | `blit_image` |
| [`vktApiResolveTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiResolveTests.hpp) | `resolve_image` |
| [`vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp) | `dynamic_state_meta_ops` (non-VKSC) |
| [`vktApiCopiesAndBlittingReinterpretTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.hpp) | `reinterpret` |
| [`vktApiCopyMultiplaneImageTransferQueueTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyMultiplaneImageTransferQueueTests.hpp) | `multiplane_transfer_queue` |
| [`vktApiCopyMemoryIndirectTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopyMemoryIndirectTests.hpp) | `memory_to_image_indirect`, `image_to_buffer_indirect` (non-VKSC) |
| [`vktApiUseAfterCopyTests.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiUseAfterCopyTests.hpp) | `use_after_copy` |

## Test Hierarchy

Created by [`createCopiesAndBlittingTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp:267):

```
copy_and_blit
├── core
│   ├── image_to_image            (addCopyImageToImageTests, Universal)
│   ├── image_to_buffer           (addCopyImageToBufferTests, Universal)
│   ├── buffer_to_image           (addCopyBufferToImageTests, Universal)
│   ├── buffer_to_depthstencil    (addCopyBufferToDepthStencilTests, Universal)
│   ├── depthstencil_to_buffer    (addCopyDepthStencilToBufferTests, Universal)
│   ├── buffer_to_buffer          (addCopyBufferToBufferTests, Universal)
│   ├── blit_image                (addBlittingImageTests)
│   ├── resolve_image             (addResolveImageTests)
│   ├── depth_stencil_msaa_copy   (addCopyDepthStencilMSAATests)
│   ├── buffer_to_depthstencil_compute_queue      (Maint10 + ComputeOnly)
│   ├── depthstencil_to_buffer_compute_queue      (Maint10 + ComputeOnly)
│   ├── buffer_to_depthstencil_transfer_queue     (Maint10 + TransferOnly)
│   ├── depthstencil_to_buffer_transfer_queue     (Maint10 + TransferOnly)
│   ├── image_to_buffer_transfer_queue            (TransferOnly)
│   ├── buffer_to_image_transfer_queue            (TransferOnly)
│   ├── buffer_to_buffer_transfer_queue           (TransferOnly)
│   ├── image_to_buffer_compute_queue             (ComputeOnly)
│   ├── buffer_to_image_compute_queue             (ComputeOnly)
│   ├── image_to_image_general_layout             (suballocated only)
│   ├── image_to_buffer_general_layout            (suballocated only)
│   ├── buffer_to_image_general_layout            (suballocated only)
│   ├── memory_to_image_indirect                  (non-VKSC)
│   ├── memory_to_depthstencil_indirect           (non-VKSC)
│   ├── image_to_buffer_indirect                  (non-VKSC)
│   ├── buffer_offset_tests
│   └── use_after_copy                            (non-VKSC)
├── dedicated_allocation
│   └── (same copy/blit/resolve subgroups as core, no general_layout/offset/use_after_copy)
├── copy_commands2
│   └── (COPY_COMMANDS_2 + dedicated allocation)
│       ├── image_to_image_transfer_queue
│       ├── image_to_image_transfer_queue_secondary
│       └── image_to_image_transfer_sparse
├── sparse
│   └── image_to_image           (COPY_COMMANDS_2 | SPARSE_BINDING, TransferOnly)
├── multiplane_transfer_queue
├── dynamic_state_meta_ops       (non-VKSC only)
├── copy_memory_indirect         (non-VKSC only)
├── device_address               (non-VKSC only)
│   ├── image_to_buffer
│   ├── buffer_to_image
│   ├── buffer_to_depthstencil
│   └── buffer_to_buffer
└── reinterpret
```

## Key Parameter Dimensions

The dispatcher propagates [`TestGroupParams`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:334) to subgroups:

| Parameter | Values | Effect |
|-----------|--------|--------|
| `allocationKind` | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | Memory allocation strategy |
| `extensionFlags` | `NONE`, `COPY_COMMANDS_2`, `SPARSE_BINDING`, `INDIRECT_COPY`, `DEVICE_ADDRESS_COMMANDS`, `MAINTENANCE_1`, `MAINTENANCE_10` | Extension API paths |
| `queueSelection` | `Universal`, `ComputeOnly`, `TransferOnly` | Queue family for command submission |
| `useSecondaryCmdBuffer` | `bool` | Record copy commands in secondary command buffer |
| `useSparseBinding` | `bool` | Use sparse-resident image memory |
| `useGeneralLayout` | `bool` | Use `VK_IMAGE_LAYOUT_GENERAL` instead of optimal transfer layouts |

## Notes / Uncertainties

- The `core` subgroup additionally adds [`addIndirectCopyTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp:74), [`addCopyBufferToBufferOffsetTests()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp:237), and `use_after_copy` that are not present in `dedicated_allocation`.
- `dynamic_state_meta_ops`, `copy_memory_indirect`, and `device_address` are guarded by `#ifndef CTS_USES_VULKANSC` ([lines 285–289](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp:285)).