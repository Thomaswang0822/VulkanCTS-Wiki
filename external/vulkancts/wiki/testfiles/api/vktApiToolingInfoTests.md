# [vktApiToolingInfoTests.cpp](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1)

## Overview

Tests the `VK_EXT_tooling_info` extension, specifically the `vkGetPhysicalDeviceToolProperties` API. Validates correct enumeration behavior for tool properties including return codes for partial and complete queries, count consistency across calls, and structural validity of returned tool property data.

## Role of File

Implementation-heavy. Contains two test functions that exercise the enumeration API with various buffer sizes and validate the returned tool property structures.

## Source Code

- Implementation: [vktApiToolingInfoTests.cpp](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1)
- Header: [vktApiToolingInfoTests.hpp](../../modules/vulkan/api/vktApiToolingInfoTests.hpp#L1)
- Parent registration: `createToolingInfoTests()` declared at [L35](../../modules/vulkan/api/vktApiToolingInfoTests.hpp#L35)

## Registration Path

```
api
  +-- tooling_info   (non-VKSC only)
        +-- tooling_info
              +-- validate_getter
              +-- validate_tools_properties
```

## Test Hierarchy

```
tooling_info
  +-- validate_getter
  |     Tests vkGetPhysicalDeviceToolProperties enumeration
  |     behavior with various buffer sizes.
  +-- validate_tools_properties
        Validates the content of returned tool property
        structures for structural correctness.
```

## Test Families

### validate_getter

Exercises `vkGetPhysicalDeviceToolProperties` in multiple scenarios:

1. **Two-call pattern**: First call with null pointer to get count, second call with exact-sized buffer. Verifies count consistency and `VK_SUCCESS` return.

2. **Oversized buffer**: Calls with `count+1` entries. Verifies the returned count is unchanged and `VK_SUCCESS` is returned.

3. **Zero-sized buffer**: Calls with count=0 and a non-null pointer. Expects `VK_INCOMPLETE` return code and count=0.

4. **Half-sized buffer** (when toolCount > 1): Calls with `count/2` entries. Expects `VK_INCOMPLETE` and the returned count equals the requested half.

- Function: `validateGetter()` at [L61](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L61)

### validate_tools_properties

Retrieves all tool properties and validates each entry:

1. `sType` must be `VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TOOL_PROPERTIES_EXT`
2. `purposes` flags must only contain valid `VkToolPurposeFlagBitsEXT` values
3. `name` must be a non-empty null-terminated string shorter than `VK_MAX_EXTENSION_NAME_SIZE`
4. `version` must be a non-empty null-terminated string shorter than `VK_MAX_EXTENSION_NAME_SIZE`
5. `description` must be a non-empty null-terminated string shorter than `VK_MAX_DESCRIPTION_SIZE`
6. `layer` must be either empty or a valid null-terminated string shorter than `VK_MAX_EXTENSION_NAME_SIZE`

- Function: `validateToolsProperties()` at [L181](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L181)
- Purpose flag validation: `validateToolPurposeFlagBits()` at [L47](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L47)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Buffer sizes tested | 0, count/2, count, count+1 | Various enumeration scenarios |
| Valid purpose flags | VALIDATION, PROFILING, TRACING, ADDITIONAL_FEATURES, MODIFYING_FEATURES, DEBUG_REPORTING, DEBUG_MARKERS | [L49](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L49) |

## Support / Feature Requirements

| Requirement | Gate | Location |
|-------------|------|----------|
| VK_EXT_tooling_info | `context.requireDeviceFunctionality()` | [L58](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L58) |

## Verification Methods

- **Return code correctness**: `VK_SUCCESS` for complete queries, `VK_INCOMPLETE` for partial queries at [L71](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L71), [L136](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L136), [L164](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L164)
- **Count consistency**: Returned count matches expected value at [L99](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L99), [L125](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L125)
- **sType validation**: `sType == VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TOOL_PROPERTIES_EXT` at [L211](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L211)
- **Purpose flag validation**: `(purposes | validPurposes) == validPurposes` at [L53](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L53)
- **String validity**: Non-empty and within max size bounds at [L213](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L213) through [L216](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L216)

## Test Principles Observed

- **Two-call enumeration pattern**: Standard Vulkan enumeration idiom tested thoroughly
- **Boundary testing**: Zero, partial, exact, and oversized buffer scenarios
- **Structural validation**: All fields of returned structures are checked for spec compliance
- **No false positives**: Tests pass even when no tools are present (toolCount == 0 skips most checks)

## Notes / Uncertainties

- The `validate_getter` test at [L131](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L131) sets `toolCountSecondCall = 0` and passes a non-null pointer, expecting `VK_INCOMPLETE`. This tests an edge case where the implementation must not write any data and must return `VK_INCOMPLETE`.
- The `validateToolsProperties` test at [L213](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L213) checks `nameSize > 0` but the spec does not explicitly require the name to be non-empty; this may be stricter than the spec requires.
- The `validateToolPurposeFlagBits` function at [L47](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L47) uses a bitwise OR check `(purposes | validPurposes) == validPurposes` which correctly validates that no invalid bits are set.
- Both tests share the same `checkSupport` function at [L56](../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L56) that requires `VK_EXT_tooling_info`.
