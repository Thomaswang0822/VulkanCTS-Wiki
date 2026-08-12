## Overview

**Core question:** Do sparse `VkBuffer` mappings produce the expected data when the buffer is transferred, bound to a pipeline, used for indirect work, partially resident, aliased, rebound, or accessed by address?

- This page covers the implementation and registrations rooted at `sparse_resources.buffer` in [`vktSparseResourcesBufferTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L24-L32).
- The test category contains direct buffer-use families plus delegated transfer, residency, aliasing, and rebind implementations.
- Cases validate results in host-visible memory, shader output, or both. Passing `vkQueueBindSparse` alone is not sufficient.
- The page explains the registration tree, the behavior variants, the host/device timeline, and what each failure can indicate.

## Background Knowledge

- Sparse binding lets a `VkBuffer` map non-contiguous ranges of one or more `VkDeviceMemory` allocations. A sparse buffer has a defined buffer-range to memory-range mapping for each contiguous bound range. See [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L7-L20).
- Sparse residency builds on sparse binding and permits unbound ranges. With `residencyNonResidentStrict`, reads from an unbound range behave as zero and writes are discarded. Without that property, reads from such a range are undefined, so the test skips those reads rather than comparing them with a fixed value. See [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L101-L119).
- Sparse aliasing lets multiple bindings observe the same physical memory. Rebinding changes the memory mapped to a range while the resource remains alive. These tests therefore inspect data after the bind operation, not only the API return value.

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

The direct children are registered by [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808). The `transfer` family delegates `sparse_binding`, `device_group_sparse_binding`, and `rebind` cases to helper files. `ssbo` delegates memory-aliasing and residency cases, while the other direct families use the common buffer-object implementation or their local implementation in the same source file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct test family | `transfer`, `ssbo`, `ubo`, `texel_buffers`, `vertex_buffer`, `index_buffer`, `indirect_buffer`, `transform_feedback`, `indirect_dispatch`, optional `misc`, `memory_copy_indirect` | Selects the buffer operation and its validation path | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2598-L2808) |
| Common sparse flags | `sparse_binding`, `sparse_binding_aliased`, `sparse_residency`, `sparse_residency_aliased`, `sparse_residency_non_resident_strict` | Selects full binding, aliasing, holes, or strict treatment of holes | [`groups[]`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2597) |
| Device-group mode | `device_group_` variants where registered | Separates resource-device and memory-device indices during sparse binding | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2607-L2610) |
| Helper buffer size | `2^10`, `2^12`, `2^16`, `2^17`, `2^20`, `2^24` in the binding, aliasing, and residency helpers; `2^16`, `2^18`, `2^20`, `2^24` for rebind | Changes the number and layout of sparse blocks exercised | [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L348-L356), [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L412-L418) |
| Nonresident operation | copy, fill, update | Checks how commands interact with holes | [`BufferInitCommand`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L65-L83) |
| Texel-buffer matrix | uniform or storage; sparse fetch, sparse read, or ordinary read; `2^10`, `2^16`, `2^24`; `VK_FORMAT_R32_UINT` or `VK_FORMAT_R64_UINT`; strict or non-strict | Varies the resource type, operation, format, and residency rule | [`addTexelBufferSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1838-L1884) |

## Behavior Parameters

The primary behavioral axis is the direct test family. Each family changes the operation performed on sparse memory rather than merely changing setup.

### `transfer` | bind, copy, and rebind

The sparse-binding cases register six sizes from `buffer_size_2_10` through `buffer_size_2_24`. They bind the sparse ranges, copy reference bytes into the buffer, copy them back, and compare the result. Rebind cases perform full binds, fills, a partial rebind, and a final copy-out. Device-group cases also select resource and memory devices.

### `ssbo` | storage-buffer reads and writes

The family covers sparse memory aliasing, sparse residency, nonresident copy/fill/update commands, and `read_write`. Aliasing binds two buffers to shared memory and verifies that a compute write through one is visible through the other. The direct `read_write` path enables residency and strict nonresident flags for a storage buffer.

### `ubo` | uniform-buffer descriptor access

The common buffer-object path creates a sparse UBO with the selected flags, initializes its data, and has a fragment shader check the values through a descriptor. Aliased and residency variants alter the sparse allocation layout; device-group variants repeat the supported flag set with device-group binding.

### `texel_buffers` | sparse texel operations

The helper varies uniform and storage texel buffers, sparse fetch and sparse read operations, ordinary reads, two unsigned formats, buffer sizes, and strict residency. Invalid combinations, such as uniform sparse read or storage sparse fetch, are skipped by the generator.

### `vertex_buffer` | vertex input

The test fills sparse ranges with grid vertices, binds the sparse buffer as a vertex buffer twice, and draws two half-view grids. The four default flag variants are repeated for device groups; the strict-only entry is excluded from this family.

### `index_buffer` | indexed input

A regular vertex buffer supplies positions while sparse index ranges supply indexed primitives from two offsets. The result uses the same image check as the other graphics paths.

### `indirect_buffer` | indirect draw commands

The test writes `VkDrawIndirectCommand` records into sparse ranges and executes two `cmdDrawIndirect` calls from different offsets. A rendered-image mismatch identifies an incorrect command fetch or subsequent draw result.

### `transform_feedback` | sparse transform-feedback output

One residency case binds a sparse transform-feedback buffer, emits vertex indices, copies the buffer back, and compares selected entries with their indices. The family requires `VK_EXT_transform_feedback`.

### `indirect_dispatch` | indirect compute dispatch

The test leaves a hole at the start of a sparse indirect buffer, places a `VkDispatchIndirectCommand` at `sparseChunkSize + 4`, and calls `cmdDispatchIndirect`. It checks that the output buffer contains `135 + i` for each expected index.

### `misc` | null-address behavior

On non-VulkanSC builds, generated cases vary local-invocation-index use, descriptor versus buffer-device-address access, map-first behavior, and read versus write mode. The test compares mapped and unmapped behavior with the expected zero or nonzero vectors.

### `memory_copy_indirect` | indirect copy to sparse memory

The four non-strict variants use `VK_KHR_copy_memory_indirect` and `VK_KHR_buffer_device_address`. The test builds copy commands containing source and sparse-destination addresses, calls `cmdCopyMemoryIndirectKHR`, then draws from the sparse vertex buffer and checks the image.

## Shader Analysis

Several families use generated GLSL or SPIR-V, but no single shader represents the whole page. The common graphics shader reads `ivec4` entries from a descriptor-bound UBO or SSBO. It checks `3 * ndx ^ 127`, skips non-strict holes, or expects zero for strict nonresident reads. Storage-buffer cases write a value and read it back. Texel and buffer-device-address helpers use separate generated paths. The page therefore keeps shader details at the behavioral level and uses the source links in the appendix for the exact generators.

## Runtime Execution and Result Checking

- The common instance requests a sparse-binding queue and a graphics/compute queue. If the families need separate queue families, it creates the buffer with concurrent sharing for those families. The base device setup reports `NotSupportedError` when the requested queues or features are unavailable ([`SparseResourcesBaseInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194)).
- The host queries sparse requirements, constructs memory binds, resource holes, memory holes, or aliased binds, creates the buffer, and submits `vkQueueBindSparse`. The bind helper waits on a fence before later work uses the resource ([`bindSparseBuffer`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L788-L837)).
- Staging data initializes bound ranges. Families then submit transfer, draw, compute, transform-feedback, indirect draw, indirect dispatch, or indirect-copy work.
- Graphics paths copy the color image to a host-visible buffer. `imageHasErrorPixels()` treats red or blank pixels as failure ([`imageHasErrorPixels()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L447-L462)).
- Transfer and residency helpers compare host-visible bytes. Compute and indirect-dispatch paths compare result vectors. The test case fails when the relevant comparison finds a mismatch.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `transfer` | Incorrect sparse block binding, device-group bind indices, or rebind result |
| `ssbo` | Incorrect aliasing, residency semantics, sparse read/write behavior, or copy/fill/update handling |
| `ubo` | Incorrect descriptor access to sparse uniform-buffer data or flag handling |
| `texel_buffers` | Incorrect sparse texel fetch/read, format handling, or residency-status result |
| `vertex_buffer` | Incorrect vertex-input access to sparse ranges |
| `index_buffer` | Incorrect indexed draw access to sparse ranges |
| `indirect_buffer` | Incorrect indirect command fetch from sparse memory |
| `transform_feedback` | Incorrect sparse transform-feedback writes or copyback |
| `indirect_dispatch` | Incorrect indirect dispatch command fetch or output writes |
| `misc` | Incorrect null-address, mapping, descriptor, or buffer-device-address behavior |
| `memory_copy_indirect` | Incorrect indirect copy to a sparse destination or subsequent vertex access |

### Cause Analysis

#### Sparse mapping, holes, aliases, or rebinding

**Possible failure symptoms:** Copyback differs from the reference bytes, an alias does not observe the other buffer's write, or a partially rebound range contains the wrong pattern.

**Possible implementation causes:** The implementation may apply a `VkSparseMemoryBind` at the wrong buffer offset, use the wrong memory range, mishandle a resource or memory hole, or fail to make a shared or rebound mapping visible as required. The source and the sparse-resource specification support these interpretations; a more specific driver or hardware cause needs investigation.

#### Sparse access through a buffer operation

**Possible failure symptoms:** The rendered image contains red or blank pixels, an indirect command produces the wrong draw or dispatch, transform feedback contains an unexpected index, or a compute result differs from its expected vector.

**Possible implementation causes:** The operation may fetch from the wrong sparse range, or the implementation may mishandle sparse residency while reading or writing through the selected pipeline or transfer operation. The exact cause requires investigation of the failing family and parameter values.

#### Nonresident or feature-gated behavior

**Possible failure symptoms:** A strict-residency case observes a nonzero value in an unbound range, fails to discard a write, or a supported texel, transform-feedback, device-group, or indirect-copy case cannot produce the checked result.

**Possible implementation causes:** The implementation may apply the wrong `residencyNonResidentStrict` semantics or may not correctly enable or use the feature path required by that case. An unsupported device should be rejected during capability checks rather than fail the data comparison.

## Case Pruning

### Requirement-based pruning

- Sparse binding is required for all sparse-buffer cases. Residency cases require `sparseResidencyBuffer`; aliased cases require `sparseResidencyAliased`; strict cases require `sparseProperties.residencyNonResidentStrict` ([`checkSupport()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2016-L2032)).
- Device-group cases require at least two physical devices and suitable peer-memory features ([`SparseResourcesBaseInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L109-L131)).
- Transform feedback, indirect memory copy, buffer device address, and 64-bit texel cases require their corresponding extensions and features.
- `misc` is omitted under `CTS_USES_VULKANSC`. Vulkan SC does not support sparse resources ([`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L23-L32)).

### Design-based pruning

- The generators omit invalid texel-buffer operation and type combinations.
- The `vertex_buffer`, `index_buffer`, and `indirect_buffer` families use the four default flag variants and omit the strict-only variant because that behavior is not part of those test shapes.
- Helper files register their cases under the `buffer` root only when `populateTestGroup()` calls them; they do not create separate top-level test categories.

## Key Takeaways

- `sparse_resources.buffer` tests observable buffer behavior across transfer, descriptors, fixed-function input, indirect commands, transform feedback, and address-based access.
- Holes, aliases, rebinds, and device-group indices are tested through data comparisons or rendered output, not just successful bind calls.
- Strict residency changes the expected value for an unbound range. Non-strict cases avoid asserting a value for that range.
- A failure identifies the tested operation and mapping combination. The exact implementation cause still depends on the failing family and its parameters.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration and direct families | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2808) | Defines the complete `sparse_resources.buffer` tree |
| Common buffer-object setup and shader | [`BufferObjectTestInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L838-L1085) | Covers UBO and SSBO descriptor paths |
| Graphics result handling | [`Renderer::draw()` and `imageHasErrorPixels()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L447-L462) | Copies and checks rendered output |
| Sparse binding helper | [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L149-L356) | Tests copy-in/copy-out binding cases |
| Sparse residency and texel cases | [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1120-L1884) | Tests holes, commands, and sparse texel operations |
| Sparse memory aliasing | [`vktSparseResourcesBufferMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L246-L439) | Tests shared memory through two sparse buffers |
| Sparse rebind | [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L23-L418) | Tests partial rebinding and final contents |
| Queue and device setup | [`vktSparseResourcesBase.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.cpp#L88-L194) | Selects sparse, graphics, compute, and device-group support |
| Mustpass evidence | [`sparse-resources.txt`](../../../mustpass/main/vk-default/sparse-resources.txt) | Records executable `dEQP-VK.sparse_resources.*` paths |
| API test plan | [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276) | Places sparse buffers in the Vulkan test plan |
