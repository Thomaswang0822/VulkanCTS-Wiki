# vktMeshShaderMiscTestsEXT

## Overview

EXT miscellaneous tests cover broad rendering, payload, barrier, geometry, descriptor, and ordering behavior.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp) |
| Registration code | [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708) |

## Registration Hierarchy

```text
mesh_shader.ext.misc
├── complex_task_data
├── single_point
├── single_point_default_size
├── single_line
├── single_triangle
├── max_points
├── max_lines
├── max_triangles_workgroupsize_64
├── max_triangles_workgroupsize_32
├── max_triangles_workgroupsize_16
├── many_task_work_groups_x
├── many_mesh_work_groups_x
├── many_task_mesh_work_groups_x
├── many_task_work_groups_y
├── many_mesh_work_groups_y
├── many_task_mesh_work_groups_y
├── many_task_work_groups_z
├── many_mesh_work_groups_z
├── many_task_mesh_work_groups_z
├── no_points
├── no_lines
├── no_triangles
├── barrier_in_task
├── barrier_in_mesh
├── memory_barrier_shared_in_task_struct
├── memory_barrier_shared_in_task_float
├── memory_barrier_shared_in_task_vector
├── memory_barrier_shared_in_task_array
├── memory_barrier_shared_in_task_uint64
├── memory_barrier_shared_in_mesh_struct
├── memory_barrier_shared_in_mesh_float
├── memory_barrier_shared_in_mesh_vector
├── memory_barrier_shared_in_mesh_array
├── memory_barrier_shared_in_mesh_uint64
├── group_memory_barrier_in_task_struct
├── group_memory_barrier_in_task_float
├── group_memory_barrier_in_task_vector
├── group_memory_barrier_in_task_array
├── group_memory_barrier_in_task_uint64
├── group_memory_barrier_in_mesh_struct
├── group_memory_barrier_in_mesh_float
├── group_memory_barrier_in_mesh_vector
├── group_memory_barrier_in_mesh_array
├── group_memory_barrier_in_mesh_uint64
├── custom_attributes
├── custom_attributes_and_task_shader
├── clip_geom
├── clip_geom_multiview
├── clip_geom_provoking_last
├── clip_geom_provoking_last_multiview
├── clip_geom_and_task_shader
├── clip_geom_and_task_shader_multiview
├── clip_geom_and_task_shader_provoking_last
├── clip_geom_and_task_shader_provoking_last_multiview
├── clip_plane
├── clip_plane_multiview
├── clip_plane_provoking_last
├── clip_plane_provoking_last_multiview
├── clip_plane_and_task_shader
├── clip_plane_and_task_shader_multiview
├── clip_plane_and_task_shader_provoking_last
├── clip_plane_and_task_shader_provoking_last_multiview
├── push_constant
├── push_constant_and_task_shader
├── maximize_primitives
├── maximize_vertices
├── maximize_invocations_32
├── maximize_invocations_64
├── maximize_invocations_128
├── maximize_invocations_256
├── mixed_pipelines
├── mixed_pipelines_dynamic_topology
├── first_invocation_mesh
├── first_invocation_task
├── local_size_id_mesh
├── local_size_id_task
├── payload_read
├── rebind_sets
├── multiple_outputs_vertices
├── payload_not_accessed
├── emit_in_control_flow
├── emit_in_control_flow_bad_emit_last
└── work_group_ordering
```

## Test Families

### complex_task_data — Registered child

The `complex_task_data` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### single_point — Registered child

The `single_point` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### single_point_default_size — Registered child

The `single_point_default_size` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### single_line — Registered child

The `single_line` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### single_triangle — Registered child

The `single_triangle` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### max_points — Registered child

The `max_points` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### max_lines — Registered child

The `max_lines` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### max_triangles_workgroupsize_64 — Registered child

The `max_triangles_workgroupsize_64` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### max_triangles_workgroupsize_32 — Registered child

The `max_triangles_workgroupsize_32` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### max_triangles_workgroupsize_16 — Registered child

The `max_triangles_workgroupsize_16` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_task_work_groups_x — Registered child

The `many_task_work_groups_x` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_mesh_work_groups_x — Registered child

The `many_mesh_work_groups_x` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_task_mesh_work_groups_x — Registered child

The `many_task_mesh_work_groups_x` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_task_work_groups_y — Registered child

The `many_task_work_groups_y` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_mesh_work_groups_y — Registered child

The `many_mesh_work_groups_y` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_task_mesh_work_groups_y — Registered child

The `many_task_mesh_work_groups_y` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_task_work_groups_z — Registered child

The `many_task_work_groups_z` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_mesh_work_groups_z — Registered child

The `many_mesh_work_groups_z` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### many_task_mesh_work_groups_z — Registered child

The `many_task_mesh_work_groups_z` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### no_points — Registered child

The `no_points` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### no_lines — Registered child

The `no_lines` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### no_triangles — Registered child

The `no_triangles` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### barrier_in_task — Registered child

The `barrier_in_task` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### barrier_in_mesh — Registered child

The `barrier_in_mesh` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### memory_barrier_shared_in_task_struct — Registered child

The `memory_barrier_shared_in_task_struct` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### memory_barrier_shared_in_mesh_struct — Registered child

The `memory_barrier_shared_in_mesh_struct` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### group_memory_barrier_in_task_struct — Registered child

The `group_memory_barrier_in_task_struct` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### group_memory_barrier_in_mesh_struct — Registered child

The `group_memory_barrier_in_mesh_struct` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### custom_attributes — Registered child

The `custom_attributes` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### custom_attributes_and_task_shader — Registered child

The `custom_attributes_and_task_shader` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### clip_geom — Registered child

The `clip_geom` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### clip_plane — Registered child

The `clip_plane` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### push_constant — Registered child

The `push_constant` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### push_constant_and_task_shader — Registered child

The `push_constant_and_task_shader` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### maximize_primitives — Registered child

The `maximize_primitives` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### maximize_vertices — Registered child

The `maximize_vertices` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### maximize_invocations_32 — Registered child

The `maximize_invocations_32` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### maximize_invocations_64 — Registered child

The `maximize_invocations_64` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### maximize_invocations_128 — Registered child

The `maximize_invocations_128` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### maximize_invocations_256 — Registered child

The `maximize_invocations_256` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### mixed_pipelines — Registered child

The `mixed_pipelines` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### mixed_pipelines_dynamic_topology — Registered child

The `mixed_pipelines_dynamic_topology` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### first_invocation_mesh — Registered child

The `first_invocation_mesh` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### first_invocation_task — Registered child

The `first_invocation_task` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### local_size_id_mesh — Registered child

The `local_size_id_mesh` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### local_size_id_task — Registered child

The `local_size_id_task` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### payload_read — Registered child

The `payload_read` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### rebind_sets — Registered child

The `rebind_sets` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### multiple_outputs_vertices — Registered child

The `multiple_outputs_vertices` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### payload_not_accessed — Registered child

The `payload_not_accessed` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### emit_in_control_flow — Registered child

The `emit_in_control_flow` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### emit_in_control_flow_bad_emit_last — Registered child

The `emit_in_control_flow_bad_emit_last` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).
### work_group_ordering — Registered child

The `work_group_ordering` child is documented from the registration tree for `mesh_shader.ext.misc` and from the implementation source [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708).

## Parameter Dimensions

Dimensions include 3D task/mesh counts, dimension suffix, primitive type, task usage, memory-barrier payload type (`struct`, `float`, `vector`, `array`, `uint64`), clip/provoking/multiview toggles, invocation count, and dynamic topology. Extra-write no-primitive variants and `multiple_task_payloads` are present only in disabled or skipped source branches and are not registered children [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6888-L6895), [vktMeshShaderMiscTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L7138-L7147).

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
