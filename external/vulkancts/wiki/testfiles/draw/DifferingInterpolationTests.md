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

The test generates one vertex template and one fragment template, then specializes each template with an empty qualifier, `flat`, or `noperspective` ([templates](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L124-L152)). The six registered shader modules are:

| Module | Stage | Interface declaration |
|---|---|---|
| `vert` | vertex | `layout(location = 0) out vec4 out_color` |
| `vertFlatColor` | vertex | `layout(location = 0) flat out vec4 out_color` |
| `vertNoPerspective` | vertex | `layout(location = 0) noperspective out vec4 out_color` |
| `frag` | fragment | `layout(location = 0) in vec4 in_color` |
| `fragFlatColor` | fragment | `layout(location = 0) flat in vec4 in_color` |
| `fragNoPerspective` | fragment | `layout(location = 0) noperspective in vec4 in_color` |

All variants use GLSL `#version 430`, pass position and color through the shaders, and write the received color to location 0 ([shader construction](../../../modules/vulkan/draw/vktDrawDifferingInterpolationTests.cpp#L124-L160)).

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
