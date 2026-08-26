## Overview

**Core question:** Does Vulkan preserve the identity and behavior of helper fragment invocations when a fragment is demoted, including subgroup quad operations, volatile helper-invocation queries, atomics, and the Vulkan memory model?

This page documents [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L40-L112). The implementation registers three Amber test cases under `shader_invocation`; the Amber scripts perform the graphics workload, verification compute dispatch, and final buffer comparison. The family is render-pass-only and is omitted from Vulkan SC builds because the dispatcher excludes Amber tests there.

## Background Knowledge

- A helper invocation is a fragment invocation retained for derivative, quad, or related shader operations but excluded from normal side effects such as framebuffer writes. `demote`/`OpDemoteToHelperInvocation` changes an invocation's status without terminating shader execution.
- `helperInvocationEXT()` is the extension function spelling used by the first case. The two `TARGET_ENV spv1.6` cases use the GLSL built-in `gl_HelperInvocation`; this does not imply a core replacement for `OpIsHelperInvocationEXT`, which the C++ support check explicitly says was not promoted to core.
- Subgroup quad broadcasts read values from the four lanes of a 2x2 fragment quad. The scripts deliberately query the quad before and after demotion so helper lanes must contribute the specified helper value (`8.0`) rather than their ordinary rounded input.
- The fragment shader also performs an atomic add after the first demotion. The compute verification shader accepts only combinations of color masks and atomic values that are consistent with the allowed initial helper status and subsequent demotions.
- The Amber runner creates the render target, graphics and compute pipelines, submits the draw and verification work, and evaluates the script's `EXPECT` command. The C++ file supplies registration and support callbacks; it does not implement a separate host-side image algorithm.

## Registration Hierarchy

```text
draw.renderpass.shader_invocation
├── helper_invocation
├── helper_invocation_volatile
└── helper_invocation_volatile_mem_model
```

`shader_invocation` is the exact group name passed to [`createTestGroup`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L109-L112). The three exact child names and their Amber files are the entries in the `cases` array at [`createTests`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L81-L104). The parent dispatcher adds this group only when `!useDynamicRendering`, and only outside `CTS_USES_VULKANSC`, at [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117). Thus the full standard path is `draw.renderpass.shader_invocation.<case>`.

## Parameter Dimensions and Observed Values

| Case | Amber file | Shader spelling / environment | Additional support gate |
|---|---|---|---|
| `helper_invocation` | [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber) | `helperInvocationEXT()`; `TARGET_ENV spv1.3` | `VK_EXT_shader_demote_to_helper_invocation` |
| `helper_invocation_volatile` | [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber) | `gl_HelperInvocation`; `TARGET_ENV spv1.6` | SPIR-V 1.6 availability is checked by the framework |
| `helper_invocation_volatile_mem_model` | [`helper_invocation_volatile_mem_model.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile_mem_model.amber) | `gl_HelperInvocation`; `TARGET_ENV spv1.6`; `#pragma use_vulkan_memory_model` | `vulkanMemoryModel` (and framework SPIR-V 1.6 checking) |

All three cases require subgroup quad operations and the `shaderDemoteToHelperInvocation` feature. The exact checks and unsupported messages are in [`checkSupport`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L47-L63). Unsupported requirements raise `NotSupportedError`; they are not test failures.

## Behavior Parameters

The primary behavioral axis is the registered case and its shader environment.

### `helper_invocation`: extension spelling

Uses `helperInvocationEXT()` with the extension environment.

### `helper_invocation_volatile`: SPIR-V 1.6-targeted volatile query

Uses `gl_HelperInvocation` with SPIR-V 1.6.

### `helper_invocation_volatile_mem_model`: Vulkan memory model

Adds the Vulkan memory model pragma to the volatile helper-invocation path.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.shader_invocation.helper_invocation
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `helper_invocation` | Selects the extension variant, whose fragment shader uses `helperInvocationEXT()` and targets SPIR-V 1.3. |
| 2x2 render pass with four alpha keys | Gives one fragment to each quad lane and makes each lane's helper status observable through the three masks and its atomic counter. |

#### Purpose

The fragment shader checks that a demoted invocation remains available to subgroup quad operations while helper-invocation queries return the helper value. It also checks that demotion does not prevent the per-lane atomic side effect; a verification compute shader accepts any result consistent with the allowed initial helper statuses and the two later demotion points.

#### Structural Design

| Phase | Fragment-shader operation | Observable value |
|------|----------------------------|------------------|
| 1 | Read `alpha[linear_coord]`; query helper status and broadcast the lane value across the quad. | `mask0` |
| 2 | Demote lanes with `fract(alpha_value) < 0.5`; repeat the helper substitution and quad broadcasts. | `mask1` |
| 3 | `atomicAdd(atomics[linear_coord], 101u)`; demote lane 3 or an invocation whose returned counter exceeds 1000; repeat the broadcasts. | `mask2` and `atomics[]` |
| 4 | Store `vec4(1.0, mask0, mask1, mask2)` to location 0. | Render-pass color image |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_demote_to_helper_invocation : require
#extension GL_KHR_shader_subgroup_quad : require

/// Binding 0 is the read-only storage buffer containing four float inputs; the 2x2 draw maps one input to each fragment.
layout(binding = 0) readonly buffer Block0
{
    float alpha[];
};

/// Binding 1 is the writable storage buffer containing four uint atomics, one counter per fragment coordinate.
layout(binding = 1) buffer Block1
{
    uint atomics[];
};

/// The render-pass color attachment is an R32G32B32A32_SFLOAT 2x2 framebuffer; x stores a fixed validity marker and
/// y/z/w store the three quad-broadcast masks observed before and after the two demotion points.
layout(location = 0) out vec4 color;

/// A helper lane contributes 8.0 instead of its rounded input. Quad broadcasts then encode all four lanes with
/// decimal-place weights 1, 10, 100, and 1000, making the helper status visible in the output mask.
float build_alpha_shuffle(float v)
{
    v = (helperInvocationEXT() ? 8.0 : roundEven(v));
    vec4 helpers;
    helpers.x = subgroupQuadBroadcast(v, 0u);
    helpers.y = subgroupQuadBroadcast(v, 1u);
    helpers.z = subgroupQuadBroadcast(v, 2u);
    helpers.w = subgroupQuadBroadcast(v, 3u);

    return dot(helpers, vec4(1, 10, 100, 1000));
}

void main()
{
    /// The integer coordinate is row-major for the 2x2 framebuffer and selects both the input and atomic element.
    ivec2 coord = ivec2(gl_FragCoord.xy);
    int linear_coord = coord.y * 2 + coord.x;

    float alpha_value = alpha[linear_coord];
    float mask0 = build_alpha_shuffle(alpha_value);

    // Lane 1 and 2 should be nuked by this.
    if (fract(alpha_value) < 0.5)
    {
        demote;
    }

    float mask1 = build_alpha_shuffle(alpha_value);
    uint last_value = 0u;

    /// Each invocation adds 101 to its own counter; the returned pre-add value drives the second demotion condition.
    last_value = atomicAdd(atomics[linear_coord], 101u);

    if (linear_coord == 3 || last_value > 1000)
    {
        demote;
    }

    float mask2 = build_alpha_shuffle(alpha_value);

    color = vec4(1.0, mask0, mask1, mask2);
}
```

#### Additional Info

- The Amber host binds `alpha_keys` and `atomics` as storage buffers at descriptor bindings 0 and 1, binds the color buffer as a 2x2 `R32G32B32A32_SFLOAT` attachment, then dispatches the verification compute shader once; these bindings are fixed across the three cases.
- The volatile variant changes only the helper query spelling to `gl_HelperInvocation` and targets `spv1.6`; the memory-model variant additionally emits `#pragma use_vulkan_memory_model`. The demotion, quad-broadcast, atomic, and verification logic remain otherwise identical.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Helper query variant | `helper_invocation` emits `helperInvocationEXT()`; the two core variants emit `gl_HelperInvocation`. | [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber#L18-L37); [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber#L18-L37) |
| SPIR-V target | The representative extension shader targets `spv1.3`; both volatile shaders target `spv1.6`. | [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber#L18-L20); [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber#L18-L20) |
| Vulkan memory model | Only `helper_invocation_volatile_mem_model` adds `#pragma use_vulkan_memory_model`; it does not change the GLSL control flow. | [`helper_invocation_volatile_mem_model.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile_mem_model.amber#L18-L22) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 124
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformQuad
               OpCapability DemoteToHelperInvocation
               OpExtension "SPV_EXT_demote_to_helper_invocation"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_demote_to_helper_invocation"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpSourceExtension "GL_KHR_shader_subgroup_quad"
               OpName %main "main"
               OpName %build_alpha_shuffle_f1_ "build_alpha_shuffle(f1;"
               OpName %v "v"
               OpName %helpers "helpers"
               OpName %coord "coord"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %linear_coord "linear_coord"
               OpName %alpha_value "alpha_value"
               OpName %Block0 "Block0"
               OpMemberName %Block0 0 "alpha"
               OpName %_ ""
               OpName %mask0 "mask0"
               OpName %param "param"
               OpName %mask1 "mask1"
               OpName %param_0 "param"
               OpName %last_value "last_value"
               OpName %Block1 "Block1"
               OpMemberName %Block1 0 "atomics"
               OpName %__0 ""
               OpName %mask2 "mask2"
               OpName %param_1 "param"
               OpName %color "color"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %Block0 Block
               OpMemberDecorate %Block0 0 NonWritable
               OpMemberDecorate %Block0 0 Offset 0
               OpDecorate %_ NonWritable
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Block1 Block
               OpMemberDecorate %Block1 0 Offset 0
               OpDecorate %__0 Binding 1
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
          %8 = OpTypeFunction %float %_ptr_Function_float
       %bool = OpTypeBool
    %float_8 = OpConstant %float 8
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
     %uint_3 = OpConstant %uint 3
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
    %float_1 = OpConstant %float 1
   %float_10 = OpConstant %float 10
  %float_100 = OpConstant %float 100
 %float_1000 = OpConstant %float 1000
         %47 = OpConstantComposite %v4float %float_1 %float_10 %float_100 %float_1000
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
    %v2float = OpTypeVector %float 2
%_ptr_Function_int = OpTypePointer Function %int
      %int_2 = OpConstant %int 2
%_runtimearr_float = OpTypeRuntimeArray %float
     %Block0 = OpTypeStruct %_runtimearr_float
%_ptr_StorageBuffer_Block0 = OpTypePointer StorageBuffer %Block0
          %_ = OpVariable %_ptr_StorageBuffer_Block0 StorageBuffer
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
  %float_0_5 = OpConstant %float 0.5
%_ptr_Function_uint = OpTypePointer Function %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
     %Block1 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Block1 = OpTypePointer StorageBuffer %Block1
        %__0 = OpVariable %_ptr_StorageBuffer_Block1 StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
   %uint_101 = OpConstant %uint 101
      %int_3 = OpConstant %int 3
  %uint_1000 = OpConstant %uint 1000
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
      %coord = OpVariable %_ptr_Function_v2int Function
%linear_coord = OpVariable %_ptr_Function_int Function
%alpha_value = OpVariable %_ptr_Function_float Function
      %mask0 = OpVariable %_ptr_Function_float Function
      %param = OpVariable %_ptr_Function_float Function
      %mask1 = OpVariable %_ptr_Function_float Function
    %param_0 = OpVariable %_ptr_Function_float Function
 %last_value = OpVariable %_ptr_Function_uint Function
      %mask2 = OpVariable %_ptr_Function_float Function
    %param_1 = OpVariable %_ptr_Function_float Function
         %58 = OpLoad %v4float %gl_FragCoord
         %59 = OpVectorShuffle %v2float %58 %58 0 1
         %60 = OpConvertFToS %v2int %59
               OpStore %coord %60
         %63 = OpAccessChain %_ptr_Function_int %coord %uint_1
         %64 = OpLoad %int %63
         %66 = OpIMul %int %64 %int_2
         %67 = OpAccessChain %_ptr_Function_int %coord %uint_0
         %68 = OpLoad %int %67
         %69 = OpIAdd %int %66 %68
               OpStore %linear_coord %69
         %76 = OpLoad %int %linear_coord
         %78 = OpAccessChain %_ptr_StorageBuffer_float %_ %int_0 %76
         %79 = OpLoad %float %78
               OpStore %alpha_value %79
         %82 = OpLoad %float %alpha_value
               OpStore %param %82
         %83 = OpFunctionCall %float %build_alpha_shuffle_f1_ %param
               OpStore %mask0 %83
         %84 = OpLoad %float %alpha_value
         %85 = OpExtInst %float %1 Fract %84
         %87 = OpFOrdLessThan %bool %85 %float_0_5
               OpSelectionMerge %89 None
               OpBranchConditional %87 %88 %89
         %88 = OpLabel
               OpDemoteToHelperInvocation
               OpBranch %89
         %89 = OpLabel
         %92 = OpLoad %float %alpha_value
               OpStore %param_0 %92
         %93 = OpFunctionCall %float %build_alpha_shuffle_f1_ %param_0
               OpStore %mask1 %93
               OpStore %last_value %uint_0
        %100 = OpLoad %int %linear_coord
        %102 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %100
        %104 = OpAtomicIAdd %uint %102 %uint_1 %uint_0 %uint_101
               OpStore %last_value %104
        %105 = OpLoad %int %linear_coord
        %107 = OpIEqual %bool %105 %int_3
        %108 = OpLoad %uint %last_value
        %110 = OpUGreaterThan %bool %108 %uint_1000
        %111 = OpLogicalOr %bool %107 %110
               OpSelectionMerge %113 None
               OpBranchConditional %111 %112 %113
        %112 = OpLabel
               OpDemoteToHelperInvocation
               OpBranch %113
        %113 = OpLabel
        %116 = OpLoad %float %alpha_value
               OpStore %param_1 %116
        %117 = OpFunctionCall %float %build_alpha_shuffle_f1_ %param_1
               OpStore %mask2 %117
        %120 = OpLoad %float %mask0
        %121 = OpLoad %float %mask1
        %122 = OpLoad %float %mask2
        %123 = OpCompositeConstruct %v4float %float_1 %120 %121 %122
               OpStore %color %123
               OpReturn
               OpFunctionEnd
%build_alpha_shuffle_f1_ = OpFunction %float None %8
          %v = OpFunctionParameter %_ptr_Function_float
         %11 = OpLabel
         %14 = OpVariable %_ptr_Function_float Function
    %helpers = OpVariable %_ptr_Function_v4float Function
         %13 = OpIsHelperInvocationEXT %bool
               OpSelectionMerge %16 None
               OpBranchConditional %13 %15 %18
         %15 = OpLabel
               OpStore %14 %float_8
               OpBranch %16
         %18 = OpLabel
         %19 = OpLoad %float %v
         %20 = OpExtInst %float %1 RoundEven %19
               OpStore %14 %20
               OpBranch %16
         %16 = OpLabel
         %21 = OpLoad %float %14
               OpStore %v %21
         %25 = OpLoad %float %v
         %29 = OpGroupNonUniformQuadBroadcast %float %uint_3 %25 %uint_0
         %30 = OpAccessChain %_ptr_Function_float %helpers %uint_0
               OpStore %30 %29
         %31 = OpLoad %float %v
         %33 = OpGroupNonUniformQuadBroadcast %float %uint_3 %31 %uint_1
         %34 = OpAccessChain %_ptr_Function_float %helpers %uint_1
               OpStore %34 %33
         %35 = OpLoad %float %v
         %37 = OpGroupNonUniformQuadBroadcast %float %uint_3 %35 %uint_2
         %38 = OpAccessChain %_ptr_Function_float %helpers %uint_2
               OpStore %38 %37
         %39 = OpLoad %float %v
         %40 = OpGroupNonUniformQuadBroadcast %float %uint_3 %39 %uint_3
         %41 = OpAccessChain %_ptr_Function_float %helpers %uint_3
               OpStore %41 %40
         %42 = OpLoad %v4float %helpers
         %48 = OpDot %float %42 %47
               OpReturnValue %48
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

```text
create shader_invocation group
  -> create one Amber test case per caseDef entry
  -> run a 2x2 graphics draw
  -> run verification compute shader
  -> enumerate allowed helper-status/mask/atomic combinations
  -> write results[0] = all-ones only for a matching combination
  -> EXPECT results EQ_BUFFER ref_buffer
```

The verification compute shader loads the first pixel and the three remaining framebuffer pixels, reconstructs all 16 possible initial helper-status combinations, derives the expected `mask0`, `mask1`, `mask2`, and atomic values, and marks `results[0]` as `(1,1,1,1)` when the observed values match one allowed combination. The remaining result elements are the captured pixels. `ref_buffer` is sixteen float ones, so [`EXPECT results EQ_BUFFER ref_buffer`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber#L179-L193) requires every result element to equal one. The corresponding final checks are present in the volatile and memory-model scripts at their respective `EXPECT` lines.

A failure means the observed helper status, quad broadcast result, demotion behavior, atomic side effect, memory-model behavior, or Amber resource/submission path did not satisfy any allowed combination. It does not by itself identify whether the fault is shader compilation, subgroup execution, demotion lowering, atomic visibility, or image/buffer handling.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible implementation cause(s) |
|---|---|
| `helper_invocation` | Extension demotion, helper query, subgroup quad behavior, or Amber validation. |
| `helper_invocation_volatile` | SPIR-V 1.6 helper query, volatile behavior, demotion, or validation. |
| `helper_invocation_volatile_mem_model` | Vulkan memory model, atomic visibility, helper behavior, or validation. |

### Cause Analysis

#### Helper invocation and demotion

**Possible failure symptoms:** The observed masks, atomic values, or result buffer do not match an allowed helper-status combination.

**Possible implementation causes:** Shader compilation, demotion lowering, subgroup execution, atomic visibility, memory model behavior, or Amber resource handling.

## Case Pruning

### Requirement-based pruning

- Missing `VK_SUBGROUP_FEATURE_QUAD_BIT` causes `NotSupportedError` for every case.
- Missing `shaderDemoteToHelperInvocation` causes `NotSupportedError` for every case.
- Missing `VK_EXT_shader_demote_to_helper_invocation` affects only `helper_invocation`.
- Missing `vulkanMemoryModel` affects only `helper_invocation_volatile_mem_model`.
- The `CORE` and `CORE_MEM_MODEL` test types depend on SPIR-V 1.6; the source explicitly notes that this requirement is checked automatically. The source also states that `OpIsHelperInvocationEXT` was not promoted to core.

### Design-based pruning

- The family is not registered below dynamic-rendering roots because the parent calls it only when `useDynamicRendering` is false. It is also excluded under `CTS_USES_VULKANSC`.

## Key Takeaways

- The exact family is `draw.renderpass.shader_invocation` with three Amber leaves: `helper_invocation`, `helper_invocation_volatile`, and `helper_invocation_volatile_mem_model`.
- All cases exercise a 2x2 fragment quad, two demotion points, subgroup quad broadcasts, and atomic side effects.
- The first case uses `helperInvocationEXT()`; the latter two use `gl_HelperInvocation` in SPIR-V 1.6-targeted shaders, with the third enabling the Vulkan memory model. None documents a core replacement for `OpIsHelperInvocationEXT`.
- Amber's verification compute shader accepts the complete set of allowed helper-status outcomes and requires an all-ones result buffer.
- Support rejection is distinct from a failing `EXPECT` comparison.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Test type enum and support callbacks | [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L40-L79) |
| Exact case names, Amber directory, and callback binding | [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L81-L105) |
| Group creation | [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L109-L112) |
| Public declaration | [`vktDrawShaderInvocationTests.hpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.hpp#L27-L39) |
| Render-pass/Vulkan-SC registration gate | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L120) |
| Extension shader and verification | [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber) |
| SPIR-V 1.6 volatile shader and verification | [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber) |
| Vulkan memory-model shader and verification | [`helper_invocation_volatile_mem_model.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile_mem_model.amber) |
