# vktPipelineMaxVaryingsTests.cpp

## Overview

[`vktPipelineMaxVaryingsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1) implements the [`max_varyings`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1150) topic group. It stresses maximum shader I/O component limits by using specialization constants to set array sizes to device maximums, verifying that data passes correctly between stages at the limit.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMaxVaryingsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1)
- Header: [`vktPipelineMaxVaryingsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.hpp#L1)

## Registration Path

[`createMaxVaryingsTests()`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1133) returns the `max_varyings` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
max_varyings
├── test_vertex_io_between_vertex_fragment
├── test_fragment_io_between_vertex_fragment
├── test_tess_eval_io_between_tess_eval_fragment
├── test_fragment_io_between_tess_eval_fragment
├── test_geometry_io_between_geometry_fragment
└── test_fragment_io_between_geometry_fragment
```

## Test Families

### 1. Vertex/TessEval/Geometry output stress

Stresses maximum output components of the producing stage. Uses SPIR-V specialization to set array size to `maxOutputComponents / 4 - 1` vec4s.

### 2. Fragment input stress (per pipeline)

Stresses maximum fragment input components in the consuming pipeline. Specializes array to `maxFragmentInputComponents / 4` vec4s.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| outputStage | VkShaderStageFlags | VERTEX, TESSELLATION_EVALUATION, GEOMETRY |
| inputStage | VkShaderStageFlags | FRAGMENT (always) |
| stageToStressIO | VkShaderStageFlags | VERTEX, TESSELLATION_EVALUATION, GEOMETRY, FRAGMENT |
| arraySize | SPIR-V SpecId 0 | Runtime: `min(maxOutput, maxInput)` vec4s from device limits |

## Support / Feature Requirements

| Requirement | Condition | Line |
|---|---|---|
| `tessellationShader` | When tessellation stages used | [712](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L712) |
| `geometryShader` | When geometry stage used | [721](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L721) |
| Fragment input >= output | Cross-stage limit compatibility | [734](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L734) |
| Pipeline construction requirements | Always | [796](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L796) |

## Verification Methods

Fragment-shader inline verification: the fragment shader (hand-written SPIR-V) iterates over all `inputData[i]` values and checks each equals `ivec4(i)`. If all match, outputs green; otherwise red. Host compares rendered image against green reference using `tcu::floatThresholdCompare` with threshold Vec4(0.02) ([line 1116](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1116)).

## Notes / Uncertainties

- Array sizes are specialized at runtime via SPIR-V SpecId, not hardcoded
- Cross-stage limit compatibility checks ensure the test is only run when both stages support the required component count
