## Overview

**Core question:** Does a two-pipeline tessellation sequence render the expected image when one dynamic patch-control-point value is set before both draws?

- [`vktPipelineDynamicControlPoints.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1) implements the `dynamic_control_points` test family for each supported pipeline construction path.
- Each test case records one `vkCmdSetPatchControlPointsEXT(..., 3)` command, then draws with two tessellation pipelines into separate halves of a color image.
- The three test case leaves vary whether the second pipeline changes tessellation-control output, tessellation-evaluation winding, or both. The copied image is compared with a two-color reference.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Dynamic patch-control-point state.** A tessellation-control invocation consumes an input patch and produces one output control point. The patch's input-control-point count can be supplied by [`vkCmdSetPatchControlPointsEXT`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2588-L2630) for subsequent draws when the pipeline declares `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT`. The command value must be greater than zero and at most `maxTessellationPatchSize`.
- **Dynamic-state precedence.** When `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` is in the pipeline dynamic-state list, the static `VkPipelineTessellationStateCreateInfo::patchControlPoints` value is ignored and the command buffer must set the state before drawing, as specified in [the graphics-pipeline dynamic-state rules](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6141-L6148).
- **Winding and culling.** A tessellation-evaluation shader can declare clockwise or counter-clockwise triangle winding. With front-face culling enabled, changing that declaration can make one draw disappear while the opposite winding remains visible.

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_control_points
├── change_output
├── change_winding
└── change_output_winding
```

[`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) registers this concrete monolithic root. The same three leaves occur in seven Vulkan-default mustpass construction files: `monolithic/monolithic.txt`, `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-linked-spirv.txt`, `shader-object-linked-binary.txt`, `shader-object-unlinked-binary.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`, for 21 entries total.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `change_output`, `change_winding`, `change_output_winding` | Selects the output-count transition, winding transition, or their combination. | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) |
| Pipeline construction path | monolithic, pipeline library, fast linked library, and four shader-object paths represented in Vulkan-default mustpass | Reuses the same leaf configurations through each supported construction form. | mustpass files named above |
| Second tessellation-control output | three or four vertices | Four vertices add a sentinel fourth output point; the second evaluation shader reads it only when `changeOutput` is true. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L193-L234) |
| Evaluation-shader winding | `ccw` or `cw` | Controls the orientation used by rasterization and therefore the culling result. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L176-L191) |
| Cull mode | `VK_CULL_MODE_NONE` or `VK_CULL_MODE_FRONT_BIT` | Leaves that change winding use front-face culling to make the orientation observable in the color target. | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L435-L457) |
| Dynamic patch control points | 3 | The command buffer sets the input patch size once before both draws. | [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L389-L408) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf selects a different transition between the two pipeline draws while preserving the same command-buffer dynamic patch-control-point setting.

### change_output: change tessellation-control output count

The first pipeline emits three output control points and the second emits four. The second evaluation shader reads its fourth control point, which the control shader assigns a sentinel position. Both halves should be magenta because culling is disabled.

### change_winding: change tessellation-evaluation winding

Both pipelines keep three control points, but their evaluation shaders use opposite winding declarations. Front-face culling should remove the first draw and retain the second, producing white on the left and magenta on the right.

### change_output_winding: change output count and winding

This leaf combines the four-output second pipeline with the winding reversal and front-face culling. It checks the transition in which both tessellation output and culling-visible orientation differ between the draws.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.dynamic_control_points.change_output
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `change_output` | Selects the branch where the second tessellation-control shader declares four output control points while the dynamic input patch size remains three. |
| `shader_object_linked_binary` | Exercises the same generated shaders through linked shader objects created from binaries; shader construction does not alter the GLSL for this path. |
| Dynamic patch control points = `3` | Groups the six vertex-shader outputs into two three-point input patches for both draws. |
| Second TCS output vertices = `4` | Adds a fourth invocation that writes a sentinel without reading beyond the three-point input patch. |

#### Purpose

This tessellation-control shader makes the input/output patch-size distinction observable: it consumes a dynamically selected three-point input patch, emits four output control points, and places a magenta sentinel in the additional point for the second tessellation-evaluation shader to read.

#### Structural Design

| Invocation | Input access | Output action | Downstream role |
|---|---|---|---|
| `0`, `1`, `2` | Read `gl_in[gl_InvocationID].gl_Position` | Forward the corresponding input position to `gl_out` | Supplies the three positions used for tessellation interpolation. |
| `3` | None | Write `(1, 0, 1, 1)` to `gl_out[3].gl_Position` | Supplies the magenta value read by the second evaluation shader. |
| All four invocations | None | Write inner and outer tessellation levels of `2` | Requests the same triangle subdivision levels for the output patch. |

#### Shader Code

```glsl
#version 450

/// Four tessellation-control invocations emit four output control points even
/// though the dynamically selected input patch size remains three.
layout(vertices = 4) out;

void main (void)
{
    /// Every invocation writes the same tessellation levels; the generated
    /// triangles use two subdivisions on each outer edge and the inner level.
    gl_TessLevelInner[0] = 2;
    gl_TessLevelOuter[0] = 2.0;
    gl_TessLevelOuter[1] = 2.0;
    gl_TessLevelOuter[2] = 2.0;

    /// Invocations 0..2 forward the three dynamically grouped input points.
    /// Invocation 3 never indexes gl_in[3]; it emits the sentinel consumed by
    /// the second tessellation-evaluation shader as its magenta color.
    if (gl_InvocationID < 3) {
        gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    } else {
        gl_out[gl_InvocationID].gl_Position = vec4(1.0, 0.0, 1.0, 1.0);
    }
}
```

#### Additional Info

- [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L193-L233) emits this four-output `tesc2` shader only when `changeOutput` is true; its paired `tese2` shader reads `gl_in[3].gl_Position.xyz` as the fragment color.
- [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L332-L404) uses the three-output `tesc` shader for the first pipeline, selects `tesc2` for the second pipeline in this case, sets the dynamic input patch size to three once, and draws both pipelines.
- The reconstructed shader preserves the generated statements and branch behavior while normalizing generator-dependent whitespace for readability. No explicit `vk::ShaderBuildOptions` are supplied, so the CTS baseline target is SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test case leaf | `change_output` and `change_output_winding` generate this four-output TCS and make `tese2` read the fourth point; `change_winding` retains the three-output TCS and changes only evaluation-stage winding. | [`createDynamicControlPointTests()` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L128-L235) |
| Evaluation winding | The first and second evaluation shaders independently select `cw` or `ccw`; this does not change the TCS shown here. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L128-L233) |
| Pipeline construction path | All construction paths use the same generated shader text; the path changes pipeline or shader-object construction rather than this shader's declarations or control flow. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L128-L235) |

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
; Bound: 59
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %gl_TessLevelInner %gl_TessLevelOuter %gl_InvocationID %gl_out %gl_in
               OpExecutionMode %main OutputVertices 4
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %gl_out "gl_out"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpMemberName %gl_PerVertex_0 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 3 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_2 = OpConstant %float 2
%_ptr_Output_float = OpTypePointer Output %float
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
    %v4float = OpTypeVector %float 4
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_PerVertex_uint_4 = OpTypeArray %gl_PerVertex %uint_4
%_ptr_Output__arr_gl_PerVertex_uint_4 = OpTypePointer Output %_arr_gl_PerVertex_uint_4
     %gl_out = OpVariable %_ptr_Output__arr_gl_PerVertex_uint_4 Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
         %57 = OpConstantComposite %v4float %float_1 %float_0 %float_1 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %16 %float_2
         %21 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %21 %float_2
         %23 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %23 %float_2
         %25 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %25 %float_2
         %28 = OpLoad %int %gl_InvocationID
         %31 = OpSLessThan %bool %28 %int_3
               OpSelectionMerge %33 None
               OpBranchConditional %31 %32 %53
         %32 = OpLabel
         %41 = OpLoad %int %gl_InvocationID
         %47 = OpLoad %int %gl_InvocationID
         %49 = OpAccessChain %_ptr_Input_v4float %gl_in %47 %int_0
         %50 = OpLoad %v4float %49
         %52 = OpAccessChain %_ptr_Output_v4float %gl_out %41 %int_0
               OpStore %52 %50
               OpBranch %33
         %53 = OpLabel
         %54 = OpLoad %int %gl_InvocationID
         %58 = OpAccessChain %_ptr_Output_v4float %gl_out %54 %int_0
               OpStore %58 %57
               OpBranch %33
         %33 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test requires `tessellationShader`, the selected pipeline construction requirements, and `extendedDynamicState2PatchControlPoints` before execution.
- It creates a 4 x 4 `VK_FORMAT_R8G8B8A8_UNORM` color attachment, render pass, framebuffer, and a host-visible transfer-destination buffer. Two graphics pipeline wrappers use patch-list topology and `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT`.
- The first pipeline writes the left half and the second writes the right half. The command buffer begins the render pass, calls `cmdSetPatchControlPointsEXT` with 3, binds and draws the first pipeline, then binds and draws the second pipeline.
- After the render pass, the command buffer copies the color image to the buffer, submits, and waits. The host invalidates the allocation and compares all pixels against a reference whose left and right halves come from `expectedFirst` and `expectedSecond`.
- `tcu::floatThresholdCompare` uses a zero threshold. Any mismatch fails the leaf; otherwise it passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `change_output` | Dynamic patch-control-point state is not applied when the pipeline changes, or tessellation output and image validation are incorrect. |
| `change_winding` | Dynamic patch state, tessellation winding, culling, or image validation is incorrect. |
| `change_output_winding` | The combined patch-output and winding transition is handled incorrectly, or the rendered image validation is incorrect. |

### Cause Analysis

#### Dynamic patch state or tessellation-output transition

**Possible failure symptoms:** `change_output` or `change_output_winding` produces pixels that differ from its expected magenta or white/magenta halves. The comparison log includes the failed image.

**Possible implementation causes:** the implementation may fail to apply the recorded dynamic patch-control-point count to a later draw, retain incompatible patch state across the pipeline bind, or execute the tessellation-control and evaluation stages inconsistently when the second pipeline uses four output vertices. The image result cannot distinguish these paths from a downstream rasterization or copyback defect without source-level investigation.

#### Winding and culling transition

**Possible failure symptoms:** `change_winding` or `change_output_winding` renders the wrong half, culls the wrong draw, or returns colors different from the expected white-left and magenta-right image.

**Possible implementation causes:** the implementation may apply the tessellation-evaluation winding declaration incorrectly, classify front faces incorrectly after tessellation, or fail to preserve the selected dynamic patch state while binding the second pipeline. The test observes the combined result of tessellation, rasterization, and color copyback, so it does not isolate one stage.

#### Image copyback or comparison handling

**Possible failure symptoms:** any leaf reports a mismatch even when the command sequence completes.

**Possible implementation causes:** the implementation may mishandle color-attachment writes, the image-to-buffer copy, or visibility of copied pixels to the host. The CTS code invalidates the host-visible allocation before comparison; source-level investigation is needed to separate readback handling from rendering when only the final image differs.

## Case Pruning

### Requirement-based pruning

The source reports the case as not supported unless the device exposes `tessellationShader` and `extendedDynamicState2PatchControlPoints`, and unless the selected pipeline construction type meets its requirements. The command's valid patch-control-point range is constrained by the Vulkan limit described in [the tessellation command rules](../../../../vulkan-docs/src/chapters/shaders.adoc#L2619-L2628).

### Design-based pruning

The family fixes the dynamic count at three and uses exactly two draws. The pipeline wrapper's default static tessellation state also contains three patch control points, although that field must be ignored for these dynamically configured pipelines. Consequently, the image oracle checks the two-draw sequence with dynamic state set, but it cannot distinguish correct dynamic-state precedence from an implementation that incorrectly uses the same-valued static field. The family does not enumerate other legal patch sizes or cull modes; its three leaves cover output change, winding change, and their combination.

## Key Takeaways

- `dynamic_control_points` tests draw-time patch-control-point state across a two-pipeline tessellation sequence.
- Because both the dynamic command and the otherwise ignored static field contain three, passing does not independently prove dynamic-over-static precedence.
- `change_output` makes the second pipeline's fourth control point visible through a sentinel-derived magenta result.
- `change_winding` and `change_output_winding` make the transition observable through front-face culling and the white-left, magenta-right reference image.
- A failure proves that the final rendered image does not match the configured transition, but it does not by itself isolate tessellation, rasterization, transfer, or host-readback handling. See [Failure Meaning](#failure-meaning).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Pipeline-category registration | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L113) | Adds this family for each pipeline construction path. |
| Family registration | [`createDynamicControlPointTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L429-L458) | Defines all leaf configurations and expected colors. |
| Support checks | [`DynamicControlPointsTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L116-L126) | Requires tessellation and dynamic patch-control-point support. |
| Program generation | [`DynamicControlPointsTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L128-L235) | Builds the tessellation programs and the output/winding variants. |
| Command recording and validation | [`DynamicControlPointsTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L263-L426) | Creates both pipelines, records the dynamic state and draws, and compares the copied image. |
| Vulkan dynamic-state contract | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2588-L2630) | Specifies command behavior, required feature, and valid range. |
| Pipeline-state precedence | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6141-L6148) | Specifies that dynamic patch-control-point state replaces the static field. |
