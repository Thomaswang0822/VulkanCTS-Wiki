# vktMeshShaderProvokingVertexTestsEXT

## Overview

EXT provoking vertex tests cover line and triangle geometry with first/last provoking vertex modes.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderProvokingVertexTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderProvokingVertexTestsEXT.cpp#L450).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderProvokingVertexTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderProvokingVertexTestsEXT.cpp) |
| Registration code | [vktMeshShaderProvokingVertexTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderProvokingVertexTestsEXT.cpp#L450) |

## Registration Hierarchy

```text
mesh_shader.ext.provoking_vertex
├── lines
└── triangles
```

## Test Families

### lines — Registered child

The `lines` child is documented from the registration tree for `mesh_shader.ext.provoking_vertex` and from the implementation source [vktMeshShaderProvokingVertexTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderProvokingVertexTestsEXT.cpp#L450).
### triangles — Registered child

The `triangles` child is documented from the registration tree for `mesh_shader.ext.provoking_vertex` and from the implementation source [vktMeshShaderProvokingVertexTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderProvokingVertexTestsEXT.cpp#L450).

## Parameter Dimensions

Each geometry group contains first, last, first-to-last, and last-to-first provoking vertex mode sequences.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
