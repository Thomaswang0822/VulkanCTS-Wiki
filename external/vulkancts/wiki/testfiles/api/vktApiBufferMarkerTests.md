# [vktApiBufferMarkerTests.cpp](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1)

## Overview

Tests VK_AMD_buffer_marker by writing marker values into a buffer via `vkCmdWriteBufferMarkerAMD` and verifying the results. Covers sequential writes, random overwrites, and memory dependency scenarios where marker writes are interleaved with draws, compute dispatches, and buffer copies. Tests multiple queue types, pipeline stages, memory types, and buffer offsets.

## Role of File

Implementation-heavy. Contains multiple test instance classes, sparse/external memory management, shader generation, and deep test hierarchy registration.

## Source Code

| File | Description |
|------|-------------|
| [vktApiBufferMarkerTests.cpp](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1) | Test implementation and registration |
| [vktApiBufferMarkerTests.hpp](../../../modules/vulkan/api/vktApiBufferMarkerTests.hpp#L1) | Declares `createBufferMarkerTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L104) | Parent registration: `apiTests->addChild(createBufferMarkerTests(testCtx))` |

## Registration Hierarchy

```text
api.buffer_marker
├── graphics
├── compute
└── transfer
```

Evidence:
- `buffer_marker` group created at [`createBufferMarkerTestsInGroup()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1081)
- queue subgroups added from [`vktApiBufferMarkerTests.cpp`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1092) through [`vktApiBufferMarkerTests.cpp`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1248)

## Test Families

### graphics — Graphics queue marker tests

The `graphics` subgroup at [line 1095](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1095) targets `VK_QUEUE_GRAPHICS_BIT` universal/graphics queues. Beneath `graphics`, the hierarchy expands into two memory type groups (`external_host_mem` and `default_mem`), each containing two pipeline stage groups (`top_of_pipe` and `bottom_of_pipe`). Each stage group contains three test categories:

- **sequential** (`bufferMarkerSequential` at [line 248](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L248)): Writes N sequential random marker values via `vkCmdWriteBufferMarkerAMD`, then reads back and verifies all values match. Leaf tests: `4`, `64`, `64_offset_16`, `65536`, `65536_offset_1024`.
- **overwrite** (`bufferMarkerOverwrite` at [line 321](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L321)): Randomly overwrites marker slots (size*10 iterations), verifying the final values match the last write to each slot. Leaf tests: `1`, `4`, `64`, `64_offset_24`.
- **memory_dep** (`bufferMarkerMemoryDep` at [line 484](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L484)): For 1000 iterations, randomly alternates between marker writes and non-marker operations, inserting pipeline barriers when ownership changes. Verifies final buffer contents. Leaf tests include `draw`, `draw_offset_24`, `dispatch`, `dispatch_offset_24`, `buffer_copy`, and `buffer_copy_offset_24`.

### compute — Compute queue marker tests

The `compute` subgroup at [line 1095](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1095) targets `VK_QUEUE_COMPUTE_BIT` compute-only queues. The hierarchy beneath `compute` follows the same memory type and pipeline stage structure as `graphics`. The test categories are the same, except that `memory_dep` does not include `draw` or `draw_offset_24` leaves (draw operations require a graphics queue). Memory dep leaf tests: `dispatch`, `dispatch_offset_24`, `buffer_copy`, `buffer_copy_offset_24`.

### transfer — Transfer queue marker tests

The `transfer` subgroup at [line 1095](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1095) targets `VK_QUEUE_TRANSFER_BIT` transfer-only queues. The hierarchy beneath `transfer` follows the same memory type and pipeline stage structure as `graphics`. The test categories are the same, except that `memory_dep` only includes `buffer_copy` and `buffer_copy_offset_24` leaves (draw and dispatch operations require graphics or compute queues).

Two memory types are shared across all queue groups at [lines 1097-1098](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1097):

| Memory Group | useHostPtr | Description |
|-------------|-----------|-------------|
| `external_host_mem` | true | Uses VK_EXT_external_memory_host for buffer backing |
| `default_mem` | false | Uses standard allocator |

Two pipeline stages are shared across all queue groups at [lines 1108-1109](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1108):

| Stage Group | Pipeline Stage |
|------------|---------------|
| `top_of_pipe` | VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT |
| `bottom_of_pipe` | VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT |

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Queue type | Graphics, Compute, Transfer | 3 types at [line 1086](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1086) |
| Memory type | External host, Default | 2 types |
| Pipeline stage | Top of pipe, Bottom of pipe | 2 stages |
| Marker count | 1, 4, 64, 128, 65536 | Varies by test |
| Buffer offset | 0, 16, 24, 1024 | Non-zero offsets exercise alignment |
| Memory dep method | Draw, Dispatch, Copy | Draw only for graphics; dispatch for graphics+compute; copy for all |
| Memory dep iterations | 1000 | Hard-coded at [line 493](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L493) |

## Support / Feature Requirements

- `VK_AMD_buffer_marker` required for all tests ([line 1057](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1057))
- `VK_EXT_external_memory_host` required when `useHostPtr` is true ([line 1055](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1055))
- `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` required for draw memory dep tests ([line 1070](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1070))
- Queue selection targets specific queue types: transfer-only, compute-only, or universal queues via `makeQueueCreateInfo` at [line 69](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L69)

## Verification Methods

- **Sequential/overwrite**: Reads back marker buffer and compares each uint32_t against the expected value. Uses `checkMarkerBuffer` at [line 152](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L152).
- **Memory dep**: Tracks data ownership per slot (MARKER vs NON_MARKER). When ownership changes, inserts a `VkBufferMemoryBarrier` with computed access flags and stage masks via `computeMemoryDepBarrier` at [line 452](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L452). Verifies final buffer contents match the last write to each slot.

## Test Principles Observed

- Queue type coverage: tests marker writes on graphics, compute, and transfer queues
- Memory type coverage: tests both standard and external host memory
- Memory dependency correctness: verifies that pipeline barriers between marker and non-marker writes are properly respected
- Offset coverage: tests non-zero buffer offsets to exercise alignment requirements

## Notes / Uncertainties

- The test uses `InstanceFactory1WithSupport` with custom `DevCaps` to create devices with specific queue configurations and extensions, which is different from most CTS tests
- The `getRequiredCapabilitiesId` override at [line 113](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L113) generates a unique ID per queue type and offset combination, which enables device capability caching
- Transfer queue tests do not include draw or dispatch memory dependency tests since those operations require graphics or compute queues
- The `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT` stage for marker writes means the marker value is written at the start of the pipeline, which may have implementation-specific behavior
