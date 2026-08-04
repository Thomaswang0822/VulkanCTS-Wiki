## Overview

**Core question:** Can a shader correctly access one selected slice of a 3D image through a 2D image view?

- [`vktPipelineImage2DViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1) implements the `image_2d_view_3d_image` test family for `VK_EXT_image_2d_view_of_3d`.
- The tests access a selected 2D view of a 3D image through storage-image, separate-sampler, and combined-image-sampler descriptors.
- The file registers fragment cases for applicable pipeline variants and compute cases for monolithic construction.
- This page explains the registration matrix, the descriptor access forms, the host/device flow, and what an image mismatch indicates.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A 2D view of a 3D image selects one mip level and one depth slice. Shader operations through the view therefore use 2D coordinates while referring to that selected part of the 3D image. `image2DViewOf3D` enables this form of image view; `sampler2DViewOf3D` additionally enables sampled access, as defined in [the feature chapter](../../../../vulkan-docs/src/chapters/features.adoc#L7437-L7463).
- A storage-image descriptor permits shader image loads and stores. Sampled access uses either a separate sampled-image descriptor plus sampler descriptor, or a combined image sampler descriptor.
- Sparse binding creates an image whose memory binding is submitted with `queueBindSparse`. The sparse variant still has to expose the same selected 2D view and preserve the requested image contents.

## Registration Hierarchy

```text
pipeline.monolithic.image_2d_view_3d_image
├── compute
└── fragment
```

`compute` contains test cases only when `pipelineConstructionType` is `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`. `fragment` is registered for every applicable pipeline construction type. The dispatcher excludes the family from Vulkan SC with `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| execution stage | `compute`, `fragment` | Selects dispatch or graphics-pipeline execution. `compute` is monolithic only. | [`createImage2DViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1014-L1071) |
| descriptor access type | `storage`, `sampler`, `combined_image_sampler` | Selects storage access, separate sampled-image and sampler access, or combined sampled access. | [access-type registration](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1023-L1028) |
| `mipLevel` | `0`, `2` | Selects the 3D-image mip level for the 2D view. | [mip loop](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1033-L1036) |
| `layerNdx` | first and final slice of each selected mip | Checks both ends of the available depth range. For a base dimension of `64`, the registered final slices are `63` at mip `0` and `15` at mip `2`. | [layer selection](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1035-L1039) |
| image binding type | normal, `_sparse` | Selects ordinary memory binding or sparse memory binding. | [binding loop](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1039-L1051) |
| image format and base size | `VK_FORMAT_R8G8B8A8_UNORM`, `64 x 64 x 64` | Fixes the stored pixel format and the base 3D image extent. | [test parameters](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1042-L1049) |

The monolithic mustpass file has 48 leaves under this family: 24 `compute` and 24 `fragment`. Each non-monolithic applicable pipeline variant has 24 `fragment` leaves.

## Behavior Parameters

The primary behavior parameter is the descriptor access type. Each value accesses the same kind of selected 2D view, but uses a different descriptor contract.

### storage: storage-image write access

The test creates a `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` binding for the selected 2D view. The shader generates a chess pattern and writes it directly through the view with `imageStore`; it does not read the view. The host then copies the selected slice from the 3D image for comparison. This isolates storage-image writes through a 2D view of a 3D image.

### sampler: separate sampled image and sampler

The test creates separate `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` and `VK_DESCRIPTOR_TYPE_SAMPLER` bindings for the selected view. It uploads a chess pattern to the chosen 3D-image slice, samples through the 2D view, and writes the sampled result to a separate 2D storage image.

### combined_image_sampler: combined sampled access

The test binds the selected view with `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER`. It uses the same sampled-input and 2D-result-image model as `sampler`, but exercises the combined descriptor form instead of separate sampled-image and sampler bindings.

The `compute` and `fragment` test families execute these behavior values through different pipeline paths. Mip level, selected slice, and normal or sparse binding vary the resource instance without changing the primary descriptor-access behavior.

## Shader Analysis

The tested behavior includes shader access, but the source builds small parameterized shaders rather than keeping one fixed shader artifact. The relevant shader distinction is the access form selected above: storage paths use image operations, while sampled paths read through the selected 2D view and write to a result image. The registration matrix and host-side comparison are more useful here than a single representative generated shader walkthrough.

## Runtime Execution and Result Checking

- The test creates a 3D image with `VK_IMAGE_CREATE_2D_VIEW_COMPATIBLE_BIT_EXT`, three mip levels, and either sampled-image or storage-image usage according to the descriptor access type.
- Normal cases allocate image memory in the ordinary path. Sparse cases create the image, allocate memory blocks, bind them with `queueBindSparse`, and pass the resulting semaphore to the execution path.
- The test creates a `VK_IMAGE_VIEW_TYPE_2D` view with the selected `mipLevel` and `layerNdx` in its `VkImageSubresourceRange`.
- For sampled cases, the host fills the selected 3D-image slice with a chess pattern, uploads it through a buffer, clears a separate 2D result image, and binds that result image as storage output. Storage-image cases clear the test image before shader execution.
- The host selects a compute or fragment pipeline, records the associated commands, then copies the observed result to a host-visible `outputBuffer`.
- The test builds a depth-one reference image with the expected chess pattern and calls [`tcu::floatThresholdCompare`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L796) using a `0.01f` threshold. A failed comparison returns `Pixel comparison failed.`

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storage` | The implementation may create, bind, or access the selected 2D view of the 3D image incorrectly through a storage-image descriptor. |
| `sampler` | The implementation may handle the selected 2D view, separate sampled-image and sampler descriptors, or sampled readback incorrectly. |
| `combined_image_sampler` | The implementation may handle the selected 2D view or the combined image sampler descriptor incorrectly. |

A failure limited to a sparse suffix can also indicate sparse-image allocation, binding, or sparse-queue synchronization trouble before the shader access.

### Cause Analysis

#### 2D-view selection or descriptor access failure

**Possible failure symptoms:** The copied output differs from the chess-pattern reference, causing `tcu::floatThresholdCompare` to report a mismatch. The pattern of failures may be restricted to a descriptor access type, mip level, selected first or final slice, or execution stage.

**Possible implementation causes:** The implementation may associate the view with the wrong mip level or selected depth slice, fail to honor `VK_IMAGE_VIEW_TYPE_2D` access to the compatible 3D image, or mishandle the descriptor type used by the failing behavior value. The source comparison cannot distinguish these paths once the final pixel image mismatches, so source-level investigation should use the failing descriptor, view range, and registered suffix to narrow the cause.

#### Sparse binding setup or ordering failure

**Possible failure symptoms:** Only `_sparse` cases fail, while equivalent normal-binding cases pass. The observed output may contain missing or incorrect pixels before the final comparison.

**Possible implementation causes:** Sparse memory allocation or `queueBindSparse` submission may fail to make the image backing available to the subsequent pipeline work, or sparse-specific feature support may be incomplete. The test passes the sparse-binding semaphore into the execution path, so investigation should also examine sparse-queue and pipeline-work ordering.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_EXT_image_2d_view_of_3d` and `image2DViewOf3D`.
- `sampler` and `combined_image_sampler` cases also require `sampler2DViewOf3D`.
- Fragment cases require `fragmentStoresAndAtomics` because sampled paths write a result image and fragment execution uses storage-image operations.
- Sparse variants require `DEVICE_CORE_FEATURE_SPARSE_BINDING`, `VK_KHR_maintenance9`, and the `image2DViewOf3DSparse` property. The source also rejects a sparse image whose required memory exceeds `sparseAddressSpaceSize`.
- Vulkan SC does not register this family, and compute cases are restricted to monolithic pipeline construction.

### Design-based pruning

The generator tests only mip levels `0` and `2`, and only the first and final slice of each selected mip. This gives boundary coverage over the image's mip and depth selection without enumerating every slice. It fixes the image format to `VK_FORMAT_R8G8B8A8_UNORM` and base extent to `64 x 64 x 64` so the comparison can use one predictable chess-pattern reference.

## Key Takeaways

- The family verifies that a selected mip-level slice of a 3D image behaves as a 2D view for storage and sampled descriptor access.
- `storage`, `sampler`, and `combined_image_sampler` are the primary behavioral values; stage, mip, slice, and binding type extend their coverage.
- The test uses normal and sparse backing for the same view model, then compares the copied image against a depth-one chess-pattern reference.
- The monolithic variant covers both compute and fragment execution, while other applicable variants cover fragment execution only.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Feature checks | [`ComputeImage2DView3DImageTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L831-L839) | Checks required 2D-view and sampler features. |
| Resource setup and comparison | [`Image2DView3DImageTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L409-L806) | Creates images and views, executes work, copies results, and compares pixels. |
| Test registration | [`createImage2DViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1014-L1071) | Generates the access, mip, slice, sparse, and stage matrix. |
| Pipeline dispatcher | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L123-L124) | Adds the family outside Vulkan SC. |
| Feature definition | [`VkPhysicalDeviceImage2DViewOf3DFeaturesEXT`](../../../../vulkan-docs/src/chapters/features.adoc#L7437-L7463) | Defines `image2DViewOf3D` and `sampler2DViewOf3D`. |
