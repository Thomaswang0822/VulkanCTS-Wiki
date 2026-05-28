# [vktDrawPointClampTests.cpp](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L1)

## Overview

Tests that `glPointSize` is properly clamped to the device's `pointSizeRange[1]` limit. This file (~402 lines) renders a single point with a size exceeding the maximum allowed point size and verifies that the implementation clamps the rendered point to the correct maximum dimensions.

## Role of File

Implementation-heavy test file for the `point_size_clamp` subgroup. Contains the test instance function, shader creation, and a single leaf test case.

## Source Code

- Primary source: [vktDrawPointClampTests.cpp](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L1)
- Header: [vktDrawPointClampTests.hpp](../../../modules/vulkan/draw/vktDrawPointClampTests.hpp#L1)
- Parent-category registration: [createTests()](../../../modules/vulkan/draw/vktDrawTests.cpp#L126)

## Registration Hierarchy

```text
draw.renderpass.point_size_clamp
└── point_size_clamp_max
```

The `point_size_clamp` group is registered by [`createDrawPointClampTests()`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L393) and is added directly to the `renderpass` group at [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L140). It does not appear under the `dynamic_rendering` variant branch, making it renderpass-only.

Evidence:
- `point_size_clamp` group added at [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L140)
- Leaf test case added at [`vktDrawPointClampTests.cpp`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L397)

## Test Families

### point_size_clamp_max — Point size clamped to maximum

The `point_size_clamp_max` leaf test case at [`vktDrawPointClampTests.cpp`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L397) is registered via `addFunctionCaseWithPrograms`. It renders a single point with `glPointSize` set to `floor(maxPointSizeRange * 2.0)`, which is deliberately above the device's maximum point size limit. The framebuffer width is sized to accommodate the maximum point size (`ceil(maxPointSizeRange * 0.5) + 1`).

Implementation: The [`renderPointSizeClampTest()`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L93) function creates a 1-row framebuffer, renders a single point using `VK_PRIMITIVE_TOPOLOGY_POINT_LIST` with push constants for the point size, and compares the result against a reference image where the point is drawn at the clamped maximum size. The vertex shader at [`createPointSizeClampProgs()`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L59) reads the point size from push constants and assigns it to `gl_PointSize`.

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Point size | `floor(maxPointSizeRange * 2.0)` (exceeds device limit) |
| Framebuffer width | `ceil(maxPointSizeRange * 0.5) + 1` |
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_POINT_LIST` |

## Support / Feature Requirements

- `largePoints` device feature (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L387))

## Verification Methods

- **Float threshold comparison**: [`tcu::floatThresholdCompare()`](../../../modules/vulkan/draw/vktDrawPointClampTests.cpp#L380) with zero threshold. Reference image is cleared to the point color (black), then the clear color (green) is set at pixel (0,0). The test verifies the rendered point matches the clamped reference, confirming that `glPointSize` was properly clamped to `pointSizeRange[1]`.

## Notes

- Renderpass-only: added directly to the `renderpass` group, not via `createChildren()`, so it does not appear under `dynamic_rendering` variants
- The test uses a push constant to set the point size from the application side, ensuring the oversized value reaches the implementation
- The framebuffer is only 1 pixel tall, since the point is centered vertically and the test only needs to verify horizontal extent clamping
