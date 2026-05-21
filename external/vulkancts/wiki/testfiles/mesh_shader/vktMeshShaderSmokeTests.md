# vktMeshShaderSmokeTests

## Overview

NV smoke tests cover basic mesh/task drawing and fullscreen-gradient rendering.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp) |
| Registration code | [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137) |

## Registration Hierarchy

```text
mesh_shader.nv.smoke
├── mesh_shader_triangle
├── mesh_task_shader_triangle
├── task_only_shader_triangle
├── fullscreen_gradient
├── fullscreen_gradient_fs2x2
└── fullscreen_gradient_fs2x1
```

## Test Families

### mesh_shader_triangle — Registered child

The `mesh_shader_triangle` child is documented from the registration tree for `mesh_shader.nv.smoke` and from the implementation source [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).
### mesh_task_shader_triangle — Registered child

The `mesh_task_shader_triangle` child is documented from the registration tree for `mesh_shader.nv.smoke` and from the implementation source [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).
### task_only_shader_triangle — Registered child

The `task_only_shader_triangle` child is documented from the registration tree for `mesh_shader.nv.smoke` and from the implementation source [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).
### fullscreen_gradient — Registered child

The `fullscreen_gradient` child is documented from the registration tree for `mesh_shader.nv.smoke` and from the implementation source [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).
### fullscreen_gradient_fs2x2 — Registered child

The `fullscreen_gradient_fs2x2` child is documented from the registration tree for `mesh_shader.nv.smoke` and from the implementation source [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).
### fullscreen_gradient_fs2x1 — Registered child

The `fullscreen_gradient_fs2x1` child is documented from the registration tree for `mesh_shader.nv.smoke` and from the implementation source [vktMeshShaderSmokeTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137).

## Parameter Dimensions

Parameters include mesh-only, task+mesh, task-only, and optional fragment-size values for gradient cases.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
