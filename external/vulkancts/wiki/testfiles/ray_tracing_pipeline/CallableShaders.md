## Overview

**Core question:** Does the implementation correctly dispatch callable shaders through `executeCallableEXT` from raygen, closest-hit, miss, and callable stages, including single invocations, multiple invocations, and nested callable-from-callable invocations?

- [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp) implements the `ray_tracing_pipeline.callable_shader` test family.
- The file registers 12 test case leaves under one test family: 4 simple image-output leaves and 8 shader-record invocation leaves.
- The simple group validates callable dispatch with a small 8x8 r32ui storage image and a 1-instance top-level AS. Three of four leaves never trace a ray; the fourth uses ray traversal to drive callable dispatch from closest-hit and miss.
- The shader-record group validates callable dispatch from each allowed invoking stage (raygen, callable, closest-hit, miss) with single and multiple invocations, using a 12-ray scene with mixed opaque / non-opaque geometry and a callable SBT that carries per-entry parameter blocks.
- The page explains the two flow shapes, the per-leaf expected outputs, and what a failure of each leaf points to.

## Background Knowledge

- **Callable shaders.** A callable shader is a ray tracing pipeline stage entered through `executeCallableEXT(shaderIndex, location)` rather than through ray traversal. The calling shader declares outgoing callable data with `callableDataEXT` at a `location`; the callable shader receives that storage through `callableDataInEXT` at the same `location`. Writes the callable makes to that storage are visible to the caller after the callable returns.
- **Callable shader binding table region.** `executeCallableEXT(shaderIndex, location)` selects a callable shader by SBT index. The callable SBT region is a separate region from raygen, hit, and miss. Multi-callable leaves rely on SBT indexing and stride to address different callable shaders in one rgen invocation.
- **Shader record extra data.** A callable SBT entry can carry extra bytes after the shader group handle. Callable shaders read those bytes through `shaderRecordEXT` buffer storage. The shader-record invocation group uses this mechanism to pass `CallableBuffer0 { uint base; uint shift; uint offset; uint multiplier; }` and `CallableBuffer1 { float numerator; float denomenator; uint power; uint reserved; }` into the callable shaders.
- **No callable from any-hit.** The source registration comment notes that callable shaders cannot be called from any-hit per `GLSL_NV_ray_tracing`, and the same restriction is assumed for KHR. The `invokingShaders` array excludes `glu::SHADERTYPE_ANY_HIT`.

## Registration Hierarchy

```text
ray_tracing_pipeline.callable_shader
├── callable_shader_invoked_via_callable_multiple_invocations
├── callable_shader_invoked_via_callable_single_invocation
├── callable_shader_invoked_via_closest_hit_multiple_invocations
├── callable_shader_invoked_via_closest_hit_single_invocation
├── callable_shader_invoked_via_miss_multiple_invocations
├── callable_shader_invoked_via_miss_single_invocation
├── callable_shader_invoked_via_raygen_multiple_invocations
├── callable_shader_invoked_via_raygen_single_invocation
├── hit_call
├── rgen_call
├── rgen_call_call
└── rgen_multicall
```

## Parameter Dimensions and Observed Values

The full leaf matrix comes from the registration loop at [vktRayTracingCallableShadersTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1975-L2032). The table adds local meaning for each dimension.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Simple test type | `rgen_call`, `rgen_call_call`, `hit_call`, `rgen_multicall` | Selects the callable dispatch pattern: single direct call from rgen, nested callable-from-callable, callable from closest-hit and miss, or four sequential callables with different data types. | [callableShaderTestTypes](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1984-L1989) |
| Invoking stage | `raygen`, `callable`, `closest_hit`, `miss` | Selects which shader stage calls `executeCallableEXT`. The any-hit stage is intentionally excluded. | [invokingShaders](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L2006-L2009) |
| Invocation count | `single_invocation`, `multiple_invocations` | Selects whether the invoking shader calls one callable or several callables with an index-dependent branch. | [multipleInvocations](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L2003-L2004) |
| Result image size | `8 x 8` | Fixed for the simple group; gives a 6x6 inner hit square and a 1-pixel miss border. | [TEST_WIDTH, TEST_HEIGHT](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L71-L72) |
| Result buffer size | `12 * sizeof(Vec4)` | Fixed for the shader-record group; one Vec4 per pre-baked ray. | [rays.size()](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1838-L1839) |
| Shader record buffer | `CallableBuffer0 {1, 4, 3, 7}`, `CallableBuffer1 {10.5, 2.5, 2, 0}` | Fixed parameter blocks written into the callable SBT entries. `CallableBuffer0` produces `((1<<4)+3)*7 = 133`. `CallableBuffer1` produces `(10.5/2.5)^2 = 17.64`; halving produces 8.82. | [callableBuffer0, callableBuffer1](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1713-L1714) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. The representative walkthrough in this page was compiled with `--target-env vulkan1.2`, which emits SPIR-V 1.5. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L549) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. The 12 leaves group into two mechanisms with different runtime shapes, so this section uses two groups of subsections. The first group covers the simple image-output leaves. The second group covers the shader-record invocation leaves.

**Simple image-output group.** These four leaves use `SingleSquareConfiguration`. They share a fixed 8x8 r32ui storage image and a 1-instance TLAS over a 2-triangle BLAS. Three of the four leaves never trace a ray; they exercise callable dispatch in isolation.

### rgen_call — rgen invokes one callable, no ray trace

The rgen shader declares `callableDataEXT uvec4 value` at location 0, calls `executeCallableEXT(0, 0)`, then writes `value` into the result image. The callable `call_0` writes `uvec4(1,0,0,1)` into its `callableDataInEXT`. The whole 8x8 image is expected to be `1`. The bound top-level AS is never traced; chit and miss are present in the pipeline but unreachable. This leaf isolates the basic callable dispatch path from rgen.

### rgen_call_call — rgen invokes a callable that invokes another callable

The rgen shader is the same `rgen_call` shader as in the `rgen_call` leaf. The callable `call_call` receives `callableDataInEXT uvec4 result` at location 0, declares its own `callableDataEXT uvec4 info` at location 1, calls `executeCallableEXT(1, 1)` to invoke `call_0`, then copies `info` into `result`. The expected image is still all `1`. This leaf validates that callable dispatch is permitted from inside a callable stage and that data flows back through the chain.

### hit_call — rgen traces rays; chit and miss each invoke a callable

The rgen shader traces rays into the BLAS square. The inner 6x6 pixels hit the triangle and run `chit_call`, which invokes the callable, copies the result into `hitValue`, then adds 1. The 1-pixel border misses and runs `miss_call`, which invokes the callable but does not add 1. Expected values: `hitValue = (2,0,0,0)`, `missValue = (1,0,0,0)`. This leaf is the only simple leaf where ray traversal matters for the result.

### rgen_multicall — rgen invokes four callables with four data types

The rgen shader declares four `callableDataEXT` variables with different types at locations 0, 1, 2, and 4: `uvec4`, `uint`, `CallValue { ivec4 a; vec4 b; }`, and `vec3`. It calls `executeCallableEXT(0, 0)`, `executeCallableEXT(1, 1)`, `executeCallableEXT(2, 2)`, and `executeCallableEXT(3, 4)` in sequence, then sums the results. The callable SBT has four entries (`call_0..3`). The expected sum is `1 + 2 + (3 * 3) + 4 = 16`, so the whole image is `16`. This leaf validates that multiple `executeCallableEXT` calls with different data types and SBT indices all return their expected contributions.

**Shader-record invocation group.** These eight leaves use `InvokeCallableShaderTestCase`. They share a 12-ray scene with three BLAS instances mixing opaque and non-opaque geometries, and a callable SBT with extra per-entry parameter data. The eight leaves are the cross product of four invoking stages and two invocation counts. The invoking stage axis changes which shader stage calls `executeCallableEXT`. The invocation count axis changes whether the invoking shader calls one callable (`build-callable-0`, which reads `CallableBuffer0` and writes value0=133) or several callables that also produce value1=17.64 and an index-dependent value2 (35.28 or 8.82).

### callable_shader_invoked_via_raygen_single_invocation — rgen invokes callable 0

The rgen shader invokes `build-callable-0` directly. The callable reads `CallableBuffer0` from its shader record, computes `((1<<4)+3)*7 = 133`, and writes that into `callableDataUint`. The rgen shader stores 133 into `results[index].value0`. `value1` and `value2` stay 0. `closestT` is 2.0 on hit and 1000.0 on miss.

### callable_shader_invoked_via_raygen_multiple_invocations — rgen invokes three callables

The rgen shader invokes `build-callable-0` (value0=133), then `build-callable-1` (value1=17.64 from `CallableBuffer1`), then a third callable chosen by `payload.lastShader == CLOSEST_HIT ? 1 : 2`. The third callable is `build-callable-1` again on hit (value2=35.28, accumulating 17.64 on top of the prior call's 17.64) or `build-callable-2` on miss (value2=8.82, halving the 17.64 left by the prior call). The 8 hit rays see value2=35.28 and the 4 miss rays see value2=8.82; the choice depends on `lastShader` (set to `CLOSEST_HIT` on hit and `MISS` on miss), not on `index`.

### callable_shader_invoked_via_callable_single_invocation — callable invokes another callable

The rgen shader invokes the outer callable `build-callable-invoke-callable`. That callable declares its own `callableDataEXT uint callableDataUint` at location 2 and calls `executeCallableEXT(1, 2)` to invoke `build-callable-0`. The inner callable writes 133 into `callableDataUint`. The outer callable copies that into its own `callableDataInEXT` so the rgen shader can read 133 in `results[index].value0`. This leaf exercises nested callable dispatch where the inner callable uses a different `callableDataEXT` location than the outer callable's `callableDataInEXT`.

### callable_shader_invoked_via_callable_multiple_invocations — nested chain with index branch

Same as the single-invocation callable leaf, plus the outer callable invokes `build-callable-1` (value1=17.64) and a third callable chosen by `index < 6 ? 2 : 3`. The first 6 rays see value2=35.28; the rest see value2=8.82. This leaf validates that nested callable dispatch propagates all values, including the index-dependent branch.

### callable_shader_invoked_via_closest_hit_single_invocation — chit invokes callable 0

The rgen shader traces each ray. For the 8 rays that hit the geometry, `build-closesthit-invoke-callable` invokes `build-callable-0` and stores 133 into `results[index].value0`. For the 4 rays that miss, `build-miss` (no callable invocation) leaves value0 at 0. `closestT` is 2.0 on hit and 1000.0 on miss.

### callable_shader_invoked_via_closest_hit_multiple_invocations — chit invokes three callables with index branch

Same as the closest-hit single leaf, plus `build-closesthit-invoke-callable-multi` invokes `build-callable-1` (value1=17.64) and a third callable chosen by `index < 4 ? 1 : 2`. The first 4 hitting rays see value2=35.28; the other 4 hitting rays see value2=8.82. The 4 missing rays keep value1 and value2 at 0.

### callable_shader_invoked_via_miss_single_invocation — miss invokes callable 0

The rgen shader traces each ray. For the 4 rays that miss the geometry, `build-miss-invoke-callable` invokes `build-callable-0` and stores 133 into `results[index].value0`. For the 8 hitting rays, `build-closesthit` (no callable invocation) leaves value0 at 0. `closestT` is 2.0 on hit and 1000.0 on miss.

### callable_shader_invoked_via_miss_multiple_invocations — miss invokes three callables with index branch

Same as the miss single leaf, plus `build-miss-invoke-callable-multi` invokes `build-callable-1` (value1=17.64) and a third callable chosen by `index < 10 ? 1 : 2`. The first 10 rays (8 hits plus the first 2 misses) see value2=35.28; the last 2 missing rays see value2=8.82. Note that value1 and value2 are only written by the miss shader, so the 8 hitting rays keep value1 and value2 at 0 even though the third callable's index cutoff includes them.

## Shader Analysis

The shaders are generated as inline GLSL strings in `initPrograms`. This page uses one walkthrough because the `rgen_call` rgen shader is the smallest case that exercises `executeCallableEXT` and the callable SBT region in isolation. Ordinary differences for the other leaves are summarized in the variation table and the behavior parameter subsections.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative leaf: `rgen_call`. Representative CTS path: `dEQP-VK.ray_tracing_pipeline.callable_shader.rgen_call`.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `rgen_call` | Tests the simplest callable dispatch from rgen. No ray is traced. |
| `SingleSquareConfiguration` | Uses the 8x8 r32ui image and 1-instance TLAS over a 2-triangle BLAS. |
| One callable shader group | The pipeline has rgen at index 0, chit at 1, miss at 2, and the callable at 3. Only rgen and the callable run. |
| `callableDataEXT uvec4 value` at location 0 | Single 16-byte callable data slot. |
| `executeCallableEXT(0, 0)` | Invokes the callable at SBT index 0 with callable data location 0. |

#### Purpose

This shader checks that `executeCallableEXT` from rgen runs the callable shader addressed by the callable SBT and that writes the callable makes to `callableDataInEXT` are visible to the rgen caller through its `callableDataEXT` declaration.

#### Structural Design

| Step | rgen shader | callable shader (`call_0`) | Meaning |
|------|-------------|----------------------------|---------|
| 1 | `executeCallableEXT(0, 0)` | enters with `callableDataInEXT uvec4 result` at location 0 | Hands the callable data slot to the callable. |
| 2 | waits for callable to return | `result = uvec4(1,0,0,1)` | Callable writes into the same storage the caller will read. |
| 3 | `imageStore(result, ivec2(gl_LaunchIDEXT.xy), value)` | returns | Caller observes the callable's writes and stores them into the result image. |

#### Shader Code

Reconstructed rgen GLSL for this leaf, faithful to the source string in [CallableShaderTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L571-L586):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) callableDataEXT uvec4 value;
layout(r32ui, set = 0, binding = 0) uniform uimage2D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  executeCallableEXT(0, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), value);
}
```

Reconstructed callable GLSL (`call_0`), faithful to [CallableShaderTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L678-L705):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) callableDataInEXT uvec4 result;
void main()
{
  result = uvec4(1,0,0,1);
}
```

The `topLevelAS` binding is declared in rgen because the shader build pipeline expects it for all rgen shaders in this configuration, but `rgen_call` never calls `traceRayEXT`, so the AS is bound but unused.

#### Additional Info

- The pipeline layout uses a single descriptor set with two bindings: storage image at 0 and acceleration structure at 1, both visible to all ray tracing stages [descriptor set layout](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L750-L754).
- The callable SBT region for `CSTT_RGEN_CALL` has one entry at the callable group index 3 [SBT construction](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L326-L348).
- The result image is cleared to `(0xFF, 0, 0, 0)` before `cmdTraceRays`. The expected reference is `(1, 0, 0, 0)` for every pixel because `call_0` writes `uvec4(1,0,0,1)` and the r32ui format stores only the .x channel [verifyImage](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L447-L449).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Nested callable | `rgen_call_call` uses the same rgen shader but a different callable shader `call_call` that itself calls `executeCallableEXT(1, 1)` to invoke `call_0`. | [call_call shader](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L707-L721) |
| Callable from chit / miss | `hit_call` uses the `rgen` shader that traces rays, plus `chit_call` and `miss_call` shaders that each invoke the callable. | [chit_call, miss_call](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L632-L676) |
| Multiple callable data types | `rgen_multicall` declares four `callableDataEXT` variables with types `uvec4`, `uint`, `CallValue`, `vec3` at locations 0, 1, 2, 4. | [rgen_multicall shader](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L588-L616) |
| Shader-record buffer | The shader-record invocation group uses `shaderRecordEXT` buffer storage inside the callable to read `CallableBuffer0` or `CallableBuffer1` parameters. | [build-callable-0](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1426-L1443), [build-callable-1](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1481-L1504) |
| Invoking stage | The shader-record group has separate rgen, chit, miss, and callable shader generators, each calling `executeCallableEXT` from its own stage. | [getRayGenSource, getClosestHitSource, getMissSource, getCallableSource](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1130-L1331) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 29
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %value %result %gl_LaunchIDEXT %topLevelAS
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %value "value"
               OpName %result "result"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %topLevelAS "topLevelAS"
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v4uint = OpTypeVector %uint 4
%_ptr_CallableDataKHR_v4uint = OpTypePointer CallableDataKHR %v4uint
      %value = OpVariable %_ptr_CallableDataKHR_v4uint CallableDataKHR
         %13 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_13 = OpTypePointer UniformConstant %13
     %result = OpVariable %_ptr_UniformConstant_13 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
         %26 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_26 = OpTypePointer UniformConstant %26
 %topLevelAS = OpVariable %_ptr_UniformConstant_26 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpExecuteCallableKHR %uint_0 %value
         %16 = OpLoad %13 %result
         %21 = OpLoad %v3uint %gl_LaunchIDEXT
         %22 = OpVectorShuffle %v2uint %21 %21 0 1
         %24 = OpBitcast %v2int %22
         %25 = OpLoad %v4uint %value
               OpImageWrite %16 %24 %25 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

Both test classes share the same support check: `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` must be present, with `rayTracingPipeline` and `accelerationStructure` feature bits set [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L530-L545).

### Simple image-output flow

- The host builds a 2-triangle BLAS forming a square in the 8x8 image area, then a 1-instance TLAS [initBottomAccelerationStructures](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L184-L212).
- The pipeline is assembled per `CallableShaderTestType`, mapping each type to its rgen / chit / miss / callable shader groups [initRayTracingShaders](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L228-L308).
- The host creates four SBT regions: raygen (1 entry), hit (1 entry), miss (1 entry), and callable (1 entry for `CSTT_RGEN_CALL`, `CSTT_HIT_CALL`; 2 entries for `CSTT_RGEN_CALL_CALL`; 4 entries for `CSTT_RGEN_MULTICALL`) [initShaderBindingTables](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L310-L429).
- The host clears an 8x8 r32ui storage image to `(0xFF, 0, 0, 0)`, transitions it to `GENERAL`, builds and binds the AS, then calls `cmdTraceRays` with dimensions 8x8x1 [runTest](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L809-L860).
- After submit, the host copies the image to a host-visible buffer and builds a reference image: clear to `missValue`, overwrite the inner 6x6 square with `hitValue` [verifyImage](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L431-L475).
- Pass condition: `tcu::intThresholdCompare` with zero threshold returns true.

### Shader-record invocation flow

- The host builds three BLAS, each with two geometries (one opaque, one non-opaque) and a vertex layer offset, then a 3-instance TLAS [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1862-L1888).
- The pipeline has rgen at index 0, miss at 1, chit at 2, and one or more callable groups starting at 3 [pipeline assembly](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1693-L1711).
- The callable SBT stride is `deAlign32(shaderGroupHandleSize + max(sizeof(CallableBuffer0), sizeof(CallableBuffer1)), shaderGroupHandleSize)`. The host writes `CallableBuffer0` and (when `multipleInvocations`) `CallableBuffer1` into the SBT entries right after the shader group handles [SBT setup](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1713-L1765).
- The host allocates a `results` buffer of 12 `Vec4` and a `rays` buffer of 12 pre-baked `Ray` structs, then calls `cmdTraceRays` with dimensions 12x1x1 [runTest body](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1836-L1912).
- After submit, the host invalidates and reads the `results` buffer. For each of 12 rays, `verifyResultData` checks `value0`, `value1`, `value2`, and `closestT` against expected values that depend on `hits[index]`, `params.invokingShader`, and `params.multipleInvocations` [verifyResultData](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1021-L1128).
- A `mismatch[32]` union aliased to `mismatchAll` records failing rays. Pass condition: `mismatchAll == 0` after all 12 rays are checked.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `rgen_call` | Callable dispatch from rgen did not deliver the callable's `callableDataInEXT` writes back to the caller's `callableDataEXT` storage, or the SBT callable region did not address the right callable. |
| `rgen_call_call` | Nested callable dispatch failed: the outer callable could not invoke another callable, or `callableDataEXT` / `callableDataInEXT` data did not flow through the chain. |
| `hit_call` | Callable dispatch from closest-hit or miss did not preserve the `+1` increment that `chit_call` performs after the callable returns, or hit/miss SBT indexing was wrong. |
| `rgen_multicall` | Multiple sequential `executeCallableEXT` calls with different data types (uvec4, uint, struct, vec3) and callable SBT indices did not all return their expected summed contributions. |
| `callable_shader_invoked_via_raygen_single_invocation` | Callable from rgen did not compute the expected value0=133 from the shader-record `CallableBuffer0` parameters, or the shader-record stride was wrong. |
| `callable_shader_invoked_via_raygen_multiple_invocations` | rgen invoked both callable 0 (uint) and callable 1 (float) but the second callable's float result (17.64) was missing or wrong, or the index-dependent third callable (35.28 / 8.82) returned the wrong value. |
| `callable_shader_invoked_via_callable_single_invocation` | A callable invoking another callable through `executeCallableEXT` did not run, or the outer callable's `callableDataInEXT` was not updated by the inner call. |
| `callable_shader_invoked_via_callable_multiple_invocations` | The nested callable chain did not propagate all expected values, including the index-dependent branch. |
| `callable_shader_invoked_via_closest_hit_single_invocation` | Callable dispatch from closest-hit did not run for the 8 rays that hit the geometry, or the hit-T (2.0f) was wrong. |
| `callable_shader_invoked_via_closest_hit_multiple_invocations` | Same as closest-hit single, plus the second and third callable invocations did not produce value1=17.64 and the index-dependent value2 (35.28 for index<4, 8.82 otherwise). |
| `callable_shader_invoked_via_miss_single_invocation` | Callable dispatch from miss did not run for the 4 rays that miss the geometry, or the miss-T (MAX_T_VALUE=1000.0f) was wrong. |
| `callable_shader_invoked_via_miss_multiple_invocations` | Same as miss single, plus the index-dependent value2 (35.28 for index<10, 8.82 otherwise) was wrong. |

All leaves share a common infrastructure: r32ui image comparison (simple group) or per-ray Vec4 comparison (invoke group). Either comparison produces a single pass/fail per leaf.

### Cause Analysis

#### Callable data not propagated back to caller

**Possible failure symptoms:** A `rgen_call` or `rgen_call_call` failure means the 8x8 result image is not uniformly `1` in the .x channel. For `rgen_call_call`, the image may still be `1` if the outer callable's `info` slot happened to match the expected value, but more likely the image is `0` or `0xFF` (the clear value) where the callable did not run or its writes did not reach the caller.

**Possible implementation causes:** The callable data storage is shared between the caller's `callableDataEXT` declaration and the callable's `callableDataInEXT` declaration through the `CallableDataKHR` storage class in SPIR-V. The SPIR-V walkthrough shows `OpExecuteCallableKHR %uint_0 %value` handing the `value` variable to the callable, and `OpImageWrite` reading `value` after the callable returns. A grounded investigation should check whether the implementation correctly aliases the callable data storage across the call boundary, whether the SBT entry at the requested index points to the callable shader, and whether the callable's writes are made visible to the caller before `OpExecuteCallableKHR` returns. Source-level inspection would be needed to distinguish a dispatch bug from a shader-compiler bug that lowered the callable data writes incorrectly.

#### Nested callable dispatch failure

**Possible failure symptoms:** A `rgen_call_call` or `callable_shader_invoked_via_callable_*` failure means the value produced by the inner callable did not reach the outer callable's `callableDataInEXT`. For `rgen_call_call`, the result image is `0` instead of `1`. For the shader-record callable leaves, `value0` is `0` instead of `133`.

**Possible implementation causes:** The outer callable declares its own `callableDataEXT` at a different location than its `callableDataInEXT` and calls `executeCallableEXT` with the inner callable's SBT index. A grounded investigation should check whether the implementation permits `executeCallableEXT` from inside a callable stage, whether the inner callable's `callableDataInEXT` correctly aliases the outer callable's `callableDataEXT`, and whether the SBT addressing for nested calls uses the same callable SBT region as direct calls. Source-level inspection would be needed if the failure only appears in nested call paths and not in direct call paths.

#### Callable from closest-hit or miss not dispatched

**Possible failure symptoms:** A `hit_call` or `callable_shader_invoked_via_closest_hit_*` failure means `value0` is `0` for rays that hit the geometry. A `callable_shader_invoked_via_miss_*` failure means `value0` is `0` for rays that miss the geometry. For `hit_call`, the inner 6x6 image is `0` or `1` instead of `2` (missing the `+1` increment), or the border is `0` instead of `1`.

**Possible implementation causes:** The callable dispatch path from chit or miss uses the same `OpExecuteCallableKHR` instruction as from rgen, but the calling shader is reached through ray traversal. A grounded investigation should check whether the implementation correctly handles callable dispatch from inside chit or miss, whether the `+1` increment in `chit_call` is preserved across the callable return, and whether the hit/miss SBT indexing routes the ray to the correct chit or miss shader in the first place. Source-level inspection would be needed if the failure only appears in one of chit or miss and not the other.

#### Multiple callable invocations with index-dependent branch

**Possible failure symptoms:** A `rgen_multicall` failure means the result image is not uniformly `16`. A `callable_shader_invoked_via_*_multiple_invocations` failure means `value1` is `0` instead of `17.64`, or `value2` is the wrong one of `35.28` and `8.82` for some rays.

**Possible implementation causes:** The multiple-invocation leaves call `executeCallableEXT` two or three times in sequence with different SBT indices and different `callableDataEXT` locations. The third call in the shader-record group uses an index-dependent branch (`index < 4`, `index < 6`, or `index < 10`) to select between `build-callable-1` and `build-callable-2`. A grounded investigation should check whether the implementation correctly handles multiple sequential `executeCallableEXT` calls in one shader invocation, whether each call addresses the right callable SBT entry, and whether the index-dependent branch evaluates correctly inside the shader. For `rgen_multicall`, the four callable data types (`uvec4`, `uint`, `CallValue`, `vec3`) and the arithmetic in the sum expression add type-mixing pressure that is worth inspecting if the failure is specific to that leaf.

#### Shader-record buffer read failure

**Possible failure symptoms:** A `callable_shader_invoked_via_*` failure where `value0` is `0` or some non-133 value, suggesting the callable did not read `CallableBuffer0` correctly. The 12-ray `mismatch` table would show all rays failing for the relevant invoking stage.

**Possible implementation causes:** The shader-record invocation group uses `shaderRecordEXT` buffer storage inside the callable to read parameters. The SBT stride is `deAlign32(shaderGroupHandleSize + max(sizeof(CallableBuffer0), sizeof(CallableBuffer1)), shaderGroupHandleSize)`, and the host writes the parameter block right after the shader group handle. A grounded investigation should check whether the implementation returns the correct shader record data to the callable, whether the SBT stride is honored, and whether the `shaderRecordEXT` buffer layout in the shader matches the host-side `CallableBuffer0` / `CallableBuffer1` struct layout. Source-level inspection would be needed if the failure only appears in the shader-record group and not in the simple image-output group.

#### Host-side image or buffer comparison error

**Possible failure symptoms:** The host reports failure but the shader-side reasoning does not explain the observed value. For the simple group, the result image has unexpected values that do not match any callable output. For the invoke group, the `results` buffer has values that do not match any expected combination of `value0`, `value1`, `value2`, and `closestT`.

**Possible implementation causes:** The host clears the result image or buffer, builds and binds resources, submits `cmdTraceRays`, copies the image to a host buffer (simple group) or invalidates the results buffer (invoke group), then reads back. A grounded investigation should check whether the image clear and layout transitions are correct, whether the image-to-buffer copy and the post-copy memory barrier are correct, whether the results buffer invalidation is correct, and whether the `verifyImage` or `verifyResultData` reference values match the actual shader output. Source-level inspection would be needed to distinguish a shader-side dispatch bug from a host-side copyback or comparison bug.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` extensions [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L530-L545) and [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L999-L1014).
- Both `rayTracingPipeline` and `accelerationStructure` feature bits must be set. If `accelerationStructure` is not set, the test throws `TestError` because `VK_KHR_ray_tracing_pipeline` requires it.
- No additional feature or limit gates are checked. The fixed 8x8 image and 12-ray buffer are well within any reasonable device limit.

### Design-based pruning

- The any-hit stage is intentionally excluded from the invoking stage axis. The source comment states callable shaders cannot be called from any-hit per `GLSL_NV_ray_tracing`, and the same is assumed for KHR [registration loop](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L2005-L2009).
- The simple group fixes the result image to 8x8 and the AS to a single square. The 6x6 inner hit area is small enough that ray traversal is not the tested property.
- The shader-record group fixes the 12-ray scene. The 8 hits and 4 misses are spread across three BLAS instances with mixed opaque / non-opaque geometries to give chit and miss invocations enough cases without expanding the matrix.
- The `multipleInvocations` axis only has two values (`false`, `true`). The third callable in the multiple-invocation path uses an index-dependent branch, but the branch cutoff is fixed per invoking stage and not a separate parameter.
- The shader-record SBT stride is fixed at `max(sizeof(CallableBuffer0), sizeof(CallableBuffer1))`. There is no separate axis for shader-record size.

## Key Takeaways

- The 12 leaves split into two mechanisms with different runtime shapes: a simple image-output group that isolates callable dispatch, and a shader-record invocation group that stresses per-stage dispatch with parameterized callables.
- `rgen_call` and `rgen_call_call` do not trace rays. They bind the AS for pipeline validity but never call `traceRayEXT`, so the entire 8x8 image is the callable output.
- `hit_call` is the only simple leaf where ray traversal affects the result. The `+1` increment in `chit_call` is what distinguishes the hit value `(2,0,0,0)` from the miss value `(1,0,0,0)`.
- The shader-record invocation group uses `shaderRecordEXT` buffer storage to pass `CallableBuffer0` and `CallableBuffer1` parameters into callable shaders. `CallableBuffer0` produces 133; `CallableBuffer1` produces 17.64 and halves to 8.82.
- The multiple-invocation leaves add an index-dependent third callable. The cutoff index depends on the invoking stage and on hit or miss, which gives the implementation less room to fold branches incorrectly.
- See `## Failure Meaning` for the per-leaf failure cause analysis. The most common failure shapes are callable data not propagating back to the caller, nested dispatch failure, chit or miss dispatch failure, multiple-invocation or index-branch failure, and shader-record read failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration root | [vktRayTracingCallableShadersTests.cpp#L1975-L2032](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1975-L2032) | Creates `callable_shader` group and attaches all 12 leaves |
| `CallableShaderTestType` enum | [vktRayTracingCallableShadersTests.cpp#L62-L69](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L62-L69) | Defines the 4 simple test types |
| `TestParams` struct | [vktRayTracingCallableShadersTests.cpp#L107-L115](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L107-L115) | Carries `callableShaderTestType`, `invokingShader`, `multipleInvocations` |
| Simple flow shader sources | [vktRayTracingCallableShadersTests.cpp#L547-L722](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L547-L722) | `initPrograms` for `CallableShaderTestCase`: emits `rgen`, `rgen_call`, `rgen_multicall`, `chit`, `chit_call`, `miss`, `miss_call`, `call_0..3`, `call_call` |
| Simple flow pipeline assembly | [vktRayTracingCallableShadersTests.cpp#L228-L308](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L228-L308) | Maps each `CallableShaderTestType` to its shader groups |
| Simple flow SBT construction | [vktRayTracingCallableShadersTests.cpp#L310-L429](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L310-L429) | Per-type SBT entry counts and strides |
| Simple flow image verification | [vktRayTracingCallableShadersTests.cpp#L431-L475](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L431-L475) | `verifyImage` reference values per `CallableShaderTestType` |
| Simple flow runtime | [vktRayTracingCallableShadersTests.cpp#L739-L883](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L739-L883) | `runTest` body: descriptor set, pipeline, SBT, image, trace, copyback |
| Invoke flow shader generators | [vktRayTracingCallableShadersTests.cpp#L1130-L1331](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1130-L1331) | `getRayGenSource`, `getClosestHitSource`, `getMissSource`, `getCallableSource` |
| Invoke flow shader build helpers | [vktRayTracingCallableShadersTests.cpp#L1333-L1397](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1333-L1397) | `generateShaderSource` and `addShaderSource` shared prefix builders |
| Invoke flow shader record buffer setup | [vktRayTracingCallableShadersTests.cpp#L1713-L1765](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1713-L1765) | Builds SBT with extra `CallableBuffer0` / `CallableBuffer1` data |
| Invoke flow per-ray verification | [vktRayTracingCallableShadersTests.cpp#L1021-L1128](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1021-L1128) | `verifyResultData` expected-value table |
| Invoke flow 12-ray geometry | [vktRayTracingCallableShadersTests.cpp#L1784-L1834](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1784-L1834) | 12 rays, 3 BLAS, opaque / non-opaque mix |
| Invoke flow runtime | [vktRayTracingCallableShadersTests.cpp#L1565-L1971](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1565-L1971) | `iterate` body: pipeline, SBT, descriptor set, trace, readback, mismatch check |
| checkSupport | [vktRayTracingCallableShadersTests.cpp#L530-L545](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L530-L545) and [vktRayTracingCallableShadersTests.cpp#L999-L1014](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L999-L1014) | Required features for both test classes |
