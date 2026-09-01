## Overview

The `device_group` test category checks whether rendering and compute work produce the expected results when a logical device uses one or more physical devices from an enumerated device group.

## Background Knowledge

- **Physical-device groups.** Vulkan can enumerate a group of compatible physical devices and create one logical device from a subset of that group. The group determines which physical devices may participate in the test. See [device-group enumeration and logical-device creation](../../../vulkan-docs/src/chapters/devsandqueues.adoc#L2010-L2017).
- **Device masks.** A device mask selects the physical devices that execute a command or own an allocation. Split-frame and split-dispatch cases use different masks for different portions of the work; alternate cases rotate the active device between submissions.
- **Peer memory.** A device may read memory allocated for another group member only when the device group reports the required peer access. This is why peer variants have a stricter support check than ordinary split or alternate variants.

## Category Structure

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

All 18 direct test families are implemented and registered by `vktDeviceGroupRendering.cpp`. The header only declares the category factory.

## How the Families Fit Together

The families vary the work distribution and the memory arrangement used by the same device-group idea.

- `sfr*` splits rendering work between devices, while `compute_split_dispatch*` splits compute work. The SFR and split-dispatch families are absent from Vulkan SC builds when guarded by `CTS_USES_VULKANSC`.
- `afr*` assigns successive frames or dispatches to alternate devices. The rendering variants add host-memory, dedicated-allocation, peer-fetch, tessellation, or line-fill choices.
- `compute_split_dispatch*` and `compute_alternate_dispatch*` apply the corresponding distribution choices to a storage-image compute operation.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| All rendering and compute device-group families | [Rendering.md](../testfiles/device_group/Rendering.md) | Device masks, allocation and peer-memory variants, shader roles, readback checks, support gates, and failure meaning |

## Category Notes

The default Vulkan mustpass contains 18 device-group paths. Vulkan SC conditional compilation removes the split-frame and split-dispatch families from registration; the source and mustpass evidence determine the active set for the build.
