## Overview

**Core question:** Do the four local `info` cases report the selected CTS environment, and do the platform memory limits satisfy the few invariants that this file checks?

- This page covers the four test case leaves implemented in [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L132-L270): `build`, `device`, `platform`, and `memory_limits`.
- All four run on the host. They submit no Vulkan commands and create no shader pipeline.
- `build`, `device`, and `platform` report information to the test log and return a passing `TestStatus` with the message `Not validated`.
- `memory_limits` reports platform data and checks three CTS platform-memory invariants before returning `Pass`.
- [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L260-L270) attaches API feature-information cases implemented in `vktApiFeatureInfo.cpp`. They appear in the hierarchy but are outside this page's behavior analysis.

## Background Knowledge

- **Informational results.** A CTS case can return a passing result after recording diagnostics without asserting that their content meets an expected value. The result description can state that distinction; it is not a separate result code.
- **Physical-device properties.** Vulkan returns general device properties through `VkPhysicalDeviceProperties`. The structure includes `apiVersion`, vendor-defined `driverVersion`, `vendorID`, `deviceID`, and `deviceName` [Vulkan specification](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L60-L123).
- **CTS platform memory limits.** `tcu::PlatformMemoryLimits` is a CTS platform-port contract that gives tests resource budgets and page-table geometry. It is separate from Vulkan's `VkPhysicalDeviceMemoryProperties`, which describes Vulkan memory heaps and types [CTS declaration](../../../../../framework/common/tcuPlatform.hpp#L51-L75), [Vulkan memory properties](../../../../vulkan-docs/src/chapters/memory.adoc#L500-L543).

## Registration Hierarchy

```text
info
├── build
├── device
├── platform
├── memory_limits
├── physical_devices (registration only)
├── physical_device_groups (registration only)
├── instance_layers (registration only)
├── instance_extensions (registration only)
├── instance_extension_dependencies (registration only; Vulkan only)
├── instance_extension_device_functions (registration only)
├── device_features (registration only)
├── device_properties (registration only)
├── device_queue_family_properties (registration only)
├── device_memory_properties (registration only)
├── device_layers (registration only)
├── device_extensions (registration only)
├── device_extension_dependencies (registration only; Vulkan only)
├── device_no_khx_extensions (registration only)
├── device_memory_budget (registration only)
├── device_mandatory_features (registration only)
└── device_group_peer_memory_features (registration only)
```

The Vulkan and Vulkan SC package initializers both attach `info` at the package root [Vulkan registration](../../../modules/vulkan/vktTestPackage.cpp#L1343-L1348), [Vulkan SC registration](../../../modules/vulkan/vktTestPackage.cpp#L1411-L1416). The four local leaves occur in both mustpass lists [Vulkan mustpass](../../../mustpass/main/vk-default/info.txt#L1-L21), [Vulkan SC mustpass](../../../mustpass/main/vksc-default/info.txt#L1-L19). Of the delegated leaves, `instance_extension_dependencies` and `device_extension_dependencies` are omitted from Vulkan SC by compile-time guards [delegated registration](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960).

## Parameter Dimensions and Observed Values

These local cases have no generated matrix or intermediate node below `info`. The direct test case leaf is the only registered dimension that changes behavior.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Local test case leaf | `build`, `device`, `platform`, `memory_limits` | Selects the information source and whether the case only reports it or also checks platform-memory invariants. | [`createInfoTests()`](../../../modules/vulkan/vktInfoTests.cpp#L260-L270) |

The values reported inside a case depend on the CTS build, selected physical device, and platform port. They are observed runtime data, not generated parameter values or separate registered cases.

## Behavior Parameters

The local test case leaf is the primary behavioral axis. Each of its four values selects a different host-side information path.

### `build`: build-environment report

`build` reports compile-time CTS configuration. [`logBuildInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L132-L149) logs the `DE_OS`, `DE_CPU`, `DE_PTR_SIZE`, `DE_ENDIANNESS`, `DE_COMPILER`, and `DE_DEBUG` values. Helper switches convert known OS, CPU, compiler, and endianness constants to their exact symbolic names; unknown values are logged numerically [name conversion helpers](../../../modules/vulkan/vktInfoTests.cpp#L50-L130). The case does not compare any field with an expected value.

### `device`: selected physical-device report

`device` identifies the physical device selected by the CTS context. [`logDeviceInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L151-L167) logs the `--deqp-vk-device-id` selection together with `apiVersion`, `driverVersion`, `deviceName`, `vendorID`, and `deviceID` from the context's `VkPhysicalDeviceProperties`. It formats the API version and prints the driver, vendor, and device identifiers in hexadecimal. It does not validate those values against Vulkan requirements.

### `platform`: platform-description report

`platform` delegates the report content to the active Vulkan platform implementation. [`logPlatformInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L169-L178) calls `describePlatform()` with an output stream and copies the resulting text into the CTS log. The platform port decides which details appear. This case does not parse or validate the description.

### `memory_limits`: CTS platform-memory report and sanity checks

`memory_limits` reads the active platform port's `tcu::PlatformMemoryLimits`. [`logPlatformMemoryLimits()`](../../../modules/vulkan/vktInfoTests.cpp#L236-L258) logs system and device-local budgets, allocation granularity, device page size, page-table entry size, and hierarchy level count. Byte counts use the largest fitting binary unit from `TiB` through `KiB`, or `B` for smaller values [size formatting](../../../modules/vulkan/vktInfoTests.cpp#L180-L234).

This leaf then checks:

- `totalSystemMemory > 0`;
- `deviceMemoryAllocationGranularity > 0`;
- `deIsPowerOfTwo64(devicePageSize)`.

The last predicate accepts zero as well as nonzero powers of two [helper definition](../../../../../framework/delibs/debase/deInt32.h#L226-L233). The case does not validate `totalDeviceLocalMemory`, `devicePageTableEntrySize`, or `devicePageTableHierarchyLevels`.

## Shader Analysis

These cases contain no shader code. Their behavior consists of host-side context, build, and platform reporting, plus the three checks in `memory_limits`.

## Runtime Execution and Result Checking

- The CTS framework invokes one function selected by the test case leaf. The local registrations use the `addFunctionCase` overload without a support callback [local registration](../../../modules/vulkan/vktInfoTests.cpp#L260-L265), [function-case helper](../../../modules/vulkan/vktTestCaseUtil.hpp#L354-L360).
- `build` reads compile-time macros and logs them. `device` reads the selected device properties already held by `Context`. `platform` asks the active Vulkan platform to write its description. None of these three functions performs a comparison; each returns `tcu::TestStatus::pass("Not validated")` after logging [reporting results](../../../modules/vulkan/vktInfoTests.cpp#L132-L178).
- `memory_limits` asks `tcu::Platform::getMemoryLimits()` to populate a host structure, logs all six fields, and evaluates the three `TCU_CHECK` expressions. A false expression throws `tcu::TestError`, so execution does not reach the final passing return [memory checks](../../../modules/vulkan/vktInfoTests.cpp#L236-L258), [`TCU_CHECK`](../../../../../framework/common/tcuDefs.hpp#L208-L217).
- If all three expressions succeed, `memory_limits` returns `tcu::TestStatus::pass("Pass")`. There is no GPU submission, device result buffer, or readback stage.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `build` | Build-information reporting failure. |
| `device` | Selected-device reporting failure. |
| `platform` | Platform-description reporting failure. |
| `memory_limits` | Platform-memory reporting or invariant failure. |

### Cause Analysis

#### Build-information reporting failure

**Possible failure symptoms:** The case does not reach its explicit passing result, or the test log contains an incomplete build report. A wrong but printable macro value does not fail this case because the function performs no content check.

**Possible implementation causes:** [`logBuildInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L132-L149) has no failing return or explicit check. A result other than its explicit pass therefore requires an exception or another interruption in host-side or framework execution. This function does not identify a narrower cause, so the runtime error and stack trace need source-level investigation. The `DE_*` macro values affect the report but do not trigger failure.

#### Selected-device reporting failure

**Possible failure symptoms:** The case does not return `Not validated`, or its log stops before the selected device index and five `VkPhysicalDeviceProperties` fields are written. An unusual property value alone cannot fail this leaf.

**Possible implementation causes:** [`logDeviceInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L151-L167) has no failing return or explicit property check. A failing result therefore requires an interruption while the function accesses the CTS context or writes the log, and the runtime error needs source-level investigation. The Vulkan specification defines the reported fields [physical-device properties](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L74-L123), but an unusual field value alone does not fail this leaf.

#### Platform-description reporting failure

**Possible failure symptoms:** The case does not reach its passing return, or `describePlatform()` produces no complete log message. Incorrect or incomplete description text can still receive a passing result because the case does not inspect it.

**Possible implementation causes:** [`logPlatformInfo()`](../../../modules/vulkan/vktInfoTests.cpp#L169-L178) has no failing return or content check. A failing result requires an interruption in the platform port's `describePlatform()` callback or the output-stream and test-log path. The runtime error needs source-level investigation; no Vulkan property value can directly fail this leaf.

#### Platform-memory reporting or invariant failure

**Possible failure symptoms:** `TCU_CHECK` reports one of these failed expressions: `limits.totalSystemMemory > 0`, `limits.deviceMemoryAllocationGranularity > 0`, or `deIsPowerOfTwo64(limits.devicePageSize)`. The power-of-two expression fails for a nonzero value with more than one bit set; zero passes that predicate. A failure can occur before the checks if the platform callback or logging path does not complete.

**Possible implementation causes:** The CTS platform port supplies these values through `getMemoryLimits()`. A port that leaves the required budget or allocation-granularity field at its zero-initialized value, or reports a non-power-of-two device page size, violates the framework assumptions exercised here [field contract](../../../../../framework/common/tcuPlatform.hpp#L51-L75). The default platform implementation supplies nonzero, power-of-two values and ports may override them [default values](../../../../../framework/common/tcuPlatform.cpp#L57-L66). These are CTS platform configuration values, so the corresponding Vulkan memory heaps or types are not a direct oracle for this failure.

## Case Pruning

### Requirement-based pruning

The four local leaves have no per-case Vulkan version, extension, feature, format, or device-limit support check. They are registered for both Vulkan and Vulkan SC. A failure to initialize the package or selected device can prevent execution, but `vktInfoTests.cpp` does not prune a local leaf on that basis.

### Design-based pruning

- The file registers one fixed case for each of the four reporting behaviors. It does not generate variants for operating systems, compilers, CPUs, devices, or platform ports; those differences appear only in logged runtime values.
- `memory_limits` checks three generic platform assumptions. It reports the remaining fields without turning their possible values into more cases or pass/fail conditions.
- The API enumeration and feature/property validation leaves attached after the local cases are delegated to [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960), so their mechanisms do not expand this page's behavioral axis.

## Key Takeaways

- `build`, `device`, and `platform` are successful when host-side reporting completes. Their `Not validated` message makes clear that the logged content is not a conformance result.
- `memory_limits` is the only local leaf with explicit checks: nonzero system-memory and allocation-granularity values, plus the source helper's power-of-two predicate for device page size.
- `tcu::PlatformMemoryLimits` belongs to the CTS platform layer and should not be read as a second rendering of Vulkan memory heaps and types.
- Both Vulkan and Vulkan SC register all four local leaves. Their `info` hierarchies differ only in two delegated dependency cases.
- See `## Failure Meaning` before assigning a failure to a Vulkan driver. Three leaves do not validate Vulkan behavior, and the fourth checks platform-port data.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Build-name helpers and `logBuildInfo()` | [`vktInfoTests.cpp#L50-L149`](../../../modules/vulkan/vktInfoTests.cpp#L50-L149) | Converts build constants to log text and returns `Not validated`. |
| `logDeviceInfo()` | [`vktInfoTests.cpp#L151-L167`](../../../modules/vulkan/vktInfoTests.cpp#L151-L167) | Reports the selected device index and core physical-device properties. |
| `logPlatformInfo()` | [`vktInfoTests.cpp#L169-L178`](../../../modules/vulkan/vktInfoTests.cpp#L169-L178) | Delegates platform description to the active platform port. |
| Size formatting and `logPlatformMemoryLimits()` | [`vktInfoTests.cpp#L180-L258`](../../../modules/vulkan/vktInfoTests.cpp#L180-L258) | Formats platform budgets and applies the three explicit checks. |
| `createInfoTests()` and `createTests()` | [`vktInfoTests.cpp#L260-L277`](../../../modules/vulkan/vktInfoTests.cpp#L260-L277) | Registers the four local leaves and attaches the delegated API information leaves. |
| Local factory declaration | [`vktInfoTests.hpp#L30-L37`](../../../modules/vulkan/vktInfoTests.hpp#L30-L37) | Declares the `info::createTests()` package entry point. |
| Root package attachment | [`vktTestPackage.cpp#L1343-L1348`](../../../modules/vulkan/vktTestPackage.cpp#L1343-L1348), [`vktTestPackage.cpp#L1411-L1416`](../../../modules/vulkan/vktTestPackage.cpp#L1411-L1416) | Attaches `info` to both Vulkan and Vulkan SC packages. |
| Delegated registration | [`vktApiFeatureInfo.cpp#L8928-L8960`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960) | Registers the nonlocal `info` leaves and shows the two Vulkan SC exclusions. |
| Vulkan mustpass scope | [`vk-default/info.txt#L1-L21`](../../../mustpass/main/vk-default/info.txt#L1-L21) | Confirms all four local `dEQP-VK.info.*` leaves and the delegated Vulkan leaves. |
| Vulkan SC mustpass scope | [`vksc-default/info.txt#L1-L19`](../../../mustpass/main/vksc-default/info.txt#L1-L19) | Confirms all four local `dEQP-VKSC.info.*` leaves and the reduced delegated set. |
| `PlatformMemoryLimits` contract | [`tcuPlatform.hpp#L51-L75`](../../../../../framework/common/tcuPlatform.hpp#L51-L75) | Defines the CTS platform memory-budget and page-geometry fields. |
| Physical-device property semantics | [`devsandqueues.adoc#L60-L123`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L60-L123) | Defines the Vulkan properties reported by `device`. |
| Vulkan memory-property model | [`memory.adoc#L500-L543`](../../../../vulkan-docs/src/chapters/memory.adoc#L500-L543) | Distinguishes Vulkan memory heaps and types from CTS platform limits. |
