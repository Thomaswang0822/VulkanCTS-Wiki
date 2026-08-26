## Overview

**Core question:** Does a graphics pipeline deliver a producer stage's user-defined interface values to the intended inputs of later stages when declarations differ in allowed or deliberately mismatched ways?

- This page covers the `interface_matching` test family implemented by [`vktPipelineInterfaceMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L1358).
- `vector_length` and `decoration_mismatch` generate graphics-pipeline cases over stage arrangements and declaration forms. `misc.skip_output_variable` supplies one focused location-based case.
- The source also registers the non-VulkanSC `shader_layout_component_matching` test family, but delegates its implementation to [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215).
- The sections below separate the generated dimensions from the four behaviors, then follow the draw and readback path that determines the CTS result.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A user-defined output in one graphics shader stage must interface-match the corresponding input in a later stage. Matching depends on decorations and types. The specification permits a longer output vector to match a shorter input vector when `maintenance4` is enabled, and permits an output that no later stage reads ([Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L181)).
- `Location` identifies a four-component interface slot; `Component` identifies positions within that slot. Component packing changes with 16-, 32-, and 64-bit values ([Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L194-L258)).

## Registration Hierarchy

```text
pipeline.monolithic.interface_matching
├── vector_length
├── decoration_mismatch
├── shader_layout_component_matching (registration only; non-VulkanSC)
└── misc
```

The pipeline mustpass configuration is split across seven construction-mode files under [`mustpass/main/vk-default/pipeline/`](../../../mustpass/main/vk-default/pipeline/): monolithic, pipeline-library, fast-linked-library, and four shader-object variants (linked or unlinked, with binary or SPIR-V shader sources). Each contains 1,589 `interface_matching` leaves, for 11,123 leaves total. Per construction mode, those leaves comprise 972 `vector_length` cases, 360 `decoration_mismatch` cases, 256 delegated `shader_layout_component_matching` cases, and the single `misc.skip_output_variable` case.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Interface behavior | `VECTOR_LENGTH`, `DECORATION_MISMATCH`, `SKIP_OUTPUT_VARIABLE` | Selects the generated vector rule, decoration rule, or focused skipped-output case. | [`TestType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L64) |
| Vector type | `VEC2` through `VEC4`, `IVEC2` through `IVEC4`, `UVEC2` through `UVEC4` | Selects scalar kind and output/input component counts for `vector_length`. | [`VecType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L66-L77) |
| Decoration | `NONE`, `FLAT`, `NO_PERSPECTIVE`, `COMPONENT0` | Forms the producer and consumer decoration pair in `decoration_mismatch`. | [`DecorationType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L79-L85) |
| Stage arrangement | Nine `PipelineType` values from `VERT_OUT_FRAG_IN` to `VERT_TESC_TESE_GEOM_OUT_FRAG_IN` | Places the producer-consumer relationship across vertex, tessellation, geometry, and fragment stages. | [`PipelineType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L87-L106) |
| Declaration form | `LOOSE_VARIABLE`, `MEMBER_OF_BLOCK`, `MEMBER_OF_STRUCTURE`, `MEMBER_OF_ARRAY_OF_STRUCTURES`, `MEMBER_OF_STRUCTURE_IN_BLOCK`, `MEMBER_OF_ARRAY_OF_STRUCTURES_IN_BLOCK` | Checks matching through direct declarations and nested aggregate forms. | [`DefinitionType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L108-L116) |
| Pipeline construction | monolithic, pipeline-library, fast-linked-library, and shader-object mustpass roots | Exercises the same interface behavior through different construction paths. | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L118-L131), [mustpass files](../../../mustpass/main/vk-default/pipeline/) |

The generator retains vector pairs only when the output has at least as many components as the input. It uses nine stage arrangements, six declaration forms, three scalar kinds, and the valid output/input vector-size combinations. The decoration generator uses eight explicit pairs and limits `COMPONENT0` to loose variables and block members ([generation loops](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1257-L1343)).

## Behavior Parameters

The primary behavioral axis is the registered branch below `interface_matching`. Each branch changes the interface property under test rather than only its declaration configuration.

### vector_length - Longer producer vectors

This branch checks the `maintenance4` rule that allows an output vector with more components to match an input vector with the same component type and fewer components. Generated consumer code checks every declared input component against the producer's known value; it never asks the consumer to read a component it did not declare.

### decoration_mismatch - Producer and consumer decorations

This branch changes the input and output interpolation or component decorations while holding the vector type at `vec4`. It tests mismatched pairs involving `NONE`, `FLAT`, `NO_PERSPECTIVE`, and `COMPONENT0`; the generated consumer comparison reports whether the received value follows the interface declaration path.

### shader_layout_component_matching - Packed component layouts

This delegated test family covers component-decorated layouts across stage flows, declaration modes, bit widths, location counts, and packing patterns. It remains a registration-only area on this page; readers should use the rewritten [component-layout page](ShaderComponentDecoratedLayoutMatching.md) for its implementation details.

### misc.skip_output_variable - Omitted location-1 input

The vertex shader writes `v0`, `v1`, and `v2` at locations 0, 1, and 2. The fragment shader declares inputs only at locations 0 and 2 and adds them. The test checks that location 2 still supplies `v2`, as interface matching uses locations rather than compacts variables around the omitted location-1 input ([generated shader pair](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1208-L1238)).

## Shader Analysis

The source generates the producer and consumer stages from the selected vector, decoration, stage, and declaration parameters. The representative below follows the geometry-to-fragment path for a loose `vec4`: the geometry output carries `Component 0`, while the fragment input uses the same location with the generated flat interpolation qualifier. The fragment-side comparison is generated by [`genInVerification()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L862-L894); the stage selection and declarations come from [`InterfaceMatchingTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L466-L838).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.interface_matching.decoration_mismatch.out_component0_in_none_loose_variable_vert_geom_out_frag_in
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `decoration_mismatch`, `out_component0_in_none` | The geometry producer is declared at `Location 0, Component 0`; the fragment consumer is declared at `Location 0` with the generated flat interpolation qualifier and no `Component` decoration. |
| `loose_variable`, `vert_geom_out_frag_in` | The interface is a direct variable between the geometry and fragment stages. The vertex stage is a passthrough, the geometry stage produces the payload, and the fragment stage verifies it. |
| `vec4` / `vec4` | The producer writes `(-4.0, -9.0, 3.0, 7.0)` and the consumer checks all four components. |
| `shader_object_linked_binary` | The generated GLSL is compiled for the linked-binary construction path; the shader interface itself is the same generated case. |

#### Purpose

This shader pair checks that a geometry-stage output and fragment-stage input with the selected decoration mismatch still carry the intended four-component value across `Location 0`. A successful comparison paints the fragment result as one, which the host later observes in the rendered image.

#### Structural Design

| Stage | Interface role | Payload and control flow |
|-------|----------------|--------------------------|
| Geometry | Producer | Declare `looseVariable` at location 0/component 0, store the fixed `vec4`, emit three vertices as a triangle strip. |
| Fragment | Consumer and oracle | Read location 0, compare x/y/z/w against the producer constants, multiply the four Boolean results, broadcast the scalar verdict to `fragColor`. |
| Host | Result observer | Render to an 8×8 `VK_FORMAT_R8G8B8A8_UNORM` attachment, copy it to a host-visible buffer, and require every pixel to be approximately `(1, 1, 1, 1)` for the selected shader check. |

#### Shader Code

##### Geometry Shader

```glsl
#version 450
#extension GL_EXT_geometry_shader : require
layout(triangles) in;
layout(triangle_strip, max_vertices=3) out;
/// The geometry stage is the producer for this case: its location-0 output
/// carries the fixed vec4 payload into the fragment-stage interface.
layout(location = 0, component = 0) out vec4 looseVariable;
void main(void)
{
  /// Repeat the payload for each emitted vertex so the interface check is
  /// independent of which rasterized fragment is sampled.
  looseVariable = vec4(-4.0, -9.0, 3.0, 7.0);
  gl_Position = vec4( 1.0, -1.0, 0.0, 1.0);
  EmitVertex();
  looseVariable = vec4(-4.0, -9.0, 3.0, 7.0);
  gl_Position = vec4(-1.0,  1.0, 0.0, 1.0);
  EmitVertex();
  looseVariable = vec4(-4.0, -9.0, 3.0, 7.0);
  gl_Position = vec4(-1.0, -1.0, 0.0, 1.0);
  EmitVertex();
  EndPrimitive();
}
```

##### Fragment Shader

```glsl
#version 450
layout(location = 0) out vec4 fragColor;
/// This location-0 input is the geometry stage's vec4 producer. The selected
/// case leaves the fragment declaration without a Component decoration.
layout(location = 0) in flat vec4 looseVariable;
void main(void)
{
  /// Each comparison contributes one; multiplication makes any mismatched
  /// component turn the rendered result into zero.
  float result = 0.0;
  result = float(abs(looseVariable.x - -4.0) < 0.001) *
\t\t   float(abs(looseVariable.y - -9.0) < 0.001) *
\t\t   float(abs(looseVariable.z - 3.0) < 0.001) *
\t\t   float(abs(looseVariable.w - 7.0) < 0.001);
  fragColor = vec4(result);
}
```

#### Additional Info

- The vertex stage is intentionally not shown: for `VERT_GEOM_OUT_FRAG_IN`, `initPrograms()` leaves it as a passthrough `inPosition`/`gl_Position` stage; the geometry stage is the first stage that owns the tested output interface.
- `genInVerification()` uses the absolute-error expression for floating-point vectors, so the source-level `< 0.001` threshold is preserved in the reconstructed fragment shader.
- The runtime renders a single triangle to an 8×8 color attachment and rejects any byte outside the source thresholds (`red <= 2` or another channel `< 253`) in `MiscInterfaceMatchingTestInstance`'s corresponding validation path.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Decoration pair | `NONE`, `FLAT`, `NO_PERSPECTIVE`, and `COMPONENT0` alter interpolation/component qualifiers on the generated producer and consumer declarations; `COMPONENT0` is restricted to loose variables and block members. | [`getDecorationData()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L968-L979) / [decoration matrix](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1315-L1342) |
| Pipeline type | The producer/consumer relationship moves among vertex, tessellation-control, tessellation-evaluation, geometry, and fragment stages; intermediate stages use arrays and flat inputs where required. | [`getPipelineData()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L982-L1005) / [stage builders](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L647-L838) |
| Definition type | The direct variable becomes a block member, structure member, array-of-structures member, or nested block aggregate, changing the declaration and access path while preserving the selected interface payload. | [declaration switch](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L496-L633) |
| Vector type and length | `vec2`–`vec4`, `ivec2`–`ivec4`, and `uvec2`–`uvec4` select constants and comparison operators; vector-length generation retains only producer sizes at least as large as consumer sizes. | [`getVecData()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L950-L966) / [vector matrix](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1257-L1313) |

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
; Bound: 32
; Schema: 0
               OpCapability Geometry
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %looseVariable %_
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_geometry_shader"
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpName %main "main"
               OpName %looseVariable "looseVariable"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %looseVariable Location 0
               OpDecorate %looseVariable Component 0
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
%looseVariable = OpVariable %_ptr_Output_v4float Output
   %float_n4 = OpConstant %float -4
   %float_n9 = OpConstant %float -9
    %float_3 = OpConstant %float 3
    %float_7 = OpConstant %float 7
         %14 = OpConstantComposite %v4float %float_n4 %float_n9 %float_3 %float_7
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_1 = OpConstant %float 1
   %float_n1 = OpConstant %float -1
    %float_0 = OpConstant %float 0
         %26 = OpConstantComposite %v4float %float_1 %float_n1 %float_0 %float_1
         %28 = OpConstantComposite %v4float %float_n1 %float_1 %float_0 %float_1
         %30 = OpConstantComposite %v4float %float_n1 %float_n1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %looseVariable %14
         %27 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %27 %26
               OpEmitVertex
               OpStore %looseVariable %14
         %29 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %29 %28
               OpEmitVertex
               OpStore %looseVariable %14
         %31 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %31 %30
               OpEmitVertex
               OpEndPrimitive
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
; Bound: 57
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %looseVariable %fragColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %result "result"
               OpName %looseVariable "looseVariable"
               OpName %fragColor "fragColor"
               OpDecorate %looseVariable Flat
               OpDecorate %looseVariable Location 0
               OpDecorate %fragColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %float_0 = OpConstant %float 0
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%looseVariable = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
   %float_n4 = OpConstant %float -4
%float_0_00100000005 = OpConstant %float 0.00100000005
       %bool = OpTypeBool
    %float_1 = OpConstant %float 1
     %uint_1 = OpConstant %uint 1
   %float_n9 = OpConstant %float -9
     %uint_2 = OpConstant %uint 2
    %float_3 = OpConstant %float 3
     %uint_3 = OpConstant %uint 3
    %float_7 = OpConstant %float 7
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %fragColor = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
     %result = OpVariable %_ptr_Function_float Function
               OpStore %result %float_0
         %16 = OpAccessChain %_ptr_Input_float %looseVariable %uint_0
         %17 = OpLoad %float %16
         %19 = OpFSub %float %17 %float_n4
         %20 = OpExtInst %float %1 FAbs %19
         %23 = OpFOrdLessThan %bool %20 %float_0_00100000005
         %25 = OpSelect %float %23 %float_1 %float_0
         %27 = OpAccessChain %_ptr_Input_float %looseVariable %uint_1
         %28 = OpLoad %float %27
         %30 = OpFSub %float %28 %float_n9
         %31 = OpExtInst %float %1 FAbs %30
         %32 = OpFOrdLessThan %bool %31 %float_0_00100000005
         %33 = OpSelect %float %32 %float_1 %float_0
         %34 = OpFMul %float %25 %33
         %36 = OpAccessChain %_ptr_Input_float %looseVariable %uint_2
         %37 = OpLoad %float %36
         %39 = OpFSub %float %37 %float_3
         %40 = OpExtInst %float %1 FAbs %39
         %41 = OpFOrdLessThan %bool %40 %float_0_00100000005
         %42 = OpSelect %float %41 %float_1 %float_0
         %43 = OpFMul %float %34 %42
         %45 = OpAccessChain %_ptr_Input_float %looseVariable %uint_3
         %46 = OpLoad %float %45
         %48 = OpFSub %float %46 %float_7
         %49 = OpExtInst %float %1 FAbs %48
         %50 = OpFOrdLessThan %bool %49 %float_0_00100000005
         %51 = OpSelect %float %50 %float_1 %float_0
         %52 = OpFMul %float %43 %51
               OpStore %result %52
         %55 = OpLoad %float %result
         %56 = OpCompositeConstruct %v4float %55 %55 %55 %55
               OpStore %fragColor %56
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test creates a color image, a host-visible result buffer, and a command buffer. It transitions the image to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, renders a single triangle, and copies the image to the result buffer ([draw and copy](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L354-L383)).
- For the generated vector and decoration cases, the fragment-stage check writes success into two selected pixels. After queue completion and allocation invalidation, the host passes only when both selected red channels exceed 254 ([host check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L385-L400)).
- For `skip_output_variable`, the host scans the full image after the copy. It expects each pixel to encode `(0, 1, 1, 1)` within the byte thresholds in the source and logs the image on failure ([full-image check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1160-L1176)).
- The support check requires the selected pipeline-construction path, requests `VK_KHR_maintenance4` for unequal vector lengths, and rejects stage arrangements without required tessellation or geometry features ([support checks](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L946)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vector_length` | Vector interface matching with `maintenance4`, declaration-form handling, or stage-interface propagation produced a failed shader check. |
| `decoration_mismatch` | Decoration matching or pipeline-library interpolation-decoration handling produced a failed shader check. |
| `shader_layout_component_matching` | Component and location packing, width-specific layout handling, or stage-interface matching in the delegated family failed. |
| `misc.skip_output_variable` | The implementation did not preserve location-based matching when the fragment shader omitted the location-1 input. |

### Cause Analysis

#### Vector interface matching and declaration propagation

**Possible failure symptoms:** One or both selected red channels are at most 254, so the generated input-side comparison evaluated false.

**Possible implementation causes:** The implementation may reject or mislink the `maintenance4` longer-output/shorter-input rule, propagate the wrong component values across a stage boundary, or handle one of the tested block, structure, or array declaration forms incorrectly. The specification permits the vector relationship only with `maintenance4` enabled ([interface rule](../../../../vulkan-docs/src/chapters/interfaces.adoc#L140-L158)); source-level investigation is needed to localize a particular failing declaration form.

#### Decoration matching and library construction

**Possible failure symptoms:** The generated decoration case fails its shader-side value check and the host reports a failed selected pixel.

**Possible implementation causes:** The compiler or linker may apply a decoration relationship incorrectly, or a separate graphics-pipeline-library path may handle differing interpolation decorations incorrectly. The test skips relevant library cases when the implementation does not support `graphicsPipelineLibraryIndependentInterpolationDecoration` ([source gate](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L917)); the specification also defines the limit's effect on matches across the pre-rasterization and fragment boundary ([rule](../../../../vulkan-docs/src/chapters/interfaces.adoc#L168-L176)).

#### Component layout matching in the delegated family

**Possible failure symptoms:** The delegated family reports a result that differs from its expected color.

**Possible implementation causes:** A failure can involve location or component-slot assignment, width-specific packing, or interface matching after layout construction. The specification assigns component slots differently for 16-, 32-, and 64-bit values ([assignment rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L206-L248)). This parent source only registers the family, so source-level investigation in the delegated implementation is needed to identify the failing flow or packing pattern.

#### Omitted output-variable handling

**Possible failure symptoms:** The `misc.skip_output_variable` image contains a pixel outside the expected `(0, 1, 1, 1)` byte thresholds, often indicating that `v2` did not arrive as the location-2 value.

**Possible implementation causes:** The implementation may compact declared interface variables by declaration order, instead of matching the fragment input at location 2 to the producer output at location 2. Vulkan permits a shader to write outputs that the subsequent stage does not declare or read ([interface rule](../../../../vulkan-docs/src/chapters/interfaces.adoc#L178-L181)); source-level investigation is needed to separate compiler interface lowering from later pipeline linking.

## Case Pruning

### Requirement-based pruning

- Unequal vector lengths require `VK_KHR_maintenance4`.
- Tessellation and geometry stage arrangements require `tessellationShader` and `geometryShader`, respectively.
- Pipeline-library cases involving `FLAT` or `NO_PERSPECTIVE` skip when `graphicsPipelineLibraryIndependentInterpolationDecoration` is unavailable.
- `shader_layout_component_matching` is excluded from Vulkan SC by its registration guard.

### Design-based pruning

- The vector matrix drops combinations where the output vector is shorter than the input vector because they do not exercise the intended permitted longer-output relationship.
- The source omits one tessellation/geometry stage arrangement because its comment identifies it as similar to another arrangement already covered ([stage list](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1263-L1273)).
- `COMPONENT0` decoration pairs use only `LOOSE_VARIABLE` and `MEMBER_OF_BLOCK`, matching the source's focused matrix boundary.

## Key Takeaways

- The family tests interface matching as a rendered, shader-observed property rather than relying on pipeline creation success alone.
- `vector_length` isolates the `maintenance4` type exception, while `decoration_mismatch` varies interface decorations across the same stage and declaration matrix.
- `skip_output_variable` proves that a skipped declaration does not renumber later `Location`-based inputs.
- Component-layout behavior belongs to the delegated family; this page records its registration boundary and the shared interface rules that give it context.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter enumerations and `TestParams` | [`vktPipelineInterfaceMatchingTests.cpp#L57-L133`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L133) | Defines the generated case dimensions. |
| Generated input comparison | [`genInVerification()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L862-L894) | Defines integer and floating-point shader-side checks. |
| Feature and construction gates | [`InterfaceMatchingTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L946) | Applies extension and stage requirements. |
| General result readback | [draw, copy, and selected-pixel check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L354-L400) | Shows the regular host-visible pass condition. |
| Skipped-output case | [`MiscInterfaceMatchingTestCase`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1071-L1249) | Generates and validates `skip_output_variable`. |
| Registration | [`createInterfaceMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1254-L1357) | Registers the four direct branches. |
| Delegated component-layout implementation | [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215) | Owns the registered component-layout family. |
