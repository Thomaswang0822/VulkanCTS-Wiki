# [vktApiBufferAndImageAllocationUtil.cpp](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L1)

## Overview

Provides utility classes that abstract buffer and image memory allocation strategies for Vulkan CTS tests. Implements the strategy pattern via `IBufferAllocator` and `IImageAllocator` interfaces, with concrete implementations for suballocation and dedicated allocation approaches.

## Role of File

Utility/helper. Provides reusable allocation abstractions consumed by other test files (e.g., [vktApiBufferViewAccessTests.cpp](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1)).

## Source Code

- Implementation: [vktApiBufferAndImageAllocationUtil.cpp](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L1)
- Header: [vktApiBufferAndImageAllocationUtil.hpp](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L1)

## Registration Path

Utility file. Not directly registered in the test hierarchy. Used by other test files that need parameterized buffer/image allocation.

## Test Hierarchy

Not applicable (utility file).

## Classes and Utilities

### IBufferAllocator ([L47](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L47))

Abstract interface for buffer allocation. Declares `createTestBuffer()` which creates a VkBuffer, allocates memory, and binds them together. Output parameters are `Move<VkBuffer>& buffer` and `de::MovePtr<Allocation>& memory`.

### BufferSuballocation ([L60](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L60))

Concrete implementation that creates a buffer and suballocates memory from a shared allocator. Implementation at [L41](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L41). Creates a `VkBufferCreateInfo` with the given size and usage, allocates via `Allocator::allocate()`, and binds at offset 0.

### BufferDedicatedAllocation ([L69](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L69))

Concrete implementation that creates a buffer with dedicated memory allocation. Implementation at [L64](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L64). Requires `VK_KHR_dedicated_allocation` extension support ([L70](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L70)). Uses `allocateDedicated()` for memory allocation and binds at the allocation's offset.

### IImageAllocator ([L78](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L78))

Abstract interface for image allocation. Declares `createTestImage()` with parameters for size, format, tiling, and usage. Default tiling is `VK_IMAGE_TILING_OPTIMAL`; default usage is `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT`.

### ImageSuballocation ([L92](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L92))

Concrete implementation that creates a 2D image and suballocates memory. Implementation at [L92](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L92). When tiling is `VK_IMAGE_TILING_LINEAR`, forces usage to `TRANSFER_SRC | TRANSFER_DST`; otherwise appends `TRANSFER_SRC` to the provided usage flags ([L111](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L111)).

### ImageDedicatedAllocation ([L101](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L101))

Concrete implementation that creates a 2D image with dedicated memory allocation. Implementation at [L125](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L125). Requires `VK_KHR_dedicated_allocation` extension support ([L131](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L131)). Same tiling/usage logic as `ImageSuballocation`.

## Parameter Dimensions

Not applicable (utility file). The allocation strategy is selected by consuming test code.

## Support / Feature Requirements

| Requirement | Used By | Source |
|---|---|---|
| VK_KHR_dedicated_allocation | BufferDedicatedAllocation, ImageDedicatedAllocation | [L70](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L70), [L131](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L131) |

## Verification Methods

Not applicable (utility file). These classes provide allocation infrastructure; verification is performed by the consuming test instances.

## Test Principles Observed

- **Strategy pattern**: The `IBufferAllocator` and `IImageAllocator` interfaces allow test code to switch between suballocation and dedicated allocation without changing test logic.
- **Extension-aware**: Dedicated allocation implementations check for `VK_KHR_dedicated_allocation` and throw `NotSupportedError` if unavailable.
- **Consistent image usage**: Both image allocators automatically add `VK_IMAGE_USAGE_TRANSFER_SRC_BIT` for optimal tiling and force transfer-only usage for linear tiling, ensuring images are always copyable for verification.

## Notes / Uncertainties

- The `BufferSuballocation::createTestBuffer` method ignores the `Context` parameter (via `DE_UNREF(context)`) at [L46](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.cpp#L46), while `BufferDedicatedAllocation` uses it to check extension support. This asymmetry is by design since suballocation does not require any extensions.
- The `ImageSuballocation::createTestImage` default usage in the header ([L98](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L98)) differs from the interface default ([L88](../../modules/vulkan/api/vktApiBufferAndImageAllocationUtil.hpp#L88)): the interface specifies `COLOR_ATTACHMENT | TRANSFER_SRC` while the concrete class specifies only `COLOR_ATTACHMENT`. The `TRANSFER_SRC` is added internally by the implementation.
- Both image allocators create single-sample, single-mip-level, single-layer 2D images only.
