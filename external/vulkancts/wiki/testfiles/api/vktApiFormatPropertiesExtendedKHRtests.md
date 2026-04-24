# [vktApiFormatPropertiesExtendedKHRtests.cpp](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1)

## Overview

Tests for the `VK_KHR_format_feature_flags2` extension, which extends format property reporting with 64-bit feature flags (`VkFormatProperties3`). The file iterates over all core Vulkan formats and verifies that the reported format properties are a superset of the required format properties mandated by the Vulkan specification.

## Role of File

Implementation-heavy. Contains the test logic, support check, and registration function. Uses a free-function test pattern via `addFunctionCase` with a per-format parameter.

## Source Code

| File | Path |
|------|------|
| Source | [vktApiFormatPropertiesExtendedKHRtests.cpp](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1) |
| Header | [vktApiFormatPropertiesExtendedKHRtests.hpp](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.hpp#L1) |
| Parent registration | [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L125) |

## Registration Path

```
api
└── format_properties_extended_khr    (non-VKSC only, vktApiTests.cpp#L125)
    └── format_feature_flags2         (createFormatPropertiesExtendedKHRTests, line 92)
        ├── r4g4_unorm_pack8
        ├── r4g4b4a4_unorm_pack16
        ├── ... (one test per core VkFormat)
        └── ... (up to VK_CORE_FORMAT_LAST)
```

## Test Hierarchy

```
format_feature_flags2
├── r4g4_unorm_pack8
├── r4g4b4a4_unorm_pack16
├── b4g4r4a4_unorm_pack16
├── r5g6b5_unorm_pack16
├── ... (iterates VK_FORMAT_R4G4_UNORM_PACK8 through VK_CORE_FORMAT_LAST-1)
```

## Test Families

### format_feature_flags2 (per-format tests)

For each core Vulkan format from `VK_FORMAT_R4G4_UNORM_PACK8` up to `VK_CORE_FORMAT_LAST`, a test case is created with the format name (lowercased, without the `VK_FORMAT_` prefix) as the test name ([line 73-81](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73)). Each test:

1. Retrieves the format's `VkFormatProperties3` via `context.getFormatProperties()` ([line 61](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L61)).
2. Retrieves the required format properties via `context.getRequiredFormatProperties()` ([line 62](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L62)).
3. Verifies that each of the three property sets (bufferFeatures, linearTilingFeatures, optimalTilingFeatures) reported by the implementation is a superset of the required flags ([line 64-68](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L64)).

The `checkFlags` helper function computes the bitwise AND of reported and required flags, and fails with `TCU_FAIL` if any required bits are missing, reporting the missing bits in hexadecimal ([line 46-57](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46)).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| VkFormat | VK_FORMAT_R4G4_UNORM_PACK8 through VK_CORE_FORMAT_LAST-1 | [line 75-76](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L75) |
| Property set | bufferFeatures, linearTilingFeatures, optimalTilingFeatures | [line 64-68](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L64) |

## Support / Feature Requirements

| Requirement | Source |
|-------------|--------|
| VK_KHR_format_feature_flags2 | [line 42](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L42) |
| VK_KHR_get_physical_device_properties2 | [line 43](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L43) |

## Verification Methods

- **Bitwise superset check**: For each of the three format property categories, the test verifies `(reportedFlags & requiredFlags) == requiredFlags`. If any required bit is not present in the reported flags, the test fails with a message indicating which bits are missing ([line 46-57](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46)).
- **Hard failure**: Uses `TCU_FAIL` on mismatch rather than a soft check, meaning any missing required feature flag causes an immediate test failure ([line 55](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L55)).

## Test Principles Observed

- **Comprehensive format coverage**: Iterates over all core Vulkan formats rather than testing a subset ([line 75-76](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L75)).
- **Specification-backed requirements**: Uses `getRequiredFormatProperties()` which provides the minimum feature flags the Vulkan specification mandates for each format, ensuring the test is evidence-backed against the spec.
- **Clear failure diagnostics**: Reports missing bits in hexadecimal with the property set name, enabling quick identification of which feature flag is absent ([line 53-55](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L53)).

## Notes / Uncertainties

- The `getFormatProperties()` and `getRequiredFormatProperties()` methods on `Context` are not defined in this file; they are part of the CTS framework. The exact mechanism by which required properties are determined is external to this test file.
- `VK_CORE_FORMAT_LAST` is a framework-defined constant, not a standard Vulkan enum value. Its exact value depends on the Vulkan headers version used in the build.
- The `checkSupport` function receives the `VkFormat` parameter but does not use it ([line 41](../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L41)); the extension requirements are format-independent.
- This test only verifies that reported properties are a superset of required properties. It does not check that the implementation does not report unsupported feature flags (i.e., there is no upper-bound check).
