# vktMeshShaderApiTestsEXT

## Overview

EXT API tests cover mesh draw commands and add secondary-command-buffer and device-address-command variants.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp) |
| Registration code | [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783) |

## Registration Hierarchy

```text
mesh_shader.ext.api
├── draw
├── draw_indirect
└── draw_indirect_count
```

## Test Families

### draw — Registered child

The `draw` child is documented from the registration tree for `mesh_shader.ext.api` and from the implementation source [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783).
### draw_indirect — Registered child

The `draw_indirect` child is documented from the registration tree for `mesh_shader.ext.api` and from the implementation source [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783).
### draw_indirect_count — Registered child

The `draw_indirect_count` child is documented from the registration tree for `mesh_shader.ext.api` and from the implementation source [vktMeshShaderApiTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783).

## Parameter Dimensions

Dimensions include draw type/count, indirect arguments, count limits, count offsets, task usage, secondary command buffers, and selected device-address-command leaves.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
