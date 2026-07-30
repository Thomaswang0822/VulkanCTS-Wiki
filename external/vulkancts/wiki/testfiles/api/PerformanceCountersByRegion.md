## Overview

**Core question:** does `vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM` obey the standard Vulkan two-call enumeration contract, writing only as many entries as the buffer can hold, returning `VK_INCOMPLETE` when the buffer is too small, and never writing past the requested count?

- Covers the `api.performance_counters_by_region` test family, which exercises the `VK_ARM_performance_counters_by_region` extension's instance-level enumeration entry point.
- Implements one test case leaf, `enumerate_counters`, in `vktApiPerformanceCountersByRegionTests.cpp`.
- Drives internal variation across three buffer sizes (fewer than, equal to, and greater than the total counter count) and three output combinations (counters only, descriptions only, both) on top of the single registered leaf.
- The page describes what the test verifies, how it detects out-of-bounds writes via a sentinel value, what each failure message means, and which feature gates and pruning rules apply.
- `#ifndef CTS_USES_VULKANSC` excludes the test from VulkanSC builds.

## Background Knowledge

- `VK_ARM_performance_counters_by_region`: Arm-only extension that exposes performance counters partitioned by render-pass region. The CTS test exercises only the enumeration entry point; it does not collect or read counter values during rendering.
- Two-call enumeration pattern: standard Vulkan contract for variable-length results. The first call with a NULL output returns the total count; the second call with a non-NULL output writes up to `*pCount` elements and updates `*pCount` with the number actually written. When the buffer is smaller than the total, the result must be `VK_INCOMPLETE` instead of `VK_SUCCESS`.
- `vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM`: the entry point under test. It writes both `VkPerformanceCounterARM` and `VkPerformanceCounterDescriptionARM` arrays in a single call, scoped to one queue family. Counters and descriptions can be requested independently or together by passing either, both, or neither array.

## Registration Hierarchy

```text
api.performance_counters_by_region
└── enumerate_counters
```

The `performance_counters_by_region` test family is created in `createRenderPassPerformanceCountersByRegionApiTests` and added to the `api` test category by `vktApiTests.cpp#L140`. The single test case leaf `enumerate_counters` is constructed by `APIPerformanceCountersByRegionRenderPassBasicTestCase` at `vktApiPerformanceCountersByRegionTests.cpp#L348-L381`.

## Parameter Dimensions and Observed Values

| Dimension | Values | Meaning in this test | Evidence |
|-----------|--------|----------------------|----------|
| Buffer size | `1`, `perfCounterCount`, `perfCounterCount + 1` | Verifies the partial-buffer case (`VK_INCOMPLETE`, no overrun past index 0), the exact-fit case (all counters written, no overrun past the requested count), and the oversized case (the implementation must not invent extra counters or write past the real count). | [vktApiPerformanceCountersByRegionTests.cpp#L212-L343](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L212-L343) |
| Output type | counters only, descriptions only, both | Each buffer size is exercised against each output combination to verify the same enumeration contract applies regardless of which array is populated. | [vktApiPerformanceCountersByRegionTests.cpp#L213-L343](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L213-L343) |
| Queue family | `0` | Fixed queue-family index passed to the entry point by the main test calls. Other queue families are not iterated. | [vktApiPerformanceCountersByRegionTests.cpp#L189](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L189) |

## Behavior Parameters

The primary behavioral axis is the test case leaf `enumerate_counters`. There is only one registered value for this axis, and the meaningful variation is driven by the internal buffer-size and output-type loops documented above. Because the registered axis has a single value, no per-value subsections are needed; the same enumeration contract is exercised in every iteration, and the failure analysis below applies uniformly across all internal variations.

## Shader Analysis

No shader is involved. The test verifies host-side behavior of an instance-level Vulkan entry point and never submits GPU work to a queue.

## Runtime Execution and Result Checking

- **Initial count probe.** The test calls `enumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM` with `queueFamilyIndex = 0`, a pointer to `perfCounterCount`, and NULL output buffers to obtain the total counter count. If `perfCounterCount == 0`, the test fails immediately with the message `"No counters found."` and returns. ([vktApiPerformanceCountersByRegionTests.cpp#L191-L204](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L191-L204))
- **Buffer allocation.** The test allocates two vectors sized `perfCounterCount + 1`: one of `VkPerformanceCounterARM` and one of `VkPerformanceCounterDescriptionARM`. The extra element is the sentinel slot used to detect out-of-bounds writes. ([vktApiPerformanceCountersByRegionTests.cpp#L206-L207](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L206-L207))
- **Dummy value selection.** `findDummyValue` calls the entry point with the full buffers, then walks downward from `UINT32_MAX` and stops at the first value that does not appear in any `counterID` or `flags` field. That value is the sentinel for the rest of the test. The assertion `dummyValue != 0u` ensures a usable sentinel was found. ([vktApiPerformanceCountersByRegionTests.cpp#L144-L185](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L144-L185))
- **Buffer reset.** Before every enumerated call, `resetCounters` rewrites every slot's `counterID` and `flags` (and zero-initializes the first `name` byte) to the dummy value, so the post-call check can compare each slot against the sentinel. ([vktApiPerformanceCountersByRegionTests.cpp#L127-L142](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L127-L142))
- **Undersized buffer test (only when `perfCounterCount > 1`).** The test runs three calls with `count = 1` (counters only, descriptions only, both). For each call, it requires the result to be `VK_INCOMPLETE`, the updated `count` to be no larger than `1`, the entry at index `0` to contain a real value (not the dummy), and the sentinel at index `1` to be untouched. ([vktApiPerformanceCountersByRegionTests.cpp#L212-L274](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L212-L274))
- **Exact-fit buffer test.** The test runs three calls with `count = perfCounterCount` (counters only, descriptions only, both). For each call, it requires the result to be `VK_SUCCESS`, the updated `count` to equal `perfCounterCount`, every entry up to index `perfCounterCount - 1` to be written with a real value, and the sentinel at index `perfCounterCount` to be untouched. ([vktApiPerformanceCountersByRegionTests.cpp#L277-L325](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L277-L325))
- **Oversized buffer test.** The test runs one call with `count = perfCounterCount + 1` and both arrays populated. It requires the result to be `VK_SUCCESS`, the updated `count` to equal `perfCounterCount` (the implementation must not invent extra counters), and the sentinel at index `perfCounterCount` to be untouched. ([vktApiPerformanceCountersByRegionTests.cpp#L327-L343](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L327-L343))
- **Result aggregation.** A `tcu::ResultCollector` aggregates all failures; the test returns the collector's result and message as the final test status. ([vktApiPerformanceCountersByRegionTests.cpp#L345-L346](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L345-L346))

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `enumerate_counters` | Buffer overrun or underrun on enumeration; incorrect result code for partial buffers; returned count inconsistent with the real counter set; counter set empty when extension support is reported. |

### Cause Analysis

#### Buffer overrun or underrun on enumeration

**Possible failure symptoms:** `"Counters beyond the requested limit were overwritten."` (counter array), `"Counter descriptions beyond the requested limit were overwritten."` (description array), `"Too few counters were written."`, or `"Too few counter descriptions were written."` `checkCounterEnumeration` and `checkCounterDescEnumeration` emit these messages when the sentinel slot at index `count` is no longer the dummy value, or when a slot inside the requested range still contains the dummy value after the call.

**Possible implementation causes:** The implementation wrote past `*pCount` elements, or did not write all `*pCount` elements it reported. The standard Vulkan two-call enumeration contract requires writing at most `*pCount` entries and touching no caller-owned memory beyond that range. Source-level investigation is needed to attribute the violation to a specific driver, ICD, or layer; the test only proves the contract was breached.

#### Incorrect result code for partial buffers

**Possible failure symptoms:** `"Expected VK_INCOMPLETE."` emitted when the test requested fewer slots than the implementation had reported.

**Possible implementation causes:** The entry point returned a value other than `VK_INCOMPLETE` (typically `VK_SUCCESS`) for an undersized buffer. Vulkan return-code semantics for enumeration entry points require `VK_INCOMPLETE` when the output buffer cannot hold all available items. Source-level investigation is needed to determine which layer returned the wrong code.

#### Returned count inconsistent with the real counter set

**Possible failure symptoms:** `"Unexpected count when requesting few counters."` (undersized case), or `"Unexpected number of performance counters returned."` (exact-fit and oversized cases).

**Possible implementation causes:** The implementation updated `*pCount` to a value inconsistent with the requested buffer size or with the total counter count discovered during the initial probe. For the undersized case, the implementation must report `count` no greater than `1` when asked for one slot (the test fails only when `count > 1`). For the exact-fit and oversized cases, the implementation must report exactly `perfCounterCount`. A mismatch suggests the implementation is miscounting, or returning a stale or computed value rather than the true device counter count. Source-level investigation is needed to attribute the bug to a specific driver path.

#### Counter set empty when extension support is reported

**Possible failure symptoms:** `"No counters found."` emitted on the very first probe, before any sentinel logic runs.

**Possible implementation causes:** The device reports support for `VK_ARM_performance_counters_by_region` (and `VkPhysicalDevicePerformanceCountersByRegionFeaturesARM::performanceCountersByRegion` is `VK_TRUE`), but the entry point returns zero counters for queue family `0`. This could mean the device exposes no counters for queue family `0`, or the implementation failed to populate the array. Source-level investigation is needed to determine whether queue family `0` is the correct queue family to query on the device under test; the test does not iterate other queue families.

## Case Pruning

### Requirement-based pruning

- `VK_ARM_performance_counters_by_region` must be supported by the device. `checkSupport` calls `requireDeviceFunctionality("VK_ARM_performance_counters_by_region")`; without it, the test case throws `NotSupportedError`. ([vktApiPerformanceCountersByRegionTests.cpp#L362](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L362))
- `VK_KHR_get_physical_device_properties2` must be supported at instance level. ([vktApiPerformanceCountersByRegionTests.cpp#L363](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L363))
- `VkPhysicalDevicePerformanceCountersByRegionFeaturesARM::performanceCountersByRegion` must be `VK_TRUE`. If the feature bit is `VK_FALSE`, the test throws `NotSupportedError`. ([vktApiPerformanceCountersByRegionTests.cpp#L366-L374](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L366-L374))
- `#ifndef CTS_USES_VULKANSC` excludes the source file from VulkanSC builds. ([vktApiPerformanceCountersByRegionTests.cpp#L48](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L48))

### Design-based pruning

- The undersized-buffer sub-case (`count = 1`) is only executed when `perfCounterCount > 1`. If the device exposes exactly one counter, that sub-case is skipped because there is no underrun to test against. ([vktApiPerformanceCountersByRegionTests.cpp#L212](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L212))
- The main test calls only exercise queue family `0` and do not iterate other queue families. ([vktApiPerformanceCountersByRegionTests.cpp#L189](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L189))
- The oversized-buffer case only exercises the both-arrays variant; the counters-only and descriptions-only variants would duplicate the exact-fit overwrite check already covered for those arrays. ([vktApiPerformanceCountersByRegionTests.cpp#L327-L343](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L327-L343))
- The test inspects only the `counterID` field of `VkPerformanceCounterARM` and the `flags` field of `VkPerformanceCounterDescriptionARM`. Beyond zeroing `name[0]` as part of the sentinel reset, the test does not validate the `name` field of `VkPerformanceCounterDescriptionARM` (the only other non-`sType`/`pNext` field on these ARM structs).

## Key Takeaways

- The test exercises the standard Vulkan two-call enumeration contract on `vkEnumeratePhysicalDeviceQueueFamilyPerformanceCountersByRegionARM`, not the act of collecting or reading counter values during rendering.
- Three buffer sizes (fewer, exact, more) are combined with three output combinations (counters only, descriptions only, both) to verify the contract holds regardless of which arrays are requested.
- A dummy-value sentinel in the slot just past the requested count detects buffer overruns; an untouched sentinel means no overrun occurred.
- `VK_INCOMPLETE` is required for the undersized case; `VK_SUCCESS` with the original `perfCounterCount` restored is required for the exact-fit and oversized cases.
- The test is gated by `VK_ARM_performance_counters_by_region` device extension support, `VK_KHR_get_physical_device_properties2` instance extension support, and the `performanceCountersByRegion` feature bit, and is excluded from VulkanSC builds.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `PerformanceCountersByRegionRenderPassBasicTestInstance::iterate` | [vktApiPerformanceCountersByRegionTests.cpp#L187-L346](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L187-L346) | Main test body: probes the count, allocates buffers, runs all buffer-size and output-type combinations, aggregates failures. |
| `checkCounterEnumeration` | [vktApiPerformanceCountersByRegionTests.cpp#L88-L105](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L88-L105) | Validates the counter array: every slot in range was written, and the sentinel slot was not overwritten. |
| `checkCounterDescEnumeration` | [vktApiPerformanceCountersByRegionTests.cpp#L107-L125](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L107-L125) | Same validation for the description array, keyed on the `flags` field. |
| `findDummyValue` | [vktApiPerformanceCountersByRegionTests.cpp#L144-L185](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L144-L185) | Walks down from `UINT32_MAX` to find a sentinel value that does not appear in any `counterID` or `flags` field. Note: this helper queries `context.getUniversalQueueFamilyIndex()`, separate from the `queueFamilyIndex = 0` used by the main test calls. |
| `resetCounters` | [vktApiPerformanceCountersByRegionTests.cpp#L127-L142](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L127-L142) | Resets every slot to the dummy value before each enumerated call so the sentinel can detect overruns. |
| `APIPerformanceCountersByRegionRenderPassBasicTestCase::checkSupport` | [vktApiPerformanceCountersByRegionTests.cpp#L357-L375](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L357-L375) | Gates the test on the device extension, instance extension, and `performanceCountersByRegion` feature bit. |
| `createRenderPassPerformanceCountersByRegionApiTests` | [vktApiPerformanceCountersByRegionTests.cpp#L385-L392](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.cpp#L385-L392) | Registers the `performance_counters_by_region` test family and adds the `enumerate_counters` test case. |
| Parent registration in `api` test category | [vktApiTests.cpp#L140](../../../modules/vulkan/api/vktApiTests.cpp#L140) | Adds the `performance_counters_by_region` group to the `api` test category, guarded by `#ifndef CTS_USES_VULKANSC`. |
| Header declaration | [vktApiPerformanceCountersByRegionTests.hpp](../../../modules/vulkan/api/vktApiPerformanceCountersByRegionTests.hpp) | Declares the factory `createRenderPassPerformanceCountersByRegionApiTests`. |
