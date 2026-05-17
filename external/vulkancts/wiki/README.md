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

For this tracker, the `Level-3 Files` column counts the actual number of Level-3 wiki files (`.md` files) under `testfiles/{category}/`. This count is updated only after a category reaches `✅ Done`. Categories that are still `⬜ Not Started` intentionally leave this field blank.

| # | Category | Level-2 | Level-3 Files | Status |
|---|----------|---------|---------------|--------|
| 1 | info | [info.md](categories/info.md) | 2 | ✅ Done |
| 2 | api | [api.md](categories/api.md) | 54 | ✅ Done |
| 3 | memory | [memory.md](categories/memory.md) | 15 | ✅ Done |
| 4 | synchronization | [synchronization.md](categories/synchronization.md) | 17 | ✅ Done |
| 5 | synchronization2 | [synchronization2.md](categories/synchronization2.md) | (shared with synchronization) | ✅ Done |
| 6 | query_pool | [query_pool.md](categories/query_pool.md) | 8 | ✅ Done |
| 7 | binding_model | [binding_model.md](categories/binding_model.md) | 15 | ✅ Done |
| 8 | pipeline | [pipeline.md](categories/pipeline.md) | 62 | ✅ Done |
| 9 | shader_object | [shader_object.md](categories/shader_object.md) | 11 | ✅ Done |
| 10 | renderpasses | [renderpasses.md](categories/renderpasses.md) | 29 | ✅ Done |
| 11 | imageless_framebuffer | [imageless_framebuffer.md](categories/imageless_framebuffer.md) | 1 | ✅ Done |
| 12 | dynamic_state | [dynamic_state.md](categories/dynamic_state.md) | 10 | ✅ Done |
| 13 | image | [image.md](categories/image.md) |  | ⬜ Not Started |
| 14 | image_processing | [image_processing.md](categories/image_processing.md) |  | ⬜ Not Started |
| 15 | ycbcr | [ycbcr.md](categories/ycbcr.md) |  | ⬜ Not Started |
| 16 | draw | [draw.md](categories/draw.md) |  | ⬜ Not Started |
| 17 | texture | [texture.md](categories/texture.md) |  | ⬜ Not Started |
| 18 | rasterization | [rasterization.md](categories/rasterization.md) |  | ⬜ Not Started |
| 19 | fragment_operations | [fragment_operations.md](categories/fragment_operations.md) |  | ⬜ Not Started |
| 20 | clipping | [clipping.md](categories/clipping.md) |  | ⬜ Not Started |
| 21 | multiview | [multiview.md](categories/multiview.md) |  | ⬜ Not Started |
| 22 | geometry | [geometry.md](categories/geometry.md) | 8 | ✅ Done |
| 23 | tessellation | [tessellation.md](categories/tessellation.md) |  | ⬜ Not Started |
| 24 | transform_feedback | [transform_feedback.md](categories/transform_feedback.md) |  | ⬜ Not Started |
| 25 | ubo | [ubo.md](categories/ubo.md) |  | ⬜ Not Started |
| 26 | ssbo | [ssbo.md](categories/ssbo.md) |  | ⬜ Not Started |
| 27 | glsl | [glsl.md](categories/glsl.md) |  | ⬜ Not Started |
| 28 | spirv_assembly | [spirv_assembly.md](categories/spirv_assembly.md) |  | ⬜ Not Started |
| 29 | subgroups | [subgroups.md](categories/subgroups.md) |  | ⬜ Not Started |
| 30 | compute | [compute.md](categories/compute.md) |  | ⬜ Not Started |
| 31 | memory_model | [memory_model.md](categories/memory_model.md) |  | ⬜ Not Started |
| 32 | descriptor_indexing | [descriptor_indexing.md](categories/descriptor_indexing.md) |  | ⬜ Not Started |
| 33 | robustness | [robustness.md](categories/robustness.md) |  | ⬜ Not Started |
| 34 | sparse_resources | [sparse_resources.md](categories/sparse_resources.md) |  | ⬜ Not Started |
| 35 | protected_memory | [protected_memory.md](categories/protected_memory.md) |  | ⬜ Not Started |
| 36 | conditional_rendering | [conditional_rendering.md](categories/conditional_rendering.md) |  | ⬜ Not Started |
| 37 | device_group | [device_group.md](categories/device_group.md) |  | ⬜ Not Started |
| 38 | wsi | [wsi.md](categories/wsi.md) |  | ⬜ Not Started |
| 39 | drm_format_modifiers | [drm_format_modifiers.md](categories/drm_format_modifiers.md) |  | ⬜ Not Started |
| 40 | video | [video.md](categories/video.md) |  | ⬜ Not Started |
| 41 | depth | [depth.md](categories/depth.md) |  | ⬜ Not Started |
| 42 | graphicsfuzz | [graphicsfuzz.md](categories/graphicsfuzz.md) |  | ⬜ Not Started |
| 43 | fragment_shader_interlock | [fragment_shader_interlock.md](categories/fragment_shader_interlock.md) |  | ⬜ Not Started |
| 44 | fragment_shading_rate | [fragment_shading_rate.md](categories/fragment_shading_rate.md) |  | ⬜ Not Started |
| 45 | fragment_shading_barycentric | [fragment_shading_barycentric.md](categories/fragment_shading_barycentric.md) |  | ⬜ Not Started |
| 46 | mesh_shader | [mesh_shader.md](categories/mesh_shader.md) |  | ⬜ Not Started |
| 47 | ray_query | [ray_query.md](categories/ray_query.md) |  | ⬜ Not Started |
| 48 | ray_tracing_pipeline | [ray_tracing_pipeline.md](categories/ray_tracing_pipeline.md) |  | ⬜ Not Started |
| 49 | reconvergence | [reconvergence.md](categories/reconvergence.md) |  | ⬜ Not Started |
| 50 | cooperative_vector | [cooperative_vector.md](categories/cooperative_vector.md) |  | ⬜ Not Started |
| 51 | tensor | [tensor.md](categories/tensor.md) |  | ⬜ Not Started |
| 52 | data_graph | [data_graph.md](categories/data_graph.md) |  | ⬜ Not Started |
| 53 | dgc | [dgc.md](categories/dgc.md) |  | ⬜ Not Started |

**Legend**: ✅ Done | 🔄 In Progress | ⬜ Not Started

## Statistics

- **Total Categories**: 53
- **Total CPP Test Files**: 592
- **Completed Categories**: 13/53
- **Completed Test Files**: 249/592

