# vktMeshShaderMiscTests

## Overview

The NV miscellaneous source contains two factory functions: one creates the `misc` group and one creates the `in_out` group.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5230).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp) |
| `misc` registration code | [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5101) |
| `in_out` registration code | [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5104-L5230) |

## Registration Hierarchy

```text
mesh_shader.nv.misc
├── complex_task_data
├── single_point
├── single_line
├── single_triangle
├── max_points
├── max_lines
├── max_triangles
├── many_task_work_groups
├── many_mesh_work_groups
├── many_task_mesh_work_groups
├── no_points
├── no_lines
├── no_triangles
├── no_points_extra_writes
├── no_lines_extra_writes
├── no_triangles_extra_writes
├── barrier_in_task
├── barrier_in_mesh
├── memory_barrier_shared_in_task
├── memory_barrier_shared_in_mesh
├── group_memory_barrier_in_task
├── group_memory_barrier_in_mesh
├── custom_attributes
├── custom_attributes_and_task_shader
├── push_constant
├── push_constant_and_task_shader
├── maximize_primitives
├── maximize_vertices
├── maximize_invocations_32
├── maximize_invocations_64
├── maximize_invocations_128
├── maximize_invocations_256
└── mixed_pipelines
mesh_shader.nv.in_out
├── 32_bits_only
├── with_i64
├── with_f64
├── all_but_16_bits
├── with_i16
├── with_f16
└── all_types
```

## Test Families

The `misc` factory registers rendering, primitive-emission, barrier, attribute, push-constant, maximization, and mixed-pipeline cases [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5101). The same source file also defines the NV `in_out` factory with seven feature groups and pseudorandom interface-variable permutations [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5104-L5230).

## Parameter Dimensions

The `misc` group covers primitive emission, large workgroups, barriers, attributes, push constants, and mixed pipelines; `in_out` covers feature-grouped interface-variable permutations. The disabled `count_reads` block is guarded by `if (false)` and is not a registered child [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5085-L5095).

## Support and Feature Requirements

NV cases use the NV mesh-shader support helper, which requires `VK_NV_mesh_shader` plus the requested task and/or mesh feature bits [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124). Interface-variable feature groups also gate 64-bit and 16-bit numeric shader features through their case parameters [vktMeshShaderMiscTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L5117-L5123).

## Verification Methods

Verification is implemented by the individual cases in this source file, including rendered-output comparisons and shader-output checks. This page does not claim one common verification method for every child.

## Test Principles

The file contributes two portions of the `mesh_shader` category: it registers tests under the two paths shown above and varies child cases through explicit `addChild` calls, loops, and feature-group arrays.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
