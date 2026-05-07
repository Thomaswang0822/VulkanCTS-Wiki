# vktPipelineExtendedDynamicStateTests.cpp

## Overview

[`vktPipelineExtendedDynamicStateTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L1) implements the [`extended_dynamic_state`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6978) topic group. It verifies VK_EXT_extended_dynamic_state and VK_EXT_extended_dynamic_state3 functionality, testing dynamically set pipeline state including cull mode, front face, rasterization, logic op, color blend, depth bounds, depth test, stencil test, vertex input, and many more dynamic state parameters.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineExtendedDynamicStateTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L1)
- Header: [`vktPipelineExtendedDynamicStateTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.hpp#L1)

## Registration Path

[`createExtendedDynamicStateTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6977) returns the `extended_dynamic_state` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Not extra shader-object. Skipped by extra shader-object variants.

## Test Hierarchy

```text
extended_dynamic_state
└── {dynamic_state_test}
    ├── cull_none, cull_back, cull_front, cull_front_and_back
    ├── front_face_cw, front_face_ccw, front_face_cw_reversed, front_face_ccw_reversed
    ├── disable_raster, enable_raster
    ├── logic_op_or, logic_op_enable, logic_op_disable
    ├── color_blend_enable, color_blend_disable
    ├── depth_bias, depth_bias_clamped
    ├── depth_bounds, depth_bounds_clamped
    ├── depth_test_enable, depth_test_disable
    ├── stencil_test_enable, stencil_test_disable
    ├── vertex_input
    ├── patch_control_points
    ├── rasterizer_discard_enable, rasterizer_discard_disable
    ├── color_write_enable
    ├── tess_domain_origin
    ├── depth_clamp_enable, depth_clamp_disable
    ├── polygon_mode
    ├── sample_mask
    ├── line_stipple
    └── ... (many more EDS3 states)
```

## Test Families

| Family | Description |
|---|---|
| ExtendedDynamicStateTest | Verifies dynamically set pipeline state produces correct rendering results |
| EDS1 tests | VK_EXT_extended_dynamic_state: cull mode, front face, viewport, scissor, etc. |
| EDS3 tests | VK_EXT_extended_dynamic_state3: logic op, color blend, vertex input, etc. |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-extra-shader-object variant types |
| Dynamic state type | Enum | All EDS1 and EDS3 states |
| State ordering | Enum | Static-first, dynamic-first |
| VK_EXT_extended_dynamic_state | Extension | Required for EDS1 tests |
| VK_EXT_extended_dynamic_state3 | Extension | Required for EDS3 tests |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_extended_dynamic_state` | Required for EDS1 tests |
| `VK_EXT_extended_dynamic_state3` | Required for EDS3 tests |
| `VK_KHR_maintenance10` | Required for some maintenance10-related tests |
| Various feature gates | Per-test depending on state type |

## Verification Methods

- **Rendering comparison**: Set state dynamically, render, compare against expected output
- **State ordering test**: Verify that dynamic state overrides static state correctly
- **Feature gate check**: Verify that unsupported dynamic states are properly rejected

## Notes

- This is one of the largest test files in the pipeline category
- EDS3 tests are conditionally registered based on extension support
- The file uses a custom `TestGroupWithClean` class for resource cleanup
