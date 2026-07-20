## Overview

**Core question:** When a ray tracing pipeline binds `VK_NULL_HANDLE` as the top-level acceleration structure descriptor, does every traced ray always miss (invoking the miss shader), and does descriptor state survive switching the bound pipeline bind point between ray tracing and compute?

- [vktRayTracingNullASTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp) implements the single test family `null_as` under the `ray_tracing_pipeline` test category.
- The family has two test case leaves with distinct mechanisms. `test` binds a null TLAS descriptor and verifies the always-miss rule by checking every pixel equals the miss-shader value `4`. `mixed_dispatches` alternates `cmdTraceRaysKHR` and `cmdDispatch` calls against the same storage buffer and verifies each pipeline bind point keeps its own descriptor set state.
- The `test` leaf requires `nullDescriptor` from `VK_KHR_robustness2` and uses a custom device that disables the other robustness2 access features so only null descriptors are exercised.
- The page explains the always-miss rule, the mixed-dispatch descriptor-state check, the representative rgen shader, and what a failure of each leaf points to.

## Background Knowledge

- **Null descriptors.** `VK_EXT_robustness2` (promoted to `VK_KHR_robustness2`) defines `nullDescriptor`, which lets an application bind `VK_NULL_HANDLE` for descriptor types including `VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR`. The Vulkan spec states that reads of a null acceleration structure descriptor behave as if the acceleration structure is empty, so any `traceRayEXT` against it always misses.
- **Pipeline bind points.** `VK_PIPELINE_BIND_POINT_RAY_TRACING_KHR` and `VK_PIPELINE_BIND_POINT_COMPUTE` each carry their own bound descriptor sets in a command buffer. Binding a pipeline and descriptor sets for one bind point must not corrupt the descriptor state bound for the other bind point.
- **Shader binding table regions.** `cmdTraceRaysKHR` takes four `VkStridedDeviceAddressRegionKHR` regions: raygen, miss, hit, and callable. A region with base address `0`, stride `0`, and size `0` is a valid empty SBT region. The `mixed_dispatches` leaf uses empty miss, hit, and callable regions because its rgen shader never calls `traceRayEXT`.

## Registration Hierarchy

```text
ray_tracing_pipeline.null_as
├── mixed_dispatches
└── test
```

The two direct children are registered by [createNullAccelerationStructureTests](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L756-L769). `test` is a `RayTracingTestCase` with an 8x8 dispatch; `mixed_dispatches` is a `RayTracingDescriptorTestCase` with no `CaseDef` parameters.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `test`, `mixed_dispatches` | Selects the tested property: null-AS always-miss, or descriptor-state preservation across pipeline bind point switches. This is the primary behavioral axis. | [createNullAccelerationStructureTests](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L756-L769) |
| Dispatch size (`test`) | `width=8`, `height=8` | Fixed 8x8 launch dimensions for the always-miss trace. | [CaseDef](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L761-L764) |
| Dispatch size (`mixed_dispatches`) | `singleDispatchCount=16` | Fixed 16-element half-buffer written by each of the four dispatches. Used as a specialization constant in both rgen and compute shaders. | [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L715-L716) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L315) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf tests a different property, so each gets its own subsection.

### test — null acceleration structure descriptor always-miss

Binds `VK_NULL_HANDLE` as the `VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR` descriptor at binding 1, then traces one ray per pixel from the rgen shader. The spec requires a null AS to behave as an empty AS, so every ray must miss and invoke the miss shader. The miss shader writes `4` to the result image; the intersection, any-hit, and closest-hit shaders write `1`, `2`, and `3` respectively and must never run. The host validates that every pixel equals `4`. This leaf requires the `nullDescriptor` feature from `VK_KHR_robustness2`.

### mixed_dispatches — descriptor state preservation across pipeline bind point switches

Binds a ray tracing pipeline and a compute pipeline, each with its own descriptor set pointing at a different half of one storage buffer, then records four alternating dispatches: `cmdTraceRaysKHR(1,16,1)`, `cmdDispatch(1,16,1)`, `cmdTraceRaysKHR(2,16,1)`, `cmdDispatch(2,16,1)`. The rgen and compute shaders use `gl_LaunchSizeEXT.x` and `gl_NumWorkGroups.x` to identify the second dispatch and write to a different buffer section with a different base value. The host checks four buffer sections against distinct expected values. This leaf does not bind an acceleration structure and uses empty SBT regions for miss, hit, and callable. It verifies that binding a pipeline and descriptor sets for one bind point does not corrupt the descriptor state bound for the other.

## Shader Analysis

The `test` leaf's rgen shader is the representative walkthrough because it is the one that traces a ray against the null AS descriptor. The `mixed_dispatches` rgen shader never calls `traceRayEXT` and is covered by the parameter summary above; its shader text is a straight storage-buffer write keyed on `gl_LaunchSizeEXT.x`.

### Representative Shader Walkthrough 1: `null_as.test` rgen

**CTS case:** `dEQP-VK.ray_tracing_pipeline.null_as.test`

**Source:** reconstructed from [RayTracingTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L317-L318), which adds `glu::RaygenSource(updateRayTracingGLSL(getCommonRayGenerationShader()))`. The shared helper is [getCommonRayGenerationShader](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138), specialized for `set = 0, binding = 1`.

**Stage:** Ray generation (`VK_SHADER_STAGE_RAYGEN_BIT_KHR`).

**Resources:**

- `topLevelAS` (binding 1): `accelerationStructureEXT`. At runtime the descriptor write binds `VK_NULL_HANDLE` here via `VkWriteDescriptorSetAccelerationStructureKHR` with `pAccelerationStructures = &topLevelAccelerationStructure` where `topLevelAccelerationStructure = VK_NULL_HANDLE`. The spec requires this to behave as an empty AS, so `traceRayEXT` always misses.
- `hitValue` (location 0): `rayPayloadEXT vec3`. Declared but unused by the rgen; the miss shader declares the matching `rayPayloadInEXT` and also ignores it.
- `result` image (binding 0): written by the miss, intersection, any-hit, and closest-hit shaders, not by rgen.

**Shader logic:**

The rgen shader computes one ray origin per launch ID at `((x+0.5)/width, (y+0.5)/height, 0.0)` and traces straight down `-z` with `tmin=0.0`, `tmax=9.0`, `rayFlags=0`, `cullMask=0xFF`. Because the TLAS descriptor is null, traversal finds no geometry and the miss shader runs. The miss shader writes `uvec4(4,0,0,1)` to the result image at `gl_LaunchIDEXT.xy`.

#### Reconstructed GLSL

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT vec3 hitValue;
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  uint  rayFlags = 0;
  uint  cullMask = 0xFF;
  float tmin     = 0.0;
  float tmax     = 9.0;
  vec3  origin   = vec3((float(gl_LaunchIDEXT.x) + 0.5f) / float(gl_LaunchSizeEXT.x), (float(gl_LaunchIDEXT.y) + 0.5f) / float(gl_LaunchSizeEXT.y), 0.0);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  traceRayEXT(topLevelAS, rayFlags, cullMask, 0, 0, 0, origin, tmin, direct, tmax, 0);
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
; Bound: 62
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
               OpName %origin "origin"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
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
    %float_0 = OpConstant %float 0
    %float_9 = OpConstant %float 9
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
  %float_0_5 = OpConstant %float 0.5
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
   %float_n1 = OpConstant %float -1
         %47 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
         %48 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_48 = OpTypePointer UniformConstant %48
 %topLevelAS = OpVariable %_ptr_UniformConstant_48 UniformConstant
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
     %origin = OpVariable %_ptr_Function_v3float Function
     %direct = OpVariable %_ptr_Function_v3float Function
               OpStore %rayFlags %uint_0
               OpStore %cullMask %uint_255
               OpStore %tmin %float_0
               OpStore %tmax %float_9
         %25 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %26 = OpLoad %uint %25
         %27 = OpConvertUToF %float %26
         %29 = OpFAdd %float %27 %float_0_5
         %31 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %32 = OpLoad %uint %31
         %33 = OpConvertUToF %float %32
         %34 = OpFDiv %float %29 %33
         %36 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %37 = OpLoad %uint %36
         %38 = OpConvertUToF %float %37
         %39 = OpFAdd %float %38 %float_0_5
         %40 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_1
         %41 = OpLoad %uint %40
         %42 = OpConvertUToF %float %41
         %43 = OpFDiv %float %39 %42
         %44 = OpCompositeConstruct %v3float %34 %43 %float_0
               OpStore %origin %44
               OpStore %direct %47
         %51 = OpLoad %48 %topLevelAS
         %52 = OpLoad %uint %rayFlags
         %53 = OpLoad %uint %cullMask
         %54 = OpLoad %v3float %origin
         %55 = OpLoad %float %tmin
         %56 = OpLoad %v3float %direct
         %57 = OpLoad %float %tmax
               OpTraceRayKHR %51 %52 %53 %uint_0 %uint_0 %uint_0 %54 %55 %56 %57 %hitValue
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

### `test` leaf

- A custom device is created with `VK_KHR_ray_tracing_pipeline`, `VK_KHR_acceleration_structure`, `VK_KHR_buffer_device_address`, `VK_KHR_deferred_host_operations`, `VK_EXT_descriptor_indexing`, `VK_KHR_spirv_1_4`, `VK_KHR_shader_float_controls`, and `VK_KHR_robustness2` (or `VK_EXT_robustness2`). The custom device explicitly disables `robustBufferAccess`, `robustBufferAccess2`, and `robustImageAccess2` so only `nullDescriptor` is exercised [DeviceHelper](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L169-L231).
- The descriptor set layout has two bindings: binding 0 is a storage image (`r32ui` 2D image, 8x8), binding 1 is `VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR`. The descriptor write for binding 1 sets `pAccelerationStructures` to a pointer to `VK_NULL_HANDLE` [descriptor update](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L488-L500).
- The result image is cleared to `(5,5,5,255)` and transitioned to `GENERAL` before the trace. `cmdTraceRays` dispatches `8 x 8 x 1` rays. A `SHADER_WRITE` to `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` to `HOST_READ` barrier move the image into a host-visible buffer [runTest](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L466-L523).
- The host scans every pixel and counts failures against the expected value `4` [validateBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L528-L545). Pass condition: `failures == 0`.

### `mixed_dispatches` leaf

- One storage buffer of `4 * 16 * sizeof(uint32_t)` bytes is split into two halves. Two descriptor sets with the same layout (single `STORAGE_BUFFER` binding) are created: descriptor set 0 (ray tracing) points at the first half, descriptor set 1 (compute) points at the second half [descriptor setup](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L623-L643).
- Both pipelines are bound, then both descriptor sets are bound to their respective pipeline bind points. Four alternating dispatches follow: `cmdTraceRaysKHR(1,16,1)`, `cmdDispatch(1,16,1)`, `cmdTraceRaysKHR(2,16,1)`, `cmdDispatch(2,16,1)` [dispatch sequence](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L650-L665).
- The rgen shader writes `data.v[i] = i + 57 + secondTraceRays * 500` where `secondTraceRays = uint(gl_LaunchSizeEXT.x > 1)` and `i = secondTraceRays * 16 + gl_LaunchIDEXT.y`. The compute shader writes `data.v[i] = i + secondDispatch * 100` where `secondDispatch = uint(gl_NumWorkGroups.x > 1)` [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L713-L746).
- The host checks four 16-element sections in order: `i+57`, `i+573`, `i`, `i+116` for `i` in `0..15`. A single mismatched value fails the test immediately [result check](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L674-L686).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `test` | The implementation did not treat a null acceleration structure descriptor as always-miss, so a hit shader ran or the result image was not written by the miss shader. |
| `mixed_dispatches` | The implementation corrupted or lost descriptor set state when switching the bound pipeline bind point between ray tracing and compute, so a dispatch wrote to the wrong buffer section or with the wrong base value. |

### Cause Analysis

#### Null descriptor always-miss failure

**Possible failure symptoms:** One or more pixels in the 8x8 result image are not `4`. A pixel equal to `1` means the intersection shader ran, `2` means the any-hit shader ran, `3` means the closest-hit shader ran, and `5` means no shader wrote to that pixel at all. The failure count from `validateBuffer` is nonzero.

**Possible implementation causes:** The spec requires a null acceleration structure descriptor to behave as an empty acceleration structure, which means `traceRayEXT` must always invoke the miss shader. A failure points at the driver's handling of `VK_NULL_HANDLE` in an acceleration structure descriptor write. Source-level investigation should confirm the descriptor write actually bound `VK_NULL_HANDLE` (it does, via `VkWriteDescriptorSetAccelerationStructureKHR` with `pAccelerationStructures = &topLevelAccelerationStructure` where `topLevelAccelerationStructure = VK_NULL_HANDLE`) and that the miss shader binding table region was valid and reachable. If the miss shader never runs, the implementation did not lower the null descriptor to an empty traversal.

#### Descriptor state corruption across bind point switches

**Possible failure symptoms:** One of the four buffer sections has a wrong value. The first traceRays section (indices 0..15) reads a value other than `i+57`, the second traceRays section (indices 16..31) reads other than `i+573`, the first compute section (indices 32..47) reads other than `i`, or the second compute section (indices 48..63) reads other than `i+116`. The test fails on the first mismatched value with a message naming the section.

**Possible implementation causes:** The test binds both pipelines and both descriptor sets before any dispatch, then interleaves ray tracing and compute dispatches without rebinding. If the implementation clears or overwrites the descriptor set bound to one pipeline bind point when binding a pipeline or descriptor sets for the other bind point, a later dispatch reads stale or wrong descriptor state and writes to the wrong buffer region or with the wrong base value. The two descriptor sets point at different halves of one buffer, so a bind-point leak would show up as one pipeline writing into the other's section. Source-level investigation should confirm both `cmdBindDescriptorSets` calls used the correct `pipelineBindPoint` argument (`VK_PIPELINE_BIND_POINT_RAY_TRACING_KHR` and `VK_PIPELINE_BIND_POINT_COMPUTE`) and that the shader specialization produced the expected base values.

## Case Pruning

### Requirement-based pruning

- The `test` leaf requires `VK_KHR_ray_tracing_pipeline`, `VK_KHR_acceleration_structure`, `VK_KHR_deferred_host_operations`, `VK_KHR_buffer_device_address`, and `VK_KHR_robustness2` (or `VK_EXT_robustness2`). The `rayTracingPipeline` feature bit and the `nullDescriptor` feature bit must both be set, otherwise the test throws `NotSupportedError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L278-L311).
- The `mixed_dispatches` leaf requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L707-L711).

### Design-based pruning

- The family has no generated matrix. Both leaves are single fixed cases, so there is no design-based pruning to document.

## Key Takeaways

- The `null_as` family has two leaves that test distinct properties: `test` verifies the null acceleration structure descriptor always-miss rule, and `mixed_dispatches` verifies descriptor set state survives pipeline bind point switches.
- The `test` leaf is the one that exercises the null AS descriptor. Its rgen shader traces one ray per pixel against a `VK_NULL_HANDLE` TLAS; the spec requires every ray to miss, so the miss shader must write `4` to every pixel. Any other value is a failure.
- The `mixed_dispatches` leaf does not bind an acceleration structure. Its rgen shader writes directly to a storage buffer and never calls `traceRayEXT`. The test confirms that binding a compute pipeline and its descriptor set does not corrupt the ray tracing bind point's descriptor state, and vice versa.
- The `test` leaf uses a custom device that disables `robustBufferAccess`, `robustBufferAccess2`, and `robustImageAccess2` so only the `nullDescriptor` feature is exercised, isolating the null-AS behavior from other robustness2 access guarantees.
- See `## Failure Meaning` for the per-leaf cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseDef` struct | [vktRayTracingNullASTests.cpp#L56-L60](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L56-L60) | Per-case width and height for the `test` leaf |
| `DeviceHelper` constructor | [vktRayTracingNullASTests.cpp#L169-L231](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L169-L231) | Custom device with robustness2 enabled and other robustness2 access features disabled |
| `RayTracingTestCase::checkSupport` | [vktRayTracingNullASTests.cpp#L278-L311](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L278-L311) | Feature gates for the `test` leaf, including `nullDescriptor` |
| `RayTracingTestCase::initPrograms` | [vktRayTracingNullASTests.cpp#L313-L388](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L313-L388) | rgen, ahit, chit, miss, and sect shaders for the `test` leaf |
| `runTest` (null AS trace) | [vktRayTracingNullASTests.cpp#L395-L526](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L395-L526) | Null AS descriptor write, image clear, trace dispatch, and copyback |
| `validateBuffer` | [vktRayTracingNullASTests.cpp#L528-L545](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L528-L545) | Per-pixel expected-value `4` check for the `test` leaf |
| `RayTracingDescriptorTestInstance::iterate` | [vktRayTracingNullASTests.cpp#L572-L689](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L572-L689) | `mixed_dispatches` execution: dual pipelines, dual descriptor sets, four alternating dispatches, four-section result check |
| `RayTracingDescriptorTestCase::initPrograms` | [vktRayTracingNullASTests.cpp#L713-L747](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L713-L747) | rgen and compute shaders for `mixed_dispatches`, specialized with `singleDispatchCount=16` |
| `createNullAccelerationStructureTests` | [vktRayTracingNullASTests.cpp#L756-L769](../../../modules/vulkan/ray_tracing/vktRayTracingNullASTests.cpp#L756-L769) | Registration of the `null_as` group and its two children |
| shared rgen shader helper | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | `getCommonRayGenerationShader` used by the `test` leaf's rgen |
