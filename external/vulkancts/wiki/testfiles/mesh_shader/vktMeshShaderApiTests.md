# vktMeshShaderApiTests

## Overview

NV API tests cover direct, indirect, and indirect-count mesh draw commands.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderApiTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp#L658).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderApiTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp) |
| Registration code | [vktMeshShaderApiTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp#L658) |

## Registration Hierarchy

```text
mesh_shader.nv.api
├── draw
├── draw_indirect
└── draw_indirect_count
```

## Test Families

### draw — Registered child

The `draw` child is documented from the registration tree for `mesh_shader.nv.api` and from the implementation source [vktMeshShaderApiTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp#L658).
### draw_indirect — Registered child

The `draw_indirect` child is documented from the registration tree for `mesh_shader.nv.api` and from the implementation source [vktMeshShaderApiTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp#L658).
### draw_indirect_count — Registered child

The `draw_indirect_count` child is documented from the registration tree for `mesh_shader.nv.api` and from the implementation source [vktMeshShaderApiTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp#L658).

## Parameter Dimensions

Dimensions include draw count, indirect offset/stride, count-limit mode, count offset, task usage, and first-task values.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
