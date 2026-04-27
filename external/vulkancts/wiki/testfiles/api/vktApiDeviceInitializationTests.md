# [vktApiDeviceInitializationTests.cpp](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1)

## Overview

[`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1) implements the `api/device_init` subgroup registered by [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L100). The file is large and covers a wide range of instance and device creation scenarios including invalid API versions, null application info, unsupported extensions, extension name abuse, layer name abuse, allocation leak detection, multiple device creation, unsupported features, queue creation with protected memory, and intentional allocation failure.

## Role of File

Implementation-heavy test file for the `api/device_init` subgroup.

## Source Code

- Primary source: [vktApiDeviceInitializationTests.cpp](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1)
- Header: [vktApiDeviceInitializationTests.hpp](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L100)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createDeviceInitializationTests(testCtx)
          +-- device_init
              +-- create_instance_name_version
              +-- create_instance_invalid_api_version
              +-- create_instance_null_appinfo
              +-- create_instance_unsupported_extensions
              +-- create_instance_extension_name_abuse
              +-- create_instance_layer_name_abuse
              +-- enumerate_devices_alloc_leak  (not in Vulkan SC)
              +-- create_device
              +-- create_multiple_devices
              +-- create_device_unsupported_extensions
              +-- create_device_various_queue_counts
              +-- create_device_global_priority
              +-- create_device_global_priority_khr  (not in Vulkan SC)
              +-- create_device_global_priority_query  (not in Vulkan SC)
              +-- create_device_global_priority_query_khr  (not in Vulkan SC)
              +-- create_device_features2
              +-- create_device_unsupported_features/
              +-- create_device_queue2
              +-- create_instance_device_intentional_alloc_fail  (not in Vulkan SC)
              +-- create_device_queue2_two_queues
              +-- create_device_queue2_all_protected
              +-- create_device_queue2_all_unprotected
              +-- create_device_queue2_split
              +-- create_device_queue2_all_families
              +-- create_device_queue2_all_families_protected
              +-- create_device_queue2_all_combinations
```

Evidence:
- `device_init` group created at [`createDeviceInitializationTests()`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2881)
- test cases registered from [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883) through [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2951)

## Test Hierarchy

```text
api
+-- device_init
    +-- create_instance_name_version
    +-- create_instance_invalid_api_version
    +-- create_instance_null_appinfo
    +-- create_instance_unsupported_extensions
    +-- create_instance_extension_name_abuse
    +-- create_instance_layer_name_abuse
    +-- enumerate_devices_alloc_leak  (excluded for Vulkan SC)
    +-- create_device
    +-- create_multiple_devices
    +-- create_device_unsupported_extensions
    +-- create_device_various_queue_counts
    +-- create_device_global_priority
    +-- create_device_global_priority_khr  (excluded for Vulkan SC)
    +-- create_device_global_priority_query  (excluded for Vulkan SC)
    +-- create_device_global_priority_query_khr  (excluded for Vulkan SC)
    +-- create_device_features2
    +-- create_device_unsupported_features/
        +-- core
        +-- (additional per-feature subcases)
    +-- create_device_queue2
    +-- create_instance_device_intentional_alloc_fail  (excluded for Vulkan SC)
    +-- create_device_queue2_two_queues
    +-- create_device_queue2_all_protected
    +-- create_device_queue2_all_unprotected
    +-- create_device_queue2_split
    +-- create_device_queue2_all_families
    +-- create_device_queue2_all_families_protected
    +-- create_device_queue2_all_combinations
```

Source: [`createDeviceInitializationTests()`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879).

## Test Families

### 1. Instance creation tests

Six instance-creation cases are registered at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883):

- `create_instance_name_version`: validates instance creation with correct name and version fields
- `create_instance_invalid_api_version`: tests instance creation with an invalid API version
- `create_instance_null_appinfo`: tests instance creation with null `pApplicationInfo`
- `create_instance_unsupported_extensions`: tests instance creation requesting unsupported extensions
- `create_instance_extension_name_abuse`: tests instance creation with malformed extension names
- `create_instance_layer_name_abuse`: tests instance creation with malformed layer names

### 2. Device creation tests

Multiple device-creation cases are registered starting at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2899):

- `create_device`: basic device creation
- `create_multiple_devices`: creating multiple devices from the same physical device
- `create_device_unsupported_extensions`: device creation requesting unsupported extensions
- `create_device_various_queue_counts`: device creation with different queue count configurations
- `create_device_global_priority` / `create_device_global_priority_khr`: device creation with global priority (KHR variant excluded for Vulkan SC) at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906)
- `create_device_features2`: device creation using `VkPhysicalDeviceFeatures2` at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2916)
- `create_device_unsupported_features`: subgroup with per-feature subcases at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2919)

### 3. Queue creation with protected memory

Cases starting at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2934) exercise `vkCreateDeviceWithQueue2` with protected memory configurations:

- `create_device_queue2_two_queues`, `create_device_queue2_all_protected`, `create_device_queue2_all_unprotected`, `create_device_queue2_split`, `create_device_queue2_all_families`, `create_device_queue2_all_families_protected`, `create_device_queue2_all_combinations`

All protected-memory cases use `checkProtectedMemorySupport` as their support gate.

### 4. Intentional allocation failure

`create_instance_device_intentional_alloc_fail` at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2929) is excluded for Vulkan SC.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Instance creation variants | name/version, invalid API version, null appinfo, unsupported extensions, extension name abuse, layer name abuse at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883) |
| Device creation variants | basic, multiple devices, unsupported extensions, various queue counts, global priority, features2, unsupported features at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2899) |
| Global priority variants | core and KHR variants at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906) |
| Protected memory queue variants | two queues, all protected, all unprotected, split, all families, all families protected, all combinations at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2934) |
| Vulkan SC exclusions | `enumerate_devices_alloc_leak`, `create_device_global_priority_khr`, `create_device_global_priority_query_khr`, `create_instance_device_intentional_alloc_fail` under `#ifndef CTS_USES_VULKANSC` |

## Support / Feature Requirements

- global priority tests use `checkGlobalPrioritySupport` and `checkGlobalPriorityQuerySupport` at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2907)
- protected memory queue tests use `checkProtectedMemorySupport` at [`vktApiDeviceInitializationTests.cpp`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2935)
- several cases are excluded for Vulkan SC via `#ifndef CTS_USES_VULKANSC` guards

## Verification Methods

- instance and device creation tests verify that the expected `VkResult` is returned
- unsupported extension/feature tests verify that the implementation correctly rejects invalid configurations
- allocation leak tests verify that resources are properly freed
- protected memory queue tests verify correct queue creation and property reporting

## Test Principles Observed

- Cover both valid and invalid creation paths
- Test boundary conditions like null appinfo and malformed names
- Verify that the implementation correctly handles unsupported features and extensions
- Exercise protected memory queue creation across multiple configurations

## Notes / Uncertainties

- The file is very large (over 2900 lines); only the registration function at the end and the beginning of the file were fully inspected. The individual test function implementations were not read in detail, so the descriptions of verification methods are inferred from the registration pattern and test names rather than from direct code inspection.
- The `create_device_unsupported_features` subgroup contains additional per-feature subcases registered by [`addSeparateUnsupportedFeatureTests()`](../../../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921) whose individual names are not visible in the inspected excerpt.
