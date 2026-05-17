# [vktApiToolingInfoTests.cpp](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1)

## Overview

Tests the VK_EXT_tooling_info extension, validating that `vkGetPhysicalDeviceToolProperties` correctly enumerates active Vulkan tools and returns valid property structures. Verifies getter behavior with various array sizes and validates tool property fields.

## Role of File

Implementation-heavy. Contains all test logic and registration. The public entry point [createToolingInfoTests()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L258) assembles the test tree.

## Source Code

- Source: [vktApiToolingInfoTests.cpp](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1)
- Header: [vktApiToolingInfoTests.hpp](../../../modules/vulkan/api/vktApiToolingInfoTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L124) adds `tooling_info` group to `api`

## Registration Hierarchy

```text
api.tooling_info
├── validate_getter
└── validate_tools_properties
```

## Test Families

### validate_getter

Tests the `vkGetPhysicalDeviceToolProperties` getter behavior with various array sizes. Verifies: (1) two-pass query returns consistent tool counts, (2) larger-than-needed array returns `VK_SUCCESS` with correct count, (3) zero-size array returns `VK_INCOMPLETE` with count 0, (4) half-size array returns `VK_INCOMPLETE` with the partial count. Implemented by [validateGetter()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L61).

### validate_tools_properties

Validates the content of each returned `VkPhysicalDeviceToolPropertiesEXT` structure. Checks: (1) `sType` is `VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TOOL_PROPERTIES_EXT`, (2) `purposes` flags are valid bits, (3) `name` is non-empty and within `VK_MAX_EXTENSION_NAME_SIZE`, (4) `version` is non-empty and within `VK_MAX_EXTENSION_NAME_SIZE`, (5) `description` is non-empty and within `VK_MAX_DESCRIPTION_SIZE`, (6) `layer` is either empty or within `VK_MAX_EXTENSION_NAME_SIZE`. Implemented by [validateToolsProperties()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L181).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Test | validate_getter, validate_tools_properties |

This file has minimal parameterization -- only two test cases.

## Support / Feature Requirements

- `VK_EXT_tooling_info` required by all tests ([checkSupport()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L56))

## Verification Methods

- Getter validation: Verifies return codes (`VK_SUCCESS`, `VK_INCOMPLETE`) and count consistency across different array sizes ([validateGetter()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L61))
- Tool property validation: Validates each field of `VkPhysicalDeviceToolPropertiesEXT` against spec constraints using [validateToolPurposeFlagBits()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L47) and string length checks

## Test Principles Observed

- Two-pass query pattern (count then retrieve) is the standard Vulkan enumeration idiom
- Edge case testing with zero-size and half-size arrays
- Validation of all struct fields against spec limits

## Notes / Uncertainties

- The group name is `tooling_info` as confirmed in [createToolingInfoTests()](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L260)
- Tests that require active tools will pass trivially if no tools are present (toolCount == 0), since the validation loop is skipped
- The `validate_getter` test with zero-size array expects `VK_INCOMPLETE` and count 0, which tests a corner case of the enumeration protocol
