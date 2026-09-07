## Overview

**Core question:** When an array query receives excess output capacity, does it report a bounded written count and populate the entries it claims to return?

- [`vktApiArrayTests.cpp`](../../../modules/vulkan/api/vktApiArrayTests.cpp#L554-L602) implements `api.array.oversized_array`.
- Core and extension queries share a count-query, oversized-allocation, poison, and data-query sequence. WSI variants first create native surface and swapchain resources.
- Count growth can produce a quality warning. The test does not compare every property against an independent semantic reference or inspect all unused output slots.

## Background Knowledge

- Many Vulkan enumeration commands first return a count when the output pointer is null. A second call receives capacity through the count pointer and returns the number of elements written.
- The available count can change between calls. Allocating extra capacity avoids assuming that two queries observe an identical inventory.
- A poison pattern initializes output storage to a recognizable value. Detecting unchanged entries is different from checking guard bytes beyond the output array.

## Registration Hierarchy

```text
api.array.oversized_array
├── core
└── wsi
```

The [factory](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1148-L1214) registers one core leaf per `ArrayFunction` and WSI leaves beneath platform names. The current [mustpass](../../../mustpass/main/vk-default/api.txt) contains 82 leaves under `api.array`. Display-specific queries are generated only for `direct` and `direct_drm`; other WSI queries are generated for each enumerated WSI type. The [API dispatcher](../../../modules/vulkan/api/vktApiTests.cpp#L142-L148) excludes the family from Vulkan SC.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Query area | `core`, `wsi` | Selects ordinary query setup or native display/window/surface/swapchain setup. | [group construction](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1198-L1206) |
| Core query | Physical devices, instance layers/extensions, device extensions, pipeline cache data/binaries, device groups, calibrated time domains, cooperative matrices, executable properties/statistics/internal representations, tool properties, fragment shading rates | Selects the command adapter and output element type. | [enum](../../../modules/vulkan/api/vktApiArrayTests.cpp#L48-L66), [exact leaf names](../../../modules/vulkan/api/vktApiArrayTests.cpp#L977-L1015) |
| WSI query | Display/plane/mode queries, surface formats/present modes, swapchain images, present rectangles, and selected `2` query forms | Selects the WSI adapter, subject to the dispatch caveat below. | [enum](../../../modules/vulkan/api/vktApiArrayTests.cpp#L68-L85), [names](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1017-L1053) |
| Output capacity | Initial count multiplied by 64; pipeline-cache byte size plus 512 | Provides excess capacity rather than truncating the returned array. | [capacity helpers](../../../modules/vulkan/api/vktApiArrayTests.cpp#L485-L495) |
| Poison initialization | `0xDE`, with valid `sType` and null `pNext` for applicable structures | Makes wholly unwritten returned entries detectable. Internal-representation records also use null `pData` and zero `dataSize`. | [poison helpers](../../../modules/vulkan/api/vktApiArrayTests.cpp#L401-L483) |

## Behavior Parameters

The query adapter is the primary behavioral choice. Most adapters share the same check, but byte arrays, allocated handles, and WSI setup need separate interpretation.

### `core`: enumeration and extension-query arrays

The test obtains a baseline count, allocates excess capacity, initializes every entry, and repeats the query. For ordinary element types it fails when any claimed returned entry is still byte-identical to its initial poison value. This is a written-entry check, not a field-by-field validity check. Pipeline executable statistics and internal representations target executable index zero and skip when no executable is available ([dispatch](../../../modules/vulkan/api/vktApiArrayTests.cpp#L604-L734)).

### `get_pipeline_cache_data`: byte-buffer special case

The cache-data adapter uses `size_t` byte counts. Since a valid byte can naturally equal `0xDE`, its specialization does not poison-check bytes within the original queried size. It only checks the additional claimed range when the second count exceeds the original count ([byte validation](../../../modules/vulkan/api/vktApiArrayTests.cpp#L514-L532)).

### `create_pipeline_binaries`: returned handle ownership

This adapter passes capacity through `VkPipelineBinaryHandlesInfoKHR`, creates binaries for a prepared graphics pipeline, and copies the returned binary count back into the shared checker. On the normal completion path it destroys the returned binary handles ([adapter](../../../modules/vulkan/api/vktApiArrayTests.cpp#L147-L166), [cleanup](../../../modules/vulkan/api/vktApiArrayTests.cpp#L542-L552)).

### `wsi`: surface and display query arrays

Every WSI case constructs native objects, a surface, and a swapchain before dispatching its selected query. Even display-property cases therefore depend on successful swapchain setup. Display-plane-supported-displays targets plane zero and skips if no planes are exposed ([WSI execution](../../../modules/vulkan/api/vktApiArrayTests.cpp#L874-L975)).

The current `get_physical_device_display_properties2` leaf does not call the command named by the leaf: its dispatch branch queries swapchain images through `oversizedArrayTestImpl<VkSwapchainKHR, VkImage>` ([branch](../../../modules/vulkan/api/vktApiArrayTests.cpp#L945-L948)). This is an unresolved source dispatch defect; the documented leaf name must not be treated as proof of display-properties2 coverage.

## Shader Analysis

Shaders are pipeline-creation fixtures, not an executed workload in this family. The pipeline-binary and executable-query cases compile a pass-through vertex shader and a constant-color fragment shader to obtain a valid pipeline. No draw or dispatch is recorded and shader output is not checked ([programs](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1126-L1146)). No representative shader walkthrough is needed for this host-side array contract.

## Runtime Execution and Result Checking

- Query the initial count with a null array; skip when it is zero.
- Allocate and poison the oversized array, then query with its capacity as the input count.
- Check the returned `VkResult` and fail if the reported written count exceeds capacity.
- Apply the ordinary or cache-byte poison checker to the claimed returned range.
- If the second count exceeds the first, emit a quality warning because inventory growth is possible; it is not automatically a hard conformance failure.
- Clean up returned binary handles on the normal path and return pass. The checker does not verify that entries after the returned count remain unchanged, nor does it install a separate beyond-capacity guard ([shared checker](../../../modules/vulkan/api/vktApiArrayTests.cpp#L554-L602)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Ordinary array adapter | Returned count exceeds capacity, an advertised returned entry remains entirely poisoned, or a query returns an unexpected error. |
| Pipeline cache data | Byte-count handling or an extra claimed byte range disagrees with the byte-specialized checker. |
| Pipeline binaries | Binary creation/count handling or returned-handle population fails. |
| WSI adapter | Native/surface/swapchain setup fails, or the selected query violates the shared count/population checks. |

### Cause Analysis

#### Count and population disagree

**Possible failure symptoms:** A query reports more entries than supplied capacity or an entry below the written count remains wholly poisoned.

**Possible implementation causes:** The implementation may fail to update the count or leave returned elements unwritten. A poison match is not a complete semantic oracle, especially for byte data. This test does not establish that all out-of-range writes would be detected.

#### Count grows between queries

**Possible failure symptoms:** A quality warning reports that the written count may not have been updated.

**Possible implementation causes:** The count may legitimately have grown between calls, or the implementation may have left the supplied capacity in the output count. The shared checker deliberately reports a warning after its stronger checks rather than treating growth alone as failure.

## Case Pruning

### Requirement-based pruning

- Core adapters request their corresponding extensions, including pipeline binary/maintenance5, pipeline executable properties/maintenance5, device group, calibrated timestamps, cooperative matrix, tooling info, or fragment shading rate as applicable ([core support](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1055-L1097)).
- All WSI cases require surface, the selected platform-surface extension, and swapchain functionality. Selected commands add device group, surface capabilities2, display properties2, or full-screen-exclusive requirements ([WSI support](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1099-L1124)).
- Zero initial count, missing executable zero, unavailable native objects, or unsupported swapchain transfer-destination usage can prevent execution.

### Design-based pruning

Only oversized arrays are registered; there is no undersized-array matrix. Display-specific leaves are restricted to direct-display WSI types. Internal-representation queries request metadata with null data pointers rather than fetching representation payloads.

## Key Takeaways

- The shared test checks returned count and claimed population under excess capacity.
- Cache bytes use a weaker poison check than ordinary structures or handles.
- WSI setup and the display-properties2 dispatch defect limit what a named leaf proves.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Array checker | [oversizedArrayTestImpl](../../../modules/vulkan/api/vktApiArrayTests.cpp#L554-L602) | Defines hard failures, warning, and cleanup order. |
| Output validation | [validateArray overloads](../../../modules/vulkan/api/vktApiArrayTests.cpp#L497-L532) | Distinguishes ordinary entries from cache bytes. |
| Core and WSI dispatch | [core](../../../modules/vulkan/api/vktApiArrayTests.cpp#L604-L734), [WSI](../../../modules/vulkan/api/vktApiArrayTests.cpp#L874-L975) | Resolves each named adapter to actual calls. |
| Registration | [factories](../../../modules/vulkan/api/vktApiArrayTests.cpp#L1148-L1214) | Builds core, WSI, and platform branches. |
