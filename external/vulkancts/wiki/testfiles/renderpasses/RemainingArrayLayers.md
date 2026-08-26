## Overview

**Core question:** When a 3D image is viewed as a 2D array with `subresourceRange.layerCount` set to `VK_REMAINING_ARRAY_LAYERS`, does the implementation attach and render to the correct set of layers across single-layer and multi-layer framebuffers?

- This page covers the `remaining_array_layers` test family implemented in [vktRenderPassRemainingArrayLayersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp) and registered under the `renderpass1` and `renderpass2` roots of the `renderpasses` test category.
- The family is registered only for legacy render pass and render pass 2; the dispatcher excludes it from dynamic rendering at [vktRenderPassTests.cpp#L8596-L8598](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598).
- Each test creates a 3D image with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`, builds a `VK_IMAGE_VIEW_TYPE_2D_ARRAY` view whose `layerCount` is `VK_REMAINING_ARRAY_LAYERS` starting at a nonzero `baseArrayLayer`, and renders white into a framebuffer built from that view.
- Three framebuffer variants change how many layers the framebuffer exposes and how the draw reaches them: a single-layer framebuffer, a multi-layer framebuffer drawn once, and a multi-layer framebuffer drawn once per layer through a geometry shader that writes `gl_Layer`.
- Passing requires every checked pixel to be `(1.0, 1.0, 1.0, 1.0)` across all drawn layers.

## Background Knowledge

- **`VK_REMAINING_ARRAY_LAYERS`.** This sentinel, used in `VkImageViewSubresourceRange::layerCount`, means the view includes every array layer of the image from `baseArrayLayer` onward. The implementation must resolve it to the actual remaining layer count at view creation time. See [resources.adoc#L5708-L5712](../../../../vulkan-docs/src/chapters/resources.adoc#L5708-L5712).
- **`VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`.** A 3D image created with this flag can be viewed as `VK_IMAGE_VIEW_TYPE_2D` or `VK_IMAGE_VIEW_TYPE_2D_ARRAY`. Each slice of the 3D image's depth dimension maps to one array layer of the 2D-array view. See [resources.adoc#L4160-L4162](../../../../vulkan-docs/src/chapters/resources.adoc#L4160-L4162).
- **Framebuffer layer count versus draw layer routing.** A framebuffer attachment carries its own layer count, taken here from the image view. A draw can reach those layers in two ways: by default, all instances land on framebuffer layer 0; or, when a geometry shader writes `gl_Layer`, each invocation can direct its primitives to a chosen framebuffer layer. This distinction is what the three framebuffer variants exercise.

## Registration Hierarchy

```text
renderpasses.renderpass1.remaining_array_layers
├── single_layer_fb
├── multi_layer_fb
└── multi_layer_fb_gl_layer
```

The same three intermediate nodes exist under `renderpasses.renderpass2.remaining_array_layers`. Each intermediate node holds the four layer-count test case leaves `1_1`, `2_2`, `4_1`, and `1_4`, registered by [createRenderPassRemainingArrayLayersTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L488-L530).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Framebuffer variant | `single_layer_fb`, `multi_layer_fb`, `multi_layer_fb_gl_layer` | Selects the framebuffer layer count and whether a geometry shader routes instances to layers. This is the primary behavioral axis. | [framebufferTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L505-L514) |
| Layer counts (leaf) | `1_1`, `2_2`, `4_1`, `1_4` | Each leaf is `{baseLayer, additionalLayers}`. The image depth is `1 + baseLayer + additionalLayers`, and `VK_REMAINING_ARRAY_LAYERS` must expand to `additionalLayers + 1` layers starting at `baseLayer`. | [layerTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503) |
| Rendering type | legacy render pass, render pass 2 | Builds the render pass with the corresponding create-info structures. Dynamic rendering is excluded by the dispatcher. | [dispatcher gate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598) |

## Behavior Parameters

The primary behavioral axis is the framebuffer variant. Each variant changes both the framebuffer layer count and how the draw reaches those layers. The four layer-count leaves are a secondary axis that varies the numerical configuration of `baseLayer` and the remaining layer count; they do not change the rendering mechanism.

### `single_layer_fb`: one-layer framebuffer baseline

The framebuffer is created with `layers = 1` regardless of how many layers the image view exposes. One draw instance is recorded. With no geometry shader, the draw lands on framebuffer layer 0, which maps to image slice `baseLayer`. This is the baseline: it confirms that a view using `VK_REMAINING_ARRAY_LAYERS` can back a single-layer framebuffer and that the draw hits the correct slice.

### `multi_layer_fb`: multi-layer framebuffer, single draw

The framebuffer layer count is `depth - baseLayer`, matching the full remaining-layer span implied by `VK_REMAINING_ARRAY_LAYERS` starting at `baseLayer`. One draw instance is recorded with no geometry shader, so all fragments land on framebuffer layer 0. The other framebuffer layers are attached but not rendered into. This variant checks that the implementation accepts a multi-layer framebuffer built from a `VK_REMAINING_ARRAY_LAYERS` view without error, even though only one layer is actually drawn.

### `multi_layer_fb_gl_layer`: multi-layer framebuffer, per-layer routing

The framebuffer layer count is again `depth - baseLayer`, but now `instanceCount` equals the framebuffer layer count and a geometry shader writes `gl_Layer = layerIndex`, where `layerIndex` is passed from the vertex shader as `gl_InstanceIndex`. Each draw instance is routed to its own framebuffer layer, so every layer of the remaining span is filled. This variant exercises the full multi-layer path end to end: `VK_REMAINING_ARRAY_LAYERS` view expansion, a matching multi-layer framebuffer, and layer-routed rendering. It requires `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L482-L483)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.renderpass1.remaining_array_layers.multi_layer_fb_gl_layer.1_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass1` | Uses the legacy render-pass path. Shader generation is identical for the `renderpass2` cases. |
| `multi_layer_fb_gl_layer` | Enables the geometry stage, creates a five-layer framebuffer, and draws five instances so the shader can route one instance to each framebuffer layer. |
| `1_4` | Sets `baseLayer = 1` and `additionalLayers = 4`. The 3D image depth is 6, and the `VK_REMAINING_ARRAY_LAYERS` view exposes five slices, 1 through 5. |

#### Purpose

The geometry shader carries each draw instance's index into `gl_Layer`, routing the five full-coverage triangles to framebuffer layers 0 through 4. The vertex and fragment stages provide full attachment coverage and a constant white validation value.

#### Structural Design

| Stage | Shader-visible operation | Effect in this case |
|-------|--------------------------|---------------------|
| Vertex | Build an oversized triangle from `gl_VertexIndex`; write `gl_InstanceIndex` to location 0. | Each of the five instances covers the framebuffer and carries one layer number on all three vertices. |
| Geometry | Copy the three input positions and assign each input `layerIndex` to `gl_Layer`. | Instance *n* is rasterized into framebuffer layer *n*. |
| Fragment | Write `vec4(1.0f)` at location 0. | Every covered pixel in each routed layer becomes white for host readback. |

#### Shader Code

##### Geometry Shader

```glsl
#version 450

/// Location 0 receives the per-instance layer number emitted on each vertex by the vertex stage.
layout(location = 0) in int layerIndex[];
/// One invocation consumes each input triangle produced by a draw instance.
layout(triangles) in;
/// The shader forwards exactly three vertices as one triangle strip.
layout(triangle_strip, max_vertices = 3) out;

void main() {
    /// Preserve the full-coverage triangle while routing it to the instance-selected framebuffer layer.
    for (int i = 0; i < 3; i++) {
        gl_Position = gl_in[i].gl_Position;
        gl_Layer = layerIndex[i];
        EmitVertex();
    }
    EndPrimitive();
}
```

##### Vertex Shader

```glsl
#version 450
/// Location 0 transports the current draw instance to the geometry stage as its destination layer.
layout(location = 0) out int layerIndex;
void main() {
    /// The three vertex indices generate (-1,-1), (3,-1), and (-1,3), covering the 32x32 viewport.
    vec2 pos = vec2(float(gl_VertexIndex & 1), float((gl_VertexIndex >> 1) & 1)) * 4.0f - 1.0f;
    gl_Position = vec4(pos, 0.0f, 1.0f);
    layerIndex = gl_InstanceIndex;
}
```

##### Fragment Shader

```glsl
#version 450
/// Location 0 writes the framebuffer's R8G8B8A8_UNORM color attachment.
layout (location=0) out vec4 outColor;
void main() {
    /// White is the exact value required by the host-side pixel scan.
    outColor = vec4(1.0f);
}
```

#### Additional Info

- The vertex shader is fixed across the page's cases. It matters here because `gl_InstanceIndex` is the geometry shader's only layer-selection input; there are no vertex buffers, descriptors, or push constants ([shader generation](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L427-L439), [pipeline layout and vertex input](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L252-L293)).
- The fragment shader is also fixed across all cases and supplies the white value checked after readback. It does not select or observe a layer ([fragment shader](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L456-L460), [result check](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L385-L405)).
- For `1_4`, the host sets both `framebufferLayers` and `instanceCount` to 5; the shader itself contains no literal layer count ([framebuffer layer count](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L226), [instance count and draw](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L327-L351)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Framebuffer variant | `multi_layer_fb_gl_layer` attaches the geometry module. `single_layer_fb` and `multi_layer_fb` omit it, draw one instance, and therefore use the default framebuffer layer 0. | [module and pipeline selection](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L242-L246), [draw instance count](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L327-L351) |
| Base/additional layer pair | The generated shader text is unchanged. The pair changes the host-computed framebuffer layer count and, for this geometry variant, the number of instances and destination `gl_Layer` values. | [layer cases](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503), [runtime counts](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L226-L227) |
| Render-pass API | Legacy render pass and render pass 2 use the same vertex, geometry, and fragment sources; only host-side render-pass construction and commands differ. | [shader generation](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L427-L465), [render-pass selection](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L219-L224) |

#### SPIR-V

##### Geometry Shader

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
; Bound: 50
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_in %gl_Layer %layerIndex
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %i "i"
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
               OpName %gl_Layer "gl_Layer"
               OpName %layerIndex "layerIndex"
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
               OpDecorate %gl_Layer BuiltIn Layer
               OpDecorate %layerIndex Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_int = OpTypePointer Output %int
   %gl_Layer = OpVariable %_ptr_Output_int Output
%_arr_int_uint_3 = OpTypeArray %int %uint_3
%_ptr_Input__arr_int_uint_3 = OpTypePointer Input %_arr_int_uint_3
 %layerIndex = OpVariable %_ptr_Input__arr_int_uint_3 Input
%_ptr_Input_int = OpTypePointer Input %int
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
               OpStore %i %int_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %int %i
         %18 = OpSLessThan %bool %15 %int_3
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %32 = OpLoad %int %i
         %34 = OpAccessChain %_ptr_Input_v4float %gl_in %32 %int_0
         %35 = OpLoad %v4float %34
         %37 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %37 %35
         %43 = OpLoad %int %i
         %45 = OpAccessChain %_ptr_Input_int %layerIndex %43
         %46 = OpLoad %int %45
               OpStore %gl_Layer %46
               OpEmitVertex
               OpBranch %13
         %13 = OpLabel
         %47 = OpLoad %int %i
         %49 = OpIAdd %int %47 %int_1
               OpStore %i %49
               OpBranch %10
         %12 = OpLabel
               OpEndPrimitive
               OpReturn
               OpFunctionEnd
```

</details>

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
; Bound: 46
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %_ %layerIndex %gl_InstanceIndex
               OpSource GLSL 450
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %layerIndex "layerIndex"
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %layerIndex Location 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_1 = OpConstant %int 1
    %float_4 = OpConstant %float 4
    %float_1 = OpConstant %float 1
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_int = OpTypePointer Output %int
 %layerIndex = OpVariable %_ptr_Output_int Output
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v2float Function
         %13 = OpLoad %int %gl_VertexIndex
         %15 = OpBitwiseAnd %int %13 %int_1
         %16 = OpConvertSToF %float %15
         %17 = OpLoad %int %gl_VertexIndex
         %18 = OpShiftRightArithmetic %int %17 %int_1
         %19 = OpBitwiseAnd %int %18 %int_1
         %20 = OpConvertSToF %float %19
         %21 = OpCompositeConstruct %v2float %16 %20
         %23 = OpVectorTimesScalar %v2float %21 %float_4
         %25 = OpCompositeConstruct %v2float %float_1 %float_1
         %26 = OpFSub %v2float %23 %25
               OpStore %pos %26
         %35 = OpLoad %v2float %pos
         %37 = OpCompositeExtract %float %35 0
         %38 = OpCompositeExtract %float %35 1
         %39 = OpCompositeConstruct %v4float %37 %38 %float_0 %float_1
         %41 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %41 %39
         %45 = OpLoad %int %gl_InstanceIndex
               OpStore %layerIndex %45
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
; Bound: 12
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor "outColor"
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
         %11 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %outColor %11
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a 3D `VK_FORMAT_R8G8B8A8_UNORM` image with extent `{32, 32, depth}` where `depth = 1 + baseLayer + additionalLayers`, `arrayLayers = 1`, and flag `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` ([imageCreateInfo](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L184-L200)).
- A `VK_IMAGE_VIEW_TYPE_2D_ARRAY` view is created with `subresourceRange = {COLOR, baseMipLevel 0, levelCount 1, baseArrayLayer baseLayer, layerCount VK_REMAINING_ARRAY_LAYERS}` ([imageViewCreateInfo](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L205-L215)).
- The render pass has one color attachment cleared on load and stored on `STORE`, in `VK_IMAGE_LAYOUT_GENERAL` ([createRenderPass](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L96-L145)).
- The framebuffer layer count is `1` for `single_layer_fb` and `depth - baseLayer` for the multi-layer variants ([framebufferLayers](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L226)).
- A pipeline barrier transitions the image to `VK_IMAGE_LAYOUT_GENERAL`, the render pass is begun, the pipeline is bound, and `cmdDraw(3, instanceCount)` is recorded where `instanceCount` is `framebufferLayers` when `writeGlLayer` is true and `1` otherwise ([draw](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L327-L356)).
- After the render pass ends, a memory barrier makes the color attachment write visible to transfer, and `vkCmdCopyImageToBuffer` copies `instanceCount` slices starting at depth `baseLayer` into a host-visible buffer ([copyback](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L358-L375)).
- The host invalidates the buffer allocation and scans every pixel of every copied layer. The case passes only if every pixel equals `(1.0, 1.0, 1.0, 1.0)` ([result check](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L385-L405)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| 3D color image | Yes | Image view | Rendered into as color attachment | Yes, via copyback | Backs the `VK_REMAINING_ARRAY_LAYERS` 2D-array view. |
| 2D-array image view | Yes | Framebuffer attachment | Provides the layer span under test | Indirectly | Carries `layerCount = VK_REMAINING_ARRAY_LAYERS`. |
| Render pass and framebuffer | Yes | Command buffer | Defines the attachment and layer count | No | Combines the view with the framebuffer layer count variant. |
| Graphics pipeline | Yes | Pipeline state | Runs the vertex, optional geometry, and fragment shaders | No | Fills rendered layers with white. |
| Color output buffer | Yes | Transfer destination | Receives copied image data | Yes | Host-side pixel source for the final scan. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_layer_fb` | Single-layer framebuffer built from a `VK_REMAINING_ARRAY_LAYERS` view did not render to the correct slice. |
| `multi_layer_fb` | Multi-layer framebuffer built from a `VK_REMAINING_ARRAY_LAYERS` view was rejected or the single draw did not land on framebuffer layer 0. |
| `multi_layer_fb_gl_layer` | `gl_Layer` routing did not reach every framebuffer layer, or one or more layers of the remaining span were not filled. |
| Any variant | Shared infrastructure failure: image or view creation, layout transition, copyback, or the pixel scan. |

### Cause Analysis

#### Single-layer framebuffer did not render to the correct slice

**Possible failure symptoms:** For a `single_layer_fb` case, the copied slice at depth `baseLayer` is not uniformly white; at least one pixel differs from `(1.0, 1.0, 1.0, 1.0)`.

**Possible implementation causes:** The view's `baseArrayLayer` was set to `baseLayer` and `layerCount` to `VK_REMAINING_ARRAY_LAYERS`, but the framebuffer exposes only layer 0. If the implementation mis-resolves `VK_REMAINING_ARRAY_LAYERS` or maps the framebuffer's single layer to the wrong slice of the 3D image, the draw writes to a slice other than `baseLayer`. Source-level investigation would be needed to distinguish a view-creation resolution bug from a framebuffer-layer-mapping bug.

#### Multi-layer framebuffer rejected or single draw misrouted

**Possible failure symptoms:** For a `multi_layer_fb` case, framebuffer creation fails, or the single copied slice at depth `baseLayer` is not white.

**Possible implementation causes:** The framebuffer layer count is `depth - baseLayer`, taken from the same `VK_REMAINING_ARRAY_LAYERS` span as the view. If the implementation computes a different remaining-layer count for the view than for the framebuffer, framebuffer creation could fail or expose the wrong layer range. Because no geometry shader is present, the draw defaults to framebuffer layer 0; if that mapping is wrong, the rendered output lands elsewhere and the checked slice stays at the clear value. Source-level investigation would be needed to separate a layer-count resolution mismatch from a layer-routing bug.

#### `gl_Layer` routing did not reach every framebuffer layer

**Possible failure symptoms:** For a `multi_layer_fb_gl_layer` case, one or more of the `framebufferLayers` copied slices are not uniformly white, while others are.

**Possible implementation causes:** Each instance is routed by the geometry shader to `gl_Layer = gl_InstanceIndex`, so all layers from 0 to `framebufferLayers - 1` should be filled. A partial failure points at incorrect `gl_Layer` handling when the framebuffer is backed by a `VK_REMAINING_ARRAY_LAYERS` view of a 3D image, or at instance-to-layer mapping that drops or duplicates a layer. If all layers fail together, a shared cause such as geometry-shader feature gating or framebuffer setup is more likely than per-layer routing.

#### Shared infrastructure failure

**Possible failure symptoms:** Failures appear across all three variants or all four layer-count leaves for a variant, or the copyback reads back the wrong region.

**Possible implementation causes:** The image-to-buffer copy uses `imageOffset.z = baseLayer` and `imageExtent.depth = instanceCount` on the 3D image ([copyRegion](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L362-L374)). A mistake in that region, in the layout transition around the render pass, or in the host pixel scan would corrupt every case using the affected path rather than only one variant.

## Case Pruning

### Requirement-based pruning

- Render pass 2 cases require `VK_KHR_create_renderpass2` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L475-L476)).
- The `multi_layer_fb_gl_layer` variant requires the `geometryShader` core feature ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L482-L483)).
- The whole family is excluded from dynamic rendering by the dispatcher, so no `RENDERING_TYPE_DYNAMIC_RENDERING` cases are registered ([dispatcher gate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598)).

### Design-based pruning

- The four layer-count leaves cover a small set of `baseLayer` and remaining-layer combinations rather than enumerating every possible pair. `1_1` and `2_2` keep the two counts equal; `4_1` sets a high base with one remaining layer; `1_4` sets a low base with several remaining layers ([layerTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503)).
- The framebuffer variants are limited to three: a single-layer baseline, a multi-layer framebuffer drawn once, and a multi-layer framebuffer drawn per layer through `gl_Layer`. Other combinations, such as a single-layer framebuffer with a geometry shader, are not registered.

## Key Takeaways

- The family probes one property: `VK_REMAINING_ARRAY_LAYERS` in a 2D-array view of a 3D image must resolve to the correct remaining-layer span and back a framebuffer whose layer count matches that span.
- The three framebuffer variants separate the concerns: `single_layer_fb` checks basic view-to-framebuffer mapping, `multi_layer_fb` checks that a multi-layer framebuffer is accepted, and `multi_layer_fb_gl_layer` checks that every layer of the remaining span can be rendered to.
- Only `multi_layer_fb_gl_layer` actually fills every layer; the other two variants draw to framebuffer layer 0 and check only that layer.
- The shaders are not under test; they only paint a known color so the host scan can tell which layers received output.
- See `## Failure Meaning` for how a non-white pixel is interpreted depending on which variant produced it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Dispatcher attachment (dynamic-rendering gate) | [vktRenderPassTests.cpp#L8596-L8598](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598) | Adds the family only for legacy render pass and render pass 2. |
| Factory function | [vktRenderPassRemainingArrayLayersTests.cpp#L488-L530](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L488-L530) | Builds the three framebuffer groups and the four layer-count leaves under each. |
| Test parameters | [vktRenderPassRemainingArrayLayersTests.cpp#L49-L65](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L49-L65) | Defines `baseLayer`, `additionalLayers`, `multiLayeredFramebuffer`, and `writeGlLayer`. |
| Image and view creation | [vktRenderPassRemainingArrayLayersTests.cpp#L184-L217](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L184-L217) | Creates the 3D image with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` and the 2D-array view with `VK_REMAINING_ARRAY_LAYERS`. |
| Render pass creation | [vktRenderPassRemainingArrayLayersTests.cpp#L96-L145](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L96-L145) | Defines the single color attachment and subpass. |
| Runtime execution and draw | [vktRenderPassRemainingArrayLayersTests.cpp#L171-L378](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L171-L378) | Builds the framebuffer, pipeline, records the draw, and copies back. |
| Result check | [vktRenderPassRemainingArrayLayersTests.cpp#L385-L405](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L385-L405) | Scans every pixel of every copied layer for white. |
| Shader generation | [vktRenderPassRemainingArrayLayersTests.cpp#L427-L465](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L427-L465) | Emits the vertex, optional geometry, and fragment shaders. |
| Support checks | [vktRenderPassRemainingArrayLayersTests.cpp#L472-L484](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L472-L484) | Requires render pass 2 extension and geometry shader feature as applicable. |
| Mustpass entries (renderpass1) | [renderpasses.txt#L36309-L36320](../../../mustpass/main/vk-default/renderpasses.txt#L36309-L36320) | 12 leaves under `renderpass1.remaining_array_layers`. |
| Mustpass entries (renderpass2) | [renderpasses.txt#L71602-L71613](../../../mustpass/main/vk-default/renderpasses.txt#L71602-L71613) | 12 leaves under `renderpass2.remaining_array_layers`. |
