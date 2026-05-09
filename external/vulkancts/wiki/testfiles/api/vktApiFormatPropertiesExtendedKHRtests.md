# [vktApiFormatPropertiesExtendedKHRtests.cpp](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1)

## Overview

Tests the `VK_KHR_format_feature_flags2` extension by verifying that `VkFormatProperties3` reported by the implementation contains every format feature bit required by CTS for each core Vulkan format. The file compares implementation-reported flags against CTS-required properties for buffer, linear-tiling, and optimal-tiling usage.

## Role of File

Implementation-heavy Level-3 page for the top-level `api.format_feature_flags2` subgroup. The local registration entry point [createFormatPropertiesExtendedKHRTests()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93) creates the subgroup and registers one generated leaf test per core Vulkan format via [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80).

## Source Code

- Implementation: [vktApiFormatPropertiesExtendedKHRtests.cpp](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1)
- Header: [vktApiFormatPropertiesExtendedKHRtests.hpp](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.hpp#L1)
- Parent registration: [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126)
- Local subgroup registration: [createFormatPropertiesExtendedKHRTests()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93)

## Registration Hierarchy

```text
api.format_feature_flags2
```

The confirmed Level-3 root is `format_feature_flags2`, which [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126) adds directly under `api`. [createFormatPropertiesExtendedKHRTests()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93) creates that group and delegates directly to [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80), which registers generated leaf tests with `addFunctionCase()` instead of creating any direct child subgroups. This page therefore has no registered one-level-down subgroup children to expand in the canonical hierarchy tree.

## Test Families

This file does not register direct child subgroup branches under `api.format_feature_flags2`. Instead, it generates one leaf test per core Vulkan format inside the root group through the loop in [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80). Each generated case uses the lowercase format name derived from `getFormatName()` after stripping the `VK_FORMAT_` prefix in [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L78).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registration root | `api.format_feature_flags2` from [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126) and [createFormatPropertiesExtendedKHRTests()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93) |
| Direct child subgroup names | None observed; [createFormatPropertiesExtendedKHRTests()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93) installs a callback that registers leaves directly through `addFunctionCase()` in [vktApiFormatPropertiesExtendedKHRtests.cpp](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L79) |
| Format enumeration range | All core Vulkan formats from `VK_FORMAT_R4G4_UNORM_PACK8` up to but not including `VK_CORE_FORMAT_LAST` in [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L75-L76) |
| Generated test name | Lowercase `getFormatName(format)` with the leading `VK_FORMAT_` removed in [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L78) |
| Checked feature sets | `bufferFeatures`, `linearTilingFeatures`, and `optimalTilingFeatures` in [test()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L61-L68) |

## Support / Feature Requirements

- All generated cases require `VK_KHR_format_feature_flags2` through [checkSupport()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L39-L44).
- All generated cases also require `VK_KHR_get_physical_device_properties2` through [checkSupport()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L39-L44).

## Verification Methods

- [test()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L59-L70) obtains implementation-reported properties with `context.getFormatProperties()` and CTS-required properties with `context.getRequiredFormatProperties()`.
- For each of the three feature sets, [checkFlags()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) verifies that `(reportedFlags & requestedFlags) == requestedFlags` and fails if any required bits are missing.
- Failure diagnostics are explicit: [checkFlags()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L51-L55) computes the missing mask and prints it in hexadecimal together with the affected feature-set label.

## Test Principles Observed

- Exhaustive coverage over the core-format enum interval visible in [createTestCases()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L75-L80).
- CTS validates minimum required capability, not exact equality, by using a superset check in [checkFlags()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57).
- The same verification logic is reused for buffer, linear-tiling, and optimal-tiling feature-bit sets in [test()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L64-L68).

## Notes / Uncertainties

- The registered subgroup name is `format_feature_flags2`, as shown in [createFormatPropertiesExtendedKHRTests()](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93), not a symbol-derived variant such as `format_properties_extended_khr`.
- Observed registration is leaf-only below `api.format_feature_flags2`: inspected code does not create any direct child subgroup names beneath the Level-3 root.
- The required property database consumed by `context.getRequiredFormatProperties()` is used as a CTS-maintained source of mandatory feature bits, but this file alone does not expose where that database is populated.
- The test only verifies that required bits are present; inspected code does not check whether extra reported bits should be absent.
