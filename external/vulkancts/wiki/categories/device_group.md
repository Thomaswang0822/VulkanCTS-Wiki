# Device Group Tests

## Summary

The `device_group` category documents tests from one source file, `vktDeviceGroupRendering.cpp`. The tests create and use device groups to exercise split-frame rendering, alternate-frame rendering, split and alternate compute dispatch, dedicated allocations, peer access, host-memory render targets, tessellated geometry, and line-fill variants where registered. The Vulkan API test plan provides only broad device-initialization context for multiple devices from one physical device and queue configurations ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L345-L349)); source evidence below defines this category's current behavior.

## Registration Entry Point

| Item | Evidence |
|---|---|
| Package root registration | [`addRootChild("device_group", ...)`](../../modules/vulkan/vktTestPackage.cpp#L1377-L1379) |
| Category factory | [`DeviceGroup::createTests()`](../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2717-L2720) |
| Direct child registration | [`DeviceGroupTestRendering::init()`](../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2645-L2715) |
| Related test-plan context | [device initialization notes](../../../../doc/testspecs/VK/apitests.adoc#L345-L349) |

## Subgroup Structure

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

## File Inventory

| File | Registered group | Role |
|---|---:|---|
| [vktDeviceGroupRendering.cpp](../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp) | `device_group` | Category implementation and direct test registration. |
| [vktDeviceGroupTests.hpp](../../modules/vulkan/device_group/vktDeviceGroupTests.hpp) | declaration only | Declares `DeviceGroup::createTests()`; no separate Level-3 page because it does not register tests. |

## Recurring Test Families

- `sfr*` cases exercise split-frame rendering and are registered only outside `CTS_USES_VULKANSC` guards.
- `afr*` cases exercise alternate-frame rendering and include host-memory, dedicated-allocation, peer-fetch, tessellated, and line-fill variants observed in registration.
- `compute_split_dispatch*` cases exercise split compute dispatch and are registered only outside `CTS_USES_VULKANSC` guards.
- `compute_alternate_dispatch*` cases exercise alternate compute dispatch with dedicated and peer-memory variants.

## Recurring Parameters

| Dimension | Evidence |
|---|---|
| Rendering flags | [`TestModeType`](../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L71-L80) |
| Rendering direct children | [`DeviceGroupTestRendering::init()`](../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2645-L2690) |
| Compute direct children | [`DeviceGroupTestRendering::init()`](../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2692-L2715) |
| Device-group selection | Command-line group/device IDs used during initialization in rendering and compute paths. |

## Support / Feature Requirements

The rendering support path requires `VK_KHR_device_group_creation` and `VK_KHR_device_group`, adds `VK_KHR_dedicated_allocation` for dedicated variants, validates selected group and device IDs, rejects peer-fetch cases with fewer than two physical devices, and conditionally requires `VK_KHR_bind_memory2`. Tessellated and line-fill variants check `tessellationShader` and `fillModeNonSolid`. The compute path performs corresponding extension, selected-device, peer-memory, and bind-memory2 checks.

## Verification Methods

Rendering paths compare readback images to either archived sphere PNG references or generated triangle references. Compute paths compare readback images to a uniform expected color. These comparisons are implemented in the source using `tcu::fuzzyCompare()` and `tcu::intThresholdPositionDeviationCompare()`.

## Level-3 Pages

- [vktDeviceGroupRendering.md](../testfiles/device_group/vktDeviceGroupRendering.md)

## Scope Notes

This category has one Level-3 page because only `vktDeviceGroupRendering.cpp` registers tests in the inspected `device_group` source directory.
