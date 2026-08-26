## Overview

**Core question:** Do inclusive and exclusive discard rectangles produce the expected coverage for static and dynamic rectangle coordinates, with and without scissoring?

`DiscardRectanglesTests` validates `VK_EXT_discard_rectangles` in a small color-rendering workload. Each case draws a full-frame green quad into a red-cleared `VK_FORMAT_R8G8B8A8_UNORM` image and compares the readback with a software image that applies the same discard-rectangle and scissor rules. The family crosses rectangle mode, count, coordinate delivery, and scissor delivery across the registered render-pass and dynamic-rendering arrangements.

## Background Knowledge

For the shared concepts rasterization state, scissor state, render passes, dynamic rendering, and readback comparison, see [Background Knowledge](../../categories/draw.md#background-knowledge) of the `draw` page.

- **Discard rectangle coverage:** A discard rectangle is fixed-function fragment state defined in framebuffer coordinates. Inclusive mode sets sample coverage to zero outside the union of the rectangles; exclusive mode sets it to zero inside any rectangle.
- **Static and dynamic rectangle coordinates:** Rectangle coordinates can be supplied when the pipeline is created or set for later draws with `vkCmdSetDiscardRectangleEXT`. Making the coordinates dynamic does not make the rectangle count or inclusive/exclusive mode dynamic.

## Registration Hierarchy

The draw dispatcher adds `createDiscardRectanglesTests` below the draw group. The tree shows one representative count leaf for each state/mode combination in the render-pass arrangement (the `SharedGroupParams` supplied by the dispatcher selects the command/rendering arrangement where applicable):

```text
draw.renderpass.discard_rectangles
├── inclusive_rect_1
├── exclusive_rect_1
├── scissor_inclusive_rect_1
├── scissor_exclusive_rect_1
├── dynamic_scissor_inclusive_rect_1
├── dynamic_scissor_exclusive_rect_1
├── dynamic_discard_inclusive_rect_1
├── dynamic_discard_exclusive_rect_1
├── dynamic_discard_scissor_inclusive_rect_1
├── dynamic_discard_scissor_exclusive_rect_1
├── dynamic_discard_dynamic_scissor_inclusive_rect_1
└── dynamic_discard_dynamic_scissor_exclusive_rect_1
```

Each shown `_rect_1` test case has five direct sibling leaves with the exact rectangle-count suffixes `2`, `3`, `4`, `8`, and `16` described below.

The complete leaf identifier set is:

The complete leaf identifier set uses the exact six rectangle-count suffixes `1`, `2`, `3`, `4`, `8`, and `16` for each of the twelve mode prefixes listed above.

The source loops over two rectangle-coordinate paths, three scissor paths, two modes, and six counts: 72 leaves per created group. The Vulkan default mustpass list contains four such arrangements (288 leaves): render pass plus primary, partial-secondary, and complete-secondary dynamic rendering. The Vulkan SC default list contains the 72 render-pass leaves. The dispatcher deliberately excludes this family from its two nested-secondary arrangements.

The C++ factory creates the `discard_rectangles` group. The draw dispatcher supplies that factory under the render-pass draw group and reuses shared group parameters for other supported rendering modes. The exact dispatcher ownership should be kept distinct from the leaf factory: `vktDrawDiscardRectanglesTests.cpp` creates the group and leaves, while `vktDrawTests.cpp` attaches the group to the broader draw hierarchy.

## Parameter Dimensions and Observed Values

| Axis | Source-defined values | Effect |
|---|---|---|
| Discard mode | `inclusive`, `exclusive` | Selects `VK_DISCARD_RECTANGLE_MODE_INCLUSIVE_EXT` or `VK_DISCARD_RECTANGLE_MODE_EXCLUSIVE_EXT`. |
| Rectangle count | `1`, `2`, `3`, `4`, `8`, `16` | Controls `discardRectangleCount` and the number of generated `VkRect2D` values. |
| Discard-rectangle coordinates | static, dynamic | Static coordinates are pointed to by pipeline discard state; dynamic cases call `vkCmdSetDiscardRectangleEXT`. The count and mode remain pipeline state. |
| Scissor state | none, static, dynamic | No scissor uses the full target; static state is in the pipeline; dynamic state is set with `vkCmdSetScissor`. |
| Rendering arrangement | render pass, or dispatcher-selected dynamic-rendering variants | Changes attachment/rendering command setup, not the discard-rectangle matrix. |

The six rectangle counts are source constants. `generateDiscardRectangles()` places rectangles in a horizontal sequence: each rectangle is 5 pixels from the left/top margin, has height `renderHeight - 10`, and is separated by a gap of one rectangle width. The test image is 340×100 pixels. The scissor used by scissor cases has offset `(90,25)` and extent `(160,50)`. The clear color is `(1,0,0,1)` and the vertex/fragment color is `(0,1,0,1)`.

## Behavior Parameters

The primary behavioral axes are discard mode, discard-coordinate delivery, scissor-state delivery, and rectangle count. Their combinations distinguish fixed-function discard behavior from the dynamic-state paths.

### Inclusive and exclusive modes - retained coverage

Inclusive mode retains fragments inside the rectangles; exclusive mode discards fragments inside them.

### Static and dynamic rectangle coordinates - state delivery

Static rectangle coordinates are supplied at pipeline creation; dynamic coordinates are recorded with `vkCmdSetDiscardRectangleEXT`. Both paths keep `discardRectangleCount` and `discardRectangleMode` in `VkPipelineDiscardRectangleStateCreateInfoEXT`.

### Scissor variants - interaction with clipping

Scissor variants combine discard rectangles with no scissor, static scissor, or dynamic scissor state.

### Rectangle count - indexed rectangle coverage

The registered counts `1`, `2`, `3`, `4`, `8`, and `16` vary how many generated rectangles participate. In dynamic-coordinate cases, the command updates indices starting at zero for the selected count; support checking prunes counts above `maxDiscardRectangles`.

## Shader Analysis

The fragment shader writes the interpolated green color. The tested discard behavior is fixed-function rasterization state, so no representative shader walkthrough is needed.

## Runtime Execution and Result Checking

1. Registration constructs a `TestParams` value for the selected mode, count, dynamic-discard flag, scissor mode, and shared rendering parameters.
2. Support checking requires `VK_EXT_discard_rectangles`. Dynamic-rendering cases additionally require `VK_KHR_dynamic_rendering`. The implementation queries `VkPhysicalDeviceDiscardRectanglePropertiesEXT`; zero supported rectangles or a `maxDiscardRectangles` value below the requested count produces `NotSupportedError`, not a test failure.
3. The instance creates a 340×100 `R8G8B8A8_UNORM` color image with color-attachment and transfer-source usage, an image view, a host-visible transfer-destination buffer, vertex buffer, shader modules, pipeline layout, and graphics pipeline. Render-pass cases also create a render pass and framebuffer.
4. Four vertices `(-1,1)`, `(-1,-1)`, `(1,1)`, `(1,-1)` form a triangle strip covering the target. The pipeline uses one viewport and either the full-target scissor or the configured static scissor. The discard state is attached through `VkPipelineDiscardRectangleStateCreateInfoEXT`; for dynamic discard cases its rectangle pointer is null and the command supplies the values later.
5. The command buffer transitions the target, clears it red, begins the selected render scope, binds the pipeline and vertex buffer, optionally sets discard rectangles and/or scissor dynamically, and issues one `vkCmdDraw` for the four vertices. It ends the render scope, copies the image to the host-visible buffer, and submits the command buffer, waiting for completion.
6. The host invalidates the allocation, interprets the buffer as a color image, generates the software reference, and compares the two images with `tcu::floatThresholdCompare` using per-channel threshold `0.02`. A successful comparison returns `pass("OK")`; a mismatch raises `TCU_FAIL("Rendered image is not correct")`.

### Reference Image and Expected Behavior

`generateReferenceImage()` starts with either red or green depending on mode, then paints rectangle regions with the opposite color. For scissor cases it first preserves red outside the scissor, clears the scissor region to the mode-dependent base color, and applies each discard rectangle only where it intersects the scissor. This models the observable result rather than inspecting individual fragment invocations.

- Inclusive cases should show green in the discard rectangles and red elsewhere (or only within the scissor intersection for scissor cases).
- Exclusive cases should show red in the discard rectangles and green elsewhere (with scissor clipping where selected).
- Dynamic-discard cases must match the corresponding static-discard case.
- Dynamic-scissor cases must match the corresponding static-scissor case.

The test does not use randomized rectangle geometry: count and placement are fixed by the source function. It also does not compare a depth or stencil attachment.

### Generated Programs and Resources

The test generates two GLSL 440 programs in `initPrograms()`:

- `vert` accepts a location-0 `vec4` position, writes `gl_Position`, and emits a constant green `vsColor`.
- `frag` accepts `vsColor` and writes it to the location-0 color output.

The color image is copied into a host-visible buffer after rendering. The result comparison therefore covers command recording, pipeline state, vertex fetch, rasterization discard/scissor behavior, attachment writes, image layout transitions, copy, and host readback. A comparison failure cannot by itself identify which one of these stages is defective.

### Synchronization and Ordering

The implementation records all setup, draw, and copy operations into the command buffer and uses `submitCommandsAndWait` before reading the host buffer. The copy is ordered after color-attachment writes with the helper's specified access/layout transition. Dynamic discard and dynamic scissor commands occur after pipeline binding and before the draw. In dynamic-rendering mode, the source performs the color-image transition before beginning rendering; render-pass mode uses the render-pass attachment path.

## Failure Meaning

`NotSupportedError` means the device lacks the required extension/rendering functionality or cannot support the requested number of active rectangles. It is a support skip, not evidence of an implementation mismatch.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `inclusive`, `exclusive` | Incorrect mode-dependent sample coverage or reference-image agreement. |
| static, dynamic discard-rectangle coordinates | Incorrect pipeline coordinates or `vkCmdSetDiscardRectangleEXT` handling. |
| no scissor, static scissor, dynamic scissor | Incorrect discard/scissor intersection or dynamic scissor handling. |
| `1`, `2`, `3`, `4`, `8`, `16` | Incorrect rectangle count, indexing, coordinate generation, or capacity handling. |

All variants share the draw, attachment, copy, and readback path, so a final-image mismatch does not by itself isolate fixed-function discard behavior from shared infrastructure.

### Cause Analysis

#### Discard coverage and state delivery

**Possible failure symptoms:** Pixels outside the inclusive union are green, pixels inside an exclusive rectangle are green, the wrong number or placement of rectangles appears, or a dynamic-coordinate result differs from its static counterpart.

**Possible implementation causes:** The implementation may apply inclusive/exclusive coverage incorrectly, consume the wrong rectangle indices or coordinates, or fail to apply coordinates recorded by `vkCmdSetDiscardRectangleEXT` to the subsequent draw.

#### Scissor interaction

**Possible failure symptoms:** Green pixels appear outside the configured scissor, expected green pixels inside the rectangle/scissor intersection remain red, or static and dynamic scissor variants disagree.

**Possible implementation causes:** Discard-rectangle and scissor coverage may be combined incorrectly, or dynamic scissor state may not be applied to the draw as recorded. The Vulkan fragment-operations order performs the discard-rectangle test before the scissor test, while both must reject coverage outside their retained regions.

#### Shared rendering and readback path

**Possible failure symptoms:** The final image differs from the source-generated reference beyond `0.02` in at least one channel without a pattern that localizes the error to one behavior axis.

**Possible implementation causes:** Pipeline setup, vertex fetch, rasterization, attachment writes, image transitions, image-to-buffer copy, or host readback may have produced the mismatch. The image-only oracle cannot distinguish among these shared stages.

## Case Pruning

### Requirement-based pruning

Cases are skipped when `VK_EXT_discard_rectangles`, dynamic rendering, or the requested `maxDiscardRectangles` capability is unavailable.

### Design-based pruning

The dispatcher creates this family for render pass and for primary, partial-secondary, and complete-secondary dynamic rendering. It intentionally omits the family from the two nested-secondary arrangements by registering only `basic_draw` when `nestedSecondaryCmdBuffer` is true; this is a matrix-design choice, not evidence that discard rectangles are unsupported there.

The checked-in mustpass draw lists contain the category-qualified `discard_rectangles` leaves for both `vk-default` and `vksc-default` lists. The source and dispatcher establish the hierarchy; mustpass files are the release-list evidence and should be consulted when making claims about a particular profile's inclusion.

## Key Takeaways

- The family has 72 leaves for each created group: 2 rectangle-coordinate paths x 3 scissor paths x 2 modes x 6 counts.
- Static and dynamic discard-rectangle coordinates, and static and dynamic scissor state, are independently crossed.
- The workload is a fixed 340×100 red/green color image with horizontally generated rectangles.
- The verdict is an image comparison against `generateReferenceImage()`, with threshold `0.02` per channel.
- Missing functionality or insufficient `maxDiscardRectangles` is a support skip, not a failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Rectangle and reference generation | [`generateDiscardRectangles()` and `generateReferenceImage()`](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L348-L417) | Defines the fixed geometry and software oracle. |
| Runtime and comparison | [`DiscardRectanglesTestInstance::iterate()`](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L469-L640) | Creates resources, records rendering and copy commands, and applies the image verdict. |
| Dynamic commands | [`drawCommands()`](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L653-L671) | Sets dynamic rectangle coordinates and scissor state before the draw. |
| Shaders, support, and leaves | [Case implementation and `createTests()`](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L727-L831) | Defines generated programs, capability checks, and all 72 leaf names. |
| Test-family factory | [`createDiscardRectanglesTests()`](../../../modules/vulkan/draw/vktDrawDiscardRectanglesTests.cpp#L834-L837) | Names the `discard_rectangles` test family. |
| Draw dispatcher | [`createChildren()` and rendering arrangements](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L199) | Selects the render-pass and dynamic-rendering scopes and excludes nested-secondary variants. |
| Vulkan default mustpass | [Draw list](../../../mustpass/main/vk-default/draw.txt) | Includes 72 leaves in each of four arrangements. |
| Vulkan SC default mustpass | [Draw list](../../../mustpass/main/vksc-default/draw.txt) | Includes the 72 render-pass leaves. |
| Supporting analysis | [Understanding Brief](DiscardRectanglesTests_brief.md) | Records the pre-rewrite source model and audit risks. |
| Vulkan semantics | [Discard rectangles test](https://registry.khronos.org/vulkan/specs/latest/html/chapters/fragops.html#fragops-discard-rectangles) | Defines inclusive/exclusive coverage, coordinate delivery, and ordering before scissoring. |
