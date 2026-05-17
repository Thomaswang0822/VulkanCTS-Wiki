# [vktApiDeviceInitializationTests.cpp](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1)

## Overview

[`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.device_init` subtree. The file registers a broad set of direct child subgroups covering instance creation, device creation, unsupported extensions and features, queue-creation variants, global-priority paths, and several Vulkan-SC-excluded cases through [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879-L2952).

## Role of File

Implementation-heavy test file for the `api.device_init` subgroup. The public entry point is [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879-L2952).

## Source Code

- Primary source: [vktApiDeviceInitializationTests.cpp](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1)
- Header: [vktApiDeviceInitializationTests.hpp](../../../modules/vulkan/api/vktApiDeviceInitializationTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L100-L100)

## Registration Hierarchy

```text
api.device_init
├── create_instance_name_version
├── create_instance_invalid_api_version
├── create_instance_null_appinfo
├── create_instance_unsupported_extensions
├── create_instance_extension_name_abuse
├── create_instance_layer_name_abuse
├── enumerate_devices_alloc_leak (not in Vulkan SC)
├── create_device
├── create_multiple_devices
├── create_device_unsupported_extensions
├── create_device_various_queue_counts
├── create_device_global_priority
├── create_device_global_priority_khr (not in Vulkan SC)
├── create_device_global_priority_query (not in Vulkan SC)
├── create_device_global_priority_query_khr (not in Vulkan SC)
├── create_device_features2
├── create_device_unsupported_features
├── create_device_queue2
├── create_instance_device_intentional_alloc_fail (not in Vulkan SC)
├── create_device_queue2_two_queues
├── create_device_queue2_all_protected
├── create_device_queue2_all_unprotected
├── create_device_queue2_split
├── create_device_queue2_all_families
├── create_device_queue2_all_families_protected
└── create_device_queue2_all_combinations
```

The confirmed Level-3 root is `api.device_init`, created by [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879-L2952) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L100-L100). The exact direct child subgroup names are added in [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883-L2950). Most children are created through [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876), which wraps each subgroup around a single `basic` leaf, while [`create_device_unsupported_features`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2918-L2922) is an explicit subgroup that contains `core` plus additional per-feature leaves from [`addSeparateUnsupportedFeatureTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921-L2921).

## Test Families

### create_instance_name_version — Instance creation with name and version fields

Registered through [`addFunctionCaseInNewSubgroup(testCtx, ..., "create_instance_name_version", ...)`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883-L2884). This direct child is one of the simple wrapper subgroups created by [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876), so the subgroup itself contains a single `basic` leaf.

### create_instance_invalid_api_version — Invalid API-version instance creation

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2885-L2886). Like the neighboring instance-creation groups, it is a one-leaf subgroup created by [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_instance_null_appinfo — Null-application-info instance creation

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2887-L2888). The subgroup structure again comes from [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876), so the observable deeper structure under this direct child is a single `basic` test case.

### create_instance_unsupported_extensions — Unsupported-instance-extension requests

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2889-L2890). This subgroup covers instance creation while requesting unsupported extensions and follows the same single-`basic` wrapper pattern enforced by [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_instance_extension_name_abuse — Malformed instance-extension names

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2891-L2892). The subgroup contains one `basic` leaf because it is created through [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_instance_layer_name_abuse — Malformed instance-layer names

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2893-L2894). This is the last always-present instance-creation subgroup before the Vulkan-SC-guarded branch and also uses the standard single-`basic` subgroup wrapper.

### enumerate_devices_alloc_leak — Device enumeration allocation-leak coverage

Registered only when `CTS_USES_VULKANSC` is not defined, as shown by the preprocessor guard around [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2895-L2898). The subgroup itself is still produced by [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876) and therefore contains one `basic` leaf.

### create_device — Basic device creation

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2899-L2899). This direct child is a simple one-leaf subgroup created by [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_multiple_devices — Multiple logical-device creation

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2900-L2901). It uses the same single-`basic` subgroup structure as the other direct children created through [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_device_unsupported_extensions — Unsupported-device-extension requests

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2902-L2903). The subgroup is another `basic`-only wrapper created by [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_device_various_queue_counts — Queue-count variation during device creation

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2904-L2905). This direct child covers varying queue-count configurations and follows the same single-`basic` subgroup pattern.

### create_device_global_priority — Core global-priority device creation

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906-L2907). This subgroup uses [`checkGlobalPrioritySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906-L2907) as its support gate and remains a single-`basic` wrapper subgroup under [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_device_global_priority_khr — KHR global-priority device creation

Registered only outside Vulkan SC at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2908-L2910). It uses the same [`checkGlobalPrioritySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2909-L2910) gate as the core variant and is wrapped as a one-`basic` subgroup.

### create_device_global_priority_query — Queried global-priority device creation

Registered only outside Vulkan SC at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2911-L2912). This direct child switches to [`checkGlobalPriorityQuerySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2911-L2912) and, like the other helper-created branches, exposes a single `basic` leaf below the direct child.

### create_device_global_priority_query_khr — Queried KHR global-priority device creation

Registered only outside Vulkan SC at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2913-L2914). It pairs the queried-priority path with the KHR variant and uses [`checkGlobalPriorityQuerySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2913-L2914).

### create_device_features2 — Device creation via `VkPhysicalDeviceFeatures2`

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2916-L2917). The registration still goes through [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876), so the subgroup contains one `basic` leaf even though the semantic focus shifts to the `Features2` path.

### create_device_unsupported_features — Unsupported-feature subgroup

Registered as an explicit subgroup at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2918-L2922). Unlike the helper-created direct children, this branch visibly contains a `core` leaf added by [`addFunctionCase(subgroup.get(), "core", createDeviceWithUnsupportedFeaturesTest)`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2920-L2920) plus additional per-feature leaves added by [`addSeparateUnsupportedFeatureTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921-L2921). The exact names of those additional feature-specific leaves were not enumerated in the inspected excerpt and are therefore documented here only as deeper descendants, not as direct children of `api.device_init`.

### create_device_queue2 — Base `vkCreateDeviceWithQueue2` coverage

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2924-L2925). This direct child is distinct from the later protected-memory queue2 variants and follows the standard helper-created single-`basic` subgroup pattern.

### create_instance_device_intentional_alloc_fail — Intentional allocation-failure path

Registered only outside Vulkan SC at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2926-L2930). The comment immediately above the registration notes why the test is excluded from Vulkan SC builds, and the subgroup itself remains a one-`basic` wrapper from [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876).

### create_device_queue2_two_queues — Queue2 creation with two queues

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2933-L2935) as the first protected-memory queue2 variant. It uses [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2934-L2935) and exposes one `basic` leaf below the direct child.

### create_device_queue2_all_protected — Queue2 creation with all protected queues

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2936-L2937). This is one of the single-queue-family protected-memory variants guarded by [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2936-L2937).

### create_device_queue2_all_unprotected — Queue2 creation with all unprotected queues

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2938-L2939). It stays within the protected-memory support-gated queue2 group while varying the protection assignment.

### create_device_queue2_split — Queue2 creation with mixed protected and unprotected queues

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2940-L2941). The underlying test function name indicates `N` protected plus `M` unprotected queues, while the subgroup structure remains the standard single `basic` leaf.

### create_device_queue2_all_families — Queue2 creation across all queue families

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2943-L2945). The adjacent comment marks this as part of the multi-queue-family block, and it is support-gated by [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2944-L2945).

### create_device_queue2_all_families_protected — Queue2 creation with all families protected

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2946-L2948). This is another multi-family protected-memory variant using [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2946-L2948).

### create_device_queue2_all_combinations — Queue2 creation over multiple queue combinations

Registered at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2949-L2950). It is the last direct child under `api.device_init`, still support-gated by [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2949-L2950) and wrapped as a single-`basic` subgroup.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Level-3 direct child subgroups | `create_instance_name_version`, `create_instance_invalid_api_version`, `create_instance_null_appinfo`, `create_instance_unsupported_extensions`, `create_instance_extension_name_abuse`, `create_instance_layer_name_abuse`, `enumerate_devices_alloc_leak`, `create_device`, `create_multiple_devices`, `create_device_unsupported_extensions`, `create_device_various_queue_counts`, `create_device_global_priority`, `create_device_global_priority_khr`, `create_device_global_priority_query`, `create_device_global_priority_query_khr`, `create_device_features2`, `create_device_unsupported_features`, `create_device_queue2`, `create_instance_device_intentional_alloc_fail`, `create_device_queue2_two_queues`, `create_device_queue2_all_protected`, `create_device_queue2_all_unprotected`, `create_device_queue2_split`, `create_device_queue2_all_families`, `create_device_queue2_all_families_protected`, `create_device_queue2_all_combinations` from [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883-L2950) |
| Helper-created subgroup leaf shape | Most direct children receive a single `basic` leaf through [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876) |
| Unsupported-feature deeper descendants | Explicit `core` leaf plus additional per-feature leaves added by [`addSeparateUnsupportedFeatureTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2920-L2921) |
| Global-priority variants | core and KHR forms plus queried and queried-KHR forms at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906-L2914) |
| Queue2 protected-memory variants | `create_device_queue2_two_queues`, `create_device_queue2_all_protected`, `create_device_queue2_all_unprotected`, `create_device_queue2_split`, `create_device_queue2_all_families`, `create_device_queue2_all_families_protected`, `create_device_queue2_all_combinations` at [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2933-L2950) |
| Vulkan SC exclusions | `enumerate_devices_alloc_leak`, `create_device_global_priority_khr`, `create_device_global_priority_query`, `create_device_global_priority_query_khr`, and `create_instance_device_intentional_alloc_fail` are conditionally excluded by `#ifndef CTS_USES_VULKANSC` around [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2895-L2898), [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2908-L2915), and [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2926-L2930) |

## Support / Feature Requirements

- [`checkGlobalPrioritySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906-L2910) gates `create_device_global_priority` and `create_device_global_priority_khr`.
- [`checkGlobalPriorityQuerySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2911-L2914) gates `create_device_global_priority_query` and `create_device_global_priority_query_khr`.
- [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2934-L2950) gates the protected-memory queue2 direct children from `create_device_queue2_two_queues` through `create_device_queue2_all_combinations`.
- Several direct children are compiled out for Vulkan SC by the `#ifndef CTS_USES_VULKANSC` guards around [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2895-L2898), [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2908-L2915), and [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2926-L2930).

## Verification Methods

- The inspected registration code proves subgroup structure and support-gating placement through [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879-L2952) rather than the detailed leaf implementation bodies.
- Most direct children wrap a single `basic` leaf via [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2869-L2876), so each subgroup primarily represents one scenario-specific function case rather than a large generated matrix at the direct-child level.
- [`create_device_unsupported_features`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2918-L2922) is the visible exception: it contains a `core` leaf plus extra per-feature leaves added by [`addSeparateUnsupportedFeatureTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921-L2921).
- The detailed pass/fail logic for individual leaves was not re-inspected in this normalization run, so this page keeps verification claims constrained to registration-backed structure and explicit support hooks.

## Test Principles Observed

- Separate valid, invalid, unsupported, and stress-style initialization paths into individually named direct child subgroups.
- Use helper-generated one-leaf subgroups to keep the registration tree uniform across many instance/device creation scenarios.
- Isolate special support-gated paths such as global-priority and protected-memory queue creation behind explicit support-check functions.
- Use an explicit nested subgroup for unsupported-feature coverage when deeper per-feature descendants are needed.

## Notes / Uncertainties

- This normalization confirms the Level-3 root as `api.device_init` and the exact direct child subgroup names listed in [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883-L2950).
- The direct-child hierarchy is fully confirmed from registration code, but the individual implementation bodies for the leaf test functions were not re-read during this run, so scenario semantics beyond registration names and support hooks are intentionally described conservatively.
- The deeper descendant names created by [`addSeparateUnsupportedFeatureTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921-L2921) were not enumerated from the inspected excerpt and therefore remain documented only as an acknowledged deeper subtree under `create_device_unsupported_features`.
