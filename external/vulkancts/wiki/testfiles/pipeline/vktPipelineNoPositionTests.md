# vktPipelineNoPositionTests.cpp

## Overview

[`vktPipelineNoPositionTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1) implements the [`no_position`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1099) topic group. It verifies pipeline behavior when vertex shaders do not write to `gl_Position`, testing that rendering without a position output works correctly for pipelines that don't require rasterization.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineNoPositionTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1)
- Header: [`vktPipelineNoPositionTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.hpp#L1)

## Registration Path

[`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1097) returns the `no_position` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
no_position
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| NoPositionTest | Verifies pipeline behavior when vertex shader does not write gl_Position |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Shader type | Enum | Vertex-only, vertex+fragment |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| Standard pipeline support | Basic pipeline feature support |

## Verification Methods

- **Execution verification**: Verify that pipelines without position output execute without errors
- **Rasterization disable verification**: Verify that rasterization is correctly disabled when no position is written

## Notes

- This test verifies a corner case where vertex shaders omit `gl_Position` output
