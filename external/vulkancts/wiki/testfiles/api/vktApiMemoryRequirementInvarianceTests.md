# [vktApiMemoryRequirementInvarianceTests.cpp](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1)

## Overview

Tests that Vulkan memory requirements are invariant: querying memory requirements for the same resource at different times or in different allocation orders must return identical results. Also verifies that alignment values match for identically-created objects and that memory requirements from `vkGetDeviceBufferMemoryRequirements`/`vkGetDeviceImageMemoryRequirements` match those from `vkGetBufferMemoryRequirements2`/`vkGetImageMemoryRequirements2`.

## Role of File

Implementation-heavy. Contains test logic for memory requirement invariance, alignment matching, and dedicated requirements matching. The public entry point [createMemoryRequirementInvarianceTests()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L760) assembles the test tree.

## Source Code

- Source: [vktApiMemoryRequirementInvarianceTests.cpp](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1)
- Header: [vktApiMemoryRequirementInvarianceTests.hpp](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L122) adds `invariance` group to `api`

## Registration Hierarchy

```text
api.invariance
├── random
├── memory_requirements_matching
└── memory_dedicated_requirements_matching
```

## Test Families

### random

Allocates 1000 buffers and images (100 for VKSC) in a reference order, records their memory requirement sizes, then deallocates and reallocates them in a shuffled order. Verifies that the memory requirement sizes remain identical regardless of allocation order. Uses random buffer sizes (7-1030 bytes), random usage flags, random image formats, and random memory types. Implemented by [InvarianceInstance](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L244).

### memory_requirements_matching

Creates multiple VkBuffer and VkImage objects with identical create infos and verifies that their alignment values match. Also verifies that `vkGetDeviceBufferMemoryRequirements`/`vkGetDeviceImageMemoryRequirements` report the same requirements as `vkGetBufferMemoryRequirements2`/`vkGetImageMemoryRequirements2`. Additionally checks that larger resources never report smaller size requirements. Implemented by [AlignmentMatchingInstance](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L435) with `TT_REQUIREMENTS_MATCHING`.

### memory_dedicated_requirements_matching

Extends the alignment matching test to also verify that `VkMemoryDedicatedRequirements` reported by `vkGetBufferMemoryRequirements2`/`vkGetImageMemoryRequirements2` match those from `vkGetDeviceBufferMemoryRequirements`/`vkGetDeviceImageMemoryRequirements`. Implemented by [AlignmentMatchingInstance](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L435) with `TT_DEDICATED_REQUIREMENTS`.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Test Type | TT_BASIC_INVARIANCE, TT_REQUIREMENTS_MATCHING, TT_DEDICATED_REQUIREMENTS |
| Resource Type | buffer, image (randomly selected) |
| Buffer Size | 7-1030 bytes (random) |
| Buffer Usage | random VkBufferUsageFlagBits |
| Image Format | random from supported formats |
| Image Tiling | linear, optimal (randomly selected) |
| Memory Type | random from 11 legal memory type combinations |
| Allocation Mode | suballocated, dedicated (randomly selected when supported) |
| Test Cycles | 1000 (non-VKSC), 100 (VKSC) |

## Support / Feature Requirements

- `VK_KHR_maintenance4` required for `memory_requirements_matching` and `memory_dedicated_requirements_matching` tests ([InvarianceCase::checkSupport()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L754))
- `VK_KHR_dedicated_allocation` checked at runtime for dedicated allocation random tests ([InvarianceInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L272))
- `VK_KHR_sampler_ycbcr_conversion` checked for YCbCr format support ([InvarianceInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L273))
- `VK_KHR_get_memory_requirements2` checked for method2 queries ([AlignmentMatchingInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L528))

## Verification Methods

- Random invariance: Compare `vkGetBufferMemoryRequirements`/`vkGetImageMemoryRequirements` size values between reference and shuffled allocation orders ([InvarianceInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L264))
- Alignment matching: Compare alignment values across identically-created objects; compare requirements between `vkGetDevice*MemoryRequirements` and `vkGet*MemoryRequirements2` ([AlignmentMatchingInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L452))
- Size monotonicity: Verify that larger resources never report smaller size requirements ([L685-L718](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L685))
- Dedicated requirements: Compare `prefersDedicatedAllocation` and `requiresDedicatedAllocation` between method2 and device queries ([L606-L616](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L606))

## Test Principles Observed

- Randomized testing with fixed seed (0x600613) for reproducibility
- Invariance property: same create info must always yield same memory requirements
- Monotonicity property: larger resources must not report smaller size requirements
- Cross-method consistency: different API query methods must agree

## Notes / Uncertainties

- The group name is `invariance` as confirmed in [createMemoryRequirementInvarianceTests()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L762), not `memory_requirement_invariance`
- The random test uses a fixed seed (0x600613) for deterministic results across runs ([L751](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L751))
- PVRTC1 formats require power-of-2 dimensions per VUIDs 09583 and 09584 ([L186-L189](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L186))
- YCbCr 420/422 formats require width/height alignment of 2 ([L193-L198](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L193))
