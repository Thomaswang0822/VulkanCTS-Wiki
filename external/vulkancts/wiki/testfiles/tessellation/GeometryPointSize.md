## Overview

**Core question:** Does the final active pre-rasterization stage deliver the expected `gl_PointSize` after direct writes, downstream replacement, or cumulative stage-to-stage updates?

- `vktTessellationGeometryPointSizeTests.cpp` implements the seven direct test case leaves under `tessellation.geometry_interaction.point_size`.
- Each case generates a centered point and selects where the vertex, tessellation, and geometry stages set or add to its size.
- Expected widths are `2`, `4`, or `6` pixels. The host measures the non-black rasterized bounding box and requires an exact square of the expected width.
- The family separates direct stage writes from replacement by a later stage and read-modify-write propagation across stage interfaces.

## Background Knowledge

For the shared concepts tessellation pipeline stages and geometry-stage interaction, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- Vulkan rasterizes a point as a square whose width and height come from the `PointSize` built-in. The geometry shader supplies the rasterized point size when present; otherwise the tessellation evaluation shader supplies it when active, and the vertex shader supplies it when neither later stage is active. See [`primsrast-points`](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-points).
- `shaderTessellationAndGeometryPointSize` permits tessellation control, tessellation evaluation, and geometry shaders to read or write `PointSize`. Without it, those stages cannot access the built-in and points they produce have size `1.0`. See [`features-shaderTessellationAndGeometryPointSize`](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderTessellationAndGeometryPointSize).
- Tessellation evaluation `point_mode` emits points instead of lines or triangles. A `VK_KHR_portability_subset` implementation can report point mode as unsupported through `tessellationPointMode`. See [`tessellation-point-mode`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-point-mode).

## Registration Hierarchy

```text
tessellation.geometry_interaction.point_size
├── evaluation_set
├── geometry_set
├── vertex_set
├── vertex_set_control_pass_eval_add_geometry_add
├── vertex_set_evaluation_set
├── vertex_set_evaluation_set_geometry_set
└── vertex_set_geometry_set
```

The family has no intermediate nodes. All seven children are executable test case leaves, and the default mustpass list contains the same paths ([mustpass entries](../../../mustpass/main/vk-default/tessellation.txt#L25-L31)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Vertex operation | omitted, `vertex_set` | The vertex shader either leaves point size unwritten or initializes it to `2.0`. | [`FlagBits`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L62-L69), [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L172-L189) |
| Tessellation operation | omitted, `evaluation_set`, `control_pass_eval_add` | The tessellation pair is absent, sets `4.0` in evaluation, or copies the input through control and adds `2.0` in evaluation. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L205-L262) |
| Geometry operation | omitted, `geometry_set`, `geometry_add` | The geometry stage is absent, replaces the input with `6.0`, or adds `2.0` to its input. | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L264-L288) |
| Expected rasterized size | `2`, `4`, `6` pixels | The model applies later-stage replacement before earlier values and preserves downstream additions. | [`getExpectedPointSize()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L80-L103) |

The registration chooses seven combinations rather than generating the full Cartesian product:

| Test case leaf | Active point-size operations | Expected size | Behavioral group |
|----------------|------------------------------|---------------|------------------|
| `vertex_set` | vertex sets `2.0` | `2` | `single-stage set` |
| `evaluation_set` | tessellation evaluation sets `4.0` | `4` | `single-stage set` |
| `geometry_set` | geometry sets `6.0` | `6` | `single-stage set` |
| `vertex_set_evaluation_set` | vertex sets `2.0`; evaluation replaces it with `4.0` | `4` | `downstream replacement` |
| `vertex_set_geometry_set` | vertex sets `2.0`; geometry replaces it with `6.0` | `6` | `downstream replacement` |
| `vertex_set_evaluation_set_geometry_set` | vertex sets `2.0`; evaluation sets `4.0`; geometry replaces it with `6.0` | `6` | `downstream replacement` |
| `vertex_set_control_pass_eval_add_geometry_add` | vertex sets `2.0`; tessellation passes then adds `2.0`; geometry adds `2.0` | `6` | `cumulative propagation` |

## Behavior Parameters

The primary behavioral axis is the **point-size operation sequence**. The seven leaves form three groups according to whether the final size comes from one write, replacement by a downstream stage, or values transported and incremented across stages.

### `single-stage set`: one stage supplies the size

`vertex_set`, `evaluation_set`, and `geometry_set` isolate a direct `gl_PointSize` write in each eligible pre-rasterization stage. Their `2`, `4`, and `6` pixel outputs show whether rasterization receives the value from the selected stage without another point-size operation in the pipeline.

### `downstream replacement`: the last writer wins

The three replacement leaves start with a vertex value and add a later fixed write in tessellation evaluation, geometry, or both. The visible size must come from the latest active writer: evaluation replaces `2.0` with `4.0`, while geometry replaces any earlier value with `6.0`. This follows Vulkan's stage selection for rasterized point size rather than accumulating fixed writes ([point-size precedence](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-points)).

### `cumulative propagation`: stages read, pass, and add

`vertex_set_control_pass_eval_add_geometry_add` exercises the full point-size interface chain. Vertex writes `2.0`, tessellation control copies it, tessellation evaluation adds `2.0`, and geometry adds another `2.0`. The final `6 x 6` point depends on both interface transport and read-modify-write behavior; a fixed write in the final stage could not cover those paths.

## Shader Analysis

One walkthrough covers the cumulative case because it includes every nontrivial point-size transfer and arithmetic branch. The fixed-value cases remove stages or replace the `+ 2.0` expressions with direct assignments.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.geometry_interaction.point_size.vertex_set_control_pass_eval_add_geometry_add
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `vertex_set` | Initializes `gl_PointSize` to `2.0`. |
| `control_pass_eval_add` | Copies the vertex value through tessellation control, then adds `2.0` in tessellation evaluation. |
| `geometry_add` | Reads the evaluation output and adds the final `2.0`, producing `6.0`. |

#### Purpose

The selected shaders test whether `gl_PointSize` crosses the vertex-to-control, control-to-evaluation, and evaluation-to-geometry interfaces intact while the later stages update it. The geometry output must reach point rasterization as `6.0`.

#### Structural Design

| Stage | Point-size operation | Position operation | Result passed onward |
|-------|----------------------|--------------------|-----------------------|
| Vertex | Write `2.0`. | Place the input at clip-space center. | Center position and size `2.0`. |
| Tessellation control | Copy `gl_in[0].gl_PointSize` to `gl_out[0]`. | Copy the one control point and set tessellation levels to `3.0`. | One-control-point patch carrying size `2.0`. |
| Tessellation evaluation | Write input size plus `2.0`. | Keep one generated point visible and move the others outside clip space. | One visible point with size `4.0`. |
| Geometry | Write input size plus `2.0`. | Copy the visible input position and emit one point. | Final point with size `6.0`. |

#### Shader Code

##### Vertex Shader

```glsl
#version 310 es

void main (void)
{
    /// Start the cumulative point-size chain at the center of the attachment.
    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
    gl_PointSize = 2.0;
}
```

##### Tessellation Control Shader

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require
#extension GL_EXT_tessellation_point_size : require
layout(vertices = 1) out;

void main (void)
{
    /// Level 3.0 creates several triangle-domain point-mode invocations for the evaluation stage.
    gl_TessLevelOuter[0] = 3.0;
    gl_TessLevelOuter[1] = 3.0;
    gl_TessLevelOuter[2] = 3.0;
    gl_TessLevelInner[0] = 3.0;

    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    // pass as is to eval
    gl_out[gl_InvocationID].gl_PointSize = gl_in[gl_InvocationID].gl_PointSize;
}
```

##### Tessellation Evaluation Shader

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require
#extension GL_EXT_tessellation_point_size : require
layout(triangles, point_mode) in;

void main (void)
{
    // hide all but one vertex
    if (gl_TessCoord.x < 0.99)
        gl_Position = vec4(-2.0, 0.0, 0.0, 1.0);
    else
        gl_Position = gl_in[0].gl_Position;

    // add to point size
    gl_PointSize = gl_in[0].gl_PointSize + 2.0;
}
```

##### Geometry Shader

```glsl
#version 310 es
#extension GL_EXT_geometry_shader : require
#extension GL_EXT_geometry_point_size : require
layout(points) in;
layout(points, max_vertices = 1) out;

void main (void)
{
    /// Preserve the incoming clip-space position for the one emitted point.
    gl_Position  = gl_in[0].gl_Position;
    /// Read the tessellation evaluation output and add the final 2-pixel increment.
    gl_PointSize = gl_in[0].gl_PointSize + 2.0;

    EmitVertex();
}
```

#### Additional Info

- The vertex shader changes only when `vertex_set` is selected. In this case it supplies the value that both later additions consume.
- The tessellation control and evaluation shaders are generated only for `evaluation_set` or `control_pass_eval_add`. The selected add path needs both stages because control transports the per-vertex built-in to evaluation.
- The geometry shader uses direct assignment for `geometry_set`, input plus `2.0` for `geometry_add`, and is absent otherwise. Its output controls the rasterized size whenever geometry is active.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Vertex operation | Omitting `vertex_set` removes only the `gl_PointSize = 2.0` statement. | [`vertex generation`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L174-L189) |
| Tessellation operation | `evaluation_set` removes the control-stage point-size copy and writes `4.0` in evaluation. Omitting tessellation removes both stages. | [`tessellation generation`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L205-L262) |
| Geometry operation | `geometry_set` writes `6.0`; omitting geometry removes the stage. | [`geometry generation`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L264-L288) |

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
; Bound: 32
; Schema: 0
               OpCapability Geometry
               OpCapability GeometryPointSize
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_in
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputPoints
               OpExecutionMode %main OutputVertices 1
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_geometry_point_size"
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %float
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_gl_PerVertex_0_uint_1 = OpTypeArray %gl_PerVertex_0 %uint_1
%_ptr_Input__arr_gl_PerVertex_0_uint_1 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_1
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_1 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
%_ptr_Input_float = OpTypePointer Input %float
    %float_2 = OpConstant %float 2
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %20 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %21 = OpLoad %v4float %20
         %23 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %23 %21
         %26 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_1
         %27 = OpLoad %float %26
         %29 = OpFAdd %float %27 %float_2
         %31 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %31 %29
               OpEmitVertex
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [host] `test()` derives the expected size before resource creation. It unconditionally requires `tessellationShader`, `geometryShader`, and `shaderTessellationAndGeometryPointSize`, then rejects an expected size above `pointSizeRange[1]` ([requirements](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L291-L302)).
- [host] Cases with tessellation also require portability-subset `tessellationPointMode` when `VK_KHR_portability_subset` is active ([portability check](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L452-L462)).
- [host] The test creates a `32 x 32` `VK_FORMAT_R8G8B8A8_UNORM` image for color-attachment and transfer-source use, plus a host-visible transfer-destination buffer. It uses no vertex buffer, descriptors, push constants, or specialization constants.
- [host] The graphics pipeline always contains vertex and fragment stages. It adds the tessellation pair and geometry stage according to the case flags. Tessellation cases use one control point per patch; cases without tessellation use point-list topology ([pipeline setup](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L348-L379), [topology selection](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L201-L208)).
- [host] The command buffer transitions the image, clears it to opaque black, binds the pipeline, and calls `vkCmdDraw()` for one vertex. It then copies the color image to the readback buffer and waits for completion.
- [device] The selected pre-rasterization stages produce one visible center point. The fragment shader writes opaque white for its covered fragments.
- [host] After invalidating the mapped allocation, `verifyImage()` computes the bounding box of every pixel that differs from opaque black. It fails if no such pixel exists, if the box is not square, or if its width is not the exact expected value. It passes without checking point centering or individual color values beyond black versus non-black ([verification and result](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L414-L430)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single-stage set` | The selected vertex, tessellation evaluation, or geometry output did not supply the expected `gl_PointSize` to point rasterization; rendering or readback can produce the same missing or wrong bounding box. |
| `downstream replacement` | A downstream tessellation evaluation or geometry write did not replace an earlier point-size value as required, or the final stage value was not used for rasterization; shared rendering/readback causes also apply. |
| `cumulative propagation` | A point-size value was not copied through tessellation control, read and incremented by tessellation evaluation, or read and incremented by geometry before rasterization; shared rendering/readback causes also apply. |

### Cause Analysis

#### Direct point-size write or final-stage selection

**Possible failure symptoms:** A `single-stage set` leaf reports no point, a non-square point, or a square whose width differs from `2`, `4`, or `6`. A stage-specific pattern can appear if only vertex, tessellation evaluation, or geometry leaves fail.

**Possible implementation causes:** The shader compiler or pre-rasterization execution path may fail to write the selected stage's `PointSize` built-in. The rasterizer may then receive the wrong value. When geometry is active its output supplies point size; without geometry, tessellation evaluation or vertex supplies it according to the active stages ([point-size selection](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-points)).

#### Downstream replacement

**Possible failure symptoms:** A replacement leaf renders at an earlier value, such as `2` instead of `4` or `6`, while the corresponding single-stage leaf may pass.

**Possible implementation causes:** A downstream stage write may not replace the incoming built-in value, or the pipeline may use point size from an earlier stage instead of the last active stage that supplies rasterization. The exact failing combinations distinguish evaluation replacement from geometry replacement, but source-level investigation is needed to locate the defect.

#### Stage-interface propagation and addition

**Possible failure symptoms:** The cumulative leaf produces no point or a width below `6`, while fixed `geometry_set` can still pass. A width of `2` or `4` can indicate that one or both downstream additions did not affect the final value, although the image alone does not prove where the value was lost.

**Possible implementation causes:** `PointSize` may be copied incorrectly across the tessellation control interface, read incorrectly by tessellation evaluation or geometry, or lowered incorrectly for the floating-point additions. The `shaderTessellationAndGeometryPointSize` feature makes these reads and writes available in all three stages ([feature semantics](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderTessellationAndGeometryPointSize)).

#### Point rasterization, attachment, or readback

**Possible failure symptoms:** Several behavioral groups fail with absent, non-square, or implausibly sized non-black regions rather than following one stage-operation pattern.

**Possible implementation causes:** Point coverage generation, color-attachment writes, image layout transitions, image-to-buffer copy, or host memory invalidation may prevent the expected white square from reaching `verifyImage()`. The host's bounding box cannot distinguish these shared paths, so command execution and the logged image need source-level investigation.

## Case Pruning

### Requirement-based pruning

- Every leaf unconditionally requires `tessellationShader`, `geometryShader`, and `shaderTessellationAndGeometryPointSize`, even when its generated pipeline omits tessellation or geometry. Missing features produce an unsupported result before rendering.
- Tessellation leaves also require portability-subset `tessellationPointMode` when the portability extension is active.
- `checkPointSizeRequirements()` rejects a leaf when its expected width exceeds `pointSizeRange[1]`. The largest requested width is `6`; the source notes that point-size granularity is at most `1.0`, so these integer widths need no separate granularity gate ([size check](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L72-L78)).

### Design-based pruning

- The family omits cases that rely on a default `1.0` point size. Its source states that those GLES 3.1 cases are not valid in Vulkan ([ported-case note](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L466-L480)).
- The seven-case selection covers each direct setter, three downstream replacement arrangements, and one full cumulative propagation path. It does not register redundant combinations in which a later fixed `geometry_set` would hide an earlier add operation from image verification.
- The tessellation shader fixes its levels at `3.0` and uses triangle-domain point mode. Primitive type and spacing mode are not registered dimensions because this family checks point-size flow rather than tessellation subdivision variants.

## Key Takeaways

- The three single-stage leaves isolate direct `gl_PointSize` writes from vertex, tessellation evaluation, and geometry stages.
- Replacement leaves check that the last active writer determines the visible point size; the cumulative leaf checks interface transport and additions that a final fixed write would hide.
- The verifier uses the exact non-black bounding-box width. It checks point size and square shape, but not center position or an independent reference color image.
- A stage-specific failure can narrow the point-size path involved. Broad failures can also come from point rasterization, attachment writes, copyback, or readback; see `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `FlagBits` and `getExpectedPointSize()` | [`vktTessellationGeometryPointSizeTests.cpp#L62-L103`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L62-L103) | Defines stage operations and the expected last-writer/addition model. |
| `verifyImage()` | [`vktTessellationGeometryPointSizeTests.cpp#L115-L170`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L115-L170) | Defines the exact non-black square and width check. |
| `initPrograms()` | [`vktTessellationGeometryPointSizeTests.cpp#L172-L289`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L172-L289) | Generates all shader stages and point-size branches. |
| Requirements and resources | [`vktTessellationGeometryPointSizeTests.cpp#L291-L379`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L291-L379) | Checks support and builds the image, buffer, and graphics pipeline. |
| Draw, copy, and result | [`vktTessellationGeometryPointSizeTests.cpp#L381-L430`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L381-L430) | Records one draw, copies the attachment, and returns pass or fail. |
| Naming and portability support | [`vktTessellationGeometryPointSizeTests.cpp#L433-L462`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L433-L462) | Builds exact leaf names and gates tessellation point mode. |
| `createGeometryPointSizeTests()` | [`vktTessellationGeometryPointSizeTests.cpp#L466-L489`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L466-L489) | Registers the seven selected flag combinations. |
| `createGeometryInteractionTests()` | [`vktTessellationTests.cpp#L52-L61`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Places the family at `tessellation.geometry_interaction.point_size`. |
| Pipeline topology selection | [`vktTessellationUtil.cpp#L201-L208`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L201-L208) | Selects patch-list topology when tessellation control is active. |
| Shared feature checks | [`vktTessellationUtil.cpp#L802-L824`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L802-L824) | Defines the three feature gates used by this family. |
| Point rasterization | [`primsrast.adoc#primsrast-points`](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-points) | Defines square point coverage and active-stage point-size selection. |
| Tessellation/geometry point-size feature | [`features.adoc#features-shaderTessellationAndGeometryPointSize`](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderTessellationAndGeometryPointSize) | Defines legal `PointSize` access in the later stages. |
| Default mustpass entries | [`tessellation.txt#L25-L31`](../../../mustpass/main/vk-default/tessellation.txt#L25-L31) | Confirms all seven executable paths. |
