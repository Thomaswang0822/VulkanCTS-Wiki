# vktPipelineInputAttributeOffsetTests.cpp

## Overview

[`vktPipelineInputAttributeOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L1) implements the [`input_attribute_offset`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L515) topic group of the pipeline category. It verifies that vertex attribute data is correctly read when the vertex buffer is bound at various byte offsets, with different data layouts (packed, padded, overlapping) and both static and dynamic vertex input state.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineInputAttributeOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L1)
- Header: [`vktPipelineInputAttributeOffsetTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.input_attribute_offset
├── vec2
└── vec4
```

## Test Families

### vec2 — Float vec2 attribute offset tests

Tests vertex attribute reading with `TYPE_FLOAT_VEC2` (8 bytes). Offsets 0 through 7 are tested, each containing stride cases (packed, padded, overlapping), memory offset variants (no_memory_offset, with_memory_offset), and vertex input state modes (static, dynamic).

### vec4 — Float vec4 attribute offset tests

Tests vertex attribute reading with `TYPE_FLOAT_VEC4` (16 bytes). Offsets 0 through 15 are tested, each containing stride cases (packed, padded; no overlapping for vec4), memory offset variants (no_memory_offset, with_memory_offset), and vertex input state modes (static, dynamic).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| dataType | Loop | `TYPE_FLOAT_VEC2`, `TYPE_FLOAT_VEC4` |
| bindingOffset | [Loop](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L522) | `0` to `typeSize - 1` |
| strideCase | [StrideCase enum](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L94) | `PACKED`, `PADDED`, `OVERLAPPING` (vec2 only) |
| useMemoryOffset | Loop | `false`, `true` |
| dynamic | Loop | `false` (static), `true` (dynamic vertex input) |
| constructionType | Factory parameter | PipelineConstructionType |

**TestParams struct** at [line 117](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L117).

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| Pipeline construction requirements | `checkSupport` | [310](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L310) |
| `VK_EXT_vertex_input_dynamic_state` (when dynamic=true) | `checkSupport` | [326](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L326) |
| Portability subset `minVertexInputBindingStrideAlignment` (when supported) | `checkSupport` | [313](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L313) |

## Verification Methods

**Float threshold comparison** against expected color at [line 502](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L502):

```cpp
tcu::floatThresholdCompare(log, "Result", "", getDefaultColor(), resultAccess, threshold,
                            tcu::COMPARE_LOG_ON_ERROR)
```

Threshold is `tcu::Vec4(0.0f, 0.0f, 0.0f, 0.0f)` (zero tolerance -- exact match required). Expected color is `getDefaultColor()` = `Vec4(0.0f, 0.0f, 1.0f, 1.0f)` (opaque blue). The test renders a full-screen quad with vertex data at various offsets and verifies the rendered image matches the expected solid color.

## Test Principles Observed

- **Offset sweep**: Tests every possible byte offset from 0 to `typeSize - 1`, ensuring no offset value is missed
- **Layout variety**: Packed, padded, and overlapping layouts exercise different vertex buffer stride and alignment scenarios
- **Memory offset orthogonality**: Memory binding offset is tested independently from attribute offset
- **Static/dynamic state parity**: Same test logic with both static and dynamic vertex input state verifies they produce identical results

## Notes / Uncertainties

- The zero-threshold comparison implies the test expects exact rendering results, which is feasible because the test uses simple solid-color rendering
- `OVERLAPPING` stride case is only applicable to vec2 (where the shader reads more components than the attribute provides)
