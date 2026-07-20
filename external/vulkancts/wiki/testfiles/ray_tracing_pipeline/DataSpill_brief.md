# Understanding Brief: ray_tracing_pipeline.data_spill

## One-Sentence Test Purpose

This test checks whether ray tracing shader call instructions (`OpTraceRayKHR`, `OpExecuteCallableKHR`, `OpReportIntersectionKHR`) and pipeline interface variables (ray payload, callable data, hit attributes, shader record buffer) preserve caller-side data across the call, by reading an input value before and after the call and writing a confirmation value only when the two reads match.

## Background Knowledge

### Data spilling around shader calls

A ray tracing shader that invokes another shader through `traceRayEXT`, `executeCallableEXT`, or `reportIntersectionEXT` may need to spill live values to memory before the call and reload them after. SPIR-V allows the compiler to keep values in registers across ordinary instructions, but a shader call is a suspension point: the caller invocation yields and the callee runs. Any value the caller still needs after the call must be saved somewhere the callee cannot clobber and reloaded on resume. If the compiler skips the spill or reload, the value the caller observes after the call differs from the value it had before.

Why it matters here:

- The test places a value in a storage buffer, reads it with a `Volatile` load before the call, performs the call, then reads the same address with another `Volatile` load after the call. The two loaded values must be equal. A mismatch means the caller's view of memory was not preserved across the call.
- A separate `calleeBuffer` is written by the callee to confirm the call actually took place. A pass requires both the caller-side equality check and the callee-side write to succeed, so a missed call is distinguishable from a corrupted spill.

### Volatile storage buffer loads

The SPIR-V template uses `OpLoad ... Volatile` for both the pre-call and post-call reads of the input buffer. The `Volatile` decoration forbids the compiler from caching, reordering, or eliminating the load. Without it, a compiler could fold the two reads into one and hide a spill bug. The test deliberately prevents that optimization so a real spill failure produces an observable mismatch.

### Pipeline interface variables

Ray tracing pipelines pass data between stages through interface variables: `rayPayloadEXT`/`rayPayloadInEXT` for trace-ray, `callableDataEXT`/`callableDataInEXT` for execute-callable, `hitAttributeEXT` for intersection-to-closest-hit, and the shader record buffer for per-shader constants. A caller writes a value, invokes the call, and reads the value back. If the implementation does not spill and restore these interface variables correctly across the call, the value the caller reads back differs from what the callee wrote.

### Shader call types and their SBT indexing

`traceRayEXT` takes SBT offset, stride, and miss index as uint operands. `executeCallableEXT` takes an SBT offset. `reportIntersectionEXT` takes a hit kind. In this test, those operands are computed from the input buffer value minus a constant (37), so when the input is correctly 37 the operand is zero and the call targets SBT entry 0. If the input value is wrong, the SBT index is wrong and the call may miss the intended callee, surfacing as a callee-buffer mismatch.

## One Concrete Example

Reconstructed rgen for the `trace_ray.int32` case (INT32 scalar input). The source emits this as SPIR-V assembly through a `tcu::StringTemplate`; the GLSL below is the equivalent reconstruction.

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
    int32_t input_val_before = inputBuffer.val;          // Volatile load before call
    int32_t zero_int         = input_val_before - int32_t(37);
    uint    zero_for_callable = uint(zero_int);           // SBT offset/stride/miss index, expected 0
    traceRayEXT(topLevelAS, 0u, 0xFFu, zero_for_callable, zero_for_callable, zero_for_callable,
                vec3(0.5, 0.5, 0.0), 0.0, vec3(0.0, 0.0, -1.0), 9.0, 0);
    int32_t input_val_after  = inputBuffer.val;          // Volatile load after call
    bool    equal            = (input_val_before == input_val_after);
    outputBuffer.val         = equal ? 1u : 0u;
}
```

The host fills `inputBuffer.val` with `37`, so `zero_for_callable` is `0`. The closest-hit shader writes `1` to `calleeBuffer`. The host then reads both `outputBuffer` and `calleeBuffer` and passes only if both contain `1`.

## End-to-End Test Flow

```text
[host] choose CallType (or InterfaceType) and DataType/VectorType from the registration matrix
[host] create inputBuffer, outputBuffer, calleeBuffer (host-visible SSBOs); fill inputBuffer with values that sum to 37
[host] build a default BLAS/TLAS appropriate for the call type (triangle for trace_ray, AABB for report_intersection, callable for execute_callable)
[host] build a ray tracing pipeline with the calling shader and the callee shader
[host] build one-entry SBTs for raygen/hit/callable as needed
[host] cmdTraceRays over a 1x1x1 launch
[device] calling shader: Volatile load inputBuffer -> compute zero -> invoke shader call -> Volatile load inputBuffer -> compare -> write outputBuffer
[device] callee shader: write 1 to calleeBuffer
[host] invalidate outputBuffer and calleeBuffer allocations
[host] pass iff outputBuffer.val == 1 AND calleeBuffer.val == 1
```

The `pipeline_interface` cases follow the same shape but use a 6-slot storage buffer and compare each slot against a per-case expected vector, since each interface type has its own spill contract.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- A SPIR-V assembly template shared across all `trace_ray`, `execute_callable`, and `report_intersection` cases, specialized per `DataType` and `VectorType` through `tcu::StringTemplate`. The template emits the pre-call load, the call, the post-call load, the equality check, and the output store.
- Inline GLSL callee shaders: a closest-hit shader for `trace_ray`, a callable shader for `execute_callable`, and an any-hit shader for `report_intersection`. Each callee writes `1` to `calleeBuffer`.
- Inline GLSL shaders for every `pipeline_interface` case: raygen plus the relevant chit/miss/rint/call/subcall stages, with a 6-slot storage buffer.
- Built with `SPIRV_VERSION_1_4`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `inputBuffer` (SSBO, host-visible) | yes, filled with values summing to 37 | yes (binding 3) | Volatile-loaded before and after the call by the calling shader | no | Carries the value that must survive the call |
| `outputBuffer` (SSBO, host-visible) | yes, zeroed | yes (binding 2) | written by calling shader with `equal ? 1 : 0` | yes | Pass signal for the caller-side equality check |
| `calleeBuffer` (SSBO, host-visible) | yes, zeroed | yes (binding 1) | written by callee with `1` | yes | Pass signal that the callee actually ran |
| `topLevelAS` acceleration structure | yes, built on device | yes (binding 0) | read by `traceRayEXT`/`reportIntersectionEXT` | no | Provides the geometry the ray hits so the callee runs |
| Textures, samplers, combined image samplers (sampler cases only) | yes, filled with 37 | yes (bindings 4-6) | sampled by calling shader | no | Replaces the input buffer as the data source for sampler-based data types |
| Storage image (ptr_texel case only) | yes, filled with 37 | yes (binding 4) | atomically exchanged by calling shader | no | Replaces the input buffer with an image texel pointer |
| Storage buffer with 6 slots (pipeline_interface cases only) | yes, zeroed | yes (binding 1) | written by rgen and callee stages | yes | Carries the per-slot expected values for each interface type |

## What Is Checked

For `trace_ray`, `execute_callable`, and `report_intersection` cases:

- `outputBuffer.val` must equal `1`, meaning the pre-call and post-call Volatile loads of `inputBuffer` returned the same value.
- `calleeBuffer.val` must equal `1`, meaning the callee shader ran.
- Both checks are host-side `uint32_t` comparisons against `1`. Any other value fails the case.

For `pipeline_interface` cases:

- A 6-slot `storageBuffer` is compared slot-by-slot against a per-`InterfaceType` expected vector.
- Expected vectors: `RAY_PAYLOAD` = {103, 100}, `CALLABLE_DATA` = {200, 100}, `HIT_ATTRIBUTES` = {300, 315, 330}, `SHADER_RECORD_BUFFER_RGEN` = {402, 450}, `SHADER_RECORD_BUFFER_CALL` = {806, 403, 450}, `SHADER_RECORD_BUFFER_MISS`/`SHADER_RECORD_BUFFER_HIT` = {1200, 400, 490}.
- Unused slots must remain `0`.

## Behavior Parameter Identification

> **Behavior parameter:** `CallType`/`InterfaceType` (the shader call path under test, realized as the four direct children of `data_spill`)
>
> **Candidate values:** `trace_ray`, `execute_callable`, `report_intersection`, `pipeline_interface`

A secondary configuration axis is `DataType` (and `VectorType` for the non-pipeline-interface cases), but it changes what data type is being spilled, not the call path being tested. The `pipeline_interface` child uses `InterfaceType` as its own secondary axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `trace_ray` | Caller-side input value changed across `OpTraceRayKHR` (spill/reload bug), or closest-hit callee did not run (SBT or traversal issue). |
| `execute_callable` | Caller-side input value changed across `OpExecuteCallableKHR` (spill/reload bug), or callable shader did not run (SBT issue). |
| `report_intersection` | Caller-side input value changed across `OpReportIntersectionKHR` inside the intersection shader (spill/reload bug), or any-hit callee did not run (intersection not accepted). |
| `pipeline_interface` | Interface variable (ray payload, callable data, hit attributes, or shader record buffer) was not preserved across the call, so the value read back after the call differs from what the callee wrote. |

## Important Variations and Special Cases

- The `trace_ray` and `execute_callable` cases use a raygen calling shader. The `report_intersection` case uses an intersection shader as the caller, with rgen only driving the trace. This is the only case where the calling shader is not rgen.
- 11 scalar data types are tested for the three call-type cases: INT32, UINT32, INT64, UINT64, INT16, UINT16, INT8, UINT8, FLOAT32, FLOAT64, FLOAT16. Vector types V2, V3, V4, and array-of-5 (A5) are generated for the 11 numeric types only. STRUCT, sampler/image/sampled-image variants, PTR_TEXEL, OP_NULL, and OP_UNDEF are scalar-only.
- The sampler/image cases replace `inputBuffer` with sampled image data and use descriptor indexing with non-uniform array indexing. The input buffer then carries texture coordinates (zeros) instead of the value to check.
- The PTR_IMAGE/PTR_SAMPLER/PTR_SAMPLED_IMAGE cases create a second descriptor pointer before the call and use it only after the call, exercising pointer liveness across the call boundary.
- The PTR_TEXEL case uses an atomic compare-exchange on a storage image texel, swapping 37 for 5, and checks the swapped value after the call.
- The OP_NULL case uses `OpConstantNull` before and after the call. The OP_UNDEF case writes an `OpUndef` value to the output buffer before the call and overwrites it after, exercising undefined-value handling.
- The `pipeline_interface` child has seven leaves: `ray_payload`, `callable_data`, `hit_attributes`, `shader_record_buffer_rgen`, `shader_record_buffer_call`, `shader_record_buffer_miss`, `shader_record_buffer_hit`. The shader-record-buffer cases fill the SBT record with `uvec4(400, 401, 402, 403)` and test that the record is readable after a call returns.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CallType` enum | [vktRayTracingDataSpillTests.cpp#L60-L65](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L60-L65) | Defines the three call-type values for the calling-shader cases. |
| `DataType` enum | [vktRayTracingDataSpillTests.cpp#L68-L94](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L68-L94) | Defines the 20 data type values that vary the spilled value's representation. |
| `VectorType` enum | [vktRayTracingDataSpillTests.cpp#L97-L104](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L97-L104) | Defines scalar, v2, v3, v4, and a5 vector widths. |
| `InterfaceType` enum | [vktRayTracingDataSpillTests.cpp#L2130-L2139](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2130-L2139) | Defines the seven pipeline-interface leaves. |
| SPIR-V template body | [vktRayTracingDataSpillTests.cpp#L542-L657](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L542-L657) | The shared assembly template with the pre-call load, call, post-call load, equality check. |
| INT32 specialization | [vktRayTracingDataSpillTests.cpp#L678-L686](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L678-L686) | The INT32 `CALC_ZERO_FOR_CALLABLE` and `INPUT_BUFFER_VALUE_TYPE` substitutions. |
| `trace_ray` call statements | [vktRayTracingDataSpillTests.cpp#L1326-L1350](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1326-L1350) | Emits rgen with `OpTraceRayKHR` and the GLSL closest-hit callee. |
| `execute_callable` call statements | [vktRayTracingDataSpillTests.cpp#L1352-L1374](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1352-L1374) | Emits rgen with `OpExecuteCallableKHR` and the GLSL callable callee. |
| `report_intersection` call statements | [vktRayTracingDataSpillTests.cpp#L1376-L1409](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1376-L1409) | Emits rint with `OpReportIntersectionKHR`, plus GLSL rgen and ahit. |
| `DataSpillTestCase::checkSupport` | [vktRayTracingDataSpillTests.cpp#L476-L535](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L476-L535) | Per-data-type feature gates (Int64, 16-bit storage, 8-bit storage, Float64, descriptor indexing). |
| `DataSpillTestInstance::iterate` | [vktRayTracingDataSpillTests.cpp#L1684-L2128](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L1684-L2128) | Host flow: buffer setup, AS build, pipeline, trace, copyback, pass/fail check. |
| Pipeline interface GLSL | [vktRayTracingDataSpillTests.cpp#L2205-L2461](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2205-L2461) | Inline GLSL for all seven interface-type cases. |
| Pipeline interface expected values | [vktRayTracingDataSpillTests.cpp#L2815-L2854](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2815-L2854) | Per-InterfaceType expected storage buffer contents. |
| Registration loop | [vktRayTracingDataSpillTests.cpp#L2887-L3005](../../../modules/vulkan/ray_tracing/vktRayTracingDataSpillTests.cpp#L2887-L3005) | Builds the four direct children and their leaves. |

## Questions / Risk Points for User Audit

- Is the spill-across-shader-call framing correct? The test reads the same storage buffer address before and after `OpTraceRayKHR`/`OpExecuteCallableKHR`/`OpReportIntersectionKHR` and checks equality. The callee does not write the input buffer in most cases, so a mismatch implies the caller's reload returned a different value than its earlier load.
- Is the `Volatile` load the right mechanism to prevent the compiler from folding the two reads? The SPIR-V template explicitly marks both loads `Volatile`, which forbids that optimization.
- Is one representative walkthrough (rgen + chit for `trace_ray.int32`) sufficient, or should a second walkthrough cover `report_intersection` (the only case where the calling shader is `rint` rather than `rgen`)?
- Are the `pipeline_interface` expected values correctly attributed to each `InterfaceType`? They come directly from the host-side expected-data switch.

## Conversion Notes for Final Wiki Rewrite

- Distill the background knowledge into a brief bullet list: data spill around shader calls, volatile loads, pipeline interface variables, and SBT operand derivation.
- Use the `trace_ray.int32` case as the single representative walkthrough because it is the simplest expression of the spill mechanism and the source emits it as SPIR-V assembly that maps cleanly to GLSL.
- Move the SPIR-V template internals, the per-DataType specialization tables, and the pipeline-interface expected-value switch to the source appendix.
- Copy the `### Failure Cause Mapping` table directly into the final page's `### Failure Cause Mapping`.
- Write `### Cause Analysis` fresh during the rewrite, grounded in the spill/reload semantics above.
- The scalar-only restriction for STRUCT, sampler/image, PTR_TEXEL, OP_NULL, and OP_UNDEF goes in `## Case Pruning` as design-based pruning.
- The per-DataType feature gates (Int64, 16-bit, 8-bit, Float64, descriptor indexing) go in `## Case Pruning` as requirement-based pruning.
