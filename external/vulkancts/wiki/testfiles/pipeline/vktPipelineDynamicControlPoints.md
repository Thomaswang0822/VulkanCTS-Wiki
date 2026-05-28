# vktPipelineDynamicControlPoints.cpp

## Overview

[`vktPipelineDynamicControlPoints.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1) implements the [`dynamic_control_points`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L433) topic group. It verifies dynamic patch control points functionality, testing that `vkCmdSetPatchControlPointsEXT` correctly sets the number of control points at command buffer time.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDynamicControlPoints.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1)
- Header: [`vktPipelineDynamicControlPoints.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_control_points
├── change_output
├── change_winding
└── change_output_winding
```

Source: [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L431).

## Test Families

### change_output — Changing tessellation control point output count

Tests switching pipelines with dynamic control points while changing the number of tessellation control shader invocations. Uses `vkCmdSetPatchControlPointsEXT` to dynamically set different control point counts between draws.

### change_winding — Changing winding with dynamic control points

Tests switching pipelines with dynamic control points while switching the winding order. Verifies that culling behavior is correct when the patch control point count is set dynamically and the winding direction changes between draws.

### change_output_winding — Changing both output count and winding

Tests switching pipelines with dynamic control points while simultaneously changing both the number of tessellation control shader invocations and the winding order. Combines the aspects tested in `change_output` and `change_winding` into a single test case.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Control point count | Dynamic state | Set via `vkCmdSetPatchControlPointsEXT` |
| Winding order | Test config | Normal / reversed |
| Cull mode | Test config | None / front |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_extended_dynamic_state` | Required for dynamic patch control points |
| `VK_EXT_extended_dynamic_state2` | Required for dynamic patch control points |
| `tessellationShader` | Required for tessellation tests |

## Verification Methods

- **Rendering comparison**: Set patch control points dynamically, render tessellated geometry, compare against expected output
- **Control point count verification**: Verify that the correct number of control points is used

## Notes

- This is a direct child of each variant root, not nested under another topic group
