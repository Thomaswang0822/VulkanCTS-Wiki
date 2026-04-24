# [vktApiPerformanceCountersByRegionTests.cpp](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1)

## Overview

Tests the `VK_ARM_performance_counters_by_region` extension, specifically the `vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM` API. Validates correct enumeration behavior including partial count queries, VK_INCOMPLETE return codes, and that the implementation does not overwrite memory beyond the requested counter count.

## Role of File

Implementation-heavy. Contains a single test case class with a full test instance that exercises the enumeration API with various buffer sizes and validates counter/description output integrity.

## Source Code

- Implementation: [vktApiPerformanceCountersByRegionTests.cpp](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L1)
- Header: [vktApiPerformanceCountersByRegionTests.hpp](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.hpp#L1)
- Parent registration: `createRenderPassPerformanceCountersByRegionApiTests()` declared at [L32](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.hpp#L32)

## Registration Path

```
api
  +-- render_pass_performance_counters_by_region   (non-VKSC only)
        +-- performance_counters_by_region
              +-- enumerate_counters
```

## Test Hierarchy

```
performance_counters_by_region
  +-- enumerate_counters
        Enumerates performance counters by region with various
        buffer sizes: fewer than total, exact count, and more
        than needed. Validates return codes and data integrity.
```

## Test Families

### enumerate_counters

A single comprehensive test that exercises `vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM` in multiple scenarios:

1. **Partial count (count=1)**: Requests only 1 counter when more exist. Expects `VK_INCOMPLETE` return code and verifies only the requested number of counter structs were written. Tests counters only, descriptions only, and both together.

2. **Exact count**: Requests the exact number of available counters. Expects `VK_SUCCESS` and validates all counters/descriptions were written correctly.

3. **Oversized buffer**: Requests `count+1` entries. Expects `VK_SUCCESS`, the actual count returned unchanged, and that the extra entry was not overwritten.

- Test case class: `APIPerformanceCountersByRegionRenderPassBasicTestCase` at [L348](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L348)
- Test instance class: `PerformanceCountersByRegionRenderPassBasicTestInstance` at [L61](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L61)
- Core logic in `iterate()` at [L187](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L187)
- Counter validation in `checkCounterEnumeration()` at [L88](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L88)
- Description validation in `checkCounterDescEnumeration()` at [L107](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L107)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Queue family index | 0 | [L189](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L189) |
| Partial count | 1 | [L216](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L216) |
| Exact count | perfCounterCount | [L279](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L279) |
| Oversized count | perfCounterCount + 1 | [L329](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L329) |
| Dummy sentinel value | Dynamically computed to avoid collision | [L144](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L144) |

## Support / Feature Requirements

| Requirement | Gate | Location |
|-------------|------|----------|
| VK_ARM_performance_counters_by_region | `context.requireDeviceFunctionality()` | [L362](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L362) |
| VK_KHR_get_physical_device_properties2 | `context.requireInstanceFunctionality()` | [L363](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L363) |
| performanceCountersByRegion feature bit | Checked via `VkPhysicalDevicePerformanceCountersByRegionFeaturesARM` | [L373](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L373) |
| Non-VKSC build | Entire file guarded by `#ifndef CTS_USES_VULKANSC` | [L48](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L48) |

## Verification Methods

- **Partial enumeration**: Returns `VK_INCOMPLETE` when requested count is less than available at [L229](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L229)
- **Counter data integrity**: `perfCounters[idx].counterID != dummyValue` ensures the implementation wrote data into the requested slots at [L95](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L95)
- **No overwrite beyond count**: `perfCounters[count].counterID == dummyValue` ensures no data was written past the requested count at [L101](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L101)
- **Description data integrity**: Same pattern using `flags` field at [L114](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L114) and [L121](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L121)
- **Count consistency**: Returned count matches expected count at [L284](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L284)
- **Result collector**: Uses `tcu::ResultCollector` to accumulate multiple failures within a single test at [L75](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L75)

## Test Principles Observed

- **Boundary testing**: Tests with fewer, exact, and more buffer space than needed
- **No overwrite**: Verifies implementation does not write beyond the provided buffer
- **Return code correctness**: Validates VK_INCOMPLETE for partial queries and VK_SUCCESS for complete queries

## Notes / Uncertainties

- The test uses queue family index 0 at [L189](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L189) rather than the universal queue family index. This may not be a queue family that supports performance counters.
- The `findDummyValue()` function at [L144](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L144) searches downward from `UINT32_MAX` for a value not present in any counterID or flags field, which is used as a sentinel to detect overwrites. This assumes at least one value near UINT32_MAX is unused.
- The entire file is wrapped in `#ifndef CTS_USES_VULKANSC` at [L48](../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L48), making it a non-VKSC-only test.
- The test case class name `APIPerformanceCountersByRegionRenderPassBasicTestCase` contains "RenderPass" but the test does not actually use a render pass; it only tests the enumeration API.
