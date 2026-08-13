## Overview

**Core question:** Does the tessellator discard exactly those patches whose relevant outer tessellation levels are non-positive?

- This page covers the `tessellation.primitive_discard` test family implemented by [`vktTessellationPrimitiveDiscardTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L1-L658).
- The non-`_valid_levels` cases generate a grid of patches whose six supplied tessellation levels choose ordinary positive values, `-0.42`, or `0.0`. `_valid_levels` cases instead repeat positive base values for every choice, so they contain no discarded patches and provide a deterministic count baseline. The primitive mode determines which outer levels are relevant to discard.
- Surviving patches must produce white pixels. Once the ordered input reaches the first discarded patch, the rest of the corresponding image region must remain black.
- A tessellation evaluation shader invocation counter provides a second check that generated coordinates were not lost, subject to defined implementation-dependent exceptions.

## Background Knowledge

- **Patch discard uses only relevant outer levels.** The fixed-function tessellator must discard a patch if a relevant outer tessellation level is less than or equal to zero. Isolines use two outer levels, triangles use three, and quads use four. Non-positive inner levels do not discard a patch; they are clamped. See [Tessellator Patch Discard](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178).
- **Discard suppresses tessellation evaluation.** A discarded patch generates no new primitives, and its tessellation evaluation shader is not executed. The test can therefore observe discard through both absent rasterization and absent counter increments.

## Registration Hierarchy

The source-generated leaves below match the 44 entries in [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L344-L387).

```text
tessellation.primitive_discard
├── isolines_equal_spacing_ccw
├── isolines_equal_spacing_ccw_point_mode
├── isolines_equal_spacing_cw
├── isolines_equal_spacing_cw_point_mode
├── isolines_fractional_even_spacing_ccw
├── isolines_fractional_even_spacing_ccw_point_mode
├── isolines_fractional_even_spacing_cw
├── isolines_fractional_even_spacing_cw_point_mode
├── isolines_fractional_odd_spacing_ccw
├── isolines_fractional_odd_spacing_ccw_point_mode
├── isolines_fractional_odd_spacing_cw
├── isolines_fractional_odd_spacing_cw_point_mode
├── quads_equal_spacing_ccw
├── quads_equal_spacing_ccw_point_mode
├── quads_equal_spacing_cw
├── quads_equal_spacing_cw_point_mode
├── quads_fractional_even_spacing_ccw
├── quads_fractional_even_spacing_ccw_point_mode
├── quads_fractional_even_spacing_cw
├── quads_fractional_even_spacing_cw_point_mode
├── quads_fractional_odd_spacing_ccw
├── quads_fractional_odd_spacing_ccw_point_mode
├── quads_fractional_odd_spacing_ccw_point_mode_valid_levels
├── quads_fractional_odd_spacing_ccw_valid_levels
├── quads_fractional_odd_spacing_cw
├── quads_fractional_odd_spacing_cw_point_mode
├── quads_fractional_odd_spacing_cw_point_mode_valid_levels
├── quads_fractional_odd_spacing_cw_valid_levels
├── triangles_equal_spacing_ccw
├── triangles_equal_spacing_ccw_point_mode
├── triangles_equal_spacing_cw
├── triangles_equal_spacing_cw_point_mode
├── triangles_fractional_even_spacing_ccw
├── triangles_fractional_even_spacing_ccw_point_mode
├── triangles_fractional_even_spacing_cw
├── triangles_fractional_even_spacing_cw_point_mode
├── triangles_fractional_odd_spacing_ccw
├── triangles_fractional_odd_spacing_ccw_point_mode
├── triangles_fractional_odd_spacing_ccw_point_mode_valid_levels
├── triangles_fractional_odd_spacing_ccw_valid_levels
├── triangles_fractional_odd_spacing_cw
├── triangles_fractional_odd_spacing_cw_point_mode
├── triangles_fractional_odd_spacing_cw_point_mode_valid_levels
└── triangles_fractional_odd_spacing_cw_valid_levels
```

## Parameter Dimensions and Observed Values

[`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L626-L655) forms each test case name from five dimensions.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Primitive type | `isolines`, `quads`, `triangles` | Selects the tessellation domain and, most importantly, whether two, four, or three outer levels are relevant to discard. | [`CaseDefinition`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L58-L65), [`numOuterTessellationLevels()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L433-L447) |
| Spacing mode | `equal_spacing`, `fractional_even_spacing`, `fractional_odd_spacing` | Changes how positive or clamped levels produce coordinates. It does not change the non-positive relevant-outer discard predicate. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L316-L347) |
| Winding | `ccw`, `cw` | Changes the generated triangle orientation for triangle and quad domains; it does not change which patches must be discarded. | [`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L631-L648) |
| Point mode | absent, `_point_mode` | Selects point generation and may require the evaluation shader to write `gl_PointSize`. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L304-L348) |
| Level-set variant | default, `_valid_levels` | The default form includes `-0.42` and `0.0` choices. `_valid_levels` repeats positive base levels to provide a deterministic count case for fractional-odd triangles and quads. | [`genAttributes()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L93-L150), [`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L635-L650) |

Each default case enumerates three choices for each of six tessellation-level slots: the slot's base value from `3.0` through `8.0`, `-0.42`, or `0.0`. This gives 729 patches arranged as a 27 by 27 grid. The loop order puts all patches that survive the primitive-specific relevant-outer test before the first discarded patch.

## Behavior Parameters

The primary behavioral axis is **primitive type**. It changes the set of outer levels consumed by the discard rule; the other dimensions exercise the same rule under different tessellation output configurations.

### `isolines`: first two outer levels are relevant

An isoline patch must be discarded if outer level 0 or 1 is non-positive. Outer levels 2 and 3 are supplied by the test but are irrelevant, so making either one non-positive must not suppress the patch. This is the narrowest relevant set and catches implementations that inspect too many values.

### `quads`: all four outer levels are relevant

A quad patch must be discarded when any of outer levels 0 through 3 is non-positive. There are no irrelevant outer slots. The generated combinations therefore check every outer position as a discard trigger while also confirming that non-positive inner levels alone do not discard the patch.

### `triangles`: first three outer levels are relevant

A triangle patch uses outer levels 0 through 2 for discard. Outer level 3 is irrelevant and must not suppress output. This distinguishes triangle handling from both the two-level isoline rule and the four-level quad rule.

## Shader Analysis

One walkthrough is enough because the tessellation control shader that exposes the tested decision inputs has the same structure across all leaves. The chosen quad case makes every written outer level relevant and avoids point-mode-specific evaluation shader variation.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.primitive_discard.quads_equal_spacing_ccw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `quads` | All four `gl_TessLevelOuter` elements participate in the discard decision. |
| `equal_spacing` | Uses the ordinary equal-segment spacing mode after a patch survives. |
| `ccw` | Selects counter-clockwise generated triangle orientation; it does not alter discard. |
| no `_point_mode` | Uses ordinary quad-generated triangles and the evaluation shader variant that does not write `gl_PointSize`. |
| default level set | Enumerates positive, `-0.42`, and `0.0` choices in all six level slots. |

#### Purpose

This tessellation control shader transports each generated level tuple into the built-ins consumed by the fixed-function tessellator. For the selected quad case, a non-positive value in any of the four outer outputs must prevent all later tessellation evaluation and rasterization for that patch.

#### Structural Design

| Input indices | Tessellation-control output | Later role |
|---------------|-----------------------------|------------|
| `0`, `1` | `gl_TessLevelInner[0..1]` | Control interior subdivision but do not trigger patch discard. |
| `2` through `5` | `gl_TessLevelOuter[0..3]` | All four values are relevant to quad patch discard. |
| `6`, `7` | `in_te_positionScale` | Scale a surviving patch into one image-grid cell. |
| `8`, `9` | `in_te_positionOffset` | Offset a surviving patch to that cell. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

layout(vertices = 1) out;

/// Ten scalar attributes arrive through location 0 across the ten input control points of each patch.
/// Indices 0-5 carry two inner and four outer tessellation levels; indices 6-9 carry image placement.
layout(location = 0) in highp float in_tc_attr[];

/// These per-patch values place every surviving patch in its assigned cell of the result image.
layout(location = 0) patch out highp vec2 in_te_positionScale;
layout(location = 1) patch out highp vec2 in_te_positionOffset;

void main (void)
{
    in_te_positionScale  = vec2(in_tc_attr[6], in_tc_attr[7]);
    in_te_positionOffset = vec2(in_tc_attr[8], in_tc_attr[9]);

    /// The tessellator consumes these six values. A non-positive relevant outer value must discard the patch.
    gl_TessLevelInner[0] = in_tc_attr[0];
    gl_TessLevelInner[1] = in_tc_attr[1];

    gl_TessLevelOuter[0] = in_tc_attr[2];
    gl_TessLevelOuter[1] = in_tc_attr[3];
    gl_TessLevelOuter[2] = in_tc_attr[4];
    gl_TessLevelOuter[3] = in_tc_attr[5];
}
```

#### Additional Info

- The pipeline sets ten patch control points. Because the vertex format has one float at location 0, `in_tc_attr[0..9]` receives the ten consecutive floats for one logical test patch.
- The shader source is generated by [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L274-L302). The `#version 310 es` declaration comes from [`glu::getGLSLVersionDeclaration()`](../../../../../framework/opengl/gluShaderUtil.cpp#L45-L53).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Primitive type | Does not alter this control shader; it changes the evaluation shader's domain declaration and how many outer outputs the tessellator treats as relevant. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L304-L347) |
| Spacing and winding | Do not alter this control shader; both appear in the evaluation shader's input layout. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L324-L326) |
| Point mode | Does not alter this control shader; it adds `point_mode` and may select an evaluation shader that writes `gl_PointSize`. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L304-L348) |
| Level-set variant | Changes attribute values supplied to this shader, not its declarations or instructions. | [`genAttributes()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L107-L147) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tesc`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 65
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %in_te_positionScale %in_tc_attr %in_te_positionOffset %gl_TessLevelInner %gl_TessLevelOuter
               OpExecutionMode %main OutputVertices 1
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %in_te_positionScale "in_te_positionScale"
               OpName %in_tc_attr "in_tc_attr"
               OpName %in_te_positionOffset "in_te_positionOffset"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpDecorate %in_te_positionScale Patch
               OpDecorate %in_te_positionScale Location 0
               OpDecorate %in_tc_attr Location 0
               OpDecorate %in_te_positionOffset Patch
               OpDecorate %in_te_positionOffset Location 1
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Output_v2float = OpTypePointer Output %v2float
%in_te_positionScale = OpVariable %_ptr_Output_v2float Output
       %uint = OpTypeInt 32 0
    %uint_32 = OpConstant %uint 32
%_arr_float_uint_32 = OpTypeArray %float %uint_32
%_ptr_Input__arr_float_uint_32 = OpTypePointer Input %_arr_float_uint_32
 %in_tc_attr = OpVariable %_ptr_Input__arr_float_uint_32 Input
        %int = OpTypeInt 32 1
      %int_6 = OpConstant %int 6
%_ptr_Input_float = OpTypePointer Input %float
      %int_7 = OpConstant %int 7
%in_te_positionOffset = OpVariable %_ptr_Output_v2float Output
      %int_8 = OpConstant %int 8
      %int_9 = OpConstant %int 9
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
      %int_0 = OpConstant %int 0
%_ptr_Output_float = OpTypePointer Output %float
      %int_1 = OpConstant %int 1
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_6
         %19 = OpLoad %float %18
         %21 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_7
         %22 = OpLoad %float %21
         %23 = OpCompositeConstruct %v2float %19 %22
               OpStore %in_te_positionScale %23
         %26 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_8
         %27 = OpLoad %float %26
         %29 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_9
         %30 = OpLoad %float %29
         %31 = OpCompositeConstruct %v2float %27 %30
               OpStore %in_te_positionOffset %31
         %37 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_0
         %38 = OpLoad %float %37
         %40 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %40 %38
         %42 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_1
         %43 = OpLoad %float %42
         %44 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_1
               OpStore %44 %43
         %50 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_2
         %51 = OpLoad %float %50
         %52 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %52 %51
         %54 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_3
         %55 = OpLoad %float %54
         %56 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %56 %55
         %58 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_4
         %59 = OpLoad %float %58
         %60 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %60 %59
         %62 = OpAccessChain %_ptr_Input_float %in_tc_attr %int_5
         %63 = OpLoad %float %62
         %64 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_3
               OpStore %64 %63
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`genAttributes()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L93-L150) creates ten floats per patch: two inner levels, four outer levels, a two-component scale, and a two-component offset. The ordering guarantees that all surviving patches precede the first discarded patch in both the vertex buffer and the image grid.
- The host creates a vertex buffer, a zero-initialized four-byte storage buffer for the invocation count, a black-cleared 256 by 256 `VK_FORMAT_R8G8B8A8_UNORM` color image, and a host-visible image readback buffer. Set 0, binding 0 exposes the counter only to the tessellation evaluation stage.
- The graphics pipeline uses ten control points per patch. One draw consumes all generated floats, so every ten vertices form one logical patch.
- For every tessellation evaluation invocation, the shader atomically increments the SSBO and maps `gl_TessCoord.xy` into the assigned image cell. The fragment shader writes opaque white.
- After rendering, the command buffer copies the color image to the readback buffer and inserts a shader-write-to-host-read barrier for the counter. The host waits, invalidates both host-visible allocations, and checks the results.
- [`expectedVertexCount()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L244-L254) computes a point-mode reference count. Fewer observed invocations fail; equal counts pass this check; extra invocations are accepted because duplicate coordinates need not be deduplicated identically.
- The CTS skips the count check for fractional-odd triangle and quad cases that include inner levels at or below one. Its source treats the interior-vertex count as implementation-dependent for this generated variant. Image verification still applies.
- [`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L153-L242) requires at least one white pixel near each surviving patch's cell. From the first discarded patch onward, it requires the remaining grid region to contain only black pixels.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `isolines` | Incorrect use of the two relevant outer levels, or incorrect execution suppression after isoline patch discard. |
| `quads` | Incorrect use of all four outer levels, or incorrect execution suppression after quad patch discard. |
| `triangles` | Incorrect use of the first three outer levels, or incorrect execution suppression after triangle patch discard. |

All three values also depend on correct transport of the generated levels through the vertex and tessellation control stages, correct image placement and readback, and correct visibility of the tessellation evaluation shader's SSBO writes.

### Cause Analysis

#### Incorrect relevant-outer selection

**Possible failure symptoms:** A patch with a non-positive relevant outer level produces white pixels, or a patch with positive relevant outer levels disappears because an inner or irrelevant outer value was non-positive. Isoline and triangle failures can reveal use of too many outer slots; failures in any primitive type can reveal that one of its required slots was ignored.

**Possible implementation causes:** The tessellator's primitive-mode-specific discard predicate may consume the wrong `TessLevelOuter` elements or apply discard to `TessLevelInner`. This conflicts with the relevant-level and inner-level rules in [Tessellator Patch Discard](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178).

#### Evaluation execution after required discard

**Possible failure symptoms:** The trailing region contains a non-black pixel or the evaluation-stage counter includes work from patches that should have generated no coordinates.

**Possible implementation causes:** The fixed-function tessellator may identify a non-positive relevant outer level but fail to suppress primitive generation or tessellation evaluation execution. The specification requires both to be absent for a discarded patch.

#### Level transport or result-observation failure

**Possible failure symptoms:** A surviving cell has no white pixel, the invocation counter is below its checked lower bound, or the image and counter disagree across many patches rather than at one primitive-specific relevant slot.

**Possible implementation causes:** Source inspection shows several shared mechanisms that can produce these symptoms: vertex-to-control-shader attribute transport, writes to the tessellation-level built-ins, evaluation-stage SSBO atomics, rasterization into the assigned cell, image copyback, or synchronization before host reads. Further source-level investigation is needed to distinguish these causes from a failing result alone.

## Case Pruning

### Requirement-based pruning

- Runtime execution requires `tessellationShader` and `vertexPipelineStoresAndAtomics`; unsupported devices report the case as not supported.
- With `VK_KHR_portability_subset`, isoline cases require `tessellationIsolines`, and point-mode cases require `tessellationPointMode`. [`checkSupportCase()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L525-L550) performs these checks.
- Point-mode cases do not require `shaderTessellationAndGeometryPointSize`. When it is available, the pipeline selects the evaluation shader that writes `gl_PointSize`; otherwise it selects the variant that leaves the default point size unchanged.

### Design-based pruning

The registration loop considers a `_valid_levels` variant for every parameter combination, but retains it only for fractional-odd triangles and quads. Only those configurations have implementation-dependent interior-vertex counts when inner levels are at or below one. For other primitive/spacing combinations, the ordinary generated case has well-defined count behavior, so a separate all-positive leaf would be redundant.

## Key Takeaways

- Primitive type is the central axis: isolines, triangles, and quads use two, three, and four relevant outer levels, respectively.
- The input matrix includes non-positive inner and irrelevant outer values. Those values must not be mistaken for discard triggers.
- Image cells provide the primary survive/discard verdict. The evaluation invocation count is a lower-bound sanity check with a defined fractional-odd exception.
- `_valid_levels` leaves exist only where they recover a deterministic count baseline for fractional-odd triangles and quads.
- See `## Failure Meaning` for how primitive-specific and shared failures should be interpreted.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Case parameters and input generation | [`CaseDefinition`, `lessThanOneInnerLevelsDefined()`, and `genAttributes()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L58-L151) | Defines the matrix, low-level choices, and patch ordering. |
| Image checker | [`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L153-L242) | Implements white-survivor and black-discarded-region checks. |
| Invocation reference | [`expectedVertexCount()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L244-L254) | Computes the checked lower bound. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L256-L365) | Generates all four shader stages and the point-size variant. |
| Runtime path | [`test()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L367-L615) | Creates resources, draws, synchronizes, reads back, and returns the verdict. |
| Registration | [`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L619-L655) | Generates the 44 exact test case leaves. |
| Host reference predicate | [`numOuterTessellationLevels()` and `isPatchDiscarded()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L433-L456) | Encodes primitive-specific relevant outer levels. |
| Reference count utilities | [`referencePrimitiveCount()` and `referenceVertexCount()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L786-L800) | Explains the point-mode lower-bound calculation. |
| Feature checks | [`checkSupportCase()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L525-L550), [`requireFeatures()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L802-L824) | Defines portability and core-feature requirements. |
| Specification rule | [Tessellator Patch Discard](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178) | Defines discard, relevant outer levels, and evaluation suppression. |
| Mustpass paths | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L344-L387) | Confirms the Vulkan mustpass inventory for this family. |
