## Overview

The `postmortem` test category collects tests that exercise Vulkan behavior around device faults and device loss, including the APIs used to retrieve information after execution has failed.

The category has two registration surfaces. The standard package exposes the `device_fault` tests backed by `VK_EXT_device_fault`; the experimental package adds disruptive workloads and a second device-fault implementation for controlled real and fake fault paths ([standard dispatcher](../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L41-L45), [experimental dispatcher](../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L47-L54), [package registration](../../modules/vulkan/vktTestPackage.cpp#L1428-L1435)).

## Background Knowledge

- **Device loss and post-loss queries.** A device-loss event makes ordinary device execution unusable, but Vulkan still defines specific operations that can report what happened or expose the resulting status. These tests distinguish obtaining a fault report from merely detecting that work failed.
- **Fault-report query contracts.** A query may first return the number of available records or the required byte count, then populate caller-owned storage. The caller must pass the returned sizes back on the fill call and handle cases where the storage is empty, too small, or larger than needed. This pattern is shared by the device-fault families.
- **Support versus execution.** A device extension or feature check says that a test is legal to run; it does not prove that a particular fault, timeout, or post-loss result occurred. The Level-3 pages separate support skips from the result checks performed by each workload.

## Category Structure

```text
postmortem
├── device_fault
├── shader_timeout
├── use_after_free
└── device_loss
```

The standard package registers only `device_fault`. The experimental package registers all four branches. Both packages use the registered name `device_fault`, but they reach different factories: the standard branch calls `createDeviceFaultTestsKHR`, while the experimental branch calls `createDeviceFaultTests` alongside the other experimental families ([factory dispatch](../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L41-L65), [KHR device-fault tree](../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1088-L1160), [experimental device-fault tree](../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L492-L507)).

`device_fault` is the only branch represented in the default mustpass list. Its listed cases cover `no_fault`, `with_fault_base`, and `with_fault_waitidle`, including asynchronous, blocking, draining, zero-report, and vendor-binary query variants ([default mustpass](../../mustpass/main/vk-default/postmortem.txt#L1-L24)). The experimental branches are therefore documented here for package scope and navigation, but should not be read as part of the standard mustpass boundary.

## How the Families Fit Together

The families address different observations made when a device stops behaving normally.

- **Device fault** exercises structured report retrieval. The standard branch checks the KHR-maintained fault-report contract without requiring the experimental fault injector; the experimental branch supplies `real` and `fake` cases for its own implementation path.
- **Shader timeout** creates compute workloads whose iteration count grows as powers of two. It tests the postmortem outcome of a deliberately excessive shader workload rather than the contents of a fault report ([registration](../../modules/vulkan/postmortem/vktPostmortemShaderTimeoutTests.cpp#L240-L251)).
- **Use after free** submits compute work that refers to an allocation after the test releases it. The two registered leaves differ in whether the data starts in a uniform buffer or a storage buffer ([registration](../../modules/vulkan/postmortem/vktPostmortemUseAfterFreeTests.cpp#L349-L362)).
- **Device loss** has one `maintenance5` case. It checks the device-loss behavior exposed through the maintenance5 path, so it complements the fault-report tests without adding another report-shape matrix ([registration](../../modules/vulkan/postmortem/vktPostmortemDeviceLossTests.cpp#L330-L337)).

The shared question is what a CTS implementation can observe and verify once device execution has become unreliable. The families are separate because they vary the source of the event and the observation being checked: report data, workload outcome, released-resource use, or maintenance5 status.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `device_fault.no_fault` and `device_fault.with_fault_*` | [DeviceFault](../testfiles/postmortem/DeviceFault.md) | The standard KHR report queries, report-record sizing, vendor-binary buffers, and the experimental `real`/`fake` factory path. |
| `shader_timeout.compute_*` | [ShaderTimeout](../testfiles/postmortem/ShaderTimeout.md) | The generated compute workload sizes and the result expected after the timeout-oriented workload. |
| `use_after_free.ubo_to_ssbo_single_invocation` | [UseAfterFree](../testfiles/postmortem/UseAfterFree.md) | The uniform-buffer-to-storage-buffer case and what the released allocation means for the submitted work. |
| `use_after_free.ssbo_to_ssbo_single_invocation` | [UseAfterFree](../testfiles/postmortem/UseAfterFree.md) | The storage-buffer copy case and its relationship to the other use-after-free leaf. |
| `device_loss.maintenance5` | [DeviceLoss](../testfiles/postmortem/DeviceLoss.md) | The maintenance5 device-loss case, its support conditions, and its post-loss result check. |

## Category Notes

- The name `postmortem` describes the point at which these tests inspect the device, not a guarantee that every case causes device loss. In particular, the `no_fault` device-fault cases query the report interface without a preceding injected fault.
- Keep standard and experimental results separate when interpreting coverage. The default mustpass file proves coverage for the standard KHR `device_fault` branch only; it does not prove that `shader_timeout`, `use_after_free`, `device_loss`, or the experimental `device_fault` cases run in the standard package.
- The two `device_fault` factories are a registration limitation worth knowing when tracing paths. A family name alone does not identify the implementation; the package surface selects the factory.
