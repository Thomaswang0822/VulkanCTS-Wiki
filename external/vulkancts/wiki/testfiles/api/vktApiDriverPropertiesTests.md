# [vktApiDriverPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1)

## Overview

[`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.driver_properties` subtree. The file registers five direct child leaves under that root through [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170), and each leaf queries [`VkPhysicalDeviceDriverProperties`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L126-L130) through [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L125-L136) before validating one specific piece of returned driver metadata.

## Role of File

Implementation-heavy test file for the `api.driver_properties` subgroup. The public entry point is [`createDriverPropertiesTests()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L174-L177).

## Source Code

- Primary source: [vktApiDriverPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1)
- Header: [vktApiDriverPropertiesTests.hpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L142)

## Registration Hierarchy

```text
api.driver_properties
├── driver_id_match
├── name_is_not_empty
├── name_zero_terminated
├── info_zero_terminated
└── conformance_version
```

The confirmed Level-3 root is `api.driver_properties`, created by [`createDriverPropertiesTests()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L174-L177) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L90-L92). The exact direct child names are confirmed from [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170): `driver_id_match`, `name_is_not_empty`, `name_zero_terminated`, `info_zero_terminated`, and `conformance_version`.

## Test Families

### driver_id_match — Driver-ID table membership check

Covers the direct child registered through [`addFunctionCase(group, "driver_id_match", ...)`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L165-L165). The leaf executes [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L120-L161), which dispatches `TEST_TYPE_DRIVER_ID_MATCH` to [`testDriverMatch()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66-L75). That validator iterates over the included `driverIds` table from [`vkKnownDriverIds.inl`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L30-L30) and fails if the reported `driverID` does not match any known entry.

### name_is_not_empty — Non-empty driver-name check

Covers the direct child registered through [`addFunctionCase(group, "name_is_not_empty", ...)`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L166-L166). The leaf uses [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L120-L161) with `TEST_TYPE_NAME_IS_NOT_EMPTY`, which dispatches to [`testNameIsNotEmpty()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77-L81). The validator fails when `driverName[0] == 0`, so the check is specifically for an empty returned driver-name string.

### name_zero_terminated — Driver-name null-termination check

Covers the direct child registered through [`addFunctionCase(group, "name_zero_terminated", ...)`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L167-L167). The leaf dispatches `TEST_TYPE_NAME_ZERO_TERMINATED` from [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L147-L149) to [`testNameZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83-L87), which uses [`isNullTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L50-L53) with `VK_MAX_DRIVER_NAME_SIZE` to verify bounded null termination.

### info_zero_terminated — Driver-info null-termination check

Covers the direct child registered through [`addFunctionCase(group, "info_zero_terminated", ...)`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L168-L168). The leaf dispatches `TEST_TYPE_INFO_ZERO_TERMINATED` from [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L150-L152) to [`testInfoZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89-L93), which uses the same [`isNullTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L50-L53) helper with `VK_MAX_DRIVER_INFO_SIZE`.

### conformance_version — Conformance-version validation

Covers the direct child registered through [`addFunctionCase(group, "conformance_version", ...)`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L169-L169). The leaf dispatches `TEST_TYPE_VERSION` from [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L153-L155) to [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95-L118). That validator first checks that the returned conformance version is not older than the used API major/minor version at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L100-L108), then compares it against the known-version table included from [`vkKnownConformanceVersions.inl`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L98-L98) using the equality operator defined at [`operator==()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L55-L58).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child leaves | `driver_id_match`, `name_is_not_empty`, `name_zero_terminated`, `info_zero_terminated`, `conformance_version` in [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170) |
| Test-type enum | `TEST_TYPE_DRIVER_ID_MATCH`, `TEST_TYPE_NAME_IS_NOT_EMPTY`, `TEST_TYPE_NAME_ZERO_TERMINATED`, `TEST_TYPE_INFO_ZERO_TERMINATED`, `TEST_TYPE_VERSION` in [`enum TestType`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L41-L48) |
| Queried struct chain | [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L125-L136) with [`VkPhysicalDeviceDriverProperties`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L126-L134) attached through `pNext` |
| Sentinel initialization | both queried structs pre-filled with `0xaa` via [`deMemset()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L128-L133) before the query |
| String bound sizes | `VK_MAX_DRIVER_NAME_SIZE` in [`testNameZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83-L87) and `VK_MAX_DRIVER_INFO_SIZE` in [`testInfoZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89-L93) |
| Version comparison inputs | returned `conformanceVersion` against `context.getUsedApiVersion()` in [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95-L118) |

## Support / Feature Requirements

The support gate is explicit and uniform:

- every direct child uses [`checkSupport()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L60-L64), which requires the device functionality `VK_KHR_driver_properties` through [`context.requireDeviceFunctionality("VK_KHR_driver_properties")`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L63-L63)

No other feature-bit, queue-family, or platform-specific support requirement is visible in the file.

## Verification Methods

Observed verification methods are direct property checks on the returned query data:

- **known-ID membership check** through the `driverIds` table in [`testDriverMatch()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66-L75)
- **non-empty string check** on `driverName` in [`testNameIsNotEmpty()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77-L81)
- **bounded null-termination checks** using [`memchr()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L52-L52) inside [`isNullTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L50-L53)
- **version floor check** against the used API major/minor version in [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L100-L108)
- **known-version membership check** against the `knownConformanceVersions` table in [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L110-L117)

All verification flows through [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L120-L161), which performs the property query once and dispatches to the selected validator in its `switch` statement at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L139-L158).

## Test Principles Observed

- Reuse one property-query path and select targeted validators through enum-driven dispatch.
- Isolate metadata sanity checks into individually named direct-child leaves rather than combining many assertions into one case.
- Use curated known-value tables for driver IDs and conformance versions.
- Initialize destination structs with a non-zero pattern before invoking the Vulkan query path.

## Notes / Uncertainties

- This normalization confirms the Level-3 root as `api.driver_properties` and the exact direct child leaves listed in [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170).
- The file pre-fills queried structs with `0xaa` at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L128-L133), but the inspected code does not explicitly verify untouched guard bytes after the query, so no stronger overwrite-detection claim is made.
- The quality or completeness of the external known-ID and known-conformance-version tables is not evaluated here; this page only documents that membership in those tables is required by the visible code.
