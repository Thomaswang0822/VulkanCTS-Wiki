## Overview

**Core question:** Does a partially resident multisampled storage image return the selected sample count from bound tiles and zero from its unbound tile row?

- `vktSparseResourcesMultisampledImageSparseResidency.cpp` registers the `sparse_resources.multisampled_image_sparse_residency` test family.
- Each test case uses a 2D `256x512x1` image, one mip level, one array layer, one of 11 formats, and 2, 4, 8, or 16 samples.
- The test binds every sparse tile except the lowest row. A compute shader writes the sample count, loads the image with sparse residency operations, and records either that value or zero in an `r32ui` result image.
- The host copies the result image to a buffer and checks the bound and unbound regions separately.

## Background Knowledge

- Sparse image residency allows an image to exist while only selected image tiles have memory bound. This test relies on `residencyNonResidentStrict`, which requires nonresident accesses to have the strict behavior checked here.
- A multisampled storage image stores multiple samples per pixel. The shader addresses sample 0 of an `image2DMS`; the selected sample count is still the value written and expected in the bound region.
- `sparseImageLoadARB` returns a residency status as well as the loaded value. The generated shader uses `sparseTexelsResidentARB` to turn a nonresident load into zero before writing the result image.

## Registration Hierarchy

```text
sparse_resources.multisampled_image_sparse_residency
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

Each format group contains `samples_2`, `samples_4`, `samples_8`, and `samples_16` test cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Format | `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT`, the four listed `UINT` formats, and the four listed `SINT` formats | Selects the storage-image type and format-specific GLSL prefix. | [`createSparseResourcesMultisampledImageResidencyCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L769-L801) |
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16` | Selects the multisample count and the matching sparse-residency feature. | [`getDeviceCoreFeature`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L71-L89), [`createSparseResourcesMultisampledImageResidencyCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L780-L797) |
| Image shape | `256x512x1`, 2D, one mip level, one array layer | Fixes the image and result-buffer extents for every case. | [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L343-L360) |
| Residency layout | All tiles except the lowest row are bound | Separates resident values from strict nonresident values. | [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L383-L444) |

## Behavior Parameters

The behavioral axis is the registered format/sample-count test case. Format changes the typed multisampled image access; sample count changes both the required device feature and the value expected in resident elements. Every combination uses the same image shape and partial-residency layout.

### Format groups

Floating-point groups are `rgba32f`, `rgba16f`, and `r32f`. Unsigned integer groups are `rgba32ui`, `rgba16ui`, `rgba8ui`, and `r32ui`. Signed integer groups are `rgba32i`, `rgba16i`, `rgba8i`, and `r32i`. The generated shader uses no GLSL type prefix for floating-point formats, `u` for unsigned formats, and `i` for signed formats.

### Sample-count groups

Each format has `samples_2`, `samples_4`, `samples_8`, and `samples_16`. The shader writes the selected count to sample 0. Resident result elements therefore contain `2`, `4`, `8`, or `16` after conversion to the `r32ui` result image.

## Shader Analysis

The test generates one compute shader for each format/sample-count combination. It declares the selected format as a multisampled storage image and declares an `r32ui` result image:

```glsl
#extension GL_ARB_sparse_texture2 : require
layout (set = 0, binding = 0, <format>) uniform <type>image2DMS u_msImage;
layout (set = 0, binding = 1, r32ui) writeonly uniform uimage2D u_resultImage;
```

`<type>` is empty, `u`, or `i` according to the selected format. Each invocation uses `gl_GlobalInvocationID.xy` as an image coordinate and operates on sample 0. It first stores the selected sample count in `u_msImage`. It then calls `sparseImageLoadARB` and checks the returned residency code with `sparseTexelsResidentARB`. For a nonresident texel it replaces the loaded value with a zero vector. Finally, it stores the value in `u_resultImage`.

The shader performs the residency decision explicitly. The host-side check can therefore distinguish a resident value that was not preserved from a nonresident value that was not returned as zero.

## Runtime Execution and Result Checking

1. The case checks `sparseBinding`, `sparseResidencyImage2D`, the feature matching its sample count, `shaderStorageImageMultisample`, and `shaderResourceResidency`. It also requires `residencyNonResidentStrict`, a supported 2D image size and format, and a sparse image memory footprint within `sparseAddressSpaceSize` ([`MultisampledImageSparseResidencyCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270), [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L362-L390)).
2. The instance creates separate sparse-binding and compute queues, then creates the 2D image with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT | VK_IMAGE_CREATE_SPARSE_BINDING_BIT` and `VK_IMAGE_USAGE_STORAGE_BIT`.
3. It queries sparse image granularity and binds tiles through the image granularity range except for the lowest row. A sparse-bind semaphore and an empty sparse-queue submission provide completion before compute work ([`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L392-L457)).
4. The compute submission clears the result image, transitions both images to `VK_IMAGE_LAYOUT_GENERAL`, binds the descriptor set and compute pipeline, and dispatches `imgSize.x`, `imgSize.y`, and `imgSize.z` workgroups.
5. The submission transitions the result image for transfer, copies it to a host-visible buffer, waits for the compute queue, and invalidates the allocation before reading it back ([`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L509-L597)).
6. The test expects every element in the bound prefix to equal `m_params.sampleCount` and every element in the unbound lowest-row suffix to equal zero. A single mismatch returns `tcu::TestStatus::fail("Failed")` ([`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L598-L621)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any format with `samples_2`, `samples_4`, `samples_8`, or `samples_16` | Sparse multisampled image creation or binding, sample-count support, storage-image access, sparse shader load, synchronization, result copyback, or host validation does not produce the expected values. |
| Floating-point format value | Format-specific storage-image or conversion behavior may affect the value written to the `r32ui` result image. |
| Unsigned or signed integer format value | Format-specific shader type selection, storage-image access, or conversion to the unsigned result image may be incorrect. |

### Cause Analysis

#### Sparse binding or image access

**Possible failure symptoms:** A resident result element is not equal to the selected sample count, or a nonresident result element is not zero.

**Possible implementation causes:** The sparse bind may cover the wrong tile range or image subresource. The image layout transition, sparse-queue completion, compute access, or result-image copy may also expose incorrect data. The failing case and test log are needed to identify the exact layer.

#### Sample-count feature or multisampled storage-image support

**Possible failure symptoms:** A case is rejected during support checks, or its resident values fail for one sample-count group while other groups pass.

**Possible implementation causes:** The implementation may report image format sample counts or sample-count-specific sparse residency features incorrectly, or may mishandle multisampled storage-image access for the selected count. The exact cause requires the device feature and format-property report.

#### Format-specific shader access or result conversion

**Possible failure symptoms:** Failures are limited to floating-point, unsigned-integer, or signed-integer format groups while the residency layout and sample count otherwise pass.

**Possible implementation causes:** The generated GLSL type prefix, typed `image2DMS` access, conversion to `uimage2D`, or format handling may produce a value different from the expected unsigned result. The failing format identifies the relevant typed-access path, but source-level investigation and the test log are needed to locate the defect.

## Case Pruning

### Requirement-based pruning

Support checks remove cases when the device lacks sparse binding, 2D sparse image residency, the feature for the selected sample count, multisampled storage-image support, shader resource residency, strict nonresident behavior, supported image format or size, sparse image support for the requested create info, or enough sparse address space. A case also fails support when no suitable memory type is available ([`MultisampledImageSparseResidencyCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270), [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L362-L399)).

### Design-based pruning

The matrix deliberately fixes the image to one 2D extent, one mip level, and one array layer. It tests sample counts from 2 through 16 and leaves one complete lowest tile row unbound instead of generating fully resident or other partial layouts. The source registers no `samples_1` case.

## Key Takeaways

- The test checks resident and strict nonresident behavior in one multisampled storage-image access path.
- The sample count is both a feature-gating dimension and the expected value in resident result elements.
- The format groups exercise floating-point, unsigned-integer, and signed-integer typed image accesses through the same residency layout.
- A failure can come from sparse binding, multisampled image access, shader residency handling, queue synchronization, copyback, or host validation; the failing format and sample-count case narrow the investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createSparseResourcesMultisampledImageResidencyCommonTests` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L769-L803) | Registers the 11 format groups and four sample-count cases per format. |
| `MultisampledImageSparseResidencyCase::checkSupport` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270) | Defines the feature, format, size, and strict-residency gates. |
| `MultisampledImageSparseResidencyCase::initPrograms` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L272-L307) | Generates the sparse multisampled-image compute shader. |
| `MultisampledImageSparseResidencyInstance::iterate` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L321-L621) | Creates resources, binds partial residency, dispatches compute, copies back, and checks results. |
| Shared sparse helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L161-L204), [`vktSparseResourcesBase.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp#L59-L114) | Provide sparse-resource support and instance infrastructure used by the test. |
