## Overview

**Core question:** Does `OpCompositeInsert` produce the expected completed composite when the test builds vectors, matrices, and deeply nested structures from chained insert results?

- `vktSpvAsmCompositeInsertTests.cpp` implements the `spirv_assembly.instruction.compute.composite_insert` and `spirv_assembly.instruction.graphics.composite_insert` test families.
- The test starts each composite from either `OpUndef` or an `OpLoad` of an uninitialized function-local variable, then replaces every constituent that contributes to the stored result with `OpCompositeInsert`.
- Compute coverage has 26 mustpass leaves. Graphics coverage uses the same 26 base cases in five stages, producing 130 stage-suffixed leaves.
- This page explains the authored SPIR-V, the output-buffer checks, layout-sensitive matrix validation, and the failure evidence supplied by each composite shape.

## Background Knowledge

- **Value-producing composite insert:** `OpCompositeInsert` takes an object, a composite operand, and literal indices, then produces a new composite result. It does not modify the input value. The next instruction must consume the preceding result to preserve earlier inserts.
- **Matrix and structure indices:** A matrix is composed of column vectors. A single literal index selects a vector component or matrix column; a sequence of indices can reach a constituent through enclosing structs and arrays.
- **Decorated output layout:** `ColMajor`, `MatrixStride`, `ArrayStride`, member `Offset`, and `BufferBlock` describe the output buffer's memory representation. The test's matrix reference accounts for the 16-byte stride required by its three-row cases.

## Registration Hierarchy

The trees below list every direct test case leaf from the default Vulkan mustpass file. The graphics builder creates a shared base case and gives each stage a suffix.

```text
spirv_assembly.instruction.compute.composite_insert
├── mat2x2
├── mat2x3
├── mat2x4
├── mat3x2
├── mat3x3
├── mat3x4
├── mat4x2
├── mat4x3
├── mat4x4
├── nested_struct
├── undef_mat2x2
├── undef_mat2x3
├── undef_mat2x4
├── undef_mat3x2
├── undef_mat3x3
├── undef_mat3x4
├── undef_mat4x2
├── undef_mat4x3
├── undef_mat4x4
├── undef_nested_struct
├── undef_vec2
├── undef_vec3
├── undef_vec4
├── vec2
├── vec3
└── vec4

spirv_assembly.instruction.graphics.composite_insert
├── mat2x2_frag
├── mat2x2_geom
├── mat2x2_tessc
├── mat2x2_tesse
├── mat2x2_vert
├── mat2x3_frag
├── mat2x3_geom
├── mat2x3_tessc
├── mat2x3_tesse
├── mat2x3_vert
├── mat2x4_frag
├── mat2x4_geom
├── mat2x4_tessc
├── mat2x4_tesse
├── mat2x4_vert
├── mat3x2_frag
├── mat3x2_geom
├── mat3x2_tessc
├── mat3x2_tesse
├── mat3x2_vert
├── mat3x3_frag
├── mat3x3_geom
├── mat3x3_tessc
├── mat3x3_tesse
├── mat3x3_vert
├── mat3x4_frag
├── mat3x4_geom
├── mat3x4_tessc
├── mat3x4_tesse
├── mat3x4_vert
├── mat4x2_frag
├── mat4x2_geom
├── mat4x2_tessc
├── mat4x2_tesse
├── mat4x2_vert
├── mat4x3_frag
├── mat4x3_geom
├── mat4x3_tessc
├── mat4x3_tesse
├── mat4x3_vert
├── mat4x4_frag
├── mat4x4_geom
├── mat4x4_tessc
├── mat4x4_tesse
├── mat4x4_vert
├── nested_struct_frag
├── nested_struct_geom
├── nested_struct_tessc
├── nested_struct_tesse
├── nested_struct_vert
├── undef_mat2x2_frag
├── undef_mat2x2_geom
├── undef_mat2x2_tessc
├── undef_mat2x2_tesse
├── undef_mat2x2_vert
├── undef_mat2x3_frag
├── undef_mat2x3_geom
├── undef_mat2x3_tessc
├── undef_mat2x3_tesse
├── undef_mat2x3_vert
├── undef_mat2x4_frag
├── undef_mat2x4_geom
├── undef_mat2x4_tessc
├── undef_mat2x4_tesse
├── undef_mat2x4_vert
├── undef_mat3x2_frag
├── undef_mat3x2_geom
├── undef_mat3x2_tessc
├── undef_mat3x2_tesse
├── undef_mat3x2_vert
├── undef_mat3x3_frag
├── undef_mat3x3_geom
├── undef_mat3x3_tessc
├── undef_mat3x3_tesse
├── undef_mat3x3_vert
├── undef_mat3x4_frag
├── undef_mat3x4_geom
├── undef_mat3x4_tessc
├── undef_mat3x4_tesse
├── undef_mat3x4_vert
├── undef_mat4x2_frag
├── undef_mat4x2_geom
├── undef_mat4x2_tessc
├── undef_mat4x2_tesse
├── undef_mat4x2_vert
├── undef_mat4x3_frag
├── undef_mat4x3_geom
├── undef_mat4x3_tessc
├── undef_mat4x3_tesse
├── undef_mat4x3_vert
├── undef_mat4x4_frag
├── undef_mat4x4_geom
├── undef_mat4x4_tessc
├── undef_mat4x4_tesse
├── undef_mat4x4_vert
├── undef_nested_struct_frag
├── undef_nested_struct_geom
├── undef_nested_struct_tessc
├── undef_nested_struct_tesse
├── undef_nested_struct_vert
├── undef_vec2_frag
├── undef_vec2_geom
├── undef_vec2_tessc
├── undef_vec2_tesse
├── undef_vec2_vert
├── undef_vec3_frag
├── undef_vec3_geom
├── undef_vec3_tessc
├── undef_vec3_tesse
├── undef_vec3_vert
├── undef_vec4_frag
├── undef_vec4_geom
├── undef_vec4_tessc
├── undef_vec4_tesse
├── undef_vec4_vert
├── vec2_frag
├── vec2_geom
├── vec2_tessc
├── vec2_tesse
├── vec2_vert
├── vec3_frag
├── vec3_geom
├── vec3_tessc
├── vec3_tesse
├── vec3_vert
├── vec4_frag
├── vec4_geom
├── vec4_tessc
├── vec4_tesse
└── vec4_vert
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution pipeline | `compute`, `graphics` | Selects a standalone compute assembly or graphics assembly fragments. | [`createCompositeInsertComputeGroup()` and `createCompositeInsertGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L660-L680) |
| Starting composite | `undef_` prefix or no prefix | Selects `OpUndef` or an `OpLoad` from an uninitialized function-local variable for `%tmp0`; all constituents contributing to the store are then overwritten. | [`getVectorCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L88-L102) |
| Vector width | `vec2`, `vec3`, `vec4` | Changes the number of scalar inserts and expected counter values. | [`addComputeVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L172-L243) |
| Matrix shape | `mat2x2` through `mat4x4` | Changes column count, row count, identity-vector type, and matrix stride. | [`addComputeMatrixCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L333-L409) |
| Nested shape | `nested_struct` | Builds an output struct containing an array of eight `mat4x4` identity matrices. | [`addComputeNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L512-L572) |
| Graphics stage | `_vert`, `_tessc`, `_tesse`, `_geom`, `_frag` | Runs each base composite case in one graphics stage. | [`addGraphicsVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L303-L325) |

The primary behavioral axis is the composite shape. Both starting-value paths overwrite every constituent that contributes to the stored result: `undef_` supplies `OpUndef`, while the no-prefix path emits an `OpLoad` from an uninitialized function-local variable. The oracle therefore does not observe or establish a value for either starting composite; it only detects whether the chained inserts produce the completed result. The stage suffix selects the graphics utility's tested stage.

## Behavior Parameters

### `vecN` and `undef_vecN`: replace every vector component

The generator creates a `vec2`, `vec3`, or `vec4` result by inserting float constants `0`, `1`, `2`, and `3` at indices `0`, `1`, `2`, and `3` as applicable. The expected output is the same ascending counter. The `undef_` variant starts with `OpUndef`; the no-prefix variant starts with an `OpLoad` from an uninitialized function-local composite. Because every stored component is replaced, the expected result does not depend on that load's value.

### `matCxR` and `undef_matCxR`: replace every matrix column

The generator builds one identity column per matrix column and inserts them at column indices `0` through `C - 1`. The result must be an identity matrix of the requested `C` by `R` shape. For `R == 3`, the output member has `MatrixStride 16`, and the expected host data includes one ignored padding float per column.

### `nested_struct` and `undef_nested_struct`: replace a matrix column through four indices

The output type contains a struct containing an eight-element array of `mat4x4` values. For each array element and column, the generated instruction supplies indices `0 0 arrayIdx vectorIdx`. Thirty-two chained inserts populate eight identity matrices, exercising the full multi-index form of `OpCompositeInsert`.

## Shader Analysis

This test category stores CTS-authored SPIR-V assembly templates in C++ rather than reconstructing GLSL or HLSL. The representative walkthrough expands the exact compute `undef_vec4` template. Its assembly appears under `#### Source Code`; the usual published `#### SPIR-V` subsection is intentionally omitted because it would duplicate the source assembly. As an audit-time semantic check, the displayed assembly passed `spirv-as --target-env spv1.0`, `spirv-val --target-env spv1.0`, and `spirv-dis`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.composite_insert.undef_vec4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses `SpvAsmComputeShaderCase` with one `1 x 1 x 1` workgroup. |
| `undef_` | Initializes `%tmp0` with `OpUndef`; later inserts define all four components that are stored. |
| `vec4` | Requires four scalar inserts and expects `(0.0, 1.0, 2.0, 3.0)` in the output buffer. |

#### Purpose

The shader proves that a chain of four value-producing inserts preserves the preceding result and changes only the selected component. It stores the completed vector through `%vecOutPtr`, so the CTS framework can compare the four stored floats with the expected counter.

#### Structural Design

| Phase | Assembly behavior |
|-------|-------------------|
| Declarations | `%v4f32` is the vector type; `%Output` contains one vector in a `Uniform` buffer at descriptor set `0`, binding `0`. |
| Initial composite | `%tmp0` is undefined because this variant tests full initialization by the insert sequence. |
| Insert chain | `%tmp1` through `%tmp4` insert constants at literal component indices `0` through `3`, each consuming the previous result. |
| Output | `OpAccessChain` addresses `%Output` member `0`; `OpStore` writes `%tmp4`. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- The concrete expansion comes from the vector template in [`addComputeVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L179-L223) plus [`getVectorCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L88-L102).
- The source uses the legacy `Uniform` plus `BufferBlock` layout appropriate for this SPIR-V 1.0 assembly. Validation must therefore use `--target-env spv1.0`; the default newer target rejects `BufferBlock`.
- `spirv-dis` preserved the four `OpCompositeInsert` instructions, their literal indices, and the final `OpStore`, confirming that the assembled module contains the intended chain.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Starting value | Non-`undef_` cases replace `%tmp0 = OpUndef ...` with `OpLoad` from the matching function-local composite. | [`getVectorCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L92-L100) |
| Vector width | `vec2` and `vec3` shorten the type and insert sequence; `vec4` emits all four scalar inserts. | [`addComputeVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L172-L243) |
| Matrix path | Each insert object is a complete identity column, and the literal index selects a column rather than a scalar component. | [`getMatrixCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L104-L119) |
| Nested path | The insert object is a `v4f32` identity column and the instruction supplies four literal indices. | [`getNestedStructCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L149-L166) |
| Graphics stage | The same test function is placed in stage-specific graphics fragments and stored to a storage buffer. | [`addGraphicsVectorCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L272-L325) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 26
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main"
               OpExecutionMode %2 LocalSize 1 1 1
               OpSource GLSL 430
               OpMemberDecorate %_struct_3 0 Offset 0
               OpDecorate %_struct_3 BufferBlock
               OpDecorate %4 DescriptorSet 0
               OpDecorate %4 Binding 0
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
  %_struct_3 = OpTypeStruct %v4float
%_ptr_Uniform__struct_3 = OpTypePointer Uniform %_struct_3
          %4 = OpVariable %_ptr_Uniform__struct_3 Uniform
%_ptr_Function_v4float = OpTypePointer Function %v4float
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
    %float_2 = OpConstant %float 2
    %float_3 = OpConstant %float 3
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %void = OpTypeVoid
         %17 = OpTypeFunction %void
          %2 = OpFunction %void None %17
         %18 = OpLabel
         %19 = OpVariable %_ptr_Function_v4float Function
         %20 = OpUndef %v4float
         %21 = OpCompositeInsert %v4float %float_0 %20 0
         %22 = OpCompositeInsert %v4float %float_1 %21 1
         %23 = OpCompositeInsert %v4float %float_2 %22 2
         %24 = OpCompositeInsert %v4float %float_3 %23 3
         %25 = OpAccessChain %_ptr_Uniform_v4float %4 %int_0
               OpStore %25 %24
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Compute cases set `spec.numWorkGroups = IVec3(1, 1, 1)` and bind one expected output buffer. The vector builder fills the expected data with the ascending counter before constructing `SpvAsmComputeShaderCase`.
- Matrix cases build identity data in column-major order. [`verifyMatrixOutput()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L121-L147) rejects a mismatch unless the expected entry is `-1.0f`, the explicit three-row padding sentinel.
- Compute nested-struct cases create expected data for eight identity matrices, then store the final `%tmp32` structure; the compute oracle compares that full sequence. Graphics nested-struct cases use the graphics utility's default resource check, with its stage-dependent repeated-execution allowance described below.
- Graphics cases use `createTestForStage` for vertex, tessellation-control, tessellation-evaluation, geometry, and fragment execution. They bind the expected buffer as `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`. Matrix leaves use the same strict custom comparator (apart from the `-1.0f` padding sentinel); vector and nested leaves use the graphics utility's default resource check. That default accepts the expected float values exactly for the fragment stage (subject to its general one-ULP rounding allowance) but, for the other tested stages, also accepts each value plus a non-negative integer to accommodate multiple shader executions. Thus those non-fragment vector and nested leaves do not require exact readback of the counter or identity values.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vecN` | Incorrect vector constituent replacement, result forwarding between chained inserts, or output store. |
| `matCxR` | Incorrect matrix-column replacement or mismatch between the completed matrix and its decorated buffer layout. |
| `nested_struct` | Incorrect multi-index traversal through the output struct, matrix array, or matrix column. |

### Cause Analysis

#### Vector constituent replacement (`vecN`)

**Possible failure symptoms:** A fragment-stage vector leaf, or a compute vector leaf, rejects a stored entry that differs from the expected ascending counter. For vertex, tessellation, and geometry leaves, the graphics utility also accepts an expected value plus a non-negative integer to permit repeated execution, so their default verifier does not establish exact counter equality.

**Possible implementation causes:** The source grounds the symptom in the `OpCompositeInsert` chain, its literal component indices, or the final buffer store. A compiler or execution implementation may mishandle the value produced by an insert or the selected constituent. The failing assembled module and device behavior require investigation to distinguish those causes.

#### Matrix-column replacement and layout (`matCxR`)

**Possible failure symptoms:** A stored matrix differs from the expected identity matrix. For a three-row case, the comparator ignores only padding slots, so a mismatch in an actual matrix element still fails.

**Possible implementation causes:** The failure may involve column-level composite replacement, forwarding an earlier matrix result, or handling the `ColMajor` and `MatrixStride` decorations on the output member. The CTS source establishes those tested conditions; determining the implementation defect needs the failing shape and pipeline path.

#### Nested composite traversal (`nested_struct`)

**Possible failure symptoms:** One or more of the eight expected identity matrices has a missing or incorrect column after readback.

**Possible implementation causes:** The generated insert sequence uses literal indices `0 0 arrayIdx vectorIdx`. A failure can arise from incorrect traversal through the outer output struct, inner struct member, array element, or matrix column, or from loss of a prior result in the chain. Source-level and implementation investigation is needed to identify the failing step.

## Case Pruning

### Requirement-based pruning

- Graphics vector, matrix, and nested-struct builders request `vertexPipelineStoresAndAtomics` for the vertex, tessellation, and geometry paths, then request `fragmentStoresAndAtomics` for the fragment path.
- Tessellation and geometry leaves require the corresponding graphics pipeline stages to be supported by the test environment.
- The default Vulkan mustpass inventory contains the documented 26 compute and 130 graphics leaves; the `vksc-default` mustpass file is a separate profile with its own eligibility set.

### Design-based pruning

- The builders cover vector widths and matrix dimensions from 2 through 4 only. They use fixed scalar constants and identity columns so an output mismatch identifies composite-insert behavior rather than arithmetic.
- The nested case fixes its array size at eight `mat4x4` values, enough to exercise repeated four-level indices without multiplying the leaf matrix.
- The page publishes one SPIR-V walkthrough for the `undef_vec4` case. The matrix, nested, starting-value, and graphics variations remain documented in the table above instead of duplicating equivalent assembly blocks.

## Key Takeaways

- These tests treat `OpCompositeInsert` as a value-producing operation: each `%tmpN` must preserve all constituents inserted into `%tmpN-1` except at the selected index.
- `undef_` cases are meaningful because the test writes every constituent that contributes to the stored result before observing it.
- Matrix checks cover both the inserted column values and their decorated output layout, including the 16-byte stride case for three-row columns.
- The nested case turns the same instruction into a multi-index traversal test across a struct, array, matrix, and vector-column hierarchy.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Composite insert helpers | [`getVectorCompositeInserts()`, `getMatrixCompositeInserts()`, `getNestedStructCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L88-L166) | Emit the `OpUndef` or `OpLoad` start and chained `OpCompositeInsert` instructions. |
| Matrix result comparator | [`verifyMatrixOutput()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L121-L147) | Shows the exact comparison and padding-sentinel handling. |
| Compute builders | [`addComputeVectorCompositeInsertTests()`, `addComputeMatrixCompositeInsertTests()`, `addComputeNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L574) | Registers compute shapes, authored assembly, and expected outputs. |
| Graphics builders | [`addGraphicsVectorCompositeInsertTests()`, `addGraphicsMatrixCompositeInsertTests()`, `addGraphicsNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L246-L656) | Builds stage-specific fragments and feature requests. |
| Registration | [`createCompositeInsertComputeGroup()` and `createCompositeInsertGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L660-L680) | Creates the two registered `composite_insert` test families. |
| Default mustpass inventory | [`compute leaves`](../../../mustpass/main/vk-default/spirv-assembly.txt#L848-L873) and [`graphics leaves`](../../../mustpass/main/vk-default/spirv-assembly.txt#L22889-L23018) | Confirms all 26 compute and 130 graphics case leaves. |
