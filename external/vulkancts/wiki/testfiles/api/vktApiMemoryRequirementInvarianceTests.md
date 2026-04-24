# [vktApiMemoryRequirementInvarianceTests.cpp](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1)

## Overview

Tests that memory requirements reported by Vulkan for buffers and images are invariant regardless of allocation order or system state. Also validates that `vkGetDeviceBufferMemoryRequirements`/`vkGetDeviceImageMemoryRequirements` match their non-device counterparts, and that alignment and size requirements follow spec-mandated monotonicity rules.

## Role of File

Implementation-heavy. Contains two test instance classes (`InvarianceInstance` and `AlignmentMatchingInstance`), plus allocator abstractions (`BufferAllocator`, `ImageAllocator`) that encapsulate random object creation and memory requirement querying.

## Source Code

- Implementation: [vktApiMemoryRequirementInvarianceTests.cpp](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1)
- Header: [vktApiMemoryRequirementInvarianceTests.hpp](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.hpp#L1)
- Parent registration: `createMemoryRequirementInvarianceTests()` declared at [L35](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.hpp#L35)

## Registration Path

```
api
  +-- memory_requirement_invariance
        +-- invariance
              +-- random
              +-- memory_requirements_matching
              +-- memory_dedicated_requirements_matching
```

## Test Hierarchy

```
invariance
  +-- random
  |     Allocates 1000 (or 100 on VKSC) random buffers/images,
  |     records reference sizes, shuffles allocation order,
  |     re-allocates, and verifies sizes match.
  +-- memory_requirements_matching
  |     Verifies alignment consistency across identical create infos,
  |     and that vkGetDevice*MemoryRequirements matches
  |     vkGet*MemoryRequirements2.
  +-- memory_dedicated_requirements_matching
        Same as memory_requirements_matching but also verifies
        VkMemoryDedicatedRequirements consistency between
        vkGet*MemoryRequirements2 and vkGetDevice*MemoryRequirements.
```

## Test Families

### random (TT_BASIC_INVARIANCE)

Allocates `testCycles` (1000 on non-VKSC, 100 on VKSC) random buffer and image objects, records their memory requirement sizes, deallocates them, shuffles the allocation order, re-allocates in the new order, and verifies that each object reports the same size as before. Uses random buffer sizes, usage flags, image formats, tiling modes, and memory requirement types.

- Instance class: `InvarianceInstance` at [L244](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L244)
- Core logic in `iterate()` at [L264](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L264)
- Seed: `0x600613` at [L751](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L751)

### memory_requirements_matching (TT_REQUIREMENTS_MATCHING)

Creates a base image and buffer, then creates 5 additional objects with identical create infos and verifies that alignment values match. If `VK_KHR_get_memory_requirements2` is supported, also verifies that `vkGetDeviceBufferMemoryRequirements`/`vkGetDeviceImageMemoryRequirements` report the same requirements as `vkGetBufferMemoryRequirements2`/`vkGetImageMemoryRequirements2`. Additionally verifies that larger images/buffers never report smaller size requirements.

- Instance class: `AlignmentMatchingInstance` at [L435](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L435)
- Core logic in `iterate()` at [L452](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L452)
- Requires `VK_KHR_maintenance4` at [L757](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L757)

### memory_dedicated_requirements_matching (TT_DEDICATED_REQUIREMENTS)

Extends `memory_requirements_matching` by also verifying that `VkMemoryDedicatedRequirements` (prefersDedicatedAllocation, requiresDedicatedAllocation) are consistent between `vkGetBufferMemoryRequirements2`/`vkGetImageMemoryRequirements2` and `vkGetDeviceBufferMemoryRequirements`/`vkGetDeviceImageMemoryRequirements`.

- Same instance class as above, distinguished by `TT_DEDICATED_REQUIREMENTS` test type
- Dedicated requirements checks at [L576](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L576) (buffer) and [L637](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L637) (image)
- Requires `VK_KHR_maintenance4` at [L757](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L757)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| testCycles | 1000 (non-VKSC), 100 (VKSC) | [L41](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L41) |
| Random buffer size | 7..1030 | [L105](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L105) |
| Buffer usage flags | 1 << (0..8) | [L107](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L107) |
| Memory requirement types | 11 legal combinations | [L55](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L55) |
| Image tiling | LINEAR or OPTIMAL (random) | [L178](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L178) |
| Image dimensions | 3..18 (aligned for YCbCr/PVRTC) | [L189](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L189) |
| Alignment test objects | 5 | [L457](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L457) |
| Base image extent | 32x31 | [L459](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L459) |
| Base buffer size | 1023 | [L460](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L460) |

## Support / Feature Requirements

| Requirement | Gate | Location |
|-------------|------|----------|
| VK_KHR_maintenance4 | Required for `memory_requirements_matching` and `memory_dedicated_requirements_matching` | [L757](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L757) |
| VK_KHR_dedicated_allocation | Used in random test for dedicated allocation selection | [L272](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L272) |
| VK_KHR_sampler_ycbcr_conversion | Filters out YCbCr formats if unsupported | [L273](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L273) |
| VK_EXT_ycbcr_2plane_444_formats | Filters out extension formats if unsupported | [L274](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L274) |
| VK_IMG_format_pvrtc | Filters out PVRTC formats if unsupported | [L275](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L275) |
| VK_KHR_maintenance5 | Filters out A8_UNORM_KHR and A1B5G5R5_UNORM_PACK16_KHR if unsupported | [L277](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L277) |

## Verification Methods

- **Size invariance**: `val == refSizes[order[i]]` at [L414](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L414)
- **Alignment consistency**: `baseImageRequirements.alignment == imageRequirements.alignment` at [L511](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L511)
- **Device API equivalence**: `areRequirementsTheSame(requirements2[0], requirements2[1])` comparing `vkGet*MemoryRequirements2` vs `vkGetDevice*MemoryRequirements` at [L565](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L565)
- **Dedicated requirements consistency**: `dedicatedRequirements1.prefersDedicatedAllocation == dedicatedRequirements2.prefersDedicatedAllocation` at [L606](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L606)
- **Size monotonicity**: `baseImageRequirements.size <= imageRequirements.size` for larger extents at [L700](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L700)

## Test Principles Observed

- **Invariance**: Memory requirements must not change based on allocation order
- **API equivalence**: Device-level queries must match object-level queries
- **Monotonicity**: Larger create-info parameters must not yield smaller size requirements
- **Randomized stress**: Broad random coverage of formats, sizes, and memory types

## Notes / Uncertainties

- The `legalMemoryTypes` array at [L55](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L55) enumerates 11 valid `MemoryRequirement` combinations per spec chapter 10.2, but the matching logic at [L329](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L329) uses `matchesHeap()` which may not exactly correspond to Vulkan memory type property flags.
- The `VK_KHR_get_memory_requirements2` check at [L528](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L528) gates the device-level query tests, but this extension is core in Vulkan 1.1, so it is virtually always available.
- The `AlignmentMatchingInstance` test for `TT_DEDICATED_REQUIREMENTS` sets sentinel values (2 and 3) for `prefersDedicatedAllocation`/`requiresDedicatedAllocation` at [L579](../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L579) to detect whether the implementation overwrites them, which is a clever validation technique.
