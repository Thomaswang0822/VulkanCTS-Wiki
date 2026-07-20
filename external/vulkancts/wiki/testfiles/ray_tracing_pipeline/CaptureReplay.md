## Overview

**Core question:** Does the implementation reproduce identical ray tracing results when shader binding table buffers and acceleration structures are recreated at opaque device addresses captured during a prior run?

- [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp) implements the `capture_replay` test family under the `ray_tracing_pipeline` test category.
- The file registers two direct children: `shader_binding_tables` and `acceleration_structures`. The two children exercise different captured object types, so the page treats the direct child as the primary behavioral axis.
- The `shader_binding_tables` child captures and replays the opaque buffer addresses of the raygen, miss, and hit SBT regions, and varies the ordering between captured and non-captured pipelines (`pipeline_single`, `pipeline_after_captured`, `pipeline_before_captured`).
- The `acceleration_structures` child captures and replays the AS device address plus the backing buffer and backing memory opaque capture addresses, and varies the AS operation (`building`, `copy`, `compaction`, `serialization`), the build path (`cpu_built`, `gpu_built`), the operation target (`top_acceleration_structure`, `bottom_acceleration_structure`), and the bottom geometry type (`triangles`, `aabbs`).
- The test runs a capture phase and a replay phase, traces rays into a 3D result image, and compares every replay layer against the capture layer pixel-for-pixel with no tolerance.
- The reader should expect the page to explain what is captured and replayed in each child, how the rgen shader separates capture from replay output through a uniform-selected image layer, and which failure each child points to.

## Background Knowledge

- **Opaque capture/replay addresses.** `vkGetBufferOpaqueCaptureAddress`, `vkGetDeviceMemoryOpaqueCaptureAddress`, and `vkGetAccelerationStructureDeviceAddressKHR` return opaque addresses that the application can save and later feed back through `pNext` chains so buffers, device memory, and acceleration structures are recreated at the same addresses.
- **Capture-replay create flags.** `VK_BUFFER_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT`, `VK_MEMORY_ALLOCATE_DEVICE_ADDRESS_BIT` with `VkMemoryOpaqueCaptureAddressAllocateInfo`, and `VK_ACCELERATION_STRUCTURE_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT_KHR` mark objects whose addresses will be captured and replayed.
- **Feature gates.** `bufferDeviceAddressCaptureReplay` gates every case; `rayTracingPipelineShaderGroupHandleCaptureReplay` gates the SBT child; `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` gates only `pipeline_before_captured`; `accelerationStructureCaptureReplay` gates the AS child; `accelerationStructureHostCommands` also gates the `cpu_built` AS path.
- **SBT capture/replay ordering.** The spec allows implementations to forbid mixing captured and non-captured shader-group handles unless `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` is supported. The three SBT orderings exercise a single captured pipeline, a captured pipeline followed by a non-captured one, and the reverse.
- **Capture versus replay layers.** The rgen shader writes its result into a 3D image at a layer selected by a uniform buffer. The host writes `targetLayer = 0` during capture, and `targetLayer = 0` or `1` per pipeline during replay, so multiple pipelines can write into distinct layers of the same image for a single comparison pass.

## Registration Hierarchy

```text
ray_tracing_pipeline.capture_replay
├── acceleration_structures
└── shader_binding_tables
```

## Parameter Dimensions and Observed Values

The SBT child is a flat three-leaf family. The AS child is a four-axis matrix produced by nested registration loops [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1614-L1727).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct child (primary axis) | `shader_binding_tables`, `acceleration_structures` | Selects which object type has its opaque address captured and replayed: SBT buffers or acceleration structures. | [root registration](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1729-L1739) |
| SBT test type | `pipeline_single`, `pipeline_after_captured`, `pipeline_before_captured` | Selects the ordering of captured versus non-captured pipelines. `pipeline_before_captured` is the only one requiring `rayTracingPipelineShaderGroupHandleCaptureReplayMixed`. | [SBT loop](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1614-L1643) |
| AS operation type | `building`, `copy`, `compaction`, `serialization` | Selects whether the AS is rebuilt from scratch, copied, compacted, or serialized then deserialized between capture and replay. | [operation types](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1651-L1656) |
| AS build type | `cpu_built`, `gpu_built` | Selects `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` or `_DEVICE_KHR`. `cpu_built` also requires `accelerationStructureHostCommands`. | [build types](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1658-L1665) |
| AS operation target | `top_acceleration_structure`, `bottom_acceleration_structure` | Selects which AS level is copied, compacted, or serialized. The other level is built normally. | [operation targets](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1667-L1674) |
| AS bottom geometry | `triangles`, `aabbs` | Selects `BTT_TRIANGLES` (fixed-function hit) or `BTT_AABBS` (intersection shader hit) for the bottom-level AS. | [bottom test types](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1676-L1683) |
| Image and dispatch size | `8x8` (`RTCR_DEFAULT_SIZE`) | Fixed launch dimensions; each launch writes one ray per pixel into the active image layer. | [RTCR_DEFAULT_SIZE](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L57-L58) |

## Behavior Parameters

The primary behavioral axis is the direct child of `ray_tracing_pipeline.capture_replay`. Each value captures and replays a different object type and therefore points to a different failure surface. The remaining dimensions configure how hard each child's mechanism is stressed.

### shader_binding_tables — SBT buffer opaque capture/replay addresses

`shader_binding_tables` verifies that the raygen, miss, and hit SBT regions can be recreated at the exact buffer opaque capture addresses saved during the capture phase, and that the recreated SBT resolves to the same shader-group handles. During capture, the host creates the three SBT buffers with `VK_BUFFER_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT` and `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`, then records `sbtSavedRaygenAddress`, `sbtSavedMissAddress`, and `sbtSavedHitAddress` via `vkGetBufferOpaqueCaptureAddress` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L390-L433). During replay, the host recreates the SBT buffers at those saved addresses with no capture-replay flag, passing the address through `createShaderBindingTable` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L434-L577).

The `testType` sub-axis selects the pipeline ordering. `pipeline_single` recreates one captured pipeline and compares one replay layer. `pipeline_after_captured` recreates the captured pipeline first, then creates a second non-captured pipeline, and compares two replay layers. `pipeline_before_captured` reverses the order: a non-captured pipeline is created first, then the captured one, and requires `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` because the two pipelines coexist with mixed handle types.

### acceleration_structures — AS device and backing memory opaque capture/replay addresses

`acceleration_structures` verifies that an acceleration structure can be recreated at the exact AS device address, backing buffer opaque capture address, and backing memory opaque capture address saved during the capture phase, and that the recreated AS produces identical ray traversal. During capture, the host creates every AS with `VK_ACCELERATION_STRUCTURE_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT_KHR`, builds it, then records `captureAddr`, `bufferOpaqueCaptureAddr`, and `memoryOpaqueCaptureAddr` through `fillAcclerationStructureOpaqueCaptureReplayAddressInfo` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1182-L1209). During replay, the same three addresses are passed back into `createAndBuild`, `createAndCopyFrom`, or `createAndDeserializeFrom`.

The four AS sub-axes configure the operation rather than changing what is captured. `operationType` selects whether the replayed AS is built from scratch, copied, compacted, or deserialized from a serialized blob. `buildType` selects the host or device build path. `operationTarget` selects whether the top or bottom AS is the one copied, compacted, or serialized. `bottomTestType` selects triangle or AABB geometry, where the AABB path also exercises the intersection shader.

## Shader Analysis

This page uses one representative walkthrough. The rgen shader is generated once and shared by both children; the children differ in host-side SBT and AS construction, not in rgen logic. The closest-hit, miss, and intersection shaders are simple constant writers, so they do not merit separate walkthroughs. The `chit0`..`chit3` shaders write `uvec4(2*(shaderNdx+1), 0, 0, 1)`, `miss` writes `uvec4(1, 0, 0, 1)`, and `isect` reports an intersection at `t = 0.5` with a zeroed hit attribute [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L980-L1013).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.capture_replay.shader_binding_tables.pipeline_single
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `shader_binding_tables` | Tests SBT buffer opaque capture address replay. |
| `pipeline_single` | One captured pipeline is recreated during replay; one replay layer is compared against the capture layer. |
| Capture phase | SBT buffers created with `VK_BUFFER_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT`; addresses saved. |
| Replay phase | SBT buffers recreated at saved addresses with no capture-replay flag. |
| `targetLayer` | `0` in both phases, so capture and replay write into the same image layer for direct comparison. |

#### Purpose

This rgen shader drives one ray per pixel of the 8x8 launch. Each ray's hit or miss result is written into the 3D result image at the layer selected by the uniform buffer. The host compares the capture-phase layer against the replay-phase layer to confirm that the replayed SBT addresses resolve to the same shader-group handles.

#### Structural Design

| Step | rgen behavior | Meaning |
|------|---------------|---------|
| 1 | Read `gl_LaunchIDEXT.xy` and convert to a pixel-center origin `(x + 0.5, y + 0.5, 0.5)`. | Each of the 8x8 launch invocations traces one ray into the checkerboard AS. |
| 2 | Zero-initialize `hitValue`. | Miss pixels stay 0 until the miss shader overwrites them with 1; hit pixels get a non-zero slot index from the selected closest-hit shader. |
| 3 | Call `traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0)`. | Traces a ray straight down the negative Z axis. The `sbtRecordOffset`, `sbtRecordStride`, and `missIndex` are all 0; the SBT slot is selected purely by the instance's `instanceShaderBindingTableRecordOffset`. |
| 4 | `imageStore(result, ivec3(gl_LaunchIDEXT.xy, uniformParams.targetLayer), hitValue)`. | Writes the SBT-resolved value into the layer chosen by the host, separating capture output from replay output. |

The host fills `uniformParams.targetLayer` per pipeline. During capture it is always 0. During replay it is 0 for `pipeline_single`, and 0 or 1 per pipeline for the two-pipeline orderings [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1525-L1531).

#### Shader Code

Reconstructed GLSL from the `initPrograms` literal [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L955-L977):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT uvec4 hitValue;
layout(set = 0, binding = 0) uniform UniformParams
{
  uint targetLayer;
} uniformParams;
layout(r32ui, set = 0, binding = 1) uniform uimage3D result;
layout(set = 0, binding = 2) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin     = 0.0;
  float tmax     = 1.0;
  vec3  origin   = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, 0.5);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  hitValue       = uvec4(0,0,0,0);
  traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec3(gl_LaunchIDEXT.xy, uniformParams.targetLayer), hitValue);
}
```

#### Additional Info

- The rgen shader is identical across both children. The SBT child uses shader groups `rgen` (0), `miss` (1), and `chit0`..`chit3` (2..5). The AS child uses `rgen` (0), `chit1` for the triangle hit group (1), `chit1` plus `isect` for the AABB hit group (2), and `miss` (3) [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L358-L377), [AS shader setup](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L768-L785).
- The TLAS instance's `instanceShaderBindingTableRecordOffset` is set to `y % RTCR_SHADER_COUNT` in the SBT child, so each checkerboard row maps to a distinct hit SBT slot and therefore a distinct `chit` shader [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L343-L353). This is what makes the per-pixel value depend on which SBT slot the implementation selected.
- The result image is `VK_FORMAT_R32_UINT` 3D, with depth equal to `pipelineCount` so every pipeline in a replay phase can write into its own layer without overwriting another [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1111-L1129).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| SBT test type | No GLSL change. The host creates one or two pipelines and writes `targetLayer = 0` or `1` per pipeline into the uniform buffer. | [uniform fill](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1525-L1531) |
| AS operation type | No GLSL change. The host rebuilds, copies, compacts, or deserializes the AS at the saved addresses before tracing. | [AS operation switch](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1261-L1369) |
| AS build type | No GLSL change. The host selects `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` or `_DEVICE_KHR`. | [build type loop](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1690-L1724) |
| AS bottom geometry | No GLSL change to rgen. The host picks triangles or AABBs for the bottom-level AS; the AABB path binds the `isect` intersection shader in the hit group. | [bottom test type loop](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1701-L1720) |
| Capture versus replay | No GLSL change. The same rgen runs in both phases; only the host-side SBT and AS construction differs. | [runTest(bool replay)](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1046-L1597) |

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
; Bound: 71
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %hitValue %topLevelAS %result %uniformParams
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
               OpName %UniformParams "UniformParams"
               OpMemberName %UniformParams 0 "targetLayer"
               OpName %uniformParams "uniformParams"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 2
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %result Binding 1
               OpDecorate %result DescriptorSet 0
               OpDecorate %UniformParams Block
               OpMemberDecorate %UniformParams 0 Offset 0
               OpDecorate %uniformParams Binding 0
               OpDecorate %uniformParams DescriptorSet 0
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
%UniformParams = OpTypeStruct %uint
%_ptr_Uniform_UniformParams = OpTypePointer Uniform %UniformParams
%uniformParams = OpVariable %_ptr_Uniform_UniformParams Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %v3int = OpTypeVector %int 3
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
         %63 = OpAccessChain %_ptr_Uniform_uint %uniformParams %int_0
         %64 = OpLoad %uint %63
         %65 = OpBitcast %int %64
         %67 = OpCompositeExtract %int %58 0
         %68 = OpCompositeExtract %int %58 1
         %69 = OpCompositeConstruct %v3int %67 %68 %65
         %70 = OpLoad %v4uint %hitValue
               OpImageWrite %53 %69 %70 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Two-phase execution.** `iterate` calls `runTest(false)` for the capture phase and `runTest(true)` for the replay phase, then hands both result vectors to `verifyImage` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1599-L1610).
- **Pipeline count.** `pipelineCount` is 1 for the capture phase, for `pipeline_single`, and for the AS child. It is 2 for `pipeline_after_captured` and `pipeline_before_captured`, so the replay phase can run both pipelines into distinct image layers [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1063-L1066).
- **Acceleration structure setup.** Both children build a checkerboard of bottom-level ASes over the 8x8 grid, with one BLAS per odd `(x + y)` cell. The SBT child gives each instance `instanceShaderBindingTableRecordOffset = y % RTCR_SHADER_COUNT` so each row routes to a distinct hit SBT slot. The AS child uses `TTT_IDENTICAL_INSTANCES` when the bottom AS is the operation target and `TTT_DIFFERENT_INSTANCES` (one shared BLAS, instances differ by transform) when the top AS is the target [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L641-L766).
- **AS operation matrix.** When `operationType` is not `OP_NONE`, the host applies the operation to the selected `operationTarget` level between build and trace. `OP_COPY` uses `createAndCopyFrom`; `OP_COMPACT` queries the compacted size first, then copies into a smaller allocation; `OP_SERIALIZE` writes to a `SerialStorage`, then deserializes into a fresh AS. Every derived AS keeps the `DEVICE_ADDRESS_CAPTURE_REPLAY_BIT_KHR` flag and the saved addresses [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1261-L1523).
- **Query pool round trip.** The `gpu_built` path with compaction or serialization needs the compacted or serialized size on the host before allocating the destination AS. The host ends the command buffer, submits, calls `getQueryPoolResults`, resets the command pool, and begins a new command buffer [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1238-L1258), [top-level round trip](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1411-L1431).
- **Uniform buffer per pipeline.** The host writes the pipeline index (`0` or `1`) into each pipeline's uniform buffer as `targetLayer`, then flushes it. This is how the rgen shader knows which image layer to write into [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1525-L1531).
- **Image clear and barriers.** The host clears the 3D result image to `0xFF` (the R channel of `makeClearValueColorU32(0xFF, 0u, 0u, 0u)` for `VK_FORMAT_R32_UINT`), transitions it to `GENERAL` with `ACCELERATION_STRUCTURE_READ_BIT_KHR | ACCELERATION_STRUCTURE_WRITE_BIT_KHR` access, traces rays, then inserts a `SHADER_WRITE` to `TRANSFER_READ` barrier before `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` to `HOST_READ` barrier before invalidation [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1146-L1585).
- **Copyback and comparison.** The host invalidates the mapped result buffer, copies it into a `std::vector<uint32_t>`, and passes it to `verifyImage`. The SBT child compares every replay layer against the capture layer; the AS child compares the single replay layer against the capture layer. Both return `failures == 0` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L579-L597), [AS verifyImage](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L828-L844).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_binding_tables` (`pipeline_single`) | The implementation did not honor the replayed SBT buffer opaque capture addresses for the raygen, miss, or hit regions, or did not preserve shader-group handle data at those addresses when the SBT was recreated without the capture-replay create flag. |
| `shader_binding_tables` (`pipeline_after_captured`) | The implementation did not correctly isolate a captured pipeline from a subsequently created non-captured pipeline, leaking or corrupting shader-group handle state across the two pipelines. |
| `shader_binding_tables` (`pipeline_before_captured`) | The implementation did not support mixed captured/non-captured shader-group handles (`rayTracingPipelineShaderGroupHandleCaptureReplayMixed`), or did not correctly replay SBT addresses when a non-captured pipeline was created first. |
| `acceleration_structures` (`building`) | The implementation did not honor the replayed AS device address, backing buffer opaque capture address, or backing memory opaque capture address when building an AS from scratch at the captured addresses. |
| `acceleration_structures` (`copy`) | The implementation did not preserve the captured addresses through a `vkCmdCopyAccelerationStructureKHR` operation, producing a copy AS at the replayed address that does not match the original. |
| `acceleration_structures` (`compaction`) | The implementation did not preserve the captured addresses through a compaction copy, or returned an incorrect compacted size from the query pool, producing a compacted AS that does not match the original. |
| `acceleration_structures` (`serialization`) | The implementation did not preserve the captured addresses through serialize-then-deserialize, or produced a serialized blob that does not round-trip to an identical AS. |
| `acceleration_structures` (`cpu_built`) | The host-side AS build path (`VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`) did not honor the replayed addresses, gated by `accelerationStructureHostCommands`. |
| `acceleration_structures` (`gpu_built`) | The device-side AS build path did not honor the replayed addresses, or the query pool results used for compaction/serialization sizing were read back incorrectly. |
| `acceleration_structures` (`top`/`bottom` target) | The replayed address handling failed specifically for the AS level selected as the copy/compact/serialize target. |
| `acceleration_structures` (`triangles`/`aabbs`) | The replayed address handling failed for a specific bottom-level geometry type, including the intersection shader path used for AABBs. |

All cases report failure through the same host-side image comparison. The shader never writes a fail flag; it writes the SBT- or AS-resolved per-pixel value, and the host compares it against the capture layer.

### Cause Analysis

#### SBT buffer opaque capture address replay failed

**Possible failure symptoms:** A `shader_binding_tables` case fails `verifyImage`. Replay-layer pixels contain values that differ from the capture layer: hit pixels carry the wrong `chit` slot index, miss pixels carry a non-`1` value, or pixels that were hits during capture become misses during replay (or vice versa).

**Possible implementation causes:** During replay the host recreates the raygen, miss, and hit SBT buffers at `sbtSavedRaygenAddress`, `sbtSavedMissAddress`, and `sbtSavedHitAddress` without the `VK_BUFFER_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT` flag, passing the saved address through `createShaderBindingTable`. A grounded investigation should check whether the implementation honors the `opaqueCaptureAddress` argument when allocating the replay SBT buffer and its backing memory, whether the recreated SBT region addresses fed to `cmdTraceRays` resolve to the same shader-group handles as the capture phase, and whether the hit SBT region stride `RTCR_SHADER_COUNT * shaderGroupHandleSize` is preserved. If `pipeline_single` passes but the two-pipeline orderings fail, the issue is more likely in pipeline ordering than in address replay itself.

#### SBT pipeline ordering or mixed handle support failed

**Possible failure symptoms:** `pipeline_after_captured` or `pipeline_before_captured` fails while `pipeline_single` passes. One of the two replay layers matches the capture layer but the other does not, or both differ.

**Possible implementation causes:** `pipeline_after_captured` creates the captured pipeline first, then a non-captured pipeline. `pipeline_before_captured` reverses the order and also requires `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` because the spec allows implementations to forbid mixing captured and non-captured shader-group handles. A grounded investigation should check whether the implementation correctly isolates shader-group handle state between the two pipelines, whether `rayTracingPipelineShaderGroupHandleCaptureReplayMixed` is correctly reported and enforced, and whether the non-captured pipeline's SBT buffers (created with `opaqueCaptureAddress = 0`) are placed at addresses that do not collide with the captured pipeline's SBT buffers. If only `pipeline_before_captured` fails, the cause is more likely in mixed-handle support than in address replay.

#### AS opaque capture address replay failed

**Possible failure symptoms:** An `acceleration_structures.building` case fails `verifyImage`. Replay-layer pixels differ from the capture layer: hit pixels become misses, miss pixels become hits, or hits route to the wrong geometry.

**Possible implementation causes:** During replay the host passes `captureAddr`, `bufferOpaqueCaptureAddr`, and `memoryOpaqueCaptureAddr` back into `createAndBuild`. A grounded investigation should check whether the implementation honors the AS device address carried in `VkAccelerationStructureCreateInfoKHR::deviceAddress`, whether the backing buffer is allocated at the replayed opaque capture address through `VkBufferOpaqueCaptureAddressCreateInfo`, and whether the backing memory is allocated at the replayed opaque capture address through `VkMemoryOpaqueCaptureAddressAllocateInfo`. If only `cpu_built` fails, the host build path is suspect; if only `gpu_built` fails, the device build path is suspect.

#### AS copy, compaction, or serialization did not preserve addresses

**Possible failure symptoms:** An `acceleration_structures.copy`, `.compaction`, or `.serialization` case fails while `.building` passes. The replay layer differs from the capture layer even though the rebuilt-from-scratch AS round-trips correctly.

**Possible implementation causes:** `OP_COPY` calls `createAndCopyFrom` with the saved addresses. `OP_COMPACT` queries the compacted size first, then copies into a smaller allocation at the saved addresses. `OP_SERIALIZE` writes to a `SerialStorage`, then calls `createAndDeserializeFrom` at the saved addresses. A grounded investigation should check whether the derived AS preserves the `VK_ACCELERATION_STRUCTURE_CREATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT_KHR` flag and the saved device address, whether the compaction query pool returns a correct compacted size, and whether the serialized blob round-trips to an AS with identical traversal behavior. If `compaction` fails but `copy` passes, the query-pool size or the smaller allocation is suspect; if `serialization` fails, the serialize or deserialize path is suspect.

#### AS build path or query pool handling failed

**Possible failure symptoms:** An `acceleration_structures.gpu_built` case with `compaction` or `serialization` fails, and the failure correlates with the `getQueryPoolResults` round trip rather than with the AS itself.

**Possible implementation causes:** The `gpu_built` path ends the command buffer, submits, calls `getQueryPoolResults` with `VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT`, resets the command pool, and begins a new command buffer before allocating the destination AS. A grounded investigation should check whether the query pool returns the correct compacted or serialized size, whether the wait bit correctly synchronizes the build before the size is read, and whether the command pool reset releases the prior build's resources without corrupting the captured addresses. This cause is specific to `gpu_built` because the `cpu_built` path does not need a query pool round trip.

#### Host-side reference or copyback error

**Possible failure symptoms:** The host reports failure but device-side reasoning does not explain the mismatch. The replay layer contains values that look reasonable but do not match the capture layer, or the mismatch appears across many cases consistently.

**Possible implementation causes:** The host uses the same `runTest` path for capture and replay, so a bug in image clear, barrier placement, `cmdCopyImageToBuffer`, or `invalidateMappedMemoryRange` would affect both phases. The `targetLayer` uniform fill and the per-pipeline descriptor set updates are also host-side. Source-level investigation would be needed to distinguish an actual device-side capture/replay bug from a host-side reference or copyback bug; a host-side bug would likely affect many cases consistently rather than a single configuration.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_buffer_device_address`, `VK_KHR_acceleration_structure`, and `VK_KHR_ray_tracing_pipeline`, with `rayTracingPipeline == VK_TRUE`, `accelerationStructure == VK_TRUE`, and `bufferDeviceAddressCaptureReplay == VK_TRUE` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L904-L949).
- The SBT child requires `rayTracingPipelineShaderGroupHandleCaptureReplay == VK_TRUE`. The `pipeline_before_captured` case also requires `rayTracingPipelineShaderGroupHandleCaptureReplayMixed == VK_TRUE` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L915-L926).
- The AS child requires `accelerationStructureCaptureReplay == VK_TRUE` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L934-L937).
- The AS child's `cpu_built` path also requires `accelerationStructureHostCommands == VK_TRUE` [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L939-L943).

### Design-based pruning

- The SBT child registers only three leaves, one per `testType` ordering. There is no axis for build type, geometry type, or operation type because the SBT buffers are the only captured object and their recreation does not depend on those dimensions [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1614-L1643).
- The AS child pairs `TTT_DIFFERENT_INSTANCES` with `top_acceleration_structure` and `TTT_IDENTICAL_INSTANCES` with `bottom_acceleration_structure`. This keeps the operation target as the only AS that changes between capture and replay, so the copy, compaction, or serialization is applied to exactly one AS level per case [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1701-L1706).
- The AS child applies `OP_NONE` (`building`) without an operation target distinction in the registered name, because there is no copy, compact, or serialize step to target. The `operationTarget` axis still appears in the registered path for `building` cases but has no behavioral effect there [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1685-L1726).
- The image and dispatch size is fixed at `8x8` (`RTCR_DEFAULT_SIZE`) for every case. The test does not vary resolution because the capture/replay property is independent of launch dimensions [vktRayTracingCaptureReplayTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L57-L58).

## Key Takeaways

- The two children share a capture-then-replay structure but capture different object types: SBT buffers versus acceleration structures. The direct child is therefore the primary behavioral axis.
- The rgen shader is identical across both children and across all configuration axes. The host-side SBT and AS construction, plus the `targetLayer` uniform, do all the family and phase switching.
- The three SBT orderings are not separate capture/replay mechanisms; they test whether captured and non-captured shader-group handles can coexist, with `pipeline_before_captured` exercising the mixed-handle feature gate.
- The AS child's four configuration axes all exercise the same core mechanism (recreate the AS at saved addresses). They differ in which operation produces the replayed AS, which build path is used, and which AS level and geometry type are involved.
- Failure analysis splits along two axes: which object type failed to replay (SBT versus AS), and, within AS, whether the failure is in address replay itself, in the copy/compact/serialize preservation, or in the build path and query pool handling.
- Every case reports failure through the same host-side image comparison with no tolerance, so a single mismatched pixel is enough to fail a case.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category root registration | [vktRayTracingCaptureReplayTests.cpp#L1729-L1739](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1729-L1739) | Creates the `capture_replay` group and attaches the two direct children. |
| SBT family registration | [vktRayTracingCaptureReplayTests.cpp#L1614-L1643](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1614-L1643) | Registers `pipeline_single`, `pipeline_after_captured`, `pipeline_before_captured`. |
| AS family registration | [vktRayTracingCaptureReplayTests.cpp#L1645-L1727](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1645-L1727) | Registers the operationType x buildType x operationTarget x bottomTestType matrix. |
| `TestParams` struct | [vktRayTracingCaptureReplayTests.cpp#L157-L168](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L157-L168) | Captures testType, operationTarget, operationType, buildType, bottomType, topType, width/height, and the test configuration pointer. |
| `checkSupport` feature gates | [vktRayTracingCaptureReplayTests.cpp#L904-L950](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L904-L950) | Maps each test type to the Vulkan feature it requires. |
| `initPrograms` shader generation | [vktRayTracingCaptureReplayTests.cpp#L952-L1027](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L952-L1027) | Generates the rgen, chit0..3, isect, and miss shaders shared by both children. |
| SBT capture phase | [vktRayTracingCaptureReplayTests.cpp#L390-L433](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L390-L433) | Creates SBT buffers with the capture-replay bit and records opaque capture addresses. |
| SBT replay phase | [vktRayTracingCaptureReplayTests.cpp#L434-L577](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L434-L577) | Recreates SBT buffers at saved addresses for each testType ordering. |
| AS build/copy/compact/serialize | [vktRayTracingCaptureReplayTests.cpp#L1163-L1523](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1163-L1523) | Drives the AS operation matrix and records/replays opaque capture addresses. |
| `runTest` two-phase driver | [vktRayTracingCaptureReplayTests.cpp#L1046-L1597](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L1046-L1597) | Builds resources, runs capture and replay, copies back results. |
| `verifyImage` (SBT) | [vktRayTracingCaptureReplayTests.cpp#L579-L597](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L579-L597) | Pixel-by-pixel comparison of replay layers against the capture layer. |
| `verifyImage` (AS) | [vktRayTracingCaptureReplayTests.cpp#L828-L844](../../../modules/vulkan/ray_tracing/vktRayTracingCaptureReplayTests.cpp#L828-L844) | Single-layer comparison for the AS child. |
