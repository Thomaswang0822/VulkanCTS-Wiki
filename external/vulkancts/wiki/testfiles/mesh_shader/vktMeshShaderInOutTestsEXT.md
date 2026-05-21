# vktMeshShaderInOutTestsEXT

## Overview

EXT interface-variable tests register feature groups and pseudorandom variable permutations.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp) |
| Registration code | [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597) |

## Registration Hierarchy

```text
mesh_shader.ext.in_out
├── 32_bits_only
├── with_i64
├── with_f64
├── all_but_16_bits
├── with_i16
├── with_f16
└── all_types
```

## Test Families

### 32_bits_only — Registered child

The `32_bits_only` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).
### with_i64 — Registered child

The `with_i64` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).
### with_f64 — Registered child

The `with_f64` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).
### all_but_16_bits — Registered child

The `all_but_16_bits` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).
### with_i16 — Registered child

The `with_i16` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).
### with_f16 — Registered child

The `with_f16` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).
### all_types — Registered child

The `all_types` child is documented from the registration tree for `mesh_shader.ext.in_out` and from the implementation source [vktMeshShaderInOutTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597).

## Parameter Dimensions

Dimensions include owner, data type, bit width, vector dimension, interpolation, seven feature groups, 40 permutations, and mesh-only/task-mesh leaves.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
