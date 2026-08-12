## Overview

**Core question:** Can two sparse images alias the same resident image blocks while one image supplies input data and the other receives shader output?

- [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1-L22) implements the regular `sparse_resources.image_sparse_memory_aliasing` family and the device-group `sparse_resources.device_group_image_sparse_memory_aliasing` family.
- Both families cover 2D, 2D-array, cube, cube-array, and 3D images. The device-group family uses the same image-type matrix with device-group sparse-bind and submission metadata.
- Each case creates a read image and a write image. The images share the sparse residency-block memory binds, while their mip-tail allocations remain separate where the implementation requires it.
- The test copies reference data into the read image, dispatches compute shaders through the aliased write image, copies the read image back, and checks both the shader-written regions and the preserved reference regions.

## Background Knowledge

- Sparse binding lets an image reserve virtual address space while the application supplies memory for individual image blocks, mip tails, and metadata regions.
- Memory aliasing makes two resources refer to the same physical allocation. Writes through one resource can therefore be observed through another resource when the bindings and synchronization are correct.
- A sparse image can expose separate residency blocks and mip-tail requirements. This test aliases the ordinary residency blocks but tracks the read and write mip tails separately.
- Multi-planar formats may need plane-compatible storage-image views and copy regions. Cube and array images represent their layers through the image subresource layout; 3D images use depth instead.

## Registration Hierarchy

```text
sparse_resources.image_sparse_memory_aliasing
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The source registers the same five direct children under `sparse_resources.device_group_image_sparse_memory_aliasing`. Beneath each image-type group, registration expands through supported formats and the image sizes listed by the source.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `image_sparse_memory_aliasing`, `device_group_image_sparse_memory_aliasing` | Selects regular sparse binding or device-group sparse-bind and submission behavior. | [`createImageMemoryAliasingTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1104) |
| Image type | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects image dimensionality and layer or depth interpretation. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1060) |
| Image sizes | Four source-defined sizes per image type (for example, `512x256x1` for 2D, `512x256x6` for 2D-array, `256x256x1` for cube, and `256x256x16` for 3D) | Varies sparse-block counts, array layers, or 3D depth. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1054) |
| Format | Values from `getTestFormats(imageType)` | Changes channel representation, plane layout, alignment, and storage-image requirements. | [`getTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) |
| Device-group mode | `false` or `true` | Adds device-group information to sparse binds and submissions; it does not add image-type children. | [`createImageMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1091) |

The generator skips an image size when its dimensions fail the selected format's alignment requirements. This matters for formats, such as some YCbCr formats, whose valid image extents impose additional constraints. [`createImageMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1064-L1084)

## Behavior Parameters

The primary behavior choice is the registered image type. Format and extent select the concrete sparse image configuration within each family.

### `2d` : two-dimensional sparse image aliasing

The case creates two `VK_IMAGE_TYPE_2D` images with sparse binding, sparse residency, and sparse aliasing enabled. Both images use the same regular image-residency binds. The source registers four extents for each supported format. [`ImageMemoryAliasingInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L217-L245)

### `2d_array` : two-dimensional array image aliasing

The third extent component represents array layers. Copy regions and shader views use `getNumLayers()`, so validation covers every layer in the selected array configuration. [`ImageMemoryAliasingInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L223-L224), [`copyImageToBuffer`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L531-L540)

### `cube` : cube image aliasing

The source adds `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` for cube images. The shared layer mapping handles the six cube faces while the two images continue to share their regular sparse residency binds. [`ImageMemoryAliasingInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L234-L235)

### `cube_array` : cube-array image aliasing

Cube-array cases use cube-compatible creation and the shared array-layer handling. The same aliasing and readback checks apply to every selected face and array layer.

### `3d` : three-dimensional sparse image aliasing

The third extent component represents depth. The compute dispatch derives its grid from `getShaderGridSize()` and rejects configurations that exceed the device's workgroup limits before issuing `cmdDispatch`. [`ImageMemoryAliasingInstance::dispatchShader`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L734-L759)

## Shader Analysis

The test generates compute programs from the selected format and image dimensions. The shader writes deterministic per-channel values into the write image; the expected value uses the invocation index modulo 127. The source generates separate access details when a format needs a plane-compatible storage representation. [`generateComputeShader`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L932-L1022)

The validation path treats integer formats as exact comparisons. Fixed-point and floating-point formats use format-aware acceptable-error comparisons. This distinguishes an aliasing or synchronization error from ordinary representation rounding. [`verifyBufferData`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L856-L907)

## Runtime Execution and Result Checking

- `checkSupport()` requires aliased sparse residency, a supported image size and image type, and the relevant sparse image format properties. R64 formats additionally require `VK_EXT_shader_image_atomic_int64`, `shaderImageInt64Atomics`, and `sparseImageInt64Atomics`. [`ImageMemoryAliasingCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154)
- The instance checks storage-image support, storage-compatible plane formats, `sparseAddressSpaceSize`, memory-type compatibility, and peer-memory capabilities for cross-device cases. [`ImageMemoryAliasingInstance::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L247-L340)
- It creates the read and write images with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, `VK_IMAGE_CREATE_SPARSE_ALIASED_BIT`, and `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`. Cube-compatible images also receive the cube-compatible flag.
- The sparse bind gives both images identical regular residency binds. The instance keeps the mip-tail memory for the read and write images separate, then submits the bind with the required device-group metadata when `useDeviceGroup` is enabled. [`bindSparseImages`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L347-L492)
- A deterministic input buffer is copied into the read image. Compute dispatches write the aliased write image, after which the read image is copied back to a host-visible buffer. [`ImageMemoryAliasingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L564-L759)
- The host checks shader-written sparse blocks against generated values and checks the remaining mip-tail or reference data against the original input. [`ImageMemoryAliasingInstance::verify`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L929)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `2d` | Incorrect sparse aliasing, image layout transition, shader store, or transfer handling for a 2D image. |
| `2d_array` | Incorrect array-layer addressing or sparse binding for one or more layers. |
| `cube` | Incorrect cube-compatible setup, face mapping, sparse binding, or readback. |
| `cube_array` | Incorrect cube-face or array-layer mapping in the aliased access path. |
| `3d` | Incorrect depth handling, dispatch grid, sparse binding, or 3D image copy. |
| Any format | Unsupported storage-image or plane format handling, incorrect format-aware comparison, or an R64 feature mismatch. |
| Any device-group case | The regular path or its device-group bind, peer-memory selection, or device-targeted submission fails. |

### Cause Analysis

#### Shared residency binds do not alias as expected

**Possible failure symptoms:** Shader-written values are missing from the readback, or the returned data still contains the input pattern in blocks that the shader should have overwritten.

**Possible implementation causes:** The two images may not receive identical regular sparse binds, the implementation may resolve an alias to different physical memory, or a sparse bind may use the wrong offset, extent, aspect, or mip level. The failing format and sparse-bind record are needed to isolate the mapping error.

#### Synchronization or layout transition error

**Possible failure symptoms:** Results vary between runs, or the copied image contains stale data even though both images report compatible bindings.

**Possible implementation causes:** The sparse bind signal, image barriers, compute dispatch, or image-to-buffer copy may execute out of order. The source explicitly sequences these operations; the failing synchronization point requires investigation with the test log and command trace.

#### Mip-tail or plane data is corrupted

**Possible failure symptoms:** Shader-written blocks compare correctly, but mip-tail bytes or one plane differs from the original reference.

**Possible implementation causes:** The implementation may apply the shared residency binds to a mip-tail region that should use its own allocation, calculate plane offsets incorrectly, or mishandle a storage-compatible plane format during copyback.

#### Device-group targeting error

**Possible failure symptoms:** A failure occurs only under `device_group_image_sparse_memory_aliasing` or only for a particular physical-device pair.

**Possible implementation causes:** The sparse-bind device indices, peer-memory mapping, or command submission target may not match the selected resource and memory devices. The failing device pair and bind metadata are needed for attribution.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the selected extent exceeds image limits, the image type lacks sparse support, the format lacks the required sparse properties, or storage-image support is unavailable. The runtime also checks sparse address-space size, compatible memory types, and peer-memory copy or generic-destination features for cross-device cases. R64 formats require the extension and both 64-bit shader-image atomic features described above. [`checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154), [`checkSparseSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L247-L340)

### Design-based pruning

The registration keeps one image-type matrix for regular and device-group roots and passes `useDeviceGroup` into the common builder. Format-alignment checks remove invalid extents, while device-group mode changes bind and submission metadata rather than the direct-child hierarchy. [`createImageMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1104)

## Key Takeaways

- The defining check is physical-memory aliasing: both images share regular sparse image binds, then one image is written through compute while the other is read back.
- Mip tails remain separately managed where the source requires distinct read and write allocations, so the test checks aliasing without conflating it with tail binding.
- The same contract runs across 2D, array, cube, cube-array, and 3D image layouts, with format and extent filters removing unsupported combinations.
- Device-group cases reuse the image matrix and add device-targeted sparse binding and submission coverage.
- A passing case requires both the aliased shader-written blocks and the preserved reference data to survive the full bind, dispatch, and copy sequence.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test registration | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1104) | Defines regular and device-group roots, image types, extents, and format filtering. |
| `ImageMemoryAliasingCase::checkSupport` | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154) | Defines feature and format requirements, including R64 atomic support. |
| Image and sparse-bind setup | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L217-L492) | Creates both images and establishes their shared residency and separate tail binds. |
| Copy and dispatch flow | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L531-L759) | Copies input data, dispatches the write shader, and copies the aliased image back. |
| Result verification | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L1022) | Generates expected values and compares integer, fixed-point, and floating-point results. |
| Shared image helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L73-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Supplies image-type, format, plane, and sparse-support behavior shared by the family. |
| Sparse image semantics | [Vulkan sparse memory](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L497-L536) | Background for sparse image requirements, bindings, and image aspects. |

