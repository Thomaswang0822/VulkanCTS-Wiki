## Overview

**Core question: does the implementation accept every valid instance/device/queue-creation configuration the Vulkan spec permits, and reject every clearly invalid one?**

- The `api.device_init` test family lives under the `api` test category and is implemented end-to-end in [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1).
- It registers 26 intermediate nodes under `api.device_init`, each exercising one instance-creation, device-creation, or queue-creation scenario through [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2868-L2942).
- Most intermediate nodes carry a single `basic` test case leaf; `create_device_unsupported_features` is the exception, expanding into one `core` leaf plus 208 per-feature leaves generated via [`addSeparateUnsupportedFeatureTests()`](../../../framework/vulkan/generated/vulkan/vkDeviceFeatureTest.inl#L9041-L9042).
- The page maps each scenario to what is checked, what a failure means, and which configurations are pruned by support gates or by Vulkan SC build guards.
- No shaders are involved anywhere in this family; all verification is host-side `vkCreateInstance` / `vkCreateDevice` / `vkGetDeviceQueue2` behavior plus, in two cases, allocation-callback accounting.

## Background Knowledge

- **VkInstance and VkDevice creation flow.** `vkCreateInstance` takes a `VkApplicationInfo*` (which may be `NULL`) and a layer/extension list; `vkCreateDevice` takes a `VkDeviceCreateInfo` whose `pQueueCreateInfos` describe the logical queues requested. The tests drive these entry points through helpers in `vktApiDeviceInitializationTests.cpp` and inspect the returned `VkResult` rather than relying on the higher-level `vkt::api::Device` wrapper.
- **`VkDeviceQueueCreateFlagBits`.** `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` requests a protected-capable queue from a queue family that advertises `VK_QUEUE_PROTECTED_BIT`. Several `create_device_queue2_*` intermediate nodes mix protected and unprotected queues from one or more families; the test passes only when every requested queue can be retrieved through `vkGetDeviceQueue2` with the matching flags.
- **Global priority queues (`VK_EXT_global_priority`, `VK_KHR_global_priority`).** These extensions let `VkDeviceQueueCreateInfo::pNext` carry a `VkDeviceQueueGlobalPriorityCreateInfoKHR` selecting `LOW`/`MEDIUM`/`HIGH`/`REALTIME`. The spec permits the implementation to deny `HIGH` and `REALTIME` with `VK_ERROR_NOT_PERMITTED_KHR`, and requires `VK_ERROR_INITIALIZATION_FAILED` when the requested priority is outside the range reported via `VkQueueFamilyGlobalPriorityPropertiesKHR`. The four `create_device_global_priority*` nodes encode this contract.
- **Allocation callbacks.** `VkAllocationCallbacks` let the test intercept host allocations. `enumerate_devices_alloc_leak` records allocations made during `vkEnumeratePhysicalDevices` and confirms they balance; `create_instance_device_intentional_alloc_fail` repeatedly retries instance/device creation while failing one allocation at a time, expecting `VK_ERROR_OUT_OF_HOST_MEMORY` and a fully balanced tracker on every retry.

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

The family is built in [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2868-L2942) and attached to the `api` test category at [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L100). Each helper-created intermediate node wraps a single `basic` test case leaf through [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2839-L2866). The `create_device_unsupported_features` intermediate node is built explicitly: a `core` leaf via [`addFunctionCase(subgroup.get(), "core", createDeviceWithUnsupportedFeaturesTest)`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2908-L2911) plus 208 per-feature leaves generated from `vkDeviceFeatureTest.inl`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | 26 names listed in the tree above | Each intermediate node selects one scenario: instance creation, device creation, queue configuration, global priority, unsupported-feature rejection, or allocation-callback behavior. | [`createDeviceInitializationTests()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2872-L2939) |
| Test case leaf under wrapper nodes | `basic` | The single executable case per wrapper intermediate node; the helper `addFunctionCaseInNewSubgroup` always names it `basic`. | [`addFunctionCaseInNewSubgroup()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2839-L2866) |
| Test case leaves under `create_device_unsupported_features` | `core` plus 208 per-feature leaves such as `16_bit_storage_features`, `buffer_device_address_features`, `descriptor_indexing_features`, `host_query_reset_features`, `robustness2_features_khr`, `dynamic_rendering_features`, ... | `core` enumerates the legacy `VkPhysicalDeviceFeatures` bitfields; each per-feature leaf targets one `VkBool32` member of an extension feature struct and expects `VK_ERROR_FEATURE_NOT_PRESENT` when that feature was reported unsupported. | [`addSeparateUnsupportedFeatureTests()`](../../../framework/vulkan/generated/vulkan/vkDeviceFeatureTest.inl#L9041-L9042); mustpass `dEQP-VK.api.device_init.create_device_unsupported_features.*` |
| Global priority value | `VK_QUEUE_GLOBAL_PRIORITY_LOW_KHR`, `VK_QUEUE_GLOBAL_PRIORITY_MEDIUM_KHR`, `VK_QUEUE_GLOBAL_PRIORITY_HIGH_KHR`, `VK_QUEUE_GLOBAL_PRIORITY_REALTIME_KHR` | Walked per queue family in the queried-priority variants; `HIGH` and `REALTIME` may be denied, out-of-range priorities must fail. | [`createDeviceWithGlobalPriorityTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L986-L1157), [`createDeviceWithQueriedGlobalPriorityTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1195-L1316) |
| Queue configuration (queue2 variants) | single-family two-queue split, all-protected, all-unprotected, every N+M split, all-families, all-families-protected, full multi-family combination | Each leaf constructs a different `VkDeviceQueueCreateInfo` vector with `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` toggled per family, then verifies every queue can be retrieved. | [`createDeviceQueue2With*`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2059-L2444) |
| Build guard | `CTS_USES_VULKANSC` excludes 5 intermediate nodes | `enumerate_devices_alloc_leak`, `create_device_global_priority_khr`, `create_device_global_priority_query`, `create_device_global_priority_query_khr`, and `create_instance_device_intentional_alloc_fail` are compiled out for Vulkan SC. | [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2884-L2887) |

## Behavior Parameters

The primary behavioral axis is the intermediate node: each value selects a distinct initialization scenario. The 26 intermediate nodes group into eight thematic clusters. Subsections below describe each cluster; per-node detail is kept short because the registered name already identifies the scenario.

### Instance creation variants (`create_instance_*`)

Six intermediate nodes drive `vkCreateInstance` with a controlled `VkApplicationInfo` or layer/extension list and check the implementation's response.

- `create_instance_name_version` iterates over `appNames`, `engineNames`, `appVersions`, `engineVersions`, and patch-number variants of the API version, plus an `apiVersion == 0` case; every combination must create an instance successfully ([`createInstanceTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L66-L209)).
- `create_instance_invalid_api_version` feeds deliberately overflowed variant/major/minor bitfields. Vulkan 1.0 may reject with `VK_ERROR_INCOMPATIBLE_DRIVER`; Vulkan 1.1 and later must not return `VK_ERROR_INCOMPATIBLE_DRIVER` for nonstandard but in-range variant versions ([`createInstanceWithInvalidApiVersionTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L211-L320)).
- `create_instance_null_appinfo` passes `pApplicationInfo = NULL` and expects success ([`createInstanceWithNullApplicationInfoTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L322-L351)).
- `create_instance_unsupported_extensions` enables `VK_UNSUPPORTED_EXTENSION` and `THIS_IS_NOT_AN_EXTENSION`; the result must be `VK_ERROR_EXTENSION_NOT_PRESENT` and no instance handle ([`createInstanceWithUnsupportedExtensionsTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L353-L396)).
- `create_instance_extension_name_abuse` and `create_instance_layer_name_abuse` walk seven UTF-8 abuse strings (long, illegal bytes, overlong NUL, overlong sequences, "zalgo", Chinese glyphs, empty string) as fake extension or layer names; each must be rejected with `VK_ERROR_EXTENSION_NOT_PRESENT` or `VK_ERROR_LAYER_NOT_PRESENT` respectively ([`createInstanceWithExtensionNameAbuseTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L471-L518), [`createInstanceWithLayerNameAbuseTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L520-L576)).

### Device enumeration and allocation tracking (`enumerate_devices_alloc_leak`)

Single intermediate node, excluded from Vulkan SC. Installs an `AllocationCallbackRecorder` around the instance, calls `vkEnumeratePhysicalDevices` twice, and asserts that the number of recorded allocations matches the number of non-NULL frees ([`enumerateDevicesAllocLeakTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L579-L628)). A non-zero allocation balance fails the test; an out-of-memory error other than `VK_ERROR_OUT_OF_HOST_MEMORY` (such as `VK_ERROR_OUT_OF_DEVICE_MEMORY`) from `vkEnumeratePhysicalDevices` produces a quality warning rather than continuing to the balance check, while `VK_ERROR_OUT_OF_HOST_MEMORY` falls through to the balance check.

### Basic device creation (`create_device`, `create_multiple_devices`, `create_device_unsupported_extensions`, `create_device_various_queue_counts`)

- `create_device` is the smoke test: one queue family, one queue, `vkQueueWaitIdle` returns `VK_SUCCESS` ([`createDeviceTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L631-L689)).
- `create_multiple_devices` creates 5 devices (2 on Vulkan SC) on separate custom instances and waits each queue idle; partial success is reported through a `ResultCollector` ([`createMultipleDevicesTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L691-L806)).
- `create_device_unsupported_extensions` enables three fake extension names and requires `VK_ERROR_EXTENSION_NOT_PRESENT` ([`createDeviceWithUnsupportedExtensionsTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L809-L879)).
- `create_device_various_queue_counts` walks every queue family and every queue count from 1 to the family's reported maximum, retrieves each queue, and requires every `vkQueueWaitIdle` to return `VK_SUCCESS` ([`createDeviceWithVariousQueueCountsTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L893-L978)).

### Global priority queues (`create_device_global_priority*`)

Four intermediate nodes form a 2×2 matrix over the extension (`VK_EXT_global_priority` versus `VK_KHR_global_priority`) and the query path (direct creation versus querying `VkQueueFamilyGlobalPriorityPropertiesKHR` first). All four walk the four priority enums.

- `create_device_global_priority` uses the EXT extension name ([`createDeviceWithGlobalPriorityTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L986-L1157) with `useKhrGlobalPriority=false`).
- `create_device_global_priority_khr` switches the enabled extension to `VK_KHR_global_priority` (same function, `useKhrGlobalPriority=true`).
- `create_device_global_priority_query` and `create_device_global_priority_query_khr` add the corresponding query extension, call `vkGetPhysicalDeviceQueueFamilyProperties2` with the priority-properties struct, validate that the returned priorities are well-formed via [`checkGlobalPriorityProperties()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1180-L1191), and require device creation to fail with `VK_ERROR_INITIALIZATION_FAILED` when the requested priority is outside the reported range ([`createDeviceWithQueriedGlobalPriorityTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1195-L1316)).

For all four, `HIGH` and `REALTIME` may be denied with `VK_ERROR_NOT_PERMITTED_KHR` (`VK_ERROR_NOT_PERMITTED_EXT` in the EXT path); the test continues in that case. Any other failure terminates the test as a failure.

### Features2 path (`create_device_features2`)

Single intermediate node creating a device through the `VkPhysicalDeviceFeatures2` pNext chain rather than the legacy `pEnabledFeatures` pointer ([`createDeviceFeatures2Test()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1318-L1383)). The instance is created with `VK_KHR_get_physical_device_properties2`, `vkGetPhysicalDeviceFeatures2` populates the struct, and the resulting device must accept it and reach `vkQueueWaitIdle` returning `VK_SUCCESS`.

### Unsupported-feature rejection (`create_device_unsupported_features`)

This intermediate node has 209 test case leaves and is the only node with a non-`basic` leaf shape.

- The `core` leaf enumerates 54 `VkBool32` fields of `VkPhysicalDeviceFeatures` (excluding `robustBufferAccess`, which is always supported), enables each unsupported feature one at a time, and requires `VK_ERROR_FEATURE_NOT_PRESENT` from `vkCreateDevice` ([`createDeviceWithUnsupportedFeaturesTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1632-L1772)).
- The 208 per-feature leaves are generated from `vkDeviceFeatureTest.inl`. Each leaf targets one `VkBool32` member of an extension feature struct, queries the supported features, enables the unsupported member, and expects `VK_ERROR_FEATURE_NOT_PRESENT`. The shared driver is [`checkFeatures()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1399-L1630), which also enables any prerequisite features the Vulkan spec mandates (for example `multiview` when `multiviewGeometryShader` is requested, `variablePointersStorageBuffer` when `variablePointers` is requested, `robustBufferAccess` when `robustBufferAccess2` is requested, `shaderImageFloat32Atomics` when `sparseImageFloat32Atomics` is requested).

### Queue2 and protected memory (`create_device_queue2*`)

Eight intermediate nodes use Vulkan 1.1's `vkGetDeviceQueue2` and `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT`. The `checkProtectedMemorySupport` gate throws `NotSupportedError` when the device lacks protected memory ([`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1884-L1906)).

- `create_device_queue2` is the smoke test: one protected-capable queue, retrieved via `vkGetDeviceQueue2` ([`createDeviceQueue2Test()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1776-L1860)). It performs the same Vulkan 1.1 and `protectedMemory` check internally instead of through the registered support hook.
- `create_device_queue2_two_queues` is a smoke test that finds the first protected-capable family with `queueCount >= 2` and creates one protected plus one unprotected queue from it ([`createDeviceQueue2WithTwoQueuesSmokeTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2059-L2106)).
- `create_device_queue2_all_protected` walks every protected-capable family and creates the maximum reported count of protected queues ([`createDeviceQueue2WithAllProtectedQueues()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2108-L2140)).
- `create_device_queue2_all_unprotected` walks every queue family (no flag requirement) and creates the maximum reported count of unprotected queues ([`createDeviceQueue2WithAllUnprotectedQueues()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2142-L2173)).
- `create_device_queue2_split` walks every protected-capable family and, for every N+M split where `N+M == queueCount`, creates N protected and M unprotected queues from the same family. Each split is also run in reversed `VkDeviceQueueCreateInfo` order ([`createDeviceQueue2WithNProtectedAndMUnprotectedQueues()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2211-L2271)).
- `create_device_queue2_all_families` creates one `VkDeviceQueueCreateInfo` per queue family, each requesting the maximum count, all unprotected ([`createDeviceQueue2WithAllFamilies()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2372-L2404)).
- `create_device_queue2_all_families_protected` does the same but adds `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` to families that advertise `VK_QUEUE_PROTECTED_BIT` ([`createDeviceQueue2WithAllFamiliesProtected()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2406-L2444)).
- `create_device_queue2_all_combinations` builds the full cartesian product of per-family N+M splits across all protected-capable families and runs each combination in both original and reversed order ([`createDeviceQueue2WithMultipleQueueCombinations()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2273-L2370)).

All eight share [`runQueueCreationTestCombination()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2002-L2057), which creates the device, retrieves every requested queue through `vkGetDeviceQueue2` with the matching flags, and fails the test if any retrieved queue is `VK_NULL_HANDLE` or any `vkQueueWaitIdle` returns a non-`VK_SUCCESS` result.

### Intentional allocation failure (`create_instance_device_intentional_alloc_fail`)

Single intermediate node, excluded from Vulkan SC. The test installs a custom `VkAllocationCallbacks` that tracks every allocation and can be told to fail one specific allocation index. It first measures how many allocations a successful instance+device creation requires, then retries creation while failing each allocation index in turn. Each failed attempt must return `VK_ERROR_OUT_OF_HOST_MEMORY` from `vkCreateInstance`, `vkEnumeratePhysicalDevices`, or `vkCreateDevice`, must leave the allocation tracker empty (no leaks), and must not return any other error code ([`createInstanceDeviceIntentionalAllocFail()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2618-L2833)). The source comment above the registration notes this test is excluded from Vulkan SC because in the SC main process it does not really create any instance or device and the creation calls always return `VK_SUCCESS`.

## Shader Analysis

No shader is involved in this test family. Every test case leaf drives host-side Vulkan entry points and inspects the returned `VkResult` and queue handles. The `## Shader Analysis` section therefore has no representative walkthrough subsections.

## Runtime Execution and Result Checking

All verification is host-side. The shared execution shape across the family is:

- Create a `CustomInstance` through `createCustomInstanceFromContext` / `createCustomInstanceWithExtension` / `createCustomInstanceFromInfo`, optionally with a custom `VkAllocationCallbacks`.
- Pick a `VkPhysicalDevice` via `chooseDevice`.
- Build a `VkDeviceQueueCreateInfo` vector (or a single struct) matching the scenario.
- Build a `VkDeviceCreateInfo`, optionally chaining `VkPhysicalDeviceFeatures2`, `VkPhysicalDeviceProtectedMemoryFeatures`, `VkDeviceQueueGlobalPriorityCreateInfoKHR`, `VkPhysicalDeviceGlobalPriorityQueryFeaturesEXT`, or the Vulkan SC reservation structs in `pNext`.
- Call `createCustomDevice` (which expects `VK_SUCCESS`) or `createUncheckedDevice` (which returns the raw `VkResult`) depending on whether the test wants to inspect a non-success result.
- Retrieve queues via `vkGetDeviceQueue` or `vkGetDeviceQueue2` and call `vkQueueWaitIdle` to confirm the queue is usable.
- Aggregate per-iteration results through a `tcu::ResultCollector` for the multi-iteration tests, or return `pass` / `fail` directly for single-shot tests.

Pass conditions per cluster:

- Instance creation variants: every iteration returns `VK_SUCCESS` (or, for the invalid-API-version and unsupported-extension/layer cases, the spec-mandated rejection result).
- Device creation variants: `VK_SUCCESS` for the smoke and queue-count tests, `VK_ERROR_EXTENSION_NOT_PRESENT` for unsupported extensions.
- Global priority variants: `VK_SUCCESS` for in-range priorities, `VK_ERROR_NOT_PERMITTED_KHR` allowed for `HIGH`/`REALTIME`, `VK_ERROR_INITIALIZATION_FAILED` required for out-of-range priorities in the query variants.
- Features2: `VK_SUCCESS` end-to-end.
- Unsupported features: `VK_ERROR_FEATURE_NOT_PRESENT` for every unsupported feature the test enables.
- Queue2 variants: every retrieved queue is non-NULL and every `vkQueueWaitIdle` returns `VK_SUCCESS`.
- Allocation failure: each retry returns `VK_ERROR_OUT_OF_HOST_MEMORY` and leaves the allocation tracker balanced; the final successful retry returns `VK_SUCCESS`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `create_instance_name_version`, `create_instance_null_appinfo`, `create_device`, `create_multiple_devices`, `create_device_various_queue_counts`, `create_device_features2` | Valid-configuration rejection: implementation refuses a spec-permitted instance/device configuration, or returns a queue that cannot reach idle. |
| `create_instance_invalid_api_version` | API-version validation: implementation rejects an in-range nonstandard version that the spec requires to succeed, or accepts an out-of-range version that should produce `VK_ERROR_INCOMPATIBLE_DRIVER`. |
| `create_instance_unsupported_extensions`, `create_device_unsupported_extensions`, `create_instance_extension_name_abuse`, `create_instance_layer_name_abuse` | Unsupported-name acceptance: implementation creates an instance or device when the spec requires `VK_ERROR_EXTENSION_NOT_PRESENT` or `VK_ERROR_LAYER_NOT_PRESENT`. |
| `enumerate_devices_alloc_leak` | Allocation leak inside `vkEnumeratePhysicalDevices`: the implementation does not free one or more host allocations made during enumeration. |
| `create_device_global_priority`, `create_device_global_priority_khr`, `create_device_global_priority_query`, `create_device_global_priority_query_khr` | Global-priority handling: implementation accepts a priority outside the reported range, denies an in-range `LOW`/`MEDIUM` priority, or returns an unexpected error code for `HIGH`/`REALTIME`. |
| `create_device_unsupported_features` (any leaf) | Unsupported-feature acceptance: implementation creates a device with a feature that was reported as unsupported, instead of returning `VK_ERROR_FEATURE_NOT_PRESENT`. |
| `create_device_queue2`, `create_device_queue2_two_queues`, `create_device_queue2_all_protected`, `create_device_queue2_all_unprotected`, `create_device_queue2_split`, `create_device_queue2_all_families`, `create_device_queue2_all_families_protected`, `create_device_queue2_all_combinations` | Queue retrieval or wait failure: `vkGetDeviceQueue2` returns `VK_NULL_HANDLE` for a requested queue, or `vkQueueWaitIdle` returns a non-`VK_SUCCESS` result, for a queue configuration the spec permits. |
| `create_instance_device_intentional_alloc_fail` | Allocation-failure handling: implementation returns a non-`VK_ERROR_OUT_OF_HOST_MEMORY` error when an allocation is intentionally failed, or leaks allocations across a failed retry. |

### Cause Analysis

#### Valid-configuration rejection

**Possible failure symptoms:** `vkCreateInstance`, `vkCreateDevice`, or `vkQueueWaitIdle` returns an error code for a configuration the spec permits; `vkGetDeviceQueue` returns `VK_NULL_HANDLE` for an in-range queue index; the `ResultCollector` accumulates a non-pass status for one or more iterations of the multi-iteration tests.

**Possible implementation causes:** Driver rejecting valid `VkApplicationInfo` field combinations (empty strings, `NULL` `pApplicationInfo`, full 32-bit `appVersion`/`engineVersion`, non-zero patch in `apiVersion`); driver rejecting the maximum reported `queueCount` for a queue family; device creation failing because the chained `VkPhysicalDeviceFeatures2` is processed incorrectly; queue object loss between `vkCreateDevice` and `vkGetDeviceQueue`. Spec-level investigation is needed before attributing a specific iteration failure to a particular driver subsystem, because the failing iteration's logged `appName` / `engineName` / queue configuration identifies the input but not the rejection layer.

#### API-version validation

**Possible failure symptoms:** `createInstanceWithInvalidApiVersionTest` records `Fail, instance creation with invalid apiVersion is not rejected` (Vulkan 1.0 path) or `Fail, instance creation must not return VK_ERROR_INCOMPATIBLE_DRIVER for Vulkan 1.1` (Vulkan 1.1+ path).

**Possible implementation causes:** The implementation does not validate that the `apiVersion` variant, major, or minor bitfields fit in their bit-widths as defined by `VK_MAKE_API_VERSION`; the implementation returns `VK_ERROR_INCOMPATIBLE_DRIVER` for a nonstandard-but-in-range version on Vulkan 1.1+, which the spec text in the `VK_VERSION_1_1` promotion notes forbids. Source-level inspection of the implementation's version check is needed to confirm which condition triggers a given failure.

#### Unsupported-name acceptance

**Possible failure symptoms:** `createInstanceWithUnsupportedExtensionsTest` returns `Fail, creating instance with unsupported extensions succeeded.`; `createInstanceWithExtensionNameAbuseTest` or `createInstanceWithLayerNameAbuseTest` increments `failCount` for any abuse string; `createDeviceWithUnsupportedExtensionsTest` returns `Fail, create device with unsupported extension but succeeded.`

**Possible implementation causes:** The instance or device layer accepts an unrecognized extension or layer name without returning `VK_ERROR_EXTENSION_NOT_PRESENT` or `VK_ERROR_LAYER_NOT_PRESENT`; the implementation does not sanitize UTF-8 in extension/layer names before lookup, so overlong or illegal-byte strings match a different code path. The spec requires rejection of unrecognized names; source-level investigation is needed to identify which validation gap allows acceptance.

#### Allocation leak inside `vkEnumeratePhysicalDevices`

**Possible failure symptoms:** `enumerateDevicesAllocLeakTest` returns `Fail, enumeratePhysicalDevices leaked memory` with a non-zero `allocationRecords` balance; the test may also produce a quality warning if `vkEnumeratePhysicalDevices` itself throws an out-of-memory error other than `VK_ERROR_OUT_OF_HOST_MEMORY` (such as `VK_ERROR_OUT_OF_DEVICE_MEMORY`), in which case the catch returns early and leak accounting is skipped, while `VK_ERROR_OUT_OF_HOST_MEMORY` falls through to the balance check.

**Possible implementation causes:** The implementation allocates host memory during enumeration through the instance-provided allocator but does not free it before the call returns; the implementation routes some internal allocations outside the user-supplied `VkAllocationCallbacks` and then frees them later, breaking the recorder's accounting. Both would surface as a non-zero allocation balance in [`enumerateDevicesAllocLeakTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L579-L628). Source-level investigation is needed to identify which allocations are leaked.

#### Global-priority handling

**Possible failure symptoms:** `createDeviceWithGlobalPriorityTest` logs `device creation must fail but not` for an out-of-range priority in the KHR path; `vkQueueWaitIdle` returns a non-`VK_SUCCESS` and non-`VK_ERROR_NOT_PERMITTED_KHR` result for an in-range `LOW`/`MEDIUM` priority; `createDeviceWithQueriedGlobalPriorityTest` records `device creation must fail but not` when the requested priority is below the first or above the last entry of `VkQueueFamilyGlobalPriorityPropertiesEXT::priorities`.

**Possible implementation causes:** The implementation does not compare the requested priority against the queried range before device creation, so out-of-range priorities succeed when they should return `VK_ERROR_INITIALIZATION_FAILED`; the implementation denies `LOW` or `MEDIUM`, which the spec does not permit; the implementation returns an unrelated error code for `HIGH` or `REALTIME` instead of `VK_ERROR_NOT_PERMITTED_KHR` / `VK_ERROR_NOT_PERMITTED_EXT`. The spec contract is explicit in the `VK_KHR_global_priority` extension; source-level investigation is needed to confirm which check is missing.

#### Unsupported-feature acceptance

**Possible failure symptoms:** `checkFeatures` increments `numErrors` and the `ResultCollector` records `Not returning VK_ERROR_FEATURE_NOT_PRESENT when creating device with feature <name>, which was reported as unsupported.` for one or more per-feature leaves.

**Possible implementation causes:** The implementation does not cross-check the enabled feature bits against `vkGetPhysicalDeviceFeatures2` output during `vkCreateDevice`, so an unsupported feature is silently accepted; the implementation reports a feature as unsupported in the query but supports it internally, creating an inconsistency that the test catches. The `core` leaf enumerates `VkPhysicalDeviceFeatures` members, while the per-feature leaves enumerate extension struct members, so the failing leaf name identifies whether the gap is in core or extension feature validation. Source-level investigation is needed to identify the specific feature check that was bypassed.

#### Queue retrieval or wait failure

**Possible failure symptoms:** `runQueueCreationTestCombination` records `Unable to access the Queue. (queueFamilyIndex: ..., flags: ..., queue Index: ...)` because `vkGetDeviceQueue2` returned `VK_NULL_HANDLE`; or it records a `vkQueueWaitIdle` failure for a retrieved queue.

**Possible implementation causes:** The implementation does not honor `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` in `VkDeviceQueueInfo2::flags` during `vkGetDeviceQueue2`, so a protected queue created by `vkCreateDevice` cannot be retrieved; the implementation caps the actual number of queues below the reported `queueCount`, so high queue indices return `VK_NULL_HANDLE`; the implementation rejects a multi-family configuration that the spec permits, so `vkCreateDevice` itself fails before any queue can be retrieved. Spec-level investigation of the `VK_KHR_device_group_creation` and `VK_KHR_protected_memory` rules is needed before attributing a specific failure to a particular queue-creation rule.

#### Allocation-failure handling

**Possible failure symptoms:** `createInstanceDeviceIntentionalAllocFail` returns `Could not create instance and device` (the first successful measurement never completed), `Out of retries, could not create instance and device` (too many intentional failures without success), `Allocations still remain, failed on index <N>` (a leak), or `createInstance returned <code>` / `VkCreateDevice returned <code>` / `enumeratePhysicalDevices returned <code>` for any non-`VK_ERROR_OUT_OF_HOST_MEMORY` error.

**Possible implementation causes:** The implementation does not propagate allocation failure from one of its internal allocation scopes back to the caller as `VK_ERROR_OUT_OF_HOST_MEMORY`; the implementation partially constructs an object before failing and does not roll back all allocations, leaving the tracker non-empty; the implementation returns a different error code (for example `VK_ERROR_OUT_OF_DEVICE_MEMORY` or `VK_ERROR_INITIALIZATION_FAILED`) when host allocation fails. The allocation scope that fails is identified by the `failIndex` and the call site (`vkCreateInstance`, `vkEnumeratePhysicalDevices`, or `vkCreateDevice`); source-level investigation is needed to identify which internal allocation is not rolled back.

## Case Pruning

### Requirement-based pruning

- The seven `create_device_queue2_*` protected-memory variants (from `create_device_queue2_two_queues` through `create_device_queue2_all_combinations`) throw `NotSupportedError` through the registered [`checkProtectedMemorySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1884-L1906) hook when the device does not support Vulkan 1.1 or does not advertise `protectedMemory` in `VkPhysicalDeviceProtectedMemoryFeatures`. The `create_device_queue2` smoke test performs the same check internally at the start of its body ([`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1803-L1804)) instead of through the registered hook.
- `create_device_global_priority` and `create_device_global_priority_khr` require `VK_EXT_global_priority` or `VK_KHR_global_priority` respectively through [`checkGlobalPrioritySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L980-L984).
- `create_device_global_priority_query` and `create_device_global_priority_query_khr` require `VK_EXT_global_priority_query` or `VK_KHR_global_priority` through [`checkGlobalPriorityQuerySupport()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1160-L1164).
- `create_device_queue2_two_queues` skips with `NotSupportedError` when no protected-capable queue family reports `queueCount >= 2` ([`createDeviceQueue2WithTwoQueuesSmokeTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2086-L2088)).
- `create_device_queue2_all_protected`, `create_device_queue2_split`, `create_device_queue2_all_families_protected`, and `create_device_queue2_all_combinations` skip when no queue family advertises `VK_QUEUE_PROTECTED_BIT` (via `findQueueFamiliesWithCaps` in [`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1862-L1882)).
- Within `create_device_unsupported_features`, the per-iteration loop in [`checkFeatures()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1417-L1421) and [`createDeviceWithUnsupportedFeaturesTest()`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1711-L1715) skips any feature that the device already reports as supported, because requesting a supported feature cannot produce `VK_ERROR_FEATURE_NOT_PRESENT`.

### Design-based pruning

- Five intermediate nodes are compiled out for Vulkan SC builds through `#ifndef CTS_USES_VULKANSC` guards: `enumerate_devices_alloc_leak`, `create_device_global_priority_khr`, `create_device_global_priority_query`, `create_device_global_priority_query_khr`, and `create_instance_device_intentional_alloc_fail`. The source comment on the last node explains the exclusion: in the Vulkan SC main process, the test does not really create an instance or device, and the creation calls always return `VK_SUCCESS`, so the test would not exercise the intended path ([`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2915-L2920)).
- `createDeviceWithVariousQueueCountsTest` walks `queueCount` from 1 to the family maximum in steps of 1; it does not separately test the same family twice with the same count.
- The 208 per-feature leaves under `create_device_unsupported_features` are generated from `vkDeviceFeatureTest.inl` rather than enumerated by hand. Each leaf targets exactly one feature bit; combinations of unsupported features are intentionally not tested here and belong to feature-interaction tests elsewhere.
- `robustBufferAccess` is intentionally omitted from the `core` leaf's feature list because the spec requires it to always be supported ([`vktApiDeviceInitializationTests.cpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1654-L1655)).

## Key Takeaways

- The family is a configuration matrix, not a runtime test: every leaf is one host-side `vkCreateInstance` / `vkCreateDevice` / `vkGetDeviceQueue2` scenario checked through the returned `VkResult` and the retrievability of the requested queues.
- The primary behavioral axis is the intermediate node. The 26 intermediate nodes group into eight thematic clusters: instance creation, enumeration leak, basic device creation, global priority, features2, unsupported features, queue2 / protected memory, and intentional allocation failure.
- `create_device_unsupported_features` is the only intermediate node with a non-`basic` leaf shape: one `core` leaf enumerates `VkPhysicalDeviceFeatures` and 208 generated leaves enumerate extension feature structs.
- The four global-priority variants encode an explicit allow/deny contract: in-range `LOW`/`MEDIUM` must succeed, `HIGH`/`REALTIME` may be denied with `VK_ERROR_NOT_PERMITTED_KHR`, and out-of-range priorities must fail with `VK_ERROR_INITIALIZATION_FAILED` in the query variants.
- Five intermediate nodes are excluded from Vulkan SC by build guards; on Vulkan SC builds they do not appear in mustpass.
- Failure meaning is cluster-specific; see `## Failure Meaning` for the mapping from each cluster to its cause and symptoms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Public entry point: `createDeviceInitializationTests()` | [`vktApiDeviceInitializationTests.cpp#L2868-L2942`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2868-L2942) | Builds the `device_init` test family and attaches all 26 intermediate nodes. |
| Wrapper helper: `addFunctionCaseInNewSubgroup()` | [`vktApiDeviceInitializationTests.cpp#L2839-L2866`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2839-L2866) | Creates each single-`basic` intermediate node. Used for 25 of the 26 direct children. |
| Parent registration: `createApiTests()` | [`vktApiTests.cpp#L100`](../../../modules/vulkan/api/vktApiTests.cpp#L100) | Attaches `createDeviceInitializationTests()` to the `api` test category. |
| Instance creation tests | [`vktApiDeviceInitializationTests.cpp#L66-L576`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L66-L576) | Bodies for the six `create_instance_*` intermediate nodes. |
| `enumerateDevicesAllocLeakTest()` | [`vktApiDeviceInitializationTests.cpp#L579-L628`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L579-L628) | Allocation-balance check for `vkEnumeratePhysicalDevices`. |
| Basic device creation tests | [`vktApiDeviceInitializationTests.cpp#L631-L978`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L631-L978) | Bodies for `create_device`, `create_multiple_devices`, `create_device_unsupported_extensions`, `create_device_various_queue_counts`. |
| Global priority tests | [`vktApiDeviceInitializationTests.cpp#L980-L1316`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L980-L1316) | Bodies and support hooks for the four `create_device_global_priority*` intermediate nodes. |
| `createDeviceFeatures2Test()` | [`vktApiDeviceInitializationTests.cpp#L1318-L1383`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1318-L1383) | Features2 path body. |
| Unsupported-feature driver: `checkFeatures()` | [`vktApiDeviceInitializationTests.cpp#L1399-L1630`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1399-L1630) | Shared driver for the 208 per-feature leaves, including prerequisite-feature handling. |
| `createDeviceWithUnsupportedFeaturesTest()` | [`vktApiDeviceInitializationTests.cpp#L1632-L1772`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1632-L1772) | `core` leaf body, enumerating `VkPhysicalDeviceFeatures`. |
| `addSeparateUnsupportedFeatureTests()` | [`vkDeviceFeatureTest.inl#L9041-L9042`](../../../framework/vulkan/generated/vulkan/vkDeviceFeatureTest.inl#L9041-L9042) | Generator for the 208 per-feature leaves under `create_device_unsupported_features`. |
| Queue2 tests | [`vktApiDeviceInitializationTests.cpp#L1776-L2444`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L1776-L2444) | Bodies for the eight `create_device_queue2*` intermediate nodes and shared helpers. |
| `runQueueCreationTestCombination()` | [`vktApiDeviceInitializationTests.cpp#L2002-L2057`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2002-L2057) | Shared queue-retrieval and wait loop used by all protected-memory queue2 variants. |
| `createInstanceDeviceIntentionalAllocFail()` | [`vktApiDeviceInitializationTests.cpp#L2618-L2833`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.cpp#L2618-L2833) | Intentional-allocation-failure body. |
| Mustpass source | [`api.txt`](../../../mustpass/main/vk-default/api.txt) | Contains all `dEQP-VK.api.device_init.*` entries (234 leaves total). |
| Header | [`vktApiDeviceInitializationTests.hpp`](../../../modules/vulkan/api/vktApiDeviceInitializationTests.hpp#L1) | Public declaration of `createDeviceInitializationTests()`. |
