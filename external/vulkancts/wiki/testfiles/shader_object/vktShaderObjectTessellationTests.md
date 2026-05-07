# [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L1)

## Overview

[`vktShaderObjectTessellationTests.cpp`](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L1) implements the `shader_object/tessellation` branch. It registers GLSL and HLSL tessellation shader-object tests for orientation, spacing, patch vertex count, primitive mode, and point mode, each with and without a rebind suffix.

## Role of File

Implementation-heavy test file for the root-level `tessellation` branch.

## Source Code

- Primary source: [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L54)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [vktShaderObjectCreateUtil.hpp](../../../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)
- [CMakeLists.txt](../../../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Path

```text
shader_object
+-- tessellation
    +-- glsl
    |   +-- orientation_ccw[_rebind]
    |   +-- orientation_cw[_rebind]
    |   +-- spacing_equal[_rebind]
    |   +-- spacing_fractional_odd[_rebind]
    |   +-- patch_vertices_4[_rebind]
    |   +-- patch_vertices_5[_rebind]
    |   +-- primitive_quads[_rebind]
    |   +-- primitive_triangles[_rebind]
    |   +-- point_mode[_rebind]
    +-- hlsl
        +-- same test names as glsl
```

Explicit registration path prefixes for verifier extraction:

```text
`shader_object.tessellation`
`shader_object.tessellation.glsl.orientation_ccw`
`shader_object.tessellation.hlsl.point_mode_rebind`
```

Evidence: `createShaderObjectTessellationTests()` constructs `tessellation`, iterates `sourceTypeTests[]`, `testTypes[]`, and `rebind` values at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L929-L975).

## Test Hierarchy

```text
tessellation
+-- glsl
+-- hlsl
```

Each source-language group receives nine test types, each registered once with no suffix and once with `_rebind`.

## Test Families

### Source-language variants

`sourceTypeTests[]` registers `glsl` and `hlsl` groups at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L933-L940).

### Tessellation mode variants

`TestType` defines orientation, spacing, patch-vertex, primitive, and point-mode variants at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L51-L62), and `testTypes[]` maps them to registered names at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L942-L956).

### Rebind variants

Each test type is registered twice by iterating `{false, true}` and appending `_rebind` for the true case at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L962-L969).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Source type | `GLSL`, `HLSL` at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L45-L49) |
| Test type | nine `TestType` enum values at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L51-L62) |
| Rebind | `false`, `true` from loop at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L964-L968) |

## Support / Feature Requirements

- Requires `VK_EXT_shader_object` at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L415-L418).
- Requires tessellation shader support; lack of `tessellationShader` throws `NotSupportedError` at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L418-L420).

## Verification Methods

The inspected implementation creates a color attachment image and render area at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L104-L120), and shader source generation is parameterized in `initPrograms()` at [vktShaderObjectTessellationTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L422-L430). Exact image-comparison criteria were not fully expanded in this stage.

## Test Principles Observed

- Exercise tessellation shader-object behavior across source language, tessellation mode, and rebinding dimensions.
- Gate the branch at test-case level on shader-object and tessellation feature support.

## Notes / Uncertainties

- The exact rendered-output verification logic inside `ShaderObjectTessellationInstance::iterate()` was not fully inspected in this stage.
