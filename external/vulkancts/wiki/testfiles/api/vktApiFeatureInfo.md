# vktApiFeatureInfo.cpp

## Overview

[`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635) implements the early `api/info` subgroup registered by [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L96). Even within the early registration slice, this file is the broadest of the selected family: its top-level builder aggregates format-property checks, image-format and image-usage checks, extension-core-version checks, `vkGetPhysicalDevice*2`-style feature/property queries, Vulkan-version-specific feature/property consistency checks, limits validation, image-format-properties2 coverage, optional profile validation, Android-specific checks, and subgroup-feature validation.

Within this task, it is treated as a foundational early branch because it appears near the start of [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L90), but the file itself is not lightweight in implementation size.

## Role of File

Implementation-heavy test file for the `api/info` subgroup.

## Source Code

- Primary source: [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635)
- Related declarations: [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34)
- Parent-category registration: [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L96)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
└── api
    └── createTests(testCtx, "api")
        └── createApiTests(apiTests)
            └── createFeatureInfoTests(testCtx)
                └── info
                    ├── format_properties
                    ├── image_format_properties
                    ├── unsupported_image_usage
                    ├── extension_core_versions
                    ├── get_physical_device_properties2
                    ├── vulkan1p2
                    ├── vulkan1p3                       (not in Vulkan SC)
                    ├── vulkan1p4                       (not in Vulkan SC)
                    ├── vulkan1p2_limits_validation
                    ├── vulkan1p3_limits_validation
                    ├── vulkan1p4_limits_validation
                    ├── image_format_properties2
                    ├── sparse_image_format_properties2 (not in Vulkan SC)
                    ├── profiles                        (not in Vulkan SC)
                    ├── android
                    └── subgroup_features               (not in Vulkan SC)
```

Evidence:
- package-level `api` attachment in [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1349) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1417)
- subgroup attachment in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L96)
- top-level subgroup creation in [`createFeatureInfoTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635)

## Test Hierarchy

The top-level hierarchy confirmed from the inspected builder is:

```text
api
└── info
    ├── format_properties
    ├── image_format_properties
    ├── unsupported_image_usage
    ├── extension_core_versions
    ├── get_physical_device_properties2
    │   ├── features
    │   ├── properties
    │   ├── format_properties
    │   ├── queue_family_properties
    │   ├── memory_properties
    │   └── pnext_format_properties
    ├── vulkan1p2
    ├── vulkan1p3                       (excluded for Vulkan SC)
    ├── vulkan1p4                       (excluded for Vulkan SC)
    ├── vulkan1p2_limits_validation
    ├── vulkan1p3_limits_validation
    ├── vulkan1p4_limits_validation
    ├── image_format_properties2
    ├── sparse_image_format_properties2 (excluded for Vulkan SC)
    ├── profiles                        (excluded for Vulkan SC)
    ├── android
    └── subgroup_features               (excluded for Vulkan SC)
```

The inspected lines also show deeper content for some branches:

- [`get_physical_device_properties2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8654) contains a `features` subgroup plus separate one-case subgroups for `properties`, `format_properties`, `queue_family_properties`, and `memory_properties`, all created through [`addFunctionCaseInNewSubgroup()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8669)
- `pnext_format_properties` iterates from [`VK_FORMAT_UNDEFINED`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8683) up to [`VK_FORMAT_ASTC_12x12_SRGB_BLOCK`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8682), creating one subgroup per format and then multiple pNext-combination cases inside each format subgroup at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8731)

## Test Families

### 1. Format-property and image-format capability queries

The earliest top-level children in [`createFeatureInfoTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639) are:

- [`format_properties`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639), created with [`createFormatTests`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639)
- [`image_format_properties`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8641), created with [`createImageFormatTests`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8641)
- [`unsupported_image_usage`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8643), also built with [`createImageUsageTests`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8643)

These names support an evidence-backed characterization that the early `info` branch starts by validating format exposure and image capability reporting.

### 2. Extension/core-version relationship checks

[`extension_core_versions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8646) is a dedicated subgroup with a single registered case named the same at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8648), executed by [`extensionCoreVersions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8648). This appears to validate relationships between extensions and their core-version promotion state.

### 3. `get_physical_device_properties2` / pNext-based query coverage

[`get_physical_device_properties2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8654) is a substantial subtree. The inspected lines show:

- a `features` subgroup with a `core` case at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8658) plus additional “separate feature” cases from [`addSeparateFeatureTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8661)
- optional shader subgroup rotate consistency validation at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8663)
- one-case subgroups for properties, format properties, queue-family properties, and memory properties at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8669)
- a very broad `pnext_format_properties` subtree that combines formats with multiple pNext flag combinations at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8685)

### 4. Vulkan-version-specific feature/property consistency

Three sibling subgroups, [`vulkan1p2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8748), [`vulkan1p3`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8766), and [`vulkan1p4`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8782), register repeated families of cases named `features`, `properties`, `feature_extensions_consistency`, `property_extensions_consistency`, and `feature_bits_influence` at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8750), [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8768), and [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8784). This is a strong sign that the file validates consistency between versioned core features/properties and extension exposure.

### 5. Limits validation families

The builder creates three top-level validation groups:

- [`vulkan1p2_limits_validation`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8799)
- [`vulkan1p3_limits_validation`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8856)
- [`vulkan1p4_limits_validation`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8870)

The `vulkan1p2_limits_validation` branch alone registers many extension- or feature-specific cases such as [`khr_multiview`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8808), [`ext_descriptor_indexing`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8822), [`timeline_semaphore`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8844), and [`robustness2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8850).

### 6. Additional platform/profile/subgroup coverage

Later in the inspected builder, the file also adds:

- [`image_format_properties2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8880)
- optional [`sparse_image_format_properties2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8883)
- optional [`profiles`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8887), populated by iterating [`profileEntries`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8889)
- [`android`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8897), with `mandatory_extensions`, `no_unknown_extensions`, and `no_layers` at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8900)
- optional [`subgroup_features`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8913), containing a `flags` case at [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8915)

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Top-level subgroup names | `format_properties`, `image_format_properties`, `unsupported_image_usage`, `extension_core_versions`, `get_physical_device_properties2`, `vulkan1p2`, `vulkan1p3`, `vulkan1p4`, `vulkan1p2_limits_validation`, `vulkan1p3_limits_validation`, `vulkan1p4_limits_validation`, `image_format_properties2`, `sparse_image_format_properties2`, `profiles`, `android`, `subgroup_features` in [`createFeatureInfoTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635) |
| Vulkan version branches | 1.2 in [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8748), 1.3 in [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8766), 1.4 in [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8782) |
| pNext flag combinations for format-property tests | `PNEXT_DRM_FORMAT_MODIFIER_PROPERTIES_LIST`, `PNEXT_DRM_FORMAT_MODIFIER_PROPERTIES_LIST_2`, `PNEXT_FORMAT_PROPERTIES_3`, optional `PNEXT_SUBPASS_RESOLVE_PERFORMANCE_QUERY`, and several combinations in [`flagsCases`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8685) |
| Iterated format range in `pnext_format_properties` | incrementing from [`VK_FORMAT_UNDEFINED`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8683) until [`VK_FORMAT_ASTC_12x12_SRGB_BLOCK`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8682) |
| Android cases | `mandatory_extensions`, `no_unknown_extensions`, `no_layers` in [`androidTests`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8897) |
| Profiles population | one function case per entry in [`profileEntries`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8889) |
| Limits-validation case variety | general, KHR, EXT, NV, and robustness/timeline/line-rasterization families visible in [`vulkan1p2_limits_validation`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802) |

## Support / Feature Requirements

Observed support logic is extensive and mostly delegated per case:

- versioned `feature_bits_influence` and some limits/subgroup cases use explicit API-version gates via [`checkApiVersionSupport<1, 2>`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8757), [`checkApiVersionSupport<1, 3>`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8775), and [`checkApiVersionSupport<1, 4>`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8791)
- many limits-validation cases use extension-specific support checks such as [`checkSupportKhrMultiview`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8808), [`checkSupportExtDescriptorIndexing`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8822), and [`checkSupportRobustness2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8850)
- several subgroups/cases are compiled out for Vulkan SC via [`#ifndef CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8763), including `vulkan1p3`, `vulkan1p4`, `sparse_image_format_properties2`, `profiles`, and `subgroup_features`
- some cases use templated registration wrappers such as [`CustomInstanceTest<E060>`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8660) and [`CustomInstanceWithSupportTest<E060>`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8663); the exact meaning of `E060` is not established from the inspected lines, so no stronger claim is made about it here

## Verification Methods

The inspected top-level builder mostly exposes registration rather than all underlying implementations, so only high-confidence verification summaries are made:

- **enumeration/query-based validation** is strongly suggested by names such as [`deviceProperties2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8669), [`deviceMemoryProperties2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8674), and the various `image_format_properties*` groups
- **consistency validation** is explicit in case names such as [`feature_extensions_consistency`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8753), [`property_extensions_consistency`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8755), and [`shader_subgroup_rotate_property_consistency_khr`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8664)
- **limits-threshold validation** is explicit from the `*_limits_validation` group names and their delegated functions such as [`validateLimits12`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802) and [`validateLimitsRobustness2`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8850)
- **per-format combinatorial validation** is explicit from the nested loops creating one format subgroup and many pNext combinations in [`pnext_format_properties`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8721)

The exact pass/fail criteria of every delegated helper are not fully reconstructable from this inspected registration slice alone.

## Test Principles Observed

- **Use one large information-oriented subtree to aggregate many API-query themes**: `info` groups together format, property, feature, version, limit, profile, Android, and subgroup reporting/validation
- **Scale coverage through generated hierarchies**: `pnext_format_properties` uses loops over formats and pNext combinations rather than hand-written cases
- **Track Vulkan evolution explicitly**: separate `vulkan1p2`, `vulkan1p3`, and `vulkan1p4` groups mirror versioned feature/property surfaces
- **Mix generic query checks with platform-specific policy checks**: the same file contains both broad Vulkan property coverage and Android-specific policy validation
- **Use compile-time guards to shape package variants**: several branches disappear in Vulkan SC builds, so the tree differs by build target

## Notes / Uncertainties

- This document intentionally summarizes the top-level and near-top-level structure visible in the inspected registration slice around [`createFeatureInfoTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8635). It does not claim complete per-case internal verification details for every helper function in this large file.
- Because the file is large, additional shared helpers defined far earlier in the file may materially influence behavior; those details are only mentioned when directly evidenced by the inspected lines.
- The subgroup is named `info` in code at [`createFeatureInfoTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8637), even though the source file is named `vktApiFeatureInfo.cpp`; this document follows the code-visible subgroup name.
