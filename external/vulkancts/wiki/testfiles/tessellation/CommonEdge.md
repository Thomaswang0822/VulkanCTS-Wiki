## Overview

**Core question:** Do adjacent tessellated patches generate and evaluate their shared edges at matching positions, without leaving black cracks in the rendered grid?

- `vktTessellationCommonEdgeTests.cpp` implements the `tessellation.common_edge` test family and its 12 direct test-case leaves.
- Each leaf combines `triangles` or `quads`, one of the three tessellation spacing modes, and basic or `precise` arithmetic behavior.
- The test draws a `4 x 4` patch grid over a black attachment. The tessellation evaluation shader magnifies small position differences into a `0.04` diagonal offset, making mismatched common edges easier to see.
- The host copies the image to memory and fails if it finds a black pixel in the central 70 percent rectangle.

## Background Knowledge

- A tessellator subdivides each patch independently. Two adjacent patches meet without a gap only when both sides subdivide the shared edge consistently and evaluate corresponding edge coordinates to identical clip-space positions. For fractional spacing, Vulkan requires the implementation-dependent placement of the two extra segments to match for edges with identical tessellation levels. See [`tessellation-tessellator-spacing`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing).
- GLSL `precise` arithmetic becomes SPIR-V `NoContraction` decorations on the operations that feed the qualified result. The Vulkan SPIR-V environment states that `NoContraction` prevents those operations from being rearranged. See [`spirvenv-op-prec`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#spirvenv-op-prec).

## Registration Hierarchy

```text
tessellation.common_edge
├── quads_equal_spacing
├── quads_equal_spacing_precise
├── quads_fractional_even_spacing
├── quads_fractional_even_spacing_precise
├── quads_fractional_odd_spacing
├── quads_fractional_odd_spacing_precise
├── triangles_equal_spacing
├── triangles_equal_spacing_precise
├── triangles_fractional_even_spacing
├── triangles_fractional_even_spacing_precise
├── triangles_fractional_odd_spacing
└── triangles_fractional_odd_spacing_precise
```

The family has no intermediate nodes. Each child is a direct executable test-case leaf. The default mustpass list contains the same 12 paths ([mustpass entries](../../../mustpass/main/vk-default/tessellation.txt#L1-L12)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Primitive type | `triangles`, `quads` | Selects three-control-point or four-control-point patches, the host index pattern, the outer-level mapping, and the evaluation interpolation formula. | [`createCommonEdgeTests()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L500-L515), [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L131-L222) |
| Spacing mode | `equal_spacing`, `fractional_odd_spacing`, `fractional_even_spacing` | Selects how the tessellator rounds levels and places generated edge coordinates. The test gives both sides of a shared geometric edge the same endpoint-derived level. | [`SpacingMode`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L173-L180), [`getSpacingModeShaderName()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L299-L310) |
| Case type | basic, `precise` | Basic leaves omit the `_precise` suffix and arrange shared vertices at matching patch-local indices. Precise leaves alter local index ordering and qualify the arithmetic that must remain consistent. This is the primary behavioral axis. | [`CaseType`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L60-L67), [`getCaseName()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L484-L490) |

The host fixes both inner levels at `5.0`. It assigns each of the 25 grid vertices a tessellation parameter from `0.0` through `1.0`; the control shader applies `1.0 + 59.0 * average(endpoint parameters)` to each edge. Because no generated edge has both endpoints at the parameter extremes, the outer levels actually exercised range from approximately `2.22917` (`1.0 + 59.0 / 48.0`) through `58.77083` (`1.0 + 59.0 * 47.0 / 48.0`) ([grid data](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L263-L283), [outer-level expressions](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L150-L162)).

## Behavior Parameters

The primary behavioral axis is **case type**. Primitive type and spacing mode broaden the same common-edge check across different patch and subdivision rules.

### `basic`: matching patch-local control-point indices

Basic cases order each patch so a shared grid vertex occupies the same local control-point index in the adjacent patches that use it. The evaluation shader may use its ordinary interpolation expression because corresponding edge calculations follow the same expression structure. These leaves establish the common-edge behavior without relying on `precise`.

### `precise`: different local indices with protected arithmetic

Precise cases deliberately change patch-local index ordering. The triangle path rotates the second triangle's indices; the quad path reverses alternating patches ([index generation](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L286-L320)). The generated shaders require `GL_EXT_gpu_shader5`, declare `precise gl_TessLevelOuter` and `precise gl_Position`, and split quad interpolation into four terms before summation. Corresponding geometric edge positions must remain equal even when neighboring patches reach them through different local operands and expression paths.

## Shader Analysis

The test generates four stages. One precise quad tessellation evaluation shader captures the central position calculation, spacing selection, `precise` behavior, and mismatch amplifier. The vertex and fragment stages only transport values; the tessellation control stage supplies the endpoint-derived edge levels summarized below. This walkthrough follows the exact `initPrograms()` branch. The shader-analyzer/shader-disassembler CCVDO workflow compiled, validated, and disassembled the reconstructed shader.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.common_edge.quads_fractional_even_spacing_precise
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `quads` | Uses four control points and bilinear evaluation over the quad domain. |
| `fractional_even_spacing` | Rounds each outer tessellation level to an even segment count and uses the fractional-spacing edge rule. |
| `precise` | Reorders alternating patches and protects the arithmetic that feeds outer levels and `gl_Position`. |

#### Purpose

This shader evaluates each generated quad-domain coordinate into clip space. It converts any odd parity in the computed position's floating-point bits into a visible diagonal offset, so neighboring patches that compute a shared edge differently can expose black pixels.

#### Structural Design

| Phase | Operation | Why it matters |
|-------|-----------|----------------|
| Interpolate | Compute four weighted control-point terms and add them into `pos`. | Different local index orderings still represent the same geometric patch edge. |
| Color | Derive a non-black color from `gl_TessCoord`. | Rendered patch coverage replaces the black clear color. |
| Amplify | Count set bits in `floatBitsToUint(pos)` and add `0.04` when parity is odd. | A position-bit difference can move one side of a common edge enough to expose a crack. |
| Emit | Store the final `pos` in `gl_Position`. | `precise gl_Position` propagates no-contraction requirements to the position arithmetic. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require
#extension GL_EXT_gpu_shader5 : require

/// The representative leaf uses quad-domain fractional-even tessellation.
layout(quads, fractional_even_spacing) in;

/// Location 0 carries the four host-supplied patch positions through the control stage.
layout(location = 0) in highp vec2 in_te_position[];

/// The fragment stage copies this generated non-black color to the attachment.
layout(location = 0) out mediump vec4 in_f_color;

/// Protect arithmetic that contributes to the final clip-space position from contraction or reassociation.
precise gl_Position;

void main (void)
{
    /// Keep the four bilinear terms separate before summation for the precise quad path.
    highp vec2 a = (1.0-gl_TessCoord.x)*(1.0-gl_TessCoord.y)*in_te_position[0];
    highp vec2 b = (    gl_TessCoord.x)*(1.0-gl_TessCoord.y)*in_te_position[1];
    highp vec2 c = (1.0-gl_TessCoord.x)*(    gl_TessCoord.y)*in_te_position[2];
    highp vec2 d = (    gl_TessCoord.x)*(    gl_TessCoord.y)*in_te_position[3];
    highp vec2 pos = a+b+c+d;

    highp float f = sqrt(1.0 - 2.0 * max(abs(gl_TessCoord.x - 0.5), abs(gl_TessCoord.y - 0.5)))*0.5 + 0.5;
    in_f_color = vec4(0.1, gl_TessCoord.xy*f, 1.0);

    // Offset the position slightly, based on the parity of the bits in the float representation.
    // This is done to detect possible small differences in edge vertex positions between patches.
    uvec2 bits = floatBitsToUint(pos);
    uint numBits = 0u;
    for (uint i = 0u; i < 32u; i++)
        numBits += ((bits[0] >> i) & 1u) + ((bits[1] >> i) & 1u);
    pos += float(numBits&1u)*0.04;

    gl_Position = vec4(pos, 0.0, 1.0);
}
```

#### Additional Info

- The tessellation control shader copies each position and sets both inner levels to `5.0`. It computes each outer level from the average tessellation parameter at that edge's endpoints and declares `precise gl_TessLevelOuter` for this leaf.
- The vertex shader only forwards the two input attributes. The fragment shader copies `in_f_color` to location 0. Neither stage changes across the 12 leaves.
- No explicit `vk::ShaderBuildOptions` overrides the source collection target, so this walkthrough uses the baseline SPIR-V 1.0 target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Primitive type | `triangles` changes the control patch size to 3, uses three outer levels, evaluates barycentric `gl_TessCoord`, and emits a triangle-derived color. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L131-L222) |
| Spacing mode | Changes `fractional_even_spacing` in the evaluation layout to `equal_spacing` or `fractional_odd_spacing`. | [`getSpacingModeShaderName()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L299-L310) |
| Case type | Basic removes `GL_EXT_gpu_shader5`, both `precise` declarations, and the separate `a`, `b`, `c`, `d` quad terms. The parity amplifier remains present. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L131-L222) |

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
; Bound: 152
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_TessCoord %in_te_position %in_f_color %_
               OpExecutionMode %main Quads
               OpExecutionMode %main SpacingFractionalEven
               OpExecutionMode %main VertexOrderCcw
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_gpu_shader5"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %a "a"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %in_te_position "in_te_position"
               OpName %b "b"
               OpName %c "c"
               OpName %d "d"
               OpName %pos "pos"
               OpName %f "f"
               OpName %in_f_color "in_f_color"
               OpName %bits "bits"
               OpName %numBits "numBits"
               OpName %i "i"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %19 NoContraction
               OpDecorate %23 NoContraction
               OpDecorate %24 NoContraction
               OpDecorate %in_te_position Location 0
               OpDecorate %34 NoContraction
               OpDecorate %40 NoContraction
               OpDecorate %41 NoContraction
               OpDecorate %45 NoContraction
               OpDecorate %49 NoContraction
               OpDecorate %52 NoContraction
               OpDecorate %56 NoContraction
               OpDecorate %62 NoContraction
               OpDecorate %66 NoContraction
               OpDecorate %70 NoContraction
               OpDecorate %72 NoContraction
               OpDecorate %74 NoContraction
               OpDecorate %in_f_color RelaxedPrecision
               OpDecorate %in_f_color Location 0
               OpDecorate %130 NoContraction
               OpDecorate %132 NoContraction
               OpDecorate %134 NoContraction
               OpDecorate %139 NoContraction
               OpDecorate %142 NoContraction
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
    %float_1 = OpConstant %float 1
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
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
%_ptr_Function_float = OpTypePointer Function %float
    %float_2 = OpConstant %float 2
  %float_0_5 = OpConstant %float 0.5
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
 %in_f_color = OpVariable %_ptr_Output_v4float Output
%float_0_100000001 = OpConstant %float 0.100000001
     %v2uint = OpTypeVector %uint 2
%_ptr_Function_v2uint = OpTypePointer Function %v2uint
%_ptr_Function_uint = OpTypePointer Function %uint
       %bool = OpTypeBool
%float_0_0399999991 = OpConstant %float 0.0399999991
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
    %float_0 = OpConstant %float 0
       %main = OpFunction %void None %3
          %5 = OpLabel
          %a = OpVariable %_ptr_Function_v2float Function
          %b = OpVariable %_ptr_Function_v2float Function
          %c = OpVariable %_ptr_Function_v2float Function
          %d = OpVariable %_ptr_Function_v2float Function
        %pos = OpVariable %_ptr_Function_v2float Function
          %f = OpVariable %_ptr_Function_float Function
       %bits = OpVariable %_ptr_Function_v2uint Function
    %numBits = OpVariable %_ptr_Function_uint Function
          %i = OpVariable %_ptr_Function_uint Function
         %17 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %18 = OpLoad %float %17
         %19 = OpFSub %float %float_1 %18
         %21 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %22 = OpLoad %float %21
         %23 = OpFSub %float %float_1 %22
         %24 = OpFMul %float %19 %23
         %32 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_0
         %33 = OpLoad %v2float %32
         %34 = OpVectorTimesScalar %v2float %33 %24
               OpStore %a %34
         %36 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %37 = OpLoad %float %36
         %38 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %39 = OpLoad %float %38
         %40 = OpFSub %float %float_1 %39
         %41 = OpFMul %float %37 %40
         %43 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_1
         %44 = OpLoad %v2float %43
         %45 = OpVectorTimesScalar %v2float %44 %41
               OpStore %b %45
         %47 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %48 = OpLoad %float %47
         %49 = OpFSub %float %float_1 %48
         %50 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %51 = OpLoad %float %50
         %52 = OpFMul %float %49 %51
         %54 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_2
         %55 = OpLoad %v2float %54
         %56 = OpVectorTimesScalar %v2float %55 %52
               OpStore %c %56
         %58 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %59 = OpLoad %float %58
         %60 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %61 = OpLoad %float %60
         %62 = OpFMul %float %59 %61
         %64 = OpAccessChain %_ptr_Input_v2float %in_te_position %int_3
         %65 = OpLoad %v2float %64
         %66 = OpVectorTimesScalar %v2float %65 %62
               OpStore %d %66
         %68 = OpLoad %v2float %a
         %69 = OpLoad %v2float %b
         %70 = OpFAdd %v2float %68 %69
         %71 = OpLoad %v2float %c
         %72 = OpFAdd %v2float %70 %71
         %73 = OpLoad %v2float %d
         %74 = OpFAdd %v2float %72 %73
               OpStore %pos %74
         %78 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %79 = OpLoad %float %78
         %81 = OpFSub %float %79 %float_0_5
         %82 = OpExtInst %float %1 FAbs %81
         %83 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %84 = OpLoad %float %83
         %85 = OpFSub %float %84 %float_0_5
         %86 = OpExtInst %float %1 FAbs %85
         %87 = OpExtInst %float %1 FMax %82 %86
         %88 = OpFMul %float %float_2 %87
         %89 = OpFSub %float %float_1 %88
         %90 = OpExtInst %float %1 Sqrt %89
         %91 = OpFMul %float %90 %float_0_5
         %92 = OpFAdd %float %91 %float_0_5
               OpStore %f %92
         %97 = OpLoad %v3float %gl_TessCoord
         %98 = OpVectorShuffle %v2float %97 %97 0 1
         %99 = OpLoad %float %f
        %100 = OpVectorTimesScalar %v2float %98 %99
        %101 = OpCompositeExtract %float %100 0
        %102 = OpCompositeExtract %float %100 1
        %103 = OpCompositeConstruct %v4float %float_0_100000001 %101 %102 %float_1
               OpStore %in_f_color %103
        %107 = OpLoad %v2float %pos
        %108 = OpBitcast %v2uint %107
               OpStore %bits %108
               OpStore %numBits %uint_0
               OpStore %i %uint_0
               OpBranch %112
        %112 = OpLabel
               OpLoopMerge %114 %115 None
               OpBranch %116
        %116 = OpLabel
        %117 = OpLoad %uint %i
        %119 = OpULessThan %bool %117 %uint_32
               OpBranchConditional %119 %113 %114
        %113 = OpLabel
        %120 = OpAccessChain %_ptr_Function_uint %bits %uint_0
        %121 = OpLoad %uint %120
        %122 = OpLoad %uint %i
        %123 = OpShiftRightLogical %uint %121 %122
        %124 = OpBitwiseAnd %uint %123 %uint_1
        %125 = OpAccessChain %_ptr_Function_uint %bits %uint_1
        %126 = OpLoad %uint %125
        %127 = OpLoad %uint %i
        %128 = OpShiftRightLogical %uint %126 %127
        %129 = OpBitwiseAnd %uint %128 %uint_1
        %130 = OpIAdd %uint %124 %129
        %131 = OpLoad %uint %numBits
        %132 = OpIAdd %uint %131 %130
               OpStore %numBits %132
               OpBranch %115
        %115 = OpLabel
        %133 = OpLoad %uint %i
        %134 = OpIAdd %uint %133 %int_1
               OpStore %i %134
               OpBranch %112
        %114 = OpLabel
        %135 = OpLoad %uint %numBits
        %136 = OpBitwiseAnd %uint %135 %uint_1
        %137 = OpConvertUToF %float %136
        %139 = OpFMul %float %137 %float_0_0399999991
        %140 = OpLoad %v2float %pos
        %141 = OpCompositeConstruct %v2float %139 %139
        %142 = OpFAdd %v2float %140 %141
               OpStore %pos %142
        %146 = OpLoad %v2float %pos
        %148 = OpCompositeExtract %float %146 0
        %149 = OpCompositeExtract %float %146 1
        %150 = OpCompositeConstruct %v4float %148 %149 %float_0 %float_1
        %151 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %151 %150
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [host] `test()` requires `FEATURE_TESSELLATION_SHADER` before creating any resources.
- [host] It builds a `5 x 5` position grid that defines `4 x 4` cells. Triangle leaves split each cell into two patches for 32 patches and 96 indices; quad leaves use one patch per cell for 16 patches and 64 indices.
- [host] One host-visible buffer stores two vertex streams and the `uint16_t` index stream. The host also creates a `256 x 256` `VK_FORMAT_R8G8B8A8_UNORM` color image and a host-visible transfer-destination buffer.
- [host] The graphics pipeline uses patch-list input with 3 or 4 control points and the generated vertex, tessellation control, tessellation evaluation, and fragment modules.
- [host] The command buffer transitions the color image, clears it to black, binds both vertex streams plus the index stream, and calls `vkCmdDrawIndexed()` once.
- [device] The control shader computes edge levels. The fixed-function tessellator generates domain coordinates, and the evaluation shader calculates, amplifies, and emits positions. Covered fragments write the generated non-black color.
- [host] The command buffer copies the rendered image to the color buffer. After submission, wait, and memory invalidation, `verifyResult()` scans x and y from 15 percent through 85 percent of the image dimensions.
- [host] The case fails at the first pixel whose red, green, and blue channels all equal zero. It passes when the scanned central rectangle contains no such pixel ([runtime and readback](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L243-L480)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Adjacent patches generated different subdivisions or evaluated a shared edge inconsistently even though shared vertices use matching patch-local indices; rasterization, color-attachment, copyback, or image-readback behavior may also leave an unexpected black pixel. |
| `precise` | The implementation failed to preserve the `precise`/`NoContraction` arithmetic needed when neighboring patches use different patch-local control-point indices; the common tessellation or rendering/readback causes from `basic` also apply. |

### Cause Analysis

#### Common-edge subdivision or position mismatch

**Possible failure symptoms:** The verifier reports one or more black pixels inside the central scan rectangle. Failures limited to one spacing mode can follow that mode's segment rounding and placement rules; failures limited to triangles or quads can follow the corresponding edge-level mapping or evaluation formula.

**Possible implementation causes:** The tessellator may derive different segment coordinates for equal edge levels, or the evaluation path may compute different clip-space positions for corresponding edge invocations. Fractional spacing permits implementation-dependent placement of the two extra segments, but Vulkan requires identical placement for edges with identical level values.

#### `precise` arithmetic preservation

**Possible failure symptoms:** Basic leaves pass while one or more `_precise` leaves expose black cracks, especially where adjacent patches use different local control-point ordering.

**Possible implementation causes:** The shader compiler or execution path may contract or rearrange an operation that contributes to `gl_TessLevelOuter` or `gl_Position` despite the generated `precise` qualifiers and SPIR-V `NoContraction` decorations. Such a change can make mathematically equivalent neighboring edge expressions round differently.

#### Rendering or readback path

**Possible failure symptoms:** Black pixels may appear across several primitive, spacing, and case-type combinations rather than following a tessellation-specific boundary. Corrupt or stale copied image data can produce the same host-visible result.

**Possible implementation causes:** Color attachment writes, image layout transitions, image-to-buffer copy, host memory invalidation, or rasterization coverage may fail to make the colored grid visible to the verifier. The source does not establish a narrower implementation location without investigating the failed image and command execution.

## Case Pruning

### Requirement-based pruning

- Every leaf requires the `tessellationShader` feature through `FEATURE_TESSELLATION_SHADER`. A device without it reports the case as unsupported before rendering.
- The family does not register isolines. Its design needs adjacent area patches whose shared edges can expose cracks in a filled image; it covers the triangle and quad patch modes used for that check.

### Design-based pruning

- The generator registers the full `2 primitive types x 3 spacing modes x 2 case types` matrix. It does not prune any combination within that matrix.
- Inner levels remain fixed at `5.0`; outer levels vary across the grid. This keeps the check focused on common outer edges rather than making inner-level selection another registered dimension.
- The test checks exact black versus non-black coverage in a cropped region. It does not compare the generated colors against a reference image because color only helps identify patch position and orientation in logs.

## Key Takeaways

- Each shared edge receives the same endpoint-derived tessellation level from both adjacent patches, across all three spacing modes.
- Basic leaves use matching patch-local vertex indices. Precise leaves change local ordering and rely on protected arithmetic to preserve matching edge positions.
- The evaluation shader's bit-parity offset amplifies some position differences into visible geometry displacement; the host then detects cracks as black pixels.
- A black pixel can originate in tessellation or position evaluation, while broad failures can also involve rasterization, attachment writes, copyback, or readback. See `## Failure Meaning` for the evidence-based mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseType` and `CaseDefinition` | [`vktTessellationCommonEdgeTests.cpp#L60-L74`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L60-L74) | Defines primitive, spacing, and basic/precise parameters. |
| `verifyResult()` | [`vktTessellationCommonEdgeTests.cpp#L76-L105`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L76-L105) | Defines the central crop and exact black-pixel failure rule. |
| `initPrograms()` | [`vktTessellationCommonEdgeTests.cpp#L107-L241`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L107-L241) | Generates all four stages, edge levels, interpolation, qualifiers, colors, and the parity amplifier. |
| Grid and index generation | [`vktTessellationCommonEdgeTests.cpp#L257-L328`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L257-L328) | Creates adjacent patches and the case-type-dependent local ordering. |
| Resource and pipeline setup | [`vktTessellationCommonEdgeTests.cpp#L330-L403`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L330-L403) | Defines the combined input buffer, render target, readback buffer, and pipeline. |
| Draw, copy, and result | [`vktTessellationCommonEdgeTests.cpp#L405-L480`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L405-L480) | Records the indexed draw, image copy, host readback, and final status. |
| `createCommonEdgeTests()` | [`vktTessellationCommonEdgeTests.cpp#L494-L518`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L494-L518) | Registers the 12-leaf matrix. |
| Primitive and spacing names | [`vktTessellationUtil.hpp#L239-L310`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L239-L310) | Maps source enums to exact GLSL and registered-name tokens. |
| Tessellator spacing | [`tessellation.adoc#tessellation-tessellator-spacing`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing) | Specifies equal and fractional edge subdivision behavior. |
| SPIR-V operation precision | [`spirvenv.adoc#spirvenv-op-prec`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#spirvenv-op-prec) | Specifies the effect of `NoContraction` on operation rearrangement. |
| Default mustpass entries | [`tessellation.txt#L1-L12`](../../../mustpass/main/vk-default/tessellation.txt#L1-L12) | Confirms all registered leaf paths. |
