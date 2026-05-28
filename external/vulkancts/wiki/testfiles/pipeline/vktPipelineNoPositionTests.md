# vktPipelineNoPositionTests.cpp

## Overview

[`vktPipelineNoPositionTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1) implements the [`no_position`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1099) topic group. It verifies pipeline behavior when vertex shaders do not write to `gl_Position`, testing that rendering without a position output works correctly for pipelines that don't require rasterization.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineNoPositionTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1)
- Header: [`vktPipelineNoPositionTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.no_position
├── implicit_declarations
└── explicit_declarations
```

Source: [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1097) returns the `no_position` group, attached under each variant root by `createChildren()`. Variant coverage: all variants.

## Test Families

### implicit_declarations — Implicit declaration no-position tests

Verifies pipeline behavior when vertex shader does not write `gl_Position` using implicit declarations. Contains a `basic` subgroup (with `single_view` and `multiview` leaves) and an `ssbo_writes` subgroup (with `single_view`, `multiview`, and `device_index_as_view_index` leaves). Each leaf contains test cases for various shader stage combinations (vertex-only, vertex+fragment, vertex+tessellation, vertex+geometry, etc.) with write-mask variants.

### explicit_declarations — Explicit declaration no-position tests

Verifies pipeline behavior when vertex shader does not write `gl_Position` using explicit declarations. Contains the same `basic` and `ssbo_writes` subgroup structure as `implicit_declarations`, but with explicit shader output declarations. Multiview tests are skipped for shader-object construction type.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Shader type | Enum | Vertex-only, vertex+fragment |
| Declaration style | Enum | Implicit, explicit |
| Use SSBO | Boolean | Basic rendering, SSBO write verification |
| View count | Enum | Single view, multiview, device-index-as-view-index |
| Shader stage mask | Bitfield | Combinations of vertex, tessellation, geometry stages |
| Write mask | Bitfield | Which stages write gl_Position (always 0 for vertex) |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| Standard pipeline support | Basic pipeline feature support |

## Verification Methods

- **Execution verification**: Verify that pipelines without position output execute without errors
- **Rasterization disable verification**: Verify that rasterization is correctly disabled when no position is written

## Notes

- This test verifies a corner case where vertex shaders omit `gl_Position` output
- Multiview tests (`multiview` and `device_index_as_view_index`) are skipped for shader-object construction type
