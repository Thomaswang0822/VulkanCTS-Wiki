## Overview

**Core question:** Does the implementation report, create, bind, export, import, and copy images with the DRM format modifiers that the device advertises?

- `vktModifiersTests.cpp` owns the registered `drm_format_modifiers` test category. `createTests()` adds twelve direct test families and creates one format leaf in each family for every element of `formats::basicColorFormats` ([createTests](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1601-L1766)).
- The tests exercise `VK_IMAGE_TILING_DRM_FORMAT_MODIFIER_EXT` at two levels: metadata returned by `vkGetPhysicalDeviceFormatProperties2`, and image plus external-memory operations.
- The default mustpass file contains 1,572 leaves: twelve direct families times 131 format leaves ([drm-format-modifiers.txt](../../../mustpass/main/vk-default/drm-format-modifiers.txt#L1-L1572)).
- The implementation has no shader stage or generated shader source. The device work is image transfer work, and the host checks reported modifiers, external-memory setup, and copied pixels.

## Background Knowledge

- A DRM format modifier describes an implementation-defined memory arrangement for an image. It is part of the image tiling choice, not a second Vulkan format. The Vulkan specification treats the modifier properties as format and modifier properties that do not depend on one particular image ([DRM modifier properties](../../../../vulkan-docs/src/chapters/formats.adoc#VkDrmFormatModifierPropertiesEXT)).
- A format plane partitions image content. A memory plane partitions the image's backing memory. Non-linear modifiers can have a memory planecount that differs from the format planecount, so the explicit-create path must use the memory planecount reported for the selected modifier ([memory and format planes](../../../../vulkan-docs/src/chapters/formats.adoc#formats-multiplanar)).
- External image format queries combine the format, image type, tiling, usage, modifier, and handle type. An incompatible handle type or image combination returns `VK_ERROR_FORMAT_NOT_SUPPORTED` ([external image format query](../../../../vulkan-docs/src/chapters/capabilities.adoc#VkPhysicalDeviceExternalImageFormatInfo)).

## Registration Hierarchy

```text
drm_format_modifiers
├── list_modifiers
├── list_modifiers_fmt_features2
├── list_modifiers_consistency
├── create_list_modifiers
├── create_list_modifiers_fmt_features2
├── bound_to_dma_buf
├── create_explicit_modifier
├── create_explicit_modifier_fmt_features2
├── export_import
├── export_import_fmt_features2
├── export_import_with_suballoc
└── export_import_fmt_features2_with_suballoc
```

All twelve families are implemented and registered by `vktModifiersTests.cpp`; none is a registration-only child ([family construction](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1604-L1764)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Direct test family | `list_modifiers`, `list_modifiers_fmt_features2`, `list_modifiers_consistency`, `create_list_modifiers`, `create_list_modifiers_fmt_features2`, `bound_to_dma_buf`, `create_explicit_modifier`, `create_explicit_modifier_fmt_features2`, `export_import`, `export_import_fmt_features2`, `export_import_with_suballoc`, `export_import_fmt_features2_with_suballoc` | Selects the API or memory path under test. | [family registration](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1604-L1764) |
| Format | The 131 entries in `formats::basicColorFormats`, from `VK_FORMAT_R4G4_UNORM_PACK8` through `VK_FORMAT_A4B4G4R4_UNORM_PACK16` | Tests the same operations across packed, 8-bit, 16-bit, 32-bit, 64-bit, floating-point, and component-width formats. The generated case name is the lower-case format name without the `VK_FORMAT_` prefix. | [basicColorFormats](../../../framework/vulkan/generated/vulkan/vkFormatLists.inl#L1191-L1324) |
| DRM modifier | Runtime values returned in `VkDrmFormatModifierPropertiesEXT` or `VkDrmFormatModifierProperties2EXT` | Keeps the matrix device-dependent. The test never hard-codes a modifier value. | [two-call modifier query](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L104-L127) |
| Modifier-list API | `VkDrmFormatModifierPropertiesListEXT` and `VkDrmFormatModifierPropertiesList2EXT` | Compares the legacy format-feature flags path with the `VkFormatFeatureFlags2` path. | [list template instantiations](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1613-L1621) |
| Image shape | 2D, `64 x 64 x 1`, one mip level, one array layer, `VK_SAMPLE_COUNT_1_BIT` | Holds image geometry constant while the format and modifier change. | [image creation helpers](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L484-L587) |
| Image tiling and usage | `VK_IMAGE_TILING_DRM_FORMAT_MODIFIER_EXT`; color attachment plus sampled usage in the metadata and external-image compatibility queries; transfer source plus transfer destination usage on the data-path images | Distinguishes the properties used to filter modifiers from the usages of the images that carry out the transfer round-trip. | [compatibility query](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L283-L339), [transfer image setup](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L892-L895) |
| External handle | `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` or `VK_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD_BIT` | Selects a Linux dma-buf export path or a Vulkan opaque-FD export and import path. | [dma-buf filter](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L648-L670), [opaque-FD filter](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L228-L260) |
| Modifier-list length | Every increasing prefix of the compatible modifier list | Checks that the implementation chooses a modifier from the submitted list rather than requiring one particular list length. | [list creation loop](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L623-L643) |
| Memory layout | Reference image layouts queried per memory plane, with `size`, `arrayPitch`, and `depthPitch` set to zero for explicit creation | Supplies the fields the explicit-modifier valid-usage rules require and preserves the implementation's offset and row-pitch information. | [plane layout preparation](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L767-L799) |

The default mustpass has exactly 131 leaves under each direct family. Its format set matches `formats::basicColorFormats`, but the mustpass entries are emitted in a different, lower-case lexicographic order; case names are strings such as `a8_unorm`, `r8g8b8a8_unorm`, and `r64g64b64a64_sfloat` ([mustpass sample and full range](../../../mustpass/main/vk-default/drm-format-modifiers.txt#L1-L1572)).

## Behavior Parameters

The primary behavioral axis is the registered test family. The modifier and format values select the concrete device-dependent instance inside each family.

### list_modifiers, list_modifiers_fmt_features2, and list_modifiers_consistency: report and compare metadata

The two listing families perform the two-call modifier query, then use `vkGetPhysicalDeviceImageFormatProperties2` with the selected modifier, opaque-FD handle type, color-attachment and sampled usage, and required export and import features. A compatible entry must expose nonzero tiling features and usable extent and layer limits. The consistency family indexes both returned lists by `drmFormatModifier`, so ordering does not matter, and checks plane counts plus the overlapping feature bits ([listing and consistency checks](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L341-L457)).

The flags2 list must contain every legacy modifier and may expose additional high feature bits. For the low 32 bits shared by the two structures, the implementation requires equality, and it requires equal memory planecounts.

### create_list_modifiers and create_list_modifiers_fmt_features2: choose from a submitted list

For each compatible modifier, the test creates 64 x 64 images with increasing prefixes of the compatible modifier list. It calls `vkGetImageDrmFormatModifierPropertiesEXT` and fails if the reported modifier is not in the submitted prefix ([list image creation](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L590-L645)). The specification permits the implementation to choose any modifier from the list ([modifier-list create info](../../../../vulkan-docs/src/chapters/resources.adoc#VkImageDrmFormatModifierListCreateInfoEXT)).

### bound_to_dma_buf: create, bind, and export a dma-buf image

This family filters for transfer-capable modifiers that support `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT` and exportable memory. It tries every increasing compatible modifier-list prefix, allocates exportable memory, binds the image at offset zero, and obtains a native dma-buf handle ([dma-buf path](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L648-L711)). It does not perform a pixel round-trip.

### create_explicit_modifier and create_explicit_modifier_fmt_features2: recreate a queried layout

For each compatible modifier, the test first creates a reference image from a one-element modifier list. It queries each memory plane with `vkGetImageSubresourceLayout`, clears the fields that the explicit-create valid-usage rules require to be zero, and creates a second image with `VkImageDrmFormatModifierExplicitCreateInfoEXT`. The test then checks that the created image reports the requested modifier ([explicit image path](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L714-L805)). The Vulkan specification requires the plane count to match the modifier properties and says that an implementation returns `VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT` if the supplied layout does not produce a valid image ([explicit modifier create info](../../../../vulkan-docs/src/chapters/resources.adoc#VkImageDrmFormatModifierExplicitCreateInfoEXT)).

### export_import and export_import_fmt_features2: opaque-FD copy round-trip

The test fills a host-visible reference buffer with component gradients, copies it into a non-modifier source image, and copies that image into an exportable DRM-modifier destination. It checks the destination's reported modifier, exports an opaque FD, and imports it into an explicitly described DRM-modifier image. A copy to a non-modifier output image is then copied to a host-visible buffer and compared with the reference using an integer threshold of zero ([opaque-FD round-trip](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L822-L1088)).

The compatibility filter requires transfer source, transfer destination, blit source, and blit destination format features, plus opaque-FD export and import support. A missing `VK_KHR_external_memory_fd` device function stops the family before the case runs ([external-memory setup](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L228-L281)). An opaque FD is a POSIX descriptor that owns a reference to the Vulkan memory payload ([opaque-FD semantics](../../../../vulkan-docs/src/chapters/capabilities.adoc#VkExternalMemoryHandleTypeFlagBits)).

### export_import_with_suballoc and export_import_fmt_features2_with_suballoc: two images in one allocation

The suballocation path applies the same opaque-FD round-trip to two DRM-modifier images. It first rejects modifiers whose external image properties require dedicated allocation, checks both images with `vkGetImageMemoryRequirements2`, rounds the first image size up to its alignment, allocates one exportable block, and binds the second image at the aligned offset ([suballocation setup](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1226)). It exports the block, imports it with a doubled size, binds two explicit-modifier images at offsets zero and `alignedSingleImageSize`, and records copyback into `outputBuffer` and `outputSubBuffer`; however, the current checking code constructs both result views from `outputBuffer`, so the second comparison is not independent ([suballocation import and copyback](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1352-L1529)).

The wrapper records per-modifier unsupported cases. If every compatible modifier is rejected for suballocation, the test reports `NotSupportedError`; if at least one modifier runs and either comparison fails, the test fails ([suballocation result handling](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1544-L1597)).

## Shader Analysis

No shader code participates in these tests. `vktModifiersTests.cpp` creates images, records transfer commands, exports and imports memory, and compares host-visible image data. There is therefore no source-backed GLSL or HLSL case for `shader-analyzer` or `shader-disassembler` to reconstruct. Representative device status is transfer-only: the data-path families validate image copies through a selected DRM modifier, while listing, creation, binding, and suballocation families also validate Vulkan metadata and memory operations.

## Runtime Execution and Result Checking

- The host queries modifier properties with `vkGetPhysicalDeviceFormatProperties2` twice: once for the count and once to fill the property array. It then filters each modifier through `vkGetPhysicalDeviceImageFormatProperties2` with the exact format, 2D image type, DRM modifier tiling, usage, handle type, and required external-memory features ([modifier query and filter](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L104-L178)).
- The list and explicit-create helpers create 64 x 64 images with one mip level and one array layer. List creation checks membership of the reported modifier. Explicit creation checks equality with the requested modifier.
- The dma-buf family allocates exportable memory, binds the image at offset zero, and obtains a native handle. The test treats completion of those operations as its result.
- The opaque-FD data path initializes a reference with `tcu::fillWithComponentGradients`, flushes the input allocation, records image barriers and copies, submits and waits, invalidates the output allocation, and runs `tcu::intThresholdCompare` with `tcu::UVec4(0u)` ([reference and result checking](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L841-L859), [comparison](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1074-L1088)).
- The suballocation path repeats the copy for a primary and an offset-bound image, imports both explicit images from one FD-backed allocation, and compares both results after the second submission.
- For the non-suballocation families, a pass means every selected compatible modifier completed the family-specific checks. In the suballocation families, modifiers rejected as unsupported are skipped and a pass means every remaining modifier completed; if all are rejected, the case is unsupported. A case can also be unsupported when the device has no compatible modifier for the requested format, usage, handle type, or allocation model.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `list_modifiers`, `list_modifiers_fmt_features2` | The returned modifier list, tiling feature bits, plane metadata, or image-format compatibility query violates the list and image-property contract. |
| `list_modifiers_consistency` | The legacy and flags2 queries disagree about a modifier, memory planecount, or shared feature bits. |
| `create_list_modifiers`, `create_list_modifiers_fmt_features2` | Image creation selected a modifier outside the submitted list, or the device rejected a list that the test's support query considered compatible. |
| `bound_to_dma_buf` | The modifier image cannot be allocated, bound, or exported with the dma-buf handle type selected by the support query. |
| `create_explicit_modifier`, `create_explicit_modifier_fmt_features2` | The implementation rejected or misreported an explicit modifier and its queried memory-plane layout. |
| `export_import`, `export_import_fmt_features2` | Opaque-FD export/import or the image copy path changed the gradient data, or a reported modifier did not match the selected modifier. |
| `export_import_with_suballoc`, `export_import_fmt_features2_with_suballoc` | The allocation offsets, import description, two-image binding, or one of the two copyback comparisons did not preserve the image data. |

### Cause Analysis

#### Modifier metadata and feature-list mismatch

**Possible failure symptoms:** The test logs a missing modifier, mismatched memory planecount, inconsistent shared feature bits, zero tiling features, or an image-property limit below one pixel or one array layer.

**Possible implementation causes:** The format-properties query may expose inconsistent legacy and flags2 data, or the image-format query may not describe the same format, modifier, usage, and handle type that the list advertises. Source-level investigation is needed to distinguish a Vulkan implementation defect from an invalid query result.

#### Image creation or explicit-plane-layout failure

**Possible failure symptoms:** Image creation returns an error, the reported modifier differs from the submitted or requested value, or explicit creation returns `VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT`.

**Possible implementation causes:** The implementation may reject a legal modifier-list choice, calculate incompatible plane offsets or pitches, or report a memory planecount that does not match explicit creation. The source queries layout offsets and pitches from a reference image, so a failure can also expose a mismatch between list creation and explicit creation for the same format and modifier.

#### External-memory handle or binding failure

**Possible failure symptoms:** Allocation, binding, `getMemoryNative`, FD export, or FD import fails after the compatibility filter accepted the modifier.

**Possible implementation causes:** The reported `compatibleHandleTypes` or export/import feature bits may not match the actual image and usage combination. For dma-buf, the native handle path may fail even though image creation and allocation succeeded. For opaque FD, the imported allocation must satisfy the external-memory and dedicated-allocation rules for the payload being imported ([external-memory allocation rules](../../../../vulkan-docs/src/chapters/memory.adoc#memory-external)).

#### Pixel copy or suballocation result mismatch

**Possible failure symptoms:** `tcu::intThresholdCompare` reports a difference from the component-gradient reference, or a suballocation comparison fails after both images were imported and copied back.

**Possible implementation causes:** A copy, layout transition, modifier interpretation, FD payload mapping, or allocation offset may corrupt or misaddress image memory. Host invalidation or copyback handling can also affect the observed buffer, so source-level investigation must follow the exact failing family and modifier.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_image_drm_format_modifier`, instance support for `VK_KHR_get_physical_device_properties2`, device support for `VK_KHR_bind_memory2`, and `VK_KHR_image_format_list` ([base support check](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L71-L89)).
- The flags2 families additionally require `VK_KHR_format_feature_flags2` ([flags2 support check](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L91-L97)).
- `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` in non-VulkanSC builds. These formats are in the inspected generated list where applicable ([format list tail](../../../framework/vulkan/generated/vulkan/vkFormatLists.inl#L1316-L1324)).
- Listing and image-creation paths keep only modifiers compatible with the requested image properties and opaque-FD export and import requirements. `bound_to_dma_buf` uses dma-buf export support and transfer usage. Export/import paths also require `VK_KHR_external_memory_fd` ([filters](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L228-L281), [dma-buf filter](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L664-L679)).
- The suballocation families exclude modifiers whose external image properties require dedicated allocation and reject images whose `VkMemoryDedicatedRequirements::requiresDedicatedAllocation` is true ([non-dedicated filter](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L129-L178), [dedicated checks](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1117-L1123), [image checks](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1191-L1201)).

This is requirement-based pruning. A skipped case means the requested operation is not supported for that format and modifier on the current implementation. It is not a successful execution of the operation.

### Design-based pruning

- The implementation uses the one fixed 2D image shape and does not generate separate mip-level, array-layer, sample-count, or image-extent cases.
- The modifier-list creation families test increasing prefixes rather than every permutation of the compatible modifier list. The Vulkan rule under test is membership in the submitted list, not list ordering.
- The data paths use one component-gradient reference and a zero integer threshold. They do not add shader, render-pass, or format-conversion variants.

## Key Takeaways

- The 1,572 default leaves cover twelve direct families and the same 131-format set. Concrete DRM modifier values come from the physical device at runtime.
- The flags2 families are not separate modifier universes. They verify the `VkFormatFeatureFlags2` query path and compare its shared data with the legacy path.
- The list-create tests check implementation choice from an allowed list. The explicit-create tests check a requested modifier plus memory-plane layout.
- The dma-buf family checks export and binding without a pixel round-trip. The opaque-FD families add data preservation through export, import, and image copies.
- A pass or failure in these tests does not identify a particular driver layer. The result reflects the complete queried format, modifier, image, memory, handle, copy, and host-check path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test category construction | [createTests](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1601-L1766) | Registers all twelve direct families and iterates `formats::basicColorFormats`. |
| Base and flags2 support checks | [checkModifiersSupported and checkModifiersList2Supported](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L71-L97) | Defines the extension requirements for every family. |
| Runtime modifier query | [getDrmFormatModifiers](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L104-L127) | Performs the count and data queries through `VkFormatProperties2`. |
| External image compatibility | [verifyHandleTypeForFormatModifier](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L129-L178) | Checks format support, compatible handle types, export/import bits, and non-dedicated support. |
| Legacy and flags2 consistency | [listModifiersConsistency](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L385-L457) | Compares modifier keys, memory planecounts, and shared feature bits. |
| Modifier-list image creation | [createImageListModifiersCase](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L590-L645) | Tests increasing modifier-list prefixes and reported modifier membership. |
| dma-buf binding and export | [createAndBoundImageToDmaBufCase](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L648-L711) | Creates, binds, allocates, and exports a dma-buf image. |
| Explicit modifier creation | [createImageModifierExplicitCase](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L714-L805) | Reuses queried plane layouts and checks the requested modifier. |
| Opaque-FD round-trip | [exportImportMemoryExplicitModifiersCase](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L822-L1107) | Copies a gradient through export, import, explicit creation, and host comparison. |
| Suballocation round-trip | [exportImportMemoryExplicitModifiersWithSuballocationCase](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1597) | Binds two images in one allocation and handles per-modifier support and comparison results. |
| Format modifier specification | [DRM modifier properties](../../../../vulkan-docs/src/chapters/formats.adoc#VkDrmFormatModifierPropertiesEXT) | Defines modifier properties, tiling features, and memory planecount. |
| Modifier image creation specification | [modifier-list and explicit-create structures](../../../../vulkan-docs/src/chapters/resources.adoc#VkImageDrmFormatModifierListCreateInfoEXT) | Defines list selection, explicit layouts, valid usage, and invalid plane-layout errors. |
| External image capabilities specification | [external image format query](../../../../vulkan-docs/src/chapters/capabilities.adoc#VkPhysicalDeviceExternalImageFormatInfo) | Defines handle-type compatibility and `VK_ERROR_FORMAT_NOT_SUPPORTED`. |
| External memory allocation specification | [external memory chapter](../../../../vulkan-docs/src/chapters/memory.adoc) | Defines opaque-FD import and dedicated-allocation requirements. |
| Default mustpass coverage | [drm-format-modifiers.txt](../../../mustpass/main/vk-default/drm-format-modifiers.txt#L1-L1572) | Records the 1,572 registered default leaves. |

The validator commands were run for this page. Exact results: `verify_english_structure.py` exited 0 with `PASS external/vulkancts/wiki/testfiles/drm_format_modifiers` and no findings; `verify_registration_paths.py` exited 0 with `Collected 13 paths from external/vulkancts/wiki/testfiles/drm_format_modifiers`, `PASS Modifiers.md`, and `All paths verified successfully`; and `validate_wiki_links.py` exited 0 with `All local wiki links are valid.` This source-backed page has no shader behavior, and `Modifiers.md` is listed in the repository's `PAGES_WITHOUT_WALKTHROUGH` exception registry, so no shader walkthrough is required.

Known source risks remain documented rather than repaired. In the suballocation helper, `subDstProperties` is queried from `*dstImage` instead of `*dstSubImage`, both `subImageResult` and `primeImageResult` use `outputBuffer` host storage, and `outSubImage` is bound at offset zero in the output allocation ([suballocation result code](../../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1346-L1541)). These source observations may weaken the independence of the second-image checks. This rewrite does not modify source, mustpass, the exception registry, or the obsolete page.
