# [vktApiBufferMemoryRequirementsTests.cpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1)

## Overview

Tests that `vkGetBufferMemoryRequirements` and `vkGetBufferMemoryRequirements2` return non-zero `memoryTypeBits` for buffers created with various combinations of create flags, usage flags, and external memory handle types. Also verifies that buffer memory size requirements do not exceed the aligned buffer size when `VK_KHR_maintenance4` is supported.

## Role of File

Implementation-heavy. Contains all test logic, support checking, and registration. The public entry point [createBufferMemoryRequirementsTests()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L978) assembles the test tree.

## Source Code

- Source: [vktApiBufferMemoryRequirementsTests.cpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1)
- Header: [vktApiBufferMemoryRequirementsTests.hpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.hpp#L1)
- Utilities: [vktApiBufferMemoryRequirementsTestsUtils.hpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTestsUtils.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L127) adds `buffer_memory_requirements` group to `api`

## Registration Path

```
api
 +-- buffer_memory_requirements
      +-- create_<flags>
           +-- ext_mem_flags_excluded
           |    +-- method1
           |    |    +-- <fate_bits>
           |    |    +-- size_req_<fate_bits>      (non-VKSC only)
           |    +-- method2
           |         +-- <fate_bits>
           |         +-- size_req_<fate_bits>      (non-VKSC only)
           +-- ext_mem_flags_included
                +-- method1
                |    +-- <fate_bits>
                |    +-- size_req_<fate_bits>      (non-VKSC only)
                +-- method2
                     +-- <fate_bits>
                     +-- size_req_<fate_bits>      (non-VKSC only)
```

## Test Hierarchy

```
buffer_memory_requirements
 +-- create_no_flags
 |    +-- ext_mem_flags_excluded
 |    |    +-- method1
 |    |    |    +-- transfer_usage_bits
 |    |    |    +-- storage_usage_bits
 |    |    |    +-- other_usage_bits
 |    |    |    +-- acc_struct_usage_bits
 |    |    |    +-- video_usage_bits
 |    |    |    +-- size_req_*              (non-VKSC only)
 |    |    +-- method2
 |    |         +-- (same as method1)
 |    +-- ext_mem_flags_included
 |         +-- (same structure)
 +-- create_protected
 |    +-- (same structure)
 +-- create_sparse_binding       (non-VKSC only)
 |    +-- (same structure)
 +-- create_sparse_residency     (non-VKSC only)
 |    +-- (same structure)
 +-- create_sparse_aliased       (non-VKSC only)
      +-- (same structure)
```

## Test Families

### Memory Requirements Tests (per configuration)

Each test creates a buffer with the specified create flags and usage flags, queries its memory requirements via either `vkGetBufferMemoryRequirements` (method1) or `vkGetBufferMemoryRequirements2` (method2), and verifies that `memoryTypeBits` is non-zero. When `testSizeRequirements` is true (non-VKSC only), also verifies that the reported memory size does not exceed the aligned buffer size per `VK_KHR_maintenance4`. Implemented by [BufferMemoryRequirementsInstance](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L248).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Create Flags | no_flags, protected, sparse_binding, sparse_residency, sparse_aliased (last 3 non-VKSC only) |
| External Memory Flags | excluded, included |
| Query Method | method1 (vkGetBufferMemoryRequirements), method2 (vkGetBufferMemoryRequirements2) |
| Usage Fate Bits | transfer_usage_bits, storage_usage_bits, other_usage_bits, acc_struct_usage_bits, video_usage_bits |
| Size Requirements | false, true (non-VKSC only) |

## Support / Feature Requirements

- `VK_KHR_get_physical_device_properties2` required by all tests ([MemoryRequirementsTest::checkSupport()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L379))
- `VK_KHR_get_memory_requirements2` required when `useMethod2=true` ([L381-L382](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L381))
- `VK_KHR_maintenance4` required when `testSizeRequirements=true` (non-VKSC only)
- `VK_KHR_video_queue` and `VK_KHR_video_decode_queue`/`VK_KHR_video_encode_queue` required for video usage bits
- Protected memory feature required for `VK_BUFFER_CREATE_PROTECTED_BIT`
- Sparse binding feature required for sparse create flags
- External memory extensions required per handle type when `incExtMemTypeFlags=true`

## Verification Methods

- Non-zero memoryTypeBits: Verifies that `memoryTypeBits != 0` for each buffer configuration, ensuring at least one memory type is compatible
- Size requirements: When `testSizeRequirements=true`, verifies that `memoryRequirements.size <= align(bufferSize, memoryRequirements.alignment)` per VK_KHR_maintenance4 guarantees

## Test Principles Observed

- Comprehensive coverage of create flag and usage flag combinations
- Both query methods tested (method1 and method2)
- VK_SC conditional compilation removes sparse, video, and size requirement tests
- Support checking validates feature availability before test execution

## Notes / Uncertainties

- The group name is `buffer_memory_requirements` as confirmed in [createBufferMemoryRequirementsTests()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1021)
- The `fateBits` parameter controls which usage flag categories are included; the actual usage flags are expanded from these categories at test time
- The `BufferCreateBits` combinations are filtered to remove invalid combinations (e.g., sparse + protected) per VUID constraints ([updateBufferCreateFlags()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L193))
- The test uses a custom `BitsSet` utility from [vktApiBufferMemoryRequirementsTestsUtils.hpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTestsUtils.hpp#L1) for managing flag combinations
