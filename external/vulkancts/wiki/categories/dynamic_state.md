# Dynamic State

## Overview

The dynamic_state category tests Vulkan's dynamic state mechanism, which allows certain pipeline state to be set dynamically at command buffer recording time rather than being baked into the pipeline object. Tests verify that dynamic state commands correctly override pipeline static state, that state persists across pipeline binds, and that dynamic state does not interfere with compute or transfer operations.

## Registration Entry Point

[`createTests()`](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L108) in `vktDynamicStateTests.cpp` creates the root group. The [`initDynamicStateTestGroup()`](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L74) function creates 7 pipeline construction type subgroups, each containing the same set of dynamic state test groups.

## Subgroup Structure

```text
dynamic_state
├── monolithic
│   ├── vp_state
│   ├── rs_state
│   ├── cb_state
│   ├── ds_state
│   ├── general_state
│   ├── inheritance
│   ├── image
│   ├── discard
│   ├── line_width
│   └── compute_transfer        (conditional)
├── pipeline_library
│   ├── vp_state
│   ├── rs_state
│   ├── cb_state
│   ├── ds_state
│   ├── general_state
│   ├── inheritance
│   ├── image
│   ├── discard
│   └── line_width
├── fast_linked_library
│   └── (same as pipeline_library)
├── shader_object_unlinked_spirv
│   ├── vp_state
│   ├── rs_state
│   ├── cb_state
│   ├── ds_state
│   ├── general_state
│   ├── inheritance
│   ├── image
│   ├── discard
│   ├── line_width
│   └── compute_transfer        (conditional)
├── shader_object_unlinked_binary
│   └── (same as pipeline_library)
├── shader_object_linked_spirv
│   └── (same as pipeline_library)
└── shader_object_linked_binary
    └── (same as pipeline_library)
```

The 7 pipeline construction type subgroups are created at [lines 78-95](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L78). The `compute_transfer` group is only added for `monolithic` and `shader_object_unlinked_spirv` construction types at [lines 63-65](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63).

## File Inventory

### Registration / dispatcher files

| File | Role | Group Name |
|---|---|---|
| [`vktDynamicStateTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L1) | Root registration | (root) |

### Implementation files

| File | Group Name | Level-3 Doc |
|---|---|---|
| [`vktDynamicStateVPTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateVPTests.cpp#L1) | `vp_state` | [vktDynamicStateVPTests.md](../testfiles/dynamic_state/vktDynamicStateVPTests.md) |
| [`vktDynamicStateRSTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1) | `rs_state` | [vktDynamicStateRSTests.md](../testfiles/dynamic_state/vktDynamicStateRSTests.md) |
| [`vktDynamicStateCBTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L1) | `cb_state` | [vktDynamicStateCBTests.md](../testfiles/dynamic_state/vktDynamicStateCBTests.md) |
| [`vktDynamicStateDSTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1) | `ds_state` | [vktDynamicStateDSTests.md](../testfiles/dynamic_state/vktDynamicStateDSTests.md) |
| [`vktDynamicStateGeneralTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L1) | `general_state` | [vktDynamicStateGeneralTests.md](../testfiles/dynamic_state/vktDynamicStateGeneralTests.md) |
| [`vktDynamicStateInheritanceTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1) | `inheritance` | [vktDynamicStateInheritanceTests.md](../testfiles/dynamic_state/vktDynamicStateInheritanceTests.md) |
| [`vktDynamicStateClearTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L1) | `image` | [vktDynamicStateClearTests.md](../testfiles/dynamic_state/vktDynamicStateClearTests.md) |
| [`vktDynamicStateDiscardTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L1) | `discard` | [vktDynamicStateDiscardTests.md](../testfiles/dynamic_state/vktDynamicStateDiscardTests.md) |
| [`vktDynamicStateLineWidthTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L1) | `line_width` | [vktDynamicStateLineWidthTests.md](../testfiles/dynamic_state/vktDynamicStateLineWidthTests.md) |
| [`vktDynamicStateComputeTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1) | `compute_transfer` | [vktDynamicStateComputeTests.md](../testfiles/dynamic_state/vktDynamicStateComputeTests.md) |

### Helper / utility files (no Level-3 docs)

| File | Purpose |
|---|---|
| [`vktDynamicStateBaseClass.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.cpp#L1) / [`.hpp`](../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Shared base class for dynamic state test instances with common Vulkan resource setup |
| [`vktDynamicStateTestCaseUtil.hpp`](../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1) | `InstanceFactory` template and support check helpers |

## Cross-File Recurring Test Families

### Dynamic state type coverage

The category covers Vulkan dynamic states organized by functional area:

| Functional Area | Dynamic States | Files |
|---|---|---|
| Viewport/Scissor | `VK_DYNAMIC_STATE_VIEWPORT`, `VK_DYNAMIC_STATE_SCISSOR`, `VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT_EXT`, `VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT_EXT` | VP, General, Compute, Discard |
| Rasterization | `VK_DYNAMIC_STATE_LINE_WIDTH`, `VK_DYNAMIC_STATE_DEPTH_BIAS`, `VK_DYNAMIC_STATE_DEPTH_BIAS_CLAMP` | RS, LineWidth, Compute, Discard |
| Color Blend | `VK_DYNAMIC_STATE_BLEND_CONSTANTS` | CB, Compute, Discard, Clear |
| Depth/Stencil | `VK_DYNAMIC_STATE_DEPTH_BOUNDS`, `VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK`, `VK_DYNAMIC_STATE_STENCIL_WRITE_MASK`, `VK_DYNAMIC_STATE_STENCIL_REFERENCE` | DS, Compute, Discard |
| Extended Dynamic State | `VK_DYNAMIC_STATE_CULL_MODE_EXT`, `VK_DYNAMIC_STATE_FRONT_FACE_EXT`, `VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY_EXT`, and 9 more | Compute |
| NV/EXT extensions | `VK_DYNAMIC_STATE_DISCARD_RECTANGLE_EXT`, `VK_DYNAMIC_STATE_VIEWPORT_W_SCALING_NV`, etc. | Compute |

### Mesh shader variants

Most implementation files create both traditional vertex-shader and mesh-shader variants of their tests (suffixed `_mesh`), excluded on Vulkan SC builds. This pattern is observed in VP, RS, CB, DS, and General test files.

## Cross-File Recurring Parameter Dimensions

| Dimension | Values | Files |
|---|---|---|
| Pipeline construction type | `MONOLITHIC`, `LINK_TIME_OPTIMIZED_LIBRARY`, `FAST_LINKED_LIBRARY`, `SHADER_OBJECT_UNLINKED_SPIRV`, `SHADER_OBJECT_UNLINKED_BINARY`, `SHADER_OBJECT_LINKED_SPIRV`, `SHADER_OBJECT_LINKED_BINARY` | All files (from root) |
| Shader type | Vertex+Fragment vs. Mesh+Fragment | VP, RS, CB, DS, General |
| Vulkan SC exclusion | `#ifndef CTS_USES_VULKANSC` guards | VP, RS, CB, DS, General, Inheritance, Compute |

## Cross-File Recurring Support Requirements

| Requirement | Files |
|---|---|
| `VK_EXT_mesh_shader` | VP, RS, CB, DS, General (all mesh variants) |
| `DEVICE_CORE_FEATURE_WIDE_LINES` | RS, LineWidth |
| `DEVICE_CORE_FEATURE_DEPTH_BOUNDS` | DS |
| `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` | RS |
| `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` + `MULTI_VIEWPORT` | VP (viewport_array) |
| `VK_NV_inherited_viewport_scissor` | Inheritance |
| `VK_EXT_extended_dynamic_state` | Inheritance (with-count variants), Compute |
| `VK_EXT_nested_command_buffer` | Inheritance (nested variants) |
| Pipeline construction requirements | All files |

## Cross-File Recurring Verification Methods

| Method | Threshold | Files |
|---|---|---|
| `tcu::fuzzyCompare()` | 0.05f | VP, RS, CB, DS, General (state_switch, bind_order, state_persistence), Clear, Discard |
| `tcu::floatThresholdCompare()` | 0.0f (exact) | RS (nonzero), General (static_stencil_mask_zero, double_static_bind) |
| `tcu::dsThresholdCompare()` | 0.0f | General (static_stencil_mask_zero) |
| Pixel counting | N/A | LineWidth |
| CPU reference rasterization + exact comparison | N/A | Inheritance |
| Buffer content comparison | N/A | Compute |

## Notes

- The root registration file creates 7 pipeline construction type subgroups, each containing the same set of dynamic state tests. This means every test is effectively run 7 times with different pipeline construction modes.
- The `compute_transfer` group is only registered for `monolithic` and `shader_object_unlinked_spirv` construction types.
- The `image` group name (from `vktDynamicStateClearTests.cpp`) refers to image manipulation commands (clear, blit, copy, resolve) being tested for non-interference with dynamic state, not to image-related dynamic state.
