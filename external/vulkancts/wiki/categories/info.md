# info

## Overview

The [`info`](../../modules/vulkan/vktInfoTests.cpp#L274) category is registered as a top-level Vulkan CTS root by [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1348) and also by the Vulkan SC package initializer [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1416). In the inspected sources, this category is a lightweight information and capability-reporting category rather than a feature-execution category: it logs build, device, platform, and platform-memory-limit information in [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L132), then delegates most of its coverage to API feature-info helpers declared in [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34) and attached from [`createInfoTests()`](../../modules/vulkan/vktInfoTests.cpp#L260).

## Registration Entry Point

The top-level registration path observed in the inspected files is:

```text
root
└── info
    ├── build
    ├── device
    ├── platform
    ├── memory_limits
    ├── physical_devices
    ├── physical_device_groups
    ├── instance_layers
    ├── instance_extensions
    ├── instance_extension_dependencies          (not added for Vulkan SC)
    ├── instance_extension_device_functions
    ├── device_features
    ├── device_properties
    ├── device_queue_family_properties
    ├── device_memory_properties
    ├── device_layers
    ├── device_extensions
    ├── device_extension_dependencies            (not added for Vulkan SC)
    ├── device_no_khx_extensions
    ├── device_memory_budget
    ├── device_mandatory_features
    └── device_group_peer_memory_features
```

Evidence:
- root registration in [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1348)
- Vulkan SC root registration in [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1416)
- local subgroup assembly in [`createInfoTests()`](../../modules/vulkan/vktInfoTests.cpp#L260)
- delegated instance/device/device-group cases in [`createFeatureInfoInstanceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924), [`createFeatureInfoDeviceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937), and [`createFeatureInfoDeviceGroupTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953)

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L1) | Registration + implementation | Owns the top-level `info` group and implements the four lightweight local cases plus delegation into API feature-info helpers |
| [`vktInfoTests.hpp`](../../modules/vulkan/vktInfoTests.hpp#L1) | Declaration | Declares [`createTests()`](../../modules/vulkan/vktInfoTests.hpp#L34) for the category entry point |
| [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) | Implementation dependency | Provides the delegated instance, device, and device-group info cases that become part of the `info` tree |
| [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34) | Declaration dependency | Declares the feature-info group builders called from [`createInfoTests()`](../../modules/vulkan/vktInfoTests.cpp#L267) |
| [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1346) | Package registration | Registers `info` as a root category for both Vulkan and Vulkan SC package initializers |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L1) | [`vktInfoTests.md`](../testfiles/info/vktInfoTests.md) |
| [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) | [`vktApiFeatureInfo.md`](../testfiles/info/vktApiFeatureInfo.md) |

## Subgroup Structure and Major Themes

### Local `info` cases from [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L260)

[`createInfoTests()`](../../modules/vulkan/vktInfoTests.cpp#L260) registers four direct function cases before delegating further API feature-info coverage:

- [`build`](../../modules/vulkan/vktInfoTests.cpp#L262) logs compile-time environment macros such as OS, CPU, pointer size, endianness, compiler, and debug/non-debug configuration in [`logBuildInfo()`](../../modules/vulkan/vktInfoTests.cpp#L132)
- [`device`](../../modules/vulkan/vktInfoTests.cpp#L263) logs selected physical-device properties and the chosen `--deqp-vk-device-id` in [`logDeviceInfo()`](../../modules/vulkan/vktInfoTests.cpp#L151)
- [`platform`](../../modules/vulkan/vktInfoTests.cpp#L264) delegates descriptive logging to [`describePlatform()`](../../modules/vulkan/vktInfoTests.cpp#L173) through [`logPlatformInfo()`](../../modules/vulkan/vktInfoTests.cpp#L169)
- [`memory_limits`](../../modules/vulkan/vktInfoTests.cpp#L265) logs platform memory-limit values and validates a few generic invariants in [`logPlatformMemoryLimits()`](../../modules/vulkan/vktInfoTests.cpp#L236)

### Delegated instance-information cases

[`createFeatureInfoInstanceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) adds instance-scope query and validation cases under the same `info` group:

- [`physical_devices`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8926)
- [`physical_device_groups`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8927)
- [`instance_layers`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928)
- [`instance_extensions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8929)
- [`instance_extension_dependencies`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931), excluded when [`CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) is defined
- [`instance_extension_device_functions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8933)

### Delegated device-information cases

[`createFeatureInfoDeviceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937) adds device-scope query and validation cases:

- [`device_features`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8939)
- [`device_properties`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8940)
- [`device_queue_family_properties`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8941)
- [`device_memory_properties`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8942)
- [`device_layers`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8943)
- [`device_extensions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8944)
- [`device_extension_dependencies`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8946), excluded when [`CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945) is defined
- [`device_no_khx_extensions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8948)
- [`device_memory_budget`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8949)
- [`device_mandatory_features`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8950)

### Delegated device-group-information case

[`createFeatureInfoDeviceGroupTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) contributes one device-group query case:

- [`device_group_peer_memory_features`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8955)

## Cross-File Recurring Test Families or Themes

Across the inspected `info` sources, the major recurring themes are:

| Theme | Evidence |
|---|---|
| Build-environment reporting | [`logBuildInfo()`](../../modules/vulkan/vktInfoTests.cpp#L132) |
| Selected device-property reporting | [`logDeviceInfo()`](../../modules/vulkan/vktInfoTests.cpp#L151) |
| Platform description reporting | [`logPlatformInfo()`](../../modules/vulkan/vktInfoTests.cpp#L169) |
| Platform memory-limit reporting plus simple invariant checks | [`logPlatformMemoryLimits()`](../../modules/vulkan/vktInfoTests.cpp#L236) |
| Instance enumeration and extension/layer reporting | [`createFeatureInfoInstanceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) |
| Device feature/property/memory/extension reporting | [`createFeatureInfoDeviceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937) |
| Device-group capability reporting | [`createFeatureInfoDeviceGroupTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) |
| Extension-dependency validation rather than pure logging | [`instance_extension_dependencies`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931), [`device_extension_dependencies`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8946) |

## Cross-File Recurring Parameter Dimensions

The `info` category is lightweight and largely function-case driven, so it exposes fewer explicit parameter matrices than execution-heavy categories. The following dimensions are directly observable in the inspected files:

| Dimension | Observed values / notes |
|---|---|
| Package variant | `info` is attached in both Vulkan and Vulkan SC package init paths: [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1346) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1414) |
| Local info source kind | build, device, platform, memory limits from [`createInfoTests()`](../../modules/vulkan/vktInfoTests.cpp#L262) |
| API-scope grouping | instance, device, and device-group helper builders in [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34) |
| Vulkan-SC conditional coverage | dependency-validation cases are omitted under [`CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) and [`CTS_USES_VULKANSC`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945) |
| Memory-size presentation | byte counts are formatted into TiB/GiB/MiB/KiB/B units by [`getBestSizeUnit()`](../../modules/vulkan/vktInfoTests.cpp#L197) and [`operator<<`](../../modules/vulkan/vktInfoTests.cpp#L218) |

## Cross-File Recurring Support Requirements or Feature Gates

The inspected `info` registration code does not show the usual per-category feature gates seen in execution-heavy graphics categories. Instead, the observable gating is structural:

- the whole category is registered in both Vulkan and Vulkan SC packages through separate init functions at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1346) and [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1414)
- two extension-dependency checks are conditionally excluded for Vulkan SC via preprocessor guards in [`createFeatureInfoInstanceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) and [`createFeatureInfoDeviceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945)
- [`logPlatformMemoryLimits()`](../../modules/vulkan/vktInfoTests.cpp#L253) applies generic runtime assertions that total system memory and allocation granularity are non-zero and that page size is a power of two, but these are result checks rather than feature-enable gates

No stronger category-wide feature requirement is confirmed from the inspected registration snippets alone.

## Cross-File Recurring Verification Methods

Observed verification/reporting styles differ between the local file and the delegated API feature-info builder registrations:

- **Pure logging with non-validating pass status**: [`logBuildInfo()`](../../modules/vulkan/vktInfoTests.cpp#L148), [`logDeviceInfo()`](../../modules/vulkan/vktInfoTests.cpp#L166), and [`logPlatformInfo()`](../../modules/vulkan/vktInfoTests.cpp#L177) all return pass statuses whose message is `Not validated`
- **Logging plus simple invariant checks**: [`logPlatformMemoryLimits()`](../../modules/vulkan/vktInfoTests.cpp#L243) logs numeric limits, then applies [`TCU_CHECK`](../../modules/vulkan/vktInfoTests.cpp#L253) assertions before returning `Pass`
- **Delegated functional validation**: the API feature-info registrations name validation-oriented cases such as [`validateInstanceExtensionDependencies`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931), [`validateDeviceLevelEntryPointsFromInstanceExtensions`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934), [`validateDeviceExtensionDependencies`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8946), and [`deviceMandatoryFeatures`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8950). The detailed internal verification logic for those functions is not described here because it was not fully inspected end-to-end in this pass.

## Relationship to the Test Plan

[`apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc#L158) contains an `API Queries` section that states the objective is to validate that various `vkGet*` functions return correct values and lists generic checks such as returned-size sanity, no out-of-bounds writes, value stability, and concurrent-query behavior. That high-level purpose is relevant to the delegated feature-info coverage registered through [`createFeatureInfoInstanceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) and [`createFeatureInfoDeviceTests()`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937), although the test-plan text does not enumerate the exact `info` category case names seen in the code.

The same plan file also describes the Vulkan CTS `TestCase` / `TestInstance` execution model in [`Test case base class`](../../../doc/testspecs/VK/apitests.adoc#L20), which is relevant background but does not materially change the `info` category structure derived from source.

## Notes / Uncertainties

- [`vktInfoTests.hpp`](../../modules/vulkan/vktInfoTests.hpp#L1) and [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L1) are documentation-relevant declarations, but this category page treats them as supporting evidence rather than additional Level-3 targets because the user requested Level-3 docs for source files under [`testfiles/info/`](../testfiles/info/).
- The detailed verification internals for the delegated API feature-info cases are only summarized at registration level here unless directly visible in inspected snippets; unsupported claims about their deeper logic are intentionally avoided.
