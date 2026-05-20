# vktSparseResourcesBufferTests.cpp

## Overview

[`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L24-L32) registers the top-level [`sparse_resources.buffer`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2813-L2816) group and builds a nested sparse-buffer tree from local buffer-use cases plus helper files for transfer binding, residency, memory aliasing, and rebind coverage. The Vulkan API test plan separately calls out sparse resources as their own feature area and also notes sparse buffers as a targeted buffer case for very large buffers ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276), [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L434-L449)).

## Role

Implementation-heavy registration file for the `buffer` sparse-resource branch.

## Source Code

- Primary source: [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1)
- Direct helper sources inspected for nested registered cases: [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L1), [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1), [`vktSparseResourcesBufferMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L1), [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L1)
- Shared sparse base inspected for queue/device creation behavior: [`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L134)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276), [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L434-L449)

## Registration Hierarchy

```text
sparse_resources.buffer
├── transfer
├── ssbo
├── ubo
├── texel_buffers
├── vertex_buffer
├── index_buffer
├── indirect_buffer
├── transform_feedback
├── indirect_dispatch
├── misc (non-VulkanSC only)
└── memory_copy_indirect
```

## Test Families

### transfer — sparse buffer transfer, device-group binding, and rebind

The `transfer` branch contains `sparse_binding`, `device_group_sparse_binding`, and `rebind` subgroups registered by [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2616). The binding helper registers six power-of-two buffer sizes from `buffer_size_2_10` through `buffer_size_2_24` ([`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L348-L356)); each case creates a sparse buffer, binds every sparse slot, copies reference bytes into it, copies them back, and compares with `deMemCmp` ([`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L149-L240), [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L252-L338)). The rebind subgroup registers four sizes from `buffer_size_2_16` through `buffer_size_2_24` ([`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L412-L418)) and verifies the final mixed-memory pattern after full binds, fills, a partial rebind, copy-out, and host comparison ([`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L23-L40), [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L233-L400)).

### ssbo — storage-buffer sparse aliasing, residency, and strict read/write

The `ssbo` branch registers memory-aliasing subgroups, residency subgroups, and a `read_write` subgroup ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2619-L2655)). The aliasing helper binds two sparse buffers to the same memory and dispatches a compute shader that writes through one buffer and reads back through the other before comparing a modulo reference pattern ([`vktSparseResourcesBufferMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L246-L287), [`vktSparseResourcesBufferMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L320-L439)). The residency helper includes fixed-size partially resident cases, plus nonresident copy/fill/update cases generated over command type, buffer size, strict-residency mode, full-vs-partial nonresidency, copy direction, and multi-copy cases ([`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1757-L1836)). The direct `read_write` test uses `BufferObjectTestInstance` with storage-buffer type and `TEST_FLAG_RESIDENCY | TEST_FLAG_NON_RESIDENT_STRICT` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2645-L2653)).

### ubo — uniform-buffer sparse binding/residency flag matrix

The `ubo` branch creates direct tests from a local `groups[]` flag table: `sparse_binding`, `sparse_binding_aliased`, `sparse_residency`, `sparse_residency_aliased`, and `sparse_residency_non_resident_strict`, then repeats the same names with a `device_group_` prefix ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2597), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2658-L2677)). The shared buffer-object instance creates a sparse UBO or SSBO, optionally leaves a resource hole, optionally aliases a chunk, draws using a fragment shader that checks the expected values, and fails if the rendered image contains error pixels ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L838-L1085)).

### texel_buffers — sparse texel-buffer residency and sparse texel operations

The `texel_buffers` branch has one `sparse_residency` subgroup populated by `addTexelBufferSparseResidencyTests()` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2679-L2689)). The helper combines uniform/storage texel buffer type, sparse-fetch/sparse-read/plain-read operation names, buffer sizes `2^10`, `2^16`, and `2^24`, formats `VK_FORMAT_R32_UINT` and `VK_FORMAT_R64_UINT`, and strict/non-strict nonresident behavior while skipping invalid uniform sparse-read and storage sparse-fetch combinations ([`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1838-L1884)). The texel shader path either emits GLSL `texelFetch`/`imageLoad` or SPIR-V `OpImageSparseFetch`/`OpImageSparseRead`, then validates returned values or residency-status words per sparse slot ([`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1258-L1400), [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1683-L1747)).

### vertex_buffer — sparse vertex input draw coverage

The `vertex_buffer` branch registers the default four flag variants from `groups[]` and repeats them with `device_group_` prefixes; it excludes the strict-only fifth entry through `numGroupsDefaultList` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2594-L2597), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2691-L2708)). The test fills sparse chunks with grid vertices, binds the sparse buffer as a vertex buffer twice, draws two half-view grids, and relies on image-readback error-pixel detection ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1142-L1294), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1312-L1353)).

### index_buffer — sparse index-buffer draw coverage

The `index_buffer` branch uses the same four default flag variants and device-group-prefixed variants as `vertex_buffer` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2710-L2727)). The instance creates a regular vertex buffer, fills sparse index chunks, binds the sparse buffer with `cmdBindIndexBuffer`, draws indexed primitives from two offsets, and uses the common rendered-image check ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1355-L1424)).

### indirect_buffer — sparse indirect draw command coverage

The `indirect_buffer` branch also uses the four default flag variants and device-group-prefixed variants ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2729-L2746)). The instance writes `VkDrawIndirectCommand` records into sparse chunks and executes two `cmdDrawIndirect` calls from different offsets, then uses the common rendered-image check ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1426-L1487)).

### transform_feedback — sparse transform-feedback buffer residency

The `transform_feedback` branch registers one `sparse_residency` test with `TEST_FLAG_RESIDENCY | TEST_FLAG_TRANSFORM_FEEDBACK` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2748-L2755)). The instance binds a sparse transform-feedback buffer, emits vertex indices through transform feedback, copies the sparse-buffer contents back, and samples selected entries for equality with their indices ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1707-L1796)).

### indirect_dispatch — sparse indirect dispatch command buffer

The `indirect_dispatch` branch registers one `sparse_residency` test ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2757-L2764)). It leaves a hole at the beginning of a sparse indirect buffer, copies a `VkDispatchIndirectCommand` into a bound region at `sparseChunkSize + 4`, dispatches compute with `cmdDispatchIndirect`, and verifies the output buffer contains `135 + i` for each written index ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1826-L1980)).

### misc — non-VulkanSC null-address sparse-buffer behavior

The non-VulkanSC `misc` branch generates `null_address_*` cases over local-invocation-index use, descriptor-vs-buffer-address path, map-first behavior, and read-vs-write mode ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2044-L2057), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2766-L2791)). The instance checks mapped and unmapped sparse-buffer behavior against zero and nonzero vectors, using descriptors or buffer-device-address push constants depending on the case ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2140-L2154), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2262-L2505)).

### memory_copy_indirect — sparse destination via indirect memory copy

The `memory_copy_indirect` branch registers the four default non-strict group names with `TEST_FLAG_USE_COPY_INDIRECT | TEST_FLAG_USE_BUFFER_ADDRESS` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2793-L2808)). The instance builds indirect copy commands with source and sparse-destination buffer device addresses, uses `cmdCopyMemoryIndirectKHR` with sparse destination flags, then draws from the sparse vertex buffer and checks for no error pixels ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1489-L1705)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Top-level direct children | `transfer`, `ssbo`, `ubo`, `texel_buffers`, `vertex_buffer`, `index_buffer`, `indirect_buffer`, `transform_feedback`, `indirect_dispatch`, optional `misc`, and `memory_copy_indirect` are registered in [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808). |
| Sparse flags | Local names map to none, aliased, residency, residency+aliased, and residency+nonresident-strict flags in `groups[]` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2592)). |
| Device groups | Several branches repeat names with `device_group_` prefix or call helper builders with `useDeviceGroups=true` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2607-L2610), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2668-L2675)). |
| Helper buffer sizes | Binding/aliasing/residency helpers use `2^10`, `2^12`, `2^16`, `2^17`, `2^20`, and `2^24`; rebind uses `2^16`, `2^18`, `2^20`, and `2^24` ([`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L348-L356), [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L412-L418)). |
| Nonresident commands | Nonresident sparse-buffer cases cover copy, fill, and update commands through `BufferInitCommand` and `getbufferInitCmdName()` ([`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L65-L83), [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1169-L1173)). |
| Texel-buffer parameters | Texel-buffer cases vary uniform/storage type, sparse-fetch/sparse-read/read operation, sizes `2^10`, `2^16`, `2^24`, R32/R64 UINT formats, and strict flag ([`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1838-L1884)). |

## Support / Feature Requirements

Common sparse-buffer cases require `sparseBinding`; residency cases require `sparseResidencyBuffer`; aliased cases require `sparseResidencyAliased`; strict cases require `sparseProperties.residencyNonResidentStrict`; transform-feedback cases require `VK_EXT_transform_feedback` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2016-L2032)). The base device builder selects requested sparse, compute, graphics, and transfer queues and raises `NotSupportedError` when requirements cannot be matched ([`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L158-L194)). Device-group mode additionally requires at least two physical devices and enables the device-group extension path ([`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L109-L131)). Indirect memory copy requires both `VK_KHR_copy_memory_indirect` and `VK_KHR_buffer_device_address` ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2509-L2520)). Texel-buffer R64 cases require the shader-image-atomic-int64 extension and 64-bit shader/atomic features ([`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1213-L1256)).

## Verification Methods

The buffer page uses three visible verification styles: byte-for-byte host comparisons after copy/readback in helper files ([`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L326-L338), [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1120-L1161)); rendered-image checks where green means success and red/blank pixels mean failure ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L447-L462), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L702-L713)); and compute-output vector checks for indirect dispatch and null-address behavior ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L1970-L1980), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2476-L2505)).

## Test Principles Observed

- Sparse buffers are exercised as transfer, descriptor, vertex, index, indirect, transform-feedback, indirect-dispatch, and buffer-device-address resources; each usage is tied to an explicit registered child in [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808).
- The tests deliberately use holes, aliasing, rebinding, device-group memory-device/resource-device indices, and nonresident reads/writes rather than only fully bound sparse buffers ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L117-L153), [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L579-L615)).
- Cases prefer observable data-path checks: host memory comparisons, shader/compute results, or rendered output rather than only successful API calls.

## Notes / Uncertainties

- Helper files such as [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L348-L356) register cases only when called from [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2602-L2614); they do not create independent top-level `sparse_resources.*` roots in the inspected dispatcher.
- The `misc` subtree is excluded when `CTS_USES_VULKANSC` is defined, as shown by the preprocessor guard around registration ([`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2766-L2791)).
