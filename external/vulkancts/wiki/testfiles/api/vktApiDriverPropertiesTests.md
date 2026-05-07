# [vktApiDriverPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1)

## Overview

[`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1) implements the `api/driver_properties` subgroup registered by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L92). The file is compact and narrowly scoped: every case queries [`VkPhysicalDeviceDriverProperties`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L126) through [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L125) and then validates one aspect of the returned metadata.

## Role of File

Implementation-heavy test file for the `api/driver_properties` subgroup.

## Source Code

- Primary source: [vktApiDriverPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L1)
- Header: [vktApiDriverPropertiesTests.hpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L92)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createDriverPropertiesTests(testCtx)
          +-- driver_properties
              +-- driver_id_match
              +-- name_is_not_empty
              +-- name_zero_terminated
              +-- info_zero_terminated
              +-- conformance_version
```

Evidence:
- `driver_properties` group created at [`createDriverPropertiesTests()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L174)
- individual cases registered in [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163)

## Test Hierarchy

```text
api
+-- driver_properties
    +-- driver_id_match
    +-- name_is_not_empty
    +-- name_zero_terminated
    +-- info_zero_terminated
    +-- conformance_version
```

Source: [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163).

## Test Families

### 1. Driver identity and string-sanity checks

Four of the five registered cases validate basic identity/string properties of [`VkPhysicalDeviceDriverProperties`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L126):

- [`driver_id_match`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L165) calls [`testDriverMatch()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66), which checks whether `driverID` matches one of the entries included from [`vkKnownDriverIds.inl`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L30)
- [`name_is_not_empty`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L166) calls [`testNameIsNotEmpty()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77), which fails if `driverName[0] == 0`
- [`name_zero_terminated`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L167) calls [`testNameZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83), which uses [`isNullTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L50) with `VK_MAX_DRIVER_NAME_SIZE`
- [`info_zero_terminated`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L168) calls [`testInfoZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89), which uses the same helper with `VK_MAX_DRIVER_INFO_SIZE`

### 2. Conformance version validation

[`conformance_version`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L169) calls [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95). That function first checks that the returned conformance version is not older than the used API major/minor version at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L103), then checks exact membership in the table included from [`vkKnownConformanceVersions.inl`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L98) by comparing against known versions at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L110).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Test-type enum | `TEST_TYPE_DRIVER_ID_MATCH`, `TEST_TYPE_NAME_IS_NOT_EMPTY`, `TEST_TYPE_NAME_ZERO_TERMINATED`, `TEST_TYPE_INFO_ZERO_TERMINATED`, `TEST_TYPE_VERSION` in [`TestType`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L41) |
| Registered case names | `driver_id_match`, `name_is_not_empty`, `name_zero_terminated`, `info_zero_terminated`, `conformance_version` in [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L165) |
| Queried struct chain | [`VkPhysicalDeviceProperties2`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L125) with [`VkPhysicalDeviceDriverProperties`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L126) on `pNext` at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L134) |
| Sentinel initialization | both queried structs pre-filled with `0xaa` via [`deMemset()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L128) before the query |
| String bound sizes | `VK_MAX_DRIVER_NAME_SIZE` in [`testNameZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L85) and `VK_MAX_DRIVER_INFO_SIZE` in [`testInfoZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L91) |
| Version comparison inputs | returned `conformanceVersion` against `context.getUsedApiVersion()` in [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95) |

## Support / Feature Requirements

The support gate is explicit and uniform:

- every case calls [`checkSupport()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L60), which requires the device functionality `VK_KHR_driver_properties` via [`context.requireDeviceFunctionality("VK_KHR_driver_properties")`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L63)

No other feature-bit or queue-family requirement is visible in the file.

## Verification Methods

Observed verification methods are direct property checks on returned query data:

- **known-ID membership check** through the `driverIds` table in [`testDriverMatch()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66)
- **non-empty string check** on `driverName` in [`testNameIsNotEmpty()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77)
- **bounded null-termination checks** using [`memchr()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L52) inside [`isNullTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L50)
- **version floor check** against the used API major/minor version in [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L103)
- **known-version membership check** against the table from [`vkKnownConformanceVersions.inl`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L98)

All verification flows through [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L120), which performs the query once and dispatches to the selected validator in its `switch` statement at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L139).

## Test Principles Observed

- One query, multiple targeted validators: the file reuses a single property query path and selects one validator by enum-driven dispatch
- Prefer precise metadata sanity checks: each case isolates a small, auditable property rather than mixing many assertions
- Use known tables for authoritative membership: driver IDs and conformance versions are checked against curated included lists
- Defensive query setup: the destination structs are initialized with a non-zero pattern before querying

## Notes / Uncertainties

- The file pre-fills structs with `0xaa` at [`vktApiDriverPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L128), but the inspected code does not explicitly verify untouched guard bytes after the query, so no stronger claim about overwrite-detection is made here.
- The quality or completeness of the external known-ID and known-conformance-version tables is not evaluated here; this document only states that membership in those tables is required by the visible code.
