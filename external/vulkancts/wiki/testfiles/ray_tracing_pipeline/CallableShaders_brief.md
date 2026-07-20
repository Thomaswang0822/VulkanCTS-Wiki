# Understanding Brief: ray_tracing_pipeline.callable_shader

## One-Sentence Test Purpose

This test checks whether a `VK_KHR_ray_tracing_pipeline` implementation correctly dispatches callable shaders through `executeCallableEXT` from raygen, closest-hit, miss, and callable stages, including single invocations, multiple invocations, and nested callable-from-callable invocations.

## Background Knowledge

### Callable shaders in `VK_KHR_ray_tracing_pipeline`

A callable shader is a ray tracing pipeline stage entered through `executeCallableEXT(shaderIndex, location)` rather than through ray traversal. The calling shader declares outgoing callable data with `callableDataEXT` at a `location`; the callable shader receives that storage through `callableDataInEXT` at the same `location`. After the callable returns, the caller observes any writes the callable made to that storage.

Why it matters here:

- The test isolates the callable dispatch mechanism from ray traversal in most cases. Several leaves never call `traceRayEXT` and still expect the callable to run.
- Callable shaders are addressed through the callable shader binding table region. Multi-callable tests rely on SBT indexing and stride, so the callable SBT region construction is part of the tested behavior.
- A callable shader can itself invoke another callable. The nested call tests check that callable dispatch is permitted from inside a callable stage and that data flows through the chain.

### Shader record buffer for callable input

The `InvokeCallableShaderTestCase` matrix uses `shaderRecordEXT` buffer storage to pass parameters (`base`, `shift`, `offset`, `multiplier` for `CallableBuffer0`; `numerator`, `denomenator`, `power`, `reserved` for `CallableBuffer1`) into callable shaders. The shader record is per callable SBT entry; the host writes the parameters into the SBT entries directly during `createShaderBindingTable` with extra data after each shader group handle.

Why it matters here:

- This separates "what the callable does" from "where it gets its inputs". The callable reads parameters from its own SBT entry, computes a value, and writes it back into the callable data slot.
- The SBT stride is `shaderGroupHandleSize + max(sizeof(CallableBuffer0), sizeof(CallableBuffer1))` aligned to `shaderGroupHandleSize`, so each callable entry has room for both the handle and the parameter block.

### Limitation: callable shaders cannot be invoked from any-hit

The source comment at registration states callable shaders cannot be called from any-hit per `GLSL_NV_ray_tracing` and the same restriction is assumed for KHR. This is why `glu::SHADERTYPE_ANY_HIT` is absent from the `invokingShaders` array.

## One Concrete Example

`rgen_call` is the simplest leaf. The rgen shader declares `callableDataEXT uvec4 value` at location 0, calls `executeCallableEXT(0, 0)`, then writes `value` into a storage image. The callable shader `call_0` receives `callableDataInEXT uvec4 result` at location 0 and writes `result = uvec4(1,0,0,1)`. The 8x8 result image is expected to be all `1` in the .x channel.

Reconstructed rgen GLSL (faithful to source):

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

Reconstructed callable GLSL (`call_0`):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) callableDataInEXT uvec4 result;
void main()
{
  result = uvec4(1,0,0,1);
}
```

The pipeline for this leaf has four shader groups: rgen at index 0, chit at 1, miss at 2, and the callable at 3. The chit and miss groups are present in the pipeline but are never reached because rgen never calls `traceRayEXT`.

## End-to-End Test Flow

The file owns two structurally different test classes, so the flow has two shapes.

### Simple image-output flow (`CallableShaderTestCase`, `SingleSquareConfiguration`)

```text
[host] require VK_KHR_acceleration_structure and VK_KHR_ray_tracing_pipeline; require rayTracingPipeline feature
[host] build a 2-triangle bottom-level AS forming a square in the 8x8 image area
[host] build a 1-instance top-level AS referencing the BLAS
[host] create ray tracing pipeline with rgen + chit + miss + 1-or-more callable shader groups
[host] create raygen / hit / miss / callable SBT regions, one entry per group
[host] allocate 8x8 r32ui storage image, clear to (0xFF,0,0,0)
[host] trace rays with dimensions 8x8x1
[device] rgen (and for hit_call, also chit/miss) executes executeCallableEXT, callable writes callableData
[device] rgen (or chit/miss) writes callableData into the storage image
[host] copy image to host-visible buffer
[host] compare to a reference image: border = missValue, inner square = hitValue
[host] pass if int-threshold-compare is exact
```

### Shader-record invocation flow (`InvokeCallableShaderTestCase`)

```text
[host] require VK_KHR_acceleration_structure and VK_KHR_ray_tracing_pipeline; require rayTracingPipeline feature
[host] build three BLAS with two geometries each (opaque + non-opaque), with vertex layers
[host] build a 3-instance TLAS
[host] create ray tracing pipeline: rgen + miss + chit + callable group(s)
[host] build callable SBT with stride = align(shaderGroupHandleSize + max(sizeof(CallableBuffer0), sizeof(CallableBuffer1)), shaderGroupHandleSize)
[host] write CallableBuffer0 (and CallableBuffer1 when multipleInvocations) into the SBT entries after the shader group handles
[host] allocate results buffer (12 * sizeof(Vec4)) and rays buffer (12 * sizeof(Ray))
[host] trace rays with dimensions 12x1x1
[device] rgen traces each ray; depending on invokingShader, callable is invoked from rgen, chit, miss, or callable stage
[device] callable reads parameters from shaderRecordEXT, computes a value, writes it into callableData
[device] results[index] records value0, value1, value2, closestT
[host] invalidate and read results buffer
[host] for each of 12 rays, compare value0/1/2 and closestT against expected values that depend on hits[index], invokingShader, and multipleInvocations
[host] pass if all 12 rays match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL strings for `rgen`, `rgen_call`, `rgen_multicall`, `chit`, `chit_call`, `miss`, `miss_call`, `call_0..3`, `call_call` in `CallableShaderTestCase::initPrograms`. All use `#version 460 core` + `#extension GL_EXT_ray_tracing : require`.
- Inline GLSL strings generated by `getRayGenSource`, `getClosestHitSource`, `getMissSource`, `getCallableSource` in `InvokeCallableShaderTestCase::initPrograms`. These use a shared prefix that declares `Ray`, `Result`, `scene`, `rays`, and `launchIndex()` helper.
- The shader build options pin `vk::SPIRV_VERSION_1_4` regardless of Vulkan runtime version. This is the SPIR-V target for any walkthrough.
- The callable shader record buffer layout is fixed: `CallableBuffer0 { uint base; uint shift; uint offset; uint multiplier; }` and `CallableBuffer1 { float numerator; float denomenator; uint power; uint reserved; }`.

### Bound resources and memory objects

Simple image-output flow:

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result` r32ui storage image | yes | yes (binding 0) | written by rgen (or chit/miss) | yes, copied to host buffer | Holds the callable output as one uint per pixel |
| `topLevelAS` acceleration structure | yes | yes (binding 1) | read by rgen for `traceRayEXT` | no | Required to make `traceRayEXT` valid; for `rgen_call` and `rgen_call_call` the AS is bound but never traced |
| Raygen / hit / miss / callable SBT buffers | yes | yes (SBT regions) | read by `cmdTraceRays` | no | Selects which callable to run for each `executeCallableEXT` shader index |

Shader-record invocation flow:

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `results` storage buffer (12 * Vec4) | yes | yes (binding 0) | written by rgen | yes | One Vec4 per ray: value0, value1, value2, closestT |
| `scene` TLAS | yes | yes (binding 1) | read by rgen for `traceRayEXT` | no | Three instances with mixed opaque / non-opaque geometries |
| `rays` storage buffer (12 * Ray) | yes | yes (binding 2) | read by rgen | no | Pre-baked ray origins and directions for the 12 hit/miss scenarios |
| callable SBT with shader-record extra data | yes | yes (callable SBT region) | read by callable shaders via `shaderRecordEXT` | no | Carries `CallableBuffer0` / `CallableBuffer1` parameters next to each callable group handle |

## What Is Checked

### Simple image-output flow

- After `cmdTraceRays` over 8x8x1, copy the result image to a host buffer.
- Build a reference image: clear to `missValue`, then overwrite the inner 6x6 square (x in [1,6], y in [1,6]) with `hitValue`.
- Expected values per `CallableShaderTestType`:

  | Type | missValue | hitValue | Why |
  |------|-----------|----------|-----|
  | `CSTT_RGEN_CALL` | (1,0,0,0) | (1,0,0,0) | rgen invokes callable 0; no ray is traced, so the entire image is the callable output |
  | `CSTT_RGEN_CALL_CALL` | (1,0,0,0) | (1,0,0,0) | rgen invokes `call_call` which invokes `call_0`; both write 1 |
  | `CSTT_HIT_CALL` | (1,0,0,0) | (2,0,0,0) | rgen traces a ray; chit invokes callable then adds 1; miss invokes callable but does not add 1 |
  | `CSTT_RGEN_MULTICALL` | (16,0,0,0) | (16,0,0,0) | rgen invokes 4 callables with different data types and sums their outputs to 16 |

- Compare result and reference with `tcu::intThresholdCompare` and zero threshold.

### Shader-record invocation flow

- After `cmdTraceRays` over 12x1x1, invalidate and read the `results` buffer.
- For each of 12 rays, the expected `value0`, `value1`, `value2`, and `closestT` depend on `hits[index]` (true/false), `params.invokingShader`, and `params.multipleInvocations`.
- `value0` is 133.0f when the corresponding invoking shader ran the callable, otherwise 0.0f.
- `value1` is 17.64f when `multipleInvocations` is true and the invoking shader ran, otherwise 0.0f.
- `value2` is 35.28f or 8.82f when `multipleInvocations` is true; the cutoff index depends on the invoking shader and hit/miss (e.g. `index < 4` for closest-hit on hit, `index < 6` for callable, `index < 10` for miss on miss).
- `closestT` is 2.0f on hit (because geometry z=2.0) and `MAX_T_VALUE` (1000.0f) on miss.
- Float comparison uses `compareFloat` with epsilon 0.01f.
- A `mismatch[32]` union with `mismatchAll` records any failing ray; the test fails if `mismatchAll != 0`.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf under `ray_tracing_pipeline.callable_shader`
>
> **Candidate values:** `rgen_call`, `rgen_call_call`, `hit_call`, `rgen_multicall`, `callable_shader_invoked_via_raygen_single_invocation`, `callable_shader_invoked_via_raygen_multiple_invocations`, `callable_shader_invoked_via_callable_single_invocation`, `callable_shader_invoked_via_callable_multiple_invocations`, `callable_shader_invoked_via_closest_hit_single_invocation`, `callable_shader_invoked_via_closest_hit_multiple_invocations`, `callable_shader_invoked_via_miss_single_invocation`, `callable_shader_invoked_via_miss_multiple_invocations`

The 12 leaves group into two mechanisms:

1. Simple image-output group (4 leaves): `rgen_call`, `rgen_call_call`, `hit_call`, `rgen_multicall`. Each leaf changes how callable dispatch is structured (single direct call, nested call, call from hit/miss, or multiple calls with different data types).
2. Shader-record invocation group (8 leaves = 4 invoking stages x 2 invocation counts): the `callable_shader_invoked_via_*` family. The invoking stage axis changes which shader stage calls `executeCallableEXT`; the invocation count axis changes whether one or two callable shaders run per ray.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `rgen_call` | Callable dispatch from rgen did not deliver the callable's `callableDataInEXT` writes back to the caller's `callableDataEXT` storage, or the SBT callable region did not address the right callable. |
| `rgen_call_call` | Nested callable dispatch failed: the outer callable could not invoke another callable, or `callableDataEXT`/`callableDataInEXT` data did not flow through the chain. |
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

## Important Variations and Special Cases

- **`rgen_call` and `rgen_call_call` do not trace rays.** They bind the top-level AS but the rgen shader never calls `traceRayEXT`. The hit and miss shader groups are still in the pipeline but unreachable. This isolates the callable dispatch path from ray traversal.
- **`hit_call` is the only simple leaf where ray tracing matters for the result.** The rgen shader traces rays; the inner 6x6 square hits the BLAS triangle and runs `chit_call` which invokes the callable and increments by 1; the border misses and runs `miss_call` which invokes the callable without the increment. The hit/miss values differ: `(2,0,0,0)` vs `(1,0,0,0)`.
- **`rgen_multicall` invokes four callables with four different `callableDataEXT` types** in a single rgen invocation: `uvec4` at location 0, `uint` at location 1, `CallValue` struct at location 2, `vec3` at location 4. The callable SBT has four callable entries. The expected sum is 16 because `call_0`=1 + `call_1`=2 + `call_2`.a.x*floor(b.y)=3*3=9 + `call_3`.z=4 (floored) = 16.
- **`callable_shader_invoked_via_callable_*` uses a nested callable-from-callable dispatch.** The outer callable `build-callable-invoke-callable` reads `callableDataInEXT` and writes to its own `callableDataEXT` after invoking another callable through `executeCallableEXT(1, CALLABLE_DATA_UINT_OUT_LOC)`. This stresses that callable dispatch is permitted from inside a callable stage.
- **The shader-record extra-data SBT stride is variable.** It is `deAlign32(shaderGroupHandleSize + max(sizeof(CallableBuffer0), sizeof(CallableBuffer1)), shaderGroupHandleSize)`. If the implementation mishandles SBT stride with extra data, the callable would read garbage from `shaderRecordEXT`.
- **The 12-ray `InvokeCallableShaderTestCase` geometry is intentional.** 8 rays hit, 4 miss, with mixed opaque / non-opaque geometries spread across three BLAS instances. This gives the closest-hit and miss invocation axes enough cases to validate per-ray callable dispatch.
- **The any-hit stage is intentionally excluded.** The source comment at the registration loops states callable shaders cannot be called from any-hit per `GLSL_NV_ray_tracing` and the same is assumed for KHR.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration root | [vktRayTracingCallableShadersTests.cpp#L1975-L2032](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1975-L2032) | Creates `callable_shader` group and attaches all 12 leaves |
| `CallableShaderTestType` enum | [vktRayTracingCallableShadersTests.cpp#L62-L69](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L62-L69) | Defines the 4 simple test types |
| `TestParams` struct | [vktRayTracingCallableShadersTests.cpp#L107-L115](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L107-L115) | Carries `callableShaderTestType`, `invokingShader`, `multipleInvocations` |
| Simple flow shaders | [vktRayTracingCallableShadersTests.cpp#L547-L722](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L547-L722) | `initPrograms` for `CallableShaderTestCase`: emits `rgen`, `rgen_call`, `rgen_multicall`, `chit`, `chit_call`, `miss`, `miss_call`, `call_0..3`, `call_call` |
| Simple flow pipeline assembly | [vktRayTracingCallableShadersTests.cpp#L228-L308](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L228-L308) | Maps each `CallableShaderTestType` to its shader groups |
| Simple flow SBT construction | [vktRayTracingCallableShadersTests.cpp#L310-L429](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L310-L429) | Per-type SBT entry counts and strides |
| Simple flow image verification | [vktRayTracingCallableShadersTests.cpp#L431-L475](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L431-L475) | `verifyImage` reference values per `CallableShaderTestType` |
| Invoke flow shader generators | [vktRayTracingCallableShadersTests.cpp#L1130-L1331](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1130-L1331) | `getRayGenSource`, `getClosestHitSource`, `getMissSource`, `getCallableSource` |
| Invoke flow shader record buffer setup | [vktRayTracingCallableShadersTests.cpp#L1713-L1765](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1713-L1765) | Builds SBT with extra `CallableBuffer0`/`CallableBuffer1` data |
| Invoke flow per-ray verification | [vktRayTracingCallableShadersTests.cpp#L1021-L1128](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1021-L1128) | `verifyResultData` expected-value table |
| Invoke flow 12-ray geometry | [vktRayTracingCallableShadersTests.cpp#L1784-L1834](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L1784-L1834) | 12 rays, 3 BLAS, opaque / non-opaque mix |
| checkSupport | [vktRayTracingCallableShadersTests.cpp#L530-L545](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L530-L545) and [vktRayTracingCallableShadersTests.cpp#L999-L1014](../../../modules/vulkan/ray_tracing/vktRayTracingCallableShadersTests.cpp#L999-L1014) | Required features for both test classes |

## Questions / Risk Points for User Audit

- Is the grouping of 12 leaves into "simple image-output" and "shader-record invocation" the right behavioral split, or should the page treat all 12 as a single flat axis?
- The `rgen_multicall` expected sum is 16 from `call_0`=1 + `call_1`=2 + `call_2`.a.x*floor(b.y)=3*3=9 + floor(`call_3`.z)=4 = 16. Is this arithmetic correct?
- For `callable_shader_invoked_via_callable_*`, is "nested callable-from-callable" the right description, given that the inner callable uses a different `callableDataEXT` location (2) than the outer callable's `callableDataInEXT` (0)?
- The `InvokeCallableShaderTestCase` mixes opaque and non-opaque geometries across 3 BLAS. The page currently treats this as background detail and not a behavioral axis. Is that the right call?
- Should the page include a second SPIR-V walkthrough for `call_call` (nested callable) or `rgen_multicall` (multiple data types), or is one walkthrough enough?

## Conversion Notes for Final Wiki Rewrite

- Distill Background Knowledge into a brief bullet list: callable shaders and `executeCallableEXT`, `callableDataEXT`/`callableDataInEXT`, SBT callable region, shader-record buffer for the invoke group.
- Use the `rgen_call` rgen shader as the single representative walkthrough. It is the simplest case that exercises `executeCallableEXT` and the callable SBT region in isolation, and its GLSL is short enough to compile and disassemble inline.
- The `### Failure Cause Mapping` table above should be copied directly into the final page's `## Failure Meaning` -> `### Failure Cause Mapping`.
- Move the source-navigation material (function-name inventory, line ranges) into `## Source Reference Appendix`.
- The 12-leaf behavior axis should be split into two groups in `## Behavior Parameters`: simple image-output (4 subsections) and shader-record invocation (8 subsections), each with the mandated `### <value> — <description>` em-dash header.
- Skip listing every `initPrograms` string in the final page; instead summarize what is generated and reference the source range.
- The brief's beginner-friendly `Background Knowledge` should be distilled, not copied verbatim, into the final page's `Background Knowledge` list.
