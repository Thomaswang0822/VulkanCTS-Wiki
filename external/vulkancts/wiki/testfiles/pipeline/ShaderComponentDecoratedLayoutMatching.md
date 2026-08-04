## Overview

**Core question:** Do graphics pipeline stages preserve values when matching shader interfaces use `Component` decorations to pack scalars and vectors into locations?

- This page covers the implementation behind `pipeline.<construction>.interface_matching.shader_layout_component_matching`, registered by [`createShaderCompDecorLayoutMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1249).
- The test generates GLSL for four stage flows and compares the rendered image with an exact reference color.
- It varies declaration mode, scalar width, location extent, starting location, and component pattern. The same implementation is exercised under the seven pipeline-construction mustpass files listed in the source appendix.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A shader interface `Location` identifies a four-component slot. A `Component` decoration selects a component within that slot. Vulkan defines the slot consumption rules for 16-bit, 32-bit, and 64-bit interface values in [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L194-L248).
- The matching rule applies independently between adjacent graphics stages. An intermediate stage must declare compatible inputs and outputs before a value can reach the fragment shader.
- The test uses `flat` interface variables. The values are therefore copied as discrete data rather than being interpreted as ordinary interpolated floating-point varyings.

## Registration Hierarchy

```text
pipeline.monolithic.interface_matching.shader_layout_component_matching
├── vert_frag
├── vert_geom_frag
├── vert_tesc_tese_frag
└── vert_tesc_tese_geom_frag
```

The same family is dispatched under `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_linked_binary`, `shader_object_unlinked_binary`, `shader_object_linked_spirv`, and `shader_object_unlinked_spirv` construction roots. The registration tree above uses the monolithic path because the validator requires one concrete canonical root.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Stage-flow intermediate node | `vert_frag`, `vert_geom_frag`, `vert_tesc_tese_frag`, `vert_tesc_tese_geom_frag` | Selects which adjacent interfaces carry the decorated values. | [`Flow` constants](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1158-L1162) |
| Declaration mode | `loose_var`, `in_block` | Chooses standalone interface variables or interface blocks. `in_struct` is not registered. | [`modes`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1175-L1178) |
| Scalar width | `float16`, `float32`, `float64` | Selects GLSL types and the number of component/location slots consumed. | [`widths`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1179-L1179) |
| Location count | `single_location`, `multiple_locations` | Uses no array extent or an extent of three for the decorated interface variables. | [`locationCounts`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1190-L1190) |
| Starting location | `1` through `4` cyclically | Places the tested interface away from location zero and changes across generated cases. | [`Layout` construction](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1215-L1223) |
| Component pattern | `scalar_scalar_scalar_scalar`, `scalar_scalar_vec2`, `scalar_vec2_scalar`, `vec2_scalar_scalar`, `scalar_vec3`, `vec3_scalar`, `vec2_vec2`, `scalar_scalar`, `vec2` | Packs scalar and vector values into component positions. The first seven patterns run at 16 and 32 bits; the last two run at 64 bits. | [`componentSeries`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1180-L1188) |

Each registered leaf has the form `<flow>.<mode>.<width>.<location_count>.<component_pattern>`, for example `vert_frag.loose_var.float32.single_location.scalar_vec2`.

## Behavior Parameters

The primary behavioral axis is the stage-flow intermediate node. It changes which interface transfers and stage-specific transformations the implementation must preserve.

### `vert_frag` - direct vertex-to-fragment matching

The vertex shader writes the packed values and the fragment shader consumes them directly. This is the shortest path for checking declaration matching and final reconstruction.

### `vert_geom_frag` - geometry pass-through

The geometry shader reads each decorated value, multiplies it by `2.0`, and emits three vertices. The vertex shader starts at half the direct-path value so that the fragment shader still observes the same reference color.

### `vert_tesc_tese_frag` - tessellation transfer

The tessellation-control shader copies each invocation's decorated values. The tessellation-evaluation shader combines the three control-point values and divides by `1.5`; the vertex shader compensates by starting at half the direct-path value.

### `vert_tesc_tese_geom_frag` - tessellation plus geometry

This flow applies both intermediate-stage paths. The stage sequence must preserve matching through tessellation and geometry while maintaining the adjusted values used by the final fragment check.

## Shader Analysis

The test is shader-heavy because every leaf generates stage-specific GLSL. The representative case below shows the core interface declaration and producer behavior. The full implementation also generates tessellation and geometry variants through [`ShaderGen`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L130-L243).

### Representative Shader Walkthrough 1

#### Representative CTS path

`dEQP-VK.pipeline.pipeline_library.interface_matching.shader_layout_component_matching.vert_frag.loose_var.float32.single_location.scalar_vec3`

#### Structural Design

| Shader phase | What the generated code does |
|---|---|
| Vertex input | Reads `pos` at location 0 and writes `o0` at component 0 plus `o1` at component 1 of location 1. |
| Position | Converts the input rectangle position into `gl_Position`. |
| Interface payload | Writes `0.125` to the scalar and `(0.25, 0.5, 1.0)` to the vector. |
| Fragment use | Reconstructs the four reference color components from matching decorated inputs. |

#### Purpose

This case checks adjacent vertex-to-fragment matching with one scalar followed by one `vec3` inside one 32-bit location.

#### Parameter Values Chosen

| Parameter | Value |
|---|---|
| Flow | `vert_frag` |
| Mode | `loose_var` |
| Width | `float32` |
| Location count | `single_location` |
| Component pattern | `scalar_vec3` |

#### Parameter Variation Summary

Changing the width changes the GLSL type and feature requirements. Changing the component pattern changes which components the fragment shader consumes. Adding geometry or tessellation inserts stage interfaces and value compensation, while `in_block` wraps the same decorated members in interface blocks.

#### Additional Info

- The source generator filters component patterns by width instead of producing invalid 64-bit combinations.
- The test uses a `VK_FORMAT_R32G32B32A32_SFLOAT` color attachment and a 16 x 16 framebuffer, so the shader result becomes an exact image comparison.

#### Shader Code

```glsl
#version 450
layout(location = 0) in vec4 pos;
layout(location = 1, component = 0) out flat float o0;
layout(location = 1, component = 1) out flat vec3 o1;
void main()
{
    gl_Position = vec4(pos.xy, 0.0, 1.0);
    o0 = 0.125;
    o1 = vec3(0.25, 0.5, 1.0);
}
```

The source generator emits the declarations through [`genLayout()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L430-L454), writes the vertex payload in [`ShaderGen<Vert>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L456-L520), and constructs the fragment output in [`ShaderGen<Frag>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L675-L717). The exact registered leaf names are generated from the `Components::testName()` helper.

#### SPIR-V

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
; Bound: 37
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %pos %o0 %o1
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %pos "pos"
               OpName %o0 "o0"
               OpName %o1 "o1"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %pos Location 0
               OpDecorate %o0 Flat
               OpDecorate %o0 Location 1
               OpDecorate %o0 Component 0
               OpDecorate %o1 Flat
               OpDecorate %o1 Location 1
               OpDecorate %o1 Component 1
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
%_ptr_Input_v4float = OpTypePointer Input %v4float
        %pos = OpVariable %_ptr_Input_v4float Input
    %v2float = OpTypeVector %float 2
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_float = OpTypePointer Output %float
         %o0 = OpVariable %_ptr_Output_float Output
%float_0_125 = OpConstant %float 0.125
    %v3float = OpTypeVector %float 3
%_ptr_Output_v3float = OpTypePointer Output %v3float
         %o1 = OpVariable %_ptr_Output_v3float Output
 %float_0_25 = OpConstant %float 0.25
  %float_0_5 = OpConstant %float 0.5
         %36 = OpConstantComposite %v3float %float_0_25 %float_0_5 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpLoad %v4float %pos
         %20 = OpVectorShuffle %v2float %19 %19 0 1
         %23 = OpCompositeExtract %float %20 0
         %24 = OpCompositeExtract %float %20 1
         %25 = OpCompositeConstruct %v4float %23 %24 %float_0 %float_1
         %27 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %27 %25
               OpStore %o0 %float_0_125
               OpStore %o1 %36
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` verifies the pipeline construction mode, color attachment format features, tessellation and geometry features, and the selected 16-bit or 64-bit shader feature requirements. See [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L321-L357).
- `initPrograms()` generates the source for each stage in the selected flow and adds it to the CTS source collection. The implementation creates shader modules, a render pass, a graphics pipeline, a host-visible vertex buffer, and a host-visible result buffer.
- `iterate()` draws six vertices as two triangles into a 16 x 16 `VK_FORMAT_R32G32B32A32_SFLOAT` image, copies the image to the result buffer, submits the command buffer, and waits for completion.
- [`verifyResult()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L943-L966) scans every pixel. It passes only when each pixel equals `tcu::Vec4(0.125f, 0.25f, 0.5f, 1.0f)`; otherwise it reports the first mismatch and logs the result image.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vert_frag` | Direct producer-to-consumer location/component matching or fragment reconstruction failure. |
| `vert_geom_frag` | Geometry-stage interface matching or pass-through failure, or a direct-path failure. |
| `vert_tesc_tese_frag` | Tessellation interface matching or interpolation compensation failure, or a direct-path failure. |
| `vert_tesc_tese_geom_frag` | Interaction among tessellation and geometry interface transfers, or a failure shared by shorter flows. |

### Cause Analysis

#### Direct interface matching or fragment reconstruction

**Possible failure symptoms:** One or more pixels differ from `(0.125, 0.25, 0.5, 1.0)`, and the first mismatch may show a shifted, missing, or otherwise incorrect component value.

**Possible implementation causes:** The adjacent shader interfaces may disagree about `Location`, `Component`, type width, array extent, or block member layout. A generator or compiler may also lower the decorated declarations incorrectly. The final image does not identify which adjacent interface caused the mismatch, so source-level or intermediate-shader investigation is needed.

#### Geometry-stage transfer

**Possible failure symptoms:** `vert_geom_frag` fails while the direct flow passes, or the output values show the wrong geometry-stage scaling.

**Possible implementation causes:** The geometry input/output declarations may not match, the stage may copy the wrong array element, or the emitted primitive data may not preserve the intended decorated value. The failure can also come from shared vertex, fragment, or render-pass logic.

#### Tessellation-stage transfer

**Possible failure symptoms:** `vert_tesc_tese_frag` fails while `vert_frag` passes, or the fragment value changes in a way consistent with incorrect control-point combination or compensation.

**Possible implementation causes:** Tessellation-control and tessellation-evaluation interfaces may disagree, the evaluation shader may combine the wrong invocation values, or a location/component array extent may be lowered incorrectly. The final pixel cannot distinguish interface matching from the value transformation itself.

#### Combined tessellation and geometry transfer

**Possible failure symptoms:** Only `vert_tesc_tese_geom_frag` fails, or its output differs from the shorter tessellation and geometry flows.

**Possible implementation causes:** The combined stage sequence may expose an interaction between tessellation output, geometry input, geometry emission, and fragment input. The test result alone cannot isolate the failing boundary; inspect generated shaders and stage interfaces.

## Case Pruning

### Requirement-based pruning

- The color format must support color attachment and transfer-source use.
- Tessellation flows require `tessellationShader`; geometry flows require `geometryShader`.
- `float16` requires both `shaderFloat16` and `storageInputOutput16`; `float64` requires `shaderFloat64`.
- The test checks pipeline-construction support before creating the pipeline. Unsupported devices report `NotSupportedError` rather than a test failure.

### Design-based pruning

- `VariableInStruct` is present in the `Modes` enum but its registration line is commented out.
- Component patterns are filtered by width. Patterns requiring 16 or 32-bit values do not run for 64-bit widths, and only `scalar_scalar` and `vec2` run at 64 bits.
- The generator uses four component positions and two location-count forms instead of enumerating unrelated interface declarations.

## Key Takeaways

- The test varies the stage flow as its primary behavior axis, then stresses the same matching rule with different declaration modes, widths, locations, and component patterns.
- A `Component` decoration is meaningful together with its `Location` and type width. A 64-bit component consumes more interface slots than a 32-bit component.
- The final color comparison detects the observable result of the whole graphics path. It cannot, by itself, assign a failure to one particular stage boundary.
- Tessellation and geometry flows adjust generated values so intermediate-stage processing still reaches the same reference color.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration entrypoint | [`createShaderCompDecorLayoutMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1249) | Builds the four stage-flow families and the parameter matrix. |
| Parent registration | [`vktPipelineInterfaceMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1340-L1348) | Adds this family below `interface_matching`. |
| Layout declaration generation | [`ShaderGen::genLayout()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L404-L454) | Emits `Location`, `Component`, type, array, and block syntax. |
| Stage generators | [`ShaderGen<Vert>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L456-L520), [`ShaderGen<Tesc>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L522-L576), [`ShaderGen<Tese>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L577-L634), [`ShaderGen<Geom>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L635-L673), [`ShaderGen<Frag>::genCode()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L675-L717) | Defines the generated data flow. |
| Support checks | [`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L321-L357) | Defines feature and format gating. |
| Rendering and readback | [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L968-L1057) | Creates resources, submits the draw, copies the image, and checks the result. |
| Mustpass coverage | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt), [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt), [`fast-linked-library.txt`](../../../mustpass/main/vk-default/pipeline/fast-linked-library.txt), [`shader-object-linked-binary.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-linked-binary.txt), [`shader-object-unlinked-binary.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-unlinked-binary.txt), [`shader-object-linked-spirv.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-linked-spirv.txt), [`shader-object-unlinked-spirv.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt) | Each contains 256 leaves for this family, for 1,792 leaves in total. |
| Vulkan specification | [Interface matching and Location/Component rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L120-L248) | Defines the interface contract that the generated declarations exercise. |
