## Overview

The `info` test category collects host-side tests that report Vulkan CTS build, platform, and device information and check selected Vulkan API-query and capability-reporting rules.

## Background Knowledge

No common prerequisite concepts need category-level explanation for this test category.

## Category Structure

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
├── instance_extension_dependencies (Vulkan only)
├── instance_extension_device_functions
├── device_features
├── device_properties
├── device_queue_family_properties
├── device_memory_properties
├── device_layers
├── device_extensions
├── device_extension_dependencies (Vulkan only)
├── device_no_khx_extensions
├── device_memory_budget
├── device_mandatory_features
└── device_group_peer_memory_features
```

`vktInfoTests.cpp` implements the first four test case leaves and registers the category. It delegates the remaining leaves to the API feature-info builders. The two extension-dependency leaves are absent from Vulkan SC builds [registration](../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960).

## How the Families Fit Together

The category makes the CTS environment and the implementation's advertised API surface inspectable without running rendering workloads.

- `build`, `device`, and `platform` report the selected CTS and platform environment; `memory_limits` adds basic CTS platform-memory checks.
- Enumeration leaves inspect instance, device, layer, extension, and device-group lists, including selected incomplete-result and naming rules.
- Property and capability leaves validate returned physical-device structures, extension dependencies, entry points, mandatory features, memory budgets, and peer-memory support.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `build`, `device`, `platform`, `memory_limits` | [InfoTests](../testfiles/info/InfoTests.md) | The four local reporting leaves, the CTS platform-memory checks, and their failure boundaries. |
| Instance, device, and device-group API information leaves | [ApiFeatureInfo](../testfiles/info/ApiFeatureInfo.md) | Enumeration, physical-device query, extension consistency, memory-budget, mandatory-feature, and peer-memory validation. |
