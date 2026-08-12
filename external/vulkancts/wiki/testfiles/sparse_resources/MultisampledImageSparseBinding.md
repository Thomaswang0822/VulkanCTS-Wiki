## Overview

**Core question:** Does a fully bound sparse 2D multisampled storage image preserve a value written and read through sample 0 for every supported format and sample count?

- `vktSparseResourcesMultisampledImageSparseBinding.cpp` implements the `sparse_resources.multisampled_image_sparse_binding` test family.
- Each format test family contains six sample-count test cases. The cases use a `256x128x1` 2D image with one mip level and one array layer.
- The host binds the complete opaque sparse-image address range, then a compute shader writes and reloads sample 0 before storing the value in an ordinary `r32ui` result image.
- The host copies the result image to a host-visible buffer and requires every element to equal the selected sample count.

## Background Knowledge

- Sparse binding lets an image use alignment-sized ranges from one or more memory allocations. With `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` without sparse residency, the complete image must be bound before device use, and the implementation defines the mapping from image coordinates to opaque memory ranges.
- A multisampled storage image stores multiple samples at each pixel. This test uses `image2DMS` and accesses sample 0, while the selected sample count still determines the image's creation and format-support requirements.

## Registration Hierarchy

```text
sparse_resources.multisampled_image_sparse_binding
├── rgba32f
├── rgba16f
├── r32f
├── rgba32ui
├── rgba16ui
├── rgba8ui
├── r32ui
├── rgba32i
├── rgba16i
├── rgba8i
└── r32i
```

Each format test family contains the test case leaves `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, and `samples_64` ([`createSparseResourcesMultisampledImageCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L671-L713)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Format | `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT`, `VK_FORMAT_R32G32B32A32_UINT`, `VK_FORMAT_R16G16B16A16_UINT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32G32B32A32_SINT`, `VK_FORMAT_R16G16B16A16_SINT`, `VK_FORMAT_R8G8B8A8_SINT`, `VK_FORMAT_R32_SINT` | Selects the typed multisampled storage image and the matching GLSL image declaration. | [`formats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L671-L680) |
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, `samples_64` | Selects the image sample count and the integer value written and expected by the result check. | [`samples`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L682-L701) |
| Image shape | `256x128x1`, 2D, one mip level, one array layer | Fixes the image extent and the number of compute invocations and result elements. | [`TestParams`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L132-L137), [`createSparseResourcesMultisampledImageCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L696-L701) |
| Binding layout | Complete opaque range, split at `VkMemoryRequirements::alignment` | Exercises complete sparse binding without testing a resident/nonresident image region. | [`MultisampledImageSparseBindingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L301-L354) |

## Behavior Parameters

The primary behavioral axis is the registered format/sample-count test case. The format changes the typed storage-image access, while the sample count changes image creation, support checks, the shader's stored value, and the expected host result. All cases use the same image extent and complete opaque binding flow.

### Format groups: floating-point

`rgba32f`, `rgba16f`, and `r32f` use floating-point multisampled storage-image declarations. The generated shader has no `u` or `i` type prefix for these formats.

### Format groups: unsigned integer

`rgba32ui`, `rgba16ui`, `rgba8ui`, and `r32ui` use unsigned-integer multisampled storage-image declarations. The generator adds the `u` prefix to the GLSL image type and vector constructor.

### Format groups: signed integer

`rgba32i`, `rgba16i`, `rgba8i`, and `r32i` use signed-integer multisampled storage-image declarations. The generator adds the `i` prefix to the GLSL image type and vector constructor.

### Sample-count leaves

Each format has `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, and `samples_64`. For a selected count `N`, every invocation stores `N` to sample 0, reloads it, and sends the loaded value to the `r32ui` result image.

## Shader Analysis

The test generates one compute shader per format/sample-count case. It declares the selected multisampled image at descriptor binding 0 and an `r32ui` result image at binding 1 ([`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L186-L213)). A representative source shape is:

```glsl
#version 450
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout (set = 0, binding = 0, <format>) uniform <type>image2DMS u_msImage;
layout (set = 0, binding = 1, r32ui) writeonly uniform uimage2D u_resultImage;

void main (void)
{
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    imageStore(u_msImage, ivec2(gx, gy), 0, <typed>vec4(N));
    <typed>vec4 color = imageLoad(u_msImage, ivec2(gx, gy), 0);
    imageStore(u_resultImage, ivec2(gx, gy), uvec4(color));
}
```

`<type>` and `<typed>` are empty for floating-point formats, `u` for unsigned formats, and `i` for signed formats. `N` is the selected sample count. The shader uses one invocation for each `x`, `y`, and `z` coordinate generated by the dispatch. The source is generated by [`MultisampledImageSparseBindingCase::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L186-L213).

## Runtime Execution and Result Checking

- Support checks require `sparseBinding`, a supported `256x128x1` 2D image size, `shaderStorageImageMultisample`, support for the selected format as an optimal-tiled storage image, and the selected sample count in the format's `sampleCounts` ([`checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L159-L184)).
- The instance creates one sparse-binding queue and one compute queue. It creates the image with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, the selected format and sample count, `VK_IMAGE_TILING_OPTIMAL`, and `VK_IMAGE_USAGE_STORAGE_BIT` ([`iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L246-L283)).
- The test queries the image memory requirements. It rejects a footprint larger than `sparseAddressSpaceSize`, divides the requirement into alignment-sized ranges, allocates one memory object per range, and packages the ranges in `VkSparseImageOpaqueMemoryBindInfo`.
- `vkQueueBindSparse` submits the opaque image binds and signals a semaphore. An empty submission on the sparse queue waits on that semaphore before the compute work uses the image ([`iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L295-L367)).
- The host creates and binds an `r32ui` result image and a host-visible transfer-destination buffer. It binds both images in a descriptor set, clears the result image, transitions resources to `VK_IMAGE_LAYOUT_GENERAL`, dispatches `256x128x1` workgroups, and transitions and copies the result image to the buffer ([`iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L370-L490)).
- After waiting for the compute queue and invalidating the result allocation, the host compares all `256 * 128` values with `m_params.sampleCount`. It returns `Passed` only when every value matches ([`iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L494-L518)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any format with any registered sample count | Sparse image creation or opaque binding, multisampled storage-image access, queue synchronization, result copyback, or host validation does not produce the selected sample count. |
| Floating-point format value | Format-specific storage-image access or conversion to the unsigned result image may be incorrect. |
| Signed or unsigned integer format value | Typed shader image declaration, storage-image access, or conversion to the unsigned result image may be incorrect. |

### Cause Analysis

#### Sparse binding or image access

**Possible failure symptoms:** One or more result elements differ from the selected sample count after the complete opaque bind and compute dispatch.

**Possible implementation causes:** The implementation may mishandle the opaque sparse-memory binds, image layout or access transitions, or storage-image read/write access. The failure pattern and test log are needed to distinguish those cases.

#### Sample-count support or multisampled storage-image access

**Possible failure symptoms:** A case is rejected during support checks, or failures occur for one sample-count group while other groups pass.

**Possible implementation causes:** The implementation may report format sample-count properties or multisampled storage-image support incorrectly, or may mishandle access for the selected count. The device feature and format-property report are needed for further investigation.

#### Format-specific typed access or conversion

**Possible failure symptoms:** Failures are limited to floating-point, unsigned-integer, or signed-integer format groups while other groups pass.

**Possible implementation causes:** The generated typed `image2DMS` declaration, format handling, or conversion from the loaded value to the `uimage2D` result image may produce a value other than the expected count. The failing format narrows the relevant path, but source-level investigation and the test log are needed to locate the defect.

#### Synchronization or result copyback

**Possible failure symptoms:** Result values are stale, inconsistent, or incorrect across the output image even though the shader and sparse image setup appear valid.

**Possible implementation causes:** Sparse-queue completion, compute execution, image barriers, image-to-buffer transfer, host invalidation, or queue-idle handling may not establish the visibility required by the host check. The exact failure pattern is needed to identify the failing stage.

## Case Pruning

### Requirement-based pruning

Support checks remove cases when the device lacks sparse binding, multisampled storage-image support, the requested image size or format, or the requested sample count. Runtime checks also remove cases when sparse image creation is unsupported, the image memory footprint exceeds `sparseAddressSpaceSize`, or no compatible memory type exists ([`checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L159-L184), [`iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L285-L321)).

### Design-based pruning

The matrix fixes the image to one 2D extent, one mip level, and one array layer. It uses complete opaque binding, so it does not generate partially resident regions or mip-tail layouts. The sample-count matrix starts at 2 and ends at 64, and the source does not register a single-sample case.

## Key Takeaways

- This test checks access to a fully bound opaque sparse multisampled storage image, not sparse residency behavior.
- The format and sample-count leaves exercise typed `image2DMS` access through one common bind, dispatch, and readback path.
- The selected sample count becomes both the value written by the shader and the value required at every host-visible result element.
- A failure can involve sparse binding, multisampled image access, synchronization, result transfer, or format conversion. The failing format and sample-count leaf narrow the investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createSparseResourcesMultisampledImageSparseBindingTests` | [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L710-L713) | Registers the `multisampled_image_sparse_binding` test family. |
| `createSparseResourcesMultisampledImageCommonTests` | [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L671-L707) | Registers the 11 format families and six sample-count leaves per format. |
| `MultisampledImageSparseBindingCase::checkSupport` | [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L159-L184) | Defines feature, format, size, and sample-count gates. |
| `MultisampledImageSparseBindingCase::initPrograms` | [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L186-L213) | Generates the compute shader. |
| `MultisampledImageSparseBindingInstance::iterate` | [`vktSparseResourcesMultisampledImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseBinding.cpp#L246-L518) | Creates resources, binds sparse memory, dispatches compute, copies back, and checks results. |
| Shared sparse helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L161-L182), [`vktSparseResourcesBase.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp#L59-L114) | Provide sparse binding and test-instance support. |
