# [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L1)

## Overview

[`vktShaderObjectCreateTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L1) implements the `shader_object/create` branch. It covers creating multiple shader objects together and per-stage shader creation cases that are expected either to succeed or fail.

## Role of File

Implementation-heavy test file for the root-level `create` branch.

## Source Code

- Primary source: [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L52)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Hierarchy

```text
shader_object.create
├── multiple
├── vert
├── tesc
├── tese
├── geom
├── frag
├── comp
├── mesh
├── task
├── all
└── all_with_mesh
```

Evidence: `createShaderObjectCreateTests()` constructs the group named `create`, registers `multiple`, and iterates `stageTests[]` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L829-L878).

## Test Families

### multiple — Multiple shader creation

The `multiple` subgroup registers `all` and `all_with_mesh` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L833-L838). The implementation creates shader objects separately and together, destroys them, and fails if expected comparison state does not match at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L300-L312).

### vert — Vertex stage create success/failure

Stage group for vertex shader creation, receiving `succeed` and `fail` child cases from `failTests[]` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L858-L875).

### tesc — Tessellation control stage create success/failure

Stage group for tessellation control shader creation, receiving `succeed` and `fail` child cases. Requires tessellation shader feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L698-L702).

### tese — Tessellation evaluation stage create success/failure

Stage group for tessellation evaluation shader creation, receiving `succeed` and `fail` child cases. Requires tessellation shader feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L698-L702).

### geom — Geometry stage create success/failure

Stage group for geometry shader creation, receiving `succeed` and `fail` child cases. Requires geometry shader feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L698-L702).

### frag — Fragment stage create success/failure

Stage group for fragment shader creation, receiving `succeed` and `fail` child cases.

### comp — Compute stage create success/failure

Stage group for compute shader creation, receiving `succeed` and `fail` child cases.

### mesh — Mesh stage create success/failure

Stage group for mesh shader creation, receiving `succeed` and `fail` child cases. Requires `VK_EXT_mesh_shader` and mesh feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L695-L706).

### task — Task stage create success/failure

Stage group for task shader creation, receiving `succeed` and `fail` child cases. Requires `VK_EXT_mesh_shader` and task feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L695-L706).

### all — All stages without mesh create success/failure

Stage group for all shader stages without mesh, receiving `succeed` and `fail` child cases.

### all_with_mesh — All stages with mesh create success/failure

Stage group for all shader stages including mesh/task, receiving `succeed` and `fail` child cases. Requires `VK_EXT_mesh_shader` and task/mesh feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L695-L706).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `mesh`, `task`, `all`, `all_with_mesh` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L845-L856) |
| Expected outcome | `succeed`, `fail` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L858-L865) |
| Mesh-shader usage | `useMeshShaders` in `ShaderObjectCreateInstance` and `ShaderObjectStageCase` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L49-L61) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L667-L689) |

## Support / Feature Requirements

- Shader-object create cases require `VK_EXT_shader_object` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L338-L341) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L692-L694).
- Stage cases requiring mesh/task shaders require `VK_EXT_mesh_shader` and task/mesh feature support at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L695-L706).
- Tessellation and geometry stage cases require the corresponding core features at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L698-L702).

## Verification Methods

- Multiple create cases compare behavior between separate and combined shader creation and fail on mismatch at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L300-L312).
- Stage tests generate per-stage GLSL sources for ten variants in `initPrograms()` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L709-L824); exact success/failure criteria are implemented in the unexpanded `ShaderObjectStageInstance::iterate()` body.

## Test Principles Observed

- Exercise shader-object creation both as a batch and as stage-specific operations.
- Include graphics, compute, tessellation, geometry, task, and mesh stage coverage, guarded by required features.

## Notes / Uncertainties

- The detailed result handling inside `ShaderObjectStageInstance::iterate()` was not fully expanded in this stage; the registered success/failure matrix is documented from registration and support code.
