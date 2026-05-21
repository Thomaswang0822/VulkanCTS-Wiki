# vktFragmentShadingBarycentricTests.cpp

This page documents the single registered source file for the Vulkan CTS `fragment_shading_barycentric` category.

## Overview

[`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1) registers the complete `fragment_shading_barycentric` tree. The root `createTests()` function constructs the category group, adds `data` and `weights` groups to the monolithic root, and also adds `pipeline_library` and `fast_linked_library` groups containing analogous construction-type permutations at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2642-L3150).

## Role of File

- Root registration and implementation-heavy file.
- It defines data-validation and weight-validation instances, support checks, shader generation, and all registration loops in the same source file.

## Registration Hierarchy

```text
fragment_shading_barycentric
├── data
├── weights
├── pipeline_library
└── fast_linked_library
```

## Test Families

### data — Per-vertex barycentric data propagation

The `data` group is created for each pipeline construction type at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2740-L2743). Its descendants vary provoking vertex mode, static versus dynamic indexing, primitive topology, clipping, aggregate shape, GLSL data type, interpolation type, and vertex versus mesh shader paths at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2745-L2860). The group also includes `misc.pervertex_correctness` and `shader_combos` descendants at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2863-L2940).

### weights — Barycentric weight behavior

The `weights` group is created at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2946-L2963). Its descendants cover provoking vertex mode, static versus dynamic topology-in-pipeline, MSAA/interpolation subtypes, rotations, topologies, perspective versus noperspective interpolation, and vertex versus mesh shader paths at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2972-L3143).

### pipeline_library — Link-time optimized graphics pipeline-library variants

`pipeline_library` is a root-level group constructed before registration loops and associated with `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY` at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2646-L2658). It receives its own `data` and `weights` subtrees during the same loops.

### fast_linked_library — Fast-linked graphics pipeline-library variants

`fast_linked_library` is constructed at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2647-L2659) and receives analogous `data` and `weights` descendants before both library groups are added to the root at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L3146-L3147).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Pipeline construction type | Monolithic root, `pipeline_library`, and `fast_linked_library` from `constructionTypeCases[]` at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2646-L2659) |
| Primitive topology | Point, line, triangle, strip/fan, and adjacency topology names listed at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2661-L2676) |
| Data types | Float, double, signed integer, unsigned integer scalar/vector types at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2693-L2698) |
| Data interpolation modes | `per_vertex`, `per_vertex_interp`, `per_vertex_flat`, with interpolated integer/double cases skipped at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2732-L2738) and [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2797-L2803) |
| Weights subtypes | `single_sample` and several 4x MSAA interpolation/qualifier cases from `msaaCases[]` at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2948-L2960) |
| Mesh shader path | `mesh_shader` and `vertex_shader`, with mesh shader cases limited to point, line, and triangle lists at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2685-L2692) and [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2812-L2816) |

## Support / Feature Requirements

Each test case requires `VK_KHR_fragment_shader_barycentric` and the `fragmentShaderBarycentric` feature at [`FragmentShadingBarycentricTestCase::checkSupport()`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1494-L1506). Conditional requirements include `VK_EXT_provoking_vertex` and `provokingVertexLast`, `VK_EXT_extended_dynamic_state` for dynamic topology, `VK_EXT_mesh_shader` and `meshShader` for mesh shader cases, `shaderFloat64` for double data, tessellation/geometry shader core features for shader-combo subtypes, and sample-rate shading for MSAA subtypes at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1512-L1567).

## Verification Methods

Data cases render into an `R32G32B32A32_UINT` image, copy it to a host-visible buffer, and call `verify()` to decide pass/fail at [`FragmentShadingBarycentricDataTestInstance::iterate()`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L811-L965). Weight cases render both reference and tested outputs and use `tcu::intThresholdCompare` with a threshold of `(1,1,1,1)` at [`FragmentShadingBarycentricWeightTestInstance::verify()`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1251-L1262), returning pass only when the comparison succeeds at [`vktFragmentShadingBarycentricTests.cpp`](../../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1453-L1456).

## Test Principles

The tests exercise SPIR-V/GLSL barycentric inputs through `GL_EXT_fragment_shader_barycentric` / `SPV_KHR_fragment_shader_barycentric` shader paths and compare either encoded per-vertex data or computed weights. The mustpass file confirms root-level paths beginning with `data`, and library-root paths are added by the same source registration loops, with sample entries under `data` visible at [`fragment-shading-barycentric.txt`](../../../mustpass/main/vk-default/fragment-shading-barycentric.txt#L1-L24).

## Notes / Uncertainties

No separate helper-only source file in this category registers tests, so only this Level-3 page is created.
