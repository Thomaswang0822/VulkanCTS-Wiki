# [vktApiDescriptorPoolTests.cpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1)

## Overview

[`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.descriptor_pool` subtree. It registers the six direct children documented in the default Vulkan mustpass under the `descriptor_pool` group, covering repeated reset cycles, repeated free-and-reset cycles, out-of-pool-memory behavior, and zero-pool-size creation. The same source file also contains two additional Vulkan SC-only registrations that are documented in prose rather than the parseable hierarchy because they are not present in [`api.txt`](../../../mustpass/main/vk-default/api.txt).

## Role of File

Implementation-heavy test file for the `api.descriptor_pool` subgroup. The registration entry point is [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L509-L540).

## Source Code

- Primary source: [vktApiDescriptorPoolTests.cpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L1)
- Header: [vktApiDescriptorPoolTests.hpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L115)

## Registration Hierarchy

```text
api.descriptor_pool
├── repeated_reset_short
├── repeated_reset_long
├── repeated_free_reset_short
├── repeated_free_reset_long
├── out_of_pool_memory
└── zero_pool_size_count
```

The confirmed Level-3 root is `api.descriptor_pool`, created by [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L509-L540) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L115). The exact direct children present in the default Vulkan validation target [`api.txt`](../../../mustpass/main/vk-default/api.txt) are `repeated_reset_short`, `repeated_reset_long`, `repeated_free_reset_short`, `repeated_free_reset_long`, `out_of_pool_memory`, and `zero_pool_size_count`. The same registration function also adds `repeated_free_no_reset_short` and `repeated_free_no_reset_long` under [`#ifdef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L531-L538); those SC-only cases are source-backed but intentionally kept out of the parseable hierarchy so [`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) can validate this page cleanly against the default mustpass target requested for this workflow.

## Test Families

### repeated_reset_short — Short repeated descriptor-pool reset cycle

Covers the `repeated_reset_short` direct child registered by [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L515-L517). It calls [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84-L172) with [`ResetDescriptorPoolTestParams(2U)`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L516-L517), allocating descriptor sets from a pool and resetting that pool twice to confirm resource recycling succeeds.

### repeated_reset_long — Long repeated descriptor-pool reset cycle

Covers the `repeated_reset_long` direct child registered at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L518-L520). It reuses [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84-L172) with the high-iteration count `numIterationsHigh`, defined as `4096` in [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L511-L520). In Vulkan SC mode, the helper reduces the per-iteration descriptor-set allocation count internally, but the registered long-form case still exercises the repeated-reset path extensively.

### repeated_free_reset_short — Short free-then-reset cycle

Covers the `repeated_free_reset_short` direct child registered at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L521-L523). This path again uses [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84-L172), but passes [`ResetDescriptorPoolTestParams(2U, true)`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L522-L523) so descriptor sets are freed with `vkFreeDescriptorSets` before the pool reset.

### repeated_free_reset_long — Long free-then-reset cycle

Covers the `repeated_free_reset_long` direct child registered at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L524-L526). It is the long-running variant of the same free-then-reset path, using [`ResetDescriptorPoolTestParams(numIterationsHigh, true)`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L525-L526) with the shared [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84-L172).

### out_of_pool_memory — Out-of-descriptor-pool resource exhaustion

Covers the `out_of_pool_memory` direct child registered by [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L527-L528). [`outOfPoolMemoryTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L174-L330) creates pools with intentionally insufficient capacity and attempts allocations that exceed descriptor-set count or descriptor availability, verifying `VK_ERROR_OUT_OF_POOL_MEMORY` behavior when the maintenance1 semantics are available.

### zero_pool_size_count — Descriptor pool with zero pool-size entries

Covers the `zero_pool_size_count` direct child registered at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L529-L530). [`zeroPoolSizeCount()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L331-L382) creates a descriptor pool with `maxSets = 1` and `poolSizeCount = 0`, then allocates and frees an empty descriptor set to demonstrate that this edge configuration is accepted.

### repeated_free_no_reset_short — Vulkan SC short free-without-reset cycle

This source-backed subgroup is conditionally registered only under [`#ifdef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L531-L534), so it is described here rather than listed in the parseable hierarchy validated against the default Vulkan mustpass. It uses [`noResetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L384-L507) with [`ResetDescriptorPoolTestParams(2U, true)`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L533-L534), allocating and freeing descriptor sets without pool reset and instead rebuilding device state between iterations.

### repeated_free_no_reset_long — Vulkan SC long free-without-reset cycle

This source-backed subgroup is likewise conditionally registered only for Vulkan SC in [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L536-L538). It reuses [`noResetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L384-L507) with [`ResetDescriptorPoolTestParams(200U, true)`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L537-L538), providing the extended SC-only stress case.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Default-mustpass direct child | `repeated_reset_short`, `repeated_reset_long`, `repeated_free_reset_short`, `repeated_free_reset_long`, `out_of_pool_memory`, `zero_pool_size_count` from [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L509-L530) |
| Additional Vulkan SC-only direct child | `repeated_free_no_reset_short`, `repeated_free_no_reset_long` under [`#ifdef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L531-L538) |
| Iteration count | `2U` for short reset/free cases at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L515-L523); `numIterationsHigh = 4096` for long reset/free cases at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L511-L526); `200U` for `repeated_free_no_reset_long` at [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L536-L538) |
| Free-before-reset behavior | `false` for repeated-reset cases and `true` for repeated-free-reset / no-reset cases via [`ResetDescriptorPoolTestParams`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L516-L526) and [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L533-L538) |
| Descriptor-set allocation count per iteration | `2048` by default, reduced to `100` for Vulkan SC inside [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L102-L107) |
| Pool creation flags | `0` and `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` selected in [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L117-L118) from the `freeDescriptorSets` parameter |
| Out-of-pool-memory failure pattern | pool exhaustion by set count, by binding-count descriptor usage, and by array-size descriptor usage in [`outOfPoolMemoryTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L218-L330) |
| Descriptor types swept in exhaustion test | `VK_DESCRIPTOR_TYPE_SAMPLER`, `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER`, `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE`, `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`, `VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER`, `VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER`, `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`, `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`, `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC`, `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC`, and `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` in [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L178-L189) |
| Zero-pool-size configuration | `maxSets = 1`, `poolSizeCount = 0`, empty layout binding set in [`zeroPoolSizeCount()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L338-L375) |

## Support / Feature Requirements

- the repeated reset/free cases use [`checkSupportFreeDescriptorSets()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L77-L82) as their support gate, which in Vulkan SC requires `recycleDescriptorSetMemory == VK_TRUE`
- [`outOfPoolMemoryTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L200-L204) additionally requires `VK_KHR_maintenance1` semantics through [`context.requireDeviceFunctionality()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L202-L202)
- the `repeated_free_no_reset_short` and `repeated_free_no_reset_long` direct children are omitted entirely outside Vulkan SC by [`#ifdef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L531-L538)
- Vulkan SC paths use custom object reservation and command-pool reservation structures during device creation in [`noResetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L398-L447)

## Verification Methods

The visible verification style is execution- and status-based rather than image comparison:

- repeated reset/free cases perform allocation, optional free, and pool reset operations repeatedly under [`resetDescriptorPoolTest()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84-L172), relying on successful completion without earlier failure
- the exhaustion test checks specific Vulkan result codes with [`VK_CHECK_RESULT`](../../../framework/vulkan/vkQueryUtil.hpp#L354-L355) at the call sites in [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L239-L244), [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L274-L279), and [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L317-L322)
- the zero-pool-size case verifies that descriptor-set allocation and free succeed through [`VK_CHECK`](../../../framework/vulkan/vkQueryUtil.hpp#L338-L339) call sites in [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L372-L377)
- both main helper paths return pass on successful completion via [`tcu::TestStatus::pass()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L171-L171) and [`vktApiDescriptorPoolTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L506-L506)

## Test Principles Observed

- Stress descriptor-pool lifecycle behavior by repeating allocation, free, and reset sequences many times.
- Separate ordinary reset-based recycling from Vulkan SC no-reset recycling by using different helper paths and conditional registration.
- Probe API error-code correctness with intentionally undersized descriptor pools that fail in different ways.
- Include an edge-case constructor scenario where a descriptor pool has zero pool-size entries but still supports an empty descriptor-set allocation.

## Notes / Uncertainties

- This normalization confirms the canonical Level-3 root as `api.descriptor_pool`, not a legacy `api -> descriptor_pool` sketch, because the canonical contract requires the category-qualified root from [`createDescriptorPoolTests()`](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L509-L540).
- The source file registers eight direct children in total, but only six appear in the parseable hierarchy because the two `repeated_free_no_reset_*` children are Vulkan SC-only and are not present in the default Vulkan mustpass file used by [`verify_registration_paths.py`](../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) for this workflow.
- The long reset/free cases are registered with `4096` iterations, but the helper reduces per-iteration descriptor-set counts rather than the iteration count itself for Vulkan SC in the inspected code.
- The inspected file demonstrates successful operation and explicit error-code checking, but it does not include independent leak-detection instrumentation beyond whether the repeated operations complete correctly.

