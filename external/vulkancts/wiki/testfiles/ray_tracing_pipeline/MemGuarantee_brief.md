# Understanding Brief: ray_tracing_pipeline.memguarantee

## One-Sentence Test Purpose

This test checks whether a ray tracing implementation honors the Vulkan memory model's shader-call visibility guarantee, so that a storage image write performed by one shader invocation is observable (inside the same invocation, or across a shader-call boundary in a subsequent invocation) under the `gl_ScopeShaderCallEXT` release/acquire pair and the `shadercallcoherent` qualifier.

## Background Knowledge

### Shader-call scope and the repack boundary

In the Vulkan memory model, `gl_ScopeShaderCallEXT` (`ShaderCallKHR` in SPIR-V) covers the set of shader invocations reachable through ray tracing shader-call instructions: `executeCallableEXT`, `traceRayEXT`, and `reportIntersectionEXT`. A memory release performed by the caller before one of these instructions must be made available to the callee invocation that an acquire on the same scope synchronizes with.

Why it matters here:
- The `between` test variant performs `imageStore(r)` in the caller, a release barrier with `gl_ScopeShaderCallEXT`, then the repack instruction. The callee performs an acquire barrier with the same scope, then `imageLoad` must observe `r`.
- The repack instruction is the boundary the test exercises. For `rgen`, `chit`, `miss`, and `call` it is `executeCallableEXT(0, 0)`, calling a callable shader. For `sect` it is `reportIntersectionEXT(0.95f, 0u)`, which routes the callee through the any-hit shader.

### Intra-invocation visibility

A shader invocation can always observe its own prior writes to a non-coherent variable, because each invocation has a program order with itself. No barrier or qualifier is required for the same invocation to read back its own write.

Why it matters here:
- The `inside` variant places both `imageStore(r)` and `imageStore(d+1)` in the same invocation of the stage under test, separated only by the repack instruction. The image is not declared `shadercallcoherent`, and no release/acquire barrier is emitted. The `imageLoad` after the repack must still return `r`, proving the implementation did not lose the prior write across the repack.

## One Concrete Example

Reconstructed caller body for `ray_tracing_pipeline.memguarantee.between.rgen`, derived from `initPrograms` with `TEST_TYPE_BETWEEN_STAGES` and `stage = VK_SHADER_STAGE_RAYGEN_BIT_KHR`:

```glsl
layout(set = 0, binding = 0, r32ui) shadercallcoherent uniform uimage2D result;
layout(location = 0) callableDataEXT float dummy;

void main()
{
  uint  r = uint(gl_LaunchIDEXT.x + gl_LaunchSizeEXT.x * gl_LaunchIDEXT.y);
  uvec4 c = uvec4(r, 0, 0, 1);
  imageStore(result, ivec2(gl_LaunchIDEXT), c);

  memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsRelease);

  executeCallableEXT(0, 0);
}
```

Reconstructed callee (`cal0`) body for the same case:

```glsl
layout(location = 0) callableDataInEXT float dummy;
layout(set = 0, binding = 0, r32ui) uniform uimage2D result;

void main()
{
  memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsAcquire);
  uint  d = imageLoad(result, ivec2(gl_LaunchIDEXT)).x;
  imageStore(result, ivec2(gl_LaunchIDEXT), uvec4(d + 1, 0, 0, 1));
}
```

Pixel at launch `(x, y)` writes `r = x + width * y` from rgen, then the callable reads `d` (must equal `r` after the acquire), and stores `r + 1`. The host expects each pixel to read back `pos + 1`, where `pos = y * width + x`.

## End-to-End Test Flow

```text
[host] require VK_KHR_acceleration_structure and VK_KHR_ray_tracing_pipeline features
[host] build a 16x16 r32ui storage image, cleared to 1000000u
[host] build BLAS instances covering 16x16 = 256 squares across 8 instances and 4 geometries per instance (8 squares per geometry); for `miss` cases the geometry is placed at z = +1.0 so rays miss
[host] build a one-instance-per-BLAS TLAS
[host] compile rgen + (chit|miss|sect|call) + callee (cal0 or ahit) + passthrough hit/miss/intersection shaders as needed
[host] build ray tracing pipeline with raygen, miss, hit, and callable shader groups; build SBT regions
[device] rgen launches 16x16x1; for `rgen` cases the rgen writes the image and calls the callee; for other stages rgen traces a ray or calls a callable shader that performs the writes
[device] caller stage writes r, releases, repacks; callee (or same invocation for `inside`) acquires, loads d, writes d+1
[device] miss shader for `miss` cases performs the writes; rays are routed so they hit nothing
[host] copy image to host-visible buffer, invalidate mapped range, scan all 256 pixels
[host] pass iff every pixel at position pos equals pos + 1; otherwise report failure count
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL strings emitted by `RayTracingTestCase::initPrograms` with `SPIRV_VERSION_1_4`. Source: [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L301-L506).
- The generated shader set depends on which stage is under test:
  - `rgen` case: `rgen` + `cal0`.
  - `chit` case: shared `rgen` + `chit` + `cal0` + passthrough `ahit`, `miss`, `sect`.
  - `miss` case: shared `rgen` + `miss` + `cal0` + passthrough `ahit`, `chit`, `sect`.
  - `sect` case: shared `rgen` + `sect` + `ahit` (the callee) + passthrough `chit`, `miss`.
  - `call` case: `rgen` (only calls `executeCallableEXT(1, 0)`) + `call` (the stage under test) + `cal0`.
- Two conditionally injected strings change between `inside` and `between`:
  - `glslExtensions` adds `#extension GL_KHR_memory_scope_semantics : require` for `between` only.
  - `imageQualifiers` adds ` shadercallcoherent ` to the caller's image declaration for `between` only.
  - `updateBarrierCaller`/`updateBarrierCallee` add the release/acquire `memoryBarrier(gl_ScopeShaderCallEXT, ...)` calls for `between` only; for `inside` both strings are empty.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result` storage image (`r32ui`, 16x16) | yes | yes, binding 0 | yes, written by caller and callee, read by callee | yes, copied to host buffer | The single shared image whose pixel values encode pass/fail. |
| Top-level acceleration structure | yes | yes, binding 1 | yes, read by `traceRayEXT` | no | Routes rays to the hit group so `chit`, `sect`, or `miss` runs. |
| Bottom-level acceleration structures (8 instances, 4 geometries each) | yes | yes | yes, read during traversal | no | Provides the 256-square scene that gives each launch invocation a unique hit. |
| Host-visible copyback buffer (`VK_BUFFER_USAGE_TRANSFER_DST_BIT`) | yes | yes | yes, written by `cmdCopyImageToBuffer` | yes | Carries the final image back for the host scan. |
| Shader binding table regions (raygen, miss, hit, callable) | yes | yes | yes, read by `cmdTraceRays` | no | Selects which shader runs for each trace. |

## What Is Checked

- Each pixel at position `pos = y * width + x` must equal `pos + 1` after the trace. Source: [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L826-L852).
- The check is on the host, against a host-visible buffer filled by `cmdCopyImageToBuffer`.
- There is no tolerance: any pixel mismatch increments the failure counter. A single failing pixel fails the case.
- The clear value `1000000u` is far outside the expected range `[1, 256]`, so an unwritten pixel (failed imageStore, failed barrier, or failed callee execution) is detected as a mismatch.
- Each of the 10 test case leaves is checked independently. There is no aggregation across cases.

## Behavior Parameter Identification

> **Behavior parameter:** `TestType` intermediate node (`between` vs `inside`)
>
> **Candidate values:** `between`, `inside`

The stage dimension (`rgen`, `chit`, `miss`, `sect`, `call`) is a configuration dimension that varies which shader call mechanism is exercised, not what property is being tested. It is captured in `## Parameter Dimensions and Observed Values` of the final page.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `between` | Cross-shader-call visibility failure: the callee did not observe the caller's `imageStore(r)` after the release/acquire pair on `gl_ScopeShaderCallEXT`, or the `shadercallcoherent` qualifier was not honored. |
| `inside` | Intra-invocation write lost: the same shader invocation did not observe its own prior `imageStore(r)` after the repack instruction, with no barrier or qualifier required. |
| (all stages of one test type) | A single stage-specific shader dispatch or SBT routing bug, distinguishable by which stage leaves fail. |
| (all cases) | Shared image-clear, trace, or copyback infrastructure failure, distinguishable by pixels reading back the clear value `1000000u` or by failures across both test types. |

## Important Variations and Special Cases

- The `sect` case is the only case where the callee is an any-hit shader reached through `reportIntersectionEXT`, instead of a callable shader reached through `executeCallableEXT`. The repack instruction in the intersection shader is `reportIntersectionEXT(0.95f, 0u)`. The intersection passthrough reports with hit kind `0x7Eu`; the test repack uses kind `0u`. The any-hit callee is the `calleeShader` body. This case still tests the same `gl_ScopeShaderCallEXT` property, but through a different shader-call mechanism.
- The `miss` case places geometry at `z = +1.0` so the ray travels down `-Z` and hits nothing, routing execution to the miss shader. The miss shader performs the writes and repack.
- The `call` case uses a two-level callable invocation: rgen calls `executeCallableEXT(1, 0)` to invoke the `call` shader (the stage under test), which performs the writes and then `executeCallableEXT(0, 0)` to invoke `cal0` (the callee). The `call` shader is at SBT index `callableShaderGroup + 1`, and `cal0` is at `callableShaderGroup`.
- The image is declared `shadercallcoherent` only on the caller side. The callee reads the same binding without that qualifier. The release/acquire barriers carry the synchronization; the qualifier is the redundant opt-in.
- The clear value `1000000u` is intentionally far outside the expected `[1, 256]` range so that unwritten pixels are immediately distinguishable from a one-off increment error.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CaseDef` and `TestType` enum | [vktRayTracingMemGuaranteeTests.cpp#L54-L69](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L54-L69) | Defines the two behavior parameter values and the per-case configuration. |
| `initPrograms` shader emission | [vktRayTracingMemGuaranteeTests.cpp#L301-L506](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L301-L506) | Source of the reconstructed walkthrough shaders and the `inside`/`between` conditional strings. |
| `imageQualifiers`, `glslExtensions`, barrier strings | [vktRayTracingMemGuaranteeTests.cpp#L305-L331](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L305-L331) | Encodes the `between` vs `inside` shader-level difference. |
| `runTest` resource setup, trace, copyback | [vktRayTracingMemGuaranteeTests.cpp#L651-L801](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L651-L801) | Host-side flow: image clear, AS build, SBT, trace, copyback, host invalidation. |
| `iterate` pass/fail check | [vktRayTracingMemGuaranteeTests.cpp#L826-L852](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L826-L852) | Encodes the `pos + 1` expected value and the failure counter. |
| `checkSupport` feature gates | [vktRayTracingMemGuaranteeTests.cpp#L243-L258](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L243-L258) | Requires the two KHR feature bits. |
| Registration loop | [vktRayTracingMemGuaranteeTests.cpp#L855-L908](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L855-L908) | Builds the two test type groups and the five stage leaves each. |
| Mustpass evidence | [ray-tracing-pipeline.txt#L13027-L13036](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt#L13027-L13036) | Lists all 10 registered leaves. |

## Questions / Risk Points for User Audit

- Is the core test purpose (shader-call scope memory visibility, inside vs between) clear?
- Is the host/device timeline understandable, especially the dual role of the `result` image as both the test vehicle and the readback surface?
- Is the distinction between `shadercallcoherent` (declaration qualifier) and `memoryBarrier(gl_ScopeShaderCallEXT, ...)` (explicit barrier) preserved correctly?
- Is the `sect` case's any-hit callee clearly distinguished from the callable-shader callee used by the other four stages?
- Is the failure cause mapping for `inside` versus `between` sharp enough to guide a triager?

## Conversion Notes for Final Wiki Rewrite

- The `Background Knowledge` list should distill to: shader-call scope and the repack boundary; intra-invocation visibility; the `shadercallcoherent` qualifier and the release/acquire barrier pair.
- The concrete example should become the representative walkthrough for `between.rgen`. The `inside` counterpart should appear as a parameter variation note, not a second walkthrough.
- The `sect` variation should be mentioned in `## Behavior Parameters` and `## Parameter Dimensions and Observed Values`, not as a separate walkthrough.
- The `### Failure Cause Mapping` table from `## What Failure Means` should be copied directly into the final page's `### Failure Cause Mapping`. The `### Cause Analysis` is written fresh during the rewrite.
- The end-to-end flow should be condensed into `## Runtime Execution and Result Checking` bullets; the resource table can be summarized there.
- The clear value `1000000u` should be mentioned as the canary for unwritten pixels.
