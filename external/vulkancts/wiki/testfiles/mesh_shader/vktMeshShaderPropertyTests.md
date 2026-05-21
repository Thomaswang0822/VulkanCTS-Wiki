# vktMeshShaderPropertyTests

## Overview

NV property tests check required mesh-shader limit properties.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp) |
| Registration code | [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669) |

## Registration Hierarchy

```text
mesh_shader.nv.property
├── max_draw_mesh_tasks_count_with_task
├── max_draw_mesh_tasks_count_with_mesh
├── max_task_work_group_invocations
├── max_task_work_group_size
├── max_task_output_count
├── max_mesh_work_group_invocations
├── max_mesh_work_group_size
├── max_task_total_memory_size
└── max_mesh_total_memory_size
```

## Test Families

### max_draw_mesh_tasks_count_with_task — Registered child

The `max_draw_mesh_tasks_count_with_task` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_draw_mesh_tasks_count_with_mesh — Registered child

The `max_draw_mesh_tasks_count_with_mesh` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_task_work_group_invocations — Registered child

The `max_task_work_group_invocations` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_task_work_group_size — Registered child

The `max_task_work_group_size` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_task_output_count — Registered child

The `max_task_output_count` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_mesh_work_group_invocations — Registered child

The `max_mesh_work_group_invocations` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_mesh_work_group_size — Registered child

The `max_mesh_work_group_size` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_task_total_memory_size — Registered child

The `max_task_total_memory_size` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).
### max_mesh_total_memory_size — Registered child

The `max_mesh_total_memory_size` child is documented from the registration tree for `mesh_shader.nv.property` and from the implementation source [vktMeshShaderPropertyTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTests.cpp#L669).

## Parameter Dimensions

Each child maps to one advertised property or a task/mesh variant of a property check.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
