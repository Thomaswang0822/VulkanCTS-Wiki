## Overview

**Core question:** Does adding identity geometry or tessellation stages leave the rendered primitive output unchanged?

- This page covers the five executable leaves under `tessellation.geometry_interaction.passthrough`, implemented by [`vktTessellationGeometryPassthroughTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L1-L785).
- Each case renders two images from the same input through different pipeline stage arrangements. One arrangement contains a passthrough stage or stage pair; the other omits it.
- Three leaves compare tessellated output with and without an identity geometry shader. Two leaves compare geometry-shader output with and without identity tessellation stages.
- The test passes when the two images match within fixed color and position tolerances. A mismatch means the supposedly equivalent stage arrangements produced different rasterized output.
- The Vulkan port is derived from the GLES31 `functional.tessellation_geometry_interaction.render.passthrough` coverage; the executable leaves and their setup are defined by the Vulkan source cited above.

## Background Knowledge

For the shared concepts tessellation pipeline stages and geometry-stage interaction, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Tessellation turns patches into primitives.** A tessellation control shader writes patch data and tessellation levels, the fixed-function tessellator creates points, lines, or triangles in parameter space, and a tessellation evaluation shader computes their positions and attributes. If the pipeline omits both tessellation shaders, incoming primitives continue without tessellation. See [Tessellation](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L32).
- **A geometry shader consumes and emits complete primitives.** Each invocation receives all vertices of one input primitive in an array, then emits zero or more output primitives. An identity geometry shader must emit an equivalent primitive: the same vertices, positions, attributes, and coverage, even when its declared output topology (for example, `triangle_strip`) differs from the input topology (`triangles`). See [Geometry Shading](../../../../vulkan-docs/src/chapters/geometry.adoc#L6-L28).
- **Differential image comparison checks equivalence.** The test uses one pipeline result as the reference for the other. This proves that the two arrangements agree within the comparator tolerance, but a mismatch alone does not identify which arrangement is wrong.

## Registration Hierarchy

The five direct leaves match the Vulkan default mustpass entries in [`tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L20-L24).

```text
tessellation.geometry_interaction.passthrough
├── passthrough_tessellation_geometry_shade_isolines_no_change
├── passthrough_tessellation_geometry_shade_triangles_no_change
├── tessellate_isolines_passthrough_geometry_no_change
├── tessellate_quads_passthrough_geometry_no_change
└── tessellate_triangles_passthrough_geometry_no_change
```

## Parameter Dimensions and Observed Values

[`createGeometryPassthroughTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L766-L781) generates the leaves from two behavioral groups and their supported primitive types.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Behavioral group | `tessellate_*_passthrough_geometry_no_change`, `passthrough_tessellation_geometry_shade_*_no_change` | Selects whether the comparison inserts an identity geometry shader after active tessellation or inserts identity tessellation stages before active geometry shading. | [Case factories](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L745-L762) |
| Primitive type | `triangles`, `quads`, `isolines` for geometry passthrough; `triangles`, `isolines` for tessellation passthrough | Selects patch size, tessellation domain, geometry input/output primitive declarations, and the generated position/color operation. | [Shader generation](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L93-L132), [registration](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L772-L779) |
| Compared stage arrangements | tessellation plus geometry versus tessellation only; geometry plus tessellation versus geometry only | Defines the two pipelines rendered by one executable test case. | [`PipelineDescription`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L424-L454), [`createInstance()` implementations](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L743) |
| Tessellation levels | `14.0` for geometry-passthrough leaves; `1.0` fixed in the TCS for tessellation-passthrough leaves | Dense tessellation stresses geometry passthrough across many generated primitives. Unit levels make the tessellation stages reconstruct the primitive expected by the geometry-only comparison pipeline. | [Geometry-passthrough parameters](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L705), [tessellation-passthrough TCS](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L324-L345) |

## Behavior Parameters

The primary behavioral axis is the **behavioral group encoded by the test case leaf prefix**. It changes which optional stage arrangement must act as an identity transformation.

### `tessellate_*_passthrough_geometry_no_change`: identity geometry after tessellation

Both draws run the same tessellation control and evaluation logic. The first pipeline adds a geometry shader that copies each generated primitive's positions and colors and emits its vertices in order; the second sends the evaluation output toward fragment shading without a geometry stage. The group covers triangle, quad, and isoline tessellation domains with level `14.0`.

### `passthrough_tessellation_geometry_shade_*_no_change`: identity tessellation before geometry shading

Both draws run the same geometry operation, but its input comes from different producers. The first pipeline inserts tessellation control and evaluation stages with levels fixed to `1.0`; the second connects vertex output straight to a geometry shader variant with the matching input name. The group covers triangles and isolines because those primitive types have direct non-tessellated counterparts accepted by the generated geometry operation.

## Shader Analysis

One walkthrough is enough to expose the central identity operation. The selected triangle geometry-passthrough leaf uses dense tessellation before the geometry stage, so omitted, reordered, or duplicated emissions can affect many primitives.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.geometry_interaction.passthrough.tessellate_triangles_passthrough_geometry_no_change
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `tessellate_*_passthrough_geometry_no_change` | Compares active tessellation followed by an identity geometry shader against the same tessellation with no geometry stage. |
| `triangles` | Gives the geometry shader `triangles` input and `triangle_strip` output with a three-vertex budget. |
| tessellation level `14.0` | Produces many tessellated triangles before the identity geometry operation. |

#### Purpose

The geometry shader must reproduce every tessellated triangle without changing its positions or color attributes. The comparison pipeline omits this shader, so both arrangements should rasterize equivalent images.

#### Structural Design

| Geometry input | Per-vertex operation | Geometry output |
|----------------|----------------------|-----------------|
| One triangle in `gl_in[0..2]` and `v_evaluated_color[0..2]` | Copy each indexed position and color, then call `EmitVertex()` | One three-vertex triangle strip representing the same triangle |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require

/// One invocation receives one triangle produced by the tessellator.
layout(triangles) in;
/// Three emitted vertices reproduce that triangle as a triangle strip.
layout(triangle_strip, max_vertices=3) out;

layout(location = 0) in  highp vec4 v_evaluated_color[];
layout(location = 0) out highp vec4 v_fragment_color;

void main (void)
{
    /// Preserve input order, position, color, and emission count.
    for (int ndx = 0; ndx < gl_in.length(); ++ndx)
    {
        gl_Position = gl_in[ndx].gl_Position;
        v_fragment_color = v_evaluated_color[ndx];
        EmitVertex();
    }
}
```

#### Additional Info

- The tessellation evaluation shader writes the same computed position in both compared pipelines. Only its color output identifier changes from `v_evaluated_color` to `v_fragment_color` to connect to the next active stage.
- The generated geometry shader does not call `EndPrimitive()`. A single invocation emits exactly one strip and then returns.
- The source uses the default CTS shader target, SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Primitive type | Quads use triangle geometry input after tessellation and the same three-vertex identity loop. Isolines use line input, line-strip output, and a two-vertex budget. | [Geometry shader generator](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L211-L234) |
| Behavioral group | Tessellation-passthrough leaves use a different, non-identity geometry operation. They compare whether that operation receives equivalent data from vertex shading or unit-level tessellation. | [`generateGeometryShader()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L266-L318) |
| Tessellation level | Geometry-passthrough leaves keep this shader unchanged and vary the preceding tessellator domain. Tessellation-passthrough leaves do not use this shader. | [`createInstance()` implementations](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L743) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 46
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_in %v_fragment_color %v_evaluated_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpName %main "main"
               OpName %ndx "ndx"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpName %v_fragment_color "v_fragment_color"
               OpName %v_evaluated_color "v_evaluated_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpDecorate %v_fragment_color Location 0
               OpDecorate %v_evaluated_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
%v_fragment_color = OpVariable %_ptr_Output_v4float Output
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Input__arr_v4float_uint_3 = OpTypePointer Input %_arr_v4float_uint_3
%v_evaluated_color = OpVariable %_ptr_Input__arr_v4float_uint_3 Input
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %ndx = OpVariable %_ptr_Function_int Function
               OpStore %ndx %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %ndx
         %18 = OpSLessThan %bool %15 %int_3
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %30 = OpLoad %int %ndx
         %32 = OpAccessChain %_ptr_Input_v4float %gl_in %30 %int_0
         %33 = OpLoad %v4float %32
         %35 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %35 %33
         %40 = OpLoad %int %ndx
         %41 = OpAccessChain %_ptr_Input_v4float %v_evaluated_color %40
         %42 = OpLoad %v4float %41
               OpStore %v_fragment_color %42
               OpEmitVertex
               OpBranch %13
         %13 = OpLabel
         %43 = OpLoad %int %ndx
         %45 = OpIAdd %int %43 %int_1
               OpStore %ndx %45
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host allocates one vertex buffer, one tessellation-level storage buffer, a descriptor set, one 256 by 256 `VK_FORMAT_R8G8B8A8_UNORM` color attachment, and two host-visible readback buffers. It uploads the selected vertices and, for geometry-passthrough leaves, six tessellation levels set to `14.0`.
- For each of the two [`PipelineDescription`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L424-L454) entries, the host builds a graphics pipeline with the common vertex and fragment shaders, conditionally adds tessellation and geometry stages, clears the attachment to black, draws once, and copies the image into that pipeline's readback buffer.
- Both pipelines enable additive color blending with source-alpha weighting (`srcAlpha * source + destination`). Duplicate or overlapping primitive contributions can therefore change pixel values even when their outlines coincide.
- The host waits after each submission, invalidates both readback allocations, and runs [`tcu::intThresholdPositionDeviationCompare()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L648-L667). The color threshold is `(8, 8, 8, 255)`, the position deviation is `(1, 1, 0)`, and out-of-bounds search positions are ignored.
- A match returns `pass("OK")`. Any mismatch returns `fail("Image comparison failed")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `tessellate_*_passthrough_geometry_no_change` | The geometry stage changes positions, colors, primitive assembly, emission count, or rasterized overlap relative to the no-geometry pipeline. |
| `passthrough_tessellation_geometry_shade_*_no_change` | The identity tessellation stages change control-point transport, tessellator output, evaluated positions or colors, or the primitive stream received by geometry shading. |

A failure in either group can also come from shared pipeline setup, blending, image transitions, image-to-buffer copy, host-memory visibility, or differential image comparison.

### Cause Analysis

#### Geometry-stage preservation

**Possible failure symptoms:** A geometry-passthrough leaf produces pixels outside the allowed color or one-pixel positional tolerance. The difference may appear as shifted edges, changed interpolation, missing coverage, or brighter overlap from duplicate emission.

**Possible implementation causes:** Geometry shader input assembly, interface transport, `Position` output, output-strip construction, or `EmitVertex` handling may fail to preserve the primitive supplied by tessellation. The geometry shader contract requires the invocation to receive the incoming primitive vertices and form its output from emitted vertices, as described in [`geometry.adoc`](../../../../vulkan-docs/src/chapters/geometry.adoc#L6-L28).

#### Tessellation-stage preservation

**Possible failure symptoms:** A tessellation-passthrough leaf differs from the geometry-only rendering in shape, endpoint or vertex position, interpolated color, primitive count, or overlap intensity.

**Possible implementation causes:** Control-point values may cross the vertex-to-TCS or TCS-to-TES interface incorrectly; unit tessellation levels may generate an unexpected primitive stream; evaluation coordinates may map to wrong positions or colors; or the geometry stage may receive a primitive that differs from the direct vertex-stage input. The expected tessellation sequence and disabled-tessellator behavior are defined in [`tessellation.adoc`](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L32).

#### Shared rendering and readback

**Possible failure symptoms:** Several primitive types or both behavioral groups show broad corruption, stale pixels, uniform differences, or comparison input unrelated to the expected geometry.

**Possible implementation causes:** Shared pipeline state, additive blending, attachment transitions, image-to-buffer copies, allocation invalidation, or comparator inputs may be wrong. Because the test compares two generated images, the oracle cannot assign a mismatch to one pipeline without examining the logged images and lower-level execution.

## Case Pruning

### Requirement-based pruning

- Every leaf requires both `tessellationShader` and `geometryShader` features through [`requireFeatures()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L153-L162).
- On non-VulkanSC builds exposing `VK_KHR_portability_subset`, isoline leaves require `tessellationIsolines`; [`checkSupportPrimitive()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L410-L428) rejects the case when that feature is absent. VulkanSC builds compile out this portability-subset check.

### Design-based pruning

- The geometry-passthrough group covers all three tessellation domains because tessellation remains active in both compared pipelines.
- The tessellation-passthrough group covers triangles and isolines, which map to triangle-list and line-list input when tessellation is absent. The source does not generate a quad version, and [`generateGeometryShader()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L266-L318) implements only triangle and isoline operations for this group.
- The test fixes tessellation levels and input vertices per behavioral group. It compares stage equivalence rather than enumerating spacing modes, winding modes, level ranges, or arbitrary geometry programs.

## Key Takeaways

- The five leaves use paired renderings to test identity behavior at the tessellation-to-geometry boundary.
- Geometry-passthrough leaves keep tessellation fixed and remove only the identity geometry stage from the comparison pipeline.
- Tessellation-passthrough leaves keep the geometry operation fixed and remove the unit-level tessellation stages from the comparison pipeline.
- **Additive color blending** with source-alpha weighting helps turn missing or duplicate primitive emission into image differences.
- Interpret a failure by behavioral group, then consider the shared render and readback path described in `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category attachment | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Attaches `passthrough` below `tessellation.geometry_interaction`. |
| Common vertex and fragment shaders | [`addVertexAndFragmentShaders()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L58-L91) | Defines common position and color behavior for both pipeline arrangements. |
| Geometry-passthrough program generation | [`IdentityGeometryShaderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L164-L235) | Generates the level-buffer TCS, nonlinear TES variants, and identity geometry shader. |
| Tessellation-passthrough program generation | [`IdentityTessellationShaderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L320-L387) | Generates unit-level identity tessellation and geometry-input variants. |
| Shared execution and image oracle | [`PassthroughTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L465-L668) | Creates resources, renders both pipelines, copies images, and decides pass or fail. |
| Pipeline-pair parameters | [`createInstance()` implementations](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L743) | Defines vertices, levels, stage presence, shader names, and test messages. |
| Leaf construction and registration | [`createGeometryPassthroughTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L745-L781) | Names and registers all five leaves. |
| Vulkan default mustpass | [`tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L20-L24) | Confirms all five Vulkan paths. |
| Tessellation stage semantics | [`tessellation.adoc`](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L32) | Defines active and disabled tessellation behavior. |
| Geometry stage semantics | [`geometry.adoc`](../../../../vulkan-docs/src/chapters/geometry.adoc#L6-L28) | Defines geometry input primitives and emitted output. |
