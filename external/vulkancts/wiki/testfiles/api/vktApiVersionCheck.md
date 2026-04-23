# vktApiVersionCheck.cpp

## Overview

[`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L70) implements the earliest `api/version` subgroup registered by [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L90). In the inspected portion, the file combines two closely related concerns:

1. validating that the device API version is not newer than the maximum Vulkan version supported by this CTS build, and
2. validating `vkGetInstanceProcAddr` / `vkGetDeviceProcAddr` behavior for core functions, disabled-extension functions, non-existent functions, and supported enabled-extension functions.

This makes `version` more than a simple version printout despite the file header comment.

## Role of File

Implementation-heavy test file for the `api/version` subgroup.

## Source Code

- Primary source: [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L70)
- Registration entry from parent category: [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L90)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
└── api
    └── createTests(testCtx, "api")
        └── createApiTests(apiTests)
            └── createVersionSanityCheckTests(testCtx)
                └── version subgroup implemented in vktApiVersionCheck.cpp
```

Evidence:
- package-level `api` attachment in [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1349) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1417)
- `version` subgroup attachment in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L90)
- concrete test classes in [`APIVersionTestInstance`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L70), [`APIVersionTestCase`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L105), and [`APIEntryPointsTestInstance`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L123)

## Test Hierarchy Observed

The exact subgroup builder function name is not visible in the inspected excerpt, so the safest confirmed hierarchy is:

```text
api
└── version
    ├── one test backed by APIVersionTestCase / APIVersionTestInstance
    └── at least one entry-point validation test backed by APIEntryPointsTestInstance
```

Confirmed evidence:
- [`APIVersionTestCase`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L105) uses the case name `"version"` in its constructor at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L108)
- [`APIEntryPointsTestInstance`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L123) contains the function-address validation logic for another test in the same subgroup, but the inspected lines do not show the surrounding `TestCase` registration name

## Test Families

### 1. CTS-supported Vulkan version bound check

[`APIVersionTestInstance::iterate()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L76) logs the available instance version, the device version, and the used API version via [`tcu::TestLog`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L78). It then fails if the physical device major or minor version is newer than the framework's maximum supported Vulkan version at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L97); otherwise it passes with the used API version string at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L101).

### 2. Core entry-point resolution using proper and improper loaders

Inside [`APIEntryPointsTestInstance::iterate()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L138), the first execution block creates a custom instance and device without extensions at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L157) and builds an API context with both proc-address loaders at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L163). It then:

- initializes the core-function map with [`initApisMap()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L168)
- optionally adds Vulkan 1.4 host-image-copy functions when [`hostImageCopy`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L172) is present
- selects the last supported core version not newer than the used API version at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L183)
- runs a “regular check” via [`regularCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L195)
- runs a “cross check” with improper loaders via [`mixupAddressProcCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L202)

This family is evidence-backed as loader-behavior validation, not just enumeration.

### 3. Disabled-extension and non-existent-function negative checks

Still in the no-extension block, the file defines a fixed list of disabled extension functions such as [`vkTrimCommandPoolKHR`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L209), [`vkCreateSwapchainKHR`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L212), and [`vkGetImageMemoryRequirements2KHR`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L217). It then validates those through [`specialCasesCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L225). A second negative block builds intentionally invalid names like [`"vkSomeName"`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L235), [`"vkNonexistingKHR"`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L236), and the empty string at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L237), and checks them the same way at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L244).

### 4. Enabled-extension positive checks

The second main execution block enumerates supported instance and device extensions and filters them before use via [`getSupportedInstanceExtensions()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L251) and [`getSupportedDeviceExtensions()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L254). It derives callable extension functions for supported instance extensions at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L272) and supported device extensions at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L297), then performs an enabled-extensions “regular check” through [`regularCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L309).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Version values compared | framework maximum version, available instance version, device version, used API version in [`APIVersionTestInstance::iterate()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L79) |
| Loader context variants | proper `vkGet*ProcAddr` use and improper cross-use in [`regularCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L195) and [`mixupAddressProcCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L202) |
| Extension state | no-extension device/context block at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L155) and enabled-extension block at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L249) |
| Function categories | core functions from [`initApisMap()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L168), disabled-extension functions listed at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L208), non-existent function names at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L231), enabled-extension functions collected at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L264) |
| Queue-family requirement when creating a test device | graphics+compute by default or compute-only under command-line control in [`createTestDevice()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L396) |
| Extension-author filter | only names beginning with `VK_KHR_` or `VK_EXT_` are retained by [`filterMultiAuthorExtensions()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L340) |

## Support / Feature Requirements

Observed support logic includes:

- optional Vulkan 1.4 host image copy entry points are only appended when [`m_context.getDeviceVulkan14Features().hostImageCopy`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L172) is true
- enabled-extension validation only uses extensions returned by [`enumerateInstanceExtensionProperties()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L360) and [`enumerateDeviceExtensionProperties()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L374), after filtering out core-promoted extensions via [`isCoreInstanceExtension()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L365) and [`isCoreDeviceExtension()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L380)
- device creation requires a queue family with either compute-only capability or graphics+compute capability depending on command-line mode in [`createTestDevice()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L396)
- Vulkan SC-specific device-creation reservation structures are inserted under [`#ifdef CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L411)

## Verification Methods

Observed verification methods are explicit and varied:

- **version comparison**: fail if device major/minor exceeds framework-supported major/minor in [`APIVersionTestInstance::iterate()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L97)
- **proc-address null/non-null checks**: helper functions [`checkPlatformFunction()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L476), [`checkInstanceFunction()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L483), and [`checkDeviceFunction()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L490) compare returned addresses against expected nullability
- **failure accumulation**: loader mismatches are reported through [`reportFail()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L466), which increments a shared `failsQuantity`
- **final pass/fail decision**: the entry-point test fails if any mismatches were accumulated at [`vktApiVersionCheck.cpp`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L314)

## Test Principles Observed

- **Validate CTS applicability before deeper API checks**: the first observed test ensures the device version is within the Vulkan range this CTS build claims to support
- **Check both positive and negative loader behavior**: the file validates not only that expected functions can be loaded, but also that disabled or bogus names do not appear unexpectedly
- **Adapt expectations to runtime API/extension state**: supported enabled-extension functions are derived dynamically from enumerated extensions and API-version promotion rules
- **Keep low-level checks traceable**: explicit helper functions for platform/instance/device proc-address queries centralize nullability expectations and logging

## Notes / Uncertainties

- The inspected excerpt does not show the exact factory function that builds the `version` subgroup or the precise registration name of the test case backed by [`APIEntryPointsTestInstance`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L123), so this document avoids asserting a more detailed per-case hierarchy than the visible code supports.
- The internal contents of [`regularCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L195) and [`specialCasesCheck()`](../../modules/vulkan/api/vktApiVersionCheck.cpp#L225) are only partially visible from the inspected range, so their behavior is summarized from the calling pattern and nearby helper functions rather than fully reconstructed.
