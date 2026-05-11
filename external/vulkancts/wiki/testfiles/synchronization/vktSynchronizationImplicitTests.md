# [vktSynchronizationImplicitTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L1)

## Overview

This file implements tests that verify implicit synchronization ordering guarantees when multiple `VkSubmitInfo` structures are submitted within a single `vkQueueSubmit` call on the same queue. Unlike explicit synchronization (where semaphores or barriers enforce ordering), these tests rely on the implicit ordering guarantees of the Vulkan submission model: within a single `vkQueueSubmit`, submit infos are processed in order, and signal operations in earlier submit infos complete before signal operations in later submit infos.

## Role of File

This file contributes the `implicit` group to **both** the `synchronization` (LEGACY) and `synchronization2` categories. The factory function [`createImplicitSyncTests()`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L757) takes a `SynchronizationType` parameter, and the same test logic is reused across both API paths via [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp).

## Source Code

| File | Description |
|------|-------------|
| [`vktSynchronizationImplicitTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L1) | Implementation |
| [`vktSynchronizationImplicitTests.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.hpp#L1) | Public header |

## Registration Hierarchy

```text
synchronization.implicit
├── binary_semaphore
└── timeline_semaphore
```

This file contributes the `implicit` group to **both** the `synchronization` (LEGACY) and `synchronization2` categories. The factory function [`createImplicitSyncTests()`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L757) takes a `SynchronizationType` parameter, and the same test logic is reused across both API paths via [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp). The tree structure is identical between both categories; only the `SynchronizationType` parameter differs. In the `synchronization2` category, the root path is `synchronization2.implicit`.

Below each direct child, the hierarchy continues as `<writeOp>_<readOp>` / `<resource>` / `<comboIndex>`, where `<comboIndex>` is a 4-digit string encoding the submit-info type permutation (see Test Families below).

## Test Families

### binary_semaphore -- Binary semaphore implicit synchronization

Tests implicit synchronization using binary semaphores (`VK_SEMAPHORE_TYPE_BINARY_KHR`). Each wait-signal pair uses its own dedicated semaphore.

Tests are registered under `synchronization.implicit.binary_semaphore` (LEGACY) and `synchronization2.implicit.binary_semaphore` (sync2).

**Hierarchy below this group**:

```text
binary_semaphore
└── <writeOp>_<readOp>
    └── <resource>
        └── <comboIndex>
```

- `<writeOp>_<readOp>`: Operation pair group (e.g., `copy_buffer_copy_buffer`, `ssbo_vertex_copy_buffer`). See Parameter Dimensions for the reduced operation set.
- `<resource>`: The first compatible resource from [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp). Only one resource is tested per operation pair.
- `<comboIndex>`: A 4-digit string (e.g., `0000`, `0123`) encoding the submit-info type permutation. See Submit Info Combinations below.

**Core Algorithm**:
1. Define 4 base submit info types (represented by [`QueueSubmitInfo`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L113)):
   - Type 0: Wait only
   - Type 1: Wait + Command buffer
   - Type 2: Wait + Signal
   - Type 3: Wait + Command buffer + Signal
2. For each test case, select a combination of 4 submit infos (one for each position), each chosen from the 4 base types
3. The test automatically generates counterpart submit infos:
   - Type 0 (Wait only) -> Signal only
   - Type 1 (Wait + CmdBuf) -> CmdBuf + Signal
   - Type 2 (Wait + Signal) -> Signal + Wait (split into two submit infos)
   - Type 3 (Wait + CmdBuf + Signal) -> CmdBuf + Signal + Wait (split into two submit infos)
4. All submit infos (original + counterparts) are submitted together in a single `vkQueueSubmit`
5. For each submit info with a command buffer, the number of command buffers is chosen randomly between 2-10
6. Waits and signals are similarly randomized in count (2-10)
7. Verify that all write/read data pairs match

**Key Invariants**:
- All waits are signaled by counterpart operations
- All signals are waited upon by counterpart operations
- All read operations have corresponding write operations and vice versa
- Each wait-signal pair uses its own binary semaphore

### timeline_semaphore -- Timeline semaphore implicit synchronization

Tests implicit synchronization using timeline semaphores (`VK_SEMAPHORE_TYPE_TIMELINE_KHR`). A single timeline semaphore is shared across all waits/signals with different timeline values.

Tests are registered under `synchronization.implicit.timeline_semaphore` (LEGACY) and `synchronization2.implicit.timeline_semaphore` (sync2).

**Hierarchy below this group**:

```text
timeline_semaphore
└── <writeOp>_<readOp>
    └── <resource>
        └── <comboIndex>
```

The hierarchy structure and test generation algorithm are identical to `binary_semaphore`. The only difference is the semaphore type: a single timeline semaphore is shared across all waits/signals with incrementing timeline values, rather than using separate binary semaphores for each wait-signal pair.

## Parameter Dimensions

### Semaphore Type

| Group Name | VkSemaphoreType |
|------------|-----------------|
| `binary_semaphore` | `VK_SEMAPHORE_TYPE_BINARY_KHR` |
| `timeline_semaphore` | `VK_SEMAPHORE_TYPE_TIMELINE_KHR` |

### Operation Pairs

Each family iterates over a **reduced** set of write and read operations (compared to other synchronization test files):

**Write Operations (2)**:
`COPY_BUFFER`, `SSBO_VERTEX`

**Read Operations (2)**:
`COPY_BUFFER`, `SSBO_VERTEX`

This reduced set keeps the combinatorial explosion manageable given the large number of submit info permutations.

### Resources

Each write/read pair is tested with **one** compatible resource from [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp). The first supported resource is selected, and iteration stops (via `break`).

### Submit Info Combinations

The test generates 4^4 = 256 combinations of submit info types. Each combination is named by a 4-digit string where each digit (0-3) represents the base type index for that position.

The first position (`idx0`) varies with `comboCnt` (cycling through 0-3), while positions 1-3 iterate through all 4 types, producing 4 * 4 * 4 = 64 combinations per starting index.

### SynchronizationType

Every test case is instantiated for both `LEGACY` and `SYNCHRONIZATION2` via the `SynchronizationType` parameter.

### Randomized Counts

Within each test instance, the number of wait semaphores, command buffers, and signal semaphores per submit info is randomized between 2 and 10 (using [`de::Random`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L170) with seed 1024).

## Support / Feature Requirements

| Requirement | Applicable Tests |
|-------------|-----------------|
| `VK_KHR_timeline_semaphore` | `timeline_semaphore` group |
| `VK_KHR_synchronization2` | All tests when `SynchronizationType::SYNCHRONIZATION2` |
| `timelineSemaphore` feature | Checked via `context.getTimelineSemaphoreFeatures()` for timeline semaphore tests |

## Verification Methods

- **Data comparison**: For buffer resources, `deMemCmp` compares write-output data against read-output data. For indirect buffers, the counter value is checked to be at least the expected value.
- **Fence wait**: After `vkQueueSubmit`, the test waits on a fence to ensure all work is complete before verifying data.

## Test Principles

- **Implicit ordering**: The Vulkan specification guarantees that within a single `vkQueueSubmit`, submit infos are processed in order. Signal operations in earlier submit infos complete before signal operations in later submit infos. This test verifies that implementations respect this ordering even when the submit info structure is complex.
- **Counterpart generation**: The test automatically generates counterpart submit infos to ensure that every wait has a matching signal and every signal has a matching wait, creating a valid synchronization chain.
- **Single-queue constraint**: All work is submitted to the same queue, which is essential for the implicit ordering guarantee to apply.
- **API variant abstraction**: [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) abstracts `vkQueueSubmit` vs `vkQueueSubmit2KHR`, allowing the same test logic to cover both API paths.
- **Shared pipeline cache**: [`PipelineCacheData`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L93) is shared across operation pair tests to reduce shader compilation overhead.

## Notes / Uncertainties

- The operation pair set is deliberately small (2 write ops x 2 read ops) compared to other synchronization test files (19 x 28). This is because the submit info permutation space (256+ combinations per resource) already generates a large number of test cases.
- Only one resource is tested per write/read pair (the first compatible one), unlike other test files that iterate over all compatible resources.
- The [`SubmitInfoElements`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L104) enum defines `SIE_WAIT`, `SIE_CMDBUFF`, `SIE_SIGNAL`, and `SIE_NONE` to represent the elements of each submit info position.
- The test does not use multiple queues or external sharing -- all work runs on the universal queue of a single device.
