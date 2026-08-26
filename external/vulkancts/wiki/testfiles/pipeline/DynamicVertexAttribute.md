## Overview

**Core question:** Does dynamic vertex-input state map color location 7 to the correct bytes after an earlier draw configured the same record layout for location 1?

[`vktPipelineDynamicVertexAttributeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L135-L420) implements the `dynamic_vertex_attribute` test family in the pipeline category. Its one executable test case leaf, `nonsequential`, creates two graphics pipelines with `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT`, then supplies the active binding and attribute descriptions with `vkCmdSetVertexInputEXT` before each draw. The first draw uses a color input at location 1; the second uses location 7 and completely covers the first draw with the same geometry. The final comparison therefore directly checks the location-7 draw, not both sparse locations independently.

The pipeline dispatcher adds this family for each normal pipeline-construction group ([registration](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L113)). The mustpass lists contain one corresponding leaf for monolithic, both library constructions, and all four shader-object construction variants.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

### Dynamic vertex input and locations

A graphics pipeline can declare `VK_DYNAMIC_STATE_VERTEX_INPUT_EXT` and leave its static vertex-input create info empty. Before a draw, `vkCmdSetVertexInputEXT` provides binding and attribute descriptions. An attribute description maps a shader `location` to a binding, format, and byte offset; the binding supplies stride and input rate. Vulkan defines the dynamic command and state requirement in [Dynamic Vertex Input](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L258-L270), and defines the fetch address inputs in [Vertex Input Address Calculation](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1076-L1130).

A location selects an attribute description, not a position in a packed record. This test places `position` at location 0 and color at either location 1 or location 7. Both colors have `VK_FORMAT_R32G32B32A32_SFLOAT` and begin after the position field, at byte offset 16.

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_vertex_attribute
└── nonsequential
```

The factory registers `dynamic_vertex_attribute.nonsequential` with fixed `numInstances = 16u` and locations `{1u, 7u}` ([factory](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L565-L575)). The concrete mustpass leaves are:

| Construction type | Mustpass leaf |
|---|---|
| Monolithic | `dEQP-VK.pipeline.monolithic.dynamic_vertex_attribute.nonsequential` |
| Pipeline library | `dEQP-VK.pipeline.pipeline_library.dynamic_vertex_attribute.nonsequential` |
| Fast-linked library | `dEQP-VK.pipeline.fast_linked_library.dynamic_vertex_attribute.nonsequential` |
| Shader object, unlinked SPIR-V | `dEQP-VK.pipeline.shader_object_unlinked_spirv.dynamic_vertex_attribute.nonsequential` |
| Shader object, unlinked binary | `dEQP-VK.pipeline.shader_object_unlinked_binary.dynamic_vertex_attribute.nonsequential` |
| Shader object, linked SPIR-V | `dEQP-VK.pipeline.shader_object_linked_spirv.dynamic_vertex_attribute.nonsequential` |
| Shader object, linked binary | `dEQP-VK.pipeline.shader_object_linked_binary.dynamic_vertex_attribute.nonsequential` |

## Parameter Dimensions and Observed Values

| Dimension | Fixed value or alternatives | Observed effect |
|---|---|---|
| Test case leaf | `nonsequential` | Configures two sparse color locations in one render pass; the later location-7 draw determines the expected covered pixels. |
| Color locations | `1u`, `7u` | Each vertex shader declares one of these locations. |
| Position location | `0u` | Both draws fetch position from this location. |
| Record layout | `VertexInfo { vec4 position; vec4 color; }` | Position starts at offset 0; color starts at offset 16. |
| Vertex format | `VK_FORMAT_R32G32B32A32_SFLOAT` | Both attributes fetch four 32-bit floats. |
| Binding | `0u`, stride `sizeof(VertexInfo)`, vertex rate | Supplies the record layout for each draw. |
| Vertices and target | 6 vertices per draw; 32x32 `VK_FORMAT_R8G8B8A8_UNORM` image | Produces an observable color result. |
| Construction type | Monolithic, library, or shader-object variants | Changes CTS construction machinery, not the sparse-location data model. |

## Behavior Parameters

The behavior parameter is the single executable **test case leaf**, `nonsequential`. Its two draws form one operation: change the dynamic attribute description from location 1 to location 7 while preserving the same location-0 position description, format, offset, and binding layout. Because the red location-7 draw covers the green location-1 draw, the image oracle primarily observes whether the second dynamic description and draw produce the expected result.

`NonSequentialCase::checkSupport()` requires `VK_EXT_extended_dynamic_state`, `VK_EXT_vertex_input_dynamic_state`, and `VK_EXT_extended_dynamic_state2`, then checks the selected construction type ([support check](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L461-L474)). Device setup requests `vertexInputDynamicState`; library cases also request graphics-pipeline-library support, while shader-object cases request dynamic rendering and shader-object support ([capabilities](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L533-L561)).

## Shader Analysis

`initPrograms()` generates two vertex shaders. They differ only in the `inColor` location. The shared fragment shader writes the interpolated color to attachment location 0 ([source generator](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L476-L516)).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.dynamic_vertex_attribute.nonsequential
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` | Selects the normal graphics-pipeline construction path; the shader source is shared with the other construction variants. |
| `nonsequential` | Registers the only leaf in this family and runs the two-draw sparse-location sequence. |
| `m_attributeLocations = {1u, 7u}` | Generates `vert_0` with `inColor` at location 1 and `vert_1` with `inColor` at location 7; this walkthrough uses `vert_0`, matching the retained SPIR-V artifact. |
| `GLSL_VERSION_450` | Emits the `#version 450` declaration used by `initPrograms()`. |

#### Purpose

This vertex shader passes the position and dynamically selected color attribute through to the fragment stage. In the selected artifact, the color input is declared at location 1, so it represents the first draw's dynamic vertex-input description.

#### Structural Design

| Stage operation | Shader-visible carrier | Result |
|-----------------|------------------------|--------|
| Vertex fetch | `inPosition` at location 0; `inColor` at location 1 | Reads the position and color fields supplied by the active dynamic attribute descriptions. |
| Position transport | `gl_Position = inPosition` | Determines the rendered geometry. |
| Color transport | `outColor = inColor` at location 0 | Passes the fetched color to the fragment shader. |

#### Shader Code

```glsl
#version 450

layout(location = 0) in vec4 inPosition;
layout(location = 1) in vec4 inColor;
layout(location = 0) out vec4 outColor;

void main (void)
{
    gl_Position = inPosition;
    outColor = inColor;
}
```

#### Additional Info

- `initPrograms()` emits the same vertex source twice and substitutes only `m_attributeLocations[i]` into the `inColor` declaration; the second generated vertex shader therefore uses location 7 ([source generator](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L476-L498)).
- The fragment shader is fixed across the case and simply writes its location-0 input to its location-0 output ([fragment generator](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L500-L516)).
- The retained SPIR-V corresponds to the location-1 `vert_0` variant, not the location-7 `vert_1` variant.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| `m_attributeLocations[i]` | Changes only the `layout(location = ...)` qualifier of `inColor`: the registered values produce location 1 for `vert_0` and location 7 for `vert_1`; declarations and assignments otherwise remain identical. | [vertex generator](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L476-L498) |
| `pipelineConstructionType` | Does not change generated GLSL; it selects the pipeline construction and capability path around the shared shader collection. | [case construction and capabilities](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L423-L561) |
| `nonsequential` case parameters | Keeps the shader stages fixed while changing the active dynamic vertex-input descriptions between the two draws. | [dynamic descriptions and draws](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L168-L176), [draw commands](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L364-L380) |

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
; Bound: 24
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
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %inPosition = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %inColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPosition
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %23 = OpLoad %v4float %inColor
               OpStore %outColor %23
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The test creates a 32x32 color image, view, render pass, framebuffer, and two graphics pipelines. Both pipelines declare the dynamic vertex-input state and use an empty static vertex-input create info ([setup](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L178-L314)).
2. It allocates two host-visible vertex buffers. Each receives the same six position records with a uniform green or red color, then `flushAlloc` makes the host writes available ([data setup](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L316-L344)).
3. During the render pass, it binds the first pipeline and buffer, calls `vkCmdSetVertexInputEXT` with attributes for locations 0 and 1, and draws six vertices. It then repeats the operation with the second pipeline and buffer but supplies locations 0 and 7 ([commands](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L364-L380)).
4. It ends the render pass, copies the image to a host-visible transfer-destination buffer, submits, and waits. The host invalidates the copied allocation before reading it ([copy and wait](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L382-L409)).
5. The expected 32x32 image starts with the clear color and replaces the centered segment with red. The two draws use identical x/y positions, so the red second draw fully covers the green first draw. `tcu::floatThresholdCompare` compares the reference and readback with a `0.01f` threshold. Failure returns `Rendered image is not correct` ([comparison](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L390-L420)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `nonsequential` | The second dynamic vertex-input command may map location 7 to the wrong attribute, retain the preceding location-1 description, use an incorrect record offset or stride, or transfer fetched color incorrectly through the shader interface. The final image does not independently prove that the first draw fetched location 1 correctly. |

### Cause Analysis

#### Dynamic description replacement or location association

**Possible failure symptoms:** The central red segment is absent, has the preceding green color, or appears in the wrong shape after the second draw. Green is visible only if the first draw succeeds and the second draw fails to cover it; a first-draw-only defect can be overwritten and produce no mismatch.

**Possible implementation causes:** The implementation may retain the first call's attribute descriptions, associate location 7 with the wrong description, or fail to apply the second call's supplied count and descriptions at draw time. The command semantics in [Dynamic Vertex Input](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L412-L435) govern the state established by `vkCmdSetVertexInputEXT`; source-level investigation is needed to separate command-state handling from later fetch processing. Success establishes the observed location-7 path only; it cannot rule out a defect confined to location 1 or the first dynamic-state call.

#### Vertex address or format handling

**Possible failure symptoms:** One or both draw regions contain incorrect colors or geometry, including a displaced or distorted segment.

**Possible implementation causes:** Vertex fetch may select the wrong binding, byte offset, stride, or vertex index, or may decode `VK_FORMAT_R32G32B32A32_SFLOAT` incorrectly. Vulkan defines the address inputs and rate-dependent calculation in [Vertex Input Address Calculation](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1076-L1130). The final image cannot distinguish a fetch error from an interface, rasterization, attachment, copyback, or comparison failure without further investigation.

## Case Pruning

### Requirement-based pruning

Per-case support rejects devices without the three required dynamic-state extensions or without requirements for the selected construction type.

### Design-based pruning

The factory itself has no parameter loop or optional child: it always registers `nonsequential`. The pipeline dispatcher supplies the family under monolithic, pipeline-library, fast-linked-library, and four shader-object groups.

## Key Takeaways

- `nonsequential` configures dynamic location mapping with a stable record layout and sparse color locations 1 and 7.
- Each draw installs its own descriptions, but identical geometry lets the second draw overwrite the first; the final oracle directly validates the location-7 result and state change, not location 1 independently.
- The reference image provides an end-to-end observation of the render path, not a unique driver-layer diagnosis.

## Source Reference Appendix

| Evidence | Source |
|---|---|
| Factory registration | [`createDynamicVertexAttributeTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L565-L575) |
| Pipeline-category routing | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94-L113) |
| Dynamic descriptions and pipeline state | [`NonSequentialInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L165-L314) |
| Vertex data, commands, and image comparison | [`NonSequentialInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L316-L420) |
| Generated shaders and support | [`NonSequentialCase`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L423-L561) |
| Mustpass coverage | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt), [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt), [`fast-linked-library.txt`](../../../mustpass/main/vk-default/pipeline/fast-linked-library.txt), and shader-object lists under [`mustpass/main/vk-default/pipeline/`](../../../mustpass/main/vk-default/pipeline/) |
| Vulkan contracts | [`fxvertex.adoc`](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L258-L270), [dynamic command semantics](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L412-L435), and [vertex-input address calculation](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1076-L1130) |
