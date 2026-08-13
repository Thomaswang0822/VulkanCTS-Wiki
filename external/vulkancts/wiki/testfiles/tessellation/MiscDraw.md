## Overview

**Core question:** Do tessellation draws produce the right pixels when domain generation, draw form, instancing, or tessellation state changes?

- This page covers the `tessellation.misc_draw` test family in `vktTessellationMiscDrawTests.cpp`, plus its delegated Amber regression.
- The family has 107 leaves in the default Vulkan mustpass list. They test domain coverage and overlap, isolines, incomplete and instanced patches, state changes between draws, and a tessellation-control barrier regression.
- Most cases validate a rendered image. Each mechanism has its own reference: PNG images, a software-rendered result, an independently rendered second-state image, or an exact Amber framebuffer expectation.

## Background Knowledge

- **Patch tessellation:** A patch supplies control points to the tessellation stages. The tessellation control shader writes inner and outer levels, the fixed-function tessellator generates domain coordinates, and the tessellation evaluation shader maps those coordinates to positions. A relevant outer level at or below zero discards the patch. See the specification's [patch-discard rule](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178).
- **Domain guarantees:** Triangle and quad tessellation must cover the domain without overlapping generated triangles, although the detailed subdivision and primitive order can vary by implementation. Isoline tessellation derives line count and segment count from its first two outer levels. See [triangle coverage](../../../../vulkan-docs/src/chapters/tessellation.adoc#L355-L396), [quad coverage](../../../../vulkan-docs/src/chapters/tessellation.adoc#L465-L492), and [isoline generation](../../../../vulkan-docs/src/chapters/tessellation.adoc#L495-L530).
- **Bound draw state:** A draw consumes the graphics state active at that command. State-switch cases issue an offscreen draw with one tessellation configuration, bind another, and compare the visible draw with an independent reference that used the second configuration directly.

## Registration Hierarchy

The tree shows one representative executable leaf for each major behavior. The next section describes the full generated matrix, and the [default Vulkan mustpass range](../../../mustpass/main/vk-default/tessellation.txt#L237-L343) confirms it.

```text
tessellation.misc_draw
├── fill_cover_quads_equal_spacing_draw
├── fill_overlap_quads_equal_spacing_draw
├── isolines_equal_spacing_draw
├── quads_no_patches
├── quads_instances
├── switch_primitive_quads_to_triangles
└── tess_factor_barrier_bug
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Behavioral group | `fill_cover`, `fill_overlap`, `isolines`, `no_patches`, `instances`, `state_switch`, `tess_factor_barrier_bug` | Selects the tested property and validation method. | [registration](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1874-L2080) |
| Primitive domain | `triangles`, `quads`; `isolines` in isoline leaves | Changes patch size, domain coordinates, and generated primitive type. | [fill/isoline loops](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1864-L1929) |
| Spacing | `equal_spacing`, `fractional_even_spacing`, `fractional_odd_spacing` | Changes level rounding and segment placement. | [spacing loops](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1877-L1929) |
| Draw form | `draw`, `draw_indirect` | Submits the same patch through `vkCmdDraw` or `vkCmdDrawIndirect`. | [draw selection](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L325-L330) |
| Tessellation-level set | three internal sets per fill or isoline leaf | Exercises uniform and nonuniform inner/outer levels after spacing-specific rounding. This dimension repeats inside one executable case and is not part of its name. | [level generation](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L88-L112) |
| State-switch property | `primitive`, `domain_origin`, `spacing_mode`, `out_vertices` | Selects which tessellation state differs between the offscreen and visible draws. | [switch matrix](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1974-L2068) |
| Switch direction | both unequal ordered pairs | Tests both transitions, such as `quads_to_triangles` and `triangles_to_quads`. | [pair pruning](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1979-L2068) |
| Construction | no suffix, `_fast_lib`, `_shader_objects` | Uses monolithic pipelines, fast-linked pipeline libraries, or unlinked SPIR-V shader objects. | [construction cases](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1954-L1972) |
| Geometry stage | no suffix, `_with_geom_shader` | Inserts a pass-through geometry shader into state-switch cases. | [geometry variants](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1965-L1972) |
| Instanced behavior | `no_patches`, `instances` | Draws too few control points for a patch or four complete translated patch instances. | [instanced registration](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1932-L1951) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group** encoded by each test case leaf's name. These groups change the correctness property and the way failure becomes observable.

### `fill_cover`: complete triangle or quad coverage

The evaluation shader distorts the mapped domain positions while filling the patch white. Three tessellation-level sets must match PNG references. Missing generated coverage appears as dark gaps. Triangle and quad variants run under all three spacing modes through direct and indirect draws.

### `fill_overlap`: non-overlapping generated triangles

The shader assigns red, green, and blue bands from tessellation coordinates and inner levels. Incorrect overlap can replace one band's color with another, producing a reference mismatch. The domain, spacing, draw-form, and level-set matrix matches `fill_cover`.

### `isolines`: line generation and segmentation

The evaluation shader bends each line with a sinusoidal vertical offset and colors phases based on the first two outer levels. The image checks isoline count, segment count, domain coordinates, and spacing under direct and indirect draws.

### `no_patches`: incomplete input produces no primitives

The draw supplies two vertices while the pipeline requires three or four control points per patch. No complete patch exists, so the expected render target remains at its black clear value.

### `instances`: per-instance input survives tessellation

A per-vertex buffer defines a small patch and a per-instance buffer supplies four translations. One draw uses four instances. The expected image contains four magenta copies at the translated positions.

### `state_switch`: the second draw uses newly bound tessellation state

The first draw uses one primitive mode, spacing mode, domain origin, or tessellation-control output count and is pushed offscreen. The host then binds the second state and draws onscreen. An independent monolithic pipeline renders the same second state into a reference image. Equality proves that stale state from the first draw did not leak into the visible result. Variants repeat the test with pipeline libraries, shader objects, and a geometry stage.

### `tess_factor_barrier_bug`: control-barrier ordering preserves nonzero factors

The Amber case delays selected vertex work, executes `barrier()` in the tessellation control shader, assigns zero outer levels to most patches, and assigns one to patches in the final wave. The surviving patches form a green image. A failure means valid patches were discarded or failed to rasterize under this synchronized factor pattern.

## Shader Analysis

The representative walkthrough uses a fill-overlap case because its evaluation shader converts domain overlap into a colored image mismatch. State switching and the Amber synchronization regression use different mechanisms; the runtime and failure sections cover them separately.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.misc_draw.fill_overlap_quads_equal_spacing_draw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `fill_overlap` | Colors concentric quad bands so incorrect triangle overlap changes pixels. |
| `quads`, `equal_spacing` | Uses a four-control-point rectangular domain with equally divided segments. |
| `draw` | Submits one patch through `vkCmdDraw`; the indirect variant uses the same shader. |

#### Purpose

This evaluation shader checks that generated triangles cover the quad without overlap. It maps domain coordinates to clip space and assigns a deterministic color band from those coordinates and the uploaded inner levels.

#### Structural Design

| Phase | Operation | Observable role |
|-------|-----------|-----------------|
| Position | Bilinearly interpolate four control points using `gl_TessCoord.xy`. | Places every generated vertex in the rectangular patch. |
| Band index | Scale distance from each center axis by `inner0` and `inner1`. | Associates tessellation bands with an integer phase. |
| Color | Map phase modulo three to red, green, or blue. | Turns overlap or coordinate errors into image differences. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

layout(quads, equal_spacing) in;

/// Binding 0 supplies the rounded inner and outer tessellation levels used by the control and evaluation stages.
layout(set = 0, binding = 0, std430) readonly restrict buffer TessLevels {
    float inner0;
    float inner1;
    float outer0;
    float outer1;
    float outer2;
    float outer3;
} sb_levels;

/// The four control-point positions define the rectangular patch in clip space.
layout(location = 0) in highp vec2 in_te_position[];
/// The fragment shader writes this phase color into the render target.
layout(location = 0) out highp vec4 in_f_color;

void main (void)
{
    highp vec2 corner0 = in_te_position[0];
    highp vec2 corner1 = in_te_position[1];
    highp vec2 corner2 = in_te_position[2];
    highp vec2 corner3 = in_te_position[3];
    highp vec2 pos = (1.0-gl_TessCoord.x)*(1.0-gl_TessCoord.y)*corner0
                   + (    gl_TessCoord.x)*(1.0-gl_TessCoord.y)*corner1
                   + (1.0-gl_TessCoord.x)*(    gl_TessCoord.y)*corner2
                   + (    gl_TessCoord.x)*(    gl_TessCoord.y)*corner3;
    gl_Position = vec4(pos, 0.0, 1.0);
    /// Adjacent tessellation bands receive alternating colors so overlap changes the reference image.
    highp int phaseX = int(round((0.5 - abs(gl_TessCoord.x-0.5)) * sb_levels.inner0));
    highp int phaseY = int(round((0.5 - abs(gl_TessCoord.y-0.5)) * sb_levels.inner1));
    highp int phase = min(phaseX, phaseY) % 3;
    in_f_color = phase == 0 ? vec4(1.0, 0.0, 0.0, 1.0)
               : phase == 1 ? vec4(0.0, 1.0, 0.0, 1.0)
               :              vec4(0.0, 0.0, 1.0, 1.0);
}
```

#### Additional Info

- The control shader writes the same SSBO values into `gl_TessLevelInner` and `gl_TessLevelOuter`, so band calculations and fixed-function tessellation use one uploaded level set.
- The fragment shader passes `in_f_color` to the `R8G8B8A8_UNORM` attachment without blending.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Primitive domain | Triangle cases use barycentric interpolation and a concentric-triangle phase; quad cases use bilinear interpolation and X/Y phases. | [generator branches](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L518-L546) |
| Spacing | Changes the evaluation-shader layout qualifier and the rounded levels uploaded by the host. | [layout generation](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L503-L512) |
| Draw form | Does not change shader text; only the host draw command differs. | [draw selection](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L325-L330) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tese`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 137
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %in_te_position %gl_TessCoord %_ %in_f_color
               OpExecutionMode %main Quads
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCcw
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %corner0 "corner0"
               OpName %in_te_position "in_te_position"
               OpName %corner1 "corner1"
               OpName %corner2 "corner2"
               OpName %corner3 "corner3"
               OpName %pos "pos"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %phaseX "phaseX"
               OpName %TessLevels "TessLevels"
               OpMemberName %TessLevels 0 "inner0"
               OpMemberName %TessLevels 1 "inner1"
               OpMemberName %TessLevels 2 "outer0"
               OpMemberName %TessLevels 3 "outer1"
               OpMemberName %TessLevels 4 "outer2"
               OpMemberName %TessLevels 5 "outer3"
               OpName %sb_levels "sb_levels"
               OpName %phaseY "phaseY"
               OpName %phase "phase"
               OpName %in_f_color "in_f_color"
               OpDecorate %in_te_position Location 0
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %TessLevels BufferBlock
               OpMemberDecorate %TessLevels 0 Restrict
               OpMemberDecorate %TessLevels 0 NonWritable
               OpMemberDecorate %TessLevels 0 Offset 0
               OpMemberDecorate %TessLevels 1 Restrict
               OpMemberDecorate %TessLevels 1 NonWritable
               OpMemberDecorate %TessLevels 1 Offset 4
               OpMemberDecorate %TessLevels 2 Restrict
               OpMemberDecorate %TessLevels 2 NonWritable
               OpMemberDecorate %TessLevels 2 Offset 8
               OpMemberDecorate %TessLevels 3 Restrict
               OpMemberDecorate %TessLevels 3 NonWritable
               OpMemberDecorate %TessLevels 3 Offset 12
               OpMemberDecorate %TessLevels 4 Restrict
               OpMemberDecorate %TessLevels 4 NonWritable
               OpMemberDecorate %TessLevels 4 Offset 16
               OpMemberDecorate %TessLevels 5 Restrict
               OpMemberDecorate %TessLevels 5 NonWritable
               OpMemberDecorate %TessLevels 5 Offset 20
               OpDecorate %sb_levels Restrict
               OpDecorate %sb_levels NonWritable
               OpDecorate %sb_levels Binding 0
               OpDecorate %sb_levels DescriptorSet 0
               OpDecorate %in_f_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
       %uint = OpTypeInt 32 0
    %uint_32 = OpConstant %uint 32
%_arr_v2float_uint_32 = OpTypeArray %v2float %uint_32
%_ptr_Input__arr_v2float_uint_32 = OpTypePointer Input %_arr_v2float_uint_32
%in_te_position = OpVariable %_ptr_Input__arr_v2float_uint_32 Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v2float = OpTypePointer Input %v2float
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
    %float_1 = OpConstant %float 1
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Function_int = OpTypePointer Function %int
  %float_0_5 = OpConstant %float 0.5
 %TessLevels = OpTypeStruct %float %float %float %float %float %float
%_ptr_Uniform_TessLevels = OpTypePointer Uniform %TessLevels
  %sb_levels = OpVariable %_ptr_Uniform_TessLevels Uniform
%_ptr_Uniform_float = OpTypePointer Uniform %float
 %in_f_color = OpVariable %_ptr_Output_v4float Output
       %bool = OpTypeBool
%_ptr_Function_v4float = OpTypePointer Function %v4float
        %127 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
        %131 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %132 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
     %v4bool = OpTypeVector %bool 4
       %main = OpFunction %void None %3
          %5 = OpLabel
    %corner0 = OpVariable %_ptr_Function_v2float Function
    %corner1 = OpVariable %_ptr_Function_v2float Function
    %corner2 = OpVariable %_ptr_Function_v2float Function
    %corner3 = OpVariable %_ptr_Function_v2float Function
        %pos = OpVariable %_ptr_Function_v2float Function
     %phaseX = OpVariable %_ptr_Function_int Function
     %phaseY = OpVariable %_ptr_Function_int Function
      %phase = OpVariable %_ptr_Function_int Function
        %124 = OpVariable %_ptr_Function_v4float Function
         %18 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_0
         %19 = OpLoad %v2float %18
               OpStore %corner0 %19
         %22 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_1
         %23 = OpLoad %v2float %22
               OpStore %corner1 %23
         %26 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_2
         %27 = OpLoad %v2float %26
               OpStore %corner2 %27
         %30 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_3
         %31 = OpLoad %v2float %30
               OpStore %corner3 %31
         %39 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %40 = OpLoad %float %39
         %41 = OpFSub %float %float_1 %40
         %43 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %44 = OpLoad %float %43
         %45 = OpFSub %float %float_1 %44
         %46 = OpFMul %float %41 %45
         %47 = OpLoad %v2float %corner0
         %48 = OpVectorTimesScalar %v2float %47 %46
         %49 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %50 = OpLoad %float %49
         %51 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %52 = OpLoad %float %51
         %53 = OpFSub %float %float_1 %52
         %54 = OpFMul %float %50 %53
         %55 = OpLoad %v2float %corner1
         %56 = OpVectorTimesScalar %v2float %55 %54
         %57 = OpFAdd %v2float %48 %56
         %58 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %59 = OpLoad %float %58
         %60 = OpFSub %float %float_1 %59
         %61 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %62 = OpLoad %float %61
         %63 = OpFMul %float %60 %62
         %64 = OpLoad %v2float %corner2
         %65 = OpVectorTimesScalar %v2float %64 %63
         %66 = OpFAdd %v2float %57 %65
         %67 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %68 = OpLoad %float %67
         %69 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %70 = OpLoad %float %69
         %71 = OpFMul %float %68 %70
         %72 = OpLoad %v2float %corner3
         %73 = OpVectorTimesScalar %v2float %72 %71
         %74 = OpFAdd %v2float %66 %73
               OpStore %pos %74
         %79 = OpLoad %v2float %pos
         %81 = OpCompositeExtract %float %79 0
         %82 = OpCompositeExtract %float %79 1
         %83 = OpCompositeConstruct %v4float %81 %82 %float_0 %float_1
         %85 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %85 %83
         %89 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %90 = OpLoad %float %89
         %91 = OpFSub %float %90 %float_0_5
         %92 = OpExtInst %float %1 FAbs %91
         %93 = OpFSub %float %float_0_5 %92
         %98 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_0
         %99 = OpLoad %float %98
        %100 = OpFMul %float %93 %99
        %101 = OpExtInst %float %1 Round %100
        %102 = OpConvertFToS %int %101
               OpStore %phaseX %102
        %104 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
        %105 = OpLoad %float %104
        %106 = OpFSub %float %105 %float_0_5
        %107 = OpExtInst %float %1 FAbs %106
        %108 = OpFSub %float %float_0_5 %107
        %109 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_1
        %110 = OpLoad %float %109
        %111 = OpFMul %float %108 %110
        %112 = OpExtInst %float %1 Round %111
        %113 = OpConvertFToS %int %112
               OpStore %phaseY %113
        %115 = OpLoad %int %phaseX
        %116 = OpLoad %int %phaseY
        %117 = OpExtInst %int %1 SMin %115 %116
        %118 = OpSMod %int %117 %int_3
               OpStore %phase %118
        %120 = OpLoad %int %phase
        %122 = OpIEqual %bool %120 %int_0
               OpSelectionMerge %126 None
               OpBranchConditional %122 %125 %128
        %125 = OpLabel
               OpStore %124 %127
               OpBranch %126
        %128 = OpLabel
        %129 = OpLoad %int %phase
        %130 = OpIEqual %bool %129 %int_1
        %134 = OpCompositeConstruct %v4bool %130 %130 %130 %130
        %135 = OpSelect %v4float %134 %131 %132
               OpStore %124 %135
               OpBranch %126
        %126 = OpLabel
        %136 = OpLoad %v4float %124
               OpStore %in_f_color %136
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Fill and isoline cases:** The host creates a 256 by 256 `R8G8B8A8_UNORM` attachment, patch vertices, a tessellation-level SSBO, an indirect-command buffer, and a readback buffer. It loops over three level sets, records either `vkCmdDraw` or `vkCmdDrawIndirect`, copies the image, and compares it with the corresponding PNG at threshold `0.002`. All three images must pass.
- **Instanced and no-patch cases:** Two vertex bindings contain patch-local and per-instance positions. The instanced draw uses four instances; the no-patch draw supplies two vertices. The host copies the image and compares it at threshold `0.05` with a software-rendered four-patch reference or the untouched clear image.
- **State-switch cases:** The host renders a 128 by 128 reference image directly with the second state. The result command buffer draws the first state offscreen, binds the second pipeline or tessellation shader objects, and draws onscreen. RGB channels must match within `0.005`, with exact alpha.
- **Barrier regression:** Amber draws `524288` quad-patch instances. The tessellator discards most patches because they get zero outer factors; retained patches must cover the framebuffer with RGBA `(128, 255, 128, 255)`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fill_cover` | Incomplete triangle or quad domain coverage, incorrect tessellation coordinates, or a direct/indirect draw mismatch. |
| `fill_overlap` | Overlapping generated triangles, incorrect band coordinates, or a direct/indirect draw mismatch. |
| `isolines` | Incorrect isoline count, segmentation, coordinate generation, spacing behavior, or direct/indirect draw handling. |
| `no_patches` | An incomplete patch incorrectly reaches tessellation or rasterization. |
| `instances` | Per-instance input or instance count is applied incorrectly before tessellation. |
| `state_switch` | The visible draw uses stale or incorrect tessellation state after the first draw. |
| `tess_factor_barrier_bug` | Tessellation-control synchronization or zero/nonzero tessellation-factor handling discards patches that should render. |

### Cause Analysis

#### Domain generation or draw submission error

**Possible failure symptoms:** `fill_cover` shows dark gaps, `fill_overlap` has wrong color bands, or only the direct or indirect leaf disagrees with its PNG reference. `isolines` shows missing, misplaced, or wrongly colored segments.

**Possible implementation causes:** The tessellator may produce coordinates or segment placement inconsistent with the selected primitive and spacing execution modes. The draw path may consume a wrong vertex count or indirect command. The specification requires complete, non-overlapping triangle and quad coverage and defines how isoline outer levels determine lines and segments.

#### Incomplete-patch handling error

**Possible failure symptoms:** A `no_patches` image contains magenta pixels instead of remaining black.

**Possible implementation causes:** Input assembly or tessellation launch handling may treat two vertices as a complete three- or four-control-point patch. The source proves that the command submits two vertices while the pipeline's patch control point count remains three or four.

#### Per-instance input error

**Possible failure symptoms:** An `instances` image misses one of the four patches, places a patch incorrectly, or differs in color from the software reference.

**Possible implementation causes:** The implementation may advance the instance-rate binding incorrectly, use a wrong instance count, or propagate translated positions incorrectly through tessellation.

#### Tessellation-state transition error

**Possible failure symptoms:** The state-switch result differs from the independent second-state reference. The mismatch can appear in topology, line pattern, culling orientation, or patch shape depending on the changed axis.

**Possible implementation causes:** Pipeline or shader-object binding may leave the first draw's primitive mode, spacing, output count, or domain origin active for the visible draw. For domain origin, the specification states that the setting changes domain orientation and winding interpretation; the test adjusts front-face state for that relation.

#### Tessellation-control synchronization or factor classification error

**Possible failure symptoms:** The Amber framebuffer contains pixels other than `(128, 255, 128, 255)`, indicating that expected nonzero-factor patches did not cover the target.

**Possible implementation causes:** Tessellation-control execution may fail to respect the workgroup barrier before classifying patches from outer factors, or it may classify a synchronized nonzero factor as zero and discard the patch. The fixture targets this regression and does not establish a broader cause beyond the synchronization and factor-classification path.

## Case Pruning

### Requirement-based pruning

- Every C++ case requires `tessellationShader`.
- State-switch geometry variants also require `geometryShader`.
- A lower-left domain origin requires `VK_KHR_maintenance2` through the state-switch support check.
- Fast-linked-library and shader-object variants run only when their pipeline construction requirements are available.
- Isoline support uses the category's isoline support check, including relevant portability-subset restrictions.
- The Amber regression requires `tessellationShader` and `vertexPipelineStoresAndAtomics`; Vulkan SC omits it at compile time.

### Design-based pruning

- Fill-cover and fill-overlap use triangles and quads. Isolines use a separate generator because their primitive and level meanings differ.
- State-switch generation excludes isolines and skips equal before/after pairs. Only one state axis changes in each base case.
- Instanced tests fix tessellation levels to one and use only `triangles` and `quads`, which isolates complete-patch instancing from denser subdivision behavior.
- Direct and indirect suffixes do not apply to instancing, state switching, or the Amber regression because those groups test different command patterns.

## Key Takeaways

- `misc_draw` is one test family with seven behavioral groups, not one uniform parameter sweep. Each group has its own failure signal.
- Coverage and overlap cases compare implementation-independent images even though tessellation's detailed primitive order may vary.
- State-switch cases isolate stale state by comparing the visible second draw with an independently rendered second-state reference.
- Incomplete-patch, instancing, and barrier cases target launch and synchronization behavior that PNG-only fill tests do not cover. See `## Failure Meaning` for diagnoses.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Common fill/isoline runtime | [`runTest()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L138-L361) | Creates resources, executes three level sets, and performs PNG comparisons. |
| Fill and isoline shader generation | [`initCommonPrograms()` through `initProgramsIsolinesCase()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L363-L594) | Generates shaders used by coverage, overlap, and isoline leaves. |
| State-switch implementation | [`TessStateSwitchCase` and `TessStateSwitchInstance`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L601-L1100) | Defines support gates, paired shaders, state binding, reference rendering, and comparison. |
| Instancing and no-patch implementation | [`TessInstancedDrawTestCase` and `TessInstancedDrawTestInstance`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1109-L1481) | Defines complete-patch instancing, incomplete-patch submission, and software-reference comparison. |
| Test registration | [`createMiscDrawTests()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1859-L2084) | Generates all C++ leaves and registers the Amber case. |
| Barrier regression fixture | [`tess_factor_barrier_bug.amber`](../../../data/vulkan/amber/tessellation/tess_factor_barrier_bug.amber#L1-L132) | Defines synchronization, factor writes, draw size, resources, and expected pixels. |
| Current mustpass evidence | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L237-L343) | Lists all 107 current `dEQP-VK.tessellation.misc_draw.*` leaves. |
| Vulkan tessellation semantics | [`tessellation.adoc`](../../../../vulkan-docs/src/chapters/tessellation.adoc#L73-L220) | Defines primitive modes, domain coordinates, patch discard, and spacing. |
