## Overview

**Core question:** Does `vkCmdWriteBufferMarkerAMD` write the expected 32-bit marker values into the requested buffer slots under the chosen queue, memory, pipeline stage, and offset configuration, and do pipeline barriers correctly separate marker writes from interleaved non-marker writes?

- This page covers the `api.buffer_marker` test family implemented in [vktApiBufferMarkerTests.cpp](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1) and attached to the `api` test category by [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L103-L105) under `#ifndef CTS_USES_VULKANSC`, so the family is non-VulkanSC only.
- The test family registers three queue intermediate nodes (`graphics`, `compute`, `transfer`) and a fixed matrix below each: two memory types, two pipeline stages, and three test-type intermediate nodes (`sequential`, `overwrite`, `memory_dep`).
- The test exercises the `VK_AMD_buffer_marker` extension through `vkCmdWriteBufferMarkerAMD`, optionally backing the marker buffer with `VK_EXT_external_memory_host` host memory, and verifies the buffer contents on the host after submission.
- The `memory_dep` test type interleaves marker writes with non-marker writes (draw, dispatch, or `vkCmdUpdateBuffer`) and inserts pipeline barriers when slot ownership changes. It validates synchronization rather than just marker write correctness.
- The mustpass lists 156 test case leaves under `dEQP-VK.api.buffer_marker.*` in [api.txt](../../../mustpass/main/vk-default/api.txt#L3077-L3232).

## Background Knowledge

- **`VK_AMD_buffer_marker` and `vkCmdWriteBufferMarkerAMD`.** The extension provides a command that writes a single 32-bit value into a buffer at a given byte offset, ordered at a caller-chosen pipeline stage. CTS uses it as an observable side effect of pipeline progress; this test family treats the marker write itself as the unit under test.
- **Pipeline stage choice for marker writes.** `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT` and `VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT` place the marker write at opposite ends of the pipeline for a submitted command buffer. Testing both stages verifies that the implementation honors the requested stage rather than always writing at a fixed point.
- **`VK_EXT_external_memory_host`.** This extension lets a `VkBuffer` be backed by a host pointer imported through `VkImportMemoryHostPointerInfoEXT`. The `external_host_mem` variants of this test use that path so the marker buffer lives in host-managed memory. This exercises import and host coherency behavior that the default allocator does not.
- **Pipeline barriers for slot ownership transfer.** When two command types write the same buffer slot from different pipeline stages or access masks, a `VkBufferMemoryBarrier` is required to make the first write available and visible to the second. The `memory_dep` test type deliberately alternates ownership of a slot between marker and non-marker writers and inserts a barrier only when ownership changes.

## Registration Hierarchy

```text
api.buffer_marker
├── graphics
├── compute
└── transfer
```

Each queue intermediate node expands into two memory-type intermediate nodes (`external_host_mem`, `default_mem`), each of which expands into two pipeline-stage intermediate nodes (`top_of_pipe`, `bottom_of_pipe`), each of which contains the three test-type intermediate nodes (`sequential`, `overwrite`, `memory_dep`) and their test case leaves. The full tree is described in `## Parameter Dimensions and Observed Values` and `## Behavior Parameters` rather than expanded here.

The `buffer_marker` test family is created by [`createBufferMarkerTestsInGroup()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1081-L1246), which is exposed to the `api` test category through [`createBufferMarkerTests()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1250-L1253).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Queue type | `graphics`, `compute`, `transfer` | Targets universal, compute-only, or transfer-only queue families via `makeQueueCreateInfo` with `forbiddenFlags`. Determines which `memory_dep` methods are legal. | [vktApiBufferMarkerTests.cpp#L69-L92](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L69-L92), [vktApiBufferMarkerTests.cpp#L1086-L1087](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1086-L1087) |
| Memory type | `external_host_mem`, `default_mem` | `external_host_mem` imports a host pointer through `VK_EXT_external_memory_host`; `default_mem` uses the standard allocator. Both backings are host-visible so the result can be invalidated and read. | [vktApiBufferMarkerTests.cpp#L1097-L1098](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1097-L1098), [vktApiBufferMarkerTests.cpp#L206-L246](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L206-L246) |
| Pipeline stage | `top_of_pipe`, `bottom_of_pipe` | The `stage` parameter passed to `vkCmdWriteBufferMarkerAMD`. Selects when in the pipeline the marker write occurs. | [vktApiBufferMarkerTests.cpp#L1108-L1110](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1108-L1110) |
| Test type | `sequential`, `overwrite`, `memory_dep` | The primary behavioral axis. Each test type runs a different test function with its own write pattern and verification rule. | [vktApiBufferMarkerTests.cpp#L1118-L1234](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1118-L1234) |
| `memory_dep` method | `draw`, `dispatch`, `buffer_copy` | The non-marker writer interleaved with marker writes. `draw` is registered only on `graphics`; `dispatch` on `graphics` and `compute`; `buffer_copy` on all three queue types. | [vktApiBufferMarkerTests.cpp#L1199-L1231](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1199-L1231) |
| Marker buffer size | `1`, `4`, `64`, `128`, `65536` | Number of 32-bit slots in the marker buffer. `128` is fixed for `memory_dep`; `1`, `4`, `64`, `65536` cover the `sequential` and `overwrite` ranges. | [vktApiBufferMarkerTests.cpp#L1121-L1154](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1121-L1154), [vktApiBufferMarkerTests.cpp#L1163-L1185](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1163-L1185), [vktApiBufferMarkerTests.cpp#L1202-L1203](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1202-L1203) |
| Buffer offset | `0`, `16`, `24`, `1024` | Non-zero offsets exercise alignment, non-coherent atom size, and external host pointer alignment requirements. `16` pairs with size `64`; `24` with size `64` (overwrite) and size `128` (`memory_dep`); `1024` with size `65536`. | [vktApiBufferMarkerTests.cpp#L1121-L1154](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1121-L1154), [vktApiBufferMarkerTests.cpp#L1180-L1185](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1180-L1185), [vktApiBufferMarkerTests.cpp#L1196-L1197](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1196-L1197) |
| `memory_dep` iterations | `1000` | Fixed iteration count for the random ownership-alternation loop. | [vktApiBufferMarkerTests.cpp#L493](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L493) |

## Behavior Parameters

The primary behavioral axis is the test-type intermediate node (`sequential`, `overwrite`, `memory_dep`). Each value invokes a distinct test function and exercises a different write pattern. The `memory_dep` value introduces a secondary axis, the non-marker method, which is described inside its subsection.

### `sequential` — ordered sequential marker writes

Writes `params.size` marker values into consecutive 32-bit slots in submission order, then verifies the host-visible buffer contains exactly those values. The test uses a deterministic `de::Random` seeded with `12345 ^ params.size` so the expected values are reproducible. A single `VkMemoryBarrier` with `VK_ACCESS_TRANSFER_WRITE_BIT` → `VK_ACCESS_HOST_READ_BIT` separates the marker writes from host readback. Implemented in [`bufferMarkerSequential()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L248-L319).

### `overwrite` — random in-place marker overwrites

Performs `params.size * 10` random marker writes, each picking a slot and writing the iteration index as the value. The expected buffer is the last value written to each slot. This stresses the implementation's handling of repeated writes to the same slot from the same command buffer. Uses the same final memory barrier as `sequential`. Implemented in [`bufferMarkerOverwrite()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L321-L395).

### `memory_dep` — marker writes interleaved with non-marker writes

For 1000 iterations, randomly picks a slot and a new owner (`MEMORY_DEP_OWNER_MARKER` or `MEMORY_DEP_OWNER_NON_MARKER`). When ownership of the slot changes from the previous owner, the test inserts a `VkBufferMemoryBarrier` computed by [`computeMemoryDepBarrier()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L452-L480), then performs either a marker write or a non-marker write. The final barrier accumulates `writeStages` and `writeAccess` actually used and transfers them to `VK_ACCESS_HOST_READ_BIT`. Implemented in [`bufferMarkerMemoryDep()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L484-L999).

The secondary axis is the non-marker method, which determines what kind of write alternates with the marker writes:

| Method | Non-marker write | Stages/access masks | Queue availability |
|--------|------------------|---------------------|---------------------|
| `draw` | `vkCmdDraw` with fragment-shader storage-buffer write | `VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT` / `VK_ACCESS_SHADER_WRITE_BIT` | `graphics` only |
| `dispatch` | `vkCmdDispatch` with compute-shader storage-buffer write | `VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT` / `VK_ACCESS_SHADER_WRITE_BIT` | `graphics`, `compute` |
| `buffer_copy` | `vkCmdUpdateBuffer` | `VK_PIPELINE_STAGE_TRANSFER_BIT` / `VK_ACCESS_TRANSFER_WRITE_BIT` | `graphics`, `compute`, `transfer` |

The `draw` and `dispatch` methods bind the marker buffer as a storage buffer through a descriptor set and pass `slot` and `value` through push constants, so the shader writes a known value into the chosen slot. The `buffer_copy` method uses `vkCmdUpdateBuffer` and needs no shader. The shaders are simple storage-buffer writes; they are not the tested behavior and are described in `## Shader Analysis`.

## Shader Analysis

No shader is involved for `sequential` or `overwrite`; both rely only on `vkCmdWriteBufferMarkerAMD` and host readback.

The `memory_dep` test type uses trivial GLSL shaders only as the non-marker writer. The fragment shader used by the `draw` method writes `data.elems[pc.params.x] = pc.params.y;` to a `std430` storage buffer, and the compute shader used by the `dispatch` method does the same with `local_size = (1,1,1)`. These shaders exist solely to produce a non-marker shader write that competes with marker writes for the same buffer slot. The tested behavior is the host-side synchronization around those writes, so no representative shader walkthrough is provided here. Shader generation is in [`initMemoryDepPrograms()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1001-L1050).

## Runtime Execution and Result Checking

- **Device selection per queue type.** Each case is wrapped in [`BufferMarkerBaseCase`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L109-L129) or [`BufferMarkerMemDepCase`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L424-L450), both based on `InstanceFactory1WithSupport`. The `initDeviceCapabilities` override calls `caps.resetQueues({makeQueueCreateInfo(testQueue)})` so the created device exposes a queue family matching the requested type as closely as possible, and `getRequiredCapabilitiesId` returns a per-queue-and-offset cache ID via [`genBufferMarkerDeviceId()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L56-L63).
- **Extensions and features.** `VK_AMD_buffer_marker` is required for every case. `VK_EXT_external_memory_host` is required when `useHostPtr` is true. `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` is required for the `memory_dep` `draw` method because the fragment shader performs a storage-buffer store. See [`checkBufferMarkerSupport()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1052-L1072).
- **Marker buffer creation.** A `VkBuffer` of size `params.size * sizeof(uint32_t)` is created with `VK_BUFFER_USAGE_TRANSFER_DST_BIT` (plus `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` for `draw`/`dispatch`, or `VK_BUFFER_USAGE_TRANSFER_SRC_BIT` for `buffer_copy`). [`createMarkerBufferMemory()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L206-L246) either allocates through the default allocator or imports a host pointer via `VkImportMemoryHostPointerInfoEXT`, then binds buffer memory at the chosen offset.
- **Initial zeroing.** Before recording, the host zeroes the marker buffer (using `writeHostMemory` for external host memory, or `deMemcpy` plus `flushMappedMemoryRange` for default allocations) so stale data does not affect the comparison.
- **Command recording.** Each test function records its command buffer in a single begin/end pair, with `vkCmdWriteBufferMarkerAMD` calls at `params.stage` and any non-marker writes interleaved as needed. `memory_dep` inserts per-iteration `VkBufferMemoryBarrier` calls when slot ownership changes and a final accumulating `VkMemoryBarrier` to host read.
- **Submission and wait.** [`submitCommandsAndWait()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L312) submits the command buffer to the test queue and waits for completion.
- **Result comparison.** [`checkMarkerBuffer()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L152-L173) invalidates the allocation (or external host memory) and compares every `uint32_t` slot against the expected vector. The test returns `TestStatus::fail("Some marker values were incorrect")` if any slot differs, otherwise `TestStatus::pass("Pass")`.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Marker buffer | Yes | Yes, bound to `markerMemory` | Written by `vkCmdWriteBufferMarkerAMD` and (for `memory_dep`) by draw/dispatch/copy | Yes, after invalidation | Holds the per-slot 32-bit marker values checked by the host. |
| External host memory (`external_host_mem` only) | Yes, host allocation imported via `VK_EXT_external_memory_host` | Yes, as `VkDeviceMemory` backing the marker buffer | Same as marker buffer | Yes, through `invalidateHostMemory` | Provides an alternative backing that exercises host-pointer import and coherency. |
| Storage-buffer descriptor set (`memory_dep` `draw`/`dispatch` only) | Yes | Yes, descriptor binding 0 | Read/write by fragment or compute shader | No | Lets the non-marker writer store into the same marker buffer slot. |
| Pipeline (`memory_dep` only) | Yes | Yes | Bound to graphics or compute bind point | No | Carries the trivial storage-write shader used as the non-marker writer. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sequential` (any queue, memory, stage, size, or offset) | Marker write not performed, written to the wrong offset, or not made host-visible; non-zero offset or external host memory handling defect. |
| `overwrite` (any queue, memory, stage, size, or offset) | Same as `sequential`, plus incorrect handling of repeated writes to the same slot from a single command buffer. |
| `memory_dep` `draw` (graphics only) | Marker/non-marker write ordering defect due to a missing or incorrect pipeline barrier, or fragment-shader storage-buffer write not landing in the expected slot. |
| `memory_dep` `dispatch` (graphics, compute) | Marker/non-marker write ordering defect due to a missing or incorrect pipeline barrier, or compute-shader storage-buffer write not landing in the expected slot. |
| `memory_dep` `buffer_copy` (all queues) | Marker write vs `vkCmdUpdateBuffer` ordering defect due to a missing or incorrect pipeline barrier. |

Common amplifiers across all values: `external_host_mem` variants additionally stress host-pointer import and coherency; non-zero `offset` variants additionally stress alignment and `nonCoherentAtomSize` rounding.

### Cause Analysis

#### Marker write not performed, written to the wrong offset, or not made host-visible

**Possible failure symptoms:** `checkMarkerBuffer` finds at least one slot in the marker buffer that does not match the expected value from the `expected` vector built by the host, in a `sequential` or `overwrite` case where no non-marker write ever touches the buffer [vktApiBufferMarkerTests.cpp#L152-L173](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L152-L173), [vktApiBufferMarkerTests.cpp#L248-L319](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L248-L319).

**Possible implementation causes:** The implementation may fail to execute `vkCmdWriteBufferMarkerAMD` at the requested pipeline stage, may compute the write offset incorrectly, or may not make the transfer write available and visible to the host before readback. The test records a final `VkMemoryBarrier` from `VK_ACCESS_TRANSFER_WRITE_BIT` to `VK_ACCESS_HOST_READ_BIT` and waits on the queue before invalidating; a missing or weakened barrier on the implementation side would let stale data remain visible. Source-level investigation is needed to distinguish a stage-execution defect from a coherency or barrier defect.

#### Incorrect handling of repeated writes to the same slot from a single command buffer

**Possible failure symptoms:** `checkMarkerBuffer` reports a mismatch in an `overwrite` case, where the failing slot does not contain the value of the last `vkCmdWriteBufferMarkerAMD` call recorded for that slot [vktApiBufferMarkerTests.cpp#L321-L395](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L321-L395).

**Possible implementation causes:** When the same slot is written many times from one command buffer at the same pipeline stage, the implementation must serialize the writes in submission order so the final value is the last recorded write. Reordering, coalescing, or last-write-wins violations would produce a stale or intermediate value. Source-level investigation is needed to confirm whether the defect is command ordering, write coalescing, or stage scheduling.

#### Marker/non-marker write ordering defect due to a missing or incorrect pipeline barrier

**Possible failure symptoms:** `checkMarkerBuffer` reports a mismatch in a `memory_dep` case, where the failing slot contains the value from the wrong writer (marker instead of non-marker, or vice versa) for the last recorded operation on that slot [vktApiBufferMarkerTests.cpp#L484-L999](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L484-L999), [vktApiBufferMarkerTests.cpp#L877-L978](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L877-L978).

**Possible implementation causes:** The test inserts a `VkBufferMemoryBarrier` only when slot ownership changes between marker and non-marker writers, with source and destination access masks and stage masks computed by [`computeMemoryDepBarrier()`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L452-L480). A failure points to the implementation not honoring the barrier's availability/visibility operations across the two write types, executing the new write before the prior write completes, or applying the wrong stage or access mask when relating marker writes (reported as `VK_ACCESS_TRANSFER_WRITE_BIT` at `params.stage | VK_PIPELINE_STAGE_TRANSFER_BIT`) to non-marker writes. The `draw` and `dispatch` variants additionally depend on shader-side storage-buffer stores becoming visible at the expected stage; a shader compiler or storage-buffer access defect could also produce this symptom, and source-level investigation is needed to distinguish synchronization faults from shader-store faults.

#### External host memory import or coherency defect

**Possible failure symptoms:** A failure appears only on `external_host_mem` variants while the corresponding `default_mem` variant passes, with `checkMarkerBuffer` reading stale or partial marker values after invalidation [vktApiBufferMarkerTests.cpp#L143-L173](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L143-L173), [vktApiBufferMarkerTests.cpp#L206-L246](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L206-L246).

**Possible implementation causes:** The `external_host_mem` path imports a host pointer through `VkImportMemoryHostPointerInfoEXT`, aligns the buffer offset to the imported memory alignment, and reads back through `invalidateHostMemory` rather than the standard allocator invalidation. A defect in host pointer import, alignment handling, mapped memory visibility, or `invalidateMappedMemoryRange` for imported memory would produce stale reads even when the marker writes themselves are correct. Source-level investigation is needed to identify whether the defect is in import, mapping, or coherency tracking.

#### Non-zero buffer offset or alignment handling defect

**Possible failure symptoms:** A failure appears only on variants with non-zero `offset` (`16`, `24`, `1024`) while the corresponding zero-offset variant passes [vktApiBufferMarkerTests.cpp#L1135-L1154](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1135-L1154), [vktApiBufferMarkerTests.cpp#L1180-L1185](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1180-L1185), [vktApiBufferMarkerTests.cpp#L1196-L1203](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1196-L1203).

**Possible implementation causes:** Non-zero offsets exercise the `nonCoherentAtomSize` rounding configured in [`initDeviceCapabilities`](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L116-L128) and the alignment used when importing external host memory. A defect in offset arithmetic, atom-size rounding for flush/invalidate, or external-host-pointer alignment could produce slot-value corruption only at non-zero offsets. Source-level investigation is needed to identify the specific offset-handling defect.

## Case Pruning

### Requirement-based pruning

- `VK_AMD_buffer_marker` is required for every case; the device must support the extension or the case is unsupported [vktApiBufferMarkerTests.cpp#L1057](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1057).
- `VK_EXT_external_memory_host` is required when `useHostPtr` is true, so `external_host_mem` variants are skipped on implementations without that extension [vktApiBufferMarkerTests.cpp#L1054-L1055](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1054-L1055).
- `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS` is required for the `memory_dep` `draw` method because the fragment shader performs a storage-buffer store [vktApiBufferMarkerTests.cpp#L1067-L1071](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1067-L1071).
- The `draw` method is registered only on `graphics` because draw operations require a graphics queue [vktApiBufferMarkerTests.cpp#L1205-L1213](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1205-L1213).
- The `dispatch` method is registered on `graphics` and `compute` and skipped on `transfer` because compute dispatch requires a compute-capable queue [vktApiBufferMarkerTests.cpp#L1215-L1223](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1215-L1223).
- The `buffer_copy` method is registered on all three queue types because `vkCmdUpdateBuffer` is a transfer operation [vktApiBufferMarkerTests.cpp#L1225-L1230](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1225-L1230).

### Design-based pruning

- The matrix is not exhaustive. Only selected `(size, offset)` pairs are registered for `sequential` (`4/0`, `64/0`, `64/16`, `65536/0`, `65536/1024`) and `overwrite` (`1/0`, `4/0`, `64/0`, `64/24`) [vktApiBufferMarkerTests.cpp#L1118-L1190](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1118-L1190).
- `memory_dep` fixes `size = 128` and registers only `offset` values `0` and `24` [vktApiBufferMarkerTests.cpp#L1196-L1203](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1196-L1203).
- The pipeline-stage dimension is limited to `top_of_pipe` and `bottom_of_pipe`; other stages are not registered.
- The `memory_dep` iteration count is fixed at `1000`; smaller or larger stress counts are not registered [vktApiBufferMarkerTests.cpp#L493](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L493).

## Key Takeaways

- The test family treats `vkCmdWriteBufferMarkerAMD` as the unit under test, not as an infrastructure side effect. The three test types differ in write pattern: `sequential` writes each slot once, `overwrite` writes the same slots repeatedly, and `memory_dep` alternates ownership of slots between marker and non-marker writers.
- Cross-queue coverage is structural: `graphics`, `compute`, and `transfer` are tested with the most specific queue family the implementation exposes through `makeQueueCreateInfo`'s `forbiddenFlags`, and the registered `memory_dep` methods are pruned to operations legal on each queue type.
- The `external_host_mem` variants are not redundant with `default_mem`; they exercise the `VK_EXT_external_memory_host` import path and host-side coherency for imported memory.
- The `memory_dep` design isolates synchronization correctness: barriers are inserted only when slot ownership changes, with stages and access masks computed from the writer types, so a failure points directly to barrier handling rather than to marker write mechanics.
- See `## Failure Meaning` for the failure interpretation: symptoms always surface as a slot-value mismatch in `checkMarkerBuffer`, and the cause is narrowed by which axis combination fails (queue, memory, stage, offset, test type, or method).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test category attachment | [vktApiTests.cpp#L103-L105](../../../modules/vulkan/api/vktApiTests.cpp#L103-L105) | Adds `buffer_marker` to the `api` test category under `#ifndef CTS_USES_VULKANSC`. |
| Factory declaration | [vktApiBufferMarkerTests.hpp#L34](../../../modules/vulkan/api/vktApiBufferMarkerTests.hpp#L34) | Declares `createBufferMarkerTests`. |
| Test family creation | [vktApiBufferMarkerTests.cpp#L1081-L1246](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1081-L1246) | Builds the `buffer_marker` tree with queue, memory, stage, and test-type intermediate nodes. |
| Queue selection helper | [vktApiBufferMarkerTests.cpp#L69-L92](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L69-L92) | `makeQueueCreateInfo` chooses the most specific queue family for each `VkQueueFlagBits`. |
| Test case wrapper | [vktApiBufferMarkerTests.cpp#L109-L129](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L109-L129) | `BufferMarkerBaseCase` configures device queues, extensions, and allocator offset parameters per case. |
| `memory_dep` wrapper | [vktApiBufferMarkerTests.cpp#L424-L450](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L424-L450) | `BufferMarkerMemDepCase` extends the wrapper to add the `fragmentStoresAndAtomics` feature for `memory_dep`. |
| Marker buffer memory setup | [vktApiBufferMarkerTests.cpp#L206-L246](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L206-L246) | `createMarkerBufferMemory` allocates or imports host memory and binds the buffer. |
| `sequential` test function | [vktApiBufferMarkerTests.cpp#L248-L319](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L248-L319) | Records ordered marker writes and verifies the buffer. |
| `overwrite` test function | [vktApiBufferMarkerTests.cpp#L321-L395](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L321-L395) | Records random repeated marker writes and verifies the last-write value per slot. |
| `memory_dep` test function | [vktApiBufferMarkerTests.cpp#L484-L999](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L484-L999) | Records 1000 iterations of marker or non-marker writes with ownership-change barriers. |
| `computeMemoryDepBarrier` | [vktApiBufferMarkerTests.cpp#L452-L480](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L452-L480) | Computes source/destination access masks and stage masks for each writer type. |
| Result check | [vktApiBufferMarkerTests.cpp#L152-L173](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L152-L173) | `checkMarkerBuffer` invalidates memory and compares each slot against the expected vector. |
| Support checks | [vktApiBufferMarkerTests.cpp#L1052-L1072](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1052-L1072) | Requires the extensions and core features needed for each case. |
| Shader generation for `memory_dep` | [vktApiBufferMarkerTests.cpp#L1001-L1050](../../../modules/vulkan/api/vktApiBufferMarkerTests.cpp#L1001-L1050) | Emits the trivial vertex/fragment or compute shader used as the non-marker writer. |
| Mustpass entry range | [api.txt#L3077-L3232](../../../mustpass/main/vk-default/api.txt#L3077-L3232) | Lists all 156 `dEQP-VK.api.buffer_marker.*` test case leaves. |
