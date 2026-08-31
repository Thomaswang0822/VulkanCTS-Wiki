## Overview

**Core question:** Do compatible Vulkan image copies preserve every defined byte across YCbCr planes, tilings, disjoint bindings, copy paths, and large image dimensions?

- [`vktYCbCrCopyTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp) implements the `copy`, `single_plane_copy`, and `copy_dimensions` test families.
- The implementation creates source and destination `MultiPlaneImageData`, fills both with deterministic non-NaN bytes, copies selected image regions directly or through an intermediate buffer, reads the destination back, and compares it with a software reference.
- The default family generates compatible source and destination format pairs, random plane copy regions, both image tilings, both disjoint states, and direct or buffer-mediated copies. The other families add two fixed single-plane format directions and sixteen large wide or tall dimensions.
- This page explains the registered hierarchy, the behavioral choices, the transfer sequence, the byte reference, and what a mismatch can indicate.

## Background Knowledge

- **Per-plane image copies.** A multi-planar image must be copied one plane at a time. Each `VkImageCopy` names one plane aspect on the source and destination. Vulkan evaluates compatibility using the compatible format of each selected plane, rather than the multi-planar format as a whole. See the Vulkan [image copy rules](../../../../vulkan-docs/src/chapters/copies.adoc#L327-L344).
- **Block addressing.** Plane dimensions and element sizes can differ from the full image dimensions. The test therefore chooses offsets and extents in compatible-format blocks, then converts them to texel coordinates for `VkImageCopy`.
- **Linear, optimal, and disjoint images.** Linear images use host-visible image memory for direct access. Optimal images use staging resources for upload and download. A disjoint multi-planar image has separate plane memory bindings. These choices change setup and readback, but the comparison still uses the same per-plane byte representation.

## Registration Hierarchy

```text
ycbcr.copy
├── a1b5g5r5_unorm_pack16
├── a1r5g5b5_unorm_pack16
├── a2b10g10r10_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a4b4g4r4_unorm_pack16
├── a4r4g4b4_unorm_pack16
├── a8b8g8r8_unorm_pack32
├── b10g11r11_ufloat_pack32
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── b16g16r16g16_422_unorm
├── b4g4r4a4_unorm_pack16
├── b5g5r5a1_unorm_pack16
├── b5g6r5_unorm_pack16
├── b8g8r8a8_unorm
├── b8g8r8g8_422_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16r16_2plane_444_unorm
├── g16b16g16r16_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8r8_2plane_444_unorm
├── g8b8g8r8_422_unorm
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
├── r12x4g12x4b12x4a12x4_unorm_4pack16
├── r16_unorm
├── r16g16_unorm
├── r4g4_unorm_pack8
├── r4g4b4a4_unorm_pack16
├── r5g5b5a1_unorm_pack16
├── r5g6b5_unorm_pack16
├── r8_unorm
├── r8g8_unorm
└── r8g8b8a8_unorm

ycbcr.single_plane_copy
├── linear
└── optimal

ycbcr.copy_dimensions
├── src16384x4_dst16384x4
├── src16384x6_dst16384x6
├── src32768x4_dst32768x4
├── src32768x6_dst32768x6
├── src4096x4_dst4096x4
├── src4096x6_dst4096x6
├── src4x16384_dst4x16384
├── src4x32768_dst4x32768
├── src4x4096_dst4x4096
├── src4x8192_dst4x8192
├── src6x16384_dst6x16384
├── src6x32768_dst6x32768
├── src6x4096_dst6x4096
├── src6x8192_dst6x8192
├── src8192x4_dst8192x4
└── src8192x6_dst8192x6
```

The three roots are created by [`createCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023-L1026), [`createSinglePlanarCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1028-L1031), and [`createDimensionsCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1033-L1036). Their direct children come from [`initYcbcrDefaultCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L807-L868), [`initYcbcrSinglePlanarCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L870-L921), and [`initYcbcrDimensionsCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L923-L1019). The default inventory records these roots in [`ycbcr.txt`](../../../mustpass/main/vk-default/ycbcr.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `copy`, `single_plane_copy`, `copy_dimensions` | Selects generated regions, fixed single-plane cases, or large-dimension cases. | [Factory functions](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023-L1036) |
| Source and destination format | `formats::basicUnsignedFloatFormats` for `copy`; five explicit formats for `copy_dimensions`; two fixed directions for `single_plane_copy` | Selects plane count, compatible plane formats, block size, image data layout, and the format pair accepted by `isCopyCompatible()`. | [Default loop](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L816-L829), [dimension formats](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L927-L938), [single-plane table](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L880-L901) |
| Image tiling | `linear`, `optimal` for source and destination | Selects direct host-visible image-memory access or staging-buffer upload and download. | [Tiling arrays](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L807-L814), [runtime setup](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L514-L548) |
| Disjoint state | `non-disjoint`, `disjoint` for source and destination in `copy` and `copy_dimensions` | Selects the image create flag and plane-memory binding model. | [Default matrix](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L833-L858), [dimension matrix](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L985-L1006) |
| Copy path | Direct image copy; intermediate buffer in `copy` | Selects `vkCmdCopyImage`, or `vkCmdCopyImageToBuffer` followed by `vkCmdCopyBufferToImage`. | [Copy commands](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L587-L631) |
| Generated region count | `10` for cases without a fixed extent | Selects how many randomly chosen plane regions the default and dimension cases apply. | [`imageCopyTest()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L489-L502) |
| Ordinary default image size | `24x16` for YCbCr formats; `23x17` otherwise | Supplies the source and destination image dimensions for `copy`. | [Default sizes](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L816-L825) |
| Single-plane format direction and extent | `r8g8b8a8_to_g8b8g8r8_422`, extent `32x64`; `g8b8g8r8_422_to_r8g8b8a8`, extent `64x64` | Checks two explicit conversions between a single-plane RGBA format and a 4:2:2 format. | [Single-plane configurations](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L880-L915) |
| Dimension stress size | `4096x4`, `8192x4`, `16384x4`, `32768x4`, `4096x6`, `8192x6`, `16384x6`, `32768x6`, and the corresponding `4x...` and `6x...` sizes | Tests wide and tall images with power-of-two and non-power-of-two small dimensions. | [Dimension array](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L940-L951) |

The primary behavioral axis is **test family**. The family changes the copy workload and its intended stress point. Format, tiling, disjoint state, copy path, and image size extend coverage around that behavior.

## Behavior Parameters

### `copy` - Generated per-plane copies

`copy` keeps format pairs when at least one format is YCbCr and `isCopyCompatible()` finds a compatible source and destination format or plane. It varies source and destination tiling, disjoint state, and intermediate-buffer use independently. Without a fixed extent, `genCopies()` creates 10 regions by choosing compatible plane pairs and block-aligned offsets.

### `single_plane_copy` - Fixed format directions

`single_plane_copy` uses the explicit `R8G8B8A8_UNORM` to `G8B8G8R8_422_UNORM` direction and its reverse. Both images are `64x64`, and the copy extents are `32x64` in the first direction and `64x64` in the reverse. The family varies source and destination tiling but keeps images non-disjoint and uses direct image copies.

### `copy_dimensions` - Large image dimensions

`copy_dimensions` uses four 4:2:0 three-plane YCbCr formats at 8, 10, 12, and 16 bits plus `R8G8B8A8_UNORM`. It applies the generated compatible-plane copy path to sixteen wide or tall dimensions. It varies source and destination tiling and disjoint state, without an intermediate buffer.

## Shader Analysis

This implementation has no shader. `imageCopyTest()` obtains its result from transfer commands, transfer-stage barriers, host-visible memory operations, and byte comparison. No shader walkthrough is applicable to the tested behavior.

## Runtime Execution and Result Checking

- `imageCopyTest()` creates source, destination, and result `MultiPlaneImageData` objects. Each plane owns a byte array sized by the planar format description and the image size.
- A deterministic seed comes from the source and destination image configurations. The test fills source and destination data with random values while avoiding NaNs in the format selected by `chooseFloatFormat()`.
- The test creates 2D source and destination images with transfer source and transfer destination usage. Linear images start in `VK_IMAGE_LAYOUT_PREINITIALIZED`; optimal images start in `VK_IMAGE_LAYOUT_UNDEFINED`. Disjoint images use `VK_IMAGE_CREATE_DISJOINT_BIT`.
- For an optimal-tiled image, `uploadImage()` moves the plane data from staging buffers into the image. For a linear-tiled image, `fillImageMemory()` writes the bound image allocations. The source and destination images reach transfer source and transfer destination layouts.
- In the default family, `genCopies()` first lists source and destination plane pairs whose compatible formats can copy. For each of 10 regions, it selects one pair, calculates the plane block extents, chooses a common number of blocks for the copy, and emits a `VkImageCopy` with one plane aspect on each side. Fixed-extent cases use the supplied `VkExtent2D` instead.
- The direct path records `vkCmdCopyImage` for each region. The intermediate-buffer path records `vkCmdCopyImageToBuffer`, a transfer-stage `VkBufferMemoryBarrier`, and `vkCmdCopyBufferToImage`. After each region, an image barrier changes destination access from transfer write to the transfer read and write accesses needed by the next operation.
- The command buffer is submitted to the universal queue and the test waits for completion. The result comes back through `downloadImage()` for optimal tiling or `readImageMemory()` for linear tiling.
- The host starts the reference as a copy of the original destination data. It applies every region to the reference by computing source and destination plane block offsets, row pitches, and copied row sizes. It then compares every byte in every result plane, logs at most 30 mismatches, and returns `Pass` only when no mismatch remains.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `copy` | Per-plane format compatibility or block addressing, direct or buffer-mediated copy commands, tiling or disjoint image setup, transfer ordering, or byte-reference construction. |
| `single_plane_copy` | The fixed single-plane format-direction path, its copy extent, tiling combination, transfer commands, or byte comparison. |
| `copy_dimensions` | Large-width or large-height image extent handling, plane block addressing at the selected dimensions, format compatibility, tiling or disjoint setup, or the shared copy and comparison path. |

### Cause Analysis

#### Plane selection and block addressing

**Possible failure symptoms:** Mismatches cluster in one plane, one format pair, or regions whose offsets or extents touch subsampled plane boundaries.

**Possible implementation causes:** Vulkan copies multi-planar images one plane at a time and interprets compatibility through the selected plane's compatible format. The test calculates each plane's block extent and uses a common block count for the generated region. A mismatch can therefore result from incorrect plane selection, block scaling, offset handling, or row-pitch interpretation in the copy operation or in the software reference. The source does not identify which operation introduced a particular differing byte.

#### Transfer path, layout, or memory visibility

**Possible failure symptoms:** Many formats or regions return stale, unchanged, or otherwise incorrect destination bytes. Failures may be limited to direct copies, buffer-mediated copies, one tiling, or disjoint images.

**Possible implementation causes:** The source uploads or writes both images before the copy, uses transfer layouts, inserts a buffer barrier around the intermediate path, and orders later destination accesses with an image barrier. Optimal-tiled data also depends on staging transfers, while linear data depends on mapped image allocations. A failure in command execution, layout use, transfer ordering, plane binding, staging operations, or host-visible memory access can produce the observed mismatch. These possibilities are derived from the operations the test performs, not from a presumed bug location.

#### Format representation and packed low bits

**Possible failure symptoms:** Failures cluster under packed formats or appear only in the first byte of a packed element.

**Possible implementation causes:** The reference uses the compatible plane format's block size and copies raw bytes. The final comparison masks low 6 or low 4 bits in the first byte only when `areLsb6BitsDontCare()` or `areLsb4BitsDontCare()` says the source and destination formats permit those bits to differ. A mismatch in the remaining bits, or in an unmasked byte, indicates a difference in the defined representation or in the corresponding transfer and reference calculations. The source does not classify that difference further.

#### Large-dimension addressing

**Possible failure symptoms:** Only `copy_dimensions` cases fail, especially for wide or tall images near the largest registered size.

**Possible implementation causes:** These cases use the same transfer and comparison sequence with large widths or heights. The failure may involve image extent support, plane extent calculation, block row pitch, allocation size, or copy-region addressing. The source's support check can skip dimensions above `maxImageDimension2D`; it does not distinguish the remaining implementation causes after execution.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` skips a case when either image dimension exceeds `maxImageDimension2D`.
- The test requires `VK_KHR_sampler_ycbcr_conversion` and the `samplerYcbcrConversion` feature.
- `checkFormatSupport()` requires image-format support for the selected format and transfer usage. A disjoint case also requires support for each compatible plane format and `VK_FORMAT_FEATURE_DISJOINT_BIT`.
- The format pair loops skip pairs where neither side is YCbCr and pairs for which `isCopyCompatible()` finds no compatible format or plane. Unsupported cases raise `NotSupportedError` before the copy runs.

### Design-based pruning

- The default family fixes YCbCr image sizes at `24x16` and non-YCbCr image sizes at `23x17`, while `copy_dimensions` supplies its own sixteen wide or tall sizes.
- `single_plane_copy` intentionally fixes two format directions and two extents instead of using the generated format matrix.
- `copy_dimensions` fixes its five formats and uses direct image copies. It varies tiling and disjoint state, but not intermediate-buffer use.
- The default family generates 10 regions per case rather than enumerating every plane pair, offset, and block extent.

## Key Takeaways

- The test checks raw per-plane transfer results, not reconstructed YCbCr color values.
- Vulkan treats a multi-planar image copy as a set of one-plane operations. The compatible format of each selected plane controls block size and compatibility.
- The same software reference begins with the untouched destination data, applies every requested region, and compares the resulting plane bytes with the downloaded image.
- A pass covers the selected family, format pair, tiling, disjoint state, copy path, and image dimensions. It does not prove unsupported combinations that `checkSupport()` removed.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Configuration structures | [`ImageConfig` and `TestConfig`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L64-L95) | Defines the image and copy choices carried into each case. |
| Support checks | [`checkFormatSupport()` and `checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L97-L195) | Defines image limits, extension and feature requirements, transfer support, compatible-plane support, and disjoint support. |
| Region generator | [`genCopies()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L346-L414) | Selects compatible plane pairs and block-aligned copy regions. |
| Compatibility filter | [`isCopyCompatible()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L758-L805) | Filters source and destination format pairs. |
| Runtime and oracle | [`imageCopyTest()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L477-L755) | Generates data, creates images and buffers, records copies and barriers, reads back results, builds the reference, and compares bytes. |
| Default family registration | [`initYcbcrDefaultCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L807-L868) | Defines the default format, tiling, disjoint, and buffer matrix. |
| Single-plane registration | [`initYcbcrSinglePlanarCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L870-L921) | Defines the two explicit format directions and extents. |
| Dimension registration | [`initYcbcrDimensionsCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L923-L1019) | Defines the five formats and sixteen large dimensions. |
| Plane byte storage | [`MultiPlaneImageData`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.hpp#L58-L102) | Defines the per-plane host-side data representation. |
| Staging upload and readback | [`uploadImage()` and `downloadImage()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L420-L629) | Shows how optimal-tiled image data moves through per-plane staging buffers. |
| Vulkan copy semantics | [Image copy chapter](../../../../vulkan-docs/src/chapters/copies.adoc#L293-L344) | Defines per-plane copying, compatible-plane formats, and block alignment. |
| Registered default paths | [`ycbcr.txt`](../../../mustpass/main/vk-default/ycbcr.txt) | Records the default mustpass hierarchy for the category. |
