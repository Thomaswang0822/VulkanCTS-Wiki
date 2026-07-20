## Overview

**Core question:** Does a ray tracing implementation honor the Vulkan memory model's shader-call visibility guarantee, so a storage image write performed by one shader invocation is observable both inside the same invocation and across a shader-call boundary in a subsequent invocation?

- [vktRayTracingMemGuaranteeTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp) implements and registers the `memguarantee` test family under the `ray_tracing_pipeline` test category.
- Two intermediate nodes, `between` and `inside`, encode the two memory visibility modes the test exercises. Each owns five test case leaves (`rgen`, `chit`, `miss`, `sect`, `call`) that vary which shader stage performs the write-repack-read sequence.
- The core idea is a single `r32ui` storage image that the caller writes with `r = pos`, then either reads back inside the same invocation (`inside`) or has a callee read back after a shader-call boundary (`between`). The final pixel must equal `pos + 1`.
- The `between` mode adds the `shadercallcoherent` qualifier and a release/acquire `memoryBarrier(gl_ScopeShaderCallEXT, ...)` pair across `executeCallableEXT` or `reportIntersectionEXT`. The `inside` mode uses neither, relying on intra-invocation program order.
- The page explains the memory-model property under test, the per-stage shader-call mechanism, the host scan that decides pass/fail, and how a failure maps back to a missing visibility guarantee versus a stage-dispatch bug.

## Background Knowledge

- **Shader-call scope.** `gl_ScopeShaderCallEXT` (`ShaderCallKHR` in SPIR-V, scope id 6) covers shader invocations reachable through ray tracing shader-call instructions: `executeCallableEXT`, `traceRayEXT`, and `reportIntersectionEXT`. A release before one of these instructions must be made available to the callee that a matching acquire on the same scope synchronizes with.
- **Repack boundary.** The test calls `executeCallableEXT(0, 0)` (callable callee) or `reportIntersectionEXT(0.95f, 0u)` (any-hit callee) immediately after the caller's release. This is the boundary the `between` mode exercises.
- **Intra-invocation visibility.** A shader invocation always observes its own prior writes to a non-coherent variable through program order. The `inside` mode relies on this property across a repack instruction within the same invocation, with no barrier and no `shadercallcoherent` qualifier.
- **`shadercallcoherent` qualifier.** A GLSL layout qualifier that opts a variable into cross-shader-call availability/visibility. The test adds it to the caller's image declaration only; the explicit `memoryBarrier` pair carries the actual synchronization, making the qualifier a redundant opt-in.
- **`GL_KHR_memory_scope_semantics`.** GLSL extension that exposes `gl_ScopeShaderCallEXT`, `gl_StorageSemanticsImage`, `gl_SemanticsRelease`, and `gl_SemanticsAcquire`. The test enables it only in `between` mode.

## Registration Hierarchy

```text
ray_tracing_pipeline.memguarantee
├── between
└── inside
```

Each intermediate node owns five test case leaves: `rgen`, `chit`, `miss`, `sect`, `call`. Mustpass evidence lists all 10 leaves under `dEQP-VK.ray_tracing_pipeline.memguarantee.{between,inside}.{rgen,chit,miss,sect,call}` ([ray-tracing-pipeline.txt#L13027-L13036](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt#L13027-L13036)).

## Parameter Dimensions and Observed Values

The matrix is built from two arrays in the registration loop ([vktRayTracingMemGuaranteeTests.cpp#L857-L905](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L857-L905)).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `TestType` (intermediate node) | `between`, `inside` | Primary behavioral axis. Selects whether the two image writes happen across a shader-call boundary with explicit release/acquire, or inside the same invocation with no synchronization. | [testTypes array](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L867-L874) |
| Stage under test (test case leaf) | `rgen`, `chit`, `miss`, `sect`, `call` | Selects which shader stage performs the write-repack-read sequence. Changes the repack instruction and the callee shader type. | [stages array](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L857-L865) |
| Launch size | fixed `16 x 16 x 1` | 256 pixels, one per launch invocation. Each pixel's expected value is `pos + 1` with `pos = y * 16 + x`. | [width/height](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L885-L886) |
| BLAS layout | fixed `8 instances x 4 geometries x 8 squares` | Covers the 16x16 launch grid with one square per pixel so every ray hits a unique primitive. | [squaresGroupCount](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L887-L889) |
| Result image | fixed `16 x 16`, `r32ui`, cleared to `1000000u` | Storage image that encodes pass/fail per pixel. The clear value is far outside the expected `[1, 256]` range, so an unwritten pixel is immediately detectable. | [clearValue](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L745) |

## Behavior Parameters

The primary behavioral axis is the `TestType` intermediate node. The stage dimension varies which shader-call mechanism carries the boundary, but does not change the property under test.

### between — cross-shader-call visibility with release/acquire

The caller stage writes `r` to the storage image, emits `memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsRelease)`, then executes the repack instruction. The callee (a callable shader for `rgen`, `chit`, `miss`, `call`, or the any-hit shader for `sect`) emits `memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsAcquire)`, reads `d` (must equal `r`), and writes `d + 1`. The caller's image declaration carries `shadercallcoherent`. The `GL_KHR_memory_scope_semantics` extension is enabled. A failure here points to a missing or weakened shader-call-scope visibility guarantee.

### inside — intra-invocation visibility across a repack

The stage under test performs both writes in the same invocation: `imageStore(r)`, then the repack instruction, then `imageLoad(d)` (must equal `r`), then `imageStore(d + 1)`. No `shadercallcoherent` qualifier, no extension, no barrier. The callee shader exists but its body is empty. A failure here means the implementation lost a write within a single invocation across the repack instruction, which violates program-order visibility.

## Shader Analysis

The shaders are inline GLSL strings emitted by `initPrograms` with `SPIRV_VERSION_1_4` ([vktRayTracingMemGuaranteeTests.cpp#L301-L506](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L301-L506)). The `between` and `inside` modes are encoded by three conditionally injected strings:

- `glslExtensions` adds `#extension GL_KHR_memory_scope_semantics : require` for `between` only.
- `imageQualifiers` adds ` shadercallcoherent ` to the caller's image declaration for `between` only.
- `updateBarrierCaller` and `updateBarrierCallee` add the release and acquire `memoryBarrier(gl_ScopeShaderCallEXT, ...)` calls for `between` only; both are empty for `inside`.

One walkthrough covers the `between.rgen` case. It exercises the `shadercallcoherent` qualifier, the release/acquire barrier pair, and the `executeCallableEXT` repack boundary, which is the central property under test. The other stages differ only in which shader stage hosts the caller body and which repack instruction is used; those differences are summarized in the Parameter Variation Summary. The `inside` counterpart is the same caller body with the barrier lines removed and the second write appended in the same invocation.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.memguarantee.between.rgen
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `between` | Cross-shader-call visibility with release/acquire on `gl_ScopeShaderCallEXT`. |
| `rgen` | The raygen shader is the caller. It writes `r`, releases, and calls `executeCallableEXT(0, 0)`. The callee `cal0` is a callable shader. |

#### Purpose

This case checks that the callable shader `cal0`, invoked from rgen via `executeCallableEXT(0, 0)`, observes the rgen's `imageStore(r)` after the release/acquire pair on `gl_ScopeShaderCallEXT`. If the implementation does not propagate the release to the callee, `cal0` reads an undefined or clear value instead of `r`, and the final pixel fails to equal `pos + 1`.

#### Structural Design

| Step | Stage | Action | Image effect |
|------|-------|--------|--------------|
| 1 | rgen | Compute `r = gl_LaunchIDEXT.x + gl_LaunchSizeEXT.x * gl_LaunchIDEXT.y` | none |
| 2 | rgen | `imageStore(result, ivec2(gl_LaunchIDEXT), uvec4(r, 0, 0, 1))` | pixel = r |
| 3 | rgen | `memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsRelease)` | release image writes to shader-call scope |
| 4 | rgen | `executeCallableEXT(0, 0)` | repack boundary; invoke `cal0` |
| 5 | cal0 | `memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsAcquire)` | acquire prior released image writes |
| 6 | cal0 | `d = imageLoad(result, ivec2(gl_LaunchIDEXT)).x` | d must equal r |
| 7 | cal0 | `imageStore(result, ivec2(gl_LaunchIDEXT), uvec4(d + 1, 0, 0, 1))` | pixel = r + 1 |

#### Shader Code

Reconstructed rgen (caller):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_KHR_memory_scope_semantics : require
layout(set = 0, binding = 0, r32ui) shadercallcoherent uniform uimage2D result;
layout(location = 0) callableDataEXT float dummy;

void main()
{
  uint  r = uint(gl_LaunchIDEXT.x + gl_LaunchSizeEXT.x * gl_LaunchIDEXT.y);
  uvec4 c = uvec4(r, 0, 0, 1);
  imageStore(result, ivec2(gl_LaunchIDEXT), c);

  memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsRelease);

  executeCallableEXT(0, 0);
}
```

Reconstructed `cal0` (callee callable shader):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
#extension GL_KHR_memory_scope_semantics : require
layout(location = 0) callableDataInEXT float dummy;
layout(set = 0, binding = 0, r32ui) uniform uimage2D result;

void main()
{
  memoryBarrier(gl_ScopeShaderCallEXT, gl_StorageSemanticsImage, gl_SemanticsAcquire);
  uint  d = imageLoad(result, ivec2(gl_LaunchIDEXT)).x;
  imageStore(result, ivec2(gl_LaunchIDEXT), uvec4(d + 1, 0, 0, 1));
}
```

#### Additional Info

- The `shadercallcoherent` qualifier on rgen's `result` declaration is the GLSL opt-in for cross-shader-call visibility. The SPIR-V disassembly below shows no `Coherent` decoration on `%result`; `OpMemoryBarrier %uint_6 %uint_2052` (scope `ShaderCallKHR`, semantics `Release|Image`) in rgen and `OpMemoryBarrier %uint_6 %uint_2050` (scope `ShaderCallKHR`, semantics `Acquire|Image`) in `cal0` carry the synchronization.
- `executeCallableEXT(0, 0)` maps to `OpExecuteCallableKHR %uint_0 %dummy`. The first argument is the SBT record offset; the second is the callable data location.
- The `cal0` callee has no `shadercallcoherent` qualifier on its `result` declaration. The acquire barrier alone is sufficient because the release was already performed by the caller in the same shader-call scope.
- For the `inside.rgen` counterpart, the same rgen body has the two barrier lines removed and appends the `imageLoad`/`imageStore(d+1)` sequence after `executeCallableEXT(0, 0)`, all in the same invocation. The `cal0` body is empty.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this walkthrough | Evidence |
|---------------------|--------------------------------------------|----------|
| `TestType` | `inside` removes `glslExtensions`, `imageQualifiers`, and both barrier strings; the caller performs both writes in the same invocation; the callee body is empty. | [imageQualifiers, glslExtensions, barrier strings](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L305-L318) |
| Stage under test | `chit`, `miss`, and `call` use the same `executeCallableEXT(0, 0)` repack in a different caller stage. `chit` runs after a `traceRayEXT` hit; `miss` runs after a `traceRayEXT` miss (geometry placed at z = +1.0); `call` runs after rgen calls `executeCallableEXT(1, 0)` to invoke the `call` shader, which then performs the write-repack sequence. | [initPrograms stage switch](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L342-L505) |
| `sect` repack | The intersection shader is the caller. Its repack instruction is `reportIntersectionEXT(0.95f, 0u)` instead of `executeCallableEXT(0, 0)`. The callee is the any-hit shader (`ahit`), not a callable shader. | [calleeIsAnyHit, repackInstruction](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L308-L310) |

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
; Bound: 51
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %result %dummy
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpSourceExtension "GL_KHR_memory_scope_semantics"
               OpName %main "main"
               OpName %r "r"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %c "c"
               OpName %result "result"
               OpName %dummy "dummy"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
         %29 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_29 = OpTypePointer UniformConstant %29
     %result = OpVariable %_ptr_UniformConstant_29 UniformConstant
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
      %v2int = OpTypeVector %int 2
      %int_6 = OpConstant %int 6
   %int_2048 = OpConstant %int 2048
      %int_4 = OpConstant %int 4
     %uint_6 = OpConstant %uint 6
  %uint_2052 = OpConstant %uint 2052
      %int_0 = OpConstant %int 0
      %float = OpTypeFloat 32
%_ptr_CallableDataKHR_float = OpTypePointer CallableDataKHR %float
      %dummy = OpVariable %_ptr_CallableDataKHR_float CallableDataKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
          %r = OpVariable %_ptr_Function_uint Function
          %c = OpVariable %_ptr_Function_v4uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %18 = OpLoad %uint %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %21 = OpLoad %uint %20
         %22 = OpIMul %uint %18 %21
         %23 = OpIAdd %uint %15 %22
               OpStore %r %23
         %27 = OpLoad %uint %r
         %28 = OpCompositeConstruct %v4uint %27 %uint_0 %uint_0 %uint_1
               OpStore %c %28
         %32 = OpLoad %29 %result
         %33 = OpLoad %v3uint %gl_LaunchIDEXT
         %36 = OpBitcast %v3int %33
         %38 = OpCompositeExtract %int %36 0
         %39 = OpCompositeExtract %int %36 1
         %40 = OpCompositeConstruct %v2int %38 %39
         %41 = OpLoad %v4uint %c
               OpImageWrite %32 %40 %41 ZeroExtend
               OpMemoryBarrier %uint_6 %uint_2052
               OpExecuteCallableKHR %uint_0 %dummy
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
; Bound: 46
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint CallableKHR %main "main" %result %gl_LaunchIDEXT %dummy
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_ray_tracing"
               OpSourceExtension "GL_KHR_memory_scope_semantics"
               OpName %main "main"
               OpName %d "d"
               OpName %result "result"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %dummy "dummy"
               OpDecorate %result Binding 0
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %int_6 = OpConstant %int 6
   %int_2048 = OpConstant %int 2048
      %int_2 = OpConstant %int 2
       %uint = OpTypeInt 32 0
     %uint_6 = OpConstant %uint 6
  %uint_2050 = OpConstant %uint 2050
%_ptr_Function_uint = OpTypePointer Function %uint
         %15 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_15 = OpTypePointer UniformConstant %15
     %result = OpVariable %_ptr_UniformConstant_15 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
      %v3int = OpTypeVector %int 3
      %v2int = OpTypeVector %int 2
     %v4uint = OpTypeVector %uint 4
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
      %float = OpTypeFloat 32
%_ptr_IncomingCallableDataKHR_float = OpTypePointer IncomingCallableDataKHR %float
      %dummy = OpVariable %_ptr_IncomingCallableDataKHR_float IncomingCallableDataKHR
       %main = OpFunction %void None %3
          %5 = OpLabel
          %d = OpVariable %_ptr_Function_uint Function
               OpMemoryBarrier %uint_6 %uint_2050
         %18 = OpLoad %15 %result
         %22 = OpLoad %v3uint %gl_LaunchIDEXT
         %24 = OpBitcast %v3int %22
         %26 = OpCompositeExtract %int %24 0
         %27 = OpCompositeExtract %int %24 1
         %28 = OpCompositeConstruct %v2int %26 %27
         %30 = OpImageRead %v4uint %18 %28 ZeroExtend
         %32 = OpCompositeExtract %uint %30 0
               OpStore %d %32
         %33 = OpLoad %15 %result
         %34 = OpLoad %v3uint %gl_LaunchIDEXT
         %35 = OpBitcast %v3int %34
         %36 = OpCompositeExtract %int %35 0
         %37 = OpCompositeExtract %int %35 1
         %38 = OpCompositeConstruct %v2int %36 %37
         %39 = OpLoad %uint %d
         %41 = OpIAdd %uint %39 %uint_1
         %42 = OpCompositeConstruct %v4uint %41 %uint_0 %uint_0 %uint_1
               OpImageWrite %33 %38 %42 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Resource setup.** The host creates a 16x16 `r32ui` storage image with `VK_IMAGE_USAGE_STORAGE_BIT | TRANSFER_SRC_BIT | TRANSFER_DST_BIT`, plus a host-visible copyback buffer of `256 * sizeof(uint32_t)` bytes ([runTest resource setup](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L714-L729)).
- **Acceleration structures.** Eight BLAS instances, each with four geometries, each geometry with eight squares, cover the 16x16 launch grid. For `miss` cases the geometry is placed at `z = +1.0` so rays traveling down `-Z` miss; for hit cases it is placed at `z = -1.0`. A TLAS wraps all eight instances ([initBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L590-L632), [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L568-L588)).
- **Pipeline and SBT.** Shader groups are raygen (group 0), miss (group 1), hit (group 2), and callable (group 3 onward when needed). The host builds SBT regions for each group with `shaderGroupHandleSize` stride ([makePipeline](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L513-L547), [createShaderBindingTable](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L549-L566)).
- **Image clear and barriers.** The image is cleared to `1000000u` in `TRANSFER_DST_OPTIMAL` layout, then barriered to `GENERAL` with acceleration-structure read/write access before the trace ([runTest barriers](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L734-L757)).
- **Trace.** `cmdTraceRays` runs a `16 x 16 x 1` launch with the four SBT regions ([cmdTraceRays](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L782-L783)).
- **Copyback.** A shader-write to transfer-read memory barrier follows the trace, then `cmdCopyImageToBuffer` copies the image to the host-visible buffer, and a transfer-write to host-read barrier precedes `submitCommandsAndWait`. The host invalidates the mapped range before reading ([copyback](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L785-L798)).
- **Pass/fail scan.** `iterate` walks all 256 pixels. Each pixel at position `pos = y * 16 + x` must equal `pos + 1`. Any mismatch increments the failure counter. A single failing pixel fails the case. The clear value `1000000u` is far outside the expected `[1, 256]` range, so an unwritten pixel is detected as a mismatch rather than a coincidental hit ([iterate](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L826-L852)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `between` | Cross-shader-call visibility failure: the callee did not observe the caller's `imageStore(r)` after the release/acquire pair on `gl_ScopeShaderCallEXT`, or the `shadercallcoherent` qualifier was not honored. |
| `inside` | Intra-invocation write lost: the same shader invocation did not observe its own prior `imageStore(r)` after the repack instruction, with no barrier or qualifier required. |
| (all stages of one test type) | A single stage-specific shader dispatch or SBT routing bug, distinguishable by which stage leaves fail. |
| (all cases) | Shared image-clear, trace, or copyback infrastructure failure, distinguishable by pixels reading back the clear value `1000000u` or by failures across both test types. |

### Cause Analysis

#### Cross-shader-call visibility failure

**Possible failure symptoms:** For `between`, the failing pixel reads back `1000000u` (the clear value, meaning the callee never wrote) or a value other than `pos + 1` (meaning the callee read the wrong `d` and wrote the wrong increment). A reading of exactly `pos` (i.e., `r`) means the caller's `imageStore(r)` survived and the callee did not run or its write was lost; if the callee had read `d = 0` or stale data, it would have written `1` or `stale + 1`, not `r`.

**Possible implementation causes:** The release on `gl_ScopeShaderCallEXT` must make the caller's `imageStore` available to the callee that an acquire on the same scope synchronizes with. A failure here points to the implementation not propagating the release across `OpExecuteCallableKHR` (or `OpReportIntersectionKHR` for `sect`), or not treating the callee's acquire as matching the caller's release. The spec requires that a release-acquire pair on `ShaderCallKHR` scope synchronize memory accesses between invocations in the same shader call chain. A driver that lowered the barrier to a no-op, treated the scope as `Workgroup` or `Device` incorrectly, or scheduled the callee before the release completed would produce this symptom. The `shadercallcoherent` qualifier is redundant here because the explicit barriers carry the synchronization, so a qualifier-handling bug alone would not cause this failure as long as the barriers are honored.

#### Intra-invocation write lost

**Possible failure symptoms:** For `inside`, the failing pixel reads back `1000000u` (neither write happened), `pos` (only the first write happened, the second was lost), or a value other than `pos + 1` (the load read back the wrong `d`).

**Possible implementation causes:** A shader invocation must observe its own prior writes through program order, with no barrier or qualifier required. The `inside` mode places `imageStore(r)`, the repack instruction, `imageLoad(d)`, and `imageStore(d + 1)` in the same invocation. A failure here suggests the implementation reordered the second `imageStore` ahead of the `imageLoad`, dropped the first `imageStore` across the repack, or treated the repack instruction as a stronger boundary than the spec allows. The repack instruction (`OpExecuteCallableKHR` or `OpReportIntersectionKHR`) is a shader-call instruction, not a memory barrier; it does not break program-order visibility for the issuing invocation. Source-level investigation would focus on whether the compiler inserted an illegal store-load reorder or the runtime lost the invocation's local writes when suspending for the repack.

#### Stage-specific dispatch or SBT routing bug

**Possible failure symptoms:** All `between` cases of one stage fail (for example, `between.chit` and `between.miss` pass but `between.sect` fails), while the corresponding `inside` cases of the same stage also fail. Or a single stage fails across both test types.

**Possible implementation causes:** Each stage uses a different shader-call mechanism to reach the callee: `executeCallableEXT` for `rgen`, `chit`, `miss`, `call`; `reportIntersectionEXT` for `sect`. The `call` case adds a second callable invocation level. A stage-specific failure suggests the implementation mishandles that particular shader-call dispatch path or the SBT record offset resolution for that stage. The `sect` case is the most distinct because its callee is an any-hit shader reached through intersection reporting, not a callable shader; a `sect`-only failure would point to the intersection-to-any-hit memory visibility path. The `miss` case routes through a miss shader rather than a hit group; a `miss`-only failure would point to miss-shader dispatch. These causes are distinct from the core memory-model property and would be investigated by checking the stage's SBT layout and dispatch path rather than the barrier logic.

#### Shared infrastructure failure

**Possible failure symptoms:** Failures appear across both `between` and `inside` and across multiple stages. Pixels read back the clear value `1000000u`, or read back values inconsistent with any stage's expected `pos + 1` pattern.

**Possible implementation causes:** The image is cleared to `1000000u` before the trace and barriered to `GENERAL`. If the clear or the layout transition did not take effect, the rgen `imageStore` could write over stale data or be invisible to the copy. If `cmdCopyImageToBuffer` or the host invalidation missed a region, the host would read stale or uninitialized memory. The post-trace barrier (`VK_ACCESS_SHADER_WRITE_BIT` to `VK_ACCESS_TRANSFER_READ_BIT`) must complete before the copy; a missing barrier would let the copy observe pre-trace data. These causes are not specific to the memory-model property and would be investigated by checking the barriers, copy region, and host invalidation rather than the shader logic.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` device functionality, with the `rayTracingPipeline` and `accelerationStructure` feature bits enabled ([checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L243-L258)).
- The `accelerationStructure` feature is checked as a hard `TestError` rather than `NotSupportedError` because `VK_KHR_ray_tracing_pipeline` depends on it.
- `checkSupportInInstance` also rejects cases that exceed `maxPrimitiveCount`, `maxGeometryCount`, `maxInstanceCount`, or `maxMemoryAllocationCount` ([checkSupportInInstance](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L803-L824)).

### Design-based pruning

- The stage array is fixed to `rgen`, `chit`, `sect`, `miss`, `call`. There is no `ahit` leaf because the any-hit shader is used as the callee for `sect`, not as a caller stage under test.
- The launch size is fixed at `16 x 16`. There is no per-stage size variation because the test only needs one pixel per launch invocation to verify the memory property.
- The `inside` mode still emits a callee shader (callable or any-hit) with an empty body, so the pipeline and SBT layout match the `between` mode. The repack instruction still executes; only the barrier and qualifier strings differ.
- The `between` mode enables `GL_KHR_memory_scope_semantics` on both caller and callee because both shaders emit the `memoryBarrier` intrinsic. The `shadercallcoherent` qualifier, in contrast, is added only to the caller's image declaration.

## Key Takeaways

- The `between` and `inside` modes test two distinct memory-model properties: cross-shader-call visibility with explicit release/acquire, and intra-invocation visibility with no synchronization. Both must hold for the implementation to conform.
- The `shadercallcoherent` qualifier on the caller's image declaration is a redundant opt-in. `OpMemoryBarrier` with scope `ShaderCallKHR` and semantics `Release|Image` (caller) and `Acquire|Image` (callee) does the synchronization. The SPIR-V disassembly confirms no `Coherent` decoration on the variable.
- The repack instruction (`OpExecuteCallableKHR` for four stages, `OpReportIntersectionKHR` for `sect`) is the boundary the `between` mode exercises. It is not itself a memory barrier; visibility depends on the explicit release/acquire pair.
- The `sect` case is the only case where the callee is an any-hit shader rather than a callable shader. A `sect`-only failure points to the intersection-to-any-hit dispatch path rather than the core shader-call-scope property.
- The clear value `1000000u` is the canary for unwritten pixels. A reading of `1000000u` means neither write reached that pixel, which distinguishes a missing-callee or missing-barrier failure from a wrong-value failure.
- See `## Failure Meaning` for how a single failing pixel maps back to a missing visibility guarantee versus a stage-dispatch bug versus a shared infrastructure failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` enum and `CaseDef` | [vktRayTracingMemGuaranteeTests.cpp#L54-L69](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L54-L69) | Defines the two behavior parameter values and the per-case configuration. |
| `initPrograms` shader emission | [vktRayTracingMemGuaranteeTests.cpp#L301-L506](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L301-L506) | Source of the reconstructed walkthrough shaders and the `inside`/`between` conditional strings. |
| `imageQualifiers`, `glslExtensions`, barrier strings | [vktRayTracingMemGuaranteeTests.cpp#L305-L331](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L305-L331) | Encodes the `between` vs `inside` shader-level difference. |
| `runTest` host flow | [vktRayTracingMemGuaranteeTests.cpp#L651-L801](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L651-L801) | Resource creation, clear, AS build, SBT, trace, copyback, host invalidation. |
| `iterate` pass/fail check | [vktRayTracingMemGuaranteeTests.cpp#L826-L852](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L826-L852) | Encodes the `pos + 1` expected value and the failure counter. |
| `checkSupport` feature gates | [vktRayTracingMemGuaranteeTests.cpp#L243-L258](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L243-L258) | Requires the two KHR feature bits. |
| Registration loop | [vktRayTracingMemGuaranteeTests.cpp#L855-L908](../../../modules/vulkan/ray_tracing/vktRayTracingMemGuaranteeTests.cpp#L855-L908) | Builds the two test type groups and the five stage leaves each. |
| Mustpass evidence | [ray-tracing-pipeline.txt#L13027-L13036](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt#L13027-L13036) | Lists all 10 registered leaves. |
