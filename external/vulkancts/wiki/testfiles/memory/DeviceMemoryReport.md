## Overview

**Core question:** Does `VK_EXT_device_memory_report` emit complete, correctly identified callback records for device-memory allocation, release, import, and unimport events?

- This page covers the three test families implemented and registered by [`vktMemoryDeviceMemoryReportTests.cpp`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp): `create_and_destroy_object`, `vk_device_memory`, and `external_memory`.
- The tests install a device-memory report callback when creating a device, perform an operation that can consume or expose device memory, and inspect the recorded events after the relevant objects have been destroyed.
- The three families check complementary parts of the callback contract: lifecycle pairing across many object types, detailed fields for a direct `VkDeviceMemory` allocation, and identity continuity across external-memory imports.

## Background Knowledge

For the shared concepts memory types, heaps, and resource compatibility, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- [`VK_EXT_device_memory_report`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L2785-L2812) lets an application register a callback during device creation. The implementation invokes it once for each device-memory event, including allocations that Vulkan applications do not otherwise see directly. The callback is intended for memory-tracking and debugging tools.
- A [callback record](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L2835-L2881) identifies an event type, the associated Vulkan object and handle, a device-memory object ID, a size, and a heap index. `memoryObjectId` identifies the underlying memory, while `objectHandle` identifies the Vulkan object associated with a particular report.
- Importing one external allocation into several `VkDeviceMemory` objects creates several Vulkan object handles for the same underlying memory. The specification defines `memoryObjectId` as the identity used to avoid double-counting and requires a system-wide unique ID for imported external memory. Their reports therefore need distinct `objectHandle` values but the same [`memoryObjectId`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L2883-L2895).

## Registration Hierarchy

```text
memory.device_memory_report
├── create_and_destroy_object
├── vk_device_memory
└── external_memory
```

The `memory` test category registers this test family only for Vulkan, not Vulkan SC, through [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L78). The source then registers the three intermediate nodes shown above in [`createDeviceMemoryReportTests()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2199-L2357).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Behavior family | `create_and_destroy_object`, `vk_device_memory`, `external_memory` | Selects lifecycle pairing, detailed `VkDeviceMemory` field checks, or external-memory identity checks. | [Group registration](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2349-L2355) |
| Object case in `create_and_destroy_object` | 41 leaves covering device, memory, buffer, buffer view, image, image view, synchronization, query, shader/pipeline, descriptor, framebuffer, command-pool, and command-buffer objects | Exercises allocations associated with object types and object configurations that may consume device memory. | [Object case definitions](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2238-L2322) |
| Buffer size and use | 1 KiB and 16 MiB uniform or storage buffers | Varies the requested object size and usage without changing lifecycle validation. | [Buffer cases](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2244-L2261) |
| Image or image-view shape | 1D, 2D, 3D; array, cube, and cube-array views | Covers allocations associated with several image shapes and view types. | [Image and view cases](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2270-L2280) |
| Direct allocation | `allocate_and_free` with 1024 bytes and memory type index 0 | Gives the test fixed expected values for size and heap validation. | [`vkDeviceMemoryAllocateAndFreeTest()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1766-L1847) |
| External handle type | `opaque_fd`, `opaque_win32`, `opaque_win32_kmt`, `android_hardware_buffer`, `dma_buf` | Selects the native export/import mechanism and its extension requirements. | [External-memory case generation](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2175-L2194) |

The canonical mustpass list contains all 47 executable leaves: 41 object cases, one direct allocation case, and five external-memory cases. See [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L855-L901).

## Behavior Parameters

The primary behavioral axis is the intermediate node immediately below `memory.device_memory_report`. Each value changes the callback property under test.

### `create_and_destroy_object`: lifecycle pairing across object types

Each leaf constructs one selected Vulkan object and its dependencies inside a scope, then destroys them as scope-owned handles leave that scope. The callback validator tracks every `ALLOCATE` or `IMPORT` record by `(memoryObjectId, objectHandle)`. A matching `FREE` or `UNIMPORT` record must consume that pair, and no pair may remain afterward. It also rejects out-of-range heap indices on `ALLOCATE` and `ALLOCATION_FAILED` records.

The `device` leaf creates the callback-enabled device directly. Other leaves create a separate callback-enabled device so allocations made by the surrounding CTS device do not enter the recorder. Some leaves compile shaders as inputs for shader-module or pipeline creation, but the test does not execute those shaders.

### `vk_device_memory`: direct allocation record fields

The single `allocate_and_free` leaf calls `vkAllocateMemory` for 1024 bytes from memory type 0 and then calls `vkFreeMemory`. Markers set immediately before both calls let the test confirm that each matching callback occurred during the expected API operation. The allocate record must report `VK_OBJECT_TYPE_DEVICE_MEMORY`, a nonzero `memoryObjectId`, a size of at least 1024 bytes, and the heap selected by memory type 0. The free record must reuse the allocation's `memoryObjectId`.

### `external_memory`: identity across export, import, and release

Each leaf allocates exportable memory for a buffer, exports a native handle, duplicates that handle, and imports the same underlying allocation into two dedicated `VkDeviceMemory` objects. The test expects reports for the original allocation, both imports, both unimports, and the original release. All relevant records must carry `VK_OBJECT_TYPE_DEVICE_MEMORY`, sufficient size, and one shared nonzero `memoryObjectId`, even though the three Vulkan memory handles differ.

## Shader Analysis

Shader code is not part of the tested behavior. The `shader_module`, `graphics_pipeline`, and `compute_pipeline` object leaves compile minimal programs only so the host can create those Vulkan objects and observe any associated memory reports. No shader is dispatched or drawn, and no shader output contributes to pass or fail.

## Runtime Execution and Result Checking

- Every path first checks `VK_EXT_device_memory_report` support and the `deviceMemoryReport` feature. Device creation chains `VkDeviceDeviceMemoryReportCreateInfoEXT` with the recorder callback and enables the feature.
- `CallbackRecorder` copies each callback structure together with the current host marker. Validation occurs only after the operations and scoped destruction have completed.
- `create_and_destroy_object` creates the selected object plus required dependencies, destroys all scope-owned objects, and calls `validateCallbackRecords()`. The case passes only if heap indices are valid and all tracked allocation/import pairs are consumed by matching release events.
- `vk_device_memory` filters records by the allocated memory handle. It requires one valid allocate record and one free record, checks marker timing and record fields, and requires both records to share the same memory ID.
- `external_memory` filters by the original and imported handles. It requires the original allocation or import report, two import reports, two unimport reports, and the final free or unimport report. All six observations must use the same memory ID.
- An `ALLOCATION_FAILED` callback is accepted as an informative event after its heap index has been checked. It does not stand in for any lifecycle event that a specific case requires.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `create_and_destroy_object` | Invalid heap reporting, a missing or out-of-order lifecycle report, or mismatched identity between a reported allocation/import and its release. |
| `vk_device_memory` | Missing direct allocation/free callbacks, callback timing inconsistent with the API calls, or incorrect object type, memory ID, size, or heap fields. |
| `external_memory` | Missing import/unimport lifecycle reports, incorrect report fields, or failure to preserve the underlying allocation's identity across imports. |

### Cause Analysis

#### Invalid or unpaired object lifecycle reports

**Possible failure symptoms:** `validateCallbackRecords()` sees an `ALLOCATE` or `ALLOCATION_FAILED` heap index outside the advertised heap range, sees a `FREE` or `UNIMPORT` pair that was never recorded, or finishes with an unmatched `ALLOCATE` or `IMPORT` pair. The CTS result is `Invalid device memory report callback`.

**Possible implementation causes:** The implementation may report the wrong heap for an internal allocation, omit one side of an object's allocation lifecycle, emit a release before its matching acquisition report, or change `memoryObjectId` or `objectHandle` between paired events. The extension requires reported internal allocations to use advertised heaps and exists to associate memory use with Vulkan objects; broken pairing prevents a memory tracker from maintaining that association.

#### Incorrect direct `VkDeviceMemory` callback data

**Possible failure symptoms:** The test cannot find both expected callbacks for the allocation handle, a callback carries the wrong host marker, the allocate record has the wrong object type, zero or inconsistent `memoryObjectId`, a size below 1024 bytes, or a heap index different from the heap selected by memory type 0.

**Possible implementation causes:** The device-memory reporting path may construct callback data from the wrong allocation metadata, invoke the callback outside the allocation or free call being processed, or fail to retain one identity value through `vkAllocateMemory` and `vkFreeMemory`. Using the wrong memory-type-to-heap mapping can also produce the observed heap mismatch.

#### Broken external-memory identity or lifecycle reporting

**Possible failure symptoms:** One of the two imports or unimports is absent, the original allocation/release event is absent, a report has the wrong object type or insufficient size, or an imported handle receives a `memoryObjectId` different from the original allocation.

**Possible implementation causes:** The external-memory import path may assign identity per `VkDeviceMemory` handle instead of per underlying native allocation, or it may classify import destruction as an ordinary free rather than an unimport. It may also fail to propagate allocation size and identity metadata from export to import. Such behavior makes tools double-count shared external memory or lose track of its import lifetime.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_EXT_device_memory_report` and the `deviceMemoryReport` feature.
- The cube-array image-view leaf also requires the `imageCubeArray` core feature.
- External-memory leaves require `VK_KHR_external_memory_capabilities`, `VK_KHR_dedicated_allocation`, and `VK_KHR_get_memory_requirements2` when those capabilities are not core. Handle-specific device extensions must also be present.
- The external buffer configuration must advertise both exportable and importable support for the selected handle type. Otherwise the case reports `NotSupported` instead of testing an illegal combination.

### Design-based pruning

The source registers only five external handle types: opaque FD, opaque Win32, opaque Win32 KMT, Android hardware buffer, and DMA-BUF. It does not generate every value of `VkExternalMemoryHandleTypeFlagBits`. The object matrix also uses representative sizes, flags, layouts, and object configurations rather than a Cartesian product because its target is callback lifecycle behavior, not exhaustive validation of each object's creation parameters.

## Key Takeaways

- `create_and_destroy_object` checks whether callback records form a balanced lifecycle across 41 representative object cases.
- `vk_device_memory` checks the precise callback fields and timing for one controlled allocation.
- `external_memory` checks that three Vulkan memory handles referring to one native allocation share one `memoryObjectId` while retaining separate object handles and import lifetimes.
- Shader compilation supports several object-creation leaves, but no shader executes and shader behavior is outside the pass condition.
- See [Failure Meaning](#failure-meaning) for the specific symptoms and likely implementation areas associated with each behavior family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Callback recorder and callback-enabled device | [`CallbackRecorder` and `createDeviceWithMemoryReport()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L61-L209) | Captures report data and installs the callback during device creation. |
| Shared lifecycle validator | [`validateCallbackRecords()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1662-L1720) | Defines heap-range and allocation/import pairing checks. |
| Object lifecycle execution | [`createDestroyObjectTest()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1737-L1764) | Creates and destroys each object case, then applies shared validation. |
| Direct memory execution and checks | [`vkDeviceMemoryAllocateAndFreeTest()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1766-L1847) | Checks timing, object type, identity, size, heap, and callback presence. |
| External-memory support and execution | [External-memory path](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L1859-L2172) | Selects required extensions, exports and imports memory, and validates shared identity. |
| Registration and parameter definitions | [`createDeviceMemoryReportTests()`](../../../modules/vulkan/memory/vktMemoryDeviceMemoryReportTests.cpp#L2199-L2357) | Defines all object leaves and registers the three intermediate nodes. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L78) | Places `device_memory_report` under the `memory` test category. |
| Mustpass inventory | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L855-L901) | Confirms the 47 executable paths in the default Vulkan mustpass set. |
| Extension semantics | [`VK_EXT_device_memory_report`](../../../../vulkan-docs/src/appendices/VK_EXT_device_memory_report.adoc#L17-L27) | Describes callback purpose, hidden device allocations, and debugging-tool use. |
| Heap and external identity rationale | [Extension issues](../../../../vulkan-docs/src/appendices/VK_EXT_device_memory_report.adoc#L64-L71) | Explains import identity tracking through `memoryObjectId`. |
