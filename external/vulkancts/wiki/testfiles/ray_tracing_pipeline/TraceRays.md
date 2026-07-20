## Overview

**Core question:** Does every `vkCmdTraceRays*` dispatch entry point (direct, indirect with CPU- or GPU-sourced dimensions, and indirect2 with CPU- or GPU-sourced shader binding tables plus dimensions) produce the identical expected hit/miss chessboard for the same scene and launch dimensions?

- [vktRayTracingTraceRaysTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp) implements three test families under `ray_tracing_pipeline`: `trace_rays_cmds`, `trace_rays_cmds_maintenance_1`, and `trace_rays_indirect2`.
- The three families share one chessboard scene and one rgen/chit/miss shader set. What varies is the dispatch command used to launch the rays and where that command reads its parameters from (host-supplied inline, a host-filled device buffer, or a compute-filled device buffer).
- `trace_rays_cmds` covers `vkCmdTraceRaysKHR` (direct) and `vkCmdTraceRaysIndirectKHR` (indirect CPU/GPU). `trace_rays_cmds_maintenance_1` covers `vkCmdTraceRaysIndirect2KHR` (indirect2 CPU/GPU) using the extended `VkTraceRaysIndirectCommand2KHR` struct. `trace_rays_indirect2` covers `vkCmdTraceRaysIndirect2KHR` again but adds a partial-copy style and a submit-queue choice.
- The page explains the dispatch-path axis, the indirect buffer sourcing, the partial-copy struct split, and what a failure of each path points to.

## Background Knowledge

- **Direct dispatch.** `vkCmdTraceRaysKHR` takes the four shader binding table (SBT) regions and the `width`/`height`/`depth` launch dimensions as inline command parameters. Nothing is read indirectly.
- **Indirect dispatch.** `vkCmdTraceRaysIndirectKHR` takes the four SBT regions inline, but the launch dimensions are read by the device from a `VkTraceRaysIndirectCommandKHR` struct (only `width`, `height`, `depth`) at a buffer device address. Requires the `rayTracingPipelineTraceRaysIndirect` feature.
- **Indirect2 dispatch.** `vkCmdTraceRaysIndirect2KHR` takes a single buffer device address. The device reads a `VkTraceRaysIndirectCommand2KHR` struct that contains all four SBT regions *and* the launch dimensions. The spec states this command "behaves similarly to `vkCmdTraceRaysIndirectKHR` except that shader binding table parameters as well as dispatch dimensions are read by the device from `indirectDeviceAddress`." Requires the `rayTracingPipelineTraceRaysIndirect2` feature from `VK_KHR_ray_tracing_maintenance1`.
- **CPU-sourced versus GPU-sourced parameters.** For the indirect and indirect2 variants, the parameter buffer can be filled by the host (a `deMemcpy` into a host-visible buffer plus a flush) or by a compute shader that copies the values from a uniform buffer into the indirect buffer (a storage buffer with a shader device address), followed by a `SHADER_WRITE` -> `INDIRECT_COMMAND_READ` barrier.
- **Null-dimension dispatch.** The dimension matrix includes `{0,0,0}` and single-zero cases. A zero in any dimension means no raygen invocations; the test still clears an 8x8x1 fallback image and expects every voxel to remain at the clear value.

## Registration Hierarchy

```text
ray_tracing_pipeline
├── trace_rays_cmds
├── trace_rays_cmds_maintenance_1
└── trace_rays_indirect2
```

The three test families are direct children of the `ray_tracing_pipeline` test category, registered by [createTraceRaysTests](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1502), [createTraceRaysMaintenance1Tests](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1504-L1549), and [createTraceRays2Tests](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1551-L1593).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Dispatch command | `direct`, `indirect_cpu`, `indirect_gpu` (cmds); `indirect2_cpu`, `indirect2_gpu` (maintenance1); `indirect_cpu`, `indirect_gpu` (indirect2) | Selects which `vkCmdTraceRays*` command is recorded and where its parameters are sourced. This is the primary behavioral axis. | [TraceType enum](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L60-L67) |
| Launch dimensions | `{0,0,0}`, `{0,1,1}`, `{1,0,1}`, `{1,1,0}`, `{8,1,1}`, `{8,8,1}`, `{8,8,8}`, `{11,1,1}`, `{11,13,1}`, `{11,13,5}` (cmds and maintenance1); `{11,17,1}`, `{19,11,2}`, `{23,47,3}`, `{47,19,4}` (indirect2) | Scales the 3D launch volume and the chessboard AS grid. Zero values exercise null dispatch. | [traceDimensions](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1474-L1477), [extendedTraceDimensions](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1518-L1524), [indirect2 traceDimensions](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1565) |
| Copy style (indirect2 only) | `full_copy`, `partial_copy` | Selects whether the compute shader copies all 12 SBT fields of `VkTraceRaysIndirectCommand2KHR` or only a subset, with the host pre-filling the rest. | [copyStyles](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1560) |
| Submit queue (indirect2 only) | `submit_graphics`, `submit_compute` | Selects the queue family (graphics or compute) the indirect2 trace is submitted to. | [submitQueues](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1562-L1563) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L297) |

## Behavior Parameters

The primary behavioral axis is the dispatch command variant and parameter source (`traceType`). The three test families each exercise a distinct slice of this axis, so this section groups subsections by family.

### trace_rays_cmds: direct and indirect dispatch with inline SBT

**`direct`**: Records `vkCmdTraceRaysKHR` with all four SBT regions and the launch dimensions passed inline. This is the baseline: if it fails, the shared chessboard scene, SBT construction, or rgen/chit/miss shader path is broken, independent of any indirect mechanism.

**`indirect_cpu`**: Records `vkCmdTraceRaysIndirectKHR` with the SBT regions inline but the launch dimensions read from a host-written `VkTraceRaysIndirectCommandKHR`. The host `deMemcpy`s the struct into a host-visible indirect buffer and flushes it. This isolates the device's read of host-filled indirect dimensions.

**`indirect_gpu`**: Same command as `indirect_cpu`, but the dimensions are written into the indirect buffer by a compute shader (`compute_indirect_command`) that copies them from a uniform buffer. A buffer memory barrier transitions the indirect buffer from `SHADER_WRITE` to `INDIRECT_COMMAND_READ` before the trace. This adds a compute dispatch and a synchronization dependency into the command stream.

### trace_rays_cmds_maintenance_1: indirect2 dispatch with device-sourced SBT

**`indirect2_cpu`**: Records `vkCmdTraceRaysIndirect2KHR` with a single buffer device address. The host fills a `VkTraceRaysIndirectCommand2KHR` struct (all four SBT regions plus dimensions) and flushes it. The SBT region addresses/sizes/strides are computed from the SBT regions by the host and written into the struct. This exercises device-side resolution of the SBT parameters from a host-filled struct.

**`indirect2_gpu`**: Same command, but the extended struct is assembled by a compute shader that copies the SBT fields from a uniform buffer into the indirect storage buffer. The compute shader is the maintenance1 variant of `compute_indirect_command`, which copies all 12 SBT fields plus the dimensions. This exercises device-side SBT resolution from a compute-written struct.

### trace_rays_indirect2: indirect2 with copy style and submit queue

**`indirect_cpu` / `indirect_gpu`**: Same two dispatch paths as the maintenance1 family, but crossed with two extra axes.

**`full_copy`**: The compute shader copies all 12 SBT fields of `VkTraceRaysIndirectCommand2KHR` from the uniform buffer. The host pre-fills nothing into the indirect buffer; the struct is fully assembled on the device.

**`partial_copy`**: The compute shader copies only a subset of the SBT fields (driven by the `full` push constant set to 0). The host pre-fills the remaining fields via `makeIndirectStructAndFlush` with `source=false`. This stresses that `vkCmdTraceRaysIndirect2KHR` reads each field from wherever it ends up in the unified struct, regardless of who wrote it.

**`submit_graphics` / `submit_compute`**: The indirect2 trace is submitted to a queue family selected by `getQueueFamilyIndexAtExact`. `checkSupport` throws `NotSupportedError` if the exact requested queue family is absent. This adds a queue-selection requirement on top of the dispatch path.

## Shader Analysis

The rgen, chit, and miss shaders are generated as inline GLSL strings in [RayTracingTraceRaysIndirectTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L295-L415) and [TraceRaysIndirect2Case::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L931-L1051). The rgen/chit/miss set is identical across all three families; only the dispatch command and the indirect buffer filling differ. The GPU-sourced variants additionally generate a `compute_indirect_command` compute shader that copies the parameter struct.

This page uses one walkthrough because the rgen shader is the stage whose ray traversal produces the chessboard result that validates every dispatch variant. The chit and miss shaders are fixed one-liners (write the hit or miss color) and are summarized in the variation table rather than given separate walkthroughs.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path: `dEQP-VK.ray_tracing_pipeline.trace_rays_cmds.direct.8_8_8`.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `direct` | Baseline dispatch: `vkCmdTraceRaysKHR` with inline SBT regions and dimensions. No indirect buffer is involved, so the shader result isolates the ray tracing path itself. |
| `8_8_8` | A 3D 8x8x8 launch volume. The chessboard AS grid places a BLAS at every `(x,y,z)` where `(x+y+z)` is odd, giving equal hit and miss coverage. |
| rgen at group 0, chit at group 1, miss at group 2 | Three SBT regions, each with one entry. |
| `r32ui` 3D result image | One uint per voxel; `imageStore` writes the payload .x. |

#### Purpose

This shader checks that the rgen ray traversal, closest-hit, and miss shader path produces the expected hit/miss chessboard pattern for an 8x8x8 launch volume, which is the reference result that every indirect and indirect2 variant must reproduce.

#### Structural Design

| Step | rgen shader | Result |
|------|------------|--------|
| 1 | Compute ray origin from `gl_LaunchIDEXT + 0.5` | One ray per launch ID, centered in its cell. |
| 2 | Set direction to `(0, 0, -1)` | Ray travels straight down the -z axis. |
| 3 | Zero the payload `hitValue` | Default before traversal. |
| 4 | `traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0)` | Traverse into the chessboard AS; chit or miss fills `hitValue`. |
| 5 | `imageStore(result, ivec3(gl_LaunchIDEXT), hitValue)` | Write the per-voxel result into the 3D image. |

Odd `(x+y+z)` cells hit their quad; chit writes `kHitColorValue` (2). Even cells miss; miss writes `kMissColorValue` (1).

#### Shader Code

Reconstructed rgen GLSL, faithful to the source string in [RayTracingTraceRaysIndirectTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L364-L383). The `updateRayTracingGLSL` wrapper is an identity function, so the emitted source matches the string exactly.

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Ray payload carries the per-voxel hit/miss result back to rgen.
layout(location = 0) rayPayloadEXT uvec4 hitValue;
/// 3D storage image; one uint per launch ID. Cleared to 0xFF before the trace.
layout(r32ui, set = 0, binding = 0) uniform uimage3D result;
/// Top-level AS over the chessboard BLAS grid.
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin     = 0.0;
  float tmax     = 1.0;
  /// Origin is the cell center; ray travels straight down -z.
  vec3  origin   = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, float(gl_LaunchIDEXT.z + 0.5f));
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  hitValue       = uvec4(0,0,0,0);
  /// Traverse; chit writes 2 on hit, miss writes 1 on miss.
  traceRayEXT(topLevelAS, 0, 0xFF, 0, 0, 0, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec3(gl_LaunchIDEXT), hitValue);
}
```

#### Additional Info

- The closest-hit shader writes `uvec4(kHitColorValue,0,0,1)` (2) and the miss shader writes `uvec4(kMissColorValue,0,0,1)` (1); both are fixed one-liners that do not vary across any case in the three families [chit, miss sources](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L386-L414).
- The `traceRayEXT` flags are `0` (no flags), cull mask `0xFF` (no culling), SBT indices `0,0,0` (raygen-relative hit group 0, miss index 0). These are constant across all variants.
- The GPU-sourced variants add a `compute_indirect_command` compute shader that copies the parameter struct from a uniform buffer into the indirect storage buffer. That shader is not part of the ray tracing result path and is covered in the runtime section.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Dispatch command | The rgen/chit/miss shaders are identical for `direct`, `indirect_cpu`, `indirect_gpu`, `indirect2_cpu`, and `indirect2_gpu`. The dispatch command differs only on the host side. | [dispatch selection](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L776-L791) |
| Maintenance1 compute shader | The `trace_rays_cmds_maintenance_1` GPU-sourced variant of `compute_indirect_command` copies the 12 extended SBT fields plus dimensions. | [maintenance1 compute shader](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L298-L361) |
| Indirect2 partial-copy compute shader | The `trace_rays_indirect2` GPU-sourced variant adds a `push_constant uint full` that selects full vs partial field copy. | [indirect2 compute shader](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L934-L997) |
| Launch dimensions | The rgen uses `gl_LaunchIDEXT` directly, so dimensions scale the launch volume without changing shader text. Zero dimensions mean no rgen invocations. | [rgen shader](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L376-L381) |

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
; Bound: 63
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
     %uint_2 = OpConstant %uint 2
   %float_n1 = OpConstant %float -1
         %39 = OpConstantComposite %v3float %float_0 %float_0 %float_n1
     %v4uint = OpTypeVector %uint 4
%_ptr_RayPayloadKHR_v4uint = OpTypePointer RayPayloadKHR %v4uint
   %hitValue = OpVariable %_ptr_RayPayloadKHR_v4uint RayPayloadKHR
         %43 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
         %44 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_44 = OpTypePointer UniformConstant %44
 %topLevelAS = OpVariable %_ptr_UniformConstant_44 UniformConstant
   %uint_255 = OpConstant %uint 255
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
         %55 = OpTypeImage %uint 3D 0 0 0 2 R32ui
%_ptr_UniformConstant_55 = OpTypePointer UniformConstant %55
     %result = OpVariable %_ptr_UniformConstant_55 UniformConstant
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
         %32 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_2
         %33 = OpLoad %uint %32
         %34 = OpConvertUToF %float %33
         %35 = OpFAdd %float %34 %float_0_5
         %36 = OpCompositeConstruct %v3float %25 %30 %35
               OpStore %origin %36
               OpStore %direct %39
               OpStore %hitValue %43
         %47 = OpLoad %44 %topLevelAS
         %49 = OpLoad %v3float %origin
         %50 = OpLoad %float %tmin
         %51 = OpLoad %v3float %direct
         %52 = OpLoad %float %tmax
               OpTraceRayKHR %47 %uint_0 %uint_255 %uint_0 %uint_0 %uint_0 %49 %50 %51 %52 %hitValue
         %58 = OpLoad %55 %result
         %59 = OpLoad %v3uint %gl_LaunchIDEXT
         %61 = OpBitcast %v3int %59
         %62 = OpLoad %v4uint %hitValue
               OpImageWrite %58 %61 %62 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

Both test classes share the same chessboard scene construction and the same per-voxel result check. The differences are in how the indirect buffer is filled and which dispatch command is recorded.

### Chessboard scene and pipeline setup

- The host builds a 3D chessboard of bottom-level acceleration structures over the launch volume: a two-triangle quad BLAS exists at every `(x,y,z)` where `(x+y+z)` is odd; even cells have no geometry [initBottomAccelerationStructures](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L435-L480). The `trace_rays_indirect2` family uses a batched `BottomLevelAccelerationStructurePool` instead [initBottomAccellStructures](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1123-L1164).
- A top-level AS instances those BLAS [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L182-L210).
- The ray tracing pipeline has rgen at group 0, chit at group 1, miss at group 2. Three SBT regions are created with one entry each [pipeline + SBT](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L553-L578).
- A 3D `r32ui` result image sized to the launch volume is cleared to `kClearColorValue` (0xFF) and transitioned to `GENERAL` before the trace [image setup](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L580-L600).

### Indirect buffer filling

- **CPU-sourced** (`indirect_cpu`, `indirect2_cpu`): the host `deMemcpy`s the parameter struct into a host-visible indirect buffer and flushes it [INDIRECT_CPU / INDIRECT2_CPU fill](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L647-L672). For `trace_rays_indirect2`, `makeIndirectStructAndFlush` assembles the full `VkTraceRaysIndirectCommand2KHR` [struct flush](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1060-L1121).
- **GPU-sourced** (`indirect_gpu`, `indirect2_gpu`): the host writes the parameters into a uniform buffer, then records a compute dispatch of `compute_indirect_command` that copies them into the indirect storage buffer. A buffer memory barrier transitions the indirect buffer from `SHADER_WRITE` to `INDIRECT_COMMAND_READ` before the trace [INDIRECT_GPU compute + barrier](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L704-L753). For `trace_rays_indirect2` partial-copy, the host pre-fills some struct fields and the compute shader copies the rest, driven by the `full` push constant [partial-copy compute](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1342-L1367).

### Dispatch command selection

The recorded command depends on `traceType` [dispatch selection](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L776-L791):

- `DIRECT`: `cmdTraceRays` with inline SBT regions and dimensions.
- `INDIRECT_CPU` / `INDIRECT_GPU`: `cmdTraceRaysIndirect` with inline SBT regions and the indirect buffer device address.
- `INDIRECT2_CPU` / `INDIRECT2_GPU`: `vkd.cmdTraceRaysIndirect2KHR` with only the indirect buffer device address.

The `trace_rays_indirect2` family always uses `cmdTraceRaysIndirect2` [indirect2 dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1389).

### Result copyback and check

- After the trace, a memory barrier (`SHADER_WRITE` -> `TRANSFER_READ`) and `cmdCopyImageToBuffer` copy the 3D image into a host-visible result buffer, followed by a `TRANSFER_WRITE` -> `HOST_READ` barrier [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L793-L804).
- The host invalidates and scans every voxel. The expected value is `kHitColorValue` (2) for odd `(x+y+z)`, `kMissColorValue` (1) for even, or `kClearColorValue` (0xFF) for null-dimension cases where no raygen ran [per-voxel check](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L827-L842).
- Pass condition: `failures == 0`. The `trace_rays_indirect2` pass message also reports the BLAS pool allocation count [indirect2 check](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1421-L1440).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `direct` | The direct `vkCmdTraceRaysKHR` dispatch with host-supplied SBT regions and dimensions did not produce the expected hit/miss chessboard; points at SBT region setup, pipeline binding, or the rgen/chit/miss shader path itself. |
| `indirect_cpu` | `vkCmdTraceRaysIndirectKHR` did not read the host-written `VkTraceRaysIndirectCommandKHR` dimensions correctly, or the host flush of the indirect buffer was incomplete. |
| `indirect_gpu` | The compute shader that fills the indirect buffer did not write the dimensions, or the `SHADER_WRITE` -> `INDIRECT_COMMAND_READ` barrier did not make the write available/visible to the trace command. |
| `indirect2_cpu` | `vkCmdTraceRaysIndirect2KHR` did not correctly resolve the SBT regions and dimensions from the host-written `VkTraceRaysIndirectCommand2KHR`, or the extended struct fields were laid out / flushed incorrectly. |
| `indirect2_gpu` | The compute shader did not copy the extended SBT fields into the indirect storage buffer, or the barrier before the indirect2 trace did not cover the full struct, or device-side SBT address resolution from the struct failed. |
| `trace_rays_indirect2` partial_copy | The split source (host pre-fills some fields, compute copies others) produced an incomplete or inconsistent `VkTraceRaysIndirectCommand2KHR`, so device-side SBT resolution used wrong fields. |
| `trace_rays_indirect2` submit_graphics / submit_compute | The indirect2 trace on a non-default queue family (graphics or compute) did not execute or did not synchronize correctly, or the requested queue family was not selected properly. |

All leaves share the chessboard scene and the per-voxel equality check, so a failure common to all variants of one family points at shared infrastructure (AS build, SBT construction, image copyback) rather than the dispatch-specific path.

### Cause Analysis

#### Direct dispatch chessboard failure

**Possible failure symptoms:** A `direct` leaf failure means the 3D result image does not match the expected chessboard. Voxels that should be 2 (hit) are 1 (miss) or 0xFF (unwritten), or vice versa; the failure count is nonzero.

**Possible implementation causes:** The direct path has no indirect buffer, so a failure here points at the shared infrastructure: the chessboard BLAS/TLAS build, the SBT region construction, the pipeline binding, or the rgen/chit/miss shader execution. The SPIR-V walkthrough shows `OpTraceRayKHR` consuming the top-level AS and the `RayPayloadNV` storage class carrying the result back. A grounded investigation should check whether the SBT regions were built with the correct shader group handles and alignment, whether the acceleration structure was built and transitioned correctly before the trace, and whether `OpImageWrite` wrote the expected payload. If only the `direct` leaves fail and the indirect leaves pass, source-level investigation is needed to find what differs.

#### Indirect dimension read failure

**Possible failure symptoms:** An `indirect_cpu` or `indirect_gpu` leaf failure where the `direct` leaf with the same dimensions passes. Voxels may be 0xFF (as if no raygen ran, suggesting a zero or wrong dimension was read) or the image extent may be wrong.

**Possible implementation causes:** `vkCmdTraceRaysIndirectKHR` reads only `width`, `height`, `depth` from the indirect buffer at the supplied device address. For `indirect_cpu`, the host writes `VkTraceRaysIndirectCommandKHR` and flushes; an incomplete flush or a wrong device address would leave the device reading stale or zero dimensions. For `indirect_gpu`, the compute shader writes the dimensions and a `SHADER_WRITE` -> `INDIRECT_COMMAND_READ` barrier must make that write available before the trace. The spec ties `vkCmdTraceRaysIndirectKHR` to the `rayTracingPipelineTraceRaysIndirect` feature. A grounded investigation should check whether the indirect buffer device address is correct, whether the host flush covers the full struct, and whether the barrier src/dst access masks and pipeline stages are correct for the GPU-sourced path.

#### Indirect2 SBT and dimension resolution failure

**Possible failure symptoms:** An `indirect2_cpu` or `indirect2_gpu` leaf failure where the corresponding `indirect_cpu`/`indirect_gpu` leaf (same scene, inline SBT) passes. Voxels may be 0xFF (SBT not resolved, no raygen ran) or wrong (wrong SBT entry selected).

**Possible implementation causes:** `vkCmdTraceRaysIndirect2KHR` reads the full `VkTraceRaysIndirectCommand2KHR` struct (all four SBT regions plus dimensions) from a single device address. The spec states its members have the same meaning as the parameters of `vkCmdTraceRaysKHR` and must satisfy the same alignment and binding requirements. The host computes the SBT region addresses/sizes/strides from the SBT regions and writes them into the struct. For `indirect2_gpu`, the compute shader copies those fields from a uniform buffer. A grounded investigation should check whether the SBT addresses written into the struct match the actual SBT buffer device addresses, whether the struct layout matches `VkTraceRaysIndirectCommand2KHR`, whether the `rayTracingPipelineTraceRaysIndirect2` feature is supported, and (for GPU-sourced) whether the barrier covers the full struct size. Source-level investigation is needed if the failure only appears in indirect2 and not in the inline-SBT indirect path.

#### Partial-copy struct inconsistency

**Possible failure symptoms:** A `trace_rays_indirect2` `partial_copy` leaf failure where the `full_copy` leaf with the same buffer source and queue passes. The result may be partially correct (some voxels right, some wrong) or fully wrong.

**Possible implementation causes:** In the partial-copy path, the host pre-fills part of `VkTraceRaysIndirectCommand2KHR` via `makeIndirectStructAndFlush` with `source=false`, and the compute shader copies the remaining fields driven by the `full` push constant set to 0. The compute shader's `else` branch copies `raygenShaderRecordAddress`, `missShaderBindingTableStride`, `hitShaderBindingTableSize`, `callableShaderBindingTableAddress`, and `callableShaderBindingTableStride`, leaving the rest host-supplied. A grounded investigation should check whether the field split between host and compute is consistent (that every field the compute shader skips is actually pre-filled by the host) and whether the unified struct read by `vkCmdTraceRaysIndirect2KHR` reflects both writers. Source-level inspection of `makeIndirectStructAndFlush` and the compute shader's `else` branch is needed to confirm the field partitioning.

#### Submit-queue execution failure

**Possible failure symptoms:** A `trace_rays_indirect2` `submit_graphics` or `submit_compute` leaf failure where the same parameters on the other queue pass, or where all queue variants fail.

**Possible implementation causes:** The indirect2 trace is submitted to a queue family selected by `getQueueFamilyIndexAtExact`, which finds the first queue family whose flags exactly match the requested `VK_QUEUE_GRAPHICS_BIT` or `VK_QUEUE_COMPUTE_BIT`. The command pool and command buffer are allocated on that family. The spec allows ray tracing dispatch on compute-capable queues. A grounded investigation should check whether the requested queue family was found (otherwise `checkSupport` throws `NotSupportedError` before execution), whether the command buffer was allocated and submitted on the correct queue, and whether the result copyback and host read synchronize correctly against the non-default queue. If only one of graphics or compute fails, source-level investigation of the queue selection and submission is needed.

#### Shared infrastructure failure

**Possible failure symptoms:** All leaves of one or more families fail with the same pattern, regardless of dispatch command or buffer source.

**Possible implementation causes:** The chessboard BLAS grid, TLAS, SBT regions, pipeline, result image clear, image-to-buffer copy, and per-voxel check are shared across all variants within a test class. A failure common to all variants points at this shared setup rather than the dispatch-specific path. A grounded investigation should check whether the acceleration structures were built correctly, whether the SBT handles and alignment are valid, whether the image clear and layout transitions are correct, and whether the host-side expected-value rule (`(x+y+z)%2 ? hit : miss`) matches the actual geometry placement. Source-level inspection of `initBottomAccelerationStructures` and `initTopAccelerationStructure` is needed to confirm the chessboard pattern.

## Case Pruning

### Requirement-based pruning

- `trace_rays_cmds` and `trace_rays_cmds_maintenance_1` require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with `rayTracingPipeline` and `accelerationStructure` feature bits set [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L254-L293). If `accelerationStructure` is not set, the test throws `TestError`.
- The indirect variants (`indirect_cpu`, `indirect_gpu`) additionally require `rayTracingPipelineTraceRaysIndirect` [indirect feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L264-L266).
- The indirect2 variants (`indirect2_cpu`, `indirect2_gpu`) and the `trace_rays_indirect2` family require `VK_KHR_ray_tracing_maintenance1` with `rayTracingMaintenance1` and `rayTracingPipelineTraceRaysIndirect2` set [maintenance1 feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L268-L285), [indirect2 checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L898-L929).
- The `trace_rays_indirect2` family requires the requested queue family (graphics or compute) to be present; otherwise `checkSupport` throws `NotSupportedError` [queue check](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L919-L928).

### Design-based pruning

- The `trace_rays_cmds` and `trace_rays_cmds_maintenance_1` families share the same 10-entry dimension matrix (including null-dimension cases), so the indirect2 mechanism is exercised over the same launch volumes as the direct/indirect mechanism.
- The `trace_rays_indirect2` family uses a separate 4-entry dimension matrix with no null-dimension cases, because its focus is the copy-style and submit-queue axes rather than zero-extent handling.
- The copy-style and submit-queue axes exist only in `trace_rays_indirect2`; the maintenance1 family always does a full copy on the default queue.
- The callable SBT region is always zeroed (`makeStridedDeviceAddressRegionKHR(0, 0, 0)`), so no callable shaders are exercised here.

## Key Takeaways

- The three families share one chessboard scene and one rgen/chit/miss shader set; only the dispatch command and indirect buffer filling vary. This makes `direct` the baseline against which every indirect and indirect2 variant is compared.
- The behavioral axis is which `vkCmdTraceRays*` command runs and where its parameters are sourced: inline (direct), host-filled device buffer (indirect CPU), or compute-filled device buffer (indirect GPU), with indirect2 additionally sourcing the SBT regions on the device.
- The GPU-sourced path adds a compute dispatch and a `SHADER_WRITE` -> `INDIRECT_COMMAND_READ` barrier before the trace, exercising whether the indirect command reads parameters a prior compute shader wrote.
- The `trace_rays_indirect2` partial-copy style splits `VkTraceRaysIndirectCommand2KHR` between a host pre-fill and a compute copy, stressing that the indirect2 command reads each field from wherever it ends up in the unified struct.
- Null-dimension cases (`{0,0,0}` and single-zero permutations) verify that a zero-extent dispatch is a legal no-op that leaves the cleared image untouched.
- See `## Failure Meaning` for the per-path failure cause analysis. The most common failure shapes are indirect dimension read failure, indirect2 SBT resolution failure, partial-copy struct inconsistency, submit-queue execution failure, and shared infrastructure failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TraceType` enum | [vktRayTracingTraceRaysTests.cpp#L60-L67](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L60-L67) | Defines the five dispatch variants |
| `TestParams` / `TestParams2` | [vktRayTracingTraceRaysTests.cpp#L69-L82](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L69-L82) | Parameter structs for the two test classes |
| rgen / chit / miss shaders | [vktRayTracingTraceRaysTests.cpp#L364-L414](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L364-L414) | The chessboard ray-tracing shaders |
| compute_indirect_command (maintenance1) | [vktRayTracingTraceRaysTests.cpp#L298-L361](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L298-L361) | GPU-sourced struct copy with extended SBT fields |
| compute_indirect_command (indirect2) | [vktRayTracingTraceRaysTests.cpp#L934-L997](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L934-L997) | GPU-sourced struct copy with full/partial push constant |
| checkSupport (cmds + maintenance1) | [vktRayTracingTraceRaysTests.cpp#L254-L293](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L254-L293) | Feature gates for indirect and indirect2 |
| checkSupport (indirect2) | [vktRayTracingTraceRaysTests.cpp#L898-L929](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L898-L929) | Maintenance1 + indirect2 + queue family support |
| dispatch command selection | [vktRayTracingTraceRaysTests.cpp#L776-L791](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L776-L791) | Picks `cmdTraceRays` / `cmdTraceRaysIndirect` / `cmdTraceRaysIndirect2KHR` by `traceType` |
| per-voxel result check | [vktRayTracingTraceRaysTests.cpp#L827-L842](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L827-L842) | Expected-value rule and failures counter |
| indirect2 partial-copy struct split | [vktRayTracingTraceRaysTests.cpp#L1060-L1121](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1060-L1121) | `makeIndirectStructAndFlush` full vs partial field split |
| indirect2 queue selection | [vktRayTracingTraceRaysTests.cpp#L146-L179](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L146-L179) | `getQueueFamilyIndexAtExact` for graphics/compute queue |
| registration: trace_rays_cmds | [vktRayTracingTraceRaysTests.cpp#L1459-L1502](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1459-L1502) | `createTraceRaysTests` |
| registration: trace_rays_cmds_maintenance_1 | [vktRayTracingTraceRaysTests.cpp#L1504-L1549](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1504-L1549) | `createTraceRaysMaintenance1Tests` |
| registration: trace_rays_indirect2 | [vktRayTracingTraceRaysTests.cpp#L1551-L1593](../../../modules/vulkan/ray_tracing/vktRayTracingTraceRaysTests.cpp#L1551-L1593) | `createTraceRays2Tests` |
