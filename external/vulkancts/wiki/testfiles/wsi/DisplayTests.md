## Overview

**Core question:** Do the direct-display APIs enumerate, describe, create, and query display objects without violating their result, count, structure, or output-memory contracts?

- `vktWsiDisplayTests.cpp` implements the 12 test case leaves in the `wsi.display` test family. Each leaf selects one API operation through the `DisplayIndexTest` dispatch table.
- The family covers `VK_KHR_display`, the extensible query forms from `VK_KHR_get_display_properties2`, and one display-surface counter query from `VK_EXT_display_surface_counter`.
- The tests inspect display, plane, mode, capability, surface, and counter data. Enumeration cases vary the caller-provided array capacity and place a canary after the expected output range to detect excess writes.
- This family performs no rendering. It checks `VkResult` values, returned counts and handles, structure fields, and agreement between related capability queries.

## Background Knowledge

For the shared concept direct-display objects, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- A display mode supplies a visible extent and refresh rate. A display plane is a scanout layer that can target supported displays, use a selected mode, and expose source, destination, and alpha capabilities.
- Vulkan enumeration commands first report an available count when the output pointer is `NULL`. On a data call, the application supplies an array capacity through the count pointer. The command writes at most that many elements, updates the count to the number written, and may return `VK_INCOMPLETE` if the array cannot hold all available entries. See [display enumeration and its array-size rules](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1321-L1347).
- The `VK_KHR_get_display_properties2` commands wrap the original property structures in extensible structures. They retain the original query semantics while allowing information through `pNext` chains. See [the display properties2 description](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1402-L1437).

## Registration Hierarchy

```text
wsi.display
├── get_display_properties
├── get_display_plane_properties
├── get_display_plane_supported_displays
├── get_display_mode_properties
├── create_display_mode
├── get_display_plane_capabilities
├── create_display_plane_surface
├── surface_counters
├── get_display_properties2
├── get_display_plane_properties2
├── get_display_mode_properties2
└── get_display_plane_capabilities2
```

[`createDisplayCoverageTests`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L2199-L2228) registers these names. The WSI dispatcher attaches the family at `wsi.display` in [`createWsiTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91). All 12 paths appear in the default Vulkan mustpass list at [`external/vulkancts/mustpass/main/vk-default/wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L11503-L11514).

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `get_display_properties`, `get_display_plane_properties`, `get_display_plane_supported_displays`, `get_display_mode_properties`, `create_display_mode`, `get_display_plane_capabilities`, `create_display_plane_surface`, `surface_counters`, `get_display_properties2`, `get_display_plane_properties2`, `get_display_mode_properties2`, `get_display_plane_capabilities2` | Selects the API behavior and validation rules. One `DisplayIndexTest` value maps to each registered leaf. | [`DisplayIndexTest` and `iterate`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L65-L80), [`iterate`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L276-L311) |
| Query form | Original `VK_KHR_display` structure or extensible `*2` structure | The four `*2` leaves repeat the corresponding property or capability query while checking the wrapper's `sType` and `pNext`. | [`VK_KHR_get_display_properties2` dispatch and requirement](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L247-L261) |
| Enumeration capacity | `0` through the tested count plus one; display and plane loops cap their tested count at 16 | Exercises returned count, `VK_SUCCESS` versus `VK_INCOMPLETE`, initialized output, and the no-write-past-capacity rule. | [`get_display_properties` capacity loop](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L770-L891), [`get_display_plane_properties` capacity loop](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L903-L1009) |
| Physical topology | Runtime-provided displays, planes, supported display-plane pairs, and built-in modes | Determines which handles and mode-plane combinations the capability and surface cases can query. | [`getDisplays`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L319-L377), [`getDisplaysForPlane`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L388-L434), [`getDisplayModeProperties`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L445-L491) |
| Surface operation | Create only or create and query counters | Both paths find a full-display plane with opaque alpha support. `surface_counters` also compares the EXT and KHR capability results and checks the counter mask. | [`SurfaceTestKind`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L200-L207), [`testDisplaySurface`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1494-L1688) |

The family has no `wsiType` parameter and no generated shader, image, or rendering matrix.

## Behavior Parameters

The primary behavioral axis is the **test case leaf**. Each leaf selects one display query, creation operation, or surface check.

### `get_display_properties`: enumerate displays

The test queries the display count, then repeats `vkGetPhysicalDeviceDisplayPropertiesKHR` with different array capacities. It checks the returned count and result, validates handles, Boolean fields, transform bits, and nonzero physical resolution, rejects duplicate handles, and verifies that the canary after the expected range remains unchanged.

### `get_display_plane_properties`: enumerate display planes

The test builds the valid display-handle set before varying the plane-property array capacity. Every returned plane must have a stack index below the reported plane count and a `currentDisplay` that is either `VK_NULL_HANDLE` or a known display handle. A canary checks the output bound.

### `get_display_plane_supported_displays`: enumerate each plane's displays

For each tested plane, the test varies the capacity passed to `vkGetDisplayPlaneSupportedDisplaysKHR`. It checks the count and completion result, accepts null entries where the source does, rejects non-null handles outside the known display set, and detects writes after the expected output range.

### `get_display_mode_properties`: enumerate built-in modes

For every display, the test varies the capacity passed to `vkGetDisplayModePropertiesKHR`. Returned mode handles must be non-null, count and result behavior must match the capacity, and the canary mode handle must survive. Long capacity sequences retain the first three and last three requested sizes.

### `create_display_mode`: reject invalid parameters and create a valid mode

The test copies the first built-in mode's parameters. Three negative calls set the refresh rate, visible width, or visible height to zero and expect `VK_ERROR_INITIALIZATION_FAILED` with a null output handle. Those zero-valued structures violate the valid-usage requirements for `VkDisplayModeParametersKHR`, so the demanded result is not a valid conformance oracle; this remains an unresolved test-source defect. The test then creates the unchanged mode parameters, expects a valid handle, and verifies that the built-in mode enumeration count did not change.

### `get_display_plane_capabilities`: validate mode-plane limits

The test visits supported display, mode, and plane combinations and calls `vkGetDisplayPlaneCapabilitiesKHR`. It requires at least one recognized alpha bit, rejects unknown alpha bits, requires nonnegative source offsets, and checks that each minimum offset or extent does not exceed its maximum. The specification defines these fields as the limits for a selected mode and plane; destination offsets may be negative, so the source does not impose a nonnegative destination check. See [display plane capability semantics](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2018-L2108).

### `create_display_plane_surface`: create a usable display surface

The test searches for a display-mode-plane combination whose minimum destination extent matches the mode's visible region and whose alpha modes include `VK_DISPLAY_PLANE_ALPHA_OPAQUE_BIT_KHR`. It creates a display plane surface with that extent, the plane's current stack index, identity transform, and opaque alpha, then requires `VK_SUCCESS` and a non-null surface handle. The selection does not verify that the display advertises identity-transform support before hard-coding that transform, so the call can violate `VUID-VkDisplaySurfaceCreateInfoKHR-transform-06740`; this remains an unresolved test-source defect.

### `surface_counters`: compare surface capability forms

This leaf uses the same surface selection and creation path. It requires `VK_EXT_display_surface_counter`, compares the common fields returned through `VkSurfaceCapabilities2EXT` and `VkSurfaceCapabilitiesKHR`, and rejects any set bit in `supportedSurfaceCounters` other than the vertical-blank counter bit. The specification defines that bit as a counter incremented for each vertical blanking period. See [display surface counter semantics](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L3705-L3784).

### `get_display_properties2`: enumerate extensible display properties

This leaf repeats `get_display_properties` with `vkGetPhysicalDeviceDisplayProperties2KHR`. In addition to the original property checks, it requires each wrapper to retain `VK_STRUCTURE_TYPE_DISPLAY_PROPERTIES_2_KHR` and a null `pNext`.

### `get_display_plane_properties2`: enumerate extensible plane properties

This leaf repeats the plane-property count, capacity, handle, stack-index, and canary checks with `VkDisplayPlaneProperties2KHR`. It also requires the wrapper's `sType` and `pNext` to remain unchanged.

### `get_display_mode_properties2`: enumerate extensible mode properties

This leaf repeats the mode enumeration and output-bound checks with `VkDisplayModeProperties2KHR`. Each wrapper must retain its initialized `sType` and null `pNext`, and each nested mode handle must be non-null.

### `get_display_plane_capabilities2`: validate extensible plane capabilities

The test supplies `VkDisplayPlaneInfo2KHR` for each selected mode and plane, then receives `VkDisplayPlaneCapabilities2KHR`. It applies the original capability field checks to the nested structure and also checks the output wrapper's `sType` and `pNext`.

## Shader Analysis

This test family has no shader code or device-side rendering. All checks operate on API results and host-visible output structures, so shader and SPIR-V analysis do not apply.

## Runtime Execution and Result Checking

- The `DisplayCoverageTestInstance` constructor requires `VK_KHR_display` for every leaf. It also requires `VK_KHR_get_display_properties2` for the four `*2` leaves. Missing instance extensions produce `NotSupportedError`.
- `iterate()` dispatches one `DisplayIndexTest` value to one test method. Most enumeration leaves first make a count-only call, allocate initialized storage plus one canary entry, and then repeat the data call across selected capacities.
- Enumeration checks compare the returned count with `min(requested, reported)`. They expect `VK_SUCCESS` when the requested capacity can hold the reported entries and `VK_INCOMPLETE` when it cannot. The canary must remain unchanged after every call.
- Property checks use invalid initial values so unchanged or unknown fields fail. The `*2` leaves also initialize `sType` and `pNext`, then check that the query preserved them while filling the nested output structure.
- Capability and surface leaves derive their work from the runtime display topology. They enumerate displays, display-supported planes, and modes before querying capabilities or creating a surface.
- `testDisplaySurface` destroys every surface it creates. The counter leaf records a capability mismatch or invalid counter bit and returns failure after completing the available combinations.
- A leaf returns pass only after all applicable return-code, count, memory-bound, handle, and field checks succeed.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `get_display_properties` | Enumeration protocol or output-bound failure; invalid or duplicate display data. |
| `get_display_plane_properties` | Enumeration protocol or output-bound failure; inconsistent plane topology data. |
| `get_display_plane_supported_displays` | Enumeration protocol or output-bound failure; a plane reports an unknown display handle. |
| `get_display_mode_properties` | Enumeration protocol or output-bound failure; invalid built-in mode handles. |
| `create_display_mode` | Failure to create a valid copied mode or built-in mode list mutation. The zero-parameter error-result checks use invalid input and do not provide a valid conformance diagnosis. |
| `get_display_plane_capabilities` | Invalid alpha flags or inconsistent capability ranges for a supported mode-plane pair. |
| `create_display_plane_surface` | Failure to create a surface from the selected display configuration, or invalid test setup when identity transform is not advertised. |
| `surface_counters` | Display surface capability mismatch or an unrecognized surface-counter bit. |
| `get_display_properties2` | Extensible-structure handling failure plus any display enumeration or property failure. |
| `get_display_plane_properties2` | Extensible-structure handling failure plus any plane enumeration or topology failure. |
| `get_display_mode_properties2` | Extensible-structure handling failure plus any mode enumeration failure. |
| `get_display_plane_capabilities2` | Extensible-structure handling failure or invalid nested capability data. |

### Cause Analysis

#### Enumeration protocol and output bounds

**Possible failure symptoms:** A query returns the wrong element count, returns `VK_SUCCESS` instead of `VK_INCOMPLETE` for an undersized array, returns `VK_INCOMPLETE` for sufficient capacity, or changes the canary after the expected output range.

**Possible implementation causes:** The implementation may mishandle the Vulkan two-call enumeration convention, report a count that disagrees with the number written, choose the wrong completion result, or write more elements than the application supplied. The specification states the count and partial-array rules for display, supported-display, and mode enumeration; the source applies the same bounded-output check to each applicable command.

#### Returned display topology and property data

**Possible failure symptoms:** A display or mode handle remains null, display handles repeat, a plane names an unknown display, a stack index exceeds the plane range, or a checked property contains an invalid Boolean or flag value.

**Possible implementation causes:** The implementation may expose inconsistent display, plane, and mode objects across related queries or fail to populate required output fields. A precise lower-level cause requires investigation of the implementation's display enumeration and topology mapping. The nonzero physical-resolution check is an extra CTS application-safety check identified as outside the specification in the source.

#### Display mode creation

**Possible failure symptoms:** A zero refresh rate or visible extent does not produce `VK_ERROR_INITIALIZATION_FAILED`, the failed call writes a mode handle, a valid copied mode cannot be created, or the built-in mode count changes after creation.

**Possible implementation causes:** No implementation defect can be inferred from the three zero-parameter calls because they violate valid usage. For the valid copied parameters, the implementation may reject a mode it already reports as supported, mishandle the output handle, or include application-created modes in the built-in mode enumeration. The specification requires mode dimensions and refresh rate to be greater than zero and states that compatible creation parameters create an additional mode. See [display mode parameter and creation rules](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1930-L2015).

#### Plane capability data

**Possible failure symptoms:** The result contains no recognized alpha mode, contains unknown alpha bits, reports a negative source offset, or reports a minimum greater than its matching maximum.

**Possible implementation causes:** The implementation may return invalid capability limits or alpha support for the selected mode-plane pair. The specification requires at least one valid alpha bit and ordered source position ranges. It permits negative destination offsets, which the test preserves.

#### Display surface creation

**Possible failure symptoms:** `vkCreateDisplayPlaneSurfaceKHR` returns an unexpected result or a null handle for the selected full-display, opaque-alpha configuration.

**Possible implementation causes:** If identity transform is advertised, the implementation may reject a configuration assembled from its own display, mode, plane, stack, alpha, and extent query results, or fail to create the `VkSurfaceKHR` object. If identity transform is not advertised, the source itself supplies invalid input and no implementation defect can be inferred. See [display surface creation and valid usage](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2237-L2349).

#### Surface capability and counter data

**Possible failure symptoms:** The common KHR and EXT surface capability fields differ, or `supportedSurfaceCounters` contains a bit other than the recognized vertical-blank counter.

**Possible implementation causes:** The implementation may return inconsistent base capabilities through the two query forms or expose an undefined counter bit. The source compares the shared fields with `sameSurfaceCapabilities` and accepts only the counter bit defined by `VK_EXT_display_surface_counter`.

#### Extensible-structure handling

**Possible failure symptoms:** A `*2` query changes the initialized `sType` or `pNext`, fails to populate the nested original structure, or returns data inconsistent with the original query's field rules.

**Possible implementation causes:** The implementation may write the wrapper header while filling an output structure, misinterpret the `pNext` chain, or fail to route the extensible query to the original property or capability logic. The specification defines each `*2` command as the corresponding original query with extensible input or output structures.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_KHR_display`. The four `*2` leaves also require `VK_KHR_get_display_properties2`, and `surface_counters` requires `VK_EXT_display_surface_counter`.
- Tests that need display objects report `NotSupportedError` when no displays are available. Plane-dependent paths cannot run without reported planes.
- The two surface leaves need at least one mode-plane combination that targets the display, has a minimum destination extent equal to the mode's visible region, and supports opaque alpha. If the search finds none, the leaf reports `NotSupportedError`.

### Design-based pruning

- Display and plane enumeration loops test at most 16 reported objects. The cap bounds runtime without changing the registered leaves.
- Mode-property capacity loops use every requested size for short lists. For longer lists, `nextTestNumber()` keeps the first three and last three sizes and skips the middle values.
- Capability and surface paths skip planes that report no supported displays and combinations that do not satisfy the surface selection conditions.

## Key Takeaways

- The enumeration leaves check the full caller contract: result code, number written, output contents, and the array boundary.
- The topology checks connect related APIs. Plane display handles must come from display enumeration, mode handles must be valid, and capability queries use supported display-mode-plane combinations.
- The valid mode-creation path and most surface parameters use values derived from queried support. The source's zero-valued mode calls and unchecked identity transform are unresolved validity defects, so failures specific to those inputs do not establish implementation nonconformance.
- The four `*2` leaves add wrapper integrity checks to the original field validation. `surface_counters` adds cross-query consistency and counter-bit validation. See `Failure Meaning` for the symptom-to-cause mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test identifiers and dispatch | [`DisplayIndexTest` and `iterate`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L65-L80) | Maps all 12 leaves to their test methods. |
| Extension requirements | [`DisplayCoverageTestInstance` constructor](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L234-L268) | Defines the common and `*2` extension gates. |
| Shared enumeration helpers | [`getDisplays`, `getDisplaysForPlane`, and mode helpers](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L319-L647) | Supplies runtime display topology to capability and surface tests. |
| Shared field validators | [`validateDisplayProperties` through `validateDisplayModeProperties`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L657-L760) | Defines the common original and `*2` property checks. |
| Original enumeration leaves | [`get_display_properties` through `get_display_mode_properties`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L770-L1217) | Implements count, capacity, handle, canary, and result validation. |
| Display mode creation | [`testCreateDisplayModeKHR`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1226-L1330) | Covers invalid and valid creation plus built-in mode count stability. |
| Original plane capabilities | [`testGetDisplayPlaneCapabilitiesKHR`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1340-L1472) | Checks alpha flags and capability range ordering. |
| Display surface and counters | [`testDisplaySurface`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1494-L1688) | Selects and creates a surface configuration, then checks counters for the counter leaf. |
| Extensible display and plane queries | [`get_display_properties2` and `get_display_plane_properties2`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1698-L1942) | Repeats enumeration checks with wrapper integrity validation. |
| Extensible capability and mode queries | [`get_display_plane_capabilities2` and `get_display_mode_properties2`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1951-L2163) | Checks nested capabilities or modes and their wrapper headers. |
| Registration | [`createDisplayCoverageTests`](../../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L2199-L2228) | Provides the exact test case leaf names. |
| WSI dispatcher | [`createWsiTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91) | Places this test family at `wsi.display`. |
| Vulkan display specification | [`Presenting Directly to Display Devices`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1299-L1400) | Defines direct-display objects and base display properties. |
| Mustpass coverage | [`vk-default/wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L11503-L11514) | Lists all 12 registered paths in the default Vulkan mustpass set. |
