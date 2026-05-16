# [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1)

## Overview

[`vktShaderObjectLinkTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1) implements the `shader_object/link` branch. It builds linked and unlinked shader-stage combinations, next-stage chain tests, separate-link tests, and mesh/task/fragment link combinations.

## Role of File

Implementation-heavy test file for the root-level `link` branch.

## Source Code

- Primary source: [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L53)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Hierarchy

```text
shader_object.link
├── linked_linked_unlinked_unused_unlinked
├── linked_linked_linked_unused_unlinked
├── linked_linked_linked_unlinked_unlinked
├── linked_linked_linked_linked_unlinked
├── linked_linked_linked_linked_linked
├── linked_unused_unused_linked_unlinked
├── linked_unused_unused_linked_linked
├── linked_unused_unused_unused_linked
├── unlinked_unlinked_unlinked_unused_unlinked
├── unlinked_unused_unused_unlinked_unlinked
├── unlinked_unused_unused_unused_unlinked
├── unlinked_linked_linked_unused_unlinked
├── unlinked_linked_linked_linked_unlinked
├── unlinked_linked_linked_unused_linked
├── unlinked_linked_linked_linked_linked
├── unlinked_unused_unused_linked_linked
├── next_stage
├── mesh_unlinked_unlinked_unlinked
├── mesh_unlinked_unlinked_unused
├── mesh_linked_linked_unlinked
├── mesh_unlinked_linked_linked
└── mesh_linked_linked_linked
```

Evidence: `createShaderObjectLinkTests()` constructs `link`, iterates `shaderTests[]`, `bindTypeTests[]`, and `randomOrderTests[]`, adds `next_stage`, and then adds mesh-combination groups at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1351-L1650). The 16 graphics shader-combination group names are generated from `typeToString()` applied to each of the five shader stage states (vertex, tessellation_control, tessellation_evaluation, geometry, fragment) joined by underscores at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1381-L1390).

## Test Families

### linked_linked_unlinked_unused_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=LINKED, tese=UNLINKED, geom=UNUSED, frag=UNLINKED. Each graphics shader-combination group iterates bind modes `separate`, `one_linked_unlinked`, and `all` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1371-L1379), then adds `default` and `random_order` cases at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1391-L1426). When any stage is linked, it also adds `separate_link` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1428-L1447).

### linked_linked_linked_unused_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=LINKED, tese=LINKED, geom=UNUSED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### linked_linked_linked_unlinked_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=LINKED, tese=LINKED, geom=UNLINKED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### linked_linked_linked_linked_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=LINKED, tese=LINKED, geom=LINKED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### linked_linked_linked_linked_linked — Graphics linked/unlinked combination

Graphics shader combination with all five stages LINKED. Same bind-mode and ordering structure as other graphics groups.

### linked_unused_unused_linked_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=UNUSED, tese=UNUSED, geom=LINKED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### linked_unused_unused_linked_linked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=UNUSED, tese=UNUSED, geom=LINKED, frag=LINKED. Same bind-mode and ordering structure as other graphics groups.

### linked_unused_unused_unused_linked — Graphics linked/unlinked combination

Graphics shader combination with vertex=LINKED, tesc=UNUSED, tese=UNUSED, geom=UNUSED, frag=LINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_unlinked_unlinked_unused_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=UNLINKED, tese=UNLINKED, geom=UNUSED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_unused_unused_unlinked_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=UNUSED, tese=UNUSED, geom=UNLINKED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_unused_unused_unused_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=UNUSED, tese=UNUSED, geom=UNUSED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_linked_linked_unused_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=LINKED, tese=LINKED, geom=UNUSED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_linked_linked_linked_unlinked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=LINKED, tese=LINKED, geom=LINKED, frag=UNLINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_linked_linked_unused_linked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=LINKED, tese=LINKED, geom=UNUSED, frag=LINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_linked_linked_linked_linked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=LINKED, tese=LINKED, geom=LINKED, frag=LINKED. Same bind-mode and ordering structure as other graphics groups.

### unlinked_unused_unused_linked_linked — Graphics linked/unlinked combination

Graphics shader combination with vertex=UNLINKED, tesc=UNUSED, tese=UNUSED, geom=LINKED, frag=LINKED. Same bind-mode and ordering structure as other graphics groups.

### next_stage — Next-stage chain tests

`nextStageTests[]` registers named next-stage combinations such as `vert_t`, `vert_g`, `vert_tgf`, and no-fragment variants under `next_stage` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1453-L1615). These test next-stage flag specification independently from shader presence.

### mesh_unlinked_unlinked_unlinked — Mesh shader link test

Mesh shader combination with task=UNLINKED, mesh=UNLINKED, frag=UNLINKED. Registers `default` and `random_order` child cases at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1617-L1647).

### mesh_unlinked_unlinked_unused — Mesh shader link test

Mesh shader combination with task=UNLINKED, mesh=UNLINKED, frag=UNUSED. Registers `default` and `random_order` child cases.

### mesh_linked_linked_unlinked — Mesh shader link test

Mesh shader combination with task=LINKED, mesh=LINKED, frag=UNLINKED. Registers `default` and `random_order` child cases.

### mesh_unlinked_linked_linked — Mesh shader link test

Mesh shader combination with task=UNLINKED, mesh=LINKED, frag=LINKED. Registers `default` and `random_order` child cases.

### mesh_linked_linked_linked — Mesh shader link test

Mesh shader combination with task=LINKED, mesh=LINKED, frag=LINKED. Registers `default` and `random_order` child cases.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Stage link state | `UNUSED`, `LINKED`, `UNLINKED` in `ShaderType` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L45-L50) |
| Bind type | `SEPARATE`, `ONE_LINKED_UNLINKED`, `ALL` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L82-L87) |
| Random order | `false`, `true` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1366-L1369) |
| Next-stage flags | `NextStages` and `MeshNextStages` structs at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L68-L80) |

## Support / Feature Requirements

- Graphics link cases require `VK_EXT_shader_object` at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L742-L745).
- Tessellation and geometry features are required when the selected shader/next-stage parameters use those stages at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L746-L753).
- Mesh link cases require `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, and task/mesh feature support at [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1323-L1328).

## Verification Methods

The file's inspected registration and support code show that link tests vary shader linkage, binding mode, ordering, and next-stage flags. Detailed pass/fail comparison is implemented in `ShaderObjectLinkInstance::iterate()` and `MeshShaderObjectLinkCase` code outside the compact registration excerpt; this stage does not overstate exact image or buffer comparison behavior.

## Test Principles Observed

- Cross product linked/unlinked states with binding mode and order variants.
- Treat next-stage flags as a distinct dimension from shader presence.
- Include mesh/task linkage separately from classic graphics stages.

## Notes / Uncertainties

- The exact output verification logic was not fully inspected in this stage; future work should expand `iterate()` evidence before using stronger claims about rendered or buffer results.
