## Overview

**Core question:** Does `VkDeviceObjectReservationCreateInfo` provide the reservation capacity required by the Vulkan SC device and object-creation cases that use it?

- This page covers `sc.device_object_reservation`, implemented and registered in [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L756-L2072).
- The category tests three contracts: basic and chained reservation structures, selected maximum values and object request counts, and pipeline-pool capacities.
- The `vksc-default` mustpass registers 34 executable paths: 2 `basic`, 7 `max_values`, 22 `request_count`, and 3 `pipeline_pool_size` cases ([`sc.txt`](../../../mustpass/main/vksc-default/sc.txt#L107-L140)).
- The oracle is host-side Vulkan object creation and, for subprocess pipeline-pool cases, the returned `VkResult`; no case executes a shader or checks rendered or computed output.

## Background Knowledge

- `VkDeviceObjectReservationCreateInfo` is attached to `VkDeviceCreateInfo::pNext`. Its request-count members reserve numbers of Vulkan objects, while its maximum-value members describe limits such as image-view mip levels, array layers, or queries per pool. These are different contracts: creating five objects is not the same operation as creating one object with a five-level or five-layer property.
- A `pNext` chain can contain multiple reservation structures. The implementation must account for the aggregate chain, not just one structure. This matters to the chained-memory case described later.
- Vulkan SC pipeline capacity is expressed with `VkPipelinePoolSize`, which pairs a byte size with a pipeline-entry count. The pipeline cases therefore validate creation results under deliberately different capacity declarations rather than validating shader output.

## Registration Hierarchy

```text
sc.device_object_reservation
├── basic
├── limits
└── pipeline_pool_size
```

`limits` contains the `max_values` and `request_count` intermediate nodes. Their registered leaves are enumerated in the parameter section and in the registration table ([`createDeviceObjectReservationTests`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1948-L2072)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Basic reservation | `create_device`, `multiple_device_object_reservation` | Exercises the common device path and aggregation across chained reservation structures. | [`DeviceObjectReservationInstance`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L783-L887) |
| Maximum values | `descriptor_set_layout_binding_limit`, `max_imageview_miplevels`, `max_imageview_arraylayers`, `max_layeredimageview_miplevels`, `max_occlusion_queries_per_pool`, `max_pipelinestatistics_queries_per_pool`, `max_timestamp_queries_per_pool` | Sets one selected maximum and creates the corresponding descriptor layout, image, or query pool. | [`VerifyMaxValues::createTestDevice`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L899-L958), [`VerifyMaxValues::performTest`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L960-L1115) |
| Request counts | `semaphore`, `command_buffer`, `fence`, `device_memory`, `buffer`, `image`, `event`, `query_pool`, `buffer_view`, `image_view`, `layered_image_view`, `pipeline_layout`, `render_pass`, `graphics_pipeline`, `compute_pipeline`, `descriptorset_layout`, `sampler`, `descriptor_pool`, `descriptorset`, `framebuffer`, `commandpool`, `samplerycbcrconversion` | Requests five instances of the selected type and supplies dependent reservations needed to construct it. | [`VerifyRequestCounts::createTestDevice`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1158-L1310), registration ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1996-L2042)) |
| Pipeline-pool capacity | `too_small_size`, `one_fits`, `multiple_fit` | Uses a 64-byte one-entry pool, the command-line pipeline-default size for one entry, or that size for 16 entries. | [`VerifyPipelinePoolSizes::createTestDevice`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1726-L1766) |
| Feature-sensitive cases | `max_pipelinestatistics_queries_per_pool`, `samplerycbcrconversion` | Requires `pipelineStatisticsQuery` or `samplerYcbcrConversion`, respectively. | [`checkSupportVerifyMaxValues`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L890-L895), [`checkSupportVerifyRequestCounts`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1117-L1122) |

The implementation uses `VERIFYMAXVALUES_OBJECT_COUNT = 5`, `VERIFYMAXVALUES_ARRAYLAYERS = 8`, and `VERIFYMAXVALUES_MIPLEVELS = 5`; these are source constants, not additional registered dimensions ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L38-L41)).

## Behavior Parameters

The primary behavioral axis is the registered family or intermediate node. Each value changes which reservation member is populated and which Vulkan creation sequence is used.

### `basic` — establish the reservation path

`create_device` sets `semaphoreRequestCount` to 2, creates the device, and creates two semaphores. `multiple_device_object_reservation` chains three reservation structures, each with `deviceMemoryRequestCount = 2`, and then allocates six 128-byte memory objects. The six allocations test aggregation across the chain rather than the capacity of one structure ([`MultipleReservation`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L847-L887)).

### `max_values` — exercise selected resource maxima

Each leaf sets one maximum and creates a resource at the corresponding boundary:

- `descriptor_set_layout_binding_limit` sets the limit to 6, reserves five descriptor-set-layout objects, and creates a layout with binding number 5 ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L911-L917), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L969-L989)).
- `max_imageview_miplevels` uses five mip levels and a `32 x 32 x 1` `VK_FORMAT_R8_UNORM` image; `max_imageview_arraylayers` uses eight array layers on a `16 x 16 x 1` image. `max_layeredimageview_miplevels` combines five mip levels with eight layers ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L918-L935), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L991-L1070)).
- The three query leaves create one query pool with five queries: occlusion, pipeline-statistics, or timestamp. The pipeline-statistics case enables `pipelineStatisticsQuery` before device creation ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L936-L951), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1072-L1110)).

### `request_count` — exercise object-count fields

Every registered request-count leaf sets the selected request count to five. Dependencies are reserved explicitly: command buffers use a command pool; views use backing resources and memory; framebuffers use an image, memory, view, render pass, and attachment description; descriptor sets use a layout and pool; and graphics or compute pipelines use their layout and pipeline-pool dependencies ([`VerifyRequestCounts::createTestDevice`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1158-L1310)).

The creation phase covers semaphores, command buffers, fences, memory, buffers, images, events, query pools, views, pipeline layouts, render passes, pipelines, descriptor objects, framebuffers, command pools, and sampler YCbCr conversions. Several cases release half or all of a vector and create again when the corresponding Vulkan SC recycling property is enabled. This tests reuse as well as first allocation ([`VerifyRequestCounts::performTest`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1313-L1715)).

`samplerycbcrconversion` chains and enables `samplerYcbcrConversion`; it selects a supported YCbCr format before creating conversions. Its support callback skips the case when the feature is unavailable ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1117-L1122), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L696-L753)).

### `pipeline_pool_size` — distinguish capacity outcomes

All three leaves construct the same minimal graphics-pipeline description and reserve one layout, render pass, subpass description, and attachment description. `too_small_size` supplies a 64-byte pool entry for one pipeline; `one_fits` supplies the command-line pipeline-default size for one; `multiple_fit` supplies that size for 16 ([`VerifyPipelinePoolSizes::createTestDevice`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1726-L1766)).

Normal mode creates the requested number of pipelines through CTS helpers. In subprocess mode, the test calls `vkCreateGraphicsPipelines` directly, records results, destroys successful pipelines, and repeats the cycle according to `recyclePipelineMemory`. The final recorded result must be `VK_ERROR_OUT_OF_POOL_MEMORY` for `too_small_size` and `VK_SUCCESS` for both fitting cases ([`VerifyPipelinePoolSizes::performTest`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1879-L1919), [`verifyTestResults`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1922-L1941)).

## Shader Analysis

No shader participates. The test validates reserved object counts and pipeline-pool behavior through object creation and result codes; shader output is never executed or checked.

## Runtime Execution and Result Checking

- The base iterator creates a custom instance, selects the physical device, prepares a one-queue `VkDeviceCreateInfo`, copies the default reservation structure, attaches it through `pNext`, and invokes the selected test implementation ([`DeviceObjectReservationInstance::iterate`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L783-L824)).
- The selected `createTestDevice` populates reservation fields and may prepend a feature structure to the chain. `performTest` then creates the requested objects using CTS wrappers or direct Vulkan calls.
- Ordinary creation failures are surfaced by `VK_CHECK` or `TCU_CHECK`. The iterator waits for queue 0 with `queueWaitIdle`, then invokes `verifyTestResults`; the base verifier returns true after successful setup and creation ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L816-L845)).
- Pipeline-pool subprocess mode retains each direct result, stops at the first non-success result after cleaning up successful pipelines, and compares the last result with the expected result ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1887-L1941)).

A pass shows that the selected reservation structure was accepted and that the selected object-creation operations met their checks. It does not establish behavior for unregistered object types, untested counts or pool sizes, or shader execution output.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `basic.create_device` | Device creation or one of the two semaphore creations failed. |
| `basic.multiple_device_object_reservation` | Chained reservation aggregation, memory reservation, or memory allocation failed. |
| `max_values.*` | The selected maximum or its dependent resource creation failed; feature or device support may be involved. |
| `request_count.*` | The selected object or a required dependency could not be created under the requested count. |
| `pipeline_pool_size.too_small_size` | The final subprocess result was not `VK_ERROR_OUT_OF_POOL_MEMORY`. |
| `pipeline_pool_size.one_fits`, `pipeline_pool_size.multiple_fit` | The final subprocess result was not `VK_SUCCESS`. |

### Cause Analysis

#### Reservation accounting or dependency setup

**Possible failure symptoms:** A device, dependency, selected object, or pipeline creation call fails. The first failing operation may be a prerequisite rather than the object named by the leaf.

**Possible implementation causes:** The implementation may have applied the wrong reservation member, failed to aggregate chained structures, or failed to account for dependencies such as image memory, framebuffer attachments, descriptor pools, or pipeline layouts. The source localizes the first failing API operation but does not identify the implementation's internal accounting step.

#### Feature or resource support

**Possible failure symptoms:** A feature-sensitive case is skipped, or a supported case fails while creating its feature-dependent resource.

**Possible implementation causes:** `pipelineStatisticsQuery` and `samplerYcbcrConversion` are explicitly checked and enabled where required. For a supported device, further diagnosis requires the feature exposure, format or limit support, and the first failing operation; the test alone does not attribute the failure to one driver subsystem ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L890-L895), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1117-L1122)).

#### Pipeline-pool result

**Possible failure symptoms:** `too_small_size` does not end with `VK_ERROR_OUT_OF_POOL_MEMORY`, or a fitting case does not end with `VK_SUCCESS`.

**Possible implementation causes:** Pool sizing, pipeline-entry accounting, pipeline construction, or recycling behavior may be implicated. The source compares the final `VkResult`; it does not measure byte consumption independently ([`VerifyPipelinePoolSizes`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1844-L1941)).

## Case Pruning

### Requirement-based pruning

- `max_pipelinestatistics_queries_per_pool` is not supported when `pipelineStatisticsQuery` is unavailable ([`checkSupportVerifyMaxValues`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L890-L895)).
- `samplerycbcrconversion` is not supported when `samplerYcbcrConversion` is unavailable ([`checkSupportVerifyRequestCounts`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1117-L1122)).
- The selected image, format, query, and feature operations remain subject to ordinary Vulkan support; a support skip is distinct from a reservation failure.

### Design-based pruning

The source declares but does not register `surface`, `swapchain`, or `display_mode`; their execution branches are also commented out ([`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L61-L87), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1705-L1710), [`vktDeviceObjectReservationTests.cpp`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L2023-L2025)). They are therefore outside the 34-case default scope. Shader programs are likewise supporting pipeline inputs, not an independent shader-test dimension.

## Key Takeaways

- The category exercises `VkDeviceObjectReservationCreateInfo` through real Vulkan SC device and object creation.
- `max_values` targets selected resource properties; `request_count` targets five instances of each registered object type and supplies construction dependencies.
- The chained basic case verifies that three reservation structures together support six memory allocations.
- Pipeline-pool cases use an explicit result contract: the deliberately undersized entry must fail with `VK_ERROR_OUT_OF_POOL_MEMORY`, while fitting entries must succeed in subprocess mode.
- Shaders make pipeline construction possible but are never executed for validation.
- A failure identifies the selected setup and first observable API failure, not necessarily the implementation's sole internal cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Base iteration and reservation attachment | [`DeviceObjectReservationInstance::iterate`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L783-L824) | Establishes device setup, execution order, queue wait, and pass path. |
| Basic and chained reservations | [`DeviceObjectReservationInstance`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L826-L887) | Shows semaphore setup and aggregate memory reservation across three structures. |
| Maximum-value cases | [`VerifyMaxValues`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L899-L1115) | Maps maxima to descriptor, image, and query-pool creation. |
| Request-count cases | [`VerifyRequestCounts`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1158-L1715) | Defines dependencies, object creation, and recycling. |
| Pipeline-pool cases | [`VerifyPipelinePoolSizes`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1717-L1944) | Defines pool sizes, subprocess calls, cleanup, and result checks. |
| Registration | [`createDeviceObjectReservationTests`](../../../modules/vulkan/sc/vktDeviceObjectReservationTests.cpp#L1948-L2072) | Defines the exact category hierarchy and leaves. |
| Default coverage | [`sc.txt`](../../../mustpass/main/vksc-default/sc.txt#L107-L140) | Confirms the 34 default executable paths. |
