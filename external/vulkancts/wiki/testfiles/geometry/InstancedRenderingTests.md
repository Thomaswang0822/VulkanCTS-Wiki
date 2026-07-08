## Overview

**Core question:** Do draw-instance count and geometry shader invocation count multiply correctly, producing the expected image
for every instance/invocation pair?

- This page covers the `geometry.instanced` test family implemented by
  [vktGeometryInstancedRenderingTests.cpp](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L1).
- Each test case name encodes two independent multipliers: draw instances and geometry shader invocations.
- The GPU renders one point per draw instance; the geometry shader then emits one colored rectangle per invocation for that
  point.
- The host generates the same rectangles in a CPU reference image and fuzzy-compares the rendered image against that reference.

## Background Knowledge

- Draw instancing is the API form of the common “draw many copies of one object” technique: a renderer can reuse one mesh, such
  as a model, while per-instance data supplies the transform, color, or object-specific parameters for each copy.
- This test uses the same idea in a minimal form. The shared “mesh” is one point, and the per-instance data is
  one position per point instance. The vertex binding advances once per instance through `VK_VERTEX_INPUT_RATE_INSTANCE`, so
  instance 0 reads position 0, instance 1 reads position 1, and so on.
- Geometry shader invocations are separate executions of the geometry shader for the same input primitive. The invocation count is
  declared in shader text as `layout(points, invocations = N) in`.
- `gl_InvocationID` identifies which geometry shader invocation is running. The shader uses it to vary rectangle position, size,
  and blue-channel color.
- Validation is image-based. The test does not read a counter; it compares rendered pixels to a CPU-generated reference image.

## Registration Hierarchy

```text
geometry.instanced
├── draw_1_instances_1_geometry_invocations
├── draw_1_instances_2_geometry_invocations
├── draw_1_instances_8_geometry_invocations
├── draw_1_instances_32_geometry_invocations
├── draw_1_instances_64_geometry_invocations
├── draw_1_instances_127_geometry_invocations
├── draw_2_instances_1_geometry_invocations
├── draw_2_instances_2_geometry_invocations
├── draw_2_instances_8_geometry_invocations
├── draw_2_instances_32_geometry_invocations
├── draw_2_instances_64_geometry_invocations
├── draw_2_instances_127_geometry_invocations
├── draw_4_instances_1_geometry_invocations
├── draw_4_instances_2_geometry_invocations
├── draw_4_instances_8_geometry_invocations
├── draw_4_instances_32_geometry_invocations
├── draw_4_instances_64_geometry_invocations
├── draw_4_instances_127_geometry_invocations
├── draw_8_instances_1_geometry_invocations
├── draw_8_instances_2_geometry_invocations
├── draw_8_instances_8_geometry_invocations
├── draw_8_instances_32_geometry_invocations
├── draw_8_instances_64_geometry_invocations
└── draw_8_instances_127_geometry_invocations
```

All children are executable test case leaves registered by
[createInstancedRenderingTests()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L423-L454). The default
mustpass list confirms these cases at
[geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L71-L94).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw instances | `1`, `2`, `4`, `8` | Controls how many per-instance input points the draw call supplies. | [drawInstanceCases[]](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L427-L432) |
| Geometry invocations | `1`, `2`, `8`, `32`, `64`, `127` | Controls how many geometry shader executions run for each input point. | [invocationCases[]](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L433-L436) |
| Case name | `draw_<D>_instances_<G>_geometry_invocations` | Encodes both multipliers in the executable leaf name. | [case-name construction](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L438-L451) |
| Render target | 128x128 `VK_FORMAT_R8G8B8A8_UNORM` | Fixed image size and format for all cases. | [test() setup](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L371-L376) |
| Per-instance positions | deterministic random values from seed `1234` | Gives each draw instance a reproducible point position. | [generatePerInstancePosition()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L205-L220) |

## Behavior Parameters

The primary behavioral axis is the executable test case leaf. `geometry.instanced` has no intermediate nodes below the test
family; each leaf name records the two multipliers that jointly define the behavior under test:

```text
draw_<D>_instances_<G>_geometry_invocations
```

- `<D>` is the draw instance count.
- `<G>` is the geometry shader invocation count per input point.
- The expected number of generated rectangles is `<D> × <G>`.

### `draw_<D>_instances_<G>_geometry_invocations` — combined instance/invocation multiplication

Each executable leaf asks whether the implementation combines draw instancing with geometry shader invocations correctly for one
specific `<D>, <G>` pair. The draw call should produce `<D>` input points from the per-instance vertex buffer, and the geometry
shader should run `<G>` invocations for each point. For example, `draw_4_instances_8_geometry_invocations` expects 32 rectangles:
four input points, with eight geometry shader invocations generating rectangles for each input point.

## Shader Analysis

The representative walkthrough uses `dEQP-VK.geometry.instanced.draw_4_instances_8_geometry_invocations` because it exercises
both dimensions without being too large: four draw instances and eight geometry shader invocations per instance.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.instanced.draw_4_instances_8_geometry_invocations
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `draw_4_instances` | The draw call supplies four per-instance positions. |
| `8_geometry_invocations` | The geometry shader runs eight invocations for each input point. |
| Expected rectangles | `4 × 8 = 32` rectangles. |
| Primary shader | The geometry shader uses `gl_InvocationID` to generate each rectangle's position, size, and color. |

#### Purpose

This shader verifies that geometry shader invocations run once per invocation for each draw instance's input point, and that
`gl_InvocationID` produces the same rectangle pattern as the CPU reference generator.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| Input point | Reads `gl_in[0].gl_Position`, which came from one per-instance vertex attribute. | Ties each generated pattern to one draw instance. |
| Invocation layout | Uses `layout(points, invocations = 8) in`. | Requests eight geometry shader invocations per input point. |
| Modifier | Computes `float(gl_InvocationID) / 7.0`. | Normalizes invocation ID to the 0.0–1.0 range used by color, size, and offsets. |
| Rectangle attributes | Computes color, size, x offset, and sinusoidal y offset. | Gives each invocation a distinct visible rectangle. |
| Emit pattern | Emits four vertices as a triangle strip. | Produces one rectangle per geometry shader invocation. |

#### Shader Code

The vertex and fragment shaders are simple pass-through stages. The geometry shader is the primary shader because it contains the
instanced-invocation pattern under test.

##### Geometry Shader

```glsl
#version 450
/// Eight geometry shader invocations run for each input point in the representative case.
layout(points, invocations = 8) in;
/// Each invocation emits one rectangle as four triangle-strip vertices.
layout(triangle_strip, max_vertices = 4) out;
/// Fragment shader receives the invocation-derived color.
layout(location = 0) out vec4 out_color;
in gl_PerVertex {
    vec4 gl_Position;
} gl_in[];
out gl_PerVertex {
    vec4 gl_Position;
};
void main(void)
{
    /// The input point comes from one draw instance's per-instance vertex attribute.
    const vec4  pos       = gl_in[0].gl_Position;
    /// Invocation 0 maps to 0.0 and invocation 7 maps to 1.0.
    const float modifier  = float(gl_InvocationID) / float(7);
    /// Red and green encode the input point; blue encodes the invocation position in the sequence.
    const vec4  color     = vec4(abs(pos.x), abs(pos.y), 0.2 + 0.8 * modifier, 1.0);
    /// Later invocations draw slightly larger rectangles.
    const float size      = 0.05 + 0.03 * modifier;
    /// Horizontal movement heads toward the opposite side of the image.
    const float dx        = (sign(-pos.x) - pos.x) / float(8);
    /// Each invocation offsets the rectangle differently from the source point.
    const vec4  offsetPos = pos + vec4(float(gl_InvocationID) * dx,
                                       0.3 * sin(12.0 * modifier),
                                       0.0,
                                       0.0);

    gl_Position = offsetPos + vec4(-size, -size, 0.0, 0.0);
    out_color   = color;
    EmitVertex();

    gl_Position = offsetPos + vec4(-size,  size, 0.0, 0.0);
    out_color   = color;
    EmitVertex();

    gl_Position = offsetPos + vec4( size, -size, 0.0, 0.0);
    out_color   = color;
    EmitVertex();

    gl_Position = offsetPos + vec4( size,  size, 0.0, 0.0);
    out_color   = color;
    EmitVertex();
}
```

#### Additional Info

- The vertex shader reads `in_position` at location 0 and writes it to `gl_Position`. The per-instance input rate is configured
  by pipeline state, not by shader text.
- The fragment shader writes `o_color = in_color`, so validation focuses on geometry shader output and the CPU reference image.
- The walkthrough disassembly was generated for Vulkan 1.0 / SPIR-V 1.0 from the reconstructed primary geometry shader.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw instance count | Does not change shader text; it changes `vkCmdDraw(..., instanceCount, ...)` and per-instance input data count. | [draw call](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L191-L196) |
| Geometry invocation count | Changes `layout(points, invocations = N) in`, modifier divisor, and horizontal step divisor. | [geometry shader generation](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L296-L345) |
| Reference image | Uses the same position, modifier, size, offset, and color formulas as the shader. | [generateReferenceImage()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L245-L269) |
| Device support | Cases are skipped if `maxGeometryShaderInvocations` is below the requested count. | [checkSupport()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409-L417) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 10
; Bound: 112
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %gl_in %gl_InvocationID %_ %out_color
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 8
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 4
               OpSource GLSL 450
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %gl_in "gl_in"
               OpName %modifier "modifier"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %color "color"
               OpName %size "size"
               OpName %dx "dx"
               OpName %offsetPos "offsetPos"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpName %_ ""
               OpName %out_color "out_color"
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_PerVertex Block
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpDecorate %gl_PerVertex_0 Block
               OpDecorate %out_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
%gl_PerVertex = OpTypeStruct %v4float
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_gl_PerVertex_uint_1 = OpTypeArray %gl_PerVertex %uint_1
%_ptr_Input__arr_gl_PerVertex_uint_1 = OpTypePointer Input %_arr_gl_PerVertex_uint_1
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_uint_1 Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Function_float = OpTypePointer Function %float
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
    %float_7 = OpConstant %float 7
     %uint_0 = OpConstant %uint 0
%float_0_200000003 = OpConstant %float 0.200000003
%float_0_800000012 = OpConstant %float 0.800000012
    %float_1 = OpConstant %float 1
%float_0_0500000007 = OpConstant %float 0.0500000007
%float_0_0299999993 = OpConstant %float 0.0299999993
    %float_8 = OpConstant %float 8
%float_0_300000012 = OpConstant %float 0.300000012
   %float_12 = OpConstant %float 12
    %float_0 = OpConstant %float 0
%gl_PerVertex_0 = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex_0 = OpTypePointer Output %gl_PerVertex_0
          %_ = OpVariable %_ptr_Output_gl_PerVertex_0 Output
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v4float Function
   %modifier = OpVariable %_ptr_Function_float Function
      %color = OpVariable %_ptr_Function_v4float Function
       %size = OpVariable %_ptr_Function_float Function
         %dx = OpVariable %_ptr_Function_float Function
  %offsetPos = OpVariable %_ptr_Function_v4float Function
         %19 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %20 = OpLoad %v4float %19
               OpStore %pos %20
         %25 = OpLoad %int %gl_InvocationID
         %26 = OpConvertSToF %float %25
         %28 = OpFDiv %float %26 %float_7
               OpStore %modifier %28
         %31 = OpAccessChain %_ptr_Function_float %pos %uint_0
         %32 = OpLoad %float %31
         %33 = OpExtInst %float %1 FAbs %32
         %34 = OpAccessChain %_ptr_Function_float %pos %uint_1
         %35 = OpLoad %float %34
         %36 = OpExtInst %float %1 FAbs %35
         %39 = OpLoad %float %modifier
         %40 = OpFMul %float %float_0_800000012 %39
         %41 = OpFAdd %float %float_0_200000003 %40
         %43 = OpCompositeConstruct %v4float %33 %36 %41 %float_1
               OpStore %color %43
         %47 = OpLoad %float %modifier
         %48 = OpFMul %float %float_0_0299999993 %47
         %49 = OpFAdd %float %float_0_0500000007 %48
               OpStore %size %49
         %51 = OpAccessChain %_ptr_Function_float %pos %uint_0
         %52 = OpLoad %float %51
         %53 = OpFNegate %float %52
         %54 = OpExtInst %float %1 FSign %53
         %55 = OpAccessChain %_ptr_Function_float %pos %uint_0
         %56 = OpLoad %float %55
         %57 = OpFSub %float %54 %56
         %59 = OpFDiv %float %57 %float_8
               OpStore %dx %59
         %61 = OpLoad %v4float %pos
         %62 = OpLoad %int %gl_InvocationID
         %63 = OpConvertSToF %float %62
         %64 = OpLoad %float %dx
         %65 = OpFMul %float %63 %64
         %68 = OpLoad %float %modifier
         %69 = OpFMul %float %float_12 %68
         %70 = OpExtInst %float %1 Sin %69
         %71 = OpFMul %float %float_0_300000012 %70
         %73 = OpCompositeConstruct %v4float %65 %71 %float_0 %float_0
         %74 = OpFAdd %v4float %61 %73
               OpStore %offsetPos %74
         %78 = OpLoad %v4float %offsetPos
         %79 = OpLoad %float %size
         %80 = OpFNegate %float %79
         %81 = OpLoad %float %size
         %82 = OpFNegate %float %81
         %83 = OpCompositeConstruct %v4float %80 %82 %float_0 %float_0
         %84 = OpFAdd %v4float %78 %83
         %86 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %86 %84
         %88 = OpLoad %v4float %color
               OpStore %out_color %88
               OpEmitVertex
         %89 = OpLoad %v4float %offsetPos
         %90 = OpLoad %float %size
         %91 = OpFNegate %float %90
         %92 = OpLoad %float %size
         %93 = OpCompositeConstruct %v4float %91 %92 %float_0 %float_0
         %94 = OpFAdd %v4float %89 %93
         %95 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %95 %94
         %96 = OpLoad %v4float %color
               OpStore %out_color %96
               OpEmitVertex
         %97 = OpLoad %v4float %offsetPos
         %98 = OpLoad %float %size
         %99 = OpLoad %float %size
        %100 = OpFNegate %float %99
        %101 = OpCompositeConstruct %v4float %98 %100 %float_0 %float_0
        %102 = OpFAdd %v4float %97 %101
        %103 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %103 %102
        %104 = OpLoad %v4float %color
               OpStore %out_color %104
               OpEmitVertex
        %105 = OpLoad %v4float %offsetPos
        %106 = OpLoad %float %size
        %107 = OpLoad %float %size
        %108 = OpCompositeConstruct %v4float %106 %107 %float_0 %float_0
        %109 = OpFAdd %v4float %105 %108
        %110 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %110 %109
        %111 = OpLoad %v4float %color
               OpStore %out_color %111
               OpEmitVertex
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host generates deterministic per-instance positions with seed `1234`, one position for each draw instance.
- It creates a 128x128 RGBA8 color attachment, a host-visible copyback buffer, and a vertex buffer using those per-instance
  positions.
- The draw path binds the vertex buffer and calls `vkCmdDraw()` with `vertexCount = 1` and `instanceCount = numDrawInstances`.
- After rendering, the host copies the color image to the copyback buffer and invalidates the allocation.
- The host generates a CPU reference image using `generateReferenceImage()`, which mirrors the geometry shader math for every
  per-instance position and every invocation index.
- The final pass/fail decision comes from `tcu::fuzzyCompare()` with threshold `0.01f`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw_<D>_instances_<G>_geometry_invocations` | Per-instance input advancement or draw instance count is wrong; geometry shader invocation launch or `gl_InvocationID` handling is wrong; generated rectangle attributes or framebuffer output differ from the reference image; support-limit pruning for the requested invocation count is wrong. |

### Cause Analysis

#### Per-instance input advancement or draw instance count is wrong

**Possible failure symptoms:** the rendered image can miss an entire per-instance point pattern, duplicate a pattern, or draw
rectangles at positions that belong to the wrong instance.

**Possible implementation causes:** the test exposes this because the vertex input binding uses
`VK_VERTEX_INPUT_RATE_INSTANCE`, the draw call uses `instanceCount = numDrawInstances`, and the CPU reference generates one
deterministic input position per draw instance. An implementation issue in instanced draw execution, per-instance vertex attribute
advancement, vertex buffer fetch, or first-instance handling could make the vertex shader receive the wrong `in_position` for one or
more instances.

#### Geometry shader invocation launch or `gl_InvocationID` handling is wrong

**Possible failure symptoms:** the rendered image can contain too few or too many rectangles for each input point, or the
rectangles can have the wrong sequence of offsets, sizes, and blue-channel values.

**Possible implementation causes:** the test is sensitive to this because the geometry shader declares
`layout(points, invocations = N) in`, then derives its `modifier`, horizontal offset, vertical sinusoid, size, and color from
`gl_InvocationID`. A grounded implementation cause is incorrect handling of the geometry shader invocation count, incorrect
population of the `InvocationId` built-in, or incorrect enforcement of the device's `maxGeometryShaderInvocations` limit for the
compiled shader.

#### Generated rectangle attributes or framebuffer output differ from the reference image

**Possible failure symptoms:** the shader and CPU reference use the same formulas for position, rectangle size, and color, so
a mismatch can mean a rectangle was emitted at the wrong coordinates, rasterized with the wrong color, omitted, or overwritten in an
unexpected order.

**Possible implementation causes:** possible grounded causes include shader compilation or lowering errors in the
geometry-stage arithmetic, incorrect geometry output emission, fragment-stage color forwarding problems, renderpass/framebuffer
output problems, or image copyback/cache visibility issues before the host-side `tcu::fuzzyCompare()` reads the result.

#### Support-limit pruning for the requested invocation count is wrong

**Possible failure symptoms:** a case whose requested invocation count exceeds `maxGeometryShaderInvocations` should be
skipped before execution, while supported counts should run. If the case is executed despite an insufficient limit, the rendered
result is not a valid correctness signal for that device. If the case is skipped even though the limit is sufficient, CTS coverage
is lost for a legal configuration.

**Possible implementation causes:** this cause is tied to the host-side support check, not to the image-comparison path.
A failure here means the support check logic or the limit query reported the wrong value.

## Case Pruning

### Requirement-based pruning

- All cases require geometry shader support.
- A case is skipped when the device's `maxGeometryShaderInvocations` is smaller than the requested invocation count.
- This mainly affects larger invocation counts such as `64` and `127`; they are registered but only legal on devices that support
  enough geometry shader invocations.

### Design-based pruning

- Draw instance counts are limited to `1`, `2`, `4`, and `8`, giving a small scale progression without making every case huge.
- Geometry invocation counts include required lower values and larger opportunistic values.
- The test fixes render size, color format, and random seed so differences between cases come from the two intended multipliers.

## Key Takeaways

- The test case name is the decoder: `draw_<D>_instances_<G>_geometry_invocations` should produce `<D> × <G>` rectangles.
- Draw instance count changes how many input points enter the pipeline; geometry invocation count changes how many rectangles are
  generated from each point.
- The shader and CPU reference use the same math, so the rendered image must reproduce the expected instance/invocation pattern.
- Use `Failure Meaning` for the detailed interpretation of image mismatches and support-limit failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters | [TestParams](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L58-L62) | Stores draw-instance and geometry-invocation counts. |
| Vertex input rate | [makeGraphicsPipeline()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L94-L105) | Configures per-instance vertex input. |
| Draw command path | [draw()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L135-L203) | Creates render resources, binds vertex buffer, draws, and copies the image. |
| Deterministic positions | [generatePerInstancePosition()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L205-L220) | Produces reproducible per-instance input points. |
| CPU reference generation | [generateReferenceImage()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L245-L269) | Mirrors the geometry shader rectangle math. |
| Shader generation | [initPrograms()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L271-L363) | Builds the vertex, geometry, and fragment shaders. |
| Main test function | [test()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L365-L407) | Runs the case and compares the image. |
| Support check | [checkSupport()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L409-L417) | Applies geometry shader and invocation-count requirements. |
| Registration | [createInstancedRenderingTests()](../../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp#L423-L454) | Registers the Cartesian product of draw instances and invocation counts. |
| Category attachment | [createChildren()](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L41-L50) | Attaches `instanced` under the `geometry` category. |
| Mustpass evidence | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L71-L94) | Confirms executable leaves in the default Vulkan CTS geometry mustpass list. |
