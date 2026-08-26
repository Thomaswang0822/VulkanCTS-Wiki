## Overview

**Core question:** does the implementation treat `vkCmdCopyImage` as a byte-exact memcpy and honor format-mutable, block-texel-view-compatible image views when an image is copied and then sampled through a view of a different but size-compatible format?

- Covers the implementation-bearing `reinterpret` test family under `api.copy_and_blit`, registered through the `copy_and_blit` dispatcher in `vktApiCopiesAndBlittingTests.cpp`.
- The single implementation file `vktApiCopiesAndBlittingReinterpretTests.cpp` hosts the `ReinterpretTestInstance` test instance, the `ReinterpretTestCase` test case, and the `createReinterpretationTests()` registration function.
- Two intermediate nodes (`1d`, `2d`) under the test family each carry three test case leaves, one per format pair.
- Three format pairs cover the supported reinterpretation scenarios: uncompressed 32-bit (`B10G11R11_UFLOAT_PACK32` ↔ `R16G16_SFLOAT`), compressed 64-bit block (`BC1_RGB_UNORM_BLOCK` ↔ `R32G32_UINT`), and compressed 128-bit block (`BC3_UNORM_BLOCK` ↔ `R32G32B32A32_UINT`).
- Each leaf performs two independent verifications: a copy check (destination bytes equal source bytes after `vkCmdCopyImage`) and a sampling check (`texelFetch` through the view-format `VkImageView` returns the reinterpreted bytes). A failure in either check fails the case.
- The page explains which Vulkan feature each format pair exercises, how the verification mechanism differs between uncompressed and compressed cases, and what a failure of each leaf points to.

## Background Knowledge

- **Size-compatible format copying.** Vulkan permits `vkCmdCopyImage` between formats whose texel block size in bytes is identical, and models the operation as a byte-for-byte memcpy; the implementation must not reinterpret channels or convert between formats. A `VkImage` created with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` may be viewed through a `VkImageView` of a different format from the image format, provided the view format is size-compatible.
- **Block-texel-view-compatible compressed images.** For compressed formats, `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` allows an uncompressed view whose texel size matches the compressed block size in bytes; `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` lets the image be created with usage flags legal for the view format but not necessarily for the compressed image format. Both flags require `VK_KHR_maintenance2` (Vulkan 1.1+). One view texel corresponds to one compressed block in memory.
- **1D exception for compressed copy regions.** VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152 require that for `VK_IMAGE_TYPE_1D` compressed images, only the x-dimensions of `srcOffset` / `dstOffset` / `extent` are scaled by the block width; the y-dimensions are effectively ignored because the image height is 1. For `VK_IMAGE_TYPE_2D`, both x and y are scaled by block width and height respectively. The `1d` and `2d` intermediate nodes exercise this distinction.

## Registration Hierarchy

```text
api.copy_and_blit.reinterpret
├── 1d
└── 2d
```

Each intermediate node carries three test case leaves named `copy_<imageFormatStr>_sample_<viewFormatStr>`, identical between `1d` and `2d`. The `reinterpret` test family is added directly under `copy_and_blit` by [`createReinterpretationTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1119) and registered by the dispatcher at [`vktApiCopiesAndBlittingTests.cpp#L290`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L290). Mustpass lists six leaves: `dEQP-VK.api.copy_and_blit.reinterpret.{1d,2d}.copy_{b10g11r11_ufloat_pack32_sample_r16g16_sfloat, bc1_rgb_unorm_block_sample_r32g32_uint, bc3_unorm_block_sample_r32g32b32a32_uint}`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type | `VK_IMAGE_TYPE_1D`, `VK_IMAGE_TYPE_2D` | Selects the `1d` or `2d` intermediate node; controls whether the 1D exception for compressed block-size scaling applies | [`imageTypes` array](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1139) |
| Format pair (image ↔ view) | `B10G11R11_UFLOAT_PACK32` ↔ `R16G16_SFLOAT`; `BC1_RGB_UNORM_BLOCK` ↔ `R32G32_UINT`; `BC3_UNORM_BLOCK` ↔ `R32G32B32A32_UINT` | Selects the test case leaf; controls which Vulkan feature is exercised and which verification mechanism is used | [`fmtPairs` array](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1128-L1132) |
| Image extent | `default1dExtent` (`defaultSize`×1×1) for 1D; `defaultExtent` (`defaultSize`×`defaultSize`×1) for 2D | Fixed per image type; only the dimensions the test needs | [`imageTypes` array](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1139) |
| Copy region | Single whole-image `VkImageCopy` region | One copy per test; no partial or multi-region variants | [`testCopy` initialization](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1173-L1179) |
| Tiling | `VK_IMAGE_TILING_OPTIMAL` only | Fixed by `DE_ASSERT` in the test case constructor | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L896`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L896) |
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATED` only | Fixed by `DE_ASSERT` | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L897`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L897) |
| Queue selection | `Universal` only | Fixed by `DE_ASSERT`; no transfer-only variants | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L898`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L898) |
| Command variant | `vkCmdCopyImage` only | The test instance supports `COPY_COMMANDS_2`, but registration does not set the flag, so all mustpass leaves use `vkCmdCopyImage` | [`copyParams` initialization](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1155-L1185) |
| Image create flags | `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` when image format differs from view format; plus `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` and `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` when the image format is compressed | The flags under test: format-mutable views for the uncompressed pair, block-texel-view-compatible views for the compressed pairs | [constructor image creation](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L91-L96) |

## Behavior Parameters

The primary behavioral axis is the **test case leaf**: the format pair, registered identically under each `1d` / `2d` intermediate node. Each format pair changes which Vulkan feature is exercised (`MUTABLE_FORMAT_BIT` alone versus `BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` plus `EXTENDED_USAGE_BIT`), which verification mechanism is used (host-side float compare versus compute-shader green/red), and which block size class is covered. The `1d` / `2d` intermediate node is a secondary axis that changes image type and exercises the 1D exception for compressed-format copy regions.

### `copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat` — uncompressed 32-bit reinterpretation

Image format `VK_FORMAT_B10G11R11_UFLOAT_PACK32` (32 bits, 3 channels) is copied and sampled through a `VK_FORMAT_R16G16_SFLOAT` view (32 bits, 2 channels). Both formats share the same 32-bit texel size, so `formatsAreCompatible()` admits the pair, and the image is created with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` alone. The copy is verified host-side: `readImage(destination)` is compared against a host-computed reference produced by `copyRegionToTextureLevel`, which applies the source format to the destination buffer to mimic the spec's memcpy semantics. The sampling is verified by reading back the rendered color attachment and comparing against the source texture data reinterpreted through the view format. Both comparisons use `tcu::floatThresholdCompare` with threshold `0.01`. This pair isolates the simplest reinterpretation case, without compressed-format handling.

### `copy_bc1_rgb_unorm_block_sample_r32g32_uint` — compressed 64-bit block reinterpretation

Image format `VK_FORMAT_BC1_RGB_UNORM_BLOCK` (4×4 block, 64 bits per block) is copied and sampled through a `VK_FORMAT_R32G32_UINT` view (64 bits, 2 components). One view texel corresponds to one BC1 block in memory. The image is created with `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT | VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT | VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. Compressed texels cannot be seeded via `uploadImage`, so a compute shader `compFill` writes a hardcoded 64-bit pattern (mnemonic "blue") into the source and a different pattern (mnemonic "red") into the destination via `imageStore` through the view format. After `vkCmdCopyImage`, the destination must hold the "blue" pattern in every block; a second compute shader `compVerify` reads each destination texel through the view format, compares against the expected pattern, and writes green (match) or red (mismatch) to an `R8G8B8A8_UNORM` output image. The host reads the output back and compares against an all-green reference. The "blue" and "red" labels are mnemonic; the test verifies byte patterns, not colors.

### `copy_bc3_unorm_block_sample_r32g32b32a32_uint` — compressed 128-bit block reinterpretation

Image format `VK_FORMAT_BC3_UNORM_BLOCK` (4×4 block, 128 bits per block) is copied and sampled through a `VK_FORMAT_R32G32B32A32_UINT` view (128 bits, 4 components). One view texel corresponds to one BC3 block in memory. The image creation flags and the verification mechanism are identical to the BC1 case; only the block size, the view format's component count, and the hardcoded bit pattern constants differ. This pair extends BC1 coverage to 128-bit blocks, so both supported block sizes for block-texel-view compatibility are exercised.

## Shader Analysis

This family’s shaders are verification infrastructure, but the selected compressed case makes their dataflow material: compute writes establish exact BC3 block bytes, the fragment shader samples them through the alternate view, and compute verification turns every block comparison into a green/red verdict.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.api.copy_and_blit.reinterpret.2d.copy_bc3_unorm_block_sample_r32g32b32a32_uint
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `2d` / `VK_IMAGE_TYPE_2D` | The 64×64 BC3 image is addressed as a 16×16 grid of 4×4 compressed blocks; both x and y copy-region dimensions are scaled by the BC3 block dimensions. |
| `BC3_UNORM_BLOCK` → `R32G32B32A32_UINT` | A 128-bit BC3 block is exposed as one `uvec4` texel through a block-texel-view-compatible, mutable image view. |
| `compFill` + `compVerify` with `frag` sampling | The source and destination receive distinct known patterns, `vkCmdCopyImage` must preserve the source bytes, and both storage-image verification and sampled rendering must observe the copied pattern. |

#### Purpose

The shaders establish and inspect exact 128-bit block data while the host tests that `vkCmdCopyImage` copies BC3 bytes unchanged and that the destination can be viewed as `R32G32B32A32_UINT`. A mismatch becomes a red texel; a correct block becomes green.

#### Structural Design

| Stage | Shader-visible dataflow | Verdict relevance |
|-------|-------------------------|-------------------|
| `compFill` | One invocation per block writes the expected “blue” `uvec4` to `srcImg` and a different “red” `uvec4` to `dstImg`. | Creates distinguishable pre-copy bytes without compressed-texture upload. |
| `frag` | Full-screen rasterization converts `texCoord` to a 16×16 block coordinate, then `texelFetch` reads the source through the `R32G32B32A32_UINT` view. | Checks the sampling path for the alternate view format. |
| `compVerify` | One invocation per block loads `dstImg`, compares all four uint components with the expected blue pattern, and stores green or red in `outputImg`. | Provides the exact copy and sampling verdict consumed by the host. |

#### Shader Code

##### Compute Fill Shader

```glsl
#version 450
/// The source BC3 image is viewed as four unsigned 32-bit words per block.
layout(set = 0, binding = 0, rgba32ui) uniform highp uimage2D srcImg;
/// The destination receives a different pattern so the copy is observable.
layout(set = 0, binding = 1, rgba32ui) uniform highp uimage2D dstImg;
/// One invocation handles one block-view texel.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main() {
    /// The source pattern is retained by vkCmdCopyImage when the copy is byte-exact.
    uvec4 srcColor = uvec4(4294967295u, 4294967295u, 2031647, 0u); // blue
    /// The destination pattern makes an incorrect or missing copy observable.
    uvec4 dstColor = uvec4(4294967295u, 4294967295u, 4160813056u, 0u); // red
    imageStore(srcImg, ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y), srcColor);
    imageStore(dstImg, ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y), dstColor);
}
```

##### Sampling Fragment Shader

```glsl
#version 450
/// The source image is sampled through the alternate unsigned-integer view.
layout(set=0, binding=0) uniform usampler2D tex;
/// Vertex shader coordinates cover the 16×16 block-view extent.
layout(location=0) in vec2 texCoord;
/// The attachment uses the same four-component unsigned view representation.
layout(location=0) out uvec4 outColor;

void main() {
    /// One fragment fetches one BC3 block represented by one R32G32B32A32_UINT texel.
    uvec4 texColor = texelFetch(tex, ivec2(texCoord.x * 16, texCoord.y * 16), 0);
    outColor = uvec4(texColor.rgba);
}
```

##### Compute Verify Shader

```glsl
#version 450
/// The copied BC3 block is exposed as four uint32 components through the compatible view.
layout(set = 0, binding = 0, rgba32ui) uniform highp uimage2D dstImg;
/// The verdict image stores green for an exact block match and red otherwise.
layout(set = 0, binding = 1, rgba8) uniform highp image2D outputImg;
/// One invocation checks one 4x4 BC3 block represented by one view texel.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main() {
    /// This is the expected source pattern after the byte-exact image copy.
    uvec4 color = uvec4(4294967295u, 4294967295u, 2031647, 0u); // blue
    vec4 green = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    vec4 red = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    /// Read the destination block through the R32G32B32A32_UINT view.
    uvec4 dstColor = imageLoad(dstImg, ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y)).rgba;
    /// Emit a per-block verdict consumed by the host-side all-green comparison.
    imageStore(outputImg, ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y), color == dstColor ? green : red );
}
```

#### Additional Info

- `compFill` is present only for compressed format pairs; it varies with block size and image type, and here uses the BC3 128-bit constants and 2D `ivec2` coordinates. It matters because compressed images cannot be seeded with the ordinary `uploadImage` path.
- `frag` is generated for both compressed and uncompressed pairs and varies by image type, view component type, and block-render extent. Here its `usampler2D`, `uvec4`, and 16×16 fetch coordinates are the sampling-side proof of the compatible view.
- The host dispatches the compute stages with `getSizeInBlocks(...)`, barriers shader writes before the transfer and verification stages, and compares the resulting verdict image against all green.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Image type (`1d` vs `2d`) | Changes `sampler1D`/`sampler2D`, `image1D`/`image2D`, scalar vs `ivec2` coordinates, and whether y participates in block addressing. | [`initPrograms()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L981) |
| Format pair | Uncompressed `B10G11R11_UFLOAT_PACK32` uses float sampling and no compute stages; BC1 uses `uvec2`/64-bit block constants; BC3 uses `uvec4`/128-bit constants and `rgba32ui`. | [`fmtPairs`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1124-L1132) and [`initPrograms()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1012-L1108) |
| Compressed block extent | The 64×64 BC3 extent becomes 16×16 shader invocations and fragment fetch coordinates, while copy-region x/y scaling uses the 4×4 block dimensions for 2D. | [`getSizeInBlocks()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L889-L910) and [`iterate()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L539-L575) |
| Copy/check command path | Registration leaves `COPY_COMMANDS_2` unset, so this representative case uses `vkCmdCopyImage`; compressed results are checked by `compVerify` rather than a host texture decode. | [`createReinterpretationTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1155-L1190) and [`iterate()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L761-L827) |

#### SPIR-V

##### Compute Fill Shader

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
; Bound: 47
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %srcColor "srcColor"
               OpName %dstColor "dstColor"
               OpName %srcImg "srcImg"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %dstImg "dstImg"
               OpDecorate %srcImg Binding 0
               OpDecorate %srcImg DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %dstImg Binding 1
               OpDecorate %dstImg DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
%uint_4294967295 = OpConstant %uint 4294967295
%uint_2031647 = OpConstant %uint 2031647
     %uint_0 = OpConstant %uint 0
         %13 = OpConstantComposite %v4uint %uint_4294967295 %uint_4294967295 %uint_2031647 %uint_0
%uint_4160813056 = OpConstant %uint 4160813056
         %16 = OpConstantComposite %v4uint %uint_4294967295 %uint_4294967295 %uint_4160813056 %uint_0
         %17 = OpTypeImage %uint 2D 0 0 0 2 Rgba32ui
%_ptr_UniformConstant_17 = OpTypePointer UniformConstant %17
     %srcImg = OpVariable %_ptr_UniformConstant_17 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
        %int = OpTypeInt 32 1
     %uint_1 = OpConstant %uint 1
      %v2int = OpTypeVector %int 2
     %dstImg = OpVariable %_ptr_UniformConstant_17 UniformConstant
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
   %srcColor = OpVariable %_ptr_Function_v4uint Function
   %dstColor = OpVariable %_ptr_Function_v4uint Function
               OpStore %srcColor %13
               OpStore %dstColor %16
         %20 = OpLoad %17 %srcImg
         %25 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %26 = OpLoad %uint %25
         %28 = OpBitcast %int %26
         %30 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %31 = OpLoad %uint %30
         %32 = OpBitcast %int %31
         %34 = OpCompositeConstruct %v2int %28 %32
         %35 = OpLoad %v4uint %srcColor
               OpImageWrite %20 %34 %35
         %37 = OpLoad %17 %dstImg
         %38 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %39 = OpLoad %uint %38
         %40 = OpBitcast %int %39
         %41 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %42 = OpLoad %uint %41
         %43 = OpBitcast %int %42
         %44 = OpCompositeConstruct %v2int %40 %43
         %45 = OpLoad %v4uint %dstColor
               OpImageWrite %37 %44 %45
               OpReturn
               OpFunctionEnd
```

</details>

##### Sampling Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 40
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %texCoord %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %texColor "texColor"
               OpName %tex "tex"
               OpName %texCoord "texCoord"
               OpName %outColor "outColor"
               OpDecorate %tex Binding 0
               OpDecorate %tex DescriptorSet 0
               OpDecorate %texCoord Location 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
         %10 = OpTypeImage %uint 2D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
        %tex = OpVariable %_ptr_UniformConstant_11 UniformConstant
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
   %texCoord = OpVariable %_ptr_Input_v2float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
   %float_16 = OpConstant %float 16
        %int = OpTypeInt 32 1
     %uint_1 = OpConstant %uint 1
      %v2int = OpTypeVector %int 2
      %int_0 = OpConstant %int 0
%_ptr_Output_v4uint = OpTypePointer Output %v4uint
   %outColor = OpVariable %_ptr_Output_v4uint Output
       %main = OpFunction %void None %3
          %5 = OpLabel
   %texColor = OpVariable %_ptr_Function_v4uint Function
         %14 = OpLoad %11 %tex
         %21 = OpAccessChain %_ptr_Input_float %texCoord %uint_0
         %22 = OpLoad %float %21
         %24 = OpFMul %float %22 %float_16
         %26 = OpConvertFToS %int %24
         %28 = OpAccessChain %_ptr_Input_float %texCoord %uint_1
         %29 = OpLoad %float %28
         %30 = OpFMul %float %29 %float_16
         %31 = OpConvertFToS %int %30
         %33 = OpCompositeConstruct %v2int %26 %31
         %35 = OpImage %10 %14
         %36 = OpImageFetch %v4uint %35 %33 Lod %int_0
               OpStore %texColor %36
         %39 = OpLoad %v4uint %texColor
               OpStore %outColor %39
               OpReturn
               OpFunctionEnd
```

</details>

##### Compute Verify Shader

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
; Bound: 65
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %color "color"
               OpName %green "green"
               OpName %red "red"
               OpName %dstColor "dstColor"
               OpName %dstImg "dstImg"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %outputImg "outputImg"
               OpDecorate %dstImg Binding 0
               OpDecorate %dstImg DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %outputImg Binding 1
               OpDecorate %outputImg DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
%uint_4294967295 = OpConstant %uint 4294967295
%uint_2031647 = OpConstant %uint 2031647
     %uint_0 = OpConstant %uint 0
         %13 = OpConstantComposite %v4uint %uint_4294967295 %uint_4294967295 %uint_2031647 %uint_0
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %20 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %22 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
         %24 = OpTypeImage %uint 2D 0 0 0 2 Rgba32ui
%_ptr_UniformConstant_24 = OpTypePointer UniformConstant %24
     %dstImg = OpVariable %_ptr_UniformConstant_24 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
        %int = OpTypeInt 32 1
     %uint_1 = OpConstant %uint 1
      %v2int = OpTypeVector %int 2
         %43 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_43 = OpTypePointer UniformConstant %43
  %outputImg = OpVariable %_ptr_UniformConstant_43 UniformConstant
       %bool = OpTypeBool
     %v4bool = OpTypeVector %bool 4
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %color = OpVariable %_ptr_Function_v4uint Function
      %green = OpVariable %_ptr_Function_v4float Function
        %red = OpVariable %_ptr_Function_v4float Function
   %dstColor = OpVariable %_ptr_Function_v4uint Function
               OpStore %color %13
               OpStore %green %20
               OpStore %red %22
         %27 = OpLoad %24 %dstImg
         %32 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %33 = OpLoad %uint %32
         %35 = OpBitcast %int %33
         %37 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %38 = OpLoad %uint %37
         %39 = OpBitcast %int %38
         %41 = OpCompositeConstruct %v2int %35 %39
         %42 = OpImageRead %v4uint %27 %41
               OpStore %dstColor %42
         %46 = OpLoad %43 %outputImg
         %47 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %48 = OpLoad %uint %47
         %49 = OpBitcast %int %48
         %50 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %51 = OpLoad %uint %50
         %52 = OpBitcast %int %51
         %53 = OpCompositeConstruct %v2int %49 %52
         %54 = OpLoad %v4uint %color
         %55 = OpLoad %v4uint %dstColor
         %58 = OpIEqual %v4bool %54 %55
         %59 = OpAll %bool %58
         %60 = OpLoad %v4float %green
         %61 = OpLoad %v4float %red
         %62 = OpCompositeConstruct %v4bool %59 %59 %59 %59
         %63 = OpSelect %v4float %62 %60 %61
               OpImageWrite %46 %53 %63
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates the source `VkImage` with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_STORAGE_BIT`, and the destination `VkImage` with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_STORAGE_BIT` (no `SAMPLED_BIT`, since only the source is sampled through the view). `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is added when the image format differs from the view format, and `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT | VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` is added when the image format is compressed. Memory is bound suballocated on the universal queue.
- For uncompressed cases, the host fills source and destination `tcu::TextureLevel` objects via `generateBuffer` (`FILL_MODE_RED` for source, `FILL_MODE_BLACK` for destination), computes the expected result via `copyRegionToTextureLevel` (which applies the source format to the destination buffer to mimic the memcpy semantics), and uploads via `uploadImage`.
- For compressed cases, the host dispatches the `compFill` compute shader with workgroup count equal to `getSizeInBlocks(...)`, binding source and destination as storage images through the view format. `compFill` writes the hardcoded "blue" pattern into the source and "red" pattern into the destination via `imageStore`. Pipeline barriers then move both images from `VK_IMAGE_LAYOUT_GENERAL` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`.
- The host records a transfer-stage pipeline barrier moving the source to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` and the destination to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, then records `vkCmdCopyImage` with a single whole-image `VkImageCopy` region. For compressed sources, the per-region `srcOffset.x` and `extent.width` are multiplied by `getBlockWidth`; for 2D compressed sources, `srcOffset.y` and `extent.height` are also multiplied by `getBlockHeight`. The 1D exception per VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152 skips the y-scaling when the image type is 1D.
- The host then records a pipeline barrier moving the source from `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`, builds a graphics pipeline (vertex + fragment shader), and draws a 6-vertex triangle strip. The fragment shader calls `texelFetch` on the source through the view-format `imageView` and writes the result to a color attachment in the view format.
- For uncompressed sampling, the host copies the color attachment to a host-visible `VkBuffer` via `copyImageToBuffer`. For compressed sampling, the host dispatches `compVerify` against the rendered output image, then copies the `compVerify` output image to a host-visible buffer.
- For uncompressed copy, the host calls `readImage(destination)` and `tcu::floatThresholdCompare`s against `m_expectedTextureLevel[0]` with threshold `0.01`. For compressed copy, the host dispatches `compVerify` against the destination image, reads back the green/red verdict image, and compares against an all-green reference with the same threshold.
- A mismatch in either the copy check or the sampling check fails the test case. The `0.01` float threshold absorbs floating-point rounding in the host reference computation; it does not forgive byte differences in the compressed-case green/red verdict, which is exact.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `copy_b10g11r11_ufloat_pack32_sample_r16g16_sfloat` (uncompressed 32-bit pair) | `vkCmdCopyImage` not byte-exact across size-compatible uncompressed pairs; `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` not honored by the sampling path; view-format sampling reads wrong channels; host-side memcpy reference mismatch. |
| `copy_bc1_rgb_unorm_block_sample_r32g32_uint` (compressed 64-bit block) | `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` not honored for 64-bit blocks; `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` not honored; storage-image `imageStore`/`imageLoad` through the view does not access the underlying block bytes; copy does not memcpy the 64-bit block; 1D vs 2D block-size scaling wrong. |
| `copy_bc3_unorm_block_sample_r32g32b32a32_uint` (compressed 128-bit block) | Same as BC1 case but for 128-bit blocks; view texel size to compressed block size mapping wrong; `R32G32B32A32_UINT` view of a BC3 image misaligned. |
| All leaves under `1d` (secondary axis) | 1D-specific block-size scaling: y-dimensions of `srcOffset`/`dstOffset`/`extent` mishandled per VUID-vkCmdCopyImage-srcImage-00146 / VUID-vkCmdCopyImage-dstImage-00152. |
| All leaves under `2d` (secondary axis) | 2D block-size scaling: x and y both must be scaled by block width and height; image type routing wrong. |

### Cause Analysis

#### Uncompressed 32-bit pair failures

**Possible failure symptoms:** the copy check fails because `readImage(destination)` does not match the host-computed memcpy reference within the `0.01` threshold; or the sampling check fails because the rendered color attachment does not match the source data reinterpreted through the `R16G16_SFLOAT` view.

**Possible implementation causes:** the driver reinterprets channels instead of treating the copy as a memcpy between size-compatible uncompressed formats; the implementation does not honor `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` when sampling through a view of a different format, so `texelFetch` reads the wrong channels; or the implementation's view-format sampling path decodes `B10G11R11_UFLOAT_PACK32` texels as if they were `R16G16_SFLOAT` and produces wrong float values.

#### Compressed 64-bit block failures

**Possible failure symptoms:** the `compVerify` output image is not all green, meaning at least one destination texel read through the `R32G32_UINT` view does not equal the expected "blue" pattern; or the sampling-side `compVerify` against the rendered output image is not all green, meaning the fragment shader's `texelFetch` did not return the expected pattern.

**Possible implementation causes:** the driver does not honor `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` for BC1, so the `R32G32_UINT` view does not map one texel to one 64-bit block; `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` is not honored, so the image cannot be created with the requested usage flags and the storage-image path fails; the storage-image `imageStore`/`imageLoad` through the view does not access the underlying block bytes; the `vkCmdCopyImage` path does not memcpy the 64-bit block as a unit; or the 1D versus 2D block-size scaling is wrong, causing the copy region to cover the wrong bytes.

#### Compressed 128-bit block failures

**Possible failure symptoms:** the `compVerify` output image is not all green for the BC3 case, meaning at least one destination texel read through the `R32G32B32A32_UINT` view does not equal the expected "blue" pattern.

**Possible implementation causes:** same as the BC1 case but for 128-bit blocks; the view texel size to compressed block size mapping is wrong, so one `R32G32B32A32_UINT` texel does not correspond to one BC3 block; or the implementation handles 64-bit block-texel views correctly but not 128-bit block-texel views. Source-level investigation is needed if the failure pattern differs between BC1 and BC3 in a way not explained by the block size or component count.

#### 1D versus 2D block-size scaling failures

**Possible failure symptoms:** all `1d` leaves fail while `2d` leaves pass, or vice versa; or only the compressed cases under one intermediate node fail because the copy region covers the wrong bytes.

**Possible implementation causes:** the driver scales the y-dimensions of `srcOffset` / `dstOffset` / `extent` for `VK_IMAGE_TYPE_1D` compressed images, violating VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152; or the driver fails to scale the y-dimensions for `VK_IMAGE_TYPE_2D` compressed images, producing a region that is too small. The 1D exception exists because a 1D image has height 1, so scaling y by the block height would be a no-op in correct implementations but a bug if applied.

## Case Pruning

### Requirement-based pruning

- Compressed cases require `VK_KHR_maintenance2` (or Vulkan 1.1+) for `VK_IMAGE_CREATE_BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` and `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. Devices without support throw `NotSupportedError` in `checkSupport()` and the case is skipped, not failed. See [`checkSupport()` at line 924](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L924).
- Both image format and view format must pass `vkGetPhysicalDeviceImageFormatProperties()` with `VK_ERROR_FORMAT_NOT_SUPPORTED` not returned; otherwise the case is skipped. See [image format query at line 931](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L931) and [view format query at line 940](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L940).
- Source and destination image dimensions must not exceed `maxImageDimension1D` (for 1D) or `maxImageDimension2D` (for 2D); otherwise the case is skipped. See [1D limit check at line 953](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L953) and [2D limit check at line 963](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L963).
- `checkExtensionSupport()` gates `COPY_COMMANDS_2` if the flag were set; the registered leaves do not set it, so this gate is dormant for mustpass. See [line 948](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L948).

### Design-based pruning

- The format pair matrix is fixed at three pairs: one uncompressed pair and two compressed pairs covering the two supported block sizes (64-bit and 128-bit). Other size-compatible reinterpretations are not covered by this test family.
- The `DE_ASSERT` constraints in the `ReinterpretTestCase` constructor pin tiling to optimal, allocation to suballocated, queue to universal, and disable clear-red, secondary command buffer, sparse binding, and general layout. The test family exercises only the format reinterpretation scenario, not the full parameter space of copy operations. See [`ReinterpretTestCase` constructor at line 886](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L886).
- 3D image types are not tested.
- `vkCmdBlitImage` with reinterpreted formats is not tested; only `vkCmdCopyImage`.
- The test instance supports `vkCmdCopyImage2` via `COPY_COMMANDS_2`, but registration does not set the flag, so all mustpass leaves use `vkCmdCopyImage`.

## Key Takeaways

- The test treats `vkCmdCopyImage` as a byte-exact memcpy across size-compatible format pairs; any driver reinterpretation of channels fails the comparison.
- Each test case leaf verifies both copy correctness and sampling correctness independently. A failure in either check fails the case.
- The three format pairs cover the supported reinterpretation scenarios: uncompressed 32-bit (testing `MUTABLE_FORMAT_BIT` alone), compressed 64-bit block (testing `BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` plus `EXTENDED_USAGE_BIT` for BC1), and compressed 128-bit block (same flags for BC3).
- The verification mechanism is asymmetric by design: uncompressed cases use host-side `tcu::floatThresholdCompare` against a host-computed memcpy reference, while compressed cases use a compute-shader green/red verdict because compressed texels cannot be seeded or read back via `uploadImage`/`readImage` portably.
- The `1d` / `2d` intermediate nodes exercise the 1D exception for compressed block-size scaling per VUID-vkCmdCopyImage-srcImage-00146 and VUID-vkCmdCopyImage-dstImage-00152.
- See `## Failure Meaning` for the per-leaf failure cause mapping and analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ReinterpretTestInstance` class | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L35-L57`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L35-L57) | Owns source/destination images, view format, and overrides `iterate()`, `checkTestResult()`, `copyRegionToTextureLevel()`. |
| Image creation with `MUTABLE_FORMAT_BIT` and `BLOCK_TEXEL_VIEW_COMPATIBLE_BIT` | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L59-L140`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L59-L140) | Shows when each flag is added based on whether the format differs from the view and whether the format is compressed. |
| `copyRegionToTextureLevel` memcpy reference | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L152-L216`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L152-L216) | Host-side reference for uncompressed copy verification; replaces destination format with source format to mimic memcpy. |
| `fillCompressedImages` (`compFill` dispatch) | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L218-L311`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L218-L311) | Dispatches `compFill` over `getSizeInBlocks`, binds storage image descriptors, records pre/post barriers. |
| `checkTestResult(testImage, ...)` (`compVerify` dispatch) | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L316-L466`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L316-L466) | Dispatches `compVerify` against a test image, reads back the green/red output, and compares against an all-green reference. |
| `iterate()` end-to-end | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L468-L863`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L468-L863) | Wires upload/fill, copy, sampling renderpass, and verification; gates per-branch on `srcCompressed`. |
| `ReinterpretTestCase` constructor with `DE_ASSERT` constraints | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L886-L905`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L886-L905) | Documents the constrained parameter space. |
| `checkSupport()` | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L912-L979`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L912-L979) | Gates `VK_KHR_maintenance2`, queries image format properties for both image and view formats, validates 1D/2D dimension limits. |
| `initPrograms()` shader generation | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L981-L1110`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L981-L1110) | Generates `vert`, `frag`, and (compressed only) `compFill` plus `compVerify`. |
| `createReinterpretationTests()` registration | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L1119-L1198`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L1119-L1198) | Defines the three format pairs and two image types, registers leaves under `1d` and `2d`. |
| `formatsAreCompatible()` size check | [`vktApiCopiesAndBlittingReinterpretTests.cpp#L881-L884`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.cpp#L881-L884) | Admits the uncompressed pair; compressed cases bypass this check. |
| Header declaration | [`vktApiCopiesAndBlittingReinterpretTests.hpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingReinterpretTests.hpp) | Declares `createReinterpretationTests()`. |
| Dispatcher registration | [`vktApiCopiesAndBlittingTests.cpp#L290`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L290) | Adds `createReinterpretationTests()` directly under `copy_and_blit`. |
| `getSizeCompatibleTcuTextureFormat()` helper | [`vktApiCopiesAndBlittingUtil.cpp#L170-L177`](../../../modules/vulkan/api/vktApiCopiesAndBlittingUtil.cpp#L170-L177) | Maps compressed formats to size-compatible uncompressed tcu formats for host-side texture levels. |
