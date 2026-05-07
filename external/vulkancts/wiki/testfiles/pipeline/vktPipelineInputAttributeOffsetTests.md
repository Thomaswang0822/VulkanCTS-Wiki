# vktPipelineInputAttributeOffsetTests.cpp

## Overview

[`vktPipelineInputAttributeOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L1) implements the [`input_attribute_offset`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L515) topic group of the pipeline category. It verifies that vertex attribute data is correctly read when the vertex buffer is bound at various byte offsets, with different data layouts (packed, padded, overlapping) and both static and dynamic vertex input state.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineInputAttributeOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L1)
- Header: [`vktPipelineInputAttributeOffsetTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.hpp#L1)

## Registration Path

This file contributes the subgroup returned by [`createInputAttributeOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L511), which is attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1).

**Variant coverage**: All variants.

## Test Hierarchy

```text
input_attribute_offset
├── vec2                                  (TYPE_FLOAT_VEC2, 8 bytes)
│   ├── offset_0
│   │   ├── packed
│   │   │   ├── no_memory_offset
│   │   │   │   ├── static
│   │   │   │   └── dynamic
│   │   │   └── with_memory_offset
│   │   │       ├── static
│   │   │       └── dynamic
│   │   ├── padded
│   │   │   ├── no_memory_offset / with_memory_offset
│   │   │   │   ├── static / dynamic
│   │   └── overlapping
│   │       ├── no_memory_offset / with_memory_offset
│   │       │   ├── static / dynamic
│   ├── offset_1 through offset_7
│   └── (same structure per offset)
└── vec4                                  (TYPE_FLOAT_VEC4, 16 bytes)
    ├── offset_0 through offset_15
    │   ├── packed / padded               (NO overlapping for vec4)
    │   │   ├── no_memory_offset / with_memory_offset
    │   │   │   ├── static / dynamic
    └── (same structure per offset)
```

Source: [`createInputAttributeOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L511).

## Test Families

### 1. vec2 / vec4 (data type groups)

Data type of the vertex attribute. Determines attribute size (8 or 16 bytes) and the range of offsets tested. Vec2 tests offsets 0-7; vec4 tests offsets 0-15.

### 2. offset_N (binding offset groups)

Vertex binding offset from 0 to `typeSize - 1`. Tests that attribute data is correctly read when the vertex buffer is bound at various byte offsets.

### 3. packed / padded / overlapping (stride case groups)

Vertex data layout in the buffer: tightly packed, with padding between attributes, or overlapping (vec2 data read as vec4 in shader). `OVERLAPPING` is skipped for vec4 ([line 529](../../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L529)).

### 4. no_memory_offset / with_memory_offset

Whether an additional offset is applied when binding memory to the vertex buffer.

### 5. static / dynamic

Whether vertex input state is set statically in the pipeline or dynamically via `VK_EXT_vertex_input_dynamic_state`.

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
