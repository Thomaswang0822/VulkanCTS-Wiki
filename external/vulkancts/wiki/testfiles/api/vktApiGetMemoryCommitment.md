# [vktApiGetMemoryCommitment.cpp](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1)

## Overview

Tests the `vkGetDeviceMemoryCommitment` API, which reports the amount of memory currently committed for a lazily-allocated memory type. The file validates that committed memory values are consistent before and after rendering operations, and that allocation-only memory reports zero or within-bounds commitment.

## Role of File

Implementation-heavy. Contains two full test classes (`MemoryCommitmentTestCase`/`MemoryCommitmentTestInstance` and `MemoryCommitmentAllocateOnlyTestCase`/`MemoryCommitmentAllocateOnlyTestInstance`) with substantial Vulkan object setup including images, render passes, pipelines, and command buffers.

## Source Code

- Implementation: [vktApiGetMemoryCommitment.cpp](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1)
- Header: [vktApiGetMemoryCommitment.hpp](../../modules/vulkan/api/vktApiGetMemoryCommitment.hpp#L1)
- Parent registration: `createMemoryCommitmentTests()` declared at [L36](../../modules/vulkan/api/vktApiGetMemoryCommitment.hpp#L36)

## Registration Path

```
api
  +-- memory_commitment
        +-- get_memory_commitment
              +-- memory_commitment
              +-- memory_commitment_allocate_only
```

## Test Hierarchy

```
get_memory_commitment
  +-- memory_commitment
  |     Full rendering pipeline test: creates lazily-allocated image,
  |     renders, checks commitment before and after.
  +-- memory_commitment_allocate_only
        Allocates memory with LAZILY_ALLOCATED_BIT, queries commitment
        without binding to any resource.
```

## Test Families

### memory_commitment

Creates a 256x256 `VK_FORMAT_R32_UINT` image with `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT`, allocates lazily-allocated memory, binds it, builds a full graphics pipeline (vertex + fragment shaders), records and submits a render pass with `cmdClearAttachments`, then queries `vkGetDeviceMemoryCommitment` before and after the render. Passes if both queries report committed memory not exceeding the image's memory requirements size.

- Test case class: `MemoryCommitmentTestCase` at [L91](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L91)
- Test instance class: `MemoryCommitmentTestInstance` at [L72](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L72)
- Core logic in `iterate()` at [L113](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L113)
- Commitment validation in `isDeviceMemoryCommitmentOk()` at [L447](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L447)
- Shader programs at [L410](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L410)

### memory_commitment_allocate_only

Iterates over all memory types with `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT`, allocates 10 random-sized memory objects per type, queries `vkGetDeviceMemoryCommitment` immediately after allocation (no resource binding). Verifies that committed bytes are zero (logs a warning if nonzero) and never exceed the allocation size.

- Test case class: `MemoryCommitmentAllocateOnlyTestCase` at [L341](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L341)
- Test instance class: `MemoryCommitmentAllocateOnlyTestInstance` at [L334](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L334)
- Core logic in `iterate()` at [L362](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L362)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| bufferSize | 2048 | [L482](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L482) |
| bufferViewSize | 256 | [L483](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L483) |
| elementOffset | 0 | [L484](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L484) |
| Image format | VK_FORMAT_R32_UINT | [L147](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L147) |
| Image extent | 256x256 | [L148](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L148) |
| Memory property | VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT | [L115](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L115) |
| Random alloc sizes | rand()%1000+1 | [L381](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L381) |
| Alloc iterations | 10 per memory type | [L371](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L371) |

## Support / Feature Requirements

| Requirement | Gate | Location |
|-------------|------|----------|
| Lazily allocated memory type | `TCU_THROW(NotSupportedError)` if no memory type has `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` | [L139](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L139), [L375](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L375) |

## Verification Methods

- **Commitment bound check**: `pCommittedMemoryInBytes <= memoryRequirements.size` at [L472](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L472)
- **Pre/post render consistency**: Both `isDeviceMemoryCommitmentOk()` calls must return true at [L267](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L267) and [L326](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L326)
- **Allocation-only zero check**: `pCommittedMemoryInBytes != 0` logs a warning at [L398](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L398); `pCommittedMemoryInBytes > allocSize[i]` fails at [L403](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L403)

## Test Principles Observed

- **Invariance**: Commitment values are checked before and after rendering to confirm consistency
- **Boundary validation**: Committed memory must not exceed allocation size
- **Graceful skip**: NotSupportedError thrown when lazily-allocated memory is unavailable

## Notes / Uncertainties

- The `MemoryCommitmentCaseParams` struct includes `bufferSize`, `bufferViewSize`, and `elementOffset` fields, but `bufferSize` and `elementOffset` do not appear to be used in the test instance logic. Only `bufferViewSize` is used for `m_renderSize` at [L87](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L87).
- The `memory_commitment_allocate_only` test uses `rand()` (C stdlib) rather than the framework's `deRandom`, which may produce non-deterministic results across platforms at [L381](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L381).
- The fragment shader uses `GL_EXT_texture_buffer` extension at [L421](../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L421), but no texel buffer is actually bound during rendering; the shader is compiled but the descriptor set is never updated or bound.
