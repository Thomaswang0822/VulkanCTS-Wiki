# vktApiFeatureInfo.cpp

## Overview

[`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) contributes most of the executable surface that appears under the lightweight [`info`](../../categories/info.md) category. In the inspected range, the file does not create a nested subgroup for these cases; instead, it appends instance-, device-, and device-group-oriented function cases directly into the parent group passed from [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L260).

## Role

Implementation file used by the `info` category.

## Source Code

- Primary inspected source: [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924)
- Related declarations: [`vktApiFeatureInfo.hpp`](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34)
- Calling site from the `info` category: [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L267)

## Registration Path

The inspected registration path is:

```text
TestPackage::init / TestPackageSC::init
└── info
    └── createTests(testCtx, "info")
        └── createInfoTests(testGroup)
            ├── createFeatureInfoInstanceTests(testGroup)
            ├── createFeatureInfoDeviceTests(testGroup)
            └── createFeatureInfoDeviceGroupTests(testGroup)
```

Evidence:
- root attachment in [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1348) and [`TestPackageSC::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1416)
- delegation from [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L267)
- declarations in [`vktApiFeatureInfo.hpp`](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L35)

## Test Hierarchy

```text
info
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

Source: [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924), [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937), and [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953).

## Test Families

### 1. Instance enumeration and dependency validation

[`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) adds six instance-scope cases to the parent group:

- [`physical_devices`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8926) via [`enumeratePhysicalDevices`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8926)
- [`physical_device_groups`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8927) via [`enumeratePhysicalDeviceGroups`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8927)
- [`instance_layers`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928) via [`enumerateInstanceLayers`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928)
- [`instance_extensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8929) via [`enumerateInstanceExtensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8929)
- [`instance_extension_dependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931) via [`validateInstanceExtensionDependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931), omitted when [`CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) is defined
- [`instance_extension_device_functions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8933) via [`validateDeviceLevelEntryPointsFromInstanceExtensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934)

The family mixes pure enumeration-style names with validation-style names, so the inspected registration suggests both reporting and correctness checking responsibilities.

### 2. Device feature/property/memory/extension coverage

[`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937) adds ten device-scope cases:

- [`device_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8939)
- [`device_properties`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8940)
- [`device_queue_family_properties`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8941)
- [`device_memory_properties`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8942)
- [`device_layers`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8943)
- [`device_extensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8944)
- [`device_extension_dependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8946), omitted when [`CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945) is defined
- [`device_no_khx_extensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8948)
- [`device_memory_budget`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8949)
- [`device_mandatory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8950)

This family covers feature/property discovery, queue-family and memory properties, extension reporting/dependency validation, and a few policy-oriented checks whose exact internal logic is not fully described in the inspected snippet.

### 3. Device-group peer-memory query

[`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) adds one device-group-oriented case:

- [`device_group_peer_memory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8955) via [`deviceGroupPeerMemoryFeatures`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8956)

Although it is only one case, it shows that the file extends beyond plain instance/device queries into device-group capability reporting.

## Parameter Dimensions

| Parameter / dimension | Observed values / source |
|---|---|
| API scope | instance in [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924), device in [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937), device group in [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) |
| Function-case style | plain [`addFunctionCase`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8926) and templated [`addFunctionCase<CustomInstanceTest<E071>>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8927) |
| Vulkan-SC conditional cases | instance dependency validation excluded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930), device dependency validation excluded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945) |
| Instance-scope case set | physical devices, physical device groups, layers, extensions, extension dependencies, instance-extension device functions from [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) |
| Device-scope case set | features, properties, queue-family properties, memory properties, layers, extensions, extension dependencies, no-KHX check, memory budget, mandatory features from [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937) |
| Device-group case set | peer-memory-features query from [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) |

## Support / Feature Requirements

Observed structural requirements in the inspected range are:

- these registrations only appear when [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L267) delegates into them
- the dependency-validation cases are not compiled into Vulkan SC builds because of [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) and [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945)
- [`physical_device_groups`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8927) and [`device_group_peer_memory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8955) are wrapped with [`CustomInstanceTest<E071>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8927), but the significance of `E071` is not explained in the inspected snippet, so no stronger claim is made here

No explicit feature-bit gate is visible in this registration slice.

## Verification Methods

The inspected range mostly exposes registration names rather than internal function bodies, so the safest evidence-backed summary is:

- **enumeration/reporting-oriented cases** are suggested by names such as [`enumeratePhysicalDevices`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8926), [`enumerateInstanceLayers`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928), and [`enumerateDeviceExtensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8944)
- **validation-oriented cases** are explicitly named [`validateInstanceExtensionDependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931), [`validateDeviceLevelEntryPointsFromInstanceExtensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934), [`validateDeviceExtensionDependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8946), and [`deviceMandatoryFeatures`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8950)
- the exact pass/fail criteria of those delegated functions are **not confirmed from the inspected snippet alone**, so this document intentionally avoids describing deeper result logic that was not directly examined

## Test Principles Observed

- **Flat augmentation of the parent group**: this file adds cases directly to the `info` group instead of introducing another subgroup layer
- **Separate API scopes by helper function**: instance, device, and device-group coverage are split across three builder functions declared in [`vktApiFeatureInfo.hpp`](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34)
- **Use naming to communicate intent**: the case/function names distinguish enumeration-oriented queries from validation-oriented dependency or mandatory-feature checks
- **Preserve portability across package variants**: Vulkan-SC-specific exclusions are handled with compile-time guards rather than runtime branching in the inspected range

## Notes / Uncertainties

- This document is intentionally based on the inspected registration region around [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924). It does not claim detailed per-case verification internals beyond what the visible function names justify.
- The full file is much larger than the inspected slice, so there may be additional helper types or shared logic elsewhere in the file that influence these tests; those details are not asserted here unless directly visible in the cited lines.
