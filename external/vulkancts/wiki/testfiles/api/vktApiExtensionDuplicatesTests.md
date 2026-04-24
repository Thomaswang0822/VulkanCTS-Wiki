# [vktApiExtensionDuplicatesTests.cpp](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1)

## Overview

Tests that Vulkan instances and devices can be created with duplicate extension names in the `ppEnabledExtensionNames` arrays. The Vulkan specification requires implementations to ignore duplicate extension names, and this file verifies that behavior by deliberately passing duplicated extension names both as repeated pointer values and as separate string copies.

## Role of File

Implementation-heavy. Contains two `TestInstance` subclasses ([InstanceExtensionDuplicatesInstance](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L154), [DeviceExtensionDuplicatesInstance](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L168)), a `TestCase` subclass ([ExtensionDuplicatesCase](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L182)), a helper `StringDuplicator` utility, and the registration function.

## Source Code

| File | Path |
|------|------|
| Source | [vktApiExtensionDuplicatesTests.cpp](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1) |
| Header | [vktApiExtensionDuplicatesTests.hpp](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.hpp#L1) |
| Parent registration | [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L138) |

## Registration Path

```
api
└── extension_duplicates             (vktApiTests.cpp#L138)
    ├── instance
    │   ├── by_pointers
    │   └── by_names
    └── device
        ├── by_pointers
        └── by_names
```

## Test Hierarchy

```
extension_duplicates
├── instance
│   ├── by_pointers   (InstanceExtensionDuplicatesInstance, byPointersOrNames=true)
│   └── by_names      (InstanceExtensionDuplicatesInstance, byPointersOrNames=false)
└── device
    ├── by_pointers   (DeviceExtensionDuplicatesInstance, byPointersOrNames=true)
    └── by_names      (DeviceExtensionDuplicatesInstance, byPointersOrNames=false)
```

## Test Families

### InstanceExtensionDuplicatesInstance

Enumerates all available instance extensions and creates a new `VkInstance` with those extensions duplicated in the `ppEnabledExtensionNames` array ([line 204-271](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L204)). The duplication method depends on the `m_byPointersOrNames` flag:

- **by_pointers**: Uses `StringDuplicator::duplicatePointers()` which inserts the same `const char*` pointer multiple times into the extension list ([line 83-113](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L83)). This tests the case where the same memory address appears repeatedly.

- **by_names**: Uses `StringDuplicator::duplicateStrings()` which creates separate `std::string` copies of each extension name and pushes their `c_str()` pointers ([line 114-151](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L114)). This tests the case where different memory addresses contain the same extension name string.

The test passes if `vkCreateInstance` returns `VK_SUCCESS` ([line 270](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L270)). If no instance extensions are available, the test returns `QP_TEST_RESULT_QUALITY_WARNING` ([line 212-213](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L212)).

### DeviceExtensionDuplicatesInstance

Takes the device creation extensions from the context and creates a new `VkDevice` with those extensions duplicated ([line 273-366](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L273)). The same two duplication methods (by_pointers and by_names) apply. On Vulkan SC, the test creates a custom instance and uses `DeviceDriver` to destroy the device ([line 340-346](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L340)). On non-SC, it uses the context's device interface to destroy the device ([line 345](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L345)).

The test passes if `vkCreateDevice` returns `VK_SUCCESS` ([line 365](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L365)). If no device extensions are available, the test returns `QP_TEST_RESULT_QUALITY_WARNING` ([line 293-294](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L293)).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| instanceOrDevice | instance (true), device (false) | [line 373](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L373) |
| byPointersOrNames | by_pointers (true), by_names (false) | [line 375](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L375) |
| Duplication count per extension | 2x (even index), 3x (index divisible by 3), 4x (other) | [line 86-112](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L86) |

## Support / Feature Requirements

No explicit extension or feature requirements are checked. The tests use `createUncheckedInstance` and `createUncheckedDevice` which allow the creation calls to proceed without validation-layer-based rejection. The tests are registered unconditionally (not guarded by `#ifndef CTS_USES_VULKANSC` in [vktApiTests.cpp#L138](../../modules/vulkan/api/vktApiTests.cpp#L138)).

## Verification Methods

- **Instance creation success**: `vkCreateInstance` must return `VK_SUCCESS` when duplicate extension names are provided ([line 251-270](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L251)).
- **Device creation success**: `vkCreateDevice` must return `VK_SUCCESS` when duplicate extension names are provided ([line 334-365](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L334)).
- **Quality warning on empty lists**: If the available extension list is empty, the test returns `QP_TEST_RESULT_QUALITY_WARNING` rather than pass or fail, since the duplicate behavior cannot be exercised ([line 212, 293](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L212)).

## Test Principles Observed

- **Specification compliance**: Directly tests a spec requirement that implementations must tolerate duplicate extension names.
- **Two duplication strategies**: Tests both pointer-level duplication (same address repeated) and string-level duplication (different addresses, same content), covering two possible implementation pitfalls ([line 83-151](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L83)).
- **Vulkan SC compatibility**: Includes conditional code paths for `CTS_USES_VULKANSC` with proper device cleanup ([line 275-283, 307-317, 340-346](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L275)).
- **Graceful handling of empty extension sets**: Returns quality warning rather than failing when no extensions are available to duplicate ([line 212, 293](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L212)).

## Notes / Uncertainties

- The `StringDuplicator` utility uses a deterministic but non-uniform duplication pattern: extensions at even indices are duplicated 2x, at indices divisible by 3 are duplicated 3x, and all others are duplicated 4x ([line 86-112](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L86)). The rationale for this specific pattern is not documented.
- The instance test creates a new instance with all available extensions enabled (duplicated), which may include extensions that conflict or require specific features. The test relies on the implementation correctly handling this.
- The device test uses `m_context.getDeviceCreationExtensions()` as the source list ([line 287](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L287)), which are the extensions already enabled on the current device, ensuring they are known to be supported.
- The `distinct()` helper function uses `std::set<const char*>` which compares pointer values, not string content ([line 55-63](../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L55)). This means if the input already contains duplicate pointers, they will be deduplicated before re-duplication.
