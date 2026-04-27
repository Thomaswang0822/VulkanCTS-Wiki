# [vktApiBufferMarkerTests.cpp](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1)

## Overview

Tests VK_AMD_buffer_marker by writing marker values into a buffer via `vkCmdWriteBufferMarkerAMD` and verifying the results. Covers sequential writes, random overwrites, and memory dependency scenarios where marker writes are interleaved with draws, compute dispatches, and buffer copies. Tests multiple queue types, pipeline stages, memory types, and buffer offsets.

## Role of File

Implementation-heavy. Contains multiple test instance classes, sparse/external memory management, shader generation, and deep test hierarchy registration.

## Source Code

| File | Description |
|------|-------------|
| [vktApiBufferMarkerTests.cpp](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1) | Test implementation and registration |
| [vktApiBufferMarkerTests.hpp](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.hpp#L1) | Declares `createBufferMarkerTests` |
| [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L104) | Parent registration: `apiTests->addChild(createBufferMarkerTests(testCtx))` |

## Registration Path

```
api
  +-- buffer_marker
       +-- graphics
       |    +-- external_host_mem
       |    |    +-- top_of_pipe
       |    |    |    +-- sequential
       |    |    |    |    +-- 4, 64, 64_offset_16, 65536, 65536_offset_1024
       |    |    |    +-- overwrite
       |    |    |    |    +-- 1, 4, 64, 64_offset_24
       |    |    |    +-- memory_dep
       |    |    |         +-- draw, draw_offset_24, dispatch, dispatch_offset_24,
       |    |    |            buffer_copy, buffer_copy_offset_24
       |    |    +-- bottom_of_pipe
       |    |         +-- <same structure as top_of_pipe>
       |    +-- default_mem
       |         +-- top_of_pipe
       |         |    +-- <same structure>
       |         +-- bottom_of_pipe
       |              +-- <same structure>
       +-- compute
       |    +-- <same memory/stage/test structure>
       +-- transfer
            +-- <same memory/stage/test structure>
                 (no draw/dispatch memory_dep tests for transfer queue)
```

## Test Hierarchy

```
buffer_marker
  +-- <queue_type: graphics|compute|transfer>
       +-- <memory_type: external_host_mem|default_mem>
            +-- <pipeline_stage: top_of_pipe|bottom_of_pipe>
                 +-- sequential
                 |    Writes N markers sequentially, verifies all values
                 |    +-- 4, 64, 64_offset_16, 65536, 65536_offset_1024
                 +-- overwrite
                 |    Randomly overwrites marker slots, verifies final values
                 |    +-- 1, 4, 64, 64_offset_24
                 +-- memory_dep
                      Interleaves marker writes with other operations,
                      inserts pipeline barriers, verifies final values
                      +-- draw / draw_offset_24       (graphics queue only)
                      +-- dispatch / dispatch_offset_24 (graphics+compute queues)
                      +-- buffer_copy / buffer_copy_offset_24 (all queues)
```

## Test Families

### buffer_marker

Group name verified at [vktApiBufferMarkerTests.cpp:1084](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1084): `new tcu::TestCaseGroup(testCtx, "buffer_marker")`.

Three queue types at [line 1086](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1086):

| Queue Group | Queue Flag | Target Queue |
|-------------|-----------|--------------|
| `graphics` | VK_QUEUE_GRAPHICS_BIT | Universal/graphics queues |
| `compute` | VK_QUEUE_COMPUTE_BIT | Compute-only queues |
| `transfer` | VK_QUEUE_TRANSFER_BIT | Transfer-only queues |

Two memory types at [lines 1097-1098](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1097):

| Memory Group | useHostPtr | Description |
|-------------|-----------|-------------|
| `external_host_mem` | true | Uses VK_EXT_external_memory_host for buffer backing |
| `default_mem` | false | Uses standard allocator |

Two pipeline stages at [lines 1108-1109](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1108):

| Stage Group | Pipeline Stage |
|------------|---------------|
| `top_of_pipe` | VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT |
| `bottom_of_pipe` | VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT |

Three test categories:

**sequential** - `bufferMarkerSequential` at [line 248](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L248): Writes N sequential random marker values via `vkCmdWriteBufferMarkerAMD`, then reads back and verifies all values match.

**overwrite** - `bufferMarkerOverwrite` at [line 321](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L321): Randomly overwrites marker slots (size*10 iterations), verifying the final values match the last write to each slot.

**memory_dep** - `bufferMarkerMemoryDep` at [line 484](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L484): For 1000 iterations, randomly alternates between marker writes and non-marker operations (draw/dispatch/copy), inserting pipeline barriers when ownership changes between marker and non-marker writes. Verifies final buffer contents.

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Queue type | Graphics, Compute, Transfer | 3 types at [line 1086](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1086) |
| Memory type | External host, Default | 2 types |
| Pipeline stage | Top of pipe, Bottom of pipe | 2 stages |
| Marker count | 1, 4, 64, 128, 65536 | Varies by test |
| Buffer offset | 0, 16, 24, 1024 | Non-zero offsets exercise alignment |
| Memory dep method | Draw, Dispatch, Copy | Draw only for graphics; dispatch for graphics+compute; copy for all |
| Memory dep iterations | 1000 | Hard-coded at [line 493](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L493) |

## Support / Feature Requirements

- `VK_AMD_buffer_marker` required for all tests ([line 1057](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1057))
- `VK_EXT_external_memory_host` required when `useHostPtr` is true ([line 1055](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1055))
- `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` required for draw memory dep tests ([line 1070](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1070))
- Queue selection targets specific queue types: transfer-only, compute-only, or universal queues via `makeQueueCreateInfo` at [line 69](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L69)

## Verification Methods

- **Sequential/overwrite**: Reads back marker buffer and compares each uint32_t against the expected value. Uses `checkMarkerBuffer` at [line 152](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L152).
- **Memory dep**: Tracks data ownership per slot (MARKER vs NON_MARKER). When ownership changes, inserts a `VkBufferMemoryBarrier` with computed access flags and stage masks via `computeMemoryDepBarrier` at [line 452](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L452). Verifies final buffer contents match the last write to each slot.

## Test Principles Observed

- Queue type coverage: tests marker writes on graphics, compute, and transfer queues
- Memory type coverage: tests both standard and external host memory
- Memory dependency correctness: verifies that pipeline barriers between marker and non-marker writes are properly respected
- Offset coverage: tests non-zero buffer offsets to exercise alignment requirements

## Notes / Uncertainties

- The test uses `InstanceFactory1WithSupport` with custom `DevCaps` to create devices with specific queue configurations and extensions, which is different from most CTS tests
- The `getRequiredCapabilitiesId` override at [line 113](../../../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L113) generates a unique ID per queue type and offset combination, which enables device capability caching
- Transfer queue tests do not include draw or dispatch memory dependency tests since those operations require graphics or compute queues
- The `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT` stage for marker writes means the marker value is written at the start of the pipeline, which may have implementation-specific behavior
