## Overview

**Core question:** does the implementation correctly populate the two physical-device property structures introduced by `VK_KHR_maintenance7` (the layered API Vulkan properties chain and the total dynamic buffer descriptor limits)?

- Covers the `maintenance7` test family in the `api` test category, implemented in [vktApiMaintenance7Tests.cpp](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L1).
- Two test case leaves under `api.maintenance7`: `layered_api_vulkan_properties` and `total_dynamic_buffers_properties`.
- `layered_api_vulkan_properties` queries the `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` chain and checks that layered Vulkan APIs report consistent `deviceID`/`vendorID` and that the implementation zero-fills `limits`/`sparseProperties` for Vulkan layered APIs while leaving them untouched for non-Vulkan layered APIs.
- `total_dynamic_buffers_properties` queries `VkPhysicalDeviceMaintenance7PropertiesKHR` and verifies six monotonicity inequalities against Vulkan 1.0 and Vulkan 1.2 device limits, covering both regular and update-after-bind dynamic buffer descriptors.
- The whole source file is guarded by `#ifndef CTS_USES_VULKANSC`, so this family is non-VulkanSC only; the parent registration in [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L135) is inside the matching VulkanSC guard.

## Background Knowledge

- **Layered Vulkan implementations.** A Vulkan implementation may be layered on top of another Vulkan implementation (a layered API), exposed through `VK_KHR_maintenance7`'s `VkPhysicalDeviceLayeredApiPropertiesListKHR` chain on `VkPhysicalDeviceProperties2`. The chain reports each layered API's `vendorID`, `deviceID`, and `layeredAPI` kind, and may carry a `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` extension structure for layered APIs that are themselves Vulkan. Knowing this layered model is required to understand why `deviceID`/`vendorID` consistency and zero-filled `limits` are the properties under test.
- **Update-after-bind descriptor limits.** Vulkan 1.2 promoted `VkPhysicalDeviceDescriptorIndexingProperties` (originally `VK_EXT_descriptor_indexing`) and exposed `max*UpdateAfterBind*` limits that apply to descriptors created with `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT_EXT`. The `total_dynamic_buffers_properties` test case compares `VK_KHR_maintenance7` total-update-after-bind limits against these Vulkan 1.2 component limits, so the reader needs to know that update-after-bind is a separate descriptor-pool category with its own limits.

## Registration Hierarchy

```text
api.maintenance7
├── layered_api_vulkan_properties
└── total_dynamic_buffers_properties
```

The two test case leaves are registered directly under the `maintenance7` test family by [createMaintenance7Tests](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L307-L317), with no intermediate nodes between the test family and the test case leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `layered_api_vulkan_properties`, `total_dynamic_buffers_properties` | Each leaf targets a distinct `VK_KHR_maintenance7` property structure and exercises an independent property contract. | [vktApiMaintenance7Tests.cpp#L312-L314](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L312) |
| Layered API kind | `VK_PHYSICAL_DEVICE_LAYERED_API_VULKAN_KHR`, non-Vulkan layered APIs, none reported | Decides which consistency rule applies in the layered-API leaf: Vulkan layered APIs must zero-fill `limits`/`sparseProperties` and match `deviceID`/`vendorID`; non-Vulkan layered APIs must have those fields left untouched. The leaf passes trivially if no layered APIs are reported. | [vktApiMaintenance7Tests.cpp#L93-L173](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L93) |
| Descriptor category | uniform buffers, storage buffers, total buffers | The dynamic-buffer leaf checks that the maintenance7 total limit is at least the matching component limit (uniform-only, storage-only) and at least the sum of the two components. | [vktApiMaintenance7Tests.cpp#L221-L249](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221) |
| Binding mode | regular, update-after-bind | The same three monotonicity checks are repeated against Vulkan 1.2 update-after-bind limits, giving the six checks that make up the leaf. | [vktApiMaintenance7Tests.cpp#L252-L284](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L252) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf exercises an independent `VK_KHR_maintenance7` property contract.

### layered_api_vulkan_properties — Layered API Vulkan property chain correctness

Verifies that the `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` chain hanging off `VkPhysicalDeviceProperties2` is populated correctly. The leaf first queries `VkPhysicalDeviceLayeredApiPropertiesListKHR` to obtain the layered-API count, then allocates per-entry `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` structures, pre-fills their `limits` and `sparseProperties` with `0xFF`, and re-queries. For each layered API the test checks: (1) if the layered API is `VK_PHYSICAL_DEVICE_LAYERED_API_VULKAN_KHR`, the `deviceID` and `vendorID` in `VkPhysicalDeviceLayeredApiPropertiesKHR` must match the same fields in the chained `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR::properties.properties`; (2) for Vulkan layered APIs, every byte of `limits` and `sparseProperties` in the chained Vulkan properties must be zero, proving the implementation wrote them; (3) for non-Vulkan layered APIs, every byte must remain `0xFF`, proving the implementation ignored the Vulkan-specific extension. See [iterate](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L48-L178).

### total_dynamic_buffers_properties — Total dynamic buffer descriptor limit monotonicity

Verifies that the six `max*Total*` and `max*UpdateAfterBindTotal*` limits in `VkPhysicalDeviceMaintenance7PropertiesKHR` are consistent with existing Vulkan 1.0 and Vulkan 1.2 dynamic-buffer limits. The leaf queries the maintenance7 structure through the `pNext` chain of `VkPhysicalDeviceProperties2`, then checks that each total limit is greater than or equal to its component limit, and that each combined total is greater than or equal to the sum of the uniform and storage components. The same three checks are applied to the regular and update-after-bind categories. See [iterate](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L211-L287).

## Shader Analysis

No shader is involved in this test family. Both leaves query physical-device properties on the host through `vkGetPhysicalDeviceProperties2` and validate the returned structures. There is no pipeline, dispatch, draw, or device-side computation, so no representative shader walkthrough is applicable.

## Runtime Execution and Result Checking

Both test case leaves run on the host; no queue submissions, resources, or synchronization are involved.

`layered_api_vulkan_properties` execution flow:

- Query `VkPhysicalDeviceProperties2` with a `VkPhysicalDeviceLayeredApiPropertiesListKHR` pNext to obtain `layeredApiCount` ([vktApiMaintenance7Tests.cpp#L54-L65](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L54)).
- If the count is non-zero, allocate per-entry `VkPhysicalDeviceLayeredApiPropertiesKHR` and `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR` structures. For each entry, chain the Vulkan-properties structure into the layered-API properties `pNext`, set its `sType`, and `memset` both `limits` and `sparseProperties` to `0xFF` so the test can detect whether the implementation writes them ([vktApiMaintenance7Tests.cpp#L66-L88](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L66)).
- Re-query `vkGetPhysicalDeviceProperties2` with the populated chain.
- For each layered-API entry, perform the deviceID/vendorID and zero-fill/ignore byte-by-byte checks described under `### layered_api_vulkan_properties`.
- The leaf returns `pass` if no check fails, or `fail` with a log message naming the offending index and field.

`total_dynamic_buffers_properties` execution flow:

- Build a `VkPhysicalDeviceMaintenance7PropertiesKHR` and chain it into `VkPhysicalDeviceProperties2`; query `vkGetPhysicalDeviceProperties2` ([vktApiMaintenance7Tests.cpp#L213-L217](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L213)).
- Read the Vulkan 1.0 `VkPhysicalDeviceLimits` and Vulkan 1.2 `VkPhysicalDeviceVulkan12Properties` from the context.
- Apply six inequality checks: three for regular dynamic buffers (uniform, storage, total-vs-sum) and three mirrored for update-after-bind. Each failed check logs the maintenance7 value and the offending component value.
- The leaf returns `pass` if all six checks hold, or `fail` with the first violating inequality.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layered_api_vulkan_properties` | Layered API property mismatch; layered API limits/sparseProperties not zero-filled or not ignored as required. |
| `total_dynamic_buffers_properties` | Total dynamic buffer descriptor limit monotonicity violation. |

### Cause Analysis

#### Layered API property mismatch

**Possible failure symptoms:** the test logs that `deviceID` or `vendorID` of `VkPhysicalDeviceLayeredApiPropertiesKHR` and `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR::properties::properties` at a given layered-API index do not match, and returns `fail` ([vktApiMaintenance7Tests.cpp#L95-L110](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L95)).

**Possible implementation causes:** the implementation fills the layered-API property structure with values that are inconsistent with the chained Vulkan-properties structure. Per `VK_KHR_maintenance7`, a layered API identified as `VK_PHYSICAL_DEVICE_LAYERED_API_VULKAN_KHR` must report the same `deviceID` and `vendorID` in both structures. A mismatch points to driver-side population of the chained structure being out of sync with the top-level layered-API entry, for example by copying stale identifiers or by leaving the chained structure's `properties.properties.deviceID`/`vendorID` uninitialized. Source-level investigation is needed if the symptom appears without an obvious identifier-source mismatch.

#### Layered API limits not zero-filled or not ignored

**Possible failure symptoms:** the test logs that, for a Vulkan layered API, `VkPhysicalDeviceLayeredApiVulkanPropertiesKHR::properties::limits` or `sparseProperties` was not zero-filled; or, for a non-Vulkan layered API, that those fields were not left at the pre-filled `0xFF` value ([vktApiMaintenance7Tests.cpp#L113-L173](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L113)).

**Possible implementation causes:** the `0xFF` pre-fill is a robustness probe: it lets the test distinguish "implementation wrote the field" from "implementation left the field untouched". For Vulkan layered APIs, `VK_KHR_maintenance7` requires the chained `limits` and `sparseProperties` to be zero-filled; a non-zero byte indicates the implementation either wrote stale data or only partially cleared the structure. For non-Vulkan layered APIs, the extension requires the Vulkan-specific chained structure to be ignored; any byte that is no longer `0xFF` indicates the implementation wrote to a structure it should not have touched. Both behaviors point to driver-side handling of the layered-API property chain being incorrect for the reported `layeredAPI` kind.

#### Total dynamic buffer descriptor limit monotonicity violation

**Possible failure symptoms:** the test logs that one of the six maintenance7 total limits is smaller than its component limit (or, for the combined total, smaller than the sum of the uniform and storage component limits), and returns `fail` ([vktApiMaintenance7Tests.cpp#L221-L284](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L221)).

**Possible implementation causes:** `VK_KHR_maintenance7` defines the `maxDescriptorSetTotal*` limits as the maximum number of dynamic descriptors of a given category that can be present in a descriptor set overall, and `maxDescriptorSetUpdateAfterBindTotal*` as the equivalent for update-after-bind descriptor sets. By construction, each total limit must be at least as large as its single-category component (uniform-only or storage-only) and at least as large as the sum of both components, because a set using only one category is a valid subset of any mixed usage. A failure indicates that the implementation reported a total that is smaller than a legal subset, which is a contradiction in the advertised limits. The likely driver-side cause is computing the maintenance7 totals from a different source than the existing Vulkan 1.0/1.2 component limits, or failing to clamp the totals to be at least the components. Source-level investigation is needed to confirm the specific reporting path.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_maintenance7` is required by both test case leaves; `checkSupport` calls `ctx.requireDeviceFunctionality("VK_KHR_maintenance7")` for each ([vktApiMaintenance7Tests.cpp#L190](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L190), [vktApiMaintenance7Tests.cpp#L299](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L299)).
- The entire source file is guarded by `#ifndef CTS_USES_VULKANSC` ([vktApiMaintenance7Tests.cpp#L30](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L30), [vktApiMaintenance7Tests.cpp#L322](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L322)), so the family is not registered on VulkanSC builds. The parent registration in [vktApiTests.cpp#L128-L137](../../../modules/vulkan/api/vktApiTests.cpp#L128) sits inside the matching VulkanSC guard.
- The `total_dynamic_buffers_properties` leaf reads Vulkan 1.2 properties through `m_context.getDeviceVulkan12Properties()`. The CTS context exposes these on any Vulkan 1.2+ device or on devices exposing `VK_EXT_descriptor_indexing` with the appropriate promotion handling; implementations that do not support update-after-bind descriptor indexing still expose the Vulkan 1.2 properties structure, with the relevant limits reported as zero, in which case the inequalities collapse to `total >= 0` and the leaf passes.

### Design-based pruning

- No parameter matrix is generated. Each test case leaf is a single fixed instance that walks all reported layered APIs or all six total-limit inequalities in one run, rather than emitting one CTS case per layered-API entry or per inequality.
- The `layered_api_vulkan_properties` leaf is designed to pass trivially when no layered APIs are reported (`layeredApiCount == 0`); there is no separate case for "no layered APIs" versus "layered APIs present". This is intentional: the property under test is vacuously correct when there is nothing to report.

## Key Takeaways

- The `maintenance7` test family verifies two independent `VK_KHR_maintenance7` property contracts through pure host-side queries of `vkGetPhysicalDeviceProperties2`; no shaders, pipelines, or queue work are involved.
- `layered_api_vulkan_properties` uses an `0xFF` pre-fill as a write-probe: zero bytes after the query prove the implementation wrote the Vulkan layered-API `limits`/`sparseProperties`; preserved `0xFF` bytes prove the implementation ignored the chained Vulkan structure for non-Vulkan layered APIs.
- `total_dynamic_buffers_properties` checks six monotonicity inequalities; the structural rule is that any legal single-category usage is a subset of mixed usage, so each total limit must dominate its components and their sum.
- See `## Failure Meaning` for the cause analysis behind each observable failure symptom.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createMaintenance7Tests` | [vktApiMaintenance7Tests.cpp#L307-L317](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L307) | Registers the `maintenance7` test family and its two test case leaves. |
| `Maintenance7LayeredApiVulkanPropertiesTestInstance::iterate` | [vktApiMaintenance7Tests.cpp#L48-L178](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L48) | Implements the layered-API property chain query, the `0xFF` pre-fill probe, and the deviceID/vendorID plus zero-fill/ignore verification. |
| `Maintenance7LayeredApiVulkanPropertiesTestCase::checkSupport` | [vktApiMaintenance7Tests.cpp#L188-L191](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L188) | Gates the layered-API leaf on `VK_KHR_maintenance7`. |
| `Maintenance7TotalDynamicBuffersPropertiesTestInstance::iterate` | [vktApiMaintenance7Tests.cpp#L211-L287](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L211) | Queries `VkPhysicalDeviceMaintenance7PropertiesKHR` and applies the six total-dynamic-buffer monotonicity checks. |
| `Maintenance7TotalDynamicBuffersPropertiesTestCase::checkSupport` | [vktApiMaintenance7Tests.cpp#L297-L300](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L297) | Gates the dynamic-buffer leaf on `VK_KHR_maintenance7`. |
| `createMaintenance7Tests` declaration | [vktApiMaintenance7Tests.hpp#L34](../../../modules/vulkan/api/vktApiMaintenance7Tests.hpp#L34) | Header declaration consumed by the parent registration. |
| Parent registration | [vktApiTests.cpp#L135](../../../modules/vulkan/api/vktApiTests.cpp#L135) | Adds `createMaintenance7Tests` under the `api` test category, inside the VulkanSC guard at [vktApiTests.cpp#L128-L137](../../../modules/vulkan/api/vktApiTests.cpp#L128). |
| VulkanSC file guard | [vktApiMaintenance7Tests.cpp#L30](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L30), [vktApiMaintenance7Tests.cpp#L322](../../../modules/vulkan/api/vktApiMaintenance7Tests.cpp#L322) | Wraps the whole implementation; the family is non-VulkanSC only. |
