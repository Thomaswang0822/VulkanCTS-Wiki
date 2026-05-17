# [vktDrawMultiExtTests.cpp](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1)

## Overview

Tests for the `VK_EXT_multi_draw` extension, which provides `vkCmdDrawMultiEXT` and `vkCmdDrawMultiIndexedEXT` commands that allow submitting multiple draw calls in a single command. This file (~1640 lines) exercises a deeply nested parameter space covering mesh types, draw types, draw counts, strides, instance counts, shader stages, and multiview, verifying both color and stencil output against CPU-generated reference images.

## Role of File

Implementation-heavy test file for the `multi_draw` subgroup. Contains the `MultiDrawTest` test case class, the `MultiDrawInstance` test instance class, draw info packing logic, triangle generation classes, and the full test registration hierarchy.

## Source Code

- Primary source: [vktDrawMultiExtTests.cpp](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1)
- Header: [vktDrawMultiExtTests.hpp](../../../modules/vulkan/draw/vktDrawMultiExtTests.hpp#L1)
- Parent-category registration: [createChildren()](../../../modules/vulkan/draw/vktDrawTests.cpp#L70)

## Registration Hierarchy

```text
draw.renderpass.multi_draw
├── mosaic
└── overlapping
```

The `multi_draw` group is registered by [`createDrawMultiExtTests()`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1396) and appears under both `draw.renderpass` and `draw.dynamic_rendering` variant branches. The hierarchy tree above uses the `draw.renderpass` variant as the representative path. Under `draw.dynamic_rendering`, the group appears in the `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, `nested_partial_secondary_cmd_buff`, and `nested_complete_secondary_cmd_buff` sub-variants, though with reduced test counts when secondary command buffers are used.

Evidence:
- `multi_draw` group added at [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L104) (gated by `!CTS_USES_VULKANSC`)
- Subgroups added from [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1400) through [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1634)

## Test Families

### mosaic — Mosaic mesh multi-draw tests

The `mosaic` subgroup at [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1403) uses the `TriangleMosaicGenerator` to create small triangles centered on each pixel of a 32x32 framebuffer (1024 triangles total). Each triangle covers only its target pixel, allowing per-pixel verification of draw index, instance index, and stencil increments.

Direct children of `mosaic`:

- **normal** — Non-indexed multi-draw via `vkCmdDrawMultiEXT`
- **indexed_mixed** — Indexed multi-draw via `vkCmdDrawMultiIndexedEXT` with `VertexOffsetType::MIXED` (no `pVertexOffset`, per-struct offsets vary)
- **indexed_random** — Indexed multi-draw with `VertexOffsetType::CONSTANT_RANDOM` (constant `pVertexOffset`, random per-struct offsets)
- **indexed_packed** — Indexed multi-draw with `VertexOffsetType::CONSTANT_PACK` (constant `pVertexOffset`, packed stride that omits the offset member)

Each draw-type group contains `no_draws`, `one_draw`, `16_draws`, `max_draws` subgroups for draw count, which in turn contain `stride_zero`, `standard_stride`, `stride_extra_4`, `stride_extra_12` subgroups for stride, then `no_instances`, `1_instance`, `10_instances`, `2_instances_base_3` subgroups for instance parameters, then `vert_only`, `with_geom`, `with_tess`, `tess_geom` subgroups for shader stages, and finally `single_view`, `multiview` leaf groups. Leaf test cases are named `no_offset` or `offset_6` (for indexed draws), with an optional `_no_draw_id` suffix when `gl_DrawID` is not used.

Implementation: The [`MultiDrawInstance::iterate()`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L823) method creates a 32x32 color attachment (`VK_FORMAT_R8G8B8A8_UINT`) and depth/stencil attachment, generates mosaic triangle vertices, packs draw info structures with the [`DrawInfoPacker`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L246) class, and submits multi-draw commands. Verification compares both color and stencil buffers against reference images.

### overlapping — Overlapping mesh multi-draw tests

The `overlapping` subgroup at [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1403) uses the `TriangleOverlapGenerator` to create full-screen triangles at decreasing depth values (0.75 to 0.25). Depth testing is enabled, so only the front-most triangle survives per pixel. This tests that multi-draw correctly handles depth ordering across draw calls.

Direct children of `overlapping`:

- **normal** — Non-indexed multi-draw with depth test enabled
- **indexed_mixed** — Indexed multi-draw with mixed vertex offsets and depth test
- **indexed_random** — Indexed multi-draw with random constant vertex offsets and depth test
- **indexed_packed** — Indexed multi-draw with packed stride and depth test

The nesting structure below each draw-type group mirrors the `mosaic` family, with the constraint that overlapping meshes skip instanced cases (`instanceCount > 1`) since the depth test makes instancing with overlapping triangles impractical.

Implementation: Same as mosaic but uses [`TriangleOverlapGenerator`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L213) which generates full-screen triangles with varying Z. Depth compare op is `VK_COMPARE_OP_LESS` for non-indexed and `VK_COMPARE_OP_GREATER` for indexed (due to reversed index order). Stencil increments verify all draws occurred.

## Parameter Dimensions

| Parameter | Observed Values |
|-----------|----------------|
| Mesh type | `mosaic`, `overlapping` |
| Draw type | `normal`, `indexed_mixed`, `indexed_random`, `indexed_packed` |
| Draw count | `0` (no_draws), `1` (one_draw), `16` (16_draws), `1024` (max_draws) |
| Stride | `0` (stride_zero), base size (standard_stride), base+4 (stride_extra_4), base+12 (stride_extra_12) |
| Instance count | `0` (no_instances), `1` (1_instance), `10` (10_instances), `2` with firstInstance=3 (2_instances_base_3) |
| Shader stages | `vert_only`, `with_geom`, `with_tess`, `tess_geom` |
| Multiview | `single_view`, `multiview` |
| Draw ID | enabled (default), disabled (`_no_draw_id` suffix) |
| Vertex offset | `no_offset`, `offset_6` (indexed draws only) |

## Support Requirements

- `VK_EXT_multi_draw` extension (checked at [`checkSupport()`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L423))
- `VK_KHR_shader_draw_parameters` when `drawId` is true
- `DEVICE_CORE_FEATURE_TESSELLATION_SHADER` when `useTessellation` is true
- `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` when `useGeometry` is true
- Multiview feature (`multiview`) when `multiview` is true
- `multiviewTessellationShader` when both multiview and tessellation are enabled
- `multiviewGeometryShader` when both multiview and geometry are enabled
- `VK_KHR_dynamic_rendering` when using dynamic rendering variant

## Verification Methods

- **Color buffer**: Integer threshold comparison via [`tcu::intThresholdCompare()`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1383) with zero threshold. Reference color encodes draw index in R/G channels, instance index in B channel (as 255-index), and view index in A channel (as 255-view).
- **Stencil buffer**: Depth-stencil threshold comparison via [`tcu::dsThresholdCompare()`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1387) with 0.0 threshold. Reference stencil value equals `(instanceCount * stencilIncrements) % 256` using `VK_STENCIL_OP_INCREMENT_AND_WRAP`.
- **Reference generation**: CPU-side reference images are generated in the iterate loop at [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1314-L1377), accounting for stride-zero repetition, indexed draw reversal, and mixed-mode vertex offsets.

## Notes

- VK only: gated by `!CTS_USES_VULKANSC` at registration in [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103)
- When secondary command buffers are used in dynamic rendering variants, test counts are reduced: only `mosaic` mesh type, only `CONSTANT_RANDOM` offset type, and only `one_draw` draw count are tested
- For draw counts > 1, stride must be at least the base structure size and aligned to 4 bytes (VUID-vkCmdDrawMultiEXT-drawCount-09628 / VUID-vkCmdDrawMultiIndexedEXT-drawCount-09629)
- Overlapping meshes skip instanced cases (instanceCount > 1) per assertion at [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1583)
- The `DrawInfoPacker` class handles stride-zero as a special case where all draw info entries overlap at the same memory location
- For packed indexed draws, extra padding bytes are appended to satisfy VUID-vkCmdDrawMultiIndexedEXT-drawCount-04940
