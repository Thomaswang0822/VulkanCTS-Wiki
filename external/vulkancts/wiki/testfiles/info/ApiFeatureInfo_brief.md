# Understanding Brief: ApiFeatureInfo

## One-Sentence Test Purpose

This page covers the API-information leaves that query Vulkan instance, device, and device-group state and check that the returned data, enumeration behavior, and advertised capabilities satisfy selected CTS rules.

## Background Knowledge

### Vulkan enumeration and query results

Many Vulkan queries use a count-and-data pattern. CTS can call an enumeration with deliberately limited storage to check the API's incomplete-result behavior, then inspect the returned list for duplicate or disallowed entries.

Why it matters here:

- Enumeration leaves validate both the reported objects and selected robustness behavior of the query API.
- Property leaves use caller-owned buffers with guard bytes, so they can detect writes past the structure being queried.

### Advertised capability versus usable entry point

An extension name in an enumeration is a capability claim. The test suite can separately check its generated dependency rules or ask `vkGetDeviceProcAddr` for device-level commands promised by a supported instance extension.

Why it matters here:

- A driver can enumerate a name yet omit a required dependency or entry point.
- These checks do not execute shaders or render work; they assess API-query and capability-reporting contracts.

## One Concrete Example

The `device_features` leaf fills a `VkPhysicalDeviceFeatures` buffer with a guard pattern, calls `vkGetPhysicalDeviceFeatures`, then checks that the guard bytes survive and that the tracked members were initialized. It also requires `robustBufferAccess`. This one query shows the two recurring checks in this file: returned data must be complete, and the implementation must not write outside the caller's structure.

## End-to-End Test Flow

```text
[host] select one registered info leaf
[host] enumerate, query, or create the small device-group setup required by that leaf
[host] log the returned API data
[host] apply the leaf's duplicate, guard-byte, initialization, dependency, name, range, or feature rule
[host] return pass, fail, or NotSupportedError
```

## Generated Test Artifacts and Bound Resources

This page has no generated shaders, GPU work, result image, or readback buffer. Guard-filled host buffers are the important test artifact: they expose query writes beyond a returned structure. `device_group_peer_memory_features` creates a Vulkan device group to issue its query, but it does not submit workload commands.

## What Is Checked

- Enumeration leaves check incomplete-result handling and, where applicable, duplicate layer or extension names and unknown Khronos extension names.
- Query leaves check guard bytes, structure initialization, selected consistency rules, and API-version or mandatory-feature requirements.
- Capability leaves check generated extension dependencies, paired extension-support requirements, device-level entry-point availability, absence of obsolete `VK_KHX_` names, memory-budget ranges and usage growth, or peer-memory flags.
- Unsupported `VK_EXT_memory_budget` configurations are skipped by the leaves' shared support check, and insufficient device-group configurations throw `NotSupportedError`; neither is reported as a failure.

## Behavior Parameter Identification

> **Behavior parameter:** behavior group
>
> **Candidate values:** enumeration and list validation; core physical-device query validation; extension and entry-point consistency; optional memory-budget and device-group capability checks.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `enumeration and list validation` | Enumeration result handling, duplicate-name reporting, or Khronos extension-name validation failure. |
| `core physical-device query validation` | Query buffer overwrite, incomplete initialization, inconsistent reported properties, memory properties, or mandatory features. |
| `extension and entry-point consistency` | Advertised extension dependency, paired extension-support requirement, device-level entry-point, or obsolete extension-name failure. |
| `optional memory-budget and device-group capability checks` | Invalid memory-budget values, missing heap-usage growth after allocation, cross-instance budget inconsistency, or peer-memory flags after the required extension or device-group configuration is available. |

## Important Variations and Special Cases

- `instance_extension_dependencies` and `device_extension_dependencies` are registered in both package profiles; the former `CTS_USES_VULKANSC` compile-time exclusion was removed.
- `physical_device_groups` and `device_group_peer_memory_features` use `CustomInstanceTest<E071>` to request `VK_KHR_device_group_creation`.
- `device_memory_budget` and `device_memory_budget_multi_instance` require `VK_EXT_memory_budget` through a shared `checkSupport()` function.
- `device_group_peer_memory_features` needs the selected device group to contain at least two physical devices.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `info` registrations | [`vktApiFeatureInfo.cpp#L9163-L9195`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L9163-L9195) | Defines every leaf in this page; both package profiles register the same set. |
| Enumeration and extension checks | [`vktApiFeatureInfo.cpp#L2592-L2993`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2592-L2993) | Implements enumeration, dependency, paired-support, entry-point, and extension-name checks. |
| Core property queries | [`vktApiFeatureInfo.cpp#L3032-L3469`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3032-L3469) | Implements feature, property, queue-family, and memory-property checks. |
| Optional capabilities | [`vktApiFeatureInfo.cpp#L3471-L3936`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3471-L3936) | Implements peer-memory, memory-budget (single and multi-instance), and mandatory-feature checks. |

## Questions / Risk Points for User Audit

- Does grouping the flat leaves by validation mechanism make their differing pass conditions clear?
- Does the page distinguish unsupported optional capability configurations from failures?

## Conversion Notes for Final Wiki Rewrite

- Keep the behavior groups as the final page's behavioral axis.
- Copy the Failure Cause Mapping table unchanged.
- Keep the final Background Knowledge shorter than this teaching brief.
- No shader walkthrough is needed.
