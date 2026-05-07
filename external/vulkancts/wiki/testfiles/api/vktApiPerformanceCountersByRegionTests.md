# [vktApiPerformanceCountersByRegionTests.cpp](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1)

## Overview

Tests VK_ARM_performance_counters_by_region by verifying the `vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM` function. Checks that counter enumeration behaves correctly with various buffer sizes: fewer than total, exactly total, and more than total counters, and that the implementation does not overwrite memory beyond the requested count.

## Role of File

Implementation-heavy. Contains test instance, support utilities, and registration logic.

## Source Code

| File | Description |
|------|-------------|
| [vktApiPerformanceCountersByRegionTests.cpp](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1) | Test implementation and registration |
| [vktApiPerformanceCountersByRegionTests.hpp](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.hpp#L1) | Declares `createRenderPassPerformanceCountersByRegionApiTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L140) | Parent registration: `apiTests->addChild(createRenderPassPerformanceCountersByRegionApiTests(testCtx))` |

## Registration Path

```
api
  +-- performance_counters_by_region
       +-- enumerate_counters
```

## Test Hierarchy

```
performance_counters_by_region
  +-- enumerate_counters
       Tests vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM
       with various buffer sizes and output parameter combinations
```

## Test Families

### performance_counters_by_region

Group name verified at [vktApiPerformanceCountersByRegionTests.cpp:387](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L387): `new tcu::TestCaseGroup(testCtx, "performance_counters_by_region")`.

Single test case `enumerate_counters` at [line 389](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L389).

The test instance `PerformanceCountersByRegionRenderPassBasicTestInstance` at [line 61](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L61) performs these checks:

1. Queries the total counter count via `enumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM` with null output ([lines 197-198](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L197))
2. Finds a "dummy value" not present in any counter's counterID or flags, to use as a sentinel for overwrite detection ([lines 144-185](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L144))
3. If count > 1, tests with buffer size 1 (expects `VK_INCOMPLETE` and no overwrite beyond index 0) ([lines 213-274](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L213))
4. Tests with exact buffer size (expects all counters written, no overwrite beyond count) ([lines 278-325](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L278))
5. Tests with buffer size = count + 1 (expects all counters written, no overwrite beyond count) ([lines 329-343](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L329))

Each test is run with three output combinations: counters only, descriptions only, and both together.

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Buffer size | 1, perfCounterCount, perfCounterCount+1 | Only if count > 1 for size=1 |
| Output type | Counters only, descriptions only, both | 3 variants per buffer size |
| Queue family | 0 | Hard-coded at [line 189](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L189) |

## Support / Feature Requirements

- `VK_ARM_performance_counters_by_region` required ([line 362](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L362))
- `VK_KHR_get_physical_device_properties2` required ([line 363](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L363))
- `VkPhysicalDevicePerformanceCountersByRegionFeaturesARM::performanceCountersByRegion` must be VK_TRUE ([lines 366-374](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L366))
- Entire file is guarded by `#ifndef CTS_USES_VULKANSC` at [line 48](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L48)

## Verification Methods

- **Counter enumeration check**: Verifies that `counterID` fields are not equal to the dummy value for indices < count, and ARE equal to the dummy value at index = count (no overwrite) ([lines 88-105](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L88))
- **Description enumeration check**: Same pattern using `flags` field of `VkPerformanceCounterDescriptionARM` ([lines 107-125](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L107))
- **VK_INCOMPLETE check**: When requesting fewer counters than available, the result must be `VK_INCOMPLETE` ([lines 229-232](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L229))
- **Count consistency**: The returned count must match the expected value ([lines 284-287](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L284))

## Test Principles Observed

- Enumeration pattern testing: follows the standard Vulkan two-call enumeration pattern
- Buffer safety: verifies no out-of-bounds writes beyond the requested count
- Result code validation: checks for VK_INCOMPLETE when buffer is too small

## Notes / Uncertainties

- The factory function is named `createRenderPassPerformanceCountersByRegionApiTests` but the group name is `performance_counters_by_region`; the "renderpass" prefix in the function name appears to be a legacy artifact
- The test uses `queueFamilyIndex = 0` rather than the universal queue family index; this may not be a valid queue family for performance queries on all implementations
- The test passes if `perfCounterCount == 0` with a failure message "No counters found"
