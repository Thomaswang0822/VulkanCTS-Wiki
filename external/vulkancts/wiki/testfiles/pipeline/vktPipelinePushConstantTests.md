# vktPipelinePushConstantTests.cpp

## Overview

[`vktPipelinePushConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1) implements the [`push_constant`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3606) topic group. It verifies push constant behavior across graphics and compute pipelines, including range sizes, overlapping ranges, multi-stage sharing, data updates, lifetime semantics, and overwrite behavior.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelinePushConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1)
- Header: [`vktPipelinePushConstantTests.hpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Path

[`createPushConstantTests()`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3337) returns the `push_constant` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants (VulkanSC only for push_constant). Compute pipeline sub-group is monolithic only.

## Test Hierarchy

```text
push_constant
├── graphics_pipeline
│   ├── range_size_4..range_size_256      (disjoint ranges)
│   ├── range_size_128_longvec            (non-SC only)
│   ├── range_size_256_longvec            (non-SC only)
│   ├── range_size_max                    (queried from device)
│   ├── count_2_shaders_vert_frag         (disjoint, shared range)
│   ├── count_3_shaders_vert_geom_frag
│   ├── count_5_shaders_vert_tess_geom_frag
│   ├── data_update_partial_1/2           (partial updates)
│   ├── data_update_multiple              (multiple updates)
│   ├── dynamic_index_vert/frag           (dynamically uniform indexing)
│   ├── overlap_2_shaders_vert_frag       (overlapping ranges)
│   ├── overlap_3_shaders_vert_geom_frag
│   ├── overlap_4_shaders_vert_tess_frag
│   ├── overlap_5_shaders_vert_tess_geom_frag
│   ├── [..._command2 variants]           (non-SC only, vkCmdPushConstants2KHR)
│   ├── overwrite
│   ├── unused_disjoint_1..6
│   └── unused_overlap_1..6
├── compute_pipeline                      (monolithic only)
│   ├── simple_test
│   ├── uninitialized
│   └── overwrite
└── lifetime
    ├── push_range0_bind_layout1
    ├── push_range1_bind_layout1_push_range0
    └── ... (9 command-sequence tests)
```

## Test Families

### 1. graphics_pipeline (disjoint)

Tests push constants with non-overlapping ranges across varying range sizes (4-256 bytes, max), shader stage counts (1-5 stages), partial and multiple data updates, and dynamic indexing.

### 2. graphics_pipeline (overlap)

Tests push constants with overlapping ranges across 2-5 shader stages.

### 3. graphics_pipeline (overwrite)

Verifies push constant values are correctly overwritten across multiple push commands.

### 4. graphics_pipeline (unused)

Tests where some declared push constant ranges are not consumed by shaders.

### 5. compute_pipeline

Tests push constants in compute pipelines. Includes uninitialized read test (pass-by-survival). Monolithic only.

### 6. lifetime

Tests push constant lifetime semantics: binding different layouts, pushing then rebinding, overlapping ranges across layouts, and switching between graphics and compute pipelines.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| RangeSizeCase | [Enum](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L76) | SIZE_CASE_4 through SIZE_CASE_256_LONGVEC, SIZE_CASE_MAX |
| PushConstantUseStageType | [Enum](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L103) | PC_USE_STAGE_NONE through PC_USE_STAGE_ALL |
| IndexType | [Enum](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L148) | CONST_LITERAL, DYNAMICALLY_UNIFORM_EXPR |
| pushConstant2 | bool | false (vkCmdPushConstants), true (vkCmdPushConstants2KHR, non-SC) |
| graphicsParams | [Static array](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3340) | 16 entries |
| overlapGraphicsParams | [Static array](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3457) | 4 entries |
| lifetimeParams | [Static array](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3507) | 9 entries |

## Support / Feature Requirements

| Requirement | Condition | Line |
|---|---|---|
| `VK_KHR_maintenance6` | When `pushConstant2 == true` | [1159](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1159) |
| `VK_KHR_maintenance4` | CTT_UNINITIALIZED compute test | [2047](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2047) |
| `VK_EXT_shader_long_vector` | When `longVec == true` | [1176](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1176) |
| maxPushConstantsSize | Checked for each range | [1169](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1169) |
| tessellationShader / geometryShader | When stages used | [1196](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1196) |

## Verification Methods

- **Graphics (disjoint/overlap)**: `tcu::intThresholdPositionDeviationCompare()` against reference renderer ([line 691](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L691))
- **Compute (simple)**: `deMemCmp()` against expected Vec4(1,0,0,1) x 8 ([line 2241](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2241))
- **Compute (uninitialized)**: Pass-by-survival (no value check) ([line 2235](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2235))
- **Lifetime**: Dual: graphics reference renderer + compute buffer comparison ([line 2870](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2870))
- **Overwrite**: Per-pixel `getPixelUint()` comparison on 2x2 storage image ([line 3274](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3274))
