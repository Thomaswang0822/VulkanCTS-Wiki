# DRM Format Modifiers Tests

## Overview

The `drm_format_modifiers` Vulkan CTS category verifies image creation, metadata queries, external-memory binding, and export/import behavior for images using `VK_IMAGE_TILING_DRM_FORMAT_MODIFIER_EXT`. The public category root is registered by the Vulkan test package as `drm_format_modifiers`, which calls `modifiers::createTests` ([vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1385-L1387)). The implementation lives in `modules/vulkan/modifiers/`, not in a source directory named `drm_format_modifiers` ([vktModifiersTests.hpp](../../modules/vulkan/modifiers/vktModifiersTests.hpp#L29-L35), [CMakeLists.txt](../../modules/vulkan/modifiers/CMakeLists.txt#L8-L20)).

`doc/testspecs/VK/apitests.adoc` was inspected as required, but text search found no DRM-format-modifier-specific section. Category-specific statements below are therefore derived from the inspected source and mustpass evidence.

## Registration Entry Point

| Level | Evidence |
|---|---|
| Package root | `TestPackage::init()` registers `drm_format_modifiers` and passes control to `modifiers::createTests` ([vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1385-L1387)). |
| Vulkan SC status | The Vulkan SC package has the `drm_format_modifiers` root commented out in the inspected source ([vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1451-L1454)). |
| Category builder | `modifiers::createTests()` creates a `TestCaseGroup` using the supplied root name and adds twelve direct child groups ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1601-L1766)). |
| Mustpass coverage | The default Vulkan mustpass file contains `dEQP-VK.drm_format_modifiers.*` paths for the registered child groups ([drm-format-modifiers.txt](../../mustpass/main/vk-default/drm-format-modifiers.txt#L1180-L1310)). |

## Subgroup Structure

The direct children below are the groups constructed in `modifiers::createTests()` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1604-L1764)) and are also present in default mustpass paths ([drm-format-modifiers.txt](../../mustpass/main/vk-default/drm-format-modifiers.txt#L1180-L1310)).

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

## File Inventory

| Source file | Wiki page | Role |
|---|---|---|
| [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp) | [vktModifiersTests](../testfiles/drm_format_modifiers/vktModifiersTests.md) | Registers and implements every observed `drm_format_modifiers` child group. |
| [vktModifiersTests.hpp](../../modules/vulkan/modifiers/vktModifiersTests.hpp) | Covered by [vktModifiersTests](../testfiles/drm_format_modifiers/vktModifiersTests.md) | Declares `modifiers::createTests`; it does not register separate tests by itself. |
| [CMakeLists.txt](../../modules/vulkan/modifiers/CMakeLists.txt) | Covered by [vktModifiersTests](../testfiles/drm_format_modifiers/vktModifiersTests.md) | Builds the `deqp-vk-modifiers` library from the implementation and header. |
| [vkFormatLists.inl](../../framework/vulkan/generated/vulkan/vkFormatLists.inl) | Referenced by [vktModifiersTests](../testfiles/drm_format_modifiers/vktModifiersTests.md) | Provides the generated `formats::basicColorFormats` list used to create format leaves. |

Only `vktModifiersTests.cpp` receives a Level-3 page because it is the only inspected file in the module that registers tests.

## Level-3 Documentation

- [vktModifiersTests](../testfiles/drm_format_modifiers/vktModifiersTests.md) — documents the category builder, the twelve direct families, shared parameter generation, support gates, and verification methods.

## Recurring Test Families and Themes

| Theme | Evidence-backed summary |
|---|---|
| Modifier-list queries | `list_modifiers` and `list_modifiers_fmt_features2` enumerate DRM modifier properties through legacy and flags2 list structures, then check compatible 2D image format properties and nonzero tiling features ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L341-L382), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1604-L1626)). |
| Legacy-vs-flags2 consistency | `list_modifiers_consistency` compares the two list APIs by modifier value, plane count, and overlapping feature bits ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L385-L457), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1628-L1637)). |
| Image creation with modifier lists | `create_list_modifiers` and its flags2 variant create 64x64 DRM-modifier images from increasing compatible modifier-list prefixes and verify the reported modifier was in the create list ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L590-L645), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1639-L1661)). |
| dma-buf binding | `bound_to_dma_buf` filters for `VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT`, binds exportable memory to DRM-modifier images, and exports a native handle ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L648-L711), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1663-L1677)). |
| Explicit modifier creation | `create_explicit_modifier` and its flags2 variant obtain per-plane layouts from a list-created image and recreate an image through `VkImageDrmFormatModifierExplicitCreateInfoEXT` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L714-L805), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1679-L1703)). |
| Export/import data paths | `export_import` and `export_import_with_suballoc`, plus their flags2 variants, export opaque-FD memory from DRM-modifier images, import it into explicit-modifier images, and copy data back for comparison; the suballocation helper issues two comparison calls but constructs both inspected comparison accessors from `outputBuffer` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L822-L1088), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1541)). |

## Recurring Parameter Dimensions

| Dimension | Category-level evidence |
|---|---|
| Format leaves | All direct child groups iterate `formats::basicColorFormats` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1610-L1760)). The generated Vulkan list contains 131 formats ([vkFormatLists.inl](../../framework/vulkan/generated/vulkan/vkFormatLists.inl#L1191-L1324)), and the default mustpass file shows 131 leaves for each observed direct child group ([drm-format-modifiers.txt](../../mustpass/main/vk-default/drm-format-modifiers.txt#L1180-L1310)). |
| Modifier values | Modifier IDs are queried at runtime with `vkGetPhysicalDeviceFormatProperties2` and a DRM modifier-list structure in `pNext`; no fixed modifier values are hard-coded in the test source ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L104-L127)). |
| API variant | Most families have a legacy modifier-list variant and a `VK_KHR_format_feature_flags2` variant using `VkDrmFormatModifierPropertiesList2EXT`; `bound_to_dma_buf` and `list_modifiers_consistency` are observed as single direct groups ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1604-L1764)). |
| Image geometry | Helper-created modifier images use 2D, 64x64, one mip level, one array layer, and sample count 1 ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L516-L532), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L569-L585)). |
| External handle type | Opaque FD is used for export/import compatibility filters and memory export/import paths; dma-buf is specifically used by `bound_to_dma_buf` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L250-L255), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L668-L670)). |

## Recurring Support Requirements

The base support path requires `VK_EXT_image_drm_format_modifier`, `VK_KHR_get_physical_device_properties2`, `VK_KHR_bind_memory2`, and `VK_KHR_image_format_list` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L71-L89)). Flags2 groups add `VK_KHR_format_feature_flags2` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L91-L97)). Export/import groups add `VK_KHR_external_memory_fd` before checking compatible DRM modifiers ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L265-L281)).

Runtime support is also data-dependent: cases can be unsupported when a format has no DRM modifiers, when no modifier matches the requested image usage and external-memory feature requirements, or when the suballocation path encounters dedicated-allocation requirements ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L350-L380), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L619-L621), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1191-L1201)).

## Recurring Verification Methods

- **Metadata checks:** modifier lists are checked for nonzero tiling features, compatible image properties, and consistency between legacy and flags2 query paths ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L353-L375), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L398-L455)).
- **Reported modifier checks:** image-creation paths query `vkGetImageDrmFormatModifierPropertiesEXT` and compare the reported modifier against the create-list or explicit modifier expectation ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L630-L642), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L796-L803), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L970-L971)).
- **External-memory operations:** dma-buf and opaque-FD paths verify image binding, exportable memory allocation, native handle export, and import helper success where used ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L698-L708), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1000-L1010)).
- **Pixel readback:** export/import families compare copied output images against a generated reference image with zero integer threshold; in the suballocation helper, the inspected code issues prime and suballocated compare calls while constructing both result accessors from `outputBuffer` ([vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L856-L859), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1081-L1088), [vktModifiersTests.cpp](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1526-L1541)).

## Scope and Uncertainties

- The inspected tree has `external/vulkancts/modules/vulkan/modifiers/`; no `external/vulkancts/modules/vulkan/drm_format_modifiers/` directory was found during source discovery. The source-to-category mapping is evidenced by the package registration call and the `modifiers::createTests` declaration.
- The default mustpass evidence inspected is under `mustpass/main/vk-default/drm-format-modifiers.txt`; no category-specific `apitests.adoc` prose was found.
- This page does not claim exhaustive coverage of every DRM modifier value, because modifier IDs are implementation-reported at runtime rather than fixed in the source.
