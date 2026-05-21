# vktMeshShaderTests

## Overview

The category dispatcher creates `mesh_shader` and separates coverage into `nv` and `ext` branches.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp) |
| Registration code | [vktMeshShaderTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55) |

## Registration Hierarchy

```text
mesh_shader
├── nv
└── ext
```

## Test Families

### nv — Registered child

The `nv` child is documented from the registration tree for `mesh_shader` and from the implementation source [vktMeshShaderTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55).
### ext — Registered child

The `ext` child is documented from the registration tree for `mesh_shader` and from the implementation source [vktMeshShaderTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55).

## Parameter Dimensions

The root file delegates to child factory functions and does not define leaf test parameters itself.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
