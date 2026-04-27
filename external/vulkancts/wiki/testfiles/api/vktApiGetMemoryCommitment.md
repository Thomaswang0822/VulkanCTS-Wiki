# [vktApiGetMemoryCommitment.cpp](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1)

## Overview

Tests vkGetDeviceMemoryCommitment with lazily allocated memory types. Verifies that the reported commitment is valid (non-zero but not exceeding allocation size after binding, and not exceeding allocation size before binding) and that lazily allocated memory works correctly with transient attachment images.

## Role of File

Implementation-heavy. Contains all test logic, helper classes, and the registration function [createMemoryCommitmentTests()](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L479).

## Source Code

- Implementation: [vktApiGetMemoryCommitment.cpp](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1)
- Header: [vktApiGetMemoryCommitment.hpp](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L115)

## Registration Path

```
api
  +-- get_memory_commitment
```

## Test Hierarchy

```
get_memory_commitment
  +-- memory_commitment
  +-- memory_commitment_allocate_only
```

## Test Families

### Memory Commitment

[MemoryCommitmentTestInstance::iterate()](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L113) creates a transient color attachment image (VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT) with lazily allocated memory, renders to it using a graphics pipeline, and then checks vkGetDeviceMemoryCommitment both before and after rendering. Verifies that the committed memory size does not exceed the memory requirements size.

The test uses a 256x256 R32_UINT image, creates a render pass, framebuffer, and graphics pipeline, and performs a clear attachment operation before checking memory commitment.

### Memory Commitment Allocate Only

[MemoryCommitmentAllocateOnlyTestInstance::iterate()](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L362) allocates memory with VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT and immediately calls vkGetDeviceMemoryCommitment without binding it to any resource. Tests 10 random allocation sizes per memory type. Verifies that the committed size is not greater than the allocation size. Logs a warning if the committed size is non-zero before binding.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Image format | VK_FORMAT_R32_UINT |
| Image extent | 256x256 |
| Image usage | COLOR_ATTACHMENT + TRANSIENT_ATTACHMENT |
| Memory property | VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT |
| Buffer size | 2048 |
| Buffer view size | 256 |
| Element offset | 0 |
| Random allocation sizes | 10 per memory type (1-1000 bytes) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT | All tests (skipped if no memory type supports it) |

## Verification Methods

- **Commitment size check**: [isDeviceMemoryCommitmentOk()](../../../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L447) verifies that committed memory does not exceed the memory requirements size
- **Pre-binding check**: memory_commitment_allocate_only verifies that commitment before binding does not exceed allocation size
- **VK_CHECK**: API calls are verified for success
- **NotSupportedError**: Tests skip if no memory type supports VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT

## Test Principles Observed

- Lazily allocated memory: tests specifically target the VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT property
- Pre/post binding: commitment is checked both before and after the memory is actually used
- Randomization: allocate-only tests use random allocation sizes for variety
- Spec compliance: verifies the guarantees made by vkGetDeviceMemoryCommitment

## Notes / Uncertainties

- The factory function is named `createMemoryCommitmentTests` but the group name is `get_memory_commitment`
- The memory_commitment test uses a full graphics pipeline with vertex and fragment shaders to render to the transient image, which is a heavyweight approach for testing memory commitment
- The memory_commitment_allocate_only test uses rand() for allocation sizes, which is not seeded deterministically
- Tests will be skipped on devices that do not support any lazily allocated memory types (common on desktop GPUs)
