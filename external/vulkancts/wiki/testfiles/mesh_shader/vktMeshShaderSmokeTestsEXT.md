# vktMeshShaderSmokeTestsEXT

## Overview

EXT smoke tests repeat basic rendering across pipeline construction modes.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp) |
| Registration code | [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547) |

## Registration Hierarchy

```text
mesh_shader.ext.smoke
├── monolithic
├── optimized_lib
├── fast_lib
└── shader_objects
```

## Test Families

### monolithic — Registered child

The `monolithic` child is documented from the registration tree for `mesh_shader.ext.smoke` and from the implementation source [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547).
### optimized_lib — Registered child

The `optimized_lib` child is documented from the registration tree for `mesh_shader.ext.smoke` and from the implementation source [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547).
### fast_lib — Registered child

The `fast_lib` child is documented from the registration tree for `mesh_shader.ext.smoke` and from the implementation source [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547).
### shader_objects — Registered child

The `shader_objects` child is documented from the registration tree for `mesh_shader.ext.smoke` and from the implementation source [vktMeshShaderSmokeTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547).

## Parameter Dimensions

The top-level dimension is pipeline construction type; nested cases cover triangles, partial use, gradients, shared fragment libraries/shader objects, and depth-only rendering.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
