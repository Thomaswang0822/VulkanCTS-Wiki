# [vktApiBufferMarkerTests.cpp](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1)

## Overview

Tests the VK_AMD_buffer_marker extension, which provides `cmdWriteBufferMarkerAMD` to write marker values into a buffer at specified pipeline stages. The file validates that marker writes produce correct values both in sequential and random-overwrite scenarios, and that proper memory dependencies are enforced between marker writes and other GPU operations (draws, dispatches, copies).

## Role of File

Implementation-heavy. Contains test instance logic, shader program generation, and test group construction for the VK_AMD_buffer_marker extension.

## Source Code

- Implementation: [vktApiBufferMarkerTests.cpp](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1)
- Header: [vktApiBufferMarkerTests.hpp](../../modules/vulkan/api/vktApiBufferMarkerTests.hpp#L1)
- Parent registration: `vktApiTests.cpp` registers `createBufferMarkerTests()` under `api` -> `buffer_marker` (non-VKSC only)

## Registration Path

```
api
  +-- buffer_marker
        +-- graphics
        |     +-- external_host_mem
        |     |     +-- top_of_pipe
        |     |     |     +-- sequential
        |     |     |     +-- overwrite
        |     |     |     +-- memory_dep
        |     |     +-- bottom_of_pipe
        |     |           +-- sequential
        |     |           +-- overwrite
        |     |           +-- memory_dep
        |     +-- default_mem
        |           +-- top_of_pipe
        |           +-- bottom_of_pipe
        +-- compute
        |     +-- ...
        +-- transfer
              +-- ...
```

## Test Hierarchy

```
buffer_marker
  +-- <queue_type>              -- graphics | compute | transfer
        +-- <memory_type>       -- external_host_mem | default_mem
              +-- <stage>        -- top_of_pipe | bottom_of_pipe
                    +-- sequential
                    |     +-- 4
                    |     +-- 64
                    |     +-- 64_offset_16
                    |     +-- 65536
                    |     +-- 65536_offset_1024
                    +-- overwrite
                    |     +-- 1
                    |     +-- 4
                    |     +-- 64
                    |     +-- 64_offset_24
                    +-- memory_dep
                          +-- draw | draw_offset_24
                          +-- dispatch | dispatch_offset_24
                          +-- buffer_copy | buffer_copy_offset_24
```

## Test Families

### Sequential ([L248](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L248))

Writes N sequential marker values into a buffer via `cmdWriteBufferMarkerAMD`, then reads back and compares against expected random values. Tests that each marker slot receives the correct value in order. Sizes tested: 4, 64, 65536 with optional buffer offsets (0, 16, 1024).

### Overwrite ([L321](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L321))

Randomly overwrites marker slots (10x the buffer size iterations) using `cmdWriteBufferMarkerAMD`. Validates that the final value in each slot matches the last write to that slot. Sizes tested: 1, 4, 64 with optional offset (0, 24).

### Memory Dependency ([L484](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L484))

Interleaves `cmdWriteBufferMarkerAMD` writes with other GPU operations (draw via fragment shader, compute dispatch, or `cmdUpdateBuffer` copy) that write to the same buffer slots. Inserts pipeline barriers when ownership changes between marker and non-marker writers. Runs 1000 iterations with random slot/owner selection. Validates final buffer contents match expected values.

- **draw** sub-family: Uses graphics pipeline with fragment shader writing via storage buffer. Only available for `VK_QUEUE_GRAPHICS_BIT` queues ([L1205](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1205)).
- **dispatch** sub-family: Uses compute pipeline with storage buffer. Available for graphics and compute queues, not transfer-only queues ([L1215](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1215)).
- **buffer_copy** sub-family: Uses `cmdUpdateBuffer` for non-marker writes. Available for all queue types ([L1225](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1225)).

## Parameter Dimensions

| Dimension | Values | Notes |
|---|---|---|
| Queue type | graphics, compute, transfer | Targets specific queue families via [makeQueueCreateInfo](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L69) |
| Memory type | external_host_mem, default_mem | Controls `useHostPtr` flag; external uses VK_EXT_external_memory_host |
| Pipeline stage | top_of_pipe, bottom_of_pipe | VkPipelineStageFlagBits for marker write stage |
| Test type | sequential, overwrite, memory_dep | Three distinct test families |
| Buffer size | 4, 64, 65536 (sequential); 1, 4, 64 (overwrite); 128 (memory_dep) | Number of uint32_t marker slots |
| Buffer offset | 0, 16, 1024 (sequential); 0, 24 (overwrite); 0, 24 (memory_dep) | Byte offset into buffer |
| Memory dep method | draw, dispatch, buffer_copy | Only in memory_dep family; availability depends on queue type |

## Support / Feature Requirements

| Requirement | Gate | Source |
|---|---|---|
| VK_AMD_buffer_marker | `context.requireDeviceFunctionality` | [L1057](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1057) |
| VK_EXT_external_memory_host | Required when `useHostPtr=true` | [L1054](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1054) |
| fragmentStoresAndAtomics | Required for memory_dep draw method | [L1070](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1070) |
| Custom device with specific queue family | `DevCaps::resetQueues` via `BufferMarkerBaseCase` / `BufferMarkerMemDepCase` | [L117](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L117) |

## Verification Methods

- **Sequential/Overwrite**: After GPU execution, the marker buffer is invalidated and read back. Each uint32_t slot is compared against the expected value. Any mismatch yields `TestStatus::fail` ([L314](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L314)).
- **Memory Dependency**: Same readback-and-compare approach, but expected values track the last writer (marker or non-marker) per slot across 1000 random iterations ([L994](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L994)).
- **External host memory**: Uses `invalidateHostMemory` instead of `invalidateAlloc` for readback ([L156](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L156)).

## Test Principles Observed

- **Extension coverage**: Tests all documented behaviors of VK_AMD_buffer_marker (sequential writes, overwrites, memory dependencies).
- **Queue family specificity**: Targets transfer-only, compute-only, and universal queues separately via [makeQueueCreateInfo](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L69).
- **Memory model correctness**: Memory dependency tests exercise pipeline barriers between marker and non-marker writes, validating Vulkan memory model semantics.
- **Offset coverage**: Tests non-zero buffer offsets to verify correct offset handling in marker writes.

## Notes / Uncertainties

- The `BufferMarkerBaseCase` and `BufferMarkerMemDepCase` classes use `InstanceFactory1WithSupport` with custom `DevCaps` to create devices with specific queue configurations, which is an unusual pattern compared to standard CTS tests.
- The `genBufferMarkerDeviceId` function ([L56](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L56)) uses `typeid(WorkingDevice).name()` as part of the capabilities ID, which may produce platform-specific identifiers.
- The memory_dep draw sub-family requires `fragmentStoresAndAtomics` but the `BufferMarkerMemDepCase::initDeviceCapabilities` unconditionally adds this feature ([L448](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L448)) even for non-draw methods, which appears to be a minor redundancy.
- Shader programs for memory_dep tests are generated in [initMemoryDepPrograms](../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1001) using GLSL 450; the copy method does not require any shader programs.
