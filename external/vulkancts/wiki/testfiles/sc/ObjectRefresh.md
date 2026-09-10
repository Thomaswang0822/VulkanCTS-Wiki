## Overview

**Core question:** Does `VK_KHR_object_refresh` expose a coherent refreshable-type list and accept refresh commands for the live objects selected by the test?

- This page documents `external/vulkancts/modules/vulkan/sc/vktObjectRefreshTests.cpp` and the `sc.object_refresh` test family.
- The family registers `query_refreshable_objects`, `refresh_individual_objects`, and `refresh_all_objects`.
- The query case checks null-output enumeration, capacity truncation, result codes, returned counts, and object-type values.
- The two command cases create a set of Vulkan objects, keep only reported types with live handles, record either one-entry lists or one compact list, and submit the command buffer.
- The cases report API and command-stream success. They do not read an object back, dispatch the compute pipeline, or compare a rendered or buffer result.

The SC root registers this family through [`createChildren()`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L56). The default SC mustpass file lists the three executable paths at [`sc.txt#L145-L147`](../../../mustpass/main/vksc-default/sc.txt#L145-L147).

## Background Knowledge

- Object refresh restores implementation-internal object data from a backup in memory protected against single event upsets (SEUs). It differs from reloading application-owned buffer or image contents. The extension lets applications query which object types have internal data in SEU-susceptible memory (Vulkan SC specification object-refresh semantics).
- `VkObjectType` identifies the kind of Vulkan handle represented by a refresh entry. The physical-device query returns types; the application must still provide a handle of the corresponding type.
- Count-and-data queries use the supplied count as output-array capacity and return the number written. An undersized array may require another call to obtain the full list.
- `VkRefreshObjectKHR` couples an object type with a 64-bit handle and per-entry reserved flags. `VkRefreshObjectListKHR` supplies the entry count and array pointer to `vkCmdRefreshObjectsKHR`; the list itself has no `flags` member (Vulkan SC specification refresh structures).
- A primary command buffer records device work for later queue submission. Recording and waiting for a refresh command tests command acceptance and completion, but does not demonstrate a visible mutation of an object.

## Registration Hierarchy

```text
sc.object_refresh
├── query_refreshable_objects
├── refresh_individual_objects
└── refresh_all_objects
```

`createObjectRefreshTests()` constructs the group and registers the three leaves at [`vktObjectRefreshTests.cpp#L377-L388`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L377-L388).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case | `query_refreshable_objects`, `refresh_individual_objects`, `refresh_all_objects` | Selects enumeration checking, repeated one-entry commands, or one batched command | [`createObjectRefreshTests()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L377-L388) |
| Query capacity | `0` through `countReported + 1` | Covers zero, undersized, exact, and oversized output capacities | [`queryRefreshableObjects()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L63-L90) |
| Refresh list shape | `objectCount == 1` per command, or one list with all usable entries | Compares repeated individual recording with the batch form | [`refreshObjects()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L294-L341) |
| Object selection | Reported type with a nonzero local handle | Prevents commands from using uncreated or unavailable handles | [`objectHandlesMap`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L258-L289) |

The capacity loop is internal to the query case. The two refresh modes are fixed registered leaves; the source does not generate a parameter cross-product.

## Behavior Parameters

The primary behavioral axis is the registered test case: each leaf exercises a different API or command-list shape.

### `query_refreshable_objects` — validate enumeration

The case first calls `vkGetPhysicalDeviceRefreshableObjectTypesKHR` with a null output array. It requires `VK_SUCCESS` and a nonzero reported count. It allocates `countReported + 2` entries and requests capacities from zero through `countReported + 1`; the allocation size is not itself a requested capacity ([initial query and loop](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L49-L72)).

Before each data call, the test fills the entire vector with `VK_OBJECT_TYPE_UNKNOWN`. It then checks:

| Observation | Accepted result | Limit of the check |
|---|---|---|
| API return code | `VK_SUCCESS` or `VK_INCOMPLETE` | The test accepts either code at every capacity; it does not require `VK_INCOMPLETE` only for truncation. |
| Returned count | `min(countRequested, countReported)` | The expected count uses the initial null-output query as its reference. |
| Returned entries | Every entry below `countRetrieved` differs from `VK_OBJECT_TYPE_UNKNOWN` | The test does not check uniqueness, list stability, completeness against an independent list, or untouched entries beyond the returned count. |

The sentinel catches an unwritten returned slot, but a different unexpected enum value can pass this particular check. All explicit rejection paths throw `NotSupportedError`, including malformed enumeration responses; none returns a test-failure status directly ([query validation](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L74-L92)).

### `refresh_individual_objects` — record one-entry lists

The case queries the complete refreshable-type list, creates its representative objects, and maps object types to live handles or zero. It skips types absent from the device list and types whose local handle is zero. For each remaining entry it records a `VkRefreshObjectKHR` in a list with `objectCount == 1`, then records a pipeline barrier ([`vktObjectRefreshTests.cpp#L294-L320`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L294-L320)).

### `refresh_all_objects` — record one filtered batch

The case uses the same setup but follows the reported type-list order to build one compact vector. It looks up each reported type with `objectHandlesMap.at(objectType)`, omits entries whose mapped handle is zero, and writes `{objectType, objectHandle, 0}` at the next used position. One `VkRefreshObjectListKHR` contains `countUsed` entries, followed by one refresh command and the same barrier ([batch recording](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L321-L341)).

`all` means the selected entries in this batch, not all Vulkan objects or all reported types. The two branches also differ in lookup behavior: the individual branch walks the local map and ignores unrepresented reported types; the batch branch assumes that every reported type exists in the map. An absent map key would make `std::map::at` throw before recording the refresh command. That is a host-side coverage limitation, not evidence of a device refresh failure.

Neither branch asserts that filtering leaves a usable handle. With no selected entries, the individual branch records no refresh commands, while the batch branch still records a list with `objectCount == 0`. The page does not infer a nonempty-list guarantee from the initial nonzero type count.

## Shader Analysis

No shader participates. The refresh cases create or enumerate Vulkan objects and submit refresh commands; they do not execute a shader or check shader output.

## Runtime Execution and Result Checking

- Every leaf requires `VK_KHR_object_refresh` through `checkRefreshSupport()` ([`vktObjectRefreshTests.cpp#L360-L373`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L360-L373)).
- Each refresh case performs a null-output query and a full data query. A failed query or zero reported count raises `NotSupportedError` ([`vktObjectRefreshTests.cpp#L95-L110`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L95-L110)).
- The setup creates a command pool and primary command buffer, fence, semaphore, event, occlusion query pool, host-visible buffer and buffer view, sampler, sampler YCbCr conversion, image and image view, shader module, render pass, framebuffer, read-only application-storage pipeline cache, pipeline layout, compute pipeline, descriptor pool, descriptor-set layout, and descriptor set ([`vktObjectRefreshTests.cpp#L112-L256`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L112-L256)).
- `objectHandlesMap` stores live handles for created objects and zero for types such as instance, physical device, device, queue, command buffer, surface, swapchain, display, display mode, and debug messenger ([`vktObjectRefreshTests.cpp#L258-L289`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L258-L289)).
- The command buffer records refresh commands followed by a `VkMemoryBarrier` from `VK_ACCESS_TRANSFER_WRITE_BIT` to `VK_ACCESS_MEMORY_READ_BIT`, ends, and submits to the universal queue with `submitCommandsAndWait` ([`vktObjectRefreshTests.cpp#L291-L346`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L291-L346)). The barrier does not provide host-side read-back.
- The refresh cases return `pass("Pass")` after submission completes. The query case returns `pass("pass")` after its checks ([`vktObjectRefreshTests.cpp#L49-L92`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L49-L92), [`vktObjectRefreshTests.cpp#L343-L346`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L343-L346)).

### Object inventory and dependencies

Both refresh cases create the same objects before filtering by the device list. Creation is not conditional on whether that object's type will be refreshed. A failure in an unused candidate can therefore stop setup ([object creation](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L112-L256)).

| Resource set | Concrete setup | Role and coverage boundary | Evidence |
|---|---|---|---|
| Command resources | Reset-capable command pool in the universal queue family and one primary command buffer | The pool has a refreshable candidate handle. The command buffer records the test but its map entry is zero. | [Command allocation](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L113-L120), [map](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L258-L284) |
| Synchronization and queries | Fence, semaphore, event, and an occlusion query pool with one query | These provide candidate object handles. The command stream does not signal this semaphore, set this event, or begin/end an occlusion query. | [Creation](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L121-L132), [recording](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L294-L344) |
| Buffer, memory, and view | A 64-byte exclusive buffer with `TRANSFER_SRC` and `STORAGE_TEXEL_BUFFER` usage; host-visible memory; an `R32G32B32A32_SFLOAT` view covering the whole buffer | The map uses the buffer allocation's `VkDeviceMemory` as its device-memory candidate. Host visibility does not imply read-back: the test does not initialize or compare buffer contents. | [Buffer setup](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L133-L150), [memory candidate](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L263-L272) |
| Sampler and YCbCr conversion | Nearest filtering, clamp-to-edge sampler; separate `G8_B8_R8_3PLANE_420_UNORM` conversion with identity model, full range, midpoint chroma locations, and nearest chroma filtering | The sampler does not chain the conversion through `pNext`. Both are candidate handles; the test does not sample an image. | [Sampler setup](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L151-L187) |
| Image, memory, and view | A `64 × 64 × 1` optimal-tiled `R8G8B8A8_UNORM` image, one mip level, one layer, one sample; `TRANSFER_SRC` and `COLOR_ATTACHMENT` usage; allocated memory and a color image view | The image starts in `UNDEFINED` layout. The test records no layout transition or pixel write. It maps the image and view, but not the image allocation as a separate memory entry. | [Image setup](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L188-L211), [map](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L263-L284) |
| Render pass and framebuffer | Render pass matching the image format and a `64 × 64` framebuffer using its view | These provide live handles without starting a render pass or drawing. | [Creation](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L214-L215) |
| Pipeline objects | `comp` shader module, pipeline layout, compute pipeline, and a cache with `READ_ONLY` and `USE_APPLICATION_STORAGE` flags backed by the resource interface's cache data | The explicit cache is a refresh candidate. The `makeComputePipeline` call does not pass that cache handle. The command buffer does not bind or dispatch the pipeline. | [Pipeline setup](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L212-L226) |
| Descriptor objects | Pool allowing eight sets and eight sampler descriptors; layout with one sampler at binding zero visible to all shader stages; one allocated descriptor set | The test creates candidate pool/layout/set handles but does not update the set or bind it to a pipeline. | [Descriptor setup](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L227-L256) |

The map gives zero handles to `INSTANCE`, `PHYSICAL_DEVICE`, `DEVICE`, `QUEUE`, `COMMAND_BUFFER`, `SURFACE_KHR`, `SWAPCHAIN_KHR`, `DISPLAY_KHR`, `DISPLAY_MODE_KHR`, and `DEBUG_UTILS_MESSENGER_EXT` object types. Some corresponding context objects exist; zero means the test does not select them for refresh ([complete map](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L258-L289)).

### Recording, synchronization, and completion

The test sets each selected `VkRefreshObjectKHR::flags` to zero. Individual mode walks the type-keyed map and records a refresh command plus barrier for each selected handle; batch mode follows the query order and records one command plus barrier. Both modes use one primary command buffer and one queue submission ([recording branches](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L291-L344)).

Each barrier specifies `VK_PIPELINE_STAGE_TRANSFER_BIT` to `VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT`, with a global memory barrier from `VK_ACCESS_TRANSFER_WRITE_BIT` to `VK_ACCESS_MEMORY_READ_BIT`. The source supplies no buffer or image barriers. The extension classifies refresh accesses as transfer writes and requires the transfer stage in their synchronization scope ([specification](../../../../vulkan-docs/src/chapters/copies.adoc#L3170-L3178)). The test does not use the barrier to make shader output or application data available to a host comparison.

`submitCommandsAndWait()` creates a submission fence, checks `queueSubmit`, and waits for that fence with a checked `waitForFences` call. This fence is separate from the candidate fence in the object map ([submission helper](../../../framework/vulkan/vkCmdUtil.cpp#L283-L340)). The candidate objects remain in scope through the wait.

`vkCmdRefreshObjectsKHR` has no result return value. The refresh body reaches `pass("Pass")` after command-buffer completion and the submission wait; it performs no object-integrity check, SEU injection, or fault-data query ([completion](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L343-L346)). The extension even permits the implementation to ignore a supplied object whose internal data is not in SEU-susceptible memory ([specification note](../../../../vulkan-docs/src/chapters/copies.adoc#L3175-L3179)). Passing establishes successful execution of this command sequence, not recovery from demonstrated corruption.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `query_refreshable_objects` | Enumeration result code, count, or returned object-type handling does not satisfy the tested query contract. |
| `refresh_individual_objects` | One-entry refresh-list recording, repeated command processing, object/type pairing, or submission failed for the selected live handles. |
| `refresh_all_objects` | Batch-list construction, mixed-entry processing, object/type pairing, or submission failed for the selected live handles. |

### Cause Analysis

#### Enumeration contract or capability data

**Possible failure symptoms:** The query case raises `NotSupportedError` for an invalid result, zero initial count, unexpected returned count, or `VK_OBJECT_TYPE_UNKNOWN` entry.

**Possible implementation causes:** The implementation may mishandle null-versus-data queries, capacity truncation, `VK_INCOMPLETE`, returned counts, or type population. The test observes public query results and cannot locate the internal cause.

#### Object setup or handle/type pairing

**Possible failure symptoms:** A refresh case fails while creating an object, recording a selected entry, ending the command buffer, or waiting for submission.

**Possible implementation causes:** Setup may not produce the required live object, a handle may be paired with the wrong type, or refresh validation may reject a live handle. The map narrows the input but does not identify a failing member.

#### Individual-list processing

**Possible failure symptoms:** The individual case fails while the batch case passes, or submission fails after a one-entry command.

**Possible implementation causes:** The implementation may mishandle repeated `vkCmdRefreshObjectsKHR` recording or one-entry list traversal. The comparison does not prove a particular internal defect.

#### Batch-list processing

**Possible failure symptoms:** The batch case fails while the individual case passes, or the single refresh command cannot complete.

**Possible implementation causes:** The implementation may mishandle `objectCount`, list storage, mixed object types, or traversal of the compacted list. The source does not record per-entry results.

#### Shader and pipeline setup dependency

**Possible failure symptoms:** Setup fails while creating the `comp` shader module or compute pipeline.

**Possible implementation causes:** Shader package loading, compilation, or ordinary pipeline creation may have failed. This is a setup dependency; the source never dispatches the shader.

## Case Pruning

### Requirement-based pruning

All three leaves require `VK_KHR_object_refresh`. The query and refresh bodies also treat a zero reported refreshable-type count as unsupported ([`vktObjectRefreshTests.cpp#L49-L64`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L49-L64), [`vktObjectRefreshTests.cpp#L102-L110`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L102-L110)). The source has no format, limit, or generated-parameter gate.

### Design-based pruning

The family does not cover invalid handles, invalid flags, malformed list counts, every possible object type, or post-refresh object observation. The handle map leaves several types at zero and skips them. The default mustpass scope remains the three paths at [`sc.txt#L145-L147`](../../../mustpass/main/vksc-default/sc.txt#L145-L147).

## Key Takeaways

- The query case checks result codes, truncation counts, and returned types across boundary capacities.
- Refresh commands use the intersection of reported types and live handles created by the setup.
- The individual case records repeated one-entry lists; the all-object case records one filtered list.
- Passing means recording, ending, submitting, and waiting succeeded. It does not mean the test observed a changed object.
- The compute shader supports object creation only; the test never dispatches it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Root registration | [`createChildren()`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L56) | Places `object_refresh` below `sc`. |
| Case registration | [`createObjectRefreshTests()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L377-L388) | Defines the exact three leaves. |
| Query checks | [`queryRefreshableObjects()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L49-L92) | Defines capacity, result, count, and type validation. |
| Object setup | [`refreshObjects()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L95-L256) | Creates the representative handles and command resources. |
| Type-to-handle map | [`objectHandlesMap`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L258-L289) | Defines live and skipped object types. |
| Command recording and completion | [`refreshObjects()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L291-L346) | Defines individual/batch commands, barrier, submission, and pass result. |
| Minimal compute source | [`createComputeSource()`](../../../modules/vulkan/sc/vktObjectRefreshTests.cpp#L349-L357) | Defines the setup-only compute program. |
| Default SC coverage | [`sc.txt#L145-L147`](../../../mustpass/main/vksc-default/sc.txt#L145-L147) | Confirms the three registered paths. |