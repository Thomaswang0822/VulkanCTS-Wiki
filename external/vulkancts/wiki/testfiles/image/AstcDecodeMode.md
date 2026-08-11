## Overview

**Core question:** For ASTC formats affected by the extension, does an image view decode through the selected legal intermediate format and yield a sample consistent with an ordinary view? For sRGB ASTC formats, where the specification says `decodeMode` has no effect, do the two views still agree?

- This page covers [`vktImageAstcDecodeModeTests.cpp`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L1-L621), which implements the `image.astc_decode_mode` test family.
- Each test case populates two ASTC images with the same generated valid block stream. One image view chains `VkImageViewASTCDecodeModeEXT`; the other remains an ordinary ASTC view. A compute shader samples both and writes a pass marker when they agree ([execution path](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L95-L371)).
- The matrix spans 2D ASTC UNORM and sRGB block footprints, all three legal decode-mode formats, and, outside VulkanSC, 3D ASTC UNORM, sRGB, and SFLOAT footprints ([registration matrix](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L488-L617)).

## Background Knowledge

- **View-local ASTC decoding.** `VkImageViewASTCDecodeModeEXT` selects the intermediate format used to decode ASTC compressed formats for one image view. Vulkan allows `R16G16B16A16_SFLOAT`, `R8G8B8A8_UNORM`, and `E5B9G9R9_UFLOAT_PACK32`; shared exponent requires the matching feature, and `R8G8B8A8_UNORM` is invalid for a view containing ASTC HDR-mode blocks. For an sRGB image-view format, `decodeMode` has no effect ([view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L7098-L7135)).
- **Independent views can expose independent interpretation.** The test compares two separately populated but byte-identical ASTC images: a tested view with the extension structure and a reference view without it. Sampling both at one coordinate lets the shader turn an interpretation mismatch into a single result texel.

## Registration Hierarchy

```text
image.astc_decode_mode
├── 10x10_srgb_to_e5b9g9r9_ufloat_pack32
├── 10x10_srgb_to_r16g16b16a16_sfloat
├── 10x10_srgb_to_r8g8b8a8_unorm
├── 10x10_unorm_to_e5b9g9r9_ufloat_pack32
├── 10x10_unorm_to_r16g16b16a16_sfloat
├── 10x10_unorm_to_r8g8b8a8_unorm
├── 10x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 10x5_srgb_to_r16g16b16a16_sfloat
├── 10x5_srgb_to_r8g8b8a8_unorm
├── 10x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 10x5_unorm_to_r16g16b16a16_sfloat
├── 10x5_unorm_to_r8g8b8a8_unorm
├── 10x6_srgb_to_e5b9g9r9_ufloat_pack32
├── 10x6_srgb_to_r16g16b16a16_sfloat
├── 10x6_srgb_to_r8g8b8a8_unorm
├── 10x6_unorm_to_e5b9g9r9_ufloat_pack32
├── 10x6_unorm_to_r16g16b16a16_sfloat
├── 10x6_unorm_to_r8g8b8a8_unorm
├── 10x8_srgb_to_e5b9g9r9_ufloat_pack32
├── 10x8_srgb_to_r16g16b16a16_sfloat
├── 10x8_srgb_to_r8g8b8a8_unorm
├── 10x8_unorm_to_e5b9g9r9_ufloat_pack32
├── 10x8_unorm_to_r16g16b16a16_sfloat
├── 10x8_unorm_to_r8g8b8a8_unorm
├── 12x10_srgb_to_e5b9g9r9_ufloat_pack32
├── 12x10_srgb_to_r16g16b16a16_sfloat
├── 12x10_srgb_to_r8g8b8a8_unorm
├── 12x10_unorm_to_e5b9g9r9_ufloat_pack32
├── 12x10_unorm_to_r16g16b16a16_sfloat
├── 12x10_unorm_to_r8g8b8a8_unorm
├── 12x12_srgb_to_e5b9g9r9_ufloat_pack32
├── 12x12_srgb_to_r16g16b16a16_sfloat
├── 12x12_srgb_to_r8g8b8a8_unorm
├── 12x12_unorm_to_e5b9g9r9_ufloat_pack32
├── 12x12_unorm_to_r16g16b16a16_sfloat
├── 12x12_unorm_to_r8g8b8a8_unorm
├── 3x3x3_sfloat_to_e5b9g9r9_ufloat_pack32
├── 3x3x3_sfloat_to_r16g16b16a16_sfloat
├── 3x3x3_srgb_to_e5b9g9r9_ufloat_pack32
├── 3x3x3_srgb_to_r16g16b16a16_sfloat
├── 3x3x3_srgb_to_r8g8b8a8_unorm
├── 3x3x3_unorm_to_e5b9g9r9_ufloat_pack32
├── 3x3x3_unorm_to_r16g16b16a16_sfloat
├── 3x3x3_unorm_to_r8g8b8a8_unorm
├── 4x3x3_sfloat_to_e5b9g9r9_ufloat_pack32
├── 4x3x3_sfloat_to_r16g16b16a16_sfloat
├── 4x3x3_srgb_to_e5b9g9r9_ufloat_pack32
├── 4x3x3_srgb_to_r16g16b16a16_sfloat
├── 4x3x3_srgb_to_r8g8b8a8_unorm
├── 4x3x3_unorm_to_e5b9g9r9_ufloat_pack32
├── 4x3x3_unorm_to_r16g16b16a16_sfloat
├── 4x3x3_unorm_to_r8g8b8a8_unorm
├── 4x4_srgb_to_e5b9g9r9_ufloat_pack32
├── 4x4_srgb_to_r16g16b16a16_sfloat
├── 4x4_srgb_to_r8g8b8a8_unorm
├── 4x4_unorm_to_e5b9g9r9_ufloat_pack32
├── 4x4_unorm_to_r16g16b16a16_sfloat
├── 4x4_unorm_to_r8g8b8a8_unorm
├── 4x4x3_sfloat_to_e5b9g9r9_ufloat_pack32
├── 4x4x3_sfloat_to_r16g16b16a16_sfloat
├── 4x4x3_srgb_to_e5b9g9r9_ufloat_pack32
├── 4x4x3_srgb_to_r16g16b16a16_sfloat
├── 4x4x3_srgb_to_r8g8b8a8_unorm
├── 4x4x3_unorm_to_e5b9g9r9_ufloat_pack32
├── 4x4x3_unorm_to_r16g16b16a16_sfloat
├── 4x4x3_unorm_to_r8g8b8a8_unorm
├── 4x4x4_sfloat_to_e5b9g9r9_ufloat_pack32
├── 4x4x4_sfloat_to_r16g16b16a16_sfloat
├── 4x4x4_srgb_to_e5b9g9r9_ufloat_pack32
├── 4x4x4_srgb_to_r16g16b16a16_sfloat
├── 4x4x4_srgb_to_r8g8b8a8_unorm
├── 4x4x4_unorm_to_e5b9g9r9_ufloat_pack32
├── 4x4x4_unorm_to_r16g16b16a16_sfloat
├── 4x4x4_unorm_to_r8g8b8a8_unorm
├── 5x4_srgb_to_e5b9g9r9_ufloat_pack32
├── 5x4_srgb_to_r16g16b16a16_sfloat
├── 5x4_srgb_to_r8g8b8a8_unorm
├── 5x4_unorm_to_e5b9g9r9_ufloat_pack32
├── 5x4_unorm_to_r16g16b16a16_sfloat
├── 5x4_unorm_to_r8g8b8a8_unorm
├── 5x4x4_sfloat_to_e5b9g9r9_ufloat_pack32
├── 5x4x4_sfloat_to_r16g16b16a16_sfloat
├── 5x4x4_srgb_to_e5b9g9r9_ufloat_pack32
├── 5x4x4_srgb_to_r16g16b16a16_sfloat
├── 5x4x4_srgb_to_r8g8b8a8_unorm
├── 5x4x4_unorm_to_e5b9g9r9_ufloat_pack32
├── 5x4x4_unorm_to_r16g16b16a16_sfloat
├── 5x4x4_unorm_to_r8g8b8a8_unorm
├── 5x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 5x5_srgb_to_r16g16b16a16_sfloat
├── 5x5_srgb_to_r8g8b8a8_unorm
├── 5x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 5x5_unorm_to_r16g16b16a16_sfloat
├── 5x5_unorm_to_r8g8b8a8_unorm
├── 5x5x4_sfloat_to_e5b9g9r9_ufloat_pack32
├── 5x5x4_sfloat_to_r16g16b16a16_sfloat
├── 5x5x4_srgb_to_e5b9g9r9_ufloat_pack32
├── 5x5x4_srgb_to_r16g16b16a16_sfloat
├── 5x5x4_srgb_to_r8g8b8a8_unorm
├── 5x5x4_unorm_to_e5b9g9r9_ufloat_pack32
├── 5x5x4_unorm_to_r16g16b16a16_sfloat
├── 5x5x4_unorm_to_r8g8b8a8_unorm
├── 5x5x5_sfloat_to_e5b9g9r9_ufloat_pack32
├── 5x5x5_sfloat_to_r16g16b16a16_sfloat
├── 5x5x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 5x5x5_srgb_to_r16g16b16a16_sfloat
├── 5x5x5_srgb_to_r8g8b8a8_unorm
├── 5x5x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 5x5x5_unorm_to_r16g16b16a16_sfloat
├── 5x5x5_unorm_to_r8g8b8a8_unorm
├── 6x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 6x5_srgb_to_r16g16b16a16_sfloat
├── 6x5_srgb_to_r8g8b8a8_unorm
├── 6x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 6x5_unorm_to_r16g16b16a16_sfloat
├── 6x5_unorm_to_r8g8b8a8_unorm
├── 6x5x5_sfloat_to_e5b9g9r9_ufloat_pack32
├── 6x5x5_sfloat_to_r16g16b16a16_sfloat
├── 6x5x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 6x5x5_srgb_to_r16g16b16a16_sfloat
├── 6x5x5_srgb_to_r8g8b8a8_unorm
├── 6x5x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 6x5x5_unorm_to_r16g16b16a16_sfloat
├── 6x5x5_unorm_to_r8g8b8a8_unorm
├── 6x6_srgb_to_e5b9g9r9_ufloat_pack32
├── 6x6_srgb_to_r16g16b16a16_sfloat
├── 6x6_srgb_to_r8g8b8a8_unorm
├── 6x6_unorm_to_e5b9g9r9_ufloat_pack32
├── 6x6_unorm_to_r16g16b16a16_sfloat
├── 6x6_unorm_to_r8g8b8a8_unorm
├── 6x6x5_sfloat_to_e5b9g9r9_ufloat_pack32
├── 6x6x5_sfloat_to_r16g16b16a16_sfloat
├── 6x6x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 6x6x5_srgb_to_r16g16b16a16_sfloat
├── 6x6x5_srgb_to_r8g8b8a8_unorm
├── 6x6x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 6x6x5_unorm_to_r16g16b16a16_sfloat
├── 6x6x5_unorm_to_r8g8b8a8_unorm
├── 6x6x6_sfloat_to_e5b9g9r9_ufloat_pack32
├── 6x6x6_sfloat_to_r16g16b16a16_sfloat
├── 6x6x6_srgb_to_e5b9g9r9_ufloat_pack32
├── 6x6x6_srgb_to_r16g16b16a16_sfloat
├── 6x6x6_srgb_to_r8g8b8a8_unorm
├── 6x6x6_unorm_to_e5b9g9r9_ufloat_pack32
├── 6x6x6_unorm_to_r16g16b16a16_sfloat
├── 6x6x6_unorm_to_r8g8b8a8_unorm
├── 8x5_srgb_to_e5b9g9r9_ufloat_pack32
├── 8x5_srgb_to_r16g16b16a16_sfloat
├── 8x5_srgb_to_r8g8b8a8_unorm
├── 8x5_unorm_to_e5b9g9r9_ufloat_pack32
├── 8x5_unorm_to_r16g16b16a16_sfloat
├── 8x5_unorm_to_r8g8b8a8_unorm
├── 8x6_srgb_to_e5b9g9r9_ufloat_pack32
├── 8x6_srgb_to_r16g16b16a16_sfloat
├── 8x6_srgb_to_r8g8b8a8_unorm
├── 8x6_unorm_to_e5b9g9r9_ufloat_pack32
├── 8x6_unorm_to_r16g16b16a16_sfloat
├── 8x6_unorm_to_r8g8b8a8_unorm
├── 8x8_srgb_to_e5b9g9r9_ufloat_pack32
├── 8x8_srgb_to_r16g16b16a16_sfloat
├── 8x8_srgb_to_r8g8b8a8_unorm
├── 8x8_unorm_to_e5b9g9r9_ufloat_pack32
├── 8x8_unorm_to_r16g16b16a16_sfloat
└── 8x8_unorm_to_r8g8b8a8_unorm
```

The source registers 164 Vulkan test case leaves in the default mustpass matrix. The 2D leaves cover 28 source-format names times three decode modes. Non-VulkanSC builds add 80 3D leaves: 10 UNORM and 10 sRGB source formats times three modes, plus 10 SFLOAT source formats times the two allowed modes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type and nominal/output extent | 2D, `64 x 64 x 1`; 3D, `64 x 64 x 3` outside VulkanSC | Selects image/view/sampler dimensionality, result-image extent, and dispatch size. The two compressed images are actually created with `getCompressedImageResolutionInBlocks(format, imageSize)` as their extent. | [Image creation](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L102-L149) [Case construction](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L573-L613) |
| 2D source ASTC format | `4x4` through `12x12`, each in `unorm` and `srgb` | Varies the 2D compressed block footprint and source encoding. | [2D format array](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L497-L526) |
| 3D source ASTC format | `3x3x3` through `6x6x6`, in `unorm`, `srgb`, and `sfloat` outside VulkanSC | Varies 3D block footprints and adds HDR-capable SFLOAT sources. | [3D format array](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L527-L560) |
| Decode mode | `r16g16b16a16_sfloat`, `r8g8b8a8_unorm`, `e5b9g9r9_ufloat_pack32` | Selects the intermediate decode format on the tested image view. | [Decode-mode array](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L562-L569) |
| Support-query tested image usage | `TRANSFER_SRC`, `TRANSFER_DST`, `SAMPLED` | The support check asks whether the selected ASTC format accepts this usage set; execution uploads the image and samples it. | [Case construction](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L577-L586) |
| Support-query result format and usage | `R8G8B8A8_UNORM`, `STORAGE` | The support check requires storage-image capability; execution uses the result image for shader storage and transfer readback. | [Case construction](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L585-L609) |

## Behavior Parameters

The selected decode mode forms the primary behavioral axis. Each registered leaf combines one of these values with an ASTC source-format name; the suffix after `_to_` names the selected mode.

### `r16g16b16a16_sfloat`: Half-float intermediate decoding

The tested view chains `VK_FORMAT_R16G16B16A16_SFLOAT` as its decode mode. The shader samples that view and the ordinary reference view through the same sampler type, then records whether their values are within the generated distance threshold ([view and comparison setup](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L160-L180) [shader generation](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L437-L475)).

### `r8g8b8a8_unorm`: Normalized unsigned intermediate decoding

The tested view chains `VK_FORMAT_R8G8B8A8_UNORM`. Vulkan disallows this choice for an image view containing ASTC HDR blocks, and the registration loop therefore omits the 3D SFLOAT-source combinations ([spec rule](../../../../vulkan-docs/src/chapters/resources.adoc#L7125-L7127) [matrix pruning](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L592-L613)).

### `e5b9g9r9_ufloat_pack32`: Shared-exponent intermediate decoding

The tested view chains `VK_FORMAT_E5B9G9R9_UFLOAT_PACK32`. The case requires `decodeModeSharedExponent`; for selected source-format flags, the generated shader adjusts its comparison reference by clamping negative channels and setting alpha to one. The SFLOAT branch also limits the tested value to 65504 before the distance test. One source-data anomaly matters here: `3x3x3_sfloat` is registered with both `isUnorm` and `isSfloat` true, so it takes the earlier UNORM branch and does **not** apply the 65504 clamp ([support check](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L414-L416) [shader branch](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L459-L473) [format flags](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L527-L534)).

## Shader Analysis

[`AstcDecodeModeCase::initPrograms()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L425-L479) generates the compute shader. The walkthrough uses the 2D UNORM shared-exponent case because it exercises the source's E5B9G9R9-specific reference adjustment. All other 2D cases retain the same descriptor and coordinate structure; 3D cases replace the 2D coordinate, sampler, and storage-image types.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.astc_decode_mode.4x4_unorm_to_e5b9g9r9_ufloat_pack32
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `4x4_unorm` | Selects `VK_FORMAT_ASTC_4x4_UNORM_BLOCK` and the 2D case with a `64 x 64 x 1` nominal/output extent. The compressed image is created with the corresponding block-grid extent (`16 x 16 x 1`). |
| `e5b9g9r9_ufloat_pack32` | Places the shared-exponent decode mode on the tested view and chooses the UNORM E5B9G9R9 reference-adjustment branch. |

#### Purpose

The shader samples the tested and reference ASTC views at the same normalized coordinate. It writes 0.5 when the tested sample matches the adjusted reference within 0.01, otherwise zero.

#### Structural Design

| Phase | Shader action | Observable result |
|-------|---------------|-------------------|
| Address | Maps `gl_GlobalInvocationID.xy` to an integer result coordinate and a normalized sample coordinate. | One invocation handles one output texel. |
| Sample | Reads binding 0 from the decode-mode view and binding 1 from the ordinary view. | Both samples correspond to the same source block data. |
| Normalize comparison | Clamps the reference to `vec4(0,0,0,1)` for this UNORM shared-exponent case. | The comparison matches the source-defined E5B9G9R9 handling. |
| Mark | Stores 0.5 for a distance below 0.01 and 0.0 otherwise. | The host can distinguish pass markers from failure markers after copyback. |

#### Shader Code

```glsl
#version 450
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// Binding 0 samples the tested ASTC image view, whose pNext chain carries
/// VK_FORMAT_E5B9G9R9_UFLOAT_PACK32 as the ASTC decode mode.
layout (binding = 0) uniform sampler2D compressed_tested;
/// Binding 1 samples a separate ASTC image with identical uploaded blocks through an ordinary view.
layout (binding = 1) uniform sampler2D compressed_reference;
/// Binding 2 is the host-read-back R8G8B8A8_UNORM storage image.
layout (binding = 2, rgba8) writeonly uniform image2D result;
void main (void)
{
    const vec2 pixels_resolution = vec2(gl_NumWorkGroups.xy);
    const vec2 cord = vec2(gl_GlobalInvocationID.xy) / vec2(pixels_resolution);
    const ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    vec4 tested = texture(compressed_tested, cord);
    vec4 reference = texture(compressed_reference, cord);
    /// The E5B9G9R9 comparison rule clamps negative reference channels and sets alpha to 1.
    reference = max(vec4(0,0,0,1), reference);
    float result_color = 0.5 * float(distance(tested, reference) < 0.01);
    imageStore(result, pos, vec4(result_color));
}
```

#### Additional Info

- The source uses `gl_NumWorkGroups` as the pixel-resolution denominator because the host dispatches one local-size-1 workgroup per uncompressed texel ([dispatch](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L320-L320)).
- The generated shader has no explicit sampler LOD. With the minification/magnification configuration and the base-only image, the reconstructed shader compiles to explicit level-zero sampling in the generated SPIR-V.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Image type | 3D cases emit `vec3`, `ivec3`, a 3D sampler, and a 3D storage image instead of the 2D forms shown here. | [2D/3D branch](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L446-L457) |
| Decode mode | Non-E5B9G9R9 modes omit the reference clamp. E5B9G9R9 cases flagged only as SFLOAT also clamp `tested` to 65504; the anomalously dual-flagged `3x3x3_sfloat` case takes the UNORM branch instead. For sRGB source formats, the specification says the selected decode mode has no effect. | [Decode-mode branches](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L459-L473) [sRGB rule](../../../../vulkan-docs/src/chapters/resources.adoc#L7133-L7133) |
| Source format | The format maps to the generated sampler type, while the result image remains a format-qualified `R8G8B8A8_UNORM` storage image. | [Type selection](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L429-L442) |

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
; Bound: 72
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %pixels_resolution "pixels_resolution"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %cord "cord"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %pos "pos"
               OpName %tested "tested"
               OpName %compressed_tested "compressed_tested"
               OpName %reference "reference"
               OpName %compressed_reference "compressed_reference"
               OpName %result_color "result_color"
               OpName %result "result"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %compressed_tested Binding 0
               OpDecorate %compressed_tested DescriptorSet 0
               OpDecorate %compressed_reference Binding 1
               OpDecorate %compressed_reference DescriptorSet 0
               OpDecorate %result NonReadable
               OpDecorate %result Binding 2
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %35 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %36 = OpTypeSampledImage %35
%_ptr_UniformConstant_36 = OpTypePointer UniformConstant %36
%compressed_tested = OpVariable %_ptr_UniformConstant_36 UniformConstant
    %float_0 = OpConstant %float 0
%compressed_reference = OpVariable %_ptr_UniformConstant_36 UniformConstant
    %float_1 = OpConstant %float 1
         %49 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_1
%_ptr_Function_float = OpTypePointer Function %float
  %float_0_5 = OpConstant %float 0.5
%float_0_00999999978 = OpConstant %float 0.00999999978
       %bool = OpTypeBool
         %63 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_63 = OpTypePointer UniformConstant %63
     %result = OpVariable %_ptr_UniformConstant_63 UniformConstant
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%pixels_resolution = OpVariable %_ptr_Function_v2float Function
       %cord = OpVariable %_ptr_Function_v2float Function
        %pos = OpVariable %_ptr_Function_v2int Function
     %tested = OpVariable %_ptr_Function_v4float Function
  %reference = OpVariable %_ptr_Function_v4float Function
%result_color = OpVariable %_ptr_Function_float Function
         %15 = OpLoad %v3uint %gl_NumWorkGroups
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpConvertUToF %v2float %16
               OpStore %pixels_resolution %17
         %20 = OpLoad %v3uint %gl_GlobalInvocationID
         %21 = OpVectorShuffle %v2uint %20 %20 0 1
         %22 = OpConvertUToF %v2float %21
         %23 = OpLoad %v2float %pixels_resolution
         %24 = OpFDiv %v2float %22 %23
               OpStore %cord %24
         %29 = OpLoad %v3uint %gl_GlobalInvocationID
         %30 = OpVectorShuffle %v2uint %29 %29 0 1
         %31 = OpBitcast %v2int %30
               OpStore %pos %31
         %39 = OpLoad %36 %compressed_tested
         %40 = OpLoad %v2float %cord
         %42 = OpImageSampleExplicitLod %v4float %39 %40 Lod %float_0
               OpStore %tested %42
         %45 = OpLoad %36 %compressed_reference
         %46 = OpLoad %v2float %cord
         %47 = OpImageSampleExplicitLod %v4float %45 %46 Lod %float_0
               OpStore %reference %47
         %50 = OpLoad %v4float %reference
         %51 = OpExtInst %v4float %1 FMax %49 %50
               OpStore %reference %51
         %55 = OpLoad %v4float %tested
         %56 = OpLoad %v4float %reference
         %57 = OpExtInst %float %1 Distance %55 %56
         %60 = OpFOrdLessThan %bool %57 %float_0_00999999978
         %61 = OpSelect %float %60 %float_1 %float_0
         %62 = OpFMul %float %float_0_5 %61
               OpStore %result_color %62
         %66 = OpLoad %63 %result
         %67 = OpLoad %v2int %pos
         %68 = OpLoad %float %result_color
         %69 = OpCompositeConstruct %v4float %68 %68 %68 %68
               OpImageWrite %66 %67 %69
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`BasicComputeTestInstance::iterate()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L95-L371) creates two mutable-format, block-texel-view-compatible ASTC images at the computed block-grid extent and one uncompressed result image at the nominal extent. It creates the tested view with `VkImageViewASTCDecodeModeEXT` in its `pNext` chain, but creates the reference view without that structure.
- The host generates one valid ASTC block stream, writes it to a host-visible buffer, and copies it into both ASTC images. It then transitions both images from transfer-destination to shader-read-only layout and the result image to `VK_IMAGE_LAYOUT_GENERAL` ([uploads and barriers](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L264-L318)).
- The compute dispatch dimensions equal the uncompressed image extent. Binding 0 receives the tested image/sampler, binding 1 receives the reference image/sampler, and binding 2 receives the storage image ([descriptor update](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L250-L262) [dispatch](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L297-L320)).
- After the dispatch, the host transitions the result image to transfer-source layout, copies it into a host-visible result buffer, and makes the transfer write visible to host reads ([copyback barriers](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L322-L356)).
- The host rejects the case when the first byte of any four-byte result texel falls outside 100 through 150. A successful shader marker of 0.5 encodes near 128 in the UNORM result format ([result check](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L358-L371)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `r16g16b16a16_sfloat` | The ASTC view override, floating-point intermediate conversion, tested/reference sampling, or result-image comparison path disagrees with the reference behavior. |
| `r8g8b8a8_unorm` | The normalized-unsigned override path, its legal non-HDR source handling, tested/reference sampling, or result-image comparison path disagrees with the reference behavior. |
| `e5b9g9r9_ufloat_pack32` | The shared-exponent feature/override path or its nonnegative-and-alpha comparison adjustment disagrees with the tested sample result. |

### Cause Analysis

#### ASTC view override and sampled conversion

**Possible failure symptoms:** One or more output texels contain zero rather than the expected marker range. Failures confined to one source footprint, image type, or decode-mode suffix narrow the disagreement to that configuration.

**Possible implementation causes:** The tested image view may ignore or misapply the `VkImageViewASTCDecodeModeEXT` `decodeMode`, or the implementation may convert sampled ASTC data through the wrong intermediate representation. The source keeps the two images' uploaded blocks identical, so the comparison isolates view interpretation and sampling from input-data generation.

#### Normalized-unsigned legal source handling

**Possible failure symptoms:** `r8g8b8a8_unorm` leaves fail while other decode-mode suffixes for the same eligible source format pass, or a source-format combination reports unexpected behavior.

**Possible implementation causes:** Vulkan prohibits the normalized-unsigned decode mode for views containing ASTC HDR blocks. The source removes 3D SFLOAT-to-UNORM leaves, so a failure among registered normalized-unsigned leaves points to the allowed path, its sampling, or the comparison execution rather than the excluded HDR combination.

#### Shared-exponent feature and comparison adjustment

**Possible failure symptoms:** `e5b9g9r9_ufloat_pack32` cases fail or run unexpectedly on an implementation that does not expose `decodeModeSharedExponent`; affected UNORM or SFLOAT cases can differ from ordinary-mode cases.

**Possible implementation causes:** The implementation may report or honor `decodeModeSharedExponent` incorrectly, or may decode a shared-exponent view differently from the adjustment modeled by the generated shader. For E5B9G9R9 cases, the source clamps the reference to nonnegative channels with alpha one; SFLOAT-flagged cases additionally cap the tested sample at 65504. This test's observable result derives from that source-defined comparison rule.

#### Result storage, synchronization, or readback

**Possible failure symptoms:** Broad failures across decode modes and ASTC formats produce result bytes outside the accepted range, even when sampling behavior may be correct.

**Possible implementation causes:** The compute storage-image write, transfer visibility barriers, result-image copy, or host-visible allocation coherence path may corrupt or hide the pass marker. The source transitions the ASTC images before sampling and the result image before copyback, then invalidates the host allocation before scanning it.

## Case Pruning

### Requirement-based pruning

- [`checkSupport()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L392-L423) requires `VK_EXT_astc_decode_mode`, `textureCompressionASTC_LDR`, supported image-format properties for the selected tested and result images, and storage-image support for the result format.
- `e5b9g9r9_ufloat_pack32` requires `decodeModeSharedExponent`; unsupported implementations skip those cases ([feature gate](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L414-L416)).
- VulkanSC builds omit the source's 3D ASTC format array and its 3D test-case registration loop ([compile guard](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L527-L560) [registration guard](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L592-L615)).

### Design-based pruning

- The 3D SFLOAT-format entries omit the `r8g8b8a8_unorm` mode at registration time ([source condition](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L595-L599)). This is conservative format-based pruning: the Vulkan validity rule itself is phrased in terms of whether the view contains blocks using ASTC HDR modes, while this test generates its blocks with `ASTCMODE_LDR` ([block generation](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L211-L220)).
- The test fixes one mip level, one array layer, nearest filtering, and a local workgroup size of 1. These choices keep each result texel tied to one sampled coordinate while the registered matrix varies source format, dimensionality, and decode mode.

## Key Takeaways

- The test checks a view-local ASTC decode-mode override against an ordinary view of identical compressed data, rather than checking fixed decoded colors.
- The decode-mode suffix controls the principal behavior. Source ASTC footprint, encoding, and 2D or 3D image shape provide the coverage matrix.
- The shader writes a simple pass marker, while the host validates the marker range after explicit image-layout transitions and copyback.
- Shared-exponent and normalized-unsigned paths carry distinct validity and comparison rules. Registration/support checks prune unsupported paths, and sRGB cases verify the specified no-effect behavior.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters | [`TestParameters`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L63-L76) | Defines image type, extent, source format flags, decode mode, and usage fields. |
| Runtime executor | [`BasicComputeTestInstance::iterate()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L95-L371) | Allocates resources, uploads identical blocks, creates views and descriptors, records commands, and validates readback. |
| Support gate | [`AstcDecodeModeCase::checkSupport()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L392-L423) | Checks extension, features, image configuration, and storage-image support. |
| Program generator | [`AstcDecodeModeCase::initPrograms()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L425-L479) | Generates the compute shader and E5B9G9R9 branches. |
| Test-case registration | [`createImageAstcDecodeModeTests()`](../../../modules/vulkan/image/vktImageAstcDecodeModeTests.cpp#L488-L617) | Defines ASTC format arrays, decode modes, VulkanSC guard, and invalid-combination pruning. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) | Adds `astc_decode_mode` to the `image` test category. |
| Vulkan view semantics | [ASTC decode-mode image-view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L7098-L7135) | Defines allowed decode modes, feature requirement, HDR restriction, and sRGB behavior. |
| Vulkan feature semantics | [`decodeModeSharedExponent`](../../../../vulkan-docs/src/chapters/features.adoc#L2248-L2269) | Defines support for the shared-exponent intermediate precision. |
