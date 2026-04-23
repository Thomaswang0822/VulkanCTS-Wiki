# [vktApiDeviceInitializationTests.cpp](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879)

## Overview

[`vktApiDeviceInitializationTests.cpp`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879) implements the early foundational `api/device_init` subtree registered by [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L100). Within the API registration order, it sits immediately after the already-documented lightweight `version`, `driver_properties`, `smoke`, `info`, and `device_drm_properties` branches, and before [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiTests.cpp#L101).

This file is implementation-heavy rather than lightweight: it covers instance creation tolerance, invalid and abusive names, unsupported instance/device extensions, basic and repeated device creation, queue-count variation, global-priority device creation, feature-chain based device creation, rejection of unsupported features, [`vkGetDeviceQueue2`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1864) behavior with protected queues, and one non-Vulkan-SC allocation-failure path. The inspected file is large, so this document focuses on the registration-visible families and on internal helper logic that was directly inspected.

## Role of File

Implementation-heavy test file for the `api/device_init` subgroup.

## Source Code

- Primary source: [`vktApiDeviceInitializationTests.cpp`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1)
- Declaration: [`vktApiDeviceInitializationTests.hpp`](../../modules/vulkan/api/vktApiDeviceInitializationTests.hpp#L34)
- Parent-category registration: [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L100)
- Related generated include used by unsupported-feature coverage: [`vkDeviceFeatureTest.inl`](../../modules/vulkan/api/vkDeviceFeatureTest.inl)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
└── api
    └── createTests(testCtx, "api")
        └── createApiTests(apiTests)
            └── createDeviceInitializationTests(testCtx)
                └── device_init
                    ├── create_instance_name_version
                    │   └── basic
                    ├── create_instance_invalid_api_version
                    │   └── basic
                    ├── create_instance_null_appinfo
                    │   └── basic
                    ├── create_instance_unsupported_extensions
                    │   └── basic
                    ├── create_instance_extension_name_abuse
                    │   └── basic
                    ├── create_instance_layer_name_abuse
                    │   └── basic
                    ├── enumerate_devices_alloc_leak                (not in Vulkan SC)
                    │   └── basic
                    ├── create_device
                    │   └── basic
                    ├── create_multiple_devices
                    │   └── basic
                    ├── create_device_unsupported_extensions
                    │   └── basic
                    ├── create_device_various_queue_counts
                    │   └── basic
                    ├── create_device_global_priority
                    │   └── basic
                    ├── create_device_global_priority_khr           (not in Vulkan SC)
                    │   └── basic
                    ├── create_device_global_priority_query         (not in Vulkan SC)
                    │   └── basic
                    ├── create_device_global_priority_query_khr     (not in Vulkan SC)
                    │   └── basic
                    ├── create_device_features2
                    │   └── basic
                    ├── create_device_unsupported_features
                    │   ├── core
                    │   └── additional generated feature subgroups
                    ├── create_device_queue2
                    │   └── basic
                    ├── create_instance_device_intentional_alloc_fail (not in Vulkan SC)
                    │   └── basic
                    ├── create_device_queue2_two_queues
                    │   └── basic
                    ├── create_device_queue2_all_protected
                    │   └── basic
                    ├── create_device_queue2_all_unprotected
                    │   └── basic
                    ├── create_device_queue2_split
                    │   └── basic
                    ├── create_device_queue2_all_families
                    │   └── basic
                    ├── create_device_queue2_all_families_protected
                    │   └── basic
                    └── create_device_queue2_all_combinations
                        └── basic
```

Evidence:
- package-level `api` attachment in [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1349) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1417)
- parent attachment in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L100)
- subgroup factory in [`createDeviceInitializationTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879)
- one-case subgroup helper in [`addFunctionCaseInNewSubgroup()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2850), which always creates a subgroup and inserts a single `basic` case

## Test Hierarchy

The top-level hierarchy directly confirmed from [`createDeviceInitializationTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2879) is:

```text
api
└── device_init
    ├── instance creation acceptance/rejection tests
    ├── device creation acceptance/rejection tests
    ├── global-priority device creation tests
    ├── features2 and unsupported-feature rejection tests
    └── vkGetDeviceQueue2 / protected-queue combination tests
```

More concretely:

- most subgroups are one-case wrappers whose only child is named `basic`, due to [`addFunctionCaseInNewSubgroup()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2850)
- [`create_device_unsupported_features`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2919) is different: it contains a visible `core` case plus additional generated children from [`addSeparateUnsupportedFeatureTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921)
- the queue2-related subgroups all use [`checkProtectedMemorySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1894) as their support gate in registration lines [`2933-2950`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2933)

## Test Families

### 1. Instance creation tolerance and rejection

The first six registered subgroups all target `VkInstance` creation behavior in progressively more adversarial ways:

- [`create_instance_name_version`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883) uses [`createInstanceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L66)
- [`create_instance_invalid_api_version`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2885) uses [`createInstanceWithInvalidApiVersionTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L211)
- [`create_instance_null_appinfo`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2887) uses [`createInstanceWithNullApplicationInfoTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L322)
- [`create_instance_unsupported_extensions`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2889) uses [`createInstanceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L353)
- [`create_instance_extension_name_abuse`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2891) uses [`createInstanceWithExtensionNameAbuseTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L471)
- [`create_instance_layer_name_abuse`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2893) uses [`createInstanceWithLayerNameAbuseTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L520)

Observed behavior from the inspected implementations:

- [`createInstanceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L66) generates many [`VkApplicationInfo`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L84) variants by iterating over app names, engine names, app/engine versions, patch-version variations, and an explicit `apiVersion == 0` case before attempting instance creation for each combination at [`vktApiDeviceInitializationTests.cpp#L181`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L181)
- [`createInstanceWithInvalidApiVersionTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L211) constructs deliberately nonstandard API-variant, major, and minor values, then distinguishes expected outcomes based on runtime API version and Vulkan SC compilation at [`vktApiDeviceInitializationTests.cpp#L268`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L268)
- [`createInstanceWithNullApplicationInfoTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L322) checks that `pApplicationInfo == nullptr` does not cause failure in the tested path
- [`createInstanceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L353) expects [`VK_ERROR_EXTENSION_NOT_PRESENT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L388) when two fake instance extensions are enabled
- [`createInstanceWithExtensionNameAbuseTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L471) reuses the UTF-8 abuse corpus produced by [`getUTF8AbuseString()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L410) and expects rejection with [`VK_ERROR_EXTENSION_NOT_PRESENT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L507)
- [`createInstanceWithLayerNameAbuseTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L520) uses the same abuse corpus for layer names and expects [`VK_ERROR_LAYER_NOT_PRESENT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L565)

### 2. Device creation smoke, repetition, and unsupported-extension rejection

The next registration block covers basic device creation behavior:

- [`create_device`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2899) uses [`createDeviceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L631)
- [`create_multiple_devices`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2900) uses [`createMultipleDevicesTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L693)
- [`create_device_unsupported_extensions`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2902) uses [`createDeviceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L811)
- [`create_device_various_queue_counts`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2904) uses [`createDeviceWithVariousQueueCountsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L897)

Observed themes:

- [`createDeviceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L631) creates a single queue from family index `0`, retrieves it, and requires [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L688) to succeed
- [`createMultipleDevicesTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L693) repeats device creation across multiple custom instances (`5` devices outside Vulkan SC, `2` in Vulkan SC) and destroys all created devices afterward at [`vktApiDeviceInitializationTests.cpp#L798`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L798)
- [`createDeviceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L811) enables three fake device extensions and expects [`VK_ERROR_EXTENSION_NOT_PRESENT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L875)
- [`createDeviceWithVariousQueueCountsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L897) enumerates all queue families, then iterates every queue count from `1` to each family maximum at [`vktApiDeviceInitializationTests.cpp#L911`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L911), creating a device for each choice and validating every created queue through [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L972)

### 3. Global-priority queue creation and query-based admissibility

Four adjacent registration entries form a coherent global-priority slice:

- [`create_device_global_priority`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2906) guarded by [`checkGlobalPrioritySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L985) with `useKhrGlobalPriority = false`
- [`create_device_global_priority_khr`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2909) with the same support helper but `useKhrGlobalPriority = true`
- [`create_device_global_priority_query`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2911) guarded by [`checkGlobalPriorityQuerySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1166) with `useKhrGlobalPriority = false`
- [`create_device_global_priority_query_khr`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2913) with `useKhrGlobalPriority = true`

Observed details:

- support gates require either `VK_EXT_global_priority`, `VK_KHR_global_priority`, or `VK_EXT_global_priority_query` depending on branch in [`checkGlobalPrioritySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L985) and [`checkGlobalPriorityQuerySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1166)
- [`createDeviceWithGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L991) iterates four priorities (`LOW`, `MEDIUM`, `HIGH`, `REALTIME`) at [`vktApiDeviceInitializationTests.cpp#L1000`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1000), tries device creation with queue priority pNext structures, and tolerates permission denial for priorities above medium via [`VK_ERROR_NOT_PERMITTED_KHR`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1114)
- in the KHR-query-aware path, the same function first queries [`VkQueueFamilyGlobalPriorityPropertiesKHR`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1011) and may require initialization failure when a requested priority falls outside the advertised range at [`vktApiDeviceInitializationTests.cpp#L1094`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1094)
- [`createDeviceWithQueriedGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1201) generalizes that logic across all queue families, validates queried priority arrays with [`checkGlobalPriorityProperties()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1186), and tests every family/priority pair against the queried admissible range at [`vktApiDeviceInitializationTests.cpp#L1242`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1242)

### 4. `VkPhysicalDeviceFeatures2` creation and unsupported-feature rejection

The next registration block covers feature-enabled device creation:

- [`create_device_features2`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2916) uses [`createDeviceFeatures2Test()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1324)
- [`create_device_unsupported_features`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2919) contains a `core` case backed by [`createDeviceWithUnsupportedFeaturesTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1641) plus more generated feature-specific cases through [`addSeparateUnsupportedFeatureTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921)

Observed details:

- [`createDeviceFeatures2Test()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1324) explicitly creates an instance with `VK_KHR_get_physical_device_properties2`, queries [`VkPhysicalDeviceFeatures2`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1337), passes that structure through `pNext` into [`VkDeviceCreateInfo`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1360), and validates the resulting queue with [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1387)
- [`checkFeatures()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1407) is the core negative-test helper for many generated unsupported-feature paths: for every reported-unsupported feature, it enables only that feature (plus visible prerequisites when needed), calls [`createUncheckedDevice()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1624), and requires [`VK_ERROR_FEATURE_NOT_PRESENT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1627)
- the inspected prerequisite adjustments in [`checkFeatures()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1441) include multiview dependencies, `variablePointers` implying `variablePointersStorageBuffer`, robustness2 implying core `robustBufferAccess`, sparse image atomic features implying corresponding non-sparse image atomic features, mesh-shader dependencies, and one ray-tracing dependency in non-Vulkan-SC builds
- [`createDeviceWithUnsupportedFeaturesTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1641) performs the same rejection principle for core [`VkPhysicalDeviceFeatures`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1663) by iterating many individual feature bits and expecting [`VK_ERROR_FEATURE_NOT_PRESENT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1765) whenever a reported-unsupported core feature is force-enabled

### 5. `vkGetDeviceQueue2` and protected-queue configuration tests

The final major family is a coherent protected-memory / queue2 branch:

- [`create_device_queue2`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2924) uses [`createDeviceQueue2Test()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1785)
- [`create_device_queue2_two_queues`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2934) uses [`createDeviceQueue2WithTwoQueuesSmokeTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2070)
- [`create_device_queue2_all_protected`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2936) uses [`createDeviceQueue2WithAllProtectedQueues()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2119)
- [`create_device_queue2_all_unprotected`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2938) uses [`createDeviceQueue2WithAllUnprotectedQueues()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2153)
- [`create_device_queue2_split`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2940) uses [`createDeviceQueue2WithNProtectedAndMUnprotectedQueues()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2222)
- [`create_device_queue2_all_families`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2944) uses [`createDeviceQueue2WithAllFamilies()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2383)
- [`create_device_queue2_all_families_protected`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2946) uses [`createDeviceQueue2WithAllFamiliesProtected()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2417)
- [`create_device_queue2_all_combinations`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2949) uses [`createDeviceQueue2WithMultipleQueueCombinations()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2284)

Observed behavior:

- all these cases are support-gated by [`checkProtectedMemorySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1894), which requires Vulkan 1.1 and `protectedMemory == VK_TRUE`
- [`createDeviceQueue2Test()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1785) enables protected memory, creates a protected queue with [`VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1818), then retrieves it through [`getDeviceQueue2()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1864)
- queue-family discovery is abstracted by [`findQueueFamiliesWithCaps()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1872), which filters families by required capability bits and throws when none match
- device creation for queue-combination tests is centralized in [`createProtectedDeviceWithQueueConfig()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1918), while queue retrieval is centralized in [`getDeviceQueue2WithOptions()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1992)
- [`runQueueCreationTestCombination()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2013) is the shared executor: it creates the device from a vector of queue-creation descriptors, queries every requested queue, and records pass/fail results based on whether the queue handle is non-null and [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2059) succeeds
- [`buildQueueConfigurations()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2189) generates all `N` protected / `M` unprotected splits for each protected-capable family, where `N + M == queueCount`
- [`createDeviceQueue2WithNProtectedAndMUnprotectedQueues()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2222) tests those single-family splits in both forward and reversed queue-create-info order
- [`createDeviceQueue2WithMultipleQueueCombinations()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2284) lifts that idea across multiple queue families by generating a Cartesian product of per-family configurations before executing both forward and reversed orders

### 6. Non-Vulkan-SC allocation-behavior special cases

Two registered branches are explicitly excluded from Vulkan SC builds:

- [`enumerate_devices_alloc_leak`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2896) runs [`enumerateDevicesAllocLeakTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L579), which records host-allocation callbacks around repeated [`enumeratePhysicalDevices()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L590) calls and fails if allocations and frees do not balance at [`vktApiDeviceInitializationTests.cpp#L625`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L625)
- [`create_instance_device_intentional_alloc_fail`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2928) is registered, but its implementation was not inspected in this run because the chosen documentation slice centers on foundational initialization families above; therefore only its registration presence is claimed here

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Top-level subgroup names | All names registered in [`createDeviceInitializationTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2883) |
| Per-subgroup child naming | Most groups contain one child named `basic` via [`addFunctionCaseInNewSubgroup()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2850); [`create_device_unsupported_features`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2919) instead contains `core` plus generated children |
| Instance app-name values | `"appName"`, `nullptr`, `""`, punctuation-heavy names, newline-containing names in [`createInstanceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L70) |
| Instance engine-name values | analogous engine-name variants in [`createInstanceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L72) |
| API patch values tested for instance creation | `0, 1, 2, 3, 4, 5, 13, 4094, 4095` in [`patchNumbers`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L75) |
| Invalid API-version dimensions | invalid variant, invalid major, invalid minor, and extra Vulkan-SC-only invalid cases in [`createInstanceWithInvalidApiVersionTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L222) |
| UTF-8 abuse corpus | long name, illegal bytes, overlong-NUL, overlong encodings, zalgo text, Chinese text, empty string in [`getUTF8AbuseString()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L410) |
| Unsupported extension-name lists | instance list has two fake names in [`createInstanceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L356); device list has three fake names in [`createDeviceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L817) |
| Queue-count sweep | every queue family, with queue counts from `1` to family `queueCount` in [`createDeviceWithVariousQueueCountsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L911) |
| Global-priority values | `LOW`, `MEDIUM`, `HIGH`, `REALTIME` in [`createDeviceWithGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1000) and [`createDeviceWithQueriedGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1209) |
| Unsupported core feature set | long explicit list of core feature bits beginning with [`fullDrawIndexUint32`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1665) and ending with [`inheritedQueries`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1718) |
| Queue2 split dimensions | per-family protected/unprotected splits generated in [`buildQueueConfigurations()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2189) |
| Multi-family queue-combination dimension | Cartesian product of per-family queue configurations in [`createDeviceQueue2WithMultipleQueueCombinations()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2299) |

## Support / Feature Requirements

Observed support requirements include:

- several subgroups are compiled out for Vulkan SC in [`createDeviceInitializationTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2895)
- global-priority tests require corresponding device extensions through [`checkGlobalPrioritySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L985) and [`checkGlobalPriorityQuerySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1166)
- some global-priority paths add `VK_KHR_get_physical_device_properties2` when the context does not already support Vulkan 1.1 in [`createDeviceWithGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1042) and [`createDeviceWithQueriedGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1237)
- protected-queue tests require Vulkan 1.1 plus `protectedMemory == VK_TRUE` via [`checkProtectedMemorySupport()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1894)
- [`createDeviceQueue2Test()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1812) also explicitly aborts when protected memory is not supported
- unsupported-feature rejection uses runtime-reported supported feature sets from [`DeviceFeatures`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1654) and from queried feature structures inside [`checkFeatures()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1427)
- many creation helpers inject Vulkan-SC reservation and SC-feature structures under `#ifdef CTS_USES_VULKANSC`, for example in [`createDeviceTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L656), [`createDeviceWithVariousQueueCountsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L932), and [`checkFeatures()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1597)

## Verification Methods

High-confidence verification methods visible in inspected code are:

- **success/failure by Vulkan result code**: many tests explicitly require `VK_SUCCESS`, `VK_ERROR_EXTENSION_NOT_PRESENT`, `VK_ERROR_LAYER_NOT_PRESENT`, or `VK_ERROR_FEATURE_NOT_PRESENT`, such as [`createInstanceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L388), [`createDeviceWithUnsupportedExtensionsTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L875), and [`checkFeatures()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1627)
- **queue usability check**: successful device-creation paths commonly retrieve queues and call [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L688), [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L775), or [`queueWaitIdle()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2059)
- **enumeration-stability / leak accounting**: [`enumerateDevicesAllocLeakTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L579) counts allocation and free callbacks and fails when the count is nonzero at [`vktApiDeviceInitializationTests.cpp#L625`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L625)
- **queried-range consistency**: queried global-priority families are validated by checking `priorityCount`, legal enum values, monotonic doubling order, and whether requested priorities lie inside the advertised range in [`checkGlobalPriorityProperties()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1186) and [`createDeviceWithQueriedGlobalPriorityTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1279)
- **reported-unsupported implies creation rejection**: both core-feature and pNext-feature negative tests force-enable unsupported features and require `VK_ERROR_FEATURE_NOT_PRESENT` in [`createDeviceWithUnsupportedFeaturesTest()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1765) and [`checkFeatures()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1627)
- **queue-handle presence**: queue2-combination tests treat null queue handles as failures in [`runQueueCreationTestCombination()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2057)

## Test Principles Observed

- **Probe initialization robustness by varying creation metadata rather than using later functionality**: the earliest instance tests focus on acceptance or rejection of different `VkApplicationInfo`, extension-name, and layer-name inputs
- **Use negative initialization tests to check strict error signaling**: unsupported extensions and unsupported features are expected to fail with specific Vulkan error codes rather than generic failure
- **Scale queue-creation coverage combinatorially**: the queue2 branch systematically spans queue counts, protected/unprotected splits, reversed orderings, and multi-family products instead of relying on only a smoke test
- **Treat runtime-reported capabilities as the oracle for negative tests**: unsupported-feature checks first query supported bits and only then try enabling absent ones
- **Differentiate build variants explicitly**: the registration tree and some expectations differ under [`CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2895)

## Notes / Uncertainties

- This document intentionally covers one coherent foundational slice centered on the full `device_init` branch registered at [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L100). It does not attempt to synthesize adjacent branches such as [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiTests.cpp#L101), [`createBufferTests()`](../../modules/vulkan/api/vktApiTests.cpp#L102), or the grouped [`buffer_view`](../../modules/vulkan/api/vktApiTests.cpp#L106) subtree.
- [`create_instance_device_intentional_alloc_fail`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2928) is only documented at registration level here. Its internal implementation was not inspected in this run, so no stronger claims are made about its detailed verification logic.
- The generated children added by [`addSeparateUnsupportedFeatureTests()`](../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2921) were not exhaustively enumerated from [`vkDeviceFeatureTest.inl`](../../modules/vulkan/api/vkDeviceFeatureTest.inl). The safe claim is that the subgroup contains additional generated unsupported-feature cases beyond the visible `core` case.
- Some local variables such as queried queue-family property vectors are populated but not deeply analyzed for every helper. Claims above are limited to logic directly confirmed in the inspected lines.
