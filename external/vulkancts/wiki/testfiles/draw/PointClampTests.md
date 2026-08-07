## Overview

**Core question:** Does `gl_PointSize` clamp an oversized point to the device's advertised maximum point size?

- This page covers `vktDrawPointClampTests.cpp`, which implements the `draw.renderpass.point_size_clamp` test family.
- Its only registered test case, `point_size_clamp_max`, supplies a point size above `pointSizeRange[1]` and checks the rendered extent.
- The test uses a one-row color attachment, a vertex push constant, a point-list draw, image-to-buffer readback, and an exact pixel comparison.
- The source entry points and registration evidence are collected in the [Source Reference Appendix](#source-reference-appendix).

## Background Knowledge

- Vulkan exposes the supported point-size interval through `VkPhysicalDeviceLimits::pointSizeRange`. The upper endpoint limits the rasterized size when a vertex shader writes `gl_PointSize`.
- A render pass writes the color attachment, while the test later copies that image into a host-visible buffer. The comparison therefore checks the complete path from point-size handling through rasterization, attachment writes, and readback.

## Registration Hierarchy

```text
draw.renderpass.point_size_clamp
└── point_size_clamp_max
```

`vktDrawTests.cpp` adds `point_size_clamp` directly to the `renderpass` group. The dispatcher creates a separate `dynamic_rendering` branch, but this family is not added there. The same leaf appears in both the Vulkan and Vulkan SC mustpass files.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case | `point_size_clamp_max` | Exercises the upper point-size limit with one fixed oversized input | [`createDrawPointClampTests`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L393-L400) |
| Point size | `floor(maxPointSizeRange * 2.0)` | Supplies a value intended to exceed `pointSizeRange[1]` | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L105-L114) |
| Render size | `ceil(maxPointSizeRange * 0.5) + 1` by `1` pixel | Provides horizontal space for the clamped point and keeps the vertical extent to one row | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L107-L124) |
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_POINT_LIST` | Makes the draw contain one point primitive | [`makeGraphicsPipeline`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L263-L278) |
| Point position | `x = 2 * (fbWidthSize - 0.25) / fbWidthSize - 1`, `y = 0` | Places the point near the right edge while its center lies on the single framebuffer row | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L120-L124) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Defines the attachment and readback pixel format | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L102-L104), [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L366-L370) |

## Behavior Parameters

The primary behavioral axis is the single registered test case. The source does not generate a broader matrix; the fixed case targets the maximum point-size clamp.

### `point_size_clamp_max`: upper point-size clamp

The test reads the device's maximum point size, doubles it, and floors the result before passing it to the vertex shader through a push constant. The vertex shader assigns that value to `gl_PointSize`. The draw then uses `VK_PRIMITIVE_TOPOLOGY_POINT_LIST`, so the observed coverage depends on the implementation applying the device limit rather than accepting the oversized value unchanged.

## Shader Analysis

The source builds two GLSL programs in `createPointSizeClampProgs`:

- The vertex shader accepts position at location `0` and color at location `1`. A one-float push-constant block named `pointSizeBlk` supplies `psize`; `main` writes it to `gl_PointSize`, copies the input position to `gl_Position`, and forwards the color.
- The fragment shader receives the flat color and writes it to the color attachment.

The shader contains no branching or generated value matrix. The behavior under test comes from the rasterizer's handling of the vertex shader's oversized `gl_PointSize` value. The source shader construction is at [`createPointSizeClampProgs`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L59-L91).

## Runtime Execution and Result Checking

- The test creates an `R8G8B8A8_UNORM` image and a one-row framebuffer whose width is derived from the device limit. It also creates a host-visible vertex buffer and a host-visible readback buffer.
- It builds a graphics pipeline with the generated vertex and fragment shaders, a push-constant range for one vertex-stage float, and `VK_PRIMITIVE_TOPOLOGY_POINT_LIST`.
- Before drawing, it records a host-write-to-vertex-read memory barrier and transitions the color image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`.
- The command buffer begins a render pass with green as the clear color, binds the pipeline and vertex buffer, pushes `testPointSize`, and draws one vertex. The test then copies the image to the readback buffer and waits for completion.
- The reference image is black except for pixel `(0, 0)`, which is set to green. The host compares the reference and result with `tcu::floatThresholdCompare` using a zero threshold. A mismatch returns `fail`; an exact match returns `pass("Rendering succeeded")`.

The complete draw, synchronization, copyback, and comparison path is in [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L93-L385).

## Failure Meaning

### Failure Cause Mapping

Because this page has one fixed behavioral value, the failure mapping is a direct statement rather than a multi-row matrix.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `point_size_clamp_max` | Incorrect point-size clamping or rasterized coverage; vertex input, push-constant handling, shader compilation, render-pass execution, image copyback, or result comparison errors can also produce the observed mismatch. |

### Cause Analysis

#### Point-size handling and rasterized coverage

**Possible failure symptoms:** The result buffer differs from the reference at one or more pixels. The test expects black point coverage with green at `(0, 0)`; any other value fails the zero-threshold comparison.

**Possible implementation causes:** The implementation may apply the maximum point-size limit incorrectly, rasterize the clamped point with the wrong coverage, or mishandle the oversized `gl_PointSize` value. The source establishes the input and expected coverage, but it does not isolate which pipeline stage caused a mismatch.

#### Command, resource, or comparison path

**Possible failure symptoms:** The same exact pixel mismatch can arise even when point-size rasterization is correct if the vertex buffer, push constant, attachment contents, image-to-buffer copy, host invalidation, or format interpretation is wrong.

**Possible implementation causes:** The inspected test source does not distinguish these causes after the readback. Investigating the test log and the implementation's handling of the relevant Vulkan commands would be required to identify the failing stage.

## Case Pruning

### Requirement-based pruning

`checkSupport` rejects the case when the device does not advertise `largePoints`. Such a device receives `NotSupportedError("Large points not supported")`, so the test does not run and does not report a rendering failure. The support check is at [`checkSupport`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L387-L391).

### Design-based pruning

The source registers one fixed maximum-clamp case. It does not generate point-size, topology, format, or rendering-mode variants. The one-row framebuffer and fixed colors keep the check focused on the horizontal extent and the selected reference pixel.

## Key Takeaways

- `point_size_clamp_max` pushes `floor(pointSizeRange[1] * 2.0)` into the vertex shader, then relies on the implementation to clamp `gl_PointSize`.
- The case runs under `draw.renderpass.point_size_clamp` and is not registered under the dispatcher's `dynamic_rendering` branch.
- A zero-threshold image comparison checks the final attachment contents after draw, copyback, and host readback, so a failure identifies an incorrect result but does not by itself localize the responsible stage.
- Devices without `largePoints` are skipped as unsupported rather than marked as failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Shader construction | [`createPointSizeClampProgs`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L59-L91) | Defines the vertex push constant, `gl_PointSize` assignment, and fragment output. |
| Test execution and comparison | [`renderPointSizeClampTest`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L93-L385) | Defines limits, resources, pipeline, draw, synchronization, readback, reference image, and pass/fail logic. |
| Support gate and registration | [`checkSupport` and `createDrawPointClampTests`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L387-L400) | Checks `largePoints` and registers the sole test case. |
| Renderpass dispatcher | [`createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L142) | Places `point_size_clamp` under `draw.renderpass`. |
| Vulkan mustpass evidence | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28976) | Lists `dEQP-VK.draw.renderpass.point_size_clamp.point_size_clamp_max`. |
| Vulkan SC mustpass evidence | [`draw.txt`](../../../mustpass/main/vksc-default/draw.txt#L1528) | Lists `dEQP-VKSC.draw.renderpass.point_size_clamp.point_size_clamp_max`. |
| Source declaration | [`vktDrawPointClampTests.hpp`](../../../modules/vulkan/draw/vktDrawPointClampTests.hpp#L35) | Declares the registration factory used by the dispatcher. |
