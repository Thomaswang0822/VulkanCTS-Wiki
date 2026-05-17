# [vktApiGetDeviceProcAddrTests.cpp](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L1)

## Overview

Tests that `vkGetDeviceProcAddr` returns `NULL` for device-level extension functions that have not been enabled at device creation time. The test creates a device with no extensions and queries a large list of known extension function names, verifying each returns `NULL`.

## Role of File

Registration/dispatcher. The `.cpp` file is a thin wrapper that creates the test group and delegates to an auto-generated `.inl` file for the actual test logic and function name list.

## Source Code

| File | Description |
|------|-------------|
| [vktApiGetDeviceProcAddrTests.cpp](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L1) | Group registration and delegation |
| [vktApiGetDeviceProcAddrTests.hpp](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.hpp#L1) | Declares `createGetDeviceProcAddrTests` |
| [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1) | Auto-generated test implementation and function-name list |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L130) | Parent registration: `apiTests->addChild(createGetDeviceProcAddrTests(testCtx))` |

## Registration Hierarchy

```text
api.get_device_proc_addr
└── non_enabled
```

The confirmed Level-3 root is `get_device_proc_addr`, which [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L130) adds directly under `api`. [createGetDeviceProcAddrTests()](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L38-L43) creates that root group, and [addGetDeviceProcAddrTests()](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1086-L1089) registers exactly one direct child test case, `non_enabled`.

## Test Families

### non_enabled — Querying non-enabled device extension entry points

[addGetDeviceProcAddrTests()](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1086-L1089) registers `non_enabled` as the only direct child under `api.get_device_proc_addr`.

The test logic in [testGetDeviceProcAddr()](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L21-L1084):
1. Creates a `CustomInstance` and a `CustomDevice` with zero device extensions enabled ([vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L44-L58)).
2. Builds a large auto-generated vector of extension device-function names ([vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L60-L1070)).
3. Calls `deviceDriver.getDeviceProcAddr(device.get(), function.c_str())` for each name ([vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1073-L1079)).
4. Fails if any queried function returns a non-`NULL` pointer, otherwise passes with "All functions are NULL" ([vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1081-L1083)).

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Registration root | `api.get_device_proc_addr` | Confirmed by [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L130) and [createGetDeviceProcAddrTests()](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L38-L43) |
| Direct child subgroup names | `non_enabled` | Registered by [addGetDeviceProcAddrTests()](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1086-L1089) |
| Function list | ~500+ names | Auto-generated from the Vulkan XML registry in [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L60-L1070) |
| Device extensions | None | Device is created with `enabledExtensionCount = 0` in [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L44-L56) |
| Queue setup | `queueFamilyIndex = 0`, `queueCount = 1`, `queuePriority = 1.0f` | Hard-coded in [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L29-L42) |

## Support / Feature Requirements

No explicit extension or feature requirements are enabled for the test. It creates its own instance and device, and the device is deliberately created with no device extensions enabled ([vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L44-L58)).

## Verification Methods

- **`NULL` pointer check**: For each queried function name, `vkGetDeviceProcAddr` must return `NULL`. Any non-`NULL` result is logged and causes the test to fail ([vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1072-L1083)).

## Test Principles Observed

- Negative API testing: verifies that unenabled device-level extension entry points are not exposed.
- Registry-driven breadth: checks a large auto-generated list of known extension device functions rather than a hand-picked subset.

## Notes / Uncertainties

- The function-name list is auto-generated by `scripts/gen_framework.py`, so the exact list size and names will change as the Vulkan registry evolves.
- This file covers only device-level function lookup behavior; instance-level function queries are not tested here.
- The inspected repository also contains a Vulkan SC generated variant of [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1), but this page documents the non-SC path referenced by [vktApiGetDeviceProcAddrTests.cpp](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L30).
