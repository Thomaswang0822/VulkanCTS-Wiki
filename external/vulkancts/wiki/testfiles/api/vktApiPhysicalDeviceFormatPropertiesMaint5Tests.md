# [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1)

## Overview

Tests the VK_KHR_maintenance5 extension behavior for unsupported parameters in vkGetPhysicalDevice*FormatProperties* API functions. Verifies that when invalid VkFormat values or invalid VkImageUsageFlags are passed, the implementation returns zeroed or unchanged output structures as mandated by the maintenance5 specification.

## Role of File

Implementation-heavy. Contains two test instance classes (format-based and flags-based), a shared test case class, helper functions, and the registration entry point.

## Source Code

- Implementation: [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L1)
- Header: [vktApiPhysicalDeviceFormatPropertiesMaint5Tests.hpp](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.hpp#L1)
- Registration function: [createMaintenance5Tests()](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L335)
- Registered under: api -> maintenance5 (non-VKSC only)

## Registration Path

```
api
+-- maintenance5
    +-- maintenance5
```

## Test Hierarchy

```
maintenance5
+-- format
|   +-- device_format_props
|   +-- device_format_props2
|   +-- image_format_props
|   +-- image_format_props2
|   +-- sparse_image_format_props
|   +-- sparse_image_format_props2
+-- flags
    +-- image_format_props
    +-- image_format_props2
    +-- sparse_image_format_props
    +-- sparse_image_format_props2
```

## Test Families

### format (group)

Tests that passing 5 invalid VkFormat values (VK_FORMAT_MAX_ENUM - i for i in 0..4) to the six vkGetPhysicalDevice*FormatProperties* functions results in either zeroed output structures or the output structures remaining unchanged from their pre-filled invalid sentinel values. This validates the maintenance5 requirement that implementations must not write garbage to output structures for unsupported formats.

- Instance: [UnsupportedParametersMaintenance5FormatInstance](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L60)
- iterate(): [L147-L243](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L147)
- Test functions covered:
  - getPhysicalDeviceFormatProperties ([L193-L196](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L193))
  - getPhysicalDeviceFormatProperties2 ([L199-L202](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L199))
  - getPhysicalDeviceImageFormatProperties ([L205-L209](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L205))
  - getPhysicalDeviceImageFormatProperties2 ([L213-L216](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L213))
  - getPhysicalDeviceSparseImageFormatProperties ([L219-L223](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L219))
  - getPhysicalDeviceSparseImageFormatProperties2 ([L226-L230](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L226))

### flags (group)

Tests that passing 5 invalid VkImageUsageFlags values (VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i for i in 0..4) to the image and sparse image format properties functions results in zeroed or unchanged output structures. Uses VK_FORMAT_R8G8B8A8_UNORM as the format. For sparse image format functions, the verdict is always true because some implementations ignore invalid flags.

- Instance: [UnsupportedParametersMaintenance5FlagsInstance](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L75)
- iterate(): [L245-L331](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L245)
- Test functions covered:
  - getPhysicalDeviceImageFormatProperties ([L287-L291](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L287))
  - getPhysicalDeviceImageFormatProperties2 ([L294-L298](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L294))
  - getPhysicalDeviceSparseImageFormatProperties (always passes; [L301-L308](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L301))
  - getPhysicalDeviceSparseImageFormatProperties2 (always passes; [L311-L318](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L311))

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|---|---|---|
| funcID | DeviceFormatProps, DeviceFormatPropsSecond, DeviceImageFormatProps, DeviceImageFormatPropsSecond, DeviceSparseImageFormatProps, DeviceSparseImageFormatPropsSecond | 6 function IDs at [L337-L343](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L337) |
| testFormatOrFlags | true (format group), false (flags group) | Determines which instance class to use; [L111-L113](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L111) |
| invalid format iteration | VK_FORMAT_MAX_ENUM - i, i in 0..4 | 5 iterations at [L189](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L189) |
| invalid flags iteration | VK_IMAGE_USAGE_FLAG_BITS_MAX_ENUM - i, i in 0..4 | 5 iterations at [L283](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L283) |

## Support / Feature Requirements

| Requirement | Where | Context |
|---|---|---|
| VK_KHR_maintenance5 | [L118](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L118) | All tests |
| maintenance5 feature == VK_TRUE | [L119-L122](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L119) | All tests |

## Verification Methods

- **Sentinel pre-fill**: Pre-fills output structures with 0xFF via [makeInvalidVulkanStructure()](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L138), then checks that after the API call the output is either zeroed or still contains the sentinel ([L196](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L196), [L209](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L209))
- **Empty-or-unchanged check**: Verdict is true if output equals emptyProps or invalidProps (the sentinel), meaning the implementation either zeroed the output or left it untouched ([L196](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L196))
- **Sparse count check**: For sparse image format functions, verifies that propsCount is 0 for invalid formats ([L222-L223](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L222))
- **All-true verdict**: Pass requires all 5 iterations to return true AND the final res to be VK_ERROR_FORMAT_NOT_SUPPORTED ([L239-L242](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L239))

## Test Principles Observed

- **Sentinel pre-fill**: Uses 0xFF memset via makeInvalidVulkanStructure() to detect whether the implementation writes to output structures ([L138-L145](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L138))
- **Robustness testing**: Tests implementation behavior with invalid inputs rather than valid ones, validating the maintenance5 guarantee of clean output for unsupported parameters
- **Permissive verdict for sparse flags**: Acknowledges that some implementations ignore invalid flags in sparse format queries and always passes those cases ([L306-L308](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L306), [L316-L318](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L316))

## Notes / Uncertainties

- The file name mentions "Maint5" and the registration function is createMaintenance5Tests(), but the group name in the test tree is simply "maintenance5" ([L345](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L345)).
- The HAS_FORMAT_PARAM and HAS_FLAGS_PARAM bit flags at [L43-L44](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L43) are used to determine which tests belong in the format vs. flags subgroups. DeviceFormatProps and DeviceFormatPropsSecond only have HAS_FORMAT_PARAM, so they only appear in the format group.
- The sparse image format tests with invalid flags always pass because "some implementations ignore wrong flags" ([L306-L308](../../modules/vulkan/api/vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L306)). This means these tests do not actually validate the maintenance5 behavior for sparse format queries with invalid flags.
- The file is not explicitly guarded with `#ifndef CTS_USES_VULKANSC`, but the registration context indicates it is non-VKSC only.
