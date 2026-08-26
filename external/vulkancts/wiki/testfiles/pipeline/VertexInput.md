## Overview

**Core question:** Do declared vertex-input locations, bindings, formats, offsets, strides, and rates deliver the intended values to vertex shaders?

- [`vktPipelineVertexInputTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1) implements `pipeline.monolithic.vertex_input`, a test family that turns fetched attributes into diagnostic rendered colors.
- The direct intermediate nodes cover one attribute, multi-attribute layouts, the advertised attribute limit, 64-bit component-width mismatch, and focused state changes. This source also registers `legacy_vertex_attributes` and `srgb_vertex_formats`; their implementations are in [`LegacyAttr.md`](LegacyAttr.md) and [`VertexInputSRGB.md`](VertexInputSRGB.md).
- The page follows one matrix case through layout construction, generated shader checks, rendering, and attachment comparison.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A shader input `location` maps to a vertex-input attribute, that attribute maps to a binding, and a draw binds a buffer to that binding. The attribute supplies the format and element-relative offset; the binding supplies the stride and input rate. Vulkan describes this chain in [Fixed-Function Vertex Processing](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L14-L38).
- `VK_VERTEX_INPUT_RATE_VERTEX` addresses data with the vertex index, while `VK_VERTEX_INPUT_RATE_INSTANCE` addresses it with the instance index ([rate definitions](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L324-L368)).
- Vertex input converts the selected buffer element according to the declared `VkFormat`. The format must support `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT`; offset, binding, and stride also have validity requirements ([attribute description](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L370-L405)).

## Registration Hierarchy

```text
pipeline.monolithic.vertex_input
├── single_attribute
├── multiple_attributes (not shader-object)
├── max_attributes (not shader-object)
├── component_mismatch
├── misc
├── legacy_vertex_attributes (registration only; monolithic and fast_linked_library)
└── srgb_vertex_formats (registration only)
```

[`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096-L3123) adds `multiple_attributes` and `max_attributes` only outside shader-object construction. It delegates the final two intermediate nodes to separate implementations.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Shader input type | integer and unsigned scalar/vector types; `float`/`vec*`; float16 scalar/vector types; matrices; `double`/`dvec*`/`dmat*` | Determines compatible formats, declarations, component checks, and sometimes feature support. | [`GlslType`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L122-L157) |
| Vertex format | Required, scaled, sRGB, 64-bit, and packed formats | Determines byte width and conversion before shader input. | [`vertexFormats`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1839-L1879) |
| Input rate | `VK_VERTEX_INPUT_RATE_VERTEX`, `VK_VERTEX_INPUT_RATE_INSTANCE` | Chooses vertex-index or instance-index addressing. | [case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1881-L1899) |
| Binding mapping | `ONE_TO_ONE`, `ONE_TO_MANY` | Places each attribute in its own binding or shares bindings. | [enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L168-L172) |
| Attribute layout | `INTERLEAVED`, `SEQUENTIAL` | Changes offsets and strides within a shared binding. | [enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L174-L179) |
| Location placement | layout skip enabled/disabled; in-order/out-of-order | Exercises non-contiguous and reordered shader locations. | [enums](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L181-L191) |
| Stress count | `16`, `32`, `64`, `128`, device maximum | Scales the number of input attributes. | [`createMaxAttributeTests`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2137) |
| Misc variants | tessellation on/off, geometry on/off, static/dynamic input state, float/integer unbound input | Isolates stride, unused binding, and absent-attribute behavior. | [misc registration](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3053-L3091) |

The implementation rejects a selected format without `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT`, rejects a 64-bit floating-point format without `shaderFloat64`, and checks float16 support. It also checks `maxVertexInputAttributes`, the number of generated bindings, and portability-subset stride alignment ([support and layout checks](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L493-L513), [layout construction](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L540-L689)).

## Behavior Parameters

The primary behavioral axis is the direct intermediate node, because each node changes the property that the rendered image diagnoses.

### single_attribute: One location, format, and rate

This family binds one compatible format to one shader input, for both vertex and instance rates. It also tests short formats consumed through widened declarations, so the generated checks cover missing-component conversion.

### multiple_attributes: Layout and location relationships

This family combines three selected types while varying one-to-one or one-to-many bindings, interleaved or sequential storage, layout skips, and location order. The shared-binding cases make the offset and stride calculations observable through several inputs at once.

### max_attributes: Advertised-limit stress

This family generates many inputs and uses a specialization constant for the device-query case. It tests whether the implementation can fetch and expose the number of attributes it reports through `maxVertexInputAttributes`.

### component_mismatch: 64-bit input width

This family uses the specific mappings in [`createComponentMismatchTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2204) where a 64-bit format has more components than the shader type consumes. It exercises the legal shader-interface interpretation instead of treating extra stored components as an error.

### misc: State changes and absent descriptions

`stride_change_*` draws with pipelines that differ in binding stride after one vertex-buffer bind. `unused_binding` checks that a declared but unused binding does not alter valid inputs, with static and dynamic vertex-input descriptions. `unbound_input` omits the color attribute and checks the `VK_KHR_maintenance9` default value, including the device-reported alpha convention.

### legacy_vertex_attributes: Delegated behavior

This source registers the intermediate node only for monolithic and fast-linked-library construction. [`LegacyAttr.md`](LegacyAttr.md) documents its implementation.

### srgb_vertex_formats: Delegated behavior

This source registers the intermediate node through `createVertexInputSRGBTests()`. [`VertexInputSRGB.md`](VertexInputSRGB.md) documents its conversion behavior.

## Shader Analysis

The general matrix generates source from the selected attributes: the vertex shader declares inputs at generated locations, validates fetched components, emits red for the first instance and blue for the second when all comparisons succeed, and the fragment shader copies that color ([generator](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L695-L849)). The focused `misc` shaders keep the diagnostic path smaller.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.vertex_input.single_attribute.vec4.as_r32g32b32a32_sfloat_rate_vertex
```

This is the `single_attribute` `vec4` leaf for `VK_FORMAT_R32G32B32A32_SFLOAT` with `VK_VERTEX_INPUT_RATE_VERTEX`; it is the exact representative used for this walkthrough ([mustpass leaf](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L461764)).

| Parameter choice | Meaning in this representative case |
|---|---|
| Pipeline construction: `monolithic` | The leaf is under `dEQP-VK.pipeline.monolithic`; the factory registers `single_attribute` for every construction type ([registration](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096-L3105)). |
| Test family: `single_attribute` | The factory adds the one-attribute group ([registration](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096-L3100)). |
| Shader input type: `vec4` | The leaf name selects the `vec4` GLSL type; single-attribute construction records the selected GLSL type in `AttributeInfo` ([case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1883-L1891)). |
| Vertex format: `VK_FORMAT_R32G32B32A32_SFLOAT` | The exact format appears in the registered compatible format list ([format list](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1852-L1855)). |
| Input rate: `VK_VERTEX_INPUT_RATE_VERTEX` | The leaf suffix is `_rate_vertex`; case creation assigns the vertex rate ([case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1882-L1887)). |
| Binding/layout: one-to-one, interleaved | The single-attribute case is constructed with `BINDING_MAPPING_ONE_TO_ONE` and `ATTRIBUTE_LAYOUT_INTERLEAVED` ([case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1888-L1891)). |

#### Purpose

This representative verifies the direct, unconverted `vec4` path for a four-component 32-bit floating-point vertex attribute. The fetched position and color values are passed through in the vertex stage, making the shader-interface mapping directly observable in the generated artifact: location 0 supplies `inPos` to `gl_Position`, and location 1 supplies `inColor` to `outColor`.

#### Structural Design

| Interface element | Location | Operation | Result |
|---|---:|---|---|
| `inPos` | 0 | Load the fetched `vec4` position | Store it in `gl_Position` (`gl_PerVertex.Position`) |
| `inColor` | 1 | Load the fetched `vec4` color | Store it in `outColor` at location 0 |

The fragment stage is not part of this walkthrough. The selected vertex stage contains only the two input declarations, the built-in position write, and the color pass-through represented by the preserved SPIR-V artifact below.

#### Shader Code

```glsl
#version 460
layout(location = 0) in vec4 inPos;
layout(location = 1) in vec4 inColor;
layout(location = 0) out vec4 outColor;

void main()
{
    gl_Position = inPos;
    outColor = inColor;
}
```

This reconstruction matches the artifact's `OpEntryPoint`, `Location 0`/`Location 1` decorations, `OpLoad` operations, and stores to `Position` and `outColor` ([shader generator](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L695-L719)).

#### Additional Info

- `VK_FORMAT_R32G32B32A32_SFLOAT` is a required, unpacked four-component format in the single-attribute format list ([format list](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1842-L1855)).
- The `_rate_vertex` case addresses the attribute with the vertex index; the paired `_rate_instance` case is generated from the same format/type combination ([case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1882-L1899)).
- The surrounding matrix's generated diagnostic shader is broader than this exact pass-through artifact: it declares generated `attrN` inputs and checks fetched components before writing diagnostic color ([input declarations and check](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L732-L849)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `...as_r32g32b32a32_sfloat_rate_instance` | Input rate changes to `VK_VERTEX_INPUT_RATE_INSTANCE` | [single-attribute case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1893-L1899) |
| Other `vec4` formats | The declared vertex format changes while the `vec4` input remains compatible | [registered vertex formats](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1842-L1875) |
| `..._missing_components` cases | The generated declaration expands to four components to check format-to-RGBA conversion | [missing-component case creation](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1902-L1927) |
| `multiple_attributes` | More attributes vary binding mapping, layout, skipped locations, and location order | [family registration](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3100-L3105) and [parameter dimensions](#parameter-dimensions-and-observed-values) |

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
               OpEntryPoint Vertex %main "main" %_ %inPos %outColor %inColor
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
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
      %inPos = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %inColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPos
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %23 = OpLoad %v4float %inColor
               OpStore %outColor %23
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The matrix implementation builds binding descriptions and attribute descriptions from the selected parameters. For a shared binding, interleaved layout increments an element-relative offset and then aligns the stride; sequential layout places each attribute's array apart and uses a rounded element stride ([construction](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L540-L659)).
- It fills vertex data with values the generated shader can recompute, creates the color attachment and graphics pipeline, draws, submits, and reads the attachment. `VertexInputInstance::iterate()` waits for the work before `verifyImage()` reads it ([iteration](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1728-L1737)).
- The main matrix expects red in the left half and blue in the right half. `intThresholdPositionDeviationCompare` permits the source-defined small channel and position tolerances ([comparison](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1776-L1816)).
- `stride_change` copies its attachment to a host-visible buffer and expects exact blue. `unused_binding` and `unbound_input` each render four quadrants, copy to a buffer, invalidate the allocation, and require exact expected pixels ([focused checks](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2551-L2564), [unused-binding check](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2785-L2812), [unbound-input check](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3014-L3047)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_attribute` | Location-to-binding fetch, format conversion, or vertex/instance rate selection is incorrect. |
| `multiple_attributes` | Multi-binding mapping, interleaved or sequential placement, skipped locations, or out-of-order locations is incorrect. |
| `max_attributes` | Fetch or shader input handling does not scale to the advertised attribute limit. |
| `component_mismatch` | Legal 64-bit component conversion or the shader interface width is handled incorrectly. |
| `misc` | A stride update, unused binding, dynamic vertex-input state, or maintenance9 default attribute value is handled incorrectly. |
| `legacy_vertex_attributes` | The delegated legacy-attribute behavior is incorrect; see `vktPipelineLegacyAttrTests.md`. |
| `srgb_vertex_formats` | The delegated sRGB conversion behavior is incorrect; see `vktPipelineVertexInputSRGBTests.md`. |

### Cause Analysis

#### Attribute fetch or conversion

**Possible failure symptoms:** The main comparison reports an image mismatch, often with red or blue diagnostic regions missing or displaced. The single-attribute, multi-attribute, and component-mismatch cases can fail without identifying a unique source location.

**Possible implementation causes:** Attribute address calculation can select a wrong binding, offset, stride, or vertex/instance index, or conversion can produce a value inconsistent with the declared format. Vulkan defines the address inputs and rate-dependent offset calculation in [Vertex Input Address Calculation](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1076-L1130); source-level investigation is needed to localize a particular failure to fetch, conversion, compiler interface handling, or another path.

#### Layout, location, or limit handling

**Possible failure symptoms:** Cases that share a binding, skip locations, reorder locations, or approach the advertised attribute count fail while simple one-attribute cases pass.

**Possible implementation causes:** The implementation may associate a shader location with the wrong attribute description, compute sequential/interleaved placement incorrectly, or fail to support an advertised count. The specification requires distinct attribute locations and bindings and bounds the corresponding counts ([pipeline vertex-input validity](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L292-L311)).

#### Dynamic or special vertex-input state

**Possible failure symptoms:** A `misc` image differs from its exact reference. Dynamic leaves can fail while static leaves pass; `unbound_input` can produce an unexpected alpha or color.

**Possible implementation causes:** A stride update may not replace the active stride, `vkCmdSetVertexInputEXT` may not establish the supplied descriptions, an unused binding may interfere with used locations, or the maintenance9 default value may be applied incorrectly. The dynamic command replaces vertex-input descriptions when the relevant state is enabled ([dynamic vertex input](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L258-L270), [command semantics](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L412-L435)).

#### Delegated conversion or legacy behavior

**Possible failure symptoms:** A registered `legacy_vertex_attributes` or `srgb_vertex_formats` leaf fails under a construction type that includes it.

**Possible implementation causes:** This source only routes those intermediate nodes. The detailed implementation and failure localization require the delegated source and its Level-3 page, rather than an inference from this dispatcher call.

## Case Pruning

### Requirement-based pruning

- The dynamic form of `unused_binding` and `unbound_input` requires `VK_EXT_vertex_input_dynamic_state` unless shader-object construction supplies the state path.
- `unbound_input` is excluded from Vulkan SC and requires `VK_KHR_maintenance9`; tessellation and geometry stride cases require their respective core features.
- Per-case support checks also prune unsupported float16, float64, format-feature, attribute-count, binding-count, and portability-subset stride configurations.

### Design-based pruning

- The factory omits `multiple_attributes` and `max_attributes` for shader-object construction types.
- `legacy_vertex_attributes` is present only for monolithic and fast-linked-library construction types.
- The `unused_binding` and `unbound_input` leaves exist only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction.

## Key Takeaways

- The family checks the complete mapping from buffer bytes to shader input locations, not merely pipeline creation validity.
- The broad matrix varies formats and layouts, while `misc` isolates state replacement, unused descriptions, and absent attributes.
- Rendered colors make fetch errors observable to host-side image comparison; a failed image classifies the exercised operation shape but does not by itself isolate the driver or hardware layer.
- `legacy_vertex_attributes` and `srgb_vertex_formats` remain separate implementation-bearing pages even though this source registers their paths.

## Source Reference Appendix

| Evidence | Source |
|---|---|
| Test-family registration and construction guards | [`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096-L3123) |
| Type, binding, layout, and location dimensions | [`VertexInputTest` enums](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L119-L208) |
| Attribute and binding description generation | [`VertexInputTest::createInstance()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L516-L693) |
| Generated shader and component diagnostic | [`initPrograms()` and `getGlslVertexCheck()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L695-L849) |
| Matrix image reference and comparison | [`VertexInputInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1776-L1816) |
| Focused stride, unused-binding, and unbound-input cases | [`StrideChangeCase`, `UnusedBinding`, `UnboundInput`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2277-L3050) |
| Mustpass coverage | [`fast-linked-library.txt`](../../../mustpass/main/vk-default/pipeline/fast-linked-library.txt), [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt), [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt), and shader-object pipeline lists under [`mustpass/main/vk-default/pipeline/`](../../../mustpass/main/vk-default/pipeline/) |
| Vulkan vertex-input contracts | [`fxvertex.adoc`](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L14-L38) |
