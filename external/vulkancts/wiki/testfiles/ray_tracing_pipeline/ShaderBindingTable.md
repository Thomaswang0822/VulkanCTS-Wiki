## Overview

**Core question:** Does the implementation resolve shader binding table (SBT) entries through `traceRayEXT`'s `sbtRecordOffset`, `sbtRecordStride`, and `missIndex` arguments exactly as the spec defines, and does it preserve shader-group handle and shader-record data integrity at every advertised power-of-two alignment?

- [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp) implements the `shader_binding_table` test family under the `ray_tracing_pipeline` test category.
- The file registers four direct children: `indexing_hit`, `indexing_miss`, `indexing_call`, and `handle_alignment`.
- The `indexing_*` families render an 8x8 checkerboard image where each pixel's stored value identifies which SBT slot the implementation picked. The host recomputes the expected value with the spec-defined indexing formula and compares with zero tolerance.
- The `handle_alignment` family pads each hit SBT record with shader-record data of a chosen size and reads that data back through an SSBO to verify alignment is honored for power-of-two alignments from 1 to 32 bytes.
- The reader should expect the page to explain the SBT indexing formula for each family, the role of `sbt_offset`, `shaderrecord`, and the extra-bits variants, and the alignment-stressing mechanism.

## Background Knowledge

- **SBT regions.** The SBT is split into raygen, miss, hit, and callable regions, each described by a `VkStridedDeviceAddressRegionKHR`. Each region is an array of records; a record begins with a shader-group handle and may carry a shader-record data block after it.
- **`shaderGroupBaseAlignment`, `shaderGroupHandleSize`, `shaderGroupHandleAlignment`.** These ray tracing properties constrain, respectively, the start of every SBT region and any host-supplied offset into an SBT buffer, the size of a single shader-group handle, and the alignment of each record inside a region.
- **Hit SBT indexing.** `traceRayEXT` resolves the hit-group record at `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`. The instance contribution comes from `VkAccelerationStructureInstanceKHR::instanceShaderBindingTableRecordOffset`.
- **Miss SBT indexing.** The miss shader is selected from the miss region at offset `missIndex` strides.
- **Low-bit-only semantics.** Implementations are only required to honor the low 4 bits of `sbtRecordOffset` and `sbtRecordStride` for hit indexing, and the low 16 bits of `missIndex` for miss indexing. The test deliberately feeds values with extra high bits set in the maximum-offset and maximum-stride cases to exercise this allowance.
- **Shader Record.** `layout(shaderRecordEXT) buffer block { ... }` exposes the per-record data after the shader-group handle. The host writes a unique value per record so the receiving shader can confirm which SBT slot it ran from.

## Registration Hierarchy

```text
ray_tracing_pipeline.shader_binding_table
├── handle_alignment
├── indexing_call
├── indexing_hit
└── indexing_miss
```

## Parameter Dimensions and Observed Values

The `indexing_*` matrix is built by nested loops over shader test type, SBT buffer offset, shader-record presence, SBT record offset, and SBT record stride [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1622-L1722). The `handle_alignment` matrix is a single loop over power-of-two alignments with a paired long-vector variant on non-VulkanSC builds [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1724-L1743).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `indexing_hit`, `indexing_miss`, `indexing_call`, `handle_alignment` | Selects which SBT property the case exercises: hit-region indexing, miss-region indexing, callable-region indexing, or shader-group handle alignment with shader-record padding. | [family loop](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1622-L1743) |
| SBT buffer offset | `sbt_offset_0`, `sbt_offset_4`, `sbt_offset_7`, `sbt_offset_16` | Multiplies `shaderGroupBaseAlignment` to produce the host-supplied offset into the active SBT buffer. Verifies the implementation honors `shaderBindingTableOffset` when computing region addresses. | [shaderBufferOffsets](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1632-L1641) |
| Shader-record presence | `no_shaderrecord`, `shaderrecord` | Chooses between per-slot constant shaders and a single shader that reads its slot index from `layout(shaderRecordEXT)`. The `shaderrecord` variants stress both indexing and shader-record data placement. | [shaderRecords](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1643-L1650) |
| SBT record offset | `0`, `1`, `2`, `3` (max gets `_extrabits` suffix) | Drives `sbtRecordOffset` (or `missIndex` for `indexing_miss`). The maximum value is also passed with extra high bits set to verify only the low bits are honored. | [sbtRecordOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1678-L1695) |
| SBT record stride | `0` through `MAX_HIT_SBT_RECORD_STRIDE` (max gets `_extraSBTRecordStrideBits` suffix) | Drives `sbtRecordStride`. Only `indexing_hit` and `indexing_call` use non-zero strides; `indexing_miss` fixes stride at 0 because the miss index already selects the slot. | [sbtRecordStride loop](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1679-L1695) |
| Handle alignment | `alignment_1`, `alignment_2`, `alignment_4`, `alignment_8`, `alignment_16`, `alignment_32` | Pads each hit SBT record so shader-group handles land at the chosen power-of-two alignment. Geometry count scales as `32/alignment + 1`. | [kAlignments](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1725-L1740) |
| Long-vector shader-record | `_longvec` suffix on each `handle_alignment` case | Uses `vector<elemType, elementCount>` instead of an array for the shader-record block, gated on `VK_EXT_shader_long_vector`. Skipped on VulkanSC. | [longvec variant](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1736-L1739) |

## Behavior Parameters

The primary behavioral axis is the test family: the direct child of `ray_tracing_pipeline.shader_binding_table`. Each value exercises a distinct SBT property. The remaining dimensions configure how hard each family's mechanism is stressed.

### indexing_hit — Hit-region SBT record selection

`indexing_hit` verifies that the hit-group record is selected by `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`. The host arranges checkerboard triangles so each hit pixel maps to a known `(instanceOffset, geometryIndex)` pair, then compares the per-pixel stored value against that formula [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L680-L688). The family accepts non-zero `sbtRecordStride` values, so it is the only family that exercises the stride-multiplied geometry-index term.

### indexing_miss — Miss-region SBT record selection

`indexing_miss` verifies that the miss shader is selected by the `missIndex` argument to `traceRayEXT`. All instances share the same `instanceCustomIndex`, and any hit routes to `chit_0` which writes 0; pixels that miss get their value from the selected miss shader [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L689-L692). Stride is fixed at 0 because the miss index alone selects the slot. The extra-bits variant uses `~((1u << 16) - 1)` masking instead of the 4-bit masking used by the hit and call families.

### indexing_call — Callable-region SBT record selection

`indexing_call` verifies that `executeCallableEXT` selects the callable record at the index it is given. `traceRayEXT`'s hit SBT lookup selects the `chit_call_<idx>` closest-hit shader at the slot computed by `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride`; that shader calls `executeCallableEXT(idx, 0)` with its baked-in slot index, and copies the callable data written by `call_<idx>` into the ray payload [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L850-L869). This family reuses the hit SBT indexing formula but routes the result through the callable region instead of the hit region.

### handle_alignment — Shader-group handle alignment with shader-record padding

`handle_alignment` pads each hit SBT record with shader-record data of size `alignment` bytes (1, 2, 4, 8, 16, or 32), producing SBT record stride `shaderGroupHandleSize + alignment`. The closest-hit shader reads its shader-record data and writes it to an SSBO; the host reads back the SSBO and compares it byte-by-byte against the per-geometry shader-record data [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1469-L1612). The family verifies that the implementation preserves shader-group handle alignment and shader-record data integrity at every advertised power-of-two alignment.

## Shader Analysis

This page uses one representative walkthrough. The rgen shader is shared across all `indexing_*` families; family differences come from host-side UBO contents and SBT construction, which the runtime section covers. The `handle_alignment` family uses a different chit shader parameterized at GLSL-generation time by alignment and element type; the runtime section and variation tables cover its mechanism, and a separate walkthrough would repeat that material.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.shader_binding_table.indexing_hit.sbt_offset_0.no_shaderrecord.0_0
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `indexing_hit` | Tests hit SBT indexing with `sbtRecordOffset = 0` and `sbtRecordStride = 0`. |
| `sbt_offset_0` | The hit SBT buffer is not offset by `shaderGroupBaseAlignment`. |
| `no_shaderrecord` | Each hit SBT slot uses a distinct `chit_<idx>` shader that writes its own index as a constant. |
| `0_0` | `sbtRecordOffset = 0`, `sbtRecordStride = 0`. The hit slot is selected purely by `instanceContributionToHitGroupIndex + geometryIndex * 0`. |

#### Purpose

This rgen shader drives one ray per pixel of the 8x8 result image. Each ray's hit or miss result is written back to the result image at the launching pixel. The host then compares the stored value against the expected SBT-indexing formula.

#### Structural Design

| Step | rgen behavior | Meaning |
|------|---------------|---------|
| 1 | Read `gl_LaunchIDEXT.xy` and convert to a pixel-center origin `(x + 0.5, y + 0.5, 0.5)`. | Each of the 8x8 launch invocations traces one ray into the checkerboard. |
| 2 | Zero-initialize `hitValue`. | Miss pixels remain 0; hit pixels get a non-zero index from the selected closest-hit shader. |
| 3 | Read `trParams` from the UBO and call `traceRayEXT` with `(sbtRecordOffset, sbtRecordStride, missIndex) = (trParams.x, trParams.y, trParams.z)`. | Pushes the per-case SBT indexing parameters into the fixed-function SBT lookup. |
| 4 | `imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue)`. | Writes the SBT-resolved value back to the result image for host comparison. |

The host fills `trParams` per family in `initUniformBuffer` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L268-L304). For `indexing_hit`, `trParams = (sbtRecordOffsetPassedToTraceRay, sbtRecordStride, 0)`. For `indexing_miss`, `trParams = (0, 0, sbtRecordOffsetPassedToTraceRay)`. For `indexing_call`, `trParams` matches the hit family. The shader itself is identical in all three cases; the UBO does the family switching.

#### Shader Code

Reconstructed GLSL from the `initPrograms` literal:

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT uvec4 hitValue;
layout(r32ui, set = 0, binding = 0) uniform uimage2D result;
layout(set = 0, binding = 1) uniform TraceRaysParamsUBO
{
    uvec4 trParams; // x = sbtRecordOffset, y = sbtRecordStride, z = missIndex
};
layout(set = 0, binding = 2) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin     = 0.0;
  float tmax     = 1.0;
  vec3  origin   = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, 0.5f);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  hitValue       = uvec4(0,0,0,0);
  traceRayEXT(topLevelAS, 0, 0xFF, trParams.x, trParams.y, trParams.z, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue);
}
```

#### Additional Info

- The `rgen` shader is generated once and reused across all `indexing_*` cases [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L788-L812). The `updateRayTracingGLSL` post-processing hook rewrites the source for the active Vulkan version.
- The closest-hit shaders are generated per SBT slot. `chit_<idx>` writes `uvec4(idx, 0, 0, 1)`, so the host can read the slot index from the result image. With `shaderrecord`, a single `chit_shaderRecord` shader reads `info` from `layout(shaderRecordEXT)` and writes that, allowing the host to write the slot index into the shader-record data instead of compiling a new shader per slot [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L814-L848).
- The `indexing_call` family adds `chit_call_<idx>` and `call_<idx>` shaders. `chit_call_<idx>` calls `executeCallableEXT(idx, 0)` and copies callable data to the payload; `call_<idx>` writes `uvec4(idx, 0, 0, 1)` to callable data [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L850-L925).
- The `handle_alignment` chit shader reads `srb.data[i]` from `layout(shaderRecordEXT, std430) buffer srbBlock` and writes it to `ssbo.data[gl_LaunchIDEXT.x][i]`. The element type, element count, and shader-record extension are selected at GLSL generation time based on the alignment value [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1324-L1398).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `sbt_offset_*` | No GLSL change. The host adds `sbtOffset * shaderGroupBaseAlignment` bytes to the active SBT buffer address when constructing the SBT region. | [shaderBindingTableOffset](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L472-L473) |
| `shaderrecord` presence | Replaces `chit_<idx>` (and `miss_<idx>`, `call_<idx>`) with the `*_shaderRecord` variant that reads `info` from `layout(shaderRecordEXT)`. The host writes `uvec4(idx, 0, 0, 0)` per record into the SBT buffer. | [shaderRecord variant generation](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L833-L848), [shader-record fill](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L513-L528) |
| `sbtRecordOffset` and `sbtRecordStride` | No GLSL change. The host writes these into the UBO as `trParams.x` and `trParams.y` for HIT and CALL, or routes `sbtRecordOffset` into `trParams.z` for MISS. | [UBO fill](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L279-L298) |
| Extra-bits cases | No GLSL change. The host ORs `~((1u << 4) - 1)` or `~((1u << 16) - 1)` into the value stored in `trParams` for the maximum-offset or maximum-stride case, expecting the implementation to ignore the high bits. | [extra-bits construction](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1670-L1695) |
| `indexing_miss` | The same rgen shader is used; `trParams.z` carries the miss index, and `trParams.x`/`trParams.y` are 0. Miss shaders replace the hit shaders as the indexed region. | [STT_MISS UBO branch](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L286-L289) |
| `indexing_call` | The same rgen shader is used; `chit_call_<idx>` adds `executeCallableEXT(idx, 0)` and `call_<idx>` shaders write to callable data. The callable region is the indexed region. | [STT_CALL shader generation](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L850-L925) |
| `handle_alignment` | Different rgen, chit, and miss shaders. The chit shader is parameterized by alignment, element type (`uint8_t`, `uint16_t`, `uint32_t`), element count, and the corresponding GLSL integer-width extension. The long-vector variant uses `vector<elemType, elementCount>` for the shader-record block. | [handle_alignment shader generation](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1324-L1398) |

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
; Bound: 71
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %hitValue %topLevelAS %_ %result
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
               OpName %TraceRaysParamsUBO "TraceRaysParamsUBO"
               OpMemberName %TraceRaysParamsUBO 0 "trParams"
               OpName %_ ""
               OpName %result "result"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %topLevelAS Binding 2
               OpDecorate %topLevelAS DescriptorSet 0
               OpDecorate %TraceRaysParamsUBO Block
               OpMemberDecorate %TraceRaysParamsUBO 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
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
%TraceRaysParamsUBO = OpTypeStruct %v4uint
%_ptr_Uniform_TraceRaysParamsUBO = OpTypePointer Uniform %TraceRaysParamsUBO
          %_ = OpVariable %_ptr_Uniform_TraceRaysParamsUBO Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_2 = OpConstant %uint 2
         %61 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_61 = OpTypePointer UniformConstant %61
     %result = OpVariable %_ptr_UniformConstant_61 UniformConstant
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
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
         %50 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %uint_0
         %51 = OpLoad %uint %50
         %52 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %uint_1
         %53 = OpLoad %uint %52
         %55 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %uint_2
         %56 = OpLoad %uint %55
         %57 = OpLoad %v3float %origin
         %58 = OpLoad %float %tmin
         %59 = OpLoad %v3float %direct
         %60 = OpLoad %float %tmax
               OpTraceRayKHR %42 %uint_0 %uint_255 %51 %53 %56 %57 %58 %59 %60 %hitValue
         %64 = OpLoad %61 %result
         %66 = OpLoad %v3uint %gl_LaunchIDEXT
         %67 = OpVectorShuffle %v2uint %66 %66 0 1
         %69 = OpBitcast %v2int %67
         %70 = OpLoad %v4uint %hitValue
               OpImageWrite %64 %69 %70 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Acceleration structure setup.** The host builds a checkerboard of triangles on every odd `(x + y)` cell of the 8x8 grid. Triangles are grouped `HIT_GEOMETRY_COUNT = 3` per BLAS, and the BLAS instances are shuffled with a fixed seed so the instance ordering does not follow a simple pattern [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L202-L266). For `indexing_miss`, all instances use `instanceCustomIndex = 0` so any hit routes to `chit_0`; for `indexing_hit` and `indexing_call`, `instanceCustomIndex = i` so each instance contributes a distinct offset to the hit SBT index.
- **UBO fill per family.** `initUniformBuffer` packs `trParams` from the test parameters. HIT and CALL fill `(sbtRecordOffsetPassedToTraceRay, sbtRecordStride, 0)`; MISS fills `(0, 0, sbtRecordOffsetPassedToTraceRay)` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L268-L304).
- **Pipeline construction.** The host adds shader groups in a fixed order: rgen at 0, hit shaders at `1..N`, miss at `N+1`, and (for CALL) callable shaders at `N+2..`. The hit shader count is `HIT_INSTANCE_COUNT + HIT_GEOMETRY_COUNT * MAX_HIT_SBT_RECORD_STRIDE + MAX_SBT_RECORD_OFFSET + 1` to ensure every reachable `(offset, geometryIndex * stride)` combination has a corresponding slot [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L124-L132), [pipeline construction](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L306-L454).
- **SBT construction.** The active region (hit for HIT, miss for MISS, callable for CALL) is given a non-zero `shaderBindingTableOffset = sbtOffset * shaderGroupBaseAlignment` from the start of its buffer. When `shaderRecordPresent`, the active region uses stride `deAlign32(shaderGroupHandleSize + sizeof(tcu::UVec4), shaderGroupHandleSize)` and the host writes `uvec4(idx, 0, 0, 0)` after each shader-group handle, then flushes the writes [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L456-L639).
- **Extra-bits handling.** When `sbtRecordOffset` equals its maximum (`MAX_SBT_RECORD_OFFSET = 3`) or `sbtRecordStride` equals its maximum, the value passed to `traceRayEXT` is OR'd with `~((1u << 4) - 1)` for hit/stride/offset and `~((1u << 16) - 1)` for `missIndex`. The leaf name gains `_extrabits` or `_extraSBTRecordStrideBits` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1670-L1695).
- **Dispatch and copyback.** The host clears the result image to `0xFF000000`, inserts the appropriate image layout barriers, builds the acceleration structures, binds descriptor sets and pipeline, and calls `cmdTraceRays` over `8x8x1`. A `RAY_TRACING_SHADER` to `TRANSFER` memory barrier precedes `cmdCopyImageToBuffer`, then a `TRANSFER` to `HOST` barrier precedes `invalidateMappedMemoryRange` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1034-L1114).
- **Reference image and pass/fail.** `verifyImage` recreates the same checkerboard corners and instance ordering, then sets each hit pixel's reference value to the family-specific formula and each miss pixel's value to the family-specific miss value. The result is compared with `tcu::intThresholdCompare` at zero tolerance [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L641-L709).
- **`handle_alignment` runtime.** The host builds a single BLAS with `geoCount = 32/alignment + 1` triangle geometries translated along X, and a TLAS with one instance. It creates the hit SBT with stride `shaderGroupHandleSize + alignment`, passing per-geometry shader-record data and disabling autoalign so the explicit alignment is preserved. After `cmdTraceRays` over `geoCount x 1 x 1`, the host reads back the SSBO and compares it byte-by-byte against the per-geometry shader-record data, logging the first mismatch [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1405-L1613).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `indexing_hit` | The implementation computed the hit-group SBT index using a different formula than `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`, ignored the `sbtOffset * shaderGroupBaseAlignment` buffer offset, mishandled shader-record data placement, or honored upper bits of `sbtRecordOffset`/`sbtRecordStride` that the spec allows to be ignored. |
| `indexing_miss` | The implementation indexed the miss region using something other than `missIndex`, ignored the SBT buffer offset into the miss region, or honored non-low-16 bits of `missIndex` that the spec allows to be ignored. |
| `indexing_call` | The implementation indexed the callable region using something other than the `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride` value passed to `executeCallableEXT`, or did not preserve that index through the callable-data path. |
| `handle_alignment` | The implementation did not preserve shader-group handle alignment or shader-record data integrity when shader-record buffers pad each handle to a power-of-two alignment between 1 and 32 bytes, including 8-bit, 16-bit, 32-bit, and long-vector shader-record element layouts. |

All four families report failure through the same host-side image or SSBO comparison. The shader itself never writes a fail flag; it writes the SBT-resolved value, and the host compares it against the expected formula.

### Cause Analysis

#### Hit-region SBT index computed incorrectly

**Possible failure symptoms:** An `indexing_hit` case fails `tcu::intThresholdCompare`. Hit pixels in the result image contain values that do not match `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride`, or miss pixels contain non-zero values when the host expected 0.

**Possible implementation causes:** The hit-group index depends on `instanceContributionToHitGroupIndex`, `sbtRecordOffset`, `geometryIndex`, and `sbtRecordStride`. A grounded investigation should check whether the implementation honors the `sbtOffset * shaderGroupBaseAlignment` host-supplied buffer offset when computing the hit region base address, whether it uses the spec-defined formula for the per-ray record offset, and whether it honors only the low 4 bits of `sbtRecordOffset` and `sbtRecordStride` in the `_extrabits` and `_extraSBTRecordStrideBits` leaves. If the `shaderrecord` variant fails but the `no_shaderrecord` variant passes, the issue is more likely in shader-record data placement than in the indexing arithmetic itself.

#### Miss-region SBT index computed incorrectly

**Possible failure symptoms:** An `indexing_miss` case fails the image comparison. Miss pixels contain values that do not match `sbtRecordOffset` (the value passed as `missIndex`), or hit pixels contain non-zero values when `chit_0` was supposed to write 0.

**Possible implementation causes:** The miss index selects the slot directly with no geometry-multiplied stride. A grounded investigation should check whether the implementation honors the `sbtOffset * shaderGroupBaseAlignment` offset into the miss region buffer, and whether it honors only the low 16 bits of `missIndex` in the `_extrabits` leaves. The `_extraSBTRecordStrideBits` suffix does not appear in this family because the stride is fixed at 0.

#### Callable-region SBT index computed incorrectly

**Possible failure symptoms:** An `indexing_call` case fails the image comparison. Hit pixels contain values that do not match `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride`, which is the index passed to `executeCallableEXT` by the closest-hit shader.

**Possible implementation causes:** The callable region is indexed by the literal argument to `executeCallableEXT`, not by the `traceRayEXT` parameters. A grounded investigation should check whether the implementation uses the `executeCallableEXT` argument directly as the callable SBT record index, whether the callable-data write in `call_<idx>` is correctly visible to the closest-hit shader's read, and whether the `sbtOffset * shaderGroupBaseAlignment` offset is honored for the callable region. If the same `sbtOffset` and `sbtRecordOffset` values pass under `indexing_hit` but fail under `indexing_call`, the issue is more likely in the callable SBT path than in the trace-ray SBT path.

#### Shader-group handle alignment or shader-record data corruption

**Possible failure symptoms:** A `handle_alignment` case fails the byte-by-byte SSBO comparison. The host logs "Unexpected output data" with the actual byte value and the expected byte value.

**Possible implementation causes:** The host constructs the hit SBT with explicit record stride `shaderGroupHandleSize + alignment` and disables autoalign, so the implementation must read each shader-group handle from an address that is `alignment` bytes apart from the previous one. A grounded investigation should check whether the implementation honors `shaderGroupHandleAlignment` for the chosen alignment, whether shader-record data of 8-bit, 16-bit, or 32-bit element types is correctly read through `layout(shaderRecordEXT)`, and whether the long-vector variant correctly maps `vector<elemType, elementCount>` to the same memory layout as the array variant. The `alignment=1` case requires `shaderInt8` and `storageBuffer8BitAccess`; the `alignment=2` case requires `shaderInt16` and `storageBuffer16BitAccess`; failures in those specific sub-cases point to 8-bit or 16-bit storage handling rather than alignment itself.

#### Host-side reference or copyback error

**Possible failure symptoms:** The host reports failure but shader-side reasoning does not explain the mismatch. The result image or SSBO contains values that look reasonable but do not match the host-recomputed reference.

**Possible implementation causes:** The host recreates the checkerboard corner ordering and instance offsets in `verifyImage` using the same fixed seed, then recomputes the expected per-pixel value. Source-level investigation would be needed to distinguish an actual device-side SBT bug from a host-side reference computation bug, an image-clear or barrier issue, or an SSBO invalidation issue. The fixed `SBT_RANDOM_SEED = 1410` makes the corner ordering deterministic, so a reference-computation bug would likely affect many cases consistently.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with `rayTracingPipeline == VK_TRUE` and `accelerationStructure == VK_TRUE` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L765-L780), [handle_alignment support](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1278-L1289).
- `handle_alignment` skips alignments below `VkPhysicalDeviceRayTracingPropertiesKHR::shaderGroupHandleAlignment` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1287-L1289).
- `handle_alignment` with `alignment=1` requires `shaderInt8` and `storageBuffer8BitAccess`; `alignment=2` requires `shaderInt16` (core feature) and `storageBuffer16BitAccess` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1290-L1316).
- The `_longvec` variants require `VK_EXT_shader_long_vector` with `longVector == VK_TRUE` and are skipped on VulkanSC [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1318-L1321), [VulkanSC gating](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1736-L1739).

### Design-based pruning

- `indexing_miss` and `indexing_call` skip the `sbtRecordStride == maxSbtRecordStride` case because the stride is not part of their indexing formula; only `indexing_hit` uses the full stride range [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1667-L1685).
- `indexing_miss` uses 16-bit masking for the extra-bits variant because the spec allows the upper bits of `missIndex` to be ignored; `indexing_hit` and `indexing_call` use 4-bit masking for `sbtRecordOffset` and `sbtRecordStride` [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1670-L1676).
- The `shaderrecord` and `no_shaderrecord` variants are both generated for every `sbt_offset_*` and `sbtRecordOffset_sbtRecordStride` combination because they stress different code paths: per-slot constant shaders test indexing alone, while the shader-record variant tests both indexing and per-record data placement.
- `handle_alignment` geometry count scales as `32/alignment + 1` so that the test exercises every possible alignment value within a 32-byte window. This means `alignment=1` produces 33 geometries and `alignment=32` produces 2 geometries [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1182-L1185).

## Key Takeaways

- The four families share an SBT-focused scope but exercise distinct properties: hit indexing, miss indexing, callable indexing, and shader-group handle alignment.
- The rgen shader is identical across the `indexing_*` families; the host-side UBO and SBT construction do the family switching. This keeps the device-side test surface small.
- The `_extrabits` and `_extraSBTRecordStrideBits` leaves are not separate behavior; they verify the spec rule that implementations may ignore the upper bits of `sbtRecordOffset`, `sbtRecordStride`, and `missIndex`.
- The `shaderrecord` variants are not separate behavior either; they verify that shader-record data placement does not corrupt the SBT index lookup, by routing the slot index through `layout(shaderRecordEXT)` instead of through a per-slot constant shader.
- `handle_alignment` is the only family that does not use the indexing formula. It uses shader-record buffers as padding to drive power-of-two alignment, then reads the data back through an SSBO for a byte-by-byte comparison.
- Failure analysis is per-family: hit indexing, miss indexing, callable indexing, and alignment/data integrity each have their own cause analysis in `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category root registration | [vktRayTracingShaderBindingTableTests.cpp#L1617-L1646](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1617-L1646) | Builds the `shader_binding_table` group and attaches all four direct children. |
| Indexing family loop | [vktRayTracingShaderBindingTableTests.cpp#L1622-L1722](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1622-L1722) | Defines the `indexing_hit`/`indexing_miss`/`indexing_call` matrix and the extra-bits scheme. |
| Handle-alignment family loop | [vktRayTracingShaderBindingTableTests.cpp#L1724-L1743](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1724-L1743) | Defines the alignment values and long-vector variants. |
| `TestParams` struct | [vktRayTracingShaderBindingTableTests.cpp#L110-L122](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L110-L122) | Captures sbtOffset, sbtRecordOffset/Stride values, the versions passed to traceRay, and shaderRecordPresent. |
| UBO fill per family | [vktRayTracingShaderBindingTableTests.cpp#L268-L304](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L268-L304) | Maps `trParams.x/y/z` to sbtRecordOffset, sbtRecordStride, or missIndex per family. |
| SBT construction per family | [vktRayTracingShaderBindingTableTests.cpp#L456-L639](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L456-L639) | Shows `shaderBindingTableOffset` math, shader-record aligned size, and shader-record buffer fills. |
| Reference image computation | [vktRayTracingShaderBindingTableTests.cpp#L641-L709](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L641-L709) | Host-side re-derivation of expected per-pixel shader index for each family. |
| Indexing support checks | [vktRayTracingShaderBindingTableTests.cpp#L765-L780](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L765-L780) | Feature gates for the indexing families. |
| Indexing shader generation | [vktRayTracingShaderBindingTableTests.cpp#L782-L944](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L782-L944) | Generates rgen, chit_*, miss_*, call_*, and the *_shaderRecord variants. |
| Indexing runtime | [vktRayTracingShaderBindingTableTests.cpp#L961-L1124](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L961-L1124) | Builds resources, runs `cmdTraceRays`, copies back, and verifies the result image. |
| Handle-alignment params struct | [vktRayTracingShaderBindingTableTests.cpp#L1169-L1237](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1169-L1237) | Defines alignment, geometry count, element type, and per-geometry record data. |
| Handle-alignment support checks | [vktRayTracingShaderBindingTableTests.cpp#L1278-L1322](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1278-L1322) | Feature and property gates for the alignment family. |
| Handle-alignment shader generation | [vktRayTracingShaderBindingTableTests.cpp#L1324-L1398](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1324-L1398) | Parameterizes the chit shader by alignment, element type, and long-vector usage. |
| Handle-alignment runtime | [vktRayTracingShaderBindingTableTests.cpp#L1405-L1613](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1405-L1613) | Builds AS, pipeline, SBT with explicit alignment, runs `cmdTraceRays`, and verifies SSBO contents byte-by-byte. |
