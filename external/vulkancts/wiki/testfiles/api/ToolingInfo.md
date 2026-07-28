## Overview

**Core question:** does the implementation correctly enumerate active Vulkan tools through `vkGetPhysicalDeviceToolPropertiesEXT` from `VK_EXT_tooling_info`, both for the getter protocol and for the contents of each returned `VkPhysicalDeviceToolPropertiesEXT` structure?

- Source file: [`vktApiToolingInfoTests.cpp`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L1) in the `api` source directory.
- Test category `api`, test family `tooling_info`, registered under `dEQP-VK.api.tooling_info`.
- Two test case leaves, `validate_getter` and `validate_tools_properties`, exercise the two distinct properties: the array-size behavior of the enumeration call, and the field-level validity of every returned structure.
- The test family is registered only for non-VulkanSC builds; the parent dispatcher guards it with `#ifndef CTS_USES_VULKANSC`.
- The page covers a host-only property-query test with no shader or GPU work, focused on enumeration protocol edge cases and struct field validation against spec-defined limits.

## Background Knowledge

- `VK_EXT_tooling_info` exposes `vkGetPhysicalDeviceToolPropertiesEXT`, a host-side query that enumerates tools active on a physical device (validation layers, profiling tools, tracing tools, and similar). Each tool is reported through a `VkPhysicalDeviceToolPropertiesEXT` structure.
- Vulkan enumeration idiom: a count query with a `NULL` array pointer returns `VK_SUCCESS` and writes the count; a follow-up call with a non-`NULL` array of that size returns `VK_SUCCESS` and fills the array; a call with an array smaller than the count returns `VK_INCOMPLETE` and writes only the number of entries that fit. An oversized array still returns `VK_SUCCESS` and reports the actual count.
- `VkPhysicalDeviceToolPropertiesEXT` carries an `sType` that must be `VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TOOL_PROPERTIES_EXT`, a `purposes` bitmask drawn from the `VkToolPurposeFlagBitsEXT` set, and four string fields (`name`, `version`, `description`, `layer`) bounded by `VK_MAX_EXTENSION_NAME_SIZE` and `VK_MAX_DESCRIPTION_SIZE`. The `layer` field may be empty when the tool is not associated with a layer.

## Registration Hierarchy

```text
api.tooling_info
├── validate_getter
└── validate_tools_properties
```

The test family has no intermediate nodes; [`createTestCases()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L250-L254) registers both test case leaves directly under `tooling_info`. The parent dispatcher attaches `tooling_info` to the `api` test category only inside `#ifndef CTS_USES_VULKANSC` ([vktApiTests.cpp#L123-L126](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `validate_getter`, `validate_tools_properties` | Each leaf tests a distinct property of the extension: the getter protocol across array sizes, or the field-level validity of returned structures. | [`createTestCases()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L250-L254) |

The test family has no parameter matrix beyond this leaf axis. Both leaves require `VK_EXT_tooling_info` ([`checkSupport()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L56-L59)) and share no generated artifacts.

## Behavior Parameters

The primary behavioral axis is the test case leaf: each leaf selects a different property being tested.

### `validate_getter`: array-size behavior of the enumeration call

Exercises the count-then-retrieve protocol with several array sizes against a single call site, [`validateGetter()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L61-L179). The leaf verifies that the implementation returns the correct `VkResult` and consistent counts for: a `NULL` array pointer (count query), an exact-size array, an oversized array, a zero-size array, and (when more than one tool is present) a half-size array. The oversized, zero-size, and half-size cases are the meaningful edge cases; the exact-size case establishes the baseline count used for comparison.

### `validate_tools_properties`: field-level validity of returned structures

Exercises the contents of each `VkPhysicalDeviceToolPropertiesEXT` returned by the implementation, via [`validateToolsProperties()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L181-L248). For each reported tool the leaf checks `sType`, the `purposes` bitmask against the valid `VkToolPurposeFlagBitsEXT` set, and the length bounds of `name`, `version`, `description`, and `layer`. `layer` is the only field that may be empty.

## Shader Analysis

No shader is involved in this test family. The tested behavior is a host-side physical-device property query, and there is no pipeline, dispatch, or GPU work. No representative shader walkthrough is needed.

## Runtime Execution and Result Checking

All execution is host-side, performed through `context.getInstanceInterface().getPhysicalDeviceToolProperties()`, which dispatches to `vkGetPhysicalDeviceToolPropertiesEXT`.

`validate_getter`:

- Count query: call with `&toolCount` and `nullptr`; require `VK_SUCCESS` and any non-negative count ([L68-L76](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L68-L76)).
- If `toolCount > 0`, allocate an exact-size array, set `sType` on every element, and call again with the same count; require `VK_SUCCESS` and the same count returned ([L78-L104](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L78-L104)).
- Increment the count by one and resize the array; call again; require `VK_SUCCESS` and the original count ([L106-L129](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L106-L129)).
- Reset the count to zero; call again with the oversized backing array; require `VK_INCOMPLETE` and a written count of zero ([L131-L147](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L131-L147)).
- If `toolCount > 1`, allocate a half-size array, set `sType` on every element, and call again; require `VK_INCOMPLETE` and a written count equal to `toolCount / 2` ([L150-L176](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L150-L176)).

`validate_tools_properties`:

- Count query with `nullptr`; require `VK_SUCCESS` via `VK_CHECK` ([L188-L189](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L188-L189)).
- If `toolCount > 0`, allocate an exact-size array, set `sType` on every element, and call again; require `VK_SUCCESS` via `VK_CHECK` ([L191-L201](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L191-L201)).
- For each tool, compute `strnlen` of `name`, `version`, `description`, and `layer` against `VK_MAX_EXTENSION_NAME_SIZE` and `VK_MAX_DESCRIPTION_SIZE`, validate `sType`, and validate `purposes` through [`validateToolPurposeFlagBits()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L47-L54) ([L203-L217](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L203-L217)).
- On the first failing tool, log name, version, description, purposes, and (when non-empty) layer, then break out of the loop ([L218-L236](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L218-L236)).

Final pass/fail: each leaf returns `tcu::TestStatus::pass` only if every checked condition holds; otherwise it returns `tcu::TestStatus::fail`. Both leaves pass trivially when `toolCount == 0` because the test skips the validation body.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `validate_getter` | Getter return code or count mismatch (wrong `VkResult` for one of the array sizes, or inconsistent count across calls). |
| `validate_tools_properties` | Tool property field validation failure (`sType`, `purposes`, or string length bound violation). |

### Cause Analysis

#### Getter return code or count mismatch

**Possible failure symptoms:** the test logs `getPhysicalDeviceToolPropertiesEXT wrong result code`, `Got different tools count on the second call`, `Bigger array causes an error`, `Zero array causes an error`, or `Smaller array causes an error`, and returns `Fail`. The symptom names which array-size case failed.

**Possible implementation causes:** the driver returns a `VkResult` other than `VK_SUCCESS` for a count query, exact-size, or oversized array; or returns a `VkResult` other than `VK_INCOMPLETE` for a zero-size or half-size array; or writes a count that differs from the count reported by the count query. Per the Vulkan enumeration contract described in `Background Knowledge`, an implementation must return `VK_SUCCESS` for full and oversized arrays and `VK_INCOMPLETE` for undersized arrays, with the written count reflecting the number of entries written. A mismatch points to driver-side handling of the array-size argument in `vkGetPhysicalDeviceToolPropertiesEXT`; source-level investigation of the driver is needed to identify the specific branch.

#### Tool property field validation failure

**Possible failure symptoms:** the test logs `Tool validation failed` along with the offending tool's `name`, `version`, `description`, `purposes` (as a flag string), and `layer` when non-empty, then returns `Fail`.

**Possible implementation causes:** one or more returned structures have an `sType` other than `VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TOOL_PROPERTIES_EXT`; a `purposes` bitmask containing bits outside the valid `VkToolPurposeFlagBitsEXT` set; an empty `name`, `version`, or `description`; a `name`, `version`, or `layer` string whose length is not less than `VK_MAX_EXTENSION_NAME_SIZE`; or a `description` whose length is not less than `VK_MAX_DESCRIPTION_SIZE`. Each of these violates a field-level contract of `VkPhysicalDeviceToolPropertiesEXT` as checked in [`validateToolsProperties()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L203-L217). The root cause is in the tool that populates the structure (a layer or the driver's tooling reporting path); source-level investigation of that tool's property reporting is needed to pinpoint which field contract was violated.

## Case Pruning

### Requirement-based pruning

- Both test case leaves require `VK_EXT_tooling_info` device functionality, enforced by [`checkSupport()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L56-L59). Implementations without the extension skip the entire test family.
- VulkanSC builds exclude the test family: the parent dispatcher attaches `tooling_info` to the `api` test category only inside `#ifndef CTS_USES_VULKANSC` ([vktApiTests.cpp#L123-L126](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126)).
- `validate_getter` executes the half-size array case only when `toolCount > 1`; an implementation reporting zero or one tool does not exercise that branch ([L150](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L150)).

### Design-based pruning

- The two leaves do not parameterize over tool identity, tool count, or purpose combinations. The design treats any active tool set as sufficient input and validates whatever the implementation reports.
- The struct-field checks do not enumerate purpose bit combinations; they verify that the reported `purposes` mask is a subset of the valid flag bits via [`validateToolPurposeFlagBits()`](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L47-L54). Combinatorial coverage of individual purpose bits is out of scope.

## Key Takeaways

- The test family verifies the `VK_EXT_tooling_info` enumeration contract through two complementary leaves: protocol correctness across array sizes, and field-level validity of every returned structure.
- `validate_getter` exercises the standard Vulkan count-then-retrieve idiom plus three edge cases (oversized, zero-size, half-size arrays) that distinguish `VK_SUCCESS` from `VK_INCOMPLETE` returns.
- `validate_tools_properties` validates `sType`, `purposes`, and string-length bounds for `name`, `version`, `description`, and `layer`; `layer` is the only field that may be empty.
- Both leaves pass trivially when no tools are active, because the test skips the validation bodies. Meaningful coverage requires at least one active tool, and the half-size case requires at least two.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createToolingInfoTests()` | [vktApiToolingInfoTests.cpp#L258-L261](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L258-L261) | Public entry point that creates the `tooling_info` test group. |
| `createTestCases()` | [vktApiToolingInfoTests.cpp#L250-L254](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L250-L254) | Registers the two test case leaves and binds them to their implementations. |
| `checkSupport()` | [vktApiToolingInfoTests.cpp#L56-L59](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L56-L59) | Shared support check requiring `VK_EXT_tooling_info`. |
| `validateGetter()` | [vktApiToolingInfoTests.cpp#L61-L179](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L61-L179) | Implementation of the `validate_getter` leaf. |
| `validateToolsProperties()` | [vktApiToolingInfoTests.cpp#L181-L248](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L181-L248) | Implementation of the `validate_tools_properties` leaf. |
| `validateToolPurposeFlagBits()` | [vktApiToolingInfoTests.cpp#L47-L54](../../../modules/vulkan/api/vktApiToolingInfoTests.cpp#L47-L54) | Helper that checks `purposes` against the valid `VkToolPurposeFlagBitsEXT` set. |
| Parent dispatcher guard | [vktApiTests.cpp#L123-L126](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126) | Wraps `tooling_info` registration in `#ifndef CTS_USES_VULKANSC`, confirming the non-VulkanSC scope. |
| Header | [vktApiToolingInfoTests.hpp](../../../modules/vulkan/api/vktApiToolingInfoTests.hpp#L1) | Declares `createToolingInfoTests()`. |
