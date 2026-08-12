# Understanding Brief: sparse buffer test family

## One-Sentence Test Purpose

This test family checks whether Vulkan sparse `VkBuffer` bindings remain correct when buffer data is transferred, accessed through descriptors or vertex input, used for indirect work, partially resident, aliased, rebound, or addressed through buffer-device-address operations.

## Background Knowledge

### Sparse buffer binding and residency

A sparse buffer is created with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT` and is mapped to memory in sparse blocks through `vkQueueBindSparse`. Sparse binding still requires the resource's accessed ranges to be backed before use. Sparse residency adds the option to leave ranges unbound. If `residencyNonResidentStrict` is supported, reads from an unbound range return zero and writes are discarded. Without that property, reads from an unbound range are undefined, so the test must avoid treating them as a fixed value.

### Aliasing and rebinding

With sparse aliasing, one physical memory range can serve more than one binding. Two buffer objects can therefore observe the same contents. Rebinding changes which memory backs a sparse range while the resource remains alive. The important observation is the data visible after the bind operation, not merely whether `vkQueueBindSparse` accepts the command.

## One Concrete Example

A representative descriptor case creates a sparse storage buffer, binds its sparse ranges, fills the bound data with `ivec4(3 * i ^ 127, 0, 0, 0)`, and leaves a resource hole for residency cases. The fragment shader reads each entry. A strict-residency case expects zero in the hole, while a non-strict case skips validation of that range. The shader writes green when all checked entries match and red otherwise; the host then scans the copied image.

This is a simplified description of the `BufferObjectTestInstance` path, not a replacement for the generated shader source.

## End-to-End Test Flow

```text
[host] select a registered buffer use, flags, size, and optional device-group mode
[host] query sparse memory requirements and construct memory binds, holes, or aliases
[host] create the sparse buffer and submit vkQueueBindSparse, waiting on a fence
[host] initialize staging data and copy it into the bound ranges
[host] submit transfer, graphics, compute, transform-feedback, or indirect work
[device] read and, for storage-buffer cases, write the sparse buffer through the selected use
[host] copy buffer or rendered results back to host-visible memory
[host] compare bytes, vectors, or rendered pixels with the expected result
[host] report a failed test case when any checked value differs
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The common graphics path generates `vert` and `frag` GLSL programs. The fragment program is specialized for data size and sparse chunk size and checks uniform-buffer or storage-buffer contents.
- Other paths generate compute shaders for aliased storage-buffer reads, sparse texel operations, indirect dispatch output, and buffer-device-address cases.
- Indirect draw and dispatch cases generate command records such as `VkDrawIndirectCommand` or `VkDispatchIndirectCommand` in buffer memory.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Sparse target `VkBuffer` | yes | yes, through sparse binds | yes | often | The resource whose block mapping is under test |
| Sparse `VkDeviceMemory` ranges | yes | through `VkSparseMemoryBind` | indirectly | no | Supplies bound blocks, holes, aliases, and rebind targets |
| Host-visible staging buffer | yes | yes | transfer source or destination | yes | Provides reference data and copyback |
| Descriptor-bound UBO or SSBO | yes | yes | shader read, and SSBO write | through image or buffer result | Exercises descriptor access to sparse ranges |
| Color and result buffers | yes | yes | rendering writes and transfer copy | yes | Converts graphics verification into a host scan |

## What Is Checked

- Transfer helpers compare copied bytes with the original data using `deMemCmp`.
- Graphics paths copy the color image to a host-visible buffer. Red or blank pixels indicate an error.
- Compute and indirect-dispatch paths compare output vectors with the expected sequence.
- Strict nonresident cases check zero reads and discarded writes in the unbound range.
- Aliasing and rebinding cases check the final contents seen through the relevant buffer mapping.

## Behavior Parameter Identification

> **Behavior parameter:** test family under `sparse_resources.buffer`
>
> **Candidate values:** `transfer`, `ssbo`, `ubo`, `texel_buffers`, `vertex_buffer`, `index_buffer`, `indirect_buffer`, `transform_feedback`, `indirect_dispatch`, `misc`, `memory_copy_indirect`

## What Failure Means

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

## Important Variations and Special Cases

- Default flag variants cover sparse binding, aliased binding, residency, and strict nonresident residency. Several graphics families repeat applicable variants with a `device_group_` prefix.
- Binding and rebind helpers cover power-of-two sizes including `2^10` through `2^24`; the exact set differs by helper.
- `misc` is excluded when `CTS_USES_VULKANSC` is defined. The sparse resource specification also says sparse resources are not supported in Vulkan SC.
- Device-group cases require at least two physical devices and check peer-memory capabilities. Transform feedback, indirect memory copy, buffer device address, and 64-bit texel cases add their corresponding feature or extension requirements.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Common registration and flag matrix | [`populateTestGroup()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L2565-L2808) | Defines the test category's families and variants |
| Common sparse setup and result scan | [`SparseBufferTestInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferTests.cpp#L838-L1085) | Creates queues, sparse buffers, rendering output, and pass/fail checks |
| Sparse binding and rebind helpers | [`vktSparseResourcesBufferSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseBinding.cpp#L149-L356), [`vktSparseResourcesBufferRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferRebind.cpp#L23-L418) | Implements transfer and rebinding cases |
| Residency and texel helpers | [`vktSparseResourcesBufferSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferSparseResidency.cpp#L1169-L1884) | Defines holes, strict behavior, commands, and texel variants |
| Aliasing helper | [`vktSparseResourcesBufferMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBufferMemoryAliasing.cpp#L246-L439) | Tests shared physical memory |
| Specification semantics | [`sparsemem.adoc`](../../../../../vulkan-docs/src/chapters/sparsemem.adoc#L7-L20) | Defines sparse binding, residency, and rebind behavior |

## Questions / Risk Points for User Audit

- The page groups several mechanisms under one behavior axis because the source registers them below one `sparse_resources.buffer` test category. Is that grouping useful for readers?
- The exact mustpass file contains a large generated inventory. The page should describe its dimensions without reproducing thousands of leaves.
- Shader walkthroughs are intentionally summarized here; the final page should add only source-backed representative generated shader material if the shader-analysis workflow is available.

## Conversion Notes for Final Wiki Rewrite

Keep `sparse_resources.buffer` as the registration root and explain each direct test family by the resource use it exercises. Carry the behavior parameter and failure mapping into the final page. Keep the final Background Knowledge to sparse binding, residency, aliasing, and rebinding. Put helper filenames and line ranges in the appendix. Preserve the strict-residency distinction and the Vulkan SC exclusion because both change how results must be interpreted.
