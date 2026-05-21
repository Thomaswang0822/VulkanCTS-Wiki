# vktMeshShaderBuiltinTestsEXT

## Overview

EXT built-in source contains two factory functions: `builtin` registers built-in-variable cases, while `pipeline` registers pipeline-construction built-in cases.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderBuiltinTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2560).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderBuiltinTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp) |
| Registration code | [vktMeshShaderBuiltinTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2560) |

## Registration Hierarchy

```text
mesh_shader.ext.builtin
├── position
├── point_size
├── clip_distance
├── clip_distance_mix
├── cull_distance
├── cull_distance_mix
├── primitive_id_glsl
├── primitive_id_spirv
├── layer
├── layer_shared
├── layer_no_write
├── viewport_index
├── viewport_index_shared
├── viewport_index_no_write
├── work_group_id_in_mesh
├── work_group_id_in_task
├── num_work_groups_mesh
├── num_work_groups_task_and_mesh
├── local_invocation_id_in_mesh
├── local_invocation_id_in_task
├── local_invocation_index_in_task
├── local_invocation_index_in_mesh
├── global_invocation_id_in_mesh
├── global_invocation_id_in_task
├── draw_index_in_mesh
├── draw_index_in_task
├── view_index
├── cull_primitives
├── primitive_shading_rate_2x2_2x2
├── primitive_shading_rate_2x2_2x1
├── primitive_shading_rate_2x2_1x1
├── primitive_shading_rate_2x1_2x2
├── primitive_shading_rate_2x1_2x1
├── primitive_shading_rate_2x1_1x1
├── primitive_shading_rate_1x1_2x2
├── primitive_shading_rate_1x1_2x1
└── primitive_shading_rate_1x1_1x1
mesh_shader.ext.pipeline
└── builtin
```

## Test Families

### builtin — Registered child

The `builtin` root registers explicit built-in cases plus generated primitive-shading-rate cases [vktMeshShaderBuiltinTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2560-L2620).
### pipeline — Registered root

The `pipeline` root contains a `builtin` subgroup with optimized-library, fast-library, and shader-object construction modes below it [vktMeshShaderBuiltinTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2623-L2651).

## Parameter Dimensions

The `builtin` root contains explicit built-in cases and generated primitive-shading-rate cases; `pipeline` contains a `builtin` subgroup with optimized-library, fast-library, and shader-object construction children.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
