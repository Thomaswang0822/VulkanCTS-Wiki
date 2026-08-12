# Understanding Brief: MultisampledImageSparseBinding

## One-Sentence Test Purpose

This test checks whether Vulkan correctly binds and accesses a fully resident sparse 2D multisampled storage image across supported formats and sample counts.

## Background Knowledge

### Opaque sparse binding

A sparse image created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` uses opaque address ranges. The application must bind the complete image before device use, but the mapping from texel coordinates to memory offsets is implementation-dependent. The test therefore binds the image's complete memory requirement in alignment-sized ranges and validates image access rather than assuming a texel-to-offset mapping.

### Multisampled storage images

A multisampled storage image has several samples for each pixel. The shader uses `image2DMS` and accesses sample 0. The selected sample count still controls image creation, format properties, and the value written for verification.

## One Concrete Example

For `r32ui.samples_4`, the host creates a `256x128` 2D sparse image with four samples and `VK_IMAGE_USAGE_STORAGE_BIT`. The generated compute shader stores `4` into sample 0 at each invocation coordinate, loads that sample, converts the loaded value to `uvec4`, and writes it to an `r32ui` result image. The host copies the result image to a buffer and expects every element to equal `4`.

## End-to-End Test Flow

```text
[host] select one format and one sample count
[host] check sparse binding, multisampled storage-image, format, size, and sample-count support
[host] create a 2D sparse image, allocate alignment-sized memory ranges, and package opaque binds
[host] submit vkQueueBindSparse and signal a semaphore
[host] submit an empty sparse-queue command buffer waiting on the semaphore
[host] create a resident result image, a host-visible result buffer, descriptors, and a compute pipeline
[device] execute one compute invocation per image element
[device] store the selected sample count to sample 0, load it, and write the value to the result image
[host] copy the result image to the host-visible buffer
[host] compare every uint32 result with the selected sample count
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test builds one GLSL compute source string for each format and sample-count case. The source declares the selected typed `image2DMS` storage image and an `r32ui` write-only result image. The sample count is embedded in the `imageStore` value.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Sparse multisampled image | yes | yes, through opaque sparse binds | shader reads and writes sample 0 | no | The tested resource. |
| `VK_FORMAT_R32_UINT` result image | yes | yes | shader writes, transfer reads | copied to buffer | Converts the shader observation into host-readable data. |
| Host-visible result buffer | yes | yes | transfer writes | yes | Supplies the pass/fail values. |
| Descriptor set and compute pipeline | yes | n/a | binds both storage images | no | Connects the generated shader to the resources. |

## What Is Checked

The host reads one `uint32_t` per image element. The test passes only when every element equals `m_params.sampleCount`. A missing memory type, unsupported case, or any mismatched result fails or skips the case according to the source path.

## Behavior Parameter Identification

> **Behavior parameter:** format and sample-count test case
>
> **Candidate values:** 11 format values (`rgba32f`, `rgba16f`, `r32f`, `rgba32ui`, `rgba16ui`, `rgba8ui`, `r32ui`, `rgba32i`, `rgba16i`, `rgba8i`, `r32i`), each crossed with `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, and `samples_64`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any format with any registered sample count | Sparse image creation or opaque binding, multisampled storage-image access, queue synchronization, result copyback, or host validation does not produce the selected sample count. |
| Floating-point format value | Format-specific storage-image access or conversion to the unsigned result image may be incorrect. |
| Signed or unsigned integer format value | Typed shader image declaration, storage-image access, or conversion to the unsigned result image may be incorrect. |

## Important Variations and Special Cases

The format list covers floating-point, unsigned-integer, and signed-integer storage images. The shader selects no GLSL prefix for floating-point formats, `u` for unsigned formats, and `i` for signed formats. Sample counts extend through 64 samples, unlike the separate multisampled sparse-residency family, because this binding-only test does not require sparse residency sample-count feature gates.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Support checks and generated shader | [`MultisampledImageSparseBindingCase`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L139-L214) | Defines feature gates, format checks, and shader behavior. |
| Sparse image creation and opaque binds | [`MultisampledImageSparseBindingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L246-L368) | Shows complete alignment-sized binding and semaphore ordering. |
| Dispatch and result checking | [`MultisampledImageSparseBindingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L419-L518) | Defines execution, copyback, and pass/fail behavior. |
| Registration matrix | [`createSparseResourcesMultisampledImageCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L671-L713) | Defines exact format and sample-count paths. |
| Sparse binding semantics | [`Sparse Resource Features`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#sparsememory-sparseresourcefeatures) | Defines sparse binding and multisampled sparse-residency distinctions. |

## Questions / Risk Points for User Audit

- Does the distinction between opaque fully resident binding and sparse residency remain clear?
- Is the format and sample-count matrix sufficiently explicit without repeating every leaf?
- Does the result-image conversion need a more detailed format-specific explanation?

## Conversion Notes for Final Wiki Rewrite

Keep the final page focused on the one registered test family. Distill opaque sparse binding, sample-count support, generated typed `image2DMS` access, sparse-queue synchronization, and all-element result checking into the Level-3 sections. Use the failure mapping table above as the final page's mapping table and write cause analysis separately.
