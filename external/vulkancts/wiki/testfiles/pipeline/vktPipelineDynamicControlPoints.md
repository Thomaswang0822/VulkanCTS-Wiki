# vktPipelineDynamicControlPoints.cpp

## Overview

[`vktPipelineDynamicControlPoints.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1) implements the [`dynamic_control_points`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L433) topic group. It verifies dynamic patch control points functionality, testing that `vkCmdSetPatchControlPointsEXT` correctly sets the number of control points at command buffer time.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDynamicControlPoints.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1)
- Header: [`vktPipelineDynamicControlPoints.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.hpp#L1)

## Registration Path

[`createDynamicControlPointsTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L431) returns the `dynamic_control_points` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
dynamic_control_points
├── change_output
├── change_input_output
└── change_input_output_with_mesh
```

## Test Families

| Family | Description |
|---|---|
| DynamicControlPointsTestCase | Verifies dynamic patch control points with tessellation shaders |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Control point count | Array | Various tessellation control point counts |
| Use mesh shader | Bool | With/without mesh shader variant |

## Support/Feature Requirements

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
