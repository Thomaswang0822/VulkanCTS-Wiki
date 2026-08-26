## Overview

**Core question:** Does vertex fetch linearize the RGB components of an sRGB vertex attribute while leaving alpha unchanged?

- This page covers the implementation behind the `pipeline.monolithic.vertex_input.srgb_vertex_formats` test family in [`vktPipelineVertexInputSRGBTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L441-L484).
- The family exercises six packed 8-bit sRGB formats. Each valid component has a normal leaf and a `_strict` leaf.
- The selected component controls the height of a rendered quad. The image comparison therefore exposes whether vertex fetch applied sRGB conversion before the vertex shader used the value as a coordinate.
- Pipeline construction variants reuse the same test logic. The source adds the family from [`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096-L3123).

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- Vertex input maps a shader location to an attribute description, then maps that attribute to a binding and a draw-time vertex buffer. The attribute's `format` determines how buffer bytes are extracted and converted ([Fixed-Function Vertex Processing](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L14-L38)).
- An sRGB format stores nonlinear color values. With `VK_KHR_maintenance10` and its `maintenance10` feature enabled, Vulkan requires conversion to linear values for sRGB vertex formats. Without the feature, conversion remains a recommendation, and implementations that do not convert should not expose `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` for those formats ([sRGB vertex conversion](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1179-L1199)).

## Registration Hierarchy

```text
pipeline.monolithic.vertex_input.srgb_vertex_formats
├── r8_srgb
├── r8g8_srgb
├── r8g8b8_srgb
├── b8g8r8_srgb
├── r8g8b8a8_srgb
└── b8g8r8a8_srgb
```

The same test family is instantiated for the construction types represented by the pipeline mustpass files. Each format intermediate node contains component leaves named `r`, `g`, `b`, or `a`, with a second leaf carrying the `_strict` suffix.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction | Monolithic, pipeline library, fast-linked library, shader-object variants | Changes how the graphics pipeline and shaders are constructed while keeping vertex-fetch behavior under test. | [`SRGBVertexInputParams`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L71-L87) |
| Format | `r8_srgb`, `r8g8_srgb`, `r8g8b8_srgb`, `b8g8r8_srgb`, `r8g8b8a8_srgb`, `b8g8r8a8_srgb` | Changes channel count and, for BGR formats, the byte order. | [`kTestedFormats[]`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L441-L453) |
| Component | `r`, `g`, `b`, `a` where present | Selects the one fetched component assigned to the quad's Y coordinate. | [`createVertexInputSRGBTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L457-L479) |
| Strictness | `<component>`, `<component>_strict` | For RGB, selects whether missing conversion can produce a quality warning after a pre-linearized retry or must fail immediately. Alpha uses direct values in both runs, so its retry cannot recover from an initial mismatch; the strict suffix still controls the maintenance10 requirement. | [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L398-L429) |
| Target and random coverage | 16x16; seeded `coveredRows` from 1 through 14 | Gives the reference image a nontrivial coverage boundary and makes the case reproducible from format and component. | [`SRGBVertexInputParams::getExtent()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L71-L87), [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L386-L396) |

The six format nodes contribute 2, 4, 6, 6, 8, and 8 leaves, respectively, for 34 leaves in each construction-specific mustpass file.

## Behavior Parameters

The primary behavioral axis is the format intermediate node. It changes both the number of stored channels and the byte order that `prepareVertexBufferContents()` must honor.

### `r8_srgb`: one-channel conversion

The `r8` intermediate node tests the red component of `VK_FORMAT_R8_SRGB`. Its only component has normal and strict leaves.

### `r8g8_srgb`: two-channel conversion

The `r8g8` intermediate node tests red and green components of `VK_FORMAT_R8G8_SRGB`. Each component is tested in normal and strict forms.

### `r8g8b8_srgb`: three-channel RGB conversion

The `r8g8b8` intermediate node tests red, green, and blue components of `VK_FORMAT_R8G8B8_SRGB`. The component bytes remain in RGB order.

### `b8g8r8_srgb`: three-channel BGR conversion

The `b8g8r8` intermediate node tests the same shader components with `VK_FORMAT_B8G8R8_SRGB`. The host packing helper reverses the RGB byte position before vertex fetch, so this node also checks component ordering.

### `r8g8b8a8_srgb`: four-channel RGBA conversion

The `r8g8b8a8` intermediate node tests all four components of `VK_FORMAT_R8G8B8A8_SRGB`. RGB components use the sRGB conversion path; the alpha leaves supply the coordinate directly and check that vertex fetch leaves alpha unchanged.

### `b8g8r8a8_srgb`: four-channel BGRA conversion

The `b8g8r8a8` intermediate node combines four-channel coverage with BGR ordering. RGB component selection is reversed in the packed bytes, while alpha stays in the fourth position.

## Shader Analysis

The test uses a generated vertex shader and a fixed fragment shader. One representative shader is enough because format, component, and strictness change the host data and selected swizzle, not the shader's control structure.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.vertex_input.srgb_vertex_formats.r8_srgb.r
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` construction | Builds the graphics pipeline through the monolithic pipeline path while leaving the vertex-fetch operation under test. |
| `r8_srgb` format | Uses the one-channel `VK_FORMAT_R8_SRGB` vertex attribute; the selected red byte is the fetched value. |
| `r` component | Selects `inCoords.x` in the generated vertex shader, and assigns that value to the quad's Y coordinate. |
| Non-strict `r` leaf | Runs the expected sRGB-to-linear check first, then permits a pre-linearized retry to report a quality warning if conversion is absent. |

#### Purpose

This walkthrough isolates the shader behavior exercised by the selected representative case.

#### Structural Design

1. `gl_VertexIndex % 4` selects one of four positions for a triangle strip.
2. `inCoords.x` replaces the placeholder Y coordinate. Alternating zero and nonzero vertex values create a horizontal coverage boundary.
3. The scale and offset convert coordinates from 0..1 into clip space. The fragment shader writes blue, so blue coverage identifies the geometry produced by the fetched value.

#### Shader Code

The following is reconstructed from [`SRGBVertexInputCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L175-L210) for an `r8_srgb.r` case. The host writes four vertex records and the shader uses the fetched `x` component as the quad's Y coordinate.

```glsl
#version 460
layout (location=0) in vec4 inCoords;
vec4 vertices[4] = vec4[](
    vec4(0.0, 10.0, 0.0, 1.0),
    vec4(0.0, 10.0, 0.0, 1.0),
    vec4(1.0, 10.0, 0.0, 1.0),
    vec4(1.0, 10.0, 0.0, 1.0)
);
void main(void) {
    vec4 position = vertices[gl_VertexIndex % 4];
    position.y = inCoords.x;
    position = position * vec4(2.0, 2.0, 1.0, 1.0) - vec4(1.0, 1.0, 0.0, 0.0);
    gl_Position = position;
}
```

#### Additional Info

- The generated vertex source uses SPIR-V 1.0 baseline compilation in this reconstruction.
- The shader has no descriptor, image, buffer, or push-constant resource. The vertex attribute is its only external input.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Selected component | The generated source substitutes `x`, `y`, `z`, or `w` for the component read from `inCoords`. | [`SRGBVertexInputCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L175-L210) |
| Vertex format | The host packs the byte into the selected channel for RGB or BGR formats; unused bytes receive `255` padding. | [case generation](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L457-L479) |
| Strictness | The fragment shader remains unchanged; strictness changes the host-side result policy rather than shader code. | [result checking](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L386-L429) |

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
; Bound: 53
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %inCoords %_
               OpSource GLSL 460
               OpName %main "main"
               OpName %vertices "vertices"
               OpName %position "position"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %inCoords "inCoords"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %inCoords Location 0
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_ptr_Private__arr_v4float_uint_4 = OpTypePointer Private %_arr_v4float_uint_4
   %vertices = OpVariable %_ptr_Private__arr_v4float_uint_4 Private
    %float_0 = OpConstant %float 0
   %float_10 = OpConstant %float 10
    %float_1 = OpConstant %float 1
         %16 = OpConstantComposite %v4float %float_0 %float_10 %float_0 %float_1
         %17 = OpConstantComposite %v4float %float_1 %float_10 %float_0 %float_1
         %18 = OpConstantComposite %_arr_v4float_uint_4 %16 %16 %17 %17
%_ptr_Function_v4float = OpTypePointer Function %v4float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_4 = OpConstant %int 4
%_ptr_Private_v4float = OpTypePointer Private %v4float
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %inCoords = OpVariable %_ptr_Input_v4float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
%_ptr_Function_float = OpTypePointer Function %float
    %float_2 = OpConstant %float 2
         %41 = OpConstantComposite %v4float %float_2 %float_2 %float_1 %float_1
         %43 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_0
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
   %position = OpVariable %_ptr_Function_v4float Function
               OpStore %vertices %18
         %24 = OpLoad %int %gl_VertexIndex
         %26 = OpSMod %int %24 %int_4
         %28 = OpAccessChain %_ptr_Private_v4float %vertices %26
         %29 = OpLoad %v4float %28
               OpStore %position %29
         %34 = OpAccessChain %_ptr_Input_float %inCoords %uint_0
         %35 = OpLoad %float %34
         %38 = OpAccessChain %_ptr_Function_float %position %uint_1
               OpStore %38 %35
         %39 = OpLoad %v4float %position
         %42 = OpFMul %v4float %39 %41
         %44 = OpFSub %v4float %42 %43
               OpStore %position %44
         %50 = OpLoad %v4float %position
         %52 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %52 %50
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` checks the selected pipeline construction, requires `VK_KHR_maintenance10` for strict cases, and rejects formats without `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` ([`checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L159-L173)).
- `iterate()` derives a reproducible row count from `format` and `component`. For RGB components, it converts the wanted linear coordinates to sRGB before storing them. For alpha, it stores the wanted coordinate directly to check that alpha is not linearized.
- `runWithCoords()` packs the values according to the selected format, creates a vertex buffer with one binding and one attribute at location 0, creates the pipeline and 16x16 color target, records a triangle-strip draw, and copies the target to host memory ([`runWithCoords()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L269-L363)).
- The host compares the copied result with an image whose top `coveredRows` rows are blue and whose remaining rows retain the clear color. The comparison uses zero component threshold.
- For an RGB leaf, the first run expects sRGB-to-linear conversion. If it fails, a non-strict leaf retries with pre-linearized values; a successful retry returns `QP_TEST_RESULT_QUALITY_WARNING`, while a failed retry fails the case. A strict RGB leaf fails immediately after the first mismatch. For alpha, the first run instead expects the direct value to remain unchanged. Its non-strict retry uses the same coordinates, so an initial alpha mismatch cannot become a quality warning; both alpha leaf forms ultimately fail on that mismatch.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `r8_srgb` | Single-channel sRGB vertex fetch or conversion is incorrect. |
| `r8g8_srgb` | Two-channel sRGB fetch, component selection, or conversion is incorrect. |
| `r8g8b8_srgb` | Three-channel sRGB fetch or conversion is incorrect. |
| `b8g8r8_srgb` | BGR component ordering or three-channel sRGB conversion is incorrect. |
| `r8g8b8a8_srgb` | Four-channel sRGB fetch or conversion is incorrect. |
| `b8g8r8a8_srgb` | BGRA component ordering or four-channel sRGB conversion is incorrect. |

### Cause Analysis

#### Single-channel sRGB fetch or conversion

**Possible failure symptoms:** The first coverage comparison fails for `r8_srgb`. In non-strict mode the pre-linearized retry passes and the case reports a quality warning; in strict mode the case fails.

**Possible implementation causes:** Vertex fetch may expose the stored nonlinear value directly, apply the wrong sRGB transfer function, or misread the one-byte format. The Vulkan contract is the conversion requirement described in [`fxvertex.adoc`](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1179-L1199); source-level investigation is needed to localize an implementation fault further.

#### Multi-channel RGB fetch or conversion

**Possible failure symptoms:** One or more component leaves under `r8g8_srgb` or `r8g8b8_srgb` produce a coverage boundary different from the reference.

**Possible implementation causes:** The implementation may fetch the wrong byte, convert a component incorrectly, or associate the attribute format with the wrong component position. The source's single attribute and explicit component selection make the failure observable, but source-level investigation is needed to distinguish fetch addressing from conversion.

#### BGR ordering or conversion

**Possible failure symptoms:** A `b8g8r8_srgb` or `b8g8r8a8_srgb` component leaf fails while an equivalent RGB leaf passes, or the wrong selected component controls coverage.

**Possible implementation causes:** The BGR packing branch may expose a channel in the wrong logical position, or the implementation may mishandle conversion for a BGR numeric format. The test's operation shape cannot isolate host packing, vertex fetch ordering, and conversion from the final image alone; source-level investigation is needed.

#### Four-channel RGBA fetch or conversion

**Possible failure symptoms:** RGB or alpha leaves under `r8g8b8a8_srgb` produce unexpected coverage. Alpha failures are evaluated with direct linear values because the test does not apply an sRGB encoding to alpha; the non-strict alpha retry repeats those values and cannot recover as a quality warning.

**Possible implementation causes:** The implementation may mishandle the fourth channel, use the wrong component count, or apply color conversion to alpha. The exact source path identifies the expected distinction, while implementation localization requires further investigation.

## Case Pruning

### Requirement-based pruning

- A format must expose `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT`, or the case is reported unsupported.
- Strict leaves require `VK_KHR_maintenance10`.
- Pipeline construction requirements and the related extensions and features are checked before execution. The source adds support for graphics pipeline library, shader object, dynamic rendering dependencies, and maintenance10 as needed ([`initDeviceCapabilities()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L134-L157)).

### Design-based pruning

- The generator skips a component when its index is greater than or equal to the format's used channel count. This prevents meaningless leaves such as alpha for a one-channel format.
- The test keeps one attribute, one binding, a vertex input rate of `VK_VERTEX_INPUT_RATE_VERTEX`, and a 16x16 target. These fixed choices isolate sRGB vertex conversion rather than testing general vertex-input layout combinations.
- For RGB leaves, the non-strict retry is a result policy, not a second registered behavior. It distinguishes an implementation that lacks conversion from one that cannot render the fallback input correctly. Alpha leaves execute the same retry path, but their direct input values do not change between runs.

## Key Takeaways

- The family makes sRGB vertex conversion visible through geometry height instead of a color-space image comparison.
- The six format intermediate nodes cover channel count and RGB versus BGR byte ordering; component leaves isolate one logical channel at a time.
- Strict leaves require `VK_KHR_maintenance10` and enforce its vertex-fetch behavior: RGB is linearized and alpha remains unchanged. For RGB, non-strict leaves preserve compatibility by turning a conversion miss into a quality warning when pre-linearized input succeeds; alpha has no distinct fallback input.
- A failing image identifies an incorrect fetched coordinate or conversion path, but the final image alone cannot localize the defect to host packing, vertex fetch, or implementation conversion.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter and target extent | [`SRGBVertexInputParams`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L71-L87) | Defines the tested dimensions and reproducible target size. |
| Capability checks | [`SRGBVertexInputCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L159-L173) | Defines feature and format support pruning. |
| Shader generation | [`SRGBVertexInputCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L175-L210) | Defines the coordinate-producing shader. |
| Vertex-buffer packing | [`prepareVertexBufferContents()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L212-L267) | Defines channel placement and BGR reversal. |
| Draw and comparison | [`SRGBVertexInputInstance::runWithCoords()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L269-L383) | Defines resource setup, submission, copyback, and image comparison. |
| Outcome policy | [`SRGBVertexInputInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L386-L429) | Defines pass, warning, and failure results. |
| Registration | [`createVertexInputSRGBTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L441-L484) | Defines format, component, and strictness leaves. |
| Mustpass examples | [`pipeline/monolithic/monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) | Contains 34 leaves for the monolithic construction. |
| Specification | [`fxvertex.adoc`](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L1179-L1199) | Defines the sRGB vertex conversion contract. |
