# [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1)

## Overview

[`vktShaderObjectBindingTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1) implements the `shader_object/binding` branch. It registers shader binding, swap, disabled-stage, draw/dispatch interleaving, mesh swap, general `bindings`, and unbind families under the verified group `binding` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2074-L2200). Verification uses rendered color comparisons and storage-buffer checks for draw/dispatch and unbind scenarios at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L600-L652), [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1240-L1267), and [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1858-L1965).

## Role of File

Implementation-heavy test file for the root-level `binding` branch.

## Source Code

- Primary source: [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Hierarchy

```text
shader_object.binding
├── unbind_passthrough_geom
├── swap_vert
├── swap_tesc
├── swap_tese
├── swap_geom
├── swap_frag
├── swap_vert_unused_output_vert_binary_vert_before
├── swap_vert_unused_output_vert_binary_vert_after
├── swap_vert_unused_output_vert_binary_tesc_before
├── swap_vert_unused_output_vert_binary_tesc_after
├── swap_vert_unused_output_vert_binary_tese_before
├── swap_vert_unused_output_vert_binary_tese_after
├── swap_vert_unused_output_vert_binary_geom_before
├── swap_vert_unused_output_vert_binary_geom_after
├── swap_vert_unused_output_vert_binary_frag_before
├── swap_vert_unused_output_vert_binary_frag_after
├── swap_vert_unused_output_tesc_binary_vert_before
├── swap_vert_unused_output_tesc_binary_vert_after
├── swap_vert_unused_output_tesc_binary_tesc_before
├── swap_vert_unused_output_tesc_binary_tesc_after
├── swap_vert_unused_output_tesc_binary_tese_before
├── swap_vert_unused_output_tesc_binary_tese_after
├── swap_vert_unused_output_tesc_binary_geom_before
├── swap_vert_unused_output_tesc_binary_geom_after
├── swap_vert_unused_output_tesc_binary_frag_before
├── swap_vert_unused_output_tesc_binary_frag_after
├── swap_vert_unused_output_tese_binary_vert_before
├── swap_vert_unused_output_tese_binary_vert_after
├── swap_vert_unused_output_tese_binary_tesc_before
├── swap_vert_unused_output_tese_binary_tesc_after
├── swap_vert_unused_output_tese_binary_tese_before
├── swap_vert_unused_output_tese_binary_tese_after
├── swap_vert_unused_output_tese_binary_geom_before
├── swap_vert_unused_output_tese_binary_geom_after
├── swap_vert_unused_output_tese_binary_frag_before
├── swap_vert_unused_output_tese_binary_frag_after
├── swap_vert_unused_output_geom_binary_vert_before
├── swap_vert_unused_output_geom_binary_vert_after
├── swap_vert_unused_output_geom_binary_tesc_before
├── swap_vert_unused_output_geom_binary_tesc_after
├── swap_vert_unused_output_geom_binary_tese_before
├── swap_vert_unused_output_geom_binary_tese_after
├── swap_vert_unused_output_geom_binary_geom_before
├── swap_vert_unused_output_geom_binary_geom_after
├── swap_vert_unused_output_geom_binary_frag_before
├── swap_vert_unused_output_geom_binary_frag_after
├── swap_vert_unused_output_frag_binary_vert_before
├── swap_vert_unused_output_frag_binary_vert_after
├── swap_vert_unused_output_frag_binary_tesc_before
├── swap_vert_unused_output_frag_binary_tesc_after
├── swap_vert_unused_output_frag_binary_tese_before
├── swap_vert_unused_output_frag_binary_tese_after
├── swap_vert_unused_output_frag_binary_geom_before
├── swap_vert_unused_output_frag_binary_geom_after
├── swap_vert_unused_output_frag_binary_frag_before
├── swap_vert_unused_output_frag_binary_frag_after
├── swap_tesc_unused_output_vert_binary_vert_before
├── swap_tesc_unused_output_vert_binary_vert_after
├── swap_tesc_unused_output_vert_binary_tesc_before
├── swap_tesc_unused_output_vert_binary_tesc_after
├── swap_tesc_unused_output_vert_binary_tese_before
├── swap_tesc_unused_output_vert_binary_tese_after
├── swap_tesc_unused_output_vert_binary_geom_before
├── swap_tesc_unused_output_vert_binary_geom_after
├── swap_tesc_unused_output_vert_binary_frag_before
├── swap_tesc_unused_output_vert_binary_frag_after
├── swap_tesc_unused_output_tesc_binary_vert_before
├── swap_tesc_unused_output_tesc_binary_vert_after
├── swap_tesc_unused_output_tesc_binary_tesc_before
├── swap_tesc_unused_output_tesc_binary_tesc_after
├── swap_tesc_unused_output_tesc_binary_tese_before
├── swap_tesc_unused_output_tesc_binary_tese_after
├── swap_tesc_unused_output_tesc_binary_geom_before
├── swap_tesc_unused_output_tesc_binary_geom_after
├── swap_tesc_unused_output_tesc_binary_frag_before
├── swap_tesc_unused_output_tesc_binary_frag_after
├── swap_tesc_unused_output_tese_binary_vert_before
├── swap_tesc_unused_output_tese_binary_vert_after
├── swap_tesc_unused_output_tese_binary_tesc_before
├── swap_tesc_unused_output_tese_binary_tesc_after
├── swap_tesc_unused_output_tese_binary_tese_before
├── swap_tesc_unused_output_tese_binary_tese_after
├── swap_tesc_unused_output_tese_binary_geom_before
├── swap_tesc_unused_output_tese_binary_geom_after
├── swap_tesc_unused_output_tese_binary_frag_before
├── swap_tesc_unused_output_tese_binary_frag_after
├── swap_tesc_unused_output_geom_binary_vert_before
├── swap_tesc_unused_output_geom_binary_vert_after
├── swap_tesc_unused_output_geom_binary_tesc_before
├── swap_tesc_unused_output_geom_binary_tesc_after
├── swap_tesc_unused_output_geom_binary_tese_before
├── swap_tesc_unused_output_geom_binary_tese_after
├── swap_tesc_unused_output_geom_binary_geom_before
├── swap_tesc_unused_output_geom_binary_geom_after
├── swap_tesc_unused_output_geom_binary_frag_before
├── swap_tesc_unused_output_geom_binary_frag_after
├── swap_tesc_unused_output_frag_binary_vert_before
├── swap_tesc_unused_output_frag_binary_vert_after
├── swap_tesc_unused_output_frag_binary_tesc_before
├── swap_tesc_unused_output_frag_binary_tesc_after
├── swap_tesc_unused_output_frag_binary_tese_before
├── swap_tesc_unused_output_frag_binary_tese_after
├── swap_tesc_unused_output_frag_binary_geom_before
├── swap_tesc_unused_output_frag_binary_geom_after
├── swap_tesc_unused_output_frag_binary_frag_before
├── swap_tesc_unused_output_frag_binary_frag_after
├── swap_tese_unused_output_vert_binary_vert_before
├── swap_tese_unused_output_vert_binary_vert_after
├── swap_tese_unused_output_vert_binary_tesc_before
├── swap_tese_unused_output_vert_binary_tesc_after
├── swap_tese_unused_output_vert_binary_tese_before
├── swap_tese_unused_output_vert_binary_tese_after
├── swap_tese_unused_output_vert_binary_geom_before
├── swap_tese_unused_output_vert_binary_geom_after
├── swap_tese_unused_output_vert_binary_frag_before
├── swap_tese_unused_output_vert_binary_frag_after
├── swap_tese_unused_output_tesc_binary_vert_before
├── swap_tese_unused_output_tesc_binary_vert_after
├── swap_tese_unused_output_tesc_binary_tesc_before
├── swap_tese_unused_output_tesc_binary_tesc_after
├── swap_tese_unused_output_tesc_binary_tese_before
├── swap_tese_unused_output_tesc_binary_tese_after
├── swap_tese_unused_output_tesc_binary_geom_before
├── swap_tese_unused_output_tesc_binary_geom_after
├── swap_tese_unused_output_tesc_binary_frag_before
├── swap_tese_unused_output_tesc_binary_frag_after
├── swap_tese_unused_output_tese_binary_vert_before
├── swap_tese_unused_output_tese_binary_vert_after
├── swap_tese_unused_output_tese_binary_tesc_before
├── swap_tese_unused_output_tese_binary_tesc_after
├── swap_tese_unused_output_tese_binary_tese_before
├── swap_tese_unused_output_tese_binary_tese_after
├── swap_tese_unused_output_tese_binary_geom_before
├── swap_tese_unused_output_tese_binary_geom_after
├── swap_tese_unused_output_tese_binary_frag_before
├── swap_tese_unused_output_tese_binary_frag_after
├── swap_tese_unused_output_geom_binary_vert_before
├── swap_tese_unused_output_geom_binary_vert_after
├── swap_tese_unused_output_geom_binary_tesc_before
├── swap_tese_unused_output_geom_binary_tesc_after
├── swap_tese_unused_output_geom_binary_tese_before
├── swap_tese_unused_output_geom_binary_tese_after
├── swap_tese_unused_output_geom_binary_geom_before
├── swap_tese_unused_output_geom_binary_geom_after
├── swap_tese_unused_output_geom_binary_frag_before
├── swap_tese_unused_output_geom_binary_frag_after
├── swap_tese_unused_output_frag_binary_vert_before
├── swap_tese_unused_output_frag_binary_vert_after
├── swap_tese_unused_output_frag_binary_tesc_before
├── swap_tese_unused_output_frag_binary_tesc_after
├── swap_tese_unused_output_frag_binary_tese_before
├── swap_tese_unused_output_frag_binary_tese_after
├── swap_tese_unused_output_frag_binary_geom_before
├── swap_tese_unused_output_frag_binary_geom_after
├── swap_tese_unused_output_frag_binary_frag_before
├── swap_tese_unused_output_frag_binary_frag_after
├── swap_geom_unused_output_vert_binary_vert_before
├── swap_geom_unused_output_vert_binary_vert_after
├── swap_geom_unused_output_vert_binary_tesc_before
├── swap_geom_unused_output_vert_binary_tesc_after
├── swap_geom_unused_output_vert_binary_tese_before
├── swap_geom_unused_output_vert_binary_tese_after
├── swap_geom_unused_output_vert_binary_geom_before
├── swap_geom_unused_output_vert_binary_geom_after
├── swap_geom_unused_output_vert_binary_frag_before
├── swap_geom_unused_output_vert_binary_frag_after
├── swap_geom_unused_output_tesc_binary_vert_before
├── swap_geom_unused_output_tesc_binary_vert_after
├── swap_geom_unused_output_tesc_binary_tesc_before
├── swap_geom_unused_output_tesc_binary_tesc_after
├── swap_geom_unused_output_tesc_binary_tese_before
├── swap_geom_unused_output_tesc_binary_tese_after
├── swap_geom_unused_output_tesc_binary_geom_before
├── swap_geom_unused_output_tesc_binary_geom_after
├── swap_geom_unused_output_tesc_binary_frag_before
├── swap_geom_unused_output_tesc_binary_frag_after
├── swap_geom_unused_output_tese_binary_vert_before
├── swap_geom_unused_output_tese_binary_vert_after
├── swap_geom_unused_output_tese_binary_tesc_before
├── swap_geom_unused_output_tese_binary_tesc_after
├── swap_geom_unused_output_tese_binary_tese_before
├── swap_geom_unused_output_tese_binary_tese_after
├── swap_geom_unused_output_tese_binary_geom_before
├── swap_geom_unused_output_tese_binary_geom_after
├── swap_geom_unused_output_tese_binary_frag_before
├── swap_geom_unused_output_tese_binary_frag_after
├── swap_geom_unused_output_geom_binary_vert_before
├── swap_geom_unused_output_geom_binary_vert_after
├── swap_geom_unused_output_geom_binary_tesc_before
├── swap_geom_unused_output_geom_binary_tesc_after
├── swap_geom_unused_output_geom_binary_tese_before
├── swap_geom_unused_output_geom_binary_tese_after
├── swap_geom_unused_output_geom_binary_geom_before
├── swap_geom_unused_output_geom_binary_geom_after
├── swap_geom_unused_output_geom_binary_frag_before
├── swap_geom_unused_output_geom_binary_frag_after
├── swap_geom_unused_output_frag_binary_vert_before
├── swap_geom_unused_output_frag_binary_vert_after
├── swap_geom_unused_output_frag_binary_tesc_before
├── swap_geom_unused_output_frag_binary_tesc_after
├── swap_geom_unused_output_frag_binary_tese_before
├── swap_geom_unused_output_frag_binary_tese_after
├── swap_geom_unused_output_frag_binary_geom_before
├── swap_geom_unused_output_frag_binary_geom_after
├── swap_geom_unused_output_frag_binary_frag_before
├── swap_geom_unused_output_frag_binary_frag_after
├── swap_frag_unused_output_vert_binary_vert_before
├── swap_frag_unused_output_vert_binary_vert_after
├── swap_frag_unused_output_vert_binary_tesc_before
├── swap_frag_unused_output_vert_binary_tesc_after
├── swap_frag_unused_output_vert_binary_tese_before
├── swap_frag_unused_output_vert_binary_tese_after
├── swap_frag_unused_output_vert_binary_geom_before
├── swap_frag_unused_output_vert_binary_geom_after
├── swap_frag_unused_output_vert_binary_frag_before
├── swap_frag_unused_output_vert_binary_frag_after
├── swap_frag_unused_output_tesc_binary_vert_before
├── swap_frag_unused_output_tesc_binary_vert_after
├── swap_frag_unused_output_tesc_binary_tesc_before
├── swap_frag_unused_output_tesc_binary_tesc_after
├── swap_frag_unused_output_tesc_binary_tese_before
├── swap_frag_unused_output_tesc_binary_tese_after
├── swap_frag_unused_output_tesc_binary_geom_before
├── swap_frag_unused_output_tesc_binary_geom_after
├── swap_frag_unused_output_tesc_binary_frag_before
├── swap_frag_unused_output_tesc_binary_frag_after
├── swap_frag_unused_output_tese_binary_vert_before
├── swap_frag_unused_output_tese_binary_vert_after
├── swap_frag_unused_output_tese_binary_tesc_before
├── swap_frag_unused_output_tese_binary_tesc_after
├── swap_frag_unused_output_tese_binary_tese_before
├── swap_frag_unused_output_tese_binary_tese_after
├── swap_frag_unused_output_tese_binary_geom_before
├── swap_frag_unused_output_tese_binary_geom_after
├── swap_frag_unused_output_tese_binary_frag_before
├── swap_frag_unused_output_tese_binary_frag_after
├── swap_frag_unused_output_geom_binary_vert_before
├── swap_frag_unused_output_geom_binary_vert_after
├── swap_frag_unused_output_geom_binary_tesc_before
├── swap_frag_unused_output_geom_binary_tesc_after
├── swap_frag_unused_output_geom_binary_tese_before
├── swap_frag_unused_output_geom_binary_tese_after
├── swap_frag_unused_output_geom_binary_geom_before
├── swap_frag_unused_output_geom_binary_geom_after
├── swap_frag_unused_output_geom_binary_frag_before
├── swap_frag_unused_output_geom_binary_frag_after
├── swap_frag_unused_output_frag_binary_vert_before
├── swap_frag_unused_output_frag_binary_vert_after
├── swap_frag_unused_output_frag_binary_tesc_before
├── swap_frag_unused_output_frag_binary_tesc_after
├── swap_frag_unused_output_frag_binary_tese_before
├── swap_frag_unused_output_frag_binary_tese_after
├── swap_frag_unused_output_frag_binary_geom_before
├── swap_frag_unused_output_frag_binary_geom_after
├── swap_frag_unused_output_frag_binary_frag_before
├── swap_frag_unused_output_frag_binary_frag_after
├── unbind_tesc_null_pshaders
├── unbind_tesc_null_handle
├── unbind_geom_null_pshaders
├── unbind_geom_null_handle
├── mesh_swap_task
├── mesh_swap_mesh
├── disabled_geom
├── disabled_tess
├── disabled_geom_bind
├── disabled_tess_bind
├── draw_dispatch_draw
├── dispatch_draw_dispatch
├── bindings
├── bindings_mesh_shaders
├── unbind_vtg
├── unbind_task_mesh
└── unbind_mesh_draw_vertex
```

The displayed branch name is verified from `TestCaseGroup(testCtx, "binding")` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2074-L2076). The root file registers this branch directly at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57).

## Test Families

### unbind_passthrough_geom — Graphics binding, swap, disabled-stage, and draw/dispatch cases

`BindingDrawParams` defines the core dimensions for graphics and compute/draw interleaving: test type, stage, unused-output stage, binary stage, unsupported-stage binding, state ordering, and null-unbind style at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L52-L71). Registration creates a baseline `unbind_passthrough_geom`, five simple swap cases (`swap_vert`, `swap_tesc`, `swap_tese`, `swap_geom`, `swap_frag`), a nested cross product over stage, unused-output stage, binary stage, and state timing producing 250 `swap_*_unused_output_*_binary_*_{before,after}` cases, tessellation/geometry unbind cases (`unbind_tesc_null_pshaders`, `unbind_tesc_null_handle`, `unbind_geom_null_pshaders`, `unbind_geom_null_handle`), disabled-stage cases (`disabled_geom`, `disabled_tess`, `disabled_geom_bind`, `disabled_tess_bind`), and draw/dispatch interleaving cases (`draw_dispatch_draw`, `dispatch_draw_dispatch`) at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2078-L2184).

### mesh_swap_task — Mesh swap cases

`meshStageTest[]` registers `mesh_swap_task` and `mesh_swap_mesh` using `MeshShaderObjectBindingCase` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2154-L2169).

### bindings — General bindings and unbind cases

`bindings` and `bindings_mesh_shaders` exercise binding lists with and without mesh shaders at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2186-L2190). The final unbind family registers `unbind_vtg`, `unbind_task_mesh`, and `unbind_mesh_draw_vertex` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2192-L2198).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Main `TestType` | `PASSTHROUGH_GEOM`, `SWAP`, `DISABLED`, `UNBIND`, `DRAW_DISPATCH_DRAW`, `DISPATCH_DRAW_DISPATCH` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L52-L60) |
| Classic stages | `vert`, `tesc`, `tese`, `geom`, `frag` in `stageTest[]` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2089-L2099) |
| Mesh stages | `task`, `mesh` in `meshStageTest[]` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2154-L2161) |
| Null-unbind style | `null_pshaders` and `null_handle` generated from `unbindWithNullpShaders` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2142-L2150) |
| Mesh binding toggle | `bindings` and `bindings_mesh_shaders` from `BindingParams::useMeshShaders` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2186-L2190) |
| Final unbind mode | `UNBIND_VTG`, `UNBIND_TASK_MESH`, `UNBIND_MESH_DRAW_VERTEX` registered at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2192-L2198) |

## Support / Feature Requirements

- `ShaderObjectBindingDrawCase` requires `VK_EXT_shader_object`; tessellation and geometry features are required when the selected stage or binary stage uses them at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L677-L689).
- Mesh swap cases require `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, and task/mesh feature support at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1293-L1301).
- General `bindings` cases require `VK_EXT_shader_object`; `bindings_mesh_shaders` additionally requires `VK_EXT_mesh_shader` at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1419-L1424).
- Final unbind cases require `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, and task/mesh feature support at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1990-L1998).
- Registration itself is unconditional once the root adds the branch factory at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L57).

## Verification Methods

- Draw/dispatch interleaving checks storage buffers for expected `0..15` values in dispatch paths and otherwise compares each rendered pixel against expected black or colored regions with a numeric threshold at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L600-L652).
- General `bindings` cases execute command-buffer binding sequences and pass if no command execution failure is raised; the inspected `iterate()` returns pass after submitting the command buffer at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L896-L1048).
- Mesh swap cases verify task-stage output `[4, 5, 2, 3]` or mesh-stage output `[0, 1, 6, 7]` in a host-visible buffer at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1240-L1267).
- Final unbind cases compare rendered pixels against white, black, or red regions depending on unbind mode and also check buffer values `[0, 1, 2, 3]` for modes that write side effects at [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1858-L1965).

## Test Principles Observed

- Exercise shader binding order, unbinding style, and unsupported-stage behavior without root-level conditional registration.
- Use both image results and storage-buffer side effects to validate shader-stage binding effects.
- Keep mesh/task binding behavior separate from classic graphics-stage binding behavior.

## Notes / Uncertainties

- The page records the observed pass/fail logic in inspected ranges. It does not enumerate every generated `swap_*_unused_output_*_binary_*` leaf name because those names are a large cross product generated in the registration loop.
