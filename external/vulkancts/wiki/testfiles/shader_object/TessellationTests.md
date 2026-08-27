## Overview

**Core question:** Do per-stage tessellation shader objects apply the selected execution modes and render the expected pattern after an optional temporary stage rebind?

- [`vktShaderObjectTessellationTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp) implements the `shader_object.tessellation` test family.
- The test creates direct SPIR-V shader objects for vertex, tessellation control, tessellation evaluation, and fragment stages. It renders one patch into a 32x32 image and compares a 17x17 region against an exact black-and-white mask.
- The 36 registered test cases combine two execution-mode placement variants, nine tessellation behaviors, and an optional `_rebind` sequence.
- A rebind case replaces one tessellation stage with a temporary shader object, restores the selected object before drawing, and checks that the temporary execution modes leave no stale state.

## Background Knowledge

For the shared concepts shader objects, per-stage binding, and tessellation stages, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- `OutputVertices` declares the tessellation control output patch size. The evaluation stage reads that size through the `PatchVertices` built-in, which can differ from the dynamic input patch control-point count.

## Registration Hierarchy

```text
shader_object.tessellation
├── glsl
└── hlsl
```

Each intermediate node contains the same nine base behavior leaves and nine `_rebind` leaves. The source registers 36 executable test cases in total.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Execution-mode placement | `glsl`, `hlsl` | Selects which tessellation stages carry the execution-mode declarations in the direct SPIR-V artifacts: `glsl` places primitive, spacing, orientation, and point mode on evaluation; `hlsl` places spacing, orientation, and point mode on control while declaring the primitive mode on both control and evaluation. The names do not select a runtime source compiler. | [Mode placement branches](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L574-L598), [evaluation mode placement](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L720-L742) |
| Test case behavior | `orientation_ccw`, `orientation_cw`, `spacing_equal`, `spacing_fractional_odd`, `patch_vertices_4`, `patch_vertices_5`, `primitive_quads`, `primitive_triangles`, `point_mode` | Selects the tessellation property that controls the expected rasterized mask. | [Registration matrix](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L942-L970) |
| Binding history | base leaf, `_rebind` leaf | The `_rebind` suffix adds a temporary stage bind followed by restoration of the selected shader before the draw. | [Rebind commands](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L190-L206) |

The primary behavioral axis is the test case behavior before the optional `_rebind` suffix. The placement and binding-history dimensions change how the selected behavior reaches the draw, but they preserve its expected output.

## Behavior Parameters

The primary behavioral axis is `test case behavior before the optional _rebind suffix`. Its values are `orientation_ccw`, `orientation_cw`, `spacing_equal`, `spacing_fractional_odd`, `patch_vertices_4`, `patch_vertices_5`, `primitive_quads`, `primitive_triangles`, and `point_mode`.

### `orientation_ccw`: visible counter-clockwise tessellation

The evaluation-stage modes select counter-clockwise vertex order. Back-face culling remains enabled for this case, so the tessellated triangles produce the visible `basic` line mask.

### `orientation_cw`: culled clockwise tessellation

The evaluation-stage modes select clockwise vertex order while the host keeps back-face culling enabled. The expected 17x17 region stays black, which exposes ignored or misplaced orientation state.

### `spacing_equal`: equal edge subdivision

The tessellator uses `SpacingEqual` with inner and outer levels set to `2.0`. Line polygon mode turns the generated quad-domain edges into the `basic` mask.

### `spacing_fractional_odd`: fractional-odd edge subdivision

The tessellator uses `SpacingFractionalOdd` at the same tessellation levels. Its different edge subdivision pattern produces the dedicated `fractionalOdd` mask.

### `patch_vertices_4`: four control outputs from five inputs

The host sets the dynamic input patch size to five and draws five vertices. The control shader declares `OutputVertices 4`, so the evaluation stage sees four patch vertices and leaves the output position unchanged.

### `patch_vertices_5`: five control outputs and evaluation offset

The host again provides five input control points, but the control stage declares `OutputVertices 5`. The evaluation stage observes `PatchVertices > 4` and adds `0.3` to the output y coordinate. The host checks the expected mask five pixels lower.

### `primitive_quads`: quad parameter domain

The tessellator generates quad-domain coordinates. The evaluation stage performs bilinear interpolation across four control points, which yields the `basic` mask under equal spacing.

### `primitive_triangles`: triangle parameter domain

The tessellator generates triangle-domain coordinates. The same evaluation instructions consume the available coordinate components and control-point positions, producing the dedicated `triangles` mask.

### `point_mode`: tessellator-generated points

`PointMode` changes the tessellator output to points. The host still sets line polygon mode, but the expected output is the sparse `pointMode` mask rather than connected edges.

## Shader Analysis

The test supplies CTS-authored SPIR-V assembly through `spirvAsmSources`; it does not generate GLSL or HLSL source. The walkthrough follows the evaluation stage because its execution modes select the representative spacing behavior and its position calculation determines the rasterized pattern.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.shader_object.tessellation.glsl.spacing_fractional_odd_rebind
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `glsl` | Places `OutputVertices` on the control stage and the quad, fractional-odd spacing, and counter-clockwise modes on the evaluation stage. |
| `spacing_fractional_odd` | Selects `SpacingFractionalOdd` and the dedicated `fractionalOdd` output mask. |
| `_rebind` | Binds a control shader object with opposite mode choices, then restores the selected control object before drawing. |

#### Purpose

This case checks that the selected evaluation execution modes drive fractional-odd quad tessellation after the host disturbs and restores the control-stage binding. The generated lines must match the exact `fractionalOdd` mask.

#### Structural Design

| Stage or operation | Role in the selected case |
|--------------------|---------------------------|
| Tessellation control | Writes all inner and outer levels as `2.0`, copies four control-point positions, and declares `OutputVertices 4`. |
| Fixed-function tessellator | Applies `Quads`, `SpacingFractionalOdd`, and `VertexOrderCcw` to generate tessellation coordinates. |
| Tessellation evaluation | Uses bilinear interpolation for the four patch positions. Its five-vertex offset branch remains inactive because `PatchVertices` is four. |
| Rasterization and fragment shading | Rasterizes the generated edges in line mode and writes white fragments over the black clear color. |

#### Shader Code

##### Tessellation Evaluation Shader

This stage uses CTS-authored direct SPIR-V assembly and does not use GLSL or HLSL source. The authoritative assembly appears under the matching stage heading in `#### SPIR-V`.

#### Additional Info

- The temporary shader object affects the tessellation control stage in this `glsl` case. The host restores the selected control object before dynamic rendering begins, so the draw must use the selected four-output control stage.
- The evaluation algorithm has no descriptor, push-constant, specialization-constant, or user-varying inputs. It reads tessellation built-ins and per-vertex positions.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test case behavior | Changes one or more execution modes, changes `OutputVertices`, or activates `PointMode`; the evaluation body changes only through its `PatchVertices > 4` branch. | [Execution-mode selection](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L436-L485), [evaluation artifact](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L705-L878) |
| Execution-mode placement | `glsl` places spacing and orientation on the evaluation stage; `hlsl` places spacing, orientation, and point mode on the control stage while declaring the primitive mode on both control and evaluation. | [Control and evaluation placement branches](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L574-L598) |
| Binding history | `_rebind` adds opposite-mode control and evaluation artifacts. Runtime code replaces and restores control for `glsl`, or evaluation for `hlsl`. | [Artifact insertion](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L909-L924), [rebind commands](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L190-L206) |

#### SPIR-V

##### Tessellation Evaluation SPIR-V

- Status: generated and validated
- Source: CTS-authored direct SPIR-V from this walkthrough
- Stage: tese
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 87
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_TessCoord %_ %gl_in %gl_PatchVerticesIn
               OpExecutionMode %main Quads
               OpExecutionMode %main SpacingFractionalOdd
               OpExecutionMode %main VertexOrderCcw
               OpSource GLSL 450
               OpName %main "main"
               OpName %u "u"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %v "v"
               OpName %omu "omu"
               OpName %omv "omv"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %gl_PatchVerticesIn "gl_PatchVerticesIn"
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpDecorate %gl_PatchVerticesIn BuiltIn PatchVertices
       %void = OpTypeVoid
         %14 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
    %float_1 = OpConstant %float 1
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
      %int_1 = OpConstant %int 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Input_int = OpTypePointer Input %int
%gl_PatchVerticesIn = OpVariable %_ptr_Input_int Input
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
%float_0_300000012 = OpConstant %float 0.300000012
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %14
         %42 = OpLabel
          %u = OpVariable %_ptr_Function_float Function
          %v = OpVariable %_ptr_Function_float Function
        %omu = OpVariable %_ptr_Function_float Function
        %omv = OpVariable %_ptr_Function_float Function
         %43 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %44 = OpLoad %float %43
               OpStore %u %44
         %45 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %46 = OpLoad %float %45
               OpStore %v %46
         %47 = OpLoad %float %u
         %48 = OpFSub %float %float_1 %47
               OpStore %omu %48
         %49 = OpLoad %float %v
         %50 = OpFSub %float %float_1 %49
               OpStore %omv %50
         %51 = OpLoad %float %omu
         %52 = OpLoad %float %omv
         %53 = OpFMul %float %51 %52
         %54 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %55 = OpLoad %v4float %54
         %56 = OpVectorTimesScalar %v4float %55 %53
         %57 = OpLoad %float %u
         %58 = OpLoad %float %omv
         %59 = OpFMul %float %57 %58
         %60 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %61 = OpLoad %v4float %60
         %62 = OpVectorTimesScalar %v4float %61 %59
         %63 = OpFAdd %v4float %56 %62
         %64 = OpLoad %float %u
         %65 = OpLoad %float %v
         %66 = OpFMul %float %64 %65
         %67 = OpAccessChain %_ptr_Input_v4float %gl_in %int_3 %int_0
         %68 = OpLoad %v4float %67
         %69 = OpVectorTimesScalar %v4float %68 %66
         %70 = OpFAdd %v4float %63 %69
         %71 = OpLoad %float %omu
         %72 = OpLoad %float %v
         %73 = OpFMul %float %71 %72
         %74 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %75 = OpLoad %v4float %74
         %76 = OpVectorTimesScalar %v4float %75 %73
         %77 = OpFAdd %v4float %70 %76
         %78 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %78 %77
         %79 = OpLoad %int %gl_PatchVerticesIn
         %80 = OpSGreaterThan %bool %79 %int_4
               OpSelectionMerge %81 None
               OpBranchConditional %80 %82 %81
         %82 = OpLabel
         %83 = OpAccessChain %_ptr_Output_float %_ %int_0 %uint_1
         %84 = OpLoad %float %83
         %85 = OpFAdd %float %84 %float_0_300000012
         %86 = OpAccessChain %_ptr_Output_float %_ %int_0 %uint_1
               OpStore %86 %85
               OpBranch %81
         %81 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates selected vertex, control, evaluation, and fragment shader objects. A `_rebind` case also creates temporary control and evaluation objects with opposite execution-mode choices.
- It creates a 32x32 `R8G8B8A8_UNORM` color image and a host-visible transfer buffer. The image starts black and receives white fragment output.
- The command buffer binds the four selected graphics stages. A `glsl` rebind case replaces and restores the control stage; an `hlsl` rebind case replaces and restores the evaluation stage. No draw occurs while the temporary object is bound.
- Dynamic state selects patch-list topology and line polygon mode. Orientation cases enable back-face culling. Patch-vertex cases set five dynamic input control points and draw five vertices; other cases draw four.
- After dynamic rendering, a barrier makes color writes available to transfer, and the command buffer copies the image to the host-visible buffer. Submission completes before the host reads the pixels.
- The host checks a 17x17 region at image coordinates `(7..23, 7..23)`. `patch_vertices_5` shifts the checked y coordinate by five pixels.
- `spacing_fractional_odd`, `primitive_triangles`, and `point_mode` use dedicated masks. `orientation_cw` expects black at every checked pixel. All remaining behaviors use the `basic` mask.
- Each set cell must equal `(1,1,1,1)`, and each unset cell must equal `(0,0,0,1)`. The first exact RGBA mismatch fails the test; there is no tolerance.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `orientation_ccw` | Counter-clockwise tessellator winding, front-face interpretation, back-face culling, or execution-mode placement produced the wrong visible edges. |
| `orientation_cw` | Clockwise tessellated triangles were not culled as expected, or the orientation mode was ignored or read from the wrong shader object. |
| `spacing_equal` | Equal-spacing edge subdivision or its shader-object execution mode produced the wrong line pattern. |
| `spacing_fractional_odd` | Fractional-odd edge subdivision or its shader-object execution mode produced the wrong line pattern. |
| `patch_vertices_4` | Dynamic input patch size, four-vertex control output, or evaluation-stage `PatchVertices` handling produced the wrong base pattern. |
| `patch_vertices_5` | Five-control-point input/output handling or the `PatchVertices > 4` y-offset branch failed. |
| `primitive_quads` | Quad-domain tessellation or bilinear evaluation produced the wrong base pattern. |
| `primitive_triangles` | Triangle-domain tessellation, coordinate interpretation, or evaluation of the available control points produced the wrong triangular pattern. |
| `point_mode` | `PointMode` did not convert tessellator output to the expected sparse point pattern. |

Any `_rebind` failure also points to stage-binding persistence: the temporary control object in `glsl` or temporary evaluation object in `hlsl` may have remained active after the selected object was restored. A failure shared by both source types can also come from common drawing, rasterization, image synchronization, copyback, or exact pixel comparison paths.

### Cause Analysis

#### Orientation, front-face interpretation, and culling

**Possible failure symptoms:** `orientation_ccw` produces missing or misplaced white edges, or `orientation_cw` produces any white pixel in the checked region.

**Possible implementation causes:** The implementation may apply `VertexOrderCcw` or `VertexOrderCw` from the wrong stage, misinterpret the generated triangle winding, or mishandle the combination of winding, dynamic front-face state, and back-face culling.

#### Edge-spacing subdivision

**Possible failure symptoms:** `spacing_equal` deviates from the `basic` mask, or `spacing_fractional_odd` deviates from its dedicated mask while other mode cases render correctly.

**Possible implementation causes:** The fixed-function tessellator may subdivide edges with the wrong spacing rule, or shader-object execution-mode state may supply the wrong `SpacingEqual` or `SpacingFractionalOdd` declaration to the draw.

#### Input and output patch vertex counts

**Possible failure symptoms:** `patch_vertices_4` misses the base mask, or `patch_vertices_5` fails to render the same shape at the five-pixel y offset.

**Possible implementation causes:** The implementation may use the dynamic input patch count as the control output count, mishandle `OutputVertices`, report the wrong `PatchVertices` value to evaluation, or mishandle the `PatchVertices > 4` branch.

#### Primitive domain and evaluation coordinates

**Possible failure symptoms:** `primitive_quads` misses the base mask, or `primitive_triangles` fails its triangular mask while spacing and point cases pass.

**Possible implementation causes:** The tessellator may generate coordinates for the wrong primitive domain, or the evaluation stage may receive the wrong `TessCoord` or control-point positions during interpolation.

#### Point mode

**Possible failure symptoms:** `point_mode` produces connected edges, missing points, or extra white pixels instead of the sparse point mask.

**Possible implementation causes:** The implementation may ignore `PointMode`, retain line or triangle primitive generation, or rasterize the tessellator-generated points at incorrect locations.

#### Stage-binding persistence

**Possible failure symptoms:** A base leaf passes while its `_rebind` partner fails or renders a pattern associated with the temporary object's opposite modes.

**Possible implementation causes:** `vkCmdBindShadersEXT` may fail to replace the temporary stage binding with the restored selected shader object. The affected stage differs by placement variant: control for `glsl`, evaluation for `hlsl`.

#### Shared rendering and readback path

**Possible failure symptoms:** Many unrelated behaviors and both placement variants report wrong colors or common spatial corruption.

**Possible implementation causes:** The common dynamic drawing state, tessellation-to-rasterization path, color attachment writes, image barrier, image-to-buffer copy, or host-visible readback may produce bytes that do not match the exact expected colors. Source-level investigation is needed to distinguish these shared paths from a tessellation-mode defect.

## Case Pruning

### Requirement-based pruning

- The case requires `VK_EXT_shader_object`.
- The device must support the `tessellationShader` feature. The test reports the family as unsupported when that feature is absent.

### Design-based pruning

- The generator registers nine focused behavior values rather than a cross product of every primitive, spacing, orientation, output-count, and point-mode combination. Most cases hold the other modes at the quad, equal-spacing, counter-clockwise, four-output baseline.
- Each behavior has one base leaf and one `_rebind` leaf for each placement variant. The rebind suffix changes binding history without changing the expected mask.
- The `patch_vertices_4` and `patch_vertices_5` cases both use five dynamic input control points so that the control stage's `OutputVertices` declaration, rather than the draw's input count, controls the evaluation-stage `PatchVertices` value.

## Key Takeaways

- The nine behavior leaves isolate orientation, spacing, patch output count, primitive domain, and point mode while preserving a small fixed patch and exact masks.
- The `glsl` and `hlsl` intermediate nodes describe execution-mode placement in direct SPIR-V artifacts. They do not invoke GLSL or HLSL compilation at runtime.
- `_rebind` leaves test per-stage binding replacement. The host restores the selected object before the draw, so each base leaf and its `_rebind` partner must render the same mask.
- Exact black-and-white pixel checks turn tessellation-mode, interpolation, culling, and stale-binding errors into distinct visible patterns. See `## Failure Meaning` for the failure mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Runtime resources, binding, draw, and copyback | [ShaderObjectTessellationInstance::iterate](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L87-L258) | Creates shader objects and image resources, performs optional rebind, draws, and copies the result. |
| Expected masks and exact pixel check | [Mask tables and validation loop](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L260-L384) | Defines the observable result for all nine behaviors. |
| Support requirements | [ShaderObjectTessellationCase::checkSupport](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L415-L420) | Requires shader objects and tessellation shader support. |
| Execution-mode selection | [initPrograms mode branches](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L422-L485) | Chooses selected and temporary execution modes. |
| Control shader artifact | [Control SPIR-V construction](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L558-L703) | Writes tessellation levels and copies control points. |
| Evaluation shader artifact | [Evaluation SPIR-V construction](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L705-L878) | Interpolates patch positions and applies the five-vertex offset. |
| Artifact insertion | [Program collection](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L909-L924) | Adds the direct SPIR-V stages and optional rebind artifacts. |
| Registration matrix | [createShaderObjectTessellationTests](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L929-L975) | Registers all 36 leaves. |
| Default mustpass paths | [tessellation.txt](../../../mustpass/main/vk-default/shader-object/tessellation.txt) | Lists the 36 executable paths. |
| Tessellation execution modes | [Tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L109) | Defines tessellation stage flow and shader-object execution-mode ownership. |
| Shader-object binding | [Shader Objects chapter](../../../../vulkan-docs/src/chapters/shaders.adoc#L912-L1050) | Defines per-stage shader-object binding and required dynamic state. |
| Patch vertex built-in | [PatchVertices definition](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4024-L4055) | Defines the input patch vertex count visible to tessellation stages. |
