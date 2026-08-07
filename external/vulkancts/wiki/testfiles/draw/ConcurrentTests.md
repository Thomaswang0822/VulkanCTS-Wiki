## Overview

**Core question:** Can independent compute and graphics submissions on separate logical devices and queues both complete correctly while they are in flight in the same test?

This page documents `vktDrawConcurrentTests.cpp`. The implementation registers one fixed test case, `compute_and_triangle_list`, under the render-pass path and three non-nested dynamic-rendering command-buffer paths. It creates a second logical device and queue for compute work, uses the normal context device and universal queue for graphics work, submits the two workloads separately, waits for both fences, and validates the rendered image. Normal Vulkan execution, and Vulkan SC subprocess execution, also validate the storage-buffer result.

The workloads do not share resources and have no producer-consumer dependency: the compute shader modifies a storage buffer, while the graphics pipeline renders to a separate color target. The intended contract is that each independent submission remains correct while both may be in flight. The current source has a device-interface mismatch in the draw fence and submission path; this source-level issue is described under `Submission and ordering` and `Failure Meaning`.

## Background Knowledge

For the shared concepts of render passes, dynamic rendering, and result readback, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- Different Vulkan queues may be scheduled independently. Submission to one queue does not implicitly order work on another queue, and independent resources need no cross-queue memory dependency.
- A logical device owns its queues and device-level objects. A device-level function pointer obtained for one device must be called only with that device or one of its child objects; this ownership rule is necessary to understand the source-level mismatch discussed later.
- Host writes to mapped memory must be made available to the device, and shader writes must be made available and visible before host readback. Flush/invalidate operations and buffer memory barriers provide the relevant host/device transitions.
- A fence is a device object associated with a queue submission. Waiting for it lets the host observe completion of that submission; it does not create a dependency on an independent submission to another queue.

Relevant Vulkan specification topics are [device queues](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#devsandqueues), [fences](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#synchronization-fences), [host access types](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#synchronization-host-access-types), [`vkGetDeviceProcAddr`](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/vkGetDeviceProcAddr.html), and [`vkWaitForFences`](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/vkWaitForFences.html).

## Registration Hierarchy

```text
draw.renderpass.concurrent
└── compute_and_triangle_list
draw.dynamic_rendering.primary_cmd_buff.concurrent
└── compute_and_triangle_list
draw.dynamic_rendering.partial_secondary_cmd_buff.concurrent
└── compute_and_triangle_list
draw.dynamic_rendering.complete_secondary_cmd_buff.concurrent
└── compute_and_triangle_list
```

`concurrent` and `compute_and_triangle_list` are the exact identifiers registered by `ConcurrentDrawTests`. The shared draw dispatcher instantiates the family once for the render-pass path and once for each non-nested dynamic-rendering command-buffer path. It deliberately omits `concurrent` from the two nested secondary-command-buffer paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|---|---|---|---|
| Rendering path | `renderpass`; `dynamic_rendering.primary_cmd_buff`; `dynamic_rendering.partial_secondary_cmd_buff`; `dynamic_rendering.complete_secondary_cmd_buff` | Selects legacy render-pass recording or one of the supported primary/secondary dynamic-rendering arrangements. | [`createTests` and `createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198) |
| Test case | `compute_and_triangle_list` | Selects the one fixed pair of independent compute and graphics workloads. | [`ConcurrentDrawTests::init`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L535-L546) |
| Graphics shaders | `vulkan/draw/VertexFetch.vert`, `vulkan/draw/VertexFetch.frag` | Produces a blue rectangle only when the fetched reference vertex indices match `gl_VertexIndex`. | [`testSpec`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L537-L541) |
| Compute shader | `vulkan/draw/ConcurrentPayload.comp` | Replaces every storage-buffer value with its bitwise complement. | [`testSpec`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L537-L541), [`ConcurrentPayload.comp`](../../../data/vulkan/draw/ConcurrentPayload.comp) |
| Graphics topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` | Interprets the six drawn vertices as two triangles. | [`testSpec`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L537-L541) |
| Compute input and dispatch | 1024 `uint32_t` values; `vkCmdDispatch(1, 1, 1)` | One compute invocation loops over all 1024 elements. | [`numValues`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L117), [`dispatch`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L303-L312) |
| Graphics draw call | `vkCmdDraw(..., 6, 1, 2, 0)` | Draws six vertices beginning at vertex 2; only the first stored rectangle is consumed. | [`graphics recording`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L333-L395) |

## Behavior Parameters

This test family has no varying behavioral axis. Its sole test case always runs one storage-buffer compute workload and one triangle-list graphics workload, then checks their outputs independently. The rendering path changes command-buffer and rendering setup, not the property checked by the fixed case.

## Shader Analysis

`ConcurrentPayload.comp` has a `1 x 1 x 1` local size. Because the host dispatches one workgroup, its sole invocation loops over the complete 1024-element storage buffer and replaces each value with its bitwise complement.

`VertexFetch.vert` forwards the input color only when `gl_VertexIndex` equals the fetched `in_refVertexIndex`; otherwise it emits red. For the six vertices beginning at `firstVertex = 2`, the stored reference indices are 2 through 7, so the expected rectangle is blue. `VertexFetch.frag` forwards that color unchanged. The buffer and image checks therefore validate the outputs of the compute and graphics shader paths separately; neither shader consumes the other workload's output.

## Runtime Execution and Result Checking

```text
Choose physical device and compute queue family
  -> create custom compute device and queue
  -> allocate host-visible storage buffer and fill 1024 random uint32 values
  -> bind buffer to ConcurrentPayload.comp and record barriers + dispatch
  -> prepare shared graphics draw and record the selected rendering path
  -> submit compute and graphics to their queues with separate fences
  -> wait for both fences
  -> validate bitwise-NOT buffer result and fuzzy image result
```

### Compute workload

The implementation searches physical-device queue families for the first family advertising `VK_QUEUE_COMPUTE_BIT`. If none is found, it throws `NotSupportedError` with `Compute queue couldn't be created`. A custom device is created with that family and one queue. The buffer is host-visible, contains 1024 values generated from deterministic seed `0x82ce7f`, and is bound as one storage-buffer descriptor.

The compute command buffer binds `ConcurrentPayload.comp`, inserts the host-write/compute-read buffer barrier, dispatches one workgroup (`vkCmdDispatch(1, 1, 1)`), and inserts the compute-write/host-read barrier. The shader's result contract is one bitwise complement per input value.

### Graphics workload

`ConcurrentDraw` derives from `DrawTestsBaseClass`. Its vertex data contains two setup vertices, 1000 repetitions of the same six-vertex blue rectangle, and one trailing vertex. The draw starts at vertex 2 and consumes only six vertices, so only the first repeated rectangle reaches the graphics pipeline. The remaining repetitions enlarge the allocated and uploaded vertex buffer but do not increase the GPU draw count.

The base class handles graphics pipeline and attachment setup. Depending on `SharedGroupParams`, the source records legacy rendering, primary-command-buffer dynamic rendering, or one of two secondary-command-buffer dynamic-rendering arrangements. The graphics queue is `m_context.getUniversalQueue()` on the normal context device.

### Submission and ordering

The compute submission has no wait or signal semaphores and is sent to the custom compute queue with `computeFence`. The intended graphics submission likewise has no semaphores and targets the universal draw queue with `drawFence`. This lack of cross-queue synchronization is deliberate because the workloads are independent. Both fence waits are attempted before a wait error is returned.

The current source does not consistently use the two devices' dispatch interfaces. It constructs `vk` as a `DeviceDriver` for the custom compute device, then passes the context device and its universal queue through that compute-device interface when creating `drawFence`, submitting the graphics command buffer, and waiting for `drawFence` ([source](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L217-L230), [draw path](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L397-L437)). The Vulkan requirement for a device-specific function pointer is that its first dispatchable object be that device or one of its children. The page therefore documents the intended draw submission and the observed mismatch, rather than claiming that this source path is valid.

### Result checking

After both waits, normal Vulkan builds invalidate the compute allocation and require every element to equal `~inputData[ndx]`. A mismatch reports the index, reference, result, and input value. In Vulkan SC, both the wait-result checks and the compute-buffer comparison are inside the subprocess-only block, so a non-subprocess run proceeds directly to graphics validation.

The graphics reference is opaque black with an opaque blue rectangle inside `ReferenceImageCoordinates`. The color attachment is read in `VK_IMAGE_LAYOUT_GENERAL` and compared with `tcu::fuzzyCompare` at threshold `0.05`; an image mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

The fixed case can fail through a fence wait, a compute-buffer mismatch, or an image mismatch. These observations localize the failure to completion of one submission or to the corresponding independent workload; an image mismatch is not evidence that graphics failed to consume compute output, because no such data flow exists.

### Cause Analysis

The source-level mismatch below can invalidate both submission observations. If that path is corrected, the remaining checks localize failures as follows.

#### Device-interface mismatch in the source

**Possible failure symptoms:** Device/queue validation errors, a draw submission or fence wait that does not complete successfully, or inability to reach reliable output validation.

**Possible implementation causes:** This is an unresolved CTS source-level issue, not an inferred implementation defect. `vk` is constructed for `computeDevice` at lines 217-230, but it is used with `drawDevice` and `drawQueue` at lines 400 and 428-437. The Vulkan [`vkGetDeviceProcAddr` requirement](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/vkGetDeviceProcAddr.html) restricts a returned device function pointer to its device and that device's children.

#### Compute completion or output

**Possible failure symptoms:** The compute fence wait fails, or at least one of the 1024 elements differs from the bitwise complement of its saved input.

**Possible implementation causes:** On a valid submission path, investigate compute command execution, descriptor or pipeline binding, shader execution, mapped-memory flush/invalidate handling, and the host/compute buffer barriers.

#### Graphics completion or output

**Possible failure symptoms:** The draw fence wait fails, or the captured image differs from the black-and-blue reference beyond the fuzzy comparison threshold.

**Possible implementation causes:** On a valid submission path, investigate graphics command recording and execution, vertex fetching and `gl_VertexIndex`, primitive assembly and rasterization, color attachment handling, and image readback.

## Case Pruning

### Requirement-based pruning

- A queue family with `VK_QUEUE_COMPUTE_BIT` is required; otherwise the test throws `NotSupportedError` rather than reporting a conformance failure.
- A dynamic-rendering path requires `VK_KHR_dynamic_rendering` through `context.requireDeviceFunctionality`.
- Dynamic rendering is excluded from Vulkan SC by the dispatcher build guard.

### Design-based pruning

- The dispatcher omits `concurrent` from the nested partial and nested complete secondary-command-buffer paths because `createChildren` adds it only when `nestedSecondaryCmdBuffer` is false.
- The family has one fixed case. Shared-resource, semaphore, queue-family ownership-transfer, and compute-to-graphics producer-consumer variants are outside its design.

## Key Takeaways

- `compute_and_triangle_list` runs independent compute and graphics workloads on separate logical devices and queues; the graphics shader does not consume the compute buffer.
- The Vulkan mustpass contains the render-pass path and three non-nested dynamic-rendering paths, while nested secondary-command-buffer paths are intentionally omitted.
- A passing result requires the 1024-element bitwise-NOT buffer check and the fuzzy blue-rectangle image check to succeed after the fence waits.
- The current source routes draw-device operations through the compute device's `DeviceDriver`; this remains an unresolved source-level defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test implementation | [`ConcurrentDraw::iterate`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L101-L518) | Creates both workloads, submits them, and checks their results. |
| Compute setup and recording | [queue, device, buffer, pipeline, barriers, and dispatch](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L117-L324) | Defines the custom compute path and its output contract. |
| Graphics recording | [rendering-path branches and draw](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L326-L395) | Defines the supported graphics command-buffer arrangements. |
| Submission and validation | [fences, submissions, waits, and checks](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L397-L518) | Exposes the device-interface mismatch and both result oracles. |
| Family registration | [`ConcurrentDrawTests`](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L528-L546) | Supplies the exact `concurrent.compute_and_triangle_list` identifiers. |
| Draw dispatcher | [`createChildren` and `createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198) | Places the family under render-pass and non-nested dynamic-rendering paths. |
| Shared draw base | [`DrawTestsBaseClass`](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L51-L216) | Creates the graphics resources, pipeline, vertex buffer, and attachment barriers. |
| Shader inputs | [`ConcurrentPayload.comp`](../../../data/vulkan/draw/ConcurrentPayload.comp), [`VertexFetch.vert`](../../../data/vulkan/draw/VertexFetch.vert), [`VertexFetch.frag`](../../../data/vulkan/draw/VertexFetch.frag) | Defines the compute complement and blue-rectangle shader outputs. |
| Vulkan mustpass | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L346), [`renderpass entry`](../../../mustpass/main/vk-default/draw.txt#L17808), [`Vulkan SC entry`](../../../mustpass/main/vksc-default/draw.txt#L330) | Confirms the registered Vulkan variants and Vulkan SC render-pass path. |
| Class declaration | [`vktDrawConcurrentTests.hpp`](../../../modules/vulkan/draw/vktDrawConcurrentTests.hpp) | Declares the family and its shared group parameters. |
