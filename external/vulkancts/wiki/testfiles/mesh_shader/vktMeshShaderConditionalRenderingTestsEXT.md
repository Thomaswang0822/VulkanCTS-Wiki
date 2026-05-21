# vktMeshShaderConditionalRenderingTestsEXT

## Overview

EXT conditional rendering tests combine conditional rendering with mesh draw commands.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderConditionalRenderingTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.cpp#L599).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderConditionalRenderingTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.cpp) |
| Registration code | [vktMeshShaderConditionalRenderingTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.cpp#L599) |

## Registration Hierarchy

```text
mesh_shader.ext.conditional_rendering
├── draw
├── draw_indirect
└── draw_indirect_count
```

## Test Families

### draw — Registered child

The `draw` child is documented from the registration tree for `mesh_shader.ext.conditional_rendering` and from the implementation source [vktMeshShaderConditionalRenderingTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.cpp#L599).
### draw_indirect — Registered child

The `draw_indirect` child is documented from the registration tree for `mesh_shader.ext.conditional_rendering` and from the implementation source [vktMeshShaderConditionalRenderingTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.cpp#L599).
### draw_indirect_count — Registered child

The `draw_indirect_count` child is documented from the registration tree for `mesh_shader.ext.conditional_rendering` and from the implementation source [vktMeshShaderConditionalRenderingTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.cpp#L599).

## Parameter Dimensions

Dimensions include draw type, command-buffer type, binding offset, condition offset, inversion, task usage, condition value, and multiview.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
