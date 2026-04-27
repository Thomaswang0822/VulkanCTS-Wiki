# [vktApiFormatPropertiesExtendedKHRtests.cpp](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1)

## Overview

Tests the VK_KHR_format_feature_flags2 extension, verifying that `VkFormatProperties3` reported by the implementation includes all required format feature flags for every core Vulkan format. Compares implementation-reported flags against the CTS-required feature set.

## Role of File

Implementation-heavy. Contains all test logic and registration. The public entry point [createFormatPropertiesExtendedKHRTests()](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90) assembles the test tree.

## Source Code

- Source: [vktApiFormatPropertiesExtendedKHRtests.cpp](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1)
- Header: [vktApiFormatPropertiesExtendedKHRtests.hpp](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L125) adds `format_feature_flags2` group to `api`

## Registration Path

```
api
 +-- format_feature_flags2
      +-- <format_name>          (one test per core Vulkan format)
```

## Test Hierarchy

```
format_feature_flags2
 +-- r4g4_unorm_pack8
 +-- r4g4b4a4_unorm_pack16
 +-- ...                         (one test per core format from VK_FORMAT_R4G4_UNORM_PACK8 to VK_CORE_FORMAT_LAST)
 +-- e5b9g9r9_ufloat_pack32
```

## Test Families

### Per-format tests

For each core Vulkan format (from `VK_FORMAT_R4G4_UNORM_PACK8` to `VK_CORE_FORMAT_LAST`), queries `VkFormatProperties3` via `context.getFormatProperties()` and `context.getRequiredFormatProperties()`, then verifies that the implementation's reported flags are a superset of the required flags. Checks three flag sets: `bufferFeatures`, `linearTilingFeatures`, and `optimalTilingFeatures`. Implemented by [test()](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L59).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Format | All core Vulkan formats from VK_FORMAT_R4G4_UNORM_PACK8 to VK_CORE_FORMAT_LAST |

## Support / Feature Requirements

- `VK_KHR_format_feature_flags2` required by all tests ([checkSupport()](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L39))
- `VK_KHR_get_physical_device_properties2` required by all tests ([checkSupport()](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L43))

## Verification Methods

- Flag superset check: For each format, verifies that `(reportedFlags & requiredFlags) == requiredFlags` for each of the three feature flag sets. If any required bits are missing, the test fails with a message identifying the missing bits. Implemented by [checkFlags()](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46).

## Test Principles Observed

- Exhaustive format coverage: every core Vulkan format is tested
- Required-feature validation: implementation must support at least the features CTS deems required
- Clear failure diagnostics: missing flag bits are reported in hex

## Notes / Uncertainties

- The group name is `format_feature_flags2` as confirmed in [createFormatPropertiesExtendedKHRTests()](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L92), not `format_properties_extended_khr`
- The test name for each format is derived by stripping the `VK_FORMAT_` prefix and converting to lowercase ([L78](../../../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L78))
- The required format properties come from `context.getRequiredFormatProperties()` which is a CTS-maintained database of minimum required features per format
- The test only checks that required flags are present; it does not validate that unsupported flags are absent
