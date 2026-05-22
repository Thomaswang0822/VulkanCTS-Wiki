# DGC Tests

The `dgc` category documents Vulkan CTS device-generated-command coverage under the source directory [device_generated_commands](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L25-L54). The root registration file builds the top-level `nv` and `ext` branches and attaches compute, graphics, misc, and ray tracing subgroups through explicit `TestCaseGroup` and `addChild()` calls in [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L68-L120).

## Registration Entry Point

```text
dgc
├── nv
└── ext
```

The immediate top-level names are verified by the root group construction in [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L72-L120) and by the mustpass paths in [dgc.txt](../../mustpass/main/vk-default/dgc.txt#L1).

## Subgroup Structure

- `dgc.nv.compute` contains `get_info`, `smoke`, `layout`, `misc`, `preprocess`, `subgroups`, and `conditional_rendering`, registered from [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L75-L88).
- `dgc.nv.misc` contains `properties`, registered from [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L76-L93).
- `dgc.ext.compute` mirrors the compute families for the EXT extension path, registered from [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L78-L101).
- `dgc.ext.misc` contains `properties`, registered from [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L79-L115).
- `dgc.ext.graphics` contains draw, draw-count, conditional-rendering, mesh, miscellaneous, transform-feedback, tessellation-state, and multiview groups, registered from [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L80-L116).
- `dgc.ext.ray_tracing` is registered directly under the EXT branch from [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L117-L120).

## File Inventory

| Registration path | Level-3 page | Role | Registration evidence |
|---|---|---|---|
| `dgc` | [vktDGCTests](../testfiles/dgc/vktDGCTests.md) | registration dispatcher | [source](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L70) |
| `dgc.nv.compute.get_info` | [vktDGCComputeGetInfoTests](../testfiles/dgc/vktDGCComputeGetInfoTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTests.cpp#L386) |
| `dgc.nv.compute.smoke` | [vktDGCComputeSmokeTests](../testfiles/dgc/vktDGCComputeSmokeTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L558) |
| `dgc.nv.compute.layout` | [vktDGCComputeLayoutTests](../testfiles/dgc/vktDGCComputeLayoutTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L756) |
| `dgc.nv.compute.misc` | [vktDGCComputeMiscTests](../testfiles/dgc/vktDGCComputeMiscTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L737) |
| `dgc.nv.compute.preprocess` | [vktDGCComputePreprocessTests](../testfiles/dgc/vktDGCComputePreprocessTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502) |
| `dgc.nv.compute.subgroups` | [vktDGCComputeSubgroupTests](../testfiles/dgc/vktDGCComputeSubgroupTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L363) |
| `dgc.nv.compute.conditional_rendering` | [vktDGCComputeConditionalTests](../testfiles/dgc/vktDGCComputeConditionalTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L619) |
| `dgc.nv.misc.properties` | [vktDGCPropertyTests](../testfiles/dgc/vktDGCPropertyTests.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1236) |
| `dgc.ext.compute.get_info` | [vktDGCComputeGetInfoTestsExt](../testfiles/dgc/vktDGCComputeGetInfoTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L260) |
| `dgc.ext.compute.smoke` | [vktDGCComputeSmokeTestsExt](../testfiles/dgc/vktDGCComputeSmokeTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L588) |
| `dgc.ext.compute.layout` | [vktDGCComputeLayoutTestsExt](../testfiles/dgc/vktDGCComputeLayoutTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1161) |
| `dgc.ext.compute.misc` | [vktDGCComputeMiscTestsExt](../testfiles/dgc/vktDGCComputeMiscTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2523) |
| `dgc.ext.compute.preprocess` | [vktDGCComputePreprocessTestsExt](../testfiles/dgc/vktDGCComputePreprocessTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L531) |
| `dgc.ext.compute.subgroups` | [vktDGCComputeSubgroupTestsExt](../testfiles/dgc/vktDGCComputeSubgroupTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L360) |
| `dgc.ext.compute.conditional_rendering` | [vktDGCComputeConditionalTestsExt](../testfiles/dgc/vktDGCComputeConditionalTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L593) |
| `dgc.ext.misc.properties` | [vktDGCPropertyTestsExt](../testfiles/dgc/vktDGCPropertyTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L817) |
| `dgc.ext.graphics.draw` | [vktDGCGraphicsDrawTestsExt](../testfiles/dgc/vktDGCGraphicsDrawTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2074) |
| `dgc.ext.graphics.draw_count` | [vktDGCGraphicsDrawCountTestsExt](../testfiles/dgc/vktDGCGraphicsDrawCountTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1471) |
| `dgc.ext.graphics.conditional_rendering` | [vktDGCGraphicsConditionalTestsExt](../testfiles/dgc/vktDGCGraphicsConditionalTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L510) |
| `dgc.ext.graphics.mesh` | [vktDGCGraphicsMeshTestsExt](../testfiles/dgc/vktDGCGraphicsMeshTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2324) |
| `dgc.ext.graphics.mesh.conditional_rendering` | [vktDGCGraphicsMeshConditionalTestsExt](../testfiles/dgc/vktDGCGraphicsMeshConditionalTestsExt.md) | nested implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L680) |
| `dgc.ext.graphics.misc` | [vktDGCGraphicsMiscTestsExt](../testfiles/dgc/vktDGCGraphicsMiscTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8379) |
| `dgc.ext.graphics.xfb` | [vktDGCGraphicsXfbTestsExt](../testfiles/dgc/vktDGCGraphicsXfbTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L887) |
| `dgc.ext.graphics.tess_state` | [vktDGCGraphicsTessStateTestsExt](../testfiles/dgc/vktDGCGraphicsTessStateTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1162) |
| `dgc.ext.graphics.multiview` | [vktDGCGraphicsMultiviewTestsExt](../testfiles/dgc/vktDGCGraphicsMultiviewTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L828) |
| `dgc.ext.ray_tracing` | [vktDGCRayTracingTestsExt](../testfiles/dgc/vktDGCRayTracingTestsExt.md) | implementation | [source](../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1996) |

## Recurring Test Themes

- Compute DGC coverage focuses on command memory requirements, smoke dispatches, token-layout combinations, preprocessing, subgroup builtins, conditional rendering, and miscellaneous execution/property cases. Evidence spans the compute registration block in [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L82-L101).
- Graphics DGC coverage focuses on direct and counted generated draws, conditional rendering, mesh draws, transform feedback, tessellation state, multiview, and broad graphics miscellaneous scenarios. Evidence is in the graphics registration block in [vktDGCTests.cpp](../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L105-L112).
- EXT-specific files add shader objects, execution sets, descriptor heaps/buffers, dynamic pipeline layouts, and ray tracing coverage where their support checks require those features. Examples include [vktDGCComputeLayoutTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L228-L249), [vktDGCGraphicsDrawTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L389-L407), and [vktDGCRayTracingTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L384-L386).

## Recurring Parameter Dimensions

The category repeatedly varies queue selection, preprocessing mode, count buffers or sequence counts, pipeline/shader-object construction, execution sets, and feature-specific dimensions. These dimensions are visible in loops such as compute smoke generation in [vktDGCComputeSmokeTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L600-L617), compute layout generation in [vktDGCComputeLayoutTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1179-L1203), graphics draw generation in [vktDGCGraphicsDrawTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2112-L2155), and ray tracing generation in [vktDGCRayTracingTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1998-L2007).

## Recurring Support Requirements

Support checks require DGC helper support and, depending on the family, features such as conditional rendering, shader objects, mesh shader, graphics pipeline library, descriptor heap/buffer, transform feedback stages, multiview, and ray tracing extensions. Representative source gates include [vktDGCComputeConditionalTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTestsExt.cpp#L74), [vktDGCGraphicsMeshTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L354-L358), [vktDGCGraphicsMultiviewTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L166-L174), and [vktDGCRayTracingTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L384-L386).

## Recurring Verification Methods

DGC tests generally execute generated commands and then compare externally visible results: mapped compute output buffers, rendered color/depth attachments, transform-feedback buffers, property-derived values, or ray tracing payload records. Representative checks include compute output-buffer comparison in [vktDGCComputeLayoutTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1105-L1152), graphics color comparison in [vktDGCGraphicsDrawTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2027-L2066), transform-feedback comparison in [vktDGCGraphicsXfbTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L790-L878), and ray tracing payload checks in [vktDGCRayTracingTestsExt.cpp](../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1839-L1988).

## Scope Notes

- The file inventory is based on DGC source files that register tests and the nested mesh conditional-rendering registration unit. Helper files such as `vktDGCUtil*.cpp` are not given Level-3 pages because they do not register test groups in the inspected evidence.
- The official API test plan prerequisite was inspected, but DGC-specific coverage detail was not found in the inspected plan text; this page therefore relies on implementation and mustpass evidence.
