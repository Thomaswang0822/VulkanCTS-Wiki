## Overview

**Core question: when several viewport-scissor pairs are bound at once, does each fragment get clipped by the scissor rectangle indexed by its own viewport, rather than by one shared rectangle?**

[`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L1) implements the `multi_viewport` test family nested under `fragment_operations.scissor`. It registers test case leaves `scissor_1` through `scissor_16`, one per active viewport count from 1 to the guaranteed `multiViewport` floor of 16.

The test idea is direct. Each case binds N identical fullscreen viewports plus N distinct scissor rectangles tiled into a grid over a 128x128 target. A geometry shader turns N input points into N fullscreen quads and writes `gl_ViewportIndex = gl_PrimitiveIDIn`, so quad `i` is routed to viewport-scissor pair `i`. Every quad tries to paint the whole framebuffer, but the scissor test should confine each to its own rectangle. The expected image is a colored grid on a gray background, one cell per pair, with no bleed between cells.

The page explains the viewport-scissor indexing property, the geometry shader that drives it, the host-side reference and compare, and what a mismatch points to.

## Background Knowledge

For the shared concept of viewport and scissor selection by `ViewportIndex`, see [Background Knowledge](../../categories/fragment_operations.md#background-knowledge) of the `fragment_operations` page.

- The pre-rasterization shader stage must assign one consistent `ViewportIndex` to every vertex of a primitive; otherwise the result is undefined. This page relies on that requirement when it maps each emitted quad to one viewport-scissor pair.
- **`multiViewport` plus the `maxViewports` floor of 16 define the sweep range.** With `multiViewport` unsupported, both counts must be 1. When it is supported, `maxViewports` has a required minimum of 16. The test sweeps the full guaranteed range, so `checkSupport()` rejects devices below that floor.

## Registration Hierarchy

```text
fragment_operations.scissor.multi_viewport
├── scissor_1
├── scissor_2
├── scissor_3
├── scissor_4
├── scissor_5
├── scissor_6
├── scissor_7
├── scissor_8
├── scissor_9
├── scissor_10
├── scissor_11
├── scissor_12
├── scissor_13
├── scissor_14
├── scissor_15
└── scissor_16
```

Registration loop: [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L451), which iterates `numViewports` from 1 to [`MIN_MAX_VIEWPORTS`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L61-L64) and names each leaf `scissor_<n>`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Viewport count | `scissor_1` ... `scissor_16` | The only registered axis; sets the number of active viewport-scissor pairs and the grid tiling derived from it | [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L446-L448) |
| Render size | 128x128 (fixed) | Fixed framebuffer for every case; grid cells scale with viewport count | [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L386) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixed; the compare uses a float tolerance of 0.02 | [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L387) |
| Scissor layout | grid of equal rectangles | Tiles the render area; columns = ceil(sqrt(N)), rows = ceil(N / cols) | [`generateScissors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) |
| Color palette | up to 16 fixed colors | One distinct color per pair, taken in order from a 16-entry table | [`generateColors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L163-L177) |

## Behavior Parameters

The primary behavioral axis is the test case leaf itself: viewport count. Each leaf changes how many viewport-scissor pairs are active and therefore how many grid cells the reference image must contain, but the shader and validation logic are identical across all 16 cases.

### `scissor_1`, single-viewport baseline

One viewport and one scissor cover the first grid cell of the 128x128 target. Only the clear, render, and compare path is exercised; no multi-viewport indexing is involved. This case anchors the infrastructure: if it fails, the defect is in the shared setup or compare rather than in viewport routing.

### `scissor_2` through `scissor_16`, multi-viewport sweep

Each leaf binds N viewport-scissor pairs and draws N fullscreen quads routed by `gl_ViewportIndex`. The grid grows from a 2x1 strip toward a 4x4 block as N rises. For non-square counts the last row is partially filled, so some cells stay gray by design. Every case beyond `scissor_1` exercises the per-fragment `ViewportIndex` selection that is the tested property.

## Shader Analysis

The tested property lives entirely in the geometry shader. The vertex and fragment shaders are pass-through and do not vary across cases, so they are summarized below rather than given separate walkthroughs.

- Vertex shader ([`initPrograms()` vertex block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L204-L217)): forwards `in_color` to `out_color`. It exists because the geometry shader consumes a vertex-stage output.
- Fragment shader ([`initPrograms()` fragment block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L262-L276)): writes `in_color` to the color attachment. No logic of its own.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.fragment_operations.scissor.multi_viewport.scissor_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Viewport count 4 | Small count whose 2x2 grid is easy to reason about; exercises multi-viewport indexing without the 4x4 visual noise of `scissor_16` |
| `gl_ViewportIndex = gl_PrimitiveIDIn` | Routes primitive `i` to viewport-scissor pair `i`, the mechanism under test |
| Fullscreen quad corners (-1,-1) to (1,1) | Forces every fragment to attempt coverage of the whole target, so only the scissor test can clip it |

#### Purpose

Verify that a geometry shader can direct each emitted primitive to a distinct viewport, and that the scissor test then clips that primitive to the matching scissor rectangle rather than to a shared one.

#### Structural Design

| Phase | Input | Output | Effect |
|-------|-------|--------|--------|
| Read primitive id | `gl_PrimitiveIDIn` (int, built-in) | loaded value `i` | Identifies which input point this is |
| Set viewport target | `i` | `gl_ViewportIndex = i` | Selects viewport `i` for viewport transform and scissor test |
| Set position | constant corner vec4 | `gl_Position` | One of four fullscreen corners, same for all viewports |
| Carry color | `in_color[0]` | `out_color` | One distinct color per primitive |
| Emit | four vertices | triangle strip quad | One fullscreen quad per input point |

The four `EmitVertex()` calls repeat the same `gl_ViewportIndex` assignment before each vertex. This satisfies the spec rule that a primitive's `ViewportIndex` be consistent across all its vertices.

#### Shader Code

##### Geometry Shader

```glsl
#version 450

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

out gl_PerVertex {
    vec4 gl_Position;
};

layout(location = 0) in  vec4 in_color[];
layout(location = 0) out vec4 out_color;

void main(void)
{
    gl_ViewportIndex = gl_PrimitiveIDIn;
    gl_Position      = vec4(-1.0, -1.0, 0.0, 1.0);
    out_color        = in_color[0];
    EmitVertex();
    gl_ViewportIndex = gl_PrimitiveIDIn;
    gl_Position      = vec4(-1.0, 1.0, 0.0, 1.0);
    out_color        = in_color[0];
    EmitVertex();
    gl_ViewportIndex = gl_PrimitiveIDIn;
    gl_Position      = vec4(1.0, -1.0, 0.0, 1.0);
    out_color        = in_color[0];
    EmitVertex();
    gl_ViewportIndex = gl_PrimitiveIDIn;
    gl_Position      = vec4(1.0, 1.0, 0.0, 1.0);
    out_color        = in_color[0];
    EmitVertex();
}
```

#### Additional Info

- The shader is byte-identical across all 16 cases. [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L199-L201) ignores the `numViewports` parameter, so no case regenerates the geometry source.
- `max_vertices = 4` matches the four emitted corners. The input is `points`, so each invocation processes exactly one primitive and writes exactly one quad.
- Because the quad spans the entire clip space, any fragment that survives to the scissor test does so only because the scissor rectangle at `ViewportIndex` permits it. A wrong index would put the wrong color in the wrong cell.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Viewport count | None. The shader source is static; only the host-side draw count, viewport array size, and scissor array change between cases. | [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L199-L201) |

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
; Bound: 48
; Schema: 0
               OpCapability Geometry
               OpCapability MultiViewport
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_ViewportIndex %gl_PrimitiveIDIn %_ %out_color %in_color
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 4
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_ViewportIndex "gl_ViewportIndex"
               OpName %gl_PrimitiveIDIn "gl_PrimitiveIDIn"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_ViewportIndex BuiltIn ViewportIndex
               OpDecorate %gl_PrimitiveIDIn BuiltIn PrimitiveId
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Output_int = OpTypePointer Output %int
%gl_ViewportIndex = OpVariable %_ptr_Output_int Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_PrimitiveIDIn = OpVariable %_ptr_Input_int Input
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
   %float_n1 = OpConstant %float -1
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %21 = OpConstantComposite %v4float %float_n1 %float_n1 %float_0 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_v4float_uint_1 = OpTypeArray %v4float %uint_1
%_ptr_Input__arr_v4float_uint_1 = OpTypePointer Input %_arr_v4float_uint_1
   %in_color = OpVariable %_ptr_Input__arr_v4float_uint_1 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
         %34 = OpConstantComposite %v4float %float_n1 %float_1 %float_0 %float_1
         %39 = OpConstantComposite %v4float %float_1 %float_n1 %float_0 %float_1
         %44 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %11 = OpLoad %int %gl_PrimitiveIDIn
               OpStore %gl_ViewportIndex %11
         %23 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %23 %21
         %31 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %32 = OpLoad %v4float %31
               OpStore %out_color %32
               OpEmitVertex
         %33 = OpLoad %int %gl_PrimitiveIDIn
               OpStore %gl_ViewportIndex %33
         %35 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %35 %34
         %36 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %37 = OpLoad %v4float %36
               OpStore %out_color %37
               OpEmitVertex
         %38 = OpLoad %int %gl_PrimitiveIDIn
               OpStore %gl_ViewportIndex %38
         %40 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %40 %39
         %41 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %42 = OpLoad %v4float %41
               OpStore %out_color %42
               OpEmitVertex
         %43 = OpLoad %int %gl_PrimitiveIDIn
               OpStore %gl_ViewportIndex %43
         %45 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %45 %44
         %46 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %47 = OpLoad %v4float %46
               OpStore %out_color %47
               OpEmitVertex
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Feature gate.** [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L438) requires the `geometryShader` and `multiViewport` core features and rejects devices whose `limits.maxViewports` is below 16. This test uses a geometry stage to write `ViewportIndex`; without `multiViewport` only one pair is legal.
- **Resource setup.** [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L380-L429) creates a 128x128 `R8G8B8A8_UNORM` color image, a host-visible vertex buffer holding one colored point per viewport, and a host-visible readback buffer. [`generateScissors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) tiles the render area into equal rectangles; [`generateColors()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L163-L177) supplies the first `numViewports` colors from a fixed 16-entry table.
- **Pipeline.** [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L94-L129) binds `numViewports` identical fullscreen viewports and the tiled scissor rectangles, with point-list topology. The viewport and scissor counts match, as the spec requires.
- **Draw.** [`ScissorRenderer::draw()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L327-L350) begins the render pass, clears to gray (0.5, 0.5, 0.5, 1.0), binds the pipeline and vertex buffer, and issues `cmdDraw(numViewports, 1, 0, 0)`: one point per viewport.
- **Copyback.** The rendered color image is copied to the host-visible buffer, which is then invalidated and read on the host.
- **Pass/fail.** [`generateReferenceImage()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L180-L197) clears the reference to gray and then clears each scissor subregion to its expected color. [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L422-L425) compares the rendered and reference images across the whole framebuffer at a per-channel threshold of 0.02. Any pixel mismatch above tolerance fails the case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `scissor_1` | Scissor rectangle setup, clear, or image compare infrastructure (single-viewport baseline) |
| `scissor_2` through `scissor_16` | Per-viewport `ViewportIndex` routing, scissor-array indexing, or multi-viewport scissor clipping |

All cases share the reference-image and compare path, so an infrastructure defect would tend to fail `scissor_1` as well.

### Cause Analysis

#### Shared clear, render, or compare infrastructure

**Possible failure symptoms:** the rendered image disagrees with the reference even for the single-viewport case, with mismatches spread across the whole target rather than confined to specific grid cells. Colors may be wrong, shifted, or the clear color may not match.

**Possible implementation causes:** a defect in the host reference image generation, the image-to-buffer copyback, the color format mapping, or the threshold compare itself. Because `scissor_1` exercises no viewport indexing, a failure here points at the shared path rather than at the tested property. Source-level investigation of [`generateReferenceImage()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L180-L197) and the copyback in [`ScissorRenderer::draw()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L346) would be the next step.

#### Per-viewport ViewportIndex routing, scissor-array indexing, or multi-viewport scissor clipping

**Possible failure symptoms:** `scissor_1` passes but one or more multi-viewport cases fail. The mismatch concentrates at cell boundaries: colors appear in the wrong cell, bleed across cells, or fill regions that should stay gray. Some cells may be empty when they should be filled, or filled when they should be empty.

**Possible implementation causes:** several distinct mechanisms could produce this, and the test alone cannot tell them apart. A driver might misroute primitives by mishandling the geometry-shader `ViewportIndex` write, so primitive `i` lands in the wrong viewport. The fixed-function scissor test might index the scissor array incorrectly, applying the wrong rectangle to a given `ViewportIndex`. Distinguishing these needs driver- or hardware-level investigation beyond what CTS source shows.

## Case Pruning

### Requirement-based pruning

- The `geometryShader` feature is required because this test writes `ViewportIndex` from its geometry shader, since only a geometry shader can do so in the core feature set used by this test. Devices lacking it are skipped by [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L434).
- The `multiViewport` feature is required; without it only one viewport-scissor pair is legal. Checked at [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L434).
- `limits.maxViewports` must be at least 16 so the full sweep is legal. Devices below the floor are rejected at [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L436-L437).

### Design-based pruning

- The sweep stops at 16 because that is the guaranteed `multiViewport` floor, not an arbitrary cap. Counts above 16 would not run on every conformant implementation and are intentionally excluded.
- No other parameter dimension is varied. Primitive type, color format, render size, and shader source are fixed across all cases.

## Key Takeaways

- The tested property is per-fragment scissor indexing by `ViewportIndex`, not geometry-shader correctness. The geometry shader is only the mechanism that routes each primitive to a viewport.
- Every emitted quad covers all of clip space, so only the scissor test at the matching index can clip it. A wrong index or a shared rectangle produces immediate, visible bleed.
- All 16 cases share one shader and one compare path; only the viewport count, grid tiling, and color subset change. `scissor_1` is the infrastructure baseline, and `scissor_2` through `scissor_16` add the multi-viewport indexing load.
- Because the reference image clears each scissor subregion to its own color, the single compare detects routing errors, clipping-bound errors, and inter-cell bleed at once.
- See `## Failure Meaning` for how to read a mismatch: a `scissor_1` failure points at shared infrastructure, while a multi-viewport-only failure points at viewport routing or scissor-array indexing.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createScissorMultiViewportTests()` | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L451`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L451) | Registers `scissor_1`..`scissor_16` via the 1..16 loop |
| `checkSupport()` | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L438`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L438) | Feature and limit gate |
| `test()` | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L380-L429`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L380-L429) | Host flow: setup, draw, compare |
| `initPrograms()` geometry block | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L219-L260`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L219-L260) | The shader under test |
| `generateScissors()` | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L131-L161) | Grid tiling |
| `generateReferenceImage()` | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L180-L197`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L180-L197) | Reference image construction |
| `makeGraphicsPipeline()` | [`vktFragmentOperationsScissorMultiViewportTests.cpp#L94-L129`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L94-L129) | Viewport and scissor array binding |
| Parent registration | [`vktFragmentOperationsScissorTests.cpp#L573-L576`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576) | Where `multi_viewport` is attached under `scissor` |
