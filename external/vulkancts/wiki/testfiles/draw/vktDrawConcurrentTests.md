# vktDrawConcurrentTests.cpp

## Overview

Tests that exercise concurrent execution of a compute workload and a graphics draw workload on separate queues. The compute queue performs a bitwise NOT operation on a buffer, while the graphics queue renders a blue rectangle using `vkCmdDraw`. Both queues are submitted simultaneously, and the results of both operations are validated independently.

## Role

This file provides the `concurrent` test group, which validates that compute and graphics queues can operate concurrently without interfering with each other. This tests the implementation's ability to handle multi-queue submissions and ensures memory isolation between concurrent operations on different queue families.

## Source Code

- [vktDrawConcurrentTests.cpp](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.concurrent
└── compute_and_triangle_list
```

## Test Families

### compute_and_triangle_list — Concurrent compute and graphics draw

Creates a separate compute device and queue, fills a storage buffer with 1024 random uint32 values, and submits a compute shader that performs a bitwise NOT on each value. Simultaneously submits a graphics draw command that renders a blue rectangle using `vkCmdDraw(cmdBuffer, 6, 1, 2, 0)` (instanceCount=1) with `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`, while the vertex buffer contains 1000 repeated copies of the triangle data (6000 vertices total) to increase the graphics workload. Both submissions are fenced and waited upon. The compute result is validated by checking `bufferPtr[ndx] == ~inputData[ndx]` for each value. The graphics result is validated by fuzzy image comparison against a reference blue rectangle.

The test creates a custom device for the compute queue using `createCustomDevice` to ensure a separate queue family is used. The draw uses shaders `VertexFetch.vert` and `VertexFetch.frag`, while the compute uses `ConcurrentPayload.comp`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Rendering variant | renderpass, dynamic_rendering, secondary_cmd_buffer | Controlled by `SharedGroupParams` (not nested variants only) |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| `VK_QUEUE_COMPUTE_BIT` queue | Always required; test throws `NotSupportedError` if no compute queue family is found |
| `VK_KHR_dynamic_rendering` | When `groupParams.useDynamicRendering` is true |

## Verification Methods

The test performs **dual validation**:

1. **Compute validation**: After both fences are signaled, the storage buffer is read back and each value is compared against the expected bitwise NOT of the input: `bufferPtr[ndx] == ~inputData[ndx]`. Any mismatch results in a test failure with a detailed message including the index, reference, result, and input values (see [iterate](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L456-L475)).

2. **Graphics validation**: The rendered image is compared against a manually constructed reference image (blue rectangle on black background) using `tcu::fuzzyCompare` with threshold 0.05, using `ReferenceImageCoordinates` for the expected bounds (see [iterate](../../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L478-L518)).

Additionally, fence wait failures are detected separately as `ERROR_WAIT_COMPUTE` or `ERROR_WAIT_DRAW` to ensure both queues complete correctly.

## Notes

- The compute device is created separately from the main context device using `createCustomDevice`, which allows selecting a compute-capable queue family that may differ from the graphics queue family.
- On VulkanSC builds, the compute validation (buffer comparison) is only performed in subprocess mode (`isSubProcess()`).
- The vertex buffer contains 1000 repeated copies of the 6-vertex triangle data (6000 vertices total) to increase the graphics workload, making concurrent execution more likely. Only a single instance is drawn (instanceCount=1).
- The `ConcurrentDraw` class inherits from `DrawTestsBaseClass` and uses the standard `TestSpecBase` for its test specification.
