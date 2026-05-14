# vktPipelinePushConstantTests.cpp

## Overview

[`vktPipelinePushConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1) implements the [`push_constant`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3606) topic group. It verifies push constant behavior across graphics and compute pipelines, including range sizes, overlapping ranges, multi-stage sharing, data updates, lifetime semantics, and overwrite behavior.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelinePushConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1)
- Header: [`vktPipelinePushConstantTests.hpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.hpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.push_constant
├── graphics_pipeline
├── compute_pipeline (monolithic only)
└── lifetime
```

**Variant coverage**: All variants. The `compute_pipeline` subgroup is monolithic only.

## Test Families

### graphics_pipeline — Graphics pipeline push constants

Tests push constants with non-overlapping (disjoint) and overlapping ranges across varying range sizes (4-256 bytes, max), shader stage counts (1-5 stages), partial and multiple data updates, and dynamic indexing. Also includes:

- **Disjoint ranges**: Tests with non-overlapping push constant ranges across 1-5 shader stages. Range sizes from 4 to 256 bytes, plus a max-size range queried from the device. Includes `_command2` variants (using `vkCmdPushConstants2KHR`) on non-VulkanSC.
- **Overlap ranges**: Tests with overlapping push constant ranges across 2-5 shader stages. Includes `_command2` variants on non-VulkanSC.
- **Overwrite**: Verifies push constant values are correctly overwritten across multiple push commands.
- **Unused**: Tests where some declared push constant ranges are not consumed by shaders (unused_disjoint_1-6, unused_overlap_1-6).

Non-SC variants also include `range_size_128_longvec` and `range_size_256_longvec` tests (using `VK_EXT_shader_long_vector`).

### compute_pipeline — Compute pipeline push constants (monolithic only)

Tests push constants in compute pipelines. Includes:

- **simple_test**: Basic push constant value verification.
- **uninitialized**: Pass-by-survival test for uninitialized push constant reads (requires `VK_KHR_maintenance4`).
- **overwrite**: Verifies push constant overwrite behavior in compute pipelines.

### lifetime — Push constant lifetime semantics

Tests push constant lifetime semantics across 9 command-sequence scenarios: binding different layouts, pushing then rebinding, overlapping ranges across layouts, and switching between graphics and compute pipelines. Each test verifies that push constants remain valid only within their specified lifetime rules.

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
