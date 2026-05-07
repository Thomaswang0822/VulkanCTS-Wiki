# [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1)

## Overview

Tests VK_KHR_maintenance5 behavior for `vkGetPhysicalDevice*FormatProperties*` API functions when called with unsupported format values or unsupported image usage flag values. Verifies that implementations return zeroed/empty properties for invalid parameters rather than writing garbage.

## Role of File

Implementation-heavy. Contains test instance classes, test case class, and registration logic.

## Source Code

| File | Description |
|------|-------------|
| [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1) | Test implementation and registration |
| [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.hpp](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.hpp#L1) | Declares `createMaintenance5Tests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L133) | Parent registration: `apiTests->addChild(createMaintenance5Tests(testCtx))` |

## Registration Path

```
api
  +-- maintenance5
       +-- format
       |    +-- device_format_props
       |    +-- device_format_props2
       |    +-- image_format_props
       |    +-- image_format_props2
       |    +-- sparse_image_format_props
       |    +-- sparse_image_format_props2
       +-- flags
            +-- image_format_props
            +-- image_format_props2
            +-- sparse_image_format_props
            +-- sparse_image_format_props2
```

## Test Hierarchy

```
maintenance5
  +-- format
  |    Tests with VK_FORMAT_MAX_ENUM - i for i in [0..4]
  |    +-- device_format_props        -> getPhysicalDeviceFormatProperties
  |    +-- device_format_props2       -> getPhysicalDeviceFormatProperties2
  |    +-- image_format_props         -> getPhysicalDeviceImageFormatProperties
  |    +-- image_format_props2        -> getPhysicalDeviceImageFormatProperties2
  |    +-- sparse_image_format_props  -> getPhysicalDeviceSparseImageFormatProperties
  |    +-- sparse_image_format_props2 -> getPhysicalDeviceSparseImageFormatProperties2
  +-- flags
       Tests with VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i for i in [0..4]
       +-- image_format_props         -> getPhysicalDeviceImageFormatProperties
       +-- image_format_props2        -> getPhysicalDeviceImageFormatProperties2
       +-- sparse_image_format_props  -> getPhysicalDeviceSparseImageFormatProperties
       +-- sparse_image_format_props2 -> getPhysicalDeviceSparseImageFormatProperties2
```

## Test Families

### maintenance5

Group name verified at [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp:345](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L345): `new tcu::TestCaseGroup(testCtx, "maintenance5")`.

The `format` subgroup tests use `UnsupportedParametersMaintenance5FormatInstance` ([line 60](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L60)). For each of 5 invalid format values near `VK_FORMAT_MAX_ENUM`, it:
1. Pre-fills the output structure with 0xFF bytes via `makeInvalidVulkanStructure` ([line 138](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L138))
2. Calls the format properties query function
3. Verifies the output is either zeroed or still contains the 0xFF pattern (indicating the implementation did not write to it) ([lines 196-237](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L196))

The `flags` subgroup tests use `UnsupportedParametersMaintenance5FlagsInstance` ([line 75](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L75)). For each of 5 invalid usage flag values near `VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM`, it performs similar verification ([lines 245-331](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L245)).

The function-to-test-case mapping is defined at [lines 337-343](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L337):

| Test Name | FuncIDs | API Function |
|-----------|---------|-------------|
| `device_format_props` | DeviceFormatProps | getPhysicalDeviceFormatProperties |
| `device_format_props2` | DeviceFormatPropsSecond | getPhysicalDeviceFormatProperties2 |
| `image_format_props` | DeviceImageFormatProps | getPhysicalDeviceImageFormatProperties |
| `image_format_props2` | DeviceImageFormatPropsSecond | getPhysicalDeviceImageFormatProperties2 |
| `sparse_image_format_props` | DeviceSparseImageFormatProps | getPhysicalDeviceSparseImageFormatProperties |
| `sparse_image_format_props2` | DeviceSparseImageFormatPropsSecond | getPhysicalDeviceSparseImageFormatProperties2 |

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Format values | VK_FORMAT_MAX_ENUM - i for i in [0..4] | 5 invalid format values |
| Usage flags | VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i for i in [0..4] | 5 invalid flag values |
| API function | 6 variants | 3 function pairs (format, image format, sparse), each with and without "2" suffix |
| Image type | VK_IMAGE_TYPE_2D | Hard-coded |
| Tiling | VK_IMAGE_TILING_OPTIMAL | Hard-coded |

## Support / Feature Requirements

- `VK_KHR_maintenance5` required via `checkSupport` at [line 118](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L118)
- `maintenance5` feature must be VK_TRUE ([line 119](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L119))

## Verification Methods

- **Output structure validation**: Pre-fills output structures with 0xFF, calls the API, then checks that the output is either zeroed or unchanged from the 0xFF pattern. For format tests, `VkFormatProperties` must be empty or invalid ([line 196](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L196)). For sparse format tests, the count must be 0 ([line 223](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L223)).
- **Sparse flag tolerance**: For sparse image format tests with invalid flags, the test always passes because "some implementations ignore wrong flags" ([lines 307-308](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L307)).

## Test Principles Observed

- Robustness testing: verifies implementation behavior with invalid parameters
- Maintenance5 specification compliance: checks that unsupported parameters yield zeroed output

## Notes / Uncertainties

- The sparse image format tests with invalid flags always pass regardless of output, which reduces their effectiveness as conformance tests
- The test uses `VK_FORMAT_R8G8B8A8_UNORM` as the valid format for flags tests but invalid formats near `VK_FORMAT_MAX_ENUM` for format tests
- The `HAS_FORMAT_PARAM` and `HAS_FLAGS_PARAM` bit flags at [lines 43-44](../../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L43) determine which subgroup each test case is added to
