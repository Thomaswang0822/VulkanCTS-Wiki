# vktSpvAsmCompositeInsertTests

## Overview

Tests for the SPIR-V OpCompositeInsert instruction, covering vector, matrix, and nested struct composite insert operations. Tests both OpUndef-based and variable-load-based starting values across compute and graphics pipelines.

## Role

Implementation file

## Source

- [vktSpvAsmCompositeInsertTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L660)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.composite_insert
├── vec2
├── vec3
├── vec4
├── undef_vec2
├── undef_vec3
├── undef_vec4
├── mat2x2
├── mat2x3
├── mat2x4
├── mat3x2
├── mat3x3
├── mat3x4
├── mat4x2
├── mat4x3
├── mat4x4
├── undef_mat2x2
├── undef_mat2x3
├── undef_mat2x4
├── undef_mat3x2
├── undef_mat3x3
├── undef_mat3x4
├── undef_mat4x2
├── undef_mat4x3
├── undef_mat4x4
├── nested_struct
└── undef_nested_struct

spirv_assembly.instruction.graphics.composite_insert
├── vec2_vert
├── vec2_tessc
├── vec2_tesse
├── vec2_geom
├── vec2_frag
├── vec3_vert
├── vec3_tessc
├── vec3_tesse
├── vec3_geom
├── vec3_frag
├── vec4_vert
├── vec4_tessc
├── vec4_tesse
├── vec4_geom
├── vec4_frag
├── undef_vec2_vert
├── undef_vec2_tessc
├── undef_vec2_tesse
├── undef_vec2_geom
├── undef_vec2_frag
├── undef_vec3_vert
├── undef_vec3_tessc
├── undef_vec3_tesse
├── undef_vec3_geom
├── undef_vec3_frag
├── undef_vec4_vert
├── undef_vec4_tessc
├── undef_vec4_tesse
├── undef_vec4_geom
├── undef_vec4_frag
├── mat2x2_vert
├── mat2x2_tessc
├── mat2x2_tesse
├── mat2x2_geom
├── mat2x2_frag
├── mat2x3_vert
├── mat2x3_tessc
├── mat2x3_tesse
├── mat2x3_geom
├── mat2x3_frag
├── mat2x4_vert
├── mat2x4_tessc
├── mat2x4_tesse
├── mat2x4_geom
├── mat2x4_frag
├── mat3x2_vert
├── mat3x2_tessc
├── mat3x2_tesse
├── mat3x2_geom
├── mat3x2_frag
├── mat3x3_vert
├── mat3x3_tessc
├── mat3x3_tesse
├── mat3x3_geom
├── mat3x3_frag
├── mat3x4_vert
├── mat3x4_tessc
├── mat3x4_tesse
├── mat3x4_geom
├── mat3x4_frag
├── mat4x2_vert
├── mat4x2_tessc
├── mat4x2_tesse
├── mat4x2_geom
├── mat4x2_frag
├── mat4x3_vert
├── mat4x3_tessc
├── mat4x3_tesse
├── mat4x3_geom
├── mat4x3_frag
├── mat4x4_vert
├── mat4x4_tessc
├── mat4x4_tesse
├── mat4x4_geom
├── mat4x4_frag
├── undef_mat2x2_vert
├── undef_mat2x2_tessc
├── undef_mat2x2_tesse
├── undef_mat2x2_geom
├── undef_mat2x2_frag
├── undef_mat2x3_vert
├── undef_mat2x3_tessc
├── undef_mat2x3_tesse
├── undef_mat2x3_geom
├── undef_mat2x3_frag
├── undef_mat2x4_vert
├── undef_mat2x4_tessc
├── undef_mat2x4_tesse
├── undef_mat2x4_geom
├── undef_mat2x4_frag
├── undef_mat3x2_vert
├── undef_mat3x2_tessc
├── undef_mat3x2_tesse
├── undef_mat3x2_geom
├── undef_mat3x2_frag
├── undef_mat3x3_vert
├── undef_mat3x3_tessc
├── undef_mat3x3_tesse
├── undef_mat3x3_geom
├── undef_mat3x3_frag
├── undef_mat3x4_vert
├── undef_mat3x4_tessc
├── undef_mat3x4_tesse
├── undef_mat3x4_geom
├── undef_mat3x4_frag
├── undef_mat4x2_vert
├── undef_mat4x2_tessc
├── undef_mat4x2_tesse
├── undef_mat4x2_geom
├── undef_mat4x2_frag
├── undef_mat4x3_vert
├── undef_mat4x3_tessc
├── undef_mat4x3_tesse
├── undef_mat4x3_geom
├── undef_mat4x3_frag
├── undef_mat4x4_vert
├── undef_mat4x4_tessc
├── undef_mat4x4_tesse
├── undef_mat4x4_geom
├── undef_mat4x4_frag
├── nested_struct_vert
├── nested_struct_tessc
├── nested_struct_tesse
├── nested_struct_geom
├── nested_struct_frag
├── undef_nested_struct_vert
├── undef_nested_struct_tessc
├── undef_nested_struct_tesse
├── undef_nested_struct_geom
└── undef_nested_struct_frag
```

## Test Families

### Vector composite insert tests

Tests [`OpCompositeInsert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L244) on vectors (vec2, vec3, vec4). Each element is inserted sequentially using [`OpCompositeInsert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L244), building a vector with values 0, 1, 2, 3. Two variants: starting from [`OpUndef`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L244) (`undef_vecN`) or starting from a loaded variable (`vecN`).

Observed in [`addComputeVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L244) at [vktSpvAsmCompositeInsertTests.cpp#L168-L244](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L244) and [`addGraphicsVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L246-L327) at [vktSpvAsmCompositeInsertTests.cpp#L246-L327](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L246-L327).

### Matrix composite insert tests

Tests [`OpCompositeInsert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L329-L411) on matrices (mat2x2 through mat4x4). Identity vectors are inserted column-by-column to construct an identity matrix. Matrix stride is 16 for 3-row matrices (padding), otherwise rows*4. Two variants: starting from [`OpUndef`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L329-L411) (`undef_matCxR`) or starting from a loaded variable (`matCxR`).

Observed in [`addComputeMatrixCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L329-L411) at [vktSpvAsmCompositeInsertTests.cpp#L329-L411](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L329-L411) and [`addGraphicsMatrixCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L413-L506) at [vktSpvAsmCompositeInsertTests.cpp#L413-L506](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L413-L506).

### Nested struct composite insert tests

Tests [`OpCompositeInsert`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L508-L574) on a deeply nested struct containing an array of 8 mat4x4. Identity vectors are inserted at specific array and column indices using multi-level access chains (0, 0, arrayIdx, vectorIdx). Two variants: starting from [`OpUndef`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L508-L574) (`undef_nested_struct`) or starting from a loaded variable (`nested_struct`).

Observed in [`addComputeNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L508-L574) at [vktSpvAsmCompositeInsertTests.cpp#L508-L574](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L508-L574) and [`addGraphicsNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L576-L656) at [vktSpvAsmCompositeInsertTests.cpp#L576-L656](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L576-L656).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| useUndef | true, false | Whether to start from OpUndef or a loaded variable |
| Vector elements | 2, 3, 4 | Vector component count |
| Matrix rows | 2, 3, 4 | Matrix row count |
| Matrix cols | 2, 3, 4 | Matrix column count |
| ShaderStage | vert, tessc, tesse, geom, frag (graphics only) | Graphics pipeline stage |

Test naming convention:
- Compute: `{undef_}vec{N}`, `{undef_}mat{C}x{R}`, `{undef_}nested_struct`
- Graphics: `{undef_}vec{N}_{stage}`, `{undef_}mat{C}x{R}_{stage}`, `{undef_}nested_struct_{stage}`

## Support / Feature Requirements

- **vertexPipelineStoresAndAtomics** — required for vertex, tessellation, and geometry stages in graphics tests — [vktSpvAsmCompositeInsertTests.cpp#L303](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L303)
- **fragmentStoresAndAtomics** — required for fragment stage in graphics tests — [vktSpvAsmCompositeInsertTests.cpp#L322](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L322)
- **tessellationShader** — implicitly required for tessellation stages (graphics)
- **geometryShader** — implicitly required for geometry stage (graphics)

## Verification Methods

- **Vector tests**: Output buffer is compared against a running counter (0, 1, 2, ..., elements-1) — [vktSpvAsmCompositeInsertTests.cpp#L229-L231](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L229-L231)
- **Matrix tests**: Uses custom [`verifyMatrixOutput`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L121-L147) function that compares output against expected identity matrix data. Padding values in 3-row matrices are marked with -1.0f and skipped during comparison — [vktSpvAsmCompositeInsertTests.cpp#L121-L147](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L121-L147)
- **Nested struct tests**: Output is compared against an array of 8 identity matrices — [vktSpvAsmCompositeInsertTests.cpp#L564-L567](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L564-L567)

## Notes

- For 3-row matrices, padding of -1.0f is inserted after each column to align to 16-byte stride, and the [`verifyMatrixOutput`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L121-L147) function skips these padding values — [vktSpvAsmCompositeInsertTests.cpp#L397-L399](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L397-L399)
- Graphics tests use [`createTestForStage`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L305-L325) per stage rather than `createTestsForAllStages`, resulting in flat test names with stage suffixes
- The nested struct test uses a fixed array size of 8 mat4x4 matrices — [vktSpvAsmCompositeInsertTests.cpp#L516](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L516)
