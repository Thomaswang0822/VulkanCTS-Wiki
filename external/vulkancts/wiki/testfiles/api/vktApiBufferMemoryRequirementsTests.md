# [vktApiBufferMemoryRequirementsTests.cpp](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1)

## Overview

Tests that `vkGetBufferMemoryRequirements` and `vkGetBufferMemoryRequirements2` return non-zero `memoryTypeBits` for buffers created with various combinations of create flags, usage flags, and external memory handle types. Also validates the VK_KHR_maintenance4 size requirement guarantee that buffer memory size is less than or equal to the aligned buffer size.

## Role of File

Implementation-heavy. Contains the `BufferMemoryRequirementsInstance` test instance, `MemoryRequirementsTest` test case with support checking, and the combinatorial test group construction.

## Source Code

- Implementation: [vktApiBufferMemoryRequirementsTests.cpp](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1)
- Header: [vktApiBufferMemoryRequirementsTests.hpp](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.hpp#L1)
- Utils: [vktApiBufferMemoryRequirementsTestsUtils.hpp](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTestsUtils.hpp#L1) (provides `BitsSet`, `combine`, `mergeFlags` utilities)
- Parent registration: `vktApiTests.cpp` registers `createBufferMemoryRequirementsTests()` under `api` -> `buffer_memory_requirements`

## Registration Path

```
api
  +-- buffer_memory_requirements
        +-- create_<flags>
              +-- ext_mem_flags_excluded | ext_mem_flags_included
                    +-- method1 | method2
                          +-- <fate_name> | size_req_<fate_name>
```

## Test Hierarchy

```
buffer_memory_requirements
  +-- create_no_flags
  |     +-- ext_mem_flags_excluded
  |     |     +-- method1
  |     |     |     +-- transfer_usage_bits
  |     |     |     +-- storage_usage_bits
  |     |     |     +-- other_usage_bits
  |     |     |     +-- acc_struct_usage_bits
  |     |     |     +-- video_usage_bits
  |     |     |     +-- size_req_transfer_usage_bits
  |     |     |     +-- ...
  |     |     +-- method2
  |     |           +-- ...
  |     +-- ext_mem_flags_included
  |           +-- ...
  +-- create_protected
  |     +-- ...
  +-- create_sparse_binding
  |     +-- ...
  +-- create_sparse_residency
  |     +-- ...
  +-- create_sparse_aliased
        +-- ...
```

## Test Families

### memoryTypeBits non-zero check ([L948](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L948))

The primary test family. Creates a buffer with the given create flags, usage flags, and optional external memory handle type flags, then queries memory requirements via either `vkGetBufferMemoryRequirements` (method1) or `vkGetBufferMemoryRequirements2` (method2). Passes if `memoryTypeBits` is non-zero, fails otherwise. Buffer size is fixed at 4096 bytes ([L882](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L882)).

### size_req check ([L890](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L890))

Tests the VK_KHR_maintenance4 guarantee that `memoryRequirements.size <= align(bufferSize, memoryRequirements.alignment)`. Creates buffers of increasing size from 1 to `maxBufferSize` (powers of 2 plus 1) and validates the size requirement for each. Only available when VK_KHR_maintenance4 is supported. Test names are prefixed with `size_req_`.

## Parameter Dimensions

| Dimension | Values | Notes |
|---|---|---|
| Create flags | no_flags, protected, sparse_binding, sparse_residency, sparse_aliased | Combinatorial via [AvailableBufferCreateBits](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L119); sparse flags excluded on VKSC |
| Usage fate | transfer_usage_bits, storage_usage_bits, other_usage_bits, acc_struct_usage_bits, video_usage_bits | Categorizes usage flags into fate groups ([L73](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L73)) |
| External memory flags | excluded, included | When included, iterates over all external memory handle types |
| Query method | method1, method2 | method1 = vkGetBufferMemoryRequirements; method2 = vkGetBufferMemoryRequirements2 |
| Size requirements | false, true | true adds size_req_ prefixed tests; only on non-VKSC |

## Support / Feature Requirements

| Requirement | Gate | Source |
|---|---|---|
| VK_KHR_get_physical_device_properties2 | Always required | [L379](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L379) |
| VK_KHR_get_memory_requirements2 | Required for method2 | [L382](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L382) |
| VK_KHR_dedicated_allocation | Implicit via method2 | Required for VkMemoryDedicatedRequirements chain |
| sparseBinding | Required for VK_BUFFER_CREATE_SPARSE_BINDING_BIT | [L405](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L405) |
| sparseResidencyBuffer | Required for VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT | [L410](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L410) |
| sparseResidencyAliased | Required for VK_BUFFER_CREATE_SPARSE_ALIASED_BIT | [L417](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L417) |
| protectedMemory | Required for VK_BUFFER_CREATE_PROTECTED_BIT | [L424](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L424) |
| VK_KHR_acceleration_structure | Required for acceleration structure usage bits | [L462](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L462) |
| VK_EXT_buffer_device_address | Required for shader device address usage | [L478](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L478) |
| VK_KHR_video_queue | Required for video usage bits | [L494](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L494) |
| VK_KHR_video_encode_h264 | Required for video encode usage bits | [L511](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L511) |
| VK_KHR_video_decode_h264 | Required for video decode usage bits | [L537](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L537) |
| VK_KHR_maintenance4 | Required for size_req tests | [L617](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L617) |
| VK_KHR_maintenance5 | Required for bind usage differentiation (video profiles) | Implicit via VkBufferUsageFlags2CreateInfoKHR |

## Verification Methods

- **memoryTypeBits check**: After querying memory requirements, the test checks `reqs.memoryTypeBits != 0`. If zero, the sub-test is counted as failed and the create/usage/ext-mem flags are logged ([L953](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L953)).
- **size_req check**: Validates `reqs.size <= deAlign64(createInfo.size, reqs.alignment)` for each buffer size. Failures are logged with the associated flag combination ([L922](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L922)).
- **Protected memory**: When `VK_BUFFER_CREATE_PROTECTED_BIT` is set, a custom device with protected memory feature enabled is created via [createProtectedDevice](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L794) ([L843](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L843)).
- **Aggregate pass/fail**: The test accumulates pass/fail counts across all sub-tests (create flags x usage flags x ext mem flags). Returns `TestStatus::fail` with the fail count if any sub-test fails, or `TestStatus::pass` with the pass count otherwise ([L967](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L967)).

## Test Principles Observed

- **Combinatorial coverage**: Uses `BitsSet` and `combine` utilities to generate all valid combinations of create flags and usage flags, ensuring broad API coverage.
- **VUID enforcement**: `updateBufferCreateFlags` enforces VUID-00918 (sparse residency/aliased implies sparse binding) and VUID-01888 (sparse and protected are mutually exclusive) at test construction time ([L193](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L193)).
- **Graceful unsupported handling**: The `checkSupport` method filters out unsupported usage flag combinations rather than failing, allowing partial test execution ([L565](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L565)).
- **Video codec support detection**: Queries `VkQueueFamilyVideoPropertiesKHR` to check for actual video codec support before running video-related tests ([L336](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L336)).

## Notes / Uncertainties

- The `BufferFateBits` approach groups usage flags into categories (Transfer, Storage, Other, AccStructure, Video) rather than testing every individual usage flag combination, which reduces combinatorial explosion but may miss some specific usage flag interactions.
- The `fateBitPtrs` generation uses individual fate bits rather than their full combinatorial product (the cartesian product code is commented out at [L1007](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1007)), which is a deliberate complexity reduction.
- The `chainVkStructure<VkVideoProfileListInfoKHR>` specialization uses `static` local variables ([L740](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L740)), which means it is not thread-safe, though CTS typically runs tests sequentially.
- The `chainVkStructure<VkExternalMemoryBufferCreateInfo>` also uses a static local ([L721](../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L721)), with the same thread-safety consideration.
- The size_req test iterates buffer sizes as `(1 << N) + 1` up to `maxBufferSize`, catching potential off-by-one issues in alignment calculations.
