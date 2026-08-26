## Overview

**Core question:** Do the GLSL built-in implementations produce the required results across supported types, precisions, stages, and conversion paths?

- `createBuiltinTests()` registers the `glsl.builtin` test category beneath the GLSL package. The factory places `function`, four precision families, and `precision_fconvert` below the `builtin` test family. [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59) is the registration and aggregation point; [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1276) attaches it to the GLSL package.
- The `function` test family delegates common, integer, and pack/unpack built-ins to three implementation files. The precision families generate reference-checked floating-point cases, and `precision_fconvert` generates type-conversion cases.
- Cases build GLSL programs, execute them through ShaderExecutor or a compute pipeline, read results back, and compare them with operation-specific host references. Unsupported feature combinations are rejected before execution.
- This page explains the registered hierarchy, the dimensions that shape the generated matrix, the behavioral families, the shader and host-side checks, and what a reported failure does and does not identify.

## Background Knowledge

- GLSL built-ins operate on scalar and vector values, and some precision tests also operate on matrices. The vector length changes the number of component operations performed by one case.
- Shader precision is part of the test contract. The precision tests use separate floating-point models for `mediump`, `highp`, 16-bit, and 64-bit paths, so the host oracle must allow the range and accuracy of the selected model.
- A shader test can be unsupported without being incorrect. CTS support checks inspect device features, storage features, stage support, vector-length support, and device limits before the test instance runs.
- A storage-buffer conversion test needs both a shader-side conversion and host-side readback. The host can then compare the returned bit patterns or values with the conversion rules represented by the CTS reference code.

## Registration Hierarchy

```text
glsl.builtin
├── function
├── precision
├── precision_fp16_storage16b
├── precision_fp16_storage32b
├── precision_double
└── precision_fconvert
```

The `function` test family contains the `common`, `integer`, and `packing` intermediate nodes. The tree intentionally stops one level below `glsl.builtin`; generated operation names and test case leaves are documented in the parameter and behavior sections. The direct children and their implementation ownership come from [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L44-L57). The extracted mustpass paths are listed in [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `function`, `precision`, `precision_fp16_storage16b`, `precision_fp16_storage32b`, `precision_double`, `precision_fconvert` | Selects a different built-in implementation or numeric representation. | [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L44-L57) |
| Function implementation family | `common`, `integer`, `packing` | Selects the operation set under `function`. | [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L46-L50) |
| Common function | `abs`, `sign`, `isnan`, `isinf`, `floatbitstoint`, `floatbitstouint`, `intbitstofloat`, `uintbitstofloat` | Selects a scalar, vector, classification, or bit reinterpretation operation. | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1133) |
| Integer function | Registered operation names such as `bitcount`, bitfield operations, carry/borrow, extended multiply, and find-LSB operations | Selects an integer operation and its host comparison routine. | [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L1273-L1305) |
| Packing function | 4x8 normalized conversions, 2x16 normalized conversions, `packHalf2x16`, `unpackHalf2x16` | Selects a packing or unpacking operation and its supported shader stages. | [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1417-L1494) |
| Numeric precision | `mediump`, `highp`, 16-bit, and 64-bit paths where the family supports them | Selects the floating-point format and the reference interval or exact comparison rules. | [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8681-L8718) |
| Vector length | Scalar and vector lengths 1 through 5 where supported; conversion cases use `kMinVectorLength` through `kMaxVectorLength` | Changes the number of components processed by one operation or conversion. `vec5` function cases are limited to compute in the integer generator. | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1120-L1132), [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L241-L260), [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1414-L1441) |
| Shader stage | Compute and selected graphics stages for integer and packing functions | Exercises stage-specific ShaderExecutor support. | [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L253-L260), [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L106-L109) |
| FConvert type pair | Regular Vulkan builds: E5M2, E4M3, bfloat16, float16, float32, float64, plus signed and unsigned 32-bit integer conversions; Vulkan SC: float16, float32, float64 and integer conversions | Selects the source and destination representation. Same-type pairs are removed, and supported saturated cases are restricted to FP8 destinations. | [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1401-L1462) |
| Precision sample count | Positive command-line iteration count, otherwise `16384` for precision families | Sets the number of generated samples used by the floating-point reference checks. | [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8739-L8767) |

## Behavior Parameters

The primary behavioral axis is the test family. Each direct child of `glsl.builtin` selects a different implementation and validation mechanism.

### `function` | common, integer, and packing built-ins

`function` delegates to three intermediate nodes. `common` covers classification, sign and absolute-value operations, and float/integer bit reinterpretation. `integer` covers integer bit operations and arithmetic helpers. `packing` covers normalized and half-float pack/unpack operations. The delegate registrations are in [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L46-L50).

### `precision` | 32-bit floating-point built-ins

`precision` creates the regular floating-point factory set, then makes compute cases at `mediump` and `highp`. The factories cover arithmetic, trigonometric, exponential and logarithmic, common, geometric, matrix, `frexp`, `ldexp`, and `fma` operations. The test evaluates random or specialized samples against intervals derived from the selected format. [`createBuiltinCases()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8418-L8511) and [`createFuncGroup()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8681-L8701) define this path.

### `precision_fp16_storage16b` | 16-bit arithmetic with 16-bit storage access

This family uses the 16-bit factory set and a 16-bit precision model. It requests both 16-bit shader arithmetic and 16-bit uniform and storage-buffer access. Its cases therefore test the built-in operation and the storage path used to supply and retrieve 16-bit values. [`createFuncGroup16Bit()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8736) and the family constructor at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8797-L8809) define the distinction.

### `precision_fp16_storage32b` | 16-bit arithmetic with 32-bit storage

This family also uses 16-bit arithmetic, but its `storage32` path does not request 16-bit uniform and storage-buffer access. The distinction changes storage requirements while retaining the 16-bit floating-point reference model. [`createFuncGroup16Bit()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8736) and the family constructor at [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8811-L8823) provide the source evidence.

### `precision_double` | 64-bit floating-point built-ins

`precision_double` builds the double factory set and runs one compute case per factory with a 64-bit floating-point format. The case context enables the 64-bit shader-float feature path. [`createBuiltinDoubleCases()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8514-L8584) and [`createFuncGroupDouble()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8704-L8718) define this behavior.

### `precision_fconvert` | conversions between floating-point and integer representations

`precision_fconvert` creates names in the form `<from>_to_<to>_size_<k>` and adds `_sat` for eligible saturated conversions. Floating-point pairs cover the build-specific type list, while additional cases convert signed and unsigned 32-bit integers to and from each floating-point type. The generated shader uses a constructor for ordinary conversion and `saturatedConvertEXT` for saturated conversion. [`createPrecisionFconvertGroup()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1401-L1464) and [`FConvertTestCase::initPrograms()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L890-L970) define the case and shader paths.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.builtin.function.common.floatbitstoint.vec2_highp_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `function.common.floatbitstoint` | Selects the common built-in case whose operation source is `out0 = floatBitsToInt(in0);`. The registration is in `ShaderCommonFunctionTests::init()`. [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1110) |
| `vec2_highp_compute` | Selects a two-component 32-bit floating input, a two-component signed-integer output, high precision, and the compute executor. `addFunctionCases()` creates vector sizes 1 through 5 and mediump/highp variants; `CommonFunctionCase::initPrograms()` routes the case to `generateSources()`. [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L381-L405), [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L410-L420) |
| `ShaderSpec`: `in0: highp vec2`, `out0: highp ivec2`, `localSizeX = 1` | Determines the two std430 runtime-array records, one workgroup invocation per value, and the vector form of the generated built-in expression. [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L984-L998), [`vktShaderExecutor.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.hpp#L64-L83) |

#### Purpose

This case checks that the GLSL `floatBitsToInt` built-in preserves the bit pattern of each component while reinterpreting a highp `vec2` as an `ivec2`. The host comparison reconstructs the expected 32-bit float bits and permits the precision-dependent ULP threshold selected by the case.

#### Structural Design

| Phase | Generated shader behavior | Shader-visible object |
|---|---|---|
| Index | Linearize the three-dimensional workgroup ID into `invocationNdx`. | Compute built-ins `gl_NumWorkGroups` and `gl_WorkGroupID` |
| Load | Read `inputs[invocationNdx].in0` from the input runtime array. | Set 0, binding 0, `InBuffer` |
| Built-in | Evaluate `floatBitsToInt(in0)` component-wise. | Function-local `vec2 in0`, `ivec2 out0` |
| Store | Write `out0` to the matching output record. | Set 0, binding 1, `OutBuffer` |

The exact shader-generation entrypoint is `ComputeShaderExecutor::generateComputeShader()` in `vktShaderExecutor.cpp`. It emits the compute header, `local_size_x`, buffer declarations, invocation index, and `generateExecBufferIo()`; the case-specific `ShaderSpec::source` is inserted between local declarations and the output assignment. [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2130), [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3121)

#### Shader Code

```glsl
#version 450

#extension GL_EXT_long_vector : enable

layout(local_size_x = 1) in;

struct Inputs
{
    highp vec2 in0;
};

struct Outputs
{
    highp ivec2 out0;
};

/// Binding 0 is the host-uploaded std430 runtime array. Each record contains
/// the two float components used by one compute invocation.
layout(set = 0, binding = 0, std430) buffer InBuffer
{
    Inputs inputs[];
};

/// Binding 1 is the host-visible std430 runtime array receiving one ivec2
/// result per invocation.
layout(set = 0, binding = 1, std430) buffer OutBuffer
{
    Outputs outputs[];
};

void main (void)
{
    /// The executor dispatches one workgroup per value; this expression also
    /// matches the generator's general three-dimensional workgroup mapping.
    uint invocationNdx = gl_NumWorkGroups.x*gl_NumWorkGroups.y*gl_WorkGroupID.z
                       + gl_NumWorkGroups.x*gl_WorkGroupID.y + gl_WorkGroupID.x;
    vec2 in0 = vec2(inputs[invocationNdx].in0);
    ivec2 out0;

    /// This is the case-specific source snippet from FloatBitsToIntCase.
    out0 = floatBitsToInt(in0);

    outputs[invocationNdx].out0 = out0;
}
```

#### Additional Info

- `CommonFunctionTestInstance::iterate()` allocates planar input/output storage for 100 values, calls `ShaderExecutor::execute()`, and compares each value; a mismatch is logged with its index and values and returns `Result comparison failed`. [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L465-L508), [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L521-L563)
- The compute executor binds the input and output storage buffers at bindings 0 and 1, dispatches the current value count, inserts a shader-write-to-host-read barrier, waits for completion, and reads the output buffer back. [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3146-L3163), [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3224-L3298)
- For this highp float-to-int case the host reference is the `tcu::Float32(in0).bits()` value; the selected `vec2` case applies the same check independently to both components. [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L939-L980)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Common operation | Changes only the case-specific statement and output type; `abs`, `sign`, classification, and other bit reinterpretation cases use their own `ShaderSpec::source` and comparison class. | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1132) |
| Vector length | Changes `vec2`/`ivec2`, buffer record layout, and the number of component results; common cases generate lengths 1 through 5 where supported. | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L381-L405) |
| Precision | Changes the input precision and host oracle range/tolerance for float cases; integer outputs remain highp. | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L939-L980), [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L984-L998) |
| Shader stage | Common-function registration uses the compute executor, while the integer and packing families additionally select graphics-stage executors with stage-specific generated wrappers. | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L417-L420), [`vktShaderExecutor.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4198-L4229) |

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
; Bound: 64
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_long_vector"
               OpName %main "main"
               OpName %invocationNdx "invocationNdx"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %in0 "in0"
               OpName %Inputs "Inputs"
               OpMemberName %Inputs 0 "in0"
               OpName %InBuffer "InBuffer"
               OpMemberName %InBuffer 0 "inputs"
               OpName %_ ""
               OpName %out0 "out0"
               OpName %Outputs "Outputs"
               OpMemberName %Outputs 0 "out0"
               OpName %OutBuffer "OutBuffer"
               OpMemberName %OutBuffer 0 "outputs"
               OpName %__0 ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpMemberDecorate %Inputs 0 Offset 0
               OpDecorate %_runtimearr_Inputs ArrayStride 8
               OpDecorate %InBuffer BufferBlock
               OpMemberDecorate %InBuffer 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpMemberDecorate %Outputs 0 Offset 0
               OpDecorate %_runtimearr_Outputs ArrayStride 8
               OpDecorate %OutBuffer BufferBlock
               OpMemberDecorate %OutBuffer 0 Offset 0
               OpDecorate %__0 Binding 1
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
     %Inputs = OpTypeStruct %v2float
%_runtimearr_Inputs = OpTypeRuntimeArray %Inputs
   %InBuffer = OpTypeStruct %_runtimearr_Inputs
%_ptr_Uniform_InBuffer = OpTypePointer Uniform %InBuffer
          %_ = OpVariable %_ptr_Uniform_InBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v2float = OpTypePointer Uniform %v2float
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
    %Outputs = OpTypeStruct %v2int
%_runtimearr_Outputs = OpTypeRuntimeArray %Outputs
  %OutBuffer = OpTypeStruct %_runtimearr_Outputs
%_ptr_Uniform_OutBuffer = OpTypePointer Uniform %OutBuffer
        %__0 = OpVariable %_ptr_Uniform_OutBuffer Uniform
%_ptr_Uniform_v2int = OpTypePointer Uniform %v2int
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%invocationNdx = OpVariable %_ptr_Function_uint Function
        %in0 = OpVariable %_ptr_Function_v2float Function
       %out0 = OpVariable %_ptr_Function_v2int Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %18 = OpLoad %uint %17
         %19 = OpIMul %uint %15 %18
         %22 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %19 %23
         %25 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpIAdd %uint %24 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %invocationNdx %33
         %45 = OpLoad %uint %invocationNdx
         %47 = OpAccessChain %_ptr_Uniform_v2float %_ %int_0 %45 %int_0
         %48 = OpLoad %v2float %47
               OpStore %in0 %48
         %52 = OpLoad %v2float %in0
         %53 = OpBitcast %v2int %52
               OpStore %out0 %53
         %59 = OpLoad %uint %invocationNdx
         %60 = OpLoad %v2int %out0
         %62 = OpAccessChain %_ptr_Uniform_v2int %__0 %int_0 %59 %int_0
               OpStore %62 %60
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Common and integer cases allocate input and output arrays for `100` values, initialize the inputs, execute the generated shader, and compare each output tuple with an operation-specific `compare()` implementation. A mismatch records the value index and input/output values, and the test returns `Result comparison failed` if any value fails. [`CommonFunctionTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L495-L563) and [`IntegerFunctionTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L366-L429) implement this flow.
- Common comparisons include exact boolean classification and operation-specific bit or ULP checks. For `isnan`, double and high-precision float cases require the expected classification; lower-precision float cases reject false positives while allowing the reduced precision contract. [`IsnanCaseInstance::compare()`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L773-L812) shows that rule.
- Packing cases compare returned values with host references. Normalized packing applies the operation's clamping, rounding, and precision-dependent tolerance, while unpacking checks the decoded result against the expected representation. [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L148-L232) and [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L815-L843) contain the reference and validation paths.
- Precision cases generate the selected sample set, evaluate a host-side reference for the selected `FloatFormat`, and require each shader result to remain inside the permitted interval. The default sample count is `16384` when the command-line count is not positive. [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L7444-L7693) and [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8739-L8767) show the oracle and iteration setup.
- FConvert cases pack generated input values into the input storage buffer, dispatch enough compute workgroups to cover the vectors, copy the output storage buffer back, and call `verifyConversion()`. The test passes only when the conversion oracle accepts the returned memory. [`FConvertTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1068-L1100) and [`FConvertTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1385-L1397) cover setup and final status.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `function` | Generated shader behavior, stage support or pipeline setup, input/output marshalling, or the operation-specific host comparison disagrees with the shader result. |
| `precision` | The selected built-in result falls outside the host reference interval, or the generated shader, numeric lowering, execution, or readback does not preserve the tested precision behavior. |
| `precision_fp16_storage16b` | A 16-bit arithmetic result or 16-bit storage/readback result fails the precision oracle. |
| `precision_fp16_storage32b` | A 16-bit arithmetic result fails when the surrounding storage path uses 32-bit storage. |
| `precision_double` | A 64-bit built-in result fails the double-precision reference check, or the generated program does not preserve the selected operation and operands. |
| `precision_fconvert` | The returned storage-buffer values do not satisfy the selected ordinary or saturated conversion rules. |

Support failures are reported before execution when the device lacks a required feature or limit. They are not result mismatches from an executed case.

### Cause Analysis

#### Generated shader or pipeline result mismatch

**Possible failure symptoms:** A common, integer, or packing case logs one or more failed values and returns `Result comparison failed`, or a precision case reports a value outside its permitted interval.

**Possible implementation causes:** The source inspection identifies several possible layers, including generated GLSL, compilation and lowering, pipeline or ShaderExecutor setup, execution, synchronization, readback, and the host comparison. The CTS source does not assign a mismatch to one layer, so source-level or device-level investigation is needed for a specific failure.

#### Precision model mismatch

**Possible failure symptoms:** A `precision`, `precision_fp16_storage16b`, `precision_fp16_storage32b`, or `precision_double` case produces a result outside the interval calculated from its selected `FloatFormat`.

**Possible implementation causes:** The mismatch may arise from arithmetic or built-in lowering that does not meet the selected precision semantics, or from a disagreement between the generated shader result and the host reference model. The inspected CTS code supplies the interval and format but does not identify which implementation layer failed. Further investigation is needed.

#### Storage representation or readback mismatch

**Possible failure symptoms:** A 16-bit storage case or an FConvert case reads back bytes that fail the host conversion or precision check.

**Possible implementation causes:** The symptom can result from shader-side representation, storage-buffer layout, conversion, synchronization, or host unpacking. The source shows the buffers, packing, and validation calls, but it does not isolate a driver, hardware, compiler, or host cause. Further investigation is needed.

#### Unsupported feature or limit

**Possible failure symptoms:** CTS raises `NotSupportedError` before the result comparison because the selected stage, vector length, floating-point type, storage access, extension, or compute workgroup count is unavailable.

**Possible implementation causes:** The device or configuration lacks the feature or limit checked by the case. This is a support result, not evidence that an executed shader returned an incorrect value. The exact feature checks are in [`FConvertTestCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L973-L1065), the integer checks at [`IntegerFunctionCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L309-L329), and the precision setup at [`createFuncGroup16Bit()`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8736).

## Case Pruning

### Requirement-based pruning

- Common, integer, and packing cases reject unsupported shader stages through `checkSupportShader()` where stage support is part of the case. [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L309-L312) and [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L106-L109) provide the checks.
- Cases using five-component vectors require `VK_EXT_shader_long_vector` and, in the integer generator, are created only for compute. Vulkan SC builds cap the generated vector size at four in the common and integer generators. [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L444-L462), [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1120-L1128), and [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L241-L260) document these requirements.
- Double cases require `shaderFloat64`. 16-bit cases require `shaderFloat16`; the `storage16b` path additionally requires the relevant 16-bit uniform and storage-buffer access. FConvert checks the features for float64, float16, bfloat16, and FP8, along with the storage requirements for float16. [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8733) and [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L973-L1019) provide the checks.
- FConvert rejects cases that exceed `maxComputeWorkGroupCount[0]`. Vulkan SC omits bfloat16 and FP8 from its generated floating-point list because the source marks those extensions unavailable there. [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1000-L1019) and [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1055-L1065) show these conditions.

### Design-based pruning

- The integer generator skips non-highp precision when `allPrec` is false, and it omits five-component vectors from non-compute stages. These choices keep the generated set aligned with the operation and stage support encoded by each registration call. [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L225-L265)
- Precision families use different factory sets. The 16-bit families do not claim to instantiate the regular 32-bit factory list, and the double family uses its own signatures and one compute case per factory. [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8514-L8584) and [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8586-L8678)
- FConvert removes same-type pairs because they do not perform a conversion. It also adds saturation only for FP8 destinations and does not enable saturation when the source is already FP8. [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1422-L1436)
- FConvert adds scalar integer-to/from-float cases as a separate loop instead of treating them as ordinary floating-point pairs. The generated names preserve the source and destination type order and vector length. [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1445-L1462)

## Key Takeaways

- `glsl.builtin` is an aggregation point. `vktShaderBuiltinTests.cpp` fixes the public hierarchy, while delegate files own generation, support checks, shader construction, and result checking.
- The matrix is intentionally bounded. Stage availability, vector-length support, feature requirements, storage mode, conversion eligibility, and special precision families all remove combinations before execution.
- A passing case means the generated shader result matched the applicable host oracle for the selected operation, precision, representation, and parameters.
- A support result and a result-comparison failure have different meanings. The first says the selected case cannot run on the current configuration; the second says an executed case failed its validation rule.
- A failed comparison does not identify a specific source of the defect. The generated program, compiler, pipeline or ShaderExecutor, device execution, synchronization, readback, and host oracle remain possible investigation points until additional evidence narrows the cause.

## Source Reference Appendix

| Entry point | Link |
|---|---|
| GLSL package attachment | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1276) |
| Built-in registration and aggregation | [`vktShaderBuiltinTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L59) |
| Common built-in registration and execution | [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L495-L563), [`vktShaderCommonFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderCommonFunctionTests.cpp#L1099-L1133) |
| Integer built-in generation and execution | [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L225-L266), [`vktShaderIntegerFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderIntegerFunctionTests.cpp#L366-L429) |
| Pack/unpack registration and validation | [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L1417-L1494), [`vktShaderPackingFunctionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderPackingFunctionTests.cpp#L148-L232) |
| Precision factories, formats, and sample count | [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8418-L8511), [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8681-L8767) |
| 16-bit and double precision family registration | [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8514-L8584), [`vktShaderBuiltinPrecisionTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderBuiltinPrecisionTests.cpp#L8722-L8823) |
| FConvert shader generation and support | [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L890-L1025) |
| FConvert registration and validation | [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1068-L1100), [`vktShaderFConvertTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderFConvertTests.cpp#L1385-L1464) |
| Mustpass registration evidence | [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt) |
