## Overview

**Core question:** Does each separately bound plane of a linear disjoint YCbCr image report a zero subresource offset?

- This page covers `ycbcr.subresource_offset`, implemented by `vktYCbCrImageOffsetTests.cpp`.
- The test creates one 8x8 linear image for each registered format, binds every plane to its own host-visible allocation, and queries each plane layout.
- A case passes only when every queried `VkSubresourceLayout::offset` is zero.
- The format list supplies the cases. The behavior and result check are host-side; this test has no shader code.

## Background Knowledge

- A multi-planar image stores its format components in separate planes. A disjoint image uses a separate memory binding for each plane, as specified for `VK_IMAGE_CREATE_DISJOINT_BIT` in [Image Creation Flags](../../../../vulkan-docs/src/chapters/resources.adoc#resources-image-create-flags).
- `VkSubresourceLayout::offset` describes where the queried subresource begins relative to the image or plane memory binding. Because this test queries separately bound planes, the expected offset is relative to each plane binding rather than the allocation's deliberately nonzero binding offset.

## Registration Hierarchy

```text
ycbcr.subresource_offset
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16r16_2plane_444_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8r8_2plane_422_unorm
└── g8_b8r8_2plane_444_unorm
```

`initYcbcrImageOffsetTests()` registers one test case for each entry in `formats::disjointPlanesFormats`. The category and test family are created by [`createImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154-L170).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | The 24 exact test case names in the registration tree | Selects the YCbCr bit width, plane count, and chroma sampling arrangement whose plane layouts are checked | [`initYcbcrImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154-L162) |
| Image extent | `8x8` | Keeps the image shape fixed while the format changes | [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93-L99) |
| Tiling and flags | `VK_IMAGE_TILING_LINEAR`, `VK_IMAGE_CREATE_DISJOINT_BIT` | Selects the linear disjoint image layout model under test | [`createImage()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L71-L90) |
| Plane aspects | `VK_IMAGE_ASPECT_PLANE_0_BIT`, `VK_IMAGE_ASPECT_PLANE_1_BIT`, `VK_IMAGE_ASPECT_PLANE_2_BIT` as applicable | Selects each plane that belongs to the format | [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L102-L112) and [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L136-L142) |
| Memory binding offset | `deAlign64(reqs.size, reqs.alignment)` | Places each plane binding at an aligned nonzero offset in a larger host-visible allocation, separating the binding offset from the queried plane-relative layout offset | [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L113-L131) |

## Behavior Parameters

The primary behavioral axis is the registered format test case. Each format changes the number and arrangement of planes, while the test applies the same per-plane offset rule.

### g10x6_b10x6_r10x6_3plane_420_unorm_3pack16

Checks the zero offset rule for a 10-bit, three-plane 4:2:0 format.

### g10x6_b10x6_r10x6_3plane_422_unorm_3pack16

Checks the rule for the corresponding 10-bit, three-plane 4:2:2 format.

### g10x6_b10x6_r10x6_3plane_444_unorm_3pack16

Checks the rule for the corresponding 10-bit, three-plane 4:4:4 format.

### g10x6_b10x6r10x6_2plane_420_unorm_3pack16

Checks the rule for a 10-bit, two-plane 4:2:0 format.

### g10x6_b10x6r10x6_2plane_422_unorm_3pack16

Checks the rule for a 10-bit, two-plane 4:2:2 format.

### g10x6_b10x6r10x6_2plane_444_unorm_3pack16

Checks the rule for a 10-bit, two-plane 4:4:4 format.

### g12x4_b12x4_r12x4_3plane_420_unorm_3pack16

Checks the rule for a 12-bit, three-plane 4:2:0 format.

### g12x4_b12x4_r12x4_3plane_422_unorm_3pack16

Checks the rule for a 12-bit, three-plane 4:2:2 format.

### g12x4_b12x4_r12x4_3plane_444_unorm_3pack16

Checks the rule for a 12-bit, three-plane 4:4:4 format.

### g12x4_b12x4r12x4_2plane_420_unorm_3pack16

Checks the rule for a 12-bit, two-plane 4:2:0 format.

### g12x4_b12x4r12x4_2plane_422_unorm_3pack16

Checks the rule for a 12-bit, two-plane 4:2:2 format.

### g12x4_b12x4r12x4_2plane_444_unorm_3pack16

Checks the rule for a 12-bit, two-plane 4:4:4 format.

### g16_b16_r16_3plane_420_unorm

Checks the rule for a 16-bit, three-plane 4:2:0 format.

### g16_b16_r16_3plane_422_unorm

Checks the rule for a 16-bit, three-plane 4:2:2 format.

### g16_b16_r16_3plane_444_unorm

Checks the rule for a 16-bit, three-plane 4:4:4 format.

### g16_b16r16_2plane_420_unorm

Checks the rule for a 16-bit, two-plane 4:2:0 format.

### g16_b16r16_2plane_422_unorm

Checks the rule for a 16-bit, two-plane 4:2:2 format.

### g16_b16r16_2plane_444_unorm

Checks the rule for a 16-bit, two-plane 4:4:4 format.

### g8_b8_r8_3plane_420_unorm

Checks the rule for an 8-bit, three-plane 4:2:0 format.

### g8_b8_r8_3plane_422_unorm

Checks the rule for an 8-bit, three-plane 4:2:2 format.

### g8_b8_r8_3plane_444_unorm

Checks the rule for an 8-bit, three-plane 4:4:4 format.

### g8_b8r8_2plane_420_unorm

Checks the rule for an 8-bit, two-plane 4:2:0 format.

### g8_b8r8_2plane_422_unorm

Checks the rule for an 8-bit, two-plane 4:2:2 format.

### g8_b8r8_2plane_444_unorm

Checks the rule for an 8-bit, two-plane 4:4:4 format.

## Shader Analysis

This test has no shader code. It tests host-side image creation, per-plane memory binding, subresource layout queries, and the returned offsets. The absence of shader code is consistent with the implementation in [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93-L152).

## Runtime Execution and Result Checking

- `checkSupport()` requires `VK_KHR_sampler_ycbcr_conversion` and checks that the selected format's linear-tiling features include `VK_FORMAT_FEATURE_DISJOINT_BIT`. Unsupported formats are skipped before the test body runs.
- `createImage()` creates an 8x8, one-mip-level, single-sample, 2D image with `VK_IMAGE_CREATE_DISJOINT_BIT`, `VK_IMAGE_TILING_LINEAR`, `VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, and `VK_IMAGE_LAYOUT_PREINITIALIZED`.
- The test obtains the number of planes with `getPlaneCount()`. For each plane, it queries plane-specific memory requirements, doubles the requirement size, and allocates host-visible memory.
- The binding offset is `deAlign64(reqs.size, reqs.alignment)`, which is a nonzero aligned offset. The test attaches `VkBindImagePlaneMemoryInfo` to each `VkBindImageMemoryInfo` and binds all planes with `vkBindImageMemory2`.
- The test queries `vkGetImageSubresourceLayout` for plane aspects in order. It checks `subresourceLayout.offset` for every plane, and returns failure if any value differs from zero. Otherwise it returns `Pass`.

The spec describes disjoint images as images whose planes are separately bound to memory in [Image Creation Flags](../../../../vulkan-docs/src/chapters/resources.adoc#resources-image-create-flags). The image subresource query returns the implementation's layout information for the selected plane.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any of the 24 format values | The returned `VkSubresourceLayout::offset` for at least one plane is not zero after separate plane binding. |

### Cause Analysis

#### Nonzero plane-relative subresource offset

**Possible failure symptoms:** The test reports `Failed, subresource layout offset != 0` for the selected format after `vkGetImageSubresourceLayout` returns a nonzero `offset` for one of the format's planes.

**Possible implementation causes:** The implementation's reported layout for a disjoint linear image may not use the separately bound plane memory as the base for the queried plane, or the plane binding and subresource-layout calculation may disagree. This interpretation follows the test's source comment and the Vulkan rule that `VK_IMAGE_CREATE_DISJOINT_BIT` separately binds each plane. Further implementation-level diagnosis requires investigation of the failing format and plane.

#### Unsupported format or required functionality

**Possible failure symptoms:** The case is reported as unsupported before image creation because `VK_KHR_sampler_ycbcr_conversion` is unavailable or the format lacks `VK_FORMAT_FEATURE_DISJOINT_BIT` for linear tiling.

**Possible implementation causes:** The device does not expose the required extension or does not advertise the required format feature. This is a support decision, not a nonzero-offset result.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` skips a format when `VK_KHR_sampler_ycbcr_conversion` is unavailable.
- `checkSupport()` skips a format when its linear-tiling format features do not include `VK_FORMAT_FEATURE_DISJOINT_BIT`.
- The test only creates formats present in `formats::disjointPlanesFormats`, so formats outside that source list are not registered here.

### Design-based pruning

- The test uses one fixed 8x8, one-mip-level, single-sample 2D image. It does not generate other extents, mip levels, array layers, sample counts, or tiling modes because those dimensions are outside this test family's offset check.
- Each registered format is tested once. The format matrix covers the listed bit widths, two- and three-plane arrangements, and 4:2:0, 4:2:2, and 4:4:4 sampling forms without adding duplicate cases.

## Key Takeaways

- The binding offset and the queried plane-relative layout offset are different quantities. The test deliberately binds each plane at a nonzero aligned allocation offset and expects the queried `offset` to be zero.
- The check applies to every plane exposed by each registered multi-planar format, including both two-plane and three-plane formats.
- A nonzero result identifies a mismatch in the implementation's handling or reporting of a separately bound plane layout. An unsupported format is pruned by `checkSupport()` instead.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `checkSupport()` | [`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L61-L69) | Defines the required extension and linear disjoint-format feature gate. |
| `createImage()` | [`createImage()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L71-L90) | Defines the fixed image type, extent, tiling, flags, usage, and initial layout. |
| `imageOffsetTest()` setup | [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93-L134) | Allocates host-visible memory and binds each plane at an aligned nonzero offset. |
| `imageOffsetTest()` result check | [`imageOffsetTest()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L136-L152) | Queries each plane layout and applies the zero-offset pass condition. |
| `initYcbcrImageOffsetTests()` | [`initYcbcrImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154-L162) | Registers the exact format test case names. |
| `createImageOffsetTests()` | [`createImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167-L170) | Creates the `subresource_offset` test family. |
| Disjoint image semantics | [Image Creation Flags](../../../../vulkan-docs/src/chapters/resources.adoc#resources-image-create-flags) | Defines separate plane memory binding for `VK_IMAGE_CREATE_DISJOINT_BIT`. |
