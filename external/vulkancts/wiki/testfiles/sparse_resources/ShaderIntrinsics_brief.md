# Understanding Brief: ShaderIntrinsics

## One-Sentence Test Purpose

This test checks whether sparse image shader instructions return both the requested texel and a correct residency result when image mip levels have different sparse-memory bindings.

## Background Knowledge

### Sparse image residency

A sparse image can have independently bound image memory for its mip levels. This test binds alternating mip levels and uses the shader result's residency code to distinguish a texel read from a residency report.

### Sparse image operations

`OpImageSparseFetch`, `OpImageSparseRead`, and the sparse sampling and gather operations return a structure containing the operation result and a residency code. `OpImageSparseTexelsResident` converts that code into the Boolean used by the generated shader.

## One Concrete Example

The representative case `dEQP-VK.sparse_resources.shader_intrinsics.2d_sparse_read.<format>.11_37_1` uses the storage-image builder. For each invocation, the generated compute program forms a 2D coordinate from `gl_GlobalInvocationID`, performs `OpImageSparseRead`, writes the returned texel to one output image, and writes either `MEMORY_BLOCK_BOUND_VALUE` or `MEMORY_BLOCK_NOT_BOUND_VALUE` to a residency image.

## End-to-End Test Flow

```text
[host] choose image type, format, extent, operation, and optional operand
[host] create a sparse image and bind alternating mip levels; bind the mip tail
[host] fill reference texel data and copy it into resident sparse image memory
[host] generate the compute SPIR-V program and configure descriptors per mip level
[host] submit sparse binds, transfer operations, barriers, and compute dispatches
[device] execute the sparse image operation and write texel and residency images
[host] copy both output images back to buffers
[host] compare resident texels, mip-tail texels, and every residency value with references
[host] decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`SparseShaderIntrinsicsCaseStorage::initPrograms` emits SPIR-V assembly for a compute entry point. It declares one sparse image, one texel-output image, and one residency-output image per plane, plus specialization constants for the grid and workgroup sizes. The selected `Nontemporal` variant changes the target assembly to SPIR-V 1.6.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Sparse image | yes | sparse image memory is bound per mip level | read | indirectly through output | Supplies resident and nonresident mip data |
| Texel output image | yes | yes | written | yes | Captures the returned texel |
| Residency output image | yes | yes | written | yes | Captures the result of `OpImageSparseTexelsResident` |
| Per-mip descriptor set | yes | yes | used for image access | no | Selects the sparse, texel, and residency views for each mip level |
| Reference data and readback buffers | yes | yes | transfer source or destination | yes | Provide expected texels and host-side comparison data |

## What Is Checked

- The host expects even-indexed sparse mip levels and the mip tail to be resident, while odd-indexed levels remain nonresident.
- The residency output must match the corresponding bound or unbound reference value for every output texel.
- Resident mip texels and mip-tail texels must match the initialized reference data. Strict nonresident checks may require zero output when enabled by the case.

## Behavior Parameter Identification

> **Behavior parameter:** sparse intrinsic test family
>
> **Candidate values:** `2d_sparse_fetch`, `2d_array_sparse_fetch`, `3d_sparse_fetch`, `2d_sparse_read`, `2d_array_sparse_read`, `cube_sparse_read`, `cube_array_sparse_read`, `3d_sparse_read`, `2d_sparse_sample_explicit_lod`, `2d_array_sparse_sample_explicit_lod`, `2d_sparse_sample_implicit_lod`, `2d_array_sparse_sample_implicit_lod`, `2d_sparse_gather`, `2d_array_sparse_gather`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any sparse intrinsic family | Sparse image binding or image-operation behavior returned wrong texels or residency information; shader generation or descriptor setup selected the wrong operation or resource type |
| `*_nontemporal` case | The implementation did not support or correctly process the `Nontemporal` operand and its SPIR-V 1.6 variant |

## Important Variations and Special Cases

- Image type controls coordinate shape, array layers, cube compatibility, and the families that registration permits.
- Formats include single-plane, multi-planar, integer, floating-point, and R64 cases. R64 cases require `VK_EXT_shader_image_atomic_int64` features used by sparse image atomics.
- The smallest listed image size receives a second case with the `Nontemporal` operand. Format alignment can remove odd-sized cases, and sampled operations exclude cube, cube-array, and 3D images.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case registration and matrix | [`createSparseResourcesShaderIntrinsicsTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L51-L160) | Defines families, image types, sizes, formats, pruning, and operands |
| Storage shader builder | [`SparseShaderIntrinsicsCaseStorage::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L50-L415) | Emits the selected compute SPIR-V |
| Sparse operation printers | [`SparseCaseOpImageSparseFetch::sparseImageOpString`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L427-L464) | Shows the exact fetch/read instruction forms |
| Binding and execution | [`SparseShaderIntrinsicsInstanceStorage::recordCommands`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L531-L751) | Configures descriptors, specialization, dispatch, and barriers |
| Shared setup and checking | [`SparseShaderIntrinsicsInstanceBase::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L574-L845) | Creates sparse images, binds mip levels, and initializes references |
| Result comparison | [`SparseShaderIntrinsicsInstanceBase::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L986-L1238) | Copies outputs back and checks texel and residency results |

## Questions / Risk Points for User Audit

- Should the final page keep the intrinsic family as the primary behavior axis, or should the operation and image type be documented as two separate axes?
- Is one storage-image walkthrough sufficient, with sampled differences summarized in the variation table?
- The owning builder emits SPIR-V assembly directly rather than GLSL or HLSL. The final page should state this source fact instead of presenting a hand-translated shader as generated code.

## Conversion Notes for Final Wiki Rewrite

Use the storage compute path as the representative walkthrough because it exposes the sparse operation result and residency write in one shader. Keep the vertex and geometry stages out of the walkthrough unless a sampled case is added. Preserve the failure mapping table and distill the sparse residency prerequisite into the final Background Knowledge section.
