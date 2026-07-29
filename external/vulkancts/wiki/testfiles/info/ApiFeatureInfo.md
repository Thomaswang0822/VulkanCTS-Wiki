## Overview

**Core question:** Do the `info` leaves implemented in `vktApiFeatureInfo.cpp` report Vulkan API state through valid enumeration and query behavior, with consistent advertised capabilities?

- This page covers the 17 direct `info` test case leaves registered by [`createFeatureInfoInstanceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8939), [`createFeatureInfoDeviceTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8941-L8955), and [`createFeatureInfoDeviceGroupTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8957-L8960).
- The file adds its leaves directly under the `info` test category. [`vktInfoTests.cpp`](../../../modules/vulkan/vktInfoTests.cpp#L260-L270) owns the four local reporting leaves documented in [InfoTests](InfoTests.md).
- Each case runs host-side Vulkan API calls. The cases do not compile shaders, submit commands, or compare rendered output.
- The page groups the flat registration list by the validation mechanism that changes what a failing result means.

## Background Knowledge

- **Enumeration queries.** Vulkan enumeration APIs commonly first return a count and then fill caller-provided storage. A query may return an incomplete result if the supplied capacity is too small. Several leaves deliberately exercise that behavior, then inspect the reported list.
- **Caller-owned query structures.** APIs such as `vkGetPhysicalDeviceFeatures` write into memory provided by the application. CTS pre-fills adjacent guard bytes and checks them afterward, so a result can expose a write outside the target structure as well as bad contents.
- **Advertised capabilities.** An enumerated extension name is a capability claim. The extension-dependency and entry-point leaves check whether such claims agree with generated dependency data and callable device-level commands.

## Registration Hierarchy

```text
info
├── physical_devices
├── physical_device_groups
├── instance_layers
├── instance_extensions
├── instance_extension_dependencies (Vulkan only)
├── instance_extension_device_functions
├── device_features
├── device_properties
├── device_queue_family_properties
├── device_memory_properties
├── device_layers
├── device_extensions
├── device_extension_dependencies (Vulkan only)
├── device_no_khx_extensions
├── device_memory_budget
├── device_mandatory_features
└── device_group_peer_memory_features
```

The two dependency leaves are not registered when `CTS_USES_VULKANSC` is defined [registration](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960). The Vulkan mustpass list contains all 17 leaves, while the Vulkan SC list omits those two dependency leaves [Vulkan mustpass](../../../mustpass/main/vk-default/info.txt#L1-L21), [Vulkan SC mustpass](../../../mustpass/main/vksc-default/info.txt#L1-L19).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| API scope | instance, device, device group | Chooses the Vulkan object or API level whose information is queried. | [registration builders](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960) |
| Query form | enumeration, direct property query, capability check | Determines whether CTS checks list behavior, returned structure bytes, or a semantic capability rule. | [implementation ranges](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2632-L3802) |
| Package variant | Vulkan; Vulkan SC without two dependency leaves | Changes only the compile-time presence of the dependency-validation leaves. | [conditional registrations](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8934-L8950) |
| Optional support | `VK_EXT_memory_budget`; selected multi-device group | Causes the relevant optional leaf to skip when its required configuration is unavailable. | [memory budget](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3667-L3730), [peer memory](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3495-L3665) |

## Behavior Parameters

The primary behavioral axis is the validation mechanism. Each group covers exact registered leaves with the same broad observable contract.

### `enumeration and list validation`: enumerate and inspect returned lists

`physical_devices` and `physical_device_groups` log returned handles or groups and test incomplete-result behavior. `instance_layers` and `device_layers` additionally reject duplicate layer names. `instance_extensions` and `device_extensions` enumerate both global and layer-specific lists, reject duplicate names, reject unknown Khronos-controlled extension names, and test incomplete-result behavior [enumeration and list checks](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2632-L2825), [device list checks](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2922-L2990).

### `core physical-device query validation`: validate returned feature and property structures

`device_features`, `device_properties`, and `device_memory_properties` query physical-device structures into guard-filled buffers. They reject writes past those structures and check selected initialization and consistency rules. `device_features` requires `robustBufferAccess`; `device_properties` checks feature-dependent limits, a terminated device name, and an API version within the framework range; `device_memory_properties` checks heap and type relationships plus a host-visible, host-coherent memory type [feature query](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3056-L3154), [property query](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3276-L3346), [memory-property query](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3362-L3493).

`device_queue_family_properties` is the lightweight member of this group. It logs the returned queue-family properties and returns pass after the query [queue-family query](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3348-L3360).

### `extension and entry-point consistency`: check advertised API surface

`instance_extension_dependencies` and `device_extension_dependencies` check advertised extensions against generated dependency rules for the first released API version supported by the context. `instance_extension_device_functions` asks `vkGetDeviceProcAddr` for each generated device-level command required by a supported instance extension. `device_no_khx_extensions` fails when an enumerated instance or device extension begins with the obsolete `VK_KHX_` prefix [dependency and entry-point checks](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2828-L2919), [device dependency check](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2993-L3016).

### `optional memory-budget and device-group capability checks`: validate supported optional paths

`device_memory_budget` chains `VkPhysicalDeviceMemoryBudgetPropertiesEXT` into `VkPhysicalDeviceMemoryProperties2`. It requires `VK_EXT_memory_budget`, protects the query buffer with guards, requires nonzero supported-heap budgets that do not exceed heap sizes, and requires zero budget and usage for unused heap slots [memory-budget check](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3667-L3730).

`device_group_peer_memory_features` requires a selected group and selected device index that are valid, plus at least two physical devices. It creates the device group, queries peer-memory features for each distinct device pair and heap, protects the result buffer with guards, and requires `VK_PEER_MEMORY_FEATURE_COPY_DST_BIT` without bits outside the defined peer-memory feature set [peer-memory check](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3495-L3665).

`device_mandatory_features` checks generated mandatory-feature requirements. In non-compute-only Vulkan 1.4 contexts, it also checks the host-image-copy or graphics-and-transfer-queue condition [mandatory-feature check](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3739-L3802).

## Shader Analysis

These leaves do not test shader behavior. They issue host-side instance and physical-device queries, inspect returned structures and lists, and occasionally create a device group to query peer-memory support.

## Runtime Execution and Result Checking

- The framework chooses one registered function case. Most leaves call a Vulkan enumeration or physical-device query, write the results to the CTS log, and collect validation failures in `tcu::ResultCollector` or return a direct failing `TestStatus`.
- Enumeration leaves use result collectors for incomplete-result probes, duplicate names, and unknown Khronos extension names. Dependency and entry-point leaves fail when advertised capability data does not meet their generated rule or command lookup.
- Direct property queries use guard-filled host buffers. The cases fail if a guard byte changes, a tracked member remains uninitialized, or a leaf-specific property rule fails.
- `device_memory_budget` throws `NotSupportedError` when `VK_EXT_memory_budget` is unavailable. `device_group_peer_memory_features` throws `NotSupportedError` for a missing or too-small selected device group. Those outcomes prune unsupported configurations rather than assert an invalid implementation result.
- The cases produce no GPU output buffer or image. The observed result is the function's collected failure state, direct `TestStatus`, or supported-configuration skip.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `enumeration and list validation` | Enumeration result handling, duplicate-name reporting, or Khronos extension-name validation failure. |
| `core physical-device query validation` | Query buffer overwrite, incomplete initialization, inconsistent reported properties, memory properties, or mandatory features. |
| `extension and entry-point consistency` | Advertised extension dependency, device-level entry-point, or obsolete extension-name failure. |
| `optional memory-budget and device-group capability checks` | Invalid memory-budget values or peer-memory flags after the required extension or device-group configuration is available. |

### Cause Analysis

#### Enumeration and list validation failure

**Possible failure symptoms:** The result collector reports an incomplete-result, duplicate layer or extension name, or unknown Khronos extension-name error. The affected leaf returns the collector's failure result.

**Possible implementation causes:** The implementation may report an enumeration count or incomplete result inconsistently, repeat a layer or extension name in one returned list, or expose a `VK_KHR_` extension that CTS does not recognize. The relevant list checks are implemented in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2632-L2825) and [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2922-L2990).

#### Core physical-device query validation failure

**Possible failure symptoms:** A leaf reports a changed guard byte, incomplete structure initialization, an invalid feature, property, memory-heap, memory-type, or mandatory-feature condition, or an API-version mismatch.

**Possible implementation causes:** A query implementation can overwrite bytes beyond the supplied structure, leave returned members uninitialized, report data inconsistent with a checked feature or memory rule, or omit a mandatory feature. `device_queue_family_properties` has no comparable post-query validation, so its direct return only establishes whether the query path completed [queue-family query](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3348-L3360). The other checks are source-defined CTS rules rather than a general diagnosis of a particular driver component.

#### Extension and entry-point consistency failure

**Possible failure symptoms:** CTS reports a missing dependency for an advertised extension, a missing device-level entry point for a supported instance extension, or an invalid `VK_KHX_` name.

**Possible implementation causes:** Extension enumeration may advertise an extension without its generated dependency set, `vkGetDeviceProcAddr` may fail to expose a required command for a supported instance extension, or the implementation may retain an obsolete extension prefix. The source performs these exact checks in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2828-L2919) and [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2993-L3016).

#### Optional memory-budget and device-group capability check failure

**Possible failure symptoms:** After a supported configuration is established, CTS reports a changed guard byte, zero or oversized supported-heap budget, nonzero values for unused heap slots, a missing peer-memory copy-destination bit, or peer-memory bits outside the accepted set.

**Possible implementation causes:** `VK_EXT_memory_budget` data may not match the queried memory heaps, or the peer-memory query can return a flag set that violates the source's accepted condition. A missing extension, invalid selected group, or group with fewer than two devices is a `NotSupportedError`, not this failure category [memory-budget conditions](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3667-L3730), [peer-memory conditions](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3495-L3665).

## Case Pruning

### Requirement-based pruning

- `instance_extension_dependencies` and `device_extension_dependencies` are excluded from Vulkan SC builds at compile time.
- `physical_device_groups` and `device_group_peer_memory_features` request `VK_KHR_device_group_creation` through `CustomInstanceTest<E071>` [custom instance wrapper](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L749-L776).
- `device_memory_budget` skips when `VK_EXT_memory_budget` is unsupported.
- `device_group_peer_memory_features` skips when the selected group or device index is invalid, or when the selected group has fewer than two physical devices.

### Design-based pruning

- Each leaf fixes its API scope and validation rule. The file does not combine every enumeration, structure, extension, and device-group check into a generated matrix.
- Dependency validation uses the first supported released API version rather than repeating the generated dependency check for every version [dependency loop](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2828-L2850).
- Peer-memory validation iterates only distinct local and remote device indices because querying a device against itself does not test peer access [peer-memory loop](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3625-L3665).

## Key Takeaways

- This file is the implementation boundary for the delegated `info` leaves. Its registrations remain flat even though their validation mechanisms differ.
- Enumeration cases test more than logging: they check incomplete-result behavior and, for layer and extension lists, name validity.
- Guard bytes and initialization checks make property-query failures meaningful even without a rendering workload.
- A capability leaf can fail because a driver advertises an inconsistent API surface. Unsupported optional configurations are skipped instead.
- The `device_group_peer_memory_features` result applies only after CTS establishes a usable multi-device configuration.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `info` registration builders | [`vktApiFeatureInfo.cpp#L8928-L8960`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8928-L8960) | Defines the 17 page-scope leaves and the two Vulkan SC exclusions. |
| Enumeration and extension checks | [`vktApiFeatureInfo.cpp#L2632-L3016`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2632-L3016) | Implements list enumeration, dependency, entry-point, and obsolete-name validation. |
| Core query checks | [`vktApiFeatureInfo.cpp#L3056-L3493`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3056-L3493) | Implements feature, property, queue-family, and memory-property leaves. |
| Device-group peer-memory query | [`vktApiFeatureInfo.cpp#L3495-L3665`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3495-L3665) | Establishes support conditions and validates peer-memory flags. |
| Memory-budget and mandatory-feature checks | [`vktApiFeatureInfo.cpp#L3667-L3802`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3667-L3802) | Implements optional budget validation and generated mandatory-feature checks. |
| Category caller | [`vktInfoTests.cpp#L260-L270`](../../../modules/vulkan/vktInfoTests.cpp#L260-L270) | Adds these leaves under `info` after the local reporting cases. |
| Vulkan and Vulkan SC mustpass scope | [`vk-default/info.txt#L1-L21`](../../../mustpass/main/vk-default/info.txt#L1-L21), [`vksc-default/info.txt#L1-L19`](../../../mustpass/main/vksc-default/info.txt#L1-L19) | Confirms the package-specific leaf inventories. |
