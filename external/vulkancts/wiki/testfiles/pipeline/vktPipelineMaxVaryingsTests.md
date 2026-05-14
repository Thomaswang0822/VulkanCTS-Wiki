# vktPipelineMaxVaryingsTests.cpp

## Overview

[`vktPipelineMaxVaryingsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1) implements the [`max_varyings`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1150) topic group. It stresses maximum shader I/O component limits by using specialization constants to set array sizes to device maximums, verifying that data passes correctly between stages at the limit.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMaxVaryingsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1)
- Header: [`vktPipelineMaxVaryingsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.max_varyings
├── test_vertex_io_between_vertex_fragment
├── test_fragment_io_between_vertex_fragment
├── test_tess_eval_io_between_tess_eval_fragment
├── test_fragment_io_between_tess_eval_fragment
├── test_geometry_io_between_geometry_fragment
└── test_fragment_io_between_geometry_fragment
```

## Test Families

### test_vertex_io_between_vertex_fragment — Vertex output stress (VS-FS)

Stresses maximum output components of the vertex shader stage in a vertex-to-fragment pipeline. Uses SPIR-V specialization to set array size to `maxVertexOutputComponents / 4 - 1` vec4s, verifying all data passes correctly from vertex to fragment.

### test_fragment_io_between_vertex_fragment — Fragment input stress (VS-FS)

Stresses maximum fragment input components in a vertex-to-fragment pipeline. Specializes array to `maxFragmentInputComponents / 4` vec4s, verifying the fragment shader can consume all inputs at the device limit.

### test_tess_eval_io_between_tess_eval_fragment — Tessellation evaluation output stress (VS-TCS-TES-FS)

Stresses maximum output components of the tessellation evaluation stage in a tessellation pipeline. Uses SPIR-V specialization to set array size based on `maxTessellationEvaluationOutputComponents`. Requires `tessellationShader`.

### test_fragment_io_between_tess_eval_fragment — Fragment input stress (VS-TCS-TES-FS)

Stresses maximum fragment input components in a tessellation pipeline. Specializes array to `maxFragmentInputComponents / 4` vec4s. Requires `tessellationShader`.

### test_geometry_io_between_geometry_fragment — Geometry output stress (VS-GS-FS)

Stresses maximum output components of the geometry shader stage in a geometry pipeline. Uses SPIR-V specialization to set array size based on `maxGeometryOutputComponents`. Requires `geometryShader`.

### test_fragment_io_between_geometry_fragment — Fragment input stress (VS-GS-FS)

Stresses maximum fragment input components in a geometry pipeline. Specializes array to `maxFragmentInputComponents / 4` vec4s. Requires `geometryShader`.

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
