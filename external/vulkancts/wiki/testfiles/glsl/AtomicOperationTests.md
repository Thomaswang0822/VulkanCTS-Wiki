## Overview

**Core question:** Do GLSL atomic operations produce a result that matches one legal serialization when two shader invocations update the same location?

- [`vktAtomicOperationTests.cpp`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1) implements the `glsl.atomic_operations` test family.
- Each test case selects an atomic operation, data type, shader stage, and memory form. The source generates the matching GLSL 4.50 shader and runs it through the shader-executor framework.
- Thirty-two participating invocations target sixteen atomic values, so two operations contend for each value. The host accepts either legal operation order and checks both the final value and the values returned by the atomic calls.
- The same semantic check runs against descriptor-backed storage buffers, workgroup-shared storage, task payload, and buffer-reference storage where those combinations are legal and supported.

## Background Knowledge

- A GLSL atomic read-modify-write operation updates one memory location without allowing another atomic operation on that location to observe a partially completed update. The function returns the value that was in memory before its own update.
- Concurrent invocations do not have a fixed execution order. If two valid atomic operations target one location, either one may execute first. A correct oracle must accept every result allowed by those two serial orders.
- Workgroup `shared` variables and `taskPayloadSharedEXT` objects are shader-local storage forms rather than host-bound storage buffers. The test copies data between them and a descriptor-backed result buffer before and after the atomic phase.
- A GLSL buffer reference lets shader code reach storage through a device address. The `_reference` cases therefore use a uniform buffer to carry the address of the storage buffer.

## Registration Hierarchy

```text
glsl
└── atomic_operations
```

The Vulkan test package registers `createAtomicOperationTests()` directly below `glsl`, and the factory creates `atomic_operations` ([package registration](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1278), [factory](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1589-L1592)). Generated test cases are direct children of this test family. For example, `add_signed_compute_shared` and `exchange_float32_fragment_reference` are test case leaves, not intermediate nodes. The Vulkan mustpass list confirms the registered prefix and concrete leaves ([mustpass](../../../mustpass/main/vk-default/glsl.txt#L175)).

## Parameter Dimensions and Observed Values

A leaf name has the form `<operation>_<data-type>_<stage><memory-suffix>`. An empty memory suffix denotes the ordinary descriptor-backed buffer form.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Atomic operation | `exchange`, `comp_swap`, `add`, `min`, `max`, `and`, `or`, `xor` | Selects the GLSL atomic function and the host reference calculation. | [Operation table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1524-L1535) |
| Data type | `signed`, `unsigned`, `float32`, `signed64bit`, `unsigned64bit`, `float64`; non-Vulkan-SC builds also use `float16`, `f16vec2`, `f16vec4` | Changes the scalar or vector element type, required extensions, comparison rules, and feature checks. | [Type table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1498-L1522) |
| Shader stage | `vertex`, `fragment`, `geometry`, `tess_ctrl`, `tess_eval`, `compute`, `task`, `mesh` | Exercises atomic lowering and resource access through each registered stage. | [Stage table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1472-L1485) |
| Memory suffix | empty, `_shared`, `_reference`, `_payload` | Chooses a storage buffer, workgroup-shared object, buffer reference, or task payload. | [Memory table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1487-L1496) |

The generator filters the matrix before it creates leaves:

- Floating-point types use `add` and `exchange`; non-Vulkan-SC builds also include `min` and `max`. They do not use compare-swap or bitwise operations ([operation filter](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1543-L1557)).
- `_shared` appears only with `compute`, `task`, and `mesh`. `_payload` appears only with `task` because mesh shaders receive task payload as read-only input ([memory filters](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1559-L1571)).
- Vulkan SC omits the 16-bit floating-point types and floating-point min/max combinations guarded by `CTS_USES_VULKANSC`.

## Behavior Parameters

The operation token is the primary behavioral axis because it changes the state transition and the legal returned values. Data type, stage, and memory form move that behavior across different representations and execution paths.

### `exchange`: replace the stored value

Two invocations each replace the same value and receive its previous contents. The final value is the second invocation's input; the two outputs must form the corresponding chain from the initial value through the first exchange ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L596-L600)).

### `comp_swap`: conditionally replace an integer value

The integer-only compare-swap cases initialize comparison operands so one contender can match, with the matching half alternating by element parity. The oracle accepts the legal outcomes for either contender arriving first ([initialization](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L301-L319), [oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L603-L615)).

### `add`: accumulate both inputs

Each invocation atomically adds its input to the same location and returns the preceding value. The final integer result includes both inputs regardless of order; the returned values identify which addition ran first ([integer oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L550-L554)). Floating-point cases use a separate reference path that accounts for floating-point behavior.

### `min`: retain a legal minimum

Each invocation atomically applies minimum to the current value and its input. Integer cases use exact signed or unsigned minimum calculations. Floating-point cases also admit source-defined legal results for NaNs and signed zero ([integer oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L578-L584), [exception handling](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L646-L689)).

### `max`: retain a legal maximum

This value mirrors `min` with maximum as the state transition. Integer cases compare exact results, while floating-point cases include the allowed NaN and signed-zero alternatives before matching the observed output ([integer oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L587-L593), [exception handling](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L646-L689)).

### `and`: combine integer bits with AND

The final value is the initial value ANDed with both inputs. Each returned value must match the state immediately before that invocation's operation in one of the two legal orders ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L557-L561)).

### `or`: combine integer bits with OR

The final value is the initial value ORed with both inputs. The host checks the two possible returned-value sequences with exact byte comparison ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L564-L568)).

### `xor`: combine integer bits with XOR

The final value is the initial value XORed with both inputs. As with the other bitwise cases, the final value alone is not enough; the two returned pre-operation values must also match one legal order ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L571-L575)).

## Shader Analysis

The family uses one generated kernel with substitutions for operation, type, stage, and memory form. The compute/storage-buffer integer-add leaf below shows the core contention pattern without the extra copy and barrier code of shared-like storage. Other variants retain the same two-operations-per-destination validation model.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.atomic_operations.add_signed_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `add` | Selects `atomicAdd` for the tested values and for the two internal counters. |
| `signed` | Uses 32-bit GLSL `int`, which needs no optional atomic extension. |
| `compute` with no memory suffix | Dispatches 32 one-invocation workgroups and operates directly on the descriptor-backed storage buffer. |

#### Purpose

This shader checks that two signed integer atomic additions to each storage-buffer destination produce the final sum and returned pre-operation values from one legal execution order.

#### Structural Design

| Step | Effect |
|------|--------|
| Reserve participation | `invocationHitCount[0]` admits the first 32 shader invocations. |
| Allocate an index | `index` assigns each admitted invocation one value from 0 through 31. |
| Create contention | `idx % 16` maps indices `i` and `i + 16` to the same destination. |
| Record the atomic result | `atomicAdd` updates that destination and writes its returned old value to `outputValues[idx]`. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_long_vector : enable

struct AtomicStruct
{
    int inoutValues[32/2];
    int inputValues[32];
    int compareValues[32];
    int outputValues[32];
    int invocationHitCount[32];
    int index;
};

/// Set 1, binding 0 is the host-visible storage buffer that carries both input state and atomic results.
layout (set = 1, binding = 0) buffer AtomicBuffer {
    AtomicStruct data;
} buf;

layout(local_size_x = 1) in;

struct Outputs
{
    highp uint outData;
};

/// The shader-executor output buffer is framework plumbing; host validation reads `buf` instead.
layout(set = 0, binding = 1, std430) buffer OutBuffer
{
    Outputs outputs[];
};

void main (void)
{
    uint invocationNdx = gl_NumWorkGroups.x*gl_NumWorkGroups.y*gl_WorkGroupID.z
                       + gl_NumWorkGroups.x*gl_WorkGroupID.y + gl_WorkGroupID.x;
    highp uint outData;

    /// Each of the 32 one-invocation workgroups reserves one index. Indices separated by 16 update the same destination.
    if (atomicAdd(buf.data.invocationHitCount[0], 1) < 32)
    {
        int idx = atomicAdd(buf.data.index, 1);
        buf.data.outputValues[idx] = atomicAdd(buf.data.inoutValues[idx % (32/2)], buf.data.inputValues[idx]);
    }

    outputs[invocationNdx].outData = outData;
}

```

#### Additional Info

- `createShaderSpec()` supplies the declarations and operation body, while `ComputeShaderExecutor::generateComputeShader()` supplies `#version 450`, the local-size declaration, `main()`, and the framework output buffer ([case generator](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1298-L1466), [compute wrapper](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3122)).
- The executor output `outData` is framework plumbing for this family. `iterate()` validates the separate atomic-operation buffer after invalidating its host mapping ([execution and checking](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L985-L1007)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation | Replaces the tested `atomicAdd` call and may add the compare operand required by `atomicCompSwap`. | [Specializations](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1442-L1451) |
| Data type | Replaces `int` in `AtomicStruct` and emits the required integer-64, floating-point, or vector-atomic extensions. | [Type and extension generation](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1415-L1447) |
| Shader stage | Changes invocation selection: vertex uses `gl_VertexIndex`, fragment excludes helper invocations, and other stages use the shared hit counter. | [Generated stage bodies](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1375-L1413) |
| Memory form | Shared and payload cases add copy barriers around the operation; reference cases use a buffer-reference declaration and uniform address transport. | [Declarations and shared path](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1320-L1401) |

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
; Bound: 84
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
               OpName %AtomicStruct "AtomicStruct"
               OpMemberName %AtomicStruct 0 "inoutValues"
               OpMemberName %AtomicStruct 1 "inputValues"
               OpMemberName %AtomicStruct 2 "compareValues"
               OpMemberName %AtomicStruct 3 "outputValues"
               OpMemberName %AtomicStruct 4 "invocationHitCount"
               OpMemberName %AtomicStruct 5 "index"
               OpName %AtomicBuffer "AtomicBuffer"
               OpMemberName %AtomicBuffer 0 "data"
               OpName %buf "buf"
               OpName %idx "idx"
               OpName %Outputs "Outputs"
               OpMemberName %Outputs 0 "outData"
               OpName %OutBuffer "OutBuffer"
               OpMemberName %OutBuffer 0 "outputs"
               OpName %_ ""
               OpName %outData "outData"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %_arr_int_uint_16 ArrayStride 4
               OpDecorate %_arr_int_uint_32 ArrayStride 4
               OpDecorate %_arr_int_uint_32_0 ArrayStride 4
               OpDecorate %_arr_int_uint_32_1 ArrayStride 4
               OpDecorate %_arr_int_uint_32_2 ArrayStride 4
               OpMemberDecorate %AtomicStruct 0 Offset 0
               OpMemberDecorate %AtomicStruct 1 Offset 64
               OpMemberDecorate %AtomicStruct 2 Offset 192
               OpMemberDecorate %AtomicStruct 3 Offset 320
               OpMemberDecorate %AtomicStruct 4 Offset 448
               OpMemberDecorate %AtomicStruct 5 Offset 576
               OpDecorate %AtomicBuffer BufferBlock
               OpMemberDecorate %AtomicBuffer 0 Offset 0
               OpDecorate %buf Binding 0
               OpDecorate %buf DescriptorSet 1
               OpMemberDecorate %Outputs 0 Offset 0
               OpDecorate %_runtimearr_Outputs ArrayStride 4
               OpDecorate %OutBuffer BufferBlock
               OpMemberDecorate %OutBuffer 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
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
        %int = OpTypeInt 32 1
    %uint_16 = OpConstant %uint 16
%_arr_int_uint_16 = OpTypeArray %int %uint_16
    %uint_32 = OpConstant %uint 32
%_arr_int_uint_32 = OpTypeArray %int %uint_32
%_arr_int_uint_32_0 = OpTypeArray %int %uint_32
%_arr_int_uint_32_1 = OpTypeArray %int %uint_32
%_arr_int_uint_32_2 = OpTypeArray %int %uint_32
%AtomicStruct = OpTypeStruct %_arr_int_uint_16 %_arr_int_uint_32 %_arr_int_uint_32_0 %_arr_int_uint_32_1 %_arr_int_uint_32_2 %int
%AtomicBuffer = OpTypeStruct %AtomicStruct
%_ptr_Uniform_AtomicBuffer = OpTypePointer Uniform %AtomicBuffer
        %buf = OpVariable %_ptr_Uniform_AtomicBuffer Uniform
      %int_0 = OpConstant %int 0
      %int_4 = OpConstant %int 4
%_ptr_Uniform_int = OpTypePointer Uniform %int
      %int_1 = OpConstant %int 1
     %int_32 = OpConstant %int 32
       %bool = OpTypeBool
%_ptr_Function_int = OpTypePointer Function %int
      %int_5 = OpConstant %int 5
      %int_3 = OpConstant %int 3
     %int_16 = OpConstant %int 16
    %Outputs = OpTypeStruct %uint
%_runtimearr_Outputs = OpTypeRuntimeArray %Outputs
  %OutBuffer = OpTypeStruct %_runtimearr_Outputs
%_ptr_Uniform_OutBuffer = OpTypePointer Uniform %OutBuffer
          %_ = OpVariable %_ptr_Uniform_OutBuffer Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%invocationNdx = OpVariable %_ptr_Function_uint Function
        %idx = OpVariable %_ptr_Function_int Function
    %outData = OpVariable %_ptr_Function_uint Function
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
         %49 = OpAccessChain %_ptr_Uniform_int %buf %int_0 %int_4 %int_0
         %51 = OpAtomicIAdd %int %49 %uint_1 %uint_0 %int_1
         %54 = OpSLessThan %bool %51 %int_32
               OpSelectionMerge %56 None
               OpBranchConditional %54 %55 %56
         %55 = OpLabel
         %60 = OpAccessChain %_ptr_Uniform_int %buf %int_0 %int_5
         %61 = OpAtomicIAdd %int %60 %uint_1 %uint_0 %int_1
               OpStore %idx %61
         %63 = OpLoad %int %idx
         %64 = OpLoad %int %idx
         %66 = OpSMod %int %64 %int_16
         %67 = OpAccessChain %_ptr_Uniform_int %buf %int_0 %int_0 %66
         %68 = OpLoad %int %idx
         %69 = OpAccessChain %_ptr_Uniform_int %buf %int_0 %int_1 %68
         %70 = OpLoad %int %69
         %71 = OpAtomicIAdd %int %67 %uint_1 %uint_0 %70
         %72 = OpAccessChain %_ptr_Uniform_int %buf %int_0 %int_3 %63
               OpStore %72 %71
               OpBranch %56
         %56 = OpLabel
         %78 = OpLoad %uint %invocationNdx
         %80 = OpLoad %uint %outData
         %82 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %78 %int_0
               OpStore %82 %80
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- `iterate()` creates the typed host view, seeds deterministic input generation with `0x62a15e34`, fills the mapped allocation, and flushes it before execution ([execution setup](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L900-L931)).
- Ordinary, shared, and payload cases bind the main allocation as a storage buffer. Reference cases add shader-device-address usage and pass that buffer's address through a uniform buffer.
- The shader-executor framework runs the selected stage. Shared-like cases arrange one workgroup of 32 local invocations; the generated stage logic limits other paths to 32 participating operations.
- After execution, the host invalidates the mapped allocation and calls the type-specific `checkResults()` path ([execution path](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L900-L1007)).
- For each of sixteen destinations, the integer oracle constructs the two triples allowed by the two serialization orders: final `inout` value, output from index `i`, and output from index `i + 16`. A case fails if neither triple matches ([model](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L524-L546), [comparison](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L623-L642)).
- Integer values use exact byte comparison. Floating-point values use a NaN-aware approximate comparison with tolerance `0.00001`, or `0.01` for `deFloat16` ([comparison helpers](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L327-L378)). The floating-point input includes signaling NaNs, quiet NaNs, and signed zeros, and the min/max oracle adds legal exceptional outcomes before comparison ([input generation](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L412-L453), [exception handling](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L646-L689)).

A pass means every destination matches at least one complete legal triple. Accepting either order does not permit unrelated combinations of a legal final value and illegal return values.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `exchange` | Incorrect atomic replacement or incorrect returned pre-operation value |
| `comp_swap` | Incorrect comparison, conditional replacement, or returned value |
| `add` | Incorrect atomic accumulation or floating-point atomic-add handling |
| `min` | Incorrect minimum operation, signedness, or floating-point exceptional-value handling |
| `max` | Incorrect maximum operation, signedness, or floating-point exceptional-value handling |
| `and` | Incorrect integer atomic AND result or return-value ordering |
| `or` | Incorrect integer atomic OR result or return-value ordering |
| `xor` | Incorrect integer atomic XOR result or return-value ordering |

Failures limited to one stage, data type, or memory suffix can instead point to that variant's shader lowering, feature path, resource declaration, address transport, or shared-like copy and synchronization path.

### Cause Analysis

#### Atomic state transition or return-value failure

**Possible failure symptoms:** At least one destination's final atomic value and two returned values match neither legal serialization. The log reports the index, both expected triples, the observed triple, and the two inputs.

**Possible implementation causes:** The implementation may lower the selected GLSL atomic operation with the wrong opcode, operand order, signedness, comparison rule, or result value. A defect that performs the update correctly but returns the post-operation value also fails because the oracle checks the returned pre-operation values.

#### Floating-point atomic result failure

**Possible failure symptoms:** An `add`, `exchange`, `min`, or `max` floating-point leaf produces a value outside the accepted tolerance or outside the legal NaN and signed-zero alternatives constructed by the reference code.

**Possible implementation causes:** The floating-point atomic path may mishandle the selected width, vector lanes, NaN behavior, signed zero, or the operation-specific extension semantics. The source checks the relevant extension feature before execution, so a result mismatch after support checking concerns the executed path rather than a missing advertised capability.

#### Stage or memory-form execution failure

**Possible failure symptoms:** Cases cluster by a stage or by the empty, `_shared`, `_reference`, or `_payload` suffix, while the same operation and type pass in other variants. Results may remain at their initialization pattern, contain too few valid outputs, or form no accepted triple.

**Possible implementation causes:** The stage-specific shader path may admit the wrong invocations or lower atomics incorrectly. Shared-like variants may fail during the copy, barrier, or copyback sequence. Reference variants may use the transported device address incorrectly. Source-level investigation is needed to distinguish shader compilation, descriptor/address setup, execution, and memory visibility when the observed data does not isolate one of those steps.

#### Test infrastructure or readback failure

**Possible failure symptoms:** Many unrelated operations, types, stages, or memory forms return unchanged initialization data or broadly inconsistent results.

**Possible implementation causes:** Buffer allocation, descriptor binding, submission, host flush/invalidate handling, or shader-executor setup could corrupt the observation path. The page's source evidence does not identify one layer from that symptom alone; logs and implementation-level tracing are needed.

## Case Pruning

### Requirement-based pruning

Support checking rejects a registered case when the implementation lacks its required capability:

- Signed and unsigned 64-bit integer cases require `VK_KHR_shader_atomic_int64`. Buffer and reference forms require `shaderBufferInt64Atomics`; shared-like forms require `shaderSharedInt64Atomics` ([checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1058-L1077)).
- Scalar float16 uses operation-specific buffer or shared feature bits from `VK_EXT_shader_atomic_float2`. `f16vec2` and `f16vec4` require `VK_NV_shader_atomic_float16_vector` and `shaderFloat16VectorAtomics` ([scalar checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1079-L1143), [vector checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1145-L1154)).
- Float32 and float64 cases require `VK_EXT_shader_atomic_float`; min/max also require `VK_EXT_shader_atomic_float2` and the corresponding min/max feature bit ([float32 checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1156-L1221), [float64 checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1223-L1288)).
- `_reference` requires `VK_KHR_buffer_device_address`, and every case runs the common selected-stage support check ([checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1290-L1296)).

A missing requirement yields `NotSupported`; it does not change the source-defined registration hierarchy.

### Design-based pruning

The registration loops intentionally omit combinations that do not belong to this test design:

- Floating-point compare-swap and bitwise operations are absent. Vulkan SC also omits floating-point min/max here.
- Workgroup-shared storage is absent from vertex, fragment, geometry, tessellation-control, and tessellation-evaluation cases.
- Task payload atomics are absent from non-task stages, including mesh, where task payload is read-only.
- Vulkan SC omits `float16`, `f16vec2`, and `f16vec4` leaves.

These omissions occur before leaf creation in `addAtomicOperationTests()` and are distinct from runtime support rejection ([registration loops](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1537-L1584)).

## Key Takeaways

- Each destination receives two contending atomic operations. The oracle checks the final value and both returned pre-operation values as one legal serialization triple.
- The operation token defines the tested state transition. Type, stage, and memory suffix apply it to different shader and storage paths.
- Floating-point validation includes tolerances and explicit alternatives for NaNs and signed zero; integer validation is exact.
- Registration filters illegal or out-of-scope combinations, while per-case feature checks turn unsupported registered leaves into `NotSupported` results.
- See `Failure Meaning` for how an operation-specific mismatch differs from a stage, memory-form, or readback-path failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Public factory declaration | [`vktAtomicOperationTests.hpp`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.hpp#L23-L35) | Declares the test-family factory. |
| Test data and exact integer comparison | [`TestBuffer`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L264-L354) | Defines overlapping inputs, outputs, and exact comparison. |
| Floating-point data and comparison | [`TestBufferFloatingPoint`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L380-L488) | Defines floating-point inputs, tolerances, and special values. |
| Host reference oracle | [`checkOperation()` and floating-point helpers](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L518-L799) | Constructs legal outcomes for each operation and execution order. |
| Execution and support checks | [`iterate()` through `checkSupport()`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L900-L1296) | Covers resources, submission through the executor, readback, and required features. |
| Shader generator | [`createShaderSpec()`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1298-L1466) | Generates declarations, stage logic, atomic calls, barriers, and extensions. |
| Case matrix generator | [`addAtomicOperationTests()`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1468-L1585) | Defines exact operation, type, stage, and memory dimensions plus design filters. |
| Family factory | [`createAtomicOperationTests()`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1589-L1592) | Registers the `atomic_operations` test family. |
| Package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1278) | Places the family directly below `glsl`. |
| Vulkan mustpass evidence | [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L175) | Confirms concrete `dEQP-VK.glsl.atomic_operations.*` leaves. |
