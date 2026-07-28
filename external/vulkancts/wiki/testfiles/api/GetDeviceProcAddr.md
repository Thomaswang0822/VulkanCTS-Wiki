## Overview

**Core question:** Does `vkGetDeviceProcAddr` return `NULL` for every extension and non-device-level entry point when the device is created with no extensions enabled?

- Covers the `api.get_device_proc_addr` test family, implemented in [vktApiGetDeviceProcAddrTests.cpp](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L38-L43) and the auto-generated [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L21-L1101).
- Registers one test case leaf, `non_enabled`, under the `get_device_proc_addr` test family in the `api` test category.
- The test creates a `VkDevice` with `enabledExtensionCount = 0u`, then queries a large registry-derived list of extension and WSI function names through `vkGetDeviceProcAddr` and verifies each returns `NULL`.
- The page explains what the test checks, why the function list is auto-generated, what a failure means, and why the case is non-VulkanSC only.

## Background Knowledge

- `vkGetDeviceProcAddr(device, pName)` resolves device-level commands. Per the Vulkan specification, it returns a valid function pointer for core device-level commands and for device-level extension commands whose extension is enabled at device creation; it returns `NULL` for device-level extension commands whose extension is not enabled, and for any name that is not a device-level command (for example, instance-level or physical-device-level commands).
- Device extension enablement is fixed at `vkCreateDevice` time. A device created with `enabledExtensionCount = 0u` has no device extensions enabled, so every device-level extension command queried through that device must resolve to `NULL`.

## Registration Hierarchy

```text
api.get_device_proc_addr
└── non_enabled
```

[vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L128-L131) adds the `get_device_proc_addr` test family directly under the `api` test category, guarded by `#ifndef CTS_USES_VULKANSC`. [addGetDeviceProcAddrTests()](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1103-L1106) registers the single test case leaf `non_enabled`, and [testGetDeviceProcAddr()](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L21-L1101) implements the test logic.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `non_enabled` | The only registered case; names the device state (no extensions enabled) rather than a selectable variant | [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1103-L1106) |
| Queried function names | ~500+ vendor-suffixed extension and WSI entry points derived from `vk.xml` | The breadth axis of the test; each name is one query that must resolve to `NULL` | [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L59-L1086) |
| Device extension count | `0u` | Fixed by the test; the precondition that makes every extension query expected to return `NULL` | [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L43-L55) |
| Queue setup | `queueFamilyIndex = 0`, `queueCount = 1`, `queuePriority = 1.0f` | Minimum queue configuration required to create a valid `VkDevice` | [vkGetDeviceProcAddr.inl](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L28-L41) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. This family has a single value, `non_enabled`, which names the device state under test (no device extensions enabled) rather than a selectable variant. Because there is only one value, no per-value subsections are needed. The behavior of interest is whether `vkGetDeviceProcAddr` returns `NULL` for every entry in the auto-generated function-name list when queried against a device created with `enabledExtensionCount = 0u`.

## Shader Analysis

This test does not use a shader. It exercises host-side entry-point resolution only and does not create any pipeline, shader module, or dispatch workload.

## Runtime Execution and Result Checking

- The test creates a `CustomInstance` from the test context and selects a physical device.
- It builds a `VkDeviceQueueCreateInfo` with one queue from family index 0, then a `VkDeviceCreateInfo` with `enabledExtensionCount = 0u` and `ppEnabledExtensionNames = nullptr`, and calls `createCustomDevice` to obtain a `VkDevice` with no device extensions enabled.
- It constructs the `DeviceDriver` wrapper and iterates the auto-generated function-name vector, calling `deviceDriver.getDeviceProcAddr(device.get(), function.c_str())` for each name.
- For each query, if the returned pointer is not `NULL`, the test logs `Function <name> is not NULL` and sets the failure flag.
- The pass condition is that no query returned a non-`NULL` pointer; the test then returns `pass("All functions are NULL")`. If any query returned non-`NULL`, it returns `fail("Fail")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `non_enabled` | `vkGetDeviceProcAddr` returned a non-`NULL` pointer for a name that must resolve to `NULL` on a device with no extensions enabled. |

### Cause Analysis

#### Non-NULL return for an unenabled extension or non-device-level command

**Possible failure symptoms:** The test log contains one or more `Function <name> is not NULL` messages naming the offending entry points, and the case returns `tcu::TestStatus::fail("Fail")` instead of `pass("All functions are NULL")`.

**Possible implementation causes:** Per the Vulkan specification, `vkGetDeviceProcAddr` must return `NULL` for device-level extension commands whose extension is not enabled at `vkCreateDevice` time, and for any name that is not a device-level command. A non-`NULL` return indicates the implementation chain (loader, dispatch table, or ICD) is exposing an entry point that the spec requires to be unavailable for this device. The test symptom alone does not identify which layer exposes the entry point; finding the specific root cause requires source-level investigation of the implementation chain.

## Case Pruning

### Requirement-based pruning

- The `#ifndef CTS_USES_VULKANSC` guard in [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L128-L131) limits registration of the `get_device_proc_addr` test family to non-SC builds. The Vulkan SC profile does not include this test family.
- The test requires no device features, extensions, or limits, and creates the device with no extensions enabled.

### Design-based pruning

- `scripts/gen_framework.py` generates the function-name list from `vk.xml`, not from a hand-picked selection. The list changes whenever the script regenerates against the evolving Vulkan registry, so its exact size and contents vary over time.
- The list includes only device-level extension entry points and WSI entry points that are not device-level commands. Core device-level commands and instance-level core commands are absent because their expected return values would not exercise the `non_enabled` property.
- The test does not vary the device extension set. Varying which extensions are enabled would test a different property (correct exposure of enabled extension entry points) and is out of scope for this family.

## Key Takeaways

- The test verifies a negative API contract: with no device extensions enabled, `vkGetDeviceProcAddr` must not expose any extension or non-device-level entry point.
- Registry-driven breadth is central to the design. Checking the full `vk.xml`-derived list rather than a hand-picked subset catches implementations that selectively expose some unenabled extensions while correctly hiding others.
- The single test case leaf `non_enabled` is sufficient because the tested property is binary per queried name; there is no behavioral axis to vary.
- See `## Failure Meaning` for the analysis of what a non-`NULL` return implies and why the test cannot attribute the failure to a specific layer of the implementation chain.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createGetDeviceProcAddrTests()` | [vktApiGetDeviceProcAddrTests.cpp#L38-L43](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.cpp#L38-L43) | Creates the `get_device_proc_addr` test family group and delegates to the generated `.inl` registration helper. |
| Parent registration | [vktApiTests.cpp#L128-L131](../../../modules/vulkan/api/vktApiTests.cpp#L128-L131) | Adds the family under the `api` test category, guarded by `#ifndef CTS_USES_VULKANSC`. |
| `testGetDeviceProcAddr()` | [vkGetDeviceProcAddr.inl#L21-L1101](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L21-L1101) | Implements the test logic: device creation, function-name iteration, and pass/fail decision. |
| Device creation with no extensions | [vkGetDeviceProcAddr.inl#L43-L56](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L43-L56) | `VkDeviceCreateInfo` with `enabledExtensionCount = 0u`; the precondition for every expected `NULL` return. |
| Function-name list | [vkGetDeviceProcAddr.inl#L59-L1086](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L59-L1086) | Auto-generated vector of extension and WSI entry-point names queried by the test. |
| Per-name NULL check and pass/fail | [vkGetDeviceProcAddr.inl#L1089-L1100](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1089-L1100) | Loop body that flags non-`NULL` returns and the final pass/fail return. |
| `addGetDeviceProcAddrTests()` | [vkGetDeviceProcAddr.inl#L1103-L1106](../../../framework/vulkan/generated/vulkan/vkGetDeviceProcAddr.inl#L1103-L1106) | Registers the `non_enabled` test case leaf under the family group. |
| Header declaration | [vktApiGetDeviceProcAddrTests.hpp#L37](../../../modules/vulkan/api/vktApiGetDeviceProcAddrTests.hpp#L37) | Declares `createGetDeviceProcAddrTests` for the parent dispatcher. |
