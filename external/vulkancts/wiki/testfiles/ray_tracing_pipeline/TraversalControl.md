## Overview

**Core question:** Does a ray tracing pipeline honor the any-hit shader's `ignoreIntersectionEXT`, `terminateRayEXT`, and pass-through behavior, and the intersection shader's `reportIntersectionEXT` decision, so that each operation produces the spec-mandated set of subsequent hit stages?

- [vktRayTracingTraversalControlTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp) implements and registers the `traversal_control` test family under the `ray_tracing_pipeline` test category.
- Five test case leaves vary the any-hit or intersection shader body across `isect_report_intersection`, `isect_dont_report_intersection`, `ahit_pass_through`, `ahit_ignore_intersection`, and `ahit_terminate_ray`. Each leaf has a `triangles` or `aabbs` bottom-geometry child.
- The core idea is one shared ray setup and one shared single-square acceleration structure. Only the traversal-control instruction under test changes between cases, so the resulting two-layer image directly reflects which hit stages ran.
- A two-layer `r32ui` result image separates the any-hit or miss contribution (layer 0, written through `hitValue.x`) from the closest-hit contribution (layer 1, written through `hitValue.y`). The host builds a per-case reference image and compares with a zero threshold.

## Background Knowledge

- **Ray tracing pipeline hit stages.** Raygen calls `traceRayEXT`. For each candidate intersection the runtime runs the any-hit shader; after traversal finds the closest accepted intersection it runs the closest-hit shader. If no candidate is accepted it runs the miss shader. The intersection shader runs only for procedural (AABB) geometry, where the shader must call `reportIntersectionEXT` to declare a candidate hit.
- **`ignoreIntersectionEXT` (`OpIgnoreIntersectionKHR`).** Terminates the any-hit invocation and discards the candidate. Traversal continues looking for other candidates. Payload writes before the call remain visible.
- **`terminateRayEXT` (`OpTerminateRayKHR`).** Terminates the any-hit invocation and ends ray traversal. The candidate is accepted, so the closest-hit shader runs for it. Payload writes before the call remain visible. In SPIR-V this is a block terminator, so any code after it in the same block is unreachable.
- **Empty any-hit (pass-through).** The candidate is accepted without payload modification. Traversal continues and the closest-hit shader runs for the closest accepted hit.
- **`reportIntersectionEXT` (`OpReportIntersectionKHR`).** Inside an intersection shader, declares a candidate hit at a given `t` with a hit kind. An intersection shader that never calls it produces no candidates, so the ray misses.
- **Ray payload sharing.** `rayPayloadEXT` in rgen and `rayPayloadInEXT` in ahit, chit, and miss refer to the same storage for one ray. The rgen initializes the payload to zero, so a stage that does not write a component leaves it at zero, and a miss shader writing `x` overwrites an earlier any-hit `x` write when the intersection was ignored.

## Registration Hierarchy

```text
ray_tracing_pipeline.traversal_control
├── ahit_ignore_intersection
├── ahit_pass_through
├── ahit_terminate_ray
├── isect_dont_report_intersection
└── isect_report_intersection
```

Each direct child is an intermediate node that owns one or two test case leaves (`triangles`, `aabbs`). The intersection-shader children only own an `aabbs` leaf because intersection shaders require procedural geometry.

## Parameter Dimensions and Observed Values

The matrix is built from two explicit arrays in the registration loop
[vktRayTracingTraversalControlTests.cpp#L771-L791](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L771-L791).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `HitShaderTestType` | `isect_report_intersection`, `isect_dont_report_intersection`, `ahit_pass_through`, `ahit_ignore_intersection`, `ahit_terminate_ray` | Selects the any-hit or intersection shader body; this is the primary behavioral axis. | [hitShaderTestTypes](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L776-L782) |
| `BottomTestType` | `triangles`, `aabbs` | Chooses fixed-function triangle intersection or procedural AABB geometry. AABB cases bind an intersection shader; triangle cases do not. | [bottomTestTypes](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L784-L791) |
| Launch size | fixed `8 x 8` | One ray per launch invocation. Central 6x6 pixels hit the square; border pixels miss. | [TEST_WIDTH/HEIGHT](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L75-L76) |
| Result image | fixed `8 x 8 x 2`, `r32ui` | Layer 0 carries the any-hit or miss `x` value; layer 1 carries the closest-hit `y` value. | [verifyImage](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L322-L384) |

## Behavior Parameters

The primary behavioral axis is `HitShaderTestType`, realized as the test case leaf under `ray_tracing_pipeline.traversal_control`. Each value swaps a different any-hit or intersection shader into the same pipeline while leaving rgen, chit, and miss unchanged.

### isect_report_intersection — intersection shader declares a candidate hit

The intersection shader calls `reportIntersectionEXT(0.5f, 0)` [isect_report](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L481-L494). The runtime accepts the candidate, runs the any-hit shader (which sets `hitValue.x = 1`), then runs the closest-hit shader (which sets `hitValue.y = 3`). Expected inside the square: layer 0 = 1, layer 1 = 3. This is the positive procedural-geometry baseline; it is restricted to the `aabbs` leaf because intersection shaders only run for AABB geometry.

### isect_dont_report_intersection — intersection shader produces no candidate

The intersection shader body is empty and never calls `reportIntersectionEXT` [isect_pass_through](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L496-L506). The runtime receives no candidate, so no any-hit or closest-hit shader runs and the miss shader sets `hitValue.x = 4`. Expected everywhere: layer 0 = 4, layer 1 = 0. This case is also restricted to the `aabbs` leaf.

### ahit_pass_through — empty any-hit accepts the candidate

The any-hit shader body is empty [ahit_pass_through](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L521-L531). The candidate is accepted without payload modification, traversal continues, and the closest-hit shader sets `hitValue.y = 3`. Because rgen initialized the payload to zero and no stage writes `x` on this hit path, layer 0 stays 0. Expected inside the square: layer 0 = 0, layer 1 = 3. This case generates both `triangles` and `aabbs` leaves.

### ahit_ignore_intersection — any-hit discards the candidate

The any-hit shader sets `hitValue.x = 1`, then calls `ignoreIntersectionEXT`, followed by an unreachable `hitValue.x = 2` [ahit_ignore](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L533-L547). The candidate is discarded and traversal continues. Nothing else is in the scene, so the ray misses and the miss shader overwrites `hitValue.x` with 4. Expected inside the square: layer 0 = 4, layer 1 = 0. The post-ignore `x = 2` is a canary that should never execute. This case generates both `triangles` and `aabbs` leaves.

### ahit_terminate_ray — any-hit ends traversal and accepts the candidate

The any-hit shader sets `hitValue.x = 1`, then calls `terminateRayEXT`, followed by an unreachable `hitValue.x = 2` [ahit_terminate](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L549-L563). Traversal ends, but the candidate is accepted, so the closest-hit shader still runs and sets `hitValue.y = 3`. Expected inside the square: layer 0 = 1, layer 1 = 3. The post-terminate `x = 2` is a canary that should never execute. This case generates both `triangles` and `aabbs` leaves.

## Shader Analysis

The shaders are inline GLSL strings emitted by `initPrograms` with `SPIRV_VERSION_1_4`
[vktRayTracingTraversalControlTests.cpp#L456-L591](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L456-L591).
Five shader-name sets are indexed by `HitShaderTestType`
[vktRayTracingTraversalControlTests.cpp#L251-L257](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L251-L257).
Each set shares the same rgen, chit, and miss shaders; only the any-hit shader (and the intersection shader for AABB cases) changes.

One walkthrough covers the `ahit_terminate_ray` case because `terminateRayEXT` is the most distinctive traversal-control operation and its post-terminate canary makes the pass/fail signal directly observable. The same rgen drives every case, and the chit and miss shaders are single-statement payload writes that the expected-value table already captures.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.traversal_control.ahit_terminate_ray.triangles
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ahit_terminate_ray` | The any-hit shader sets `hitValue.x = 1`, calls `terminateRayEXT`, and places `hitValue.x = 2` after the call as a canary. |
| `triangles` | Uses fixed-function triangle intersection; no intersection shader is bound. Hit group 1 contains only the any-hit and closest-hit shaders. |

#### Purpose

This case checks that `terminateRayEXT` ends the any-hit invocation and ends traversal, while still accepting the candidate so the closest-hit shader runs. If the implementation continues past `terminateRayEXT`, layer 0 reads back `2` instead of `1`. If it discards the candidate instead of accepting it, layer 1 reads back `0` instead of `3`.

#### Structural Design

| Step | Stage | Action | Payload effect |
|------|-------|--------|----------------|
| 1 | rgen | Initialize `hitValue` to `(0,0,0,0)`, trace one ray per launch invocation straight down `-Z` | payload = 0 |
| 2 | ahit (central pixels) | `hitValue.x = 1; terminateRayEXT;` | payload.x = 1; invocation ends; traversal ends |
| 3 | chit (central pixels) | `hitValue.y = 3` | payload.y = 3 |
| 4 | rgen | `imageStore` layer 0 from `hitValue.x`, layer 1 from `hitValue.y` | layer 0 = 1, layer 1 = 3 |
| 5 | miss (border pixels) | `hitValue.x = 4` | layer 0 = 4, layer 1 = 0 |

#### Shader Code

Reconstructed rgen (shared by every case):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT uvec4 hitValue;
layout(r32ui, set = 0, binding = 0) uniform uimage3D result;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin     = 0.0;
  float tmax     = 1.0;
  vec3  origin   = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, 0.5f);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  hitValue       = uvec4(0,0,0,0);
  traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec3(gl_LaunchIDEXT.xy, 0), uvec4(hitValue.x, 0, 0, 0));
  imageStore(result, ivec3(gl_LaunchIDEXT.xy, 1), uvec4(hitValue.y, 0, 0, 0));
}
```

Reconstructed `ahit_terminate` any-hit shader:

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadInEXT uvec4 hitValue;
void main()
{
  hitValue.x = 1;
  terminateRayEXT;
  hitValue.x = 2;
}
```

#### Additional Info

- The rgen traces rays with `flags = 0`, `cullMask = 0xFF`, `sbtRecordOffset = 0`, `sbtRecordStride = 0`, and `missIndex = 0`. With a single instance and single geometry, every central pixel follows the same hit-group record.
- The disassembled any-hit shader below shows that glslang treats `OpTerminateRayKHR` as a block terminator. The post-terminate `hitValue.x = 2` is unreachable and is removed from the SPIR-V entirely, so the runtime can never observe `2` through a conformant SPIR-V path. The runtime check remains as a defense against an implementation that continued execution past the terminate.
- The shared chit shader sets `hitValue.y = 3` and the shared miss shader sets `hitValue.x = 4`
  [chit](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L565-L577),
  [miss](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L579-L590).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this walkthrough | Evidence |
|---------------------|--------------------------------------------|----------|
| `HitShaderTestType` | Swaps the any-hit shader body (`ahit`, `ahit_pass_through`, `ahit_ignore`, `ahit_terminate`) or the intersection shader body (`isect_report`, `isect_pass_through`); rgen, chit, and miss stay the same. | [shaderNames table](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L251-L257) |
| `BottomTestType` | AABB cases bind an intersection shader in hit group 1; triangle cases omit it. The BLAS geometry changes from a two-triangle square to a single AABB. | [initBottomAccelerationStructures](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L187-L229), [initRayTracingShaders](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L245-L284) |

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
; Bound: 78
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %hitValue %topLevelAS %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %direct "direct"
               OpName %hitValue "hitValue"
               OpName %topLevelAS "topLevelAS"
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
  %float_0_5 = OpConstant %float 0.5
     %uint_1 = OpConstant %uint 1
   %float_n1 = OpConstant %float -1
         %34 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
     %v4uint = OpTypeVector %uint 4
%_ptr_RayPayloadKHR_v4uint = OpTypePointer RayPayloadKHR %v4uint
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v4uint RayPayloadKHR
         %38 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
         %39 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_39 = OpTypePointer UniformConstant %39
 %topLevelAS = OpVariable %_ptr_UniformConstant_39 UniformConstant
   %uint_255 = OpConstant %uint 255
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
         %50 = OpTypeImage %uint 3D 0 0 0 2 R32ui
%_ptr_UniformConstant_50 = OpTypePointer UniformConstant %50
     %result = OpVariable %_ptr_UniformConstant_50 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
      %v3int = OpTypeVector %int 3
%_ptr_RayPayloadKHR_uint = OpTypePointer RayPayloadKHR %uint
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %tmin %float_0
               OpStore %tmax %float_1
         %21 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %22 = OpLoad %uint %21
         %23 = OpConvertUToF %float %22
         %25 = OpFAdd %float %23 %float_0_5
         %27 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %28 = OpLoad %uint %27
         %29 = OpConvertUToF %float %28
         %30 = OpFAdd %float %29 %float_0_5
         %31 = OpCompositeConstruct %v3float %25 %30 %float_0_5
               OpStore %origin %31
               OpStore %direct %34
               OpStore %hitValue %38
         %42 = OpLoad %39 %topLevelAS
         %44 = OpLoad %v3float %origin
         %45 = OpLoad %float %tmin
         %46 = OpLoad %v3float %direct
         %47 = OpLoad %float %tmax
               OpTraceRayKHR %42 %uint_0 %uint_255 %uint_0 %uint_0 %uint_0 %44 %45 %46 %47 %hitValue
         %53 = OpLoad %50 %result
         %55 = OpLoad %v3uint %gl_LaunchIDEXT
         %56 = OpVectorShuffle %v2uint %55 %55 0 1
         %58 = OpBitcast %v2int %56
         %60 = OpCompositeExtract %int %58 0
         %61 = OpCompositeExtract %int %58 1
         %62 = OpCompositeConstruct %v3int %60 %61 %int_0
         %64 = OpAccessChain %_ptr_RayPayloadKHR_uint %hitValue %uint_0
         %65 = OpLoad %uint %64
         %66 = OpCompositeConstruct %v4uint %65 %uint_0 %uint_0 %uint_0
               OpImageWrite %53 %62 %66 ZeroExtend
         %67 = OpLoad %50 %result
         %68 = OpLoad %v3uint %gl_LaunchIDEXT
         %69 = OpVectorShuffle %v2uint %68 %68 0 1
         %70 = OpBitcast %v2int %69
         %72 = OpCompositeExtract %int %70 0
         %73 = OpCompositeExtract %int %70 1
         %74 = OpCompositeConstruct %v3int %72 %73 %int_1
         %75 = OpAccessChain %_ptr_RayPayloadKHR_uint %hitValue %uint_1
         %76 = OpLoad %uint %75
         %77 = OpCompositeConstruct %v4uint %76 %uint_0 %uint_0 %uint_0
               OpImageWrite %67 %74 %77 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rahit`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 17
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint AnyHitKHR %main "main" %hitValue
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %hitValue "hitValue"
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_IncomingRayPayloadKHR_v4uint = OpTypePointer IncomingRayPayloadKHR %v4uint
   %hitValue = OpVariable %_ptr_IncomingRayPayloadKHR_v4uint IncomingRayPayloadKHR
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
%_ptr_IncomingRayPayloadKHR_uint = OpTypePointer IncomingRayPayloadKHR %uint
     %uint_2 = OpConstant %uint 2
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpAccessChain %_ptr_IncomingRayPayloadKHR_uint %hitValue %uint_0
               OpStore %13 %uint_1
               OpTerminateRayKHR
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Resource setup.** The host builds one bottom-level acceleration structure containing a single square geometry. For `triangles` it is a two-triangle quad; for `aabbs` it is a single AABB covering the same area. A one-instance top-level acceleration structure wraps that BLAS
  [initBottomAccelerationStructures](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L187-L229),
  [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L231-L243).
- **Pipeline.** Three shader groups: group 0 is raygen, group 1 is the hit group (intersection for AABB plus any-hit plus closest-hit), group 2 is miss. The host builds one-entry raygen, hit, and miss shader binding tables sized to `shaderGroupHandleSize`
  [initRayTracingShaders](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L245-L284),
  [initShaderBindingTables](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L286-L320).
- **Image clear and barrier.** The 2-layer `r32ui` storage image is cleared to `0xFF` in transfer-dst layout, then barriered to `GENERAL` with acceleration-structure read and write access before the trace
  [runTest image barriers](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L678-L695).
- **Trace.** `cmdTraceRays` runs an `8 x 8 x 1` launch
  [cmdTraceRays](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L728-L729).
- **Copyback.** A shader-write to transfer-read memory barrier follows the trace, then `cmdCopyImageToBuffer` copies the 2-layer image to a host-visible buffer, and a transfer-write to host-read barrier precedes `submitCommandsAndWait`. The host invalidates the mapped range before reading
  [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L731-L749).
- **Reference comparison.** `verifyImage` builds a 2-layer reference image. It clears both layers to the miss values (`x = 4`, `y = 0`), then for central pixels writes the per-case hit values. The result and reference are compared with `tcu::intThresholdCompare` using a zero UVec4 threshold, so any single-pixel mismatch fails the case
  [verifyImage](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L322-L384).
- **Pass/fail.** The instance returns pass iff the comparison matches; otherwise it returns fail
  [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L754-L762).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `isect_report_intersection` | Intersection shader's `reportIntersectionEXT` call did not produce an accepted candidate, so ahit and chit did not run and the pixel reported miss instead of hit. |
| `isect_dont_report_intersection` | Intersection shader that never calls `reportIntersectionEXT` still produced a candidate hit, so ahit and chit ran instead of miss. |
| `ahit_pass_through` | Empty any-hit shader was treated as ignore, or the closest-hit shader did not run for an accepted candidate. |
| `ahit_ignore_intersection` | `ignoreIntersectionEXT` did not discard the candidate, so closest-hit ran (layer 1 = 3) instead of miss (layer 1 = 0); or the candidate was discarded but the miss shader did not run. |
| `ahit_terminate_ray` | `terminateRayEXT` did not end the any-hit invocation (post-terminate `hitValue.x = 2` executed, layer 0 = 2), or it did not accept the candidate (closest-hit did not run, layer 1 != 3). |

All cases share the same image-clear, trace, copyback, and reference-comparison path, so a shared infrastructure failure would surface identically across cases and is distinguishable from a single-case traversal-control failure by which case or pixel mismatched.

### Cause Analysis

#### Intersection report did not produce an accepted candidate

**Possible failure symptoms:** For `isect_report_intersection`, central pixels read back the miss value (`x = 4`) instead of the ahit value (`x = 1`), and layer 1 reads `0` instead of `3`.

**Possible implementation causes:** The intersection shader called `reportIntersectionEXT(0.5f, 0)` and the runtime should accept the candidate at that `t`. A failure here points to the procedural-geometry intersection dispatch: the runtime did not invoke the any-hit shader for the reported candidate, or it rejected the candidate before any-hit ran. The spec requires that a reported candidate with a `t` inside `[tmin, tmax]` be presented to the any-hit shader unless ray flags cull it, and this test uses no cull flags.

#### Unreported intersection still produced a candidate

**Possible failure symptoms:** For `isect_dont_report_intersection`, central pixels read back a hit value (`x = 1` or `y = 3`) instead of the miss value (`x = 4`, `y = 0`).

**Possible implementation causes:** The intersection shader body is empty and never calls `reportIntersectionEXT`. The spec says the intersection shader must report candidates explicitly; an empty shader should produce none. A failure here suggests the runtime fabricated a candidate hit for the AABB without an explicit report, possibly by treating the AABB bounds as an implicit intersection.

#### Empty any-hit did not accept the candidate

**Possible failure symptoms:** For `ahit_pass_through`, layer 0 reads `4` (miss) inside the square, or layer 1 reads `0` instead of `3`.

**Possible implementation causes:** The spec says an any-hit shader that returns without calling `ignoreIntersectionEXT` or `terminateRayEXT` accepts the candidate. A miss value inside the square means the candidate was rejected anyway. A `0` on layer 1 means the candidate was accepted but the closest-hit shader did not run for the closest accepted hit, which violates the traversal order guarantee.

#### ignoreIntersection did not discard the candidate

**Possible failure symptoms:** For `ahit_ignore_intersection`, layer 1 reads `3` inside the square, meaning the closest-hit shader ran for a candidate that should have been discarded. Alternatively, layer 0 reads a value other than `4` inside the square, meaning the miss shader did not run after traversal found no other candidate.

**Possible implementation causes:** `ignoreIntersectionEXT` must terminate the any-hit invocation and remove the candidate from consideration. A closest-hit run indicates the implementation treated the ignored candidate as accepted. A wrong layer 0 value after a confirmed miss (layer 1 = 0) indicates the miss shader did not execute or did not write the payload. The canary `hitValue.x = 2` after `ignoreIntersectionEXT` would read back as `2` on layer 0 if the implementation continued past the ignore, but the SPIR-V removes that code as unreachable, so observing `2` would point to a driver-side execution issue rather than a shader-compiler issue.

#### terminateRay did not end the invocation or did not accept the candidate

**Possible failure symptoms:** For `ahit_terminate_ray`, layer 0 reads `2` inside the square, meaning the post-`terminateRayEXT` canary executed. Or layer 1 reads `0` instead of `3`, meaning the closest-hit shader did not run for the accepted candidate.

**Possible implementation causes:** `OpTerminateRayKHR` is a SPIR-V block terminator, so the disassembled shader contains no code after it; the `hitValue.x = 2` store is removed by glslang. Observing `2` at runtime would therefore indicate an implementation that did not honor the terminator semantics at the execution level. A `0` on layer 1 means the implementation treated `terminateRayEXT` like `ignoreIntersectionEXT`, discarding the candidate and running miss instead. The spec distinction is explicit: `terminateRayEXT` ends traversal but accepts the candidate, so the closest-hit shader must run for it.

#### Shared image-clear, trace, or copyback error

**Possible failure symptoms:** A failure that appears across multiple unrelated cases, or pixels that read back the clear value `0xFF` instead of any expected hit or miss value.

**Possible implementation causes:** The image is cleared to `0xFF` before the trace and barriered to `GENERAL`. If the clear or barrier did not take effect, the rgen `imageStore` could write over stale data or be invisible to the copy. If `copyImageToBuffer` or the host invalidation missed a layer, the host would read stale or uninitialized memory. These causes are not specific to traversal control and would be investigated by checking the barriers and copy region rather than the shader.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` device functionality, with the `rayTracingPipeline` and `accelerationStructure` feature bits enabled
  [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L439-L454).
- The `accelerationStructure` feature is checked as a hard error rather than `NotSupportedError` because `VK_KHR_ray_tracing_pipeline` depends on it.

### Design-based pruning

- The two intersection-shader cases (`isect_report_intersection`, `isect_dont_report_intersection`) are registered with `onlyAabbTest = true`, so they only generate the `aabbs` leaf. Intersection shaders only run for procedural geometry, so a `triangles` leaf would have no intersection shader to test
  [onlyAabbTest gate](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L777-L778),
  [skip loop](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L798-L801).
- The three any-hit cases generate both `triangles` and `aabbs` leaves because the any-hit shader runs for both geometry types. The AABB leaves of these cases bind the `isect_report` intersection shader so a candidate exists for the any-hit shader to act on.

## Key Takeaways

- The same rgen, chit, and miss shaders drive every case. Only the any-hit or intersection shader body changes, so each case isolates one traversal-control operation.
- `ignoreIntersectionEXT` and `terminateRayEXT` differ in what happens to the candidate: ignore discards it and continues traversal, terminate accepts it and ends traversal. The expected-value table reflects this through which later stage writes the payload.
- `ahit_terminate_ray` expects the closest-hit shader to run, which distinguishes terminate from ignore. `ahit_ignore_intersection` expects the miss shader to run after nothing else is found, which distinguishes ignore from terminate.
- The post-control-instruction canary assignments (`hitValue.x = 2`) are removed by glslang as unreachable code, so the SPIR-V cannot produce `2` through a conformant path. Observing `2` at runtime would point to execution-level rather than compiler-level behavior.
- The intersection-shader cases are AABB-only by design because triangle geometry uses fixed-function intersection and never invokes an intersection shader.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `HitShaderTestType` enum | [vktRayTracingTraversalControlTests.cpp#L59-L67](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L59-L67) | Defines the five behavior parameter values. |
| `SingleSquareConfiguration` class | [vktRayTracingTraversalControlTests.cpp#L160-L399](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L160-L399) | Implements BLAS/TLAS, pipeline, SBT, and result verification for all cases. |
| BLAS geometry construction | [vktRayTracingTraversalControlTests.cpp#L187-L229](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L187-L229) | Triangle square vs single AABB. |
| Pipeline shader binding | [vktRayTracingTraversalControlTests.cpp#L245-L284](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L245-L284) | Maps each `HitShaderTestType` to its shader set and binds the three shader groups. |
| SBT construction | [vktRayTracingTraversalControlTests.cpp#L286-L320](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L286-L320) | One-entry raygen, hit, and miss tables. |
| `verifyImage` expected-value switch | [vktRayTracingTraversalControlTests.cpp#L322-L384](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L322-L384) | Encodes the per-case reference image semantics. |
| `checkSupport` feature gates | [vktRayTracingTraversalControlTests.cpp#L439-L454](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L439-L454) | Requires the two KHR feature bits. |
| `initPrograms` GLSL literals | [vktRayTracingTraversalControlTests.cpp#L456-L591](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L456-L591) | Source of the reconstructed walkthrough shaders. |
| `runTest` host flow | [vktRayTracingTraversalControlTests.cpp#L608-L752](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L608-L752) | Resource creation, clear, trace, copyback, host invalidation. |
| Registration loop | [vktRayTracingTraversalControlTests.cpp#L766-L813](../../../modules/vulkan/ray_tracing/vktRayTracingTraversalControlTests.cpp#L766-L813) | Builds the five test case groups and their triangle/AABB leaves, applying `onlyAabbTest`. |
