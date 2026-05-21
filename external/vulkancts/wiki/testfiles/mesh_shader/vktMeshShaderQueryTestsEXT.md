# vktMeshShaderQueryTestsEXT

## Overview

EXT query tests cover primitive and mesh/task statistics query combinations.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp) |
| Registration code | [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387) |

## Registration Hierarchy

```text
mesh_shader.ext.query
├── no_queries
├── prim_query
├── task_invs_query
├── mesh_invs_query
├── all_stats_query
└── all_queries
```

## Test Families

### no_queries — Registered child

The `no_queries` child is documented from the registration tree for `mesh_shader.ext.query` and from the implementation source [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).
### prim_query — Registered child

The `prim_query` child is documented from the registration tree for `mesh_shader.ext.query` and from the implementation source [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).
### task_invs_query — Registered child

The `task_invs_query` child is documented from the registration tree for `mesh_shader.ext.query` and from the implementation source [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).
### mesh_invs_query — Registered child

The `mesh_invs_query` child is documented from the registration tree for `mesh_shader.ext.query` and from the implementation source [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).
### all_stats_query — Registered child

The `all_stats_query` child is documented from the registration tree for `mesh_shader.ext.query` and from the implementation source [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).
### all_queries — Registered child

The `all_queries` child is documented from the registration tree for `mesh_shader.ext.query` and from the implementation source [vktMeshShaderQueryTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1387).

## Parameter Dimensions

Dimensions include query type combination, geometry, reset/access method, wait flag, draw call type, result size, availability, draw blocks, task shader, render-pass ordering, multiview, and command-buffer type.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
