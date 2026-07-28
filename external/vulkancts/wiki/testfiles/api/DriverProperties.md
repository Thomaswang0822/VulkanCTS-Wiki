## Overview

**Core question:** does the implementation's reported `VkPhysicalDeviceDriverProperties` contain sane, spec-shaped driver metadata?

- This page covers the `api.driver_properties` test family implemented in [vktApiDriverPropertiesTests.cpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp) and attached to the `api` test category by [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L91-L91).
- The family registers exactly five test case leaves, one per field of `VkPhysicalDeviceDriverProperties` that CTS validates: `driver_id_match`, `name_is_not_empty`, `name_zero_terminated`, `info_zero_terminated`, and `conformance_version` [createTestCases()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170), [api.txt](../../../mustpass/main/vk-default/api.txt#L269464-L269468).
- Each leaf runs the same host-side query through `vkGetPhysicalDeviceProperties2` and dispatches to one targeted validator selected by an enum.
- The family is property-validation only: it queries driver metadata on the host and checks the returned fields, with no shaders or device-side resources involved.
- Passing means the queried driver metadata satisfies the leaf-specific sanity rule. Each leaf produces its own pass/fail result.

## Background Knowledge

- `VK_KHR_driver_properties` lets applications query driver metadata by chaining a `VkPhysicalDeviceDriverProperties` struct into `VkPhysicalDeviceProperties2.pNext` and calling `vkGetPhysicalDeviceProperties2`. The struct exposes `driverID`, `driverName`, `driverInfo`, and `conformanceVersion`. The CTS support gate refers to the extension by name even when the implementation exposes it through Vulkan 1.2+ core promotion.
- `conformanceVersion` is a `VkConformanceVersion` value (major, minor, subminor, patch) identifying the Vulkan CTS revision the driver claims to conform to. CTS treats it as a sanity-checkable identifier rather than a runtime feature gate.

## Registration Hierarchy

The test family is created as a single child of the `api` test category by [`createDriverPropertiesTests()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L174-L177) and attached in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L91-L91). It has five direct test case leaves, registered in source order by [`createTestCases()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170).

```text
api.driver_properties
├── driver_id_match
├── name_is_not_empty
├── name_zero_terminated
├── info_zero_terminated
└── conformance_version
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `driver_id_match`, `name_is_not_empty`, `name_zero_terminated`, `info_zero_terminated`, `conformance_version` | Selects which field of `VkPhysicalDeviceDriverProperties` is validated after the shared query. | [createTestCases()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170), [api.txt](../../../mustpass/main/vk-default/api.txt#L269464-L269468) |
| Test-type enum | `TEST_TYPE_DRIVER_ID_MATCH`, `TEST_TYPE_NAME_IS_NOT_EMPTY`, `TEST_TYPE_NAME_ZERO_TERMINATED`, `TEST_TYPE_INFO_ZERO_TERMINATED`, `TEST_TYPE_VERSION` | Carries the leaf selection into the shared validator's `switch` dispatch. | [enum TestType](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L41-L48) |
| Struct chain | `VkPhysicalDeviceProperties2` → `VkPhysicalDeviceDriverProperties` | Single query path used by every leaf; the driver-properties struct is attached through `pNext`. | [testQueryProperties() struct setup](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L125-L136) |
| Sentinel fill | `0xaa` byte pattern | Pre-fills both structs before the query. The inspected code does not re-check sentinel bytes after the query, so this is a defense-in-depth pattern, not a verified overwrite detector. | [deMemset() calls](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L128-L133) |
| String bound sizes | `VK_MAX_DRIVER_NAME_SIZE`, `VK_MAX_DRIVER_INFO_SIZE` | Bounds passed to `isNullTerminated()` when scanning for a `'\0'` byte. | [testNameZeroTerminated()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83-L87), [testInfoZeroTerminated()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89-L93) |
| Version comparison inputs | returned `conformanceVersion` and `context.getUsedApiVersion()` | Used by the conformance-version leaf for both the floor check and the known-version table lookup. | [testVersion()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95-L118) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf runs the same property query and dispatches to a different validator. The leaves are independent: any one can fail without implying anything about the others.

### `driver_id_match`: known-driver-ID membership

The leaf queries the driver-properties struct and verifies that the returned `driverID` matches one of the entries in the CTS-maintained `driverIds` table included from `vkKnownDriverIds.inl`. Membership means the implementation reports a `VkDriverId` value CTS recognizes [testDriverMatch()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66-L75).

### `name_is_not_empty`: driver-name non-empty

The leaf fails when `driverName[0] == 0`, i.e. the first byte of the driver-name buffer is the null terminator. This is a minimum sanity check; it does not validate the rest of the string [testNameIsNotEmpty()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77-L81).

### `name_zero_terminated`: driver-name null-termination

The leaf uses `isNullTerminated()` with `VK_MAX_DRIVER_NAME_SIZE` to scan the driver-name buffer for a `'\0'` byte. The check fails only if no null terminator appears anywhere within the bounded buffer [testNameZeroTerminated()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83-L87).

### `info_zero_terminated`: driver-info null-termination

Same mechanism as the driver-name leaf, but applied to `driverInfo` with `VK_MAX_DRIVER_INFO_SIZE` [testInfoZeroTerminated()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89-L93).

### `conformance_version`: version floor and known-version membership

The leaf first checks that the returned `conformanceVersion` is not older than the used API major/minor version, then scans the `knownConformanceVersions` table (included from `vkKnownConformanceVersions.inl`) for an exact match. The leaf fails if either check fails [testVersion()](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95-L118).

## Shader Analysis

No shader is involved in this test family. The leaves only query driver-properties metadata and validate it on the host.

## Runtime Execution and Result Checking

Each leaf runs the same host-side sequence inside [`testQueryProperties()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L120-L161):

1. Acquire the physical device handle from the test context.
2. Pre-fill both `VkPhysicalDeviceDriverProperties` and `VkPhysicalDeviceProperties2` with the `0xaa` byte pattern, then set their `sType` fields and chain the driver-properties struct through `pNext` [struct setup](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L125-L136).
3. Call `vkGetPhysicalDeviceProperties2` through the instance interface to populate the chained structs [query call](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L136-L136).
4. Dispatch to one of `testDriverMatch()`, `testNameIsNotEmpty()`, `testNameZeroTerminated()`, `testInfoZeroTerminated()`, or `testVersion()` based on the leaf's `TestType` value [switch dispatch](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L139-L158).
5. Each validator either returns normally on success or calls `TCU_FAIL(...)` to mark the case as failed.
6. The leaf returns `tcu::TestStatus::pass("Pass")` when the dispatched validator returns without raising [pass return](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L160-L160).

There is no device-side work beyond the property query itself.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `driver_id_match` | Reported `driverID` is not in the CTS known-driver-ID table. |
| `name_is_not_empty` | Reported `driverName` is the empty string. |
| `name_zero_terminated` | Reported `driverName` has no null terminator within `VK_MAX_DRIVER_NAME_SIZE`. |
| `info_zero_terminated` | Reported `driverInfo` has no null terminator within `VK_MAX_DRIVER_INFO_SIZE`. |
| `conformance_version` | Reported `conformanceVersion` is older than the used API version, or is not in the CTS known-conformance-version table. |

All leaves also share a common infrastructure cause: the implementation advertises `VK_KHR_driver_properties` but does not populate the chained struct as expected. The shared support gate in [`checkSupport()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L60-L64) filters out devices that do not advertise the extension, but a driver that advertises the extension yet leaves the struct unpopulated would surface as a failure in whichever leaf runs first.

### Cause Analysis

#### Reported `driverID` is not a known `VkDriverId`

**Possible failure symptoms:** [`testDriverMatch()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66-L75) reaches the end of the `driverIds` table without finding a match and calls `TCU_FAIL("Driver ID did not match any known driver")`. The case terminates with a failed status and that message.

**Possible implementation causes:** the implementation reports a `driverID` value that is not a registered `VkDriverId` from the `VK_KHR_driver_properties` enumeration, or the CTS copy of `vkKnownDriverIds.inl` is out of date relative to the Vulkan headers the driver was built against. Source-level investigation is needed to confirm which side is stale before treating this as a driver defect.

#### Reported `driverName` is empty

**Possible failure symptoms:** [`testNameIsNotEmpty()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77-L81) sees `driverName[0] == 0` and calls `TCU_FAIL("Driver name is empty")`.

**Possible implementation causes:** the implementation wrote an empty string to `driverName`, or zero-initialized the struct during its own setup but failed to populate `driverName` with an actual driver-name string. The Vulkan spec for `VK_KHR_driver_properties` requires `driverName` to contain a UTF-8 string, so an empty value is non-conformant. Note that the `0xaa` sentinel pre-fill alone would not trigger this leaf, because `0xaa` is not `'\0'`; an unpopulated field would surface in `name_zero_terminated` instead.

#### Reported `driverName` is not null-terminated

**Possible failure symptoms:** [`testNameZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83-L87) calls `isNullTerminated(driverName, VK_MAX_DRIVER_NAME_SIZE)`, which uses `memchr` to scan for `'\0'`; if no null byte is found within the bound, the leaf calls `TCU_FAIL("Driver name is not a null-terminated string")`.

**Possible implementation causes:** the implementation wrote a string longer than `VK_MAX_DRIVER_NAME_SIZE` without truncation, or did not write a null terminator at all. The Vulkan spec requires `driverName` to be null-terminated within the declared bound; a non-terminated buffer is non-conformant.

#### Reported `driverInfo` is not null-terminated

**Possible failure symptoms:** [`testInfoZeroTerminated()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89-L93) calls `isNullTerminated(driverInfo, VK_MAX_DRIVER_INFO_SIZE)`; if no null byte is found within the bound, the leaf calls `TCU_FAIL("Driver info is not a null-terminated string")`.

**Possible implementation causes:** the implementation wrote a driver-info string longer than `VK_MAX_DRIVER_INFO_SIZE` without truncation, or did not write a null terminator. The Vulkan spec requires `driverInfo` to be null-terminated within the declared bound; a non-terminated buffer is non-conformant.

#### Reported `conformanceVersion` fails the floor or known-version check

**Possible failure symptoms:** [`testVersion()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95-L118) either calls `TCU_FAIL("Wrong driver conformance version (older than used API version)")` when the returned `conformanceVersion.major` or `minor` is below the used API version [floor check](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L100-L108), or calls `TCU_FAIL("Wrong driver conformance version (not known)")` when the version is not present in the `knownConformanceVersions` table [table lookup](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L110-L117).

**Possible implementation causes:** the implementation reports a conformance version older than the API version the test ran against, or reports a version that is not in the CTS-maintained `knownConformanceVersions` table. The first case is a clear driver-side defect. The second case may also indicate that the CTS copy of `vkKnownConformanceVersions.inl` is out of date relative to the driver's claimed conformance version; source-level investigation is needed to distinguish a stale CTS table from a driver reporting an unrecognized version.

#### Shared infrastructure failure: extension advertised but struct not populated

**Possible failure symptoms:** the queried `VkPhysicalDeviceDriverProperties` retains the `0xaa` sentinel pattern in its fields, so `driverID` matches no known entry, `driverName[0]` is `0xaa` rather than `'\0'`, and `isNullTerminated()` finds no null byte. Any of the leaves can fail with the corresponding message above.

**Possible implementation causes:** the implementation advertises `VK_KHR_driver_properties` (or Vulkan 1.2+) but does not populate the chained `VkPhysicalDeviceDriverProperties` struct on `vkGetPhysicalDeviceProperties2`. This is a clear driver-side defect. The inspected code does not explicitly re-check the sentinel pattern after the query, so this cause would surface as one of the leaf-specific failures rather than as a dedicated sentinel check.

## Case Pruning

### Requirement-based pruning

All five leaves share the same support gate in [`checkSupport()`](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L60-L64): the device must support `VK_KHR_driver_properties`. A device that does not expose the extension will not run any leaf in this family. No other feature, queue-family, or platform requirement is checked.

### Design-based pruning

The test design splits driver-metadata validation into five independent leaves rather than collapsing them into a single multi-assertion case. This makes the failure message identify which property is non-conformant. The family generates no combinations; the matrix is exactly the five leaves.

## Key Takeaways

- The `api.driver_properties` family is a host-side property-validation family; it does not execute any device-side work.
- All five leaves share a single query path through `VkPhysicalDeviceProperties2` and differ only in which field of `VkPhysicalDeviceDriverProperties` they validate.
- The `conformance_version` leaf combines a floor check (not older than the used API version) with a known-version table lookup; either failure produces a distinct message.
- `driver_id_match` and `conformance_version` both depend on CTS-maintained tables (`vkKnownDriverIds.inl`, `vkKnownConformanceVersions.inl`). A failure in either leaf can indicate a stale CTS table as well as a driver defect; see `## Failure Meaning` for the case-by-case analysis.
- The `0xaa` sentinel pre-fill is a defense-in-depth pattern; the inspected code does not re-check sentinel bytes after the query, so a missing overwrite would surface as one of the leaf-specific failures rather than as a dedicated check.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDriverPropertiesTests()` | [vktApiDriverPropertiesTests.cpp#L174-L177](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L174-L177) | Public entry point that creates the `driver_properties` test group. |
| `createTestCases()` | [vktApiDriverPropertiesTests.cpp#L163-L170](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L163-L170) | Registers the five test case leaves and their `TestType` values. |
| `testQueryProperties()` | [vktApiDriverPropertiesTests.cpp#L120-L161](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L120-L161) | Shared host-side query and validator dispatch. |
| `testDriverMatch()` | [vktApiDriverPropertiesTests.cpp#L66-L75](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L66-L75) | `driver_id_match` validator. |
| `testNameIsNotEmpty()` | [vktApiDriverPropertiesTests.cpp#L77-L81](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L77-L81) | `name_is_not_empty` validator. |
| `testNameZeroTerminated()` | [vktApiDriverPropertiesTests.cpp#L83-L87](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L83-L87) | `name_zero_terminated` validator. |
| `testInfoZeroTerminated()` | [vktApiDriverPropertiesTests.cpp#L89-L93](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L89-L93) | `info_zero_terminated` validator. |
| `testVersion()` | [vktApiDriverPropertiesTests.cpp#L95-L118](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L95-L118) | `conformance_version` validator. |
| `checkSupport()` | [vktApiDriverPropertiesTests.cpp#L60-L64](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L60-L64) | Shared support gate requiring `VK_KHR_driver_properties`. |
| `isNullTerminated()` | [vktApiDriverPropertiesTests.cpp#L50-L53](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L50-L53) | Bounded null-termination helper used by the two `*_zero_terminated` leaves. |
| `enum TestType` | [vktApiDriverPropertiesTests.cpp#L41-L48](../../../modules/vulkan/api/vktApiDriverPropertiesTests.cpp#L41-L48) | Leaf-to-validator dispatch enum. |
| Parent registration | [vktApiTests.cpp#L91-L91](../../../modules/vulkan/api/vktApiTests.cpp#L91-L91) | Where the `driver_properties` group is attached to the `api` test category. |
| Header | [vktApiDriverPropertiesTests.hpp](../../../modules/vulkan/api/vktApiDriverPropertiesTests.hpp) | Public declaration of `createDriverPropertiesTests()`. |
| Mustpass entries | [api.txt#L269464-L269468](../../../mustpass/main/vk-default/api.txt#L269464-L269468) | The five `dEQP-VK.api.driver_properties.*` leaves in the canonical mustpass. |
