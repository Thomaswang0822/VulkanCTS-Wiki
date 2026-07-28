## Overview

**Core question:** does the implementation correctly manage the descriptor-pool lifecycle (allocate, free, reset), return the expected error code when pool resources are exhausted, and accept the zero-pool-size edge configuration?

- Covers the `api.descriptor_pool` test family, registered by `createDescriptorPoolTests()` and attached to the `api` test category in `createApiTests()`.
- Implements six direct test case leaves in the default Vulkan mustpass: `repeated_reset_short`, `repeated_reset_long`, `repeated_free_reset_short`, `repeated_free_reset_long`, `out_of_pool_memory`, and `zero_pool_size_count`.
- Stresses descriptor-pool recycling through repeated allocate / free / reset cycles, probes `VK_ERROR_OUT_OF_POOL_MEMORY` semantics under intentionally undersized pools, and verifies a pool created with `poolSizeCount = 0` still services an empty descriptor set.
- Two additional Vulkan SC-only leaves (`repeated_free_no_reset_short`, `repeated_free_no_reset_long`) exist in source but are intentionally absent from the default mustpass validated here.

## Background Knowledge

- **Descriptor pool.** A `VkDescriptorPool` is a host-side allocation arena from which `VkDescriptorSet` objects are allocated via `vkAllocateDescriptorSets`. The pool is created with a `maxSets` limit and one or more `VkDescriptorPoolSize` entries that cap how many descriptors of each type the pool can hold in total.
- **Pool reset versus individual free.** `vkResetDescriptorPool` returns all descriptor sets allocated from the pool at once and recycles the underlying storage. Individual `vkFreeDescriptorSets` calls are only valid when the pool was created with `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT`; otherwise freeing individual sets is a usage error.
- **Out-of-pool-memory.** When `VK_KHR_maintenance1` is supported, `vkAllocateDescriptorSets` may return `VK_ERROR_OUT_OF_POOL_MEMORY` if the request exceeds the pool's `maxSets` limit or its per-type descriptor capacity. Without that extension, the implementation may return `VK_ERROR_OUT_OF_HOST_MEMORY` or `VK_ERROR_OUT_OF_DEVICE_MEMORY` instead, so the test only enforces the strict result code when the extension is present.

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

The two `repeated_free_no_reset_*` leaves registered under `#ifdef CTS_USES_VULKANSC` in `createDescriptorPoolTests()` are deliberately omitted from this tree because they are not present in the default Vulkan mustpass target `api.txt`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Iteration count | `2`, `4096` (`numIterationsHigh`), `200` (SC-only long no-reset) | Short cases sanity-check the path; long cases stress repeated recycling to expose leaks or state corruption. | [vktApiDescriptorPoolTests.cpp#L510](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L510), [vktApiDescriptorPoolTests.cpp#L536-L537](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L536-L537) |
| Free-before-reset behavior | `false`, `true` | `false` exercises reset-only recycling; `true` additionally calls `vkFreeDescriptorSets` before reset, which requires the `FREE_DESCRIPTOR_SET_BIT` pool flag. | [vktApiDescriptorPoolTests.cpp#L61-L71](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L61-L71), [vktApiDescriptorPoolTests.cpp#L102-L103](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L102-L103) |
| Descriptor sets per iteration | `2048` (default), `100` (Vulkan SC) | Bounds the per-iteration allocation pressure that the pool must recycle. | [vktApiDescriptorPoolTests.cpp#L86-L90](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L86-L90) |
| Pool creation flags | `0`, `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` | Selected from `m_freeDescriptorSets`; controls whether individual frees are permitted. | [vktApiDescriptorPoolTests.cpp#L102-L103](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L102-L103) |
| Out-of-pool exhaustion pattern | set-count, binding-count, array-size, array-size-across-bindings | Each pattern saturates a different pool capacity field to drive allocation failure. | [vktApiDescriptorPoolTests.cpp#L189-L232](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L189-L232) |
| Descriptor types swept in exhaustion test | all `VK_DESCRIPTOR_TYPE_*` from `SAMPLER` through `INPUT_ATTACHMENT` | Confirms the exhaustion contract holds uniformly across descriptor types. | [vktApiDescriptorPoolTests.cpp#L245-L246](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L245-L246) |
| Zero-pool-size configuration | `maxSets = 1`, `poolSizeCount = 0`, empty layout | Probes the edge case where a pool has no per-type capacity but still must accept an empty descriptor set. | [vktApiDescriptorPoolTests.cpp#L336-L354](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L336-L354) |

## Behavior Parameters

The primary behavioral axis is the test case leaf: each leaf exercises a distinct descriptor-pool mechanism, so the leaves themselves are the behavior choices.

### repeated_reset_short — short allocate-and-reset cycle

Calls `resetDescriptorPoolTest()` with `ResetDescriptorPoolTestParams(2U)`, performing two iterations of `vkAllocateDescriptorSets` for `2048` sampler descriptor sets followed by `vkResetDescriptorPool`. The pool is created without `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` because individual frees are not exercised. This is the minimal sanity check that pool recycling works at all. See [vktApiDescriptorPoolTests.cpp#L515-L516](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L515-L516).

### repeated_reset_long — long allocate-and-reset cycle

Same path as `repeated_reset_short` but with `numIterationsHigh = 4096` iterations. The higher count is intended to expose slow leaks or state corruption that a two-iteration run would miss; the source comment at [vktApiDescriptorPoolTests.cpp#L161](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L161) notes that the test should crash inside the loop if a leak exists. The watchdog is touched every `1024` iterations to avoid false timeout failure on slow implementations.

### repeated_free_reset_short — short free-then-reset cycle

Calls `resetDescriptorPoolTest()` with `ResetDescriptorPoolTestParams(2U, true)`. The `true` parameter selects `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` and inserts a `vkFreeDescriptorSets` call for the first allocated set before each `vkResetDescriptorPool`. This exercises the free-before-reset path that recycles individually freed sets in addition to the bulk reset. See [vktApiDescriptorPoolTests.cpp#L521-L522](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L521-L522).

### repeated_free_reset_long — long free-then-reset cycle

Long-running counterpart of `repeated_free_reset_short`, using `ResetDescriptorPoolTestParams(numIterationsHigh, true)` for `4096` iterations of allocate / free / reset. The free-before-reset path is exercised under sustained pressure. See [vktApiDescriptorPoolTests.cpp#L524-L525](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L524-L525).

### out_of_pool_memory — exhaustion error-code contract

`outOfPoolMemoryTest()` constructs five `FailureCase` configurations whose pool capacity is intentionally too small for the requested allocation, sweeps all `VkDescriptorType` values for each configuration, and inspects the `VkResult` returned by `vkAllocateDescriptorSets`. When `VK_KHR_maintenance1` is supported, a non-success result must be exactly `VK_ERROR_OUT_OF_POOL_MEMORY`; otherwise the implementation is permitted to return any non-success code and the case passes as long as at least one allocation failed. See [vktApiDescriptorPoolTests.cpp#L527](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L527) and the case table at [vktApiDescriptorPoolTests.cpp#L189-L232](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L189-L232).

### zero_pool_size_count — zero-pool-size edge case

`zeroPoolSizeCount()` creates a pool with `maxSets = 1`, `poolSizeCount = 0`, and the `FREE_DESCRIPTOR_SET_BIT` flag, then allocates and frees one descriptor set backed by a layout with zero bindings. This verifies that a pool with no per-type capacity is still a legal object that services an empty descriptor set. See [vktApiDescriptorPoolTests.cpp#L529](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L529) and the implementation at [vktApiDescriptorPoolTests.cpp#L331-L381](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L331-L381).

## Shader Analysis

No shader is involved in this test family. Every leaf operates on host-side descriptor-pool objects and validates `VkResult` codes returned by `vkAllocateDescriptorSets`, `vkFreeDescriptorSets`, and `vkResetDescriptorPool`. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

- **Reset / free-reset cases.** `resetDescriptorPoolTest()` creates one `VkDescriptorPool` sized for `2048` sampler descriptor sets (or `100` on Vulkan SC) and `2048` matching descriptor-set layouts up front. The per-iteration body allocates all sets, optionally frees the first one when `m_freeDescriptorSets` is `true`, and then resets the pool. The watchdog is touched every `1024` iterations. See [vktApiDescriptorPoolTests.cpp#L94-L166](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L94-L166).
- **Pass condition for reset / free-reset cases.** Every `vkAllocateDescriptorSets`, `vkFreeDescriptorSets`, and `vkResetDescriptorPool` call must return `VK_SUCCESS` (enforced through `VK_CHECK` at [vktApiDescriptorPoolTests.cpp#L162-L165](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L162-L165)); on loop completion the case returns `pass`. The source comment at [vktApiDescriptorPoolTests.cpp#L161](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L161) documents that a memory leak is expected to surface as a crash inside this loop rather than as a returned failure status.
- **Out-of-pool-memory case.** `outOfPoolMemoryTest()` iterates five `FailureCase` rows; for each row it iterates every `VkDescriptorType` and calls `vkAllocateDescriptorSets` against an undersized pool. The result handling is at [vktApiDescriptorPoolTests.cpp#L308-L322](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L308-L322): a non-success result increments `numErrorsReturned`, and if `VK_KHR_maintenance1` is supported any non-success result other than `VK_ERROR_OUT_OF_POOL_MEMORY` causes an immediate `fail`. A successful allocation is logged but does not fail the case.
- **Pass condition for out-of-pool-memory.** If at least one allocation returned a non-success result, the case passes with message `"Pass"`; otherwise it passes with `"Not validated"`. The case never returns `fail` from the per-allocation path unless the strict maintenance1 result-code check is violated. See [vktApiDescriptorPoolTests.cpp#L325-L328](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L325-L328).
- **Zero-pool-size case.** `zeroPoolSizeCount()` allocates one empty descriptor set and frees it back. Each call must return `VK_SUCCESS`; any other result produces a `fail` with the actual `VkResult` name embedded in the message. See [vktApiDescriptorPoolTests.cpp#L369-L378](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L369-L378).
- **No device-side work.** No queues, command buffers, semaphores, or barriers are involved. Every check is a host-side `VkResult` inspection.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `repeated_reset_short` | Allocation/free/reset API misuse by the implementation, or pool recycling state corruption visible at low iteration count. |
| `repeated_reset_long` | Per-iteration resource leak or state accumulation that only manifests under sustained recycling. |
| `repeated_free_reset_short` | Incorrect handling of individual `vkFreeDescriptorSets` before reset, including bookkeeping that breaks subsequent allocation. |
| `repeated_free_reset_long` | Leak or corruption that only manifests when free-before-reset is repeated many times. |
| `out_of_pool_memory` | Wrong `VkResult` returned when pool capacity is exceeded, or pool capacity bookkeeping that never reports exhaustion. |
| `zero_pool_size_count` | Rejection of a legal zero-`poolSizeCount` pool or failure to allocate an empty descriptor set from it. |

### Cause Analysis

#### Reset-cycle failure

**Possible failure symptoms:** `VK_CHECK` at [vktApiDescriptorPoolTests.cpp#L162-L165](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L162-L165) reports a non-`VK_SUCCESS` `VkResult` from `vkAllocateDescriptorSets`, `vkFreeDescriptorSets`, or `vkResetDescriptorPool`; or the process crashes inside the iteration loop.

**Possible implementation causes:** after the first reset, the implementation must return the previously allocated descriptor-set storage to a state that accepts a fresh `vkAllocateDescriptorSets` call of the same size. A driver that does not fully recycle internal pool storage on reset will eventually return `VK_ERROR_OUT_OF_POOL_MEMORY` or `VK_ERROR_OUT_OF_HOST_MEMORY`, or will overrun an internal accounting structure and crash. The source comment at [vktApiDescriptorPoolTests.cpp#L161](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L161) explicitly notes that a leak should crash the loop. Whether the failure surfaces at iteration `2` or only after thousands of iterations distinguishes a coarse recycling defect from a slow leak; source-level investigation of the driver's pool accounting is needed to identify the exact root cause in any specific failure.

#### Free-before-reset failure

**Possible failure symptoms:** Same `VK_CHECK` failure pattern as the reset-cycle case, but specifically triggered only when `m_freeDescriptorSets` is `true` (the `repeated_free_reset_*` leaves).

**Possible implementation causes:** with `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT` set, the implementation must maintain a free list or equivalent structure so that individually freed sets are reusable. If the free path corrupts that structure (for example, by returning the same slot twice or by not marking the slot as free), subsequent allocation can return the wrong handle, fail with `VK_ERROR_OUT_OF_POOL_MEMORY` despite pool capacity being available, or crash. The reset that follows must still recycle everything, including any sets not individually freed. Whether the symptom appears only in the long variant hints at slow free-list growth; source-level investigation is otherwise needed to localize the defect.

#### Out-of-pool-memory result-code failure

**Possible failure symptoms:** `outOfPoolMemoryTest()` returns `fail` with message `"Expected VK_ERROR_OUT_OF_POOL_MEMORY but got <actual> instead"` at [vktApiDescriptorPoolTests.cpp#L315-L317](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L315-L317), or the case returns `"Not validated"` because no allocation across any of the five `FailureCase` rows ever returned a non-success result.

**Possible implementation causes:** when `VK_KHR_maintenance1` is supported, the Vulkan contract requires `vkAllocateDescriptorSets` to return `VK_ERROR_OUT_OF_POOL_MEMORY` when the request exceeds pool capacity; returning `VK_ERROR_OUT_OF_HOST_MEMORY` or `VK_ERROR_OUT_OF_DEVICE_MEMORY` in that situation is non-conformant. A driver that silently over-allocates beyond the requested pool capacity would never report exhaustion and the case would end in `"Not validated"`. A driver that returns the wrong non-success code reveals incorrect error-code routing. Which `FailureCase` row triggers the symptom (set-count exhaustion at [vktApiDescriptorPoolTests.cpp#L192-L199](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L192-L199), binding-count at [vktApiDescriptorPoolTests.cpp#L208-L215](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L208-L215), or array-size at [vktApiDescriptorPoolTests.cpp#L216-L231](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L216-L231)) indicates which capacity field is mishandled; source-level investigation is required to pin the defect to a specific descriptor-type or pool-size code path.

#### Zero-pool-size rejection

**Possible failure symptoms:** `zeroPoolSizeCount()` returns `fail` with message `"Expected vkAllocateDescriptorSets to return VK_SUCCESS but got <actual> instead"` at [vktApiDescriptorPoolTests.cpp#L370-L372](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L370-L372), or the analogous message for `vkFreeDescriptorSets` at [vktApiDescriptorPoolTests.cpp#L375-L378](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L375-L378).

**Possible implementation causes:** the pool is created with `maxSets = 1` and `poolSizeCount = 0`, paired with a descriptor-set layout that has zero bindings. The Vulkan specification permits this configuration: an empty descriptor set consumes no per-type descriptors, so it must be allocatable from a pool whose `maxSets` is at least one even when no `VkDescriptorPoolSize` entries are supplied. A driver that rejects pool creation, rejects the allocation, or rejects the free in this configuration is enforcing a stricter invariant than the spec requires. Whether the symptom appears at pool creation, allocation, or free indicates where the implementation's validation is over-strict; source-level investigation is needed to confirm the exact cause.

## Case Pruning

### Requirement-based pruning

- The free-before-reset leaves (`repeated_free_reset_short`, `repeated_free_reset_long`) call `checkSupportFreeDescriptorSets()` as their support gate. On Vulkan SC, the gate throws `NotSupportedError` when `recycleDescriptorSetMemory == VK_FALSE`; on non-SC Vulkan it is a no-op because individual frees are always permitted when the pool flag is set. See [vktApiDescriptorPoolTests.cpp#L73-L82](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L73-L82).
- The strict result-code enforcement in `outOfPoolMemoryTest()` is gated on `VK_KHR_maintenance1` being supported, queried via `context.isDeviceFunctionalitySupported("VK_KHR_maintenance1")` at [vktApiDescriptorPoolTests.cpp#L178](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L178). Implementations without the extension still run the test but are not held to the `VK_ERROR_OUT_OF_POOL_MEMORY` exact-code contract.
- The two `repeated_free_no_reset_*` leaves are registered only under `#ifdef CTS_USES_VULKANSC` at [vktApiDescriptorPoolTests.cpp#L530-L538](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L530-L538) and are absent from the default Vulkan mustpass target.

### Design-based pruning

- The short/long split is a deliberate iteration-count matrix: short cases (`2` iterations) catch coarse defects quickly; long cases (`4096` iterations for reset/free-reset, `200` for the SC-only no-reset path) expose slow leaks and accumulation. There is no intermediate count because the matrix only needs the two extremes to bound the behavior.
- The `out_of_pool_memory` case sweeps every `VkDescriptorType` for every `FailureCase` row but does not cross-product with pool flags or layout variations; the contract being tested is per-type capacity accounting, not flag interactions.
- The `zero_pool_size_count` case is a single fixed configuration rather than a matrix; the edge case is narrow by design.
- The Vulkan SC-only `noResetDescriptorPoolTest()` path is intentionally separate from `resetDescriptorPoolTest()` because it rebuilds device state between iterations rather than relying on `vkResetDescriptorPool`, reflecting a different SC-specific recycling contract.

## Key Takeaways

- The `api.descriptor_pool` family verifies host-side descriptor-pool lifecycle contracts: allocation success on legal configurations, correct `VkResult` routing on exhaustion, and silent recycling on reset.
- The reset and free-reset leaves rely on a crash-or-`VK_CHECK` oracle rather than explicit leak detection; sustained-iteration runs are the primary mechanism for surfacing slow leaks.
- `out_of_pool_memory` only enforces the strict `VK_ERROR_OUT_OF_POOL_MEMORY` result code when `VK_KHR_maintenance1` is present; without the extension the case passes as long as some allocation fails, which respects the looser contract that pre-maintenance1 Vulkan permits.
- `zero_pool_size_count` confirms that `poolSizeCount = 0` with `maxSets >= 1` is a legal pool configuration for empty descriptor sets, which is a useful boundary for validation-layer and driver-internal invariant testing.
- See `## Failure Meaning` for the symptom-to-cause mapping for each leaf.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDescriptorPoolTests()` registration | [vktApiDescriptorPoolTests.cpp#L508-L541](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L508-L541) | Owns the test family registration; defines `numIterationsHigh = 4096` and the six default-mustpass leaves plus the two SC-only conditional leaves. |
| Parent registration in `createApiTests()` | [vktApiTests.cpp#L112](../../../modules/vulkan/api/vktApiTests.cpp#L112) | Attaches `descriptor_pool` to the `api` test category. |
| `ResetDescriptorPoolTestParams` struct | [vktApiDescriptorPoolTests.cpp#L61-L71](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L61-L71) | Carries the iteration count and free-before-reset flag that distinguish the four reset/free-reset leaves. |
| `checkSupportFreeDescriptorSets()` | [vktApiDescriptorPoolTests.cpp#L73-L82](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L73-L82) | Support gate for the free-before-reset leaves on Vulkan SC. |
| `resetDescriptorPoolTest()` | [vktApiDescriptorPoolTests.cpp#L84-L172](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L84-L172) | Implementation of the four reset/free-reset leaves; contains the per-iteration allocate / free / reset loop and the `VK_CHECK` oracle. |
| `outOfPoolMemoryTest()` | [vktApiDescriptorPoolTests.cpp#L174-L329](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L174-L329) | Implementation of the `out_of_pool_memory` leaf; defines the `FailureCase` table and the maintenance1-gated result-code check. |
| `FailureCase` table | [vktApiDescriptorPoolTests.cpp#L181-L232](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L181-L232) | Five exhaustion patterns: set-count, descriptors-by-set-count, descriptors-by-binding-count, descriptors-by-array-size, descriptors-by-array-size-across-bindings. |
| Result-code enforcement | [vktApiDescriptorPoolTests.cpp#L308-L328](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L308-L328) | Strict `VK_ERROR_OUT_OF_POOL_MEMORY` check under maintenance1 and final pass-condition logic. |
| `zeroPoolSizeCount()` | [vktApiDescriptorPoolTests.cpp#L331-L381](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L331-L381) | Implementation of the `zero_pool_size_count` leaf; creates the zero-`poolSizeCount` pool and verifies allocate/free of an empty set. |
| `noResetDescriptorPoolTest()` (Vulkan SC only) | [vktApiDescriptorPoolTests.cpp#L384-L503](../../../modules/vulkan/api/vktApiDescriptorPoolTests.cpp#L384-L503) | SC-only alternative recycling path that rebuilds device state instead of calling `vkResetDescriptorPool`. Documented for context; not part of the default mustpass validated here. |
| `VK_CHECK` macro definition | [vkDefs.hpp#L89](../../../framework/vulkan/vkDefs.hpp#L89) | Macro used by the reset/free-reset leaves to enforce `VK_SUCCESS` from each pool operation. |
| Mustpass entries | [api.txt](../../../mustpass/main/vk-default/api.txt) | Default Vulkan mustpass target listing the six `dEQP-VK.api.descriptor_pool.*` leaves. |
| Header | [vktApiDescriptorPoolTests.hpp](../../../modules/vulkan/api/vktApiDescriptorPoolTests.hpp) | Declares `createDescriptorPoolTests()`. |
