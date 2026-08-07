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

The Amber scripts contain the shaders that produce the geometry and color used by the depth-bias check. The triangle-list scripts use a vertex shader that writes `gl_Position = vec4(inPosition, 1.0)` and forwards `inColor` to the fragment shader. The fragment shader writes that color unchanged. The patch-list scripts add tessellation-control and tessellation-evaluation stages: the control shader sets tessellation levels and forwards control-point positions, while the evaluation shader interpolates the three positions with `gl_TessCoord` using triangular, clockwise, equal-spacing tessellation. Its color path is also a pass-through.

The verification compute shader loads each pixel from `framebuffer` and writes green to `verifyImage` when the rendered pixel has zero red and full alpha. Otherwise it writes red. The script then requires every pixel in `verifyImage` to equal opaque green. No shader computes the depth bias. The fixed-function depth test and rasterization state determine which rectangle remains visible.

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
