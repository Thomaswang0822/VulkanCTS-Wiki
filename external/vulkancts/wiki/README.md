# Vulkan CTS Wiki

This wiki provides comprehensive documentation of the Vulkan Conformance Test Suite (CTS) test structure.

## Structure

```
wiki/
├── README.md                                   # This file
├── Vulkan_CTS_Framework_and_Mechanism.md       # Level 1: Framework overview
├── categories/                                 # Level 2: Category documentation
│   ├── api.md
│   ├── memory.md
│   └── ...
└── testfiles/                                  # Level 3: CPP test file documentation
    ├── api/
    │   ├── vktApiBufferTests.md
    │   └── ...
    └── ...
```

## Documentation Levels

| Level | Description | Count |
|-------|-------------|-------|
| Level 1 | Framework and mechanism overview | 1 |
| Level 2 | Test category documentation | 53 |
| Level 3 | CPP test file documentation | 592 |

## Progress Tracking

### Level 1: Framework Overview

| Document | Status |
|----------|--------|
| [Vulkan_CTS_Framework_and_Mechanism.md](Vulkan_CTS_Framework_and_Mechanism.md) | ✅ Done |

### Level 2 & 3: Categories

The category order below is intended as a learning path from Vulkan fundamentals toward more specialized and extension-heavy areas. It is the default order to follow when creating or reading category documentation, unless a user explicitly asks for a different category.

| # | Category | Level-2 | Level-3 Files | Status |
|---|----------|---------|---------------|--------|
| 1 | info | [info.md](categories/info.md) | 2 | ✅ Done |
| 2 | api | [api.md](categories/api.md) | 49 | ⬜ Not Started |
| 3 | memory | [memory.md](categories/memory.md) | 15 | ⬜ Not Started |
| 4 | synchronization | [synchronization.md](categories/synchronization.md) | 17 | ⬜ Not Started |
| 5 | synchronization2 | [synchronization2.md](categories/synchronization2.md) | 3 | ⬜ Not Started |
| 6 | query_pool | [query_pool.md](categories/query_pool.md) | 5 | ⬜ Not Started |
| 7 | binding_model | [binding_model.md](categories/binding_model.md) | 16 | ⬜ Not Started |
| 8 | pipeline | [pipeline.md](categories/pipeline.md) | 63 | ⬜ Not Started |
| 9 | shader_object | [shader_object.md](categories/shader_object.md) | 9 | ⬜ Not Started |
| 10 | renderpasses | [renderpasses.md](categories/renderpasses.md) | 29 | ⬜ Not Started |
| 11 | imageless_framebuffer | [imageless_framebuffer.md](categories/imageless_framebuffer.md) | 2 | ⬜ Not Started |
| 12 | dynamic_state | [dynamic_state.md](categories/dynamic_state.md) | 10 | ⬜ Not Started |
| 13 | image | [image.md](categories/image.md) | 23 | ⬜ Not Started |
| 14 | image_processing | [image_processing.md](categories/image_processing.md) | 4 | ⬜ Not Started |
| 15 | ycbcr | [ycbcr.md](categories/ycbcr.md) | 4 | ⬜ Not Started |
| 16 | draw | [draw.md](categories/draw.md) | 27 | ⬜ Not Started |
| 17 | texture | [texture.md](categories/texture.md) | 12 | ⬜ Not Started |
| 18 | rasterization | [rasterization.md](categories/rasterization.md) | 9 | ⬜ Not Started |
| 19 | fragment_operations | [fragment_operations.md](categories/fragment_operations.md) | 5 | ⬜ Not Started |
| 20 | clipping | [clipping.md](categories/clipping.md) | 4 | ⬜ Not Started |
| 21 | multiview | [multiview.md](categories/multiview.md) | 4 | ⬜ Not Started |
| 22 | geometry | [geometry.md](categories/geometry.md) | 7 | ✅ Done |
| 23 | tessellation | [tessellation.md](categories/tessellation.md) | 15 | ⬜ Not Started |
| 24 | transform_feedback | [transform_feedback.md](categories/transform_feedback.md) | 3 | ⬜ Not Started |
| 25 | ubo | [ubo.md](categories/ubo.md) | 4 | ⬜ Not Started |
| 26 | ssbo | [ssbo.md](categories/ssbo.md) | 4 | ⬜ Not Started |
| 27 | glsl | [glsl.md](categories/glsl.md) | 9 | ⬜ Not Started |
| 28 | spirv_assembly | [spirv_assembly.md](categories/spirv_assembly.md) | 44 | ⬜ Not Started |
| 29 | subgroups | [subgroups.md](categories/subgroups.md) | 20 | ⬜ Not Started |
| 30 | compute | [compute.md](categories/compute.md) | 6 | ⬜ Not Started |
| 31 | memory_model | [memory_model.md](categories/memory_model.md) | 5 | ⬜ Not Started |
| 32 | descriptor_indexing | [descriptor_indexing.md](categories/descriptor_indexing.md) | 3 | ⬜ Not Started |
| 33 | robustness | [robustness.md](categories/robustness.md) | 7 | ⬜ Not Started |
| 34 | sparse_resources | [sparse_resources.md](categories/sparse_resources.md) | 6 | ⬜ Not Started |
| 35 | protected_memory | [protected_memory.md](categories/protected_memory.md) | 15 | ⬜ Not Started |
| 36 | conditional_rendering | [conditional_rendering.md](categories/conditional_rendering.md) | 3 | ⬜ Not Started |
| 37 | device_group | [device_group.md](categories/device_group.md) | 4 | ⬜ Not Started |
| 38 | wsi | [wsi.md](categories/wsi.md) | 14 | ⬜ Not Started |
| 39 | drm_format_modifiers | [drm_format_modifiers.md](categories/drm_format_modifiers.md) | 4 | ⬜ Not Started |
| 40 | video | [video.md](categories/video.md) | 6 | ⬜ Not Started |
| 41 | depth | [depth.md](categories/depth.md) | 1 | ⬜ Not Started |
| 42 | graphicsfuzz | [graphicsfuzz.md](categories/graphicsfuzz.md) | 3 | ⬜ Not Started |
| 43 | fragment_shader_interlock | [fragment_shader_interlock.md](categories/fragment_shader_interlock.md) | 2 | ⬜ Not Started |
| 44 | fragment_shading_rate | [fragment_shading_rate.md](categories/fragment_shading_rate.md) | 6 | ⬜ Not Started |
| 45 | fragment_shading_barycentric | [fragment_shading_barycentric.md](categories/fragment_shading_barycentric.md) | 2 | ⬜ Not Started |
| 46 | mesh_shader | [mesh_shader.md](categories/mesh_shader.md) | 8 | ⬜ Not Started |
| 47 | ray_query | [ray_query.md](categories/ray_query.md) | 4 | ⬜ Not Started |
| 48 | ray_tracing_pipeline | [ray_tracing_pipeline.md](categories/ray_tracing_pipeline.md) | 31 | ⬜ Not Started |
| 49 | reconvergence | [reconvergence.md](categories/reconvergence.md) | 2 | ⬜ Not Started |
| 50 | cooperative_vector | [cooperative_vector.md](categories/cooperative_vector.md) | 1 | ⬜ Not Started |
| 51 | tensor | [tensor.md](categories/tensor.md) | 1 | ⬜ Not Started |
| 52 | data_graph | [data_graph.md](categories/data_graph.md) | 1 | ⬜ Not Started |
| 53 | dgc | [dgc.md](categories/dgc.md) | 5 | ⬜ Not Started |

**Legend**: ✅ Done | 🔄 In Progress | ⬜ Not Started

## Statistics

- **Total Categories**: 53
- **Total CPP Test Files**: 592
- **Completed Categories**: 2/53
- **Completed Test Files**: 10/592

