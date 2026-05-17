# vktPipelineLegacyAttrTests.cpp

## Overview

[`vktPipelineLegacyAttrTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L1) implements the [`legacy_vertex_attributes`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3117) nested subgroup under the `vertex_input` group of the pipeline category. It verifies `VK_EXT_legacy_vertex_attributes` behavior, which allows vertex attribute data to be fetched with a stride and format that may differ from what the shader expects, using dynamic vertex input state.

## Role

Implementation file. Nested subgroup under [`vktPipelineVertexInputTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1). The parent file creates the group with name `"legacy_vertex_attributes"` and passes it to [`createLegacyVertexAttributesTests()`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L833).

## Source Code

- Primary source: [`vktPipelineLegacyAttrTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L1)
- Header: [`vktPipelineLegacyAttrTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.vertex_input.legacy_vertex_attributes
├── single_binding
└── multi_binding
```

**Variant coverage**: Monolithic and fast_linked_library only (parent restricts at [line 3114](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3114)).

## Test Families

### single_binding — Single vertex binding tests

Tests `VK_EXT_legacy_vertex_attributes` with a single vertex binding per test. Each case varies the vertex format, shader reinterpretation format, binding stride, attribute offset, and memory offset. Verifies that vertex data is correctly fetched through the legacy vertex attribute path with dynamic vertex input. Contains many leaf test cases generated from the cross-product of ~47 formats, shader formats (FLOAT, SIGNED_INT, UNSIGNED_INT), strides ({0, 1, formatSize, 2*formatSize-1}), attribute offsets ({0, 1}), and memory offsets ({0, 1}).

### multi_binding — Multi vertex binding tests

Tests `VK_EXT_legacy_vertex_attributes` with 3 simultaneous vertex bindings per test. Uses curated format tuples mixing different component counts, numeric types, and bit widths. Verifies correct data fetching across multiple bindings with varied strides and offsets. Contains leaf test cases from 3 curated format tuples with normal and single-byte strides, plus attribute/memory offset combinations.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkFormat (single) | [`formatsToTest[]`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L841) | ~47 formats: R8 through R16G16B16_SFLOAT |
| VkFormat (multi) | [`formatTuples[]`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L998) | 3 curated tuples of 3 formats each |
| ShaderFormat | [Enum](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L58) | `FLOAT`, `SIGNED_INT`, `UNSIGNED_INT` |
| Binding stride (single) | [`strides`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L922) | {0, 1, formatSize, 2*formatSize-1} |
| Binding stride (multi) | `singleByteStride` | `false` (formatSize) / `true` (1 byte) |
| Attribute offset | Loop | {0, 1} |
| Memory offset | Loop | {0, 1} |
| PipelineConstructionType | Factory parameter | Monolithic or fast-linked library only |

**BindingParams struct** at [line 66](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L66), **LegacyVertexAttributesParams** at [line 135](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L135).

Filtering rules: float-like formats use alternating shader_int/shader_uint by format ID parity; integer formats with sub-32-bit channels skip shader_float; attribute/memory offset tests skip formats with only 8-bit channels.

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `VK_EXT_vertex_input_dynamic_state` | `checkSupport` | [342](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L342) |
| `VK_EXT_legacy_vertex_attributes` | `checkSupport` | [343](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L343) |
| `fragmentStoresAndAtomics` core feature | `checkSupport` | [341](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L341) |
| `VK_EXT_scalar_block_layout` (3-component formats) | `checkSupport` | [354](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L354) |
| `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` | `checkSupport` | [360](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L360) |
| Pipeline construction requirements | `checkSupport` | [340](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L340) |

## Verification Methods

**Dual verification** strategy ([line 415](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L415)):

1. **Color buffer verification** ([line 687](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L687)): After rendering 16 point primitives, the color attachment is compared against a reference (all blue pixels) using `tcu::floatThresholdCompare` with zero threshold. Confirms the geometry was actually rendered.

2. **Storage buffer verification** ([line 700](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L700)): The fragment shader writes vertex attribute data to storage buffers (one per binding). After rendering, the CPU reads back these buffers and compares against expected output data computed by `getOutputData()`. Comparison varies by channel class:
   - **Floating-point / fixed-point**: Per-component absolute difference within threshold computed from format bit depth
   - **Signed/unsigned integer**: Exact 32-bit match required

## Test Principles Observed

- **Format-shader reinterpretation**: Tests the core legacy vertex attributes feature where the shader interprets data differently from the vertex format
- **Stride variety**: Tests zero stride, single-byte stride, normal stride, and oversized stride
- **Offset orthogonality**: Attribute offset and memory offset are tested independently
- **Storage buffer verification**: Uses SSBO writes from the fragment shader to capture actual vertex data values, enabling precise per-component comparison

## Notes / Uncertainties

- The `fragmentStoresAndAtomics` feature is required because the test uses fragment shader SSBO writes for verification
- `VK_EXT_scalar_block_layout` is needed for 3-component formats to avoid vec3 padding issues in the SSBO layout
- Input data generation rejects NaN, Inf, denorm, and zero values for float-interpreted data to ensure deterministic round-trip verification
