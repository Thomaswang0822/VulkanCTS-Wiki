## Overview

**Core question: does the implementation accept duplicate entries in the `ppEnabledExtensionNames` list passed to `vkCreateInstance` and `vkCreateDevice`?**

- This page covers the `api.extension_duplicates` test family, implemented in [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1) and attached to the `api` test category by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L138-L138).
- The family registers two intermediate nodes (`instance`, `device`), each with two test case leaves (`by_pointers`, `by_names`), for a total of four executable cases matching [`api.txt`](../../../mustpass/main/vk-default/api.txt#L270789-L270792).
- Each leaf enumerates the extensions actually exposed by the runtime (instance extensions via `vkEnumerateInstanceExtensionProperties`, device-creation extensions via `Context::getDeviceCreationExtensions()`), then duplicates every entry two, three, or four times before passing the resulting list to `vkCreateInstance` or `vkCreateDevice`.
- The two test case leaves differ only in how the duplication is represented: `by_pointers` reuses the same `const char *` pointer multiple times in the list; `by_names` produces separate `std::string` copies with identical contents and uses their `.c_str()` pointers.
- Passing means object creation returned `VK_SUCCESS` despite the duplicated extension names. A quality warning is reported when the runtime exposes no candidate extensions to duplicate, so the case cannot exercise the contract.

## Background Knowledge

- **`ppEnabledExtensionNames` deduplication contract.** `VkInstanceCreateInfo::ppEnabledExtensionNames` and `VkDeviceCreateInfo::ppEnabledExtensionNames` are `const char * const *` arrays whose contents are compared as strings, not as pointer identities. The Vulkan spec does not require the implementation to reject duplicate string entries; the implementation is expected to enable each named extension once regardless of how many times its name appears in the list. This family verifies that contract by deliberately passing duplicate entries and requiring object creation to succeed.
- **`createUncheckedInstance()` and `createUncheckedDevice()`.** These CTS helpers in [`vktCustomInstancesDevices.cpp`](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L466-L466) wrap `vkCreateInstance` and `vkCreateDevice` and return the raw `VkResult` instead of throwing on failure. The test uses them so it can observe both success and rejection without an exception unwinding the test body.
- **Quality warning fallback.** A CTS `tcu::TestStatus` may report `QP_TEST_RESULT_QUALITY_WARNING`, which is neither pass nor hard fail. The instance and device branches use this status when their input extension list is empty, because the case cannot exercise the deduplication contract without at least one extension to duplicate.

## Registration Hierarchy

The family is built by [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L368-L388) and attached to the `api` test category at [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L138-L138). The two intermediate nodes (`instance`, `device`) come from the `types` array; the two test case leaves under each (`by_pointers`, `by_names`) come from the shared `methods` array looped inside each intermediate node. The four resulting executable paths are `api.extension_duplicates.instance.by_pointers`, `api.extension_duplicates.instance.by_names`, `api.extension_duplicates.device.by_pointers`, and `api.extension_duplicates.device.by_names`, all listed in [`api.txt`](../../../mustpass/main/vk-default/api.txt#L270789-L270792).

```text
api.extension_duplicates
├── instance
└── device
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `instance`, `device` | Selects which Vulkan object-creation entry point receives the duplicated extension list: `vkCreateInstance` or `vkCreateDevice`. | [`types` array](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L371-L371) |
| Test case leaf | `by_pointers`, `by_names` | Selects the duplication representation: pointer reuse or distinct string copies with identical contents. | [`methods` array](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L373-L373) |
| Duplicate multiplicity | 2, 3, or 4 copies per input extension | Each input extension is repeated two, three, or four times in the output list, depending on its zero-based index `i` in the deduplicated input: `i % 2 == 0` yields 2, `i % 3 == 0` yields 3, otherwise 4. | [`duplicatePointers()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L83-L113), [`duplicateStrings()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L114-L151) |
| Instance extension source | all extensions reported by `vkEnumerateInstanceExtensionProperties(nullptr)` | Drives the instance branch input list at runtime; the actual contents are platform-dependent. | [`InstanceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L208-L208) |
| Device extension source | `Context::getDeviceCreationExtensions()` | Drives the device branch input list at runtime; these are the extensions the test context already enables for the device under test. | [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L286-L286) |
| Build guard | `CTS_USES_VULKANSC` | On Vulkan SC builds the device branch chains `VkDeviceObjectReservationCreateInfo` and `VkPhysicalDeviceVulkanSC10Features` through `VkDeviceCreateInfo::pNext` before creation, and uses a `DeviceDriver` wrapper for destruction. | [SC-only block](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L275-L316) |

## Behavior Parameters

The family has two meaningful behavioral axes. The intermediate node axis selects the Vulkan object-creation entry point; the test case leaf axis selects the duplication representation.

### Intermediate node axis

#### `instance`: `vkCreateInstance` with duplicated extension names

The leaf enumerates available instance extensions through `vkEnumerateInstanceExtensionProperties`, copies each `extensionName` into a `std::string`, takes the `.c_str()` of each, deduplicates that pointer set through `ut::distinct()`, then duplicates the resulting list via `ut::StringDuplicator`. The duplicated list is passed as `ppEnabledExtensionNames` to a `VkInstanceCreateInfo` whose `pApplicationInfo` sets `apiVersion` to `m_context.getUsedApiVersion()`. The test then calls [`createUncheckedInstance()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L251-L252) and requires `VK_SUCCESS`. See [`InstanceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L204-L271).

If the platform reports zero instance extensions, the case returns `QP_TEST_RESULT_QUALITY_WARNING` with the message `Unable to perform test due to empty instance extension list` instead of attempting creation ([`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L210-L214)).

#### `device`: `vkCreateDevice` with duplicated extension names

The leaf takes the device-creation extension list from `Context::getDeviceCreationExtensions()`, deduplicates and duplicates it the same way as the instance branch, then builds a `VkDeviceQueueCreateInfo` for the universal queue family with priority `1.0f` and a `VkDeviceCreateInfo` whose `ppEnabledExtensionNames` is the duplicated list. The test calls [`createUncheckedDevice()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L333-L335) and requires `VK_SUCCESS`. On success the created device is explicitly destroyed through `DeviceInterface::destroyDevice()` on regular Vulkan or `DeviceDriver::destroyDevice()` on Vulkan SC, so the acceptance check itself does not leak a device. See [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L273-L365).

If the device-creation extension list is empty after deduplication, the case returns `QP_TEST_RESULT_QUALITY_WARNING` with the message `Unable to perform test due to empty device extension list` ([`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L290-L294)).

### Test case leaf axis

#### `by_pointers`: pointer reuse

The leaf selects `ut::StringDuplicator::duplicatePointers()`, which inserts the same `const char *` pointer into the output vector multiple times. All duplicate entries point to the same memory address. This representation tests whether the implementation rejects a list whose entries compare equal as pointers, not just as strings. See [`duplicatePointers()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L83-L113).

#### `by_names`: distinct string copies with identical contents

The leaf selects `ut::StringDuplicator::duplicateStrings()`, which constructs separate `std::string` objects holding identical copies of each extension name and returns their `.c_str()` pointers. Duplicate entries point to different memory addresses but compare equal as strings. This representation tests the canonical case the spec text addresses: distinct name strings that happen to be equal. See [`duplicateStrings()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L114-L151).

## Shader Analysis

No shader is involved in this test family. Every test case leaf drives host-side Vulkan object-creation entry points and inspects the returned `VkResult`. The `## Shader Analysis` section therefore has no representative walkthrough subsections.

## Runtime Execution and Result Checking

All verification is host-side. The shared execution shape across the four leaves is:

1. Acquire the input extension list: `vkEnumerateInstanceExtensionProperties(nullptr)` for the `instance` intermediate node, or `Context::getDeviceCreationExtensions()` for the `device` intermediate node.
2. If the input list is empty, return `QP_TEST_RESULT_QUALITY_WARNING` and stop; the deduplication contract cannot be exercised without at least one extension to duplicate ([instance branch](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L210-L214), [device branch](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L290-L294)).
3. Build a `ut::StringDuplicator` over the deduplicated input. The constructor runs `ut::distinct()` which keeps one `const char *` per distinct pointer in the input set.
4. Select the duplication strategy from the test case leaf: `duplicatePointers()` for `by_pointers`, `duplicateStrings()` for `by_names` ([instance selection](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L224-L227), [device selection](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L286-L289)).
5. Build the create-info struct:
   - For `instance`: a `VkApplicationInfo` with `apiVersion = m_context.getUsedApiVersion()` and a `VkInstanceCreateInfo` whose `enabledExtensionCount` and `ppEnabledExtensionNames` carry the duplicated list ([struct setup](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L229-L248)).
   - For `device`: a `VkDeviceQueueCreateInfo` for the universal queue family with priority `1.0f`, optional Vulkan SC `pNext` chaining, and a `VkDeviceCreateInfo` whose `enabledExtensionCount` and `ppEnabledExtensionNames` carry the duplicated list ([struct setup](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L296-L330)).
6. Call `createUncheckedInstance()` or `createUncheckedDevice()` and capture the returned `VkResult`.
7. For the `device` branch only, on `VK_SUCCESS` with a non-null handle, explicitly destroy the device through `DeviceInterface::destroyDevice()` or, on Vulkan SC, through a `DeviceDriver` wrapper that calls `destroyDevice()` ([cleanup block](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L334-L345)).
8. Decide pass/fail:
   - `VK_SUCCESS` → `tcu::TestStatus::pass()` with a message reporting the duplicate count and the input extension count, for example `Created <dup> duplicates of <input> extensions` ([instance pass message](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L262-L268), [device pass message](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L355-L361)).
   - Any other `VkResult` → `tcu::TestStatus::fail()` with a message of the form `vkCreateInstance returned <name>` or `vkCreateDevice returned <name>` ([instance fail message](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L254-L260), [device fail message](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L347-L353)).

There is no device-side work beyond object creation and, in the `device` branch, destruction.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `instance.by_pointers` | `vkCreateInstance` rejection of an extension list whose entries are pointer-equal duplicates of supported instance extensions. |
| `instance.by_names` | `vkCreateInstance` rejection of an extension list whose entries are distinct strings with identical contents, all naming supported instance extensions. |
| `device.by_pointers` | `vkCreateDevice` rejection of an extension list whose entries are pointer-equal duplicates of supported device-creation extensions. |
| `device.by_names` | `vkCreateDevice` rejection of an extension list whose entries are distinct strings with identical contents, all naming supported device-creation extensions. |

All four leaves share a common infrastructure failure mode: the input extension list is empty at runtime, in which case the leaf reports `QP_TEST_RESULT_QUALITY_WARNING` rather than a hard failure. The instance branch triggers this when `vkEnumerateInstanceExtensionProperties` returns zero extensions; the device branch triggers it when `Context::getDeviceCreationExtensions()` returns an empty list.

### Cause Analysis

#### `vkCreateInstance` rejection of duplicated extension names

**Possible failure symptoms:** `InstanceExtensionDuplicatesInstance::iterate()` returns `tcu::TestStatus::fail()` with the message `vkCreateInstance returned <name>` where `<name>` is the implementation-reported `VkResult` name. The reported result is anything other than `VK_SUCCESS`, typically `VK_ERROR_EXTENSION_NOT_PRESENT` if the implementation misclassified a duplicate entry as unsupported, or `VK_ERROR_INITIALIZATION_FAILED` if the implementation aborted instance initialization while processing the duplicated list.

**Possible implementation causes:** the implementation compares `ppEnabledExtensionNames` entries by pointer identity instead of by string contents, so identical-pointer entries (`by_pointers`) or distinct-address equal-string entries (`by_names`) are treated as unrecognized extensions; the implementation does not deduplicate the enabled-extension list before validation, so a name that appears multiple times trips an "extension already enabled" check that the spec does not permit; or the implementation populates its internal extension-enable table once per list entry and corrupts state when the same name is encountered a second time. The Vulkan spec text for `VkInstanceCreateInfo` requires that `ppEnabledExtensionNames` contain strings, with no prohibition on duplicates; source-level investigation is needed to identify which validation step rejects the duplicated list.

#### `vkCreateDevice` rejection of duplicated extension names

**Possible failure symptoms:** `DeviceExtensionDuplicatesInstance::iterate()` returns `tcu::TestStatus::fail()` with the message `vkCreateDevice returned <name>` where `<name>` is the implementation-reported `VkResult` name. As with the instance branch, the reported result is typically `VK_ERROR_EXTENSION_NOT_PRESENT` or `VK_ERROR_INITIALIZATION_FAILED`.

**Possible implementation causes:** the same root causes as the instance branch, applied to `vkCreateDevice`: pointer-identity comparison instead of string comparison, an internal "extension already enabled" rejection that the spec does not permit, or state corruption when the device-creation extension list contains repeated entries. On Vulkan SC, the additional `pNext` structures chained by the test (`VkDeviceObjectReservationCreateInfo`, `VkPhysicalDeviceVulkanSC10Features`) interact with the duplicated extension list during device creation, so a failure specific to the SC build could also indicate that the SC reservation or feature struct validation does not tolerate duplicate extension entries; source-level investigation is needed to distinguish an SC-specific defect from a general deduplication defect.

#### Shared infrastructure failure: empty input extension list

**Possible failure symptoms:** the leaf returns `QP_TEST_RESULT_QUALITY_WARNING` with the message `Unable to perform test due to empty instance extension list` (instance branch, [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L210-L214)) or `Unable to perform test due to empty device extension list` (device branch, [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L290-L294)). The case is not marked pass or fail; it is reported as a quality warning.

**Possible implementation causes:** the platform reports no instance extensions through `vkEnumerateInstanceExtensionProperties`, or the test context's device-creation extension list is empty. This is an environment condition rather than a conformance defect; the warning exists so that platforms without candidate extensions do not falsely fail a contract they could not exercise. No source-level investigation is needed unless the warning appears on a platform known to expose extensions.

## Case Pruning

### Requirement-based pruning

No feature bit, named extension, queue-family capability, or platform requirement is enforced as a registered support gate by this family. The test creates raw `VkInstance` and `VkDevice` objects through the unchecked helpers and accepts whatever extensions the platform exposes. The Vulkan SC build guards add `pNext` structures to device creation but do not prune any test case leaf; all four leaves exist in both regular and Vulkan SC builds.

### Design-based pruning

The family generates no parameter combinations. The two intermediate nodes are fixed (`instance`, `device`); the two test case leaves under each are fixed (`by_pointers`, `by_names`). The duplicate multiplicity (2, 3, or 4 copies per extension) is not a registered parameter; it is fixed by `ut::StringDuplicator` based on the input extension's zero-based index. The input extension list itself is runtime-dependent and not enumerated as a test parameter, because the contract being tested is independent of which specific extensions are duplicated.

## Key Takeaways

- The family is a host-side object-creation contract test: every leaf creates a `VkInstance` or `VkDevice` with a deliberately duplicated `ppEnabledExtensionNames` list and requires `VK_SUCCESS`.
- The two intermediate nodes (`instance`, `device`) select the Vulkan entry point; the two test case leaves (`by_pointers`, `by_names`) select the duplication representation. Both axes are meaningful, and a failure of any of the four combinations is a distinct symptom.
- `by_pointers` exercises pointer-equal duplicates; `by_names` exercises distinct-address equal-string duplicates. Both must be accepted by a conformant implementation.
- The duplicate multiplicity pattern (2, 3, or 4 copies per extension) is incidental to the test design; the contract is independent of how many times each name appears, only that duplicates as a class are accepted.
- An empty input extension list is reported as a quality warning, not a failure, because the contract cannot be exercised. See `## Failure Meaning` for the analysis.
- The `device` branch explicitly destroys the device it creates on success, so the test does not leak a device object while checking the acceptance contract.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Public entry point: `createExtensionDuplicatesTests()` | [`vktApiExtensionDuplicatesTests.cpp#L368-L388`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L368-L388) | Builds the `extension_duplicates` test family and attaches the `instance` and `device` intermediate nodes with their `by_pointers` / `by_names` leaves. |
| Parent registration | [`vktApiTests.cpp#L138-L138`](../../../modules/vulkan/api/vktApiTests.cpp#L138-L138) | Where the `extension_duplicates` group is attached to the `api` test category. |
| `InstanceExtensionDuplicatesInstance::iterate()` | [`vktApiExtensionDuplicatesTests.cpp#L204-L271`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L204-L271) | Body for both `instance.by_pointers` and `instance.by_names`. |
| `DeviceExtensionDuplicatesInstance::iterate()` | [`vktApiExtensionDuplicatesTests.cpp#L273-L365`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L273-L365) | Body for both `device.by_pointers` and `device.by_names`. |
| `ExtensionDuplicatesCase::createInstance()` | [`vktApiExtensionDuplicatesTests.cpp#L192-L197`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L192-L197) | Dispatches between the instance and device test instance based on the intermediate node flag. |
| `ut::StringDuplicator::duplicatePointers()` | [`vktApiExtensionDuplicatesTests.cpp#L83-L113`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L83-L113) | `by_pointers` duplication strategy: reuses the same pointer multiple times. |
| `ut::StringDuplicator::duplicateStrings()` | [`vktApiExtensionDuplicatesTests.cpp#L114-L151`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L114-L151) | `by_names` duplication strategy: creates separate string copies with identical contents. |
| `ut::distinct()` | [`vktApiExtensionDuplicatesTests.cpp#L55-L63`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L55-L63) | Builds the input set for `StringDuplicator` from the runtime extension list. |
| `createUncheckedInstance()` | [`vktCustomInstancesDevices.cpp#L466-L466`](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L466-L466) | Wrapper around `vkCreateInstance` that returns the raw `VkResult`. |
| `createUncheckedDevice()` | [`vktCustomInstancesDevices.cpp#L564-L564`](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L564-L564) | Wrapper around `vkCreateDevice` that returns the raw `VkResult`. |
| Header | [`vktApiExtensionDuplicatesTests.hpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.hpp#L1) | Public declaration of `createExtensionDuplicatesTests()`. |
| Mustpass entries | [`api.txt#L270789-L270792`](../../../mustpass/main/vk-default/api.txt#L270789-L270792) | The four `dEQP-VK.api.extension_duplicates.*` leaves in the canonical mustpass. |
