## Overview

**Core question:** Do normal and NV generated-command compute dispatches report the required subgroup scalar and mask built-ins?

- This page covers the implementation behind the `dgc.nv.compute.subgroups` test family and its `builtins` test family.
- The generated compute shader checks four subgroup scalar built-ins and five subgroup mask built-ins for every invocation.
- The matrix runs the same checks through either a normal compute pipeline or an NV DGC compute pipeline, and can use the universal or compute queue.
- The registered matrix uses workgroup and subgroup sizes from `16`, `32`, `64`, and `128`; the page also explains which combinations the generator removes and why unsupported cases are skipped.

## Background Knowledge

- A compute workgroup is partitioned into subgroups. `gl_NumSubgroups`, `gl_SubgroupID`, `gl_SubgroupSize`, and `gl_SubgroupInvocationID` describe the partition and an invocation's position within it. The test requires a fixed subgroup size so it can compare those values with the selected parameters.
- A subgroup mask built-in is a `uvec4` bit mask. Bit `i` describes the invocation with subgroup-local ID `i`; bits beyond the subgroup size must be zero. The five relational mask built-ins distinguish invocations whose subgroup-local IDs are equal to, greater than or equal to, greater than, less than or equal to, or less than the current invocation's ID.

## Registration Hierarchy

```text
dgc.nv.compute.subgroups
└── builtins
```

The source registers one `builtins` test family. The implementation expands it into the exact test case leaves listed in the parameter section and in the `dgc.txt` mustpass file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `workgroupSize` | `16`, `32`, `64`, `128` | Sets the generated shader's `local_size_x` and total invocation count. | [`createDGCComputeSubgroupTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L366-L381) |
| `subgroupSize` | `16`, `32`, `64`, `128` | Sets the required subgroup size and the expected `gl_SubgroupSize`. | [`BuiltinParams` and generated shader](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L50-L61) |
| Pipeline selection | `_normal_pipeline`, `_dgc_pipeline` | Chooses a normal compute pipeline or an NV DGC compute pipeline. | [`verifyBuiltins` pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L233-L252) |
| Queue selection | no suffix, `_cq` | Chooses the universal queue or the compute queue. | [`verifyBuiltins` queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L173-L181) |

For every retained size pair, the registered test name has this exact form:

```text
workgroup_size_<workgroupSize>_subgroup_size_<subgroupSize>_<dgc_pipeline|normal_pipeline><_cq when computeQueue is true>
```

The current NV entries in `external/vulkancts/mustpass/main/vk-default/dgc.txt` are:

```text
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_128_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_128_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_128_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_128_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_16_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_16_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_16_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_16_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_32_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_32_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_32_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_32_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_64_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_64_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_64_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_128_subgroup_size_64_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_16_subgroup_size_16_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_16_subgroup_size_16_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_16_subgroup_size_16_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_16_subgroup_size_16_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_16_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_16_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_16_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_16_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_32_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_32_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_32_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_32_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_16_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_16_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_16_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_16_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_32_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_32_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_32_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_32_normal_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_64_dgc_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_64_dgc_pipeline_cq
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_64_normal_pipeline
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_64_subgroup_size_64_normal_pipeline_cq
```

## Behavior Parameters

The primary behavioral axis is `subgroupSize`. It changes the required subgroup partition and the expected subgroup built-in values; pipeline and queue selection exercise the same checks through different execution paths.

### `16` subgroup size

The shader requires `gl_SubgroupSize == 16`, expects `workgroupSize / 16` subgroups, and checks all five masks across 16 valid bits.

### `32` subgroup size

The shader requires `gl_SubgroupSize == 32`, expects `workgroupSize / 32` subgroups, and checks all five masks across 32 valid bits.

### `64` subgroup size

The shader requires `gl_SubgroupSize == 64`, expects `workgroupSize / 64` subgroups, and checks all five masks across 64 valid bits.

### `128` subgroup size

The shader requires `gl_SubgroupSize == 128`, expects `workgroupSize / 128` subgroups, and checks all five masks across 128 valid bits.

## Shader Analysis

The test generates one compute shader for each case. It enables `GL_KHR_shader_subgroup_basic` and `GL_KHR_shader_subgroup_ballot`, declares `local_size_x = totalInvocations`, and writes nine verification arrays. The shader uses `gl_SubgroupInvocationID + gl_SubgroupID * gl_SubgroupSize` as the output index, which gives each invocation a distinct position in the workgroup-sized arrays.

The scalar checks compare `gl_NumSubgroups`, `gl_SubgroupID`, `gl_SubgroupSize`, and `gl_SubgroupInvocationID` with the expected relationships. The mask helper inspects all four 32-bit components, treats only the first `gl_SubgroupSize` bits as valid, and requires unused bits to be zero. The five mask-built-in checks expect the current bit pattern for equality, greater-than-or-equal, greater-than, less-than-or-equal, and less-than comparisons.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.compute.subgroups.builtins.workgroup_size_32_subgroup_size_16_normal_pipeline
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `workgroup_size_32` | The generated shader launches 32 invocations. |
| `subgroup_size_16` | The pipeline requires 16-wide subgroups, so the workgroup contains two subgroups. |
| `normal_pipeline` | The dispatch uses a normal compute pipeline rather than a pipeline token in the generated stream. |

#### Purpose

This case checks the same built-ins and ballot masks as every other retained matrix entry. The selected values make the subgroup partition easy to inspect: two 16-invocation subgroups cover the 32 output positions.

#### Structural Design

- The shader computes an output index from `gl_SubgroupID`, `gl_SubgroupSize`, and `gl_SubgroupInvocationID`.
- Four scalar checks validate the subgroup count, subgroup ID, subgroup size, and subgroup-local invocation ID.
- Five mask checks validate the equality and ordered ballot masks.
- Each check writes `1` for success and `0` for failure to its own storage buffer.

#### Shader Code

```glsl
#version 460
#extension GL_KHR_shader_subgroup_basic : require
#extension GL_KHR_shader_subgroup_ballot : require
layout(local_size_x = 32, local_size_y = 1, local_size_z = 1) in;
layout(set = 0, binding = 0) buffer NumSubgroupsBlock { uint verification[]; } numSubgroupsBuffer;
layout(set = 0, binding = 1) buffer SubgroupIdBlock { uint verification[]; } subgroupIdBuffer;
layout(set = 0, binding = 2) buffer SubgroupSizeBlock { uint verification[]; } subgroupSizeBuffer;
layout(set = 0, binding = 3) buffer InvocationIdBlock { uint verification[]; } invocationIdBuffer;
layout(set = 0, binding = 4) buffer EqMaskBlock { uint verification[]; } eqMaskBuffer;
layout(set = 0, binding = 5) buffer GeMaskBlock { uint verification[]; } geMaskBuffer;
layout(set = 0, binding = 6) buffer GtMaskBlock { uint verification[]; } gtMaskBuffer;
layout(set = 0, binding = 7) buffer LeMaskBlock { uint verification[]; } leMaskBuffer;
layout(set = 0, binding = 8) buffer LtMaskBlock { uint verification[]; } ltMaskBuffer;

uint boolToUint(bool value) { return value ? 1u : 0u; }

bool checkMaskComponent(uint mask, uint offset, uint validBits, uint bitIndex, uint expectedLess, uint expectedEqual, uint expectedGreater)
{
    for (uint i = 0u; i < 32u; ++i)
    {
        uint idx = offset + i;
        uint bit = (mask >> i) & 1u;
        if (idx < validBits)
        {
            uint expected = idx < bitIndex ? expectedLess : (idx == bitIndex ? expectedEqual : expectedGreater);
            if (bit != expected) return false;
        }
        else if (bit != 0u) return false;
    }
    return true;
}

bool checkMask(uvec4 mask, uint validBits, uint bitIndex, uint expectedLess, uint expectedEqual, uint expectedGreater)
{
    return checkMaskComponent(mask.x, 0u, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater)
        && checkMaskComponent(mask.y, 32u, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater)
        && checkMaskComponent(mask.z, 64u, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater)
        && checkMaskComponent(mask.w, 96u, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater);
}

void main()
{
    uint index = gl_SubgroupInvocationID + gl_SubgroupID * gl_SubgroupSize;
    numSubgroupsBuffer.verification[index] = boolToUint(gl_NumSubgroups == 2u);
    subgroupIdBuffer.verification[index] = boolToUint(gl_SubgroupID < gl_NumSubgroups);
    subgroupSizeBuffer.verification[index] = boolToUint(gl_SubgroupSize == 16u);
    invocationIdBuffer.verification[index] = boolToUint(gl_SubgroupInvocationID < gl_SubgroupSize);
    eqMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupEqMask, gl_SubgroupSize, gl_SubgroupInvocationID, 0u, 1u, 0u));
    geMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupGeMask, gl_SubgroupSize, gl_SubgroupInvocationID, 0u, 1u, 1u));
    gtMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupGtMask, gl_SubgroupSize, gl_SubgroupInvocationID, 0u, 0u, 1u));
    leMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupLeMask, gl_SubgroupSize, gl_SubgroupInvocationID, 1u, 1u, 0u));
    ltMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupLtMask, gl_SubgroupSize, gl_SubgroupInvocationID, 1u, 0u, 0u));
}
```

#### Additional Info

- The source constructs this shader as a C++ string and supplies the selected workgroup and subgroup values for each case.
- The source helper checks the four mask components separately and requires all bits beyond `gl_SubgroupSize` to be zero.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| `workgroupSize` and `subgroupSize` | Changes `local_size_x`, the expected subgroup count, the required subgroup size, and the number of valid mask bits. | [`builtinVerificationProgram`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L83-L170) |
| Pipeline and queue selection | Does not change the shader source. It changes how the same module is selected and dispatched. | [`verifyBuiltins`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L233-L326) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: comp
- Target SPIRV version: spirv1.6

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.6
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 329
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_SubgroupInvocationID %gl_SubgroupID %gl_SubgroupSize %numSubgroupsBuffer %gl_NumSubgroups %subgroupIdBuffer %subgroupSizeBuffer %invocationIdBuffer %eqMaskBuffer %gl_SubgroupEqMask %geMaskBuffer %gl_SubgroupGeMask %gtMaskBuffer %gl_SubgroupGtMask %leMaskBuffer %gl_SubgroupLeMask %ltMaskBuffer %gl_SubgroupLtMask
               OpExecutionMode %main LocalSize 32 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %boolToUint_b1_ "boolToUint(b1;"
               OpName %value "value"
               OpName %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ "checkMaskComponent(u1;u1;u1;u1;u1;u1;u1;"
               OpName %mask "mask"
               OpName %offset "offset"
               OpName %validBits "validBits"
               OpName %bitIndex "bitIndex"
               OpName %expectedLess "expectedLess"
               OpName %expectedEqual "expectedEqual"
               OpName %expectedGreater "expectedGreater"
               OpName %checkMask_vu4_u1_u1_u1_u1_u1_ "checkMask(vu4;u1;u1;u1;u1;u1;"
               OpName %mask_0 "mask"
               OpName %validBits_0 "validBits"
               OpName %bitIndex_0 "bitIndex"
               OpName %expectedLess_0 "expectedLess"
               OpName %expectedEqual_0 "expectedEqual"
               OpName %expectedGreater_0 "expectedGreater"
               OpName %i "i"
               OpName %idx "idx"
               OpName %bit "bit"
               OpName %expected "expected"
               OpName %param "param"
               OpName %param_0 "param"
               OpName %param_1 "param"
               OpName %param_2 "param"
               OpName %param_3 "param"
               OpName %param_4 "param"
               OpName %param_5 "param"
               OpName %param_6 "param"
               OpName %param_7 "param"
               OpName %param_8 "param"
               OpName %param_9 "param"
               OpName %param_10 "param"
               OpName %param_11 "param"
               OpName %param_12 "param"
               OpName %param_13 "param"
               OpName %param_14 "param"
               OpName %param_15 "param"
               OpName %param_16 "param"
               OpName %param_17 "param"
               OpName %param_18 "param"
               OpName %param_19 "param"
               OpName %param_20 "param"
               OpName %param_21 "param"
               OpName %param_22 "param"
               OpName %param_23 "param"
               OpName %param_24 "param"
               OpName %param_25 "param"
               OpName %param_26 "param"
               OpName %index "index"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %gl_SubgroupID "gl_SubgroupID"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %NumSubgroupsBlock "NumSubgroupsBlock"
               OpMemberName %NumSubgroupsBlock 0 "verification"
               OpName %numSubgroupsBuffer "numSubgroupsBuffer"
               OpName %gl_NumSubgroups "gl_NumSubgroups"
               OpName %param_27 "param"
               OpName %SubgroupIdBlock "SubgroupIdBlock"
               OpMemberName %SubgroupIdBlock 0 "verification"
               OpName %subgroupIdBuffer "subgroupIdBuffer"
               OpName %param_28 "param"
               OpName %SubgroupSizeBlock "SubgroupSizeBlock"
               OpMemberName %SubgroupSizeBlock 0 "verification"
               OpName %subgroupSizeBuffer "subgroupSizeBuffer"
               OpName %param_29 "param"
               OpName %InvocationIdBlock "InvocationIdBlock"
               OpMemberName %InvocationIdBlock 0 "verification"
               OpName %invocationIdBuffer "invocationIdBuffer"
               OpName %param_30 "param"
               OpName %EqMaskBlock "EqMaskBlock"
               OpMemberName %EqMaskBlock 0 "verification"
               OpName %eqMaskBuffer "eqMaskBuffer"
               OpName %gl_SubgroupEqMask "gl_SubgroupEqMask"
               OpName %param_31 "param"
               OpName %param_32 "param"
               OpName %param_33 "param"
               OpName %param_34 "param"
               OpName %param_35 "param"
               OpName %param_36 "param"
               OpName %param_37 "param"
               OpName %GeMaskBlock "GeMaskBlock"
               OpMemberName %GeMaskBlock 0 "verification"
               OpName %geMaskBuffer "geMaskBuffer"
               OpName %gl_SubgroupGeMask "gl_SubgroupGeMask"
               OpName %param_38 "param"
               OpName %param_39 "param"
               OpName %param_40 "param"
               OpName %param_41 "param"
               OpName %param_42 "param"
               OpName %param_43 "param"
               OpName %param_44 "param"
               OpName %GtMaskBlock "GtMaskBlock"
               OpMemberName %GtMaskBlock 0 "verification"
               OpName %gtMaskBuffer "gtMaskBuffer"
               OpName %gl_SubgroupGtMask "gl_SubgroupGtMask"
               OpName %param_45 "param"
               OpName %param_46 "param"
               OpName %param_47 "param"
               OpName %param_48 "param"
               OpName %param_49 "param"
               OpName %param_50 "param"
               OpName %param_51 "param"
               OpName %LeMaskBlock "LeMaskBlock"
               OpMemberName %LeMaskBlock 0 "verification"
               OpName %leMaskBuffer "leMaskBuffer"
               OpName %gl_SubgroupLeMask "gl_SubgroupLeMask"
               OpName %param_52 "param"
               OpName %param_53 "param"
               OpName %param_54 "param"
               OpName %param_55 "param"
               OpName %param_56 "param"
               OpName %param_57 "param"
               OpName %param_58 "param"
               OpName %LtMaskBlock "LtMaskBlock"
               OpMemberName %LtMaskBlock 0 "verification"
               OpName %ltMaskBuffer "ltMaskBuffer"
               OpName %gl_SubgroupLtMask "gl_SubgroupLtMask"
               OpName %param_59 "param"
               OpName %param_60 "param"
               OpName %param_61 "param"
               OpName %param_62 "param"
               OpName %param_63 "param"
               OpName %param_64 "param"
               OpName %param_65 "param"
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %178 RelaxedPrecision
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %182 RelaxedPrecision
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %NumSubgroupsBlock Block
               OpMemberDecorate %NumSubgroupsBlock 0 Offset 0
               OpDecorate %numSubgroupsBuffer Binding 0
               OpDecorate %numSubgroupsBuffer DescriptorSet 0
               OpDecorate %gl_NumSubgroups BuiltIn NumSubgroups
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %SubgroupIdBlock Block
               OpMemberDecorate %SubgroupIdBlock 0 Offset 0
               OpDecorate %subgroupIdBuffer Binding 1
               OpDecorate %subgroupIdBuffer DescriptorSet 0
               OpDecorate %_runtimearr_uint_1 ArrayStride 4
               OpDecorate %SubgroupSizeBlock Block
               OpMemberDecorate %SubgroupSizeBlock 0 Offset 0
               OpDecorate %subgroupSizeBuffer Binding 2
               OpDecorate %subgroupSizeBuffer DescriptorSet 0
               OpDecorate %214 RelaxedPrecision
               OpDecorate %_runtimearr_uint_2 ArrayStride 4
               OpDecorate %InvocationIdBlock Block
               OpMemberDecorate %InvocationIdBlock 0 Offset 0
               OpDecorate %invocationIdBuffer Binding 3
               OpDecorate %invocationIdBuffer DescriptorSet 0
               OpDecorate %225 RelaxedPrecision
               OpDecorate %226 RelaxedPrecision
               OpDecorate %_runtimearr_uint_3 ArrayStride 4
               OpDecorate %EqMaskBlock Block
               OpMemberDecorate %EqMaskBlock 0 Offset 0
               OpDecorate %eqMaskBuffer Binding 4
               OpDecorate %eqMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupEqMask BuiltIn SubgroupEqMask
               OpDecorate %241 RelaxedPrecision
               OpDecorate %243 RelaxedPrecision
               OpDecorate %_runtimearr_uint_4 ArrayStride 4
               OpDecorate %GeMaskBlock Block
               OpMemberDecorate %GeMaskBlock 0 Offset 0
               OpDecorate %geMaskBuffer Binding 5
               OpDecorate %geMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupGeMask BuiltIn SubgroupGeMask
               OpDecorate %260 RelaxedPrecision
               OpDecorate %262 RelaxedPrecision
               OpDecorate %_runtimearr_uint_5 ArrayStride 4
               OpDecorate %GtMaskBlock Block
               OpMemberDecorate %GtMaskBlock 0 Offset 0
               OpDecorate %gtMaskBuffer Binding 6
               OpDecorate %gtMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupGtMask BuiltIn SubgroupGtMask
               OpDecorate %279 RelaxedPrecision
               OpDecorate %281 RelaxedPrecision
               OpDecorate %_runtimearr_uint_6 ArrayStride 4
               OpDecorate %LeMaskBlock Block
               OpMemberDecorate %LeMaskBlock 0 Offset 0
               OpDecorate %leMaskBuffer Binding 7
               OpDecorate %leMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupLeMask BuiltIn SubgroupLeMask
               OpDecorate %298 RelaxedPrecision
               OpDecorate %300 RelaxedPrecision
               OpDecorate %_runtimearr_uint_7 ArrayStride 4
               OpDecorate %LtMaskBlock Block
               OpMemberDecorate %LtMaskBlock 0 Offset 0
               OpDecorate %ltMaskBuffer Binding 8
               OpDecorate %ltMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupLtMask BuiltIn SubgroupLtMask
               OpDecorate %317 RelaxedPrecision
               OpDecorate %319 RelaxedPrecision
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
       %uint = OpTypeInt 32 0
          %9 = OpTypeFunction %uint %_ptr_Function_bool
%_ptr_Function_uint = OpTypePointer Function %uint
         %14 = OpTypeFunction %bool %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
         %26 = OpTypeFunction %bool %_ptr_Function_v4uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint %_ptr_Function_uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
    %uint_32 = OpConstant %uint 32
      %false = OpConstantFalse %bool
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
       %true = OpConstantTrue %bool
    %uint_64 = OpConstant %uint 64
     %uint_2 = OpConstant %uint 2
    %uint_96 = OpConstant %uint 96
     %uint_3 = OpConstant %uint 3
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%gl_SubgroupID = OpVariable %_ptr_Input_uint Input
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
%_runtimearr_uint = OpTypeRuntimeArray %uint
%NumSubgroupsBlock = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_NumSubgroupsBlock = OpTypePointer StorageBuffer %NumSubgroupsBlock
%numSubgroupsBuffer = OpVariable %_ptr_StorageBuffer_NumSubgroupsBlock StorageBuffer
      %int_0 = OpConstant %int 0
%gl_NumSubgroups = OpVariable %_ptr_Input_uint Input
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
%SubgroupIdBlock = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_SubgroupIdBlock = OpTypePointer StorageBuffer %SubgroupIdBlock
%subgroupIdBuffer = OpVariable %_ptr_StorageBuffer_SubgroupIdBlock StorageBuffer
%_runtimearr_uint_1 = OpTypeRuntimeArray %uint
%SubgroupSizeBlock = OpTypeStruct %_runtimearr_uint_1
%_ptr_StorageBuffer_SubgroupSizeBlock = OpTypePointer StorageBuffer %SubgroupSizeBlock
%subgroupSizeBuffer = OpVariable %_ptr_StorageBuffer_SubgroupSizeBlock StorageBuffer
    %uint_16 = OpConstant %uint 16
%_runtimearr_uint_2 = OpTypeRuntimeArray %uint
%InvocationIdBlock = OpTypeStruct %_runtimearr_uint_2
%_ptr_StorageBuffer_InvocationIdBlock = OpTypePointer StorageBuffer %InvocationIdBlock
%invocationIdBuffer = OpVariable %_ptr_StorageBuffer_InvocationIdBlock StorageBuffer
%_runtimearr_uint_3 = OpTypeRuntimeArray %uint
%EqMaskBlock = OpTypeStruct %_runtimearr_uint_3
%_ptr_StorageBuffer_EqMaskBlock = OpTypePointer StorageBuffer %EqMaskBlock
%eqMaskBuffer = OpVariable %_ptr_StorageBuffer_EqMaskBlock StorageBuffer
%_ptr_Input_v4uint = OpTypePointer Input %v4uint
%gl_SubgroupEqMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_4 = OpTypeRuntimeArray %uint
%GeMaskBlock = OpTypeStruct %_runtimearr_uint_4
%_ptr_StorageBuffer_GeMaskBlock = OpTypePointer StorageBuffer %GeMaskBlock
%geMaskBuffer = OpVariable %_ptr_StorageBuffer_GeMaskBlock StorageBuffer
%gl_SubgroupGeMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_5 = OpTypeRuntimeArray %uint
%GtMaskBlock = OpTypeStruct %_runtimearr_uint_5
%_ptr_StorageBuffer_GtMaskBlock = OpTypePointer StorageBuffer %GtMaskBlock
%gtMaskBuffer = OpVariable %_ptr_StorageBuffer_GtMaskBlock StorageBuffer
%gl_SubgroupGtMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_6 = OpTypeRuntimeArray %uint
%LeMaskBlock = OpTypeStruct %_runtimearr_uint_6
%_ptr_StorageBuffer_LeMaskBlock = OpTypePointer StorageBuffer %LeMaskBlock
%leMaskBuffer = OpVariable %_ptr_StorageBuffer_LeMaskBlock StorageBuffer
%gl_SubgroupLeMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_7 = OpTypeRuntimeArray %uint
%LtMaskBlock = OpTypeStruct %_runtimearr_uint_7
%_ptr_StorageBuffer_LtMaskBlock = OpTypePointer StorageBuffer %LtMaskBlock
%ltMaskBuffer = OpVariable %_ptr_StorageBuffer_LtMaskBlock StorageBuffer
%gl_SubgroupLtMask = OpVariable %_ptr_Input_v4uint Input
     %v3uint = OpTypeVector %uint 3
        %328 = OpConstantComposite %v3uint %uint_32 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_uint Function
   %param_27 = OpVariable %_ptr_Function_bool Function
   %param_28 = OpVariable %_ptr_Function_bool Function
   %param_29 = OpVariable %_ptr_Function_bool Function
   %param_30 = OpVariable %_ptr_Function_bool Function
   %param_31 = OpVariable %_ptr_Function_v4uint Function
   %param_32 = OpVariable %_ptr_Function_uint Function
   %param_33 = OpVariable %_ptr_Function_uint Function
   %param_34 = OpVariable %_ptr_Function_uint Function
   %param_35 = OpVariable %_ptr_Function_uint Function
   %param_36 = OpVariable %_ptr_Function_uint Function
   %param_37 = OpVariable %_ptr_Function_bool Function
   %param_38 = OpVariable %_ptr_Function_v4uint Function
   %param_39 = OpVariable %_ptr_Function_uint Function
   %param_40 = OpVariable %_ptr_Function_uint Function
   %param_41 = OpVariable %_ptr_Function_uint Function
   %param_42 = OpVariable %_ptr_Function_uint Function
   %param_43 = OpVariable %_ptr_Function_uint Function
   %param_44 = OpVariable %_ptr_Function_bool Function
   %param_45 = OpVariable %_ptr_Function_v4uint Function
   %param_46 = OpVariable %_ptr_Function_uint Function
   %param_47 = OpVariable %_ptr_Function_uint Function
   %param_48 = OpVariable %_ptr_Function_uint Function
   %param_49 = OpVariable %_ptr_Function_uint Function
   %param_50 = OpVariable %_ptr_Function_uint Function
   %param_51 = OpVariable %_ptr_Function_bool Function
   %param_52 = OpVariable %_ptr_Function_v4uint Function
   %param_53 = OpVariable %_ptr_Function_uint Function
   %param_54 = OpVariable %_ptr_Function_uint Function
   %param_55 = OpVariable %_ptr_Function_uint Function
   %param_56 = OpVariable %_ptr_Function_uint Function
   %param_57 = OpVariable %_ptr_Function_uint Function
   %param_58 = OpVariable %_ptr_Function_bool Function
   %param_59 = OpVariable %_ptr_Function_v4uint Function
   %param_60 = OpVariable %_ptr_Function_uint Function
   %param_61 = OpVariable %_ptr_Function_uint Function
   %param_62 = OpVariable %_ptr_Function_uint Function
   %param_63 = OpVariable %_ptr_Function_uint Function
   %param_64 = OpVariable %_ptr_Function_uint Function
   %param_65 = OpVariable %_ptr_Function_bool Function
        %178 = OpLoad %uint %gl_SubgroupInvocationID
        %180 = OpLoad %uint %gl_SubgroupID
        %182 = OpLoad %uint %gl_SubgroupSize
        %183 = OpIMul %uint %180 %182
        %184 = OpIAdd %uint %178 %183
               OpStore %index %184
        %190 = OpLoad %uint %index
        %192 = OpLoad %uint %gl_NumSubgroups
        %193 = OpIEqual %bool %192 %uint_2
               OpStore %param_27 %193
        %195 = OpFunctionCall %uint %boolToUint_b1_ %param_27
        %197 = OpAccessChain %_ptr_StorageBuffer_uint %numSubgroupsBuffer %int_0 %190
               OpStore %197 %195
        %202 = OpLoad %uint %index
        %203 = OpLoad %uint %gl_SubgroupID
        %204 = OpLoad %uint %gl_NumSubgroups
        %205 = OpULessThan %bool %203 %204
               OpStore %param_28 %205
        %207 = OpFunctionCall %uint %boolToUint_b1_ %param_28
        %208 = OpAccessChain %_ptr_StorageBuffer_uint %subgroupIdBuffer %int_0 %202
               OpStore %208 %207
        %213 = OpLoad %uint %index
        %214 = OpLoad %uint %gl_SubgroupSize
        %216 = OpIEqual %bool %214 %uint_16
               OpStore %param_29 %216
        %218 = OpFunctionCall %uint %boolToUint_b1_ %param_29
        %219 = OpAccessChain %_ptr_StorageBuffer_uint %subgroupSizeBuffer %int_0 %213
               OpStore %219 %218
        %224 = OpLoad %uint %index
        %225 = OpLoad %uint %gl_SubgroupInvocationID
        %226 = OpLoad %uint %gl_SubgroupSize
        %227 = OpULessThan %bool %225 %226
               OpStore %param_30 %227
        %229 = OpFunctionCall %uint %boolToUint_b1_ %param_30
        %230 = OpAccessChain %_ptr_StorageBuffer_uint %invocationIdBuffer %int_0 %224
               OpStore %230 %229
        %235 = OpLoad %uint %index
        %239 = OpLoad %v4uint %gl_SubgroupEqMask
               OpStore %param_31 %239
        %241 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_32 %241
        %243 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_33 %243
               OpStore %param_34 %uint_0
               OpStore %param_35 %uint_1
               OpStore %param_36 %uint_0
        %247 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_31 %param_32 %param_33 %param_34 %param_35 %param_36
               OpStore %param_37 %247
        %249 = OpFunctionCall %uint %boolToUint_b1_ %param_37
        %250 = OpAccessChain %_ptr_StorageBuffer_uint %eqMaskBuffer %int_0 %235
               OpStore %250 %249
        %255 = OpLoad %uint %index
        %258 = OpLoad %v4uint %gl_SubgroupGeMask
               OpStore %param_38 %258
        %260 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_39 %260
        %262 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_40 %262
               OpStore %param_41 %uint_0
               OpStore %param_42 %uint_1
               OpStore %param_43 %uint_1
        %266 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_38 %param_39 %param_40 %param_41 %param_42 %param_43
               OpStore %param_44 %266
        %268 = OpFunctionCall %uint %boolToUint_b1_ %param_44
        %269 = OpAccessChain %_ptr_StorageBuffer_uint %geMaskBuffer %int_0 %255
               OpStore %269 %268
        %274 = OpLoad %uint %index
        %277 = OpLoad %v4uint %gl_SubgroupGtMask
               OpStore %param_45 %277
        %279 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_46 %279
        %281 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_47 %281
               OpStore %param_48 %uint_0
               OpStore %param_49 %uint_0
               OpStore %param_50 %uint_1
        %285 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_45 %param_46 %param_47 %param_48 %param_49 %param_50
               OpStore %param_51 %285
        %287 = OpFunctionCall %uint %boolToUint_b1_ %param_51
        %288 = OpAccessChain %_ptr_StorageBuffer_uint %gtMaskBuffer %int_0 %274
               OpStore %288 %287
        %293 = OpLoad %uint %index
        %296 = OpLoad %v4uint %gl_SubgroupLeMask
               OpStore %param_52 %296
        %298 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_53 %298
        %300 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_54 %300
               OpStore %param_55 %uint_1
               OpStore %param_56 %uint_1
               OpStore %param_57 %uint_0
        %304 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_52 %param_53 %param_54 %param_55 %param_56 %param_57
               OpStore %param_58 %304
        %306 = OpFunctionCall %uint %boolToUint_b1_ %param_58
        %307 = OpAccessChain %_ptr_StorageBuffer_uint %leMaskBuffer %int_0 %293
               OpStore %307 %306
        %312 = OpLoad %uint %index
        %315 = OpLoad %v4uint %gl_SubgroupLtMask
               OpStore %param_59 %315
        %317 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_60 %317
        %319 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_61 %319
               OpStore %param_62 %uint_1
               OpStore %param_63 %uint_0
               OpStore %param_64 %uint_0
        %323 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_59 %param_60 %param_61 %param_62 %param_63 %param_64
               OpStore %param_65 %323
        %325 = OpFunctionCall %uint %boolToUint_b1_ %param_65
        %326 = OpAccessChain %_ptr_StorageBuffer_uint %ltMaskBuffer %int_0 %312
               OpStore %326 %325
               OpReturn
               OpFunctionEnd
%boolToUint_b1_ = OpFunction %uint None %9
      %value = OpFunctionParameter %_ptr_Function_bool
         %12 = OpLabel
         %35 = OpLoad %bool %value
         %38 = OpSelect %uint %35 %uint_1 %uint_0
               OpReturnValue %38
               OpFunctionEnd
%checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ = OpFunction %bool None %14
       %mask = OpFunctionParameter %_ptr_Function_uint
     %offset = OpFunctionParameter %_ptr_Function_uint
  %validBits = OpFunctionParameter %_ptr_Function_uint
   %bitIndex = OpFunctionParameter %_ptr_Function_uint
%expectedLess = OpFunctionParameter %_ptr_Function_uint
%expectedEqual = OpFunctionParameter %_ptr_Function_uint
%expectedGreater = OpFunctionParameter %_ptr_Function_uint
         %23 = OpLabel
          %i = OpVariable %_ptr_Function_uint Function
        %idx = OpVariable %_ptr_Function_uint Function
        %bit = OpVariable %_ptr_Function_uint Function
   %expected = OpVariable %_ptr_Function_uint Function
         %68 = OpVariable %_ptr_Function_uint Function
               OpStore %i %uint_0
               OpBranch %42
         %42 = OpLabel
               OpLoopMerge %44 %45 None
               OpBranch %46
         %46 = OpLabel
         %47 = OpLoad %uint %i
         %49 = OpULessThan %bool %47 %uint_32
               OpBranchConditional %49 %43 %44
         %43 = OpLabel
         %51 = OpLoad %uint %offset
         %52 = OpLoad %uint %i
         %53 = OpIAdd %uint %51 %52
               OpStore %idx %53
         %55 = OpLoad %uint %mask
         %56 = OpLoad %uint %i
         %57 = OpShiftRightLogical %uint %55 %56
         %58 = OpBitwiseAnd %uint %57 %uint_1
               OpStore %bit %58
         %59 = OpLoad %uint %idx
         %60 = OpLoad %uint %validBits
         %61 = OpULessThan %bool %59 %60
               OpSelectionMerge %63 None
               OpBranchConditional %61 %62 %87
         %62 = OpLabel
         %65 = OpLoad %uint %idx
         %66 = OpLoad %uint %bitIndex
         %67 = OpULessThan %bool %65 %66
               OpSelectionMerge %70 None
               OpBranchConditional %67 %69 %72
         %69 = OpLabel
         %71 = OpLoad %uint %expectedLess
               OpStore %68 %71
               OpBranch %70
         %72 = OpLabel
         %73 = OpLoad %uint %idx
         %74 = OpLoad %uint %bitIndex
         %75 = OpIEqual %bool %73 %74
         %76 = OpLoad %uint %expectedEqual
         %77 = OpLoad %uint %expectedGreater
         %78 = OpSelect %uint %75 %76 %77
               OpStore %68 %78
               OpBranch %70
         %70 = OpLabel
         %79 = OpLoad %uint %68
               OpStore %expected %79
         %80 = OpLoad %uint %bit
         %81 = OpLoad %uint %expected
         %82 = OpINotEqual %bool %80 %81
               OpSelectionMerge %84 None
               OpBranchConditional %82 %83 %84
         %83 = OpLabel
               OpReturnValue %false
         %84 = OpLabel
               OpBranch %63
         %87 = OpLabel
         %88 = OpLoad %uint %bit
         %89 = OpINotEqual %bool %88 %uint_0
               OpSelectionMerge %91 None
               OpBranchConditional %89 %90 %91
         %90 = OpLabel
               OpReturnValue %false
         %91 = OpLabel
               OpBranch %63
         %63 = OpLabel
               OpBranch %45
         %45 = OpLabel
         %93 = OpLoad %uint %i
         %96 = OpIAdd %uint %93 %int_1
               OpStore %i %96
               OpBranch %42
         %44 = OpLabel
               OpReturnValue %true
               OpFunctionEnd
%checkMask_vu4_u1_u1_u1_u1_u1_ = OpFunction %bool None %26
     %mask_0 = OpFunctionParameter %_ptr_Function_v4uint
%validBits_0 = OpFunctionParameter %_ptr_Function_uint
 %bitIndex_0 = OpFunctionParameter %_ptr_Function_uint
%expectedLess_0 = OpFunctionParameter %_ptr_Function_uint
%expectedEqual_0 = OpFunctionParameter %_ptr_Function_uint
%expectedGreater_0 = OpFunctionParameter %_ptr_Function_uint
         %34 = OpLabel
      %param = OpVariable %_ptr_Function_uint Function
    %param_0 = OpVariable %_ptr_Function_uint Function
    %param_1 = OpVariable %_ptr_Function_uint Function
    %param_2 = OpVariable %_ptr_Function_uint Function
    %param_3 = OpVariable %_ptr_Function_uint Function
    %param_4 = OpVariable %_ptr_Function_uint Function
    %param_5 = OpVariable %_ptr_Function_uint Function
    %param_6 = OpVariable %_ptr_Function_uint Function
    %param_7 = OpVariable %_ptr_Function_uint Function
    %param_8 = OpVariable %_ptr_Function_uint Function
    %param_9 = OpVariable %_ptr_Function_uint Function
   %param_10 = OpVariable %_ptr_Function_uint Function
   %param_11 = OpVariable %_ptr_Function_uint Function
   %param_12 = OpVariable %_ptr_Function_uint Function
   %param_13 = OpVariable %_ptr_Function_uint Function
   %param_14 = OpVariable %_ptr_Function_uint Function
   %param_15 = OpVariable %_ptr_Function_uint Function
   %param_16 = OpVariable %_ptr_Function_uint Function
   %param_17 = OpVariable %_ptr_Function_uint Function
   %param_18 = OpVariable %_ptr_Function_uint Function
   %param_19 = OpVariable %_ptr_Function_uint Function
   %param_20 = OpVariable %_ptr_Function_uint Function
   %param_21 = OpVariable %_ptr_Function_uint Function
   %param_22 = OpVariable %_ptr_Function_uint Function
   %param_23 = OpVariable %_ptr_Function_uint Function
   %param_24 = OpVariable %_ptr_Function_uint Function
   %param_25 = OpVariable %_ptr_Function_uint Function
   %param_26 = OpVariable %_ptr_Function_uint Function
        %101 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_0
        %102 = OpLoad %uint %101
               OpStore %param %102
               OpStore %param_0 %uint_0
        %105 = OpLoad %uint %validBits_0
               OpStore %param_1 %105
        %107 = OpLoad %uint %bitIndex_0
               OpStore %param_2 %107
        %109 = OpLoad %uint %expectedLess_0
               OpStore %param_3 %109
        %111 = OpLoad %uint %expectedEqual_0
               OpStore %param_4 %111
        %113 = OpLoad %uint %expectedGreater_0
               OpStore %param_5 %113
        %114 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param %param_0 %param_1 %param_2 %param_3 %param_4 %param_5
               OpSelectionMerge %116 None
               OpBranchConditional %114 %115 %116
        %115 = OpLabel
        %118 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_1
        %119 = OpLoad %uint %118
               OpStore %param_6 %119
               OpStore %param_7 %uint_32
        %122 = OpLoad %uint %validBits_0
               OpStore %param_8 %122
        %124 = OpLoad %uint %bitIndex_0
               OpStore %param_9 %124
        %126 = OpLoad %uint %expectedLess_0
               OpStore %param_10 %126
        %128 = OpLoad %uint %expectedEqual_0
               OpStore %param_11 %128
        %130 = OpLoad %uint %expectedGreater_0
               OpStore %param_12 %130
        %131 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param_6 %param_7 %param_8 %param_9 %param_10 %param_11 %param_12
               OpBranch %116
        %116 = OpLabel
        %132 = OpPhi %bool %114 %34 %131 %115
               OpSelectionMerge %134 None
               OpBranchConditional %132 %133 %134
        %133 = OpLabel
        %138 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_2
        %139 = OpLoad %uint %138
               OpStore %param_13 %139
               OpStore %param_14 %uint_64
        %142 = OpLoad %uint %validBits_0
               OpStore %param_15 %142
        %144 = OpLoad %uint %bitIndex_0
               OpStore %param_16 %144
        %146 = OpLoad %uint %expectedLess_0
               OpStore %param_17 %146
        %148 = OpLoad %uint %expectedEqual_0
               OpStore %param_18 %148
        %150 = OpLoad %uint %expectedGreater_0
               OpStore %param_19 %150
        %151 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param_13 %param_14 %param_15 %param_16 %param_17 %param_18 %param_19
               OpBranch %134
        %134 = OpLabel
        %152 = OpPhi %bool %132 %116 %151 %133
               OpSelectionMerge %154 None
               OpBranchConditional %152 %153 %154
        %153 = OpLabel
        %158 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_3
        %159 = OpLoad %uint %158
               OpStore %param_20 %159
               OpStore %param_21 %uint_96
        %162 = OpLoad %uint %validBits_0
               OpStore %param_22 %162
        %164 = OpLoad %uint %bitIndex_0
               OpStore %param_23 %164
        %166 = OpLoad %uint %expectedLess_0
               OpStore %param_24 %166
        %168 = OpLoad %uint %expectedEqual_0
               OpStore %param_25 %168
        %170 = OpLoad %uint %expectedGreater_0
               OpStore %param_26 %170
        %171 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param_20 %param_21 %param_22 %param_23 %param_24 %param_25 %param_26
               OpBranch %154
        %154 = OpLabel
        %172 = OpPhi %bool %152 %134 %171 %153
               OpReturnValue %172
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates nine host-visible storage buffers, initializes each element to zero, and binds them at descriptor bindings 0 through 8. The bindings correspond to the four scalar checks followed by the five ballot-mask checks.
- With `pipelineToken = false`, the host creates and binds a normal compute pipeline. With `pipelineToken = true`, it creates a `DGCComputePipeline`, obtains its device address, and places that address in the generated command stream.
- The indirect-command layout contains the pipeline token when selected and a dispatch token. The stream supplies dispatch dimensions `1, 1, 1`, and the test executes one sequence. The host prepares a preprocess buffer for that sequence and inserts a metadata-to-preprocess barrier for the DGC pipeline path.
- The command buffer binds the descriptor set, executes the generated command, and inserts a compute-shader-write to host-read memory barrier before submission. The host waits for completion and reads all nine buffers.
- The host compares every element in every buffer with `1`. It logs each mismatch with its binding and position, then returns failure if any mismatch remains.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `16` | The implementation reports or evaluates subgroup scalar or mask built-ins incorrectly for 16-wide subgroups, or the selected pipeline and queue path does not preserve those values. |
| `32` | The implementation reports or evaluates subgroup scalar or mask built-ins incorrectly for 32-wide subgroups, or the selected pipeline and queue path does not preserve those values. |
| `64` | The implementation reports or evaluates subgroup scalar or mask built-ins incorrectly for 64-wide subgroups, or the selected pipeline and queue path does not preserve those values. |
| `128` | The implementation reports or evaluates subgroup scalar or mask built-ins incorrectly for 128-wide subgroups, or the selected pipeline and queue path does not preserve those values. |

### Cause Analysis

#### Subgroup scalar or mask built-in mismatch

**Possible failure symptoms:** One or more output elements is `0` or another value instead of `1`. The log identifies the output binding and invocation position, but the same failure string covers all nine check arrays.

**Possible implementation causes:** The selected subgroup size, subgroup partition, scalar built-in values, or mask-built-in lowering may not match the Vulkan subgroup semantics exercised by the generated shader. The source does not identify a narrower implementation cause, so a failing case needs investigation of the reported binding, shader compilation, and execution path.

#### Generated-command or queue execution mismatch

**Possible failure symptoms:** A case using `_dgc_pipeline` or `_cq` produces unexpected values while a corresponding normal-pipeline or universal-queue case passes. The host reports each differing binding and position for each buffer scan.

**Possible implementation causes:** The failure may lie in pipeline selection through the NV generated-command path, command-stream interpretation, queue support, or synchronization before host readback. The test source does not establish which layer is responsible; compare the matching variants before assigning a cause.

## Case Pruning

### Requirement-based pruning

The case support callback skips a case with `NotSupportedError` when any required condition fails:

- DGC compute support is unavailable for the selected `pipelineToken` mode.
- The equivalent Vulkan API version is below Vulkan 1.3.
- `subgroupSize` falls outside `minSubgroupSize` or `maxSubgroupSize`.
- The compute stage is absent from `requiredSubgroupSizeStages`.
- The `_cq` case has no compute queue.

These are support results, not test failures. The callback checks the queue only for the compute-queue variants.

### Design-based pruning

The generator iterates both size lists in ascending order and stops the inner loop when `subgroupSize > workgroupSize`. It therefore retains only pairs where the subgroup fits within the workgroup. The full Cartesian product would contain 16 size pairs, while the retained set has 10 pairs. Each retained pair expands to four pipeline and queue variants, producing 40 test case leaves.

This exclusion keeps the generated matrix aligned with `getNumSubgroups()`, which asserts that `totalInvocations` is divisible by `subgroupSize`; it is part of test construction, not a device capability failure.

## Key Takeaways

- The test checks subgroup scalar and mask built-ins from inside the compute shader, then reduces every check to a host-visible `1` or `0`.
- `workgroupSize` controls the number of invocations; `subgroupSize` controls the partition and is the primary behavior choice.
- The same shader checks run through normal and NV DGC pipeline paths and on universal or compute queues.
- Unsupported environments skip cases through explicit support checks. Invalid size relationships never enter the registered matrix.
- A failure identifies an unexpected shader result. Comparing the paired pipeline and queue variants helps locate whether the issue is tied to generated-command execution or to subgroup behavior itself.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter structure and support gates | [`BuiltinParams` and `checkSubgroupSupport`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L50-L81) | Defines size derivation and requirement-based pruning. |
| Generated shader | [`builtinVerificationProgram`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L83-L171) | Defines the subgroup built-in and ballot-mask checks. |
| Resource and pipeline setup | [`verifyBuiltins` setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L173-L297) | Creates output buffers, descriptors, and normal or DGC pipeline state. |
| Generated dispatch and synchronization | [`verifyBuiltins` execution](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L299-L326) | Builds the command stream, executes one sequence, and makes shader writes visible to the host. |
| Output scan | [`verifyBuiltins` result check](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L328-L355) | Defines mismatch logging and the pass/fail result. |
| Registration matrix | [`createDGCComputeSubgroupTests`](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L359-L388) | Defines exact names, values, and design pruning. |
| Registered mustpass leaves | [`dgc.txt` subgroup entries](../../../mustpass/main/vk-default/dgc.txt#L4538-L4577) | Confirms the 40 current registered variants. |
