## Overview

**Core question:** Do `texture*Offset` operations accept an offset whose value varies by shader invocation, and return the texel selected by that offset?

- [`vktImageNonUniformOffsetSampleTests.cpp`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp) implements the `image.non_uniform_offset_sample` test family.
- Each case samples a known 3×3 texture from fixed base coordinates. A shuffled offset array in a uniform buffer chooses the actual texel separately for each invocation.
- The test covers ordinary, texel-fetch, explicit-LOD, projective, and projective explicit-LOD offset operations in the vertex, fragment, and eligible compute stages.
- This page explains the generated case matrix, representative compute shader, resource flow, result comparison, and the exclusions in that matrix.

## Background Knowledge

- **Texture offsets.** GLSL `texture*Offset` operations add an integer texel offset to the coordinate used by a texture operation. An offset is usually a compile-time constant; these tests exercise the `GL_EXT_texture_offset_non_const` path, where the shader reads it from data that varies between invocations.
- **Implicit and explicit LOD.** `textureOffset` and `textureProjOffset` select a mip level from derivatives, while `texelFetchOffset`, `textureLodOffset`, and `textureProjLodOffset` take an explicit LOD. Compute shaders have no ordinary implicit derivatives, which determines part of the generated-case pruning.

## Registration Hierarchy

```text
image.non_uniform_offset_sample
├── texture_offset
├── texel_fetch_offset
├── texture_lod_offset
├── texture_proj_offset
└── texture_proj_lod_offset
```

[`createImageNonUniformOffsetSampleTests()`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L714-L772) creates these five test families and generates their mip-level and shader-stage leaves. The Vulkan and Vulkan SC mustpass lists each contain the resulting 22 executable cases in [`non-uniform-offset-sample.txt`](../../../mustpass/main/vk-default/image/non-uniform-offset-sample.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Offset operation | `texture_offset`, `texel_fetch_offset`, `texture_lod_offset`, `texture_proj_offset`, `texture_proj_lod_offset` | Selects the GLSL texture operation and whether it uses integer coordinates, projection, or an explicit LOD. | [Operation selection](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L209-L234) |
| Mip-level form | `single_mip`, `multi_mip` | `single_mip` creates one mip level. `multi_mip` creates four and samples the last one, so it is generated only for operations with an explicit LOD argument. | [Image and LOD setup](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L310-L343) and [factory pruning](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L747-L765) |
| Shader stage | `vert`, `frag`, `comp` | Selects the shader stage that reads the offset and performs the texture operation. Compute leaves exist only for explicit-LOD operations. | [Stage-specific programs](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L236-L301) |
| Texture and result extent | `3×3×1` | Nine invocations address nine output pixels, and the nine shuffled offsets cover every texel in the sampled 3×3 level. | [Fixed extent](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L134-L138) and [offset generation](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L456-L468) |
| Format and sampling state | `VK_FORMAT_R8G8B8A8_UNORM`, nearest filtering, clamp-to-edge | A coordinate-derived color makes every source texel distinguishable. Nearest filtering keeps the expected lookup exact apart from UNORM conversion tolerance. | [Texture initialization](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L345-L376) and [sampler setup](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L379-L399) |
| Offset values | all `(x, y)` pairs where `x, y` are in `0..2`, shuffled with a parameter-derived seed | The offsets select all nine texels but their order differs with stage, operation, and mip form. The values remain inside Vulkan's required texture-offset range. | [Offset construction](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L456-L477) |

## Behavior Parameters

The primary behavioral axis is **offset operation**. Each family reads an invocation-varying `ivec2` from the uniform buffer, but it passes that value to a different GLSL operation.

### `texture_offset`: implicit-LOD sampled lookup

This family calls `textureOffset` with normalized two-component coordinates. The fixed coordinate points to the first texel center, so the non-uniform offset selects the texel that produces each output pixel. It has `single_mip_vert` and `single_mip_frag` leaves.

### `texel_fetch_offset`: explicit-LOD integer lookup

This family calls `texelFetchOffset` with integer texel coordinates and `int(pc.lod)`. It covers both single- and multi-mip forms in all three supported stages, including compute.

### `texture_lod_offset`: explicit-LOD sampled lookup

This family calls `textureLodOffset` with normalized coordinates and the float LOD in push constants. It separates dynamic-offset handling from implicit derivative selection and includes all stage and mip combinations.

### `texture_proj_offset`: implicit-LOD projective lookup

This family calls `textureProjOffset` with three-component projective coordinates. The test sets the projective divisor to one, so the projected base coordinate still targets the first texel center; only the offset selects the sampled texel. It has vertex and fragment `single_mip` leaves.

### `texture_proj_lod_offset`: explicit-LOD projective lookup

This family calls `textureProjLodOffset`, combining projective coordinates, a push-constant LOD, and the dynamic offset. It includes all three stages and both mip forms.

## Shader Analysis

[`NonUniformOffsetCase::initPrograms()`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L190-L302) generates the shader strings. The representative case below uses the compute-stage explicit-LOD fetch path because it exposes the per-invocation index, uniform-buffer offset load, sampled image fetch, and storage-image output in one shader.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.non_uniform_offset_sample.texel_fetch_offset.multi_mip_comp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `texel_fetch_offset` | Uses `texelFetchOffset` with integer coordinates and an explicit LOD. |
| `multi_mip` | Creates four mip levels and passes the final mip index through `pc.lod`. |
| `comp` | Uses a 3×3 local workgroup; each invocation loads a different offset and writes one output pixel. |

#### Purpose

The shader fetches the top-left texel coordinate at the requested LOD, adds a per-invocation offset from binding 0, and stores the fetched color at the matching local invocation coordinate. The host-side reference uses the same shuffled offset entry for that output pixel.

#### Structural Design

| Shader element | Action | Tested property |
|----------------|--------|-----------------|
| `gl_LocalInvocationID` | Flattens the 3×3 local coordinate to an index in `0..8`. | Each compute invocation loads a distinct uniform-buffer entry. |
| `offsetData.offsets[index].xy` | Reads the selected `ivec2` offset. | The operation receives a non-constant offset. |
| `texelFetchOffset` | Fetches at fixed integer coordinates, explicit LOD, and loaded offset. | Tests dynamic offset handling for explicit-LOD texel fetch. |
| `imageStore` | Writes the fetched color to the output image at the local coordinate. | Makes each invocation's lookup visible to host comparison. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_texture_offset_non_const : enable

/// Push constants provide the fixed base coordinate, output size, and selected LOD.
layout (push_constant, std430) uniform PCBlock { vec4 coords; vec2 size; float lod; } pc;
/// Binding 0 stores nine shuffled offsets as std140-compatible ivec4 values; the shader uses xy.
layout (set=0, binding=0) uniform OffsetDataBlock { ivec4 offsets[9]; } offsetData;
/// Binding 1 is the nearest-filtered sampled 2D texture.
layout (set=0, binding=1) uniform sampler2D inTex;
/// Binding 2 is the 3×3 RGBA8 storage image that carries the sampled result to readback.
layout (rgba8, set=0, binding=2) uniform image2D outColor;
/// One workgroup covers the complete 3×3 result image.
layout (local_size_x=3, local_size_y=3, local_size_z=1) in;

void main(void) {
    /// Flatten the local coordinate so each invocation selects one shuffled offset.
    const uint offsetIndex = (gl_LocalInvocationID.y * gl_WorkGroupSize.x) + gl_LocalInvocationID.x;
    const ivec2 offset = offsetData.offsets[offsetIndex].xy;
    const ivec2 texCoords = ivec2(pc.coords.xy);
    const vec4 pixel = texelFetchOffset(inTex, texCoords, int(pc.lod), offset);
    imageStore(outColor, ivec2(gl_LocalInvocationID.xy), pixel);
}
```

#### Additional Info

- The source builds all stage variants with `ShaderBuildOptions::FLAG_ALLOW_NON_CONST_OFFSETS` and SPIR-V 1.0. The GLSL extension appears in the generated compute, fragment, and tested vertex shaders.
- The source stores offsets as `ivec4` to avoid `std140` layout ambiguity, although the shader uses only `xy`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Offset operation | Replaces the `texelFetchOffset` statement with `textureOffset`, `textureLodOffset`, `textureProjOffset`, or `textureProjLodOffset`; coordinate type and LOD operand change with that operation. | [Generated operation statements](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L209-L234) |
| Shader stage | Compute indexes by `gl_LocalInvocationID`; fragment uses `gl_FragCoord`; vertex derives a pixel ID from the input position and passes the sampled result through a varying. | [Stage-specific index generation](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L236-L301) |
| Mip-level form | `multi_mip` selects the last of four levels through `pc.lod`; only explicit-LOD operations receive this form. | [Push constants](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L480-L488) and [factory pruning](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L747-L756) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 76
; Schema: 0
               OpCapability Shader
               OpCapability ImageGatherExtended
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID
               OpExecutionMode %main LocalSize 3 3 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_texture_offset_non_const"
               OpName %main "main"
               OpName %offsetIndex "offsetIndex"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %offset "offset"
               OpName %OffsetDataBlock "OffsetDataBlock"
               OpMemberName %OffsetDataBlock 0 "offsets"
               OpName %offsetData "offsetData"
               OpName %texCoords "texCoords"
               OpName %PCBlock "PCBlock"
               OpMemberName %PCBlock 0 "coords"
               OpMemberName %PCBlock 1 "size"
               OpMemberName %PCBlock 2 "lod"
               OpName %pc "pc"
               OpName %pixel "pixel"
               OpName %inTex "inTex"
               OpName %outColor "outColor"
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %_arr_v4int_uint_9 ArrayStride 16
               OpDecorate %OffsetDataBlock Block
               OpMemberDecorate %OffsetDataBlock 0 Offset 0
               OpDecorate %offsetData Binding 0
               OpDecorate %offsetData DescriptorSet 0
               OpDecorate %PCBlock Block
               OpMemberDecorate %PCBlock 0 Offset 0
               OpMemberDecorate %PCBlock 1 Offset 16
               OpMemberDecorate %PCBlock 2 Offset 24
               OpDecorate %inTex Binding 1
               OpDecorate %inTex DescriptorSet 0
               OpDecorate %outColor Binding 2
               OpDecorate %outColor DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_3 = OpConstant %uint 3
     %uint_0 = OpConstant %uint 0
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
      %v4int = OpTypeVector %int 4
     %uint_9 = OpConstant %uint 9
%_arr_v4int_uint_9 = OpTypeArray %v4int %uint_9
%OffsetDataBlock = OpTypeStruct %_arr_v4int_uint_9
%_ptr_Uniform_OffsetDataBlock = OpTypePointer Uniform %OffsetDataBlock
 %offsetData = OpVariable %_ptr_Uniform_OffsetDataBlock Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v4int = OpTypePointer Uniform %v4int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
    %v2float = OpTypeVector %float 2
    %PCBlock = OpTypeStruct %v4float %v2float %float
%_ptr_PushConstant_PCBlock = OpTypePointer PushConstant %PCBlock
         %pc = OpVariable %_ptr_PushConstant_PCBlock PushConstant
%_ptr_PushConstant_v4float = OpTypePointer PushConstant %v4float
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %52 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %53 = OpTypeSampledImage %52
%_ptr_UniformConstant_53 = OpTypePointer UniformConstant %53
      %inTex = OpVariable %_ptr_UniformConstant_53 UniformConstant
      %int_2 = OpConstant %int 2
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
         %66 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_66 = OpTypePointer UniformConstant %66
   %outColor = OpVariable %_ptr_UniformConstant_66 UniformConstant
     %v2uint = OpTypeVector %uint 2
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_3 %uint_3 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%offsetIndex = OpVariable %_ptr_Function_uint Function
     %offset = OpVariable %_ptr_Function_v2int Function
  %texCoords = OpVariable %_ptr_Function_v2int Function
      %pixel = OpVariable %_ptr_Function_v4float Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_1
         %15 = OpLoad %uint %14
         %17 = OpIMul %uint %15 %uint_3
         %19 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %20 = OpLoad %uint %19
         %21 = OpIAdd %uint %17 %20
               OpStore %offsetIndex %21
         %33 = OpLoad %uint %offsetIndex
         %35 = OpAccessChain %_ptr_Uniform_v4int %offsetData %int_0 %33
         %36 = OpLoad %v4int %35
         %37 = OpVectorShuffle %v2int %36 %36 0 1
               OpStore %offset %37
         %46 = OpAccessChain %_ptr_PushConstant_v4float %pc %int_0
         %47 = OpLoad %v4float %46
         %48 = OpVectorShuffle %v2float %47 %47 0 1
         %49 = OpConvertFToS %v2int %48
               OpStore %texCoords %49
         %56 = OpLoad %53 %inTex
         %57 = OpLoad %v2int %texCoords
         %60 = OpAccessChain %_ptr_PushConstant_float %pc %int_2
         %61 = OpLoad %float %60
         %62 = OpConvertFToS %int %61
         %63 = OpLoad %v2int %offset
         %64 = OpImage %52 %56
         %65 = OpImageFetch %v4float %64 %57 Lod|Offset %62 %63
               OpStore %pixel %65
         %69 = OpLoad %66 %outColor
         %71 = OpLoad %v3uint %gl_LocalInvocationID
         %72 = OpVectorShuffle %v2uint %71 %71 0 1
         %73 = OpBitcast %v2int %72
         %74 = OpLoad %v4float %pixel
               OpImageWrite %69 %73 %74
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a `VK_FORMAT_R8G8B8A8_UNORM` texture and fills the selected mip level with a 3×3 color ramp: red varies by x coordinate, green by y coordinate, blue is `0.5`, and alpha is `1.0`.
- It creates and shuffles the nine offsets, uploads them in a host-visible uniform buffer, and binds that buffer at descriptor binding 0. The sampled texture and sampler use binding 1; compute cases also bind the storage output image at binding 2.
- The push constants set the base coordinate to the first texel center, the size to `(3, 3)`, and the LOD to the last mip level. Thus the offset, rather than the base coordinate, determines the source texel.
- For a compute case, one 3×3×1 local workgroup writes the storage image. For graphics, the fragment path draws a full-screen triangle strip and the vertex path draws one triangle for each output pixel. The test copies the output image to host-visible memory after the draw or dispatch.
- The reference image reads the host texture at `offsets[y * 3 + x]` for each output pixel. `tcu::floatThresholdCompare` compares the result and reference with an RGB threshold of `0.005`; a mismatch fails the test. See [execution and comparison](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L646-L709).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `texture_offset` | Incorrect lowering or execution of a non-constant offset in an implicit-LOD sampled lookup; incorrect fragment or vertex offset indexing. |
| `texel_fetch_offset` | Incorrect lowering or execution of a non-constant offset, integer-coordinate fetch, or explicit LOD operand. |
| `texture_lod_offset` | Incorrect lowering or execution of a non-constant offset in an explicit-LOD sampled lookup. |
| `texture_proj_offset` | Incorrect handling of the non-constant offset together with projective coordinate processing in an implicit-LOD lookup. |
| `texture_proj_lod_offset` | Incorrect handling of the non-constant offset, projection, or explicit LOD in the combined operation. |

### Cause Analysis

#### Non-constant offset operation handling

**Possible failure symptoms:** One or more output pixels differ from the color at the shuffled offset selected for that invocation. The comparison log identifies the differing image values.

**Possible implementation causes:** Shader compilation or execution may fail to preserve the offset loaded from the uniform buffer as the `Offset` operand of the texture instruction. This page's reconstructed fetch shader shows that lowering as `OpImageFetch` with `Lod|Offset`; the generated GLSL uses the extension and CTS build option that permit this operand form.

#### Operation-specific coordinate or LOD handling

**Possible failure symptoms:** Failures occur only in a particular operation family, or only in `multi_mip` leaves, while other offset operations pass.

**Possible implementation causes:** An implementation may mishandle integer versus normalized coordinates, an explicit LOD, or the projective coordinate division while composing the texture operation with its offset. The source fixes the projected divisor at one and the base coordinate at the top-left texel center, which limits the expected result to the chosen offset texel.

#### Stage-specific offset indexing and output transport

**Possible failure symptoms:** A family passes in one stage but produces misplaced or repeated colors in another stage.

**Possible implementation causes:** The stages derive their uniform-buffer index from different built-ins or inputs: local invocation coordinates in compute, `gl_FragCoord` in fragment, and the generated primitive position in vertex. A fault in that indexing path, stage interpolation/output transport, or storage-image/color-attachment write can therefore appear as a stage-specific mismatch. The source-level test does not isolate these possibilities further.

## Case Pruning

### Requirement-based pruning

Every test case requires `VK_KHR_maintenance8` through [`NonUniformOffsetCase::checkSupport()`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L154-L180). Cases that do not meet that device-functionality requirement are not run.

### Design-based pruning

- `multi_mip` leaves exist only for `texel_fetch_offset`, `texture_lod_offset`, and `texture_proj_lod_offset`, because those operations accept an explicit LOD. The case constructor asserts that same relationship.
- Compute leaves are excluded for `texture_offset` and `texture_proj_offset`. Those implicit-LOD operations need derivatives, and the source deliberately avoids the separate compute-derivatives extension path.
- The test does not generate `textureGrad*` operations. The source explicitly excludes them to keep the test focused on non-uniform offsets.

## Key Takeaways

- Each invocation obtains its own offset from a shuffled uniform-buffer array, so the test requires the implementation to preserve a dynamically selected offset through shader compilation and texture execution.
- The fixed base coordinate and identifiable 3×3 texture turn every output pixel into a direct check of one selected offset entry.
- The generated matrix separates texture-operation forms, LOD forms, and shader stages while omitting combinations that cannot supply the needed implicit derivatives.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters and support check | [`TestParams` and `NonUniformOffsetCase`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L110-L180) | Defines the stage, operation, mip form, deterministic shuffle seed, and `VK_KHR_maintenance8` requirement. |
| Generated shader programs | [`NonUniformOffsetCase::initPrograms()`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L190-L302) | Selects each GLSL operation and constructs the compute, fragment, and vertex programs. |
| Resource setup and offset data | [iteration setup](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L306-L525) | Creates the texture, sampler, output image, descriptor bindings, push constants, and shuffled offset buffer. |
| Dispatch, readback, and comparison | [execution and verification](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L527-L709) | Submits the selected pipeline, reads back the output, builds the reference image, and compares it. |
| Registration factory | [`createImageNonUniformOffsetSampleTests()`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L714-L772) | Registers the five test families and applies the stage/mip pruning rules. |
