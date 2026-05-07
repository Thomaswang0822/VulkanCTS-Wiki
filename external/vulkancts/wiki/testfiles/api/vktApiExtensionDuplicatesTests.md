# [vktApiExtensionDuplicatesTests.cpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1)

## Overview

Tests that Vulkan instances and devices can be created with duplicate extension names in the `ppEnabledExtensionNames` array. Verifies both pointer-based duplication (same pointer appearing multiple times) and string-based duplication (different pointers to identical strings).

## Role of File

Implementation-heavy. Contains instance/device creation logic, string duplication utilities, and test registration.

## Source Code

| File | Description |
|------|-------------|
| [vktApiExtensionDuplicatesTests.cpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1) | Test implementation and registration |
| [vktApiExtensionDuplicatesTests.hpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.hpp#L1) | Declares `createExtensionDuplicatesTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L138) | Parent registration: `apiTests->addChild(createExtensionDuplicatesTests(testCtx))` |

## Registration Path

```
api
  +-- extension_duplicates
       +-- instance
       |    +-- by_pointers
       |    +-- by_names
       +-- device
            +-- by_pointers
            +-- by_names
```

## Test Hierarchy

```
extension_duplicates
  +-- instance
  |    Tests vkCreateInstance with duplicate extension names
  |    +-- by_pointers
  |    |    Same char* pointer appears multiple times
  |    +-- by_names
  |         Different char* pointers to identical strings
  +-- device
       Tests vkCreateDevice with duplicate extension names
       +-- by_pointers
       |    Same char* pointer appears multiple times
       +-- by_names
            Different char* pointers to identical strings
```

## Test Families

### extension_duplicates

Group name verified at [vktApiExtensionDuplicatesTests.cpp:378](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L378): `new tcu::TestCaseGroup(testCtx, "extension_duplicates")`.

The `StringDuplicator` utility class at [line 65](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L65) generates duplicate extension entries in two modes:
- `duplicatePointers()`: Reuses the same `const char*` pointer multiple times ([line 83](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L83))
- `duplicateStrings()`: Creates separate `std::string` objects with the same content, producing different pointers ([line 114](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L114))

**Instance tests** - `InstanceExtensionDuplicatesInstance` at [line 154](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L154):
1. Enumerates all available instance extensions ([line 208](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L208))
2. Duplicates the extension list using the selected method ([lines 224-227](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L224))
3. Creates a `VkInstanceCreateInfo` with the duplicated extension list ([lines 229-248](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L229))
4. Calls `createUncheckedInstance` and checks for `VK_SUCCESS` ([lines 251-252](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L251))

**Device tests** - `DeviceExtensionDuplicatesInstance` at [line 168](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L168):
1. Gets the device creation extensions from context ([line 287](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L287))
2. Duplicates the extension list using the selected method ([line 289](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L289))
3. Creates a `VkDeviceCreateInfo` with the duplicated extension list ([lines 297-331](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L297))
4. Calls `createUncheckedDevice` and checks for `VK_SUCCESS` ([lines 334-335](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L334))
5. Destroys the created device ([lines 336-347](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L336))

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Target | instance, device | Whether to test instance or device creation |
| Duplication method | by_pointers, by_names | Pointer reuse vs. string duplication |
| Duplicate count | 2-4 per extension | Varies by extension index modulo 2/3 |

## Support / Feature Requirements

No explicit extension requirements. The test uses whatever extensions are available on the system.

## Verification Methods

- **Instance creation**: `vkCreateInstance` must return `VK_SUCCESS` when duplicate extensions are provided ([line 270](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L270))
- **Device creation**: `vkCreateDevice` must return `VK_SUCCESS` when duplicate extensions are provided ([line 365](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L365))
- **Quality warning**: If no extensions are available, the test returns `QP_TEST_RESULT_QUALITY_WARNING` rather than failing ([lines 211-213](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L211))

## Test Principles Observed

- Specification compliance: Vulkan allows duplicate extension names in creation info
- Pointer vs. string distinction: tests both interpretations of "duplicate"

## Notes / Uncertainties

- The device test uses `createUncheckedDevice` which bypasses some validation; the test verifies the driver accepts the duplicate list, not that validation layers handle it correctly
- On Vulkan SC, the device test uses `CustomInstance` and `DeviceDriver` for proper cleanup ([lines 275-283](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L275))
- The duplication pattern varies: even-indexed extensions get 2 copies, mod-3-indexed get 3 copies, others get 4 copies ([lines 86-112](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L86))
