## Overview

**Core question:** Do geometry-shader built-in variables keep their specified meaning when they cross shader stages, primitive
boundaries, and the GLSL/HLSL source boundary?

- This page covers the `geometry.builtin_variable` test family implemented by
  [vktGeometryBuiltinVariableGeometryShaderTests.cpp](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L1).
- The family contains five executable leaves grouped under `in_block` and `outside_block`.
- The leaves exercise `gl_PointSize`, `gl_PrimitiveIDIn`, `gl_PrimitiveID`, and an HLSL `SV_POSITION` geometry-shader path.
- Every case renders a small deterministic image and compares it with a reference PNG through the shared geometry render path.

## Background Knowledge

- **Geometry-stage built-ins.** Built-in variables are part of the contract between pipeline stages and fixed-function behavior. A geometry shader can consume input built-ins, write output built-ins, and pass values that later stages or rasterization interpret specially.
- **Input and output primitive IDs.** `gl_PrimitiveIDIn` identifies the input primitive being processed by the geometry shader. `gl_PrimitiveID` can be written by the geometry shader and then observed by fragment shading as the primitive ID for emitted geometry.
- **Geometry-stage point size.** `gl_PointSize` written by the geometry shader controls rasterized point size when the device supports geometry-stage point-size writes.
- **Interface style and language mapping.** GLSL can declare built-ins inside `gl_PerVertex` blocks, while HLSL expresses position through semantics such as `SV_POSITION`. Both forms must map to the same pipeline-visible built-in meanings.

## Registration Hierarchy

```text
geometry.builtin_variable
├── in_block
└── outside_block
```

The two intermediate nodes are registered by
[createBuiltinVariableGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L428-L448).
The default mustpass list confirms the five executable paths at
[geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L15-L19).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `in_block`, `outside_block` | Separates GLSL interface-block cases from the HLSL position case. | [registration](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L430-L446) |
| Built-in mode | `TEST_POINT_SIZE`, `TEST_PRIMITIVE_ID_IN`, `TEST_PRIMITIVE_ID`, `TEST_POSITION` | Selects the generated shaders, topology, and validation image name. | [VariableTest](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L64-L70) |
| Primitive topology | point list, line strip, triangle strip | Matches the built-in being tested: points for point size/output primitive ID, lines for input primitive ID, triangle strip for position. | [constructor](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L91-L99) |
| Vertex data | five fixed positions and five fixed secondary attributes | Provides deterministic geometry and attribute values. | [genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L103-L120) |
| Indexed restart | off for four leaves; on for `primitive_id_in_restarted` | Tests `gl_PrimitiveIDIn` across an explicit `0xFFFF` primitive-restart marker. | [restart indices](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L121-L130) |
| Validation target | reference PNG named after the leaf | The rendered image is compared with `vulkan/data/geometry/<leaf>.png`. | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) |

## Behavior Parameters

The primary behavioral axis is the executable test case leaf. The `in_block` and `outside_block` intermediate nodes still matter
because they separate GLSL interface-block cases from the HLSL position case, but each leaf chooses a distinct built-in contract,
shader shape, draw path, or validation image.

### `in_block.point_size` — geometry-written point size

This leaf checks whether a geometry shader can write `gl_PointSize` through an explicit GLSL `gl_PerVertex` output block. The
vertex shader forwards the secondary attribute, the geometry shader writes `gl_PointSize = value + 1.0`, emits one white point, and
the reference image verifies the resulting point sizes. This is the only leaf with the extra `shaderTessellationAndGeometryPointSize`
feature gate.

### `in_block.primitive_id_in` — input primitive ID for line-strip geometry input

This leaf checks whether `gl_PrimitiveIDIn` has the expected value for each line primitive consumed by the geometry shader. The
geometry shader uses `colors[gl_PrimitiveIDIn % 4]`, so a wrong input primitive ID changes the color pattern in the output image.
It uses non-indexed `vkCmdDraw` over the fixed five-vertex line strip.

### `in_block.primitive_id_in_restarted` — input primitive ID across primitive restart

This leaf uses the same `gl_PrimitiveIDIn` shader behavior as `primitive_id_in`, but changes the host draw path to indexed drawing
with indices `1, 4, 0xFFFF, 2, 1`. Its purpose is to isolate whether primitive restart splits the line strip and numbers the
geometry-shader input primitives as expected.

### `in_block.primitive_id` — geometry-written primitive ID observed by fragment shading

This leaf checks the output `gl_PrimitiveID` path. The vertex shader forwards a secondary attribute, the geometry shader writes
`int(floor(value)) + 3` to `gl_PrimitiveID` for each emitted triangle vertex, and the fragment shader maps `gl_PrimitiveID % 4` to a
color table. The reference image therefore verifies that the geometry-written ID reaches fragment shading.

### `outside_block.position` — HLSL `SV_POSITION` geometry-stage pass-through

This leaf checks the mixed-language position path. The vertex and fragment shaders are GLSL, while the geometry shader is HLSL and
copies `SV_POSITION` from `triangle VSOut input[3]` into a `TriangleStream<VSOut>`. The fixed yellow fragment output makes the
emitted triangle shape and placement the observable signal.

The shared point, line, and attribute data come from
[genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L103-L132). The indexed
restart variant switches from `vkCmdDraw` to `vkCmdDrawIndexed` in
[drawCommand()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L161-L170).

## Shader Analysis

The representative walkthrough uses `dEQP-VK.geometry.builtin_variable.in_block.primitive_id` because it exercises the most complete
built-in value chain: vertex attribute → geometry shader input varying → geometry-written `gl_PrimitiveID` → fragment-stage
`gl_PrimitiveID` color selection.

A second walkthrough covers `dEQP-VK.geometry.builtin_variable.outside_block.position`. This is the special HLSL case in the family.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.builtin_variable.in_block.primitive_id
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Intermediate node | `in_block`, so the geometry shader uses GLSL `gl_PerVertex` interface-block declarations. |
| Input topology | Point list: each input point becomes one geometry shader invocation. |
| Secondary attribute values | `0`, `1`, `2`, `3`, `0`; the geometry shader turns these into primitive IDs `3`, `4`, `5`, `6`, `3`. |
| Output primitive shape | One triangle per input point, emitted as three triangle-strip vertices. |
| Fragment color | Selected from `colors[gl_PrimitiveID % 4]`, proving the fragment stage saw the geometry-written ID. |

#### Purpose

This shader verifies that a value assigned to `gl_PrimitiveID` by the geometry shader becomes the primitive ID observed by the
fragment shader. If the compiler drops the write, uses the input primitive ID instead, or fails to pass the value to fragment
shading, the rendered color pattern differs from the reference PNG.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| Vertex attribute forwarding | The vertex shader forwards `a_primitiveID` as `v_geom_primitiveID`. | Supplies a known per-point value without relying on input primitive numbering. |
| Geometry input | The geometry shader reads `v_geom_primitiveID[0].x`. | Uses the value attached to the current point. |
| ID assignment | It writes `int(floor(value)) + 3` to `gl_PrimitiveID` before every emitted vertex. | Makes the output primitive ID deterministic and visibly different from the raw attribute. |
| Triangle emission | It emits three vertices around the source point. | Creates visible fragments that can observe the ID. |
| Fragment color lookup | The fragment shader writes `colors[gl_PrimitiveID % 4]`. | Turns the built-in value into a visible pass/fail signal. |

#### Shader Code

The vertex shader is a simple position and attribute forwarder. The fragment shader maps `gl_PrimitiveID` to one of four colors.
The geometry shader is the primary shader because it writes the built-in being tested.

##### Geometry Shader

```glsl
#version 450
/// Geometry input built-ins for the single point currently being expanded.
in gl_PerVertex
{
    vec4 gl_Position;
    float gl_PointSize;
} gl_in[];
/// Geometry output built-ins. This case writes `gl_Position` and the separate built-in `gl_PrimitiveID`.
out gl_PerVertex
{
    vec4 gl_Position;
    float gl_PointSize;
};
/// One geometry shader invocation consumes one point-list primitive.
layout(points, invocations=1) in;
/// The invocation emits one triangle as three triangle-strip vertices.
layout(triangle_strip, max_vertices = 3) out;
/// Location 0 carries the per-point attribute value that will be converted into the output primitive ID.
layout(location = 0) in vec4 v_geom_primitiveID[];
void main (void)
{
    /// First output vertex: shift slightly right from the input point.
    gl_Position = gl_in[0].gl_Position + vec4(0.05, 0.0, 0.0, 0.0);
    /// Write the output primitive ID that the fragment shader should observe.
    gl_PrimitiveID = int(floor(v_geom_primitiveID[0].x)) + 3;
    EmitVertex();

    /// Second output vertex: shift slightly left.
    gl_Position = gl_in[0].gl_Position - vec4(0.05, 0.0, 0.0, 0.0);
    gl_PrimitiveID = int(floor(v_geom_primitiveID[0].x)) + 3;
    EmitVertex();

    /// Third output vertex: shift slightly upward to complete the triangle.
    gl_Position = gl_in[0].gl_Position + vec4(0.0, 0.05, 0.0, 0.0);
    gl_PrimitiveID = int(floor(v_geom_primitiveID[0].x)) + 3;
    EmitVertex();
}
```

#### Additional Info

- Source shader generation for this path is in
  [BuiltinVariableRenderTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L231-L347).
- The fragment shader color table is deliberately ordered as `yellow`, `red`, `green`, `blue`, so the modulo result changes visible
  color rather than only metadata
  ([fragment shader generation](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L394-L405)).
- The walkthrough disassembly was generated for Vulkan 1.0 / SPIR-V 1.0 from the reconstructed primary geometry shader.

#### Parameter Variation Summary

| Variation | Shader/runtime change | Evidence |
|-----------|-----------------------|----------|
| `point_size` | Geometry shader writes `gl_PointSize` and emits points with white color; requires `GL_EXT_geometry_point_size`. | [point-size geometry shader](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L259-L284) |
| `primitive_id_in` | Geometry shader reads `gl_PrimitiveIDIn` for line-strip input and uses it to choose output color. | [primitive-ID-in geometry shader](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L285-L319) |
| `primitive_id_in_restarted` | Uses the same shader as `primitive_id_in`, but host drawing is indexed with a `0xFFFF` primitive-restart marker. | [restart setup](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L121-L130) |
| `outside_block.position` | Geometry shader source is HLSL and copies `SV_POSITION` values into a triangle stream. | [HLSL geometry shader](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L349-L365) |

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
; Bound: 60
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_in %gl_PrimitiveID %v_geom_primitiveID
               OpExecutionMode %main InputPoints
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_PointSize"
               OpName %gl_in "gl_in"
               OpName %gl_PrimitiveID "gl_PrimitiveID"
               OpName %v_geom_primitiveID "v_geom_primitiveID"
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn PointSize
               OpDecorate %gl_PerVertex_0 Block
               OpDecorate %gl_PrimitiveID BuiltIn PrimitiveId
               OpDecorate %v_geom_primitiveID Location 0
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
%float_0_0500000007 = OpConstant %float 0.0500000007
    %float_0 = OpConstant %float 0
         %24 = OpConstantComposite %v4float %float_0_0500000007 %float_0 %float_0 %float_0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_int = OpTypePointer Output %int
%gl_PrimitiveID = OpVariable %_ptr_Output_int Output
%_arr_v4float_uint_1 = OpTypeArray %v4float %uint_1
%_ptr_Input__arr_v4float_uint_1 = OpTypePointer Input %_arr_v4float_uint_1
%v_geom_primitiveID = OpVariable %_ptr_Input__arr_v4float_uint_1 Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
      %int_3 = OpConstant %int 3
         %52 = OpConstantComposite %v4float %float_0 %float_0_0500000007 %float_0 %float_0
       %main = OpFunction %void None %3
          %5 = OpLabel
         %20 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %21 = OpLoad %v4float %20
         %25 = OpFAdd %v4float %21 %24
         %27 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %27 %25
         %35 = OpAccessChain %_ptr_Input_float %v_geom_primitiveID %int_0 %uint_0
         %36 = OpLoad %float %35
         %37 = OpExtInst %float %1 Floor %36
         %38 = OpConvertFToS %int %37
         %40 = OpIAdd %int %38 %int_3
               OpStore %gl_PrimitiveID %40
               OpEmitVertex
         %41 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %42 = OpLoad %v4float %41
         %43 = OpFSub %v4float %42 %24
         %44 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %44 %43
         %45 = OpAccessChain %_ptr_Input_float %v_geom_primitiveID %int_0 %uint_0
         %46 = OpLoad %float %45
         %47 = OpExtInst %float %1 Floor %46
         %48 = OpConvertFToS %int %47
         %49 = OpIAdd %int %48 %int_3
               OpStore %gl_PrimitiveID %49
               OpEmitVertex
         %50 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %51 = OpLoad %v4float %50
         %53 = OpFAdd %v4float %51 %52
         %54 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %54 %53
         %55 = OpAccessChain %_ptr_Input_float %v_geom_primitiveID %int_0 %uint_0
         %56 = OpLoad %float %55
         %57 = OpExtInst %float %1 Floor %56
         %58 = OpConvertFToS %int %57
         %59 = OpIAdd %int %58 %int_3
               OpStore %gl_PrimitiveID %59
               OpEmitVertex
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.geometry.builtin_variable.outside_block.position
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Intermediate node | `outside_block`, so the geometry shader is generated as HLSL instead of GLSL `gl_PerVertex` block syntax. |
| Input topology | Triangle strip, so each geometry shader invocation receives a triangle as `input[3]`. |
| Position semantic | `SV_POSITION` carries the position field through the HLSL `VSOut` structure. |
| Output stream | `TriangleStream<VSOut>` appends three vertices, preserving the triangle positions. |
| Fragment color | Fixed yellow; visible correctness comes from whether the HLSL geometry stage emits the expected triangle. |

#### Purpose

This shader verifies the HLSL geometry-stage position path used by the `outside_block.position` leaf. The important behavior is that
`SV_POSITION` inputs are accepted for a geometry shader, copied to output `SV_POSITION`, and emitted through the HLSL triangle stream
in a form that produces the expected reference image.

#### Structural Design

| Step | Shader behavior | Why it matters |
|------|-----------------|----------------|
| HLSL interface struct | `VSOut` contains only `float4 Position : SV_POSITION`. | Keeps the case focused on position semantic mapping rather than user varyings. |
| Geometry input | The entry point receives `triangle VSOut input[3]`. | Matches the triangle-strip topology selected for `TEST_POSITION`. |
| Output stream | The entry point writes `output.Position` and calls `TriStream.Append(output)` three times. | Emits the same three positions as one triangle. |
| Validation signal | The fragment shader writes fixed yellow. | Any wrong position mapping or missing stream append changes the rendered triangle image. |

#### Shader Code

The HLSL geometry shader is the primary shader for this walkthrough because it is the only HLSL-generated stage in the family and
contains the tested `SV_POSITION` interface.

##### Geometry Shader

```hlsl
/// The only geometry-stage payload is the position semantic. CTS uses the same struct for input and output.
struct VSOut
{
    float4 Position : SV_POSITION;
};

/// The source requests room for up to 10 emitted vertices, although this exact case appends only 3.
[maxvertexcount(10)]
void main(triangle VSOut input[3], inout TriangleStream<VSOut> TriStream)
{
    VSOut output;

    /// Copy the first triangle vertex position from geometry input to output stream.
    output.Position = input[0].Position;
    TriStream.Append(output);

    /// Copy the second triangle vertex position.
    output.Position = input[1].Position;
    TriStream.Append(output);

    /// Copy the third triangle vertex position, completing one emitted triangle.
    output.Position = input[2].Position;
    TriStream.Append(output);
}
```

#### Additional Info

- The HLSL shader text is selected only for `TEST_POSITION` and is inserted through `sourceCollections.hlslSources.add("geometry")`
  ([HLSL insertion](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L349-L365)).
- The vertex shader for this leaf still comes from the GLSL path and writes both `v_position = a_position` and
  `gl_Position = a_position`; the HLSL geometry shader consumes the position semantic rather than that user varying
  ([vertex shader branch](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L240-L247)).
- The fragment shader is fixed yellow, so this walkthrough's validation signal is the emitted triangle shape and placement rather
  than a color table
  ([fragment shader branch](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L406-L412)).

#### Parameter Variation Summary

| Variation | Shader/runtime change | Evidence |
|-----------|-----------------------|----------|
| `outside_block.position` | Uses HLSL `SV_POSITION` and `TriangleStream<VSOut>` in the geometry stage. | [HLSL geometry shader](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L349-L365) |
| `in_block` leaves | Use GLSL geometry shaders with explicit `gl_PerVertex` declarations and built-in variables such as `gl_PointSize`, `gl_PrimitiveIDIn`, or `gl_PrimitiveID`. | [GLSL geometry branches](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L259-L347) |
| Runtime topology | `TEST_POSITION` selects `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`, matching the HLSL geometry input. | [topology selection](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L91-L99) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed HLSL from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 10
; Bound: 55
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %TriStream_Position %input_Position
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 10
               OpSource HLSL 500
               OpName %main "main"
               OpName %TriStream_Position "TriStream.Position"
               OpName %input_Position "input.Position"
               OpDecorate %TriStream_Position BuiltIn Position
               OpDecorate %input_Position BuiltIn Position
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%TriStream_Position = OpVariable %_ptr_Output_v4float Output
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Input__arr_v4float_uint_3 = OpTypePointer Input %_arr_v4float_uint_3
%input_Position = OpVariable %_ptr_Input__arr_v4float_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %47 = OpAccessChain %_ptr_Input_v4float %input_Position %int_0
         %48 = OpLoad %v4float %47
         %50 = OpAccessChain %_ptr_Input_v4float %input_Position %int_1
         %51 = OpLoad %v4float %50
         %53 = OpAccessChain %_ptr_Input_v4float %input_Position %int_2
         %54 = OpLoad %v4float %53
               OpStore %TriStream_Position %48
               OpEmitVertex
               OpStore %TriStream_Position %51
               OpEmitVertex
               OpStore %TriStream_Position %54
               OpEmitVertex
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each leaf creates a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` color attachment and a host-visible copyback buffer through the shared
  `GeometryExpanderRenderTestInstance::iterate()` path
  ([setup](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L130)).
- The host packs five `vec4` positions and five `vec4` secondary attributes into a single vertex buffer. Attribute location 0 is
  position, and location 1 is the secondary value
  ([vertex input setup](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L98-L120)).
- The selected leaf chooses point-list, line-strip, or triangle-strip input topology in the test-instance constructor
  ([topology selection](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L91-L99)).
- The `primitive_id_in_restarted` leaf additionally binds a `uint16_t` index buffer and issues `vkCmdDrawIndexed`; all other leaves
  issue `vkCmdDraw` over the five input vertices
  ([drawCommand()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L161-L170)).
- After rendering, the host copies the color image to the copyback buffer, invalidates the host allocation, and calls
  `compareWithFileImage()`
  ([copy and compare](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L185-L200)).
- `compareWithFileImage()` loads `vulkan/data/geometry/<testName>.png`, first tries fuzzy comparison with threshold `0.0015`, and
  then applies integer-threshold position-deviation comparison when appropriate
  ([comparison helper](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `in_block.point_size` | Geometry-stage point-size output path mismatch. |
| `in_block.primitive_id_in` | Incorrect input primitive ID assignment for geometry-shader line input. |
| `in_block.primitive_id_in_restarted` | Incorrect primitive-restart splitting or primitive ID assignment after restart. |
| `in_block.primitive_id` | Incorrect geometry-written `gl_PrimitiveID` propagation to fragment shading. |
| `outside_block.position` | Incorrect HLSL `SV_POSITION` mapping or geometry stream emission. |

If all or most leaves fail together, the likely cause shifts away from one built-in variable and toward shared geometry-shader
execution, vertex input, render target, copyback, or reference-image comparison infrastructure.

### Cause Analysis

#### Geometry-stage point-size output path mismatch

**Possible failure symptoms:** for `in_block.point_size`, the rendered white points have the wrong size or placement relative
to `point_size.png`.

**Possible implementation causes:** the test derives point size from the secondary vertex attribute and writes it as
`gl_PointSize = value + 1.0` in the geometry shader, so the failure points to a problem in accepting, lowering, or applying
geometry-stage `gl_PointSize` writes, or in using that built-in during point rasterization. Because this leaf is gated by
`shaderTessellationAndGeometryPointSize`, a failure after the support check means the feature was advertised but the rendered behavior
did not match the CTS reference.

#### Incorrect input primitive ID assignment for geometry-shader line input

**Possible failure symptoms:** for `in_block.primitive_id_in`, the observable error is a wrong color pattern: the geometry
shader chooses colors from `gl_PrimitiveIDIn % 4` for each consumed line primitive.

**Possible implementation causes:** the geometry shader may receive incorrect primitive IDs for line-strip input, or the
primitive ID value may not be preserved correctly through shader compilation and geometry-stage execution. Since the fragment shader
only forwards the color produced by the geometry shader, this leaf mainly isolates the input-side primitive ID contract.

#### Incorrect primitive-restart splitting or primitive ID assignment after restart

**Possible failure symptoms:** for `in_block.primitive_id_in_restarted`, the shader logic is the same as `primitive_id_in`;
the distinguishing behavior is the indexed draw with a `0xFFFF` restart marker. A failure specific to this leaf means the
implementation may split the line strip incorrectly at the restart marker, count primitives incorrectly after the restart, or feed an
unexpected `gl_PrimitiveIDIn` value to the geometry shader for the restarted segment.

**Possible implementation causes:** a failure shared with `primitive_id_in` is less specific and should first be read as a
basic `gl_PrimitiveIDIn` problem rather than a restart-specific problem. A failure unique to this leaf points to primitive-restart
assembly or post-restart primitive numbering.

#### Incorrect geometry-written `gl_PrimitiveID` propagation to fragment shading

**Possible failure symptoms:** for `in_block.primitive_id`, emitted triangles receive the wrong colors from the fragment
shader's `colors[gl_PrimitiveID % 4]` table.

**Possible implementation causes:** the geometry shader writes a deterministic ID from the forwarded vertex attribute
before each `EmitVertex()`, so a mismatch can mean the write to the output built-in is dropped, substituted with the input primitive
ID, assigned to the wrong emitted primitive, or not delivered to fragment shading. This leaf specifically tests the geometry-output
to fragment-input path for `gl_PrimitiveID`.

#### Incorrect HLSL `SV_POSITION` mapping or geometry stream emission

**Possible failure symptoms:** for `outside_block.position`, the fragment shader always writes yellow, so color is not the main
signal. A failure means the emitted triangle's shape, location, or coverage differs from `position.png`, or the HLSL geometry stage
does not emit the expected three vertices.

**Possible implementation causes:** the likely implementation areas are HLSL `SV_POSITION` mapping into the SPIR-V
`Position` built-in, geometry-shader input array handling for `triangle VSOut input[3]`, or `TriangleStream<VSOut>` append lowering.

#### Shared geometry render or image-comparison path mismatch

**Possible failure symptoms:** when multiple unrelated leaves fail together, the common path becomes more important than the
individual built-in contracts. A broad failure can come from common geometry-shader execution, vertex input interpretation, color
attachment rendering, image copyback, host-visible memory invalidation, or reference-image comparison setup.

**Possible implementation causes:** the shared path creates the RGBA8 render target, binds fixed vertex data, executes the
geometry pipeline, copies the image to a host-visible buffer, and compares it with a reference PNG. Source-level investigation is
needed to separate a shared CTS infrastructure problem from an implementation problem when the failure is not isolated to one behavior
parameter value.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `geometryShader`
  ([checkSupport()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L194-L197)).
- The `point_size` leaf additionally requires `shaderTessellationAndGeometryPointSize`
  ([point-size gate](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L198-L200)). This pruning
  prevents running a point-size write test on implementations where geometry-stage point-size writes are not supported.

### Design-based pruning

- The family keeps one leaf per targeted built-in behavior instead of generating a large parameter matrix.
- Only `primitive_id_in` has a primitive-restart companion leaf, because primitive restart specifically changes input-primitive
  formation and therefore can affect `gl_PrimitiveIDIn`.
- The HLSL path is limited to `outside_block.position`; adding HLSL variants for every GLSL built-in leaf would duplicate the core
  image tests rather than clarify a distinct behavior.

## Key Takeaways

- `geometry.builtin_variable` is a compact set of built-in-variable image tests, not a broad geometry-shader matrix.
- The `in_block` leaves validate GLSL interface-block behavior for point size and primitive IDs.
- `primitive_id_in_restarted` is the only indexed case, and its purpose is specifically to check `gl_PrimitiveIDIn` across a
  primitive-restart boundary.
- `outside_block.position` covers a mixed GLSL/HLSL path where the geometry shader expresses position through `SV_POSITION`.
- All leaves share the same render/copyback/reference-image comparison infrastructure; use `## Failure Meaning` to distinguish
  leaf-specific built-in failures from shared-path failures.

## Source Reference Appendix

| Topic | Source link |
|-------|-------------|
| Primary source file | [vktGeometryBuiltinVariableGeometryShaderTests.cpp](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L1) |
| Built-in mode enum | [VariableTest](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L64-L70) |
| Test-instance constructor and topology selection | [BuiltinVariableRenderTestInstance::BuiltinVariableRenderTestInstance()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L91-L101) |
| Fixed positions, attributes, and restart indices | [BuiltinVariableRenderTestInstance::genVertexAttribData()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L103-L132) |
| Index-buffer creation | [BuiltinVariableRenderTestInstance::createIndicesBuffer()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L134-L159) |
| Draw command selection | [BuiltinVariableRenderTestInstance::drawCommand()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L161-L170) |
| Feature support checks | [BuiltinVariableRenderTest::checkSupport()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L194-L200) |
| Shader generation | [BuiltinVariableRenderTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L202-L419) |
| Test instance creation | [BuiltinVariableRenderTest::createInstance()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L421-L424) |
| Registration | [createBuiltinVariableGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp#L428-L448) |
| Shared render and compare flow | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L202) |
| Reference-image comparison helper | [compareWithFileImage()](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L412-L425) |
| Default mustpass evidence | [geometry.txt](../../../mustpass/main/vk-default/geometry.txt#L15-L19) |
