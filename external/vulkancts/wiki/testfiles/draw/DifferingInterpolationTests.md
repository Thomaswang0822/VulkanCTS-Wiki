## Overview

**Core question:** Does fragment-input interpolation remain unchanged when the matching vertex output carries a different interpolation decoration?

`vktDrawDifferingInterpolationTests.cpp` checks vertex-to-fragment interpolation when the interpolation decoration is present on only one side of the interface. It renders the same triangle twice with paired shader modules and requires the two complete color images to be identical. The test covers `flat` and `noperspective` decorations, with the decoration mismatch placed on either the vertex output or fragment input.

This is an implementation test, not a comparison against a software-rendered image: the second draw is the reference configuration, and the result is a byte-exact image comparison.

## Background Knowledge

For the shared concepts of shader interfaces and interpolation qualifiers, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- **Fragment inputs select interpolation:** Vulkan specifies that interpolation decorations on pre-rasterization shader inputs and outputs do not affect interpolation. An undecorated fragment input uses perspective-correct interpolation, `NoPerspective` selects linear interpolation, and `Flat` selects the provoking vertex without interpolation ([Interpolation Decorations](https://docs.vulkan.org/spec/latest/chapters/shaders.html#shaders-interpolation-decorations)). This rule explains why changing only the vertex-output decoration must not change this test's image.

## Registration Hierarchy

```text
draw.renderpass.differing_interpolation
├── flat_0
├── flat_1
├── noperspective_0
└── noperspective_1
```

The four direct children are registered literally by `createTests()` ([registration](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L461-L479)). The same leaf set is instantiated under the dynamic-rendering `primary_cmd_buff`, `partial_secondary_cmd_buff`, and `complete_secondary_cmd_buff` branches; the default mustpass lists those paths as well as the render-pass path ([dynamic-rendering mustpass entries](../../../mustpass/main/vk-default/draw.txt#L363-L366), [partial entries](../../../mustpass/main/vk-default/draw.txt#L2897-L2900), [primary entries](../../../mustpass/main/vk-default/draw.txt#L5497-L5500), [render-pass entries](../../../mustpass/main/vk-default/draw.txt#L17933-L17936)). The hierarchy block uses the render-pass instance as the canonical page root; the child names are identical in each registered variant.

## Parameter Dimensions and Observed Values

| Dimension | Registered or fixed values | Meaning in this test | Evidence |
|---|---|---|---|
| Interpolation decoration | `flat`, `noperspective` | Selects whether the fragment input takes the provoking-vertex value or uses linear interpolation. | [`createTests`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L461-L479) |
| Mismatch direction | `_0`, `_1` | `_0` leaves omit the decoration from the test vertex output; `_1` leaves add it only to the test vertex output. The fragment input is held fixed within each test/reference pair. | [`createTests`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L464-L469) |
| Geometry | One triangle with three differently colored vertices | Non-uniform colors and clip-space `w` values make interpolation behavior visible across the triangle. | [`vertices`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L239-L250), [`draw`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L419-L427) |
| Color target | 256 x 256, `VK_FORMAT_R8G8B8A8_UNORM`, one sample | Provides the complete image compared by the host. | [`target image`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L194-L212) |
| Rendering paths | Render pass; dynamic rendering with primary, partial-secondary, or complete-secondary recording | Repeats the same family across the non-nested paths selected by the draw dispatcher. | [`dispatcher`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L121) |

## Behavior Parameters

### `flat_0`: Fragment-side `flat` decoration

The test image uses `vert` with `fragFlatColor`. Its reference image uses `vertFlatColor` with `fragFlatColor` ([parameter setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L464-L465)). Thus the fragment input is decorated `flat` in both images, while the vertex output differs. The pair tests that this cross-stage decoration difference produces the same result as matching `flat` declarations.

### `flat_1`: Vertex-side `flat` decoration

The test image uses `vertFlatColor` with `frag`; its reference uses `vert` with `frag` ([parameter setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L464-L465)). The fragment input is undecorated in both images, while the vertex output differs. Both images must therefore use perspective-correct interpolation; the `flat` decoration on the test vertex output has no effect.

### `noperspective_0`: Fragment-side `noperspective` decoration

The test image uses `vert` with `fragNoPerspective`; its reference uses `vertNoPerspective` with `fragNoPerspective` ([parameter setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L467-L468)). The fragment input is `noperspective` in both images, while the vertex output differs. Both images must therefore use linear interpolation.

### `noperspective_1`: Vertex-side `noperspective` decoration

The test image uses `vertNoPerspective` with `frag`; its reference uses `vert` with `frag` ([parameter setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L467-L469)). The fragment input is undecorated in both images, while the vertex output differs. Both images must therefore use perspective-correct interpolation; the `noperspective` decoration on the test vertex output has no effect.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.draw.renderpass.differing_interpolation.flat_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `flat` | Adds `flat` to the test vertex shader's location-0 color output. |
| `_1` | Places the differing decoration only on the test vertex output; both fragment inputs are undecorated. |
| `renderpass` | Uses the canonical render-pass registration of this leaf; rendering-path variants reuse the same generated modules. |

#### Purpose

This case checks that `flat` on a vertex output does not change interpolation when the matching fragment input is undecorated. The test and reference images must both use perspective-correct color interpolation and match exactly.

#### Structural Design

| Draw | Vertex location-0 output | Fragment location-0 input | Fragment interpolation selected |
|---|---|---|---|
| Test | `flat out vec4 out_color` | `in vec4 in_color` | Perspective-correct |
| Reference | `out vec4 out_color` | `in vec4 in_color` | Perspective-correct |

#### Shader Code

```glsl
#version 430
/// Location 0 supplies clip-space position; the three host vertices use unequal w values so perspective correction is observable.
layout(location = 0) in vec4 in_position;
/// Location 1 supplies a different RGBA color at each vertex.
layout(location = 1) in vec4 in_color;
/// This test-side output alone is flat; the matching fragment input remains undecorated.
layout(location = 0) flat out vec4 out_color;
/// The explicit built-in block carries the clip-space position and fixes point size even though the pipeline draws a triangle.
out gl_PerVertex {
    vec4  gl_Position;
    float gl_PointSize;
};
void main() {
    /// Forward the host attributes unchanged; only the output interpolation decoration differs from the reference vertex shader.
    gl_PointSize = 1.0;
    gl_Position  = in_position;
    out_color    = in_color;
}
```

#### Additional Info

- The fixed fragment shader declares undecorated `layout(location = 0) in vec4 in_color` and directly copies it to the location-0 color output; it is identical in both draws of this leaf ([shader template](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L140-L146)).
- The reference vertex shader is generated from the same template with an empty qualifier substitution; `flat` is the only shader-text difference relevant to the compared pair ([specializations](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L148-L159), [pair selection](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L464-L465)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Interpolation decoration | `noperspective` replaces `flat` on the selected interface declaration in the neighboring family, selecting linear interpolation only when it appears on the fragment input. | [`initPrograms`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L148-L159) |
| Mismatch direction | `_0` leaves the test vertex output undecorated and decorates the fixed fragment input; `_1` decorates only the test vertex output and leaves the fragment input undecorated. | [`createTests`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L461-L479) |
| Rendering path | Render-pass and dynamic-rendering registrations do not change generated GLSL; they vary pipeline and command-buffer setup around the same module names. | [`initPrograms`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L124-L160) |

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
; Bound: 25
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %out_color %in_color
               OpSource GLSL 430
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %in_position Location 0
               OpDecorate %out_color Flat
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %15 %float_1
         %19 = OpLoad %v4float %in_position
         %21 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %21 %19
         %24 = OpLoad %v4float %in_color
               OpStore %out_color %24
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

Each leaf runs two frames, selecting the test and reference vertex/fragment module names from its `DrawParams` ([iteration setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L173-L194)). For each frame the instance:

1. Creates a 256 × 256 single-sample `VK_FORMAT_R8G8B8A8_UNORM` color image and view ([image setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L194-L218)).
2. Uploads the same three position/color vertices ([vertex-buffer setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L239-L261)).
3. Builds a triangle-list graphics pipeline using the selected shader pair ([pipeline setup](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L263-L311)).
4. Clears the target, records `vkCmdDraw(..., 3, 1, 0, 0)`, submits, and reads the full image back ([command recording and readback](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L317-L390)).
5. Compares the two returned pixel buffers with `tcu::intThresholdCompare` and `tcu::UVec4(0)` ([final comparison](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L392-L398)).

The zero integer threshold requires every compared channel of every pixel to match exactly after readback. A mismatch in either image pair returns `QP_TEST_RESULT_FAIL`.

### Test Principle

The test isolates fragment-input interpolation control by holding geometry, vertex data, fragment-input declaration, pipeline topology, target format, clear value, draw command, and readback path constant within each pair. Only the vertex-output decoration differs between the test and reference shader pairs. Passing therefore demonstrates byte-for-byte agreement for the tested decoration and mismatch direction on the selected rendering/command-buffer path; it does not by itself establish behavior for decorations or interface layouts not registered here.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `flat_0` | The undecorated vertex output incorrectly changes a fragment input that must remain `flat`, or shared rendering/readback setup differs between the two frames. |
| `flat_1` | The `flat` vertex-output decoration incorrectly affects the undecorated fragment input, or shared rendering/readback setup differs between the two frames. |
| `noperspective_0` | The undecorated vertex output incorrectly changes a fragment input that must remain `noperspective`, or shared rendering/readback setup differs between the two frames. |
| `noperspective_1` | The `noperspective` vertex-output decoration incorrectly affects the undecorated fragment input, or shared rendering/readback setup differs between the two frames. |

### Cause Analysis

#### Fragment-input `flat` selection

**Possible failure symptoms:** `flat_0` or `flat_1` produces at least one channel mismatch between the two complete readback images. Because the fragment input is identical within each pair, that mismatch shows that the vertex-output decoration changed the result.

**Possible implementation causes:** Vulkan specifies that a pre-rasterization output's interpolation decoration has no effect, while a fragment input decorated `Flat` takes its value from the provoking vertex. A failure can therefore indicate that the implementation incorrectly used the vertex-output decoration or failed to honor the fragment-input decoration ([Interpolation Decorations](https://docs.vulkan.org/spec/latest/chapters/shaders.html#shaders-interpolation-decorations)).

#### Fragment-input `noperspective` selection

**Possible failure symptoms:** `noperspective_0` or `noperspective_1` produces at least one channel mismatch between the two complete readback images. The non-uniform clip-space `w` values make an unintended change between linear and perspective-correct interpolation observable.

**Possible implementation causes:** Vulkan assigns linear interpolation to a fragment input decorated `NoPerspective` and perspective-correct interpolation to an undecorated fragment input, regardless of the pre-rasterization output decoration. A failure can indicate incorrect interpolation-mode selection from the fragment interface ([Interpolation Decorations](https://docs.vulkan.org/spec/latest/chapters/shaders.html#shaders-interpolation-decorations)).

#### Shared rendering or readback setup

**Possible failure symptoms:** Multiple leaves or one rendering path reports image inequality even though each pair uses identical geometry and non-shader state. A dynamic-rendering-only failure narrows the difference to that path's attachment or command-buffer setup.

**Possible implementation causes:** The two frames independently create, clear, render to, and read back their target images before the exact comparison ([execution](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L173-L398)). A fault in pipeline construction, command recording, image transitions, rendering attachment setup, or readback can therefore produce inequality unrelated to interpolation.

The oracle compares two device-rendered images and cannot prove that either image is intrinsically correct when both configurations produce the same wrong result. It detects disagreement caused by the differing vertex-output decorations, not all incorrect interpolation behavior.

## Case Pruning

### Requirement-based pruning

Dynamic-rendering instances require `VK_KHR_dynamic_rendering` ([support check](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L162-L166)). An implementation that does not meet this requirement skips the affected instance rather than failing the image comparison.

### Design-based pruning

The dispatcher registers this family only when `nestedSecondaryCmdBuffer` is false, so it appears under the render-pass branch and the three non-nested dynamic-rendering command-buffer branches but not under either nested branch ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L121)). The default mustpass selects the resulting 16 leaves: four per branch ([complete secondary](../../../mustpass/main/vk-default/draw.txt#L363-L366), [partial secondary](../../../mustpass/main/vk-default/draw.txt#L2897-L2900), [primary](../../../mustpass/main/vk-default/draw.txt#L5497-L5500), [render pass](../../../mustpass/main/vk-default/draw.txt#L17933-L17936)).

## Key Takeaways

- The registered family has exactly four leaves: `flat_0`, `flat_1`, `noperspective_0`, and `noperspective_1`.
- Each leaf renders a fixed three-vertex triangle twice with different qualifier placement and compares the complete readback images.
- Final validation uses an integer threshold of zero, so the expected result is exact equality of final bytes.
- Dynamic-rendering variants are gated by `VK_KHR_dynamic_rendering`; the default mustpass records render-pass and three dynamic-rendering command-buffer paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Shader templates and six specializations | [`initPrograms`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L124-L160) | Defines the decorated and undecorated shader interfaces. |
| Support gate | [`checkSupport`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L162-L166) | Gates dynamic-rendering instances. |
| Four shader-pair parameter sets | [`createTests`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L461-L479) | Registers the exact leaves and test/reference modules. |
| Image execution and readback | [`iterate`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L173-L390) | Renders both independently created frames and reads them back. |
| Exact final image comparison | [`intThresholdCompare`](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L392-L398) | Supplies the pass/fail oracle. |
| Dispatcher scope | [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L121) | Includes the family only on non-nested draw branches. |
| Default mustpass leaves | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L363-L366) | Confirms one selected dynamic-rendering branch; the other branch ranges are linked above. |
