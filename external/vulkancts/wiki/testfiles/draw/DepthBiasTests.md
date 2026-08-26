## Overview

**Core question:** Does a negative constant depth bias make later geometry at a slightly greater depth win a `less` depth test across triangle and patch input and fill, line, and point polygon modes?

The `depth_bias` family checks fixed-function depth bias in Amber-rendered Vulkan graphics pipelines. Each case draws a red rectangle at depth 0.17, then a green rectangle at depth 0.18 with a negative constant bias. The green rectangle should pass the depth test and cover the red one. The family varies the input primitive topology and rasterization polygon mode, so the same depth-bias operation is exercised for ordinary triangles and tessellated patches, including line and point rasterization.

The test family is created by [`createDepthBiasTests()`](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L71-L74). It is attached only to the render-pass draw group, not to the dynamic-rendering groups, and the parent dispatcher excludes it from Vulkan SC builds.

## Background Knowledge

For the shared concepts rasterization state and image-based result checking, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- **Depth-bias computation.** Depth bias offsets fragment depth before the depth comparison. Its constant term is `depthBiasConstantFactor` multiplied by a minimum resolvable difference, `r`, derived from the depth attachment representation; the numeric constant factor is not itself a direct normalized-depth offset. The slope factor contributes a depth-slope term, and the clamp can limit the combined offset.
- **Polygon modes and patch topology.** Polygon mode determines whether triangle primitives rasterize interiors, edges, or vertices. A patch list is tessellated into primitives before rasterization, so generated triangles are subsequently subject to the selected polygon mode and depth bias.
- **Amber scripts.** Amber is a declarative graphics-test language. Its Vulkan runner creates objects from script declarations, executes the scripted commands, and performs the scripted result checks; this family uses C++ only to register those scripts and attach support requirements.

## Registration Hierarchy

```text
draw.renderpass.depth_bias
├── depth_bias_triangle_list_fill
├── depth_bias_triangle_list_line
├── depth_bias_triangle_list_point
├── depth_bias_patch_list_tri_fill
├── depth_bias_patch_list_tri_line
└── depth_bias_patch_list_tri_point
```

The root is registered under `draw.renderpass.depth_bias`. The six leaves map one-to-one to the entries in the `cases` array in [`vktDrawDepthBiasTests.cpp`](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L45-L57). The parent adds this root only when `useDynamicRendering` is false, inside the non-Vulkan-SC section of [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117).

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Effect on the case |
|---|---|---|
| Input primitive topology | `triangle_list`, `patch_list` | Selects direct triangle rasterization or tessellation into triangles. |
| Polygon mode | `fill`, `line`, `point` | Selects interior, edge, or vertex rasterization. `line` and `point` require `Features.fillModeNonSolid`. |
| Depth bias | Constant factor `-700.0`, clamp `0.0`, slope `0.0` | Produces a constant term of `-700.0 * r`, where `r` depends on the D16 depth representation. The script comments give the nominal `r = 2^-16` value, `-0.01068115234375`; the negative offset moves the second rectangle toward the camera. |
| Depth attachment | `D16_UNORM` | Stores the depth values used by the comparison. |
| Color attachment | `R8G8B8A8_UNORM`, 100 by 100 | Receives the rectangle colors and the verification image. |
| Script file | `<case-name>.amber` under `draw/depth_bias` | Supplies the shaders, buffers, pipelines, draws, and final `EXPECT`. |
| Feature requirements | none; `Features.fillModeNonSolid`; `Features.tessellationShader`; both | Gate the polygon-mode and tessellation variants. |

## Behavior Parameters

The primary behavioral axis is the pair of rendering dimensions that changes how Vulkan produces fragments: primitive topology and polygon mode. The depth-bias values remain fixed so a failure can be attributed to the interaction between depth bias and fragment generation rather than to a changing bias formula.

### `triangle_list` with `fill`

`depth_bias_triangle_list_fill` draws both rectangles as triangle lists with `POLYGON_MODE fill`. It has no additional feature requirement beyond the base Vulkan support used by the Amber runner.

### `triangle_list` with `line` or `point`

`depth_bias_triangle_list_line` and `depth_bias_triangle_list_point` keep triangle-list input and select `line` or `point` polygon mode. Both pass `Features.fillModeNonSolid` to the Amber test case.

### `patch_list` with `fill`

`depth_bias_patch_list_tri_fill` draws a patch list with three control points per patch and tessellates it as triangles. It requires `Features.tessellationShader`.

### `patch_list` with `line` or `point`

`depth_bias_patch_list_tri_line` and `depth_bias_patch_list_tri_point` combine tessellation with non-solid polygon modes. Each case requires both `Features.tessellationShader` and `Features.fillModeNonSolid`.

## Shader Analysis

The representative case is the triangle-list/fill Amber script. Its graphics shader path is deliberately simple: the vertex stage supplies clip-space position and a color varying, and the fragment stage writes that varying without modifying depth. The compute stage is part of the validation signal rather than the depth-bias implementation: it classifies each rendered pixel and stores the pass/fail image. The patch-list cases add tessellation stages around the same position/color transport; they do not introduce a different depth-bias calculation.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.depth_bias.depth_bias_triangle_list_fill
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `triangle_list` | The vertex stage receives the six vertices of the rectangle directly; no tessellation stages are present. |
| `fill` | Rasterization produces filled triangles, while the shader interface remains the same as the line and point variants. |
| `D16_UNORM`, constant bias `-700.0` | These are fixed-function depth-test inputs. No shader stage writes or adjusts depth, so the shader evidence isolates position/color transport from the bias operation. |
| `R8G8B8A8_UNORM` color and verifier dispatch | The fragment output is read by the compute verifier, which converts the rendered color into the image used by `EXPECT`. |

#### Purpose

This shader path supplies two rectangles at different vertex depths and preserves their per-draw colors so fixed-function depth bias and the `less` test determine which fragments remain visible. The verifier then turns the color result into a full-image pass/fail signal; depth bias itself is not implemented in GLSL.

#### Structural Design

| Stage | Inputs | Core operation | Output used by |
|---|---|---|---|
| Vertex (`vert_shader`) | `inPosition` at location 0; `inColor` at location 1 | Construct `gl_Position` with `w = 1.0`; copy the color | Fragment stage |
| Fragment (`frag_shader`) | Color at location 0 | Store the interpolated color unchanged | `framebuffer` |
| Compute (`comp_shader`) | `resultImage` binding 0; `verifyImage` binding 1; `gl_GlobalInvocationID` | Load one framebuffer pixel; classify `red == 0` and `alpha == 1` as expected | `verifyImage`, checked by `EXPECT` |

#### Shader Code

##### Vertex Shader

```glsl
#version 450

/// The position buffer supplies rectangle coordinates with z = 0.17 or 0.18.
layout (location = 0) in vec3 inPosition;
/// The per-draw color buffer carries red for the first draw and green for the second.
layout (location = 1) in vec4 inColor;

/// This varying is the only graphics-stage payload besides the built-in position.
layout (location = 0) out vec4 outColor;

void main()
{
  /// Fixed-function depth bias acts after this position reaches rasterization.
  gl_Position = vec4(inPosition, 1.0);
  /// Preserve the draw color for fragment output.
  outColor = inColor;
}
```

##### Fragment Shader

```glsl
#version 450

/// Receives the vertex color through location 0; interpolation is the default.
layout (location = 0) in vec4 inColor;
/// Writes the color attachment observed by the compute verifier.
layout (location = 0) out vec4 outColor;

void main()
{
  /// No fragment-depth assignment occurs; Vulkan depth testing remains fixed-function.
  outColor = inColor;
}
```

##### Compute Verification Shader

```glsl
#version 450

/// Ten-by-ten workgroups cover the 100-by-100 image with 100 invocations per group.
layout(local_size_x=10,local_size_y=10) in;
/// Binding 0 is the rendered color image; binding 1 receives the classification image.
uniform layout(set=0, binding=0, rgba8) image2D resultImage;
uniform layout(set=0, binding=1, rgba8) image2D verifyImage;

void main()
{
  /// Each invocation maps one global ID directly to one image coordinate.
  ivec2 uv = ivec2(gl_GlobalInvocationID.xy);
  vec4 color = imageLoad(resultImage, uv);

  /// This predicate accepts both opaque green and opaque black clear pixels because it checks only red and alpha.
  if(color.r == 0.0 && color.a == 1.0) imageStore(verifyImage, uv, vec4(0.0, 1.0, 0.0, 1.0));
  else imageStore(verifyImage, uv, vec4(1.0, 0.0, 0.0, 1.0));
}
```

#### Additional Info

- The six Amber files reuse the same vertex/fragment interface. The `line` and `point` files change only `POLYGON_MODE`; they do not change the shader source.
- The patch-list files keep the vertex and fragment color path but insert a three-control-point tessellation-control stage and a triangular, clockwise, equal-spacing tessellation-evaluation stage. Those stages forward positions and patch color before the same fragment write.
- The verification predicate is intentionally weaker than an exact green-color comparison: an untouched opaque-black clear pixel also satisfies `color.r == 0.0 && color.a == 1.0`. This is a limitation of the Amber oracle, not shader-side depth-bias behavior.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `triangle_list` vs `patch_list` | `patch_list` adds `tessellation_control` and `tessellation_evaluation` stages; the triangle-list representative has only vertex and fragment graphics stages. | [`depth_bias_patch_list_tri_fill.amber`](../../../data/vulkan/amber/draw/depth_bias/depth_bias_patch_list_tri_fill.amber#L28-L91) |
| `fill` vs `line` vs `point` | Polygon mode changes rasterization after the vertex stage; the vertex, fragment, and compute shader text remains shared across the corresponding scripts. | [`depth_bias_triangle_list_fill.amber`](../../../data/vulkan/amber/draw/depth_bias/depth_bias_triangle_list_fill.amber#L25-L50) |
| First vs second draw | The shader code is unchanged; the host binds different position/color buffers (`z = 0.17`, red versus `z = 0.18`, green) and changes only the fixed-function bias state. | [`depth_bias_triangle_list_fill.amber`](../../../data/vulkan/amber/draw/depth_bias/depth_bias_triangle_list_fill.amber#L56-L90), [`vktDrawDepthBiasTests.cpp`](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L51-L64) |

#### SPIR-V

##### Vertex Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 31
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPosition %outColor %inColor
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPosition "inPosition"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPosition Location 0
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
 %inPosition = OpVariable %_ptr_Input_v3float Input
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %inColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpLoad %v3float %inPosition
         %21 = OpCompositeExtract %float %19 0
         %22 = OpCompositeExtract %float %19 1
         %23 = OpCompositeExtract %float %19 2
         %24 = OpCompositeConstruct %v4float %21 %22 %23 %float_1
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
         %30 = OpLoad %v4float %inColor
               OpStore %outColor %30
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader

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
; Bound: 13
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %inColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %inColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %inColor
               OpStore %outColor %12
               OpReturn
               OpFunctionEnd
```

</details>

##### Compute Verification Shader
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
; Bound: 56
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 10 10 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %uv "uv"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %color "color"
               OpName %resultImage "resultImage"
               OpName %verifyImage "verifyImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %resultImage Binding 0
               OpDecorate %resultImage DescriptorSet 0
               OpDecorate %verifyImage Binding 1
               OpDecorate %verifyImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %22 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_22 = OpTypePointer UniformConstant %22
%resultImage = OpVariable %_ptr_UniformConstant_22 UniformConstant
       %bool = OpTypeBool
     %uint_0 = OpConstant %uint 0
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
     %uint_3 = OpConstant %uint 3
    %float_1 = OpConstant %float 1
%verifyImage = OpVariable %_ptr_UniformConstant_22 UniformConstant
         %48 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %52 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
    %uint_10 = OpConstant %uint 10
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_10 %uint_10 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %uv = OpVariable %_ptr_Function_v2int Function
      %color = OpVariable %_ptr_Function_v4float Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpBitcast %v2int %16
               OpStore %uv %17
         %25 = OpLoad %22 %resultImage
         %26 = OpLoad %v2int %uv
         %27 = OpImageRead %v4float %25 %26
               OpStore %color %27
         %31 = OpAccessChain %_ptr_Function_float %color %uint_0
         %32 = OpLoad %float %31
         %34 = OpFOrdEqual %bool %32 %float_0
               OpSelectionMerge %36 None
               OpBranchConditional %34 %35 %36
         %35 = OpLabel
         %38 = OpAccessChain %_ptr_Function_float %color %uint_3
         %39 = OpLoad %float %38
         %41 = OpFOrdEqual %bool %39 %float_1
               OpBranch %36
         %36 = OpLabel
         %42 = OpPhi %bool %34 %5 %41 %35
               OpSelectionMerge %44 None
               OpBranchConditional %42 %43 %49
         %43 = OpLabel
         %46 = OpLoad %22 %verifyImage
         %47 = OpLoad %v2int %uv
               OpImageWrite %46 %47 %48
               OpBranch %44
         %49 = OpLabel
         %50 = OpLoad %22 %verifyImage
         %51 = OpLoad %v2int %uv
               OpImageWrite %50 %51 %52
               OpBranch %44
         %44 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The Amber runner creates a 100 by 100 `R8G8B8A8_UNORM` color target, a `D16_UNORM` depth buffer, and the vertex and color buffers. The patch cases also create the tessellation pipeline stages.
2. The first pipeline uses zero bias, clears depth to `0.3`, and draws the red rectangle at depth `0.17`.
3. The second pipeline uses `BIAS constant -700.0 clamp 0.0 slope 0.0` and draws the green rectangle at depth `0.18`. With the negative bias, its depth should become less than the red rectangle's depth.
4. The compute verification pipeline reads the color result. It writes green for pixels whose red channel is zero and alpha is one, and red for all other pixels.
5. `EXPECT verifyImage IDX 0 0 SIZE 100 100 EQ_RGBA 0 255 0 255` requires the complete verification image to be opaque green. A passing source pixel need not itself be green: both an opaque green pixel from the second draw and an opaque black clear pixel have zero red and full alpha. An opaque red pixel left by the first draw becomes a red verification pixel and fails the `EXPECT`.

The oracle therefore checks that no opaque red fragment from the first draw remains where the matching second draw should replace it. It does not independently prove that every pipeline stage produced the expected coverage, because opaque black clear pixels also pass. It also does not compare a host-generated floating-point depth image; the script's compute shader converts the rendered color result into the pass/fail image.

## Failure Meaning

### Failure Cause Mapping

| Behavior parameter value | Possible failure cause(s) |
|---|---|
| `triangle_list` with `fill` | Constant depth bias, depth comparison, filled-triangle rasterization, or the associated color and depth resources may not produce the expected ordering. |
| `triangle_list` with `line` or `point` | In addition to the shared depth-bias path, non-solid rasterization may leave first-draw red fragments without corresponding passing fragments from the second draw. |
| `patch_list` with `fill` | Tessellation or its interaction with fixed-function depth bias may prevent second-draw fragments from replacing matching first-draw red fragments. |
| `patch_list` with `line` or `point` | Tessellation and non-solid rasterization may each affect whether second-draw fragments replace matching first-draw red fragments. |

### Cause Analysis

#### Constant depth-bias and depth-test path

**Possible failure symptoms:** The verification image contains red pixels because the green rectangle did not replace the red rectangle.

**Possible implementation causes:** The implementation may apply the constant factor with the wrong sign or magnitude, ignore the bias state, use the wrong depth comparison, or write an unexpected depth representation. The source establishes the state and the Amber script supplies the expected image, but this evidence does not identify a particular device or driver component.

#### Primitive topology and polygon mode

**Possible failure symptoms:** Failures occur only for `line`, `point`, or one of the topology groups, while the filled triangle-list case passes.

**Possible implementation causes:** Fragment coverage or depth interpolation may differ between the two draws for the selected polygon mode or primitive topology. For non-solid modes, the feature-gated rasterization path may not implement the expected depth-bias behavior. For patch cases, tessellation or the generated primitives may prevent the second draw from replacing first-draw fragments. Errors that suppress or identically alter both draws' coverage can escape this oracle because opaque black pixels pass verification.

#### Verification and resource path

**Possible failure symptoms:** The color result is not classified as green even when the depth ordering appears correct, or the failure affects the whole image.

**Possible implementation causes:** The framebuffer binding, color writes, image layout or copy path used by Amber, compute verification dispatch, or `EXPECT` comparison may be incorrect. The CTS source invokes the Amber framework and does not expose a narrower failure location; further investigation requires the Amber log and rendered images.

## Case Pruning

### Requirement-based pruning

The C++ registration loop does not prune individual cases beyond attaching their feature requirements. [`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L248) reports a case as unsupported before execution when an attached feature is unavailable:

- `depth_bias_triangle_list_fill` has no additional requirement.
- `depth_bias_triangle_list_line` and `depth_bias_triangle_list_point` require `Features.fillModeNonSolid`.
- `depth_bias_patch_list_tri_fill` requires `Features.tessellationShader`.
- `depth_bias_patch_list_tri_line` and `depth_bias_patch_list_tri_point` require both `Features.tessellationShader` and `Features.fillModeNonSolid`.

### Design-based pruning

All six combinations in the intended two-topology by three-polygon-mode matrix are registered; none is deliberately removed. The dispatcher places the entire family under `draw.renderpass`, so it does not appear below the `dynamic_rendering` roots, and compiles it out under `CTS_USES_VULKANSC`. These are family-wide registration boundaries, not alternate expected results.

## Key Takeaways

- The family tests one fixed depth-bias setup across six combinations of topology and polygon mode.
- The two rectangles differ in depth by `0.01`; the negative constant bias is intended to make the later green draw win the `less` depth test.
- Amber scripts perform the rendering and final image check. CTS C++ registers the leaf names and feature requirements.
- Line and point cases require `fillModeNonSolid`; patch cases require `tessellationShader`.
- The family runs only in the render-pass draw group and is absent from Vulkan SC and dynamic-rendering registration paths.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Case names and feature requirements | [`vktDrawDepthBiasTests.cpp#L40-L65`](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L40-L65) |
| Depth-bias test-group creation | [`vktDrawDepthBiasTests.cpp#L71-L74`](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L71-L74) |
| Parent registration and render-pass gate | [`vktDrawTests.cpp#L103-L117`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117) |
| Amber data directory and script files | [`external/vulkancts/data/vulkan/amber/draw/depth_bias/`](../../../data/vulkan/amber/draw/depth_bias/) |
| Triangle-list Amber pipeline and verification | [`depth_bias_triangle_list_fill.amber`](../../../data/vulkan/amber/draw/depth_bias/depth_bias_triangle_list_fill.amber) |
| Patch-list tessellation and verification | [`depth_bias_patch_list_tri_fill.amber`](../../../data/vulkan/amber/draw/depth_bias/depth_bias_patch_list_tri_fill.amber) |
| Amber test-case construction | [`vktDrawDepthBiasTests.cpp#L59-L65`](../../../modules/vulkan/draw/vktDrawDepthBiasTests.cpp#L59-L65) |
| Amber feature support checks | [`vktAmberTestCase.cpp#L203-L248`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L248) |
| Vulkan depth-bias semantics | [Depth Bias Computation](https://docs.vulkan.org/spec/latest/chapters/primsrast.html#primsrast-depthbias-computation) |
| Mustpass registration evidence | [`external/vulkancts/mustpass/main/vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt) |
