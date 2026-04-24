# api

## Overview

The [`api`](../../modules/vulkan/api/vktApiTests.cpp#L86) category is the main Vulkan API conformance bucket registered by [`createTests()`](../../modules/vulkan/api/vktApiTests.cpp#L146) and populated by [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L86). In the inspected sources, this top-level category mixes foundational object-lifetime and buffer-contract coverage with a large copy/blit subtree and many additional API-focused subgroups.

This document is intentionally **partial**. It summarizes only the Level-3 API slices that are currently documented and/or explicitly inspected for this synthesis. The registration tree is grounded in [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L86), but claims about detailed test families, parameters, support gates, and verification methods are limited to the completed Level-3 documents linked below. Undocumented API subgroups are listed for navigational context only and should not be treated as covered by this summary.

## Registration Entry Point

The category is rooted in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L86), which adds the following observed top-level children in registration order:

```text
api
├── version_sanity_check
├── debug_utils
├── driver_properties
├── smoke                                  (not in Vulkan SC)
├── feature_info
├── device_drm_properties                  (not in Vulkan SC)
├── device_initialization
├── object_management
├── buffer
├── buffer_marker                          (not in Vulkan SC)
├── buffer_view
│   ├── create
│   └── access
├── command_buffers
├── copy_and_blit
├── ds_color_bit_copy
├── image_clearing
├── fill_and_update_buffer
├── descriptor_pool
├── null_handle
├── granularity_query
├── memory_commitment
├── external_memory                        (not in Vulkan SC)
├── maintenance3
├── descriptor_set
├── pipeline
├── memory_requirement_invariance
├── tooling_info                           (not in Vulkan SC)
├── format_properties_extended_khr         (not in Vulkan SC)
├── buffer_memory_requirements
├── image_compression_control              (not in Vulkan SC)
├── get_device_proc_addr                   (not in Vulkan SC)
├── maintenance6                           (not in Vulkan SC)
├── frame_boundary                         (not in Vulkan SC)
├── maintenance5                           (not in Vulkan SC)
├── fragment_shader_output                 (not in Vulkan SC)
├── maintenance7                           (not in Vulkan SC)
├── device_address_commands                (not in Vulkan SC)
├── extension_duplicates
└── renderpass_performance_counters_by_region_api (not in Vulkan SC)
```

Sources:
- top-level API group creation in [`createTests()`](../../modules/vulkan/api/vktApiTests.cpp#L146)
- child registration in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L90)
- nested `buffer_view` aggregator in [`createBufferViewTests()`](../../modules/vulkan/api/vktApiTests.cpp#L78)


## File Inventory

The inspected registration file includes many implementation headers, showing that the `api` category is a broad umbrella rather than one narrow feature area; see the include list in [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L27). For the currently synthesized partial state, the following files are the evidence-backed Level-3 anchors:

| File | Role | Notes |
|---|---|---|
| [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L1) | Registration | Top-level API registration tree and `buffer_view` sub-aggregation |
| [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1) | Implementation | Object creation/destruction, repeated creation, multithreading, allocation callbacks, and private-data coverage |
| [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L1) | Implementation | Buffer creation/allocation/binding coverage across usage and allocation modes |
| [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1) | Registration / dispatcher | Dispatches the large `copy_and_blit` subtree to many implementation files |
| [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1) | Implementation | Post-copy image usability coverage inside `copy_and_blit/core/use_after_copy` |

## Level-3 Documents Included in This Partial Synthesis

| Source file | Wiki document |
|---|---|
| [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L1) | [`vktApiBufferTests.md`](../testfiles/api/vktApiBufferTests.md) |
| [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L1) | [`vktApiObjectManagementTests.md`](../testfiles/api/vktApiObjectManagementTests.md) |
| [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L1) | [`vktApiCopiesAndBlittingTests.md`](../testfiles/api/vktApiCopiesAndBlittingTests.md) |
| [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1) | [`vktApiUseAfterCopyTests.md`](../testfiles/api/vktApiUseAfterCopyTests.md) |

No other API Level-3 documents are treated as synthesized here, even if additional markdown files already exist under [`testfiles/api/`](../testfiles/api/), because this task is limited to currently completed/inspected slices with evidence-backed claims.

## Subgroup Structure and Major Themes

### Foundational object and resource lifetime coverage

Early in the registration order, [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L100) adds [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiTests.cpp#L101) and then [`createBufferTests()`](../../modules/vulkan/api/vktApiTests.cpp#L102). In the currently completed Level-3 docs, these two files form the clearest foundational API slice.

From [`vktApiObjectManagementTests.md`](../testfiles/api/vktApiObjectManagementTests.md), the observed `object_management` subtree covers:
- single-object create/destroy smoke paths;
- repeated creation with unique versus shared resources;
- maximum concurrently live objects;
- several multithreaded construction patterns;
- host allocation callback accounting and OOM behavior on non-Vulkan-SC builds;
- private-data attachment persistence when [`VK_EXT_private_data`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L2658) style support is available.

That emphasis aligns with the Vulkan API test plan's object-management section in [`apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc#L134), which describes create/destroy, repeated allocation, concurrent creation, and freeing behavior as the core object-management goals.

From [`vktApiBufferTests.md`](../testfiles/api/vktApiBufferTests.md), the observed `buffer` subtree covers:
- recursive combinations of nine buffer-usage bits generated by [`createBufferUsageCases()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L588);
- suballocated versus dedicated allocation paths;
- sparse-binding-related create-flag variants outside Vulkan SC;
- very large-buffer boundary cases in the `basic` branch;
- invalid depth/stencil buffer-format exposure checks via queried [`VkFormatProperties`](../../modules/vulkan/api/vktApiBufferTests.cpp#L663).

Taken together, the documented `object_management` and `buffer` slices show that the inspected `api` category begins with basic Vulkan object existence, memory binding, and API-contract validation before moving into more feature-specific groups.

### Aggregated `buffer_view` subtree

The top-level registration file does not register `buffer_view` through one external factory; instead, it creates a local subgroup with [`createTestGroup()`](../../modules/vulkan/api/vktApiTests.cpp#L106) and populates it through [`createBufferViewTests()`](../../modules/vulkan/api/vktApiTests.cpp#L78), which adds `create` and `access` children by calling [`createBufferViewCreateTests()`](../../modules/vulkan/api/vktApiTests.cpp#L82) and [`createBufferViewAccessTests()`](../../modules/vulkan/api/vktApiTests.cpp#L83).

This is relevant to the category shape even though no `api.md` claims beyond that registration fact are made here for `buffer_view`, because no completed Level-3 synthesis for the full buffer-view slice was used in this document.

### Copy and blit as a major mid-category subtree

[`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L108) adds [`createCopiesAndBlittingTests()`](../../modules/vulkan/api/vktApiTests.cpp#L108), and the inspected dispatcher file shows this is one of the largest structured subtrees inside `api`.

From [`vktApiCopiesAndBlittingTests.md`](../testfiles/api/vktApiCopiesAndBlittingTests.md) and the dispatcher source in [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119), the observed top-level `copy_and_blit` organization includes:
- `core` and `dedicated_allocation` branches that reuse the same broad family of copy/blit/resolve operations with different allocation strategies;
- `copy_commands2` and `sparse` branches for selected extension/feature paths;
- separate top-level branches for `multiplane_transfer_queue`, `reinterpret`, and several non-Vulkan-SC-only areas such as `dynamic_state_meta_ops`, `copy_memory_indirect`, and `device_address`.

Within that large subtree, the completed [`vktApiUseAfterCopyTests.md`](../testfiles/api/vktApiUseAfterCopyTests.md) documents one inspected implementation slice under `copy_and_blit/core/use_after_copy`. That slice verifies that copied images remain usable afterward in later graphics consumption paths, not merely that the copy command itself completes.

### Post-copy usability as a representative API-contract theme

The inspected [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710) slice shows a recurring API-category principle: command correctness is often validated indirectly through later use.

As summarized in [`vktApiUseAfterCopyTests.md`](../testfiles/api/vktApiUseAfterCopyTests.md), the `use_after_copy` subtree checks:
- sampled color-image use after copy;
- depth/stencil attachment use after copy;
- multiple copy paths leading into later use, including classic buffer-to-image, image-to-image, and file-visible indirect-copy logic;
- queue-family and layout variants that stress state transitions as well as data preservation.

This makes the documented `copy_and_blit` slice complementary to `object_management` and `buffer`: the former validates later semantic use after transfer, whereas the latter two emphasize creation, allocation, binding, and handle-lifetime contracts.

## Recurring Parameter Dimensions

Across the currently synthesized API slices, the following parameter dimensions recur:

| Dimension | Observed examples |
|---|---|
| Allocation strategy | suballocated vs dedicated allocation in [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L49) and dispatcher-level [`TestGroupParams`](../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.hpp#L334) usage cited by [`vktApiCopiesAndBlittingTests.md`](../testfiles/api/vktApiCopiesAndBlittingTests.md) |
| Object/resource sharing model | single, multiple unique resources, multiple shared resources, and multithreaded sharing patterns in [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3595) |
| Queue selection | universal, compute-only, and transfer-only paths in [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L121) and [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1765) |
| Usage-flag / create-flag combinations | recursive buffer usage masks and sparse-related create-flag variants in [`createBufferUsageCases()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L588) |
| Image layout and copy-path choice | `TRANSFER_DST_OPTIMAL` vs `GENERAL`, plus buffer-to-image vs image-to-image vs indirect paths in [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1757) and [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1848) |
| Object type / format matrices | object-specific case tables in [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3646) and format-driven per-group expansion in [`vktApiUseAfterCopyTests.cpp`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1715) |

These inspected files suggest that the `api` category commonly builds matrices over object type, allocation style, queue family, usage flags, and later-consumption mode rather than relying on single-path smoke tests.

## Recurring Support Requirements

The currently documented slices show support gating at several layers:

- feature and extension gates tied to object categories, such as cube-array, event, pipeline-cache-control, descriptor-set recycling, and private-data checks in [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3484);
- allocation-path requirements such as dedicated allocation support in [`DedicatedAllocationBuffersTestCase::checkSupport()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L175);
- sparse binding, sparse residency, and sparse aliasing requirements in [`BuffersTestCase::checkSupport()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L135);
- queue/layout/feature requirements in `use_after_copy`, including indirect copy, maintenance1, maintenance10, 2D views of 3D, format support, and queue capability checks in [`AfterUsageCase::checkSupport()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L253);
- broad non-Vulkan-SC divergence at registration level in [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L93) and inside the copy/blit dispatcher in [`vktApiCopiesAndBlittingTests.cpp`](../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L76).

A category-level takeaway from the inspected work is that `api` coverage is heavily conditional: many branches exist only when specific core features, extensions, queue capabilities, or build targets are available.

## Recurring Verification Methods

The synthesized slices use several distinct verification styles:

- structural success/failure of creation, allocation, binding, and destruction in [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L380) and [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L203);
- negative API-contract validation, such as expected OOM error codes, callback accounting, null-handle expectations, and invalid depth/stencil buffer-feature exposure in [`vktApiObjectManagementTests.cpp`](../../modules/vulkan/api/vktApiObjectManagementTests.cpp#L3234) and [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L666);
- CPU-generated reference images plus thresholded framebuffer comparison in `use_after_copy`, culminating in [`tcu::floatThresholdCompare()`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1691);
- indirect semantic validation, where copied depth or color content is judged by later rendering behavior rather than immediate raw transfer readback, as described in [`vktApiUseAfterCopyTests.md`](../testfiles/api/vktApiUseAfterCopyTests.md).

For the inspected subset, this means the `api` category is not limited to "did the call succeed" checks; it also verifies side conditions, error behavior, and correctness of later consumption after an API action.

## Relationship to the Test Plan

[`apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc#L134) is relevant for the documented `object_management` slice because it explicitly describes object-management goals around create/destroy behavior, repeated allocation, and multithreaded operations. More general framework context from [`apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc#L15) also matches the observed Vulkan CTS pattern of [`TestCase`](../../../doc/testspecs/VK/apitests.adoc#L30) plus [`TestInstance`](../../../doc/testspecs/VK/apitests.adoc#L43) implementations used throughout the API files.

For the other currently synthesized API slices, the source files themselves are the primary evidence. This partial category summary therefore prefers code-backed subgroup structure and completed Level-3 docs over broader unsupported claims from the high-level plan.

## Notes / Uncertainties

- This category summary is **partial by design**. The top-level `api` registration tree in [`vktApiTests.cpp`](../../modules/vulkan/api/vktApiTests.cpp#L86) contains many more subgroups than are synthesized here.
- The registration tree above is complete for the inspected file, but the thematic summary only covers currently documented/inspected slices: [`object_management`](../../modules/vulkan/api/vktApiTests.cpp#L101), [`buffer`](../../modules/vulkan/api/vktApiTests.cpp#L102), [`buffer_view`](../../modules/vulkan/api/vktApiTests.cpp#L106) at registration-only level, [`copy_and_blit`](../../modules/vulkan/api/vktApiTests.cpp#L108) at dispatcher level, and [`use_after_copy`](../../modules/vulkan/api/vktApiUseAfterCopyTests.cpp#L1710) as one implementation slice beneath it.
- No attempt is made here to summarize undocumented API files such as [`vktApiCommandBuffersTests.cpp`](../../modules/vulkan/api/vktApiCommandBuffersTests.cpp), [`vktApiPipelineTests.cpp`](../../modules/vulkan/api/vktApiPipelineTests.cpp), or other registered groups unless their behavior was supported by completed Level-3 documentation used in this synthesis.
