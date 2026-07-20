## Overview

**Core question:** Does `VK_KHR_ray_tracing_pipeline` traversal report exactly one hit (no cracks, no duplicates) when a ray passes through a shared edge or shared vertex between adjacent triangles in a fan or closed-fan arrangement?

This page covers one test family registered from [vktRayTracingWatertightnessTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L938):

- `watertightness` registers twelve direct children: ten numbered groups `0` through `9`, plus `closedFan` and `closedFan2`.
- The ten numbered groups generate random recursive fan triangulations and fire one downward ray per pixel through the fan. They detect cracks (misses) but not duplicates, because the any-hit shader uses non-atomic `imageStore`.
- `closedFan` and `closedFan2` build a closed fan of triangles sharing a center vertex. The raygen shader fires rays that aim at the center vertex and at the midpoint of each shared edge. The any-hit shader uses `imageAtomicAdd` and each geometry carries `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR`, so the host can detect both cracks (quality warning) and duplicate any-hit invocations (failure).
- `closedFan` places all triangles in one bottom-level acceleration structure as separate geometries and uses `gl_PrimitiveID` for the result z coordinate. `closedFan2` places each triangle in its own bottom-level acceleration structure and uses `gl_GeometryIndexEXT`.

## Background Knowledge

- Watertightness in ray traversal means a ray that passes through a shared edge or shared vertex between two adjacent triangles is reported as a hit by exactly one triangle. Cracks let the ray slip through (miss). Duplicate hits let both adjacent triangles report a hit.
- `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` is a geometry flag that requests the implementation not invoke the any-hit shader more than once per primitive per ray. Without this flag, a single triangle could trigger multiple any-hit invocations when the ray hits it in multiple internal acceleration structure nodes. The closed fan variants set this flag so a duplicate hit can only come from two distinct adjacent triangles, not from a single triangle revisited.
- `gl_PrimitiveID` is the index of the triangle within the current geometry. `gl_GeometryIndexEXT` is the index of the geometry within the current bottom-level acceleration structure. In `closedFan` each geometry has one triangle, so `gl_PrimitiveID` is zero for every hit. In `closedFan2` each BLAS has one geometry, so `gl_GeometryIndexEXT` is zero for every hit. Both variants therefore accumulate hit counts at z equals zero in the 3D result image; the per-ray `(x, y)` position keeps rays separate.
- The Vulkan spec discourages but does not forbid misses at shared edges and vertices. The closed fan variants report a miss as `QP_TEST_RESULT_QUALITY_WARNING`, not as a failure.

## Registration Hierarchy

```text
ray_tracing_pipeline.watertightness
├── 0
├── 1
├── 2
├── 3
├── 4
├── 5
├── 6
├── 7
├── 8
├── 9
├── closedFan
└── closedFan2
```

Each numbered child `0` through `9` is a group containing eight test case leaves named by triangle count: `4`, `16`, `64`, `256`, `1024`, `4096`, `16384`, `65536`. Each of `closedFan` and `closedFan2` is a group containing five test case leaves: `4`, `16`, `64`, `256`, `1024`. The numbered groups differ only in the random seed `5 * testNdx + 11 * size + baseSeed` and produce different recursive fan triangulations for the same triangle count.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test variant | `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `closedFan`, `closedFan2` | Selects fan topology and detection mechanism. `0-9` use a random recursive fan with `imageStore` (crack detection only). `closedFan` and `closedFan2` use a closed fan with `imageAtomicAdd` (crack and duplicate detection). | [vktRayTracingWatertightnessTests.cpp#L872-L938](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L938) |
| Triangle count | `4`, `16`, `64`, `256`, `1024`, `4096`, `16384`, `65536` (numbered groups); `4`, `16`, `64`, `256`, `1024` (closed fan) | Number of triangles in the fan. More triangles means more shared edges and vertices, increasing watertightness stress. The closed fan variants stop at `1024` because the regular fan geometry does not benefit from larger counts. | [vktRayTracingWatertightnessTests.cpp#L882-L883](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L882-L883), [vktRayTracingWatertightnessTests.cpp#L907](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L907) |
| Random seed | `5 * testNdx + 11 * size + baseSeed` (numbered groups only) | Controls the recursive fan triangulation. Ten numbered groups give ten different triangulations per triangle count. | [vktRayTracingWatertightnessTests.cpp#L890-L891](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L890-L891) |
| BLAS topology | single BLAS, N geometries (`closedFan`); N BLASes, one geometry each (`closedFan2`) | Changes how triangles are organized in the acceleration structure. `closedFan` exercises one instance with multiple geometries. `closedFan2` exercises multiple instances with one geometry each. | [vktRayTracingWatertightnessTests.cpp#L601-L639](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L601-L639) |
| Result z built-in | `gl_PrimitiveID` (`closedFan`), `gl_GeometryIndexEXT` (`closedFan2`) | Selects which ray tracing built-in identifies the hit slot in the result image z dimension. Both report zero in their respective topologies. | [vktRayTracingWatertightnessTests.cpp#L337](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L337) |

## Behavior Parameters

The primary behavioral axis is the test variant: the direct child of `watertightness`. The ten numbered children `0` through `9` share the same mechanism and differ only in the random seed, so they are treated as one behavioral value. `closedFan` and `closedFan2` are distinct because they change the BLAS topology, the result image dimensionality, the any-hit write mechanism, and the validation logic.

### 0-9 — Legacy random fan, crack detection via imageStore

The host builds a single bottom-level acceleration structure containing one geometry with N triangles. The triangles come from recursive random splitting: the test starts with a unit square split into two triangles, then repeatedly picks a random triangle, adds a vertex inside it, and splits it into three. The `pointInTriangle2D` and `pointFits` checks reject degenerate splits that would produce inconsistent winding or vertices too close to the longest side.

The raygen shader is the common helper [`getCommonRayGenerationShader`](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138). It fires one ray per launch invocation from `((x + 0.5) / width, (y + 0.5) / height, 0.0)` in direction `(0, 0, -1)`, with `tmax = 9.0`. The launch size is `256 x 256`.

The any-hit shader does `imageStore(result, ivec2(gl_LaunchIDEXT.xy), uvec4(1,0,0,1))`. The miss shader does `imageStore(result, ivec2(gl_LaunchIDEXT.xy), uvec4(2,0,0,1))`. The host checks the first `squaresGroupCount` pixels and requires each to equal `1`. A value of `2` means the ray missed a triangle in the fan, indicating a crack. Because `imageStore` is non-atomic, duplicate hits overwrite with the same value `1` and are invisible to the host. This variant detects cracks only.

### closedFan — Closed fan, single BLAS, crack and duplicate detection via imageAtomicAdd

The host builds a closed fan of N triangles arranged around the origin in the XY plane. All triangles share the center vertex `(0, 0, 0)` and each triangle shares an edge with its neighbor. The fan lives in a single bottom-level acceleration structure as N separate geometries, each with one triangle and each created with `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR`.

The raygen shader fires `N + 2` active rays (the early-return test is `nRay > nSharedEdges + 1`). Ray 0 aims at the shared center vertex. Rays 1 through N aim at the midpoint of each shared edge. Ray N+1 is a spare that re-targets the first shared edge; see `## Shader Analysis` for the per-ray geometry. The any-hit shader does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, gl_PrimitiveID), 1)`. The miss shader does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, 0), 10000)`.

The host scans every cell of the 3D result image. A cell value greater than `1` (excluding the magic `10000`) is a duplicate-hit failure. A cell value equal to `10000` is a miss and produces a quality warning. With the `NO_DUPLICATE_ANY_HIT` flag set, a value greater than `1` can only come from two distinct adjacent triangles reporting a hit at the same shared edge, not from a single triangle revisited.

### closedFan2 — Closed fan, multiple BLASes, gl_GeometryIndexEXT variant

The host builds the same closed fan geometry as `closedFan`, but splits the triangles across N bottom-level acceleration structures, one triangle per BLAS. The top-level acceleration structure holds N instances. The pipeline creates `squaresGroupCount` hit groups in the shader binding table, all bound to the same any-hit shader module, even though `traceRayEXT` uses `sbtRecordOffset = 0` and `sbtRecordStride = 0` so only hit group 0 is invoked.

The any-hit shader does `imageAtomicAdd(result, ivec3(gl_LaunchIDEXT.xy, gl_GeometryIndexEXT), 1)`. Because each BLAS has one geometry, `gl_GeometryIndexEXT` is zero for every hit, so all writes land at z equals zero. The host validation is identical to `closedFan`. This variant exercises watertightness when shared edges cross instance boundaries rather than geometry boundaries within a single BLAS, and it verifies that `gl_GeometryIndexEXT` is readable in the any-hit shader.

## Shader Analysis

The page uses one representative walkthrough. The `closedFan` raygen shader is the only shader that directly targets shared edges and vertices; it is the core of the watertightness test. The legacy fan raygen shader is the common helper used by many other ray tracing tests and adds no watertightness-specific behavior. The any-hit and miss shaders are short atomic-add or image-store one-liners covered in `## Behavior Parameters`.

### Representative Shader Walkthrough 1

**CTS case:** `ray_tracing_pipeline.watertightness.closedFan.4`

**Source location:** [vktRayTracingWatertightnessTests.cpp#L399-L442](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L399-L442)

**What this shader tests:** The raygen shader computes a linear ray index `nRay` from `gl_LaunchIDEXT`. Ray 0 targets the shared center vertex of the closed fan. Rays 1 through N target the midpoint of each shared edge, computed as `mix(centerVertex, perimeterVertex[i], 0.5)`. Each ray fires `traceRayEXT` from `(0, 0, -1)` toward the target point at `z = 0`. The any-hit shader does `imageAtomicAdd` on the 3D result image; the miss shader writes the magic `10000`. If the implementation has a crack at a shared edge or vertex, the ray misses and the miss shader writes `10000` (quality warning). If the implementation has a duplicate-hit bug, two adjacent triangles both invoke the any-hit shader and the cell value exceeds `1` (failure).

For `closedFan.4`, `nSharedEdges = 4`, so `angleDiff = 2 * pi / 4 = pi / 2`. The active rays are `nRay = 0..5` (six rays total: one center-vertex ray plus four shared-edge rays plus one spare). Rays with `nRay > 5` return early.

**Shader-visible resources:**

- `%topLevelAS` (`accelerationStructureKHR`, set 0, binding 1): top-level acceleration structure holding the closed fan instances. Read by `OpTraceRayKHR`.
- `%hitValue` (`RayPayloadKHR`, `vec3`, location 0): ray payload. Unused beyond dispatch; the any-hit shader communicates through the result image, not through the payload.
- `%gl_LaunchIDEXT` (`vec3 uint`, `BuiltIn LaunchIdKHR`): input built-in giving the current invocation coordinates. Used to compute the linear ray index.
- `%gl_LaunchSizeEXT` (`vec3 uint`, `BuiltIn LaunchSizeKHR`): input built-in giving the launch extent. Used to compute the linear ray index.

**Reconstructed GLSL:**

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require

/// Ray payload (unused beyond traceRayEXT dispatch; the any-hit shader
/// does the actual work via imageAtomicAdd on the result image).
layout(location = 0)         rayPayloadEXT vec3                     hitValue;
/// Top-level acceleration structure bound at set 0, binding 1.
/// Holds the closed fan of triangles sharing a center vertex.
layout(set = 0, binding = 1) uniform       accelerationStructureEXT topLevelAS;

void main()
{
    uint  rayFlags = 0;
    uint  cullMask = 0xFF;
    float tmin     = 0.01;
    float tmax     = 9.0;
    /// Linear ray index within the launch. Only rays 0..nSharedEdges+1 do work.
    uint  nRay     = gl_LaunchIDEXT.y * gl_LaunchSizeEXT.x + gl_LaunchIDEXT.x;
    /// Ray origin sits above the fan plane (z = -1); the fan lives at z = 0.
    vec3  origin   = vec3(0.0, 0.0, -1.0);

    /// nSharedEdges = 4 for closedFan.4; active rays are 0..5.
    if (nRay > 5)
    {
        return;
    }

    float kPi          = 3.141592653589;
    /// Angular spacing between shared edges of the closed fan.
    float angleDiff    = 2.0 * kPi / 4;
    /// Ray 0 targets the center vertex (angle unused). Rays 1..4 target
    /// the midpoint of shared edge i, at angle (angleDiff*(i-1) - pi).
    float angle        = ((nRay == 0) ? 0.0
                                      : (angleDiff * (nRay - 1) - kPi));
    vec2  sharedEdgeP1 = vec2(0, 0);
    vec2  sharedEdgeP2 = ((nRay == 0) ? vec2     (0, 0)
                                      : vec2     (sin(angle), cos(angle)));
    /// Target the midpoint of the shared edge (or center vertex for ray 0).
    vec3  target       = vec3     (mix(sharedEdgeP1, sharedEdgeP2, vec2(0.5)), 0.0);
    vec3  direct       = normalize(target - origin);

    traceRayEXT(topLevelAS, rayFlags, cullMask, 0, 0, 0, origin, tmin, direct, tmax, 0);
}
```

Built with `glslangValidator -V --target-env spirv1.4 -S rgen`. Validated with `spirv-val --target-env spv1.4`. SPIR-V version 1.4, Bound 114. **Target SPIR-V environment:** `spirv1.4` (CTS build options target `vk::SPIRV_VERSION_1_4`).

The `OpTraceRayKHR` instruction at the end of `main` dispatches the ray into the top-level acceleration structure. The `sbtRecordOffset` and `sbtRecordStride` arguments are both zero, so all rays use hit group 0.

**Parameter variation note:** For other `closedFan.<size>` cases, the `nSharedEdges + 1` literal in the early-return comparison and the `2.0 * kPi / <nSharedEdges>` divisor change. For `closedFan2.<size>`, the raygen shader is identical; only the any-hit shader switches `gl_PrimitiveID` to `gl_GeometryIndexEXT`. For the numbered groups `0-9`, the raygen shader is replaced entirely by `getCommonRayGenerationShader`, which fires one downward ray per pixel from `((x + 0.5) / width, (y + 0.5) / height, 0.0)`.

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
; Bound: 114
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %topLevelAS %hitValue
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %rayFlags "rayFlags"
               OpName %cullMask "cullMask"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %nRay "nRay"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %origin "origin"
               OpName %kPi "kPi"
               OpName %angleDiff "angleDiff"
               OpName %angle "angle"
               OpName %sharedEdgeP1 "sharedEdgeP1"
               OpName %sharedEdgeP2 "sharedEdgeP2"
               OpName %target "target"
               OpName %direct "direct"
               OpName %topLevelAS "topLevelAS"
               OpName %hitValue "hitValue"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%float_0_00999999978 = OpConstant %float 0.00999999978
    %float_9 = OpConstant %float 9
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %float_0 = OpConstant %float 0
   %float_n1 = OpConstant %float -1
         %38 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
     %uint_5 = OpConstant %uint 5
       %bool = OpTypeBool
%float_3_14159274 = OpConstant %float 3.14159274
    %float_2 = OpConstant %float 2
    %float_4 = OpConstant %float 4
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
         %72 = OpConstantComposite %v2float %float_0 %float_0
  %float_0_5 = OpConstant %float 0.5
         %90 = OpConstantComposite %v2float %float_0_5 %float_0_5
        %100 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_100 = OpTypePointer UniformConstant %100
 %topLevelAS = OpVariable %_ptr_UniformConstant_100 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_RayPayloadKHR_v3float = OpTypePointer RayPayloadKHR %v3float
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v3float RayPayloadKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
   %rayFlags = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
       %nRay = OpVariable %_ptr_Function_uint Function
     %origin = OpVariable %_ptr_Function_v3float Function
        %kPi = OpVariable %_ptr_Function_float Function
  %angleDiff = OpVariable %_ptr_Function_float Function
      %angle = OpVariable %_ptr_Function_float Function
         %57 = OpVariable %_ptr_Function_float Function
%sharedEdgeP1 = OpVariable %_ptr_Function_v2float Function
%sharedEdgeP2 = OpVariable %_ptr_Function_v2float Function
         %76 = OpVariable %_ptr_Function_v2float Function
     %target = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0_00999999978
               OpStore %tmax %float_9
         %24 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %25 = OpLoad %uint %24
         %27 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %25 %28
         %30 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %31 = OpLoad %uint %30
         %32 = OpIAdd %uint %29 %31
               OpStore %nRay %32
               OpStore %origin %38
         %39 = OpLoad %uint %nRay
         %42 = OpUGreaterThan %bool %39 %uint_5
               OpSelectionMerge %44 None
               OpBranchConditional %42 %43 %44
         %43 = OpLabel
               OpReturn
         %44 = OpLabel
               OpStore %kPi %float_3_14159274
         %50 = OpLoad %float %kPi
         %51 = OpFMul %float %float_2 %50
         %53 = OpFDiv %float %51 %float_4
               OpStore %angleDiff %53
         %55 = OpLoad %uint %nRay
         %56 = OpIEqual %bool %55 %uint_0
               OpSelectionMerge %59 None
               OpBranchConditional %56 %58 %60
         %58 = OpLabel
               OpStore %57 %float_0
               OpBranch %59
         %60 = OpLabel
         %61 = OpLoad %float %angleDiff
         %62 = OpLoad %uint %nRay
         %63 = OpISub %uint %62 %uint_1
         %64 = OpConvertUToF %float %63
         %65 = OpFMul %float %61 %64
         %66 = OpLoad %float %kPi
         %67 = OpFSub %float %65 %66
               OpStore %57 %67
               OpBranch %59
         %59 = OpLabel
         %68 = OpLoad %float %57
               OpStore %angle %68
               OpStore %sharedEdgeP1 %72
         %74 = OpLoad %uint %nRay
         %75 = OpIEqual %bool %74 %uint_0
               OpSelectionMerge %78 None
               OpBranchConditional %75 %77 %79
         %77 = OpLabel
               OpStore %76 %72
               OpBranch %78
         %79 = OpLabel
         %80 = OpLoad %float %angle
         %81 = OpExtInst %float %1 Sin %80
         %82 = OpLoad %float %angle
         %83 = OpExtInst %float %1 Cos %82
         %84 = OpCompositeConstruct %v2float %81 %83
               OpStore %76 %84
               OpBranch %78
         %78 = OpLabel
         %85 = OpLoad %v2float %76
               OpStore %sharedEdgeP2 %85
         %87 = OpLoad %v2float %sharedEdgeP1
         %88 = OpLoad %v2float %sharedEdgeP2
         %91 = OpExtInst %v2float %1 FMix %87 %88 %90
         %92 = OpCompositeExtract %float %91 0
         %93 = OpCompositeExtract %float %91 1
         %94 = OpCompositeConstruct %v3float %92 %93 %float_0
               OpStore %target %94
         %96 = OpLoad %v3float %target
         %97 = OpLoad %v3float %origin
         %98 = OpFSub %v3float %96 %97
         %99 = OpExtInst %v3float %1 Normalize %98
               OpStore %direct %99
        %103 = OpLoad %100 %topLevelAS
        %104 = OpLoad %uint %rayFlags
        %105 = OpLoad %uint %cullMask
        %106 = OpLoad %v3float %origin
        %107 = OpLoad %float %tmin
        %108 = OpLoad %v3float %direct
        %109 = OpLoad %float %tmax
               OpTraceRayKHR %103 %104 %105 %uint_0 %uint_0 %uint_0 %106 %107 %108 %109 %hitValue
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

The test instance `RayTracingWatertightnessTestInstance::runTest` builds all resources and records a single command buffer per case.

Resource setup:

- A storage image of `VK_FORMAT_R32_UINT`. For numbered groups it is 2D `256 x 256`; for closed fan variants it is 3D `(1 + sqrt(N)) x sqrt(N) x N`. The image is cleared to `5,5,5,255` for numbered groups or `0,0,0,0` for closed fan variants.
- A host-visible readback buffer of `pixelCount * sizeof(uint32)` bytes.
- Bottom-level acceleration structure(s) built from the fan or closed-fan triangle data.
- A top-level acceleration structure with one instance (numbered groups, `closedFan`) or N instances (`closedFan2`).
- A ray tracing pipeline with one raygen, one miss, and one or more any-hit hit groups. The hit group count is `1` for numbered groups and `closedFan`, and `squaresGroupCount` for `closedFan2`.
- Shader binding table regions for raygen, miss, and hit groups, sized from `VkPhysicalDeviceRayTracingPipelinePropertiesKHR::shaderGroupHandleSize` and `shaderGroupBaseAlignment`.

Command buffer recording:

- Image layout transition to `TRANSFER_DST_OPTIMAL`, clear, then transition to `GENERAL` with `VK_ACCESS_ACCELERATION_STRUCTURE_READ_BIT_KHR | VK_ACCESS_ACCELERATION_STRUCTURE_WRITE_BIT_KHR`.
- Build bottom-level and top-level acceleration structures.
- Update the descriptor set with the storage image (binding 0) and the top-level acceleration structure (binding 1).
- Bind descriptor sets and pipeline, then call `cmdTraceRays`. For numbered groups the launch size is `width x height x 1` (`256 x 256 x 1`). For closed fan variants the launch size is `(1 + width) x height x 1` to fit the extra center-vertex ray.
- Pipeline barrier from `RAY_TRACING_SHADER_BIT_KHR` to `TRANSFER_BIT`, then `cmdCopyImageToBuffer` into the readback buffer.
- Pipeline barrier from `TRANSFER_BIT` to `HOST_BIT`.

Result checking in `iterate`:

- Numbered groups: scan the first `squaresGroupCount` pixels. Each must equal `1`. Any other value increments the failure counter.
- Closed fan variants: scan every cell of the 3D image. A cell value of `10000` sets the quality-warning flag. A cell value greater than `1` (excluding `10000`) increments the failure counter.
- If `failures == 0` and `qualityWarningIssued`, return `QP_TEST_RESULT_QUALITY_WARNING` with message `"Miss shader invoked for a shared edge/vertex."`. If `failures == 0` and no warning, return `pass`. Otherwise return `fail` with the failure count.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `0-9` (legacy random fan) | Crack in the acceleration structure traversal: a ray that should hit a triangle in the fan misses it, typically at a shared edge or vertex. The any-hit writes `1` on hit and the miss shader writes `2` on miss, so any non-`1` pixel is a miss. |
| `closedFan` | Either a crack (ray misses the shared center vertex or shared edge, producing a `10000` quality warning) or a duplicate any-hit invocation (ray hits two adjacent triangles at the shared edge, producing a cell value greater than `1`). The `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` flag is set, so a duplicate invocation indicates the implementation did not honor the flag or has a watertightness bug. |
| `closedFan2` | Same crack/duplicate mechanisms as `closedFan`, but exercised across multiple bottom-level acceleration structures (one triangle per BLAS, one BLAS per instance). A failure here points to watertightness bugs that appear when shared edges cross instance boundaries, or to `gl_GeometryIndexEXT` reporting a wrong value. |

### Cause Analysis

#### Crack at a shared edge or vertex

**Possible failure symptoms:** For numbered groups, a result pixel equals `2` (miss shader value) instead of `1` (any-hit value). For closed fan variants, a result cell equals `10000` (miss shader magic value), which produces a quality warning rather than a failure.

**Possible implementation causes:** The acceleration structure builder split the shared edge or vertex into separate internal nodes, and the ray-triangle intersection test in each adjacent triangle rejected the ray due to floating-point roundoff at the edge boundary. The traversal engine did not apply a watertight edge test (such as the "water-tight" intersection algorithm that assigns each edge to exactly one triangle based on ray direction). The closed fan geometry is the worst case because all triangles share the center vertex, so any roundoff at that vertex can cause a miss.

#### Duplicate any-hit invocation at a shared edge

**Possible failure symptoms:** Only visible in `closedFan` and `closedFan2`. A result cell has value greater than `1` (for example `2`), meaning the any-hit shader ran more than once for the same ray at the same `(x, y, z)` position. The host treats this as a failure.

**Possible implementation causes:** The implementation did not honor `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` and invoked the any-hit shader twice for the same geometry. Or, two distinct adjacent triangles both reported a hit for the same ray at the shared edge because the traversal engine did not apply a single-triangle-wins rule at shared boundaries. In `closedFan2`, the duplicate could also come from two instances whose geometries overlap at the shared edge, with the traversal engine not culling the second hit. The `NO_DUPLICATE_ANY_HIT` flag only suppresses duplicates within a single geometry, so a true cross-triangle duplicate indicates a watertightness bug in the intersection or traversal logic.

#### gl_GeometryIndexEXT reports a wrong value

**Possible failure symptoms:** Only visible in `closedFan2`. A result cell at an unexpected z position gets incremented, or the cell at z equals zero gets fewer increments than expected. This could mask a real duplicate or produce a spurious failure if the wrong cell exceeds `1`.

**Possible implementation causes:** The driver reported a wrong `gl_GeometryIndexEXT` value for the hit geometry. In `closedFan2` each BLAS has one geometry, so `gl_GeometryIndexEXT` should always be zero. A nonzero value would indicate a driver bug in populating the hit geometry index during traversal. This cause is specific to `closedFan2` because `closedFan` uses `gl_PrimitiveID` instead.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_ray_tracing_pipeline` and `VK_KHR_acceleration_structure` device features. The `checkSupport` method throws `NotSupportedError` if `rayTracingPipeline` is false and `TestError` if `accelerationStructure` is false.
- The result image format `VK_FORMAT_R32_UINT` must support the required image type (2D for numbered groups, 3D for closed fan variants) with `OPTIMAL` tiling and the storage usage flags. `checkSupport` queries `vkGetPhysicalDeviceImageFormatProperties` and throws `NotSupportedError` if the dimensions exceed the reported max extent.
- `checkSupportInInstance` verifies that the device's `maxPrimitiveCount`, `maxGeometryCount`, and `maxInstanceCount` can hold the test's triangle, geometry, and instance counts, and that `maxMemoryAllocationCount` can hold the required allocation count. Cases exceeding these limits throw `NotSupportedError`.

### Design-based pruning

- The closed fan variants stop at `1024` triangles. The closed fan geometry is regular (all triangles share one vertex), so larger counts would repeat the same edge configuration without adding coverage. The numbered groups extend to `65536` because the recursive random fan produces different edge configurations at every count.
- The numbered groups `0` through `9` use the same eight triangle counts but different random seeds. The ten seeds give ten different recursive fan triangulations per count, increasing the chance of hitting edge configurations that expose watertightness bugs.
- The legacy fan uses `imageStore` and cannot detect duplicate hits. This is by design: the legacy fan predates the closed fan variants and focuses on crack detection. The closed fan variants were added later to cover duplicate detection with `imageAtomicAdd` and the `NO_DUPLICATE_ANY_HIT` flag.
- The `closedFan2` variant creates `squaresGroupCount` hit groups in the SBT but only hit group 0 is invoked (because `sbtRecordOffset` and `sbtRecordStride` are both zero). The extra hit groups exercise SBT sizing with many groups but do not change the shader behavior.

## Key Takeaways

- The numbered groups `0-9` detect cracks only, because the any-hit shader uses non-atomic `imageStore` and duplicate hits overwrite with the same value. A miss produces value `2`; the host requires every checked pixel to equal `1`.
- The `closedFan` and `closedFan2` variants detect both cracks and duplicates. The any-hit shader uses `imageAtomicAdd`, so duplicate hits accumulate. A cell value greater than `1` (excluding the magic `10000`) is a failure; a cell value of `10000` is a quality warning.
- The closed fan variants depend on `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR`. Without it, a single triangle visited in multiple internal nodes could produce a value greater than `1` that is not a watertightness bug. With the flag, a duplicate can only come from two distinct adjacent triangles.
- The `closedFan` raygen shader directly targets shared edges and vertices. Ray 0 aims at the center vertex shared by all triangles. Rays 1 through N aim at the midpoint of each shared edge. This is the most direct watertightness stress test in the family.
- The quality warning for misses in the closed fan variants reflects the Vulkan spec, which discourages but does not forbid misses at shared edges and vertices. A quality warning is not a conformance failure.
- See `## Failure Meaning` for the distinction between crack, duplicate, and `gl_GeometryIndexEXT` failure causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseDef` struct | [vktRayTracingWatertightnessTests.cpp#L56-L66](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L56-L66) | Per-case parameters: width, height, squares/instances/geometry counts, seed, depth, useManyGeometries. |
| `pointInTriangle2D` and `pointFits` | [vktRayTracingWatertightnessTests.cpp#L109-L160](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L109-L160) | Host-side geometry validation used during recursive fan triangulation to avoid degenerate splits. |
| `makePipeline` | [vktRayTracingWatertightnessTests.cpp#L180-L198](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L180-L198) | Builds the ray tracing pipeline with one raygen, one miss, and one or more any-hit hit groups. |
| `RayTracingTestCase::checkSupport` | [vktRayTracingWatertightnessTests.cpp#L284-L314](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L284-L314) | Feature and image format support checks. |
| `RayTracingTestCase::initPrograms` | [vktRayTracingWatertightnessTests.cpp#L316-L443](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L316-L443) | Generates `ahit`, `miss`, and `rgen` shaders for both `useClosedFan` values. |
| `initBottomAccelerationStructure` (legacy fan) | [vktRayTracingWatertightnessTests.cpp#L472-L550](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L472-L550) | Recursive random fan triangulation from a unit square. |
| `initBottomAccelerationStructures` (closed fan) | [vktRayTracingWatertightnessTests.cpp#L552-L644](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L552-L644) | Closed fan construction and the `useManyGeometries` switch between one BLAS and N BLASes. |
| `runTest` | [vktRayTracingWatertightnessTests.cpp#L646-L795](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L646-L795) | Pipeline, AS, image, SBT setup, descriptor update, `cmdTraceRays`, copyback. |
| `checkSupportInInstance` | [vktRayTracingWatertightnessTests.cpp#L797-L818](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L797-L818) | Runtime primitive, geometry, instance, and allocation limit checks. |
| `iterate` validation | [vktRayTracingWatertightnessTests.cpp#L820-L868](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L820-L868) | Host-side pass, fail, and quality-warning decision for both variants. |
| `createWatertightnessTests` registration | [vktRayTracingWatertightnessTests.cpp#L872-L938](../../../modules/vulkan/ray_tracing/vktRayTracingWatertightnessTests.cpp#L872-L938) | Registers the ten numbered groups plus `closedFan` and `closedFan2` with their size sweeps. |
| Common raygen shader helper | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | Returns the standard downward-firing raygen shader used by the numbered groups. |
