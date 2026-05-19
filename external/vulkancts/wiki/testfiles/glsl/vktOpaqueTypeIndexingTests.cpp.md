# vktOpaqueTypeIndexingTests.cpp

## Overview

Tests for opaque type array indexing in Vulkan shaders. Verifies correct behavior when indexing into arrays of samplers, uniform buffer objects (UBOs), shader storage buffer objects (SSBOs), and atomic counters using various index expression types (constant literal, constant expression, uniform, dynamically uniform).

## Role

Combined registration and implementation file. Contains the `OpaqueTypeIndexingTests` TestCaseGroup class with its `init()` method that builds the test hierarchy, as well as the test case classes (`SamplerIndexingCase`, `BlockArrayIndexingCase`, `AtomicCounterIndexingCase`) and their corresponding test instance implementations.

## Source Code

- [vktOpaqueTypeIndexingTests.cpp](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1-L2051) (full file)
- Registration class: [OpaqueTypeIndexingTests](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1898-L1907)
- Init/hierarchy: [OpaqueTypeIndexingTests::init()](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1918-L2041)
- Entry point: [createOpaqueTypeIndexingTests()](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2045-L2048)

## Registration Hierarchy

```text
glsl.opaque_type_indexing
├── sampler
├── ubo
├── ssbo
├── ssbo_storage_buffer_decoration
└── atomic_counter
```

## Test Families

| Family | Class | Description |
|--------|-------|-------------|
| SamplerIndexingCase | [SamplerIndexingCase](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1004-L1136) | Tests indexing into arrays of combined image samplers (23 sampler types) |
| BlockArrayIndexingCase | [BlockArrayIndexingCase](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1368-L1510) | Tests indexing into arrays of uniform/storage buffer blocks |
| AtomicCounterIndexingCase | [AtomicCounterIndexingCase](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1801-L1905) | Tests indexing into arrays of atomic counters |

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| IndexExprType | CONST_LITERAL, CONST_EXPRESSION, UNIFORM, DYNAMIC_UNIFORM |
| ShaderType | vertex, fragment, geometry, tess_ctrl, tess_eval, compute |
| SamplerType | 23 variants (sampler1D, sampler2D, samplerCube, sampler3D, isampler*, usampler*, *_shadow, *_array) |
| BlockType | UNIFORM (UBO), BUFFER (SSBO) |

## Support/Feature Requirements

| Feature | Condition |
|---------|-----------|
| VK_KHR_storage_buffer_storage_class | Required for `ssbo_storage_buffer_decoration` sub-group (FLAG_USE_STORAGE_BUFFER) |
| vertexPipelineStoresAndAtomics | Required for atomic_counter tests in vertex/tessellation/geometry stages |
| fragmentStoresAndAtomics | Required for atomic_counter tests in fragment stage |
| VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER | Required for sampler tests (checked via `checkSupported()`) |

## Verification Methods

- **Sampler**: Texture lookup verification. Each sampler array element is bound to a texture with a known color value; the shader reads from the indexed sampler and outputs the result. CPU compares the output color against the expected reference texture sample value.
- **UBO/SSBO**: Value comparison. Each buffer array element is filled with a unique value; the shader reads from the indexed buffer and outputs the value. CPU compares output against expected values per invocation.
- **Atomic counter**: Value comparison. Each atomic counter array element is initialized to a known value; the shader reads from the indexed counter and outputs the result. CPU validates the output matches the expected value.

## Notes

- The `sampler` sub-group has a deeper hierarchy: `sampler/{index_type}/{shader_stage}/{sampler_type}`, while `ubo`, `ssbo`, `ssbo_storage_buffer_decoration`, and `atomic_counter` use a flat naming scheme: `{index_type}_{shader_stage}`
- The `ssbo_storage_buffer_decoration` sub-group tests SSBO indexing using the `VK_KHR_storage_buffer_storage_class` extension (BlockLayout flag `FLAG_USE_STORAGE_BUFFER`), which uses the `Buffer` decoration instead of the default `Uniform` decoration for SSBO blocks
- Sampler tests only cover vertex, fragment, and compute stages (not geometry or tessellation), as noted in the source code comment for Vulkan CTS 1.0.2 compatibility
