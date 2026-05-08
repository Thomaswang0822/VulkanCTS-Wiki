# vktDynamicStateComputeTests.cpp

## Overview

[`vktDynamicStateComputeTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1) implements the [`compute_transfer`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1194) subgroup of the dynamic_state category. It tests that setting graphics dynamic state commands before or after compute dispatch or transfer operations does not interfere with the correct execution of those operations.

## Role

Implementation file.

## Registration Path

This file contributes the group returned by [`createDynamicStateComputeTests()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1188) (named `"compute_transfer"`), which is conditionally attached under the `monolithic` and `shader_object_unlinked_spirv` pipeline construction type subgroups by [`createChildren()`](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63).

## Test Hierarchy

```text
compute_transfer
├── single
│   ├── compute
│   │   ├── viewport
│   │   │   ├── before
│   │   │   └── after
│   │   ├── scissor
│   │   │   ├── before
│   │   │   └── after
│   │   ├── line_width
│   │   │   ├── before
│   │   │   └── after
│   │   ├── depth_bias
│   │   │   ├── before
│   │   │   └── after
│   │   ├── blend_constants
│   │   │   ├── before
│   │   │   └── after
│   │   ├── depth_bounds
│   │   │   ├── before
│   │   │   └── after
│   │   ├── stencil_compare_mask
│   │   │   ├── before
│   │   │   └── after
│   │   ├── stencil_write_mask
│   │   │   ├── before
│   │   │   └── after
│   │   ├── stencil_reference
│   │   │   ├── before
│   │   │   └── after
│   │   ├── discard_rectangle_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── sample_locations_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── ray_tracing_pipeline_stack_size_khr  (non-VulkanSC)
│   │   │   ├── before
│   │   │   └── after
│   │   ├── fragment_shading_rate_khr
│   │   │   ├── before
│   │   │   └── after
│   │   ├── line_stipple_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── cull_mode_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── front_face_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── primitive_topology_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── viewport_with_count_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── scissor_with_count_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── vertex_input_binding_stride_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── depth_test_enable_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── depth_write_enable_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── depth_compare_op_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── depth_bounds_test_enable_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── stencil_test_enable_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── stencil_op_ext
│   │   │   ├── before
│   │   │   └── after
│   │   ├── viewport_w_scaling_nv          (non-VulkanSC)
│   │   │   ├── before
│   │   │   └── after
│   │   ├── viewport_shading_rate_palette_nv  (non-VulkanSC)
│   │   │   ├── before
│   │   │   └── after
│   │   ├── viewport_coarse_sample_order_nv   (non-VulkanSC)
│   │   │   ├── before
│   │   │   └── after
│   │   └── exclusive_scissor_nv              (non-VulkanSC)
│   │       ├── before
│   │       └── after
│   └── transfer
│       └── (same state subgroups as compute)
└── multi
    ├── compute
    │   ├── before
    │   └── after
    └── transfer
        ├── before
        └── after
```

Source: [`createDynamicStateComputeTests()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1188).

## Test Families

### 1. Single-state tests

The `single` subgroup tests one dynamic state at a time. For each of the 27-30 dynamic states in [`dynamicStateList[]`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474), it creates tests under both `compute` and `transfer` operations, with `before` and `after` variants.

### 2. Multi-state tests

The `multi` subgroup tests multiple dynamic states together. It uses the first 10 "basic" states (viewport through stencil_reference) that have no extension requirements, testing them all at once under both `compute` and `transfer` operations.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Operation type | `COMPUTE` or `TRANSFER` from [`OperType`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L769) |
| When to set | `BEFORE` or `AFTER` from [`WhenToSet`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L773) |
| Dynamic state | 27-30 values from [`dynamicStateList[]`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L474) (single tests), first 10 basic states (multi tests) |

### Dynamic state list with extension requirements

| Dynamic State | Extension Requirement |
|---|---|
| VIEWPORT, SCISSOR, LINE_WIDTH, DEPTH_BIAS, BLEND_CONSTANTS, DEPTH_BOUNDS, STENCIL_COMPARE_MASK, STENCIL_WRITE_MASK, STENCIL_REFERENCE | (none) |
| DISCARD_RECTANGLE_EXT | `VK_EXT_discard_rectangles` |
| SAMPLE_LOCATIONS_EXT | `VK_EXT_sample_locations` |
| RAY_TRACING_PIPELINE_STACK_SIZE_KHR | `VK_KHR_ray_tracing_pipeline` (non-VulkanSC) |
| FRAGMENT_SHADING_RATE_KHR | `VK_KHR_fragment_shading_rate` |
| LINE_STIPPLE_EXT | `VK_KHR_or_EXT_line_rasterization` |
| CULL_MODE_EXT through STENCIL_OP_EXT (12 states) | `VK_EXT_extended_dynamic_state` |
| VIEWPORT_W_SCALING_NV | `VK_NV_clip_space_w_scaling` (non-VulkanSC) |
| VIEWPORT_SHADING_RATE_PALETTE_NV, VIEWPORT_COARSE_SAMPLE_ORDER_NV | `VK_NV_shading_rate_image` (non-VulkanSC) |
| EXCLUSIVE_SCISSOR_NV | `VK_NV_scissor_exclusive` (non-VulkanSC) |

## Support / Feature Requirements

The [`checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L841) method enforces:
- Pipeline construction requirements
- Per-state extension requirements via [`getDynamicStateInfo()`](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L519)
- `DEVICE_CORE_FEATURE_DEPTH_BOUNDS` for `VK_DYNAMIC_STATE_DEPTH_BOUNDS_TEST_ENABLE_EXT`
- Special handling for `VK_KHR_or_EXT_line_rasterization` (accepts either KHR or EXT variant)

Device helper selection at [lines 740-754](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L740):
- States requiring `VK_NV_shading_rate_image` use a custom device with the extension enabled and the `VkPhysicalDeviceShadingRateImageFeaturesNV` feature struct.
- All other states use the default context device.

## Verification Methods

### Transfer operation verification

Creates source and destination buffers. For each dynamic state, records either: set-state-before then `vkCmdCopyBuffer`, or `vkCmdCopyBuffer` then set-state-after. Verifies that each element in the destination buffer matches the corresponding source element. A mismatch triggers `TCU_FAIL`.

### Compute operation verification

Creates a storage buffer initialized with zeros. For each dynamic state, records either: set-state-before then compute dispatch, or compute dispatch then set-state-after. The compute shader writes `1u` to the output buffer. Verifies that every position equals `1u`. A value other than `1u` triggers `TCU_FAIL`.

### Core principle

Both paths verify that **setting a graphics dynamic state command before or after a compute/transfer operation does not interfere with the correct execution of that operation**.

## Test Principles Observed

- **Graphics-compute isolation**: Tests verify that graphics dynamic state commands do not affect compute or transfer operations.
- **Before/after symmetry**: Both orderings (set state before operation, set state after operation) are tested.
- **Comprehensive state coverage**: All known dynamic states are tested, including extension-specific states.
- **Multi-state stress test**: The multi subgroup tests multiple dynamic states simultaneously.

## Notes / Uncertainties

- This group is only registered for `monolithic` and `shader_object_unlinked_spirv` pipeline construction types.
- When using shader object construction type, `VK_DYNAMIC_STATE_VIEWPORT` is replaced with `VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT_EXT` and `VK_DYNAMIC_STATE_SCISSOR` is replaced with `VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT_EXT` at [lines 1125-1131](../../../modules/vulkan/dynamic_state/vktDynamicStateComputeTests.cpp#L1125).
- Some NV-specific states are excluded on Vulkan SC builds.
