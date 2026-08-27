## Overview

**Core question:** When a device exposes `VK_EXT_shader_object`, does it also provide the API surface that the extension depends on?

- This page covers the `shader_object.api` test family, implemented in [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp) and attached to the test category root by [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63).
- The test family registers five test case leaves: `get_device_proc_addr`, `discard_rectangles`, `scissor_exclusive`, `dynamic_rendering`, and `shader_binary_uuid` [registration](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L353-L374), [api.txt](../../../mustpass/main/vk-default/shader-object/api.txt#L1-L5).
- Every check runs on the host. One leaf resolves device proc addresses for 49 dynamic-state commands on a custom device; the other four read the physical device's extension and property tables. No shader object is created and nothing is rendered.
- The page explains what each leaf asserts, how it runs, and which implementation defect a failure points to.

## Background Knowledge

For the shared concepts shader objects, dynamic state, and dynamic rendering, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Device proc-address lookup.** Applications obtain device-level functions through `vkGetDeviceProcAddr`. The returned pointer is only guaranteed for core commands and for commands belonging to enabled extensions, so a NULL result for a command the implementation is expected to provide marks a missing entry point. The test relies on this contract rather than on platform symbol lookup.
- **Extension revisions.** Each entry in the physical device's extension list reports a `specVersion`, the extension revision the implementation supports. Extensions gain functionality across revisions, so an extension being present does not by itself mean the needed revision is present.

## Registration Hierarchy

```text
shader_object.api
├── get_device_proc_addr
├── discard_rectangles
├── scissor_exclusive
├── dynamic_rendering
└── shader_binary_uuid
```

[createShaderObjectApiTests()](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L353-L374) builds the `api` test family: it adds `get_device_proc_addr` directly, then iterates a four-entry table to add the remaining leaves. The category root file attaches this test family as its first registered child [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63). All five leaves appear in the shader-object mustpass file [api.txt](../../../mustpass/main/vk-default/shader-object/api.txt#L1-L5), which the main mustpass includes through its `dEQP-VK.*` wildcard [main.txt](../../../mustpass/main/src/main.txt); only the `performance` test family of this category is excluded [excluded-tests.txt](../../../mustpass/main/src/excluded-tests.txt).

## Parameter Dimensions and Observed Values

The test family has no generated matrix. The table below lists the fixed dimensions that define its five leaves.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `get_device_proc_addr`, `discard_rectangles`, `scissor_exclusive`, `dynamic_rendering`, `shader_binary_uuid` | Selects the API contract being checked; each leaf is one fixed host-side check. | [registration](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L353-L374) |
| Checked command set | 49 command names from four dynamic-state extensions | Defines the proc-address surface that must resolve on a device enabled with only `VK_EXT_shader_object`. | [command list](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L108-L162) |
| Minimum extension revision | `2` | Threshold the two optional extensions must meet when present alongside shader objects. | [revision checks](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L278-L313) |
| API version threshold | Vulkan `1.3` | Below this version, `VK_KHR_dynamic_rendering` must be advertised alongside shader object support. | [version check](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L255-L277) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. The five leaves share no parameters; each checks one property of the API surface around `VK_EXT_shader_object`.

### get_device_proc_addr: dynamic-state commands must resolve

This leaf checks that the dynamic-state commands the shader-object model draws on can be resolved from a device that enables nothing besides `VK_EXT_shader_object`. `iterate()` creates a custom device with exactly one enabled extension and calls `vkGetDeviceProcAddr` for 49 command names; the first NULL pointer fails the leaf with that command's name [iterate()](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L63-L172), [command list](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L108-L162).

The single-extension device is the point of the design. The shared CTS context device enables many extensions, so a resolvable pointer there would not show that shader object support alone makes the command available. The command list spans `VK_EXT_extended_dynamic_state`, `VK_EXT_extended_dynamic_state2`, `VK_EXT_extended_dynamic_state3`, and `VK_EXT_vertex_input_dynamic_state`; the dynamic-state-3 portion includes NV-suffixed names such as `vkCmdSetCoverageModulationModeNV` because that extension incorporated them [command list](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L128-L159).

This is the only leaf that creates a device. The other four query the physical device directly.

### discard_rectangles: optional extension must report revision 2

A device supporting both `VK_EXT_shader_object` and `VK_EXT_discard_rectangles` must report the latter at `specVersion` 2 or newer; this leaf enforces that requirement. `iterate()` scans the enumerated device extension list for `VK_EXT_discard_rectangles`; a `specVersion` below 2 fails the leaf with a log message naming the reported version [revision checks](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L278-L313).

The support gate requires both extensions, so the leaf runs only where the interaction applies. `scissor_exclusive` performs the identical check for the NV extension.

### scissor_exclusive: second revision check for the NV extension

This leaf applies the same revision expectation to `VK_NV_scissor_exclusive`: when it is supported alongside shader objects, its `specVersion` must be at least 2. The scan mirrors `discard_rectangles`, failing with the reported version when the threshold is not met [revision checks](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L297-L313).

Together the two leaves pin the revisions whose dynamic-state commands shader objects rely on.

### dynamic_rendering: dynamic rendering must be available below Vulkan 1.3

A device below Vulkan 1.3 that supports shader objects must also advertise `VK_KHR_dynamic_rendering`; this leaf enforces the dependency. `iterate()` unpacks the device API version; only when the major version is 1 and the minor version is below 3 does it scan the extension list for `VK_KHR_dynamic_rendering`, failing when the extension is absent [version check](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L255-L277).

On Vulkan 1.3 or newer the leaf passes without checking anything, because dynamic rendering was promoted to core in Vulkan 1.3. The leaf adds no support requirement beyond `VK_EXT_shader_object`; it exists to cover pre-1.3 devices, where the dependency can be violated.

### shader_binary_uuid: property UUID must be nonzero

`shaderBinaryUUID` in `VkPhysicalDeviceShaderObjectPropertiesEXT` must contain at least one nonzero byte; this leaf scans the full array to verify it. `iterate()` chains the properties structure into `VkPhysicalDeviceProperties2`, retrieves it, and fails with a log message when every byte is zero [UUID check](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L238-L254).

This is the only leaf that reads the shader-object properties structure; the neighboring `shaderBinaryVersion` field is not checked.

## Shader Analysis

This test family creates no shaders and executes no rendering or compute work. Its subject is the host-side API surface around `VK_EXT_shader_object`: device proc-address resolution, extension version reporting, and physical-device properties. A shader walkthrough would not clarify any of the checked behavior, so none is provided.

## Runtime Execution and Result Checking

`get_device_proc_addr` runs entirely on the host:

- [host] `checkSupport()` requires `VK_EXT_shader_object` [support gate](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L191-L194).
- [host] `iterate()` queries `VkPhysicalDeviceFeatures2` with `VkPhysicalDeviceShaderObjectFeaturesEXT` chained in `pNext`, then attaches the filled feature chain to `VkDeviceCreateInfo::pNext`, so the custom device is created with the shader object feature enabled [feature chain](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L85-L100).
- [host] `createCustomDevice()` creates the device with `VK_EXT_shader_object` as the only enabled extension [device creation](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L83-L102).
- [host] A `DeviceDriver` wraps the custom device, and the leaf resolves each of the 49 command names through `vkGetDeviceProcAddr` [proc-address loop](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L104-L169).
- [host] The first NULL pointer returns `fail("Failed: <command name>")`; once all names resolve, the leaf returns `pass("Pass")` [result](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L164-L171).

The four property leaves share one code path:

- [host] `checkSupport()` requires `VK_EXT_shader_object`, plus `VK_EXT_discard_rectangles` or `VK_NV_scissor_exclusive` for the two revision leaves [support gates](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L339-L350).
- [host] `iterate()` builds an `InstanceDriver`, queries `VkPhysicalDeviceProperties2` with `VkPhysicalDeviceShaderObjectPropertiesEXT` in `pNext`, and enumerates the cached device extension list [queries](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L216-L236).
- [host] Each leaf applies its own check to the query results; a failing check writes an explanatory message to the test log before returning `fail` [checks](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L238-L313).

Each leaf is a separate CTS test case with an independent pass/fail status. No state carries between them.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `get_device_proc_addr` | A required dynamic-state entry point resolves to NULL. |
| `discard_rectangles` | Supported `VK_EXT_discard_rectangles` reports `specVersion` below 2. |
| `scissor_exclusive` | Supported `VK_NV_scissor_exclusive` reports `specVersion` below 2. |
| `dynamic_rendering` | Device version below Vulkan 1.3 without `VK_KHR_dynamic_rendering` advertised. |
| `shader_binary_uuid` | All `shaderBinaryUUID` bytes are zero. |

### Cause Analysis

#### A required dynamic-state entry point resolves to NULL

**Possible failure symptoms:** The leaf stops at the first unresolved command and fails with `Failed: <command name>`, naming the exact dynamic-state function that did not resolve [proc-address loop](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L164-L169).

**Possible implementation causes:** The custom device enables only `VK_EXT_shader_object`, so a NULL result means the implementation does not expose that command on a shader-object device. Because shader objects issue pipeline state through dynamic-state commands, an implementation exposing the extension must keep those entry points reachable. The fault can lie in the driver's proc-address table, or in a loader or an active layer that fails to forward the entry point. The test names the missing command but does not localize the fault further; distinguishing driver from loader requires implementation-level investigation.

#### A supported optional extension reports specVersion below 2

**Possible failure symptoms:** The log names both extensions and the reported revision, for example `VK_EXT_shader_object and VK_EXT_discard_rectangles are supported, but VK_EXT_discard_rectangles reports version 1`, and the leaf fails [revision checks](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L278-L313).

**Possible implementation causes:** The implementation exposes an old revision of the optional extension alongside shader objects. Revision 2 of `VK_EXT_discard_rectangles` and `VK_NV_scissor_exclusive` added the dynamic-state commands for discard rectangles and exclusive scissors, and shader objects rely on those commands to set state dynamically. Reporting a lower revision means the implementation lacks the commands the interaction requires. An implementation that reports an inaccurate `specVersion` for its actual capability fails the same check.

#### VK_KHR_dynamic_rendering is missing below Vulkan 1.3

**Possible failure symptoms:** The log records that `VK_EXT_shader_object` is supported while the Vulkan version is below 1.3 and `VK_KHR_dynamic_rendering` is not, and the leaf fails [version check](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L255-L277).

**Possible implementation causes:** Shader objects render through dynamic rendering, so an implementation that exposes them on a pre-1.3 device must also advertise `VK_KHR_dynamic_rendering`. The failure points to a device that enables shader object support without the rendering dependency, or to an extension list that disagrees with the device's actual capability. Devices at Vulkan 1.3 or newer cannot fail this leaf, because dynamic rendering was promoted to core in Vulkan 1.3.

#### shaderBinaryUUID is all zero

**Possible failure symptoms:** The log records `All shaderBinaryUUID bytes are 0` and the leaf fails [UUID check](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L238-L254).

**Possible implementation causes:** The properties query returned zeroed UUID data. Either the implementation did not fill the `VkPhysicalDeviceShaderObjectPropertiesEXT` structure chained into the query, which points to property plumbing in the driver, or it reports an empty identifier for its shader binary format. The UUID identifies the shader binary format the device accepts, so the test treats an all-zero value as an invalid property rather than a valid empty one.

## Case Pruning

### Requirement-based pruning

- All five leaves require `VK_EXT_shader_object`; without it they are reported as not supported instead of failing [support gate](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L191-L194), [support gates](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L339-L341).
- `discard_rectangles` also requires `VK_EXT_discard_rectangles`, and `scissor_exclusive` requires `VK_NV_scissor_exclusive`, so those leaves run only where both sides of the interaction exist [per-leaf gates](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L342-L349).
- `dynamic_rendering` and `shader_binary_uuid` impose no requirements beyond `VK_EXT_shader_object`.

### Design-based pruning

- The test family registers five fixed leaves; there is no generated case matrix [registration](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L353-L374).
- `dynamic_rendering` performs no check on devices reporting Vulkan 1.3 or newer, because dynamic rendering was promoted to core in Vulkan 1.3. The leaf exists to cover pre-1.3 devices.
- The revision leaves scan the full extension list but can only fail on a present-but-old revision; the support gate already guarantees presence, so the scan acts as a revision check.
- The proc-address list is fixed at 49 commands from four dynamic-state extensions and is not pruned per feature at runtime [command list](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L108-L162).

## Key Takeaways

- The `api` test family is a host-side guard: it checks the API surface `VK_EXT_shader_object` depends on before other test families in the category create and draw with shader objects.
- The custom device with one enabled extension makes the proc-address result attributable to shader object support alone.
- The revision, dynamic-rendering, and UUID leaves assert dependencies rather than execution. Passing them says the extension coexists with the API contracts it needs, not that rendering works.
- See `## Failure Meaning` for what each leaf's failure points to.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Selector enum | [vktShaderObjectApiTests.cpp#L42-L48](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L42-L48) | Names the four property and extension checks behind the table-driven leaves. |
| Custom device and proc-address loop | [vktShaderObjectApiTests.cpp#L63-L172](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L63-L172) | Implements `get_device_proc_addr`: single-extension device creation and the 49-command resolution loop. |
| Command list | [vktShaderObjectApiTests.cpp#L108-L162](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L108-L162) | The 49 dynamic-state command names, grouped by source extension. |
| `get_device_proc_addr` support gate | [vktShaderObjectApiTests.cpp#L191-L194](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L191-L194) | Requires `VK_EXT_shader_object`. |
| Property and extension checks | [vktShaderObjectApiTests.cpp#L214-L315](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L214-L315) | Implements the four table-driven leaves: UUID scan, dynamic-rendering dependency, and revision checks. |
| Per-leaf support gates | [vktShaderObjectApiTests.cpp#L339-L350](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L339-L350) | Adds the `VK_EXT_discard_rectangles` and `VK_NV_scissor_exclusive` requirements. |
| Test family registration | [vktShaderObjectApiTests.cpp#L353-L374](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L353-L374) | Builds the `api` group and adds the five leaves. |
| Category root registration | [vktShaderObjectTests.cpp#L47-L63](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Attaches the `api` test family to the `shader_object` test category. |
| Mustpass entries | [api.txt#L1-L5](../../../mustpass/main/vk-default/shader-object/api.txt#L1-L5) | The five registered leaves in the shader-object mustpass file. |
| Mustpass inclusion and exclusion | [main.txt](../../../mustpass/main/src/main.txt), [excluded-tests.txt](../../../mustpass/main/src/excluded-tests.txt) | The `dEQP-VK.*` wildcard includes this test family; only `shader_object.performance` is excluded. |
