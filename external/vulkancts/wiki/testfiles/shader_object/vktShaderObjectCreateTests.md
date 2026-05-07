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

## Registration Path

```text
shader_object
+-- create
    +-- multiple
    |   +-- all
    |   +-- all_with_mesh
    +-- vert/{succeed,fail}
    +-- tesc/{succeed,fail}
    +-- tese/{succeed,fail}
    +-- geom/{succeed,fail}
    +-- frag/{succeed,fail}
    +-- comp/{succeed,fail}
    +-- mesh/{succeed,fail}
    +-- task/{succeed,fail}
    +-- all/{succeed,fail}
    +-- all_with_mesh/{succeed,fail}
```

Explicit registration path prefixes for verifier extraction:

```text
`shader_object.create`
`shader_object.create.multiple.all`
`shader_object.create.vert.succeed`
`shader_object.create.comp.fail`
```

Evidence: `createShaderObjectCreateTests()` constructs the group named `create`, registers `multiple`, and iterates `stageTests[]` with `failTests[]` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L829-L878).

## Test Hierarchy

```text
create
+-- multiple
+-- (stage groups from stageTests[])
    +-- succeed
    +-- fail
```

## Test Families

### Multiple shader creation

The `multiple` subgroup registers `all` and `all_with_mesh` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L833-L838). The implementation creates shader objects separately and together, destroys them, and fails if expected comparison state does not match at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L300-L312).

### Stage create success/failure matrix

`stageTests[]` covers vertex, tessellation-control, tessellation-evaluation, geometry, fragment, compute, mesh, task, all stages without mesh, and all stages with mesh at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L840-L856). Each stage group receives `succeed` and `fail` child cases from `failTests[]` at [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L858-L875).

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
