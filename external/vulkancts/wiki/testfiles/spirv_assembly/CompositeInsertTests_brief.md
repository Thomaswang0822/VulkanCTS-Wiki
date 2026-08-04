# Understanding Brief: `CompositeInsertTests`

## One-Sentence Test Purpose

This test checks that `OpCompositeInsert` replaces the selected constituent of vectors, matrices, and a nested struct without disturbing the constituents inserted earlier.

## Background Knowledge

### `OpCompositeInsert` builds a new composite value

`OpCompositeInsert` takes an object to insert, a composite operand, and one or more literal indices. It produces a new composite value; it does not mutate the input composite. Each later instruction in this test therefore consumes the `%tmpN` result of the preceding insert.

Why it matters here:
- The vector and matrix cases test single-index replacements, while the nested-struct case supplies four indices to reach a matrix column inside a structure and array.
- The `undef_` cases begin with `OpUndef`, but they overwrite every value later read by the test. The non-`undef_` cases begin with `OpLoad`; that starting value must not change the final fully populated result.

### Composite storage layout

Matrices are arrays of column vectors in the authored SPIR-V. Buffer decorations such as `ColMajor`, `MatrixStride`, `Offset`, and `ArrayStride` describe how the completed composite is stored in the output buffer. A three-row matrix has a 16-byte matrix stride, so the host reference carries a padding sentinel that its custom comparator ignores.

## One Concrete Example

The compute path `dEQP-VK.spirv_assembly.instruction.compute.composite_insert.undef_vec4` starts with an undefined four-float vector and applies four inserts:

```llvm
%tmp0 = OpUndef %v4f32
%tmp1 = OpCompositeInsert %v4f32 %c_f32_0 %tmp0 0
%tmp2 = OpCompositeInsert %v4f32 %c_f32_1 %tmp1 1
%tmp3 = OpCompositeInsert %v4f32 %c_f32_2 %tmp2 2
%tmp4 = OpCompositeInsert %v4f32 %c_f32_3 %tmp3 3
```

The final `%tmp4` contains `{0.0, 1.0, 2.0, 3.0}` and is stored through an output-buffer access chain. If an implementation treats an insert as in-place, drops a prior insert, or misreads an index, the buffer comparison catches it.

## End-to-End Test Flow

```text
[host] choose composite shape, dimensions, `useUndef`, and, for graphics, shader stage
[host] generate the CTS-authored SPIR-V assembly or graphics assembly fragments
[host] create an output storage buffer containing the expected float sequence
[host] submit one compute workgroup or a graphics-stage test
[device] chain `OpCompositeInsert` results to build the selected composite
[device] store the completed vector, matrix, or nested structure to the output buffer
[host] compare readback with the expected counter or identity-matrix data
[host] fail the case on any non-padding mismatch
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source builds SPIR-V assembly strings rather than compiling GLSL. [`getVectorCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L88-L102), [`getMatrixCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L104-L119), and [`getNestedStructCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L149-L166) select `OpUndef` or `OpLoad` and append the appropriate insert sequence. Graphics tests place declarations, decorations, and the test function into fragments passed to `createTestForStage`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Output buffer | yes | yes | written | yes | Holds the completed composite for comparison. |
| Function-local `%vec`, `%mat`, or `%nestedstruct` | no | no | read only in non-`undef_` variants, then superseded by inserts | no | Supplies the starting composite operand. |
| Expected float data | yes | used by CTS verification | no | yes | Defines the counter or identity-matrix result. |

## What Is Checked

- Vector cases compare the stored result with `0.0, 1.0, ...`, one value for each component.
- Matrix cases construct identity columns and use [`verifyMatrixOutput()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L121-L147) to compare the output. The comparator ignores `-1.0f` padding sentinels used for three-row columns.
- Nested-struct cases expect eight `mat4x4` identity matrices after 32 inserts, four columns for each array element.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `vecN`, `matCxR`, `nested_struct`

The `undef_` prefix and graphics-stage suffix extend these test-family behaviors but do not change their fundamental composite shape.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vecN` | Incorrect vector constituent replacement, result forwarding between chained inserts, or output store. |
| `matCxR` | Incorrect matrix-column replacement or mismatch between the completed matrix and its decorated buffer layout. |
| `nested_struct` | Incorrect multi-index traversal through the output struct, matrix array, or matrix column. |

## Important Variations and Special Cases

- The compute group has 26 mustpass leaves: six vector cases, eighteen matrix cases, and two nested-struct cases. The graphics group expands the same 26 base cases over `vert`, `tessc`, `tesse`, `geom`, and `frag`, for 130 leaves.
- Three-row matrix cases use `MatrixStride 16` rather than 12 bytes. The test data includes an ignored padding value after each column.
- Graphics cases set `vertexPipelineStoresAndAtomics` for vertex, tessellation, and geometry paths, then switch to `fragmentStoresAndAtomics` for the fragment path.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Insert-sequence generators | [`getVectorCompositeInserts()`, `getMatrixCompositeInserts()`, `getNestedStructCompositeInserts()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L88-L166) | Select starting value and emit the chained instructions. |
| Compute vector and matrix builders | [`addComputeVectorCompositeInsertTests()` and `addComputeMatrixCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L168-L411) | Build assembly, expected output, and compute cases. |
| Compute nested-struct builder | [`addComputeNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L508-L574) | Defines the four-level insert indices and eight-matrix expectation. |
| Graphics builders | [`addGraphicsVectorCompositeInsertTests()`, `addGraphicsMatrixCompositeInsertTests()`, and `addGraphicsNestedStructCompositeInsertTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L246-L656) | Expand each base case across graphics stages. |
| Group registration | [`createCompositeInsertComputeGroup()` and `createCompositeInsertGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L660-L680) | Register the `composite_insert` family below compute and graphics instruction paths. |

## Questions / Risk Points for User Audit

- Resolved: the `undef_` variants are safe to observe because each constituent that contributes to the expected result is overwritten before storage.
- Resolved: the matrix verifier deliberately ignores only the `-1.0f` padding sentinels, not matrix values.
- Resolved: the representative SPIR-V 1.0 `undef_vec4` expansion passed `spirv-as --target-env spv1.0`, `spirv-val --target-env spv1.0`, and `spirv-dis`.

## Conversion Notes for Final Wiki Rewrite

Use the compute `undef_vec4` expansion as the representative SPIR-V walkthrough. Keep the authored assembly in an unfolded `#### Source Code` block and omit a duplicated `#### SPIR-V` block, as required by the `spirv_assembly` page contract. Carry the failure-cause table directly into the final page, and put the full compute and graphics leaf inventory in the parseable registration trees.
