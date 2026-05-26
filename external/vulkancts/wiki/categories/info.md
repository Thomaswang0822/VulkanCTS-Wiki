# info

## Overview

The [`info`](../../modules/vulkan/vktInfoTests.cpp#L260) category is a lightweight information and capability-reporting category registered by [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1347) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1415). It logs build, device, platform, and platform-memory-limit information, then delegates most of its coverage to API feature-info helpers declared in [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34).

## Registration Entry Point

The category is rooted in [`createInfoTests()`](../../modules/vulkan/vktInfoTests.cpp#L260), which adds a flat set of direct leaf cases: 21 in Vulkan builds and 19 in Vulkan SC builds because the two extension-dependency cases are guarded out. Group names below are verified against [`info.txt`](../../mustpass/main/vk-default/info.txt).

```text
info
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

Source: [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L260), verified against mustpass [`info.txt`](../../mustpass/main/vk-default/info.txt).

## File Inventory

| File | Role | Verified group name | Level-3 doc |
|---|---|---|---|
| [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L1) | Registration + implementation | (root) | [`vktInfoTests.md`](../testfiles/info/vktInfoTests.md) |
| [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928) | Implementation dependency | (flat augmentation) | [`vktApiFeatureInfo.md`](../testfiles/info/vktApiFeatureInfo.md) |
| [`vktInfoTests.hpp`](../../modules/vulkan/vktInfoTests.hpp#L1) | Declaration | — | — |
| [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34) | Declaration dependency | — | — |
| [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1347) | Package registration | — | — |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L1) | [`vktInfoTests.md`](../testfiles/info/vktInfoTests.md) |
| [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928) | [`vktApiFeatureInfo.md`](../testfiles/info/vktApiFeatureInfo.md) |

## Why the info Category Lives in the Root Module Path

Unlike every other category, `info` does not have its own subdirectory under `external/vulkancts/modules/vulkan/`. The source files [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp) and [`vktInfoTests.hpp`](../../modules/vulkan/vktInfoTests.hpp) reside directly in the root `modules/vulkan/` directory alongside [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp).

The reason is primarily historical and structural:

1. **Minimal scope**: The `info` category is one of the smallest categories in the CTS. The entire local implementation spans only ~280 lines in a single file, with just four lightweight local test cases (`build`, `device`, `platform`, `memory_limits`).

2. **Cross-category dependency**: The bulk of the `info` tree is not implemented in `vktInfoTests.cpp` at all. It is delegated to three builder functions defined in [`vktApiFeatureInfo.cpp`](../../modules/vulkan/api/vktApiFeatureInfo.cpp) — a file that belongs to the `api/` subdirectory. Creating a separate `info/` subdirectory for just two small files that delegate most of their work to `api/` was apparently not warranted.

3. **Early addition**: The `info` category was one of the first categories added to the CTS (copyright 2016). At that point, the convention of one subdirectory per category may not have been fully established, and the minimal file count did not justify creating a directory.

## Subgroup Structure and Major Themes

### Local cases from [`vktInfoTests.cpp`](../../modules/vulkan/vktInfoTests.cpp#L260)

Four direct function cases are registered before delegating to API feature-info coverage:

- `build` — logs compile-time environment macros such as OS, CPU, pointer size, endianness, compiler, and debug/non-debug configuration
- `device` — logs selected physical-device properties and the chosen `--deqp-vk-device-id`
- `platform` — delegates descriptive logging to the Vulkan platform's [`describePlatform()`](../../modules/vulkan/vktInfoTests.cpp#L173)
- `memory_limits` — logs platform memory-limit values and validates a few generic invariants

### Instance-information cases

Up to six instance-scope query and validation cases under the same `info` group; Vulkan SC omits the dependency-validation case:

- `physical_devices`
- `physical_device_groups`
- `instance_layers`
- `instance_extensions`
- `instance_extension_dependencies` (excluded when `CTS_USES_VULKANSC` is defined)
- `instance_extension_device_functions`

### Device-information cases

Up to ten device-scope query and validation cases; Vulkan SC omits the dependency-validation case:

- `device_features`
- `device_properties`
- `device_queue_family_properties`
- `device_memory_properties`
- `device_layers`
- `device_extensions`
- `device_extension_dependencies` (excluded when `CTS_USES_VULKANSC` is defined)
- `device_no_khx_extensions`
- `device_memory_budget`
- `device_mandatory_features`

### Device-group-information case

One device-group query case:

- `device_group_peer_memory_features`

## Cross-File Recurring Parameter Dimensions

| Dimension | Observed values / notes |
|---|---|
| Package variant | `info` is attached in both Vulkan and Vulkan SC package init paths |
| Local info source kind | build, device, platform, memory_limits |
| API-scope grouping | instance, device, and device-group builders in [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34) |
| Vulkan-SC conditional coverage | dependency-validation cases are omitted under `CTS_USES_VULKANSC` |

## Cross-File Recurring Support Requirements or Feature Gates

The inspected `info` registration code does not show the usual per-category feature gates seen in execution-heavy graphics categories. Instead, the observable gating is structural:

- the whole category is registered in both Vulkan and Vulkan SC packages through separate init functions
- two extension-dependency checks are conditionally excluded for Vulkan SC via preprocessor guards
- [`logPlatformMemoryLimits()`](../../modules/vulkan/vktInfoTests.cpp#L253) applies generic runtime assertions that total system memory and allocation granularity are non-zero and that page size is a power of two, but these are result checks rather than feature-enable gates
- delegated cases add narrower runtime requirements, including `device_memory_budget` requiring `VK_EXT_memory_budget` and `device_group_peer_memory_features` requiring a selected device group with at least two physical devices

## Cross-File Recurring Verification Methods

- **Pure logging with non-validating pass status**: `build`, `device`, and `platform` all return pass statuses whose message is `Not validated`
- **Logging plus simple invariant checks**: `memory_limits` logs numeric limits, then applies `TCU_CHECK` assertions before returning `Pass`
- **Delegated functional validation**: the API feature-info registrations include validation-oriented cases such as `instance_extension_dependencies`, `instance_extension_device_functions`, `device_extension_dependencies`, and `device_mandatory_features`. The detailed internal verification logic is documented at a summary level in the Level-3 delegated API feature-info page.

## Relationship to the Test Plan

[`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L161) describes API-query tests as validating that `vkGet*` functions return correct values, with generic checks for result sizing, pointer bounds, value stability, and concurrent queries. This matches the delegated instance/device feature-info query coverage summarized above.

## Notes / Uncertainties

- [`vktInfoTests.hpp`](../../modules/vulkan/vktInfoTests.hpp#L1) and [`vktApiFeatureInfo.hpp`](../../modules/vulkan/api/vktApiFeatureInfo.hpp#L1) are documentation-relevant declarations, but this category page treats them as supporting evidence rather than additional Level-3 targets because they are pure declaration files without registration paths.
- The detailed verification internals for delegated API feature-info cases are summarized in the corresponding Level-3 page; this category page intentionally keeps those details at a cross-file summary level.
