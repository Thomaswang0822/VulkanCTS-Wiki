## Overview

**Core question:** Does a compute shader access every intended element of a generated nested, runtime-sized SSBO layout through a non-uniformly indexed storage-buffer descriptor array, while preserving the checked leading guard ranges?

- This page documents the `nested_unsized_arrays` test case leaf under the `ssbo.unsized_array_length` test family. The parent creates the family, while [`vktSSBOLayoutNestedUnsizedArraysTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L829-L1158) implements this leaf.
- The test generates nested structures containing scalars, vectors, matrices, fixed arrays, arrays of structures, and a final runtime-sized array. It creates a ranged storage-buffer descriptor for each outer element.
- One compute workgroup selects descriptor ranges with `nonuniformEXT`, writes the generated structure contents, and leaves two descriptor ranges at each end untouched.
- The host reconstructs the expected data and compares every dword in the two leading ranges and the active ranges; the two trailing ranges are allocated but not compared.

## Background Knowledge

- A runtime-sized array is the final member of a storage-buffer block. Its available element count comes from the buffer range, but its elements still follow the block layout's alignment and stride rules.
- A descriptor array provides multiple storage-buffer descriptors at one binding. If invocations use different descriptor indices, the shader marks the index non-uniform so descriptor selection is valid for that access pattern.
- `std430` controls the placement and stride of structure members and arrays in this storage buffer. The test depends on those rules matching the host's generated structure model.

## Registration Hierarchy

```text
ssbo.unsized_array_length
└── nested_unsized_arrays
```

[`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231) creates the parent test family, and [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) adds this test case leaf. Mustpass includes `dEQP-VK.ssbo.unsized_array_length.nested_unsized_arrays` and `dEQP-VKSC.ssbo.unsized_array_length.nested_unsized_arrays`.

## Parameter Dimensions and Observed Values

| Dimension | Registered or generated values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `nested_unsized_arrays` | Selects the generated nested-layout and descriptor-array test. | [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) |
| Outer descriptor-array length | `4`, `8`, `12` | Sets the local X size, active `Root` elements, and descriptor-array length after guard ranges are added. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1097-L1103) |
| Nested final-array length | `3`, `6`, `9` | Sets the generated final unsized-array member's element count for the generated test structure. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1097-L1103) |
| Structure contents | Seed-derived arrangement of `float`, `vec3`, `mat2x3`, fixed arrays, structures, and arrays of structures | Varies the layout paths that the generated shader walks before reaching the final unsized array. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1030-L1103) |
| Guard ranges | Two leading and two trailing descriptor ranges | The two leading ranges detect writes before the active outer-array elements. Two trailing ranges are allocated but `verify()` does not compare them. | [`NestedUnsizedArraysTestCase`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L849-L867), [`verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) |

The descriptor range stride is the generated structure's logical size aligned to `minStorageBufferOffsetAlignment`. The full buffer contains `guardZoneCount + outerArrayLen + guardZoneCount` such ranges.

## Behavior Parameters

The primary behavioral axis is the generated outer descriptor-array length. It changes how many compute invocations select descriptors and how many active `Root` elements the verifier expects.

### `4` - four active descriptor ranges

The workgroup has four local invocations. Each invocation selects one of four active ranges after the two leading guard ranges and writes one generated `Root` element.

### `8` - eight active descriptor ranges

The same generated access pattern covers eight active descriptor ranges. This expands the set of invocation-derived non-uniform descriptor indices and expected structures.

### `12` - twelve active descriptor ranges

The workgroup covers twelve active descriptor ranges. The host checks the same two leading ranges before the active data; the two trailing ranges remain allocated but are not part of the comparison.

The nested final-array length and generated field ordering vary the data layout within each selected range. They are generated structure variations rather than separate registered behavior values.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ssbo.unsized_array_length.nested_unsized_arrays
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `outerArrayLen = 12` | Selects twelve active descriptor ranges and sets `local_size_x` to 12. |
| `nestedArrayLen = 3`, base seed `17` | Produces the shown seed-derived nested structure and its runtime-sized `S0_11` member; the generated initial shader seed is `1746455982`. |
| `guardZoneCount = 2` | Makes descriptor index `gl_LocalInvocationID.x + 2` address the active ranges after two leading guard ranges. |

#### Purpose

This compute shader validates that a generated nested `std430` SSBO layout remains addressable through a non-uniform storage-buffer descriptor array. Each invocation writes the expected increasing scalar sequence into one active `Root` element, allowing the host to detect layout, stride, descriptor-selection, and leading-guard corruption.

#### Structural Design

| Phase | Shader operation | Layout or validation significance |
|---|---|---|
| Select range | Read `gl_LocalInvocationID.x`, add 2, and apply `nonuniformEXT` | Maps the 12 local invocations to active descriptor-array elements 2–13, leaving the two leading guards untouched. |
| Walk generated tree | Iterate fixed arrays, structures, vectors, and matrices | Exercises nested member offsets, matrix columns, and array strides within one `Root`. |
| Reach runtime tail | Iterate `S0_11[0..2]` | Exercises the final runtime-sized array member of the SSBO block. |
| Write sequence | Store `seed`, then increment it | Produces deterministic per-member values that the host reconstructs and compares as dwords. |

#### Shader Code

```glsl
/// The generated compute shader uses GLSL 4.50 and the EXT non-uniform qualifier.
#version 450 core
#extension GL_EXT_nonuniform_qualifier : require
/// One local invocation handles one active descriptor range; this representative uses outerArrayLen = 12.
layout(local_size_x = 12, local_size_y = 1, local_size_z = 1) in;
/// The host supplies the initial value and per-invocation increment through push constants.
layout(push_constant) uniform PC {
    float seed;
    int visits;
} pc;
struct S0 {
    vec3   vec3_0;
    mat2x3 mat2x3_1;
    vec3   vec3_2[2];
    mat2x3 mat2x3_3[3];
};
struct S1 {
    vec3   vec3_0;
    mat2x3 mat2x3_1;
    vec3   vec3_2[2];
    mat2x3 mat2x3_3[3];
};
/// std430 lays out the generated Root members; the final S0 array is runtime-sized.
layout(std430, binding = 0) buffer Root {
    S0     S0_0[1];
    S1     S1_1[3];
    float  float_2;
    mat2x3 mat2x3_3[3];
    vec3   vec3_4[2];
    vec3   vec3_5;
    float  float_6[2];
    S0     S0_7;
    S0     S0_8[1];
    S1     S1_9;
    mat2x3 mat2x3_10;
    S0     S0_11[/* 3 */];
} root[/* 2 + 12 + 2 */];
/// Two leading descriptor ranges are guards; active invocations select indices 2 through 13.
void main() {
    /// Each invocation writes a deterministic increasing sequence into its selected Root element.
    /// The invocation-local sequence is disjoint when visits matches the generated structure walk.
    float seed = pc.seed + gl_LocalInvocationID.x * pc.visits;
    for (uint S0_0_0 = 0; S0_0_0 < 1; ++S0_0_0) {
        for (uint vec3_0_1 = 0; vec3_0_1 < 3; ++vec3_0_1) {
            /// The non-uniform descriptor index skips the two leading guard ranges.
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_0[S0_0_0].vec3_0[vec3_0_1] = float(seed++);
        }
        for (uint mat2x3_1_2 = 0; mat2x3_1_2 < 2; ++mat2x3_1_2) {
            for (uint mat2x3_1_3 = 0; mat2x3_1_3 < 3; ++mat2x3_1_3) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_0[S0_0_0].mat2x3_1[mat2x3_1_2][mat2x3_1_3] = float(seed++);
            }
        }
        for (uint vec3_2_4 = 0; vec3_2_4 < 2; ++vec3_2_4) {
            for (uint vec3_0_5 = 0; vec3_0_5 < 3; ++vec3_0_5) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_0[S0_0_0].vec3_2[vec3_2_4][vec3_0_5] = float(seed++);
            }
        }
        for (uint mat2x3_3_6 = 0; mat2x3_3_6 < 3; ++mat2x3_3_6) {
            for (uint mat2x3_0_7 = 0; mat2x3_0_7 < 2; ++mat2x3_0_7) {
                for (uint mat2x3_0_8 = 0; mat2x3_0_8 < 3; ++mat2x3_0_8) {
                    root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_0[S0_0_0].mat2x3_3[mat2x3_3_6][mat2x3_0_7][mat2x3_0_8] = float(seed++);
                }
            }
        }
    }
    for (uint S1_1_9 = 0; S1_1_9 < 3; ++S1_1_9) {
        for (uint vec3_0_10 = 0; vec3_0_10 < 3; ++vec3_0_10) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_1[S1_1_9].vec3_0[vec3_0_10] = float(seed++);
        }
        for (uint mat2x3_1_11 = 0; mat2x3_1_11 < 2; ++mat2x3_1_11) {
            for (uint mat2x3_1_12 = 0; mat2x3_1_12 < 3; ++mat2x3_1_12) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_1[S1_1_9].mat2x3_1[mat2x3_1_11][mat2x3_1_12] = float(seed++);
            }
        }
        for (uint vec3_2_13 = 0; vec3_2_13 < 2; ++vec3_2_13) {
            for (uint vec3_0_14 = 0; vec3_0_14 < 3; ++vec3_0_14) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_1[S1_1_9].vec3_2[vec3_2_13][vec3_0_14] = float(seed++);
            }
        }
        for (uint mat2x3_3_15 = 0; mat2x3_3_15 < 3; ++mat2x3_3_15) {
            for (uint mat2x3_0_16 = 0; mat2x3_0_16 < 2; ++mat2x3_0_16) {
                for (uint mat2x3_0_17 = 0; mat2x3_0_17 < 3; ++mat2x3_0_17) {
                    root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_1[S1_1_9].mat2x3_3[mat2x3_3_15][mat2x3_0_16][mat2x3_0_17] = float(seed++);
                }
            }
        }
    }
    root[nonuniformEXT(gl_LocalInvocationID.x + 2)].float_2 = float(seed++);
    for (uint mat2x3_3_18 = 0; mat2x3_3_18 < 3; ++mat2x3_3_18) {
        for (uint mat2x3_0_19 = 0; mat2x3_0_19 < 2; ++mat2x3_0_19) {
            for (uint mat2x3_0_20 = 0; mat2x3_0_20 < 3; ++mat2x3_0_20) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].mat2x3_3[mat2x3_3_18][mat2x3_0_19][mat2x3_0_20] = float(seed++);
            }
        }
    }
    for (uint vec3_4_21 = 0; vec3_4_21 < 2; ++vec3_4_21) {
        for (uint vec3_0_22 = 0; vec3_0_22 < 3; ++vec3_0_22) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].vec3_4[vec3_4_21][vec3_0_22] = float(seed++);
        }
    }
    for (uint vec3_5_23 = 0; vec3_5_23 < 3; ++vec3_5_23) {
        root[nonuniformEXT(gl_LocalInvocationID.x + 2)].vec3_5[vec3_5_23] = float(seed++);
    }
    for (uint float_6_24 = 0; float_6_24 < 2; ++float_6_24) {
        root[nonuniformEXT(gl_LocalInvocationID.x + 2)].float_6[float_6_24] = float(seed++);
    }
    for (uint vec3_0_25 = 0; vec3_0_25 < 3; ++vec3_0_25) {
        root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_7.vec3_0[vec3_0_25] = float(seed++);
    }
    for (uint mat2x3_1_26 = 0; mat2x3_1_26 < 2; ++mat2x3_1_26) {
        for (uint mat2x3_1_27 = 0; mat2x3_1_27 < 3; ++mat2x3_1_27) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_7.mat2x3_1[mat2x3_1_26][mat2x3_1_27] = float(seed++);
        }
    }
    for (uint vec3_2_28 = 0; vec3_2_28 < 2; ++vec3_2_28) {
        for (uint vec3_0_29 = 0; vec3_0_29 < 3; ++vec3_0_29) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_7.vec3_2[vec3_2_28][vec3_0_29] = float(seed++);
        }
    }
    for (uint mat2x3_3_30 = 0; mat2x3_3_30 < 3; ++mat2x3_3_30) {
        for (uint mat2x3_0_31 = 0; mat2x3_0_31 < 2; ++mat2x3_0_31) {
            for (uint mat2x3_0_32 = 0; mat2x3_0_32 < 3; ++mat2x3_0_32) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_7.mat2x3_3[mat2x3_3_30][mat2x3_0_31][mat2x3_0_32] = float(seed++);
            }
        }
    }
    for (uint S0_8_33 = 0; S0_8_33 < 1; ++S0_8_33) {
        for (uint vec3_0_34 = 0; vec3_0_34 < 3; ++vec3_0_34) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_8[S0_8_33].vec3_0[vec3_0_34] = float(seed++);
        }
        for (uint mat2x3_1_35 = 0; mat2x3_1_35 < 2; ++mat2x3_1_35) {
            for (uint mat2x3_1_36 = 0; mat2x3_1_36 < 3; ++mat2x3_1_36) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_8[S0_8_33].mat2x3_1[mat2x3_1_35][mat2x3_1_36] = float(seed++);
            }
        }
        for (uint vec3_2_37 = 0; vec3_2_37 < 2; ++vec3_2_37) {
            for (uint vec3_0_38 = 0; vec3_0_38 < 3; ++vec3_0_38) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_8[S0_8_33].vec3_2[vec3_2_37][vec3_0_38] = float(seed++);
            }
        }
        for (uint mat2x3_3_39 = 0; mat2x3_3_39 < 3; ++mat2x3_3_39) {
            for (uint mat2x3_0_40 = 0; mat2x3_0_40 < 2; ++mat2x3_0_40) {
                for (uint mat2x3_0_41 = 0; mat2x3_0_41 < 3; ++mat2x3_0_41) {
                    root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_8[S0_8_33].mat2x3_3[mat2x3_3_39][mat2x3_0_40][mat2x3_0_41] = float(seed++);
                }
            }
        }
    }
    for (uint vec3_0_42 = 0; vec3_0_42 < 3; ++vec3_0_42) {
        root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_9.vec3_0[vec3_0_42] = float(seed++);
    }
    for (uint mat2x3_1_43 = 0; mat2x3_1_43 < 2; ++mat2x3_1_43) {
        for (uint mat2x3_1_44 = 0; mat2x3_1_44 < 3; ++mat2x3_1_44) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_9.mat2x3_1[mat2x3_1_43][mat2x3_1_44] = float(seed++);
        }
    }
    for (uint vec3_2_45 = 0; vec3_2_45 < 2; ++vec3_2_45) {
        for (uint vec3_0_46 = 0; vec3_0_46 < 3; ++vec3_0_46) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_9.vec3_2[vec3_2_45][vec3_0_46] = float(seed++);
        }
    }
    for (uint mat2x3_3_47 = 0; mat2x3_3_47 < 3; ++mat2x3_3_47) {
        for (uint mat2x3_0_48 = 0; mat2x3_0_48 < 2; ++mat2x3_0_48) {
            for (uint mat2x3_0_49 = 0; mat2x3_0_49 < 3; ++mat2x3_0_49) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S1_9.mat2x3_3[mat2x3_3_47][mat2x3_0_48][mat2x3_0_49] = float(seed++);
            }
        }
    }
    for (uint mat2x3_10_50 = 0; mat2x3_10_50 < 2; ++mat2x3_10_50) {
        for (uint mat2x3_10_51 = 0; mat2x3_10_51 < 3; ++mat2x3_10_51) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].mat2x3_10[mat2x3_10_50][mat2x3_10_51] = float(seed++);
        }
    }
    for (uint S0_11_52 = 0; S0_11_52 < 3; ++S0_11_52) {
        for (uint vec3_0_53 = 0; vec3_0_53 < 3; ++vec3_0_53) {
            root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_11[S0_11_52].vec3_0[vec3_0_53] = float(seed++);
        }
        for (uint mat2x3_1_54 = 0; mat2x3_1_54 < 2; ++mat2x3_1_54) {
            for (uint mat2x3_1_55 = 0; mat2x3_1_55 < 3; ++mat2x3_1_55) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_11[S0_11_52].mat2x3_1[mat2x3_1_54][mat2x3_1_55] = float(seed++);
            }
        }
        for (uint vec3_2_56 = 0; vec3_2_56 < 2; ++vec3_2_56) {
            for (uint vec3_0_57 = 0; vec3_0_57 < 3; ++vec3_0_57) {
                root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_11[S0_11_52].vec3_2[vec3_2_56][vec3_0_57] = float(seed++);
            }
        }
        for (uint mat2x3_3_58 = 0; mat2x3_3_58 < 3; ++mat2x3_3_58) {
            for (uint mat2x3_0_59 = 0; mat2x3_0_59 < 2; ++mat2x3_0_59) {
                for (uint mat2x3_0_60 = 0; mat2x3_0_60 < 3; ++mat2x3_0_60) {
                    root[nonuniformEXT(gl_LocalInvocationID.x + 2)].S0_11[S0_11_52].mat2x3_3[mat2x3_3_58][mat2x3_0_59][mat2x3_0_60] = float(seed++);
                }
            }
        }
    }
}
```

#### Additional Info

- The generated `Root` has a 176-byte structure stride in the shown assembly; the host separately aligns each descriptor range to `minStorageBufferOffsetAlignment`.
- `root[/* 2 + 12 + 2 */]` documents the two leading and two trailing allocated ranges. The verifier compares the two leading ranges and all active ranges, but not the trailing ranges.
- The exact field order and loop bounds are deterministic for this seed-derived representative; other base seeds can generate different nested declarations while retaining the same generator path.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Outer descriptor-array length | Changes `local_size_x`, the descriptor-array extent, and the active index range after the two leading guards. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1097-L1103), [`initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1119-L1151) |
| Nested final-array length | Changes the generated runtime-array bound and the corresponding loop count in the generated walk. | [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1027-L1104), [`SG::generateLoops()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1070-L1094) |
| Base seed | Changes generated type/order choices, member declarations, and emitted loop sequence. | [`NestedUnsizedArraysTestCase::delayedInit()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1011-L1025), [`generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1027-L1104) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 964
; Schema: 0
               OpCapability Shader
               OpCapability ShaderNonUniform
               OpCapability RuntimeDescriptorArray
               OpCapability StorageBufferArrayNonUniformIndexing
               OpExtension "SPV_EXT_descriptor_indexing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID
               OpExecutionMode %main LocalSize 12 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpName %main "main"
               OpName %seed "seed"
               OpName %PC "PC"
               OpMemberName %PC 0 "seed"
               OpMemberName %PC 1 "visits"
               OpName %pc "pc"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %S0_0_0 "S0_0_0"
               OpName %vec3_0_1 "vec3_0_1"
               OpName %S0 "S0"
               OpMemberName %S0 0 "vec3_0"
               OpMemberName %S0 1 "mat2x3_1"
               OpMemberName %S0 2 "vec3_2"
               OpMemberName %S0 3 "mat2x3_3"
               OpName %S1 "S1"
               OpMemberName %S1 0 "vec3_0"
               OpMemberName %S1 1 "mat2x3_1"
               OpMemberName %S1 2 "vec3_2"
               OpMemberName %S1 3 "mat2x3_3"
               OpName %Root "Root"
               OpMemberName %Root 0 "S0_0"
               OpMemberName %Root 1 "S1_1"
               OpMemberName %Root 2 "float_2"
               OpMemberName %Root 3 "mat2x3_3"
               OpMemberName %Root 4 "vec3_4"
               OpMemberName %Root 5 "vec3_5"
               OpMemberName %Root 6 "float_6"
               OpMemberName %Root 7 "S0_7"
               OpMemberName %Root 8 "S0_8"
               OpMemberName %Root 9 "S1_9"
               OpMemberName %Root 10 "mat2x3_10"
               OpMemberName %Root 11 "S0_11"
               OpName %root "root"
               OpName %mat2x3_1_2 "mat2x3_1_2"
               OpName %mat2x3_1_3 "mat2x3_1_3"
               OpName %vec3_2_4 "vec3_2_4"
               OpName %vec3_0_5 "vec3_0_5"
               OpName %mat2x3_3_6 "mat2x3_3_6"
               OpName %mat2x3_0_7 "mat2x3_0_7"
               OpName %mat2x3_0_8 "mat2x3_0_8"
               OpName %S1_1_9 "S1_1_9"
               OpName %vec3_0_10 "vec3_0_10"
               OpName %mat2x3_1_11 "mat2x3_1_11"
               OpName %mat2x3_1_12 "mat2x3_1_12"
               OpName %vec3_2_13 "vec3_2_13"
               OpName %vec3_0_14 "vec3_0_14"
               OpName %mat2x3_3_15 "mat2x3_3_15"
               OpName %mat2x3_0_16 "mat2x3_0_16"
               OpName %mat2x3_0_17 "mat2x3_0_17"
               OpName %mat2x3_3_18 "mat2x3_3_18"
               OpName %mat2x3_0_19 "mat2x3_0_19"
               OpName %mat2x3_0_20 "mat2x3_0_20"
               OpName %vec3_4_21 "vec3_4_21"
               OpName %vec3_0_22 "vec3_0_22"
               OpName %vec3_5_23 "vec3_5_23"
               OpName %float_6_24 "float_6_24"
               OpName %vec3_0_25 "vec3_0_25"
               OpName %mat2x3_1_26 "mat2x3_1_26"
               OpName %mat2x3_1_27 "mat2x3_1_27"
               OpName %vec3_2_28 "vec3_2_28"
               OpName %vec3_0_29 "vec3_0_29"
               OpName %mat2x3_3_30 "mat2x3_3_30"
               OpName %mat2x3_0_31 "mat2x3_0_31"
               OpName %mat2x3_0_32 "mat2x3_0_32"
               OpName %S0_8_33 "S0_8_33"
               OpName %vec3_0_34 "vec3_0_34"
               OpName %mat2x3_1_35 "mat2x3_1_35"
               OpName %mat2x3_1_36 "mat2x3_1_36"
               OpName %vec3_2_37 "vec3_2_37"
               OpName %vec3_0_38 "vec3_0_38"
               OpName %mat2x3_3_39 "mat2x3_3_39"
               OpName %mat2x3_0_40 "mat2x3_0_40"
               OpName %mat2x3_0_41 "mat2x3_0_41"
               OpName %vec3_0_42 "vec3_0_42"
               OpName %mat2x3_1_43 "mat2x3_1_43"
               OpName %mat2x3_1_44 "mat2x3_1_44"
               OpName %vec3_2_45 "vec3_2_45"
               OpName %vec3_0_46 "vec3_0_46"
               OpName %mat2x3_3_47 "mat2x3_3_47"
               OpName %mat2x3_0_48 "mat2x3_0_48"
               OpName %mat2x3_0_49 "mat2x3_0_49"
               OpName %mat2x3_10_50 "mat2x3_10_50"
               OpName %mat2x3_10_51 "mat2x3_10_51"
               OpName %S0_11_52 "S0_11_52"
               OpName %vec3_0_53 "vec3_0_53"
               OpName %mat2x3_1_54 "mat2x3_1_54"
               OpName %mat2x3_1_55 "mat2x3_1_55"
               OpName %vec3_2_56 "vec3_2_56"
               OpName %vec3_0_57 "vec3_0_57"
               OpName %mat2x3_3_58 "mat2x3_3_58"
               OpName %mat2x3_0_59 "mat2x3_0_59"
               OpName %mat2x3_0_60 "mat2x3_0_60"
               OpDecorate %PC Block
               OpMemberDecorate %PC 0 Offset 0
               OpMemberDecorate %PC 1 Offset 4
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %_arr_v3float_uint_2 ArrayStride 16
               OpDecorate %_arr_mat2v3float_uint_3 ArrayStride 32
               OpMemberDecorate %S0 0 Offset 0
               OpMemberDecorate %S0 1 ColMajor
               OpMemberDecorate %S0 1 MatrixStride 16
               OpMemberDecorate %S0 1 Offset 16
               OpMemberDecorate %S0 2 Offset 48
               OpMemberDecorate %S0 3 ColMajor
               OpMemberDecorate %S0 3 MatrixStride 16
               OpMemberDecorate %S0 3 Offset 80
               OpDecorate %_arr_S0_uint_1 ArrayStride 176
               OpDecorate %_arr_v3float_uint_2_0 ArrayStride 16
               OpDecorate %_arr_mat2v3float_uint_3_0 ArrayStride 32
               OpMemberDecorate %S1 0 Offset 0
               OpMemberDecorate %S1 1 ColMajor
               OpMemberDecorate %S1 1 MatrixStride 16
               OpMemberDecorate %S1 1 Offset 16
               OpMemberDecorate %S1 2 Offset 48
               OpMemberDecorate %S1 3 ColMajor
               OpMemberDecorate %S1 3 MatrixStride 16
               OpMemberDecorate %S1 3 Offset 80
               OpDecorate %_arr_S1_uint_3 ArrayStride 176
               OpDecorate %_arr_mat2v3float_uint_3_1 ArrayStride 32
               OpDecorate %_arr_v3float_uint_2_1 ArrayStride 16
               OpDecorate %_arr_float_uint_2 ArrayStride 4
               OpDecorate %_arr_S0_uint_1_0 ArrayStride 176
               OpDecorate %_runtimearr_S0 ArrayStride 176
               OpDecorate %Root BufferBlock
               OpMemberDecorate %Root 0 Offset 0
               OpMemberDecorate %Root 1 Offset 176
               OpMemberDecorate %Root 2 Offset 704
               OpMemberDecorate %Root 3 ColMajor
               OpMemberDecorate %Root 3 MatrixStride 16
               OpMemberDecorate %Root 3 Offset 720
               OpMemberDecorate %Root 4 Offset 816
               OpMemberDecorate %Root 5 Offset 848
               OpMemberDecorate %Root 6 Offset 860
               OpMemberDecorate %Root 7 Offset 880
               OpMemberDecorate %Root 8 Offset 1056
               OpMemberDecorate %Root 9 Offset 1232
               OpMemberDecorate %Root 10 ColMajor
               OpMemberDecorate %Root 10 MatrixStride 16
               OpMemberDecorate %Root 10 Offset 1408
               OpMemberDecorate %Root 11 Offset 1440
               OpDecorate %root Binding 0
               OpDecorate %root DescriptorSet 0
               OpDecorate %76 NonUniform
               OpDecorate %83 NonUniform
               OpDecorate %105 NonUniform
               OpDecorate %111 NonUniform
               OpDecorate %135 NonUniform
               OpDecorate %142 NonUniform
               OpDecorate %174 NonUniform
               OpDecorate %182 NonUniform
               OpDecorate %210 NonUniform
               OpDecorate %215 NonUniform
               OpDecorate %237 NonUniform
               OpDecorate %243 NonUniform
               OpDecorate %267 NonUniform
               OpDecorate %273 NonUniform
               OpDecorate %305 NonUniform
               OpDecorate %312 NonUniform
               OpDecorate %324 NonUniform
               OpDecorate %327 NonUniform
               OpDecorate %355 NonUniform
               OpDecorate %361 NonUniform
               OpDecorate %387 NonUniform
               OpDecorate %393 NonUniform
               OpDecorate %409 NonUniform
               OpDecorate %414 NonUniform
               OpDecorate %428 NonUniform
               OpDecorate %433 NonUniform
               OpDecorate %447 NonUniform
               OpDecorate %452 NonUniform
               OpDecorate %474 NonUniform
               OpDecorate %479 NonUniform
               OpDecorate %503 NonUniform
               OpDecorate %508 NonUniform
               OpDecorate %540 NonUniform
               OpDecorate %546 NonUniform
               OpDecorate %572 NonUniform
               OpDecorate %578 NonUniform
               OpDecorate %600 NonUniform
               OpDecorate %606 NonUniform
               OpDecorate %630 NonUniform
               OpDecorate %636 NonUniform
               OpDecorate %668 NonUniform
               OpDecorate %675 NonUniform
               OpDecorate %695 NonUniform
               OpDecorate %700 NonUniform
               OpDecorate %722 NonUniform
               OpDecorate %727 NonUniform
               OpDecorate %751 NonUniform
               OpDecorate %756 NonUniform
               OpDecorate %788 NonUniform
               OpDecorate %794 NonUniform
               OpDecorate %820 NonUniform
               OpDecorate %826 NonUniform
               OpDecorate %850 NonUniform
               OpDecorate %856 NonUniform
               OpDecorate %878 NonUniform
               OpDecorate %884 NonUniform
               OpDecorate %908 NonUniform
               OpDecorate %914 NonUniform
               OpDecorate %946 NonUniform
               OpDecorate %953 NonUniform
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
        %int = OpTypeInt 32 1
         %PC = OpTypeStruct %float %int
%_ptr_PushConstant_PC = OpTypePointer PushConstant %PC
         %pc = OpVariable %_ptr_PushConstant_PC PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
     %uint_3 = OpConstant %uint 3
    %v3float = OpTypeVector %float 3
%mat2v3float = OpTypeMatrix %v3float 2
     %uint_2 = OpConstant %uint 2
%_arr_v3float_uint_2 = OpTypeArray %v3float %uint_2
%_arr_mat2v3float_uint_3 = OpTypeArray %mat2v3float %uint_3
         %S0 = OpTypeStruct %v3float %mat2v3float %_arr_v3float_uint_2 %_arr_mat2v3float_uint_3
%_arr_S0_uint_1 = OpTypeArray %S0 %uint_1
%_arr_v3float_uint_2_0 = OpTypeArray %v3float %uint_2
%_arr_mat2v3float_uint_3_0 = OpTypeArray %mat2v3float %uint_3
         %S1 = OpTypeStruct %v3float %mat2v3float %_arr_v3float_uint_2_0 %_arr_mat2v3float_uint_3_0
%_arr_S1_uint_3 = OpTypeArray %S1 %uint_3
%_arr_mat2v3float_uint_3_1 = OpTypeArray %mat2v3float %uint_3
%_arr_v3float_uint_2_1 = OpTypeArray %v3float %uint_2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_arr_S0_uint_1_0 = OpTypeArray %S0 %uint_1
%_runtimearr_S0 = OpTypeRuntimeArray %S0
       %Root = OpTypeStruct %_arr_S0_uint_1 %_arr_S1_uint_3 %float %_arr_mat2v3float_uint_3_1 %_arr_v3float_uint_2_1 %v3float %_arr_float_uint_2 %S0 %_arr_S0_uint_1_0 %S1 %mat2v3float %_runtimearr_S0
%_runtimearr_Root = OpTypeRuntimeArray %Root
%_ptr_Uniform__runtimearr_Root = OpTypePointer Uniform %_runtimearr_Root
       %root = OpVariable %_ptr_Uniform__runtimearr_Root Uniform
    %float_1 = OpConstant %float 1
%_ptr_Uniform_float = OpTypePointer Uniform %float
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
      %int_6 = OpConstant %int 6
      %int_7 = OpConstant %int 7
      %int_8 = OpConstant %int 8
      %int_9 = OpConstant %int 9
     %int_10 = OpConstant %int 10
     %int_11 = OpConstant %int 11
    %uint_12 = OpConstant %uint 12
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_12 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %seed = OpVariable %_ptr_Function_float Function
     %S0_0_0 = OpVariable %_ptr_Function_uint Function
   %vec3_0_1 = OpVariable %_ptr_Function_uint Function
 %mat2x3_1_2 = OpVariable %_ptr_Function_uint Function
 %mat2x3_1_3 = OpVariable %_ptr_Function_uint Function
   %vec3_2_4 = OpVariable %_ptr_Function_uint Function
   %vec3_0_5 = OpVariable %_ptr_Function_uint Function
 %mat2x3_3_6 = OpVariable %_ptr_Function_uint Function
 %mat2x3_0_7 = OpVariable %_ptr_Function_uint Function
 %mat2x3_0_8 = OpVariable %_ptr_Function_uint Function
     %S1_1_9 = OpVariable %_ptr_Function_uint Function
  %vec3_0_10 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_11 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_12 = OpVariable %_ptr_Function_uint Function
  %vec3_2_13 = OpVariable %_ptr_Function_uint Function
  %vec3_0_14 = OpVariable %_ptr_Function_uint Function
%mat2x3_3_15 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_16 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_17 = OpVariable %_ptr_Function_uint Function
%mat2x3_3_18 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_19 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_20 = OpVariable %_ptr_Function_uint Function
  %vec3_4_21 = OpVariable %_ptr_Function_uint Function
  %vec3_0_22 = OpVariable %_ptr_Function_uint Function
  %vec3_5_23 = OpVariable %_ptr_Function_uint Function
 %float_6_24 = OpVariable %_ptr_Function_uint Function
  %vec3_0_25 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_26 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_27 = OpVariable %_ptr_Function_uint Function
  %vec3_2_28 = OpVariable %_ptr_Function_uint Function
  %vec3_0_29 = OpVariable %_ptr_Function_uint Function
%mat2x3_3_30 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_31 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_32 = OpVariable %_ptr_Function_uint Function
    %S0_8_33 = OpVariable %_ptr_Function_uint Function
  %vec3_0_34 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_35 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_36 = OpVariable %_ptr_Function_uint Function
  %vec3_2_37 = OpVariable %_ptr_Function_uint Function
  %vec3_0_38 = OpVariable %_ptr_Function_uint Function
%mat2x3_3_39 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_40 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_41 = OpVariable %_ptr_Function_uint Function
  %vec3_0_42 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_43 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_44 = OpVariable %_ptr_Function_uint Function
  %vec3_2_45 = OpVariable %_ptr_Function_uint Function
  %vec3_0_46 = OpVariable %_ptr_Function_uint Function
%mat2x3_3_47 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_48 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_49 = OpVariable %_ptr_Function_uint Function
%mat2x3_10_50 = OpVariable %_ptr_Function_uint Function
%mat2x3_10_51 = OpVariable %_ptr_Function_uint Function
   %S0_11_52 = OpVariable %_ptr_Function_uint Function
  %vec3_0_53 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_54 = OpVariable %_ptr_Function_uint Function
%mat2x3_1_55 = OpVariable %_ptr_Function_uint Function
  %vec3_2_56 = OpVariable %_ptr_Function_uint Function
  %vec3_0_57 = OpVariable %_ptr_Function_uint Function
%mat2x3_3_58 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_59 = OpVariable %_ptr_Function_uint Function
%mat2x3_0_60 = OpVariable %_ptr_Function_uint Function
         %15 = OpAccessChain %_ptr_PushConstant_float %pc %int_0
         %16 = OpLoad %float %15
         %23 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %24 = OpLoad %uint %23
         %27 = OpAccessChain %_ptr_PushConstant_int %pc %int_1
         %28 = OpLoad %int %27
         %29 = OpBitcast %uint %28
         %30 = OpIMul %uint %24 %29
         %31 = OpConvertUToF %float %30
         %32 = OpFAdd %float %16 %31
               OpStore %seed %32
               OpStore %S0_0_0 %uint_0
               OpBranch %35
         %35 = OpLabel
               OpLoopMerge %37 %38 None
               OpBranch %39
         %39 = OpLabel
         %40 = OpLoad %uint %S0_0_0
         %43 = OpULessThan %bool %40 %uint_1
               OpBranchConditional %43 %36 %37
         %36 = OpLabel
               OpStore %vec3_0_1 %uint_0
               OpBranch %45
         %45 = OpLabel
               OpLoopMerge %47 %48 None
               OpBranch %49
         %49 = OpLabel
         %50 = OpLoad %uint %vec3_0_1
         %52 = OpULessThan %bool %50 %uint_3
               OpBranchConditional %52 %46 %47
         %46 = OpLabel
         %73 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %74 = OpLoad %uint %73
         %75 = OpIAdd %uint %74 %uint_2
         %76 = OpCopyObject %uint %75
         %77 = OpLoad %uint %S0_0_0
         %78 = OpLoad %uint %vec3_0_1
         %79 = OpLoad %float %seed
         %81 = OpFAdd %float %79 %float_1
               OpStore %seed %81
         %83 = OpAccessChain %_ptr_Uniform_float %root %76 %int_0 %77 %int_0 %78
               OpStore %83 %79
               OpBranch %48
         %48 = OpLabel
         %84 = OpLoad %uint %vec3_0_1
         %85 = OpIAdd %uint %84 %int_1
               OpStore %vec3_0_1 %85
               OpBranch %45
         %47 = OpLabel
               OpStore %mat2x3_1_2 %uint_0
               OpBranch %87
         %87 = OpLabel
               OpLoopMerge %89 %90 None
               OpBranch %91
         %91 = OpLabel
         %92 = OpLoad %uint %mat2x3_1_2
         %93 = OpULessThan %bool %92 %uint_2
               OpBranchConditional %93 %88 %89
         %88 = OpLabel
               OpStore %mat2x3_1_3 %uint_0
               OpBranch %95
         %95 = OpLabel
               OpLoopMerge %97 %98 None
               OpBranch %99
         %99 = OpLabel
        %100 = OpLoad %uint %mat2x3_1_3
        %101 = OpULessThan %bool %100 %uint_3
               OpBranchConditional %101 %96 %97
         %96 = OpLabel
        %102 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %103 = OpLoad %uint %102
        %104 = OpIAdd %uint %103 %uint_2
        %105 = OpCopyObject %uint %104
        %106 = OpLoad %uint %S0_0_0
        %107 = OpLoad %uint %mat2x3_1_2
        %108 = OpLoad %uint %mat2x3_1_3
        %109 = OpLoad %float %seed
        %110 = OpFAdd %float %109 %float_1
               OpStore %seed %110
        %111 = OpAccessChain %_ptr_Uniform_float %root %105 %int_0 %106 %int_1 %107 %108
               OpStore %111 %109
               OpBranch %98
         %98 = OpLabel
        %112 = OpLoad %uint %mat2x3_1_3
        %113 = OpIAdd %uint %112 %int_1
               OpStore %mat2x3_1_3 %113
               OpBranch %95
         %97 = OpLabel
               OpBranch %90
         %90 = OpLabel
        %114 = OpLoad %uint %mat2x3_1_2
        %115 = OpIAdd %uint %114 %int_1
               OpStore %mat2x3_1_2 %115
               OpBranch %87
         %89 = OpLabel
               OpStore %vec3_2_4 %uint_0
               OpBranch %117
        %117 = OpLabel
               OpLoopMerge %119 %120 None
               OpBranch %121
        %121 = OpLabel
        %122 = OpLoad %uint %vec3_2_4
        %123 = OpULessThan %bool %122 %uint_2
               OpBranchConditional %123 %118 %119
        %118 = OpLabel
               OpStore %vec3_0_5 %uint_0
               OpBranch %125
        %125 = OpLabel
               OpLoopMerge %127 %128 None
               OpBranch %129
        %129 = OpLabel
        %130 = OpLoad %uint %vec3_0_5
        %131 = OpULessThan %bool %130 %uint_3
               OpBranchConditional %131 %126 %127
        %126 = OpLabel
        %132 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %133 = OpLoad %uint %132
        %134 = OpIAdd %uint %133 %uint_2
        %135 = OpCopyObject %uint %134
        %136 = OpLoad %uint %S0_0_0
        %138 = OpLoad %uint %vec3_2_4
        %139 = OpLoad %uint %vec3_0_5
        %140 = OpLoad %float %seed
        %141 = OpFAdd %float %140 %float_1
               OpStore %seed %141
        %142 = OpAccessChain %_ptr_Uniform_float %root %135 %int_0 %136 %int_2 %138 %139
               OpStore %142 %140
               OpBranch %128
        %128 = OpLabel
        %143 = OpLoad %uint %vec3_0_5
        %144 = OpIAdd %uint %143 %int_1
               OpStore %vec3_0_5 %144
               OpBranch %125
        %127 = OpLabel
               OpBranch %120
        %120 = OpLabel
        %145 = OpLoad %uint %vec3_2_4
        %146 = OpIAdd %uint %145 %int_1
               OpStore %vec3_2_4 %146
               OpBranch %117
        %119 = OpLabel
               OpStore %mat2x3_3_6 %uint_0
               OpBranch %148
        %148 = OpLabel
               OpLoopMerge %150 %151 None
               OpBranch %152
        %152 = OpLabel
        %153 = OpLoad %uint %mat2x3_3_6
        %154 = OpULessThan %bool %153 %uint_3
               OpBranchConditional %154 %149 %150
        %149 = OpLabel
               OpStore %mat2x3_0_7 %uint_0
               OpBranch %156
        %156 = OpLabel
               OpLoopMerge %158 %159 None
               OpBranch %160
        %160 = OpLabel
        %161 = OpLoad %uint %mat2x3_0_7
        %162 = OpULessThan %bool %161 %uint_2
               OpBranchConditional %162 %157 %158
        %157 = OpLabel
               OpStore %mat2x3_0_8 %uint_0
               OpBranch %164
        %164 = OpLabel
               OpLoopMerge %166 %167 None
               OpBranch %168
        %168 = OpLabel
        %169 = OpLoad %uint %mat2x3_0_8
        %170 = OpULessThan %bool %169 %uint_3
               OpBranchConditional %170 %165 %166
        %165 = OpLabel
        %171 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %172 = OpLoad %uint %171
        %173 = OpIAdd %uint %172 %uint_2
        %174 = OpCopyObject %uint %173
        %175 = OpLoad %uint %S0_0_0
        %177 = OpLoad %uint %mat2x3_3_6
        %178 = OpLoad %uint %mat2x3_0_7
        %179 = OpLoad %uint %mat2x3_0_8
        %180 = OpLoad %float %seed
        %181 = OpFAdd %float %180 %float_1
               OpStore %seed %181
        %182 = OpAccessChain %_ptr_Uniform_float %root %174 %int_0 %175 %int_3 %177 %178 %179
               OpStore %182 %180
               OpBranch %167
        %167 = OpLabel
        %183 = OpLoad %uint %mat2x3_0_8
        %184 = OpIAdd %uint %183 %int_1
               OpStore %mat2x3_0_8 %184
               OpBranch %164
        %166 = OpLabel
               OpBranch %159
        %159 = OpLabel
        %185 = OpLoad %uint %mat2x3_0_7
        %186 = OpIAdd %uint %185 %int_1
               OpStore %mat2x3_0_7 %186
               OpBranch %156
        %158 = OpLabel
               OpBranch %151
        %151 = OpLabel
        %187 = OpLoad %uint %mat2x3_3_6
        %188 = OpIAdd %uint %187 %int_1
               OpStore %mat2x3_3_6 %188
               OpBranch %148
        %150 = OpLabel
               OpBranch %38
         %38 = OpLabel
        %189 = OpLoad %uint %S0_0_0
        %190 = OpIAdd %uint %189 %int_1
               OpStore %S0_0_0 %190
               OpBranch %35
         %37 = OpLabel
               OpStore %S1_1_9 %uint_0
               OpBranch %192
        %192 = OpLabel
               OpLoopMerge %194 %195 None
               OpBranch %196
        %196 = OpLabel
        %197 = OpLoad %uint %S1_1_9
        %198 = OpULessThan %bool %197 %uint_3
               OpBranchConditional %198 %193 %194
        %193 = OpLabel
               OpStore %vec3_0_10 %uint_0
               OpBranch %200
        %200 = OpLabel
               OpLoopMerge %202 %203 None
               OpBranch %204
        %204 = OpLabel
        %205 = OpLoad %uint %vec3_0_10
        %206 = OpULessThan %bool %205 %uint_3
               OpBranchConditional %206 %201 %202
        %201 = OpLabel
        %207 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %208 = OpLoad %uint %207
        %209 = OpIAdd %uint %208 %uint_2
        %210 = OpCopyObject %uint %209
        %211 = OpLoad %uint %S1_1_9
        %212 = OpLoad %uint %vec3_0_10
        %213 = OpLoad %float %seed
        %214 = OpFAdd %float %213 %float_1
               OpStore %seed %214
        %215 = OpAccessChain %_ptr_Uniform_float %root %210 %int_1 %211 %int_0 %212
               OpStore %215 %213
               OpBranch %203
        %203 = OpLabel
        %216 = OpLoad %uint %vec3_0_10
        %217 = OpIAdd %uint %216 %int_1
               OpStore %vec3_0_10 %217
               OpBranch %200
        %202 = OpLabel
               OpStore %mat2x3_1_11 %uint_0
               OpBranch %219
        %219 = OpLabel
               OpLoopMerge %221 %222 None
               OpBranch %223
        %223 = OpLabel
        %224 = OpLoad %uint %mat2x3_1_11
        %225 = OpULessThan %bool %224 %uint_2
               OpBranchConditional %225 %220 %221
        %220 = OpLabel
               OpStore %mat2x3_1_12 %uint_0
               OpBranch %227
        %227 = OpLabel
               OpLoopMerge %229 %230 None
               OpBranch %231
        %231 = OpLabel
        %232 = OpLoad %uint %mat2x3_1_12
        %233 = OpULessThan %bool %232 %uint_3
               OpBranchConditional %233 %228 %229
        %228 = OpLabel
        %234 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %235 = OpLoad %uint %234
        %236 = OpIAdd %uint %235 %uint_2
        %237 = OpCopyObject %uint %236
        %238 = OpLoad %uint %S1_1_9
        %239 = OpLoad %uint %mat2x3_1_11
        %240 = OpLoad %uint %mat2x3_1_12
        %241 = OpLoad %float %seed
        %242 = OpFAdd %float %241 %float_1
               OpStore %seed %242
        %243 = OpAccessChain %_ptr_Uniform_float %root %237 %int_1 %238 %int_1 %239 %240
               OpStore %243 %241
               OpBranch %230
        %230 = OpLabel
        %244 = OpLoad %uint %mat2x3_1_12
        %245 = OpIAdd %uint %244 %int_1
               OpStore %mat2x3_1_12 %245
               OpBranch %227
        %229 = OpLabel
               OpBranch %222
        %222 = OpLabel
        %246 = OpLoad %uint %mat2x3_1_11
        %247 = OpIAdd %uint %246 %int_1
               OpStore %mat2x3_1_11 %247
               OpBranch %219
        %221 = OpLabel
               OpStore %vec3_2_13 %uint_0
               OpBranch %249
        %249 = OpLabel
               OpLoopMerge %251 %252 None
               OpBranch %253
        %253 = OpLabel
        %254 = OpLoad %uint %vec3_2_13
        %255 = OpULessThan %bool %254 %uint_2
               OpBranchConditional %255 %250 %251
        %250 = OpLabel
               OpStore %vec3_0_14 %uint_0
               OpBranch %257
        %257 = OpLabel
               OpLoopMerge %259 %260 None
               OpBranch %261
        %261 = OpLabel
        %262 = OpLoad %uint %vec3_0_14
        %263 = OpULessThan %bool %262 %uint_3
               OpBranchConditional %263 %258 %259
        %258 = OpLabel
        %264 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %265 = OpLoad %uint %264
        %266 = OpIAdd %uint %265 %uint_2
        %267 = OpCopyObject %uint %266
        %268 = OpLoad %uint %S1_1_9
        %269 = OpLoad %uint %vec3_2_13
        %270 = OpLoad %uint %vec3_0_14
        %271 = OpLoad %float %seed
        %272 = OpFAdd %float %271 %float_1
               OpStore %seed %272
        %273 = OpAccessChain %_ptr_Uniform_float %root %267 %int_1 %268 %int_2 %269 %270
               OpStore %273 %271
               OpBranch %260
        %260 = OpLabel
        %274 = OpLoad %uint %vec3_0_14
        %275 = OpIAdd %uint %274 %int_1
               OpStore %vec3_0_14 %275
               OpBranch %257
        %259 = OpLabel
               OpBranch %252
        %252 = OpLabel
        %276 = OpLoad %uint %vec3_2_13
        %277 = OpIAdd %uint %276 %int_1
               OpStore %vec3_2_13 %277
               OpBranch %249
        %251 = OpLabel
               OpStore %mat2x3_3_15 %uint_0
               OpBranch %279
        %279 = OpLabel
               OpLoopMerge %281 %282 None
               OpBranch %283
        %283 = OpLabel
        %284 = OpLoad %uint %mat2x3_3_15
        %285 = OpULessThan %bool %284 %uint_3
               OpBranchConditional %285 %280 %281
        %280 = OpLabel
               OpStore %mat2x3_0_16 %uint_0
               OpBranch %287
        %287 = OpLabel
               OpLoopMerge %289 %290 None
               OpBranch %291
        %291 = OpLabel
        %292 = OpLoad %uint %mat2x3_0_16
        %293 = OpULessThan %bool %292 %uint_2
               OpBranchConditional %293 %288 %289
        %288 = OpLabel
               OpStore %mat2x3_0_17 %uint_0
               OpBranch %295
        %295 = OpLabel
               OpLoopMerge %297 %298 None
               OpBranch %299
        %299 = OpLabel
        %300 = OpLoad %uint %mat2x3_0_17
        %301 = OpULessThan %bool %300 %uint_3
               OpBranchConditional %301 %296 %297
        %296 = OpLabel
        %302 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %303 = OpLoad %uint %302
        %304 = OpIAdd %uint %303 %uint_2
        %305 = OpCopyObject %uint %304
        %306 = OpLoad %uint %S1_1_9
        %307 = OpLoad %uint %mat2x3_3_15
        %308 = OpLoad %uint %mat2x3_0_16
        %309 = OpLoad %uint %mat2x3_0_17
        %310 = OpLoad %float %seed
        %311 = OpFAdd %float %310 %float_1
               OpStore %seed %311
        %312 = OpAccessChain %_ptr_Uniform_float %root %305 %int_1 %306 %int_3 %307 %308 %309
               OpStore %312 %310
               OpBranch %298
        %298 = OpLabel
        %313 = OpLoad %uint %mat2x3_0_17
        %314 = OpIAdd %uint %313 %int_1
               OpStore %mat2x3_0_17 %314
               OpBranch %295
        %297 = OpLabel
               OpBranch %290
        %290 = OpLabel
        %315 = OpLoad %uint %mat2x3_0_16
        %316 = OpIAdd %uint %315 %int_1
               OpStore %mat2x3_0_16 %316
               OpBranch %287
        %289 = OpLabel
               OpBranch %282
        %282 = OpLabel
        %317 = OpLoad %uint %mat2x3_3_15
        %318 = OpIAdd %uint %317 %int_1
               OpStore %mat2x3_3_15 %318
               OpBranch %279
        %281 = OpLabel
               OpBranch %195
        %195 = OpLabel
        %319 = OpLoad %uint %S1_1_9
        %320 = OpIAdd %uint %319 %int_1
               OpStore %S1_1_9 %320
               OpBranch %192
        %194 = OpLabel
        %321 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %322 = OpLoad %uint %321
        %323 = OpIAdd %uint %322 %uint_2
        %324 = OpCopyObject %uint %323
        %325 = OpLoad %float %seed
        %326 = OpFAdd %float %325 %float_1
               OpStore %seed %326
        %327 = OpAccessChain %_ptr_Uniform_float %root %324 %int_2
               OpStore %327 %325
               OpStore %mat2x3_3_18 %uint_0
               OpBranch %329
        %329 = OpLabel
               OpLoopMerge %331 %332 None
               OpBranch %333
        %333 = OpLabel
        %334 = OpLoad %uint %mat2x3_3_18
        %335 = OpULessThan %bool %334 %uint_3
               OpBranchConditional %335 %330 %331
        %330 = OpLabel
               OpStore %mat2x3_0_19 %uint_0
               OpBranch %337
        %337 = OpLabel
               OpLoopMerge %339 %340 None
               OpBranch %341
        %341 = OpLabel
        %342 = OpLoad %uint %mat2x3_0_19
        %343 = OpULessThan %bool %342 %uint_2
               OpBranchConditional %343 %338 %339
        %338 = OpLabel
               OpStore %mat2x3_0_20 %uint_0
               OpBranch %345
        %345 = OpLabel
               OpLoopMerge %347 %348 None
               OpBranch %349
        %349 = OpLabel
        %350 = OpLoad %uint %mat2x3_0_20
        %351 = OpULessThan %bool %350 %uint_3
               OpBranchConditional %351 %346 %347
        %346 = OpLabel
        %352 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %353 = OpLoad %uint %352
        %354 = OpIAdd %uint %353 %uint_2
        %355 = OpCopyObject %uint %354
        %356 = OpLoad %uint %mat2x3_3_18
        %357 = OpLoad %uint %mat2x3_0_19
        %358 = OpLoad %uint %mat2x3_0_20
        %359 = OpLoad %float %seed
        %360 = OpFAdd %float %359 %float_1
               OpStore %seed %360
        %361 = OpAccessChain %_ptr_Uniform_float %root %355 %int_3 %356 %357 %358
               OpStore %361 %359
               OpBranch %348
        %348 = OpLabel
        %362 = OpLoad %uint %mat2x3_0_20
        %363 = OpIAdd %uint %362 %int_1
               OpStore %mat2x3_0_20 %363
               OpBranch %345
        %347 = OpLabel
               OpBranch %340
        %340 = OpLabel
        %364 = OpLoad %uint %mat2x3_0_19
        %365 = OpIAdd %uint %364 %int_1
               OpStore %mat2x3_0_19 %365
               OpBranch %337
        %339 = OpLabel
               OpBranch %332
        %332 = OpLabel
        %366 = OpLoad %uint %mat2x3_3_18
        %367 = OpIAdd %uint %366 %int_1
               OpStore %mat2x3_3_18 %367
               OpBranch %329
        %331 = OpLabel
               OpStore %vec3_4_21 %uint_0
               OpBranch %369
        %369 = OpLabel
               OpLoopMerge %371 %372 None
               OpBranch %373
        %373 = OpLabel
        %374 = OpLoad %uint %vec3_4_21
        %375 = OpULessThan %bool %374 %uint_2
               OpBranchConditional %375 %370 %371
        %370 = OpLabel
               OpStore %vec3_0_22 %uint_0
               OpBranch %377
        %377 = OpLabel
               OpLoopMerge %379 %380 None
               OpBranch %381
        %381 = OpLabel
        %382 = OpLoad %uint %vec3_0_22
        %383 = OpULessThan %bool %382 %uint_3
               OpBranchConditional %383 %378 %379
        %378 = OpLabel
        %384 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %385 = OpLoad %uint %384
        %386 = OpIAdd %uint %385 %uint_2
        %387 = OpCopyObject %uint %386
        %389 = OpLoad %uint %vec3_4_21
        %390 = OpLoad %uint %vec3_0_22
        %391 = OpLoad %float %seed
        %392 = OpFAdd %float %391 %float_1
               OpStore %seed %392
        %393 = OpAccessChain %_ptr_Uniform_float %root %387 %int_4 %389 %390
               OpStore %393 %391
               OpBranch %380
        %380 = OpLabel
        %394 = OpLoad %uint %vec3_0_22
        %395 = OpIAdd %uint %394 %int_1
               OpStore %vec3_0_22 %395
               OpBranch %377
        %379 = OpLabel
               OpBranch %372
        %372 = OpLabel
        %396 = OpLoad %uint %vec3_4_21
        %397 = OpIAdd %uint %396 %int_1
               OpStore %vec3_4_21 %397
               OpBranch %369
        %371 = OpLabel
               OpStore %vec3_5_23 %uint_0
               OpBranch %399
        %399 = OpLabel
               OpLoopMerge %401 %402 None
               OpBranch %403
        %403 = OpLabel
        %404 = OpLoad %uint %vec3_5_23
        %405 = OpULessThan %bool %404 %uint_3
               OpBranchConditional %405 %400 %401
        %400 = OpLabel
        %406 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %407 = OpLoad %uint %406
        %408 = OpIAdd %uint %407 %uint_2
        %409 = OpCopyObject %uint %408
        %411 = OpLoad %uint %vec3_5_23
        %412 = OpLoad %float %seed
        %413 = OpFAdd %float %412 %float_1
               OpStore %seed %413
        %414 = OpAccessChain %_ptr_Uniform_float %root %409 %int_5 %411
               OpStore %414 %412
               OpBranch %402
        %402 = OpLabel
        %415 = OpLoad %uint %vec3_5_23
        %416 = OpIAdd %uint %415 %int_1
               OpStore %vec3_5_23 %416
               OpBranch %399
        %401 = OpLabel
               OpStore %float_6_24 %uint_0
               OpBranch %418
        %418 = OpLabel
               OpLoopMerge %420 %421 None
               OpBranch %422
        %422 = OpLabel
        %423 = OpLoad %uint %float_6_24
        %424 = OpULessThan %bool %423 %uint_2
               OpBranchConditional %424 %419 %420
        %419 = OpLabel
        %425 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %426 = OpLoad %uint %425
        %427 = OpIAdd %uint %426 %uint_2
        %428 = OpCopyObject %uint %427
        %430 = OpLoad %uint %float_6_24
        %431 = OpLoad %float %seed
        %432 = OpFAdd %float %431 %float_1
               OpStore %seed %432
        %433 = OpAccessChain %_ptr_Uniform_float %root %428 %int_6 %430
               OpStore %433 %431
               OpBranch %421
        %421 = OpLabel
        %434 = OpLoad %uint %float_6_24
        %435 = OpIAdd %uint %434 %int_1
               OpStore %float_6_24 %435
               OpBranch %418
        %420 = OpLabel
               OpStore %vec3_0_25 %uint_0
               OpBranch %437
        %437 = OpLabel
               OpLoopMerge %439 %440 None
               OpBranch %441
        %441 = OpLabel
        %442 = OpLoad %uint %vec3_0_25
        %443 = OpULessThan %bool %442 %uint_3
               OpBranchConditional %443 %438 %439
        %438 = OpLabel
        %444 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %445 = OpLoad %uint %444
        %446 = OpIAdd %uint %445 %uint_2
        %447 = OpCopyObject %uint %446
        %449 = OpLoad %uint %vec3_0_25
        %450 = OpLoad %float %seed
        %451 = OpFAdd %float %450 %float_1
               OpStore %seed %451
        %452 = OpAccessChain %_ptr_Uniform_float %root %447 %int_7 %int_0 %449
               OpStore %452 %450
               OpBranch %440
        %440 = OpLabel
        %453 = OpLoad %uint %vec3_0_25
        %454 = OpIAdd %uint %453 %int_1
               OpStore %vec3_0_25 %454
               OpBranch %437
        %439 = OpLabel
               OpStore %mat2x3_1_26 %uint_0
               OpBranch %456
        %456 = OpLabel
               OpLoopMerge %458 %459 None
               OpBranch %460
        %460 = OpLabel
        %461 = OpLoad %uint %mat2x3_1_26
        %462 = OpULessThan %bool %461 %uint_2
               OpBranchConditional %462 %457 %458
        %457 = OpLabel
               OpStore %mat2x3_1_27 %uint_0
               OpBranch %464
        %464 = OpLabel
               OpLoopMerge %466 %467 None
               OpBranch %468
        %468 = OpLabel
        %469 = OpLoad %uint %mat2x3_1_27
        %470 = OpULessThan %bool %469 %uint_3
               OpBranchConditional %470 %465 %466
        %465 = OpLabel
        %471 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %472 = OpLoad %uint %471
        %473 = OpIAdd %uint %472 %uint_2
        %474 = OpCopyObject %uint %473
        %475 = OpLoad %uint %mat2x3_1_26
        %476 = OpLoad %uint %mat2x3_1_27
        %477 = OpLoad %float %seed
        %478 = OpFAdd %float %477 %float_1
               OpStore %seed %478
        %479 = OpAccessChain %_ptr_Uniform_float %root %474 %int_7 %int_1 %475 %476
               OpStore %479 %477
               OpBranch %467
        %467 = OpLabel
        %480 = OpLoad %uint %mat2x3_1_27
        %481 = OpIAdd %uint %480 %int_1
               OpStore %mat2x3_1_27 %481
               OpBranch %464
        %466 = OpLabel
               OpBranch %459
        %459 = OpLabel
        %482 = OpLoad %uint %mat2x3_1_26
        %483 = OpIAdd %uint %482 %int_1
               OpStore %mat2x3_1_26 %483
               OpBranch %456
        %458 = OpLabel
               OpStore %vec3_2_28 %uint_0
               OpBranch %485
        %485 = OpLabel
               OpLoopMerge %487 %488 None
               OpBranch %489
        %489 = OpLabel
        %490 = OpLoad %uint %vec3_2_28
        %491 = OpULessThan %bool %490 %uint_2
               OpBranchConditional %491 %486 %487
        %486 = OpLabel
               OpStore %vec3_0_29 %uint_0
               OpBranch %493
        %493 = OpLabel
               OpLoopMerge %495 %496 None
               OpBranch %497
        %497 = OpLabel
        %498 = OpLoad %uint %vec3_0_29
        %499 = OpULessThan %bool %498 %uint_3
               OpBranchConditional %499 %494 %495
        %494 = OpLabel
        %500 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %501 = OpLoad %uint %500
        %502 = OpIAdd %uint %501 %uint_2
        %503 = OpCopyObject %uint %502
        %504 = OpLoad %uint %vec3_2_28
        %505 = OpLoad %uint %vec3_0_29
        %506 = OpLoad %float %seed
        %507 = OpFAdd %float %506 %float_1
               OpStore %seed %507
        %508 = OpAccessChain %_ptr_Uniform_float %root %503 %int_7 %int_2 %504 %505
               OpStore %508 %506
               OpBranch %496
        %496 = OpLabel
        %509 = OpLoad %uint %vec3_0_29
        %510 = OpIAdd %uint %509 %int_1
               OpStore %vec3_0_29 %510
               OpBranch %493
        %495 = OpLabel
               OpBranch %488
        %488 = OpLabel
        %511 = OpLoad %uint %vec3_2_28
        %512 = OpIAdd %uint %511 %int_1
               OpStore %vec3_2_28 %512
               OpBranch %485
        %487 = OpLabel
               OpStore %mat2x3_3_30 %uint_0
               OpBranch %514
        %514 = OpLabel
               OpLoopMerge %516 %517 None
               OpBranch %518
        %518 = OpLabel
        %519 = OpLoad %uint %mat2x3_3_30
        %520 = OpULessThan %bool %519 %uint_3
               OpBranchConditional %520 %515 %516
        %515 = OpLabel
               OpStore %mat2x3_0_31 %uint_0
               OpBranch %522
        %522 = OpLabel
               OpLoopMerge %524 %525 None
               OpBranch %526
        %526 = OpLabel
        %527 = OpLoad %uint %mat2x3_0_31
        %528 = OpULessThan %bool %527 %uint_2
               OpBranchConditional %528 %523 %524
        %523 = OpLabel
               OpStore %mat2x3_0_32 %uint_0
               OpBranch %530
        %530 = OpLabel
               OpLoopMerge %532 %533 None
               OpBranch %534
        %534 = OpLabel
        %535 = OpLoad %uint %mat2x3_0_32
        %536 = OpULessThan %bool %535 %uint_3
               OpBranchConditional %536 %531 %532
        %531 = OpLabel
        %537 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %538 = OpLoad %uint %537
        %539 = OpIAdd %uint %538 %uint_2
        %540 = OpCopyObject %uint %539
        %541 = OpLoad %uint %mat2x3_3_30
        %542 = OpLoad %uint %mat2x3_0_31
        %543 = OpLoad %uint %mat2x3_0_32
        %544 = OpLoad %float %seed
        %545 = OpFAdd %float %544 %float_1
               OpStore %seed %545
        %546 = OpAccessChain %_ptr_Uniform_float %root %540 %int_7 %int_3 %541 %542 %543
               OpStore %546 %544
               OpBranch %533
        %533 = OpLabel
        %547 = OpLoad %uint %mat2x3_0_32
        %548 = OpIAdd %uint %547 %int_1
               OpStore %mat2x3_0_32 %548
               OpBranch %530
        %532 = OpLabel
               OpBranch %525
        %525 = OpLabel
        %549 = OpLoad %uint %mat2x3_0_31
        %550 = OpIAdd %uint %549 %int_1
               OpStore %mat2x3_0_31 %550
               OpBranch %522
        %524 = OpLabel
               OpBranch %517
        %517 = OpLabel
        %551 = OpLoad %uint %mat2x3_3_30
        %552 = OpIAdd %uint %551 %int_1
               OpStore %mat2x3_3_30 %552
               OpBranch %514
        %516 = OpLabel
               OpStore %S0_8_33 %uint_0
               OpBranch %554
        %554 = OpLabel
               OpLoopMerge %556 %557 None
               OpBranch %558
        %558 = OpLabel
        %559 = OpLoad %uint %S0_8_33
        %560 = OpULessThan %bool %559 %uint_1
               OpBranchConditional %560 %555 %556
        %555 = OpLabel
               OpStore %vec3_0_34 %uint_0
               OpBranch %562
        %562 = OpLabel
               OpLoopMerge %564 %565 None
               OpBranch %566
        %566 = OpLabel
        %567 = OpLoad %uint %vec3_0_34
        %568 = OpULessThan %bool %567 %uint_3
               OpBranchConditional %568 %563 %564
        %563 = OpLabel
        %569 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %570 = OpLoad %uint %569
        %571 = OpIAdd %uint %570 %uint_2
        %572 = OpCopyObject %uint %571
        %574 = OpLoad %uint %S0_8_33
        %575 = OpLoad %uint %vec3_0_34
        %576 = OpLoad %float %seed
        %577 = OpFAdd %float %576 %float_1
               OpStore %seed %577
        %578 = OpAccessChain %_ptr_Uniform_float %root %572 %int_8 %574 %int_0 %575
               OpStore %578 %576
               OpBranch %565
        %565 = OpLabel
        %579 = OpLoad %uint %vec3_0_34
        %580 = OpIAdd %uint %579 %int_1
               OpStore %vec3_0_34 %580
               OpBranch %562
        %564 = OpLabel
               OpStore %mat2x3_1_35 %uint_0
               OpBranch %582
        %582 = OpLabel
               OpLoopMerge %584 %585 None
               OpBranch %586
        %586 = OpLabel
        %587 = OpLoad %uint %mat2x3_1_35
        %588 = OpULessThan %bool %587 %uint_2
               OpBranchConditional %588 %583 %584
        %583 = OpLabel
               OpStore %mat2x3_1_36 %uint_0
               OpBranch %590
        %590 = OpLabel
               OpLoopMerge %592 %593 None
               OpBranch %594
        %594 = OpLabel
        %595 = OpLoad %uint %mat2x3_1_36
        %596 = OpULessThan %bool %595 %uint_3
               OpBranchConditional %596 %591 %592
        %591 = OpLabel
        %597 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %598 = OpLoad %uint %597
        %599 = OpIAdd %uint %598 %uint_2
        %600 = OpCopyObject %uint %599
        %601 = OpLoad %uint %S0_8_33
        %602 = OpLoad %uint %mat2x3_1_35
        %603 = OpLoad %uint %mat2x3_1_36
        %604 = OpLoad %float %seed
        %605 = OpFAdd %float %604 %float_1
               OpStore %seed %605
        %606 = OpAccessChain %_ptr_Uniform_float %root %600 %int_8 %601 %int_1 %602 %603
               OpStore %606 %604
               OpBranch %593
        %593 = OpLabel
        %607 = OpLoad %uint %mat2x3_1_36
        %608 = OpIAdd %uint %607 %int_1
               OpStore %mat2x3_1_36 %608
               OpBranch %590
        %592 = OpLabel
               OpBranch %585
        %585 = OpLabel
        %609 = OpLoad %uint %mat2x3_1_35
        %610 = OpIAdd %uint %609 %int_1
               OpStore %mat2x3_1_35 %610
               OpBranch %582
        %584 = OpLabel
               OpStore %vec3_2_37 %uint_0
               OpBranch %612
        %612 = OpLabel
               OpLoopMerge %614 %615 None
               OpBranch %616
        %616 = OpLabel
        %617 = OpLoad %uint %vec3_2_37
        %618 = OpULessThan %bool %617 %uint_2
               OpBranchConditional %618 %613 %614
        %613 = OpLabel
               OpStore %vec3_0_38 %uint_0
               OpBranch %620
        %620 = OpLabel
               OpLoopMerge %622 %623 None
               OpBranch %624
        %624 = OpLabel
        %625 = OpLoad %uint %vec3_0_38
        %626 = OpULessThan %bool %625 %uint_3
               OpBranchConditional %626 %621 %622
        %621 = OpLabel
        %627 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %628 = OpLoad %uint %627
        %629 = OpIAdd %uint %628 %uint_2
        %630 = OpCopyObject %uint %629
        %631 = OpLoad %uint %S0_8_33
        %632 = OpLoad %uint %vec3_2_37
        %633 = OpLoad %uint %vec3_0_38
        %634 = OpLoad %float %seed
        %635 = OpFAdd %float %634 %float_1
               OpStore %seed %635
        %636 = OpAccessChain %_ptr_Uniform_float %root %630 %int_8 %631 %int_2 %632 %633
               OpStore %636 %634
               OpBranch %623
        %623 = OpLabel
        %637 = OpLoad %uint %vec3_0_38
        %638 = OpIAdd %uint %637 %int_1
               OpStore %vec3_0_38 %638
               OpBranch %620
        %622 = OpLabel
               OpBranch %615
        %615 = OpLabel
        %639 = OpLoad %uint %vec3_2_37
        %640 = OpIAdd %uint %639 %int_1
               OpStore %vec3_2_37 %640
               OpBranch %612
        %614 = OpLabel
               OpStore %mat2x3_3_39 %uint_0
               OpBranch %642
        %642 = OpLabel
               OpLoopMerge %644 %645 None
               OpBranch %646
        %646 = OpLabel
        %647 = OpLoad %uint %mat2x3_3_39
        %648 = OpULessThan %bool %647 %uint_3
               OpBranchConditional %648 %643 %644
        %643 = OpLabel
               OpStore %mat2x3_0_40 %uint_0
               OpBranch %650
        %650 = OpLabel
               OpLoopMerge %652 %653 None
               OpBranch %654
        %654 = OpLabel
        %655 = OpLoad %uint %mat2x3_0_40
        %656 = OpULessThan %bool %655 %uint_2
               OpBranchConditional %656 %651 %652
        %651 = OpLabel
               OpStore %mat2x3_0_41 %uint_0
               OpBranch %658
        %658 = OpLabel
               OpLoopMerge %660 %661 None
               OpBranch %662
        %662 = OpLabel
        %663 = OpLoad %uint %mat2x3_0_41
        %664 = OpULessThan %bool %663 %uint_3
               OpBranchConditional %664 %659 %660
        %659 = OpLabel
        %665 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %666 = OpLoad %uint %665
        %667 = OpIAdd %uint %666 %uint_2
        %668 = OpCopyObject %uint %667
        %669 = OpLoad %uint %S0_8_33
        %670 = OpLoad %uint %mat2x3_3_39
        %671 = OpLoad %uint %mat2x3_0_40
        %672 = OpLoad %uint %mat2x3_0_41
        %673 = OpLoad %float %seed
        %674 = OpFAdd %float %673 %float_1
               OpStore %seed %674
        %675 = OpAccessChain %_ptr_Uniform_float %root %668 %int_8 %669 %int_3 %670 %671 %672
               OpStore %675 %673
               OpBranch %661
        %661 = OpLabel
        %676 = OpLoad %uint %mat2x3_0_41
        %677 = OpIAdd %uint %676 %int_1
               OpStore %mat2x3_0_41 %677
               OpBranch %658
        %660 = OpLabel
               OpBranch %653
        %653 = OpLabel
        %678 = OpLoad %uint %mat2x3_0_40
        %679 = OpIAdd %uint %678 %int_1
               OpStore %mat2x3_0_40 %679
               OpBranch %650
        %652 = OpLabel
               OpBranch %645
        %645 = OpLabel
        %680 = OpLoad %uint %mat2x3_3_39
        %681 = OpIAdd %uint %680 %int_1
               OpStore %mat2x3_3_39 %681
               OpBranch %642
        %644 = OpLabel
               OpBranch %557
        %557 = OpLabel
        %682 = OpLoad %uint %S0_8_33
        %683 = OpIAdd %uint %682 %int_1
               OpStore %S0_8_33 %683
               OpBranch %554
        %556 = OpLabel
               OpStore %vec3_0_42 %uint_0
               OpBranch %685
        %685 = OpLabel
               OpLoopMerge %687 %688 None
               OpBranch %689
        %689 = OpLabel
        %690 = OpLoad %uint %vec3_0_42
        %691 = OpULessThan %bool %690 %uint_3
               OpBranchConditional %691 %686 %687
        %686 = OpLabel
        %692 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %693 = OpLoad %uint %692
        %694 = OpIAdd %uint %693 %uint_2
        %695 = OpCopyObject %uint %694
        %697 = OpLoad %uint %vec3_0_42
        %698 = OpLoad %float %seed
        %699 = OpFAdd %float %698 %float_1
               OpStore %seed %699
        %700 = OpAccessChain %_ptr_Uniform_float %root %695 %int_9 %int_0 %697
               OpStore %700 %698
               OpBranch %688
        %688 = OpLabel
        %701 = OpLoad %uint %vec3_0_42
        %702 = OpIAdd %uint %701 %int_1
               OpStore %vec3_0_42 %702
               OpBranch %685
        %687 = OpLabel
               OpStore %mat2x3_1_43 %uint_0
               OpBranch %704
        %704 = OpLabel
               OpLoopMerge %706 %707 None
               OpBranch %708
        %708 = OpLabel
        %709 = OpLoad %uint %mat2x3_1_43
        %710 = OpULessThan %bool %709 %uint_2
               OpBranchConditional %710 %705 %706
        %705 = OpLabel
               OpStore %mat2x3_1_44 %uint_0
               OpBranch %712
        %712 = OpLabel
               OpLoopMerge %714 %715 None
               OpBranch %716
        %716 = OpLabel
        %717 = OpLoad %uint %mat2x3_1_44
        %718 = OpULessThan %bool %717 %uint_3
               OpBranchConditional %718 %713 %714
        %713 = OpLabel
        %719 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %720 = OpLoad %uint %719
        %721 = OpIAdd %uint %720 %uint_2
        %722 = OpCopyObject %uint %721
        %723 = OpLoad %uint %mat2x3_1_43
        %724 = OpLoad %uint %mat2x3_1_44
        %725 = OpLoad %float %seed
        %726 = OpFAdd %float %725 %float_1
               OpStore %seed %726
        %727 = OpAccessChain %_ptr_Uniform_float %root %722 %int_9 %int_1 %723 %724
               OpStore %727 %725
               OpBranch %715
        %715 = OpLabel
        %728 = OpLoad %uint %mat2x3_1_44
        %729 = OpIAdd %uint %728 %int_1
               OpStore %mat2x3_1_44 %729
               OpBranch %712
        %714 = OpLabel
               OpBranch %707
        %707 = OpLabel
        %730 = OpLoad %uint %mat2x3_1_43
        %731 = OpIAdd %uint %730 %int_1
               OpStore %mat2x3_1_43 %731
               OpBranch %704
        %706 = OpLabel
               OpStore %vec3_2_45 %uint_0
               OpBranch %733
        %733 = OpLabel
               OpLoopMerge %735 %736 None
               OpBranch %737
        %737 = OpLabel
        %738 = OpLoad %uint %vec3_2_45
        %739 = OpULessThan %bool %738 %uint_2
               OpBranchConditional %739 %734 %735
        %734 = OpLabel
               OpStore %vec3_0_46 %uint_0
               OpBranch %741
        %741 = OpLabel
               OpLoopMerge %743 %744 None
               OpBranch %745
        %745 = OpLabel
        %746 = OpLoad %uint %vec3_0_46
        %747 = OpULessThan %bool %746 %uint_3
               OpBranchConditional %747 %742 %743
        %742 = OpLabel
        %748 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %749 = OpLoad %uint %748
        %750 = OpIAdd %uint %749 %uint_2
        %751 = OpCopyObject %uint %750
        %752 = OpLoad %uint %vec3_2_45
        %753 = OpLoad %uint %vec3_0_46
        %754 = OpLoad %float %seed
        %755 = OpFAdd %float %754 %float_1
               OpStore %seed %755
        %756 = OpAccessChain %_ptr_Uniform_float %root %751 %int_9 %int_2 %752 %753
               OpStore %756 %754
               OpBranch %744
        %744 = OpLabel
        %757 = OpLoad %uint %vec3_0_46
        %758 = OpIAdd %uint %757 %int_1
               OpStore %vec3_0_46 %758
               OpBranch %741
        %743 = OpLabel
               OpBranch %736
        %736 = OpLabel
        %759 = OpLoad %uint %vec3_2_45
        %760 = OpIAdd %uint %759 %int_1
               OpStore %vec3_2_45 %760
               OpBranch %733
        %735 = OpLabel
               OpStore %mat2x3_3_47 %uint_0
               OpBranch %762
        %762 = OpLabel
               OpLoopMerge %764 %765 None
               OpBranch %766
        %766 = OpLabel
        %767 = OpLoad %uint %mat2x3_3_47
        %768 = OpULessThan %bool %767 %uint_3
               OpBranchConditional %768 %763 %764
        %763 = OpLabel
               OpStore %mat2x3_0_48 %uint_0
               OpBranch %770
        %770 = OpLabel
               OpLoopMerge %772 %773 None
               OpBranch %774
        %774 = OpLabel
        %775 = OpLoad %uint %mat2x3_0_48
        %776 = OpULessThan %bool %775 %uint_2
               OpBranchConditional %776 %771 %772
        %771 = OpLabel
               OpStore %mat2x3_0_49 %uint_0
               OpBranch %778
        %778 = OpLabel
               OpLoopMerge %780 %781 None
               OpBranch %782
        %782 = OpLabel
        %783 = OpLoad %uint %mat2x3_0_49
        %784 = OpULessThan %bool %783 %uint_3
               OpBranchConditional %784 %779 %780
        %779 = OpLabel
        %785 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %786 = OpLoad %uint %785
        %787 = OpIAdd %uint %786 %uint_2
        %788 = OpCopyObject %uint %787
        %789 = OpLoad %uint %mat2x3_3_47
        %790 = OpLoad %uint %mat2x3_0_48
        %791 = OpLoad %uint %mat2x3_0_49
        %792 = OpLoad %float %seed
        %793 = OpFAdd %float %792 %float_1
               OpStore %seed %793
        %794 = OpAccessChain %_ptr_Uniform_float %root %788 %int_9 %int_3 %789 %790 %791
               OpStore %794 %792
               OpBranch %781
        %781 = OpLabel
        %795 = OpLoad %uint %mat2x3_0_49
        %796 = OpIAdd %uint %795 %int_1
               OpStore %mat2x3_0_49 %796
               OpBranch %778
        %780 = OpLabel
               OpBranch %773
        %773 = OpLabel
        %797 = OpLoad %uint %mat2x3_0_48
        %798 = OpIAdd %uint %797 %int_1
               OpStore %mat2x3_0_48 %798
               OpBranch %770
        %772 = OpLabel
               OpBranch %765
        %765 = OpLabel
        %799 = OpLoad %uint %mat2x3_3_47
        %800 = OpIAdd %uint %799 %int_1
               OpStore %mat2x3_3_47 %800
               OpBranch %762
        %764 = OpLabel
               OpStore %mat2x3_10_50 %uint_0
               OpBranch %802
        %802 = OpLabel
               OpLoopMerge %804 %805 None
               OpBranch %806
        %806 = OpLabel
        %807 = OpLoad %uint %mat2x3_10_50
        %808 = OpULessThan %bool %807 %uint_2
               OpBranchConditional %808 %803 %804
        %803 = OpLabel
               OpStore %mat2x3_10_51 %uint_0
               OpBranch %810
        %810 = OpLabel
               OpLoopMerge %812 %813 None
               OpBranch %814
        %814 = OpLabel
        %815 = OpLoad %uint %mat2x3_10_51
        %816 = OpULessThan %bool %815 %uint_3
               OpBranchConditional %816 %811 %812
        %811 = OpLabel
        %817 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %818 = OpLoad %uint %817
        %819 = OpIAdd %uint %818 %uint_2
        %820 = OpCopyObject %uint %819
        %822 = OpLoad %uint %mat2x3_10_50
        %823 = OpLoad %uint %mat2x3_10_51
        %824 = OpLoad %float %seed
        %825 = OpFAdd %float %824 %float_1
               OpStore %seed %825
        %826 = OpAccessChain %_ptr_Uniform_float %root %820 %int_10 %822 %823
               OpStore %826 %824
               OpBranch %813
        %813 = OpLabel
        %827 = OpLoad %uint %mat2x3_10_51
        %828 = OpIAdd %uint %827 %int_1
               OpStore %mat2x3_10_51 %828
               OpBranch %810
        %812 = OpLabel
               OpBranch %805
        %805 = OpLabel
        %829 = OpLoad %uint %mat2x3_10_50
        %830 = OpIAdd %uint %829 %int_1
               OpStore %mat2x3_10_50 %830
               OpBranch %802
        %804 = OpLabel
               OpStore %S0_11_52 %uint_0
               OpBranch %832
        %832 = OpLabel
               OpLoopMerge %834 %835 None
               OpBranch %836
        %836 = OpLabel
        %837 = OpLoad %uint %S0_11_52
        %838 = OpULessThan %bool %837 %uint_3
               OpBranchConditional %838 %833 %834
        %833 = OpLabel
               OpStore %vec3_0_53 %uint_0
               OpBranch %840
        %840 = OpLabel
               OpLoopMerge %842 %843 None
               OpBranch %844
        %844 = OpLabel
        %845 = OpLoad %uint %vec3_0_53
        %846 = OpULessThan %bool %845 %uint_3
               OpBranchConditional %846 %841 %842
        %841 = OpLabel
        %847 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %848 = OpLoad %uint %847
        %849 = OpIAdd %uint %848 %uint_2
        %850 = OpCopyObject %uint %849
        %852 = OpLoad %uint %S0_11_52
        %853 = OpLoad %uint %vec3_0_53
        %854 = OpLoad %float %seed
        %855 = OpFAdd %float %854 %float_1
               OpStore %seed %855
        %856 = OpAccessChain %_ptr_Uniform_float %root %850 %int_11 %852 %int_0 %853
               OpStore %856 %854
               OpBranch %843
        %843 = OpLabel
        %857 = OpLoad %uint %vec3_0_53
        %858 = OpIAdd %uint %857 %int_1
               OpStore %vec3_0_53 %858
               OpBranch %840
        %842 = OpLabel
               OpStore %mat2x3_1_54 %uint_0
               OpBranch %860
        %860 = OpLabel
               OpLoopMerge %862 %863 None
               OpBranch %864
        %864 = OpLabel
        %865 = OpLoad %uint %mat2x3_1_54
        %866 = OpULessThan %bool %865 %uint_2
               OpBranchConditional %866 %861 %862
        %861 = OpLabel
               OpStore %mat2x3_1_55 %uint_0
               OpBranch %868
        %868 = OpLabel
               OpLoopMerge %870 %871 None
               OpBranch %872
        %872 = OpLabel
        %873 = OpLoad %uint %mat2x3_1_55
        %874 = OpULessThan %bool %873 %uint_3
               OpBranchConditional %874 %869 %870
        %869 = OpLabel
        %875 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %876 = OpLoad %uint %875
        %877 = OpIAdd %uint %876 %uint_2
        %878 = OpCopyObject %uint %877
        %879 = OpLoad %uint %S0_11_52
        %880 = OpLoad %uint %mat2x3_1_54
        %881 = OpLoad %uint %mat2x3_1_55
        %882 = OpLoad %float %seed
        %883 = OpFAdd %float %882 %float_1
               OpStore %seed %883
        %884 = OpAccessChain %_ptr_Uniform_float %root %878 %int_11 %879 %int_1 %880 %881
               OpStore %884 %882
               OpBranch %871
        %871 = OpLabel
        %885 = OpLoad %uint %mat2x3_1_55
        %886 = OpIAdd %uint %885 %int_1
               OpStore %mat2x3_1_55 %886
               OpBranch %868
        %870 = OpLabel
               OpBranch %863
        %863 = OpLabel
        %887 = OpLoad %uint %mat2x3_1_54
        %888 = OpIAdd %uint %887 %int_1
               OpStore %mat2x3_1_54 %888
               OpBranch %860
        %862 = OpLabel
               OpStore %vec3_2_56 %uint_0
               OpBranch %890
        %890 = OpLabel
               OpLoopMerge %892 %893 None
               OpBranch %894
        %894 = OpLabel
        %895 = OpLoad %uint %vec3_2_56
        %896 = OpULessThan %bool %895 %uint_2
               OpBranchConditional %896 %891 %892
        %891 = OpLabel
               OpStore %vec3_0_57 %uint_0
               OpBranch %898
        %898 = OpLabel
               OpLoopMerge %900 %901 None
               OpBranch %902
        %902 = OpLabel
        %903 = OpLoad %uint %vec3_0_57
        %904 = OpULessThan %bool %903 %uint_3
               OpBranchConditional %904 %899 %900
        %899 = OpLabel
        %905 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %906 = OpLoad %uint %905
        %907 = OpIAdd %uint %906 %uint_2
        %908 = OpCopyObject %uint %907
        %909 = OpLoad %uint %S0_11_52
        %910 = OpLoad %uint %vec3_2_56
        %911 = OpLoad %uint %vec3_0_57
        %912 = OpLoad %float %seed
        %913 = OpFAdd %float %912 %float_1
               OpStore %seed %913
        %914 = OpAccessChain %_ptr_Uniform_float %root %908 %int_11 %909 %int_2 %910 %911
               OpStore %914 %912
               OpBranch %901
        %901 = OpLabel
        %915 = OpLoad %uint %vec3_0_57
        %916 = OpIAdd %uint %915 %int_1
               OpStore %vec3_0_57 %916
               OpBranch %898
        %900 = OpLabel
               OpBranch %893
        %893 = OpLabel
        %917 = OpLoad %uint %vec3_2_56
        %918 = OpIAdd %uint %917 %int_1
               OpStore %vec3_2_56 %918
               OpBranch %890
        %892 = OpLabel
               OpStore %mat2x3_3_58 %uint_0
               OpBranch %920
        %920 = OpLabel
               OpLoopMerge %922 %923 None
               OpBranch %924
        %924 = OpLabel
        %925 = OpLoad %uint %mat2x3_3_58
        %926 = OpULessThan %bool %925 %uint_3
               OpBranchConditional %926 %921 %922
        %921 = OpLabel
               OpStore %mat2x3_0_59 %uint_0
               OpBranch %928
        %928 = OpLabel
               OpLoopMerge %930 %931 None
               OpBranch %932
        %932 = OpLabel
        %933 = OpLoad %uint %mat2x3_0_59
        %934 = OpULessThan %bool %933 %uint_2
               OpBranchConditional %934 %929 %930
        %929 = OpLabel
               OpStore %mat2x3_0_60 %uint_0
               OpBranch %936
        %936 = OpLabel
               OpLoopMerge %938 %939 None
               OpBranch %940
        %940 = OpLabel
        %941 = OpLoad %uint %mat2x3_0_60
        %942 = OpULessThan %bool %941 %uint_3
               OpBranchConditional %942 %937 %938
        %937 = OpLabel
        %943 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
        %944 = OpLoad %uint %943
        %945 = OpIAdd %uint %944 %uint_2
        %946 = OpCopyObject %uint %945
        %947 = OpLoad %uint %S0_11_52
        %948 = OpLoad %uint %mat2x3_3_58
        %949 = OpLoad %uint %mat2x3_0_59
        %950 = OpLoad %uint %mat2x3_0_60
        %951 = OpLoad %float %seed
        %952 = OpFAdd %float %951 %float_1
               OpStore %seed %952
        %953 = OpAccessChain %_ptr_Uniform_float %root %946 %int_11 %947 %int_3 %948 %949 %950
               OpStore %953 %951
               OpBranch %939
        %939 = OpLabel
        %954 = OpLoad %uint %mat2x3_0_60
        %955 = OpIAdd %uint %954 %int_1
               OpStore %mat2x3_0_60 %955
               OpBranch %936
        %938 = OpLabel
               OpBranch %931
        %931 = OpLabel
        %956 = OpLoad %uint %mat2x3_0_59
        %957 = OpIAdd %uint %956 %int_1
               OpStore %mat2x3_0_59 %957
               OpBranch %928
        %930 = OpLabel
               OpBranch %923
        %923 = OpLabel
        %958 = OpLoad %uint %mat2x3_3_58
        %959 = OpIAdd %uint %958 %int_1
               OpStore %mat2x3_3_58 %959
               OpBranch %920
        %922 = OpLabel
               OpBranch %835
        %835 = OpLabel
        %960 = OpLoad %uint %S0_11_52
        %961 = OpIAdd %uint %960 %int_1
               OpStore %S0_11_52 %961
               OpBranch %832
        %834 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L887-L959) computes an aligned descriptor stride, allocates one host-visible coherent storage buffer, and makes one storage-buffer descriptor range for each guard or active element.
- The descriptor set layout has one storage-buffer array binding. The test writes every array element at binding 0, with each descriptor pointing at the next aligned range of the same buffer.
- The host fills the entire buffer with `1`, creates a compute pipeline from the generated shader, binds the descriptor set, pushes `seed` and `visits`, and dispatches `1 x 1 x 1` workgroups. The shader's local X size supplies the active invocation count.
- After `submitCommandsAndWait()`, [`verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) starts with an all-`1` expected buffer. It clones the generated structure for each active outer element, runs its host-side loop, serializes the expected result at the aligned offset, then compares the two leading ranges and all active ranges. Although the expected buffer also contains two trailing ranges, the comparison count excludes them.
- A mismatch logs its dword index and expected and observed hexadecimal values. The case passes only when all compared dwords match.

The test first requires Vulkan 1.2 `runtimeDescriptorArray` and `shaderStorageBufferArrayNonUniformIndexing`; devices without either feature skip the case before pipeline creation.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `4` | Layout or stride handling for a four-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |
| `8` | Layout or stride handling for an eight-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |
| `12` | Layout or stride handling for a twelve-element descriptor-indexed active range; descriptor-array indexing or guard-zone corruption. |

### Cause Analysis

#### Generated layout or stride handling

**Possible failure symptoms:** The dword comparison reports a mismatch in an active range. The reported offset may point to a member after a nested array or to data in a later descriptor range.

**Possible implementation causes:** A driver compiler, descriptor-range calculation, or storage-buffer access path may disagree with the generated `std430` member offsets or array strides. The host comparison derives expected bytes from the same generated structure model, so a mismatch identifies disagreement between that model and device-visible access rather than a tolerance issue.

#### Non-uniform descriptor-array indexing

**Possible failure symptoms:** One or more active ranges retain `1` values or contain data expected for another invocation, while other ranges match.

**Possible implementation causes:** The compute shader marks the invocation-derived descriptor index with `nonuniformEXT`, and the support gate requires `shaderStorageBufferArrayNonUniformIndexing`. A failure can indicate incorrect descriptor selection or access through that non-uniform index. Source-level investigation is needed to attribute a particular mismatch to compiler lowering, descriptor management, or another implementation layer.

#### Guard-zone corruption

**Possible failure symptoms:** The comparison reports a mismatch in a leading guard range, where the expected value remains `1`. Writes confined to the two trailing allocated ranges are not observed by this verifier.

**Possible implementation causes:** An out-of-range generated access, a wrong descriptor offset or range, or an incorrect active-index calculation can write a leading guard range. The test does not isolate which layer produced the write, so source-level investigation is needed after the logged dword offset identifies the affected range; corruption confined to trailing allocated ranges cannot cause this test to fail.

## Case Pruning

### Requirement-based pruning

Devices that lack either required Vulkan 1.2 descriptor-indexing feature skip the case.

### Design-based pruning

The test exposes one registered test case leaf, not a cross-product of user-selectable leaves. Its internally generated layouts use a deterministic seed, which can be overridden through the CTS base-seed command-line setting during `delayedInit()`.

## Key Takeaways

- The test checks generated nested SSBO layouts through a storage-buffer descriptor array, not a single contiguous shader declaration.
- Every local invocation selects an active descriptor range with a non-uniform index, then walks and writes its own generated `Root` element.
- Alignment affects descriptor range boundaries, while `std430` affects contents inside each range. Both must agree with the host model.
- The two leading guard ranges turn writes before the active outer array into observable dword mismatches; the two trailing allocated ranges are not validated.

## Source Reference Appendix

| Evidence | Source |
|---|---|
| Registration under the parent test family | [`createUnsizedArrayTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2202-L2231), [`appendNestedUnsizedArraysTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1155-L1158) |
| Generated structure shapes and size choices | [`NestedUnsizedArraysTestCase::generateStructure()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1027-L1104) |
| Required descriptor-indexing features | [`NestedUnsizedArraysTestCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1106-L1117) |
| Generated compute shader | [`NestedUnsizedArraysTestCase::initPrograms()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L1119-L1151) |
| Buffer, descriptors, dispatch, and result status | [`NestedUnsizedArraysTestInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L887-L959) |
| Expected-data construction and dword comparison | [`NestedUnsizedArraysTestInstance::verify()`](../../../modules/vulkan/ssbo/vktSSBOLayoutNestedUnsizedArraysTests.cpp#L961-L1011) |
| Shared SSBO layout support | [`vktSSBOLayoutCase.hpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.hpp#L38-L330), [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1644) |
| Vulkan and Vulkan SC mustpass entries | [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L12225), [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L12162) |
