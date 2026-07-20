## Overview

**Core question:** Do `VK_EXT_ray_tracing_invocation_reorder` (`GL_EXT_shader_invocation_reorder`) reorder entry points and the `hitObjectEXT` API preserve ray tracing execution invariants across built-in, motion, and large-dimension launch shapes?

- [vktRayTracingShaderExecutionReorderTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp) implements the test family `ser` under the `ray_tracing_pipeline` test category.
- The family splits into four intermediate nodes registered by [createShaderExecutionReorderTests](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2364): `builtin_var`, `reorder`, `motion`, and `large_dim`.
- The core test idea is invariant checking: a correct implementation produces the same observable result with or without reordering. Reorder hints are optimization hints, not synchronization primitives, so the tests verify payload, SBT selection, hit object state, and subgroup reductions rather than the reordering itself.
- The page explains the four intermediate-node behaviors, the representative `reorder.reorder_hint` shader walkthrough, the dual image-vs-storage-buffer validation path, and what each failure mode points to.

## Background Knowledge

- `VK_EXT_ray_tracing_invocation_reorder` exposes `GL_EXT_shader_invocation_reorder` and the SPIR-V capability `ShaderInvocationReorderEXT`. The implementation may honor or ignore a reorder hint; observable invariants must hold in both cases.
- `hitObjectEXT` is the opaque type from the same extension. A hit object records the result of a trace, a miss, or a ray query and can later be executed, inspected, or used as a reorder hint. Tested operations include `hitObjectTraceRayEXT`, `hitObjectRecordEmptyEXT`, `hitObjectRecordMissEXT`, `hitObjectRecordFromQueryEXT`, `hitObjectExecuteShaderEXT`, `hitObjectReorderExecuteEXT`, `hitObjectTraceReorderExecuteEXT`, and a large set of property getters.
- Three reorder entry points exist: `reorderThreadEXT(uint hint, uint bits)` (hint-only), `reorderThreadEXT(hitObjectEXT hObj)` (hit-object-as-hint), and `reorderThreadEXT(hitObjectEXT hObj, uint hint, uint bits)` (combined). `hitObjectReorderExecuteEXT` and `hitObjectTraceReorderExecuteEXT` fold reorder plus execute (and plus trace) into a single call.
- `VK_NV_ray_tracing_motion_blur` adds motion variants: `hitObjectTraceRayMotionEXT`, `hitObjectRecordMissMotionEXT`, `hitObjectGetCurrentTimeEXT`, and `hitObjectTraceMotionReorderExecuteEXT`. Motion BLAS carries a rest-pose and a t=1.0 shifted geometry; the TLAS, BLAS, and pipeline carry motion create flags.
- Large-dimension cases stress `VkPhysicalDeviceLimits::maxImageDimension2D` and `VkPhysicalDeviceRayTracingPipelinePropertiesKHR::maxRayDispatchInvocationCount`. The checkSupport step throws `NotSupportedError` when either limit is exceeded.

## Registration Hierarchy

```text
ray_tracing_pipeline.ser
├── builtin_var
├── large_dim
├── motion
└── reorder
```

The four intermediate nodes are registered by [createShaderExecutionReorderTests](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2364). Each node iterates the `HitObjectTestType` enum range and adds one `RayTracingTestCase` per test type with the launch dimensions encoded in the leaf name.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `builtin_var`, `reorder`, `motion`, `large_dim` | Selects which SER / hit-object API surface the case exercises. Each node maps to a contiguous range of `HitObjectTestType` values. | [groups table](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2266-L2270) |
| Test type leaf | 62 total leaves: `empty`, `trace_ray`, `tmin`, `tmax`, `custom_index`, `instance_id`, `get_tri_vertices`, `primitive_index`, `geometry_index`, `geometry_index_multi`, `ray_flags`, `hit_kind`, `world_ray_origin`, `object_ray_origin`, `world_ray_direction`, `object_ray_direction`, `object_to_world`, `world_to_object`, `get_sbt_record_index`, `get_sbt_record_handle`, `get_attribute`, `array`, `array_nonuniform`, `multi_attrib_locations`, `get_attr_from_intersection`, `record_from_query_*`, `set_sbt_record_index`, `record_miss`, `hit_object_from_chit`, `hit_object_from_miss`, `query_from_chit`, `query_from_miss`, `query_hitkind_aabb`, `query_hitkind_tri`, `reorder_hint`, `reorder_hit_object`, `reorder_execute`, `reorder_execute_hint`, `reorder_hit_object_hint`, `reorder_trace_execute`, `reorder_trace_execute_hint`, `trace_with_and_without_reorder_*`, `reorder_subgroup`, `motion_trace_ray`, `motion_record_miss`, `motion_get_time`, `motion_reorder_execute`, `motion_reorder_execute_hint`, `large_dim_X_execute_hint`, `large_dim_Y_hobj_hint`, `large_dim_Z_hobj_hint` | One leaf per `HitObjectTestType`. The leaf name is `HitObjectTestNames[t] + sizeSuffix`. | [HitObjectTestNames](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L144-L207) |
| Launch dimensions | `160x91x1` (default), `256x64x1` (`reorder_subgroup` only), `15210x23x1` (`large_dim_X`), `44x15181x1` (`large_dim_Y`), `44x1x17233` (`large_dim_Z`) | Standard size for all non-large cases. Subgroup case uses even `256*64` to make subgroup reduction references clean. Large-dimension cases pick one axis at the device limit boundary. | [addTestsToGroup](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2292-L2353) |
| Geometry kind | triangles (default), AABB (procedural) | AABB cases (`get_attr_from_intersection`, `record_from_query_procedural_attribs*`, `record_from_query_sbt_index_aabb`, `multi_attrib_locations`, `query_hitkind_aabb`) build a single AABB BLAS and use the intersection shader. All other cases build two opaque triangles. | [initBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1713-L1775) |
| Per-test SBT / miss index | `sbtRecordOffset0`/`missIndex0` (default), `sbtRecordOffset1`/`missIndex1` (reorder_hint, hobj_hint, large_dim_*) | The hint-only and hit-object-plus-hint reorder cases (`reorder_hint`, `reorder_hit_object_hint`, and the `large_dim_*` cases that mirror them) route to `chit2` (writes `7.0`) and `miss2` (writes `11.0`) so the validation can distinguish hit from miss in the right-half region. The default cases (including `reorder_execute_hint` and `trace_with_and_without_reorder_*`) route to `chit1` (writes `3.0`) and `miss1` (writes `4.0`). | [rgen shared header](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L560-L573) |
| Image write coordinate | `(x, y)` (default), `(x, z)` (`large_dim_Z_hobj_hint`) | The Z-large case uses depth as the image height because the result image is 2D. | [LARGE_DIM_Z_HOBJ_HINT rgen](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1398-L1409) |
| TLAS transform | identity (default), +0.5 X shift (`object_ray_origin`, `object_to_world`, `world_to_object`) | The X shift moves the two triangles to the right half so hit/miss values swap in the validation. | [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1630-L1656) |

## Behavior Parameters

The primary behavioral axis is the intermediate node. Each node changes what is being tested about the SER and hit-object API surface.

### `builtin_var` — hitObjectEXT API built-in operations

Each case selects one `hitObjectEXT` operation or property getter and verifies that it returns the spec-required value for the current ray, geometry, instance, and SBT entry. The 43 leaves cover: empty-record and `IsEmpty` query; `hitObjectTraceRayEXT` plus `IsHit`/`IsMiss`/`IsEmpty` queries; `hitObjectRecordMissEXT`; `hitObjectRecordFromQueryEXT` (with proceed, with trace-execute, with SBT index, with attributes, with procedural attributes, with multi-attribute locations, with miss); `hitObjectSetShaderBindingTableRecordIndexEXT`; `hitObjectGetRayTMinEXT`/`TMaxEXT`; `hitObjectGetInstanceCustomIndexEXT`/`InstanceIdEXT`; `hitObjectGetPrimitiveIndexEXT`/`GeometryIndexEXT`; `hitObjectGetRayFlagsEXT`/`HitKindEXT`; `hitObjectGetWorldRayOriginEXT`/`DirectionEXT`/`ObjectRayOriginEXT`/`DirectionEXT`; `hitObjectGetObjectToWorldEXT`/`WorldToObjectEXT`; `hitObjectGetShaderBindingTableRecordIndexEXT`/`RecordBufferHandleEXT`; `hitObjectGetAttributesEXT`; `hitObjectGetIntersectionTriangleVertexPositionsEXT` (requires `VK_KHR_ray_tracing_position_fetch`); array and `nonuniformEXT` array forms; hit objects created from a closest-hit or miss shader; the 5-argument `hitObjectRecordFromQueryEXT` overload with explicit `hitKind` (requires SER specVersion >= 2). The host validates one float per launch invocation against a per-test expected `anyHitValue`/`missValue` pair.

### `reorder` — reorder entry points and their combined forms

The 11 leaves exercise every reorder entry point. `reorder_hint` uses `reorderThreadEXT(gl_SubgroupInvocationID % 2, 1)`. `reorder_hit_object` uses `reorderThreadEXT(hObj)` with the hit object as the hint. `reorder_hit_object_hint` uses the combined three-argument `reorderThreadEXT(hObj, hint, bits)` form. `reorder_execute` uses `hitObjectReorderExecuteEXT(hObj, 0)`, and `reorder_execute_hint` extends it with hint arguments via `hitObjectReorderExecuteEXT(hObj, hint, bits, sbt)`. `reorder_trace_execute` and `reorder_trace_execute_hint` use `hitObjectTraceReorderExecuteEXT`, which folds trace, reorder, and execute into one call. The `trace_with_and_without_reorder_*` cases call `hitObjectExecuteShaderEXT` twice (with and without an intervening reorder) and require both executions to produce the same payload. `reorder_subgroup` performs subgroup reductions (`subgroupAdd`, `Min`, `Max`, `All`, `Ballot`, `Shuffle`) before and after `reorderThreadEXT(sid % 2, 1)` and validates through the storage buffer instead of the result image. The reorder group is the only group that uses both validation paths.

### `motion` — motion-blur hit object variants

The 5 leaves exercise the motion variants of the trace, record-miss, get-time, and trace-reorder-execute operations with `time = 0.25`. `motion_trace_ray` calls `hitObjectTraceRayMotionEXT` and checks `IsHit`/`IsMiss`. `motion_record_miss` calls `hitObjectRecordMissMotionEXT` and requires the miss shader to run. `motion_get_time` calls `hitObjectGetCurrentTimeEXT` and expects the result image to equal the requested time. `motion_reorder_execute` and `motion_reorder_execute_hint` call `hitObjectTraceMotionReorderExecuteEXT` (with and without hint arguments). Motion geometry is shifted by +2 in X at t=1.0, so the validation swaps `anyHitValue` and `missValue` relative to the default cases.

### `large_dim` — reorder hint at extreme launch extents

The 3 leaves reuse the `reorder_hint` and `reorder_hit_object_hint` rgen bodies with one very large dispatch axis: `large_dim_X_execute_hint` (15210x23x1), `large_dim_Y_hobj_hint` (44x15181x1), and `large_dim_Z_hobj_hint` (44x1x17233). checkSupport throws `NotSupportedError` when `maxImageDimension2D` or `maxRayDispatchInvocationCount` is exceeded, so these cases also serve as limit gates. The Z-large case writes the result image at `(x, z)` and the host validation uses `depth` as the image height.

## Shader Analysis

The page uses one representative walkthrough. The `reorder.reorder_hint_160x91` case exercises the simplest hint-only form of `reorderThreadEXT` over a standard 160x91 launch. Other `reorder` leaves differ only in the reorder entry point or the combined trace-reorder-execute call; their rgen bodies share the same shared header, SBT selection, and validation pattern. The `builtin_var`, `motion`, and `large_dim` leaves differ in the operation under test but follow the same image-store-and-validate flow, so they do not need separate walkthroughs.

### Representative Shader Walkthrough 1

**CTS case:** `dEQP-VK.ray_tracing_pipeline.ser.reorder.reorder_hint_160x91`

**Source location:** [vktRayTracingShaderExecutionReorderTests.cpp#L1161-L1169](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1161-L1169) (per-case body inlined into the shared header at [L549-L573](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L549-L573)).

**What this shader tests:** The raygen shader traces a primary ray into SBT offset 1 / miss index 1, then calls `reorderThreadEXT(gl_SubgroupInvocationID % 2, 1)` to ask the implementation to reorder by odd/even subgroup invocation, then calls `hitObjectExecuteShaderEXT(hObj, 0)` to invoke the recorded hit or miss shader. The matching `chit2` writes `payload = vec4(7,0,0,1)`; `miss2` writes `payload = vec4(11,0,0,1)`. Geometry spans the left half of the launch grid. If reorder preserves the invariants, left-half rays must observe `7.0` (hit) and right-half rays must observe `11.0` (miss). If the implementation corrupts payload, SBT selection, or hit object state across the reorder point, the result image diverges from the expected pattern.

**Shader-visible resources:**

- `%result` (`image2D`, set 0, binding 0, `r32f`): 2D storage image, one texel per launch invocation. Written by `OpImageWrite` from `%payload`.
- `%topLevelAS` (`accelerationStructureEXT`, set 0, binding 1): traversal input for `OpHitObjectTraceRayEXT`.
- `%storageBuffer` (`StorageBuffer`, set 0, binding 2, runtime array of `uint`): declared by the shared header; unused by this case but bound by the host.
- `%payload` (`vec4`, `RayPayloadKHR`, location 0): written by the closest-hit or miss shader invoked through `%hObj`, then stored into the image.
- `%hObj` (`hitObjectEXT`, `Private`): records the trace result and drives `OpHitObjectExecuteShaderEXT`.
- `%gl_LaunchIDEXT` / `%gl_LaunchSizeEXT` (BuiltIn `LaunchIdKHR` / `LaunchSizeKHR`): used to compute `origin` and the image write coordinate.
- `%gl_SubgroupInvocationID` (BuiltIn `SubgroupLocalInvocationId`): provides the hint value `%79 = UMod %gl_SubgroupInvocationID %uint_2`.

**Reconstructed GLSL:**

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_shader_invocation_reorder : require
#extension GL_KHR_shader_subgroup_basic : require
/// 2D r32f storage image at binding 0; one texel per launch invocation.
layout(r32f, set = 0, binding = 0) uniform image2D result;
/// Top-level acceleration structure at binding 1.
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;
/// Storage buffer at binding 2 (unused in this case but always declared by the shared header).
layout(set = 0, binding = 2) buffer StorageBuffer { uint data[]; } storageBuffer;
/// Ray payload at location 0; closest-hit / miss shaders write into it.
layout(location = 0) rayPayloadEXT vec4 payload;

void main()
{
  uint  rayFlags         = gl_RayFlagsOpaqueEXT;
  uint  sbtRecordOffset0 = 0;
  uint  sbtRecordOffset1 = 1;
  uint  sbtRecordStride  = 1;
  uint  missIndex0       = 0;
  uint  missIndex1       = 1;
  uint  cullMask         = 0xFF;
  float tmin             = 0.5f;
  float tmax             = 9.0f;
  /// origin spans the launch grid; rays on the left half hit, rays on the right half miss.
  vec3  origin           = vec3((float(gl_LaunchIDEXT.x) + 0.5f) / float(gl_LaunchSizeEXT.x),
                                (float(gl_LaunchIDEXT.y) + 0.5f) / float(gl_LaunchSizeEXT.y), 0.0);
  vec3  direct           = vec3(0.0, 0.0, -1.0);

  hitObjectEXT hObj;
  payload = vec4(1,0,0,1);
  /// Trace into SBT offset 1 / miss index 1: chit2 writes 7.0, miss2 writes 11.0.
  hitObjectTraceRayEXT(hObj, topLevelAS, rayFlags, cullMask, sbtRecordOffset1, sbtRecordStride,
                       missIndex1, origin, tmin, direct, tmax, 0);
  /// SER hint: reorder by odd/even subgroup invocation; implementation may honor or ignore.
  reorderThreadEXT(gl_SubgroupInvocationID % 2, 1);
  /// Execute the recorded hit object; must invoke the same SBT entry as the trace above.
  hitObjectExecuteShaderEXT(hObj, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), payload);
}
```

**SPIR-V Bound:** 94. **SPIR-V Version:** 1.5. **Target environment:** `vulkan1.2` (CTS build options target `vk::SPIRV_VERSION_1_4`).

The disassembly was produced with glslang 16.2.0 and spirv-dis from the same release. The system `spirv-val` (VulkanSDK 1.4.321.1 and packman 1.3.231.1) does not recognize the `ShaderInvocationReorderEXT` capability (5388) from `SPV_EXT_shader_invocation_reorder`, so validation fails with `Invalid capability operand: 5388`. This is a tooling version gap, not a shader defect; the sister page `InvocationReorderActivity.md` records the same gap.

The SPIR-V instructions of interest are `OpHitObjectTraceRayEXT` (records the trace into `%hObj`), `OpReorderThreadWithHintEXT` (the hint-only reorder form, taking `%79 = UMod %gl_SubgroupInvocationID %uint_2` and `uint_1` as the bits argument), and `OpHitObjectExecuteShaderEXT` (invokes the SBT entry recorded in `%hObj`). The `reorder_hit_object` and `reorder_hit_object_hint` cases use `OpReorderThreadWithHitObjectEXT` instead; the `reorder_execute` and `reorder_trace_execute` cases use `OpHitObjectReorderExecuteEXT` and `OpHitObjectTraceReorderExecuteEXT` respectively.

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
; Bound: 94
; Schema: 0
               OpCapability GroupNonUniform
               OpCapability RayTracingKHR
               OpCapability ShaderInvocationReorderEXT
               OpExtension "SPV_EXT_shader_invocation_reorder"
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %payload %hObj %topLevelAS %gl_SubgroupInvocationID %result %storageBuffer
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpSourceExtension "GL_EXT_shader_invocation_reorder"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %rayFlags "rayFlags"
               OpName %sbtRecordOffset0 "sbtRecordOffset0"
               OpName %sbtRecordOffset1 "sbtRecordOffset1"
               OpName %sbtRecordStride "sbtRecordStride"
               OpName %missIndex0 "missIndex0"
               OpName %missIndex1 "missIndex1"
               OpName %cullMask "cullMask"
               OpName %tmin "tmin"
               OpName %tmax "tmax"
               OpName %origin "origin"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %direct "direct"
               OpName %payload "payload"
               OpName %hObj "hObj"
               OpName %topLevelAS "topLevelAS"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %result "result"
               OpName %StorageBuffer "StorageBuffer"
               OpMemberName %StorageBuffer 0 "data"
               OpName %storageBuffer "storageBuffer"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %gl_SubgroupInvocationID Volatile
               OpDecorate %gl_SubgroupInvocationID Coherent
               OpDecorate %77 RelaxedPrecision
               OpDecorate %79 RelaxedPrecision
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %StorageBuffer Block
               OpMemberDecorate %StorageBuffer 0 Offset 0
               OpDecorate %storageBuffer Binding 2
               OpDecorate %storageBuffer DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
   %uint_255 = OpConstant %uint 255
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
  %float_0_5 = OpConstant %float 0.5
    %float_9 = OpConstant %float 9
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
    %float_0 = OpConstant %float 0
   %float_n1 = OpConstant %float -1
         %52 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
    %v4float = OpTypeVector %float 4
%_ptr_RayPayloadKHR_v4float = OpTypePointer RayPayloadKHR %v4float
    %payload = OpVariable %_ptr_RayPayloadKHR_v4float RayPayloadKHR
    %float_1 = OpConstant %float 1
         %57 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
         %58 = OpTypeHitObjectEXT
%_ptr_Private_58 = OpTypePointer Private %58
       %hObj = OpVariable %_ptr_Private_58 Private
         %61 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_61 = OpTypePointer UniformConstant %61
 %topLevelAS = OpVariable %_ptr_UniformConstant_61 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
     %uint_2 = OpConstant %uint 2
         %80 = OpTypeImage %float 2D 0 0 0 2 R32f
%_ptr_UniformConstant_80 = OpTypePointer UniformConstant %80
     %result = OpVariable %_ptr_UniformConstant_80 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
%_runtimearr_uint = OpTypeRuntimeArray %uint
%StorageBuffer = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_StorageBuffer = OpTypePointer StorageBuffer %StorageBuffer
%storageBuffer = OpVariable %_ptr_StorageBuffer_StorageBuffer StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
   %rayFlags = OpVariable %_ptr_Function_uint Function
%sbtRecordOffset0 = OpVariable %_ptr_Function_uint Function
%sbtRecordOffset1 = OpVariable %_ptr_Function_uint Function
%sbtRecordStride = OpVariable %_ptr_Function_uint Function
 %missIndex0 = OpVariable %_ptr_Function_uint Function
 %missIndex1 = OpVariable %_ptr_Function_uint Function
   %cullMask = OpVariable %_ptr_Function_uint Function
       %tmin = OpVariable %_ptr_Function_float Function
       %tmax = OpVariable %_ptr_Function_float Function
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %rayFlags %uint_1
               OpStore %sbtRecordOffset0 %uint_0
               OpStore %sbtRecordOffset1 %uint_1
               OpStore %sbtRecordStride %uint_1
               OpStore %missIndex0 %uint_0
               OpStore %missIndex1 %uint_1
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0_5
               OpStore %tmax %float_9
         %31 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %32 = OpLoad %uint %31
         %33 = OpConvertUToF %float %32
         %34 = OpFAdd %float %33 %float_0_5
         %36 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %37 = OpLoad %uint %36
         %38 = OpConvertUToF %float %37
         %39 = OpFDiv %float %34 %38
         %40 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %41 = OpLoad %uint %40
         %42 = OpConvertUToF %float %41
         %43 = OpFAdd %float %42 %float_0_5
         %44 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %45 = OpLoad %uint %44
         %46 = OpConvertUToF %float %45
         %47 = OpFDiv %float %43 %46
         %49 = OpCompositeConstruct %v3float %39 %47 %float_0
               OpStore %origin %49
               OpStore %direct %52
               OpStore %payload %57
         %64 = OpLoad %61 %topLevelAS
         %65 = OpLoad %uint %rayFlags
         %66 = OpLoad %uint %cullMask
         %67 = OpLoad %uint %sbtRecordOffset1
         %68 = OpLoad %uint %sbtRecordStride
         %69 = OpLoad %uint %missIndex1
         %70 = OpLoad %v3float %origin
         %71 = OpLoad %float %tmin
         %72 = OpLoad %v3float %direct
         %73 = OpLoad %float %tmax
               OpHitObjectTraceRayEXT %hObj %64 %65 %66 %67 %68 %69 %70 %71 %72 %73 %payload
         %77 = OpLoad %uint %gl_SubgroupInvocationID
         %79 = OpUMod %uint %77 %uint_2
               OpReorderThreadWithHintEXT %79 %uint_1
               OpHitObjectExecuteShaderEXT %hObj %payload
         %83 = OpLoad %80 %result
         %85 = OpLoad %v3uint %gl_LaunchIDEXT
         %86 = OpVectorShuffle %v2uint %85 %85 0 1
         %88 = OpBitcast %v2int %86
         %89 = OpLoad %v4float %payload
               OpImageWrite %83 %88 %89
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- For non-AABB cases, the BLAS contains two opaque triangles spanning `x ∈ [0, 0.5]` at `z = -1.0`. For AABB cases, the BLAS contains one AABB `[(0,0,-2), (0.5,1,-1)]` and an intersection shader reports hits with `hitAttr = vec2(111.0, 222.0)`. For motion cases, the BLAS adds a second vertex set shifted by +2 in X at t=1.0 and the TLAS, BLAS, and pipeline carry motion create flags. The TLAS contains one instance with `kInstanceCustomIndex = 49`; the `object_ray_origin`, `object_to_world`, and `world_to_object` cases shift the instance transform by +0.5 in X.
- The host builds a `RayTracingPipeline` with one raygen, two closest-hit, two miss, and (for AABB cases) one intersection shader. The raygen SBT region carries shader-record data `{10, 20, 30, 40}` for the `get_sbt_record_handle` case. Motion cases add `VK_PIPELINE_CREATE_RAY_TRACING_ALLOW_MOTION_BIT_NV`.
- Descriptor set binding 0 is the r32f storage image; binding 1 is the TLAS; binding 2 is a 1024-byte uint storage buffer zeroed by the host. The storage buffer is only read back for `reorder_subgroup`.
- The host dispatches `cmdTraceRaysKHR` with `(width, height, depth)`. The rgen shader computes `origin` from `gl_LaunchIDEXT`, traces/reorders/executes per `testType`, and stores a float into the result image at `gl_LaunchIDEXT.xy` (or `(x, z)` for `large_dim_Z`).
- The host clears the image to `(5,5,5,255)` before the trace, transitions it to `GENERAL` before the trace, then issues a `SHADER_WRITE → TRANSFER_READ` memory barrier before `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE → HOST_READ` barrier before host invalidation.
- The host copies the image into a host-visible buffer, invalidates mapped memory, and scans every `(x, y)` against a per-test `anyHitValue` (left half) and `missValue` (right half) with `epsilon = 1e-6f`. Motion and transform-shifted cases swap the two halves because the +X shift or the +2 motion shift moves hits to the right half. `large_dim_Z` validates against `depth` as the image height.
- For `reorder_subgroup`, the host invalidates the 1024-byte storage buffer instead and checks that the before-reorder reductions at offsets `[0..5]` and the after-reorder reductions at offsets `[10..15]` both equal the no-reorder reference: `sum = n*(n-1)/2`, `min = 0`, `max = n-1`, `all = n`, `shuffleSum = n*(n-1)/2`, `ballot = n`, where `n = width*height = 16384`.
- The case passes if and only if every scanned entry matches within epsilon (image path) or every checked reduction matches (storage buffer path).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `builtin_var` | A `hitObjectEXT` built-in operation (record, trace, miss, query-record, execute, get-property, set-sbt-index, get-attributes, get-tri-vertices, get-sbt-handle) returned a value or invoked a shader that does not match the spec-required hit/miss/geometry state for the current ray. |
| `reorder` | A reorder entry point (`reorderThreadEXT`, `hitObjectReorderExecuteEXT`, `hitObjectTraceReorderExecuteEXT`) corrupted payload, SBT selection, hit object state, or subgroup semantics across the reorder point, or the trace-with-and-without-reorder invariants diverged. |
| `motion` | A motion-blur hit object variant (`hitObjectTraceRayMotionEXT`, `hitObjectRecordMissMotionEXT`, `hitObjectGetCurrentTimeEXT`, `hitObjectTraceMotionReorderExecuteEXT`) reported wrong hit/miss, wrong time, or invoked the wrong SBT entry for the requested `time`. |
| `large_dim` | The reorder-hint path at a large dispatch dimension exceeded or miscomputed against device limits, or hit a tiling/padding/coordinate bug in the reorder or image-write path at extreme launch extents. |

### Cause Analysis

#### `builtin_var` built-in operation returned wrong value or invoked wrong SBT entry

**Possible failure symptoms:** One or more result image entries differ from the per-test `anyHitValue` (left half) or `missValue` (right half). The mismatch pattern depends on which operation failed. Scalar getters (`tmin`, `tmax`, `custom_index`, `instance_id`, `primitive_index`, `geometry_index`, `hit_kind`, `ray_flags`) fail with a single wrong float at every hit or miss pixel. Matrix getters (`object_to_world`, `world_to_object`) fail when any matrix entry differs from the identity-plus-shift reference. The `record_from_query_*` and `query_hitkind_*` cases fail when the hit object recorded from a ray query does not match the spec-required intersection state. The `get_sbt_record_handle` case fails when the dereferenced SBT data does not equal `{10, 20, 30, 40}`.

**Possible implementation causes:** The shader compiler lowered a `hitObject*EXT` built-in to the wrong SPIR-V instruction or evaluated it at the wrong program point. The driver populated the hit object with the wrong hit, miss, geometry, instance, or SBT state for the current ray. The acceleration structure builder produced geometry or instance data that does not match the test's hard-coded expectations. For `record_from_query_*`, the ray query integration returned a stale or incomplete intersection. For `query_hitkind_*` with the 5-argument overload, the implementation did not honor the explicit `hitKind` argument (requires SER specVersion >= 2). For `get_tri_vertices`, the driver did not return the spec-required triangle vertex positions (requires `VK_KHR_ray_tracing_position_fetch`). Source-level investigation is needed to distinguish a compiler bug from a driver bug when multiple getters fail with the same offset pattern.

#### `reorder` corrupted payload, SBT selection, hit object state, or subgroup semantics

**Possible failure symptoms:** For the `reorder_hint`, `reorder_hit_object`, `reorder_hit_object_hint`, `reorder_execute`, `reorder_execute_hint`, `reorder_trace_execute`, and `reorder_trace_execute_hint` cases, the result image contains `3.0` where `7.0` was expected (or `4.0` where `11.0` was expected), indicating that the wrong SBT entry was invoked after the reorder. For the `trace_with_and_without_reorder_*` cases, the first and second executions of the same hit object produce different payloads, so the result image contains `4.0` (mismatch) instead of `3.0` (match). For `reorder_subgroup`, the before-reorder and after-reorder subgroup reductions at offsets `[0..5]` and `[10..15]` diverge from each other or from the no-reorder reference.

**Possible implementation causes:** The reorder unit lost or corrupted the hit object state when moving the invocation to a new subgroup, so `hitObjectExecuteShaderEXT` invoked the wrong SBT entry or read a stale payload. The reorder unit broke subgroup composition invariants, so post-reorder subgroup reductions (`subgroupAdd`, `Min`, `Max`, `All`, `Ballot`, `Shuffle`) returned values inconsistent with the participating invocations. The combined `hitObjectReorderExecuteEXT` or `hitObjectTraceReorderExecuteEXT` path skipped a step (trace, record, reorder, or execute) or executed them in the wrong order. The trace-with-and-without-reorder divergence implicates the reorder point itself, since both executions use the same recorded hit object. Source-level investigation is needed to confirm whether the failure is in the reorder unit, the SBT lookup, or the hit object lifetime tracking.

#### `motion` reported wrong hit, miss, time, or SBT entry

**Possible failure symptoms:** For `motion_trace_ray`, `motion_reorder_execute`, and `motion_reorder_execute_hint`, the result image swaps the expected `anyHitValue`/`missValue` pattern: hits appear on the wrong half because the implementation did not interpolate geometry to the requested `time = 0.25`. For `motion_record_miss`, the miss shader does not run and the payload stays at its initial value. For `motion_get_time`, the result image does not equal `0.25`, indicating `hitObjectGetCurrentTimeEXT` returned the wrong time or the hit object did not store the requested time.

**Possible implementation causes:** The motion BLAS build did not incorporate the t=1.0 shifted vertex set, so the trace saw only the rest-pose geometry. The driver did not pass the `time` argument through `hitObjectTraceRayMotionEXT` or `hitObjectTraceMotionReorderExecuteEXT` to the traversal unit. The TLAS or pipeline was created without the motion create flags, so the implementation treated the trace as a non-motion trace. The reorder-execute motion variant failed for the same reasons as the non-motion `reorder_execute` cause, plus a motion-specific time-state corruption. Source-level investigation is needed to separate motion-traversal bugs from motion-hit-object-state bugs.

#### `large_dim` exceeded device limits or hit a coordinate bug at extreme launch extents

**Possible failure symptoms:** The case is skipped with `NotSupportedError` when `maxImageDimension2D` or `maxRayDispatchInvocationCount` is exceeded, which is the intended limit-gate behavior. When the case runs, the result image contains wrong values at the edges of the large axis (first or last few rows/columns) or a uniform wrong value across the whole image. For `large_dim_Z_hobj_hint`, the wrong values appear at the wrong `(x, z)` mapping, indicating the host validation used the wrong height.

**Possible implementation causes:** The reorder unit tiled the large dispatch into chunks and lost the per-tile reorder hint, so threads near tile boundaries observed a different SBT entry than expected. The image-write path overflowed an internal coordinate at the large axis, so writes near the edge wrapped to the wrong texel. The host computed the readback buffer size or copy region with the wrong dimension for the Z-large case. Source-level investigation is needed to confirm whether the failure is in the reorder tiling, the image coordinate handling, or the host copy region setup.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, and `VK_EXT_ray_tracing_invocation_reorder`, plus the corresponding feature bits `rayTracingPipeline`, `accelerationStructure`, and `rayTracingInvocationReorder`. checkSupport throws `NotSupportedError` or `TestError` when any is missing.
- The five motion cases also require `VK_NV_ray_tracing_motion_blur` and `VkPhysicalDeviceRayTracingMotionBlurFeaturesNV::rayTracingMotionBlur`.
- `get_tri_vertices` requires `VK_KHR_ray_tracing_position_fetch` and `VkPhysicalDeviceRayTracingPositionFetchFeaturesKHR::rayTracingPositionFetch`.
- `query_hitkind_aabb` and `query_hitkind_tri` require `VK_EXT_ray_tracing_invocation_reorder` specVersion >= 2 for the 5-argument `hitObjectRecordFromQueryEXT` overload. Older implementations skip these cases.
- The three `large_dim` cases validate against `VkPhysicalDeviceLimits::maxImageDimension2D` and `VkPhysicalDeviceRayTracingPipelinePropertiesKHR::maxRayDispatchInvocationCount` and throw `NotSupportedError` when either limit is exceeded. The maximum single-axis dimension (15210, 15181, or 17233) and the total invocation count must both fit.

### Design-based pruning

- The `reorder_subgroup` case uses `256x64` instead of the default `160x91` so that the subgroup reduction references (`sum`, `min`, `max`, `all`, `shuffleSum`, `ballot` over `n = 16384` invocations) are clean and the storage buffer layout stays simple.
- The `large_dim` group exercises only one large axis per case rather than all three at once, so a failure can be attributed to a specific axis.
- The `trace_with_and_without_reorder_*` cases reset the payload to `vec4(0,0,0,0)` between the two executions, so a divergent second result isolates the reorder point from the trace itself.
- The 5-argument `hitObjectRecordFromQueryEXT` overload is only used by `query_hitkind_aabb` and `query_hitkind_tri`; other `record_from_query_*` cases use the 4-argument form, avoiding redundant specVersion-2 gating.
- The `record_from_query_*` and `query_*` cases use `GL_EXT_ray_query` only when the test type needs a ray query; the extension is not enabled for the pure hit-object cases.

## Key Takeaways

- The `ser` family verifies SER and `hitObjectEXT` invariants across four intermediate nodes. The reorder hint is an optimization hint, so every test is invariant-based: a correct implementation produces the same observable result with or without reordering.
- The `reorder` group is the only group that uses both validation paths. The image path covers payload and SBT-selection invariants; the storage buffer path covers subgroup-reduction invariants for `reorder_subgroup`.
- The `trace_with_and_without_reorder_*` cases are the most direct reorder-point test: they execute the same hit object twice with an intervening reorder and require identical payloads.
- The `motion` group reuses the same image-store-and-validate flow with motion-specific extensions, motion create flags on the TLAS / BLAS / pipeline, and a t=1.0 shifted geometry that swaps the hit/miss halves.
- The `large_dim` group doubles as a limit gate: checkSupport throws `NotSupportedError` when `maxImageDimension2D` or `maxRayDispatchInvocationCount` is exceeded, and the running cases stress reorder tiling and image-write coordinate handling at extreme launch extents.
- See `## Failure Meaning` for the four-way mapping from intermediate-node failure to implementation cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `HitObjectTestType` enum and `HitObjectTestNames` table | [vktRayTracingShaderExecutionReorderTests.cpp#L61-L207](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L61-L207) | Defines the 63 test cases and their string names. |
| `TestParams` and `RayTracingSERTestInstance` constructor | [vktRayTracingShaderExecutionReorderTests.cpp#L209-L312](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L209-L312) | Sets `m_isMotion` and `m_isAABB` per test type. |
| `RayTracingTestCase::checkSupport` | [vktRayTracingShaderExecutionReorderTests.cpp#L342-L438](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L342-L438) | Extension, feature, specVersion, and device-limit gates. |
| `RayTracingTestCase::initPrograms` rgen shared header | [vktRayTracingShaderExecutionReorderTests.cpp#L440-L573](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L440-L573) | Per-case extension enables and the shared `origin`/`direct`/`tmin`/`tmax`/flags block. |
| `REORDER_HINT` rgen body | [vktRayTracingShaderExecutionReorderTests.cpp#L1161-L1169](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1161-L1169) | The representative walkthrough case body. |
| Other `REORDER_*` rgen bodies | [vktRayTracingShaderExecutionReorderTests.cpp#L1171-L1326](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1171-L1326) | `reorder_hit_object`, `reorder_execute*`, `reorder_trace_execute*`, `trace_with_and_without_reorder_*`, `reorder_subgroup`. |
| `MOTION_*` rgen bodies | [vktRayTracingShaderExecutionReorderTests.cpp#L1328-L1376](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1328-L1376) | Motion variants of trace, record-miss, get-time, trace-reorder-execute. |
| `LARGE_DIM_*` rgen bodies | [vktRayTracingShaderExecutionReorderTests.cpp#L1378-L1409](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1378-L1409) | Large-dimension variants; the Z case writes at `(x, z)`. |
| Closest-hit / miss / intersection shaders | [vktRayTracingShaderExecutionReorderTests.cpp#L1418-L1622](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1418-L1622) | `chit1` (3.0), `chit2` (7.0), `miss1` (4.0), `miss2` (11.0), and the AABB intersection shader. |
| `initBottomAccelerationStructure` | [vktRayTracingShaderExecutionReorderTests.cpp#L1713-L1775](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1713-L1775) | BLAS geometry: triangles, AABB, multi-geometry, and motion. |
| `initTopAccelerationStructure` | [vktRayTracingShaderExecutionReorderTests.cpp#L1630-L1656](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1630-L1656) | TLAS instance, custom index, and +0.5 X shift for transform cases. |
| `initMotionBuffer` | [vktRayTracingShaderExecutionReorderTests.cpp#L1677-L1711](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1677-L1711) | Builds the t=1.0 shifted motion vertex buffer. |
| `RayTracingSERTestInstance::runTest` | [vktRayTracingShaderExecutionReorderTests.cpp#L1794-L2015](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L1794-L2015) | Pipeline, SBT, descriptor, image, and dispatch setup. |
| `RayTracingSERTestInstance::validateBuffer` | [vktRayTracingShaderExecutionReorderTests.cpp#L2024-L2242](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2024-L2242) | Per-test `anyHitValue`/`missValue` table and the image-vs-storage-buffer validation split. |
| `createShaderExecutionReorderTests` registration | [vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2364](../../../modules/vulkan/ray_tracing/vktRayTracingShaderExecutionReorderTests.cpp#L2253-L2364) | Builds `ser.{builtin_var, reorder, motion, large_dim}` and the per-leaf names. |
| Category dispatcher | [vktRayTracingTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp) | Routes `ser` to `createShaderExecutionReorderTests`. |
| Sister page `InvocationReorderActivity.md` | [InvocationReorderActivity.md](InvocationReorderActivity.md) | Companion test family `rtir_activity` that detects whether `reorderThreadEXT` perturbs subgroup composition. Uses the same glslang 16.2.0 + spirv-dis toolchain and records the same `spirv-val` capability-5388 gap. |
