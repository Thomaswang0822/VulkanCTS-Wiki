# vktApiUseAfterCopyTests.cpp

Brief summary: [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1) is an implementation-heavy Level-3 file that builds the `use_after_copy` subtree under the Vulkan CTS API `copy_and_blit` category. It verifies that image contents copied into a destination image can still be consumed correctly afterward, either by sampling the copied image in a graphics pass or by using it as a depth/stencil attachment whose contents affect later rendering, across multiple copy APIs, queue types, layouts, image/view types, and sample-count variants.

## Role of the file

- **Role:** implementation-heavy test file.
- **Primary source:** [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1).
- **Minimal registration context inspected:**
  - [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232) for placement under `copy_and_blit/core`.
  - [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L86) for placement under the top-level `api` category.

## Registration path

The inspected registration chain is:

```text
api
└── copy_and_blit
    └── core
        └── use_after_copy
```

Evidence:

- [`createTests()`](../../modules/vulkan/api/vktApiTests.cpp#L146) returns the top-level API group, and [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L86) adds [`createCopiesAndBlittingTests()`](../../modules/vulkan/api/vktApiTests.cpp#L108).
- [`createCopiesAndBlittingTests()`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L267) creates the `copy_and_blit` group.
- [`addCoreCopiesAndBlittingTests()`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L232) adds [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L238) to the `core` subgroup.
- [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710) creates the `use_after_copy` group.

## Observed test hierarchy

The file generates tests with the following hierarchy:

```text
use_after_copy
├── <format>
│   ├── transfer_dst_optimal
│   │   └── <generated test cases>
│   └── general
│       └── <generated test cases>
└── ...
```

Evidence:

- The root `use_after_copy` group is created in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710).
- A per-format subgroup is created from the `testFormats` list in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1715).
- Each format gets `transfer_dst_optimal` and `general` subgroups in the loop over transfer layouts in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757).
- Leaf test names are synthesized from parameter choices before constructing [`AfterUsageCase`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1933).

## Test families

### 1. Post-copy color-texture use

For non-depth/stencil formats, the copied image is created with sampled usage by [`AfterUsageParams::getImageCreateInfo()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L59), a sampler and sampled-image descriptor are created in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1375), and the fragment shader fetches texels from the copied image in [`AfterUsageCase::initPrograms()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L450). The rendered output is then copied back for comparison in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1540).

What this family verifies, as observed in code:

- copied color images remain readable as textures after the transfer;
- this is exercised for full-image and per-layer partial copies;
- the usage path includes normal graphics rendering, not just a direct readback.

### 2. Post-copy depth/stencil attachment use

For depth/stencil formats, the destination image is created with depth/stencil attachment usage in [`AfterUsageParams::getImageCreateInfo()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L59). During verification, the copied image is bound as the render pass depth/stencil attachment in framebuffer creation logic inside [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1422), while points with pseudorandom depths are drawn and pass/fail the depth test according to copied values in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1442) and the reference construction in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1642).

What this family verifies, as observed in code:

- copied depth values can be consumed through later depth testing;
- the correctness criterion is whether blue points appear exactly where `geomVal < bufferVal` after the copy;
- verification is indirect through color-buffer results, not by reading the depth image itself.

### 3. Copy-path variants leading into later use

The same post-copy usage checks are exercised after three transfer mechanisms:

- **Indirect memory-to-image copy** via [`cmdCopyMemoryToImageIndirectKHR()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1306) when the `indirect` group parameter is true.
- **Image-to-image copy** via [`cmdCopyImage()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1325) when `imageToImage` is selected.
- **Classic buffer-to-image copy** via [`cmdCopyBufferToImage()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1345) otherwise.

This means the file is not only about using copied images later; it also checks that the preceding copy mechanism does not leave the image in a state that breaks subsequent use.

### 4. Multisample auxiliary-image path

Multisample variants are only enabled together with `imageToImage` in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1860). The file explains why: buffer-to-image cannot target multisample images directly. Instead, multisample content is generated through a graphics pipeline into an auxiliary image in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1149), then copied to the tested destination image by image-to-image copy in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1325).

## Parameter dimensions and observed values

| Dimension | Observed values / construction | Evidence |
|----------|--------------------------------|----------|
| Format | 20 explicit formats: 5 depth/depth-stencil plus 15 color formats including UNORM, packed UNORM, sRGB, and one UFLOAT format | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1715) |
| Transfer layout | `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, `VK_IMAGE_LAYOUT_GENERAL` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757) |
| Layer count / depth extent | `1` and `2`; used as Z extent in `tcu::IVec3(baseSize, baseSize, layerCount)` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1763) |
| Queue selection | `Universal`, `ComputeOnly`, `TransferOnly` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1765) |
| Base extent | `32x32` on universal/compute queues, `64x64` on transfer queues | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1769) |
| Copy coverage | full copy or generated per-layer partial regions | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1780) |
| 3D image backing | `false`, `true` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1806) |
| 3D view | `false`, `true`, only when backing image is 3D | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1819) |
| Color-attachment usage bit on copied image | `false`, `true`, only for color cases and only with `transfer_dst_optimal` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1836) |
| Copy source type | buffer-to-image vs image-to-image | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1848) |
| Tiling | optimal and selected linear-tiling cases | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1849) |
| Linear-tiling formats | limited to `VK_FORMAT_R32G32B32_SFLOAT` in inspected file | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1743) |
| Sample count | `1` or `4` samples | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1860) |
| Large-image expansion for color-attachment-flag cases | scaled from base extent to `1024x1024xlayerCount` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1883) |

### Partial-copy region construction

When `fullCopy` is false, one `VkRect2D` is generated per layer. Each region uses half-size extents divided again on one axis and offsets one axis by a quarter-image amount, with different axis choices per layer in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1782). This creates asymmetric per-layer regions rather than a single repeated rectangle.

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

Evidence: test-name construction in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1903).

## Support and feature requirements

The file has a substantial support gate in [`AfterUsageCase::checkSupport()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L253). Observed requirements include:

| Requirement | When it applies | Evidence |
|------------|-----------------|----------|
| `VK_KHR_copy_memory_indirect` and `indirectMemoryToImageCopy` feature | indirect-copy cases | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L255) |
| `VK_KHR_maintenance1` | 3D image with 2D-array-compatible view when `extent.z() > 1` | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L268) |
| `VK_EXT_image_2d_view_of_3d` features `image2DViewOf3D` and, for color sampling, `sampler2DViewOf3D` | single-slice 3D image viewed as 2D on non-SC builds | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L272) |
| `VK_KHR_maintenance10` plus queue-specific depth-copy format features | classic non-universal depth copies on compute or transfer queues | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L290) |
| `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR` | indirect cases | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L309) |
| Transfer-queue granularity compatibility | transfer-only queue with partial regions | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L320) |
| Queue support for indirect-copy commands | indirect cases on chosen queue family | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L335) |
| Format/image support via `vkGetPhysicalDeviceImageFormatProperties` | all cases | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L365) |
| `VK_EXT_shader_viewport_index_layer` | multi-slice cases | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L384) |
| core geometry shader feature | multi-slice color cases | [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L388) |

## Combination-pruning rules observed in generation code

The generator deliberately removes combinations before runtime support checks:

- indirect depth/stencil copies only remain on the universal queue, due to the cited VUID comment in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1775);
- Vulkan SC excludes single-slice `use3DImage` cases because `VK_EXT_image_2d_view_of_3d` is unavailable in the inspected branch at [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1808);
- depth/stencil cases never use 3D images or 3D views in generated combinations, see [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1814) and [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1824);
- color cases skip 3D-image + multi-slice + non-3D-view combinations to avoid the cited descriptor-image VUID in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1827);
- `colorAttFlag` is only kept for color formats, `transfer_dst_optimal` layout, and non-3D views in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1836);
- image-to-image cases are skipped when `indirect` is true, when `use3DImage` is true, or when `layerCount == 1`, according to [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1855);
- multisample cases are only kept when `imageToImage` is true in [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1860).

## Verification methods

### 1. Render-after-copy verification

The test does not validate copied data immediately after the transfer. Instead, it performs a later graphics use of the copied image:

- sampled texture reads for color cases in the fragment shader generated by [`AfterUsageCase::initPrograms()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L450);
- attachment-based depth testing for depth/stencil cases through the graphics pipeline built in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1422).

This is the core `use after copy` principle observed in the file.

### 2. Reference-image synthesis from the same parameters

The expected framebuffer is synthesized on the CPU after execution in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1620):

- outside partial-copy regions, expected pixels stay at the clear color in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1631);
- for depth/stencil cases, expected blue/black pixels are derived from the copied depth value versus the point depth in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1642);
- for color cases, expected texel values come from the generated source texture data, with explicit sRGB handling notes in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1658).

### 3. Thresholded image comparison

The result color attachment is copied to a buffer in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1540), mapped as a TCU image in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1683), and compared layer-by-layer with [`tcu::floatThresholdCompare()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1691).

Threshold selection is format-aware:

- depth/stencil cases use zero threshold in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1688);
- color cases compute thresholds from format bit depth or mantissa width via [`getColorFormatThreshold()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L504) and [`bitWidthToThreshold()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L493).

## Test principles observed in the file

- **State validity after copy matters as much as copy correctness.** The copied destination image is transitioned and then consumed through realistic later usage, rather than verified only by direct readback; see queue ownership and layout transitions in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1027) and later graphics usage in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1477).
- **Queue-family transfer paths are first-class coverage.** The file explicitly supports universal, compute-only, and transfer-only queues via [`AfterUsageParams::getQueueFamilyIndex()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L181) and semaphored multi-submit execution in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1547).
- **Partial copies are checked by observing preserved clear values outside copied rectangles.** That principle appears in the CPU reference logic in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1631).
- **Color and depth/stencil cases use different oracles.** Color cases compare sampled texels; depth/stencil cases compare whether later depth testing admitted geometry, as described in comments and implementation around [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L708).
- **MSAA coverage uses an auxiliary fill path because direct buffer-to-image copy is unavailable.** This principle is documented in comments and implemented in [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L676) and [`AfterUsageInstance::iterate()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1149).

## Notes and uncertainties

- The inspected registration context shows only one call site for [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710): `copy_and_blit/core` in [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L238). Within the scoped files requested by the user, no additional registration path was observed.
- [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710) takes a boolean `indirect` parameter, but the inspected registration call passes `false` in [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L238). The file clearly contains indirect-copy generation and support logic, but that indirect subtree was **not observed as registered** within the requested minimal registration context.
- The file uses both `copy` and `xfer` terminology in symbol names, for example [`createUseAfterXferGroup()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710), but the actual public group name is `use_after_copy` in the same function.
- The exact number of generated leaf tests was not computed here. The file uses many pruning conditions, and the requested task emphasized evidence-backed structural documentation rather than a derived total count.
