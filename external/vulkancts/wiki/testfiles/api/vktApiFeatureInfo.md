# [vktApiFeatureInfo.cpp](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1)

## Overview

[`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1) implements the `api/info` subgroup registered by [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L96). The file is extremely large and covers querying and validating physical device features, properties, format properties, image format properties, extension core versions, extended properties via `vkGetPhysicalDeviceProperties2`, Vulkan 1.2/1.3/1.4 feature/property consistency, limits validation, and platform-specific tests (Android, subgroup features, profiles).

## Role of File

Implementation-heavy test file for the `api/info` subgroup.

## Source Code

- Primary source: [vktApiFeatureInfo.cpp](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1)
- Header: [vktApiFeatureInfo.hpp](../../../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L96)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createFeatureInfoTests(testCtx)
          +-- info
              +-- format_properties/
              +-- image_format_properties/
              +-- unsupported_image_usage/
              +-- extension_core_versions/
              +-- get_physical_device_properties2/
              +-- vulkan1p2/
              +-- vulkan1p3/  (not in Vulkan SC)
              +-- vulkan1p4/  (not in Vulkan SC)
              +-- vulkan1p2_limits_validation/
              +-- vulkan1p3_limits_validation/
              +-- vulkan1p4_limits_validation/
              +-- image_format_properties2/
              +-- sparse_image_format_properties2/  (not in Vulkan SC)
              +-- profiles/  (not in Vulkan SC)
              +-- android/
              +-- subgroup_features/  (not in Vulkan SC)
```

Evidence:
- `info` group created at [`createFeatureInfoTests()`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8637)
- subgroups added from [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639) through [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8918)

## Test Hierarchy

```text
api
+-- info
    +-- format_properties/
    +-- image_format_properties/
    +-- unsupported_image_usage/
    +-- extension_core_versions/
        +-- extension_core_versions
    +-- get_physical_device_properties2/
        +-- features/
            +-- core
            +-- (per-feature subcases)
            +-- shader_subgroup_rotate_property_consistency_khr  (not in Vulkan SC)
        +-- properties
        +-- format_properties
        +-- queue_family_properties
        +-- memory_properties
        +-- pnext_format_properties/
            +-- (per-format groups with drm_format_mod_1, drm_format_mod_2, format_props_3, ...)
    +-- vulkan1p2/
        +-- features
        +-- properties
        +-- feature_extensions_consistency
        +-- property_extensions_consistency
        +-- feature_bits_influence
    +-- vulkan1p3/  (excluded for Vulkan SC)
        +-- features
        +-- properties
        +-- feature_extensions_consistency
        +-- property_extensions_consistency
        +-- feature_bits_influence
    +-- vulkan1p4/  (excluded for Vulkan SC)
        +-- features
        +-- properties
        +-- feature_extensions_consistency
        +-- property_extensions_consistency
        +-- feature_bits_influence
    +-- vulkan1p2_limits_validation/
        +-- general
        +-- khr_push_descriptor  (not in Vulkan SC)
        +-- khr_multiview
        +-- ext_discard_rectangles
        +-- ext_sample_locations
        +-- ext_external_memory_host
        +-- ext_blend_operation_advanced
        +-- khr_maintenance_3
        +-- ext_conservative_rasterization
        +-- ext_descriptor_indexing
        +-- ext_inline_uniform_block  (not in Vulkan SC)
        +-- ext_vertex_attribute_divisor  (not in Vulkan SC)
        +-- khr_vertex_attribute_divisor
        +-- nv_mesh_shader  (not in Vulkan SC)
        +-- ext_transform_feedback  (not in Vulkan SC)
        +-- fragment_density_map  (not in Vulkan SC)
        +-- nv_ray_tracing  (not in Vulkan SC)
        +-- timeline_semaphore
        +-- ext_line_rasterization
        +-- khr_line_rasterization
        +-- robustness2
    +-- vulkan1p3_limits_validation/
        +-- khr_maintenance4  (not in Vulkan SC)
        +-- max_inline_uniform_total_size  (not in Vulkan SC)
    +-- vulkan1p4_limits_validation/
        +-- general  (not in Vulkan SC)
    +-- image_format_properties2/
    +-- sparse_image_format_properties2/  (excluded for Vulkan SC)
    +-- profiles/  (excluded for Vulkan SC)
    +-- android/
        +-- mandatory_extensions
        +-- no_unknown_extensions
        +-- no_layers
    +-- subgroup_features/  (excluded for Vulkan SC)
        +-- flags
```

Source: [`createFeatureInfoTests()`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635).

## Test Families

### 1. Format property queries

The `format_properties` subgroup at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639) tests `vkGetPhysicalDeviceFormatProperties`. The `image_format_properties` subgroup at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8640) tests `vkGetPhysicalDeviceImageFormatProperties`. The `unsupported_image_usage` subgroup at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8642) tests that drivers do not expose unsupported image usage flags.

### 2. Extension core versions

The `extension_core_versions` subgroup at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8646) tests that extensions promoted to core are properly reported.

### 3. Extended physical device properties

The `get_physical_device_properties2` subgroup at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8654) tests `vkGetPhysicalDeviceProperties2` and its sub-queries:
- `features` subgroup at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8658): extended device features
- `properties`, `format_properties`, `queue_family_properties`, `memory_properties` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8669)
- `pnext_format_properties` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8678): tests `pNext` chains with DRM format modifier, format properties 3, and subpass resolve performance query structures

### 4. Vulkan version-specific feature/property consistency

Three version-specific subgroups validate feature and property consistency between core and extension reporting:
- `vulkan1p2` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8748)
- `vulkan1p3` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8766) (excluded for Vulkan SC)
- `vulkan1p4` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8782) (excluded for Vulkan SC)

Each contains: `features`, `properties`, `feature_extensions_consistency`, `property_extensions_consistency`, and `feature_bits_influence`.

### 5. Limits validation

Three limits-validation subgroups at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8798):
- `vulkan1p2_limits_validation`: validates limits for Vulkan 1.2 and related extensions
- `vulkan1p3_limits_validation`: validates limits for Vulkan 1.3 extensions
- `vulkan1p4_limits_validation`: validates limits for Vulkan 1.4

### 6. Platform-specific and auxiliary tests

- `android` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8897): Android-specific mandatory extension and layer tests
- `subgroup_features` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8913): subgroup feature flag validation (excluded for Vulkan SC)
- `profiles` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8887): profile validation (excluded for Vulkan SC)

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Format range | `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST` in format property tests |
| pNext flag combinations | `PNEXT_DRM_FORMAT_MODIFIER_PROPERTIES_LIST`, `PNEXT_DRM_FORMAT_MODIFIER_PROPERTIES_LIST_2`, `PNEXT_FORMAT_PROPERTIES_3`, `PNEXT_SUBPASS_RESOLVE_PERFORMANCE_QUERY` and their combinations at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8690) |
| Vulkan versions | 1.2, 1.3, 1.4 at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8748) |
| Extension-specific limits | khr_push_descriptor, khr_multiview, ext_discard_rectangles, ext_sample_locations, ext_external_memory_host, ext_blend_operation_advanced, khr_maintenance_3, ext_conservative_rasterization, ext_descriptor_indexing, ext_inline_uniform_block, ext_vertex_attribute_divisor, khr_vertex_attribute_divisor, nv_mesh_shader, ext_transform_feedback, fragment_density_map, nv_ray_tracing, timeline_semaphore, ext_line_rasterization, khr_line_rasterization, robustness2 at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802) |

## Support / Feature Requirements

- version-specific tests use `checkApiVersionSupport<1, N>` support gates at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8757)
- extension-specific limits tests use dedicated support check functions (e.g., `checkSupportKhrPushDescriptor`, `checkSupportExtDiscardRectangles`) at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802)
- `shader_subgroup_rotate_property_consistency_khr` requires `VK_KHR_shader_subgroup_rotate` via `checkSupportKhrShaderSubgroupRotate` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8664)
- Android tests use `android::checkSupportAndroid` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8900)
- subgroup features test requires Vulkan 1.4 via `checkApiVersionSupport<1, 4>` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8915)

## Verification Methods

- format property tests verify that mandatory format features are supported
- feature/property consistency tests compare core and extension-reported values for equality
- limits validation tests verify that reported limits meet minimum requirements
- `feature_bits_influence` tests verify that enabling feature bits affects device creation behavior

## Test Principles Observed

- Systematic format and feature coverage across Vulkan versions
- Consistency checks between core and extension reporting paths
- Limits validation against spec-mandated minimums
- Platform-specific requirements enforced through dedicated support gates

## Notes / Uncertainties

- The file is extremely large (over 8900 lines); only the registration function was fully inspected. The individual test function implementations were not read in detail.
- The `createFeatureInfoInstanceTests`, `createFeatureInfoDeviceTests`, and `createFeatureInfoDeviceGroupTests` functions declared in the header at [`vktApiFeatureInfo.hpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L35) are defined in this file but are called from elsewhere (not from `createFeatureInfoTests`); their registration path is not shown in this document.
- The `pnext_format_properties` subgroup iterates over all formats from `VK_FORMAT_UNDEFINED + 1` through `VK_FORMAT_ASTC_12x12_SRGB_BLOCK` at [`vktApiFeatureInfo.cpp`](../../../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8722), generating a large number of per-format test groups.
