## Overview

**Core question:** Does the implementation report an API version the CTS build can run, and do `vkGetInstanceProcAddr` / `vkGetDeviceProcAddr` resolve exactly the function set that the requested API version and current extension state permit?

- [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp) implements the `api.version_check` test family, registered under the `api` test category by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L90).
- The test family registers three test case leaves: `version`, `entry_points`, and `unavailable_entry_points`. Each leaf tests a distinct property of the implementation's version reporting or proc-address resolution.
- `version` checks that the device's reported API version is not newer than the maximum Vulkan version this CTS build supports.
- `entry_points` checks `vkGetInstanceProcAddr` and `vkGetDeviceProcAddr` against core, disabled-extension, enabled-extension, and non-existent function names, using both proper and improper loader contexts.
- `unavailable_entry_points` checks that `vkGetDeviceProcAddr` returns `NULL` for device functions belonging to API versions above the version requested by the application.

## Background Knowledge

- **Framework maximum, available instance, device, and used API versions.** CTS distinguishes the maximum Vulkan version the framework itself was built to understand, the version the platform's Vulkan loader exposes for instance creation, the version reported by the chosen physical device, and the version actually requested for the test's instance/device. The `version` leaf compares the device version against the framework maximum, because running tests against an unsupported version would itself be invalid.
- **`vkGetInstanceProcAddr` and `vkGetDeviceProcAddr` contracts.** `vkGetInstanceProcAddr` can query platform-level, instance-level, and device-level functions, while `vkGetDeviceProcAddr` is only required to return valid pointers for device-level functions. Vulkan spec rules also describe what these entry points must return for unsupported or non-existent names. The `entry_points` leaf probes both correct and incorrect combinations of loader and function category.
- **Core promotion and per-version function sets.** Functions added in Vulkan 1.1, 1.2, 1.3, and 1.4 are organized by the API version that introduced them. The `unavailable_entry_points` leaf relies on this grouping to ask, for each lower API version an application can request, whether device functions that belong only to higher versions are correctly reported as unavailable.

## Registration Hierarchy

```text
api.version_check
├── version
├── entry_points
└── unavailable_entry_points
```

All three children are test case leaves directly under the `version_check` test family; there are no intermediate nodes. `unavailable_entry_points` is registered only for non-VulkanSC builds, behind `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Compared version set | framework maximum, available instance version, device version, used API version | Drives the `version` leaf's pass/fail decision; the device version is the one compared against the framework maximum. | [APIVersionTestInstance::iterate()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L76-L102) |
| Function origin | `FUNCTIONORIGIN_PLATFORM`, `FUNCTIONORIGIN_INSTANCE`, `FUNCTIONORIGIN_DEVICE` | Selects which proc-address loader and which nullability expectation apply for each function name in `entry_points`. | [initApisMap()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L168), [regularCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L550-L599) |
| Extension state | no extensions enabled, all supported `VK_KHR_`/`VK_EXT_` extensions enabled | Splits `entry_points` into a negative path (disabled extensions must return `nullptr`) and a positive path (enabled extension functions must resolve). | [no-extension block](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L155-L247), [enabled-extension block](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L249-L312), [filterMultiAuthorExtensions()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L340-L355) |
| Function category | core, disabled-extension, enabled-extension, non-existent | Each category carries a different nullability expectation under Vulkan's proc-address rules. | [specialCasesCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L533-L548), [regularCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L550-L599) |
| Loader context | proper, improper | `regularCheck` uses the proper loader for each origin; `mixupAddressProcCheck` queries through the wrong loader to confirm `nullptr`. | [mixupAddressProcCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L510-L531) |
| Requested API version | each version present in `functionsPerVersion` up to the device's supported API version | For each requested version, `unavailable_entry_points` checks that device functions introduced in higher versions are unavailable. | [APIUnavailableEntryPointsTestInstance::iterate()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L627-L753) |
| Optional 1.4 host-image-copy functions | appended only when the `hostImageCopy` Vulkan 1.4 feature is present | Optional promotion of `VK_EXT_host_image_copy` entry points into Vulkan 1.4. | [hostImageCopy block](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L170-L181) |

## Behavior Parameters

The primary behavioral axis is the **test case leaf** under `api.version_check`. Each leaf changes which property of the implementation is being tested: reported version validity, proc-address resolution correctness, or per-version function availability.

### version — Device API version bound check

`version` reads the framework maximum Vulkan version, the available instance version, the device version, and the used API version, logs the available instance, device, and used API versions, and fails if the device's major or minor version is newer than the framework maximum [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L76-L102). The check uses the framework maximum rather than the used API version because the test detects when CTS runs against a Vulkan version it was not built to understand. On pass, the leaf returns the used API version string as the status message.

### entry_points — Core and extension proc-address resolution

`entry_points` runs five sub-checks against two instance/device pairs. The first pair is created with no extensions enabled, the second with all supported `VK_KHR_` and `VK_EXT_` extensions enabled, and each pair drives several phases [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L138-L318):

- Regular check: for core functions of every API version at or below the used API version, the proper loader must return a non-null pointer [regularCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L550-L599).
- Cross check: querying instance or device core functions through the wrong loader must return `nullptr` [mixupAddressProcCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L510-L531).
- Disabled-extension check: a fixed list of `VK_KHR_*` function names must return `nullptr` when the corresponding extensions are not enabled [disabled-extension list](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L208-L218).
- Non-existent-function check: names like `vkSomeName`, `vkNonexistingKHR`, and the empty string must return `nullptr` for every origin [non-existent list](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L231-L238).
- Enabled-extension check: functions exposed by every supported `VK_KHR_`/`VK_EXT_` instance or device extension must resolve through the proper loader [enabled-extension block](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L249-L312).

A single failure counter accumulates mismatches across all phases. The leaf fails if any mismatch was recorded [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L314-L317).

### unavailable_entry_points — Per-version function availability

`unavailable_entry_points` iterates over each API version present in the framework's per-version function map, creates a fresh instance and device that request that specific API version, then for each higher API version iterates the device functions it introduced and verifies that `vkGetDeviceProcAddr` returns `NULL` for them [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L627-L753). The leaf requires `VK_KHR_maintenance5` because Maintenance5 defines the predictable null-return behavior for functions outside the requested API version that this test exercises.

The leaf skips Vulkan 1.0 requests because `VK_KHR_maintenance5` requires at least Vulkan 1.1 [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L641-L642). It stops at the device's supported API version and skips re-checking the highest version present in the map, since there is no higher version to test against.

## Shader Analysis

No shader is involved in this test family. The leaves exercise host-side version reporting and proc-address resolution only.

## Runtime Execution and Result Checking

- **Instance and device creation.** `entry_points` builds two instance/device pairs: one with no extensions enabled, one with all supported `VK_KHR_`/`VK_EXT_` instance and device extensions enabled [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L155-L312). `unavailable_entry_points` builds one instance/device pair per requested API version, requests `VK_KHR_maintenance5` plus a small set of supporting extensions, and queries `VkPhysicalDeviceMaintenance5FeaturesKHR` through `VkPhysicalDeviceFeatures2` [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L652-L704).
- **Proc-address loader acquisition.** Each test acquires `vkGetInstanceProcAddr` from the platform Vulkan loader, then obtains `vkGetDeviceProcAddr` through `vkGetInstanceProcAddr(instance, "vkGetDeviceProcAddr")` [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L159-L163), [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L256-L260). This is the loader path a real application would use.
- **Function set construction.** `initApisMap()` populates the per-version core function map; the Vulkan 1.4 host-image-copy entry points are appended only when the corresponding feature is present [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L167-L181). Extension functions are enumerated from `vkEnumerateInstanceExtensionProperties` and `vkEnumerateDeviceExtensionProperties`, filtered to `VK_KHR_`/`VK_EXT_` prefixes, and core-promoted extensions are removed before the enabled-extension phase [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L340-L385).
- **Per-function nullability checks.** `checkPlatformFunction`, `checkInstanceFunction`, and `checkDeviceFunction` compare the returned address against the expected nullability for that function and loader combination, and `reportFail` logs every mismatch while incrementing a single failure counter [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L465-L494).
- **Per-version null check.** `unavailable_entry_points` skips any function name that already appeared in a previous (lower) API version, so it only checks functions genuinely introduced above the requested version [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L710-L744).
- **Final pass/fail rule.** `version` passes when the device major/minor is at or below the framework maximum and fails otherwise. `entry_points` passes when the failure counter is still zero after all phases. `unavailable_entry_points` passes when no tested higher-version device function returned a non-null pointer.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `version` | The implementation reports a device API version newer than the maximum Vulkan version this CTS build was built to understand. |
| `entry_points` | A proc-address query returned the wrong nullability for a core, disabled-extension, enabled-extension, or non-existent function name, or for a deliberately mismatched loader/function pair. |
| `unavailable_entry_points` | `vkGetDeviceProcAddr` returned a non-null pointer for a device function that belongs to an API version above the one requested by the application. |

### Cause Analysis

#### Device version exceeds framework maximum

**Possible failure symptoms:** The `version` leaf returns `tcu::TestStatus::fail` with a message stating that this CTS version does not support the reported Vulkan device version [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L97-L99). The test log shows the available instance version, the device version, and the used API version.

**Possible implementation causes:** This is not a driver bug. The check exists so that running CTS against a newer Vulkan version than the framework was built for is reported as an environment mismatch rather than as spurious failures inside individual tests. The appropriate resolution is to use a CTS build whose maximum supported Vulkan version is at least the device's reported version.

#### Wrong proc-address nullability

**Possible failure symptoms:** `entry_points` returns `tcu::TestStatus::fail("Fail")` because the failure counter is non-zero [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L314-L315). The test log lists each offending query in the form `vkGetInstanceProcAddr(<firstParam>, "<functionName>") returned <actual>. Should return <expected>.`, where `<firstParam>` is `nullptr`, `instance`, or `device` depending on which helper reported the failure [reportFail()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L465-L473).

**Possible implementation causes:** The failing path depends on which sub-check produced the mismatch. A regular-check failure for a core function indicates the loader is not exposing an entry point that should be available at the used API version. A cross-check failure indicates the loader returned a non-null pointer through a loader that the spec requires to return `nullptr`, or returned `nullptr` where the proper loader should have succeeded. A disabled-extension or non-existent-function failure indicates the loader returns pointers for names it must not resolve. An enabled-extension failure indicates the loader does not expose functions for an extension the test enumerated as supported. Grounded investigation should compare the offending function name and loader against the Vulkan spec's `vkGetInstanceProcAddr` / `vkGetDeviceProcAddr` contracts, including the rules for core-promoted extensions and the special-case gates the test already applies for `VK_KHR_draw_indirect_count`, `VK_KHR_push_descriptor`, and `vkGetInstanceProcAddr` itself [regularCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L550-L599).

#### Higher-version device function returned non-null

**Possible failure symptoms:** `unavailable_entry_points` returns `tcu::TestStatus::fail("Fail")` after logging `getDeviceProcAddr(<funcName>) returned non-null pointer, expected NULL` for at least one function [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L738-L743). The log also records the requested API version for each iteration so the failing version boundary is identifiable.

**Possible implementation causes:** The implementation is expected to honor `VK_KHR_maintenance5` semantics for `vkGetDeviceProcAddr` when the application requested a lower API version than the device supports. A non-null return for a function introduced in a higher version means the loader is exposing entry points outside the contract defined by the requested API version and the Maintenance5 extension. Grounded investigation should confirm that `VK_KHR_maintenance5` was actually enabled on the failing device, that the offending function name is genuinely introduced in a higher version (and not also present in a lower version, which the test's duplicate-suppression step should already have handled), and that the loader's per-version filtering matches the Maintenance5 specification.

## Case Pruning

### Requirement-based pruning

- `unavailable_entry_points` requires `VK_KHR_maintenance5` through `checkSupport()`, so the test case is reported as unsupported rather than failed when the extension or feature is absent [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L764-L767).
- `unavailable_entry_points` is not registered for VulkanSC builds; the test case leaf exists only behind `#ifndef CTS_USES_VULKANSC` [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L783-L785).
- The Vulkan 1.4 host-image-copy entry points are only appended to the core function map when `m_context.getDeviceVulkan14Features().hostImageCopy` is true; otherwise those names are not tested as core 1.4 functions [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L170-L181).
- `unavailable_entry_points` skips Vulkan 1.0 instances because `VK_KHR_maintenance5` requires at least Vulkan 1.1 [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L641-L642).

### Design-based pruning

- The enabled-extension phase only enumerates extensions whose names begin with `VK_KHR_` or `VK_EXT_`, so other author namespaces are intentionally not covered by `entry_points` [filterMultiAuthorExtensions()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L340-L355).
- Extensions that have been promoted to core for the requested API version are filtered out before the enabled-extension phase, so they are not double-tested as both core and extension functions [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L357-L385).
- `regularCheck` skips `vkGetInstanceProcAddr` itself below Vulkan 1.2, skips `vkCmdDrawIndirectCount` / `vkCmdDrawIndexedIndirectCount` unless `VK_KHR_draw_indirect_count` is supported, and skips `vkCmdPushDescriptorSetWithTemplateKHR` unless the prerequisite push-descriptor and (below 1.1) descriptor-update-template extensions are present. These skips reflect per-function availability rules that the spec does not express purely through the API version [regularCheck()](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L550-L599).
- `unavailable_entry_points` skips the highest API version in the per-version map because there is no higher version whose functions it could test [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L649-L650).
- The queue-family requirement for `entry_points` defaults to graphics-plus-compute, switching to compute-only under explicit command-line control [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L396-L398). This is a test-configuration choice rather than a per-case pruning rule.

## Key Takeaways

- The three leaves under `api.version_check` test three different properties: reported version validity, proc-address resolution across function categories and loader contexts, and per-version function availability under Maintenance5.
- `version` is an environment check, not a driver-correctness check; a failure means CTS itself is being run against a Vulkan version it was not built to support.
- `entry_points` combines positive checks (core and enabled-extension functions must resolve) with negative checks (disabled-extension, non-existent, and cross-loader queries must return `nullptr`), all routed through a single failure counter.
- `unavailable_entry_points` depends on `VK_KHR_maintenance5` and is therefore Vulkan-1.1-or-later only; it is also absent from VulkanSC builds.
- See `## Failure Meaning` for the per-leaf failure interpretation: environment mismatch for `version`, proc-address contract violation for `entry_points`, and per-version availability violation for `unavailable_entry_points`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [vktApiTests.cpp#L90](../../../modules/vulkan/api/vktApiTests.cpp#L90) | Attaches `version_check` as a child of the `api` test category. |
| Test family factory | [vktApiVersionCheck.cpp#L777-L788](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L777-L788) | Creates the `version_check` group and adds the three test case leaves, with `unavailable_entry_points` behind `#ifndef CTS_USES_VULKANSC`. |
| Header declaration | [vktApiVersionCheck.hpp#L37](../../../modules/vulkan/api/vktApiVersionCheck.hpp#L37) | Declares `createVersionSanityCheckTests`. |
| `version` test instance | [vktApiVersionCheck.cpp#L70-L103](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L70-L103) | Logs version info and fails when the device version exceeds the framework maximum. |
| `entry_points` test instance | [vktApiVersionCheck.cpp#L123-L600](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L123-L600) | Runs the five proc-address sub-checks across no-extension and enabled-extension instance/device pairs. |
| `unavailable_entry_points` test instance | [vktApiVersionCheck.cpp#L620-L753](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L620-L753) | Iterates requested API versions and checks that higher-version device functions return `NULL`. |
| Proc-address helpers | [vktApiVersionCheck.cpp#L465-L494](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L465-L494) | `reportFail`, `checkPlatformFunction`, `checkInstanceFunction`, and `checkDeviceFunction` implement the nullability comparison used by every `entry_points` sub-check. |
| Maintenance5 support gate | [vktApiVersionCheck.cpp#L764-L767](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L764-L767) | `checkSupport` for `unavailable_entry_points` requires `VK_KHR_maintenance5`. |
| Mustpass entries | [api.txt#L327793-L327795](../../../mustpass/main/vk-default/api.txt#L327793-L327795) | The three `dEQP-VK.api.version_check.*` lines in the default mustpass list. |
