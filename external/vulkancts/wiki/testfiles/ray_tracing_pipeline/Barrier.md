## Overview

**Core question:** Does a `vkCmdPipelineBarrier` correctly synchronize a writer stage and a reader stage when at least one of them is a ray tracing shader stage, across the three resource types `UNIFORM_BUFFER`, `STORAGE_BUFFER`, and `STORAGE_IMAGE`, and across the two barrier shapes `vkMemoryBarrier` and `vkBufferMemoryBarrier`/`vkImageMemoryBarrier`?

- [vktRayTracingBarrierTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp) implements and registers the `barrier` test family under the `ray_tracing_pipeline` test category.
- Three direct children (`ubo`, `ssbo`, `simg`) select the barrier resource type. Each child has two intermediate nodes (`memory_barrier`, `specific_barrier`) that select the barrier shape. Each intermediate node has test case leaves named `from_<writer>_to_<reader>` covering ten stages: `host`, `xfer`, `rgen`, `isec`, `ahit`, `chit`, `miss`, `call`, `comp`, `frag`.
- The core idea: a writer stage produces `1024` values (`id1d + 2048`) into a barrier resource, a pipeline barrier synchronizes the write, and a reader stage reads those values back into a host-visible verification buffer. The host checks every entry equals `2048 + i`.
- The registration loop skips combinations that do not involve any ray tracing stage, that would require host access to a storage image, or that would require a shader write to a UBO. The total registered case count is `336`.

## Background Knowledge

- **Pipeline barrier execution and memory dependencies.** A `vkCmdPipelineBarrier` establishes an execution dependency from source pipeline stages to destination pipeline stages and a memory dependency from source access flags to destination access flags. The execution dependency orders work; the memory dependency performs an availability operation that flushes source-stage writes to device memory and a visibility operation that makes those writes observable by destination-stage reads. Without the memory dependency, the destination stage can observe stale or partial data even when execution ordering holds.
- **Two barrier shapes.** `vkMemoryBarrier` (`BarrierType::GENERAL`) is a global barrier with no resource handle; it flushes and makes visible every prior write matching the source access mask. `vkBufferMemoryBarrier` and `vkImageMemoryBarrier` (`BarrierType::SPECIFIC`) are scoped to a specific buffer or image subresource range. The image barrier also performs a layout transition via its `oldLayout`/`newLayout` pair.
- **Single ray tracing pipeline stage.** Vulkan represents every ray tracing shader stage (raygen, intersection, any-hit, closest-hit, miss, callable) with the single `VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR` flag. The test's [`getPipelineStage`](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L113-L145) helper collapses all six stages to this one bit, so the host barrier always names the same source or destination stage for any ray tracing case.
- **Access flag mapping.** Shader writer stages use `VK_ACCESS_SHADER_WRITE_BIT`. HOST uses `VK_ACCESS_HOST_WRITE_BIT`; TRANSFER uses `VK_ACCESS_TRANSFER_WRITE_BIT`. On the reader side, UBO reads use `VK_ACCESS_UNIFORM_READ_BIT`; SSBO and storage image reads use `VK_ACCESS_SHADER_READ_BIT`; HOST uses `VK_ACCESS_HOST_READ_BIT`; TRANSFER uses `VK_ACCESS_TRANSFER_READ_BIT`. The mapping lives in [`getWriterAccessFlag`](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L147-L175) and [`getReaderAccessFlag`](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L177-L206).
- **Verification buffer readback.** Every reader stage writes the value it observed into a host-visible `verificationBuffer` (std430, `1024` uint32_t values). The host scans this buffer after submission. This indirection lets one host check cover every reader stage, including ray tracing, compute, fragment, transfer, and host.

## Registration Hierarchy

```text
ray_tracing_pipeline.barrier
├── simg
├── ssbo
└── ubo
```

Each direct child is a resource-type group containing two barrier-type intermediate nodes (`memory_barrier`, `specific_barrier`). Each barrier-type node contains test case leaves named `from_<writer>_to_<reader>`. The ten stage tokens are `host`, `xfer`, `rgen`, `isec`, `ahit`, `chit`, `miss`, `call`, `comp`, `frag`. The registration loop and pruning rules are in [`createBarrierTests`](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1750-L1826).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Resource type | `ubo`, `ssbo`, `simg` | Selects `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`, `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`, or `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`. Changes the descriptor type, the reader access flag (`UNIFORM_READ` vs `SHADER_READ`), the SPECIFIC barrier shape (buffer vs image), and the set of legal stage combinations. | [resourceTypes](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1755-L1763) |
| Barrier type | `memory_barrier`, `specific_barrier` | Selects `BarrierType::GENERAL` (`vkMemoryBarrier`) or `BarrierType::SPECIFIC` (`vkBufferMemoryBarrier` or `vkImageMemoryBarrier`). The SPECIFIC image barrier also transitions the image layout. | [barrierTypes](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1775-L1782) |
| Writer stage | `host`, `xfer`, `rgen`, `isec`, `ahit`, `chit`, `miss`, `call`, `comp`, `frag` | The stage that produces the barrier resource data. Each stage uses a different pipeline (ray tracing, compute, graphics) or a host/transfer fill. | [stageList](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1765-L1773) |
| Reader stage | `host`, `xfer`, `rgen`, `isec`, `ahit`, `chit`, `miss`, `call`, `comp`, `frag` | The stage that reads the barrier resource and writes the verification buffer. The reader pipeline is independent of the writer pipeline. | [stageList](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1765-L1773) |
| Buffer element count | fixed `1024` | `kBufferElements`. Each writer invocation produces one uint32_t; the 32x32 launch gives 1024 invocations. | [kBufferElements](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L58) |
| Values offset | fixed `2048` | `kValuesOffset`. The writer computes `val = id1d + 2048`; the host checks `verificationBuffer[i] == 2048 + i`. | [kValuesOffset](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L61) |
| Launch / dispatch size | fixed `32 x 32` | `kImageDim`. Ray tracing cases use `cmdTraceRaysKHR(32, 32, 1)`; compute cases use `cmdDispatch(32, 32, 1)`; fragment cases draw a full-screen quad over a 32x32 viewport. | [kImageDim](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L62) |

## Behavior Parameters

The primary behavioral axis is the resource type: the direct child of `barrier`. It is the primary axis because it changes the descriptor type, the SPECIFIC barrier shape, the reader access flag, and the set of legal stage combinations simultaneously. The barrier type is a secondary axis documented in the table above; it changes the barrier shape but not the resource semantics. The writer/reader stage pair is the leaf generator and is covered in the table above.

### ubo — uniform buffer, HOST or TRANSFER writer only

The barrier resource is a std140 `UNIFORM_BUFFER` with 1024 uint32_t slots. UBOs cannot be written from shaders, so the registration loop skips every UBO case whose writer is not HOST or TRANSFER. The remaining cases pair a HOST or TRANSFER writer with a ray tracing reader (`rgen`, `isec`, `ahit`, `chit`, `miss`, `call`), because at least one stage must be a ray tracing stage and those are the only readers that can legally read a UBO under the test's stage set. The reader access flag is `VK_ACCESS_UNIFORM_READ_BIT`, which is the flag the test's `getReaderAccessFlag` returns for UBO reads. The SPECIFIC barrier uses a `vkBufferMemoryBarrier` scoped to the UBO. The UBO group registers 24 cases (12 per barrier type).

### ssbo — storage buffer, all stage combinations

The barrier resource is a std140 `STORAGE_BUFFER` with 1024 uint32_t slots. SSBOs allow shader writes, so every writer/reader stage combination is legal as long as at least one stage is a ray tracing stage. This includes HOST writer or HOST reader cases where the other stage is ray tracing, and shader-to-shader cases. The writer access flag is `VK_ACCESS_SHADER_WRITE_BIT` for shader writers; the reader access flag is `VK_ACCESS_SHADER_READ_BIT`. The SPECIFIC barrier uses a `vkBufferMemoryBarrier` scoped to the SSBO. The SSBO group registers 168 cases (84 per barrier type) and is the largest of the three resource types.

### simg — storage image, no HOST writer or reader

The barrier resource is a 32x32 `VK_FORMAT_R32_UINT` storage image. The image is allocated with `MemoryRequirement::Any` (not host-visible), so the registration loop skips every case whose writer or reader is HOST. The writer uses `imageStore`; the reader uses `imageLoad` (shader readers) or `cmdCopyImageToBuffer` (TRANSFER reader). The SPECIFIC barrier uses a `vkImageMemoryBarrier` that also transitions the image layout: the writer leaves the image in `VK_IMAGE_LAYOUT_GENERAL` (shader writers) or `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (TRANSFER writer with SPECIFIC barrier), and the barrier transitions it to `VK_IMAGE_LAYOUT_GENERAL` (shader readers) or `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` (TRANSFER reader). The simg group registers 144 cases (72 per barrier type) and is the only group that exercises image layout transitions.

## Shader Analysis

The shaders are inline GLSL strings emitted by `BarrierTestCase::initPrograms` with `SPIRV_VERSION_1_4` build options. Each case generates a writer shader and a reader shader. The shader body depends on the stage and resource type. For ray tracing writer or reader stages other than RAYGEN, an additional `writer_aux_rgen` or `reader_aux_rgen` is generated from the shared helper [`getCommonRayGenerationShader`](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138), which fires one downward ray per launch invocation against the bound TLAS. For the CALLABLE stage, the aux rgen is generated inline and calls `executeCallableEXT(0, 0)`.

One walkthrough covers the reader closest-hit shader for the `from_rgen_to_chit` SSBO case. This shader is the consumer side of the barrier: it reads the value the writer produced and writes it to the verification buffer. Its correct execution depends on the barrier making the writer's stores visible. The writer rgen shader is structurally simpler (same `id1d` computation, same SSBO declaration, one store instead of a load plus a store) and is described in the Additional Info section.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.barrier.ssbo.specific_barrier.from_rgen_to_chit
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ssbo` | The barrier resource is a std140 storage buffer with 1024 uint32_t slots. |
| `specific_barrier` | The main barrier is a `vkBufferMemoryBarrier` scoped to the SSBO, with source `SHADER_WRITE` and destination `SHADER_READ`. |
| `from_rgen` | The writer is a raygen shader that writes `ssbo.data[id1d] = id1d + 2048` directly. No ray is traced by the writer. |
| `to_chit` | The reader is a closest-hit shader. An aux rgen fires a downward ray into the default BLAS; the closest-hit shader reads `ssbo.data[id1d]` and writes `verificationBuffer.data[id1d]`. |

#### Purpose

This case checks that a `vkBufferMemoryBarrier` with source stage `RAY_TRACING_SHADER_BIT_KHR`, source access `SHADER_WRITE`, destination stage `RAY_TRACING_SHADER_BIT_KHR`, and destination access `SHADER_READ` makes the writer rgen's SSBO stores visible to the reader closest-hit shader's SSBO load. If the barrier's availability or visibility operation is missing or wrong, the closest-hit load returns stale or zero data, and the host verification fails.

#### Structural Design

| Step | Stage | Action | Resource effect |
|------|-------|--------|-----------------|
| 1 | writer rgen | Compute `id1d = gl_LaunchIDEXT.y * 32 + gl_LaunchIDEXT.x`; store `ssbo.data[id1d] = id1d + 2048` | SSBO filled with 1024 values |
| 2 | host (barrier) | `vkCmdPipelineBarrier` with `vkBufferMemoryBarrier` on the SSBO | SSBO writes flushed and made visible |
| 3 | reader aux rgen | Fire one downward ray per launch invocation into the default BLAS | Ray hits the BLAS, closest-hit shader runs |
| 4 | reader chit | Load `val = ssbo.data[id1d]`; store `verificationBuffer.data[id1d] = val` | Verification buffer filled with observed values |
| 5 | host (barrier) | `vkCmdPipelineBarrier` with `vkBufferMemoryBarrier` on the verification buffer | Verification buffer writes flushed for host read |
| 6 | host | Invalidate verification buffer; check `verificationBuffer[i] == 2048 + i` for every `i` | Pass or fail |

#### Shader Code

Reconstructed reader closest-hit shader (set 0, binding 0 is the SSBO; binding 2 is the verification buffer; binding 1 is reserved for the TLAS, which the aux rgen uses):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require

/// Incoming ray payload. Unused by the barrier test; the reader chit shader
/// communicates through the verification buffer, not through the payload.
layout(location = 0) rayPayloadInEXT vec3 unusedPayload;

/// Hit attribute from the default BLAS. Unused.
hitAttributeEXT vec3 attribs;

/// Barrier resource (set 0, binding 0): std140 SSBO with 1024 uint32_t slots.
/// The writer rgen filled this with id1d + 2048 before the barrier.
layout(set = 0, binding = 0, std140) buffer ssbodef { uint data[1024]; } ssbo;

/// Verification buffer (set 0, binding 2): std430 SSBO with 1024 uint32_t slots.
/// Binding 2 because the reader is a ray tracing stage and binding 1 is reserved
/// for the acceleration structure. The host reads this back after submission.
layout(set = 0, binding = 2) buffer vssbodef { uint data[1024]; } verificationBuffer;

void main()
{
    /// Linear launch index. The 32x32 launch gives id1d in [0, 1024).
    const uint  id1d = gl_LaunchIDEXT.y * 32 + gl_LaunchIDEXT.x;
    const ivec2 id2d = ivec2(gl_LaunchIDEXT.xy);

    /// Read the value the writer produced. If the barrier did not make the
    /// writer's stores visible, this load returns stale or zero data.
    const uint  val  = ssbo.data[id1d];

    /// Save the observed value for host readback. The host checks
    /// verificationBuffer[i] == 2048 + i for every i.
    verificationBuffer.data[id1d] = val;
}
```

#### Additional Info

- The writer rgen shader for the same case is structurally simpler: it declares the same SSBO at binding 0, computes the same `id1d`, and stores `ssbo.data[id1d] = id1d + 2048`. It does not trace a ray. Writer rgen source: [vktRayTracingBarrierTests.cpp#L486-L496](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L486-L496).
- The reader aux rgen is the shared helper [`getCommonRayGenerationShader`](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138). It fires one ray per launch invocation from `((x + 0.5) / width, (y + 0.5) / height, 0.0)` in direction `(0, 0, -1)` with `tmax = 9.0`. The default BLAS provided by `makeBottomLevelAccelerationStructure()` guarantees a hit.
- The `id2d` local variable is declared in every ray tracing shader by the shared `rayTracingIds` string but is unused for SSBO cases (it is only used for storage image `imageStore`/`imageLoad` coordinate construction). glslang keeps it in the SPIR-V as an unused local.
- The std140 SSBO has `ArrayStride 16` (one uint32_t per UVec4 slot). The std430 verification buffer has `ArrayStride 4` (compact uint32_t array). The SPIR-V decorations reflect this difference.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this walkthrough | Evidence |
|---------------------|--------------------------------------------|----------|
| Resource type | Swaps the barrier resource declaration: `buffer ssbodef` (SSBO), `uniform ubodef` (UBO), or `uniform uimage2D simage` (storage image). The read/write statements change accordingly. | [writerResourceDecl / readerResourceDecl](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L440-L472) |
| Writer stage | Swaps the writer shader stage and body. RAYGEN writes directly; other ray tracing stages use an aux rgen plus the writer shader in the hit/miss/callable stage; COMPUTE and FRAGMENT use their own pipelines; HOST and TRANSFER use host fills and copies. | [writer shader generation](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L484-L620) |
| Reader stage | Swaps the reader shader stage and body. Same structure as the writer but with a read-plus-save statement and an extra verification buffer declaration. | [reader shader generation](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L626-L764) |
| Barrier type | Does not change the shader. Changes the host-side barrier shape: `vkMemoryBarrier` (GENERAL) vs `vkBufferMemoryBarrier`/`vkImageMemoryBarrier` (SPECIFIC). | [main barrier recording](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1547-L1592) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rchit`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 54
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint ClosestHitKHR %main "main" %gl_LaunchIDEXT %ssbo %verificationBuffer %unusedPayload %attribs
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %id1d "id1d"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %id2d "id2d"
               OpName %val "val"
               OpName %ssbodef "ssbodef"
               OpMemberName %ssbodef 0 "data"
               OpName %ssbo "ssbo"
               OpName %vssbodef "vssbodef"
               OpMemberName %vssbodef 0 "data"
               OpName %verificationBuffer "verificationBuffer"
               OpName %unusedPayload "unusedPayload"
               OpName %attribs "attribs"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %_arr_uint_uint_1024 ArrayStride 16
               OpDecorate %ssbodef Block
               OpMemberDecorate %ssbodef 0 Offset 0
               OpDecorate %ssbo Binding 0
               OpDecorate %ssbo DescriptorSet 0
               OpDecorate %_arr_uint_uint_1024_0 ArrayStride 4
               OpDecorate %vssbodef Block
               OpMemberDecorate %vssbodef 0 Offset 0
               OpDecorate %verificationBuffer Binding 2
               OpDecorate %verificationBuffer DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
    %uint_32 = OpConstant %uint 32
     %uint_0 = OpConstant %uint 0
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
     %v2uint = OpTypeVector %uint 2
  %uint_1024 = OpConstant %uint 1024
%_arr_uint_uint_1024 = OpTypeArray %uint %uint_1024
    %ssbodef = OpTypeStruct %_arr_uint_uint_1024
%_ptr_StorageBuffer_ssbodef = OpTypePointer StorageBuffer %ssbodef
       %ssbo = OpVariable %_ptr_StorageBuffer_ssbodef StorageBuffer
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_arr_uint_uint_1024_0 = OpTypeArray %uint %uint_1024
   %vssbodef = OpTypeStruct %_arr_uint_uint_1024_0
%_ptr_StorageBuffer_vssbodef = OpTypePointer StorageBuffer %vssbodef
%verificationBuffer = OpVariable %_ptr_StorageBuffer_vssbodef StorageBuffer
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_IncomingRayPayloadKHR_v3float = OpTypePointer IncomingRayPayloadKHR %v3float
%unusedPayload = OpVariable %_ptr_IncomingRayPayloadKHR_v3float IncomingRayPayloadKHR
%_ptr_HitAttributeKHR_v3float = OpTypePointer HitAttributeKHR %v3float
    %attribs = OpVariable %_ptr_HitAttributeKHR_v3float HitAttributeKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
       %id1d = OpVariable %_ptr_Function_uint Function
       %id2d = OpVariable %_ptr_Function_v2int Function
        %val = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %15 = OpLoad %uint %14
         %17 = OpIMul %uint %15 %uint_32
         %19 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %20 = OpLoad %uint %19
         %21 = OpIAdd %uint %17 %20
               OpStore %id1d %21
         %27 = OpLoad %v3uint %gl_LaunchIDEXT
         %28 = OpVectorShuffle %v2uint %27 %27 0 1
         %29 = OpBitcast %v2int %28
               OpStore %id2d %29
         %37 = OpLoad %uint %id1d
         %39 = OpAccessChain %_ptr_StorageBuffer_uint %ssbo %int_0 %37
         %40 = OpLoad %uint %39
               OpStore %val %40
         %45 = OpLoad %uint %id1d
         %46 = OpLoad %uint %val
         %47 = OpAccessChain %_ptr_StorageBuffer_uint %verificationBuffer %int_0 %45
               OpStore %47 %46
               OpReturn
               OpFunctionEnd
```

</details>## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ubo` | HOST or TRANSFER writer data was not made visible to the ray tracing reader stage; or the buffer-memory barrier used the wrong source/destination access mask; or the UBO read used `SHADER_READ` semantics where `UNIFORM_READ` was required; or the host fill did not flush before the barrier. |
| `ssbo` | Writer shader writes were not flushed (availability) or not made visible to the reader stage; or the buffer-memory barrier named the wrong pipeline stage; or for HOST reader, the host-read barrier was missing or used the wrong access mask; or for ray tracing reader, the closest-hit/any-hit/intersection shader did not run because the TLAS/BLAS setup was wrong (the read observed zeros). |
| `simg` | Image layout transition between writer and reader was wrong or missing; or the image-memory barrier's `oldLayout`/`newLayout` pair did not match the actual writer-final layout; or the writer's `imageStore` was not made visible to the reader's `imageLoad`; or for TRANSFER reader, the image was not transitioned to `TRANSFER_SRC_OPTIMAL`; or for TRANSFER writer, the image was not transitioned to `TRANSFER_DST_OPTIMAL` or `GENERAL` before the copy. |

All three resource types share the same verification path (verificationBuffer to host scan), so a shared infrastructure failure (verificationBuffer missing its host-read barrier, host invalidation skipped, wrong element count) would surface identically across resource types and is distinguishable from a resource-type-specific failure by whether the mismatch appears in one resource type or all three.

### Cause Analysis

#### UBO reader observed stale or zero data

**Possible failure symptoms:** For `ubo` cases, the host verification scan finds `verificationBuffer[i]` equals `0` or a pre-fill value instead of `2048 + i`. The mismatch appears in UBO cases only; SSBO and simg cases with the same stage pair pass.

**Possible implementation causes:** UBO reads use `VK_ACCESS_UNIFORM_READ_BIT`, which is a distinct access flag from `VK_ACCESS_SHADER_READ_BIT`. The barrier's destination access mask must include `UNIFORM_READ` for the reader to observe the writer's data. If the implementation treats `UNIFORM_READ` as covered by a broader mask, or if it does not flush the UBO cache on the availability operation, the reader observes stale data. For HOST writer cases, the host fill must `flushAlloc` before the barrier; if the flush is missing or the host-write barrier (`HOST_WRITE` to `UNIFORM_READ`) does not trigger a cache flush, the reader observes zeros. For TRANSFER writer cases, the transfer-to-reader barrier must include `TRANSFER_WRITE` in the source access mask; if the implementation does not flush the transfer write before the UBO read, the reader observes partial or zero data.

#### SSBO reader observed stale or zero data

**Possible failure symptoms:** For `ssbo` cases, the host verification scan finds `verificationBuffer[i]` equals `0` or a pre-fill value instead of `2048 + i`. The mismatch can appear in SSBO cases with any writer/reader stage pair.

**Possible implementation causes:** The barrier's source access mask must include `VK_ACCESS_SHADER_WRITE_BIT` for shader writers (or `HOST_WRITE`/`TRANSFER_WRITE` for those writers), and the destination access mask must include `VK_ACCESS_SHADER_READ_BIT` for shader readers (or `HOST_READ`/`TRANSFER_READ`). If the implementation's availability operation does not flush shader writes from L2 cache to device memory, or if the visibility operation does not invalidate the reader's cache, the reader observes stale data. For ray tracing reader cases, if the TLAS/BLAS setup is wrong, the aux rgen's ray may miss, the closest-hit or any-hit shader may not run, and the verification buffer remains at its initial value. This would look like a barrier bug but is actually an acceleration structure bug; the symptom is that all ray tracing reader cases fail regardless of barrier type, while compute and fragment reader cases pass.

#### Storage image reader observed stale, zero, or undefined data

**Possible failure symptoms:** For `simg` cases, the host verification scan finds `verificationBuffer[i]` equals `0`, `0xFFFFFFFF`, or an unpredictable value instead of `2048 + i`. The mismatch appears in simg cases only.

**Possible implementation causes:** The image-memory barrier's `oldLayout` must match the layout the writer left the image in, and `newLayout` must match the layout the reader expects. If the implementation's layout transition is missing or wrong, `imageLoad` returns undefined data. For shader-to-shader cases, both writer and reader use `VK_IMAGE_LAYOUT_GENERAL`, so the transition is a no-op; a failure here points to the availability or visibility operation, not the layout. For TRANSFER writer cases, the writer transitions the image to `TRANSFER_DST_OPTIMAL` (SPECIFIC) or `GENERAL` (GENERAL); if the implementation does not complete this transition before the copy, the copy writes to the wrong layout. For TRANSFER reader cases, the barrier must transition the image to `TRANSFER_SRC_OPTIMAL`; if it does not, `cmdCopyImageToBuffer` reads from the wrong layout and produces undefined data. The `R32_UINT` format has no implicit component swizzle, so a layout mismatch cannot be masked by format conversion.

#### Shared verification buffer or host readback failure

**Possible failure symptoms:** The mismatch appears across all three resource types for the same stage pair, or the verification buffer reads back as all zeros regardless of the writer or reader stage.

**Possible implementation causes:** The verification buffer's host-read barrier (from reader stage to `HOST_BIT` with `SHADER_WRITE` to `HOST_READ`) must flush the reader's writes before the host reads. If this barrier is missing or uses the wrong access mask, the host observes stale or zero data. If `invalidateAlloc` is not called before the host read, the host may read cached data instead of the device's writes. These causes are not specific to the barrier resource type and would be investigated by checking the verification barrier and host invalidation, not the main barrier.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` device functionality, with the `rayTracingPipeline` and `accelerationStructure` feature bits enabled, when either the writer or reader is a ray tracing stage. See [`checkSupport`](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L771-L794).
- The FRAGMENT writer case requires `fragmentStoresAndAtomics` because the fragment shader writes to the barrier resource. The check throws `NotSupportedError` if the feature is missing. See [fragment feature check](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L773-L779).
- The `accelerationStructure` feature is checked as a hard error (`TCU_FAIL`) rather than `NotSupportedError` because `VK_KHR_ray_tracing_pipeline` depends on it.

### Design-based pruning

- **No ray tracing stage skip.** The registration loop skips every combination where neither writer nor reader is a ray tracing stage. This removes pure compute-to-compute, host-to-host, and transfer-to-transfer cases. See [skip rule](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1802-L1804).
- **No host access to storage image skip.** The registration loop skips every simg case whose writer or reader is HOST, because the image is allocated with `MemoryRequirement::Any` and there is no host readback path for images. See [skip rule](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1806-L1809).
- **No shader write to UBO skip.** The registration loop skips every ubo case whose writer is not HOST or TRANSFER, because Vulkan does not allow shader writes to a `UNIFORM_BUFFER`. This restricts UBO writers to HOST and TRANSFER. See [skip rule](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1811-L1814).
- These three rules reduce the stage-pair matrix from 100 combinations (10 writers x 10 readers) per resource type per barrier type to the observed 72 (simg), 84 (ssbo), and 12 (ubo) cases per barrier type.

## Key Takeaways

- The test family exercises barrier synchronization between every legal pair of writer and reader stages where at least one is a ray tracing stage, across three resource types and two barrier shapes. The 336 registered cases come from the cross product of these dimensions after pruning.
- The single `VK_PIPELINE_STAGE_RAY_TRACING_SHADER_BIT_KHR` flag represents all six ray tracing sub-stages. The host barrier names the same source or destination stage regardless of whether the actual writer or reader is raygen, intersection, any-hit, closest-hit, miss, or callable.
- The SSBO group is the largest (168 cases) because it allows every writer/reader stage combination. The UBO group is the smallest (24 cases) because UBOs cannot be written from shaders. The simg group (144 cases) is the only one that exercises image layout transitions.
- The reader closest-hit shader is the consumer side of the barrier. Its `OpLoad` from the SSBO returns the writer's value only if the barrier's availability and visibility operations completed correctly. The host verification scan catches any mismatch with an exact zero-threshold comparison.
- A failure across all three resource types for the same stage pair points to shared infrastructure (verification buffer, host readback). A failure in one resource type only points to the barrier semantics specific to that resource type.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestParams` struct | [vktRayTracingBarrierTests.cpp#L325-L342](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L325-L342) | Defines the four test parameters: resource type, writer stage, reader stage, barrier type. |
| `getPipelineStage` | [vktRayTracingBarrierTests.cpp#L113-L145](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L113-L145) | Maps each stage to its `VkPipelineStageFlagBits`; collapses all ray tracing stages to one bit. |
| `getWriterAccessFlag` / `getReaderAccessFlag` | [vktRayTracingBarrierTests.cpp#L147-L206](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L147-L206) | Maps each stage to its write/read access flag; UBO reads use `UNIFORM_READ`. |
| `initPrograms` writer shader generation | [vktRayTracingBarrierTests.cpp#L410-L620](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L410-L620) | Generates the writer shader per stage and resource type. |
| `initPrograms` reader shader generation | [vktRayTracingBarrierTests.cpp#L622-L764](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L622-L764) | Generates the reader shader per stage and resource type, including the verification buffer write. |
| `checkSupport` | [vktRayTracingBarrierTests.cpp#L771-L794](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L771-L794) | Feature gates: `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, `fragmentStoresAndAtomics`. |
| `iterate` resource creation | [vktRayTracingBarrierTests.cpp#L1264-L1382](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1264-L1382) | Builds the barrier resource, verification buffer, and image view. |
| Writer recording | [vktRayTracingBarrierTests.cpp#L1384-L1545](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1384-L1545) | Records writer commands for every stage type. |
| Main barrier recording | [vktRayTracingBarrierTests.cpp#L1547-L1592](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1547-L1592) | Records the GENERAL or SPECIFIC barrier between writer and reader. |
| Reader recording and verification barrier | [vktRayTracingBarrierTests.cpp#L1594-L1694](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1594-L1694) | Records reader commands and the verification-buffer host-read barrier. |
| Host verification scan | [vktRayTracingBarrierTests.cpp#L1723-L1745](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1723-L1745) | Linear scan of `verificationBuffer` with exact expected value. |
| `createBarrierTests` registration loop | [vktRayTracingBarrierTests.cpp#L1750-L1826](../../../modules/vulkan/ray_tracing/vktRayTracingBarrierTests.cpp#L1750-L1826) | Builds the three resource-type groups, two barrier-type groups, and applies the three skip rules. |
| `getCommonRayGenerationShader` | [vkRayTracingUtil.cpp#L118-L138](../../../framework/vulkan/vkRayTracingUtil.cpp#L118-L138) | Shared aux rgen helper used by every non-raygen ray tracing writer/reader. |
