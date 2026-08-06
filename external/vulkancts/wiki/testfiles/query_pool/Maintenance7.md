## Overview

**Core question:** Does a timestamp query return a 32-bit value that agrees with its equivalent 64-bit value under the Vulkan rules for `VK_KHR_maintenance7`?

- The page covers the `maintenance7` test family implemented in [`vktQueryMaintenance7Tests.cpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L34-L42).
- The family contains two Vulkan-only test case leaves: `query_32b_wrap_required` and `query_32b_wrap_notrequired`.
- Each leaf writes one `VK_QUERY_TYPE_TIMESTAMP` query, reads it as both 32-bit and 64-bit data, and checks the relationship between the two results.
- The two leaves use the same command stream and differ in whether the `maintenance7` feature is enabled and which result relationship the test accepts.

## Background Knowledge

- `vkGetQueryPoolResults` returns query values as 32-bit values unless `VK_QUERY_RESULT_64_BIT` is set. For an unsigned query whose value exceeds the result width, Vulkan permits wrapping or saturation in the general case.
- `VK_KHR_maintenance7` removes that choice for an enabled `maintenance7` feature: the 32-bit result must equal the 32 least significant bits of the equivalent 64-bit result. This makes the two result widths comparable even when the timestamp has passed the 32-bit range.
- A queue family's `timestampValidBits` reports how many bits of timestamp values are valid. This test requires a universal queue with timestamps and accepts only values from 36 through 64, so the test exercises a device with a meaningful possibility of a 32-bit overflow while still allowing a full-width timestamp.

## Registration Hierarchy

```text
query_pool.maintenance7
├── query_32b_wrap_required
└── query_32b_wrap_notrequired
```

The `maintenance7` test family is attached by [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55), and its two test case leaves are created by [`createQueryMaintenance7Tests()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L228-L237). The dispatcher and implementation are enclosed by `#ifndef CTS_USES_VULKANSC`, so this family is absent from Vulkan SC.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| `maintenance7` feature state | enabled, disabled | Selects whether 32-bit wrapping is required or whether the legacy wrap-or-saturate behavior remains acceptable. | [`Maintenance7QueryFeatureTestCase`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L176-L225) |
| Query type | `VK_QUERY_TYPE_TIMESTAMP` | Produces the timestamp value compared at the two result widths. | [`VkQueryPoolCreateInfo`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L97-L104) |
| Query count | `1` | Keeps the comparison to one timestamp result. | [`VkQueryPoolCreateInfo`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L97-L104) |
| Timestamp stage | `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT` | Determines where the command records the timestamp; it does not create a second behavior variant. | [`cmdWriteTimestamp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L110-L114) |
| Queue timestamp width | `36..64` valid bits | Ensures the selected universal queue exposes the timestamp width required by this test. | [`checkValidBits`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L58-L85) |

## Behavior Parameters

The primary behavioral axis is the `maintenance7` feature state. The query type, count, stage, and queue-width range are fixed setup parameters.

### `query_32b_wrap_required`: feature enabled

The test requests `VK_KHR_maintenance7` and the `maintenance7` feature bit. With the feature enabled, Vulkan requires the 32-bit unsigned query result to equal the low 32 bits of the equivalent 64-bit result:

```text
uint32_result == (uint64_result & 0xFFFFFFFF)
```

The test fails if the implementation saturates the 32-bit result or returns any other value.

### `query_32b_wrap_notrequired`: feature disabled

The test still requires the `VK_KHR_maintenance7` device functionality, but it does not request or enable the `maintenance7` feature. Without the feature, the general query-results rule allows an overflowing unsigned result to wrap or saturate. The test therefore accepts either:

- `uint32_result == (uint64_result & 0xFFFFFFFF)`; or
- `uint64_result > 0xFFFFFFFF` and `uint32_result == 0xFFFFFFFF`.

The registered spelling is `query_32b_wrap_notrequired`; it is not normalized to `query_32b_wrap_not_required`.

## Shader Analysis

No shader code participates in this test. The device-side work is a timestamp write recorded in a command buffer.

## Runtime Execution and Result Checking

- During instance construction, [`recordComands()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L87-L115) checks the universal queue's `timestampValidBits`, creates a one-slot timestamp query pool, allocates a transient command pool and primary command buffer, and records `vkCmdResetQueryPool` followed by `vkCmdWriteTimestamp` at `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT`.
- The test submits that command buffer to the universal queue and waits for completion with [`submitCommandsAndWait`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L121-L138).
- It calls `vkGetQueryPoolResults` once into a `uint32_t` with `VK_QUERY_RESULT_WAIT_BIT`, then once into a `uint64_t` with `VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT`.
- Each API call requests one result with a stride equal to its destination value's size. `VK_CHECK` makes an API error fail the test before the value comparison.
- With `maintenance7` enabled, the exact validation is `(tsGet64Bits & 0xFFFFFFFF) == tsGet32Bits`.
- With `maintenance7` disabled, the exact validation is the low-32-bit equality above **or** `(tsGet64Bits > 0xFFFFFFFF && tsGet32Bits == 0xFFFFFFFF)`.

The Vulkan query-results specification states that `VK_QUERY_RESULT_64_BIT` selects 64-bit result arrays; otherwise results use 32-bit values. It also states that an overflowing unsigned query may wrap or saturate, then adds the `maintenance7` requirement that the 32-bit value equal the 32 least significant bits of the equivalent 64-bit value. See [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#L1272-L1291) and the [`maintenance7` feature description](../../../../vulkan-docs/src/chapters/features.adoc#L6903-L6937).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `query_32b_wrap_required` | The device's 32-bit timestamp result does not equal the low 32 bits of its 64-bit result when `maintenance7` is enabled; or query-result retrieval returned a Vulkan error. |
| `query_32b_wrap_notrequired` | The device's 32-bit timestamp result is neither the low 32 bits of the 64-bit result nor the permitted saturated `0xFFFFFFFF` value for a 64-bit result above the 32-bit range; or query-result retrieval returned a Vulkan error. |
| Common setup | The universal queue lacks timestamp support, or its `timestampValidBits` is outside the source-enforced range `36..64`. |

### Cause Analysis

#### Timestamp-width relationship violates the selected rule

**Possible failure symptoms:** The test logs a maintenance7-specific mismatch and returns `Fail` because the two retrieved values do not satisfy the selected comparison. With the feature enabled, saturation is not accepted. With it disabled, a non-overflowing mismatch and an overflowing result other than low-bit wrap or `0xFFFFFFFF` fail.

**Possible implementation causes:** The result-width conversion or query-result path does not implement the Vulkan rule selected by the feature state. The exact failing layer needs source-level investigation; this test does not identify whether the discrepancy originates in query storage, conversion, or result retrieval.

#### Query result retrieval fails

**Possible failure symptoms:** `VK_CHECK` fails one of the two `vkGetQueryPoolResults` calls, so the test cannot compare the values.

**Possible implementation causes:** The implementation returned an error for a completed one-slot timestamp query under one of the requested result widths or flags. The specific cause needs source-level investigation.

#### Timestamp support is unavailable or outside the tested range

**Possible failure symptoms:** The case is pruned as unsupported when the universal queue reports `timestampValidBits == 0`; instance setup fails with `TCU_FAIL` when the value is below `36` or above `64`.

**Possible implementation causes:** The selected queue family does not expose timestamps, or the reported valid-bit count does not meet this test's required range. This is a support/setup condition rather than evidence of a 32-bit wrapping failure.

## Case Pruning

- Both leaves require the `VK_KHR_maintenance7` device functionality. A device that does not expose the extension skips both cases through [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L185-L202).
- `query_32b_wrap_required` additionally requires the `maintenance7` feature bit. If the feature is unsupported, CTS prunes that leaf with `NotSupportedError`; this means the device cannot run the feature-enabled variant, not that it failed the wrapping rule.
- Both leaves require a universal queue with `timestampValidBits > 0`. A queue without timestamp support is pruned.
- The implementation then requires `timestampValidBits` in `36..64`. A value outside that range triggers an instance setup failure rather than a normal pass/fail comparison.
- The complete `maintenance7` family is compiled and registered only for Vulkan, not Vulkan SC, because the parent registration and implementation are guarded by `#ifndef CTS_USES_VULKANSC`.

The current mustpass list contains both executable leaves in [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt#L47-L48):

```text
dEQP-VK.query_pool.maintenance7.query_32b_wrap_notrequired
dEQP-VK.query_pool.maintenance7.query_32b_wrap_required
```

## Key Takeaways

- `VK_KHR_maintenance7` changes the 32-bit unsigned query-result contract from the general wrap-or-saturate choice to mandatory low-32-bit wrapping when `maintenance7` is enabled.
- The CTS test reads one completed timestamp at both widths and applies that contract directly.
- The feature-disabled leaf accepts both behaviors because the pre-maintenance7 rule permits either one.
- Unsupported extension, feature, queue, or timestamp-width conditions prune or stop setup; they do not represent a failed timestamp comparison.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Query-family registration | [`vktQueryPoolTests.cpp#L42-L55`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55) |
| Test case construction | [`vktQueryMaintenance7Tests.cpp#L228-L237`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L228-L237) |
| Support and capability setup | [`vktQueryMaintenance7Tests.cpp#L176-L225`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L176-L225) |
| Timestamp setup and command recording | [`vktQueryMaintenance7Tests.cpp#L58-L115`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L58-L115) |
| Result retrieval and validation | [`vktQueryMaintenance7Tests.cpp#L121-L173`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L121-L173) |
| Vulkan query result width and overflow rules | [`queries.adoc#L1272-L1291`](../../../../vulkan-docs/src/chapters/queries.adoc#L1272-L1291) |
| `maintenance7` feature semantics | [`features.adoc#L6903-L6937`](../../../../vulkan-docs/src/chapters/features.adoc#L6903-L6937) |
| Mustpass coverage | [`query-pool.txt#L47-L48`](../../../mustpass/main/vk-default/query-pool.txt#L47-L48) |
