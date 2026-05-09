# [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L1)

## Overview

[`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L1) implements the `api/version_check` subgroup registered by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L90). The file combines three concerns: validating that the device API version is not newer than the maximum Vulkan version supported by this CTS build, validating `vkGetInstanceProcAddr` / `vkGetDeviceProcAddr` behavior for core and extension functions, and verifying that `vkGetDeviceProcAddr` returns NULL for functions beyond the requested API version.

## Role of File

Implementation-heavy test file for the `api/version_check` subgroup.

## Source Code

- Primary source: [vktApiVersionCheck.cpp](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L1)
- Header: [vktApiVersionCheck.hpp](../../../modules/vulkan/api/vktApiVersionCheck.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L90)

## Registration Hierarchy

```text
api.version_check
├── version
├── entry_points
└── unavailable_entry_points (non-VulkanSC only)
```

The `version_check` group is created at [`createVersionSanityCheckTests()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L778), which is registered as a child of the `api` category by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L90).

Evidence for direct children:
- `version` test case added at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L781)
- `entry_points` test case added at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L782)
- `unavailable_entry_points` test case added under `#ifndef CTS_USES_VULKANSC` at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L785)

## Test Families

### version — CTS-supported Vulkan version bound check

[`APIVersionTestCase`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L105) is registered with name `"version"` at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L108). Its instance [`APIVersionTestInstance::iterate()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L76) logs the available instance version, the device version, and the used API version. It fails if the physical device major or minor version is newer than the framework maximum at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L97); otherwise it passes with the used API version string at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L101).

### entry_points — Core and extension entry-point resolution

[`APIEntryPointsTestCase`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L603) is registered with name `"entry_points"` at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L606). Its instance [`APIEntryPointsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L138) performs four phases:

- **Regular check**: creates a custom instance and device without extensions, initializes the core-function map via [`initApisMap()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L168), optionally adds Vulkan 1.4 host-image-copy functions when [`hostImageCopy`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L172) is present, then validates that proper `vkGet*ProcAddr` returns non-null for core functions via [`regularCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L551)
- **Cross check**: validates that core instance functions return nullptr when queried through the wrong proc-address loader via [`mixupAddressProcCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L511)
- **Disabled-extension negative check**: verifies that functions of disabled extensions return nullptr via [`specialCasesCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L534) with a fixed list at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L208)
- **Non-existent-function negative check**: verifies that bogus names like `"vkSomeName"`, `"vkNonexistingKHR"`, and the empty string return nullptr via [`specialCasesCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L244)
- **Enabled-extension positive check**: creates a second instance/device pair with all supported extensions enabled, collects extension functions, and validates them via [`regularCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L309)

### unavailable_entry_points — Unavailable entry-points check

[`APIUnavailableEntryPointsTestCase`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L757) is registered with name `"unavailable_entry_points"` at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L761). Its instance [`APIUnavailableEntryPointsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L628) creates instances for each API version, then checks that `vkGetDeviceProcAddr` returns NULL for device functions that belong to API versions above the requested version at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L739). Requires `VK_KHR_maintenance5` via [`checkSupport()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L766).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Version values compared | framework maximum version, available instance version, device version, used API version in [`APIVersionTestInstance::iterate()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L79) |
| Loader context variants | proper `vkGet*ProcAddr` use and improper cross-use in [`regularCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L551) and [`mixupAddressProcCheck()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L511) |
| Extension state | no-extension device/context at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L155) and enabled-extension block at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L249) |
| Function categories | core functions from [`initApisMap()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L168), disabled-extension functions at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L208), non-existent names at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L231), enabled-extension functions at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L264) |
| Queue-family requirement | graphics+compute by default or compute-only under command-line control in [`createTestDevice()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L396) |
| Extension-author filter | only names beginning with `VK_KHR_` or `VK_EXT_` retained by [`filterMultiAuthorExtensions()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L340) |
| API versions iterated | all versions in `functionsPerVersion` up to `supportedApiVersion` in [`APIUnavailableEntryPointsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L639) |

## Support / Feature Requirements

- optional Vulkan 1.4 host image copy entry points only appended when [`m_context.getDeviceVulkan14Features().hostImageCopy`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L172) is true
- enabled-extension validation only uses extensions returned by [`enumerateInstanceExtensionProperties()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L360) and [`enumerateDeviceExtensionProperties()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L374), after filtering out core-promoted extensions
- `unavailable_entry_points` requires `VK_KHR_maintenance5` via [`checkSupport()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L767)
- Vulkan SC-specific device-creation reservation structures under [`#ifdef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L411)

## Verification Methods

- **version comparison**: fail if device major/minor exceeds framework-supported major/minor at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L97)
- **proc-address null/non-null checks**: helpers [`checkPlatformFunction()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L476), [`checkInstanceFunction()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L483), [`checkDeviceFunction()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L490) compare returned addresses against expected nullability
- **failure accumulation**: mismatches reported through [`reportFail()`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L466), which increments `failsQuantity`
- **final pass/fail decision**: entry-point test fails if any mismatches accumulated at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L314)
- **unavailable-function null check**: `vkGetDeviceProcAddr` must return nullptr for functions beyond requested API version at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L739)

## Test Principles Observed

- Validate CTS applicability before deeper API checks
- Check both positive and negative loader behavior
- Adapt expectations to runtime API/extension state
- Keep low-level checks traceable via centralized helper functions

## Notes / Uncertainties

- The internal contents of included files [`vkExtensionFunctions.inl`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L67) and [`vkCoreFunctionalities.inl`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L68) are not inspected here; the function lists they populate are summarized from usage context only.
- The `unavailable_entry_points` test skips Vulkan 1.0 instances at [`vktApiVersionCheck.cpp`](../../../modules/vulkan/api/vktApiVersionCheck.cpp#L643) because `VK_KHR_maintenance5` requires at least Vulkan 1.1.
