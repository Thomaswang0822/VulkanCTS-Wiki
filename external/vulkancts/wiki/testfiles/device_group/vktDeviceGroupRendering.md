# vktDeviceGroupRendering.cpp

## Overview

`vktDeviceGroupRendering.cpp` is the sole registering source file in the `device_group` category. It constructs a `DeviceGroupTestRendering` group using the category name supplied by the package and registers rendering and compute tests for split-frame, alternate-frame, split-dispatch, and alternate-dispatch modes.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktDeviceGroupRendering.cpp](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp) |
| File purpose comment | [Device Group Tests comment](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L20-L23) |
| Test mode flags | [`TestModeType`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L71-L80) |
| Registered group and direct children | [`DeviceGroupTestRendering::init()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2639-L2715) |
| Category factory | [`createTests()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2717-L2720) |
| Package root registration | [`addRootChild("device_group", ...)`](../../../modules/vulkan/vktTestPackage.cpp#L1377-L1379) |

## Registration Hierarchy

```text
device_group
├── afr
├── afr_dedicated
├── afr_dedicated_peer
├── afr_sys
├── afr_tessellated
├── afr_tessellated_linefill
├── compute_alternate_dispatch
├── compute_alternate_dispatch_dedicated
├── compute_alternate_dispatch_peer
├── compute_split_dispatch
├── compute_split_dispatch_dedicated
├── compute_split_dispatch_peer
├── sfr
├── sfr_dedicated
├── sfr_dedicated_peer
├── sfr_sys
├── sfr_tessellated
└── sfr_tessellated_linefill
```

## Test Families

### Rendering mode cases

The rendering tests include split-frame rendering (`sfr*`) and alternate-frame rendering (`afr*`) cases. SFR direct children are excluded under `CTS_USES_VULKANSC` in the registration function, while AFR children remain registered in both branches observed in the source.

### Tessellated rendering cases

The `*_tessellated` and `*_tessellated_linefill` children enable tessellation and, for linefill variants, non-solid polygon filling. The SFR tessellated variants are also under the non-VulkanSC registration guard.

### Compute dispatch cases

The compute tests include split-dispatch (`compute_split_dispatch*`) and alternate-dispatch (`compute_alternate_dispatch*`) cases. Split-dispatch children are under the non-VulkanSC guard; alternate-dispatch children are registered outside that guard.

## Parameter Dimensions

| Dimension | Observed values |
|---|---|
| Rendering schedule | SFR and AFR test modes are defined as flags and used in the registered rendering cases. |
| Memory allocation variants | Host-memory render target, dedicated allocation, and peer-fetch flags appear in registered rendering modes. |
| Geometry variants | Tessellated sphere and non-solid line-fill flags are used by tessellated rendering children. |
| Compute schedule | Split dispatch and alternate dispatch modes are used by registered compute cases. |
| Compute memory variants | Dedicated allocation and peer-memory flags appear in compute children. |

## Support / Feature Requirements

Rendering cases require `VK_KHR_device_group_creation` at instance level and `VK_KHR_device_group` at device level. Dedicated-allocation variants require `VK_KHR_dedicated_allocation`. Cases that need peer access require more than one physical device in the selected group. Bind-memory2 is required when the mode is not AFR or when the selected physical-device group has more than one device. Tessellated and line-fill cases check `tessellationShader` and `fillModeNonSolid` device features. Compute cases perform parallel checks for device-group creation, `VK_KHR_device_group`, dedicated allocation, peer-memory device count, and conditional `VK_KHR_bind_memory2` support.

## Verification Methods

Rendering tests read back the rendered target. Tessellated-sphere cases compare against archived PNG references with `tcu::fuzzyCompare()`, while triangle cases render a reference image and use `tcu::intThresholdPositionDeviationCompare()` with zero color threshold and one-pixel position deviation. Compute tests clear a reference image to the expected draw color and compare the result with `tcu::intThresholdPositionDeviationCompare()` using zero color and position deviation.

## Test Principles

The category creates a logical device from a selected physical-device group, submits work with device masks, and checks that multi-device rendering or compute output matches a single expected image result.

## Notes and Uncertainties

The source registers SFR and split-dispatch children only when `CTS_USES_VULKANSC` is not defined. The default Vulkan mustpass file includes all 18 direct children, while the Vulkan SC mustpass file has fewer device-group paths. This page lists the default Vulkan direct children and calls out the source guard.
