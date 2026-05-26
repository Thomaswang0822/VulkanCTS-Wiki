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
├── a1r5g5b5_unorm_pack16
├── a8b8g8r8_srgb_pack32
├── b4g4r4a4_unorm_pack16
├── b5g5r5a1_unorm_pack16
├── b5g6r5_unorm_pack16
├── b8g8r8a8_srgb
├── d16_unorm
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
├── d32_sfloat
├── d32_sfloat_s8_uint
├── e5b9g9r9_ufloat_pack32
├── r32g32b32_sfloat
├── r4g4b4a4_unorm_pack16
├── r5g5b5a1_unorm_pack16
├── r5g6b5_unorm_pack16
├── r8_srgb
├── r8_unorm
├── r8g8_srgb
├── r8g8b8_unorm
├── r8g8b8a8_srgb
├── r8g8b8a8_unorm
└── x8_d24_unorm_pack32
```

The Level-3 root documented here is the concrete subgroup created by [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1716-L1719). Within that root, the implementation registers one direct child per format by iterating the explicit `testFormats` table and naming each child with [`getFormatSimpleName()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1721-L1759). The source formats are Vulkan enum names, but the registered CTS path components are lowercase simple names as confirmed by mustpass paths such as `api.copy_and_blit.core.use_after_copy.d16_unorm.*`. Each format child then owns deeper descendants such as `transfer_dst_optimal` and `general`, but those descendants are intentionally described in prose rather than expanded in the parseable tree because the normalizer contract requires exactly one level of direct children.

## Test Families

### format children — Destination formats copied and consumed afterward

The direct children under `use_after_copy` are the lowercase registered names produced from the explicit `testFormats` list in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1721-L1747). The list includes depth/stencil formats such as `d16_unorm`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `x8_d24_unorm_pack32`, `d32_sfloat`, and `d32_sfloat_s8_uint`; color formats such as `r8g8b8a8_unorm`, `r8g8b8_unorm`, `r8_unorm`, `r32g32b32_sfloat`, `r4g4b4a4_unorm_pack16`, `b4g4r4a4_unorm_pack16`, packed 565/5551 formats, sRGB formats, and `e5b9g9r9_ufloat_pack32`.

Depth/stencil format children use the post-copy attachment validation route: [`AfterUsageParams::getImageCreateInfo()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L59-L115) adds depth/stencil attachment usage, and [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1422-L1692) later binds the copied image as the depth/stencil attachment whose preserved values control point visibility. Color format children use sampled post-copy validation: [`AfterUsageCase::initPrograms()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L450-L503) generates fragment shaders that fetch the copied texels, and [`AfterUsageInstance::iterate()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1375-L1705) compares the rendered framebuffer against a CPU-generated reference with format-aware thresholds.

### Deeper generated subgroups shared by all direct children

Every direct format child owns two observed layout subgroups, `transfer_dst_optimal` and `general`, created from the transfer-layout loop in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1763-L1765). Beneath those layout groups, generated leaves encode several parameter axes in their names, including queue suffixes (`_cq`, `_tq`), partial-region mode (`_regions`), 3D-image and 3D-view choices (`_3d_img`, `_3d_view`), extra color-attachment usage (`_color_att_flag`), image-to-image copies (`_img2img`), linear tiling (`_linear`), and multisample variants (`_msaa`) in [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1903-L1933).

## Parameter Dimensions and Observed Values

| Dimension | Observed values / construction | Evidence |
|----------|--------------------------------|----------|
| Direct child format subgroup | `a1r5g5b5_unorm_pack16`, `a8b8g8r8_srgb_pack32`, `b4g4r4a4_unorm_pack16`, `b5g5r5a1_unorm_pack16`, `b5g6r5_unorm_pack16`, `b8g8r8a8_srgb`, `d16_unorm`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat`, `d32_sfloat_s8_uint`, `e5b9g9r9_ufloat_pack32`, `r32g32b32_sfloat`, `r4g4b4a4_unorm_pack16`, `r5g5b5a1_unorm_pack16`, `r5g6b5_unorm_pack16`, `r8_srgb`, `r8_unorm`, `r8g8_srgb`, `r8g8b8_unorm`, `r8g8b8a8_srgb`, `r8g8b8a8_unorm`, `x8_d24_unorm_pack32` | [`vktApiUseAfterCopyTests.cpp`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1721-L1759) |
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
- The direct children shown in [`Registration Hierarchy`](vktApiUseAfterCopyTests.md) are exact format subgroup names observed in the `testFormats` list, not inferred semantic buckets.
- The file clearly contains indirect-copy generation and support logic controlled by the `indirect` parameter to [`createUseAfterXferGroup()`](../../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710), but this page keeps the concrete `api.copy_and_blit.core.use_after_copy` root because that is the requested single-file normalization target and matches the parent registration context already normalized in the `api` batch.
- The exact number of generated leaf tests was not computed here. The file uses many pruning conditions, and the requested task emphasized source-backed structural normalization rather than a derived total count.
