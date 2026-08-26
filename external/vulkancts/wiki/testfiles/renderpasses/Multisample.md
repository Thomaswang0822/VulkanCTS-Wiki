## Overview

**Core question:** when a render pass writes a distinct value into each sample of a multisample attachment, can a later subpass read each individual sample back through a multisample input attachment and resolve it correctly?

- This page covers the `renderpasses.<rendering>.suballocation.multisample` test family implemented entirely in
  [vktRenderPassMultisampleTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp).
- The test family registers 57 format-named intermediate nodes plus one `separate_stencil_usage` intermediate node under
  `multisample`, attached to the `suballocation` group at
  [vktRenderPassTests.cpp#L8560](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8560).
- For every supported color, depth-only, stencil-only, and depth-stencil format, the test renders a per-sample-distinct
  pattern into a multisample attachment, then reads each sample back with a multisample input attachment in a follow-up
  subpass, resolves it to a single-sample image, and compares it against an XOR-based reference computed on the host.
- The same logic runs under legacy render pass (`renderpass1`), render pass 2 (`renderpass2`), and dynamic rendering
  (`dynamic_rendering`). The representative root shown below is `renderpass1`; the registered name differs only in the
  rendering-type root.

## Background Knowledge

- **Multisample attachment samples are independent.** A multisample color or depth/stencil attachment stores one value
  per sample location per pixel. Per-sample writes controlled by `gl_SampleMask` therefore land in distinct sample
  slots, and a correct implementation must keep those slots separate until resolve.
- **Multisample input attachment reads.** A multisample input attachment (`subpassInputMS` in GLSL) is read with
  `subpassLoad(i_attach, sampleIndex)`, which returns the value stored in one specific sample. The Vulkan spec restricts
  a fragment to the samples covered by its input `SampleMask`, so the test renders a single fully-covered triangle to
  guarantee every sample is readable in every fragment.
- **Resolve.** Resolving combines the per-sample values of a multisample image into one single-sample pixel. For color
  the default is averaging; for integer formats the test forces sample-zero resolve. The test resolves each sample
  independently into its own single-sample image, so the host can inspect every sample separately.
- **`MAX_COLOR_ATTACHMENT_COUNT` split.** Vulkan limits a subpass to four color attachments. To copy all samples of a
  high-sample-count attachment out through color attachments, the test splits the copies across multiple follow-up
  subpasses, each handling up to four samples.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.multisample
├── a2b10g10r10_uint_pack32
├── a2b10g10r10_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a8_unorm
├── a8b8g8r8_sint_pack32
├── a8b8g8r8_snorm_pack32
├── a8b8g8r8_srgb_pack32
├── a8b8g8r8_uint_pack32
├── a8b8g8r8_unorm_pack32
├── b8g8r8a8_srgb
├── b8g8r8a8_unorm
├── d16_unorm
├── d16_unorm_s8_uint
├── d24_unorm_s8_uint
├── d32_sfloat
├── d32_sfloat_s8_uint
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r16_sfloat
├── r16_sint
├── r16_snorm
├── r16_uint
├── r16_unorm
├── r16g16_sfloat
├── r16g16_sint
├── r16g16_snorm
├── r16g16_uint
├── r16g16_unorm
├── r16g16b16a16_sfloat
├── r16g16b16a16_sint
├── r16g16b16a16_snorm
├── r16g16b16a16_uint
├── r16g16b16a16_unorm
├── r32_sfloat
├── r32_sint
├── r32_uint
├── r32g32_sfloat
├── r32g32_sint
├── r32g32_uint
├── r32g32b32a32_sfloat
├── r32g32b32a32_sint
├── r32g32b32a32_uint
├── r5g6b5_unorm_pack16
├── r8_sint
├── r8_snorm
├── r8_uint
├── r8_unorm
├── r8g8_sint
├── r8g8_snorm
├── r8g8_uint
├── r8g8_unorm
├── r8g8b8a8_sint
├── r8g8b8a8_snorm
├── r8g8b8a8_srgb
├── r8g8b8a8_uint
├── r8g8b8a8_unorm
├── s8_uint
├── separate_stencil_usage
└── x8_d24_unorm_pack32
```

The `multisample` test family is created by
[`createRenderPassMultisampleTests()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2513-L2516).
Its format-named intermediate nodes are added in
[`initTests()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2392-L2509), and the
`separate_stencil_usage` node is attached at the end of that same function
([vktRenderPassMultisampleTests.cpp#L2456-L2508](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2456-L2508)).
Each format-named node expands to `samples_<N>` test case leaves for N in {2, 4, 8, 16, 32}; the
`separate_stencil_usage` node expands to `<format>/samples_<N>/test_depth` and `test_stencil` leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | 57 `VkFormat` values spanning color, depth-only, stencil-only, and depth-stencil classes | Selects the multisample attachment format. The format drives the generated fragment shader type (`vec4`/`ivec4`/`uvec4`), the input-attachment GLSL type, the destination resolve format, and the host comparison routine. | [formats array](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2394-L2453) |
| Sample count | `2`, `4`, `8`, `16`, `32` | The multisample attachment sample count. Each sample receives a distinct XOR-pattern value; higher counts exercise more split subpasses and more per-sample reads. | [sampleCounts](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2454) |
| Separate stencil usage | `TEST_DEPTH`, `TEST_STENCIL` | Only used inside `separate_stencil_usage`. Selects whether the depth aspect or the stencil aspect of a combined depth/stencil format is exercised with `VK_EXT_separate_stencil_usage`. | [TestSeparateUsage enum](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L97-L101) |

The 57 entries in the formats array map one-to-one to the 57 registered format-named nodes; each node expands to
`samples_<N>` test case leaves for N in {2, 4, 8, 16, 32}. The `separate_stencil_usage` node is a separate registration
that reuses three of the depth/stencil formats with an extra `VkImageStencilUsageCreateInfo`.

## Behavior Parameters

The primary behavioral axis is the format class of the multisample attachment, because it changes which aspect is
written, how the per-sample value is generated, and how the host validates the result. The `separate_stencil_usage`
node is a second, smaller axis that reuses the depth/stencil path with a separate-usage image.

### Color formats: per-sample XOR color written through `gl_SampleMask`

For each color format the first subpass draws one fully-covered triangle `sampleCount` times. Each draw writes exactly
one sample (`gl_SampleMask[0] = int(0x1u << sampleIndex)` for unsigned/signed/floating paths) and computes a per-pixel
color from an XOR of the fragment coordinate bits with the sample index
([Programs::init color path](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2014-L2199)). The
generated color type matches the format's channel class: `uvec4` for unsigned integer, `ivec4` for signed integer, and
`vec4` for unsigned/signed fixed-point and floating-point. Each follow-up subpass then reads the multisample input
attachment one sample at a time with `subpassLoad(i_color, sampleIndex)` and writes it to one of up to four color
attachments, which the render pass resolves to single-sample images.

### Depth-only and stencil-only formats: depth value or stencil counter per sample

Depth-only formats (`d16_unorm`, `x8_d24_unorm_pack32`, `d32_sfloat`) write a per-sample depth computed from the same
XOR bit pattern, and the stencil-only format `s8_uint` writes a per-sample stencil counter through
`VK_STENCIL_OP_INCREMENT_AND_WRAP`. The first-subpass shader for depth sets
`gl_SampleMask[0] = int((~0x0u) << sampleIndex)` and writes `gl_FragDepth`
([depth shader](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1963-L2000)); the stencil path
sets the same mask and lets the fixed-function stencil stage increment the value
([stencil shader](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2001-L2013)). Follow-up subpasses
read each sample back through a depth or stencil multisample input attachment and copy it to a color attachment.

### Depth-stencil formats: both aspects read in one pass

Combined depth/stencil formats (`d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`) write both aspects in
the first subpass and read both back through two input attachments (`i_depth` and `i_stencil`) in the split subpasses
([split shader](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2206-L2269)). The destination
format for these cases is `VK_FORMAT_R32G32_SFLOAT`, packing depth and stencil into one resolve target.

### `separate_stencil_usage`: `VK_EXT_separate_stencil_usage` aspect isolation

The `separate_stencil_usage` node applies only to the three combined depth/stencil formats. For each, it registers two
leaves per sample count: `test_depth` and `test_stencil`
([registration](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2481-L2501)). The test creates
the source image with a `VkImageStencilUsageCreateInfo` that assigns a different usage to the stencil aspect than to
the depth aspect ([createImage](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L162-L202)), then
exercises only the selected aspect through the matching input attachment view
([createSrcPrimaryInputImageView](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L315-L327)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.renderpass1.suballocation.multisample.r8g8b8a8_unorm.samples_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r8g8b8a8_unorm` | Selects the unsigned fixed-point color branch: the producer writes a `vec4`, and the split reader uses `subpassInputMS` with `vec4` outputs. |
| `samples_4` | Four draws select one sample at a time; one split subpass can export all four through four color attachments. |
| `renderpass1` | Selects the legacy render-pass path. The shader-visible input-attachment and push-constant interfaces are shared by the render-pass 2 and dynamic-rendering variants. |

#### Purpose

The producer fragment shader writes a deterministic value to exactly one multisample sample on each draw. The split reader loads the four samples independently through a multisample input attachment, making sample aliasing or incorrect sample-index routing observable after resolve.

#### Structural Design

| Phase | Shader operation | Evidence carried forward |
|-------|------------------|---------------------------|
| Per-sample producer | Read `sampleIndex`, set `gl_SampleMask[0]` to `1 << sampleIndex`, and derive `x`/`y` by XORing fragment coordinates with that index. | Coverage identifies one sample and the XOR pattern distinguishes samples. |
| Pattern construction | Accumulate selected coordinate bits into four channels using weights `0.5`, `0.25`, and `0.125`. | Every pixel/sample receives a deterministic value. |
| Split reader | Read sample `4 * splitSubpassIndex + attachmentNdx` into a separate output. | Each resolve attachment corresponds to one source sample. |

#### Shader Code

##### Fragment Producer Shader

```glsl
#version 450
layout(location = 0) out highp vec4 o_color;
layout(push_constant) uniform PushConstant {
\thighp uint sampleIndex;
} pushConstants;
void main (void)
{
\thighp uint sampleIndex = pushConstants.sampleIndex;
\tgl_SampleMask[0] = int(0x1u << sampleIndex);
\thighp float color[4];
\thighp uint x = sampleIndex ^ uint(gl_FragCoord.x);
\thighp uint y = sampleIndex ^ uint(gl_FragCoord.y);
\tcolor[0] = 0;
\tcolor[1] = 0;
\tcolor[2] = 0;
\tcolor[3] = 0;
\tcolor[0] += 0.5 * float(bitfieldExtract(x, 0, 1));
\tcolor[1] += 0.5 * float(bitfieldExtract(y, 0, 1));
\tcolor[2] += 0.5 * float(bitfieldExtract(x, 1, 1));
\tcolor[3] += 0.5 * float(bitfieldExtract(y, 1, 1));
\tcolor[0] += 0.25 * float(bitfieldExtract(x, 2, 1));
\tcolor[1] += 0.25 * float(bitfieldExtract(y, 2, 1));
\tcolor[2] += 0.25 * float(bitfieldExtract(x, 3, 1));
\tcolor[3] += 0.25 * float(bitfieldExtract(y, 3, 1));
\tcolor[0] += 0.125 * float(bitfieldExtract(x, 4, 1));
\tcolor[1] += 0.125 * float(bitfieldExtract(y, 4, 1));
\tcolor[2] += 0.125 * float(bitfieldExtract(x, 5, 1));
\tcolor[3] += 0.125 * float(bitfieldExtract(y, 5, 1));
\to_color = vec4(color[0], color[1], color[2], color[3]);
}
```

##### Fragment Split-Reader Shader

```glsl
#version 450
/// Binding 0 is the multisample color input attachment produced by the first subpass.
layout(input_attachment_index = 0, set = 0, binding = 0) uniform highp subpassInputMS i_color;
/// The host selects which group of at most four samples this split subpass exports.
layout(push_constant) uniform PushConstant {
\thighp uint splitSubpassIndex;
} pushConstants;
/// Four color attachments provide the fan-out; each is resolved separately.
layout(location = 0) out highp vec4 o_color0;
layout(location = 1) out highp vec4 o_color1;
layout(location = 2) out highp vec4 o_color2;
layout(location = 3) out highp vec4 o_color3;
void main (void)
{
\to_color0 = subpassLoad(i_color, int(4 * pushConstants.splitSubpassIndex + 0u));
\to_color1 = subpassLoad(i_color, int(4 * pushConstants.splitSubpassIndex + 1u));
\to_color2 = subpassLoad(i_color, int(4 * pushConstants.splitSubpassIndex + 2u));
\to_color3 = subpassLoad(i_color, int(4 * pushConstants.splitSubpassIndex + 3u));
}
```

#### Additional Info

- The split-reader is primary because the defining operation is the per-sample `subpassLoad`; the producer is included because it supplies the distinct values that make a wrong read observable.
- `quad-vert` is a fixed single-triangle stage shared by the format branches. Its only visible triangle fully covers fragments, which is required for reliable multisample input-attachment access.
- For `r8g8b8a8_unorm`, the generator uses `valueMin = 0`, `valueMax = 1`, four used channels, and ten source bits, yielding the literals shown above.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format channel class | Integer classes select `uvec4` or `ivec4`; fixed-point/floating classes select `vec4`; depth/stencil formats select aspect-specific readers. | [`Programs::init()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1938-L2326) |
| Sample count | The push-constant sample index remains the same; the split reader emits at most four outputs and uses `4 * splitSubpassIndex + attachmentNdx`, adding split subpasses above four samples. | [`Programs::init()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2206-L2326) |
| Separate stencil usage | The selected aspect changes the producer and split-reader declarations for depth versus stencil. | [`Programs::init()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1942-L2013) |

#### SPIR-V

##### Fragment Producer Shader

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
; Bound: 169
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_SampleMask %gl_FragCoord %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %sampleIndex "sampleIndex"
               OpName %PushConstant "PushConstant"
               OpMemberName %PushConstant 0 "sampleIndex"
               OpName %pushConstants "pushConstants"
               OpName %gl_SampleMask "gl_SampleMask"
               OpName %x "x"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %y "y"
               OpName %color "color"
               OpName %o_color "o_color"
               OpDecorate %PushConstant Block
               OpMemberDecorate %PushConstant 0 Offset 0
               OpDecorate %gl_SampleMask BuiltIn SampleMask
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %o_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%PushConstant = OpTypeStruct %uint
%_ptr_PushConstant_PushConstant = OpTypePointer PushConstant %PushConstant
%pushConstants = OpVariable %_ptr_PushConstant_PushConstant PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_1 = OpConstant %uint 1
%_arr_int_uint_1 = OpTypeArray %int %uint_1
%_ptr_Output__arr_int_uint_1 = OpTypePointer Output %_arr_int_uint_1
%gl_SampleMask = OpVariable %_ptr_Output__arr_int_uint_1 Output
%_ptr_Output_int = OpTypePointer Output %int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Function__arr_float_uint_4 = OpTypePointer Function %_arr_float_uint_4
    %float_0 = OpConstant %float 0
%_ptr_Function_float = OpTypePointer Function %float
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
  %float_0_5 = OpConstant %float 0.5
 %float_0_25 = OpConstant %float 0.25
%float_0_125 = OpConstant %float 0.125
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
%sampleIndex = OpVariable %_ptr_Function_uint Function
          %x = OpVariable %_ptr_Function_uint Function
          %y = OpVariable %_ptr_Function_uint Function
      %color = OpVariable %_ptr_Function__arr_float_uint_4 Function
         %15 = OpAccessChain %_ptr_PushConstant_uint %pushConstants %int_0
         %16 = OpLoad %uint %15
               OpStore %sampleIndex %16
         %21 = OpLoad %uint %sampleIndex
         %22 = OpShiftLeftLogical %uint %uint_1 %21
         %23 = OpBitcast %int %22
         %25 = OpAccessChain %_ptr_Output_int %gl_SampleMask %int_0
               OpStore %25 %23
         %27 = OpLoad %uint %sampleIndex
         %34 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %35 = OpLoad %float %34
         %36 = OpConvertFToU %uint %35
         %37 = OpBitwiseXor %uint %27 %36
               OpStore %x %37
         %39 = OpLoad %uint %sampleIndex
         %40 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %41 = OpLoad %float %40
         %42 = OpConvertFToU %uint %41
         %43 = OpBitwiseXor %uint %39 %42
               OpStore %y %43
         %50 = OpAccessChain %_ptr_Function_float %color %int_0
               OpStore %50 %float_0
         %52 = OpAccessChain %_ptr_Function_float %color %int_1
               OpStore %52 %float_0
         %54 = OpAccessChain %_ptr_Function_float %color %int_2
               OpStore %54 %float_0
         %56 = OpAccessChain %_ptr_Function_float %color %int_3
               OpStore %56 %float_0
         %58 = OpLoad %uint %x
         %59 = OpBitFieldUExtract %uint %58 %int_0 %int_1
         %60 = OpConvertUToF %float %59
         %61 = OpFMul %float %float_0_5 %60
         %62 = OpAccessChain %_ptr_Function_float %color %int_0
         %63 = OpLoad %float %62
         %64 = OpFAdd %float %63 %61
         %65 = OpAccessChain %_ptr_Function_float %color %int_0
               OpStore %65 %64
         %66 = OpLoad %uint %y
         %67 = OpBitFieldUExtract %uint %66 %int_0 %int_1
         %68 = OpConvertUToF %float %67
         %69 = OpFMul %float %float_0_5 %68
         %70 = OpAccessChain %_ptr_Function_float %color %int_1
         %71 = OpLoad %float %70
         %72 = OpFAdd %float %71 %69
         %73 = OpAccessChain %_ptr_Function_float %color %int_1
               OpStore %73 %72
         %74 = OpLoad %uint %x
         %75 = OpBitFieldUExtract %uint %74 %int_1 %int_1
         %76 = OpConvertUToF %float %75
         %77 = OpFMul %float %float_0_5 %76
         %78 = OpAccessChain %_ptr_Function_float %color %int_2
         %79 = OpLoad %float %78
         %80 = OpFAdd %float %79 %77
         %81 = OpAccessChain %_ptr_Function_float %color %int_2
               OpStore %81 %80
         %82 = OpLoad %uint %y
         %83 = OpBitFieldUExtract %uint %82 %int_1 %int_1
         %84 = OpConvertUToF %float %83
         %85 = OpFMul %float %float_0_5 %84
         %86 = OpAccessChain %_ptr_Function_float %color %int_3
         %87 = OpLoad %float %86
         %88 = OpFAdd %float %87 %85
         %89 = OpAccessChain %_ptr_Function_float %color %int_3
               OpStore %89 %88
         %91 = OpLoad %uint %x
         %92 = OpBitFieldUExtract %uint %91 %int_2 %int_1
         %93 = OpConvertUToF %float %92
         %94 = OpFMul %float %float_0_25 %93
         %95 = OpAccessChain %_ptr_Function_float %color %int_0
         %96 = OpLoad %float %95
         %97 = OpFAdd %float %96 %94
         %98 = OpAccessChain %_ptr_Function_float %color %int_0
               OpStore %98 %97
         %99 = OpLoad %uint %y
        %100 = OpBitFieldUExtract %uint %99 %int_2 %int_1
        %101 = OpConvertUToF %float %100
        %102 = OpFMul %float %float_0_25 %101
        %103 = OpAccessChain %_ptr_Function_float %color %int_1
        %104 = OpLoad %float %103
        %105 = OpFAdd %float %104 %102
        %106 = OpAccessChain %_ptr_Function_float %color %int_1
               OpStore %106 %105
        %107 = OpLoad %uint %x
        %108 = OpBitFieldUExtract %uint %107 %int_3 %int_1
        %109 = OpConvertUToF %float %108
        %110 = OpFMul %float %float_0_25 %109
        %111 = OpAccessChain %_ptr_Function_float %color %int_2
        %112 = OpLoad %float %111
        %113 = OpFAdd %float %112 %110
        %114 = OpAccessChain %_ptr_Function_float %color %int_2
               OpStore %114 %113
        %115 = OpLoad %uint %y
        %116 = OpBitFieldUExtract %uint %115 %int_3 %int_1
        %117 = OpConvertUToF %float %116
        %118 = OpFMul %float %float_0_25 %117
        %119 = OpAccessChain %_ptr_Function_float %color %int_3
        %120 = OpLoad %float %119
        %121 = OpFAdd %float %120 %118
        %122 = OpAccessChain %_ptr_Function_float %color %int_3
               OpStore %122 %121
        %124 = OpLoad %uint %x
        %126 = OpBitFieldUExtract %uint %124 %int_4 %int_1
        %127 = OpConvertUToF %float %126
        %128 = OpFMul %float %float_0_125 %127
        %129 = OpAccessChain %_ptr_Function_float %color %int_0
        %130 = OpLoad %float %129
        %131 = OpFAdd %float %130 %128
        %132 = OpAccessChain %_ptr_Function_float %color %int_0
               OpStore %132 %131
        %133 = OpLoad %uint %y
        %134 = OpBitFieldUExtract %uint %133 %int_4 %int_1
        %135 = OpConvertUToF %float %134
        %136 = OpFMul %float %float_0_125 %135
        %137 = OpAccessChain %_ptr_Function_float %color %int_1
        %138 = OpLoad %float %137
        %139 = OpFAdd %float %138 %136
        %140 = OpAccessChain %_ptr_Function_float %color %int_1
               OpStore %140 %139
        %141 = OpLoad %uint %x
        %143 = OpBitFieldUExtract %uint %141 %int_5 %int_1
        %144 = OpConvertUToF %float %143
        %145 = OpFMul %float %float_0_125 %144
        %146 = OpAccessChain %_ptr_Function_float %color %int_2
        %147 = OpLoad %float %146
        %148 = OpFAdd %float %147 %145
        %149 = OpAccessChain %_ptr_Function_float %color %int_2
               OpStore %149 %148
        %150 = OpLoad %uint %y
        %151 = OpBitFieldUExtract %uint %150 %int_5 %int_1
        %152 = OpConvertUToF %float %151
        %153 = OpFMul %float %float_0_125 %152
        %154 = OpAccessChain %_ptr_Function_float %color %int_3
        %155 = OpLoad %float %154
        %156 = OpFAdd %float %155 %153
        %157 = OpAccessChain %_ptr_Function_float %color %int_3
               OpStore %157 %156
        %160 = OpAccessChain %_ptr_Function_float %color %int_0
        %161 = OpLoad %float %160
        %162 = OpAccessChain %_ptr_Function_float %color %int_1
        %163 = OpLoad %float %162
        %164 = OpAccessChain %_ptr_Function_float %color %int_2
        %165 = OpLoad %float %164
        %166 = OpAccessChain %_ptr_Function_float %color %int_3
        %167 = OpLoad %float %166
        %168 = OpCompositeConstruct %v4float %161 %163 %165 %167
               OpStore %o_color %168
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Split-Reader Shader

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
; Bound: 58
; Schema: 0
               OpCapability Shader
               OpCapability InputAttachment
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color0 %o_color1 %o_color2 %o_color3
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %o_color0 "o_color0"
               OpName %i_color "i_color"
               OpName %PushConstant "PushConstant"
               OpMemberName %PushConstant 0 "splitSubpassIndex"
               OpName %pushConstants "pushConstants"
               OpName %o_color1 "o_color1"
               OpName %o_color2 "o_color2"
               OpName %o_color3 "o_color3"
               OpDecorate %o_color0 Location 0
               OpDecorate %i_color Binding 0
               OpDecorate %i_color DescriptorSet 0
               OpDecorate %i_color InputAttachmentIndex 0
               OpDecorate %PushConstant Block
               OpMemberDecorate %PushConstant 0 Offset 0
               OpDecorate %o_color1 Location 1
               OpDecorate %o_color2 Location 2
               OpDecorate %o_color3 Location 3
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %o_color0 = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float SubpassData 0 0 1 2 Unknown
%_ptr_UniformConstant_10 = OpTypePointer UniformConstant %10
    %i_color = OpVariable %_ptr_UniformConstant_10 UniformConstant
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%PushConstant = OpTypeStruct %uint
%_ptr_PushConstant_PushConstant = OpTypePointer PushConstant %PushConstant
%pushConstants = OpVariable %_ptr_PushConstant_PushConstant PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_0 = OpConstant %uint 0
      %v2int = OpTypeVector %int 2
         %29 = OpConstantComposite %v2int %int_0 %int_0
   %o_color1 = OpVariable %_ptr_Output_v4float Output
     %uint_1 = OpConstant %uint 1
   %o_color2 = OpVariable %_ptr_Output_v4float Output
     %uint_2 = OpConstant %uint 2
   %o_color3 = OpVariable %_ptr_Output_v4float Output
     %uint_3 = OpConstant %uint 3
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %10 %i_color
         %22 = OpAccessChain %_ptr_PushConstant_uint %pushConstants %int_0
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %uint_4 %23
         %26 = OpIAdd %uint %24 %uint_0
         %27 = OpBitcast %int %26
         %30 = OpImageRead %v4float %13 %29 Sample %27
               OpStore %o_color0 %30
         %32 = OpLoad %10 %i_color
         %33 = OpAccessChain %_ptr_PushConstant_uint %pushConstants %int_0
         %34 = OpLoad %uint %33
         %35 = OpIMul %uint %uint_4 %34
         %37 = OpIAdd %uint %35 %uint_1
         %38 = OpBitcast %int %37
         %39 = OpImageRead %v4float %32 %29 Sample %38
               OpStore %o_color1 %39
         %41 = OpLoad %10 %i_color
         %42 = OpAccessChain %_ptr_PushConstant_uint %pushConstants %int_0
         %43 = OpLoad %uint %42
         %44 = OpIMul %uint %uint_4 %43
         %46 = OpIAdd %uint %44 %uint_2
         %47 = OpBitcast %int %46
         %48 = OpImageRead %v4float %41 %29 Sample %47
               OpStore %o_color2 %48
         %50 = OpLoad %10 %i_color
         %51 = OpAccessChain %_ptr_PushConstant_uint %pushConstants %int_0
         %52 = OpLoad %uint %51
         %53 = OpIMul %uint %uint_4 %52
         %55 = OpIAdd %uint %53 %uint_3
         %56 = OpBitcast %int %55
         %57 = OpImageRead %v4float %50 %29 Sample %56
               OpStore %o_color3 %57
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The host builds one multisample source image, `sampleCount` multisample destination color images, `sampleCount`
single-sample resolve images, and `sampleCount` host-visible readback buffers
([constructor](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1056-L1130)).

A single command buffer records the render pass
([iterateInternal](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1368-L1427) for legacy and
render pass 2, [iterateInternalDynamicRendering](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1429-L1587)
for dynamic rendering):

- The first subpass draws the quad `sampleCount` times, each time pushing a different `sampleIndex` and letting the
  fragment shader mask coverage to one sample
  ([drawFirstSubpass](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1646-L1655)).
- For stencil-bearing formats the stencil aspect is cleared to zero before the first draw so the increment produces a
  known per-sample value ([iterateInternal](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1392-L1408)).
- Each follow-up subpass binds one split pipeline, pushes its `splitSubpassIndex`, and copies up to four samples out of
  the input attachment into color attachments that the render pass resolves
  ([drawNextSubpass](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1657-L1666)). The number of
  split subpasses is `ceil(sampleCount / 4)`.
- After the render pass, each single-sample resolve image is copied to its host-visible buffer
  ([postRenderCommands](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1668-L1677)).

Result checking happens per sample in
[`verifyResult()`](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1679-L1934). For each sample
the host recomputes the same XOR-based reference the shader used, then compares the readback buffer against it:

- **Depth** uses `tcu::floatThresholdCompare` with a threshold of `1.0f / 1024.0f`
  ([vktRenderPassMultisampleTests.cpp#L1702-L1747](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1702-L1747)).
- **Stencil** uses an exact integer comparison
  ([vktRenderPassMultisampleTests.cpp#L1724-L1747](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1724-L1747)).
- **Color** dispatches on `tcu::TextureChannelClass`: unsigned and signed integer formats use exact
  `tcu::intThresholdCompare` with a zero threshold; floating-point formats use `tcu::floatUlpThresholdCompare` allowing
  64 ULP; fixed-point formats use `tcu::floatThresholdCompare` allowing four times the minimum presentable difference
  ([vktRenderPassMultisampleTests.cpp#L1749-L1930](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1749-L1930)).
  sRGB formats are compared in sRGB space.
- Any per-sample mismatch is recorded through `m_resultCollector.fail("Compare failed for sample " + ...)`, and the
  case returns the aggregated status.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Color format | Per-sample color value wrong, input-attachment per-sample read returns the wrong sample, or resolve picked the wrong sample / averaged when it should not. |
| Depth-only format | Per-sample depth value wrong, depth input-attachment read returns the wrong sample, or depth resolve mode incorrect. |
| Stencil-only format (`s8_uint`) | Stencil clear or increment wrong, stencil input-attachment read returns the wrong sample, or stencil resolve incorrect. |
| Depth-stencil format | Depth or stencil aspect wrong (same causes as the single-aspect cases), or the two aspects interfered when packed into the `R32G32_SFLOAT` resolve target. |
| `separate_stencil_usage` `test_depth` | Depth aspect value wrong when the stencil aspect has a separate usage, or the separate-usage image view exposed the wrong aspect. |
| `separate_stencil_usage` `test_stencil` | Stencil aspect value wrong when it has a separate usage, or the stencil aspect was not actually isolated from the depth aspect. |

A failure shared across all values, for example a wrong sample count, a wrong resolve target, or a host reference bug , 
would point at the shared render-pass / resolve infrastructure rather than a format-specific path.

### Cause Analysis

#### Per-sample value or coverage wrong

**Possible failure symptoms:** the compared image for one or more samples differs from the XOR reference; the mismatch
follows a sample-index pattern (for example only odd samples, or only the first subpass's four samples).

**Possible implementation causes:** the fragment shader computed the wrong per-sample value, `gl_SampleMask` did not
isolate the intended sample, or the depth/stencil state wrote depth or stencil to a sample other than the masked one.
The host recomputes the same XOR pattern, so a shader-compiler lowering of `bitfieldExtract` or `gl_SampleMask` that
changed coverage would surface here.

#### Multisample input-attachment read returns the wrong sample

**Possible failure symptoms:** the resolve image for sample *i* contains the value that should have landed in sample
*j*, or a swapped/mirrored sample ordering across the split subpasses.

**Possible implementation causes:** the implementation's `subpassLoad` on a multisample input attachment returned the
wrong sample index, the split-pipeline `splitSubpassIndex` push constant was misrouted, or the
`VK_KHR_dynamic_rendering_local_read` attachment-location / input-attachment-index remapping pointed at the wrong
sample for the dynamic-rendering path.

#### Resolve picked the wrong sample or mode

**Possible failure symptoms:** the single-sample resolve image holds an averaged value instead of one specific sample
(for integer formats), or holds sample zero instead of the requested sample.

**Possible implementation causes:** the resolve mode was not set to `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` for integer color
formats, the resolve attachment was bound to the wrong source sample, or the per-sample single-sample resolve target
received a resolve from the wrong multisample image. The test deliberately uses one resolve target per sample to expose
exactly this kind of mismatch.

#### Depth/stencil aspect isolation or packing wrong

**Possible failure symptoms:** for combined depth/stencil formats, only one of the two channels of the `R32G32_SFLOAT`
resolve matches; for `separate_stencil_usage`, the aspect that was supposed to be untested still appears in the result.

**Possible implementation causes:** the depth and stencil input-attachment views exposed the wrong aspects, the
separate-usage create-info did not actually separate the aspects, or the packed `vec2(depth, stencil)` write was
reordered. Source-level investigation is needed before attributing these to driver or hardware.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_create_renderpass2` is required for the `renderpass2` root
  ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2328-L2380)).
- `VK_KHR_dynamic_rendering_local_read` is required for the `dynamic_rendering` root; on Vulkan 1.4 and above the test
  also requires `dynamicRenderingLocalReadMultisampledAttachments`, and for depth/stencil formats
  `dynamicRenderingLocalReadDepthStencilAttachments`.
- `VK_EXT_separate_stencil_usage` plus `VK_KHR_get_physical_device_properties2` are required for any case under
  `separate_stencil_usage`.
- `VK_KHR_maintenance5` is required for `VK_FORMAT_A8_UNORM_KHR` (`a8_unorm`).
- A case is skipped with `NotSupportedError` when the physical device does not support the format as a color or
  depth/stencil attachment at the requested sample count
  ([createImage](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L235-L292)).

### Design-based pruning

- Non-monolithic pipelines (pipeline libraries and fast-linked libraries) skip `samples_16` and `samples_32`, so only
  `samples_2`, `samples_4`, and `samples_8` are registered for those pipeline construction types
  ([initTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2467-L2470)). This trims
  redundant repetition of the same per-sample behavior at high sample counts.
- The `separate_stencil_usage` node is populated only for the three combined depth/stencil formats, because the
  extension only applies where depth and stencil coexist in one image
  ([initTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2482-L2484)).

## Key Takeaways

- The test isolates each sample of a multisample attachment by masking coverage to one sample per draw, then reads that
  sample back through a multisample input attachment. A failure almost always means a sample was not kept separate.
- The four-color-attachment limit forces the readback into `ceil(sampleCount / 4)` split subpasses; a mismatch that
  clusters by groups of four samples points at split-subpass routing, not at the format itself.
- Resolve is intentionally per-sample: one single-sample image per sample. Integer formats use sample-zero resolve;
  other color formats average; depth/stencil is copied through a packed `R32G32_SFLOAT` target.
- `separate_stencil_usage` reuses the depth/stencil path with a `VkImageStencilUsageCreateInfo`, so a failure there
  isolates whether separate stencil usage correctly decoupled the two aspects.
- See `## Failure Meaning` for how each symptom maps to a cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family creation | [createRenderPassMultisampleTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2513-L2516) | Top-level group named `multisample`. |
| Registration / matrix | [initTests](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2392-L2509) | Builds the 57 format nodes, the sample-count leaves, and the `separate_stencil_usage` node. |
| Format and sample-count tables | [formats / sampleCounts](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2394-L2454) | The generated matrix dimensions. |
| Test instance | [MultisampleRenderPassTestInstance](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L984-L1054) | Resource setup, pipelines, and iterate entry points. |
| Render pass construction | [createRenderPass (template)](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L470-L717), [createRenderPass (dispatch)](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L719-L738) | Builds the multi-subpass render pass with input and resolve attachments. |
| Separate-usage image creation | [createImage](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L162-L202) | Wires `VkImageStencilUsageCreateInfo` for `separate_stencil_usage`. |
| Shader generation | [Programs::init](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1938-L2326) | Generates `quad-vert`, `quad-frag`, and `quad-split-frag` per format class. |
| Feature / support checks | [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2328-L2380) | Extension and limit gating per rendering type. |
| Result verification | [verifyResult](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1679-L1934) | Per-sample host comparison and tolerance selection. |
| Attachment to category | [vktRenderPassTests.cpp#L8560](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8560) | Where `multisample` is attached under `suballocation`. |
