## Overview

**Core question:** When a secondary command buffer enables viewport/scissor inheritance, does it correctly receive viewport and scissor state from the primary command buffer, an earlier secondary command buffer, or a nested secondary command buffer, instead of using its own static or stale state?

- [vktDynamicStateInheritanceTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1) implements the `inheritance` test family of the `dynamic_state` test category.
- The file tests the `VK_NV_inherited_viewport_scissor` extension. A geometry-shader pipeline draws colored rectangles through several command-buffer arrangements, selecting per-rectangle viewports and scissors. Each case asks whether the inherited viewport/scissor state is the one the test intended, not the one the secondary buffer was originally built with.
- The `primary_with_count`, `secondary_with_count`, and `nested_with_count` cases exercise the same inheritance with the `VK_EXT_extended_dynamic_state` viewport/scissor-with-count commands. The `nested` and `nested_with_count` cases also require `VK_EXT_nested_command_buffer`.
- The host produces an independent CPU reference image and compares it against the device result with exact per-pixel equality.

## Background Knowledge

- **Primary and secondary command buffers.** A primary command buffer can be submitted directly to a queue. A secondary command buffer cannot be submitted directly; it is recorded once and executed inside a primary command buffer through `vkCmdExecuteCommands`. Secondary buffers are often used to record reusable drawing work.
- **Inherited viewport/scissor state.** Normally a secondary command buffer recorded with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` must set its own dynamic viewport and scissor state before drawing. `VK_NV_inherited_viewport_scissor` adds a struct, `VkCommandBufferInheritanceViewportScissorInfoNV`, that lets a secondary buffer inherit viewport/scissor state from the primary buffer that executes it, or from an earlier secondary buffer executed before it in the same primary buffer.
- **Viewport transform and depth.** A viewport maps normalized device coordinates to window coordinates, including a depth range remap. Because this test enables depth testing, an incorrect viewport (especially its `minDepth`/`maxDepth`) changes the depth values written, which changes which fragments pass the depth test and which color reaches the framebuffer.

## Registration Hierarchy

```text
dynamic_state.monolithic.inheritance
├── baseline
├── primary (non-VulkanSC only)
├── secondary (non-VulkanSC only)
├── nested (non-VulkanSC only)
├── split (non-VulkanSC only)
├── primary_with_count (non-VulkanSC only)
├── secondary_with_count (non-VulkanSC only)
└── nested_with_count (non-VulkanSC only)
```

The test family is registered once per pipeline construction type by the category dispatcher. `baseline` is available on Vulkan SC builds; every other leaf is conditionally compiled out under `CTS_USES_VULKANSC` ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1207-L1230)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Inheritance mode | 8 values from the [`InheritanceMode`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L84-L99) enum | The primary behavioral axis: selects where viewport/scissor state comes from and whether count is dynamic. | [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1207-L1230) |
| Test geometry | 8 configurations from [`makeGeometry()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084) | Varies viewport count (2 or 3), scissor rectangles, viewport dimensions, and depth ranges so that a wrong viewport or scissor produces a visibly different image. | [makeGeometry](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084) |
| Pipeline construction type | Passed from the parent group | Selects monolithic, pipeline-library, or shader-object construction. Shader-object construction uses `vkCmdSetViewportWithCount`/`vkCmdSetScissorWithCount` in place of the fixed-count commands. | [startRenderCmds](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L874) |
| Framebuffer dimensions | 256x128 (`kWidth`, `kHeight`) | A power of two to avoid rounding error in the CPU reference. | [constants](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L52-L54) |
| Color format | `VK_FORMAT_B8G8R8A8_UNORM` | Universally supported framebuffer format. | [kFormat](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L59) |

The leaf runs all 8 geometry configurations in a single test case. A `failBits` bitmask records which configurations failed, so a partial mismatch names the failing indices in the failure message.

## Behavior Parameters

The primary behavioral axis is the inheritance mode. Each value changes where the secondary command buffer's viewport/scissor state is expected to come from, and therefore changes what a correct implementation must do.

### `baseline`: inheritance disabled

The `VK_NV_inherited_viewport_scissor` struct is not attached. The secondary command buffer sets its own viewport/scissor state directly with the non-dynamic-count commands. This case is the control: it verifies the rest of the pipeline, geometry, and reference rasterizer agree before any inheritance is introduced ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1210)).

### `primary`: inherit from the primary command buffer

The secondary buffer attaches the `VkCommandBufferInheritanceViewportScissorInfoNV` struct. The viewport/scissor state is set in the primary command buffer before `vkCmdExecuteCommands`. The drawing secondary buffer records no viewport/scissor state of its own; it must use the inherited values ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1213)).

### `secondary`: inherit from an earlier secondary command buffer

Two secondary buffers are executed in sequence inside the primary buffer. The first sets the viewport/scissor state; the drawing buffer inherits that state through the extension struct. This tests inheritance across a secondary-to-secondary boundary ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1215)).

### `nested`: inherit from a nested secondary command buffer

The setting and drawing secondary buffers are themselves executed from a third secondary buffer through `vkCmdExecuteCommands`, and that outer buffer is executed by the primary. Requires `VK_EXT_nested_command_buffer` with the `nestedCommandBuffer` and `nestedCommandBufferRendering` features ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1217)).

### `split`: inherit part from primary, part from secondary

The viewport/scissor array is divided. The first viewport/scissor is set in an early secondary buffer; the remaining viewports/scissors are set in the primary buffer. The drawing buffer inherits the combined state. This tests that the extension correctly merges state from two different sources ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1219)).

### `primary_with_count`: inherit from primary, dynamic count

Same as `primary`, but the viewport/scissor count is dynamic. The state is set with `vkCmdSetViewportWithCount`/`vkCmdSetScissorWithCount` from `VK_EXT_extended_dynamic_state`, and the pipeline is built with a dynamic viewport/scissor count. Requires `VK_EXT_extended_dynamic_state` ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1221)).

### `secondary_with_count`: inherit from earlier secondary, dynamic count

Same as `secondary`, but using the with-count commands. Requires `VK_EXT_extended_dynamic_state` ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1224)).

### `nested_with_count`: inherit from nested secondary, dynamic count

Same as `nested`, but using the with-count commands. `checkSupport()` gates it on `VK_EXT_nested_command_buffer`; it also uses `VK_EXT_extended_dynamic_state` viewport/scissor-with-count commands ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183), [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1227)).

## Shader Analysis

The geometry shader is the primary stage because it turns each point record into a rectangle and writes `gl_ViewportIndex`, which selects the inherited viewport/scissor pair used by fixed-function rasterization. The vertex and fragment stages are also shown because their location-based interfaces carry every rectangle parameter into the geometry stage and its decoded color to the attachment ([shader sources](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L196-L267)).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dynamic_state.monolithic.inheritance.primary
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `primary` inheritance mode | The primary command buffer sets the viewport/scissor arrays, while the drawing secondary command buffer must inherit them. |
| Monolithic pipeline | Uses the ordinary vertex, geometry, and fragment pipeline whose shader dataflow is reconstructed below. |
| All 8 internal geometry configurations | This leaf runs every configuration without regenerating its shaders; viewport count, rectangle records, viewport dimensions/depth ranges, and scissors are host data. |
| Geometry stage as primary shader | This is the stage that expands a rectangle and assigns its `viewportIndex` to every emitted vertex. |

#### Purpose

Show how each host-provided rectangle is routed through `gl_ViewportIndex` to one inherited viewport/scissor pair, making incorrect inherited state visible in rectangle coverage and depth ordering.

#### Structural Design

| Stage or fixed-function phase | Input | Output or action | Why it matters |
|-------------------------------|-------|------------------|----------------|
| Vertex shader | One `Rectangle` vertex record | Clip-space origin plus flat packed color, size, and viewport index | Preserves the host-selected rectangle parameters by location. |
| Geometry shader | One point and its flat parameters | Four-vertex triangle-strip rectangle | Decodes RGB, expands the point by `widthHeight`, and writes the same `gl_ViewportIndex` for all four vertices. |
| Viewport transform and scissor | `gl_Position`, `gl_ViewportIndex`, inherited arrays | Window position, remapped depth, and clipped coverage | This is where the inherited state under test is consumed. |
| Fragment shader | Flat interpolated color | Color-attachment value | Makes the surviving rectangle and depth winner observable. |

#### Shader Code

##### Geometry Shader

```glsl
#version 460

/// One input point is expanded into one rectangle.
layout(points) in;
/// Four emitted vertices form a single triangle strip.
layout(triangle_strip, max_vertices=4) out;

/// Flat location-matched values come from the vertex shader's rectangle record.
layout(location=0) flat in int r8g8b8[];
layout(location=1) flat in vec2 widthHeight[];
layout(location=2) flat in int viewportIndex[];

/// The decoded rectangle color remains constant over the emitted primitive.
layout(location=0) flat out vec4 o_color;

void main()
{
    /// Decode the host's packed 0xRRGGBB integer into normalized color channels.
    int redBits   = (r8g8b8[0] >> 16) & 255;
    int greenBits = (r8g8b8[0] >> 8)  & 255;
    int blueBits  =  r8g8b8[0]        & 255;
    float n       = 1.0 / 255.0;
    vec4 color    = vec4(redBits * n, greenBits * n, blueBits * n, 1.0);

    /// Emit the origin corner and route it to the selected inherited viewport/scissor pair.
    gl_ViewportIndex = viewportIndex[0];
    gl_Position = gl_in[0].gl_Position;
    o_color     = color;
    EmitVertex();

    /// Emit the origin plus height with the same viewport index.
    gl_ViewportIndex = viewportIndex[0];
    gl_Position = gl_in[0].gl_Position + vec4(0.0, widthHeight[0].y, 0.0, 0.0);
    o_color     = color;
    EmitVertex();

    /// Emit the origin plus width with the same viewport index.
    gl_ViewportIndex = viewportIndex[0];
    gl_Position = gl_in[0].gl_Position + vec4(widthHeight[0].x, 0.0, 0.0, 0.0);
    o_color     = color;
    EmitVertex();

    /// Complete the rectangle at origin plus width and height.
    gl_ViewportIndex = viewportIndex[0];
    gl_Position = gl_in[0].gl_Position + vec4(widthHeight[0].xy, 0.0, 0.0);
    o_color     = color;
    EmitVertex();

    EndPrimitive();
}
```

##### Vertex Shader

```glsl
#version 460

/// One host-side Rectangle occupies one vertex; these locations match the pipeline's four vertex attributes.
layout(location=0) in vec3 xyz;
layout(location=1) in int r8g8b8;
layout(location=2) in vec2 widthHeight;
layout(location=3) in int viewportIndex;

/// Flat outputs preserve each rectangle's packed color, size, and viewport selection for the geometry stage.
layout(location=0) flat out int o_r8g8b8;
layout(location=1) flat out vec2 o_widthHeight;
layout(location=2) flat out int o_viewportIndex;

void main()
{
    /// Supply the rectangle origin in clip space and forward its remaining fields by location.
    gl_Position     = vec4(xyz, 1.0);
    o_r8g8b8        = r8g8b8;
    o_widthHeight   = widthHeight;
    o_viewportIndex = viewportIndex;
}
```

##### Fragment Shader

```glsl
#version 460
/// The geometry stage's location-0 flat output arrives here despite the different variable name.
layout(location=0) flat in vec4 color;
/// The surviving rectangle color is written directly to color attachment 0.
layout(location=0) out     vec4 o_color;

void main()
{
    o_color = color;
}
```

#### Additional Info

- The vertex shader is fixed across every inheritance mode and internal geometry configuration. It matters because it carries the host-selected `viewportIndex`, clip-space origin, dimensions, and packed color into the geometry stage by matching locations 0-2.
- The fragment shader is likewise fixed. It contributes no inheritance logic, but its flat location-0 input preserves the geometry shader's decoded color so the framebuffer reveals which rectangle survives viewport/scissor clipping and depth testing.
- [`initPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1185-L1190) adds all three constant source strings without explicit `ShaderBuildOptions`, so the CTS baseline target is SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Inheritance mode | None. All eight leaves use the same three shader strings; command-buffer recording changes the source of viewport/scissor state and whether count is dynamic. | [`initPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1185-L1190), [`startRenderCmds()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L937) |
| Internal test geometry | None. Rectangle records and viewport/scissor arrays vary as host data, while the geometry shader always expands one point using `widthHeight[0]` and routes it with `viewportIndex[0]`. | [`makeGeometry()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084), [`geom_glsl`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L216-L257) |
| Pipeline construction type | The GLSL source is unchanged; only host-side pipeline assembly differs. | [`initPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1185-L1190) |

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
; Bound: 113
; Schema: 0
               OpCapability Geometry
               OpCapability MultiViewport
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %r8g8b8 %gl_ViewportIndex %viewportIndex %_ %gl_in %o_color %widthHeight
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 4
               OpSource GLSL 460
               OpName %main "main"
               OpName %redBits "redBits"
               OpName %r8g8b8 "r8g8b8"
               OpName %greenBits "greenBits"
               OpName %blueBits "blueBits"
               OpName %n "n"
               OpName %color "color"
               OpName %gl_ViewportIndex "gl_ViewportIndex"
               OpName %viewportIndex "viewportIndex"
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
               OpName %o_color "o_color"
               OpName %widthHeight "widthHeight"
               OpDecorate %r8g8b8 Flat
               OpDecorate %r8g8b8 Location 0
               OpDecorate %gl_ViewportIndex BuiltIn ViewportIndex
               OpDecorate %viewportIndex Flat
               OpDecorate %viewportIndex Location 2
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
               OpDecorate %o_color Flat
               OpDecorate %o_color Location 0
               OpDecorate %widthHeight Flat
               OpDecorate %widthHeight Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_int_uint_1 = OpTypeArray %int %uint_1
%_ptr_Input__arr_int_uint_1 = OpTypePointer Input %_arr_int_uint_1
     %r8g8b8 = OpVariable %_ptr_Input__arr_int_uint_1 Input
      %int_0 = OpConstant %int 0
%_ptr_Input_int = OpTypePointer Input %int
     %int_16 = OpConstant %int 16
    %int_255 = OpConstant %int 255
      %int_8 = OpConstant %int 8
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%float_0_00392156886 = OpConstant %float 0.00392156886
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
    %float_1 = OpConstant %float 1
%_ptr_Output_int = OpTypePointer Output %int
%gl_ViewportIndex = OpVariable %_ptr_Output_int Output
%viewportIndex = OpVariable %_ptr_Input__arr_int_uint_1 Input
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
%gl_PerVertex_0 = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_arr_gl_PerVertex_0_uint_1 = OpTypeArray %gl_PerVertex_0 %uint_1
%_ptr_Input__arr_gl_PerVertex_0_uint_1 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_1
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_1 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %v2float = OpTypeVector %float 2
%_arr_v2float_uint_1 = OpTypeArray %v2float %uint_1
%_ptr_Input__arr_v2float_uint_1 = OpTypePointer Input %_arr_v2float_uint_1
%widthHeight = OpVariable %_ptr_Input__arr_v2float_uint_1 Input
%_ptr_Input_float = OpTypePointer Input %float
     %uint_0 = OpConstant %uint 0
%_ptr_Input_v2float = OpTypePointer Input %v2float
       %main = OpFunction %void None %3
          %5 = OpLabel
    %redBits = OpVariable %_ptr_Function_int Function
  %greenBits = OpVariable %_ptr_Function_int Function
   %blueBits = OpVariable %_ptr_Function_int Function
          %n = OpVariable %_ptr_Function_float Function
      %color = OpVariable %_ptr_Function_v4float Function
         %16 = OpAccessChain %_ptr_Input_int %r8g8b8 %int_0
         %17 = OpLoad %int %16
         %19 = OpShiftRightArithmetic %int %17 %int_16
         %21 = OpBitwiseAnd %int %19 %int_255
               OpStore %redBits %21
         %23 = OpAccessChain %_ptr_Input_int %r8g8b8 %int_0
         %24 = OpLoad %int %23
         %26 = OpShiftRightArithmetic %int %24 %int_8
         %27 = OpBitwiseAnd %int %26 %int_255
               OpStore %greenBits %27
         %29 = OpAccessChain %_ptr_Input_int %r8g8b8 %int_0
         %30 = OpLoad %int %29
         %31 = OpBitwiseAnd %int %30 %int_255
               OpStore %blueBits %31
               OpStore %n %float_0_00392156886
         %39 = OpLoad %int %redBits
         %40 = OpConvertSToF %float %39
         %41 = OpLoad %float %n
         %42 = OpFMul %float %40 %41
         %43 = OpLoad %int %greenBits
         %44 = OpConvertSToF %float %43
         %45 = OpLoad %float %n
         %46 = OpFMul %float %44 %45
         %47 = OpLoad %int %blueBits
         %48 = OpConvertSToF %float %47
         %49 = OpLoad %float %n
         %50 = OpFMul %float %48 %49
         %52 = OpCompositeConstruct %v4float %42 %46 %50 %float_1
               OpStore %color %52
         %56 = OpAccessChain %_ptr_Input_int %viewportIndex %int_0
         %57 = OpLoad %int %56
               OpStore %gl_ViewportIndex %57
         %67 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %68 = OpLoad %v4float %67
         %70 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %70 %68
         %72 = OpLoad %v4float %color
               OpStore %o_color %72
               OpEmitVertex
         %73 = OpAccessChain %_ptr_Input_int %viewportIndex %int_0
         %74 = OpLoad %int %73
               OpStore %gl_ViewportIndex %74
         %75 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %76 = OpLoad %v4float %75
         %83 = OpAccessChain %_ptr_Input_float %widthHeight %int_0 %uint_1
         %84 = OpLoad %float %83
         %85 = OpCompositeConstruct %v4float %float_0 %84 %float_0 %float_0
         %86 = OpFAdd %v4float %76 %85
         %87 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %87 %86
         %88 = OpLoad %v4float %color
               OpStore %o_color %88
               OpEmitVertex
         %89 = OpAccessChain %_ptr_Input_int %viewportIndex %int_0
         %90 = OpLoad %int %89
               OpStore %gl_ViewportIndex %90
         %91 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %92 = OpLoad %v4float %91
         %94 = OpAccessChain %_ptr_Input_float %widthHeight %int_0 %uint_0
         %95 = OpLoad %float %94
         %96 = OpCompositeConstruct %v4float %95 %float_0 %float_0 %float_0
         %97 = OpFAdd %v4float %92 %96
         %98 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %98 %97
         %99 = OpLoad %v4float %color
               OpStore %o_color %99
               OpEmitVertex
        %100 = OpAccessChain %_ptr_Input_int %viewportIndex %int_0
        %101 = OpLoad %int %100
               OpStore %gl_ViewportIndex %101
        %102 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
        %103 = OpLoad %v4float %102
        %105 = OpAccessChain %_ptr_Input_v2float %widthHeight %int_0
        %106 = OpLoad %v2float %105
        %107 = OpCompositeExtract %float %106 0
        %108 = OpCompositeExtract %float %106 1
        %109 = OpCompositeConstruct %v4float %107 %108 %float_0 %float_0
        %110 = OpFAdd %v4float %103 %109
        %111 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %111 %110
        %112 = OpLoad %v4float %color
               OpStore %o_color %112
               OpEmitVertex
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
; Bound: 41
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %xyz %o_r8g8b8 %r8g8b8 %o_widthHeight %widthHeight %o_viewportIndex %viewportIndex
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %xyz "xyz"
               OpName %o_r8g8b8 "o_r8g8b8"
               OpName %r8g8b8 "r8g8b8"
               OpName %o_widthHeight "o_widthHeight"
               OpName %widthHeight "widthHeight"
               OpName %o_viewportIndex "o_viewportIndex"
               OpName %viewportIndex "viewportIndex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %xyz Location 0
               OpDecorate %o_r8g8b8 Flat
               OpDecorate %o_r8g8b8 Location 0
               OpDecorate %r8g8b8 Location 1
               OpDecorate %o_widthHeight Flat
               OpDecorate %o_widthHeight Location 1
               OpDecorate %widthHeight Location 2
               OpDecorate %o_viewportIndex Flat
               OpDecorate %o_viewportIndex Location 2
               OpDecorate %viewportIndex Location 3
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
        %xyz = OpVariable %_ptr_Input_v3float Input
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_int = OpTypePointer Output %int
   %o_r8g8b8 = OpVariable %_ptr_Output_int Output
%_ptr_Input_int = OpTypePointer Input %int
     %r8g8b8 = OpVariable %_ptr_Input_int Input
    %v2float = OpTypeVector %float 2
%_ptr_Output_v2float = OpTypePointer Output %v2float
%o_widthHeight = OpVariable %_ptr_Output_v2float Output
%_ptr_Input_v2float = OpTypePointer Input %v2float
%widthHeight = OpVariable %_ptr_Input_v2float Input
%o_viewportIndex = OpVariable %_ptr_Output_int Output
%viewportIndex = OpVariable %_ptr_Input_int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpLoad %v3float %xyz
         %21 = OpCompositeExtract %float %19 0
         %22 = OpCompositeExtract %float %19 1
         %23 = OpCompositeExtract %float %19 2
         %24 = OpCompositeConstruct %v4float %21 %22 %23 %float_1
         %26 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %26 %24
         %31 = OpLoad %int %r8g8b8
               OpStore %o_r8g8b8 %31
         %37 = OpLoad %v2float %widthHeight
               OpStore %o_widthHeight %37
         %40 = OpLoad %int %viewportIndex
               OpStore %o_viewportIndex %40
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
               OpEntryPoint Fragment %main "main" %o_color %color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %o_color "o_color"
               OpName %color "color"
               OpDecorate %o_color Location 0
               OpDecorate %color Flat
               OpDecorate %color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %color
               OpStore %o_color %12
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` requires `VK_NV_inherited_viewport_scissor` for all leaves, `VK_EXT_extended_dynamic_state` for `primary_with_count` and `secondary_with_count`, and `VK_EXT_nested_command_buffer` plus its `nestedCommandBuffer` and `nestedCommandBufferRendering` features for the nested leaves. It also checks pipeline construction requirements ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183)).
- The constructor creates a color image, a depth image (format chosen at runtime from a list of supported depth attachment formats), and matching views, then builds a render pass and framebuffer. The pipeline array is indexed by static viewport/scissor count, with index 0 reserved for the dynamic-count case ([constructor setup](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L183-L538)).
- For every geometry configuration, `startRenderCmds()` records the state-setting secondary buffer, the drawing secondary buffer, and the primary buffer. The drawing buffer attaches the `VkCommandBufferInheritanceViewportScissorInfoNV` struct when inheritance is enabled. For `primary` and `primary_with_count`, the primary records the correct viewport/scissor state that the drawing secondary must inherit. For every other mode, the primary deliberately records **bogus** viewport/scissor state so that a passing result proves the correct state came from inheritance (or, for `baseline`, from the secondary's own direct setting) rather than coincidentally matching ([startRenderCmds](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L937)).
- `rasterizeExpectedResults()` runs an independent software rasterizer on the host: it applies viewport transform, scissor clamping, a depth test (`VK_COMPARE_OP_LESS`), and color assignment for each rectangle, producing the expected image ([rasterizeExpectedResults](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L938-L1021)).
- The pass/fail check compares the device image to the CPU reference pixel by pixel. The R, G, and B channels must match exactly; alpha is unused. The power-of-two framebuffer and separated depth values mean fuzzy matching is unnecessary ([comparison](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1110-L1119)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `baseline` | The pipeline, geometry, or CPU reference is wrong, or non-inherited viewport/scissor state is not applied. A `baseline` failure undermines the other modes because it shares the same harness. |
| `primary` | Viewport/scissor state set in the primary command buffer is not inherited by the secondary buffer that attached the inheritance struct. |
| `secondary` | Viewport/scissor state set in an earlier secondary buffer is not inherited by a later secondary buffer. |
| `nested` | Inheritance does not cross a secondary-to-secondary boundary inside a nested secondary buffer, or nested command buffer execution is mishandled. |
| `split` | The implementation fails to merge viewport/scissor state from two sources into one coherent array. |
| `primary_with_count`, `secondary_with_count`, or `nested_with_count` | The with-count variant of inheritance is not applied, or the dynamic-count pipeline does not consume inherited state correctly. |
| All modes | Shared infrastructure: the depth format search picked an unsupported format, or the geometry-shader viewport selection is wrong. (For the six modes that inject bogus viewport/scissor state, a failure to override that bogus state is an additional shared cause.) |

### Cause Analysis

#### Inherited state not applied or overridden by bogus state

**Possible failure symptoms:** The device image differs from the CPU reference in regions that depend on a viewport's position, size, depth range, or scissor rectangle.

**Possible implementation causes:** The implementation may ignore the `VkCommandBufferInheritanceViewportScissorInfoNV` struct, apply stale state left over in the secondary buffer, or fail to override the deliberately bogus viewport/scissor state the primary buffer records. Because the test injects bogus state and then expects inheritance to replace it, a match between the device image and the bogus-state image points directly at missed inheritance. Whether the defect lives in the driver's command-buffer recording or in the hardware viewport/scissor unit cannot be determined from the image alone; source-level investigation against the `VK_NV_inherited_viewport_scissor` specification is needed.

#### Wrong depth values from an incorrect viewport

**Possible failure symptoms:** The color pattern is right in position but wrong in which rectangle is visible, because depth ordering changed.

**Possible implementation causes:** A viewport with the wrong `minDepth`/`maxDepth` remaps depth incorrectly. Fragments that should fail the depth test then pass, or vice versa, so a different rectangle wins the overlapping pixels. The CPU reference applies the intended depth range; a mismatch isolates the failure to the depth component of the inherited viewport.

#### Dynamic-count pipeline does not consume inherited state

**Possible failure symptoms:** Only the with-count leaves fail while their fixed-count counterparts pass.

**Possible implementation causes:** The dynamic-count pipeline (static viewport count 0) may not be wired to receive inherited viewport/scissor state, or the with-count set commands may not populate the inherited state array. Comparing a with-count leaf against its fixed-count sibling narrows the failure to the count-handling path.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_NV_inherited_viewport_scissor`.
- The with-count leaves that set state through the `VK_EXT_extended_dynamic_state` commands (`primary_with_count` and `secondary_with_count`) require that extension; `nested_with_count` relies on the same commands but `checkSupport()` gates it only on `VK_EXT_nested_command_buffer` ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183)).
- The nested leaves require `VK_EXT_nested_command_buffer` with the `nestedCommandBuffer` and `nestedCommandBufferRendering` features enabled.
- The depth attachment format is selected at runtime from `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT`, and `VK_FORMAT_D32_SFLOAT_S8_UINT`; if none is supported the test cannot run ([depth format search](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L374-L406)).
- The geometry shader writes `gl_ViewportIndex`, which implicitly requires the `multiViewport` feature.

### Design-based pruning

- Only `baseline` is registered on Vulkan SC builds. All inheritance modes are conditionally compiled out under `CTS_USES_VULKANSC` because the relevant extensions and nested command buffer support are not part of Vulkan SC.
- The eight geometry configurations are fixed across all leaves rather than parameterized, so they are not exposed as separate test cases.

## Key Takeaways

- The inheritance mode is the behavioral axis. The with-count variants test the same property through `VK_EXT_extended_dynamic_state`, and the nested variants test it through `VK_EXT_nested_command_buffer`.
- Deliberately recording bogus viewport/scissor state in the primary buffer makes the test meaningful: a passing result proves inheritance replaced the bogus state, rather than that the buffers happened to agree.
- The depth test makes viewport depth-range errors observable. An inherited viewport with the wrong `minDepth`/`maxDepth` changes which rectangle wins overlapping pixels, so a depth-ordering mismatch is a viewport-inheritance symptom.
- An exact CPU reference comparison, rather than fuzzy matching, is valid here because the framebuffer is a power of two and the depth values are separated.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateInheritanceTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1207-L1230) | Registers the eight inheritance-mode leaves and the Vulkan SC guard. |
| Support checks | [`InheritanceTestCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183) | Extension and feature requirements per mode. |
| Command recording | [`InheritanceTestInstance::startRenderCmds()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L937) | Records the state-setting, drawing, nested, and primary buffers, including bogus-state injection. |
| CPU reference | [`rasterizeExpectedResults()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L938-L1021) | Independent software rasterizer used for comparison. |
| Geometry generation | [`makeGeometry()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084) | The eight fixed geometry configurations. |
| Comparison and fail tracking | [`iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1086-L1142) | Exact per-pixel check and per-geometry `failBits`. |
| Shaders | [vert/geom/frag](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L196-L267) | Pass-through vertex, rectangle-expanding geometry shader with `gl_ViewportIndex`, pass-through fragment. |
