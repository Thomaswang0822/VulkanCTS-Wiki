# [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1)

## Overview

[`vktShaderObjectBindingTests.cpp`](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1) implements the `shader_object/binding` branch. It registers shader binding, swap, disabled-stage, draw/dispatch interleaving, mesh swap, general `bindings`, and unbind families under the verified group `binding` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2074-L2200). Verification uses rendered color comparisons and storage-buffer checks for draw/dispatch and unbind scenarios at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L600-L652), [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1240-L1267), and [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1858-L1965).

## Role of File

Implementation-heavy test file for the root-level `binding` branch.

## Source Code

- Primary source: [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Path

```text
shader_object
+-- binding
    +-- unbind_passthrough_geom
    +-- swap_{vert,tesc,tese,geom,frag}
    +-- swap_*_unused_output_*_binary_*_{before,after}
    +-- unbind_{tesc,geom}_{null_pshaders,null_handle}
    +-- mesh_swap_{task,mesh}
    +-- disabled_{geom,tess}
    +-- disabled_{geom,tess}_bind
    +-- draw_dispatch_draw
    +-- dispatch_draw_dispatch
    +-- bindings
    +-- bindings_mesh_shaders
    +-- unbind_vtg
    +-- unbind_task_mesh
    +-- unbind_mesh_draw_vertex
```

Explicit registration path prefixes for verifier extraction:

```text
`shader_object.binding`
`shader_object.binding.unbind_passthrough_geom`
`shader_object.binding.swap_vert`
`shader_object.binding.mesh_swap_task`
`shader_object.binding.bindings`
`shader_object.binding.unbind_vtg`
```

The displayed branch name is verified from `TestCaseGroup(testCtx, "binding")` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2074-L2076). The root file registers this branch directly at [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57).

## Test Hierarchy

```text
binding
+-- BindingDrawParams cases
+-- MeshBindingDrawParams cases
+-- BindingParams cases
+-- UnbindParams cases
```

## Test Families

### Graphics binding, swap, disabled-stage, and draw/dispatch cases

`BindingDrawParams` defines the core dimensions for graphics and compute/draw interleaving: test type, stage, unused-output stage, binary stage, unsupported-stage binding, state ordering, and null-unbind style at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L52-L71). Registration creates a baseline `unbind_passthrough_geom`, five simple swap cases, a nested cross product over stage, unused-output stage, binary stage, and state timing, tessellation/geometry unbind cases, disabled-stage cases, and draw/dispatch interleaving cases at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2078-L2184).

### Mesh swap cases

`meshStageTest[]` registers `mesh_swap_task` and `mesh_swap_mesh` using `MeshShaderObjectBindingCase` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2154-L2169).

### General bindings and unbind cases

`bindings` and `bindings_mesh_shaders` exercise binding lists with and without mesh shaders at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2186-L2190). The final unbind family registers `unbind_vtg`, `unbind_task_mesh`, and `unbind_mesh_draw_vertex` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2192-L2198).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Main `TestType` | `PASSTHROUGH_GEOM`, `SWAP`, `DISABLED`, `UNBIND`, `DRAW_DISPATCH_DRAW`, `DISPATCH_DRAW_DISPATCH` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L52-L60) |
| Classic stages | `vert`, `tesc`, `tese`, `geom`, `frag` in `stageTest[]` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2089-L2099) |
| Mesh stages | `task`, `mesh` in `meshStageTest[]` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2154-L2161) |
| Null-unbind style | `null_pshaders` and `null_handle` generated from `unbindWithNullpShaders` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2142-L2150) |
| Mesh binding toggle | `bindings` and `bindings_mesh_shaders` from `BindingParams::useMeshShaders` at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2186-L2190) |
| Final unbind mode | `UNBIND_VTG`, `UNBIND_TASK_MESH`, `UNBIND_MESH_DRAW_VERTEX` registered at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2192-L2198) |

## Support / Feature Requirements

- `ShaderObjectBindingDrawCase` requires `VK_EXT_shader_object`; tessellation and geometry features are required when the selected stage or binary stage uses them at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L677-L689).
- Mesh swap cases require `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, and task/mesh feature support at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1293-L1301).
- Final unbind cases require `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, and task/mesh feature support at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1990-L1998).
- Registration itself is unconditional once the root adds the branch factory at [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57).

## Verification Methods

- Draw/dispatch interleaving checks storage buffers for expected `0..15` values in dispatch paths and otherwise compares each rendered pixel against expected black or colored regions with a numeric threshold at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L600-L652).
- General `bindings` cases execute command-buffer binding sequences and pass if no command execution failure is raised; the inspected `iterate()` returns pass after submitting the command buffer at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L896-L1048).
- Mesh swap cases verify task-stage output `[4, 5, 2, 3]` or mesh-stage output `[0, 1, 6, 7]` in a host-visible buffer at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1240-L1267).
- Final unbind cases compare rendered pixels against white, black, or red regions depending on unbind mode and also check buffer values `[0, 1, 2, 3]` for modes that write side effects at [vktShaderObjectBindingTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1858-L1965).

## Test Principles Observed

- Exercise shader binding order, unbinding style, and unsupported-stage behavior without root-level conditional registration.
- Use both image results and storage-buffer side effects to validate shader-stage binding effects.
- Keep mesh/task binding behavior separate from classic graphics-stage binding behavior.

## Notes / Uncertainties

- The page records the observed pass/fail logic in inspected ranges. It does not enumerate every generated `swap_*_unused_output_*_binary_*` leaf name because those names are a large cross product generated in the registration loop.
