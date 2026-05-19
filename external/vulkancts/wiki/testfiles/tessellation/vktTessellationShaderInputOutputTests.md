# vktTessellationShaderInputOutputTests.cpp

## Overview

[`vktTessellationShaderInputOutputTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L1) registers [`shader_input_output`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L971-L1080), covering tessellation built-ins, per-patch data, barriers, and cross-invocation values.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationShaderInputOutputTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.shader_input_output`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L1).

```text
tessellation.shader_input_output
├── barrier
├── cross_invocation_per_patch_float
├── cross_invocation_per_patch_int
├── cross_invocation_per_patch_mat4x3
├── cross_invocation_per_patch_uint
├── cross_invocation_per_patch_vec3
├── cross_invocation_per_patch_vec4
├── cross_invocation_per_vertex_float
├── cross_invocation_per_vertex_int
├── cross_invocation_per_vertex_mat4x3
├── cross_invocation_per_vertex_uint
├── cross_invocation_per_vertex_vec3
├── cross_invocation_per_vertex_vec4
├── gl_position_tcs_to_tes
├── gl_position_vs_to_tcs
├── gl_position_vs_to_tcs_to_tes
├── patch_vertices_10_in_5_out
├── patch_vertices_5_in_10_out
├── patch_vertices_in_tcs
├── patch_vertices_in_tes
├── primitive_id_tcs
├── primitive_id_tes
├── tess_level_inner_0_tes
├── tess_level_inner_1_tes
├── tess_level_outer_0_tes
├── tess_level_outer_1_tes
├── tess_level_outer_2_tes
└── tess_level_outer_3_tes
```

## Test Families

### barrier — Shader Input Output

Registration arrays in [`createShaderInputOutputTests()`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L974-L1080) create patch-vertex-count, tess-level, primitive-ID, barrier, and cross-invocation cases.

## Parameter Dimensions

Parameters include built-in variable selection, patch vertex count, data type, per-patch/per-vertex storage, and cross-invocation data values.

## Support / Feature Requirements

Tessellation feature support is required by the generated programs; the page does not infer additional gates beyond inspected helper use.

## Verification Methods

Rendered reference images are compared with [`tcu::fuzzyCompare()`](../../../modules/vulkan/tessellation/vktTessellationShaderInputOutputTests.cpp#L193-L194).

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
