## Overview

**Core question:** Can a single ray tracing pipeline containing up to 4096 callable shader groups be created, bound, and dispatched correctly, and does each launch ID reach the callable shader that writes its expected per-pixel value?

- [vktRayTracingBuildLargeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp) implements the single test family `large_shader_set` under the `ray_tracing_pipeline` test category.
- All leaves share one acceleration structure, one result image, and one rgen plus a wide set of callable shaders. What varies is the acceleration structure build path (`gpu` device build or `cpu_ht` host build) and, for host builds, the deferred-host worker-thread count.
- Each leaf builds a square `size x size` launch grid where `size` is 8, 16, 32, or 64. The rgen shader computes a linear index `n = width * gl_LaunchIDEXT.y + gl_LaunchIDEXT.x` and calls `executeCallableEXT(n, 0)`, so there is one callable shader per launch cell. The callable shader writes a deterministic value derived from its `(x, y)` position into a storage image, and the host compares the image against the same formula.
- The page explains the build-path axis, the size-driven shader count, the watchdog-managed pipeline creation, and what a failure of each build path points to.

## Background Knowledge

- **Callable shaders.** A ray tracing pipeline can include callable shader groups beyond raygen, hit, and miss groups. `executeCallableEXT(index, ...)` in rgen invokes the callable shader at SBT index `index`, passing data through a `callableDataEXT` / `callableDataInEXT` pair. This test populates the callable SBT with one group per launch cell, so the group count scales with the square of the size.
- **Acceleration structure build types.** `VK_KHR_acceleration_structure` defines `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR` (build recorded and executed on the device) and `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` (build performed by the host). The build type selects where the build work runs, not the traversal result.
- **Deferred host operations.** `VK_KHR_deferred_host_operations` lets a host-side AS build be split across multiple host threads. Setting the `deferredOperation` flag routes the host build through a `VkDeferredOperationKHR` handle; the worker-thread count controls how many additional threads join the deferred work. `cpu_ht` passes `workerThreadsCount == 0` (the deferred operation is joined on the calling thread); `cpu_ht_1` through `cpu_ht_8` request 1, 2, 3, 4, and 8 threads; `cpu_ht_max` requests `UINT32_MAX`, which the implementation resolves to its preferred thread count.
- **Watchdog management.** Creating a pipeline with thousands of shader modules is slow on low-clocked CPUs. The test disables the watchdog interval time limit around pipeline creation, then re-enables it, so the large build does not trip the test watchdog.

## Registration Hierarchy

```text
ray_tracing_pipeline.large_shader_set
├── cpu_ht
├── cpu_ht_1
├── cpu_ht_2
├── cpu_ht_3
├── cpu_ht_4
├── cpu_ht_8
├── cpu_ht_max
└── gpu
```

The eight direct children are registered by [createBuildLargeShaderSetTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L655). The first loop registers `gpu` and `cpu_ht` without deferred worker threads (`workerThreadsCount == 0`). The second loop registers the `cpu_ht_*` children for host builds only, each with a named worker-thread count.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| AS build path | `gpu`, `cpu_ht`, `cpu_ht_1`, `cpu_ht_2`, `cpu_ht_3`, `cpu_ht_4`, `cpu_ht_8`, `cpu_ht_max` | Selects the acceleration structure build type and, for host builds, the deferred-host worker-thread count. This is the primary behavioral axis. | [createBuildLargeShaderSetTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L655) |
| Size (shader count) | `64`, `256`, `1024`, `4096` | `size x size` launch grid and callable shader count. `size` is 8, 16, 32, or 64, so the leaf name records `size*size`. Larger sizes stress pipeline creation, SBT size, and group-handle limits. | [sizes array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L576) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L235) |

The test case leaf name is the squared size (`64`, `256`, `1024`, `4096`), so each build-path child contains four leaves, one per size.

## Behavior Parameters

The primary behavioral axis is the acceleration structure build path. Each value is a direct child of `ray_tracing_pipeline.large_shader_set` and selects a different `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_KHR` and worker-thread configuration. The callable shader set, rgen shader, result check, and scene are identical across all values.

### gpu - device-side acceleration structure build

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_DEVICE_KHR`. The build is recorded into the command buffer and executed on the device before the trace. This path never uses deferred host operations and requires no `VK_KHR_deferred_host_operations`. It is the baseline device path: if it fails, the device-side AS build or the shared trace pipeline is suspect.

### cpu_ht - host single-threaded acceleration structure build

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`. The `deferredOperation` flag is `true` but `workerThreadsCount == 0`, so the deferred operation is joined on the calling host thread without additional worker threads. This path requires both `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`. It is the baseline host path against which the multi-threaded deferred paths are compared.

### cpu_ht_1 through cpu_ht_max - host deferred-operation builds with N worker threads

Builds both BLAS and TLAS with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and `deferredOperation == true`, requesting the named worker-thread count. `cpu_ht_1` through `cpu_ht_8` request 1, 2, 3, 4, and 8 threads respectively; `cpu_ht_max` requests `UINT32_MAX`, which the implementation resolves to its preferred thread count. This path requires both `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`. The AS data and expected results are identical to `cpu_ht`; only the threading of the build differs.

## Shader Analysis

The rgen and callable shaders are generated inline in [RayTracingTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L233-L277). The rgen shader is fixed across all sizes; only the `width` literal it embeds changes. The callable shaders are generated per launch cell: one callable shader `call<shaderNdx>` for each `(x, y)`, where `shaderNdx = width * y + x`. Every `shaderNdx` whose value is divisible by 43 gets a block of dummy arithmetic work injected by [generateDummyWork](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L216-L231), which exercises a pipeline containing many callable shaders of non-trivial size rather than a uniform set of one-liners.

Shader code is part of the tested behavior. The rgen `executeCallableEXT(n, 0)` dispatch is what routes each launch cell to its own callable group, and the host compares the per-pixel writes against the same `(width * (y/3) + x) % 199` formula the callable shaders use. A mismatch means the SBT routing or callable execution did not reach the expected group.

This page uses one walkthrough because the rgen dispatch and the callable write together form the single mechanism that every build-path and size leaf validates. The callable shader text varies per cell (the dummy-work injection and the embedded `x`/`y` constants), but its structure is uniform; one representative callable is shown alongside the rgen.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path: `dEQP-VK.ray_tracing_pipeline.large_shader_set.cpu_ht_1.64`.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `cpu_ht_1` | Host deferred-operation build with 1 worker thread. The smallest size keeps the reconstruction readable while still exercising the full rgen-to-callable dispatch and the host build path. |
| `64` | `size == 8`, so the launch grid is 8x8 and there are 64 callable shader groups plus one rgen group in the pipeline. |
| rgen at group 0, `call0` through `call63` at groups 1-64 | One rgen SBT entry and 64 callable SBT entries. |
| `r32ui` 2D result image | One uint per launch cell; each callable writes its cell via `imageStore`. |

#### Purpose

This shader checks that rgen dispatches each launch ID to the callable shader at the matching linear index, and that the callable writes the expected per-pixel value, which is the result every build-path leaf must reproduce.

#### Structural Design

| Step | rgen shader | Result |
|------|------------|--------|
| 1 | Compute `n = width * gl_LaunchIDEXT.y + gl_LaunchIDEXT.x` | One linear index per launch cell, matching the callable SBT layout. |
| 2 | `executeCallableEXT(n, 0)` | Invoke the callable shader at SBT index `n`, passing the `dummy` callable data at location 0. |

| Step | callable shader `call<n>` | Result |
|------|---------------------------|--------|
| 1 | Compute `r = (width * (y/3) + x) % 199` from the embedded `x`, `y` of this cell | A deterministic per-cell value derived from the cell's position. |
| 2 | Optional `generateDummyWork` block when `shaderNdx % 43 == 0` | Extra arithmetic on `color` so some callable shaders are non-trivial. |
| 3 | `imageStore(image0_0, ivec2(gl_LaunchIDEXT.xy), color)` | Write the per-cell result into the 2D storage image. |

#### Shader Code

##### Ray Generation Shader

Reconstructed rgen GLSL, faithful to the source string in [RayTracingTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L237-L251) for `width == 8`. The `updateRayTracingGLSL` wrapper is an identity function, so the emitted source matches the string exactly.

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Outbound callable data passed to the callable shader at location 0.
layout(location = 0) callableDataEXT float dummy;
/// Top-level AS bound at descriptor set 0, binding 1.
layout(set = 0, binding = 1) uniform accelerationStructureEXT topLevelAS;

void main()
{
  /// Linear index of this launch cell; matches the callable SBT entry.
  uint n = 8 * gl_LaunchIDEXT.y + gl_LaunchIDEXT.x;
  /// Invoke the callable shader at SBT index n.
  executeCallableEXT(n, 0);
}
```

##### Callable Shader

Reconstructed callable GLSL for cell `(x=1, y=0)`, faithful to the per-cell generation loop in [RayTracingTestCase::initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L254-L276) for `width == 8`. `shaderNdx == 1`, and `1 % 43 != 0`, so no dummy work is injected. Cells where `shaderNdx % 43 == 0` get the extra arithmetic block from [generateDummyWork](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L216-L231); the rest share this structure with only the embedded `x`, `y`, and `r` constants differing.

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
/// Inbound callable data from rgen at location 0.
layout(location = 0) callableDataInEXT float dummy;
/// 2D storage image; one uint per launch cell. Cleared to (5,5,5,255) before the trace.
layout(r32ui, set = 0, binding = 0) uniform uimage2D image0_0;
void main()
{
  /// Per-cell value derived from this cell's (x, y). Here x=1, y=0, width=8.
  uint r = (8 * 0 + 1) % 199;
  uvec4 color = uvec4(r,0,0,1);
  imageStore(image0_0, ivec2(gl_LaunchIDEXT.xy), color);
}
```

#### Additional Info

- The callable shader shown is the non-dummy variant. For cells where `shaderNdx % 43 == 0`, [generateDummyWork](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L216-L231) appends up to 255 iterations of integer arithmetic on `color.b` and `color.g` before the `imageStore`, so the pipeline contains callable shaders of varying compiled size. This is why the test is a "large shader set" stress rather than a uniform callable test.
- The rgen `width` literal is the only thing that changes across sizes: `8`, `16`, `32`, or `64`. The dispatch structure (`n = width * y + x; executeCallableEXT(n, 0)`) is identical, so the larger sizes scale the callable group count and SBT size without changing rgen logic.
- The `topLevelAS` is bound but never traversed by a ray in this test; rgen calls a callable shader directly rather than tracing a ray. The AS exists so the descriptor set matches the pipeline layout the trace command expects.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Size | The rgen `width` literal changes to 8, 16, 32, or 64, and the number of generated callable shaders scales to `width*width`. The rgen dispatch structure is unchanged. | [rgen generation](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L237-L251), [callable generation loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L254-L276) |
| Dummy work | Every cell with `shaderNdx % 43 == 0` gets the `generateDummyWork` arithmetic block; other cells do not. This varies callable shader size within one pipeline. | [dummyWork condition](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L258), [generateDummyWork](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L216-L231) |
| AS build path | The rgen and callable shaders are identical for `gpu`, `cpu_ht`, and all `cpu_ht_*` values. The build path differs only on the host side. | [createBuildLargeShaderSetTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L655) |

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
; Bound: 31
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %dummy %topLevelAS
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %n "n"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %dummy "dummy"
               OpName %topLevelAS "topLevelAS"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 1
               OpDecorate %topLevelAS DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_8 = OpConstant %uint 8
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_0 = OpConstant %uint 0
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
      %float = OpTypeFloat 32
%_ptr_CallableDataKHR_float = OpTypePointer CallableDataKHR %float
      %dummy = OpVariable %_ptr_CallableDataKHR_float CallableDataKHR
         %28 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_28 = OpTypePointer UniformConstant %28
 %topLevelAS = OpVariable %_ptr_UniformConstant_28 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
          %n = OpVariable %_ptr_Function_uint Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %16 = OpLoad %uint %15
         %17 = OpIMul %uint %uint_8 %16
         %19 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %20 = OpLoad %uint %19
         %21 = OpIAdd %uint %17 %20
               OpStore %n %21
         %22 = OpLoad %uint %n
               OpExecuteCallableKHR %22 %dummy
               OpReturn
               OpFunctionEnd
```

</details>

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rcall`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 33
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint CallableKHR %main "main" %image0_0 %gl_LaunchIDEXT %dummy
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %r "r"
               OpName %color "color"
               OpName %image0_0 "image0_0"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %dummy "dummy"
               OpDecorate %image0_0 Binding 0
               OpDecorate %image0_0 DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_1 = OpConstant %uint 1
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
     %uint_0 = OpConstant %uint 0
         %16 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_16 = OpTypePointer UniformConstant %16
   %image0_0 = OpVariable %_ptr_UniformConstant_16 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
      %float = OpTypeFloat 32
%_ptr_IncomingCallableDataKHR_float = OpTypePointer IncomingCallableDataKHR %float
      %dummy = OpVariable %_ptr_IncomingCallableDataKHR_float IncomingCallableDataKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
          %r = OpVariable %_ptr_Function_uint Function
      %color = OpVariable %_ptr_Function_v4uint Function
               OpStore %r %uint_1
         %13 = OpLoad %uint %r
         %15 = OpCompositeConstruct %v4uint %13 %uint_0 %uint_0 %uint_1
               OpStore %color %15
         %19 = OpLoad %16 %image0_0
         %24 = OpLoad %v3uint %gl_LaunchIDEXT
         %25 = OpVectorShuffle %v2uint %24 %24 0 1
         %28 = OpBitcast %v2int %25
         %29 = OpLoad %v4uint %color
               OpImageWrite %19 %28 %29 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

### Scene construction

- The host builds one BLAS with `geometriesGroupCount == 1` geometry holding `squaresGroupCount == size*size` triangle primitives. Each primitive covers one pixel cell of the `size x size` image, placed by a deterministic walk (`startPos` advanced by `(13 * (n+1)) % (size*size)`) [initBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L305-L352).
- A TLAS instances that single BLAS with an identity transform [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L284-L303). The AS is a placeholder for the descriptor set; no ray is traced against it.

### Pipeline creation and SBT

- The pipeline has one rgen group and `size*size` callable groups. [makePipeline](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L86-L106) adds the rgen at group 0 and each `call<groupNdx>` callable at group `1 + groupNdx`.
- Because creating a pipeline with thousands of shader modules is slow, the watchdog interval time limit is disabled before `makePipeline` and re-enabled after it [watchdog disable/enable](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L387-L393).
- Two SBT regions are created: a rgen SBT with one entry, and a callable SBT with `callableShaderCount` entries, both using the device's `shaderGroupHandleSize` and `shaderGroupBaseAlignment` [SBT creation](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L394-L405). The miss and hit SBT regions are zeroed.

### Build path execution

- The case's `buildType` and `deferredOperation` are set on the BLAS and TLAS, and the `workerThreadsCount` is passed into `makePipeline` for deferred-operation pipeline creation [runTest build setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L354-L405).
- For multi-threaded deferred cases (`cpu_ht_*`, where `workerThreadsCount != 0`), the instance runs the test twice: once single-threaded (`runTest(0)`) and once with the case's worker-thread count (`runTest(workerThreadsCount)`), summing the failures from both [iterateWithWorkers](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L546-L555). The `workerThreadsCount == 0` cases (`gpu`, `cpu_ht`) run once single-threaded [iterateNoWorkers](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L538-L544).

### Trace and result copyback

- The result image is a 2D `r32ui` storage image sized to `size x size`. It is cleared to `(5,5,5,255)` and transitioned to `GENERAL` before the trace [image setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L407-L437).
- `cmdTraceRays` launches `size x size x 1` rays. Each rgen invocation calls `executeCallableEXT(n, 0)`, and the callable writes its per-cell value into the image [trace dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L474-L475).
- After the trace, a `SHADER_WRITE` -> `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` -> `HOST_READ` barrier move the image into a host-visible buffer [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L477-L483).

### Per-pixel result check

- The host scans every pixel. The expected value is `(width * (y/3) + x) % 199`, the same formula the callable shaders embed [validateBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L518-L536).
- Pass condition: `failures == 0` [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L557-L567). For deferred-operation cases, the single-threaded and multi-threaded runs must both pass.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `gpu` | Device-side AS build (BLAS/TLAS) did not produce a usable structure, or the device build path's shared large pipeline or callable SBT is broken. |
| `cpu_ht` | Host single-threaded AS build did not produce a correct structure, or `accelerationStructureHostCommands` host build path has a correctness bug independent of threading. |
| `cpu_ht_1` through `cpu_ht_8` | Host deferred-operation build with the named worker-thread count did not produce a correct structure, or the single-threaded vs multi-threaded runs disagree, pointing at deferred-operation work partitioning or thread-join synchronization for that thread count. |
| `cpu_ht_max` | Host deferred-operation build with the implementation's preferred (max) thread count did not produce a correct structure, or the single-threaded vs max-thread runs disagree, pointing at deferred-operation scaling to many threads. |

All leaves share the large pipeline creation, the callable SBT, the scene, and the per-pixel result check, so a failure common to all build-path values points at shared infrastructure (shader generation, SBT handles, image copyback, expected-value rule) rather than a build-path-specific issue. A failure that appears only at the largest size (4096) points at a limit or scaling issue in pipeline creation or SBT size.

### Cause Analysis

#### Device-side build correctness failure

**Possible failure symptoms:** A `gpu` leaf failure where the corresponding `cpu_ht` leaf with the same size passes. The result image has mismatched pixels: cells that should hold their `(width * (y/3) + x) % 199` value hold the clear value or a wrong callable's value, and the failure count is nonzero.

**Possible implementation causes:** The `gpu` path records the BLAS and TLAS builds into the command buffer and the device executes them. A grounded investigation should check whether the device build completed and was made visible to the trace (the build and trace are in the same command buffer), and whether the large pipeline and callable SBT were created correctly for the device path. If `gpu` and `cpu_ht` both fail at the same size, the cause is shared infrastructure, not the device build path. If only `gpu` fails and the host path passes, source-level investigation is needed.

#### Host single-threaded build correctness failure

**Possible failure symptoms:** A `cpu_ht` leaf failure where the corresponding `gpu` leaf passes, or where `cpu_ht` and all `cpu_ht_*` leaves fail together. Mismatched pixels in the result image with a nonzero failure count.

**Possible implementation causes:** The `cpu_ht` path builds BLAS and TLAS on the host with `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` and `workerThreadsCount == 0`, so the deferred operation is joined on the calling host thread without additional worker threads. It requires the `accelerationStructureHostCommands` feature. A grounded investigation should check whether the host build respected the same geometry data and instance configuration as the device path, and whether the host-built structure was made available to the device trace (the host-built TLAS handle is bound via the descriptor set before the trace). The spec ties host builds to `accelerationStructureHostCommands`; if that feature is reported but the host build is broken, the cause is in the host build implementation. If `cpu_ht` passes but a `cpu_ht_*` leaf fails, the cause is multi-threaded-join-specific.

#### Deferred-host-operation threading failure

**Possible failure symptoms:** A `cpu_ht_N` or `cpu_ht_max` leaf failure where the `cpu_ht` leaf with the same size passes. Mismatched pixels with a nonzero failure count. Because multi-threaded cases run both single-threaded and multi-threaded and sum failures, the failure may come from the multi-threaded run only, isolating the threading.

**Possible implementation causes:** The `cpu_ht_*` paths use deferred operation with N worker threads (where `cpu_ht` uses 0). The implementation must partition the host build across the worker threads and join them so the completed structure is visible before the trace. A grounded investigation should check whether the deferred-operation join completed for the failing thread count, whether the partitioning produced a structure equivalent to the single-threaded build, and whether any per-thread scratch or allocation state leaked between threads. The spec states deferred host operations may be concurrent and the implementation must complete them before returning. If only some thread counts fail, the cause is thread-count-specific partitioning or join logic, and source-level investigation of the deferred-operation join path is needed.

#### Large pipeline or SBT scaling failure

**Possible failure symptoms:** Failures that appear only at the largest size (4096 callable groups) across one or more build paths, or a failure that grows with size. Cells may hold wrong values (wrong callable invoked) or the clear value (callable did not run).

**Possible implementation causes:** This test creates a pipeline with up to 4097 shader groups (1 rgen plus 4096 callable) and a callable SBT with up to 4096 entries. A grounded investigation should check whether the implementation respects the `maxCallableShaderRecords` or related SBT size limits, whether the SBT was allocated with the correct `shaderGroupHandleSize` and `shaderGroupBaseAlignment`, and whether large pipeline creation correctly assigned each callable group handle to its SBT index. The rgen dispatches by linear index `n`, so a wrong handle at index `n` routes the launch cell to the wrong callable. If smaller sizes pass and only 4096 fails, the cause is a scaling or limit issue in pipeline or SBT construction, and source-level investigation is needed.

#### Shared infrastructure failure

**Possible failure symptoms:** All build-path values for a given size fail with the same pixel pattern, regardless of whether the build ran on the device, the host, or the host with threads.

**Possible implementation causes:** The shader generation, pipeline creation, callable SBT, result image clear and copyback, and the expected-value rule are identical across all build paths. A failure common to all paths points at this shared setup. A grounded investigation should check whether the per-cell callable shaders were generated with the correct embedded `x`, `y`, and `r` constants matching the `validateBuffer` formula, whether the dummy-work injection corrupted the `imageStore` write for the `shaderNdx % 43 == 0` cells, whether the rgen `executeCallableEXT(n, 0)` index matches the callable SBT layout, and whether the per-pixel expected-value rule in `validateBuffer` matches the shader formula. Source-level inspection of `initPrograms` and `validateBuffer` is needed to confirm the formula correspondence.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with the `rayTracingPipeline` and `accelerationStructure` feature bits set. If `accelerationStructure` is not set, the test throws `TestError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L191-L205).
- Host builds (`cpu_ht` and all `cpu_ht_*`) additionally require `VK_KHR_deferred_host_operations` and `accelerationStructureHostCommands`; otherwise the test throws `NotSupportedError` [host build feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L207-L213). The `gpu` path does not require these.
- At instance time, the test checks ray tracing property limits: `maxPrimitiveCount` must cover `squaresGroupCount`, and the estimated memory allocation count must stay under `maxMemoryAllocationCount`. Any shortfall throws `NotSupportedError` [checkSupportInInstance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L495-L516).

### Design-based pruning

- The `cpu_ht_*` children are registered for host builds only: the second registration loop skips any build type that is not `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR` [host-only filter](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L621-L622). So there is no `gpu_1` or `gpu_max` child; device builds only use the `gpu` child with no worker threads.
- The size matrix is fixed at 8, 16, 32, 64 for every build path; there is no per-path size skip, unlike the sibling `build` family which skips large device sizes. Every build path runs all four sizes [sizes array](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L576).
- `geometriesGroupCount` and `instancesGroupCount` are fixed at 1 for all cases; only `squaresGroupCount` scales with `size*size`. This keeps the AS small so the stress stays on the callable shader set, not on AS geometry count [CaseDef fill](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L599-L608).

## Key Takeaways

- The `large_shader_set` family isolates the acceleration structure build path as the behavioral axis: device build (`gpu`), host deferred-operation build with 0 worker threads (`cpu_ht`), and host deferred-operation build with 1, 2, 3, 4, 8, or max worker threads (`cpu_ht_*`). The callable shader set, rgen shader, and result check are identical across all paths.
- The size axis scales the callable shader count from 64 to 4096, stressing large pipeline creation, callable SBT size, and group-handle limits. The rgen dispatch structure is unchanged across sizes; only the embedded `width` literal and the number of callable shaders change.
- The dummy-work injection (`shaderNdx % 43 == 0`) makes the pipeline a genuine large shader set: some callable shaders carry hundreds of arithmetic lines, so the test exercises non-uniform callable shader sizes rather than a set of identical one-liners.
- The watchdog is explicitly managed around pipeline creation, since compiling and linking thousands of shader modules is slow on low-clocked CPUs.
- A failure isolated to one build path points at that path's build or synchronization correctness; a failure common to all paths points at shared shader, SBT, or check infrastructure; a failure only at the largest size points at a pipeline or SBT scaling limit. See `## Failure Meaning` for the per-path cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseDef` struct | [vktRayTracingBuildLargeTests.cpp#L56-L66](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L56-L66) | Per-case parameters including build type, deferred-operation flag, and worker-thread count |
| `generateDummyWork` | [vktRayTracingBuildLargeTests.cpp#L216-L231](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L216-L231) | Injects dummy arithmetic into `shaderNdx % 43 == 0` callable shaders |
| `initPrograms` | [vktRayTracingBuildLargeTests.cpp#L233-L277](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L233-L277) | rgen and per-cell callable shader generation |
| `makePipeline` | [vktRayTracingBuildLargeTests.cpp#L86-L106](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L86-L106) | Adds rgen plus N callable groups to the ray tracing pipeline |
| `checkSupport` | [vktRayTracingBuildLargeTests.cpp#L191-L205](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L191-L205) | Feature gates for acceleration structure, ray tracing pipeline, deferred host operations |
| `initBottomAccelerationStructure` | [vktRayTracingBuildLargeTests.cpp#L305-L352](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L305-L352) | Deterministic primitive placement for the placeholder AS |
| `initTopAccelerationStructure` | [vktRayTracingBuildLargeTests.cpp#L284-L303](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L284-L303) | TLAS instance setup |
| `runTest` | [vktRayTracingBuildLargeTests.cpp#L354-L493](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L354-L493) | Watchdog-managed pipeline creation, SBT, trace dispatch, and result copyback |
| `checkSupportInInstance` | [vktRayTracingBuildLargeTests.cpp#L495-L516](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L495-L516) | Runtime property-limit and allocation-count pruning |
| `validateBuffer` | [vktRayTracingBuildLargeTests.cpp#L518-L536](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L518-L536) | Per-pixel expected-value rule |
| `iterate` / `iterateWithWorkers` | [vktRayTracingBuildLargeTests.cpp#L538-L567](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L538-L567) | Pass/fail condition and the single-threaded plus multi-threaded run for deferred cases |
| `createBuildLargeShaderSetTests` | [vktRayTracingBuildLargeTests.cpp#L571-L655](../../../modules/vulkan/ray_tracing/vktRayTracingBuildLargeTests.cpp#L571-L655) | Registration of the eight build-path direct children and the four-size matrix |
