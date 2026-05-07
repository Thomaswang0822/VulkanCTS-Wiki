# vktPipelineLibraryTests.cpp

## Overview

[`vktPipelineLibraryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1) implements the [`graphics_library`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6249) topic group. It verifies VK_EXT_graphics_pipeline_library functionality, testing pipeline library creation, linking, and execution including independent layout sets, null descriptor combinations, and various pipeline library configurations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineLibraryTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1)
- Header: [`vktPipelineLibraryTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.hpp#L1)

## Registration Path

[`createGraphicsLibraryTests()`](../../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L6248) returns the `graphics_library` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Pipeline library only, VK only. Library-specific tests executed once.

## Test Hierarchy

```text
graphics_library
├── {pipeline_library_test_cases}
├── maintenance5
└── misc
    ├── independent_layout_sets
    │   └── {test_case}
    ├── bind_null_descriptor_combinations
    │   └── {test_case}
    ├── other
    │   ├── null_rendering_create_info
    │   ├── bad_rendering_create_info
    │   ├── common_frag_pipeline_library
    │   ├── unusual_multisample_state
    │   └── destroy_resources_before_link_samplers_{2,3}
    ├── non_graphics
    │   ├── shader_module_info_comp
    │   ├── shader_module_info_rt
    │   └── shader_module_info_rt_lib
    ├── always_null_set_layout
    │   └── {test_case}
    ├── primitive_rebind
    │   └── {test_case}
    └── view_mask
        └── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| PipelineLibraryTestCase | Verifies pipeline library creation and linking for various shader stage combinations |
| PipelineLibraryMiscTestCase | Verifies miscellaneous pipeline library behaviors |
| AlwaysNullSetLayoutCase | Verifies pipeline library with always-null descriptor set layouts |

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
