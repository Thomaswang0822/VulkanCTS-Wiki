# [vktApiFeatureInfo.cpp](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1)

## Overview

[`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1) implements the `api.info` subgroup registered by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L96) and [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635). The file is extremely large and covers querying and validating physical device features, properties, format properties, image format properties, extension core versions, extended properties via `vkGetPhysicalDeviceProperties2`, Vulkan 1.2/1.3/1.4 feature/property consistency, limits validation, and platform-specific tests such as Android, subgroup-feature, and profile checks.

## Role of File

Implementation-heavy test file for the `api.info` subgroup.

## Source Code

- Primary source: [vktApiFeatureInfo.cpp](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1)
- Header: [vktApiFeatureInfo.hpp](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L96)
- Local subgroup registration: [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635)

## Registration Hierarchy

```text
api.info
├── format_properties
├── image_format_properties
├── unsupported_image_usage
├── extension_core_versions
├── get_physical_device_properties2
├── vulkan1p2
├── vulkan1p3 (not in Vulkan SC)
├── vulkan1p4 (not in Vulkan SC)
├── vulkan1p2_limits_validation
├── vulkan1p3_limits_validation
├── vulkan1p4_limits_validation
├── image_format_properties2
├── sparse_image_format_properties2 (not in Vulkan SC)
├── profiles (not in Vulkan SC)
└── subgroup_features (not in Vulkan SC)
```

The Level-3 root is the `info` subgroup added to `api` by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L96) via [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635-L8921). The exact direct child groups listed above are registered in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639-L8918). The `android` subgroup is registered in source at [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8896-L8909), but it is intentionally excluded from the canonical validator tree because `dEQP-VK.api.info.android` is not present in [`api.txt`](../../../mustpass/main/vk-default/api.txt). Its deeper cases are still documented below as source-backed auxiliary coverage.

## Test Families

### format_properties — Physical-device format-property queries

The `format_properties` subgroup is registered by [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639) and delegates to `createFormatTests`, covering `vkGetPhysicalDeviceFormatProperties` queries over the core format range.

### image_format_properties — Image-format capability queries

The `image_format_properties` subgroup is registered by [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8640-L8641) and delegates to `createImageFormatTests` with the `imageFormatProperties` mode to exercise `vkGetPhysicalDeviceImageFormatProperties`.

### unsupported_image_usage — Unsupported image-usage rejection

The `unsupported_image_usage` subgroup is registered by [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8642-L8643) and delegates to `createImageUsageTests` with the `unsupportedImageUsage` mode to check that unsupported image-usage combinations are not exposed.

### extension_core_versions — Extension promotion reporting

The `extension_core_versions` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8646-L8650). It contains the direct leaf case `extension_core_versions`, added by [`addFunctionCase()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8648), which checks that extensions promoted into core are reported consistently.

### get_physical_device_properties2 — Extended properties and features via `vkGetPhysicalDeviceProperties2`

The `get_physical_device_properties2` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8654-L8743). Its direct children are `features`, `properties`, `format_properties`, `queue_family_properties`, `memory_properties`, and `pnext_format_properties`, registered by [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8658-L8679). The `features` branch contains the direct `core` case plus additional per-feature cases from `addSeparateFeatureTests`, and adds `shader_subgroup_rotate_property_consistency_khr` on non-VulkanSC builds at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8660-L8665). The `pnext_format_properties` branch then generates per-format subgroups, each populated with flag-combination cases such as `drm_format_mod_1`, `drm_format_mod_2`, `format_props_3`, optional `subpass_resolve_query`, and mixed combinations, as shown in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8678-L8740).

### vulkan1p2 — Vulkan 1.2 feature/property consistency

The `vulkan1p2` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8746-L8760). It registers direct leaf cases `features`, `properties`, `feature_extensions_consistency`, `property_extensions_consistency`, and `feature_bits_influence`, which compare core and extension reporting for Vulkan 1.2 and verify device-creation behavior when feature bits are enabled.

### vulkan1p3 — Vulkan 1.3 feature/property consistency

The `vulkan1p3` subgroup is created on non-VulkanSC builds in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8763-L8779). It mirrors the Vulkan 1.2 structure with direct leaf cases `features`, `properties`, `feature_extensions_consistency`, `property_extensions_consistency`, and `feature_bits_influence` for Vulkan 1.3 reporting.

### vulkan1p4 — Vulkan 1.4 feature/property consistency

The `vulkan1p4` subgroup is created on non-VulkanSC builds in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8780-L8795). It likewise registers `features`, `properties`, `feature_extensions_consistency`, `property_extensions_consistency`, and `feature_bits_influence` direct cases for Vulkan 1.4 reporting.

### vulkan1p2_limits_validation — Vulkan 1.2 and extension limits validation

The `vulkan1p2_limits_validation` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8798-L8853). Its direct leaf cases include `general`, `khr_multiview`, `ext_discard_rectangles`, `ext_sample_locations`, `ext_external_memory_host`, `ext_blend_operation_advanced`, `khr_maintenance_3`, `ext_conservative_rasterization`, `ext_descriptor_indexing`, `khr_vertex_attribute_divisor`, `timeline_semaphore`, `ext_line_rasterization`, `khr_line_rasterization`, and `robustness2`, plus non-VulkanSC-only cases `khr_push_descriptor`, `ext_inline_uniform_block`, `ext_vertex_attribute_divisor`, `nv_mesh_shader`, `ext_transform_feedback`, `fragment_density_map`, and `nv_ray_tracing`, all registered in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802-L8850).

### vulkan1p3_limits_validation — Vulkan 1.3 limits validation

The `vulkan1p3_limits_validation` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8855-L8867). On non-VulkanSC builds it registers the direct leaf cases `khr_maintenance4` and `max_inline_uniform_total_size` at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8859-L8863).

### vulkan1p4_limits_validation — Vulkan 1.4 limits validation

The `vulkan1p4_limits_validation` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8869-L8878). On non-VulkanSC builds it registers the direct leaf case `general` at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8873-L8874).

### image_format_properties2 — `vkGetPhysicalDeviceImageFormatProperties2` queries

The `image_format_properties2` subgroup is registered by [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8880-L8881) and delegates to `createImageFormatTests` with the `imageFormatProperties2` mode.

### sparse_image_format_properties2 — Sparse image-format capability queries

The `sparse_image_format_properties2` subgroup is registered on non-VulkanSC builds by [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8882-L8884) and delegates to `createImageFormatTests` with the `sparseImageFormatProperties2` mode.

### profiles — Vulkan profile validation

The `profiles` subgroup is created on non-VulkanSC builds in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8886-L8893). It iterates over `profileEntries` and registers one direct leaf case per profile entry using [`addFunctionCase()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8889-L8890).

### android — Android-specific feature-info checks

The `android` subgroup is created in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8896-L8909). It registers the direct leaf cases `mandatory_extensions`, `no_unknown_extensions`, and `no_layers` at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8900-L8906).

### subgroup_features — Subgroup feature-flag validation

The `subgroup_features` subgroup is created on non-VulkanSC builds in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8911-L8918). It registers the direct leaf case `flags` at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8915).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Format range | `VK_FORMAT_UNDEFINED + 1` through `VK_FORMAT_ASTC_12x12_SRGB_BLOCK` in the `pnext_format_properties` generator at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8681-L8738) |
| `pNext` flag combinations | `PNEXT_DRM_FORMAT_MODIFIER_PROPERTIES_LIST`, `PNEXT_DRM_FORMAT_MODIFIER_PROPERTIES_LIST_2`, `PNEXT_FORMAT_PROPERTIES_3`, optional `PNEXT_SUBPASS_RESOLVE_PERFORMANCE_QUERY`, and their mixed combinations at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8685-L8719) |
| Vulkan versions | `vulkan1p2`, `vulkan1p3`, and `vulkan1p4` direct subgroups registered at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8746-L8795) |
| Extension-specific limits cases | `general`, `khr_push_descriptor`, `khr_multiview`, `ext_discard_rectangles`, `ext_sample_locations`, `ext_external_memory_host`, `ext_blend_operation_advanced`, `khr_maintenance_3`, `ext_conservative_rasterization`, `ext_descriptor_indexing`, `ext_inline_uniform_block`, `ext_vertex_attribute_divisor`, `khr_vertex_attribute_divisor`, `nv_mesh_shader`, `ext_transform_feedback`, `fragment_density_map`, `nv_ray_tracing`, `timeline_semaphore`, `ext_line_rasterization`, `khr_line_rasterization`, and `robustness2` in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802-L8850) |
| Android direct cases | `mandatory_extensions`, `no_unknown_extensions`, and `no_layers` in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8900-L8906) |

## Support / Feature Requirements

- Vulkan-version consistency branches use [`checkApiVersionSupport<1, 2>()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8757), [`checkApiVersionSupport<1, 3>()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8775), and [`checkApiVersionSupport<1, 4>()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8791) for their `feature_bits_influence` cases.
- `vulkan1p2_limits_validation` uses dedicated extension/feature support checks such as [`checkSupportKhrPushDescriptor()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8805), [`checkSupportExtDiscardRectangles()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8810), [`checkSupportExtDescriptorIndexing()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8822), and [`checkSupportRobustness2()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8850).
- `shader_subgroup_rotate_property_consistency_khr` requires [`checkSupportKhrShaderSubgroupRotate()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8663-L8665).
- Android cases use [`android::checkSupportAndroid()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8900-L8906).
- `subgroup_features.flags` requires [`checkApiVersionSupport<1, 4>()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8915).

## Verification Methods

- `format_properties`, `image_format_properties`, `image_format_properties2`, and sparse-image-format branches validate reported format capabilities through the delegated query helpers registered in [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639-L8643) and [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8880-L8884).
- `extension_core_versions` checks consistency between extension promotion state and reported core-version behavior through the direct `extension_core_versions` case added at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8648).
- `get_physical_device_properties2`, `vulkan1p2`, `vulkan1p3`, and `vulkan1p4` compare core and extension-reported feature/property values through their direct consistency cases registered at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8658-L8675) and [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8750-L8791).
- Limits-validation branches verify that reported limits satisfy expected minimums through the direct validation cases registered at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802-L8874).
- `feature_bits_influence` cases verify that enabling selected feature bits changes device-creation behavior for the corresponding Vulkan version at [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8757-L8791).

## Test Principles Observed

- Wide registration fan-out from one implementation file, with many direct subgroups under the `api.info` root and further generated leaves beneath several of those subgroups.
- Consistency checks across legacy and `vkGetPhysicalDeviceProperties2` reporting paths.
- Version-specific feature/property validation split into Vulkan 1.2, 1.3, and 1.4 branches.
- Platform-conditional registration for VulkanSC exclusions, Android-only checks, and subgroup-feature validation.

## Notes / Uncertainties

- The file is extremely large (over 8900 lines), and this normalization pass reverified the registration structure around [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635-L8921) rather than re-reading every underlying test implementation.
- The `createFeatureInfoInstanceTests`, `createFeatureInfoDeviceTests`, and `createFeatureInfoDeviceGroupTests` declarations in [vktApiFeatureInfo.hpp](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L35) refer to additional registration entry points defined in this source file but not attached under the `api.info` hierarchy documented here.
- The `pnext_format_properties` branch generates a very large second-level tree by iterating over many formats and per-format flag-combination cases in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8721-L8738), so those deeper descendants are intentionally described in prose rather than expanded in the canonical hierarchy block.
