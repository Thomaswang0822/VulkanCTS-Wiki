# Understanding Brief: Image2DViewOf3D

## One-Sentence Test Purpose

This test checks whether an implementation can use a single slice of a 3D image through a 2D image view for storage-image, separate-sampler, and combined-image-sampler descriptor access.

## Background Knowledge

### 2D views of 3D images

`VK_EXT_image_2d_view_of_3d` permits a 2D view that selects one depth slice of a 3D image. The view selects one mip level and one layer-like depth index, so shader access through that view must address the selected 2D slice rather than the whole 3D image. The feature structure describes `image2DViewOf3D` and the additional `sampler2DViewOf3D` support used for sampling in [the feature chapter](../../../../vulkan-docs/src/chapters/features.adoc#L7437-L7463).

Why it matters here:
- The test selects the first and final depth slices at mip levels `0` and `2`.
- Storage-image access and sampled access exercise different descriptor forms against the same kind of view.

### Sparse binding

A sparse image can bind its memory through `queueBindSparse` instead of the ordinary image-memory binding path. This test uses the sparse-binding variant only after enabling the required sparse capabilities; its image still needs to expose the same selected 2D view.

## One Concrete Example

A representative monolithic fragment path is:

```text
dEQP-VK.pipeline.monolithic.image_2d_view_3d_image.fragment.sampler.mip2_layer15_sparse
```

The test creates a `64 x 64 x 64` 3D image, chooses mip level `2`, and selects layer `15`, the final slice of that mip. For sampler cases, it uploads a chess pattern into that slice, samples through the 2D view, writes the result to a 2D result image, and compares the copied result with a 2D reference image.

## End-to-End Test Flow

```text
[host] select access type, binding type, mip level, and first or final slice
[host] create a 3D image with VK_IMAGE_CREATE_2D_VIEW_COMPATIBLE_BIT_EXT
[host] allocate normal memory or bind sparse memory through queueBindSparse
[host] create a VK_IMAGE_VIEW_TYPE_2D view for the selected mip level and slice
[host] upload the chess-pattern input for sampled cases, or clear the storage image
[host] bind storage, separate-sampler, or combined-image-sampler descriptors
[device] run a compute pipeline for monolithic construction, or a fragment pipeline
[host] copy the observed image data to a host-visible buffer and compare it with the reference
```

## Generated Test Artifacts and Bound Resources

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 3D test image | yes | yes | read or written through the 2D view | yes | Supplies the 3D storage whose selected slice is tested. |
| 2D image view | yes | descriptor view | accessed by the shader | no | Selects one mip level and one 3D-image slice. |
| input buffer and image data | sampled cases | yes | copied into the 3D image | no | Provides the chess pattern. |
| 2D result image | sampled cases | yes | shader writes it | yes | Captures sampled output for comparison. |
| output buffer | yes | yes | transfer destination | yes | Holds copied image data for host validation. |

## What Is Checked

The host builds a one-slice 2D reference image containing the expected chess pattern. It copies the result to `outputBuffer` and uses [`tcu::floatThresholdCompare`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L796) with a `0.01f` threshold. A mismatch fails the case with `Pixel comparison failed.`

## Behavior Parameter Identification

> **Behavior parameter:** descriptor access type
>
> **Candidate values:** `storage`, `sampler`, `combined_image_sampler`

The execution stage is an important secondary split: `compute` is registered only under the monolithic construction type, while `fragment` is registered for each applicable variant.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storage` | The implementation may create, bind, or access the selected 2D view of the 3D image incorrectly through a storage-image descriptor. |
| `sampler` | The implementation may handle the selected 2D view, separate sampled-image and sampler descriptors, or sampled readback incorrectly. |
| `combined_image_sampler` | The implementation may handle the selected 2D view or the combined image sampler descriptor incorrectly. |

A failure limited to a sparse suffix can also indicate sparse-image allocation, binding, or sparse-queue synchronization trouble before the shader access.

## Important Variations and Special Cases

- Registration covers `storage`, `sampler`, and `combined_image_sampler` for both `fragment` and, in the monolithic construction type, `compute`.
- Each descriptor access type covers mip levels `0` and `2`, first and final slices, and normal and `_sparse` binding variants. The monolithic mustpass file contains 48 matching leaves: 24 compute and 24 fragment. Each non-monolithic pipeline variant contributes 24 fragment leaves.
- The test requires `image2DViewOf3D`; non-storage cases also require `sampler2DViewOf3D`. Fragment cases require `fragmentStoresAndAtomics`; sparse cases require sparse binding and `VK_KHR_maintenance9`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Feature checks | [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L831-L839) | Gates the required extension features. |
| Resource setup and validation | [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L409-L806) | Creates the image and view, runs work, and compares output. |
| Test registration | [`createImage2DViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1014-L1071) | Generates descriptor, mip, layer, and sparse variants. |
| Pipeline dispatcher | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L123-L124) | Attaches the family outside Vulkan SC. |

## Questions / Risk Points for User Audit

- Is the distinction between the 3D image and the selected 2D view clear?
- Does the descriptor-access behavior axis explain the failure mapping?
- Does the sparse variant need more detail for the intended reader?

## Conversion Notes for Final Wiki Rewrite

Use the descriptor access type as the primary behavior parameter. Carry the failure-cause mapping table into the final page unchanged. Keep the final page focused on 2D-view selection, descriptor form, execution stage, and the image comparison; move detailed source navigation to its appendix.
