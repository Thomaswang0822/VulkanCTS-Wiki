# [vktDrawIndirectInstancedTests.cpp](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L1)

## Overview

Tests for instanced indirect drawing via `vkCmdDrawIndirect`. This file (~630 lines) verifies that indirect draw commands correctly handle instanced rendering with various instance counts and first-instance values. The test uses a reference renderer to compare GPU output against CPU-rendered reference images.

## Role of File

Implementation-heavy test file for the `indirect_instanced` subgroup. Contains the `DrawIndirectInstancedCase` test case class, the `DrawIndirectInstancedInstance` test instance class, and reference shader classes for CPU-side rendering.

## Source Code

- Primary source: [vktDrawIndirectInstancedTests.cpp](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L1)
- Header: [vktDrawIndirectInstancedTests.hpp](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.hpp#L1)
- Parent-category registration: [createChildren()](../../../modules/vulkan/draw/vktDrawTests.cpp#L70)

## Registration Hierarchy

```text
draw.renderpass.indirect_instanced
├── 1
├── 2
├── 4
└── 16
```

The `indirect_instanced` group is registered by [`createIndirectInstancedTests()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L607) and appears under both `draw.renderpass` and `draw.dynamic_rendering` variant branches. The hierarchy tree above uses the `draw.renderpass` variant as the representative path. Under `draw.dynamic_rendering`, the group appears in the `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `nested_partial_secondary_cmd_buff`, and `nested_complete_secondary_cmd_buff` sub-variants.

Evidence:
- `indirect_instanced` group added at [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L100)
- Leaf test cases added from [`vktDrawIndirectInstancedTests.cpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L617) through [`vktDrawIndirectInstancedTests.cpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L624)

## Test Families

### 1 — Single indirect draw

The `1` leaf test case at [`vktDrawIndirectInstancedTests.cpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L615) tests `vkCmdDrawIndirect` with `drawCount=1`. A single `VkDrawIndirectCommand` is submitted, and the test iterates over multiple instance counts (0, 1, 2, 4, 20) and first-instance values (1, 3, 4, 20) internally within the test instance.

### 2 — Two indirect draws

The `2` leaf test case tests `vkCmdDrawIndirect` with `drawCount=2`. Two `VkDrawIndirectCommand` structures are submitted in sequence, each with the same instance count and first-instance value but different vertex offsets.

### 4 — Four indirect draws

The `4` leaf test case tests `vkCmdDrawIndirect` with `drawCount=4`. Four indirect draw commands are submitted, requiring `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT` support.

### 16 — Sixteen indirect draws

The `16` leaf test case tests `vkCmdDrawIndirect` with `drawCount=16`. This exercises the multi-draw indirect path with a larger draw count, requiring `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT` and sufficient `maxDrawIndirectCount` device limit.

Implementation: The [`DrawIndirectInstancedInstance::iterate()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L292) method iterates over instance counts and first-instance indices, preparing vertex data with [`prepareVertexData()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L446), creating indirect draw command buffers, and rendering via [`draw()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L492). The GPU output is compared against a CPU reference rendered using the `rr::Renderer` with custom [`TestVertShader`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L68) and [`TestFragShader`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L99) classes.

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Draw count | `1`, `2`, `4`, `16` |
| Instance count (internal) | `0`, `1`, `2`, `4`, `20` |
| First instance (internal) | `1`, `3`, `4`, `20` |
| Quad grid size | `8x8` |
| Framebuffer size | `128x128` |

## Support Requirements

- `DEVICE_CORE_FEATURE_DRAW_INDIRECT_FIRST_INSTANCE` (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L566))
- `VK_KHR_dynamic_rendering` when using dynamic rendering variant (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L570))
- `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT` when drawCount > 1 (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L573))
- `maxDrawIndirectCount` device limit >= drawCount when drawCount > 1 (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L577))

## Verification Methods

- **Fuzzy comparison**: [`tcu::fuzzyCompare()`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L438) with threshold 0.05. The GPU-rendered image is compared against a CPU reference image generated by the `rr::Renderer` using custom vertex and fragment shaders that replicate the GPU shader behavior. The reference renderer accounts for instance indexing and first-instance offsets.

## Notes

- Not nested variants only: the test does not appear under the `nested_partial_secondary_cmd_buff` and `nested_complete_secondary_cmd_buff` dynamic rendering sub-variants (it is excluded by the `nestedSecondaryCmdBuffer` guard in [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L72))
- The test uses instanced vertex attributes (binding 1 with `VK_VERTEX_INPUT_RATE_INSTANCE`) for per-instance colors
- Vertex positions are scaled by `1/instanceCount` in the X dimension to tile instances horizontally
- The `beginSecondaryCmdBuffer()` method is gated by `!CTS_USES_VULKANSC` at [`vktDrawIndirectInstancedTests.cpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L506)
