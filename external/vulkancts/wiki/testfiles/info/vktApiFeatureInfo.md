# vktApiFeatureInfo.cpp

## Overview

[`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928) contributes most of the executable surface that appears under the lightweight [`info`](../../categories/info.md) category. In the inspected range, the file does not create a nested subgroup for these cases; instead, it appends instance-, device-, and device-group-oriented function cases directly into the parent group passed from [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L260).

## Role

Implementation file used by the `info` category.

## Source Code

- Primary inspected source: [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928)
- Related declarations: [`vktApiFeatureInfo.hpp`](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34)
- Calling site from the `info` category: [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L267)

## Registration Hierarchy

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
├── instance_extension_dependencies (not added for Vulkan SC)
├── instance_extension_device_functions
├── device_features
├── device_properties
├── device_queue_family_properties
├── device_memory_properties
├── device_layers
├── device_extensions
├── device_extension_dependencies (not added for Vulkan SC)
├── device_no_khx_extensions
├── device_memory_budget
├── device_mandatory_features
└── device_group_peer_memory_features
```

Evidence:
- root attachment in [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1347) and [`TestPackageSC::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1415)
- local cases from [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L260-L265) documented separately in [`vktInfoTests.md`](vktInfoTests.md)
- instance-scope cases from [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8939)
- device-scope cases from [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8941-L8955)
- device-group case from [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8957-L8960)

## Test Families

This file implements instance-scope, device-scope, and device-group cases that are added directly to the `info` group. The first four direct children (`build`, `device`, `platform`, `memory_limits`) are implemented in [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L260-L265) and documented in [`vktInfoTests.md`](vktInfoTests.md).

### physical_devices — Physical device enumeration

[`physical_devices`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) dispatches to [`enumeratePhysicalDevices()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2632), which enumerates devices, logs the count and handles, and checks incomplete-result behavior.

### physical_device_groups — Physical device group enumeration

[`physical_device_groups`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931) dispatches to [`enumeratePhysicalDeviceGroups()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2649) through [`CustomInstanceTest<E071>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L776), which requests `VK_KHR_device_group_creation` via [`CustomInstanceDeterminant<E071>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L749-L760).

### instance_layers — Instance layer enumeration

[`instance_layers`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8932) dispatches to [`enumerateInstanceLayers()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2759), which logs layer properties, checks duplicate layer names, and checks incomplete-result behavior.

### instance_extensions — Instance extension enumeration

[`instance_extensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8933) dispatches to [`enumerateInstanceExtensions()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2779), which checks global and per-layer instance extension lists for duplicate and unknown Khronos-controlled names.

### instance_extension_dependencies — Instance extension dependency validation

[`instance_extension_dependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8935) dispatches to [`validateInstanceExtensionDependencies()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2828), which checks advertised instance extensions against generated dependency data for the first supported released API version.

This case is omitted when [`CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934) is defined.

### instance_extension_device_functions — Instance extension device function validation

[`instance_extension_device_functions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937-L8938) dispatches to [`validateDeviceLevelEntryPointsFromInstanceExtensions()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2853), which verifies device-level entry points for supported instance extensions are obtainable through `vkGetDeviceProcAddr`.

### device_features — Device feature reporting

[`device_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8943) dispatches to [`deviceFeatures()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3056), which queries `VkPhysicalDeviceFeatures`, requires `robustBufferAccess`, checks guard bytes, and validates complete initialization.

### device_properties — Device property reporting

[`device_properties`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8944) dispatches to [`deviceProperties()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3276), which validates feature-dependent limits, guard bytes, complete initialization, null-terminated device names, and API-version bounds.

### device_queue_family_properties — Device queue family property reporting

[`device_queue_family_properties`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945) dispatches to [`deviceQueueFamilyProperties()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3348), which logs queried queue-family properties and returns success.

### device_memory_properties — Device memory property validation

[`device_memory_properties`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8946) dispatches to [`deviceMemoryProperties()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3362), which checks guard bytes, heap/type bounds, accepted memory-property flag combinations, heap consistency, and required host-visible coherent memory.

### device_layers — Device layer enumeration

[`device_layers`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8947) dispatches to [`enumerateDeviceLayers()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2922), which logs device layer properties, checks duplicate layer names, and checks incomplete-result behavior.

### device_extensions — Device extension enumeration

[`device_extensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8948) dispatches to [`enumerateDeviceExtensions()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2943), which checks global and per-layer device extension lists for duplicate and unknown Khronos-controlled names.

### device_extension_dependencies — Device extension dependency validation

[`device_extension_dependencies`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8950) dispatches to [`validateDeviceExtensionDependencies()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2993), which checks advertised device extensions against generated dependency data for the first supported released API version.

This case is omitted when [`CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8949) is defined.

### device_no_khx_extensions — Device KHX extension check

[`device_no_khx_extensions`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8952) dispatches to [`testNoKhxExtensions()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2879), which combines instance and device extension properties and fails if any extension name starts with `VK_KHX_`.

### device_memory_budget — Device memory budget validation

[`device_memory_budget`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) dispatches to [`deviceMemoryBudgetProperties()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3667), which requires `VK_EXT_memory_budget`, checks guard bytes, verifies supported heaps report nonzero budgets not exceeding heap size, and verifies unused heaps report zero budget and usage.

### device_mandatory_features — Device mandatory feature validation

[`device_mandatory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8954) dispatches to [`deviceMandatoryFeatures()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3739), which uses generated mandatory-feature checks and adds a Vulkan 1.4 host-image-copy/queue-availability condition for non-compute-only Vulkan builds.

### device_group_peer_memory_features — Device group peer memory feature query

[`device_group_peer_memory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8959) dispatches to [`deviceGroupPeerMemoryFeatures()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3495) through [`CustomInstanceTest<E071>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L776). It requires a selected device group with at least two physical devices, creates a device group, checks guard bytes, and validates peer-memory feature flags.

## Parameter Dimensions

| Parameter / dimension | Observed values / source |
|---|---|
| API scope | instance in [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928), device in [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8941), device group in [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8957) |
| Function-case style | plain [`addFunctionCase`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) and templated [`addFunctionCase<CustomInstanceTest<E071>>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931) |
| Vulkan-SC conditional cases | instance dependency validation excluded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934), device dependency validation excluded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8949) |
| Instance-scope case set | physical devices, physical device groups, layers, extensions, extension dependencies, instance-extension device functions from [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928) |
| Device-scope case set | features, properties, queue-family properties, memory properties, layers, extensions, extension dependencies, no-KHX check, memory budget, mandatory features from [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8941) |
| Device-group case set | peer-memory-features query from [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8957) |

## Support / Feature Requirements

Observed structural requirements in the inspected range are:

- these registrations only appear when [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L267) delegates into them
- the dependency-validation cases are not compiled into Vulkan SC builds because of [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934) and [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8949)
- [`physical_device_groups`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8931) and [`device_group_peer_memory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8959) are wrapped with [`CustomInstanceTest<E071>`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L776), which requests `VK_KHR_device_group_creation` and throws `NotSupportedError` if that extension cannot be added
- [`device_memory_budget`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953) requires `VK_EXT_memory_budget` at runtime before querying memory-budget properties
- [`device_group_peer_memory_features`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8959) also requires the selected device group and device index to be valid and the device group to contain at least two physical devices

## Verification Methods

The inspected registration and function bodies show these result styles:

- **enumeration/reporting plus API-query robustness checks**: physical-device, layer, and extension enumeration cases log queried values and use result collectors for duplicate-name, unknown-extension, or incomplete-result checks
- **guard-byte and initialization validation**: feature, property, memory-property, memory-budget, and peer-memory-feature cases check that queried APIs do not overwrite guard bytes and, where applicable, initialize expected struct members
- **semantic capability validation**: dependency, entry-point, KHX-name, mandatory-feature, memory-property, memory-budget, and peer-memory-feature cases fail on missing dependencies, missing device entry points, invalid extension names, unsupported mandatory features, invalid memory flags/budgets, or invalid peer-memory feature flags
- **unsupported-configuration skips**: memory-budget and device-group peer-memory cases throw `NotSupportedError` for unsupported extensions or invalid/insufficient device-group configurations

## Test Principles Observed

- **Flat augmentation of the parent group**: this file adds cases directly to the `info` group instead of introducing another subgroup layer
- **Separate API scopes by helper function**: instance, device, and device-group coverage are split across three builder functions declared in [`vktApiFeatureInfo.hpp`](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34)
- **Use naming to communicate intent**: the case/function names distinguish enumeration-oriented queries from validation-oriented dependency or mandatory-feature checks
- **Preserve portability across package variants**: Vulkan-SC-specific exclusions are handled with compile-time guards rather than runtime branching in the inspected range

## Notes / Uncertainties

- This document summarizes the inspected registration region around [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928) plus the corresponding function bodies for the direct `info` children. It still avoids claiming behavior for helper code outside the inspected paths unless directly visible in the cited lines.
