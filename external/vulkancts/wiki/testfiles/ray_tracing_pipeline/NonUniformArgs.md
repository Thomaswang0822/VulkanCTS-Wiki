## Overview

**Core question:** When every `traceRayEXT` argument comes from a storage buffer (non-uniform), does the implementation select the right closest-hit shader from `sbtRecordOffset`, `sbtRecordStride`, and the hit geometry, and does it route to the right miss shader when one argument deliberately forces a miss?

- [vktRayTracingNonUniformArgsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp) implements the single test family `non_uniform_args` under the `ray_tracing_pipeline` test category.
- All 16 leaves share one rgen shader that loads every `traceRayEXT` argument from a storage buffer. No argument is a compile-time constant, so the driver must handle the non-uniform path for flags, cull mask, SBT offset, SBT stride, miss index, origin, Tmin, direction, and Tmax.
- The 10 `chit_*` leaves vary the SBT layout (1 through 4 ray types) and the active ray type. The ray hits the second of two geometries, so the hit SBT record index is `rayTypeCount + rayType`. The hit shader writes its specialization-constant ID to a result buffer; the host compares that single value against the expected ID.
- The 6 `miss_cause_*` leaves each flip one argument to a value that must force a miss (bad flags, mismatched cull mask, off-target origin, Tmin past the triangle, off-target direction, Tmax before the triangle). The miss shader writes its specialization-constant ID, and the host checks it equals the ID for `missIndex`.
- The page explains the two leaf groups, the shared rgen walkthrough, the single-value result check, and what a failure of each group points to.

## Background Knowledge

- **Non-uniform ray arguments.** `traceRayEXT` accepts arguments as runtime values. When those values come from a storage buffer instead of specialization constants or push constants, the driver must load and apply them per ray. This test isolates that path by sourcing every argument from one buffer.
- **SBT record selection for closest hit.** On a hit, the hit SBT record index is `sbtRecordBase` (0 here) plus `geometryIndex * sbtRecordStride + sbtRecordOffset`. The instance uses the default `sbtRecordOffset` of 0, so the per-ray `sbtRecordOffset` and `sbtRecordStride` arguments to `traceRayEXT` control which closest-hit shader runs.
- **Miss shader selection.** The `missIndex` argument to `traceRayEXT` selects a record from the miss SBT region. Each miss shader in this test is a copy of the same shader specialized with a distinct ID.
- **Ray flags and cull mask.** `rayFlags` can skip triangle or AABB hits; `SkipTrianglesKHR` (256) forces triangle hits to be skipped. `cullMask` is bitwise-ANDed with the instance mask; a zero result culls the instance.
- **Tmin and Tmax.** A hit is only reported for intersections whose `t` satisfies `Tmin <= t <= Tmax`. A `Tmin` past the geometry or a `Tmax` before it forces a miss.

## Registration Hierarchy

```text
ray_tracing_pipeline.non_uniform_args
├── chit_1_types_0
├── chit_2_types_0
├── chit_2_types_1
├── chit_3_types_0
├── chit_3_types_1
├── chit_3_types_2
├── chit_4_types_0
├── chit_4_types_1
├── chit_4_types_2
├── chit_4_types_3
├── miss_cause_1
├── miss_cause_2
├── miss_cause_3
├── miss_cause_4
├── miss_cause_5
└── miss_cause_6
```

The 16 direct children are registered by [createNonUniformArgsTests](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L517-L558). The 10 `chit_*` leaves come from the closest-hit loop over `typeCount` 1 to 4 and `rayType` 0 to `typeCount - 1` ([chit loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L522-L539)). The 6 `miss_cause_*` leaves come from the miss loop over `MissCause` values 1 to 6 ([miss loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L541-L555)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Leaf group | `chit_*`, `miss_cause_*` | Selects the tested property: closest-hit SBT selection or miss-cause invocation. This is the primary behavioral axis. | [createNonUniformArgsTests](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L517-L558) |
| Ray type count (`chit`) | `1`, `2`, `3`, `4` | Sets `sbtRecordStride` and the number of closest-hit shaders per geometry. Larger counts exercise deeper SBT layouts. | [chit loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L529-L538) |
| Ray type (`chit`) | `0` to `typeCount - 1` | Sets `sbtRecordOffset`. Selects which of the `typeCount` hit shaders runs for the hit geometry. | [chit loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L532-L537) |
| Miss cause (`miss_cause`) | `1`=FLAGS, `2`=CULL_MASK, `3`=ORIGIN, `4`=TMIN, `5`=DIRECTION, `6`=TMAX | Selects which argument is flipped to a bad value that must force a miss. `missIndex` is `causeIdx - 1`. | [MissCause enum](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L50-L60), [miss loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L548-L554) |
| Geometry count | 2 (offscreen first, onscreen second) | The hit geometry is always the second one, so `geometryIndex` is 1 and `sbtRecordStride` matters. | [geometries vector](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L291-L293) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L137) |

## Behavior Parameters

The primary behavioral axis is the leaf group. The 16 leaves cluster into two groups that test distinct properties, so each group gets its own subsection.

### chit_1_types_0 through chit_4_types_3 — closest-hit SBT selection via non-uniform offset and stride

The `chit` leaves set `miss=false` and feed good origin, direction, Tmin, Tmax, flags, and cull mask so the ray hits the onscreen triangle. The arguments that vary are `sbtRecordOffset` (set to `rayType`) and `sbtRecordStride` (set to `rayTypeCount`). The BLAS has two geometries; the offscreen triangle is added first so the hit geometry has `geometryIndex=1`. The hit SBT is laid out as `typeCount` closest-hit shaders per geometry, so the shader for `(geometryIndex=1, rayType)` sits at SBT index `rayTypeCount + rayType`. Each closest-hit shader is a copy of the same source specialized with `chitShaderId = makeChitId(index)`, where `index` matches the SBT position. The host expects the result buffer to hold `makeChitId(rayTypeCount + rayType)`, which is `(2 << 16) | (rayTypeCount + rayType)`. Scaling `typeCount` from 1 to 4 grows the SBT from 2 to 8 hit records and checks the offset/stride arithmetic at each size.

### miss_cause_1 through miss_cause_6 — miss shader invoked by one bad non-uniform argument

The `miss_cause` leaves set `miss=true` and fix `rayTypeCount=1`, `rayType=0`. One argument is flipped to a bad value based on `MissCause`; the rest stay good. The ray must miss, invoking the miss shader selected by `missIndex = causeIdx - 1`. Each miss shader is a copy of the same source specialized with `missShaderId = makeMissId(missIndex)`, where `missIndex` matches the SBT position. The host expects the result buffer to hold `makeMissId(missIndex)`, which is `(1 << 16) | missIndex`. The six causes and their bad values are: FLAGS uses `rayFlags=256` (`SkipTrianglesKHR`) so triangle hits are skipped; CULL_MASK uses `cullMask=0xF0` which does not match the instance mask `0x0F`; ORIGIN uses `(0, 8, 0)` which is too high for the triangle at `y=2`; TMIN uses `5.5` which starts after the triangle at `z=5`; DIRECTION uses `(1, 0, 0)` which points away from the geometry; TMAX uses `4.5` which ends before the triangle at `z=5`.

## Shader Analysis

The rgen shader is the representative walkthrough because it is where `traceRayEXT` receives every argument from the storage buffer. The closest-hit and miss shaders are trivial: each writes a single specialization-constant value to the result buffer. The rgen text is identical across all 16 leaves; only the buffer contents and the specialization constants differ.

### Representative Shader Walkthrough 1: `non_uniform_args.chit_2_types_1` rgen

**CTS case:** `dEQP-VK.ray_tracing_pipeline.non_uniform_args.chit_2_types_1`

**Source:** reconstructed from [NonUniformArgsCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L135-L205), which adds `glu::RaygenSource(rgen.str())` with `ShaderBuildOptions` targeting `SPIRV_VERSION_1_4`. The case `chit_2_types_1` feeds `sbtRecordOffset=1`, `sbtRecordStride=2`, and good values for the other arguments, so the ray hits the onscreen triangle and the closest-hit shader at SBT index `2 + 1 = 3` runs.

**Stage:** Ray generation (`VK_SHADER_STAGE_RAYGEN_BIT_KHR`).

**Resources:**

- `topLevelAS` (set 0, binding 0): `accelerationStructureEXT`. The TLAS instances one BLAS with two triangle geometries. The instance mask is `0x0F` and triangle facing cull is disabled.
- `args` (set 0, binding 1): `ArgumentsBlock` storage buffer holding `origin`, `direction`, `Tmin`, `Tmax`, `rayFlags`, `cullMask`, `sbtRecordOffset`, `sbtRecordStride`, `missIndex`. The host fills this with the case's good or bad values before the trace.
- `result` (set 0, binding 2): `ResultBlock` storage buffer holding one `uint shaderId`. It is zeroed before the trace; the hit or miss shader writes its specialization-constant ID here.
- `unused` (location 0): `rayPayloadEXT vec4`. Declared to satisfy `traceRayEXT`'s signature; neither rgen nor the hit/miss shaders read or write it.

**Shader logic:**

The rgen loads the TLAS descriptor, then loads each argument field from the `args` storage buffer. It swizzles `origin.xyz` and `direction.xyz` from their `vec4` storage. It calls `traceRayEXT(topLevelAS, args.rayFlags, args.cullMask, args.sbtRecordOffset, args.sbtRecordStride, args.missIndex, args.origin.xyz, args.Tmin, args.direction.xyz, args.Tmax, 0)`. No argument is a compile-time constant, so the driver must apply each one at trace time. For `chit_2_types_1` the buffer holds `sbtRecordOffset=1`, `sbtRecordStride=2`, and good values for origin, direction, Tmin, Tmax, flags, and cull mask, so traversal hits the onscreen triangle and the hit SBT index resolves to `1 * 2 + 1 = 3`.

#### Reconstructed GLSL

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require

layout(set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
layout(set=0, binding=1, std430) buffer ArgumentsBlock {
  vec4  origin;
  vec4  direction;
  float Tmin;
  float Tmax;
  uint  rayFlags;
  uint  cullMask;
  uint  sbtRecordOffset;
  uint  sbtRecordStride;
  uint  missIndex;
} args;
layout(set=0, binding=2, std430) buffer ResultBlock {
  uint shaderId;
} result;
layout(location=0) rayPayloadEXT vec4 unused;

void main()
{
  traceRayEXT(topLevelAS,
    args.rayFlags,
    args.cullMask,
    args.sbtRecordOffset,
    args.sbtRecordStride,
    args.missIndex,
    args.origin.xyz,
    args.Tmin,
    args.direction.xyz,
    args.Tmax,
    0);
}
```

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
; Bound: 55
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %topLevelAS %args %unused %result
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %topLevelAS "topLevelAS"
               OpName %ArgumentsBlock "ArgumentsBlock"
               OpMemberName %ArgumentsBlock 0 "origin"
               OpMemberName %ArgumentsBlock 1 "direction"
               OpMemberName %ArgumentsBlock 2 "Tmin"
               OpMemberName %ArgumentsBlock 3 "Tmax"
               OpMemberName %ArgumentsBlock 4 "rayFlags"
               OpMemberName %ArgumentsBlock 5 "cullMask"
               OpMemberName %ArgumentsBlock 6 "sbtRecordOffset"
               OpMemberName %ArgumentsBlock 7 "sbtRecordStride"
               OpMemberName %ArgumentsBlock 8 "missIndex"
               OpName %args "args"
               OpName %unused "unused"
               OpName %ResultBlock "ResultBlock"
               OpMemberName %ResultBlock 0 "shaderId"
               OpName %result "result"
               OpDecorate %topLevelAS Binding 0
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %ArgumentsBlock Block
               OpMemberDecorate %ArgumentsBlock 0 Offset 0
               OpMemberDecorate %ArgumentsBlock 1 Offset 16
               OpMemberDecorate %ArgumentsBlock 2 Offset 32
               OpMemberDecorate %ArgumentsBlock 3 Offset 36
               OpMemberDecorate %ArgumentsBlock 4 Offset 40
               OpMemberDecorate %ArgumentsBlock 5 Offset 44
               OpMemberDecorate %ArgumentsBlock 6 Offset 48
               OpMemberDecorate %ArgumentsBlock 7 Offset 52
               OpMemberDecorate %ArgumentsBlock 8 Offset 56
               OpDecorate %args Binding 1
               OpDecorate %args DescriptorSet 0
               OpDecorate %ResultBlock Block
               OpMemberDecorate %ResultBlock 0 Offset 0
               OpDecorate %result Binding 2
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
          %6 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_6 = OpTypePointer UniformConstant %6
 %topLevelAS = OpVariable %_ptr_UniformConstant_6 UniformConstant
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
%ArgumentsBlock = OpTypeStruct %v4float %v4float %float %float %uint %uint %uint %uint %uint
%_ptr_StorageBuffer_ArgumentsBlock = OpTypePointer StorageBuffer %ArgumentsBlock
       %args = OpVariable %_ptr_StorageBuffer_ArgumentsBlock StorageBuffer
        %int = OpTypeInt 32 1
      %int_4 = OpConstant %int 4
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_5 = OpConstant %int 5
      %int_6 = OpConstant %int 6
      %int_7 = OpConstant %int 7
      %int_8 = OpConstant %int 8
      %int_0 = OpConstant %int 0
    %v3float = OpTypeVector %float 3
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
      %int_2 = OpConstant %int 2
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
      %int_1 = OpConstant %int 1
      %int_3 = OpConstant %int 3
%_ptr_RayPayloadKHR_v4float = OpTypePointer RayPayloadKHR %v4float
     %unused = OpVariable %_ptr_RayPayloadKHR_v4float RayPayloadKHR
%ResultBlock = OpTypeStruct %uint
%_ptr_StorageBuffer_ResultBlock = OpTypePointer StorageBuffer %ResultBlock
     %result = OpVariable %_ptr_StorageBuffer_ResultBlock StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
          %9 = OpLoad %6 %topLevelAS
         %19 = OpAccessChain %_ptr_StorageBuffer_uint %args %int_4
         %20 = OpLoad %uint %19
         %22 = OpAccessChain %_ptr_StorageBuffer_uint %args %int_5
         %23 = OpLoad %uint %22
         %25 = OpAccessChain %_ptr_StorageBuffer_uint %args %int_6
         %26 = OpLoad %uint %25
         %28 = OpAccessChain %_ptr_StorageBuffer_uint %args %int_7
         %29 = OpLoad %uint %28
         %31 = OpAccessChain %_ptr_StorageBuffer_uint %args %int_8
         %32 = OpLoad %uint %31
         %36 = OpAccessChain %_ptr_StorageBuffer_v4float %args %int_0
         %37 = OpLoad %v4float %36
         %38 = OpVectorShuffle %v3float %37 %37 0 1 2
         %41 = OpAccessChain %_ptr_StorageBuffer_float %args %int_2
         %42 = OpLoad %float %41
         %44 = OpAccessChain %_ptr_StorageBuffer_v4float %args %int_1
         %45 = OpLoad %v4float %44
         %46 = OpVectorShuffle %v3float %45 %45 0 1 2
         %48 = OpAccessChain %_ptr_StorageBuffer_float %args %int_3
         %49 = OpLoad %float %48
               OpTraceRayKHR %9 %20 %23 %26 %29 %32 %38 %42 %46 %49 %unused
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

### Scene construction

- The BLAS holds two triangle geometries. The offscreen triangle sits at `z=-5` and the onscreen triangle at `z=5`, both centered at `(x=0, y=2)` ([geometry constants](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L251-L262)). The offscreen triangle is added first so the hit geometry has `geometryIndex=1`.
- The TLAS instances the BLAS once with an identity transform, instance mask `0x0F`, and `VK_GEOMETRY_INSTANCE_TRIANGLE_FACING_CULL_DISABLE_BIT_KHR` ([TLAS setup](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L301-L304)).
- Good ray values target the onscreen triangle: origin `(0, 2, 0)`, direction `(0, 0, 1)`, `Tmin=4.0`, `Tmax=6.0`, `rayFlags=0`, `cullMask=0x0F` ([good/bad constants](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L263-L274)).

### Pipeline and SBT setup

- One raygen, one miss shader per `missIndex` up to the case's `missIndex`, and one closest-hit shader per `(geometry, rayType)` pair. Each hit and miss shader is a copy of the same source specialized with a distinct ID built by `makeChitId` or `makeMissId` ([shader ID helpers](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L218-L236)).
- The closest-hit shaders are added in geometry-major, rayType-minor order, so SBT index `geometryIndex * rayTypeCount + rayType` maps to the shader specialized with `makeChitId` of that index ([chit shader loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L398-L400), [pipeline add loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L432-L438)).
- The miss shaders are added in `missIndex` order from 0 to the case's `missIndex` ([miss shader loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L391-L393), [pipeline add loop](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L422-L428)).
- SBT regions are created with `shaderGroupHandleSize` stride and `shaderGroupBaseAlignment` from the ray tracing properties ([SBT creation](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L442-L459)).

### Buffer fill and trace

- The host fills the `args` storage buffer with the case's good or bad values. For miss cases, only the field matching `MissCause` gets the bad value; the rest stay good ([buffer fill](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L463-L480)).
- The result buffer is zeroed before the trace ([output clear](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L318-L320)).
- `cmdTraceRaysKHR` dispatches `1 x 1 x 1` rays. A `SHADER_WRITE` to `HOST_READ` pipeline barrier follows ([trace and barrier](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L483-L491)).

### Result check

- The host reads one `uint32_t` from the result buffer. The expected value is `makeChitId(rayTypeCount + rayType)` for chit cases and `makeMissId(missIndex)` for miss cases ([expected value](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L498-L501)).
- Pass condition: `outputVal == expectedVal`. A mismatch fails with a message showing both values in hex ([iterate](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L503-L512)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `chit_*` | The implementation computed the wrong hit SBT record index from `sbtRecordOffset`, `sbtRecordStride`, and `geometryIndex`, so the wrong closest-hit shader ran, no shader ran, or the miss shader ran when it should not have. |
| `miss_cause_*` | The implementation did not treat the bad argument as a miss cause (a hit shader ran), or it routed to the wrong miss shader because `missIndex` was mishandled. |

All leaves share the rgen shader, the `args` buffer layout, the AS construction, and the single-value result check. A failure common to every leaf points at this shared infrastructure rather than a leaf-specific issue.

### Cause Analysis

#### Wrong closest-hit SBT record selection

**Possible failure symptoms:** The result value is not `makeChitId(rayTypeCount + rayType)`. It may be `makeChitId` of a different index (a different hit shader ran), `makeMissId(...)` (the miss shader ran when the ray should have hit), or `0` (no shader wrote the result buffer). The hex failure message identifies which value was observed.

**Possible implementation causes:** The hit SBT index is `sbtRecordBase + geometryIndex * sbtRecordStride + sbtRecordOffset`. With `sbtRecordBase=0`, `geometryIndex=1`, `sbtRecordStride=rayTypeCount`, and `sbtRecordOffset=rayType`, the index is `rayTypeCount + rayType`. If the implementation misapplies the stride, the offset, or the geometry index, a different shader runs. A grounded investigation should confirm the host laid out the SBT in geometry-major, rayType-minor order (it does, per the add loop) and that the buffer's `sbtRecordOffset` and `sbtRecordStride` match the case parameters. If a miss shader runs instead, the implementation may have treated a good argument as a miss cause. Source-level inspection of the buffer fill and the SBT add order is needed to confirm the expected index.

#### Bad argument did not cause a miss

**Possible failure symptoms:** A `miss_cause_*` leaf fails with the result value equal to `makeChitId(...)` instead of `makeMissId(missIndex)`. A closest-hit shader ran when the bad argument should have forced a miss.

**Possible implementation causes:** Each cause tests one argument. For FLAGS (`SkipTrianglesKHR=256`), the spec requires triangle hits to be skipped, so the implementation must not report a triangle intersection. For CULL_MASK (`0xF0` vs instance `0x0F`), the bitwise-AND is zero, so the instance must be culled. For ORIGIN (`(0,8,0)`) and DIRECTION (`(1,0,0)`), the ray does not intersect the triangle, so traversal must find no hit. For TMIN (`5.5`) and TMAX (`4.5`), the triangle at `z=5` is outside the valid `t` interval, so no hit is reported. A failure means the implementation did not apply the bad argument correctly. Source-level investigation should confirm the host actually wrote the bad value to the buffer (it does, per the fill logic) and that the good values for the other arguments would hit the onscreen triangle on their own.

#### Wrong miss shader fired

**Possible failure symptoms:** A `miss_cause_*` leaf fails with the result value equal to `makeMissId` of a different index, or `0` if no miss shader ran. The miss SBT has `missIndex + 1` entries; the case expects the entry at `missIndex` to fire.

**Possible implementation causes:** The `missIndex` argument to `traceRayEXT` selects the miss SBT record. If the implementation misroutes `missIndex` (for example, ignoring it or using a wrong stride), the wrong miss shader runs. A grounded investigation should confirm the miss SBT was created with `missIndex + 1` entries in index order and that the host wrote the correct `missIndex` to the buffer. The miss shaders are all copies of the same source specialized with distinct IDs, so a wrong ID directly identifies which miss shader ran.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, checked in [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L116-L120). Missing functionality throws `NotSupportedError`.
- No device limits are checked at instance time. The SBT sizes are small (at most 8 hit records and 6 miss records), so `maxShaderGroupStride` and `shaderGroupBaseAlignment` do not prune any case.

### Design-based pruning

- `typeCount` is capped at 4, giving 10 `chit_*` leaves. Larger counts would not test a new property; they would only grow the SBT.
- Miss causes are limited to the 6 `MissCause` enum values (FLAGS, CULL_MASK, ORIGIN, TMIN, DIRECTION, TMAX). `NONE` is skipped because it is the chit-case behavior, and `CAUSE_COUNT` is a sentinel.
- Each `miss_cause_*` leaf flips exactly one argument. Combinations of bad arguments are not generated because a single bad argument is enough to force a miss, and combining them would not isolate which argument caused the failure.

## Key Takeaways

- The `non_uniform_args` family isolates the non-uniform `traceRayEXT` path: every argument comes from a storage buffer, so the driver must load and apply each one at trace time.
- The 10 `chit_*` leaves prove that `sbtRecordOffset`, `sbtRecordStride`, and `geometryIndex` together select the right closest-hit shader. Scaling `typeCount` from 1 to 4 grows the SBT and checks the index arithmetic at each size.
- The 6 `miss_cause_*` leaves prove that each argument type can independently force a miss, and that `missIndex` selects the right miss shader. Each leaf flips exactly one argument so the failure isolates to that argument.
- The result check is a single `uint32_t` comparison. The expected value encodes the shader kind (1 for miss, 2 for closest hit) in the high 16 bits and the shader index in the low 16 bits, so a wrong value directly identifies which shader ran.
- See `## Failure Meaning` for the per-leaf-group cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `MissCause` enum | [vktRayTracingNonUniformArgsTests.cpp#L50-L60](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L50-L60) | Defines the 6 miss causes mapped to `miss_cause_*` leaves |
| `NonUniformParams` struct | [vktRayTracingNonUniformArgsTests.cpp#L62-L77](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L62-L77) | Per-case parameters: hit `rayTypeCount`/`rayType` or miss `missCause`/`missIndex` |
| `ArgsBufferData` struct | [vktRayTracingNonUniformArgsTests.cpp#L122-L133](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L122-L133) | Storage buffer layout read by the rgen shader |
| `initPrograms` | [vktRayTracingNonUniformArgsTests.cpp#L135-L205](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L135-L205) | rgen, chit, and miss shader generation; rgen loads all args from the buffer |
| `makeMissId` / `makeChitId` | [vktRayTracingNonUniformArgsTests.cpp#L226-L236](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L226-L236) | Build the expected result IDs: `(1<<16)\|index` for miss, `(2<<16)\|index` for chit |
| `iterate` | [vktRayTracingNonUniformArgsTests.cpp#L238-L513](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L238-L513) | Scene setup, SBT layout, buffer fill, trace, and single-value result check |
| Good/bad argument constants | [vktRayTracingNonUniformArgsTests.cpp#L251-L274](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L251-L274) | Triangle positions and the good/bad values for each miss cause |
| Buffer fill | [vktRayTracingNonUniformArgsTests.cpp#L463-L480](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L463-L480) | Selects good or bad value per field based on `MissCause` |
| Expected value and pass/fail | [vktRayTracingNonUniformArgsTests.cpp#L498-L512](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L498-L512) | `makeChitId`/`makeMissId` comparison and failure message |
| `createNonUniformArgsTests` | [vktRayTracingNonUniformArgsTests.cpp#L517-L558](../../../modules/vulkan/ray_tracing/vktRayTracingNonUniformArgsTests.cpp#L517-L558) | Registration of the `non_uniform_args` group and its 16 children |
