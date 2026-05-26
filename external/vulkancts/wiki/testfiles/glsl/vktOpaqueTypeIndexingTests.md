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

### sampler — Combined image sampler array indexing

The `sampler` child is added directly under `glsl.opaque_type_indexing` before the block and atomic-counter groups are created in [`OpaqueTypeIndexingTests::init()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1944-L1975). Its generated hierarchy is `sampler/{indexing type}/{shader stage}/{sampler type}`: `indexingTypes[]` defines `const_literal`, `const_expression`, `uniform`, and `dynamically_uniform` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1920-L1931), `shaderTypes[]` defines vertex, fragment, geometry, tessellation-control, tessellation-evaluation, and compute groups at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1933-L1942), and the sampler-type table contains 23 GLSL sampler, integer sampler, unsigned sampler, and shadow-sampler variants at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1946-L1970).

The source still creates shader-stage groups for all six stages, but it only populates vertex, fragment, and compute with sampler cases; geometry and tessellation stage groups are present but skipped for sampler case creation by the CTS 1.0.2 compatibility guard at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1982-L1992). Each populated sampler leaf is a `SamplerIndexingCase` named with the lower-case GLSL sampler type, created at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1994-L2002).

`SamplerIndexingCase` builds a shader that declares an array of eight combined image samplers at descriptor set `EXTRA_RESOURCES_DESCRIPTOR_SET_INDEX`, binding 0, emits four texture lookups, and chooses the array index from a literal, a `const` expression, a uniform block, or dynamically uniform shader inputs depending on `IndexExprType` at [`SamplerIndexingCase::createShaderSpec()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1070-L1128). The runtime creates one 1-pixel texture per sampler array element, binds eight combined image samplers plus an optional index uniform buffer, executes 64 invocations, and gathers four output streams at [`SamplerIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L679-L889).

### ubo — Uniform-block instance array indexing

The `ubo` child is created with the other non-sampler groups at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2007-L2018). It registers one flat case for every combination of the four indexing names and the six shader-stage names, using case names such as `{indexing type}_{shader stage}` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2020-L2032).

Each `ubo` case is a `BlockArrayIndexingCase` with `BLOCKTYPE_UNIFORM`, so its generated shader declares `layout(... ) uniform Block { highp uint value; } block[4];`, performs four reads, and writes four `uint` outputs at [`BlockArrayIndexingCase::createShaderSpec()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1441-L1505). The runtime uses four separate uniform buffers, fills each one with a random `uint`, optionally binds an index uniform buffer for `uniform` indexing, and then executes 32 invocations at [`BlockArrayIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1186-L1344).

### ssbo — Storage-buffer instance array indexing

The `ssbo` child is registered beside `ubo`, `ssbo_storage_buffer_decoration`, and `atomic_counter` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2010-L2018). Like `ubo`, it receives one flat `{indexing type}_{shader stage}` case for each of the four index-expression modes and six shader stages at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2020-L2038).

Each `ssbo` case is a `BlockArrayIndexingCase` with `BLOCKTYPE_BUFFER`, causing the generated interface declaration to use `readonly buffer` rather than `uniform` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1446-L1471). Runtime descriptor setup uses four separate storage-buffer descriptors and the same four-read, 32-invocation comparison path used by `ubo` at [`BlockArrayIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1198-L1300).

### ssbo_storage_buffer_decoration — SSBO indexing with the storage-buffer storage class build flag

The `ssbo_storage_buffer_decoration` child is a second storage-buffer branch registered next to `ssbo` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2010-L2018). Its case matrix is the same four index-expression modes by six shader stages, but each case passes `BlockArrayIndexingCaseInstance::FLAG_USE_STORAGE_BUFFER` to `BlockArrayIndexingCase` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2033-L2037).

The flag has two source-visible effects: runtime support requires `VK_KHR_storage_buffer_storage_class` at [`BlockArrayIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1217-L1221), and shader build options add `ShaderBuildOptions::FLAG_USE_STORAGE_BUFFER_STORAGE_CLASS` at [`BlockArrayIndexingCase::createShaderSpec()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1507-L1509). The data generation, descriptor layout, and output comparison otherwise follow the `ssbo` storage-buffer path.

### atomic_counter — Atomic-add indexing over a storage-buffer counter array

The `atomic_counter` child is added directly under `glsl.opaque_type_indexing` with the other non-sampler groups at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2010-L2018). It receives one flat `{indexing type}_{shader stage}` case for each index-expression mode and shader stage at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2020-L2032).

`AtomicCounterIndexingCase` generates a storage-buffer-backed counter array with four counters and four `atomicAdd(counter[index], uint(1))` operations; the selected counter index comes from the same literal, const-expression, uniform, or dynamically uniform sources used elsewhere in this file at [`AtomicCounterIndexingCase::createShaderSpec()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1837-L1893). At runtime, `AtomicCounterIndexingCaseInstance` initializes the four counters to zero, optionally binds a uniform index buffer, executes 32 invocations, invalidates the counter buffer, and validates both final counter ranges and per-operation returned values at [`AtomicCounterIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1545-L1798).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct registration children | `sampler`, `ubo`, `ssbo`, `ssbo_storage_buffer_decoration`, and `atomic_counter` are direct children added in [`OpaqueTypeIndexingTests::init()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1972-L2018). |
| Index-expression modes | `const_literal`, `const_expression`, `uniform`, and `dynamically_uniform` from `indexingTypes[]` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1920-L1931). Non-literal modes emit `#extension GL_EXT_gpu_shader5 : require` in sampler, block, and atomic shader generation at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1086-L1104), [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1459-L1482), and [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1851-L1869). |
| Shader stages | The shared stage table contains `vertex`, `fragment`, `geometry`, `tess_ctrl`, `tess_eval`, and `compute` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1933-L1942). Sampler leaves are generated only for vertex, fragment, and compute, while the block and atomic branches generate cases for all six stages at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1982-L2002) and [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2025-L2038). |
| Sampler types | 23 sampler variants are enumerated in `samplerTypes[]`, covering 1D, 1D array, 2D, cube, 2D array, 3D, shadow, signed-integer, and unsigned-integer sampler forms at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1946-L1970). |
| Sampler runtime sizes | Sampler tests use `NUM_INVOCATIONS = 64`, `NUM_SAMPLERS = 8`, and `NUM_LOOKUPS = 4` at [`SamplerIndexingCaseInstance`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L636-L644). |
| Texture forms and formats | Sampler type maps to 1D, 1D array, 2D, cube, 2D array, or 3D image/view types at [`getTextureType()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L289-L331), [`getVkImageType()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L464-L482), and [`getVkImageViewType()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L484-L504); output scalar class selects depth, RGBA UNORM8, signed-int8, or unsigned-int8 texture data at [`getSamplerTextureFormat()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L380-L401). |
| Block runtime sizes | UBO/SSBO branches use `NUM_INVOCATIONS = 32`, `NUM_INSTANCES = 4`, and `NUM_READS = 4` at [`BlockArrayIndexingCaseInstance`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1138-L1151). |
| Block descriptor type | `BLOCKTYPE_UNIFORM` selects uniform buffers; `BLOCKTYPE_BUFFER` selects storage buffers at [`BlockArrayIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1198-L1201). |
| Atomic runtime sizes | Atomic-counter tests use `NUM_INVOCATIONS = 32`, `NUM_COUNTERS = 4`, and `NUM_OPS = 4` at [`AtomicCounterIndexingCaseInstance`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1511-L1519). |
| Descriptor set index | Extra resources are declared at descriptor set `EXTRA_RESOURCES_DESCRIPTOR_SET_INDEX`, which is defined as set `1` in [`vktShaderExecutor.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.hpp#L87-L91) and used by the sampler, block, and atomic shader declarations in [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1092-L1093), [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1465-L1471), and [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1857-L1858). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Shader-stage availability | All cases inherit `OpaqueTypeIndexingCase::checkSupport()`, which delegates to `checkSupportShader(context, m_shaderType)` for the selected stage at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L174-L187) and [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L208-L211). |
| Dynamic descriptor-array indexing features | `checkSupported()` only runs descriptor-array dynamic-indexing feature checks for `uniform` and `dynamically_uniform` modes; constant literal and constant-expression cases bypass this dynamic-indexing feature gate at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L249-L275). The checked features are `shaderSampledImageArrayDynamicIndexing`, `shaderUniformBufferArrayDynamicIndexing`, and `shaderStorageBufferArrayDynamicIndexing` for combined-image-sampler, uniform-buffer, and storage-buffer descriptors respectively at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L255-L270). |
| 1D shadow image format support | Sampler cases for `sampler1DShadow` and `sampler1DArrayShadow` query `VK_FORMAT_D16_UNORM` with `VK_IMAGE_TYPE_1D` and reject unsupported format/image-type combinations at [`SamplerIndexingCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1042-L1062). |
| Storage-buffer descriptor limit for block cases | `BlockArrayIndexingCase::checkSupport()` compares the required number of storage-buffer descriptors against `maxPerStageDescriptorStorageBuffers`, adding two extra storage buffers for compute to account for `ComputeShaderExecutor` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1407-L1433). |
| Storage-buffer storage class extension | Only `ssbo_storage_buffer_decoration` cases set `FLAG_USE_STORAGE_BUFFER`; those runtime instances require `VK_KHR_storage_buffer_storage_class` at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1217-L1221). |
| Atomic stores and atomics | Atomic-counter cases require `vertexPipelineStoresAndAtomics` for vertex, tessellation-control, tessellation-evaluation, and geometry stages, require `fragmentStoresAndAtomics` for fragment stage, and add no extra stores/atomics feature check for compute at [`AtomicCounterIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1555-L1578). |
| Render-target / vertex-format support in shader executor | Graphics-stage execution validates vertex-buffer attribute formats and color-attachment formats before drawing in [`FragmentOutExecutor`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L683-L702) and [`FragmentOutExecutor::executeCommon()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L1164-L1183). |

## Verification Methods

- Sampler cases verify shader texture lookup results against CPU-side reference texture access. Shadow samplers compare each invocation against `sample2DCompare()` with a `0.005f` tolerance at [`SamplerIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L895-L924). Non-shadow floating-point sampler outputs compare against the selected reference texel with a `1.0f / 256.0f` per-component threshold, while integer outputs require exact `uvec4` equality at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L930-L969).
- Sampler cases also require all invocations after the first to reproduce the first invocation's result for each lookup, failing on inconsistent lookup results at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L971-L997).
- UBO and SSBO cases compare each read result from each of 32 invocations to the random input value selected by `m_readIndices[readNdx]`, failing on any mismatched `uint` at [`BlockArrayIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1346-L1365).
- Atomic-counter cases first validate final counter values: a counter hit by generated operations must be at least the expected hit count, while a counter with zero expected hits must remain zero at [`AtomicCounterIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1713-L1752). They then verify each returned `atomicAdd` value lies in range and no returned value is duplicated for the same counter at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1754-L1797).
- Graphics-stage output readback is performed by `FragmentOutExecutor::executeCommon()`, which renders point primitives, copies color attachments to host-visible buffers, invalidates the memory, and copies pixels into the output arrays at [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L1552-L1665). Compute execution uses `ComputeShaderExecutor::execute()` to upload inputs and bind storage-buffer outputs before dispatch at [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3124-L3180).

## Test Principles

- The file organizes one opaque-type indexing test group into five direct resource-family children and then varies index-expression type and shader stage from shared tables, so the same indexing modes are applied across samplers, block arrays, and atomic-counter storage-buffer arrays at [`OpaqueTypeIndexingTests::init()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1918-L2041).
- The test data is deterministic per shader stage, resource type, and index-expression mode because sampler, block, and atomic cases seed `de::Random` from hashes of those parameters before choosing lookup/read/operation indices and input values at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1070-L1083), [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1441-L1457), and [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1837-L1845).
- Uniform index-expression cases bind a uniform buffer containing the chosen indices, while dynamically uniform cases pass per-invocation input arrays filled with the same index for every invocation of a given lookup/read/op; this distinction is visible in the sampler, block, and atomic runtime setup paths at [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L771-L883), [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1230-L1334), and [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1594-L1694).
- Correctness is determined from shader-visible resource contents and readback values, not from successful API calls alone: sampler outputs are compared to reference texture access, block outputs are compared to seeded buffer values, and atomic outputs are checked against counter-update behavior.

## Notes / Uncertainties

- The documented hierarchy covers the direct children registered by this file under `glsl.opaque_type_indexing`; deeper generated sampler and flat block/atomic case names are described in `## Test Families` rather than expanded in the parseable hierarchy tree.
- The inspected source does not show a separate helper file for opaque-type indexing registration; the source header only declares `createOpaqueTypeIndexingTests()` at [`vktOpaqueTypeIndexingTests.hpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.hpp#L30-L36), and the Vulkan package attaches it under the `glsl` group at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1275-L1277).
