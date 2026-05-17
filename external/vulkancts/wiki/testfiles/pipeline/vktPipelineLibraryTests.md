# vktPipelineLibraryTests.cpp

## Overview

[`vktPipelineLibraryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1) implements the [`graphics_library`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6249) topic group. It verifies VK_EXT_graphics_pipeline_library functionality, testing pipeline library creation, linking, and execution including independent layout sets, null descriptor combinations, and various pipeline library configurations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineLibraryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1)
- Header: [`vktPipelineLibraryTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.pipeline_library.graphics_library
├── fast
├── optimize
└── misc
```

Source: [`createPipelineLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6247). Variant coverage: Pipeline library only (`PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`), VK only. The `graphics_library` group is attached under the `pipeline_library` variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94).

## Test Families

### fast — Pipeline library fast-link configurations

Verifies graphics pipeline library creation and linking without optimization (`addPipelineLibraryConfigurationsTests` with `optimize=false`). Uses `PipelineLibraryTestCase` instances that test various shader stage combinations and pipeline library configurations under the fast-linked construction type.

### optimize — Pipeline library optimized-link configurations

Verifies graphics pipeline library creation and linking with optimization (`addPipelineLibraryConfigurationsTests` with `optimize=true`). Uses `PipelineLibraryTestCase` instances that test the same shader stage combinations and pipeline library configurations under the link-time-optimized construction type.

### misc — Miscellaneous pipeline library behaviors

Verifies miscellaneous pipeline library behaviors using `PipelineLibraryMiscTestCase` and `AlwaysNullSetLayoutCase` instances. Contains the following subgroups:

- **independent_pipeline_layout_sets**: Tests independent pipeline layout sets with fast-linked and link-time-optimized union-handle modes.
- **bind_null_descriptor_set**: Tests various null descriptor set binding combinations, using binary patterns (e.g., `"1"`, `"11"`, `"01"`, `"101"`) to represent which descriptor set layouts are used versus null.
- **other**: Contains `compare_link_times`, `null_descriptor_set_in_monolithic_pipeline`, `null_rendering_create_info`, `bad_rendering_create_info`, `common_frag_pipeline_library`, `view_index_from_device_index` (with pipeline state mode and mesh shading variants), `unusual_multisample_state`, `transform_feedback_with_fast_link`, and `destroy_resources_before_link_samplers_2` / `destroy_resources_before_link_samplers_3`.
- **non_graphics**: Tests shader module create info for compute (`shader_module_info_comp`), ray tracing (`shader_module_info_rt`), and ray tracing library (`shader_module_info_rt_lib`) pipeline types.
- **always_null_set_layout**: Tests descriptor set layouts that are always `VK_NULL_HANDLE`, with combinations of used/unused sets and construction types (fast-linked and optimized).
- **primary_rebind**: Tests rebinding pipelines in the primary command buffer after executing things in the secondary, across monolithic, fast-linked, optimized, and extended shader object construction types.
- **view_mask**: Tests whether `viewMask` is needed in the fragment output library, with fast and optimized variants.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Pipeline library variant |
| Shader stages | Enum | Vertex, fragment, tessellation, geometry combinations |
| Layout compatibility | Enum | Compatible, incompatible layouts |
| Null descriptor | Bool | With/without null descriptors |
| View mask | Array | Single view, multi-view |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_pipeline_library` | Required for all tests |
| `VK_EXT_graphics_pipeline_library` | Primary extension for all tests |
| `VK_KHR_maintenance5` | Required for maintenance5 test |
| `VK_KHR_multiview` | Required for view mask tests |
| `VK_KHR_device_group` | Required for device group tests |

## Verification Methods

- **Pipeline execution verification**: Create pipeline library, link, execute, verify rendering output
- **Layout compatibility verification**: Verify that independent layout sets work correctly
- **Null descriptor verification**: Verify that null descriptor combinations are handled correctly
- **Resource destruction verification**: Verify that resources can be destroyed after pipeline linking

## Notes

- Only registered for pipeline library variant
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- This is the most comprehensive test for VK_EXT_graphics_pipeline_library
