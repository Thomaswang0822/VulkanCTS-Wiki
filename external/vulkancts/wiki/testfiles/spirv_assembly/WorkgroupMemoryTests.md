## Overview

**Core question:** Can all invocations in one compute workgroup exchange scalar values through `Workgroup` memory after the shader issues the authored SPIR-V memory and control barriers?

- This page covers the `workgroup_memory` test family implemented by [`vktSpvAsmWorkgroupMemoryTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L141-L261).
- Every test case specializes one SPIR-V assembly template for a scalar type. Each invocation copies one input value to `sharedData`, synchronizes, then reads the value written at the reversed local index.
- The host expects the output storage buffer to equal the input buffer in reverse order. The 11 test case leaves vary the scalar type and feature requirements, while keeping the workgroup exchange protocol fixed.

## Background Knowledge

- A compute **workgroup** is a set of shader invocations that can synchronize and share data through the SPIR-V `Workgroup` storage class. Vulkan limits the aggregate storage used by such variables in a compute shader through `maxComputeSharedMemorySize` ([Vulkan specification](../../../../vulkan-docs/src/chapters/limits.adoc#L499-L503)). `sharedData` is this shader's workgroup-local array; it is not a descriptor-bound buffer.
- `OpControlBarrier` synchronizes the participating invocations. `OpMemoryBarrier` expresses memory ordering. The SPIR-V memory model defines their behavior ([Vulkan specification](../../../../vulkan-docs/src/chapters/shaders.adoc#L3465-L3474)); this test uses them between the writes to and reads from `sharedData`.
- The local invocation ID is three-dimensional. The shader flattens `(x, y, z)` for a `16 x 4 x 2` local size into `idx = z * 64 + y * 16 + x`, giving each of the 128 invocations one unique array position.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.workgroup_memory
├── float64
├── float32
├── float16
├── int64
├── int32
├── int16
├── int8
├── uint64
├── uint32
├── uint16
└── uint8
```

The parent compute registration attaches this test family under `spirv_assembly.instruction.compute` ([registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21415)). The main Vulkan mustpass list contains all 11 leaves ([mustpass entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L19887-L19897)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Data type | `float64`, `float32`, `float16`, `int64`, `int32`, `int16`, `int8`, `uint64`, `uint32`, `uint16`, `uint8` | Selects the substituted SPIR-V type, buffer stride, input/output payload type, and applicable feature or extension requirements. | [case construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L613) |
| Array length | `128` | Fixes the number of input, workgroup, and output elements. | [`numElements`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L141-L156) |
| Local size | `16 x 4 x 2` | Creates 128 invocations, one for each array index. | [execution mode and index calculation](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L182-L183) |
| Dispatch count | `1 x 1 x 1` workgroups | Keeps the exchange within one workgroup; the test does not exercise inter-workgroup communication. | [per-case specification](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L283-L285) |

## Behavior Parameters

The primary behavioral axis is the registered **data-type test case leaf**. The synchronization and reverse-index algorithm do not change. Each leaf changes the type placed in `Workgroup` storage and, where needed, the capabilities, extensions, device features, and floating-point result check.

### `float64`: 64-bit floating point

This leaf substitutes `OpTypeFloat 64` and `OpCapability Float64`. It requests `shaderFloat64` and uses `checkResultsFloat64`, which accepts any pair of NaN bit patterns as equal ([`float64` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L292)).

### `float32`: baseline 32-bit floating point

This leaf substitutes `OpTypeFloat 32` with a 4-byte stride. It has no extra feature request and uses `checkResultsFloat32` for NaN-aware element comparison ([`float32` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L294-L318)).

### `float16`: 16-bit floating point

This leaf substitutes `OpTypeFloat 16`, `OpCapability Float16`, and `SPV_KHR_16bit_storage`. It requires `VK_KHR_16bit_storage`, `VK_KHR_shader_float16_int8`, `storageBuffer16BitAccess`, and `shaderFloat16`; `checkResultsFloat16` handles NaNs ([`float16` case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L320-L353)).

### `int64` / `uint64`: 64-bit integers

These leaves specialize the template with signed or unsigned 64-bit `OpTypeInt` declarations. Both require `OpCapability Int64` and `shaderInt64`; the ordinary compute-case output check verifies the result ([64-bit cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L355-L383)).

### `int32` / `uint32`: baseline 32-bit integers

These leaves use the template's baseline signed or unsigned 32-bit integer type and a 4-byte stride. Neither assigns extra features or a custom verification callback ([32-bit cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L385-L408)).

### `int16` / `uint16`: 16-bit integers

These leaves select signed or unsigned 16-bit `OpTypeInt`, `OpCapability Int16`, and `SPV_KHR_16bit_storage`. They require `shaderInt16`, `storageBuffer16BitAccess`, and `VK_KHR_16bit_storage` ([16-bit cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L410-L441)).

### `int8` / `uint8`: 8-bit integers

These leaves select signed or unsigned 8-bit `OpTypeInt`, `OpCapability Int8`, and `SPV_KHR_8bit_storage`. They require `shaderInt8`, `uniformAndStorageBuffer8BitAccess`, `VK_KHR_8bit_storage`, and `VK_KHR_shader_float16_int8` ([8-bit cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L443-L475)).

## Shader Analysis

The `float64` leaf is the representative case because it uses the common exchange template and also exercises the largest scalar stride and the NaN-aware floating-point verification path. The code below is CTS-authored SPIR-V assembly extracted from the shared `StringTemplate` after applying that leaf's substitutions. This audit semantically validated it with `spirv-as`, `spirv-val`, and `spirv-dis` for the SPIR-V 1.0 environment; the disassembly is not published for this `spirv_assembly` page.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.workgroup_memory.float64
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `float64` | Uses `%f64 = OpTypeFloat 64`, an 8-byte buffer stride, and `OpCapability Float64`. |
| `LocalSize 16 4 2` | Produces 128 invocations, matching the 128-element `sharedData` array. |
| `1 x 1 x 1` workgroups | Limits the communication property to one workgroup. |

#### Purpose

The shader makes each invocation consume a value produced by its reverse-index partner through `Workgroup` storage. The expected reverse ordering proves that the partner's write became available before the read.

#### Structural Design

| Phase | Instructions and data flow | Role |
|-------|----------------------------|------|
| Index | `OpLoad`, `OpIMul`, `OpIAdd` derive `idx` from `gl_LocalInvocationID` | Maps each invocation to one element in the 128-element arrays. |
| Publish | `OpLoad` from `%dataInput`, then `OpStore` through `%sharedData` | Each invocation publishes its input value into workgroup memory. |
| Synchronize | `OpMemoryBarrier %uint_1 %uint_264`, then `OpControlBarrier %uint_2 %uint_2 %uint_264` | Orders the workgroup-memory access and synchronizes the workgroup before partner reads. |
| Consume | `OpISub %uint_127 %idx`, then `OpLoad` from `%sharedData` and `OpStore` to `%dataOutput` | Reads the reverse-index partner's value and writes it to the output buffer. |

`%uint_1` is `Device` scope, `%uint_2` is `Workgroup` scope, and `%uint_264` is `0x108`: `WorkgroupMemory` plus `AcquireRelease` semantics.

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- `%dataInput` and `%dataOutput` use descriptor set `0`, bindings `0` and `1`; the template uses the legacy `BufferBlock` plus `Uniform` storage form for these storage buffers.
- `%sharedData` has `Workgroup` storage class and no descriptor binding. The host creates only the input and output resources.
- The assembly comes from [`shaderSource`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261); `float64` supplies the type, 8-byte stride, and capability substitutions ([case setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L286)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-------------------------------------------|----------|
| Data type | Replaces `%f64`, `ArrayStride 8`, and `OpCapability Float64` with the selected scalar declaration, stride, capabilities, and extensions. The publish, barrier, and reverse-read instructions remain the same. | [template and specializations](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261) |
| Floating-point verification | `float64`, `float32`, and `float16` assign a NaN-aware `verifyIO` callback; integer leaves use the default output check. | [verification callbacks and cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L55-L139) |

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
; Bound: 60
; Schema: 0
               OpCapability Shader
               OpCapability Float64
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_LocalInvocationID
               OpExecutionMode %2 LocalSize 16 4 2
               OpSource GLSL 430
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %_arr_double_uint_128_0 ArrayStride 8
               OpMemberDecorate %_struct_5 0 Offset 0
               OpDecorate %_struct_5 BufferBlock
               OpDecorate %6 DescriptorSet 0
               OpDecorate %6 Binding 0
               OpDecorate %_arr_double_uint_128_1 ArrayStride 8
               OpMemberDecorate %_struct_8 0 Offset 0
               OpDecorate %_struct_8 BufferBlock
               OpDecorate %9 DescriptorSet 0
               OpDecorate %9 Binding 1
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
         %12 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
    %uint_64 = OpConstant %uint 64
     %uint_1 = OpConstant %uint 1
    %uint_16 = OpConstant %uint 16
     %uint_0 = OpConstant %uint 0
   %uint_127 = OpConstant %uint 127
     %uint_4 = OpConstant %uint 4
        %int = OpTypeInt 32 1
     %double = OpTypeFloat 64
   %uint_128 = OpConstant %uint 128
%_arr_double_uint_128 = OpTypeArray %double %uint_128
%_ptr_Workgroup__arr_double_uint_128 = OpTypePointer Workgroup %_arr_double_uint_128
         %30 = OpVariable %_ptr_Workgroup__arr_double_uint_128 Workgroup
%_arr_double_uint_128_0 = OpTypeArray %double %uint_128
  %_struct_5 = OpTypeStruct %_arr_double_uint_128_0
%_ptr_Uniform__struct_5 = OpTypePointer Uniform %_struct_5
          %6 = OpVariable %_ptr_Uniform__struct_5 Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_double = OpTypePointer Uniform %double
%_ptr_Workgroup_double = OpTypePointer Workgroup %double
   %uint_264 = OpConstant %uint 264
%_arr_double_uint_128_1 = OpTypeArray %double %uint_128
  %_struct_8 = OpTypeStruct %_arr_double_uint_128_1
%_ptr_Uniform__struct_8 = OpTypePointer Uniform %_struct_8
          %9 = OpVariable %_ptr_Uniform__struct_8 Uniform
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_16 %uint_4 %uint_2
          %2 = OpFunction %void None %12
         %37 = OpLabel
         %38 = OpVariable %_ptr_Function_uint Function
         %39 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_2
         %40 = OpLoad %uint %39
         %41 = OpIMul %uint %40 %uint_64
         %42 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_1
         %43 = OpLoad %uint %42
         %44 = OpIMul %uint %43 %uint_16
         %45 = OpIAdd %uint %41 %44
         %46 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %47 = OpLoad %uint %46
         %48 = OpIAdd %uint %45 %47
               OpStore %38 %48
         %49 = OpLoad %uint %38
         %50 = OpLoad %uint %38
         %51 = OpAccessChain %_ptr_Uniform_double %6 %int_0 %50
         %52 = OpLoad %double %51
         %53 = OpAccessChain %_ptr_Workgroup_double %30 %49
               OpStore %53 %52
               OpMemoryBarrier %uint_1 %uint_264
               OpControlBarrier %uint_2 %uint_2 %uint_264
         %54 = OpLoad %uint %38
         %55 = OpLoad %uint %38
         %56 = OpISub %uint %uint_127 %55
         %57 = OpAccessChain %_ptr_Workgroup_double %30 %56
         %58 = OpLoad %double %57
         %59 = OpAccessChain %_ptr_Uniform_double %9 %int_0 %54
               OpStore %59 %58
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test seeds a per-case random input vector and creates a same-sized expected vector by reversing it. It binds the two vectors as storage-buffer resources at bindings `0` and `1`.
- The specialized assembly becomes `spec.assembly`; each case dispatches `IVec3(1, 1, 1)`, so the device executes one 128-invocation workgroup.
- The device writes `outputData[idx] = sharedData[127 - idx]`. The framework reads the output allocation and compares it with the expected reversed vector.
- `checkResultsFloat16`, `checkResultsFloat32`, and `checkResultsFloat64` compare floating-point storage as integer bit patterns, accepting a result and expected value when both represent NaN. Integer cases leave `spec.verifyIO` unset and use the default compute-case verification.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `float64` | Workgroup-memory synchronization or float64 storage-buffer handling, with NaN-aware comparison accounting for NaN bit-pattern differences. |
| `float32` | Workgroup-memory synchronization for baseline 32-bit float storage. |
| `float16` | Workgroup-memory synchronization for 16-bit storage, including `SPV_KHR_16bit_storage` and `Float16` capability paths. |
| `int64` / `uint64` | Workgroup-memory synchronization for 64-bit integer storage, gated by `Int64` capability and `shaderInt64` feature. |
| `int32` / `uint32` | Baseline workgroup-memory synchronization for 32-bit integer storage, no extra features required. |
| `int16` / `uint16` | Workgroup-memory synchronization for 16-bit integer storage, including `SPV_KHR_16bit_storage` and `Int16` capability. |
| `int8` / `uint8` | Workgroup-memory synchronization for 8-bit integer storage, including `SPV_KHR_8bit_storage`, `UniformAndStorageBuffer8BitAccess`, and `Int8`. |

### Cause Analysis

#### Workgroup-memory synchronization

**Possible failure symptoms:** one or more output elements differ from the corresponding reversed input element because an invocation reads `sharedData[127 - idx]` before the partner's store is visible.

**Possible implementation causes:** source and specification evidence establish that this path depends on `OpMemoryBarrier` and `OpControlBarrier` semantics. A failure across several leaves warrants investigation of the implementation's lowering or execution of the workgroup-memory ordering and control barrier, rather than attributing it to a particular hardware block.

#### Scalar storage, capability, or feature handling

**Possible failure symptoms:** only leaves in a type tier fail, while baseline 32-bit leaves pass; affected output elements may have incorrect values despite the same reverse-index exchange protocol.

**Possible implementation causes:** the affected specialization changes the SPIR-V scalar type and can add a capability, extension, and requested device feature. Investigate the relevant 64-bit, 16-bit, or 8-bit storage and feature path, including its buffer stride and type conversion handling. The CTS source does not identify a more specific implementation location.

#### Floating-point NaN comparison

**Possible failure symptoms:** a floating-point leaf fails when the output and expected values differ in ordinary bits, or when the selected callback does not recognize two NaN encodings as equal.

**Possible implementation causes:** the three floating-point callbacks deliberately compare storage bit patterns and make an exception only when both values are NaN. Investigate the float storage path first for a genuine value mismatch; if the mismatch involves NaNs, also inspect the callback's type-specific comparison path. Integer leaves do not use this callback.

## Case Pruning

### Requirement-based pruning

The source still registers every one of the 11 leaves, but non-baseline leaves request the features and extensions required by their specialization. A device that cannot support the requested configuration cannot execute that leaf as a supported test configuration.

### Design-based pruning

The matrix contains one fixed algorithm for each scalar type. It does not vary workgroup size, array length, dispatch count, barrier operands, or cross-workgroup behavior. Those omissions isolate the intended property: workgroup-memory exchange across the paired barriers.

## Key Takeaways

- Each leaf performs the same 128-element reverse exchange, so a shared failure points to the common workgroup-memory synchronization path.
- The type leaf is the behavioral axis because it changes SPIR-V declarations, access width, capability and feature requirements, and sometimes verification, while retaining the exchange protocol.
- The result is a full-array host comparison, not an in-shader pass flag. For failure interpretation, see [Failure Meaning](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Floating-point result checks | [`checkResultsFloat16`, `checkResultsFloat32`, `checkResultsFloat64`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L55-L139) | Defines bitwise comparison and NaN equality for float leaves. |
| Workgroup-memory assembly template | [`shaderSource`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261) | Defines the declarations, barriers, index calculation, and reverse read. |
| Per-type specializations | [case construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L613) | Supplies scalar types, features, extensions, resource payloads, and expected output. |
| Test-family construction | [`createWorkgroupMemoryComputeGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L618-L624) | Registers the 11 test case leaves. |
| Parent registration | [`computeTests->addChild`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21415) | Places the test family in the compute instruction hierarchy. |
| Mustpass coverage | [workgroup-memory entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L19887-L19897) | Confirms the 11 registered paths in the main Vulkan mustpass list. |
