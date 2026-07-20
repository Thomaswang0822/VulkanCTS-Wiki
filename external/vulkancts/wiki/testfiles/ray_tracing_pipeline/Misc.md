## Overview

**Core question:** Do `VK_KHR_ray_tracing_pipeline` implementations correctly handle the ray tracing edge cases that do not fit the dedicated `builtin`, `raygen`, `pipeline`, `shader_binding_table`, or `acceleration_structures` test families, including callable shader stress, cull masks, recursion, shader record layouts, intersection reporting, ray termination, empty layouts, null miss, buffer reuse, empty AS updates, and pipeline library linking?

This page covers one test family registered from [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10904-L11244):

- `misc` groups 111 direct test case leaves that each exercise a distinct ray tracing pipeline behavior. The family is heterogeneous: no single registered dimension spans every leaf. The shared infrastructure is the generic runner `RayTracingMiscTestInstance`, which builds the pipeline, descriptor set, shader binding table, and acceleration structures, then dispatches rays and copies the result buffer back for a per-test `verifyResultBuffer` check.

The 111 leaves cluster into 18 behavioral groups. Each group targets a specific mechanism: SBT and stage invocation, acceleration structure reporting, geometry and cull mask semantics, intersection and termination control, shader record memory layout, resource lifetime, or pipeline creation.

## Background Knowledge

- `VK_KHR_ray_tracing_pipeline` defines six shader stages: raygen, closest-hit, any-hit, miss, intersection, and callable. `vkCmdTraceRaysKHR` dispatches rays using a shader binding table (SBT) that holds shader group handles and optional shader record data. `traceRayEXT` can recurse through closest-hit, any-hit, miss, and intersection shaders; `executeCallableEXT` invokes callable shaders off the traversal path.
- A top-level acceleration structure (TLAS) instances one or more bottom-level acceleration structures (BLAS). A BLAS holds triangle or AABB geometry. AABB geometry needs an intersection shader to report hits. `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` asks the implementation to invoke any-hit at most once per (geometry, primitive, ray) tuple. Cull masks are ANDed between ray and instance; only the low 8 bits are meaningful, so the `extrabits` variant ORs `0x00FFFFFF` into the mask to confirm the implementation ignores the upper bits.
- `reportIntersectionEXT` returns `true` when the intersection becomes the new closest and `false` when rejected. `ignoreIntersectionEXT` discards the current candidate without changing the closest hit so far. `terminateRayEXT` stops traversal of the current ray immediately. The "statically" test variants wrap these ops in functions the compiler should not fold away; the "dynamically" variants gate them on a result buffer value so the implementation cannot statically elide them.
- `VkSpecializationInfo` attaches per-stage constant values at pipeline creation. `recursiveTraces_*` uses constant ID 1 (`MAX_RECURSIVE_DEPTH`) on closest-hit and miss stages. `maxrayhitattributesize_*` and `raypayloadin_*` use specialization constants for the attribute and payload U32 counts.
- `VK_KHR_pipeline_library` lets the application split a pipeline into libraries and link them into a final pipeline. `shaders_from_lib` splits six shaders across two libraries and verifies all stages execute after linking.

## Registration Hierarchy

```text
ray_tracing_pipeline.misc
├── AS_stresstest_AABB
├── AS_stresstest_tri
├── NO_DUPLICATE_ANY_HIT_1TL1BL1G_AABB
├── NO_DUPLICATE_ANY_HIT_1TL1BL1G_tri
├── NO_DUPLICATE_ANY_HIT_1TL1BLnG_AABB
├── NO_DUPLICATE_ANY_HIT_1TL1BLnG_tri
├── NO_DUPLICATE_ANY_HIT_1TLnBL1G_AABB
├── NO_DUPLICATE_ANY_HIT_1TLnBL1G_tri
├── NO_DUPLICATE_ANY_HIT_1TLnBLnG_AABB
├── NO_DUPLICATE_ANY_HIT_1TLnBLnG_tri
├── OpIgnoreIntersectionKHR_AnyHitDynamically
├── OpIgnoreIntersectionKHR_AnyHitStatically
├── OpTerminateRayKHR_AnyHitDynamically
├── OpTerminateRayKHR_AnyHitStatically
├── OpTerminateRayKHR_IntersectionDynamically
├── OpTerminateRayKHR_IntersectionStatically
├── callableshaderstress_1TL1BL1G_AABB_dynamic
├── callableshaderstress_1TL1BL1G_AABB_static
├── callableshaderstress_1TL1BL1G_tri_dynamic
├── callableshaderstress_1TL1BL1G_tri_static
├── callableshaderstress_1TL1BLnG_AABB_dynamic
├── callableshaderstress_1TL1BLnG_AABB_static
├── callableshaderstress_1TL1BLnG_tri_dynamic
├── callableshaderstress_1TL1BLnG_tri_static
├── callableshaderstress_1TLnBL1G_AABB_dynamic
├── callableshaderstress_1TLnBL1G_AABB_static
├── callableshaderstress_1TLnBL1G_tri_dynamic
├── callableshaderstress_1TLnBL1G_tri_static
├── callableshaderstress_1TLnBLnG_AABB_dynamic
├── callableshaderstress_1TLnBLnG_AABB_static
├── callableshaderstress_1TLnBLnG_tri_dynamic
├── callableshaderstress_1TLnBLnG_tri_static
├── cullmask_AABB
├── cullmask_AABB_extrabits
├── cullmask_tri
├── cullmask_tri_extrabits
├── empty_pipeline_layout
├── maxrayhitattributesize_1TL1BL1G
├── maxrayhitattributesize_1TL1BLnG
├── maxrayhitattributesize_1TLnBL1G
├── maxrayhitattributesize_1TLnBLnG
├── maxrtinvocations_AABB
├── maxrtinvocations_tri
├── memory_access
├── mixedPrimTL
├── null_miss
├── raypayloadin_AABB
├── raypayloadin_tri
├── recursiveTraces_AABB_0
├── recursiveTraces_AABB_1
├── recursiveTraces_AABB_10
├── recursiveTraces_AABB_11
├── recursiveTraces_AABB_12
├── recursiveTraces_AABB_13
├── recursiveTraces_AABB_14
├── recursiveTraces_AABB_15
├── recursiveTraces_AABB_2
├── recursiveTraces_AABB_3
├── recursiveTraces_AABB_4
├── recursiveTraces_AABB_5
├── recursiveTraces_AABB_6
├── recursiveTraces_AABB_7
├── recursiveTraces_AABB_8
├── recursiveTraces_AABB_9
├── recursiveTraces_tri_0
├── recursiveTraces_tri_1
├── recursiveTraces_tri_10
├── recursiveTraces_tri_11
├── recursiveTraces_tri_12
├── recursiveTraces_tri_13
├── recursiveTraces_tri_14
├── recursiveTraces_tri_15
├── recursiveTraces_tri_2
├── recursiveTraces_tri_3
├── recursiveTraces_tri_4
├── recursiveTraces_tri_5
├── recursiveTraces_tri_6
├── recursiveTraces_tri_7
├── recursiveTraces_tri_8
├── recursiveTraces_tri_9
├── report_intersection_result
├── reuse_creation_buffer_bottom
├── reuse_creation_buffer_top
├── reuse_scratch_buffer
├── shaderRecordExplicitSTD430Offset_1
├── shaderRecordExplicitSTD430Offset_2
├── shaderRecordExplicitSTD430Offset_3
├── shaderRecordExplicitSTD430Offset_4
├── shaderRecordExplicitSTD430Offset_5
├── shaderRecordExplicitSTD430Offset_6
├── shaderRecordExplicitScalarOffset_1
├── shaderRecordExplicitScalarOffset_2
├── shaderRecordExplicitScalarOffset_3
├── shaderRecordExplicitScalarOffset_4
├── shaderRecordExplicitScalarOffset_5
├── shaderRecordExplicitScalarOffset_6
├── shaderRecordSTD430_1
├── shaderRecordSTD430_2
├── shaderRecordSTD430_3
├── shaderRecordSTD430_4
├── shaderRecordSTD430_5
├── shaderRecordSTD430_6
├── shaderRecordScalar_1
├── shaderRecordScalar_2
├── shaderRecordScalar_3
├── shaderRecordScalar_4
├── shaderRecordScalar_5
├── shaderRecordScalar_6
├── shaders_from_lib
├── update_empty_bottom
└── update_empty_top
```

The `misc` family has no intermediate nodes. All 113 direct children are test case leaves. The leaves group into 18 behavioral clusters explained in `## Behavior Parameters`. The registered identifiers use the suffixes `1TL1BL1G`, `1TL1BLnG`, `1TLnBL1G`, and `1TLnBLnG` for the four acceleration structure layouts (one/many TL, one/many BL, one/many geometries), and `AABB` or `tri` for the geometry type.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Behavioral group | `callableshaderstress`, `AS_stresstest`, `cullmask`, `maxrayhitattributesize`, `maxrtinvocations`, `NO_DUPLICATE_ANY_HIT`, `mixedPrimTL`, `report_intersection_result`, `raypayloadin`, `recursiveTraces`, `shaderRecord`, `Op*` termination, `memory_access`, `null_miss`, `empty_pipeline_layout`, `reuse`, `update_empty`, `shaders_from_lib` | Selects which ray tracing mechanism the leaf exercises. This is the primary behavioral axis. | [vktRayTracingMiscTests.cpp#L10910-L11241](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10910-L11241) |
| Acceleration structure layout | `1TL1BL1G`, `1TL1BLnG`, `1TLnBL1G`, `1TLnBLnG` | Varies TLAS/BLAS/geometry count. Used by `callableshaderstress`, `NO_DUPLICATE_ANY_HIT`, `maxrayhitattributesize`. `AS_stresstest`, `cullmask`, `maxrtinvocations`, `raypayloadin`, `recursiveTraces` fix one layout. | [vktRayTracingMiscTests.cpp#L309-L357](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L309-L357) |
| Geometry type | `AABB`, `tri` | Triangle BLAS or AABB procedural BLAS. AABB needs an intersection shader. Used by most matrix-expanded groups. | [vktRayTracingMiscTests.cpp#L309-L357](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L309-L357) |
| Callable stress mode | `static`, `dynamic` | `dynamic` chains 8 callable levels; `static` chains 2. | [vktRayTracingMiscTests.cpp#L10917-L10931](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10917-L10931) |
| Cull mask extra bits | (absent), `_extrabits` | `extrabits` ORs `0x00FFFFFF` into the mask to confirm the implementation ignores upper bits. | [vktRayTracingMiscTests.cpp#L10953-L10966](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10953-L10966) |
| Recursion depth | `0`..`15` | Specialization constant `MAX_RECURSIVE_DEPTH`. Depth 0 records one rgen item per ray and traces nothing. | [vktRayTracingMiscTests.cpp#L11153-L11181](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L11153-L11181) |
| Shader record layout | `STD430`, `Scalar`, `ExplicitScalarOffset`, `ExplicitSTD430Offset` | SBT memory layout qualifier. Scalar variants need `VK_EXT_scalar_block_layout`. | [vktRayTracingMiscTests.cpp#L3756-L4055](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L3756-L4055) |
| Shader record type group | `1`..`6` | Type set in the record block: 1 = float/vec/mat2-4/int/uint, 2 = double/dvec/dmat2-3, 3 = dmat3-4, 4 = 16-bit, 5 = 64-bit, 6 = 8-bit. | [vktRayTracingMiscTests.cpp#L3756-L4055](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L3756-L4055) |
| Termination mode | `AnyHitStatically`, `AnyHitDynamically`, `IntersectionStatically`, `IntersectionDynamically` | Combines the op (`OpIgnoreIntersectionKHR`, `OpTerminateRayKHR`) with the stage (any-hit, intersection) and control flow (static, dynamic). | [vktRayTracingMiscTests.cpp#L11183-L11221](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L11183-L11221) |

## Behavior Parameters

The primary behavioral axis is the behavioral group. The `misc` family is heterogeneous, so no single registered dimension controls behavior across all 111 leaves. Each subsection below covers one behavioral cluster and its registered leaves.

### callableshaderstress — Callable shader invocation stress

Leaves: `callableshaderstress_<layout>_<geom>_<mode>` (16 leaves). Dispatches 128 rays from a raygen shader that invokes callable level 0. Each callable level N invokes level N+1 and records a result item tagged with shader stage, origin ray, level, and data chunk. The `dynamic` mode chains 8 levels; the `static` mode chains 2. The host verifies per-stage invocation counts match the expected binary chain.

### AS_stresstest — Multiple acceleration structures bound simultaneously

Leaves: `AS_stresstest_AABB`, `AS_stresstest_tri`. Binds up to 16 TLAS as a descriptor array and traces 16 separate dispatches, each with a push constant selecting the active AS index. Each AS hit reports its instance custom index and AS index. The host verifies each dispatch hits the correct AS with the correct instance index.

### cullmask — Cull mask filtering including extra upper bits

Leaves: `cullmask_<geom>` and `cullmask_<geom>_extrabits` (4 leaves). Builds a 3x5x17 grid (255 instances) and assigns cull masks 1..255. Each ray carries one cull mask and must hit exactly the instance whose mask matches. The `extrabits` variant ORs `0x00FFFFFF` into the mask to confirm the implementation uses only the low 8 bits.

### maxrayhitattributesize — Maximum ray hit attribute size

Leaves: `maxrayhitattributesize_<layout>` (4 leaves). Fills the hit attribute with `maxRayHitAttributeSize / sizeof(uint32_t)` U32s, sized through the `N_UINTS_IN_HIT_ATTRIBUTE` specialization constant. Intersection, any-hit, and closest-hit shaders write the attribute, and the host verifies each value matches `1 + nInvocation + nUint`.

### maxrtinvocations — Maximum ray dispatch invocation count

Leaves: `maxrtinvocations_AABB`, `maxrtinvocations_tri`. Dispatches `maxRayDispatchInvocationCount` rays and chunks the verification to avoid timeout. The host verifies every ray hit and that instance custom indices match the expected mapping.

### NO_DUPLICATE_ANY_HIT — No duplicate any-hit invocation flag

Leaves: `NO_DUPLICATE_ANY_HIT_<layout>_<geom>` (8 leaves). Builds a 4x4x4 grid with 32 rays and sets `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` on the BLAS. The host verifies each (instanceID, primitiveID, geometryIndex) tuple appears at most once per ray.

### mixedPrimTL — Mixed primitive types in one top-level AS

Leaf: `mixedPrimTL`. Builds a 720x1x1 grid mixing AABB and triangle BLAS instances in one TLAS. The any-hit shader stores `gl_InstanceCustomIndexEXT`, and the raygen uses `gl_RayFlagsCullBackFacingTrianglesEXT`. The host verifies each instance has a unique custom index 1..720.

### report_intersection_result — reportIntersectionEXT return value semantics

Leaf: `report_intersection_result`. The intersection shader calls `reportIntersectionEXT(0.7f, 0)` (rejected by any-hit since `gl_RayTmaxEXT` is in (0.6, 0.8)) then `reportIntersectionEXT(0.2f, 0)` (accepted). The host verifies exactly 1 rejected and 1 accepted intersection per ray across 16 rays.

### raypayloadin — Large ray payload propagation

Leaves: `raypayloadin_AABB`, `raypayloadin_tri`. Fills a ray payload with 512 U32s (`values[i] = 1+i`) sized through the `N_UINTS_IN_RAY_PAYLOAD` specialization constant. Closest-hit, any-hit, and miss shaders store the payload to the result buffer. The host verifies all values survive intact.

### recursiveTraces — Recursive ray tracing with specialization constant depth

Leaves: `recursiveTraces_<geom>_<depth>` for depth 0..15 (32 leaves). Dispatches 512 rays. The raygen records one item per ray and traces a hit ray and a miss ray at level 0. Each level-N closest-hit and miss shader records an item and, if `parentDepth < MAX_RECURSIVE_DEPTH - 1`, traces two more rays at level N+1. `MAX_RECURSIVE_DEPTH` is a specialization constant (constant ID 1) attached to closest-hit and miss stages. The host verifies the binary tree shape, parent/child links, and invocation counts. Depth 0 is degenerate: rgen records one item per ray and traces nothing.

### shaderRecord — Shader record block layout variants

Leaves: `shaderRecord<layout>_<group>` for 4 layouts and 6 type groups (24 leaves). Each leaf writes variables into the shader record block (`shaderRecordEXT`) under STD430, scalar, explicit scalar offset, or explicit STD430 offset layout. Miss, closest-hit, intersection, and any-hit shaders read the record and write values to the result buffer. The host verifies each stage read the correct value at the correct offset.

### termination — Ray termination control via ignoreIntersectionEXT and terminateRayEXT

Leaves: `OpIgnoreIntersectionKHR_AnyHitStatically`, `OpIgnoreIntersectionKHR_AnyHitDynamically`, `OpTerminateRayKHR_AnyHitStatically`, `OpTerminateRayKHR_AnyHitDynamically`, `OpTerminateRayKHR_IntersectionStatically`, `OpTerminateRayKHR_IntersectionDynamically` (6 leaves). Each leaf verifies a specific termination op under static (unconditional) or dynamic (gated on a result buffer value) control flow. The host checks a fixed `resultData[]` pattern per mode: ignore leaves expect `resultData[0]=0, resultData[1]=1`; terminate-any-hit leaves expect both zero; terminate-intersection leaves expect three zeros.

### memory_access — Memory access flag barrier variant

Leaf: `memory_access`. Reuses the `ReportIntersectionResultTest` infrastructure but swaps the acceleration structure build barriers from AS-specific access flags to `VK_ACCESS_MEMORY_WRITE_BIT` and `VK_ACCESS_MEMORY_READ_BIT`. The host verifies the same 1-rejected/1-accepted result as `report_intersection_result`, which confirms the broader barrier flags still synchronize the AS build.

### null_miss — Empty miss shader binding table entry

Leaf: `null_miss`. Builds a triangle BLAS and TLAS, then creates an empty miss SBT entry with a zeroed handle. The raygen traces a ray that misses all geometry. The host verifies the output buffer stays zero. A zero buffer means no miss shader executed despite the miss.

### empty_pipeline_layout — Pipeline with no descriptor sets

Leaf: `empty_pipeline_layout`. Creates a ray tracing pipeline with an empty pipeline layout (no descriptor sets) and empty rgen and miss shaders. The test passes if pipeline creation and the trace call do not crash.

### reuse — Creation and scratch buffer reuse

Leaves: `reuse_creation_buffer_top`, `reuse_creation_buffer_bottom`, `reuse_scratch_buffer` (3 leaves). `reuse_creation_buffer_*` builds a TLAS or BLAS into a 4 MB creation buffer, then creates another AS reusing the same buffer, then traces rays through the original AS to confirm the reuse did not corrupt live AS data. `reuse_scratch_buffer` builds two BLAS sharing one scratch buffer and verifies the image output after tracing.

### update_empty — Empty acceleration structure update

Leaves: `update_empty_bottom`, `update_empty_top` (2 leaves). Builds an empty BLAS or TLAS with `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` and `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR`, updates it in place (also empty), then traces a ray. The host verifies the miss shader runs. If the miss shader runs, the empty AS reports no hits after update.

### shaders_from_lib — Pipeline libraries for shader stages

Leaf: `shaders_from_lib`. Splits six shaders (rgen, intersection, any-hit, closest-hit, miss, callable) across two pipeline libraries created with `VK_PIPELINE_CREATE_LIBRARY_BIT_KHR`, links them into a final pipeline with four shader groups, and traces two rays (one hit, one miss). The host verifies all six stages wrote their unique index to the output buffer.

## Shader Analysis

The page uses one representative walkthrough because the `recursiveTraces` raygen shader captures the shared result-buffer recording pattern used across most `misc` leaves and shows the entry point of the recursion mechanism, which is the largest subfamily (32 leaves). The distinctive `MAX_RECURSIVE_DEPTH` specialization constant and the recursive `traceRayEXT` calls live in the closest-hit and miss shaders, covered in the parameter variation note.

### Representative Shader Walkthrough 1

**CTS case:** `ray_tracing_pipeline.misc.recursiveTraces_AABB_2`

**Source location:** [vktRayTracingMiscTests.cpp#L6482-L6535](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L6482-L6535)

**What this shader tests:** The raygen shader computes a linear invocation index from `gl_LaunchIDEXT`, records one result item into the storage buffer via `atomicAdd(nItemsStored, 1)`, then traces a hit ray and a miss ray at level 0. Each `traceRayEXT` carries a payload at location 0 holding the parent depth, origin ray, and result item index. The closest-hit and miss shaders at level 0 read that payload, record their own item, and recurse to level 1 if `parentDepth < MAX_RECURSIVE_DEPTH - 1`. With `MAX_RECURSIVE_DEPTH = 2`, the recursion stops after level 1 and produces a binary tree of 7 items per ray (`2^(depth+1) - 1`). If the implementation mishandles the specialization constant, the recursion either stops early or exceeds the depth, and host verification catches the wrong item count and wrong parent/child links.

**Shader-visible resources:**

- `%result` (`result`, set 0, binding 0, `std430` storage buffer): holds `nItemsStored`, `nCHitInvocations`, `nMissInvocations`, and a runtime array of `ResultData` items. Written by `OpAtomicIAdd` and `OpStore` through `OpAccessChain`.
- `%accelerationStructure` (set 0, binding 1, `UniformConstant` `OpTypeAccelerationStructureKHR`): the TLAS traversed by `OpTraceRayKHR`.
- `%gl_LaunchIDEXT` (`v3uint`, `BuiltIn LaunchIdKHR`): input giving the current invocation coordinates.
- `%gl_LaunchSizeEXT` (`v3uint`, `BuiltIn LaunchSizeKHR`): input giving the dispatch dimensions (512x1x1).
- `%__0` (`block`, `RayPayloadKHR`): the location-0 payload struct holding `currentDepth`, `currentNOriginRay`, `currentResultItem`.

**Reconstructed GLSL:**

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require

layout(set = 0, binding = 1) uniform accelerationStructureEXT accelerationStructure;

struct ResultData
{
    uint nOriginRay;
    uint shaderStage;
    uint depth;
    uint callerResultItem;
};

layout(set = 0, binding = 0, std430) buffer result
{
    uint       nItemsStored;
    uint       nCHitInvocations;
    uint       nMissInvocations;
    ResultData resultItems[];
};

layout(location = 0) rayPayloadEXT block
{
    uint currentDepth;
    uint currentNOriginRay;
    uint currentResultItem;
};

void main()
{
    uint nInvocation = gl_LaunchIDEXT.z * gl_LaunchSizeEXT.x * gl_LaunchSizeEXT.y
                     + gl_LaunchIDEXT.y * gl_LaunchSizeEXT.x + gl_LaunchIDEXT.x;
    uint  rayFlags      = 0;
    float tmin          = 0.001;
    float tmax          = 9.0;
    uint  cullMask      = 0xFF;
    vec3  cellStartXYZ  = vec3(0.0, 0.0, 0.0);
    vec3  cellEndXYZ    = cellStartXYZ + vec3(1.0);
    vec3  targetHit     = mix(cellStartXYZ, cellEndXYZ, vec3(0.5));
    vec3  targetMiss    = targetHit + vec3(0, 10, 0);
    vec3  origin        = targetHit - vec3(1, 0, 0);
    vec3  directionHit  = normalize(targetHit  - origin);
    vec3  directionMiss = normalize(targetMiss - origin);

    uint nItem = atomicAdd(nItemsStored, 1);

    if (nItem < 32792575)
    {
        resultItems[nItem].callerResultItem = 0xFFFFFFFF;
        resultItems[nItem].depth            = 0;
        resultItems[nItem].nOriginRay       = nInvocation;
        resultItems[nItem].shaderStage      = 3;
    }

    currentDepth      = 0;
    currentNOriginRay = nInvocation;
    currentResultItem = nItem;

    traceRayEXT(accelerationStructure, rayFlags, cullMask, 0, 0, 0, origin, tmin, directionHit,  tmax, 0);
    traceRayEXT(accelerationStructure, rayFlags, cullMask, 0, 0, 0, origin, tmin, directionMiss, tmax, 0);
}
```

Built with `glslangValidator -V --target-env spirv1.4 -S rgen`. Validated with `spirv-val --target-env spv1.4`. SPIR-V version 1.4, Bound 135. **Target SPIR-V environment:** `spirv1.4` (CTS build options target `vk::SPIRV_VERSION_1_4`).

**Parameter variation note:** The rgen shader is identical for every `recursiveTraces_*` depth from 1 through 15. The depth only changes the closest-hit and miss shader generators, which emit `depth` versions of each stage and gate recursion on `parentDepth < MAX_RECURSIVE_DEPTH - 1`. For depth 0, the source generator omits the payload definition and the two `traceRayEXT` calls, so only the rgen item recording remains. The `MAX_RECURSIVE_DEPTH` specialization constant (constant ID 1) is attached to closest-hit and miss stages only; the rgen does not consume it. AABB geometry adds an `intersection0` shader that calls `reportIntersectionEXT(0.95f, 0)`; triangle geometry uses the fixed-function triangle intersection instead. The `32792575` literal is the runtime bounds check `m_nMaxResultItemsPermitted`, derived from `(512 * 1024768 - 12) / 16`, which prevents the result buffer from overflowing on deep recursion.

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
; Bound: 135
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %_ %__0 %accelerationStructure
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %nInvocation "nInvocation"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %rayFlags "rayFlags"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %cullMask "cullMask"
               OpName %cellStartXYZ "cellStartXYZ"
               OpName %cellEndXYZ "cellEndXYZ"
               OpName %targetHit "targetHit"
               OpName %targetMiss "targetMiss"
               OpName %origin "origin"
               OpName %directionHit "directionHit"
               OpName %directionMiss "directionMiss"
               OpName %nItem "nItem"
               OpName %ResultData "ResultData"
               OpMemberName %ResultData 0 "nOriginRay"
               OpMemberName %ResultData 1 "shaderStage"
               OpMemberName %ResultData 2 "depth"
               OpMemberName %ResultData 3 "callerResultItem"
               OpName %result "result"
               OpMemberName %result 0 "nItemsStored"
               OpMemberName %result 1 "nCHitInvocations"
               OpMemberName %result 2 "nMissInvocations"
               OpMemberName %result 3 "resultItems"
               OpName %_ ""
               OpName %block "block"
               OpMemberName %block 0 "currentDepth"
               OpMemberName %block 1 "currentNOriginRay"
               OpMemberName %block 2 "currentResultItem"
               OpName %__0 ""
               OpName %accelerationStructure "accelerationStructure"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpMemberDecorate %ResultData 0 Offset 0
               OpMemberDecorate %ResultData 1 Offset 4
               OpMemberDecorate %ResultData 2 Offset 8
               OpMemberDecorate %ResultData 3 Offset 12
               OpDecorate %_runtimearr_ResultData ArrayStride 16
               OpDecorate %result Block
               OpMemberDecorate %result 0 Offset 0
               OpMemberDecorate %result 1 Offset 4
               OpMemberDecorate %result 2 Offset 8
               OpMemberDecorate %result 3 Offset 12
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %block Block
               OpDecorate %accelerationStructure Binding 1
               OpDecorate %accelerationStructure DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%float_0_00100000005 = OpConstant %float 0.00100000005
    %float_9 = OpConstant %float 9
   %uint_255 = OpConstant %uint 255
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
    %float_0 = OpConstant %float 0
         %47 = OpConstantComposite %v3float %float_0 %float_0 %float_0
    %float_1 = OpConstant %float 1
         %51 = OpConstantComposite %v3float %float_1 %float_1 %float_1
  %float_0_5 = OpConstant %float 0.5
         %57 = OpConstantComposite %v3float %float_0_5 %float_0_5 %float_0_5
   %float_10 = OpConstant %float 10
         %62 = OpConstantComposite %v3float %float_0 %float_10 %float_0
         %66 = OpConstantComposite %v3float %float_1 %float_0 %float_0
 %ResultData = OpTypeStruct %uint %uint %uint %uint
%_runtimearr_ResultData = OpTypeRuntimeArray %ResultData
     %result = OpTypeStruct %uint %uint %uint %_runtimearr_ResultData
%_ptr_StorageBuffer_result = OpTypePointer StorageBuffer %result
          %_ = OpVariable %_ptr_StorageBuffer_result StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%uint_32792575 = OpConstant %uint 32792575
       %bool = OpTypeBool
      %int_3 = OpConstant %int 3
%uint_4294967295 = OpConstant %uint 4294967295
      %int_2 = OpConstant %int 2
      %int_1 = OpConstant %int 1
     %uint_3 = OpConstant %uint 3
      %block = OpTypeStruct %uint %uint %uint
%_ptr_RayPayloadKHR_block = OpTypePointer RayPayloadKHR %block
        %__0 = OpVariable %_ptr_RayPayloadKHR_block RayPayloadKHR
%_ptr_RayPayloadKHR_uint = OpTypePointer RayPayloadKHR %uint
        %118 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_118 = OpTypePointer UniformConstant %118
%accelerationStructure = OpVariable %_ptr_UniformConstant_118 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
%nInvocation = OpVariable %_ptr_Function_uint Function
   %rayFlags = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
   %cullMask = OpVariable %_ptr_Function_uint Function
%cellStartXYZ = OpVariable %_ptr_Function_v3float Function
 %cellEndXYZ = OpVariable %_ptr_Function_v3float Function
  %targetHit = OpVariable %_ptr_Function_v3float Function
 %targetMiss = OpVariable %_ptr_Function_v3float Function
     %origin = OpVariable %_ptr_Function_v3float Function
%directionHit = OpVariable %_ptr_Function_v3float Function
%directionMiss = OpVariable %_ptr_Function_v3float Function
      %nItem = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_2
         %15 = OpLoad %uint %14
         %18 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %19 = OpLoad %uint %18
         %20 = OpIMul %uint %15 %19
         %22 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %20 %23
         %25 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpIAdd %uint %24 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %nInvocation %33
               OpStore %rayFlags %uint_0
               OpStore %tmin %float_0_00100000005
               OpStore %tmax %float_9
               OpStore %cullMask %uint_255
               OpStore %cellStartXYZ %47
         %49 = OpLoad %v3float %cellStartXYZ
         %52 = OpFAdd %v3float %49 %51
               OpStore %cellEndXYZ %52
         %54 = OpLoad %v3float %cellStartXYZ
         %55 = OpLoad %v3float %cellEndXYZ
         %58 = OpExtInst %v3float %1 FMix %54 %55 %57
               OpStore %targetHit %58
         %60 = OpLoad %v3float %targetHit
         %63 = OpFAdd %v3float %60 %62
               OpStore %targetMiss %63
         %65 = OpLoad %v3float %targetHit
         %67 = OpFSub %v3float %65 %66
               OpStore %origin %67
         %69 = OpLoad %v3float %targetHit
         %70 = OpLoad %v3float %origin
         %71 = OpFSub %v3float %69 %70
         %72 = OpExtInst %v3float %1 Normalize %71
               OpStore %directionHit %72
         %74 = OpLoad %v3float %targetMiss
         %75 = OpLoad %v3float %origin
         %76 = OpFSub %v3float %74 %75
         %77 = OpExtInst %v3float %1 Normalize %76
               OpStore %directionMiss %77
         %87 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0
         %88 = OpAtomicIAdd %uint %87 %uint_1 %uint_0 %uint_1
               OpStore %nItem %88
         %89 = OpLoad %uint %nItem
         %92 = OpULessThan %bool %89 %uint_32792575
               OpSelectionMerge %94 None
               OpBranchConditional %92 %93 %94
         %93 = OpLabel
         %96 = OpLoad %uint %nItem
         %98 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_3 %96 %int_3
               OpStore %98 %uint_4294967295
         %99 = OpLoad %uint %nItem
        %101 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_3 %99 %int_2
               OpStore %101 %uint_0
        %102 = OpLoad %uint %nItem
        %103 = OpLoad %uint %nInvocation
        %104 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_3 %102 %int_0
               OpStore %104 %103
        %105 = OpLoad %uint %nItem
        %108 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_3 %105 %int_1
               OpStore %108 %uint_3
               OpBranch %94
         %94 = OpLabel
        %113 = OpAccessChain %_ptr_RayPayloadKHR_uint %__0 %int_0
               OpStore %113 %uint_0
        %114 = OpLoad %uint %nInvocation
        %115 = OpAccessChain %_ptr_RayPayloadKHR_uint %__0 %int_1
               OpStore %115 %114
        %116 = OpLoad %uint %nItem
        %117 = OpAccessChain %_ptr_RayPayloadKHR_uint %__0 %int_2
               OpStore %117 %116
        %121 = OpLoad %118 %accelerationStructure
        %122 = OpLoad %uint %rayFlags
        %123 = OpLoad %uint %cullMask
        %124 = OpLoad %v3float %origin
        %125 = OpLoad %float %tmin
        %126 = OpLoad %v3float %directionHit
        %127 = OpLoad %float %tmax
               OpTraceRayKHR %121 %122 %123 %uint_0 %uint_0 %uint_0 %124 %125 %126 %127 %__0
        %128 = OpLoad %118 %accelerationStructure
        %129 = OpLoad %uint %rayFlags
        %130 = OpLoad %uint %cullMask
        %131 = OpLoad %v3float %origin
        %132 = OpLoad %float %tmin
        %133 = OpLoad %v3float %directionMiss
        %134 = OpLoad %float %tmax
               OpTraceRayKHR %128 %129 %130 %uint_0 %uint_0 %uint_0 %131 %132 %133 %134 %__0
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

The generic runner `RayTracingMiscTestInstance` drives every leaf that goes through the `TestBase` hierarchy. The standalone leaves (`null_miss`, `empty_pipeline_layout`, `reuse_*`, `update_empty_*`, `shaders_from_lib`) use their own instance functions but follow the same shape.

- **Descriptor setup:** binding 0 is a storage buffer holding the result data; binding 1 is an acceleration structure array sized by `getASBindingArraySize` (1 for most leaves, up to 16 for `AS_stresstest_*`).
- **Pipeline build:** the runner adds raygen, miss, any-hit, closest-hit, intersection, and callable shader modules reported by the test, attaching per-stage `VkSpecializationInfo` when the test supplies it (`recursiveTraces_*`, `maxrayhitattributesize_*`, `raypayloadin_*`).
- **Acceleration structure build:** each test's `initAS` builds the BLAS and TLAS through `GridASProvider` or `TriASProvider` on the command buffer. The `reuse_*` leaves build a second AS reusing the same creation or scratch buffer.
- **Shader binding table:** the runner builds the SBT, attaching shader record data for `shaderRecord*` leaves. `null_miss` zeroes the miss group handle.
- **Dispatch:** `vkCmdTraceRaysKHR` with the test's dispatch size (512 for `recursiveTraces_*`, 128 for `callableshaderstress_*`, 255 effective for `cullmask_*`, `maxRayDispatchInvocationCount` for `maxrtinvocations_*`, and so on).
- **Copyback and verification:** the runner copies the result buffer to host memory and calls the test's `verifyResultBuffer`, which returns the pass/fail verdict. `RayTracingMiscTestInstance::checkSupport` also verifies the result buffer size fits within `maxMemoryAllocationSize` and `maxStorageBufferRange` before execution.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `callableshaderstress` | Callable shader invocation count mismatch or callable data location corruption |
| `AS_stresstest` | TLAS array binding or per-AS instance index reporting failure |
| `cullmask` | Cull mask AND semantics wrong, or upper mask bits not ignored |
| `maxrayhitattributesize` | Hit attribute size above reported limit not supported, or attribute data corruption |
| `maxrtinvocations` | Dispatch above `maxRayDispatchInvocationCount` mishandled, or instance index reporting failure |
| `NO_DUPLICATE_ANY_HIT` | `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` not honored |
| `mixedPrimTL` | Mixed primitive type instances report wrong custom index or cull flags wrong |
| `report_intersection_result` | `reportIntersectionEXT` return value wrong, or any-hit reject/accept logic wrong |
| `raypayloadin` | Large ray payload corrupted across stages or specialization constant not substituted |
| `recursiveTraces` | Recursion depth limit wrong, specialization constant not substituted, or payload location corruption |
| `shaderRecord` | Shader record block memory layout wrong under STD430/scalar/explicit offset |
| `termination` | `ignoreIntersectionEXT` or `terminateRayEXT` not honored under static or dynamic control flow |
| `memory_access` | Barrier access flags wrong when using `VK_ACCESS_MEMORY_*` instead of AS-specific flags |
| `null_miss` | Implementation invokes a miss shader despite a zeroed SBT handle |
| `empty_pipeline_layout` | Pipeline creation crashes or rejects a layout with no descriptor sets |
| `reuse` | AS data corrupted when creation or scratch buffer is reused |
| `update_empty` | Empty AS update corrupts TLAS/BLAS state or reports a hit where none should exist |
| `shaders_from_lib` | Pipeline library linking drops or misroutes a shader stage |

### Cause Analysis

#### Invocation counting failures

**Possible failure symptoms:** `callableshaderstress_*` reports a per-stage invocation count that does not match the expected chain length (8 for dynamic, 2 for static). `recursiveTraces_*` reports `nCHitInvocations` or `nMissInvocations` that do not match `nItemsExpectedPerRay * nRaysToTest`, or the result item count does not match `nItemsExpectedPerRayInclRgen * nRaysToTest`.

**Possible implementation causes:** The callable or recursive shader stack mismanages SBT indexing across levels, dropping or duplicating invocations. For `recursiveTraces_*`, the implementation may not honor `maxRayRecursionDepth` or the `MAX_RECURSIVE_DEPTH` specialization constant, truncating or extending the recursion. The `recursiveTraces_*` payload uses `nLocationsPerPayload = 3` per level, so a payload location collision across recursion levels would corrupt `currentDepth`, `currentNOriginRay`, or `currentResultItem`. Source-level investigation is needed to distinguish stack exhaustion from a specialization constant substitution failure.

#### Acceleration structure reporting failures

**Possible failure symptoms:** `AS_stresstest_*` reports a wrong instance custom index or AS index for one of the 16 dispatches. `cullmask_*` reports fewer than 255 unique hits, a duplicate hit, or a mismatched instance custom index. `maxrtinvocations_*` reports a ray that missed or a wrong instance custom index. `mixedPrimTL` reports a duplicate or missing custom index in the 1..720 range.

**Possible implementation causes:** The TLAS array descriptor binding does not route `traceRayEXT` to the active AS selected by the push constant. The cull mask AND uses more than the low 8 bits (caught by `extrabits`) or skips an instance whose mask matches. `maxrtinvocations_*` exposes a dispatch path that does not scale to `maxRayDispatchInvocationCount` rays. `mixedPrimTL` exposes wrong `gl_InstanceCustomIndexEXT` reporting when AABB and triangle BLAS instances share a TLAS, or wrong `gl_RayFlagsCullBackFacingTrianglesEXT` handling for the mixed case.

#### Geometry flag and hit attribute failures

**Possible failure symptoms:** `NO_DUPLICATE_ANY_HIT_*` reports a (instanceID, primitiveID, geometryIndex) tuple appearing more than once per ray. `maxrayhitattributesize_*` reports an attribute value that does not match `1 + nInvocation + nUint`.

**Possible implementation causes:** The implementation does not honor `VK_GEOMETRY_NO_DUPLICATE_ANY_HIT_INVOCATION_BIT_KHR` and invokes any-hit more than once for the same candidate, which the per-ray tuple uniqueness check catches. For `maxrayhitattributesize_*`, the implementation truncates or corrupts the hit attribute when its size reaches `maxRayHitAttributeSize`, or the `N_UINTS_IN_HIT_ATTRIBUTE` specialization constant is not substituted and the shader uses the default value.

#### Intersection reporting and termination failures

**Possible failure symptoms:** `report_intersection_result` reports a reject count or accept count other than 1 per ray. `Op*` termination leaves report a `resultData[]` pattern that does not match the spec-defined expectation for the mode.

**Possible implementation causes:** `reportIntersectionEXT` returns the wrong boolean, so the intersection shader takes the wrong branch and the any-hit runs (or skips) incorrectly. The any-hit `gl_RayTmaxEXT` range check (0.6, 0.8) for rejection may be evaluated against a stale `t` value. For termination leaves, `ignoreIntersectionEXT` may not discard the candidate (so `resultData[0]` becomes 1 instead of 0), or `terminateRayEXT` may not stop traversal (so the miss shader runs and `resultData[1]` becomes 1 instead of 0). The "statically" variants test that the compiler does not fold the op away; the "dynamically" variants test that the implementation honors the op when gated on a runtime value.

#### Shader record layout failures

**Possible failure symptoms:** `shaderRecord*` leaves report a value read from the shader record block that does not match the value written by the host.

**Possible implementation causes:** The SBT memory layout does not match the qualifier under test. STD430 layout may misalign struct members; scalar layout (requiring `VK_EXT_scalar_block_layout`) may not pack tightly; explicit offset qualifiers may be ignored. The 8-bit, 16-bit, 64-bit, and double type groups expose layout or storage access bugs for those types. Source-level investigation is needed to confirm whether the failure is in SBT data upload or in shader-side offset computation.

#### Resource lifetime and pipeline creation failures

**Possible failure symptoms:** `reuse_creation_buffer_*` reports that rays traced through the original AS no longer hit after its creation buffer was reused. `reuse_scratch_buffer` reports a wrong image output. `update_empty_*` reports a hit where the empty AS should report none, or a miss where the miss shader should run. `null_miss` reports a nonzero output buffer value. `empty_pipeline_layout` crashes or fails pipeline creation. `shaders_from_lib` reports that one or more of the six stages did not write its index.

**Possible implementation causes:** Reusing a creation or scratch buffer overwrites AS metadata that the implementation still references, which corrupts traversal. Updating an empty AS with `ALLOW_UPDATE_BIT_KHR` may corrupt the TLAS or BLAS state. `null_miss` exposes a path that fetches a shader handle from a zeroed SBT entry instead of treating it as no shader. `empty_pipeline_layout` exposes a validation or driver path that rejects a layout with zero descriptor sets. `shaders_from_lib` exposes a pipeline library link step that drops a shader group or misroutes a stage to the wrong group.

## Case Pruning

### Requirement-based pruning

- `RayTracingTestCase::checkSupport` requires `VK_KHR_acceleration_structure`, `VK_KHR_buffer_device_address`, `VK_KHR_deferred_host_operations`, and `VK_KHR_ray_tracing_pipeline`, plus `rayTracingPipeline` and `accelerationStructure` features. Leaves that need more throw `NotSupportedError`.
- `shaderRecord*` scalar and explicit-scalar-offset variants require `VK_EXT_scalar_block_layout`. Type group 2 and 3 (double/dmat) require `shaderFloat64`. Type group 6 (8-bit) requires `storageBuffer8BitAccess`. Type groups 4 and 5 (16/64-bit integers) require `shaderInt16` and `shaderInt64`.
- `recursiveTraces_*` for depth N checks `maxRayRecursionDepth >= N` and throws `NotSupportedError` if the reported limit is too low.
- `RayTracingMiscTestInstance::checkSupport` throws `NotSupportedError` if the result buffer size exceeds `maxMemoryAllocationSize` or `maxStorageBufferRange`.

### Design-based pruning

- `recursiveTraces_*` registers depths 0..15 only, despite the `TestType` enum defining values through 29. The registration loop carries a TODO noting the 1..15 cap. Depth 0 is a degenerate case included to verify rgen item recording with no recursion.
- `Op*` termination leaves fix the geometry type per mode: triangles for any-hit modes, AABBs for intersection modes. They use `AccelerationStructureLayout::COUNT` as a sentinel since the layout is irrelevant to termination behavior.
- `AS_stresstest_*`, `cullmask_*`, `maxrtinvocations_*`, `raypayloadin_*`, and `recursiveTraces_*` fix the AS layout to `ONE_TL_MANY_BLS_ONE_GEOMETRY` or `ONE_TL_ONE_BL_ONE_GEOMETRY` because the tested behavior does not depend on the layout.
- `mixedPrimTL` is a single leaf, not matrix-expanded, because the test needs one TLAS with mixed primitive types.

## Key Takeaways

- The `misc` family is a heterogeneous collection of 111 test case leaves grouped into 18 behavioral clusters. The primary behavioral axis is the behavioral group, not a single registered dimension.
- Most leaves share the generic runner `RayTracingMiscTestInstance` and the result-storage-buffer pattern (binding 0, `atomicAdd` for item indexing, per-test `verifyResultBuffer`). The standalone leaves (`null_miss`, `empty_pipeline_layout`, `reuse_*`, `update_empty_*`, `shaders_from_lib`) use their own instance functions but verify the same kind of host-observable outcome.
- `recursiveTraces_*` is the largest subfamily (32 leaves) and the representative walkthrough target. The `MAX_RECURSIVE_DEPTH` specialization constant gates recursion in closest-hit and miss shaders; the rgen only seeds level 0.
- `shaderRecord*` is the largest matrix-expanded group (24 leaves) and the main consumer of feature gates (`VK_EXT_scalar_block_layout`, `shaderFloat64`, `storageBuffer8BitAccess`, `shaderInt16`, `shaderInt64`).
- The six `Op*` termination leaves distinguish static (unconditional) from dynamic (runtime-gated) control flow to defeat compiler folding and implementation elision.
- See `## Failure Meaning` for the per-cluster failure mechanism analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createMiscTests` registration | [vktRayTracingMiscTests.cpp#L10904-L11244](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10904-L11244) | Registers every direct child of `misc` |
| `RayTracingTestCase::checkSupport` | [vktRayTracingMiscTests.cpp#L10445-L10512](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10445-L10512) | Extension and feature gates, recursion depth limit check |
| `RayTracingMiscTestInstance::runTest` | [vktRayTracingMiscTests.cpp#L7958-L8417](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L7958-L8417) | Generic runner: pipeline, SBT, descriptor, trace, copyback |
| `RecursiveTracesTest::initPrograms` | [vktRayTracingMiscTests.cpp#L6228-L6536](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L6228-L6536) | Walkthrough shader source and specialization constant setup |
| `ReportIntersectionResultTest` | [vktRayTracingMiscTests.cpp#L6956-L7131](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L6956-L7131) | `reportIntersectionEXT` return value test |
| `TerminationTest` | [vktRayTracingMiscTests.cpp#L7431-L7910](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L7431-L7910) | `ignoreIntersectionEXT`/`terminateRayEXT` six modes |
| `ShaderRecordBlockTest` | [vktRayTracingMiscTests.cpp#L3756-L4055](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L3756-L4055) | 24 shader record layout variants |
| `ASStressTest` | [vktRayTracingMiscTests.cpp#L1401-L1751](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L1401-L1751) | Multiple TLAS bound as array |
| `CullMaskTest` | [vktRayTracingMiscTests.cpp#L2401-L2750](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L2401-L2750) | 255 cull masks plus extra bits variant |
| `CallableShaderStressTest` | [vktRayTracingMiscTests.cpp#L1753-L2400](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L1753-L2400) | Callable shader invocation chain |
| `MAXRayHitAttributeSizeTest` | [vktRayTracingMiscTests.cpp#L2752-L3082](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L2752-L3082) | Max hit attribute size |
| `MAXRTInvocationsSupportedTest` | [vktRayTracingMiscTests.cpp#L3083-L3441](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L3083-L3441) | Max ray dispatch invocation count |
| `NoDuplicateAnyHitTest` | [vktRayTracingMiscTests.cpp#L3442-L3701](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L3442-L3701) | No duplicate any-hit invocation flag |
| `RayPayloadInTest` | [vktRayTracingMiscTests.cpp#L7133-L7429](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L7133-L7429) | Large ray payload propagation |
| `nullMissInstance` | [vktRayTracingMiscTests.cpp#L8552-L8707](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L8552-L8707) | Empty miss SBT entry |
| `emptyPipelineLayoutInstance` | [vktRayTracingMiscTests.cpp#L8723-L8766](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L8723-L8766) | Empty pipeline layout creation |
| `reuseCreationBufferInstance` | [vktRayTracingMiscTests.cpp#L8779-L9024](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L8779-L9024) | Creation buffer reuse |
| `reuseScratchBufferInstance` | [vktRayTracingMiscTests.cpp#L9026-L9298](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L9026-L9298) | Scratch buffer reuse |
| `updateEmptyBottomASInstance` | [vktRayTracingMiscTests.cpp#L9300-L9668](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L9300-L9668) | Empty BLAS update |
| `updateEmptyTopASInstance` | [vktRayTracingMiscTests.cpp#L9669-L9951](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L9669-L9951) | Empty TLAS update |
| `shadersFromLibInstance` | [vktRayTracingMiscTests.cpp#L10052-L10415](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10052-L10415) | Pipeline library linking |
