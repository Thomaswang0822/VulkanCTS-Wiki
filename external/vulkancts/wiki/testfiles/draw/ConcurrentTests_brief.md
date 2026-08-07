# Understanding Brief: Concurrent Draw Tests

## One-Sentence Test Purpose

This test verifies that independent compute and graphics submissions can execute through separate queues and both produce correct, observable results.

## Background Knowledge

A Vulkan queue executes command buffers submitted to it, while different queues may be scheduled independently. Queue completion is observed with fences. The compute command buffer uses buffer memory barriers for host-write → compute-read and compute-write → host-read visibility; the graphics target is handled by the shared draw infrastructure.

## Exact Registration

```text
draw.renderpass.concurrent
└── compute_and_triangle_list
```

The exact leaf identifier is `compute_and_triangle_list`. The source registers graphics shaders `VertexFetch.vert`/`VertexFetch.frag`, compute shader `ConcurrentPayload.comp`, and `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`.

## One Concrete Example

The case fills a host-visible storage buffer with 1024 deterministic random `uint32_t` values, dispatches `vkCmdDispatch(1, 1, 1)` to bitwise-NOT each value, and records a six-vertex blue rectangle draw with `vkCmdDraw(..., 6, 1, 2, 0)`. It submits both command buffers with separate fences, waits for both, checks every buffer element against `~inputData[ndx]`, and fuzzy-compares the rendered image with a black-and-blue reference.

## End-to-End Test Flow

```text
Select compute queue family -> create custom compute device and buffer
-> record barriers, descriptor binding, and compute dispatch
-> record graphics render-pass/dynamic-rendering draw
-> submit compute and graphics separately with fences
-> wait for both -> validate buffer and image
```

## Generated Test Artifacts and Bound Resources

- Custom compute device, one `VK_QUEUE_COMPUTE_BIT` queue, command pool, command buffer, descriptor set, storage buffer, and compute pipeline.
- Host-visible buffer containing 1024 `uint32_t` values; host writes are flushed before submission and the allocation is invalidated before readback.
- Graphics vertex buffer with 1000 repeated six-vertex blue rectangles, graphics pipeline, color attachment, and optional secondary command buffer according to `SharedGroupParams`.

## What Is Checked

- Missing compute queue: `NotSupportedError` (`Compute queue couldn't be created`).
- Compute fence and draw fence are waited independently; failures report which queue failed.
- Compute output: each result must equal the bitwise complement of its input.
- Graphics output: the color attachment must match the generated blue-rectangle reference through `tcu::fuzzyCompare` with threshold `0.05`.
- In VulkanSC builds, compute readback comparison is gated to subprocess mode.

## Behavior Parameter Identification

The primary behavior is the fixed `compute_and_triangle_list` workload. The rendering setup varies through shared draw parameters: legacy render pass, dynamic rendering when supported, and supported secondary-command-buffer modes. Queue selection, barriers, two fences, buffer readback, and image comparison are the synchronization and observation mechanisms.

## What Failure Means

| Failure | Likely area |
|---|---|
| No compute queue | Queue-family support or device selection |
| Compute wait failure | Compute submission or custom-device execution |
| Buffer mismatch | Host visibility, barriers, descriptor, dispatch, or compute shader |
| Draw wait failure | Graphics submission or command recording |
| Image mismatch | Vertex/pipeline/rendering setup or image readback |

## Important Variations and Special Cases

- Dynamic rendering requires `VK_KHR_dynamic_rendering`.
- Compute and graphics use separate resources; this is not a cross-queue shared-resource ownership-transfer test.
- VulkanSC resource reservation and pipeline-cache setup is conditional on the build and subprocess/resource-interface state.
- Both fence waits are attempted before reporting a wait failure so the other queue is not left hanging.

## Source Mapping

- [registration and exact identifiers](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L390-L407)
- [compute queue/device and buffer setup](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L80-L239)
- [barriers and dispatch](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L240-L257)
- [graphics recording and submissions](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L258-L350)
- [dual validation](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L351-L389)
- [class declaration](../../../modules/vulkan/draw/vktDrawConcurrentTests.hpp)

## Questions / Risk Points for User Audit

- Confirm the active dispatcher path when matching the case against a particular render-pass or dynamic-rendering mustpass.
- Confirm the implementation’s queue-family choice on a device where the first compute-capable family is also universal.
- Confirm the VulkanSC subprocess distinction before interpreting absent compute readback logs as missing validation.

## Conversion Notes for Final Wiki Rewrite

Preserve `concurrent` and `compute_and_triangle_list` exactly. Keep the obsolete `vktDrawConcurrentTests.md` page unchanged; this brief supports the replacement `ConcurrentTests.md` only.
