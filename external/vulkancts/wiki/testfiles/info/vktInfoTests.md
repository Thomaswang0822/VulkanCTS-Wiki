# vktInfoTests.cpp

## Overview

[`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L1) is the primary registration file for the lightweight Vulkan CTS [`info`](../../categories/info.md) category. It implements four local function-style cases that report build, device, platform, and platform-memory information, then extends the same test group with delegated API feature-info registrations via [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924), [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937), and [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953).

## Role

Registration file with a small amount of direct implementation.

## Source Code

- Primary source: [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L1)
- Declaration: [`vktInfoTests.hpp`](../../../modules/vulkan/vktInfoTests.hpp#L34)
- Related delegated declarations: [`vktApiFeatureInfo.hpp`](../../../modules/vulkan/api/vktApiFeatureInfo.hpp#L34)
- Root-category attachment: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1348)

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
- root attachment in [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1348) and [`TestPackageSC::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1416)
- local cases registered in [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L260-L265)
- delegated instance cases from [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924-L8935)
- delegated device cases from [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937-L8951)
- delegated device-group case from [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953-L8957)

## Test Families

### build — Build-environment reporting

[`build`](../../../modules/vulkan/vktInfoTests.cpp#L262) is implemented by [`logBuildInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L132).

Observed behavior:
- derives debug/non-debug state from the [`DE_DEBUG`](../../../modules/vulkan/vktInfoTests.cpp#L134) macro
- logs OS name via [`getOsName()`](../../../modules/vulkan/vktInfoTests.cpp#L50)
- logs CPU name via [`getCpuName()`](../../../modules/vulkan/vktInfoTests.cpp#L92)
- logs endianness via [`getEndiannessName()`](../../../modules/vulkan/vktInfoTests.cpp#L119)
- logs compiler name via [`getCompilerName()`](../../../modules/vulkan/vktInfoTests.cpp#L75)
- includes pointer size and debug flag in the emitted log message at [`logBuildInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L140)

This case returns pass status with the message `Not validated` in [`logBuildInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L148).

### device — Device-property reporting

[`device`](../../../modules/vulkan/vktInfoTests.cpp#L263) is implemented by [`logDeviceInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L151).

Observed behavior:
- fetches [`VkPhysicalDeviceProperties`](../../../modules/vulkan/vktInfoTests.cpp#L154) from the framework context
- logs the selected `--deqp-vk-device-id` value at [`logDeviceInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L156)
- logs `apiVersion`, `driverVersion`, `deviceName`, `vendorID`, and `deviceID` at [`logDeviceInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L159)

This case also returns `Not validated` in [`logDeviceInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L166).

### platform — Platform-description reporting

[`platform`](../../../modules/vulkan/vktInfoTests.cpp#L264) is implemented by [`logPlatformInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L169).

Observed behavior:
- creates an [`std::ostringstream`](../../../modules/vulkan/vktInfoTests.cpp#L171)
- asks the Vulkan platform object to describe itself via [`describePlatform()`](../../../modules/vulkan/vktInfoTests.cpp#L173)
- writes the produced text to the test log in [`logPlatformInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L175)

This case returns `Not validated` in [`logPlatformInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L177).

### memory_limits — Platform-memory-limit reporting with simple invariant checks

[`memory_limits`](../../../modules/vulkan/vktInfoTests.cpp#L265) is implemented by [`logPlatformMemoryLimits()`](../../../modules/vulkan/vktInfoTests.cpp#L236).

Observed behavior:
- reads [`tcu::PlatformMemoryLimits`](../../../modules/vulkan/vktInfoTests.cpp#L239) from the platform through [`getMemoryLimits()`](../../../modules/vulkan/vktInfoTests.cpp#L241)
- formats sizes through [`prettySize()`](../../../modules/vulkan/vktInfoTests.cpp#L231), which uses [`getBestSizeUnit()`](../../../modules/vulkan/vktInfoTests.cpp#L197) and [`operator<<`](../../../modules/vulkan/vktInfoTests.cpp#L218)
- logs total system memory, total device-local memory, allocation granularity, device page size, page-table entry size, and page-table hierarchy levels at [`logPlatformMemoryLimits()`](../../../modules/vulkan/vktInfoTests.cpp#L243)
- performs three runtime checks:
  - [`limits.totalSystemMemory > 0`](../../../modules/vulkan/vktInfoTests.cpp#L253)
  - [`limits.deviceMemoryAllocationGranularity > 0`](../../../modules/vulkan/vktInfoTests.cpp#L254)
  - [`deIsPowerOfTwo64(limits.devicePageSize)`](../../../modules/vulkan/vktInfoTests.cpp#L255)

Unlike the three purely informational cases, this one returns `Pass` in [`logPlatformMemoryLimits()`](../../../modules/vulkan/vktInfoTests.cpp#L257).

### Delegated API feature-info cases

The remaining direct children under `info` are implemented in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) and documented in [`vktApiFeatureInfo.md`](vktApiFeatureInfo.md):

- `physical_devices`, `physical_device_groups`, `instance_layers`, `instance_extensions`, `instance_extension_dependencies`, `instance_extension_device_functions` (instance-scope cases)
- `device_features`, `device_properties`, `device_queue_family_properties`, `device_memory_properties`, `device_layers`, `device_extensions`, `device_extension_dependencies`, `device_no_khx_extensions`, `device_memory_budget`, `device_mandatory_features` (device-scope cases)
- `device_group_peer_memory_features` (device-group case)

After its own local cases, [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L267) appends three delegated groups of registrations:

- [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924)
- [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8937)
- [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8953)

This means [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L1) is both a direct implementation file and the top-level dispatcher for most of the `info` category surface.

## Parameter Dimensions

| Parameter / dimension | Observed values / source |
|---|---|
| Local case kind | [`build`](../../../modules/vulkan/vktInfoTests.cpp#L262), [`device`](../../../modules/vulkan/vktInfoTests.cpp#L263), [`platform`](../../../modules/vulkan/vktInfoTests.cpp#L264), [`memory_limits`](../../../modules/vulkan/vktInfoTests.cpp#L265) |
| OS naming table | [`DE_OS_VANILLA`](../../../modules/vulkan/vktInfoTests.cpp#L54), [`DE_OS_WIN32`](../../../modules/vulkan/vktInfoTests.cpp#L56), [`DE_OS_UNIX`](../../../modules/vulkan/vktInfoTests.cpp#L58), [`DE_OS_WINCE`](../../../modules/vulkan/vktInfoTests.cpp#L60), [`DE_OS_OSX`](../../../modules/vulkan/vktInfoTests.cpp#L62), [`DE_OS_ANDROID`](../../../modules/vulkan/vktInfoTests.cpp#L64), [`DE_OS_SYMBIAN`](../../../modules/vulkan/vktInfoTests.cpp#L66), [`DE_OS_IOS`](../../../modules/vulkan/vktInfoTests.cpp#L68) |
| Compiler naming table | [`DE_COMPILER_VANILLA`](../../../modules/vulkan/vktInfoTests.cpp#L79), [`DE_COMPILER_MSC`](../../../modules/vulkan/vktInfoTests.cpp#L81), [`DE_COMPILER_GCC`](../../../modules/vulkan/vktInfoTests.cpp#L83), [`DE_COMPILER_CLANG`](../../../modules/vulkan/vktInfoTests.cpp#L85) |
| CPU naming table | [`DE_CPU_VANILLA`](../../../modules/vulkan/vktInfoTests.cpp#L96), [`DE_CPU_ARM`](../../../modules/vulkan/vktInfoTests.cpp#L98), [`DE_CPU_X86`](../../../modules/vulkan/vktInfoTests.cpp#L100), [`DE_CPU_X86_64`](../../../modules/vulkan/vktInfoTests.cpp#L102), [`DE_CPU_ARM_64`](../../../modules/vulkan/vktInfoTests.cpp#L104), [`DE_CPU_MIPS`](../../../modules/vulkan/vktInfoTests.cpp#L106), [`DE_CPU_MIPS_64`](../../../modules/vulkan/vktInfoTests.cpp#L108), [`DE_CPU_RISCV_32`](../../../modules/vulkan/vktInfoTests.cpp#L110), [`DE_CPU_RISCV_64`](../../../modules/vulkan/vktInfoTests.cpp#L112) |
| Endianness naming table | [`DE_BIG_ENDIAN`](../../../modules/vulkan/vktInfoTests.cpp#L123), [`DE_LITTLE_ENDIAN`](../../../modules/vulkan/vktInfoTests.cpp#L125) |
| Memory-size units | [`TiB`](../../../modules/vulkan/vktInfoTests.cpp#L201), [`GiB`](../../../modules/vulkan/vktInfoTests.cpp#L202), [`MiB`](../../../modules/vulkan/vktInfoTests.cpp#L203), [`KiB`](../../../modules/vulkan/vktInfoTests.cpp#L204), [`B`](../../../modules/vulkan/vktInfoTests.cpp#L206) |

## Support / Feature Requirements

This file does not expose explicit Vulkan feature-enable checks for its local cases.

Observed structural conditions instead are:
- category creation is available in both Vulkan and Vulkan SC package init paths through [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1348) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1416)
- some delegated feature-info cases are conditionally removed for Vulkan SC in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8930) and [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8945)

## Verification Methods

Observed result styles in this file are:

- **informational logging only** for [`build`](../../../modules/vulkan/vktInfoTests.cpp#L262), [`device`](../../../modules/vulkan/vktInfoTests.cpp#L263), and [`platform`](../../../modules/vulkan/vktInfoTests.cpp#L264), each returning `Not validated`
- **logging plus invariant checks** for [`memory_limits`](../../../modules/vulkan/vktInfoTests.cpp#L265), which validates non-zero memory/allocation values and a power-of-two page size before returning `Pass`
- **delegated validation/reporting** for the remainder of the category via the API feature-info builders appended in [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L267)

## Test Principles Observed

- **Keep the top-level category lightweight**: the file uses direct function cases rather than elaborate test classes for its own local checks
- **Prefer environment introspection and reporting**: most local cases log framework or platform state instead of driving complex GPU workloads
- **Centralize shared capability queries elsewhere**: richer instance/device/device-group coverage is delegated to [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8924) rather than duplicated here
- **Validate only where generic invariants are obvious**: [`memory_limits`](../../../modules/vulkan/vktInfoTests.cpp#L265) performs simple sanity checks, whereas the other local cases explicitly avoid stronger validation claims

## Notes / Uncertainties

- The file comment labels this as `Build and Device Tests` in [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L21), but the actual registered scope in inspected code is slightly broader because it also includes platform and memory-limit reporting plus delegated API feature-info coverage.
- The exact line-level internals of delegated API feature-info cases are intentionally not repeated here beyond registration structure; those details are covered separately in [`vktApiFeatureInfo.md`](vktApiFeatureInfo.md).
