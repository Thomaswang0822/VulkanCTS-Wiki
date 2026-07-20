## Overview

**Core question:** Does a ray tracing shader preserve caller-side data across the three shader call instructions (`OpTraceRayKHR`, `OpExecuteCallableKHR`, `OpReportIntersectionKHR`) and across the four pipeline interface variables (ray payload, callable data, hit attributes, shader record buffer)?

- [vktRayTracingDataSpillTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp) implements and registers the `data_spill` test family under the `ray_tracing_pipeline` test category.
- Four direct children correspond to the four call paths under test: `trace_ray`, `execute_callable`, `report_intersection`, and `pipeline_interface`.
- The first three children share one test class that reads a storage buffer value before and after a shader call and writes a confirmation value only when the two reads match. The `pipeline_interface` child uses a separate class that checks per-slot expected values for each interface variable type.
- Each leaf name encodes a `DataType` and an optional `VectorType` prefix (for example `int32`, `v3float32`, `a5uint8`). The `pipeline_interface` child uses `InterfaceType` leaf names like `ray_payload` and `shader_record_buffer_call`.
- The page explains the spill mechanism, the four call paths, the parameter matrix, a representative `trace_ray.int32` shader walkthrough, the runtime pass/fail check, and what each failure points to.

## Background Knowledge

- **Data spill around shader calls.** A ray tracing shader that invokes another shader suspends and yields to the callee. Any caller-side value still needed after the call must be saved to memory the callee cannot clobber and reloaded on resume. If the compiler skips the spill or the reload, the value the caller observes after the call differs from the value it had before.
- **Volatile storage buffer loads.** The SPIR-V template marks both the pre-call and post-call reads of the input buffer as `Volatile`. The `Volatile` qualifier forbids the compiler from caching, reordering, or eliminating the load. Without it, a compiler could fold the two reads into one and hide a spill bug.
- **Pipeline interface variables.** Ray tracing pipelines pass data between stages through interface variables: `rayPayloadEXT`/`rayPayloadInEXT` for trace-ray, `callableDataEXT`/`callableDataInEXT` for execute-callable, `hitAttributeEXT` for intersection-to-closest-hit, and the shader record buffer for per-shader constants. A caller writes a value, invokes the call, and reads the value back; an incorrect spill or restore makes the read-back differ from what the callee wrote.
- **SBT operand derivation.** `traceRayEXT` takes SBT offset, stride, and miss index as uint operands; `executeCallableEXT` takes an SBT offset; `reportIntersectionEXT` takes a hit kind. In the call-type cases those operands are computed from the input value minus 37, so when the input is correctly 37 the operand is zero and the call targets SBT entry 0.

## Registration Hierarchy

```text
ray_tracing_pipeline.data_spill
├── execute_callable
├── pipeline_interface
├── report_intersection
└── trace_ray
```

The first three children are built by one registration loop over `CallType`, `DataType`, and `VectorType` [registration loop](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2939-L2972). The `pipeline_interface` child is built by a second loop over `InterfaceType` [pipeline_interface loop](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2974-L3002). Each leaf is a test case; there are no intermediate nodes below the four direct children.

## Parameter Dimensions and Observed Values

The call-type cases (`trace_ray`, `execute_callable`, `report_intersection`) share a matrix built from three arrays in the registration loop [callTypes, dataTypes, vectorTypes](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2892-L2937).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `CallType` | `execute_callable`, `trace_ray`, `report_intersection` | Selects which shader call instruction the calling shader emits. This is the primary behavioral axis. | [callTypes](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2896-L2900) |
| `DataType` | `int32`, `uint32`, `int64`, `uint64`, `int16`, `uint16`, `int8`, `uint8`, `float32`, `float64`, `float16`, `struct`, `sampler`, `image`, `combined`, `ptr_image`, `ptr_sampler`, `ptr_combined`, `ptr_texel`, `op_null`, `op_undef` | Selects the representation of the value that must survive the call. Drives SPIR-V template specialization and feature gates. | [dataTypes](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2906-L2928) |
| `VectorType` | `""` (scalar), `v2`, `v3`, `v4`, `a5` | Selects scalar, 2/3/4-component vector, or 5-element array. Only generated for the 11 numeric `DataType` values. | [vectorTypes](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2934-L2937) |
| `InterfaceType` (pipeline_interface only) | `ray_payload`, `callable_data`, `hit_attributes`, `shader_record_buffer_rgen`, `shader_record_buffer_call`, `shader_record_buffer_miss`, `shader_record_buffer_hit` | Selects which pipeline interface variable is exercised by the pipeline_interface child. | [interfaceTypes](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2982-L2990) |

The leaf name is formed as `<VectorType prefix><DataType name>` (for example `v3float32`, `a5uint8`, `struct`). The `pipeline_interface` child uses the `InterfaceType` name directly as the leaf name.

## Behavior Parameters

The primary behavioral axis is `CallType`/`InterfaceType`, realized as the four direct children of `data_spill`. Each child targets a different shader call path and exercises a distinct spill surface. The `DataType` and `VectorType` dimensions vary the representation of the spilled value but do not change the call path under test.

### trace_ray — spill across OpTraceRayKHR

The calling shader is a raygen shader. It reads `inputBuffer`, computes the SBT offset/stride/miss index from the input value, calls `OpTraceRayKHR`, then re-reads `inputBuffer` and writes `1` to `outputBuffer` when the two reads match [trace_ray call statements](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1326-L1350). The callee is a closest-hit shader that writes `1` to `calleeBuffer`. This child has the largest leaf matrix because it covers all 21 `DataType` values across all 5 `VectorType` values where applicable.

### execute_callable — spill across OpExecuteCallableKHR

The calling shader is a raygen shader. It reads `inputBuffer`, computes the SBT offset from the input value, calls `OpExecuteCallableKHR`, then re-reads `inputBuffer` and writes `1` to `outputBuffer` when the two reads match [execute_callable call statements](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1352-L1374). The callee is a callable shader that writes `1` to `calleeBuffer`. No acceleration structure traversal is needed for the call itself, but the test still builds a default BLAS/TLAS because the pipeline creation path expects it.

### report_intersection — spill across OpReportIntersectionKHR

The calling shader is an intersection shader, not a raygen shader. This is the only call-type child where the caller is not rgen. The rgen shader traces a ray into procedural (AABB) geometry [report_intersection rgen](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1390-L1398). The intersection shader reads `inputBuffer`, computes the hit kind from the input value, calls `OpReportIntersectionKHR`, then re-reads `inputBuffer` and writes `1` to `outputBuffer` when the two reads match [report_intersection rint](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1378-L1388). The callee is an any-hit shader that writes `1` to `calleeBuffer`.

### pipeline_interface — spill of interface variables

This child uses a separate test class and a different spill surface. Instead of reading a storage buffer before and after the call, it writes a value to a pipeline interface variable, invokes the call, and reads the value back after the call returns [pipeline_interface GLSL](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2205-L2461). Seven leaves cover the four interface variable kinds: `ray_payload` (ray payload across `traceRayEXT`), `callable_data` (callable data across `executeCallableEXT`), `hit_attributes` (hit attributes from intersection to closest-hit), and four `shader_record_buffer_*` leaves that test the shader record buffer survives a call return. The host checks a 6-slot storage buffer against a per-leaf expected vector.

## Shader Analysis

The call-type cases share one SPIR-V assembly template specialized per `DataType` and `VectorType` through `tcu::StringTemplate` [SPIR-V template](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L542-L657). The template emits the pre-call `Volatile` load, the call instruction, the post-call `Volatile` load, the equality check, and the output store. The callee shaders are inline GLSL. The `pipeline_interface` cases use inline GLSL for all stages with no SPIR-V template.

One walkthrough covers the `trace_ray.int32` case because it is the simplest expression of the spill mechanism: the input is a single `int32_t` holding 37, the SBT operand computes to 0, and the closest-hit callee writes `1` to `calleeBuffer`. The other call-type cases differ only in the call instruction and the callee stage; the `pipeline_interface` cases differ in the spill surface but follow the same caller-write-callee-modify-caller-read pattern.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.data_spill.trace_ray.int32
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `trace_ray` | The calling shader is rgen and the call instruction is `OpTraceRayKHR`. |
| `int32` | The input value is a single `int32_t` holding 37. The SBT offset/stride/miss index compute to 0. |
| scalar | No vector prefix; `INPUT_BUFFER_VALUE_TYPE` is `%int`. |

#### Purpose

This case checks that the rgen shader's view of `inputBuffer.val` is preserved across `OpTraceRayKHR`. If the compiler skips the spill or reload of `input_val_before`, the post-call read returns a different value and `outputBuffer.val` reads back `0` instead of `1`. If the closest-hit shader does not run, `calleeBuffer.val` reads back `0`.

#### Structural Design

| Step | Stage | Action | Effect |
|------|-------|--------|--------|
| 1 | rgen | `Volatile` load `inputBuffer.val` into `input_val_before` | captures pre-call value (37) |
| 2 | rgen | compute `zero_for_callable = uint(input_val_before - 37)` | SBT offset/stride/miss index, expected 0 |
| 3 | rgen | `traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, 0, dir, 9, 0)` | suspends rgen, runs chit |
| 4 | chit | `calleeBuffer.val = 1u` | confirms callee ran |
| 5 | rgen | resume; `Volatile` load `inputBuffer.val` into `input_val_after` | captures post-call value |
| 6 | rgen | `outputBuffer.val = (input_val_before == input_val_after) ? 1 : 0` | pass signal |
| 7 | host | read `outputBuffer` and `calleeBuffer`; pass iff both are 1 | final verdict |

#### Shader Code

Reconstructed rgen (the source emits equivalent SPIR-V assembly through the template; the GLSL below is the equivalent reconstruction):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_shader_explicit_arithmetic_types : require

layout(set = 0, binding = 0) uniform accelerationStructureEXT topLevelAS;
layout(set = 0, binding = 1) buffer CalleeBlock { uint val; } calleeBuffer;
layout(set = 0, binding = 2) buffer OutputBlock { uint val; } outputBuffer;
layout(set = 0, binding = 3) buffer InputBlock { volatile int32_t val; } inputBuffer;
layout(location = 0) rayPayloadEXT vec3 hitValue;

void main()
{
    int32_t input_val_before = inputBuffer.val;          /// Volatile load before call
    int32_t zero_int         = input_val_before - int32_t(37);
    uint    zero_for_callable = uint(zero_int);           /// SBT offset/stride/miss index, expected 0
    traceRayEXT(topLevelAS, 0u, 0xFFu, zero_for_callable, zero_for_callable, zero_for_callable,
                vec3(0.5, 0.5, 0.0), 0.0, vec3(0.0, 0.0, -1.0), 9.0, 0);
    int32_t input_val_after  = inputBuffer.val;          /// Volatile load after call
    bool    equal            = (input_val_before == input_val_after);
    outputBuffer.val         = equal ? 1u : 0u;
}
```

Reconstructed closest-hit shader (from the inline GLSL in the source):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_shader_explicit_arithmetic_types : require
layout(location = 0) rayPayloadInEXT vec3 hitValue;
hitAttributeEXT vec3 attribs;
layout(set = 0, binding = 0) uniform accelerationStructureEXT topLevelAS;
layout(set = 0, binding = 1) buffer CalleeBlock { uint val; } calleeBuffer;
layout(set = 0, binding = 2) buffer OutputBlock { uint val; } outputBuffer;
layout(set = 0, binding = 3) buffer InputBlock { int32_t val; } inputBuffer;
void main()
{
    calleeBuffer.val = 1u;
}
```

#### Additional Info

- The host fills `inputBuffer.val` with `37` [fillInputBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1522-L1682), so `zero_for_callable` is `0`. The SBT offset, stride, and miss index are all 0, so the ray hits the single geometry in hit group 1 and no miss shader is bound.
- The CTS source emits the rgen as raw SPIR-V assembly with `OpLoad ... Volatile` on both the pre-call and post-call reads. The reconstructed GLSL uses the `volatile` qualifier on the buffer member, which glslang lowers to a `Volatile` member decoration on `InputBlock`. Both forms prevent the compiler from folding the two reads into one; the SPIR-V below reflects the GLSL reconstruction.
- The chit shader does not read `inputBuffer`, so a mismatch between the two rgen reads implies the rgen's reload returned a different value than its earlier load. The callee buffer distinguishes a spill failure (outputBuffer = 0, calleeBuffer = 1) from a missed call (outputBuffer = 0, calleeBuffer = 0).
- Vector and array cases extend the template by summing all components into `%total_sum`, subtracting the per-component constant 37, and comparing the before and after vectors with `OpAll` of a component-wise equality [vector specialization](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1155-L1289).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this walkthrough | Evidence |
|---------------------|--------------------------------------------|----------|
| `CallType` | Swaps the call instruction (`OpTraceRayKHR`, `OpExecuteCallableKHR`, `OpReportIntersectionKHR`) and the callee stage (chit, call, ahit). The calling-shader template body for the pre-call load, post-call load, and equality check stays the same; only the entry-point stage changes (rgen for `trace_ray`/`execute_callable`, rint for `report_intersection`). | [call statements](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1326-L1413) |
| `DataType` | Swaps `INPUT_BUFFER_VALUE_TYPE`, the constant used in the subtraction, the conversion to `uint`, and the equality operator (`OpIEqual` for integers, `OpFOrdEqual` for floats, custom member-wise comparison for structs and samplers). | [per-DataType specialization](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L678-L996) |
| `VectorType` | Adds component pointers, a component-wise sum, and a vector equality with `OpAll` (or per-component `OpLogicalAnd` for arrays). | [vector specialization](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1155-L1289) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 64
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %inputBuffer %topLevelAS %hitValue %outputBuffer %calleeBuffer
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %input_val_before "input_val_before"
               OpName %InputBlock "InputBlock"
               OpMemberName %InputBlock 0 "val"
               OpName %inputBuffer "inputBuffer"
               OpName %zero_int "zero_int"
               OpName %zero_for_callable "zero_for_callable"
               OpName %topLevelAS "topLevelAS"
               OpName %hitValue "hitValue"
               OpName %input_val_after "input_val_after"
               OpName %equal "equal"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "val"
               OpName %outputBuffer "outputBuffer"
               OpName %CalleeBlock "CalleeBlock"
               OpMemberName %CalleeBlock 0 "val"
               OpName %calleeBuffer "calleeBuffer"
               OpDecorate %InputBlock Block
               OpMemberDecorate %InputBlock 0 Volatile
               OpMemberDecorate %InputBlock 0 Coherent
               OpMemberDecorate %InputBlock 0 Offset 0
               OpDecorate %inputBuffer Binding 3
               OpDecorate %inputBuffer DescriptorSet 0
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %OutputBlock Block
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %outputBuffer Binding 2
               OpDecorate %outputBuffer DescriptorSet 0
               OpDecorate %CalleeBlock Block
               OpMemberDecorate %CalleeBlock 0 Offset 0
               OpDecorate %calleeBuffer Binding 1
               OpDecorate %calleeBuffer DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
 %InputBlock = OpTypeStruct %int
%_ptr_StorageBuffer_InputBlock = OpTypePointer StorageBuffer %InputBlock
%inputBuffer = OpVariable %_ptr_StorageBuffer_InputBlock StorageBuffer
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
     %int_37 = OpConstant %int 37
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
         %25 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_25 = OpTypePointer UniformConstant %25
 %topLevelAS = OpVariable %_ptr_UniformConstant_25 UniformConstant
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
  %float_0_5 = OpConstant %float 0.5
    %float_0 = OpConstant %float 0
         %38 = OpConstantComposite %v3float %float_0_5 %float_0_5 %float_0
   %float_n1 = OpConstant %float -1
         %40 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
    %float_9 = OpConstant %float 9
%_ptr_RayPayloadKHR_v3float = OpTypePointer RayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v3float RayPayloadKHR
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
%OutputBlock = OpTypeStruct %uint
%_ptr_StorageBuffer_OutputBlock = OpTypePointer StorageBuffer %OutputBlock
%outputBuffer = OpVariable %_ptr_StorageBuffer_OutputBlock StorageBuffer
     %uint_1 = OpConstant %uint 1
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%CalleeBlock = OpTypeStruct %uint
%_ptr_StorageBuffer_CalleeBlock = OpTypePointer StorageBuffer %CalleeBlock
%calleeBuffer = OpVariable %_ptr_StorageBuffer_CalleeBlock StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
%input_val_before = OpVariable %_ptr_Function_int Function
   %zero_int = OpVariable %_ptr_Function_int Function
%zero_for_callable = OpVariable %_ptr_Function_uint Function
%input_val_after = OpVariable %_ptr_Function_int Function
      %equal = OpVariable %_ptr_Function_bool Function
         %14 = OpAccessChain %_ptr_StorageBuffer_int %inputBuffer %int_0
         %15 = OpLoad %int %14
               OpStore %input_val_before %15
         %17 = OpLoad %int %input_val_before
         %19 = OpISub %int %17 %int_37
               OpStore %zero_int %19
         %23 = OpLoad %int %zero_int
         %24 = OpBitcast %uint %23
               OpStore %zero_for_callable %24
         %28 = OpLoad %25 %topLevelAS
         %31 = OpLoad %uint %zero_for_callable
         %32 = OpLoad %uint %zero_for_callable
         %33 = OpLoad %uint %zero_for_callable
               OpTraceRayKHR %28 %uint_0 %uint_255 %31 %32 %33 %38 %float_0 %40 %float_9 %hitValue
         %45 = OpAccessChain %_ptr_StorageBuffer_int %inputBuffer %int_0
         %46 = OpLoad %int %45
               OpStore %input_val_after %46
         %50 = OpLoad %int %input_val_before
         %51 = OpLoad %int %input_val_after
         %52 = OpIEqual %bool %50 %51
               OpStore %equal %52
         %56 = OpLoad %bool %equal
         %58 = OpSelect %uint %56 %uint_1 %uint_0
         %60 = OpAccessChain %_ptr_StorageBuffer_uint %outputBuffer %int_0
               OpStore %60 %58
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Buffer setup.** The host creates three host-visible SSBOs: `calleeBuffer` and `outputBuffer` (both zeroed, one `uint32_t` each) and `inputBuffer` (filled with values that sum to 37 for the case's `DataType`/`VectorType`) [buffer setup](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1702-L1739). For sampler and storage-image cases, `inputBuffer` is zeroed and the value 37 is placed in the textures or storage image instead.
- **Acceleration structure.** A default BLAS/TLAS pair is built using `setDefaultGeometryData` with the stage matching the call type (closest-hit for `trace_ray`, callable for `execute_callable`, intersection for `report_intersection`) [AS build](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1742-L1757).
- **Pipeline and SBT.** One raygen shader and one callee shader (chit, call, or ahit/rint) are bound. One-entry SBTs are created for raygen and the appropriate hit or callable table [pipeline and SBT](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2026-L2089).
- **Trace.** `cmdTraceRaysKHR` runs a `1x1x1` launch [trace](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2095-L2096).
- **Barrier and readback.** A shader-write to host-read memory barrier follows the trace. The host invalidates the `outputBuffer` and `calleeBuffer` allocations and reads them back [barrier and readback](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2098-L2125).
- **Pass/fail.** The host reads `outputBuffer.val` and `calleeBuffer.val` as `uint32_t`. Both must equal `1`. Any other value fails the case [pass/fail](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2114-L2127).
- **Pipeline_interface readback.** The `pipeline_interface` cases use a 6-slot `storageBuffer`. The host compares each used slot against a per-`InterfaceType` expected vector and checks that unused slots remain `0` [pipeline_interface expected values](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2815-L2882).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `trace_ray` | Caller-side input value changed across `OpTraceRayKHR` (spill/reload bug), or closest-hit callee did not run (SBT or traversal issue). |
| `execute_callable` | Caller-side input value changed across `OpExecuteCallableKHR` (spill/reload bug), or callable shader did not run (SBT issue). |
| `report_intersection` | Caller-side input value changed across `OpReportIntersectionKHR` inside the intersection shader (spill/reload bug), or any-hit callee did not run (intersection not accepted). |
| `pipeline_interface` | Interface variable (ray payload, callable data, hit attributes, or shader record buffer) was not preserved across the call, so the value read back after the call differs from what the callee wrote. |

All call-type cases share the same buffer setup, AS build, trace, barrier, and readback path. A shared infrastructure failure would surface identically across cases and is distinguishable from a single-call-path spill failure by which case or which buffer mismatched.

### Cause Analysis

#### Caller-side input value changed across the call

**Possible failure symptoms:** `outputBuffer.val` reads back `0` while `calleeBuffer.val` reads back `1`. This means the callee ran but the pre-call and post-call `Volatile` loads of `inputBuffer` returned different values.

**Possible implementation causes:** The compiler did not spill `input_val_before` (or the storage buffer pointer) to memory before the shader call, or did not reload it correctly on resume. The `Volatile` qualifier on the load forbids folding the two reads into one, so a mismatch points to the spill or reload path of the caller's live values across the call suspension. For vector and array cases, the same bug can affect the component pointers or the partial-sum accumulators. For the sampler and storage-image cases, the same bug can affect the descriptor pointer or the sampled value held across the call.

#### Callee did not run

**Possible failure symptoms:** `calleeBuffer.val` reads back `0`. `outputBuffer.val` may also read back `0` because the callee never wrote its buffer, but the caller's equality check could still pass if the input buffer was untouched.

**Possible implementation causes:** The SBT operand computed from the input value was not zero, so the call targeted the wrong SBT entry or missed the table entirely. This would point to the SBT operand computation or the SBT layout. Alternatively, the call instruction did not dispatch the callee at all: `OpTraceRayKHR` did not find the geometry, `OpExecuteCallableKHR` did not reach the callable record, or `OpReportIntersectionKHR` did not accept the candidate. For `report_intersection`, the intersection shader's `OpReportIntersectionKHR` returned false, so the any-hit shader never ran.

#### Interface variable not preserved across the call

**Possible failure symptoms:** For `pipeline_interface` cases, a used storage-buffer slot reads back a value other than the expected one. For example, `ray_payload` expects slot 0 = 103 (the post-call payload sum) and slot 1 = 100 (the pre-call payload sum written by chit). A slot mismatch means the interface variable was not written back correctly after the call returned.

**Possible implementation causes:** The implementation did not spill the interface variable to memory before the call or did not restore it on resume. For `ray_payload`, rgen writes `vec3(10, 30, 60)` and chit increments each component by 1, so the post-call sum should be 103. A different value means the payload write from chit was lost. For `callable_data`, rgen writes 100.0 and call doubles it, so the post-call value should be 200. For `hit_attributes`, the intersection shader writes `vec3(140, 160, 30)` and chit reads the sum 330; a different value means the hit attribute was not passed from intersection to closest-hit. For the `shader_record_buffer_*` cases, the SBT record `uvec4(400, 401, 402, 403)` must be readable after the call returns; a wrong value means the SBT record pointer was not preserved across the call.

#### Shared buffer, AS, or barrier error

**Possible failure symptoms:** A failure that appears across multiple unrelated cases, or `outputBuffer`/`calleeBuffer` values that read back as the initial zero even though the shaders ran.

**Possible implementation causes:** The host-side buffer flush before the trace, the shader-write to host-read barrier after the trace, or the allocation invalidation before readback could have missed. These causes are not specific to the spill mechanism and would be investigated by checking the barrier and allocation flow rather than the shader.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` device functionality, with the `rayTracingPipeline` and `accelerationStructure` feature bits enabled [commonCheckSupport](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L462-L474).
- INT64 and UINT64 cases require `shaderInt64` [Int64 gate](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L486-L490).
- INT16, UINT16, and FLOAT16 cases require `VK_KHR_16bit_storage`, `shaderInt16` or `shaderFloat16`, and `storageBuffer16BitAccess`; FLOAT16 also requires `VK_KHR_shader_float16_int8` [16-bit gate](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L491-L527).
- INT8 and UINT8 cases require `VK_KHR_shader_float16_int8`, `VK_KHR_8bit_storage`, `shaderInt8`, and `storageBuffer8BitAccess` [8-bit gate](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L501-L511).
- FLOAT64 cases require `shaderFloat64` [Float64 gate](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L512-L516).
- Sampler, image, sampled-image, and pointer-variant cases require `VK_EXT_descriptor_indexing` and `shaderSampledImageArrayNonUniformIndexing` [descriptor indexing gate](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L528-L534).

### Design-based pruning

- STRUCT, SAMPLER, IMAGE, SAMPLED_IMAGE, PTR_IMAGE, PTR_SAMPLER, PTR_SAMPLED_IMAGE, PTR_TEXEL, OP_NULL, and OP_UNDEF are scalar-only. The registration loop skips non-scalar vector types for these `DataType` values because they are standalone types with no meaningful vector form [scalar-only gate](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2952-L2958).
- The 11 numeric types (INT32, UINT32, INT64, UINT64, INT16, UINT16, INT8, UINT8, FLOAT32, FLOAT64, FLOAT16) generate all five `VectorType` values (scalar, v2, v3, v4, a5).
- The `pipeline_interface` child does not vary `DataType` or `VectorType`; it has exactly seven leaves, one per `InterfaceType`.
- The `report_intersection` child uses AABB geometry only, because the intersection shader only runs for procedural geometry. The `trace_ray` and `execute_callable` children use the default geometry for their respective stages.

## Key Takeaways

- The four direct children correspond to four distinct shader call paths. The first three share a SPIR-V template that reads an input value before and after the call and checks equality; the fourth uses inline GLSL to check pipeline interface variable preservation.
- The `Volatile` qualifier on the pre-call and post-call loads is the mechanism that makes a spill failure observable. Without it, a compiler could fold the two reads into one and hide the bug.
- A pass requires both `outputBuffer.val == 1` (caller-side equality check) and `calleeBuffer.val == 1` (callee ran). This split distinguishes a spill failure from a missed call: a spill failure leaves `calleeBuffer = 1` and `outputBuffer = 0`, while a missed call leaves both at `0`.
- The `DataType` and `VectorType` dimensions vary the representation of the spilled value but do not change the call path under test. The scalar-only types exercise special SPIR-V constructs: `OpConstantNull` for OP_NULL, `OpUndef` for OP_UNDEF, atomic compare-exchange for PTR_TEXEL, and non-uniform descriptor array indexing for the sampler variants.
- The `pipeline_interface` child tests a different spill surface: the interface variables that carry data between stages. Each of its seven leaves has a distinct expected-value vector that encodes which stage wrote what and whether the value survived the call return.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CallType` enum | [vktRayTracingDataSpillTests.cpp#L60-L65](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L60-L65) | Defines the three call-type values for the calling-shader cases. |
| `DataType` enum | [vktRayTracingDataSpillTests.cpp#L68-L94](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L68-L94) | Defines the 21 data type values that vary the spilled value's representation. |
| `VectorType` enum | [vktRayTracingDataSpillTests.cpp#L97-L104](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L97-L104) | Defines scalar, v2, v3, v4, and a5 vector widths. |
| `InterfaceType` enum | [vktRayTracingDataSpillTests.cpp#L2130-L2139](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2130-L2139) | Defines the seven pipeline-interface leaves. |
| SPIR-V template body | [vktRayTracingDataSpillTests.cpp#L542-L657](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L542-L657) | Shared assembly template with pre-call load, call, post-call load, equality check. |
| Per-DataType specialization | [vktRayTracingDataSpillTests.cpp#L678-L996](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L678-L996) | Substitutions for each DataType. |
| Vector and array specialization | [vktRayTracingDataSpillTests.cpp#L1155-L1289](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1155-L1289) | Component sum, vector equality with OpAll, array per-component comparison. |
| `trace_ray` call statements | [vktRayTracingDataSpillTests.cpp#L1326-L1350](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1326-L1350) | Emits rgen with `OpTraceRayKHR` and the GLSL closest-hit callee. |
| `execute_callable` call statements | [vktRayTracingDataSpillTests.cpp#L1352-L1374](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1352-L1374) | Emits rgen with `OpExecuteCallableKHR` and the GLSL callable callee. |
| `report_intersection` call statements | [vktRayTracingDataSpillTests.cpp#L1376-L1409](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1376-L1409) | Emits rint with `OpReportIntersectionKHR`, plus GLSL rgen and ahit. |
| `DataSpillTestCase::checkSupport` | [vktRayTracingDataSpillTests.cpp#L476-L535](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L476-L535) | Per-data-type feature gates. |
| `fillInputBuffer` | [vktRayTracingDataSpillTests.cpp#L1522-L1682](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1522-L1682) | Host-side fill of inputBuffer with values summing to 37. |
| `DataSpillTestInstance::iterate` | [vktRayTracingDataSpillTests.cpp#L1684-L2128](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1684-L2128) | Host flow: buffer setup, AS build, pipeline, trace, copyback, pass/fail. |
| Pipeline interface GLSL | [vktRayTracingDataSpillTests.cpp#L2205-L2461](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2205-L2461) | Inline GLSL for all seven interface-type cases. |
| `createSBTWithShaderRecord` | [vktRayTracingDataSpillTests.cpp#L2533-L2554](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2533-L2554) | Fills the SBT record with `uvec4(400, 401, 402, 403)` for the shader-record-buffer cases. |
| Pipeline interface expected values | [vktRayTracingDataSpillTests.cpp#L2815-L2854](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2815-L2854) | Per-InterfaceType expected storage buffer contents. |
| Registration loop | [vktRayTracingDataSpillTests.cpp#L2887-L3005](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2887-L3005) | Builds the four direct children and their leaves. |
