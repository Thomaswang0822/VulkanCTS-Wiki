## Overview

The `dgc` test category collects tests that check whether Vulkan device-generated commands correctly describe, prepare, execute, and validate compute, graphics, and ray-tracing work.

The category contains the NV device-generated-command branch and the EXT branch. The root dispatcher registers these branches in [`vktDGCTests.cpp`](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L68-L128); the implementation details are split across the Level-3 pages below.

## Background Knowledge

- A device-generated-command layout maps records in an indirect buffer to command tokens. State tokens can select pipelines or shader objects, update push constants, bind resources, or supply sequence indices; an action token performs a dispatch, draw, or trace-ray operation.
- Explicit preprocessing separates preparation from later execution. The test must provide the required preprocess storage and synchronize the preparation result before a later command buffer consumes it. Queue-switch cases add queue-family ownership and visibility requirements.
- Execution sets let generated commands select among pipelines or shader objects by index. This changes which pre-created state handles a sequence uses; it does not make every generated case a separate source-level shader algorithm.
- CTS result checks observe the output chosen by each family: mapped storage buffers, color or depth attachments, transform-feedback buffers, property-query structures, or ray-tracing payload records. A support rejection means the requested feature combination cannot run; a comparison failure means the implementation produced an unexpected result for a supported case.

## Category Structure

```text
dgc
├── nv
└── ext
    ├── compute
    ├── misc
    ├── graphics
    ├── stat_query
    └── ray_tracing
        ├── basic
        └── conditional_rendering
```

`nv` contains compute and property families. `ext` contains compute, property, graphics, ray-tracing, and pipeline-statistics-query families. `vktDGCTests.cpp` is a registration dispatcher, so its facts are represented here rather than by a separate technical Level-3 page.

## How the Families Fit Together

The pages divide the category by the command family and the Vulkan state that makes its result observable:

- **when** the test queries requirements or addresses without executing generated work, read the get-info and property pages;
- **when** the test executes compute commands, the compute pages separate preprocessing, token-layout state, subgroup built-ins, conditional rendering, smoke execution, and miscellaneous resource paths;
- **when** the test produces rasterized output, the graphics pages separate draw actions, draw-count actions, conditional rendering, mesh work, miscellaneous state, transform feedback, tessellation state, and multiview;
- **when** the test records shader-visible traversal and payload data, read the ray-tracing page.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `dgc.nv.compute.get_info` | [ComputeGetInfo](../testfiles/dgc/ComputeGetInfo.md) | NV pipeline-address and generated-command memory-requirements queries. |
| `dgc.nv.compute.smoke` | [ComputeSmoke](../testfiles/dgc/ComputeSmoke.md) | NV generated compute dispatches, sequence counts, memory placement, preprocessing, and queue selection. |
| `dgc.nv.compute.layout` | [ComputeLayout](../testfiles/dgc/ComputeLayout.md) | NV token layouts, push constants, dispatch state, and address capture/replay. |
| `dgc.nv.compute.misc` | [ComputeMisc](../testfiles/dgc/ComputeMisc.md) | NV repeated execution, pipeline replay, and scratch-space cases. |
| `dgc.nv.compute.preprocess` | [ComputePreprocess](../testfiles/dgc/ComputePreprocess.md) | NV parallel preprocessing, count buffers, zero-count behavior, and queue switches. |
| `dgc.nv.compute.subgroups` | [ComputeSubgroup](../testfiles/dgc/ComputeSubgroup.md) | NV subgroup built-ins and ballot-mask validation through generated compute execution. |
| `dgc.nv.compute.conditional_rendering` | [ComputeConditional](../testfiles/dgc/ComputeConditional.md) | NV conditional rendering around generated compute execution and preprocessing. |
| `dgc.nv.misc.properties` | [Property](../testfiles/dgc/Property.md) | NV device-generated-command properties, limits, alignments, and query-backed execution checks. |
| `dgc.ext.compute.get_info` | [ComputeGetInfoExt](../testfiles/dgc/ComputeGetInfoExt.md) | EXT memory-requirements queries across layout, usage, pipeline, and sequence-count inputs. |
| `dgc.ext.compute.smoke` | [ComputeSmokeExt](../testfiles/dgc/ComputeSmokeExt.md) | EXT generated compute smoke cases and their queue, preprocessing, and execution-set dimensions. |
| `dgc.ext.compute.layout` | [ComputeLayoutExt](../testfiles/dgc/ComputeLayoutExt.md) | EXT dispatch layouts combining push data, execution sets, shader objects, and descriptor heaps. |
| `dgc.ext.compute.misc` | [ComputeMiscExt](../testfiles/dgc/ComputeMiscExt.md) | EXT repeated dispatch, inline uniform block, descriptor-buffer, execution-set, and scratch-space cases. |
| `dgc.ext.compute.preprocess` | [ComputePreprocessExt](../testfiles/dgc/ComputePreprocessExt.md) | EXT preprocessing with count buffers, separate state command buffers, and queue changes. |
| `dgc.ext.compute.subgroups` | [ComputeSubgroupExt](../testfiles/dgc/ComputeSubgroupExt.md) | EXT subgroup built-ins across pipeline, execution-set, and queue paths. |
| `dgc.ext.compute.conditional_rendering` | [ComputeConditionalExt](../testfiles/dgc/ComputeConditionalExt.md) | EXT conditional rendering for generated compute execution and preprocessing. |
| `dgc.ext.misc.properties` | [PropertyExt](../testfiles/dgc/PropertyExt.md) | EXT property limits, token counts, offsets, stream stride, and sequence-count checks. |
| `dgc.ext.graphics.draw` | [GraphicsDrawExt](../testfiles/dgc/GraphicsDrawExt.md) | EXT non-indexed and indexed generated draws across pipeline, shader-object, library, and preprocess paths. |
| `dgc.ext.graphics.draw_count` | [GraphicsDrawCountExt](../testfiles/dgc/GraphicsDrawCountExt.md) | EXT count and indexed-count draw tokens, padded records, and rendered validation. |
| `dgc.ext.graphics.conditional_rendering` | [GraphicsConditionalExt](../testfiles/dgc/GraphicsConditionalExt.md) | EXT conditional rendering around generated graphics execution and preprocessing. |
| `dgc.ext.graphics.mesh` | [GraphicsMeshExt](../testfiles/dgc/GraphicsMeshExt.md) | EXT mesh and task shader draws with generated graphics state. |
| `dgc.ext.graphics.mesh.conditional_rendering` | [GraphicsMeshConditionalExt](../testfiles/dgc/GraphicsMeshConditionalExt.md) | Conditional rendering combined with generated mesh and task shader draws. |
| `dgc.ext.graphics.misc` | [GraphicsMiscExt](../testfiles/dgc/GraphicsMiscExt.md) | EXT graphics state, resource, shader-stage, and mixed normal/DGC scenarios. |
| `dgc.ext.graphics.xfb` | [GraphicsXfbExt](../testfiles/dgc/GraphicsXfbExt.md) | EXT transform-feedback capture, stage combinations, and buffer validation. |
| `dgc.ext.graphics.tess_state` | [GraphicsTessStateExt](../testfiles/dgc/GraphicsTessStateExt.md) | EXT tessellation state, pipeline construction, dynamic patch control points, and reference images. |
| `dgc.ext.graphics.multiview` | [GraphicsMultiviewExt](../testfiles/dgc/GraphicsMultiviewExt.md) | EXT multiview view masks, generated draws, and per-view color/depth validation. |
| `dgc.ext.ray_tracing.basic` | [RayTracingExt](../testfiles/dgc/RayTracingExt.md) | EXT trace-ray commands, execution sets, preprocessing, ordering, shader records, and payload checks. |

### New EXT families

The root dispatcher now places the existing ray-tracing tests under `dgc.ext.ray_tracing.basic` and adds `dgc.ext.ray_tracing.conditional_rendering` and `dgc.ext.stat_query` ([registration](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L112-L123)). The existing [RayTracingExt](../testfiles/dgc/RayTracingExt.md) page covers `basic`; the new families have the following source-backed scope.

- `dgc.ext.ray_tracing.conditional_rendering` checks whether a conditional predicate permits or suppresses generated ray-generation work. Its 32 `general` leaves combine ordinary binding or a pipeline token, count-buffer use, predicate value, inversion, and universal or compute queue execution. Its 12 `preprocess` leaves vary predicate, inversion, separate state, and execution queue; compute-queue execution requires separate state. Both families expect the raygen shader to write push constant `777` when the effective predicate is true and leave the initialized output at `0` otherwise. The shader performs no ray traversal. Support checks require ray-tracing pipelines, conditional rendering, DGC raygen-stage support, and the requested pipeline-binding or compute-queue capability. See [support and shader](../../modules/vulkan/device_generated_commands/vktDGCRayTracingConditionalTestsExt.cpp#L74-L131), [general result check](../../modules/vulkan/device_generated_commands/vktDGCRayTracingConditionalTestsExt.cpp#L326-L341), [preprocess check and registration](../../modules/vulkan/device_generated_commands/vktDGCRayTracingConditionalTestsExt.cpp#L590-L667), and [44 mustpass leaves](../../mustpass/main/vk-default/dgc.txt#L4332-L4375).
- `dgc.ext.stat_query` checks pipeline statistics around generated execution and also checks the resulting storage buffer or rendered colors. Its 120 leaves combine ten statistic selections (`input_vert`, `input_prim`, `vert_inv`, `geom_inv`, `geom_prim`, `frag_inv`, `tesc_patch`, `tese_inv`, `comp_inv`, `task_mesh_inv`), three construction modes (`monolithic`, `fast_lib`, `shader_obj`), optional `_ies`, and optional `_preprocess`. The test checks exact counts for input assembly, geometry primitives, tessellation-control patches, and task/mesh invocations; other invocation checks use lower bounds. The fragment lower bound accounts for the reported maximum fragment size when fragment shading rate is available. Support checks require `pipelineStatisticsQuery`, DGC support for the selected stages and binding mode, the construction-mode requirements, and any selected geometry, tessellation, or task/mesh query features. See [support](../../modules/vulkan/device_generated_commands/vktDGCStatQueryTestsExt.cpp#L177-L203), [query recording](../../modules/vulkan/device_generated_commands/vktDGCStatQueryTestsExt.cpp#L1038-L1080), [output and statistic checks](../../modules/vulkan/device_generated_commands/vktDGCStatQueryTestsExt.cpp#L1087-L1390), [registration](../../modules/vulkan/device_generated_commands/vktDGCStatQueryTestsExt.cpp#L1404-L1449), and [120 mustpass leaves](../../mustpass/main/vk-default/dgc.txt#L4376-L4495).

## Category Notes

The preserved `vkt*.md` files remain the original source-navigation pages. The shortened CamelCase pages above are the rewritten English documents. Understanding Briefs remain internal rewrite aids and are not navigation targets.
