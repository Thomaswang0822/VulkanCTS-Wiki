# [vktApiUseAfterCopyTests.cpp](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1)

## Overview

[`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1) is an implementation-heavy Level-3 file that documents the `use_after_copy` subtree under the Vulkan CTS `api.copy_and_blit.core` registration root. It verifies that copied destination images remain usable afterward, either through sampled color reads in a later graphics pass or through depth/stencil attachment use that affects subsequent rendering. The generated coverage spans multiple destination formats, transfer layouts, queue types, copy coverage modes, image/view configurations, copy mechanisms, tiling modes, and selected multisample variants.

## Role of File

- **Role:** implementation-heavy test file.
- **Primary source:** [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1).
- **Registration context inspected:**
  - [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L108) for placement under the top-level `api` category.
  - [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232-L239) for placement under `copy_and_blit.core`.
  - [`vktApiCopyMemoryIndirectTests.cpp`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338) for the sibling indirect-registration call that reuses the same implementation entry point.

## Registration Hierarchy

```text
api.copy_and_blit.core.use_after_copy
├── D16_UNORM
├── D16_UNORM_S8_UINT
├── D24_UNORM_S8_UINT
├── D32_SFLOAT
├── D32_SFLOAT_S8_UINT
├── R5G6B5_UNORM_PACK16
├── R8G8B8A8_UNORM
├── R8G8B8A8_SRGB
├── B8G8R8A8_UNORM
├── B8G8R8A8_SRGB
├── A8B8G8R8_UNORM_PACK32
├── A8B8G8R8_SRGB_PACK32
├── A2R10G10B10_UNORM_PACK32
├── A2B10G10R10_UNORM_PACK32
├── R16G16B16A16_UNORM
├── R16G16B16A16_SFLOAT
├── R32_SFLOAT
├── R32G32_SFLOAT
├── R32G32B32_SFLOAT
└── R32G32B32A32_SFLOAT
```

The Level-3 root documented here is the concrete subgroup created by [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710-L1713). Within that root, the implementation registers one direct child per format by iterating the explicit `testFormats` table in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1715-L1741). Each format child then owns deeper descendants such as `transfer_dst_optimal` and `general`, but those descendants are intentionally described in prose rather than expanded in the parseable tree because the normalizer contract requires exactly one level of direct children.

## Test Families

### D16_UNORM — Depth-only 16-bit normalized destination format

Covers the `D16_UNORM` direct child registered from the explicit format list in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1717). As a depth-only format, these cases follow the post-copy depth-attachment validation path: [`AfterUsageParams::getImageCreateInfo()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L59-L115) adds depth/stencil attachment usage, and [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1422-L1692) later binds the copied image as the depth attachment whose preserved values control point visibility.

Observed deeper descendants under this format root include the transfer-layout groups `transfer_dst_optimal` and `general`, both created in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757-L1761), plus generated leaf cases whose names encode extent, queue choice, partial-region mode, and selected image/view options in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1903-L1933).

### D16_UNORM_S8_UINT — Combined depth/stencil 16-bit depth plus 8-bit stencil format

Covers the `D16_UNORM_S8_UINT` direct child registered in the same format loop at [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1718). These cases use the depth/stencil post-copy verification route described above rather than sampled color reads. The expected output is synthesized by checking whether each drawn point should pass the depth test against copied destination values in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1642-L1655).

Like the other format branches, this subgroup contains deeper `transfer_dst_optimal` and `general` children from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757-L1761).

### D24_UNORM_S8_UINT — Combined depth/stencil 24-bit depth plus 8-bit stencil format

Covers the `D24_UNORM_S8_UINT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1719). The implementation treats this as a depth/stencil attachment-use case after the copy. Verification remains indirect through the rendered color target rather than by reading the destination depth image directly, with threshold-free comparison for depth/stencil results in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1688-L1691).

### D32_SFLOAT — Depth-only 32-bit float destination format

Covers the `D32_SFLOAT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1720). These cases exercise floating-point depth copies that must remain valid for later depth testing. CPU reference construction for the expected rendered output is handled in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1620-L1655).

### D32_SFLOAT_S8_UINT — Combined 32-bit float depth plus 8-bit stencil format

Covers the `D32_SFLOAT_S8_UINT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1721). Functionally, this branch belongs to the same post-copy depth/stencil-attachment family as the other depth/stencil formats, including layout variants rooted at `transfer_dst_optimal` and `general`.

### R5G6B5_UNORM_PACK16 — Packed 16-bit UNORM color format

Covers the `R5G6B5_UNORM_PACK16` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1722). For color formats, [`AfterUsageParams::getImageCreateInfo()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L59-L115) gives the copied image sampled usage, [`AfterUsageCase::initPrograms()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L450-L503) generates fragment shaders that fetch the copied texels, and [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1375-L1692) renders and compares the resulting framebuffer against a CPU-generated reference.

### R8G8B8A8_UNORM — 8-bit UNORM RGBA color format

Covers the `R8G8B8A8_UNORM` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1723). This branch participates in the sampled-color post-copy usage family, including optional `_color_att_flag` expansions that add color-attachment usage on the destination image when the layout is `transfer_dst_optimal` and the view is not 3D, as generated in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1836-L1847).

### R8G8B8A8_SRGB — 8-bit sRGB RGBA color format

Covers the `R8G8B8A8_SRGB` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1724). This branch follows the same sampled-texture verification flow as the other color formats, with explicit sRGB handling called out in the expected-color synthesis code inside [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1658-L1678).

### B8G8R8A8_UNORM — 8-bit UNORM BGRA color format

Covers the `B8G8R8A8_UNORM` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1725). It belongs to the same post-copy sampled-rendering family and participates in the deeper layout, queue, partial-region, tiling, and copy-mechanism expansions generated by the nested loops in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757-L1933).

### B8G8R8A8_SRGB — 8-bit sRGB BGRA color format

Covers the `B8G8R8A8_SRGB` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1726). This branch verifies that post-copy sampled use also works for BGRA sRGB formats, again compared with format-aware thresholds through [`getColorFormatThreshold()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L504-L537).

### A8B8G8R8_UNORM_PACK32 — Packed 32-bit UNORM ABGR color format

Covers the `A8B8G8R8_UNORM_PACK32` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1727). The same color verification path applies: render using the copied image as a sampled texture, copy the result back to a host-visible buffer, then compare layer-by-layer using [`tcu::floatThresholdCompare()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1691).

### A8B8G8R8_SRGB_PACK32 — Packed 32-bit sRGB ABGR color format

Covers the `A8B8G8R8_SRGB_PACK32` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1728). This is the sRGB counterpart of the previous branch and follows the same sampled-color pipeline and thresholded comparison model.

### A2R10G10B10_UNORM_PACK32 — Packed 10:10:10:2 UNORM ARGB color format

Covers the `A2R10G10B10_UNORM_PACK32` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1729). It contributes packed-color coverage to the sampled-after-copy family while inheriting the same deeper layout and queue expansions.

### A2B10G10R10_UNORM_PACK32 — Packed 10:10:10:2 UNORM ABGR color format

Covers the `A2B10G10R10_UNORM_PACK32` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1730). As with the preceding packed-color variant, the branch validates later sampled use after the copy rather than direct copy correctness alone.

### R16G16B16A16_UNORM — 16-bit UNORM RGBA color format

Covers the `R16G16B16A16_UNORM` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1731). This branch extends the sampled-color family to higher-precision normalized color storage. Threshold selection still flows through the format-aware helper path in [`getColorFormatThreshold()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L504-L537).

### R16G16B16A16_SFLOAT — 16-bit float RGBA color format

Covers the `R16G16B16A16_SFLOAT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1732). The copied image is later sampled in a graphics pass, and tolerance derives from per-channel mantissa/bit-width information through [`bitWidthToThreshold()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L493-L502) and [`getColorFormatThreshold()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L504-L537).

### R32_SFLOAT — 32-bit float single-channel color format

Covers the `R32_SFLOAT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1733). This branch verifies post-copy sampled use for a single-channel floating-point format and participates in the same generated matrix of queue, layout, coverage, and image-configuration dimensions.

### R32G32_SFLOAT — 32-bit float two-channel color format

Covers the `R32G32_SFLOAT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1734). Like the other float color branches, the expected post-render image is synthesized from source texture data and compared with format-aware thresholds in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1658-L1692).

### R32G32B32_SFLOAT — 32-bit float three-channel color format and only observed linear-tiling color format

Covers the `R32G32B32_SFLOAT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1735). This branch is also the only format that receives the extra linear-tiling expansion in the observed generator, because `linearFormats` contains only this format in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1743-L1745).

### R32G32B32A32_SFLOAT — 32-bit float four-channel color format

Covers the `R32G32B32A32_SFLOAT` direct child from [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1736). It is the widest floating-point color branch in the direct-child format table and follows the same sampled-after-copy execution and thresholded comparison flow as the other color formats.

### Deeper generated subgroups shared by all direct children

Every direct format child owns two observed layout subgroups, `transfer_dst_optimal` and `general`, created from the transfer-layout loop in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757-L1761). Beneath those layout groups, generated leaves encode several parameter axes in their names, including queue suffixes (`_cq`, `_tq`), partial-region mode (`_regions`), 3D-image and 3D-view choices (`_3d_img`, `_3d_view`), extra color-attachment usage (`_color_att_flag`), image-to-image copies (`_img2img`), linear tiling (`_linear`), and multisample variants (`_msaa`) in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1903-L1933).

## Parameter Dimensions and Observed Values

| Dimension | Observed values / construction | Evidence |
|----------|--------------------------------|----------|
| Direct child format subgroup | `D16_UNORM`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT`, `D32_SFLOAT_S8_UINT`, `R5G6B5_UNORM_PACK16`, `R8G8B8A8_UNORM`, `R8G8B8A8_SRGB`, `B8G8R8A8_UNORM`, `B8G8R8A8_SRGB`, `A8B8G8R8_UNORM_PACK32`, `A8B8G8R8_SRGB_PACK32`, `A2R10G10B10_UNORM_PACK32`, `A2B10G10R10_UNORM_PACK32`, `R16G16B16A16_UNORM`, `R16G16B16A16_SFLOAT`, `R32_SFLOAT`, `R32G32_SFLOAT`, `R32G32B32_SFLOAT`, `R32G32B32A32_SFLOAT` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1715-L1741) |
| Transfer layout subgroup | `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, `VK_IMAGE_LAYOUT_GENERAL` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757-L1761) |
| Layer count / depth extent | `1` and `2`; used as Z extent in `tcu::IVec3(baseSize, baseSize, layerCount)` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1763-L1764) |
| Queue selection | `Universal`, `ComputeOnly`, `TransferOnly` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1765-L1767) |
| Base extent | `32x32` on universal/compute queues, `64x64` on transfer queues | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1769-L1770) |
| Copy coverage | full copy or generated per-layer partial regions | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1780-L1804) |
| 3D image backing | `false`, `true` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1806-L1814) |
| 3D view | `false`, `true`, only when backing image is 3D | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1819-L1834) |
| Color-attachment usage bit on copied image | `false`, `true`, only for color cases and only with `transfer_dst_optimal` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1836-L1847) |
| Copy source type | buffer-to-image vs image-to-image | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1848-L1859) |
| Tiling | optimal and selected linear-tiling cases | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1849-L1854) |
| Linear-tiling formats | limited to `VK_FORMAT_R32G32B32_SFLOAT` in the inspected generator | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1743-L1745) |
| Sample count | `1` or `4` samples | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1860-L1868) |
| Large-image expansion for color-attachment-flag cases | scaled from base extent to `1024x1024xlayerCount` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1883-L1888) |

### Partial-copy region construction

When `fullCopy` is false, one `VkRect2D` is generated per layer. Each region uses half-size extents divided again on one axis and offsets one axis by a quarter-image amount, with different axis choices per layer in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1782-L1804). This creates asymmetric per-layer regions rather than a single repeated rectangle.

### Generated test-name dimensions

Leaf names begin with `<width>x<height>x<depth>` and then append suffixes that expose selected parameter choices:

- `_cq` for compute queue;
- `_tq` for transfer queue;
- `_regions` for partial copies;
- `_3d_img` for 3D backing image;
- `_3d_view` for 3D view;
- `_color_att_flag` for the extra color-attachment usage bit;
- `_img2img` for image-to-image copy;
- `_linear` for linear tiling;
- `_msaa` for multisample variants.

Evidence: [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1903-L1933).

## Support and Feature Requirements

[`AfterUsageCase::checkSupport()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L253-L444) provides the main runtime support gate. Observed requirements include:

| Requirement | When it applies | Evidence |
|------------|-----------------|----------|
| `VK_KHR_copy_memory_indirect` and `indirectMemoryToImageCopy` feature | indirect-copy cases | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L255-L266) |
| `VK_KHR_maintenance1` | 3D image with 2D-array-compatible view when `extent.z() > 1` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L268-L271) |
| `VK_EXT_image_2d_view_of_3d` features `image2DViewOf3D` and, for color sampling, `sampler2DViewOf3D` | single-slice 3D image viewed as 2D on non-SC builds | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L272-L288) |
| `VK_KHR_maintenance10` plus queue-specific depth-copy format features | classic non-universal depth copies on compute or transfer queues | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L290-L307) |
| `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` | indirect cases | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L309-L319) |
| Transfer-queue granularity compatibility | transfer-only queue with partial regions | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L320-L334) |
| Queue support for indirect-copy commands | indirect cases on chosen queue family | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L335-L343) |
| Format/image support via `vkGetPhysicalDeviceImageFormatProperties` | all cases | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L365-L383) |
| `VK_EXT_shader_viewport_index_layer` | multi-slice cases | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L384-L386) |
| Core geometry shader feature | multi-slice color cases | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L388-L390) |

## Combination-Pruning Rules Observed in Generation Code

The generator removes several combinations before runtime support checks:

- indirect depth/stencil copies only remain on the universal queue, due to the cited VUID comment in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1775-L1778);
- Vulkan SC excludes single-slice `use3DImage` cases because `VK_EXT_image_2d_view_of_3d` is unavailable in the inspected branch at [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1808-L1811);
- depth/stencil cases never use 3D images or 3D views in generated combinations, see [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1814-L1834);
- color cases skip 3D-image + multi-slice + non-3D-view combinations to avoid the cited descriptor-image VUID in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1827-L1833);
- `colorAttFlag` is only kept for color formats, `transfer_dst_optimal` layout, and non-3D views in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1836-L1847);
- image-to-image cases are skipped when `indirect` is true, when `use3DImage` is true, or when `layerCount == 1`, according to [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1855-L1859);
- multisample cases are only kept when `imageToImage` is true in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1860-L1868).

## Verification Methods

### Sampled-color post-copy use

For color formats, the test does not stop at verifying transfer completion. Instead, the copied destination image is sampled in a later graphics pass through shaders created by [`AfterUsageCase::initPrograms()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L450-L503), with descriptor setup and render execution in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1375-L1540).

### Depth/stencil attachment post-copy use

For depth/stencil formats, the copied destination image is rebound as the framebuffer depth/stencil attachment in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1422-L1477). Correctness is judged indirectly by whether later point rendering passes or fails the depth test according to copied values, with reference synthesis in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1642-L1655).

### Reference-image synthesis from the same parameters

The expected framebuffer is synthesized on the CPU after execution in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1620-L1678):

- outside partial-copy regions, expected pixels stay at the clear color in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1631-L1640);
- for depth/stencil cases, expected blue/black pixels are derived from the copied depth value versus the point depth in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1642-L1655);
- for color cases, expected texel values come from the generated source texture data, including explicit sRGB handling notes in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1658-L1678).

### Thresholded image comparison

The result color attachment is copied to a buffer in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1540-L1566), mapped as a TCU image in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1683-L1690), and compared layer-by-layer with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1691).

Threshold selection is format-aware:

- depth/stencil cases use zero threshold in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1688);
- color cases compute thresholds from format bit depth or mantissa width via [`getColorFormatThreshold()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L504-L537) and [`bitWidthToThreshold()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L493-L502).

## Test Principles Observed

- **State validity after copy matters as much as copy correctness.** The copied destination image is transitioned and then consumed through realistic later usage, rather than verified only by direct readback; see queue ownership and layout transitions in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1027-L1115) and later graphics usage in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1477-L1547).
- **Queue-family transfer paths are first-class coverage.** The file explicitly supports universal, compute-only, and transfer-only queues via [`AfterUsageParams::getQueueFamilyIndex()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L181-L251) and semaphored multi-submit execution in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1547-L1566).
- **Partial copies are checked by observing preserved clear values outside copied rectangles.** That principle appears in the CPU reference logic in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1631-L1640).
- **Color and depth/stencil cases use different oracles.** Color cases compare sampled texels; depth/stencil cases compare whether later depth testing admitted geometry, as described in comments and implementation around [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L708-L735).
- **MSAA coverage uses an auxiliary fill path because direct buffer-to-image copy is unavailable.** This principle is documented in comments and implemented in [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L676-L705) and [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1149-L1199).

## Notes and Uncertainties

- This normalization uses the confirmed Level-3 root `api.copy_and_blit.core.use_after_copy` because that is the concrete path directly registered by [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710-L1713) through [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L238). The same implementation entry point is also reused from [`vktApiCopyMemoryIndirectTests.cpp`](../../../modules/vulkan/api/vktApiCopyMemoryIndirectTests.cpp#L2338), but that sibling indirect path is not the root normalized in this page.
- The direct children shown in [`Registration Hierarchy`](external/vulkancts/wiki/testfiles/api/vktApiUseAfterCopyTests.md) are exact format subgroup names observed in the `testFormats` list, not inferred semantic buckets.
- The file clearly contains indirect-copy generation and support logic controlled by the `indirect` parameter to [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710), but this page keeps the concrete `api.copy_and_blit.core.use_after_copy` root because that is the requested single-file normalization target and matches the parent registration context already normalized in the `api` batch.
- The exact number of generated leaf tests was not computed here. The file uses many pruning conditions, and the requested task emphasized source-backed structural normalization rather than a derived total count.
