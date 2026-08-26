## Overview

[`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L20-L28) implements the `glsl.shader_expect_assume` group for `VK_KHR_shader_expect_assume`. It generates GLSL using the `SPV_KHR_expect_assume` intrinsics, runs each case through a vertex, fragment, or compute pipeline, and checks a two-word result for each of 32 elements. The public factory is [`createShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1516-L1519).

The group is added to the GLSL package only in non-Vulkan-SC builds ([registration](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)). This page describes source-defined coverage and behavior; it does not claim that the cases were run on the current host.

**Core question:** Do `expectKHR` and `assumeTrueKHR` produce the intended result when their operands come from constants, specialization constants, push constants, or storage buffers, across vertex, fragment, and compute shader execution?

## Background Knowledge

- `VK_KHR_shader_expect_assume` exposes the SPIR-V `OpExpectKHR` and `OpAssumeTrueKHR` operations. The GLSL test reaches them through `GL_EXT_spirv_intrinsics` declarations for `SPV_KHR_expect_assume`.
- `expectKHR` takes a value and an expected value and returns a value of the same data type. The test uses that result to select between an expected value and a deliberately wrong value.
- `assumeTrueKHR` takes a boolean condition and is emitted before the shader writes the verification value. The test observes the resulting value rather than treating the assumption as a host-side assertion.
- Operand sourcing is part of the coverage: ordinary constants, specialization constants, push constants, and stage-indexed storage-buffer elements exercise different interfaces between host setup and generated shader code.
- Storage-buffer vectors use std430-compatible element layout. A three-component element has a four-component stride in the host input initialization, while other widths use their channel count as the stride ([input initialization](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L518-L583)).

## Registration Hierarchy

```text
glsl.shader_expect_assume.vertex
├── expect
└── assume

glsl.shader_expect_assume.fragment
├── expect
└── assume

glsl.shader_expect_assume.compute
├── expect
└── assume
```

The factory creates the three stage groups and their two direct operation groups in [`addShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1416-L1511). Each stage has 43 `expect` leaves and 4 `assume` leaves, for 47 leaves per stage. The leaf names are generated from the parameter table and receive `_vec2`–`_vec4` and/or `_wrong_expected` suffixes where applicable ([parameter loop](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1503)).

## Behavior Parameters

The registered behavior is the product of shader stage, operation, operand source, data type, channel count, and (for selected `expect` cases) whether the storage-buffer input contains the expected value or an offset wrong value. The generator iterates expectation state `false` and `true`, channel counts 1 through 4, and the twelve base entries in `testParams[]`, then prunes unsupported combinations before registering leaves ([registration loop](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1503)).

### `expectKHR` behavior

The `expect` cases exercise `expectKHR` with an operand and expected value. The generated shader initializes `control` to the wrong value, invokes the intrinsic, and selects the expected or wrong value according to the intrinsic result ([compute](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1190-L1203), [vertex](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1265-L1279), [fragment](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1371-L1384)). Normal cases validate the expected branch; `_wrong_expected` cases deliberately validate the alternate branch.

The scalar base entries are:

- `constant`
- `specializationconstant`
- `pushconstant`
- `storagebuffer_bool`
- `storagebuffer_int8`
- `storagebuffer_int16`
- `storagebuffer_int32`
- `storagebuffer_int64`

These entries are defined in the source table ([`testParams[]`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1436)). Storage-buffer `expect` cases additionally generate vector widths 2, 3, and 4, and all five storage-buffer `expect` types additionally generate wrong-expectation variants.

For storage-buffer `expect` cases, the host writes one element per index. Boolean input is true in normal cases and false in wrong-expectation cases; integer input is initialized from the element index plus channel, and wrong-expectation input is offset by one ([input initialization](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L548-L578)). The generated expected vector follows the index and channel values, while the wrong vector uses an index-derived `*2 + 3` expression ([operand setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1038-L1063)).

### `assumeTrueKHR` behavior

The `assume` cases exercise `assumeTrueKHR` and report the selected operand or its comparison result. Their scalar base entries are `constant`, `specializationconstant`, `pushconstant`, and `storagebuffer`; all use boolean data ([source table](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1437-L1442)). The shader templates emit the intrinsic before writing the verification value ([compute](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1190-L1215), [vertex](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1265-L1292), [fragment](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1371-L1395)).

For constant, specialization-constant, and push-constant `assume` cases, the generated value is the boolean operand converted to `uint`. For storage-buffer `assume`, the generated value is the comparison between the indexed input element and `true` ([operand setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L996-L1077)).

### Registered dimensions

| Dimension | Source-defined values and restrictions |
|---|---|
| Stage | `vertex`, `fragment`, and `compute` ([stage array](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1418-L1455)). |
| Operation | `expect` and `assume`; each stage receives both direct child groups ([group creation](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1457-L1461)). |
| Data class | Constant, specialization constant, push constant, or storage buffer ([enum and parameter table](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L67-L73), [table](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1442)). |
| Data type | `bool` for all non-integer entries; storage-buffer `expect` also uses `int8`, `int16`, `int32`, and `int64` ([types](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L75-L82)). |
| Channel count | The loop considers 1–4, but counts above 1 are retained only for storage-buffer `expect`; those leaves receive `_vec2`, `_vec3`, or `_vec4` ([selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1482)). |
| Expectation state | `wrongExpected` is false and true. The true state is retained only for storage-buffer `expect` and receives `_wrong_expected` ([selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488)). |
| Operand source | Constant, specialization constant, push constant, or stage-indexed storage-buffer element. Storage-buffer indexing uses `gl_GlobalInvocationID.x`, `gl_VertexIndex`, or `uint(gl_FragCoord.x)` ([operand setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L996-L1077)). |

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.shader_expect_assume.compute.expect.storagebuffer_int32_vec3_wrong_expected
```

This leaf is registered by `addShaderExpectAssumeTests()` in [`vktShaderExpectAssumeTests.cpp#L1416-L1511`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1416-L1511), under the `compute` → `expect` groups. The name is formed by the `storagebuffer_int32` table entry plus the `_vec3` and `_wrong_expected` suffixes in the registration loop.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `shaderType = VK_SHADER_STAGE_COMPUTE_BIT` | Selects `addComputeTestShader()` and one workgroup with 32 invocations; the output is written directly to the result storage buffer. |
| `opType = OpType::Expect`, `dataClass = DataClass::StorageBuffer` | Emits `expectKHR` with the operand read from descriptor set 0, binding 1; the `expect` + storage-buffer combination is the source-defined path that retains vector and wrong-expectation variants. |
| `dataType = DataType::Int32`, `dataChannelCount = 3` | Specializes the operand to `i32vec3`; std430 gives each runtime-array element a four-scalar stride, matching the host initialization rule for three channels. |
| `wrongExpectation = true` | The host writes `(i+1, i+2, i+3)` while the shader's expected vector is `(i, i+1, i+2)`. The generated alternate value is `(2i+3, 2i+4, 2i+5)`, and the final check intentionally accepts that wrong-value branch. |

#### Purpose

This shader exercises `expectKHR` on a vector loaded from a storage buffer when the host deliberately supplies a value different from the generated expected vector. It verifies the alternate branch through the common `(invocation index, 1)` output oracle.

#### Structural Design

| Phase | Shader operation | Source-backed effect |
|---|---|---|
| Input | Load `inputBuffer[gl_GlobalInvocationID.x]` | Reads the stage-indexed `i32vec3` operand from binding 1. |
| Expectation | Call `expectKHR(operand, (i, i+1, i+2))` | Compares the returned vector with the expected vector component-wise in the generated `if`. |
| Selection | Keep `(2i+3, 2i+4, 2i+5)` on the false branch | This is the branch selected by the wrong-expectation input. |
| Validation write | Store `x = i`, `y = uint(control == wrongValue)` | Produces the pair checked by the host for each of 32 invocations. |

#### Shader Code

```glsl
#version 460 core
#extension GL_EXT_spirv_intrinsics: enable
#extension GL_EXT_shader_explicit_arithmetic_types_int32: enable
spirv_instruction (extensions = ["SPV_KHR_expect_assume"], capabilities = [5629], id = 5630)
void assumeTrueKHR(bool);
spirv_instruction (extensions = ["SPV_KHR_expect_assume"], capabilities = [5629], id = 5631)
i32vec3 expectKHR(i32vec3, i32vec3);
precision highp float;
precision highp int;
/// Binding 0 is a host-visible std430 output storage buffer with 32 uvec2 elements. Each invocation writes
/// its index and a one-word pass flag; the host requires every pair to equal (index, 1).
layout(set = 0, binding = 0, std430) buffer Block0 { uvec2 outputBuffer[]; };
/// Binding 1 is the host-filled std430 input storage buffer. i32vec3 array elements have a four-scalar
/// stride, matching the host's special channel-count-3 stride rule; this case stores (index+1,index+2,index+3).
layout(set = 0, binding = 1, std430) buffer Block1 { i32vec3 inputBuffer[]; };
/// One workgroup launches exactly the 32 invocations consumed by the common 32-element output oracle.
layout(local_size_x = 32, local_size_y = 1, local_size_z = 1) in;
void main()
{
    /// The registered wrong-expectation variant expects inputBuffer[index] to differ from the generated
    /// expected vector (index,index+1,index+2), so the alternate control value is the passing result.
    i32vec3 control = i32vec3(gl_GlobalInvocationID.x*2 + 3, gl_GlobalInvocationID.x*2 + 3 + 1, gl_GlobalInvocationID.x*2 + 3 + 2);
    if ( expectKHR(inputBuffer[gl_GlobalInvocationID.x], i32vec3(gl_GlobalInvocationID.x, gl_GlobalInvocationID.x + 1, gl_GlobalInvocationID.x + 2)) == i32vec3(gl_GlobalInvocationID.x, gl_GlobalInvocationID.x + 1, gl_GlobalInvocationID.x + 2) ) {
        control = i32vec3(gl_GlobalInvocationID.x, gl_GlobalInvocationID.x + 1, gl_GlobalInvocationID.x + 2);
    } else {
        // set wrong value
        control = i32vec3(gl_GlobalInvocationID.x*2 + 3, gl_GlobalInvocationID.x*2 + 3 + 1, gl_GlobalInvocationID.x*2 + 3 + 2);
    }
    /// Record the invocation identity and whether the wrong-value branch selected by this case was retained.
    outputBuffer[gl_GlobalInvocationID.x].x = gl_GlobalInvocationID.x;
    outputBuffer[gl_GlobalInvocationID.x].y = uint(control == i32vec3(gl_GlobalInvocationID.x*2 + 3, gl_GlobalInvocationID.x*2 + 3 + 1, gl_GlobalInvocationID.x*2 + 3 + 2));
}
```

#### Additional Info

- The compute runtime binds the output buffer at binding 0 and the input buffer at binding 1, dispatches `(1, 1, 1)`, and uses a shader-write-to-host-read barrier before validating the mapped output ([runtime setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L609-L750)).
- `wrongExpectation` changes host initialization by adding one to each stored integer channel, while the shader's wrong-value expression is generated independently from the invocation index ([input initialization and operand setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L548-L578), [parameter specialization](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1038-L1063)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Stage | Vertex and fragment cases move the same operation into the vertex or fragment shader; compute uses `gl_GlobalInvocationID.x` and direct storage-buffer output. | [stage dispatch and templates](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1021-L1036), [compute template](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1153-L1229), [graphics templates](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1231-L1409) |
| Operation | `assume` emits `assumeTrueKHR` before its verification write; `expect` emits the `control` branch shown here. | [operation selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L917-L927), [operation templates](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1190-L1203) |
| Operand source | Constant, specialization constant, and push-constant cases replace the binding-1 indexed load with their source-specific declaration; storage-buffer cases use the stage index shown in `VARNAME`. | [data-class specialization](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L996-L1077) |
| Type and width | Non-storage-buffer cases stay scalar; storage-buffer `expect` retains `bool`, explicit-width integer types, and vector widths 2–4. Integer types add their matching explicit-arithmetic extension. | [type and extension selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L932-L994), [registration pruning](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488) |
| Expectation state | Normal storage-buffer `expect` cases use the expected branch and compare `control` with the expected value; `_wrong_expected` changes host input and validates the wrong-value branch. | [registration and expect output](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488), [compute output](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1218-L1222) |

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
; Bound: 147
; Schema: 0
               OpCapability Shader
               OpCapability ExpectAssumeKHR
               OpExtension "SPV_KHR_expect_assume"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 32 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types_int32"
               OpSourceExtension "GL_EXT_spirv_intrinsics"
               OpName %main "main"
               OpName %control "control"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %Block1 "Block1"
               OpMemberName %Block1 0 "inputBuffer"
               OpName %_ ""
               OpName %Block0 "Block0"
               OpMemberName %Block0 0 "outputBuffer"
               OpName %__0 ""
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_v3int ArrayStride 16
               OpDecorate %Block1 BufferBlock
               OpMemberDecorate %Block1 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_runtimearr_v2uint ArrayStride 8
               OpDecorate %Block0 BufferBlock
               OpMemberDecorate %Block0 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %uint_1 = OpConstant %uint 1
%_runtimearr_v3int = OpTypeRuntimeArray %v3int
     %Block1 = OpTypeStruct %_runtimearr_v3int
%_ptr_Uniform_Block1 = OpTypePointer Uniform %Block1
          %_ = OpVariable %_ptr_Uniform_Block1 Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v3int = OpTypePointer Uniform %v3int
       %bool = OpTypeBool
     %v3bool = OpTypeVector %bool 3
     %v2uint = OpTypeVector %uint 2
%_runtimearr_v2uint = OpTypeRuntimeArray %v2uint
     %Block0 = OpTypeStruct %_runtimearr_v2uint
%_ptr_Uniform_Block0 = OpTypePointer Uniform %Block0
        %__0 = OpVariable %_ptr_Uniform_Block0 Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
    %uint_32 = OpConstant %uint 32
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_32 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
    %control = OpVariable %_ptr_Function_v3int Function
         %16 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %17 = OpLoad %uint %16
         %19 = OpIMul %uint %17 %uint_2
         %21 = OpIAdd %uint %19 %uint_3
         %22 = OpBitcast %int %21
         %23 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %24 = OpLoad %uint %23
         %25 = OpIMul %uint %24 %uint_2
         %26 = OpIAdd %uint %25 %uint_3
         %28 = OpIAdd %uint %26 %uint_1
         %29 = OpBitcast %int %28
         %30 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %31 = OpLoad %uint %30
         %32 = OpIMul %uint %31 %uint_2
         %33 = OpIAdd %uint %32 %uint_3
         %34 = OpIAdd %uint %33 %uint_2
         %35 = OpBitcast %int %34
         %36 = OpCompositeConstruct %v3int %22 %29 %35
               OpStore %control %36
         %42 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %43 = OpLoad %uint %42
         %45 = OpAccessChain %_ptr_Uniform_v3int %_ %int_0 %43
         %46 = OpLoad %v3int %45
         %47 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %48 = OpLoad %uint %47
         %49 = OpBitcast %int %48
         %50 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %51 = OpLoad %uint %50
         %52 = OpIAdd %uint %51 %uint_1
         %53 = OpBitcast %int %52
         %54 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %55 = OpLoad %uint %54
         %56 = OpIAdd %uint %55 %uint_2
         %57 = OpBitcast %int %56
         %58 = OpCompositeConstruct %v3int %49 %53 %57
         %59 = OpExpectKHR %v3int %46 %58
         %60 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %61 = OpLoad %uint %60
         %62 = OpBitcast %int %61
         %63 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %64 = OpLoad %uint %63
         %65 = OpIAdd %uint %64 %uint_1
         %66 = OpBitcast %int %65
         %67 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %68 = OpLoad %uint %67
         %69 = OpIAdd %uint %68 %uint_2
         %70 = OpBitcast %int %69
         %71 = OpCompositeConstruct %v3int %62 %66 %70
         %74 = OpIEqual %v3bool %59 %71
         %75 = OpAll %bool %74
               OpSelectionMerge %77 None
               OpBranchConditional %75 %76 %90
         %76 = OpLabel
         %78 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %79 = OpLoad %uint %78
         %80 = OpBitcast %int %79
         %81 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %82 = OpLoad %uint %81
         %83 = OpIAdd %uint %82 %uint_1
         %84 = OpBitcast %int %83
         %85 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %86 = OpLoad %uint %85
         %87 = OpIAdd %uint %86 %uint_2
         %88 = OpBitcast %int %87
         %89 = OpCompositeConstruct %v3int %80 %84 %88
               OpStore %control %89
               OpBranch %77
         %90 = OpLabel
         %91 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %92 = OpLoad %uint %91
         %93 = OpIMul %uint %92 %uint_2
         %94 = OpIAdd %uint %93 %uint_3
         %95 = OpBitcast %int %94
         %96 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %97 = OpLoad %uint %96
         %98 = OpIMul %uint %97 %uint_2
         %99 = OpIAdd %uint %98 %uint_3
        %100 = OpIAdd %uint %99 %uint_1
        %101 = OpBitcast %int %100
        %102 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %103 = OpLoad %uint %102
        %104 = OpIMul %uint %103 %uint_2
        %105 = OpIAdd %uint %104 %uint_3
        %106 = OpIAdd %uint %105 %uint_2
        %107 = OpBitcast %int %106
        %108 = OpCompositeConstruct %v3int %95 %101 %107
               OpStore %control %108
               OpBranch %77
         %77 = OpLabel
        %114 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %115 = OpLoad %uint %114
        %116 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %117 = OpLoad %uint %116
        %119 = OpAccessChain %_ptr_Uniform_uint %__0 %int_0 %115 %uint_0
               OpStore %119 %117
        %120 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %121 = OpLoad %uint %120
        %122 = OpLoad %v3int %control
        %123 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %124 = OpLoad %uint %123
        %125 = OpIMul %uint %124 %uint_2
        %126 = OpIAdd %uint %125 %uint_3
        %127 = OpBitcast %int %126
        %128 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %129 = OpLoad %uint %128
        %130 = OpIMul %uint %129 %uint_2
        %131 = OpIAdd %uint %130 %uint_3
        %132 = OpIAdd %uint %131 %uint_1
        %133 = OpBitcast %int %132
        %134 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
        %135 = OpLoad %uint %134
        %136 = OpIMul %uint %135 %uint_2
        %137 = OpIAdd %uint %136 %uint_3
        %138 = OpIAdd %uint %137 %uint_2
        %139 = OpBitcast %int %138
        %140 = OpCompositeConstruct %v3int %127 %133 %139
        %141 = OpIEqual %v3bool %122 %140
        %142 = OpAll %bool %141
        %143 = OpSelect %uint %142 %uint_1 %uint_0
        %144 = OpAccessChain %_ptr_Uniform_uint %__0 %int_0 %121 %uint_1
               OpStore %144 %143
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `iterate()` dispatches compute cases or renders graphics cases, invalidates the output allocation, and calls the common validator ([iteration](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L106-L123)).
- Compute cases bind an output storage buffer, bind a second input storage buffer for storage-buffer operands, push a `VkBool32` true value for push-constant cases, dispatch one workgroup, and insert a compute-to-host memory barrier before waiting and flushing the mapped output ([compute setup and dispatch](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L609-L750)).
- The compute shader uses one workgroup with `local_size_x = 32` and writes directly to the output buffer ([compute shader](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1187-L1228)).
- Graphics cases allocate a `32 × 1` color attachment with format `VK_FORMAT_R32G32_UINT`, bind storage-buffer or push-constant resources when needed, and use a six-vertex triangle-list input ([attachment and pipeline setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L210-L245), [pipeline and draw](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L285-L477), [draw path](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L752-L843)).
- Graphics rendering transitions the color image, renders the six vertices, inserts a color-attachment-to-transfer barrier, copies the `32 × 1` image to the output buffer, waits for completion, and flushes the mapped allocation ([render/copy](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L816-L870)).
- Storage-buffer input is host-visible and sized for 32 elements with up to four 64-bit channels. The host initializes it according to the selected data type and channel count before flushing it ([storage buffers](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L518-L607)).

The validator checks every element for the pair `(index, 1)` and returns `Result comparison failed` on the first mismatch; otherwise it returns `Pass` ([validator](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L126-L137)). A passing result establishes agreement among generated GLSL, intrinsic compilation/execution, the selected pipeline/resource path, synchronization, and the host oracle. It does not isolate one layer; conversely, a failed comparison does not by itself identify whether the intrinsic, generated shader, pipeline, or data transfer caused the mismatch.

## Failure Meaning

### Failure Cause Mapping

| Observable result | Meaning in the source-defined test |
|---|---|
| `NotSupportedError` or an unavailable test | A required extension, feature, or storage capability was not available; this is distinct from a shader, pipeline, or result-comparison failure. |
| `Result comparison failed` | At least one of the 32 output elements was not `(index, 1)`. |
| `Pass` | Every output element matched the host oracle. |

### Cause Analysis

#### `expectKHR` result mismatch

**Possible failure symptoms:** A mismatch means that the generated `expectKHR` path did not produce the value selected by the case's expectation state.

Normal `expect` cases place the expected value in `control` when the intrinsic returns the expected value and validate `control == expected`. `_wrong_expected` cases initialize storage-buffer data to the offset wrong value and validate the alternate branch, so a failure must be interpreted with that suffix in mind ([wrong-expectation input and shader branch](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L548-L578), [expect templates](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1194-L1203)).

**Possible implementation causes:** Possible causes include incorrect intrinsic compilation or execution, incorrect operand/expected-value generation, storage-buffer layout or initialization errors, or a pipeline/resource transfer problem. The common comparison cannot isolate those layers.

#### `assumeTrueKHR` result mismatch

**Possible failure symptoms:** An `assume` failure means that the boolean value written by the shader was not the expected `1` for the selected constant, specialization constant, push constant, or storage-buffer comparison.

**Possible implementation causes:** It may indicate a problem in assumption lowering/execution, resource setup, or output transfer; the host result alone does not distinguish those causes.

#### Output or host-side validation mismatch

**Possible failure symptoms:** All paths use the same output oracle. A shader writes the element index in the first word and the verification result in the second, then the host invalidates and reads the output allocation. An unexpected nonzero or stale output is observable through the common host-side validation.

**Possible implementation causes:** Such output can arise from synchronization, image-to-buffer copying, host memory handling, or pipeline execution rather than from the intrinsic itself ([iteration and validation](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L106-L137), [graphics copy](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L847-L870)).

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_shader_expect_assume` through [`checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1111).
- `int64` cases require `shaderInt64` ([check](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1117-L1121)).
- `int16` cases require `VK_KHR_16bit_storage`, `shaderInt16`, `storageBuffer16BitAccess`, and `uniformAndStorageBuffer16BitAccess` ([check](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1122-L1135)).
- `int8` cases require `VK_KHR_shader_float16_int8`, `VK_KHR_8bit_storage`, `shaderInt8`, `storageBuffer8BitAccess`, and `uniformAndStorageBuffer8BitAccess` ([check](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1136-L1149)).
- The entire group is excluded from package registration in Vulkan SC builds by `#ifndef CTS_USES_VULKANSC` ([registration guard](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)).

A missing capability produces a not-supported result through the support checks; it is not a failed shader execution or result comparison.

### Design-based pruning

The registration loop intentionally avoids a full Cartesian product. It loops over channel counts 1–4 and both expectation states, but when the channel count is greater than one or `wrongExpected` is true, it retains only `expect` cases whose data class is `StorageBuffer` ([filter](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488)). Consequently:

- `assume` remains boolean and scalar.
- Constants, specialization constants, and push constants remain scalar; their `expect` cases use boolean operands.
- Storage-buffer `expect` supplies the scalar boolean and integer cases, vector widths 2–4, and `_wrong_expected` variants.
- Integer data types are used only by `expect`; the source asserts that integer cases are not `assume` cases ([data-type selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L944-L982)).

## Key Takeaways

- The group tests `expectKHR` and `assumeTrueKHR` through generated GLSL, rather than testing a host-only API path.
- Coverage is stage-first: the same parameter-generation rules are applied independently to vertex, fragment, and compute cases.
- Operand sourcing is tested separately through constants, specialization constants, push constants, and stage-indexed storage buffers.
- Vector and wrong-expectation variants are deliberately limited to storage-buffer `expect` cases; `assume` remains boolean and scalar.
- The common `(index, 1)` oracle makes the three stage paths comparable while preserving their different shader, pipeline, and transfer mechanisms.
- A pass means that all 32 pairs matched after the selected shader and resource path completed. It does not prove that any individual layer is correct in isolation.
- A missing capability is reported as not supported, while a comparison failure means that the executed path produced at least one output different from the oracle.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test implementation and source-defined purpose | [`vktShaderExpectAssumeTests.cpp#L20-L28`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L20-L28) | Identifies the `VK_KHR_shader_expect_assume` coverage and implementation file. |
| Public factory declaration | [`vktShaderExpectAssumeTests.hpp#L22-L35`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.hpp#L22-L35) | Declares `createShaderExpectAssumeTests()`. |
| Package registration | [`vktTestPackage.cpp#L1274-L1287`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1287) | Shows the GLSL package registration and the Vulkan SC guard. |
| Output constants and data model | [`vktShaderExpectAssumeTests.cpp#L57-L93`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L57-L93) | Defines 32 elements, `VK_FORMAT_R32G32_UINT`, operations, data classes, data types, and test parameters. |
| Runtime iteration and oracle | [`vktShaderExpectAssumeTests.cpp#L106-L137`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L106-L137) | Dispatches or renders, invalidates output, and checks `(index, 1)` for all elements. |
| Resource and pipeline setup | [`vktShaderExpectAssumeTests.cpp#L140-L870`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L140-L870) | Creates buffers, graphics attachments, pipelines, dispatches, draws, and copies output. |
| Parameter specialization | [`vktShaderExpectAssumeTests.cpp#L894-L1105`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L894-L1105) | Maps operation, data type, data class, stage, and expectation state to generated GLSL operands. |
| Feature support checks | [`vktShaderExpectAssumeTests.cpp#L1108-L1150`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1150) | Defines extension, feature, and storage prerequisites. |
| Compute shader template | [`vktShaderExpectAssumeTests.cpp#L1153-L1229`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1153-L1229) | Generates the compute path and output writes. |
| Vertex and graphics fragment templates | [`vktShaderExpectAssumeTests.cpp#L1231-L1322`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1231-L1322) | Generates the vertex operation and flat-value handoff. |
| Fragment shader template | [`vktShaderExpectAssumeTests.cpp#L1324-L1410`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1324-L1410) | Generates the fragment operation and direct color output. |
| Test registration and pruning | [`vktShaderExpectAssumeTests.cpp#L1416-L1511`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1416-L1511) | Builds stage/operation groups, expands the parameter table, and applies vector and wrong-expectation filters. |
| Factory definition | [`vktShaderExpectAssumeTests.cpp#L1516-L1519`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1516-L1519) | Creates the `shader_expect_assume` root group. |
