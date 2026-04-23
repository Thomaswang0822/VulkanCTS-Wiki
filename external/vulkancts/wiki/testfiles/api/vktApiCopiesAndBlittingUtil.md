# vktApiCopiesAndBlittingUtil

## Overview

Shared utility header and implementation for all copy-and-blit test files. Defines the core parameter types, enums, base test-instance classes, and helper functions used across the entire `copy_and_blit` subtree.

## Role

- **Helper/util file** — materially affects understanding of all implementation files in the subtree. Every implementation file includes this header.

## Source Code

- [`vktApiCopiesAndBlittingUtil.hpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp)
- [`vktApiCopiesAndBlittingUtil.cpp`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp)

## Key Enums

### [`FillMode`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:98)

Controls how source/destination buffers and images are populated with test data.

| Value | Purpose |
|-------|---------|
| `FILL_MODE_GRADIENT` | Gradient pattern (default for src) |
| `FILL_MODE_PYRAMID` | Pyramid pattern |
| `FILL_MODE_WHITE` | All-white (default for dst image) |
| `FILL_MODE_BLACK` | All-black |
| `FILL_MODE_RED` | Solid red |
| `FILL_MODE_RANDOM_GRAY` | Random gray values |
| `FILL_MODE_MULTISAMPLE` | Multisample-specific fill |
| `FILL_MODE_BLUE_RED_X/Y/Z` | Blue-red gradient along specific axis |

### [`AllocationKind`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:124)

| Value | Purpose |
|-------|---------|
| `ALLOCATION_KIND_SUBALLOCATED` | Sub-allocated from a larger memory block |
| `ALLOCATION_KIND_DEDICATED` | Dedicated allocation per resource |

### [`ExtensionUseBits`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:132)

Bitfield controlling which Vulkan extension API paths to exercise. Checked by [`checkExtensionSupport()`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:356).

| Bit | Value | Purpose |
|-----|-------|---------|
| `NONE` | `0` | Core Vulkan commands only |
| `COPY_COMMANDS_2` | `(1<<0)` | `VK_KHR_copy_commands2` / Vulkan 1.3 `cmdCopy*2` |
| `SEPARATE_DEPTH_STENCIL_LAYOUT` | `(1<<1)` | `VK_KHR_separate_depth_stencil_layouts` |
| `MAINTENANCE_1` | `(1<<2)` | `VK_KHR_maintenance1` |
| `MAINTENANCE_5` | `(1<<3)` | `VK_KHR_maintenance5` |
| `SPARSE_BINDING` | `(1<<4)` | Sparse binding/residency |
| `MAINTENANCE_8` | `(1<<5)` | `VK_KHR_maintenance8` |
| `INDIRECT_COPY` | `(1<<6)` | `VK_KHR_copy_memory_indirect` |
| `MAINTENANCE_10` | `(1<<7)` | `VK_KHR_maintenance10` |
| `DEVICE_ADDRESS_COMMANDS` | `(1<<8)` | `VK_KHR_device_address_commands` / `cmdCopyMemoryKHR` |

### [`QueueSelectionOptions`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:244)

| Value | Purpose |
|-------|---------|
| `Universal` | Universal queue family (default) |
| `ComputeOnly` | Dedicated compute queue |
| `TransferOnly` | Dedicated transfer queue |

### [`MirrorModeBits`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:114)

Used for blit coordinate mirroring: `MIRROR_MODE_X`, `MIRROR_MODE_Y`, `MIRROR_MODE_Z`.

## Key Structs

### [`CopyRegion`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:216)

A union that holds one of the Vulkan copy region structs:

- `VkBufferCopy bufferCopy`
- `VkImageCopy imageCopy`
- `VkBufferImageCopy bufferImageCopy`
- `VkImageBlit imageBlit`
- `VkImageResolve imageResolve`

### [`ImageParms`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:225)

Describes an image resource for a test: `imageType`, `format`, `extent`, `tiling`, `operationLayout`, `createFlags`, `fillMode`. Includes `texelBlockDimensions()` helper for compressed formats.

### [`BufferParams`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:258)

Describes a buffer resource: `size` and `fillMode`.

### [`TestParams`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:264)

The per-test-case parameter struct. Contains:

- `src` / `dst` — each with `.buffer` (`BufferParams`) and `.image` (`ImageParms`)
- `regions` — `std::vector<CopyRegion>` specifying copy/blit/resolve regions
- `filter` / `samples` — for blit and resolve operations
- `allocationKind`, `extensionFlags`, `queueSelection` — propagated from `TestGroupParams`
- `mipLevels`, `arrayLayers`, `conditionalPredicate`, `singleCommand`, `barrierCount`
- `clearDestinationWithRed`, `imageOffset`, `useSecondaryCmdBuffer`, `useSparseBinding`, `useGeneralLayout`, `useConditionalRender`

### [`TestGroupParams`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:334)

Per-subgroup parameter struct propagated from the dispatcher: `allocationKind`, `extensionFlags`, `queueSelection`, `useSecondaryCmdBuffer`, `useSparseBinding`, `useGeneralLayout`.

## Default Size Constants

Defined at [lines 161–175](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:161):

| Constant | Value | Usage |
|----------|-------|-------|
| `defaultSize` | 64 | Standard 2D image/buffer dimension |
| `defaultHalfSize` | 32 | Half-size for scaling tests |
| `defaultQuarterSize` | 16 | Quarter-size for scaling tests |
| `defaultLargeSize` | 4096 | Large buffer for stress tests |
| `defaultExtent` | {64,64,1} | Default 2D extent |
| `default3dExtent` | {16,16,16} | Default 3D extent |

## Base Test Instance Classes

### [`CopiesAndBlittingTestInstance`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:420)

Abstract base class inheriting `vkt::TestInstance`. Provides:

- Queue setup: universal, compute/transfer, and secondary command buffers
- Texture level storage: `m_sourceTextureLevel`, `m_destinationTextureLevel`, `m_expectedTextureLevel[16]`
- Helper methods: `generateBuffer()`, `generateExpectedResult()`, `uploadBuffer()`, `uploadImage()`, `readImage()`, `checkTestResult()`, `copyRegionToTextureLevel()` (pure virtual)
- `activeExecutionCtx()` — returns `(queue, cmdBuffer, cmdPool)` tuple based on `queueSelection`

### [`CopiesAndBlittingTestInstanceWithSparseSemaphore`](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:474)

Extends `CopiesAndBlittingTestInstance` with a `m_sparseSemaphore` for sparse image synchronization. Overrides `uploadImage()` and `readImage()` to pass the semaphore.

## Key Helper Functions

| Function | Purpose |
|----------|---------|
| `allocateBuffer()` / `allocateImage()` | Memory allocation with sub/dedicated strategy |
| `checkExtensionSupport()` | Validates required extensions are available |
| `submitCommandsAndWaitWithSync()` | Submit + wait with optional sparse semaphore |
| `submitCommandsAndWaitWithTransferSync()` | Submit + wait with transfer queue synchronization |
| `checkTransferQueueGranularity()` | Validates transfer queue granularity requirements |
| `convertvk*To*2KHR()` | Convert core Vulkan structs to `KHR`/2 versions |
| `blit()` / `scaleFromWholeSrcBuffer()` | CPU-side reference blit/scaling for comparison |
| `getFormatThreshold()` / `getCompressedFormatThreshold()` | Tolerance thresholds for format-specific comparison |
| `isSupportedDepthStencilFormat()` | Check if a depth/stencil format is supported |

## Notes / Uncertainties

- The `#define` aliases at [lines 82–90](../../../external/vulkancts/modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp:82) remap `cmdCopy*2` to `cmdCopy*2KHR` for VulkanSC, which has KHR entry points but not core 1.3 ones.
- `CompareEachPixelInEachRegion` (line 490+) is a utility struct for pixel-level comparison in copy region verification — not fully inspected beyond the header declaration.