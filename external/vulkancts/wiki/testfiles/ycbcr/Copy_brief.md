# Understanding Brief: YCbCr image copy tests

## One-Sentence Test Purpose

This test checks whether Vulkan preserves the selected bytes when compatible image regions are copied between ordinary and multi-planar YCbCr images, including disjoint images, both tilings, buffer-mediated copies, and large dimensions.

## Background Knowledge

### Multi-planar images and compatible planes

A multi-planar image stores its components in separate planes. A copy involving such an image selects one plane in each `VkImageSubresourceLayers`; it does not copy the whole YCbCr image as one color aspect. Vulkan defines compatibility for the selected plane by its compatible single-plane format, so the source and destination image formats can differ while the selected plane formats remain copy-compatible. See the Vulkan rules for [copying multi-planar images](../../../../vulkan-docs/src/chapters/copies.adoc#L327-L344) and [compatible planes](../../../../vulkan-docs/src/chapters/formats.adoc#L3410-L3446).

Why it matters here:
- `genCopies()` pairs compatible source and destination planes and chooses offsets and extents in plane blocks.
- The reference image copies bytes into the destination plane using the same block interpretation as the command region.

### Image tiling and disjoint binding

Linear tiling permits the test to access image memory directly through a host-visible allocation. Optimal tiling uses staging buffers and transfer commands. A disjoint multi-planar image has separate memory bindings for its planes, while a non-disjoint image uses the image's ordinary allocation model. These choices change resource setup and readback, but not the byte oracle.

Why it matters here:
- The default and dimension test families vary source and destination tiling and disjoint state independently.
- Support checks query transfer features and, for disjoint cases, plane-compatible format support.

## One Concrete Example

Consider a generated `copy` case with a multi-planar source and destination. `genCopies()` may select source plane 1 and destination plane 0, calculate each plane's block extent, then choose a block-aligned source offset, destination offset, and shared copy size. The recorded `VkImageCopy` contains a plane aspect for each side and the selected offsets and extent. The simplified sequence is:

```text
source plane bytes at srcOffset
        │ vkCmdCopyImage or image-to-buffer plus buffer-to-image
        ▼
destination plane bytes at dstOffset
```

This is a conceptual example of one generated region, not a fixed registered test case. The default path generates 10 such regions. The `single_plane_copy` cases instead use fixed whole-image extents and no intermediate buffer.

## End-to-End Test Flow

```text
[host] choose source and destination formats, tilings, disjoint states, and copy mode
[host] create MultiPlaneImageData for source, destination, and the eventual result
[host] generate non-NaN source and destination bytes with a configuration-derived seed
[host] create and bind the source and destination images
[host] upload optimal-tiled images through staging resources or write linear-tiled image memory
[host] generate 10 plane copy regions, or use the fixed extent for single-plane cases
[host] record direct image copies, or image-to-buffer, a buffer barrier, and buffer-to-image copies
[host] insert transfer barriers so each destination write can precede the next transfer access
[host] submit the command buffer and wait for completion
[host] download an optimal-tiled result through staging resources or read linear-tiled image memory
[host] construct a reference by applying each region's block copy to the initial destination bytes
[host] compare result and reference bytes, masking defined don't-care low bits for selected packed formats
[host] return pass only when no compared byte differs
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test does not generate or load a shader. Its generated artifacts are the `TestConfig`, the `MultiPlaneImageData` byte arrays, and the `VkImageCopy` regions. The default and dimension families derive a deterministic seed from the image configurations; the default family generates 10 random regions. The fixed `single_plane_copy` cases provide their copy extents directly.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source `VkImage` | yes | yes | read by transfer | no | Supplies the bytes for each selected plane region. |
| Destination `VkImage` | yes | yes | written by transfer | yes | Receives copied bytes and provides the comparison result. |
| Per-copy transfer buffer | yes, only for `intermediateBuffer` cases | yes | written then read by transfer | no | Carries one source region between the two image commands. |
| `MultiPlaneImageData` source and destination arrays | yes | no | no | no | Hold the initial bytes and provide the software reference input. |
| `MultiPlaneImageData` result | yes | no | no | yes | Receives the downloaded or directly read destination bytes. |
| Disjoint plane allocations | yes, when disjoint is selected | yes | read or written through the image planes | indirectly | Exercise separate plane memory binding and readback. |

## What Is Checked

- The test starts the software reference as a copy of the initial destination data.
- For each `VkImageCopy`, it finds the source and destination plane, computes the plane block offsets and row pitches, and copies the corresponding rows from source data into the reference.
- It compares every byte in every result plane with the reference. `areLsb6BitsDontCare()` and `areLsb4BitsDontCare()` permit the low 6 or low 4 bits in the first byte of affected packed formats to differ.
- The result is a pass when the comparison finds no mismatch. The test logs at most 30 mismatches before returning a failure status.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `copy`, `single_plane_copy`, `copy_dimensions`

The three test families select different copy behavior. `copy` exercises generated per-plane regions, optional intermediate buffers, and independent tiling and disjoint combinations. `single_plane_copy` uses two explicit format-direction cases with fixed extents. `copy_dimensions` repeats the generated compatible-copy path at wide and tall image sizes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `copy` | Per-plane format compatibility or block addressing, direct or buffer-mediated copy commands, tiling or disjoint image setup, transfer ordering, or byte-reference construction. |
| `single_plane_copy` | The fixed single-plane format-direction path, its copy extent, tiling combination, transfer commands, or byte comparison. |
| `copy_dimensions` | Large-width or large-height image extent handling, plane block addressing at the selected dimensions, format compatibility, tiling or disjoint setup, or the shared copy and comparison path. |

## Important Variations and Special Cases

- The default YCbCr image size is `24x16`; a non-YCbCr image uses `23x17`. This keeps the ordinary matrix distinct from the dimension-stress sizes.
- The default `copy` family tests direct `vkCmdCopyImage` and buffer-mediated `vkCmdCopyImageToBuffer` followed by `vkCmdCopyBufferToImage`. The dimension family uses direct image copies only.
- The fixed `single_plane_copy` direction `r8g8b8a8_to_g8b8g8r8_422` uses a `32x64` copy extent, while the reverse direction uses `64x64`.
- `copy_dimensions` uses `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, `VK_FORMAT_G10X6_B10X6_R10X6_3PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G12X4_B12X4_R12X4_3PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G16_B16_R16_3PLANE_420_UNORM`, and `VK_FORMAT_R8G8B8A8_UNORM` over the registered wide and tall dimensions.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test configuration types | [`ImageConfig` and `TestConfig`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L64-L95) | Defines format, tiling, disjoint state, image size, intermediate-buffer mode, and fixed extent. |
| Generated copy regions | [`genCopies()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L346-L414) | Chooses compatible plane pairs and block-aligned regions. |
| Runtime and byte oracle | [`imageCopyTest()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L477-L755) | Creates data and images, records copies, reads back the result, builds the reference, and compares bytes. |
| Copy compatibility | [`isCopyCompatible()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L758-L805) | Filters format pairs according to YCbCr plane compatibility. |
| Default registration | [`initYcbcrDefaultCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L807-L868) | Defines the format, tiling, disjoint, and buffer matrix. |
| Fixed single-plane registration | [`initYcbcrSinglePlanarCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L870-L921) | Defines the two format directions and fixed copy extents. |
| Dimension registration | [`initYcbcrDimensionsCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L923-L1019) | Defines the five formats and sixteen wide or tall dimensions. |
| Plane storage and staging | [`MultiPlaneImageData`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.hpp#L58-L102) and [`uploadImage()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L420-L555) | Shows how plane byte arrays and staging transfers represent image data. |
| Vulkan copy semantics | [Image copy chapter](../../../../vulkan-docs/src/chapters/copies.adoc#L293-L344) | Grounds the per-plane and block-copy rules. |

## Questions / Risk Points for User Audit

- Does the test-family axis correctly capture the distinct copy mechanisms, rather than treating tiling or disjoint state as the primary behavior?
- Is the difference between direct image copies and intermediate-buffer copies clear?
- Does the resource table distinguish software plane arrays from Vulkan-bound resources?
- Is the low-bit masking rule described narrowly enough to avoid implying that all packed formats permit ignored bits?
- Are the wide and tall dimension cases explained without reproducing the entire mustpass matrix?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's `## Background Knowledge` focused on per-plane copy semantics, compatible plane formats, and the linear versus optimal and disjoint resource distinction.
- Use the generated-region example to explain why offsets and extents are calculated in plane blocks, but label it as conceptual rather than a fixed leaf.
- Carry the `## Behavior Parameter Identification` conclusion into `## Behavior Parameters`, with one subsection for each test family.
- Copy the `### Failure Cause Mapping` table directly into the final page's `## Failure Meaning` section.
- Write fresh cause analysis from the source's actual byte comparison and transfer sequence. Do not infer a specific driver or hardware bug location without evidence.
- State in `## Shader Analysis` that no shader participates in this implementation. The page does not need a shader walkthrough because the tested behavior is entirely transfer and host comparison logic.
