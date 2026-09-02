## Overview

**Core question:** Does the EXT generated compute path preserve subgroup built-in values and masks across pipeline and queue execution modes?

- This page covers `vktDGCComputeSubgroupTestsExt.cpp`, which implements `dgc.ext.compute.subgroups.builtins`.
- Each test generates a compute shader, runs one dispatch through either a normal pipeline or an EXT device-generated pipeline, and checks nine per-invocation result buffers.
- Workgroup size, requested subgroup size, pipeline-token use, and queue choice form the case matrix.
- The page explains the subgroup arithmetic, EXT command sequence, result checking, pruning, and failure interpretation.

## Background Knowledge

- A compute workgroup contains one or more subgroups. `gl_SubgroupID` selects a subgroup, and `gl_SubgroupInvocationID` selects an invocation within it. `gl_SubgroupSize` gives the subgroup width and `gl_NumSubgroups` gives the number of subgroups in the workgroup.
- The subgroup ballot masks describe the relation between the current invocation and each lane. The equal mask has one bit at the current lane, while the less-than, greater-than, less-than-or-equal, and greater-than-or-equal masks contain the corresponding lanes. Bits outside the valid subgroup width must be zero.
- `VK_EXT_device_generated_commands` lets the application put command arguments in a device-addressable buffer and execute a layout of tokens. An indirect execution set supplies pipeline state to an execution-set token. A preprocess buffer holds the state needed before generated commands execute.

## Registration Hierarchy

```text
dgc.ext.compute.subgroups
└── builtins
```

The `subgroups` test family has one implemented intermediate node, `builtins`. The source registers that intermediate node and its executable test cases in [createDGCComputeSubgroupTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L356-L384).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Workgroup size | `16`, `32`, `64`, `128` | Sets the shader `local_size_x` and the number of result entries per output buffer. | [BuiltinParams and shader generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L49-L61) |
| Requested subgroup size | `16`, `32`, `64`, `128` | Sets the required subgroup size in the compute pipeline and changes the expected subgroup count and masks. | [Support checks and pipeline creation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L63-L84) |
| Pipeline execution mode | `normal_pipeline`, `dgc_pipeline` | Selects a normal compute pipeline or a pipeline placed in an EXT indirect execution set and selected by a pipeline token. | [Pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L236-L257) |
| Queue mode | default queue, encoded by no suffix; compute queue, encoded by `_cq` | Selects the queue family and queue used for command submission. | [Queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L176-L185) |

The registered case names are:

```text
workgroup_size_16_subgroup_size_16_dgc_pipeline
workgroup_size_16_subgroup_size_16_dgc_pipeline_cq
workgroup_size_16_subgroup_size_16_normal_pipeline
workgroup_size_16_subgroup_size_16_normal_pipeline_cq
workgroup_size_32_subgroup_size_16_dgc_pipeline
workgroup_size_32_subgroup_size_16_dgc_pipeline_cq
workgroup_size_32_subgroup_size_16_normal_pipeline
workgroup_size_32_subgroup_size_16_normal_pipeline_cq
workgroup_size_32_subgroup_size_32_dgc_pipeline
workgroup_size_32_subgroup_size_32_dgc_pipeline_cq
workgroup_size_32_subgroup_size_32_normal_pipeline
workgroup_size_32_subgroup_size_32_normal_pipeline_cq
workgroup_size_64_subgroup_size_16_dgc_pipeline
workgroup_size_64_subgroup_size_16_dgc_pipeline_cq
workgroup_size_64_subgroup_size_16_normal_pipeline
workgroup_size_64_subgroup_size_16_normal_pipeline_cq
workgroup_size_64_subgroup_size_32_dgc_pipeline
workgroup_size_64_subgroup_size_32_dgc_pipeline_cq
workgroup_size_64_subgroup_size_32_normal_pipeline
workgroup_size_64_subgroup_size_32_normal_pipeline_cq
workgroup_size_64_subgroup_size_64_dgc_pipeline
workgroup_size_64_subgroup_size_64_dgc_pipeline_cq
workgroup_size_64_subgroup_size_64_normal_pipeline
workgroup_size_64_subgroup_size_64_normal_pipeline_cq
workgroup_size_128_subgroup_size_16_dgc_pipeline
workgroup_size_128_subgroup_size_16_dgc_pipeline_cq
workgroup_size_128_subgroup_size_16_normal_pipeline
workgroup_size_128_subgroup_size_16_normal_pipeline_cq
workgroup_size_128_subgroup_size_32_dgc_pipeline
workgroup_size_128_subgroup_size_32_dgc_pipeline_cq
workgroup_size_128_subgroup_size_32_normal_pipeline
workgroup_size_128_subgroup_size_32_normal_pipeline_cq
workgroup_size_128_subgroup_size_64_dgc_pipeline
workgroup_size_128_subgroup_size_64_dgc_pipeline_cq
workgroup_size_128_subgroup_size_64_normal_pipeline
workgroup_size_128_subgroup_size_64_normal_pipeline_cq
workgroup_size_128_subgroup_size_128_dgc_pipeline
workgroup_size_128_subgroup_size_128_dgc_pipeline_cq
workgroup_size_128_subgroup_size_128_normal_pipeline
workgroup_size_128_subgroup_size_128_normal_pipeline_cq
```

## Behavior Parameters

The primary behavioral axis is pipeline and queue execution mode. The workgroup and requested subgroup sizes change the arithmetic tested by the shader, while these four values change how the same shader dispatch reaches the device.

### `normal_pipeline`: normal pipeline on the default queue

The host binds a compute pipeline created with the required subgroup size. The generated command layout contains only a dispatch token. The default queue submits the command buffer.

### `dgc_pipeline`: EXT pipeline token on the default queue

The host creates an indirect-bindable compute pipeline, puts it at index `0` in an EXT indirect execution set, and binds that set through a compute pipeline token. The generated command data starts with index `0` and continues with dispatch dimensions `1, 1, 1`.

### `normal_pipeline_cq`: normal pipeline on the compute queue

The normal pipeline path uses the compute queue and its family index for command-pool creation and submission. The shader and result contract stay the same.

### `dgc_pipeline_cq`: EXT pipeline token on the compute queue

The DGC path uses the compute queue while retaining the execution set, pipeline token, preprocess buffer, and dispatch token. A failure isolates neither queue choice nor generated pipeline execution by itself, so the common subgroup checks still matter.

## Shader Analysis

`builtinVerificationProgram` constructs one GLSL compute shader for each case and compiles it with `ShaderBuildOptions` targeting SPIR-V 1.6. The shader enables `GL_KHR_shader_subgroup_basic` and `GL_KHR_shader_subgroup_ballot`. It declares nine storage-buffer bindings, numbered 0 through 8, for the checks.

The shader computes a flat result index as `gl_SubgroupInvocationID + gl_SubgroupID * gl_SubgroupSize`. It writes one boolean-as-`uint` value to each buffer. The first four checks compare the number of subgroups, subgroup ID, subgroup size, and invocation ID with their expected relationships.

The five mask checks inspect the four 32-bit components of each `uvec4` mask. For valid lane indices, `checkMaskComponent` compares each bit with the expected relation to the current invocation. It also rejects any set bit at an index greater than or equal to `gl_SubgroupSize`. The expected bit patterns are:

| Mask | Lanes below the current lane | Current lane | Lanes above the current lane |
|------|-------------------------------|--------------|------------------------------|
| `gl_SubgroupEqMask` | `0` | `1` | `0` |
| `gl_SubgroupGeMask` | `0` | `1` | `1` |
| `gl_SubgroupGtMask` | `0` | `0` | `1` |
| `gl_SubgroupLeMask` | `1` | `1` | `0` |
| `gl_SubgroupLtMask` | `1` | `0` | `0` |

The shader source is assembled in [builtinVerificationProgram](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L86-L174). The walkthrough below reconstructs one exact generated case from those source branches. Its complete SPIR-V assembly comes from compiling the reconstructed GLSL for the source-selected SPIR-V 1.6 target and validating the binary before disassembly.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.ext.compute.subgroups.builtins.workgroup_size_16_subgroup_size_16_normal_pipeline
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `workgroup_size_16` | Emits `layout (local_size_x=16, local_size_y=1, local_size_z=1) in`, so one dispatch launches 16 compute invocations. |
| `subgroup_size_16` | The required subgroup size is 16, so the expected subgroup count is `16 / 16 = 1`; the first 16 bits of each mask are valid and all remaining bits must be zero. |
| `normal_pipeline` | Uses the ordinary compute-pipeline bind path; the shader itself is shared with the DGC pipeline-token variants. |
| no `_cq` suffix | Submits on the default queue rather than selecting `context.getComputeQueue()`. |

#### Purpose

This generated compute shader checks that subgroup built-ins and ballot masks describe one 16-invocation subgroup consistently. Each invocation records a `1` only when its local subgroup values and all five mask relations are correct.

#### Structural Design

| Phase | Shader operation | Recorded evidence |
|-------|------------------|-------------------|
| Index | Combine `gl_SubgroupInvocationID` with `gl_SubgroupID * gl_SubgroupSize`. | Selects one element in every output buffer. |
| Scalar built-ins | Check subgroup count, subgroup ID, subgroup size, and invocation ID. | Bindings 0 through 3. |
| Ballot masks | Check four 32-bit components, accepting only valid bits and rejecting set bits outside `gl_SubgroupSize`. | Bindings 4 through 8. |
| Host result | The host expects every stored value to equal `1`. | Any zero identifies a failed check and invocation. |

#### Shader Code

```glsl
#version 460
#extension GL_KHR_shader_subgroup_basic  : require
#extension GL_KHR_shader_subgroup_ballot : require

/// One workgroup contains 16 invocations; the selected representative requests a 16-lane subgroup.
layout (local_size_x=16, local_size_y=1, local_size_z=1) in;

/// Each host-created storage buffer has one uint entry per invocation. Bindings 0-3 record scalar built-in checks.
layout (set=0, binding=0) buffer NumSubgroupsBlock { uint verification[]; } numSubgroupsBuffer;
layout (set=0, binding=1) buffer SubgroupIdBlock   { uint verification[]; } subgroupIdBuffer;
layout (set=0, binding=2) buffer SubgroupSizeBlock { uint verification[]; } subgroupSizeBuffer;
layout (set=0, binding=3) buffer invocationIdBlock { uint verification[]; } invocationIdBuffer;
/// Bindings 4-8 record the equality, greater/equal, greater-than, less/equal, and less-than ballot-mask checks.
layout (set=0, binding=4) buffer eqMaskBlock       { uint verification[]; } eqMaskBuffer;
layout (set=0, binding=5) buffer geMaskBlock       { uint verification[]; } geMaskBuffer;
layout (set=0, binding=6) buffer gtMaskBlock       { uint verification[]; } gtMaskBuffer;
layout (set=0, binding=7) buffer leMaskBlock       { uint verification[]; } leMaskBuffer;
layout (set=0, binding=8) buffer ltMaskBlock       { uint verification[]; } ltMaskBuffer;

uint boolToUint (bool value)
{
   return (value ? 1 : 0);
}

/// Converts each boolean predicate to the uint value consumed by the host-side result scan.
bool checkMaskComponent (uint mask, uint offset, uint validBits, uint bitIndex, uint expectedLess, uint expectedEqual, uint expectedGreater)
{
    bool ok = true;
    for (uint i = 0; i < 32; ++i)
    {
        const uint bit = ((mask >> i) & 1);
        const uint idx = offset + i;

        if (idx < validBits) {
            if (idx < bitIndex && bit != expectedLess)
                ok = false;
            else if (idx == bitIndex && bit != expectedEqual)
                ok = false;
            else if (idx > bitIndex && bit != expectedGreater)
                ok = false;
        }
        else if (bit != 0)
            ok = false;
    }
    return ok;
}

/// Checks all four uvec4 components, including zeroes beyond the active subgroup width.
bool checkMask (uvec4 mask, uint validBits, uint bitIndex, uint expectedLess, uint expectedEqual, uint expectedGreater)
{
   return (checkMaskComponent(mask.x,  0, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater) &&
           checkMaskComponent(mask.y, 32, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater) &&
           checkMaskComponent(mask.z, 64, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater) &&
           checkMaskComponent(mask.w, 96, validBits, bitIndex, expectedLess, expectedEqual, expectedGreater));
}

void main (void)
{
    /// The flat index maps every invocation to the corresponding element of all nine result buffers.
    const uint index = gl_SubgroupInvocationID + gl_SubgroupID * gl_SubgroupSize;

    numSubgroupsBuffer.verification[index] = boolToUint(gl_NumSubgroups == 1);
    subgroupIdBuffer.verification  [index] = boolToUint(gl_SubgroupID >= 0 && gl_SubgroupID < gl_NumSubgroups);
    subgroupSizeBuffer.verification[index] = boolToUint(gl_SubgroupSize == 16);
    invocationIdBuffer.verification[index] = boolToUint(gl_SubgroupInvocationID >= 0 && gl_SubgroupInvocationID < gl_SubgroupSize);

    /// Expected mask relations are less-than (1,0,0), equal (0,1,0), greater-than (0,0,1), and their inclusive forms.
    eqMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupEqMask, gl_SubgroupSize, gl_SubgroupInvocationID, 0, 1, 0));
    geMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupGeMask, gl_SubgroupSize, gl_SubgroupInvocationID, 0, 1, 1));
    gtMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupGtMask, gl_SubgroupSize, gl_SubgroupInvocationID, 0, 0, 1));
    leMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupLeMask, gl_SubgroupSize, gl_SubgroupInvocationID, 1, 1, 0));
    ltMaskBuffer.verification[index] = boolToUint(checkMask(gl_SubgroupLtMask, gl_SubgroupSize, gl_SubgroupInvocationID, 1, 0, 0));
}
```

#### Additional Info

- The source fixes the generated shader's build target at `SPIRV_VERSION_1_6`; the representative assembly below was compiled with the matching `spirv1.6` environment.
- Bindings 0 through 8 are host-created `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` objects, each initialized to zero and sized for `totalInvocations`; `shared` shader-local memory is not involved.
- The normal-pipeline case uses the same generated program as the DGC cases, but only the DGC cases add a compute-pipeline token and execution-set selection to the generated command layout.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Workgroup size | Changes `local_size_x`, the flat output-buffer extent, and the literal expected subgroup count. | [BuiltinParams and shader generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L49-L61) |
| Requested subgroup size | Changes the required pipeline subgroup size and the literal scalar check; the mask helper always uses the runtime `gl_SubgroupSize`. | [Support checks and shader generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L63-L84) |
| Pipeline execution mode | Does not change this generated GLSL; it changes whether the host layout includes the DGC compute-pipeline token. | [Pipeline and token setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L236-L264) |
| Queue mode | Does not change this generated GLSL; it changes the selected queue and queue-family index for submission. | [Queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L176-L185) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.6`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.6
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 348
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_SubgroupInvocationID %gl_SubgroupID %gl_SubgroupSize %numSubgroupsBuffer %gl_NumSubgroups %subgroupIdBuffer %subgroupSizeBuffer %invocationIdBuffer %eqMaskBuffer %gl_SubgroupEqMask %geMaskBuffer %gl_SubgroupGeMask %gtMaskBuffer %gl_SubgroupGtMask %leMaskBuffer %gl_SubgroupLeMask %ltMaskBuffer %gl_SubgroupLtMask
               OpExecutionMode %main LocalSize 16 1 1
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
               OpName %ok "ok"
               OpName %i "i"
               OpName %bit "bit"
               OpName %idx "idx"
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
               OpName %invocationIdBlock "invocationIdBlock"
               OpMemberName %invocationIdBlock 0 "verification"
               OpName %invocationIdBuffer "invocationIdBuffer"
               OpName %param_30 "param"
               OpName %eqMaskBlock "eqMaskBlock"
               OpMemberName %eqMaskBlock 0 "verification"
               OpName %eqMaskBuffer "eqMaskBuffer"
               OpName %gl_SubgroupEqMask "gl_SubgroupEqMask"
               OpName %param_31 "param"
               OpName %param_32 "param"
               OpName %param_33 "param"
               OpName %param_34 "param"
               OpName %param_35 "param"
               OpName %param_36 "param"
               OpName %param_37 "param"
               OpName %geMaskBlock "geMaskBlock"
               OpMemberName %geMaskBlock 0 "verification"
               OpName %geMaskBuffer "geMaskBuffer"
               OpName %gl_SubgroupGeMask "gl_SubgroupGeMask"
               OpName %param_38 "param"
               OpName %param_39 "param"
               OpName %param_40 "param"
               OpName %param_41 "param"
               OpName %param_42 "param"
               OpName %param_43 "param"
               OpName %param_44 "param"
               OpName %gtMaskBlock "gtMaskBlock"
               OpMemberName %gtMaskBlock 0 "verification"
               OpName %gtMaskBuffer "gtMaskBuffer"
               OpName %gl_SubgroupGtMask "gl_SubgroupGtMask"
               OpName %param_45 "param"
               OpName %param_46 "param"
               OpName %param_47 "param"
               OpName %param_48 "param"
               OpName %param_49 "param"
               OpName %param_50 "param"
               OpName %param_51 "param"
               OpName %leMaskBlock "leMaskBlock"
               OpMemberName %leMaskBlock 0 "verification"
               OpName %leMaskBuffer "leMaskBuffer"
               OpName %gl_SubgroupLeMask "gl_SubgroupLeMask"
               OpName %param_52 "param"
               OpName %param_53 "param"
               OpName %param_54 "param"
               OpName %param_55 "param"
               OpName %param_56 "param"
               OpName %param_57 "param"
               OpName %param_58 "param"
               OpName %ltMaskBlock "ltMaskBlock"
               OpMemberName %ltMaskBlock 0 "verification"
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
               OpDecorate %188 RelaxedPrecision
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %192 RelaxedPrecision
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
               OpDecorate %228 RelaxedPrecision
               OpDecorate %_runtimearr_uint_2 ArrayStride 4
               OpDecorate %invocationIdBlock Block
               OpMemberDecorate %invocationIdBlock 0 Offset 0
               OpDecorate %invocationIdBuffer Binding 3
               OpDecorate %invocationIdBuffer DescriptorSet 0
               OpDecorate %239 RelaxedPrecision
               OpDecorate %243 RelaxedPrecision
               OpDecorate %244 RelaxedPrecision
               OpDecorate %_runtimearr_uint_3 ArrayStride 4
               OpDecorate %eqMaskBlock Block
               OpMemberDecorate %eqMaskBlock 0 Offset 0
               OpDecorate %eqMaskBuffer Binding 4
               OpDecorate %eqMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupEqMask BuiltIn SubgroupEqMask
               OpDecorate %260 RelaxedPrecision
               OpDecorate %262 RelaxedPrecision
               OpDecorate %_runtimearr_uint_4 ArrayStride 4
               OpDecorate %geMaskBlock Block
               OpMemberDecorate %geMaskBlock 0 Offset 0
               OpDecorate %geMaskBuffer Binding 5
               OpDecorate %geMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupGeMask BuiltIn SubgroupGeMask
               OpDecorate %279 RelaxedPrecision
               OpDecorate %281 RelaxedPrecision
               OpDecorate %_runtimearr_uint_5 ArrayStride 4
               OpDecorate %gtMaskBlock Block
               OpMemberDecorate %gtMaskBlock 0 Offset 0
               OpDecorate %gtMaskBuffer Binding 6
               OpDecorate %gtMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupGtMask BuiltIn SubgroupGtMask
               OpDecorate %298 RelaxedPrecision
               OpDecorate %300 RelaxedPrecision
               OpDecorate %_runtimearr_uint_6 ArrayStride 4
               OpDecorate %leMaskBlock Block
               OpMemberDecorate %leMaskBlock 0 Offset 0
               OpDecorate %leMaskBuffer Binding 7
               OpDecorate %leMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupLeMask BuiltIn SubgroupLeMask
               OpDecorate %317 RelaxedPrecision
               OpDecorate %319 RelaxedPrecision
               OpDecorate %_runtimearr_uint_7 ArrayStride 4
               OpDecorate %ltMaskBlock Block
               OpMemberDecorate %ltMaskBlock 0 Offset 0
               OpDecorate %ltMaskBuffer Binding 8
               OpDecorate %ltMaskBuffer DescriptorSet 0
               OpDecorate %gl_SubgroupLtMask BuiltIn SubgroupLtMask
               OpDecorate %336 RelaxedPrecision
               OpDecorate %338 RelaxedPrecision
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
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
      %int_0 = OpConstant %int 0
       %true = OpConstantTrue %bool
     %uint_0 = OpConstant %uint 0
    %uint_32 = OpConstant %uint 32
     %uint_1 = OpConstant %uint 1
      %false = OpConstantFalse %bool
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
%invocationIdBlock = OpTypeStruct %_runtimearr_uint_2
%_ptr_StorageBuffer_invocationIdBlock = OpTypePointer StorageBuffer %invocationIdBlock
%invocationIdBuffer = OpVariable %_ptr_StorageBuffer_invocationIdBlock StorageBuffer
%_runtimearr_uint_3 = OpTypeRuntimeArray %uint
%eqMaskBlock = OpTypeStruct %_runtimearr_uint_3
%_ptr_StorageBuffer_eqMaskBlock = OpTypePointer StorageBuffer %eqMaskBlock
%eqMaskBuffer = OpVariable %_ptr_StorageBuffer_eqMaskBlock StorageBuffer
%_ptr_Input_v4uint = OpTypePointer Input %v4uint
%gl_SubgroupEqMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_4 = OpTypeRuntimeArray %uint
%geMaskBlock = OpTypeStruct %_runtimearr_uint_4
%_ptr_StorageBuffer_geMaskBlock = OpTypePointer StorageBuffer %geMaskBlock
%geMaskBuffer = OpVariable %_ptr_StorageBuffer_geMaskBlock StorageBuffer
%gl_SubgroupGeMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_5 = OpTypeRuntimeArray %uint
%gtMaskBlock = OpTypeStruct %_runtimearr_uint_5
%_ptr_StorageBuffer_gtMaskBlock = OpTypePointer StorageBuffer %gtMaskBlock
%gtMaskBuffer = OpVariable %_ptr_StorageBuffer_gtMaskBlock StorageBuffer
%gl_SubgroupGtMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_6 = OpTypeRuntimeArray %uint
%leMaskBlock = OpTypeStruct %_runtimearr_uint_6
%_ptr_StorageBuffer_leMaskBlock = OpTypePointer StorageBuffer %leMaskBlock
%leMaskBuffer = OpVariable %_ptr_StorageBuffer_leMaskBlock StorageBuffer
%gl_SubgroupLeMask = OpVariable %_ptr_Input_v4uint Input
%_runtimearr_uint_7 = OpTypeRuntimeArray %uint
%ltMaskBlock = OpTypeStruct %_runtimearr_uint_7
%_ptr_StorageBuffer_ltMaskBlock = OpTypePointer StorageBuffer %ltMaskBlock
%ltMaskBuffer = OpVariable %_ptr_StorageBuffer_ltMaskBlock StorageBuffer
%gl_SubgroupLtMask = OpVariable %_ptr_Input_v4uint Input
     %v3uint = OpTypeVector %uint 3
        %347 = OpConstantComposite %v3uint %uint_16 %uint_1 %uint_1
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
        %188 = OpLoad %uint %gl_SubgroupInvocationID
        %190 = OpLoad %uint %gl_SubgroupID
        %192 = OpLoad %uint %gl_SubgroupSize
        %193 = OpIMul %uint %190 %192
        %194 = OpIAdd %uint %188 %193
               OpStore %index %194
        %199 = OpLoad %uint %index
        %201 = OpLoad %uint %gl_NumSubgroups
        %202 = OpIEqual %bool %201 %uint_1
               OpStore %param_27 %202
        %204 = OpFunctionCall %uint %boolToUint_b1_ %param_27
        %206 = OpAccessChain %_ptr_StorageBuffer_uint %numSubgroupsBuffer %int_0 %199
               OpStore %206 %204
        %211 = OpLoad %uint %index
        %212 = OpLoad %uint %gl_SubgroupID
        %213 = OpUGreaterThanEqual %bool %212 %uint_0
               OpSelectionMerge %215 None
               OpBranchConditional %213 %214 %215
        %214 = OpLabel
        %216 = OpLoad %uint %gl_SubgroupID
        %217 = OpLoad %uint %gl_NumSubgroups
        %218 = OpULessThan %bool %216 %217
               OpBranch %215
        %215 = OpLabel
        %219 = OpPhi %bool %213 %5 %218 %214
               OpStore %param_28 %219
        %221 = OpFunctionCall %uint %boolToUint_b1_ %param_28
        %222 = OpAccessChain %_ptr_StorageBuffer_uint %subgroupIdBuffer %int_0 %211
               OpStore %222 %221
        %227 = OpLoad %uint %index
        %228 = OpLoad %uint %gl_SubgroupSize
        %230 = OpIEqual %bool %228 %uint_16
               OpStore %param_29 %230
        %232 = OpFunctionCall %uint %boolToUint_b1_ %param_29
        %233 = OpAccessChain %_ptr_StorageBuffer_uint %subgroupSizeBuffer %int_0 %227
               OpStore %233 %232
        %238 = OpLoad %uint %index
        %239 = OpLoad %uint %gl_SubgroupInvocationID
        %240 = OpUGreaterThanEqual %bool %239 %uint_0
               OpSelectionMerge %242 None
               OpBranchConditional %240 %241 %242
        %241 = OpLabel
        %243 = OpLoad %uint %gl_SubgroupInvocationID
        %244 = OpLoad %uint %gl_SubgroupSize
        %245 = OpULessThan %bool %243 %244
               OpBranch %242
        %242 = OpLabel
        %246 = OpPhi %bool %240 %215 %245 %241
               OpStore %param_30 %246
        %248 = OpFunctionCall %uint %boolToUint_b1_ %param_30
        %249 = OpAccessChain %_ptr_StorageBuffer_uint %invocationIdBuffer %int_0 %238
               OpStore %249 %248
        %254 = OpLoad %uint %index
        %258 = OpLoad %v4uint %gl_SubgroupEqMask
               OpStore %param_31 %258
        %260 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_32 %260
        %262 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_33 %262
               OpStore %param_34 %uint_0
               OpStore %param_35 %uint_1
               OpStore %param_36 %uint_0
        %266 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_31 %param_32 %param_33 %param_34 %param_35 %param_36
               OpStore %param_37 %266
        %268 = OpFunctionCall %uint %boolToUint_b1_ %param_37
        %269 = OpAccessChain %_ptr_StorageBuffer_uint %eqMaskBuffer %int_0 %254
               OpStore %269 %268
        %274 = OpLoad %uint %index
        %277 = OpLoad %v4uint %gl_SubgroupGeMask
               OpStore %param_38 %277
        %279 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_39 %279
        %281 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_40 %281
               OpStore %param_41 %uint_0
               OpStore %param_42 %uint_1
               OpStore %param_43 %uint_1
        %285 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_38 %param_39 %param_40 %param_41 %param_42 %param_43
               OpStore %param_44 %285
        %287 = OpFunctionCall %uint %boolToUint_b1_ %param_44
        %288 = OpAccessChain %_ptr_StorageBuffer_uint %geMaskBuffer %int_0 %274
               OpStore %288 %287
        %293 = OpLoad %uint %index
        %296 = OpLoad %v4uint %gl_SubgroupGtMask
               OpStore %param_45 %296
        %298 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_46 %298
        %300 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_47 %300
               OpStore %param_48 %uint_0
               OpStore %param_49 %uint_0
               OpStore %param_50 %uint_1
        %304 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_45 %param_46 %param_47 %param_48 %param_49 %param_50
               OpStore %param_51 %304
        %306 = OpFunctionCall %uint %boolToUint_b1_ %param_51
        %307 = OpAccessChain %_ptr_StorageBuffer_uint %gtMaskBuffer %int_0 %293
               OpStore %307 %306
        %312 = OpLoad %uint %index
        %315 = OpLoad %v4uint %gl_SubgroupLeMask
               OpStore %param_52 %315
        %317 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_53 %317
        %319 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_54 %319
               OpStore %param_55 %uint_1
               OpStore %param_56 %uint_1
               OpStore %param_57 %uint_0
        %323 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_52 %param_53 %param_54 %param_55 %param_56 %param_57
               OpStore %param_58 %323
        %325 = OpFunctionCall %uint %boolToUint_b1_ %param_58
        %326 = OpAccessChain %_ptr_StorageBuffer_uint %leMaskBuffer %int_0 %312
               OpStore %326 %325
        %331 = OpLoad %uint %index
        %334 = OpLoad %v4uint %gl_SubgroupLtMask
               OpStore %param_59 %334
        %336 = OpLoad %uint %gl_SubgroupSize
               OpStore %param_60 %336
        %338 = OpLoad %uint %gl_SubgroupInvocationID
               OpStore %param_61 %338
               OpStore %param_62 %uint_1
               OpStore %param_63 %uint_0
               OpStore %param_64 %uint_0
        %342 = OpFunctionCall %bool %checkMask_vu4_u1_u1_u1_u1_u1_ %param_59 %param_60 %param_61 %param_62 %param_63 %param_64
               OpStore %param_65 %342
        %344 = OpFunctionCall %uint %boolToUint_b1_ %param_65
        %345 = OpAccessChain %_ptr_StorageBuffer_uint %ltMaskBuffer %int_0 %331
               OpStore %345 %344
               OpReturn
               OpFunctionEnd
%boolToUint_b1_ = OpFunction %uint None %9
      %value = OpFunctionParameter %_ptr_Function_bool
         %12 = OpLabel
         %35 = OpLoad %bool %value
         %39 = OpSelect %int %35 %int_1 %int_0
         %40 = OpBitcast %uint %39
               OpReturnValue %40
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
         %ok = OpVariable %_ptr_Function_bool Function
          %i = OpVariable %_ptr_Function_uint Function
        %bit = OpVariable %_ptr_Function_uint Function
        %idx = OpVariable %_ptr_Function_uint Function
               OpStore %ok %true
               OpStore %i %uint_0
               OpBranch %47
         %47 = OpLabel
               OpLoopMerge %49 %50 None
               OpBranch %51
         %51 = OpLabel
         %52 = OpLoad %uint %i
         %54 = OpULessThan %bool %52 %uint_32
               OpBranchConditional %54 %48 %49
         %48 = OpLabel
         %56 = OpLoad %uint %mask
         %57 = OpLoad %uint %i
         %58 = OpShiftRightLogical %uint %56 %57
         %60 = OpBitwiseAnd %uint %58 %uint_1
               OpStore %bit %60
         %62 = OpLoad %uint %offset
         %63 = OpLoad %uint %i
         %64 = OpIAdd %uint %62 %63
               OpStore %idx %64
         %65 = OpLoad %uint %idx
         %66 = OpLoad %uint %validBits
         %67 = OpULessThan %bool %65 %66
               OpSelectionMerge %69 None
               OpBranchConditional %67 %68 %100
         %68 = OpLabel
         %70 = OpLoad %uint %idx
         %71 = OpLoad %uint %bitIndex
         %72 = OpULessThan %bool %70 %71
         %73 = OpLoad %uint %bit
         %74 = OpLoad %uint %expectedLess
         %75 = OpINotEqual %bool %73 %74
         %76 = OpLogicalAnd %bool %72 %75
               OpSelectionMerge %78 None
               OpBranchConditional %76 %77 %80
         %77 = OpLabel
               OpStore %ok %false
               OpBranch %78
         %80 = OpLabel
         %81 = OpLoad %uint %idx
         %82 = OpLoad %uint %bitIndex
         %83 = OpIEqual %bool %81 %82
         %84 = OpLoad %uint %bit
         %85 = OpLoad %uint %expectedEqual
         %86 = OpINotEqual %bool %84 %85
         %87 = OpLogicalAnd %bool %83 %86
               OpSelectionMerge %89 None
               OpBranchConditional %87 %88 %90
         %88 = OpLabel
               OpStore %ok %false
               OpBranch %89
         %90 = OpLabel
         %91 = OpLoad %uint %idx
         %92 = OpLoad %uint %bitIndex
         %93 = OpUGreaterThan %bool %91 %92
         %94 = OpLoad %uint %bit
         %95 = OpLoad %uint %expectedGreater
         %96 = OpINotEqual %bool %94 %95
         %97 = OpLogicalAnd %bool %93 %96
               OpSelectionMerge %99 None
               OpBranchConditional %97 %98 %99
         %98 = OpLabel
               OpStore %ok %false
               OpBranch %99
         %99 = OpLabel
               OpBranch %89
         %89 = OpLabel
               OpBranch %78
         %78 = OpLabel
               OpBranch %69
        %100 = OpLabel
        %101 = OpLoad %uint %bit
        %102 = OpINotEqual %bool %101 %uint_0
               OpSelectionMerge %104 None
               OpBranchConditional %102 %103 %104
        %103 = OpLabel
               OpStore %ok %false
               OpBranch %104
        %104 = OpLabel
               OpBranch %69
         %69 = OpLabel
               OpBranch %50
         %50 = OpLabel
        %105 = OpLoad %uint %i
        %106 = OpIAdd %uint %105 %int_1
               OpStore %i %106
               OpBranch %47
         %49 = OpLabel
        %107 = OpLoad %bool %ok
               OpReturnValue %107
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
        %111 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_0
        %112 = OpLoad %uint %111
               OpStore %param %112
               OpStore %param_0 %uint_0
        %115 = OpLoad %uint %validBits_0
               OpStore %param_1 %115
        %117 = OpLoad %uint %bitIndex_0
               OpStore %param_2 %117
        %119 = OpLoad %uint %expectedLess_0
               OpStore %param_3 %119
        %121 = OpLoad %uint %expectedEqual_0
               OpStore %param_4 %121
        %123 = OpLoad %uint %expectedGreater_0
               OpStore %param_5 %123
        %124 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param %param_0 %param_1 %param_2 %param_3 %param_4 %param_5
               OpSelectionMerge %126 None
               OpBranchConditional %124 %125 %126
        %125 = OpLabel
        %128 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_1
        %129 = OpLoad %uint %128
               OpStore %param_6 %129
               OpStore %param_7 %uint_32
        %132 = OpLoad %uint %validBits_0
               OpStore %param_8 %132
        %134 = OpLoad %uint %bitIndex_0
               OpStore %param_9 %134
        %136 = OpLoad %uint %expectedLess_0
               OpStore %param_10 %136
        %138 = OpLoad %uint %expectedEqual_0
               OpStore %param_11 %138
        %140 = OpLoad %uint %expectedGreater_0
               OpStore %param_12 %140
        %141 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param_6 %param_7 %param_8 %param_9 %param_10 %param_11 %param_12
               OpBranch %126
        %126 = OpLabel
        %142 = OpPhi %bool %124 %34 %141 %125
               OpSelectionMerge %144 None
               OpBranchConditional %142 %143 %144
        %143 = OpLabel
        %148 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_2
        %149 = OpLoad %uint %148
               OpStore %param_13 %149
               OpStore %param_14 %uint_64
        %152 = OpLoad %uint %validBits_0
               OpStore %param_15 %152
        %154 = OpLoad %uint %bitIndex_0
               OpStore %param_16 %154
        %156 = OpLoad %uint %expectedLess_0
               OpStore %param_17 %156
        %158 = OpLoad %uint %expectedEqual_0
               OpStore %param_18 %158
        %160 = OpLoad %uint %expectedGreater_0
               OpStore %param_19 %160
        %161 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param_13 %param_14 %param_15 %param_16 %param_17 %param_18 %param_19
               OpBranch %144
        %144 = OpLabel
        %162 = OpPhi %bool %142 %126 %161 %143
               OpSelectionMerge %164 None
               OpBranchConditional %162 %163 %164
        %163 = OpLabel
        %168 = OpAccessChain %_ptr_Function_uint %mask_0 %uint_3
        %169 = OpLoad %uint %168
               OpStore %param_20 %169
               OpStore %param_21 %uint_96
        %172 = OpLoad %uint %validBits_0
               OpStore %param_22 %172
        %174 = OpLoad %uint %bitIndex_0
               OpStore %param_23 %174
        %176 = OpLoad %uint %expectedLess_0
               OpStore %param_24 %176
        %178 = OpLoad %uint %expectedEqual_0
               OpStore %param_25 %178
        %180 = OpLoad %uint %expectedGreater_0
               OpStore %param_26 %180
        %181 = OpFunctionCall %bool %checkMaskComponent_u1_u1_u1_u1_u1_u1_u1_ %param_20 %param_21 %param_22 %param_23 %param_24 %param_25 %param_26
               OpBranch %164
        %164 = OpLabel
        %182 = OpPhi %bool %162 %144 %181 %163
               OpReturnValue %182
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host allocates nine host-visible storage buffers. Each buffer has one `uint32_t` entry per local invocation and starts with zeroes. A descriptor set binds them at bindings 0 through 8.
- The host creates the compute pipeline with `VkPipelineShaderStageRequiredSubgroupSizeCreateInfo`. In `dgc_pipeline` modes, `DGCComputePipelineExt` also adds `VK_PIPELINE_CREATE_2_INDIRECT_BINDABLE_BIT_EXT`, and an execution set stores the pipeline at index `0`.
- `IndirectCommandsLayoutBuilderExt` adds a compute pipeline token only for DGC pipeline modes. It then adds a dispatch token. The dispatch token data is `(1, 1, 1)`, so one generated sequence launches one workgroup with the selected local size.
- `PreprocessBufferExt` queries the generated-command memory requirements for one sequence and creates a device-addressable preprocess buffer when the query reports a nonzero size. The generated command buffer is also device-addressable and contains the optional pipeline index followed by the dispatch dimensions.
- The command buffer binds the descriptor set and the selected pipeline, calls `cmdExecuteGeneratedCommandsEXT` with `VK_FALSE`, and inserts a memory barrier from shader writes to host reads. The selected queue then completes the submission before the host reads results.
- The host copies each output buffer into a temporary vector and checks every entry. A value other than `1` produces a log message containing its binding and position. Any mismatch returns `tcu::TestStatus::fail`; only nine buffers with all entries equal to `1` return pass.

The EXT execution path follows the Vulkan device-generated commands model: preprocessing prepares state for the layout, and execution interprets the token stream. The normal path still uses the generated dispatch layout, but it binds the ordinary compute pipeline before execution and leaves the pipeline token and execution set unused.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `normal_pipeline` | Required subgroup-size or subgroup-built-in behavior in the normal compute pipeline path; common shader, descriptor, or result-readback validation |
| `dgc_pipeline` | The EXT execution-set, pipeline token, generated dispatch, preprocessing, or DGC compute pipeline path; common subgroup-built-in validation |
| `normal_pipeline_cq` | The normal pipeline path when submitted to the compute queue; queue selection or common subgroup-built-in validation |
| `dgc_pipeline_cq` | The DGC pipeline and generated-dispatch path when submitted to the compute queue; queue selection or common subgroup-built-in validation |

### Cause Analysis

#### Required subgroup size and subgroup built-ins

**Possible failure symptoms:** One or more entries in the nine output buffers contains `0`. The log identifies the output binding and invocation position. The failing check can indicate an unexpected subgroup count, ID, size, invocation ID, or mask bit pattern.

**Possible implementation causes:** The compute shader may observe a subgroup arrangement that does not satisfy the requested size, or the implementation may expose incorrect subgroup built-in or ballot-mask values. The source establishes the expected relationships from `totalInvocations` and `subgroupSize`; a specific driver or hardware cause needs investigation against the Vulkan subgroup and required-subgroup-size rules.

#### Normal compute pipeline path

**Possible failure symptoms:** A `normal_pipeline` or `normal_pipeline_cq` case fails while the result scan reports a subgroup check or mask check other than `1`.

**Possible implementation causes:** The normal compute pipeline may apply the required subgroup-size state incorrectly, or the generated dispatch may reach a pipeline state that does not match the shader used to build the outputs. Descriptor binding, shader compilation, synchronization, and host readback also affect the same result scan, so source-level or API capture is needed to separate them.

#### EXT execution set and generated command path

**Possible failure symptoms:** A `dgc_pipeline` or `dgc_pipeline_cq` case fails with a zero in an output buffer after `cmdExecuteGeneratedCommandsEXT` completes, or the command cannot execute successfully.

**Possible implementation causes:** The execution set may select the wrong pipeline, the pipeline token or dispatch token may be interpreted incorrectly, or preprocessing may produce incorrect generated-command state. The pipeline is created as indirect-bindable and the execution set contains it at index `0`; failures in those EXT operations need investigation in the implementation and validation layers.

#### Compute queue submission

**Possible failure symptoms:** A case with `_cq` fails while the corresponding default-queue case passes, or the submission cannot complete on the selected queue.

**Possible implementation causes:** The compute queue or queue-family selection may not support the required compute and generated-command operations, or queue synchronization may expose a result before shader writes become visible to the host. The test obtains the compute queue before execution and uses a shader-write to host-read barrier, so a remaining failure needs queue and synchronization investigation.

## Case Pruning

### Requirement-based pruning

- `checkSubgroupSupport` rejects devices whose equivalent Vulkan API version is below 1.3.
- The EXT DGC support check requires compute-stage generated-command support. DGC pipeline cases require compute pipeline binding support; normal pipeline cases use the basic support path.
- The requested subgroup size must be a supported power of two within `minSubgroupSize` and `maxSubgroupSize`.
- The device must advertise required subgroup-size support for `VK_SHADER_STAGE_COMPUTE_BIT`.
- Cases with `_cq` require a usable compute queue. A missing queue produces `NotSupportedError` before execution.

These checks classify unsupported configurations as not supported rather than as failed subgroup results.

### Design-based pruning

The registration loops use the same ordered values for workgroup and subgroup size. When `subgroupSize > workgroupSize`, the inner loop breaks, so the test registers only pairs in which the requested subgroup size does not exceed the workgroup size. This avoids cases where `totalInvocations` cannot be divided into the requested subgroup arrangement. Each retained pair still covers both pipeline modes and both queue modes.

## Key Takeaways

- The shader checks subgroup IDs, sizes, counts, and five ballot-mask relationships for every invocation, rather than checking one aggregate value.
- The EXT cases test pipeline selection and dispatch generation through `VK_EXT_device_generated_commands`; the normal cases provide the same subgroup workload without an execution-set pipeline token.
- The `_cq` suffix changes queue selection, while the workgroup and subgroup suffixes change the expected subgroup arithmetic.
- Unsupported Vulkan versions, feature combinations, subgroup sizes, and queue choices are pruned before execution. Executed cases fail only when the host finds a result entry other than `1`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `BuiltinParams` and `checkSubgroupSupport` | [vktDGCComputeSubgroupTestsExt.cpp#L49-L84](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L49-L84) | Defines the four case dimensions and support gates. |
| `builtinVerificationProgram` | [vktDGCComputeSubgroupTestsExt.cpp#L86-L174](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L86-L174) | Generates the subgroup built-in and mask checks. |
| `verifyBuiltins` resource and pipeline setup | [vktDGCComputeSubgroupTestsExt.cpp#L176-L315](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L176-L315) | Creates output buffers, pipelines, tokens, preprocessing state, and execution commands. |
| `verifyBuiltins` result scan | [vktDGCComputeSubgroupTestsExt.cpp#L325-L351](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L325-L351) | Maps each non-`1` result to a logged failure and final test status. |
| `createDGCComputeSubgroupTestsExt` | [vktDGCComputeSubgroupTestsExt.cpp#L356-L384](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L356-L384) | Registers `subgroups`, `builtins`, the exact case-name matrix, and the size pruning rule. |
| `checkDGCExtComputeSupport` | [vktDGCUtilExt.cpp#L68-L75](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L68-L75) | Maps the selected DGC compute mode to EXT compute-stage support checks. |
| `PreprocessBufferExt` | [vktDGCUtilExt.cpp#L724-L803](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L724-L803) | Queries preprocess memory requirements and creates the device-addressable buffer. |
| `DGCComputePipelineExt` | [vktDGCUtilExt.cpp#L818-L878](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L818-L878) | Adds required subgroup size and the indirect-bindable pipeline creation flag. |
| EXT generated-command execution model | [device-generated commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines execution sets, token layouts, preprocessing, and generated command execution. |
| Mustpass registration | [dgc.txt#L448-L487](../../../mustpass/main/vk-default/dgc.txt#L448-L487) | Lists the registered EXT test case identifiers. |
