# Vulkan CTS Wiki

This wiki documents how Vulkan Conformance Test Suite (CTS) test categories are organized, registered,
parameterized, and verified. It is intended as a source-backed navigation layer over Vulkan CTS code, with category
summaries and per-source-file notes that link back to the implementation evidence.

## Where to Start

- New to this wiki's page structure and terminology: start with [Reader_Guide.md](Reader_Guide.md).
- New to Vulkan CTS internals: start with
  [CTS_Framework.md](CTS_Framework.md).
  A good sanity check: what is Vulkan SC and how is it different from Vulkan?
- Looking for a top-level test area: use the [Category Index](#category-index).
- Looking for source-file-level behavior: open a category page, then follow its Level-3 testfile links.
- Investigating naming mismatches between wiki pages, mustpass files, and source directories: see
  [Category Naming Notes](#category-naming-notes).

## How the Wiki Is Organized

| Area | Purpose |
|------|---------|
| [Reader_Guide.md](Reader_Guide.md) | How to read Level-2 category pages, Level-3 testfile pages, terminology, and source evidence links. |
| [CTS_Framework.md](CTS_Framework.md) | Framework, registration, execution, verification, mustpass, and Vulkan SC overview. |
| [categories/](categories/) | One page per top-level Vulkan CTS category, summarizing registration structure and cross-file behavior. |
| [testfiles/](testfiles/) | Source-file-level pages linked from category pages, covering registered groups, test families, parameters, support checks, and verification methods. |

```text
wiki/
├── README.md                                   # This navigation entry point
├── Reader_Guide.md                            # How to read rewritten wiki pages
├── CTS_Framework.md                            # Framework and mechanism overview
├── categories/                                 # Top-level category documentation
│   ├── api.md
│   ├── memory.md
│   └── ...
└── testfiles/                                  # Source-file-level documentation
    ├── api/
    │   ├── vktApiBufferTests.md
    │   └── ...
    └── ...
```

## Scope and Evidence

The wiki focuses on Vulkan CTS content under the repository's [Vulkan CTS tree](..). Category and testfile pages are
intended to summarize registration hierarchy, test families, parameter dimensions, support requirements, and
verification methods using inspected source-code evidence.

The category names in this index follow Vulkan CTS root registration paths and default mustpass categories. They are not
always identical to source directory names; see [Category Naming Notes](#category-naming-notes) for common mappings.

## Category Index

The table below lists the documented top-level Vulkan CTS categories in the recommended reading order.

| # | Category | Documentation |
|---|----------|---------------|
| 1 | info | [info.md](categories/info.md) |
| 2 | api | [api.md](categories/api.md) |
| 3 | memory | [memory.md](categories/memory.md) |
| 4 | synchronization | [synchronization.md](categories/synchronization.md) |
| 5 | synchronization2 | [synchronization2.md](categories/synchronization2.md) |
| 6 | query_pool | [query_pool.md](categories/query_pool.md) |
| 7 | binding_model | [binding_model.md](categories/binding_model.md) |
| 8 | pipeline | [pipeline.md](categories/pipeline.md) |
| 9 | shader_object | [shader_object.md](categories/shader_object.md) |
| 10 | renderpasses | [renderpasses.md](categories/renderpasses.md) |
| 11 | imageless_framebuffer | [imageless_framebuffer.md](categories/imageless_framebuffer.md) |
| 12 | dynamic_state | [dynamic_state.md](categories/dynamic_state.md) |
| 13 | image | [image.md](categories/image.md) |
| 14 | image_processing | [image_processing.md](categories/image_processing.md) |
| 15 | ycbcr | [ycbcr.md](categories/ycbcr.md) |
| 16 | draw | [draw.md](categories/draw.md) |
| 17 | texture | [texture.md](categories/texture.md) |
| 18 | rasterization | [rasterization.md](categories/rasterization.md) |
| 19 | fragment_operations | [fragment_operations.md](categories/fragment_operations.md) |
| 20 | clipping | [clipping.md](categories/clipping.md) |
| 21 | multiview | [multiview.md](categories/multiview.md) |
| 22 | geometry | [geometry.md](categories/geometry.md) |
| 23 | tessellation | [tessellation.md](categories/tessellation.md) |
| 24 | transform_feedback | [transform_feedback.md](categories/transform_feedback.md) |
| 25 | ubo | [ubo.md](categories/ubo.md) |
| 26 | ssbo | [ssbo.md](categories/ssbo.md) |
| 27 | glsl | [glsl.md](categories/glsl.md) |
| 28 | spirv_assembly | [spirv_assembly.md](categories/spirv_assembly.md) |
| 29 | subgroups | [subgroups.md](categories/subgroups.md) |
| 30 | compute | [compute.md](categories/compute.md) |
| 31 | memory_model | [memory_model.md](categories/memory_model.md) |
| 32 | descriptor_indexing | [descriptor_indexing.md](categories/descriptor_indexing.md) |
| 33 | robustness | [robustness.md](categories/robustness.md) |
| 34 | sparse_resources | [sparse_resources.md](categories/sparse_resources.md) |
| 35 | protected_memory | [protected_memory.md](categories/protected_memory.md) |
| 36 | conditional_rendering | [conditional_rendering.md](categories/conditional_rendering.md) |
| 37 | device_group | [device_group.md](categories/device_group.md) |
| 38 | wsi | [wsi.md](categories/wsi.md) |
| 39 | drm_format_modifiers | [drm_format_modifiers.md](categories/drm_format_modifiers.md) |
| 40 | video | [video.md](categories/video.md) |
| 41 | depth | [depth.md](categories/depth.md) |
| 42 | graphicsfuzz | [graphicsfuzz.md](categories/graphicsfuzz.md) |
| 43 | fragment_shader_interlock | [fragment_shader_interlock.md](categories/fragment_shader_interlock.md) |
| 44 | fragment_shading_rate | [fragment_shading_rate.md](categories/fragment_shading_rate.md) |
| 45 | fragment_shading_barycentric | [fragment_shading_barycentric.md](categories/fragment_shading_barycentric.md) |
| 46 | mesh_shader | [mesh_shader.md](categories/mesh_shader.md) |
| 47 | ray_query | [ray_query.md](categories/ray_query.md) |
| 48 | ray_tracing_pipeline | [ray_tracing_pipeline.md](categories/ray_tracing_pipeline.md) |
| 49 | reconvergence | [reconvergence.md](categories/reconvergence.md) |
| 50 | cooperative_vector | [cooperative_vector.md](categories/cooperative_vector.md) |
| 51 | tensor | [tensor.md](categories/tensor.md) |
| 52 | data_graph | [data_graph.md](categories/data_graph.md) |
| 53 | dgc | [dgc.md](categories/dgc.md) |

## Category Naming Notes

Some registered category names intentionally differ from source directory names or are implemented through
shared/root-level infrastructure. These mappings help readers locate the relevant source implementation.

| Wiki category | Mustpass entry | Source location pattern | Note |
|---------------|----------------|-------------------------|------|
| renderpasses | [renderpasses.txt](../mustpass/main/vk-default/renderpasses.txt) | [renderpass/](../modules/vulkan/renderpass/) | Registered category name differs from source directory name. |
| fragment_operations | [fragment-operations.txt](../mustpass/main/vk-default/fragment-operations.txt) | [fragment_ops/](../modules/vulkan/fragment_ops/) | Registered category name differs from source directory name. |
| drm_format_modifiers | [drm-format-modifiers.txt](../mustpass/main/vk-default/drm-format-modifiers.txt) | [modifiers/](../modules/vulkan/modifiers/) | Registered category name differs from source directory name. |
| ray_tracing_pipeline | [ray-tracing-pipeline.txt](../mustpass/main/vk-default/ray-tracing-pipeline.txt) | [ray_tracing/](../modules/vulkan/ray_tracing/) | Registered category name differs from source directory name. |
| dgc | [dgc.txt](../mustpass/main/vk-default/dgc.txt) | [device_generated_commands/](../modules/vulkan/device_generated_commands/) | Short registered category name maps to a longer source directory. |
| info | [info.txt](../mustpass/main/vk-default/info.txt) | [vktInfoTests.cpp](../modules/vulkan/vktInfoTests.cpp) | Implemented by root-level Vulkan module files, not a matching category directory. |
| glsl | [glsl.txt](../mustpass/main/vk-default/glsl.txt) | Amber and shader-render integration files | Registered as a root test group without a matching `glsl/` source directory. |
| graphicsfuzz | [graphicsfuzz.txt](../mustpass/main/vk-default/graphicsfuzz.txt) | Amber integration files | Registered as a root test group without a matching `graphicsfuzz/` source directory. |
| depth | [depth.txt](../mustpass/main/vk-default/depth.txt) | Amber depth integration files | Registered as a root test group without a matching `depth/` source directory. |
| synchronization2 | [synchronization2.txt](../mustpass/main/vk-default/synchronization2.txt) | [synchronization/](../modules/vulkan/synchronization/) | Shares implementation area with `synchronization`. |
