## Overview

**Core question:** Does `vkCmdSetLineWidth` produce the exact requested line width, and does the result hold when a dynamic-width line and a static-width line are drawn into the same framebuffer in either draw order?

- [vktDynamicStateLineWidthTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L1) implements the `line_width` test family of the `dynamic_state` test category.
- The file draws a horizontal line with a dynamic-width pipeline and a vertical line with a static-width pipeline into a two-subpass render pass. It then counts the colored pixels along the framebuffer's first row and first column and compares the counts to the requested widths.
- Eight test cases cover every combination of `LINE_LIST` and `LINE_STRIP` topologies for the static and dynamic pipelines, in both dynamic-first and static-first draw order.
- The test requires the `wideLines` feature and line widths within the device's supported range.

## Background Knowledge

- **Wide lines.** Vulkan's core `wideLines` feature allows line rasterization with widths greater than 1.0. The supported range and granularity are reported in `VkPhysicalDeviceLimits::lineWidthRange` and `lineWidthGranularity`. A dynamic line width is set with `vkCmdSetLineWidth`; a static line width is set in `VkPipelineRasterizationStateCreateInfo::lineWidth` at pipeline creation.
- **Subpasses and draw order.** A render pass can contain multiple subpasses executed in sequence. Drawing the dynamic and static lines in separate subpasses lets the test vary which pipeline draws first, checking that the dynamic width applies regardless of draw order.

## Registration Hierarchy

```text
dynamic_state.monolithic.line_width
├── dyna_static
└── static_dyna
```

The two intermediate nodes group cases by draw order. The test family is registered once per pipeline construction type by the category dispatcher ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L508-L538)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Draw order | `dyna_static`, `static_dyna` | Selects whether the dynamic pipeline draws first (subpass 0) or second (subpass 1). This also controls the order of name components. | [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L523-L524) |
| Static topology | `LINE_LIST`, `LINE_STRIP` | Topology used by the static-width pipeline. | [params table](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L510-L521) |
| Dynamic topology | `LINE_LIST`, `LINE_STRIP` | Topology used by the dynamic-width pipeline. | [params table](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L510-L521) |
| Static line width | Odd integers 1, 3, 5, 7, 9, 11, 13, 15 | Assigned by the registration loop; baked into the static pipeline. | [width assignment](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L525-L530) |
| Dynamic line width | Even integers 2, 4, 6, 8, 10, 12, 14, 16 | Assigned immediately after the static width; set with `vkCmdSetLineWidth`. | [width assignment](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L525-L530) |
| Color format | `VK_FORMAT_R32G32B32A32_SFLOAT` | High-precision color so exact color equality can distinguish dynamic and static pixels. | [params table](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L510-L521) |
| Render dimensions | 128x128 | Fixed framebuffer size. | [params table](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L510-L521) |

Four topology-pair combinations times two draw-order variants yield 8 test cases. Case names encode topology and width, following [`TestLineWidthParams::rep()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L484-L506): dynamic-first names read `<dynamicTopo><dynamicWidth>_<staticTopo><staticWidth>` (for example `strip2_list1`), and static-first names read `<staticTopo><staticWidth>_<dynamicTopo><dynamicWidth>` (for example `list3_strip4`).

## Behavior Parameters

The primary behavioral axis is the draw order. The two intermediate nodes select whether the dynamic pipeline draws first or second, which changes whether the dynamic line width is set before or after the static pipeline binds.

### `dyna_static`: dynamic pipeline first, static pipeline second

The dynamic-width pipeline draws a horizontal line in subpass 0, and the static-width pipeline draws a vertical line in subpass 1. The horizontal line uses the dynamic color (magenta) and the vertical line uses the static color (green). Case names put the dynamic topology and width first ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L523)).

### `static_dyna`: static pipeline first, dynamic pipeline second

The static-width pipeline draws a vertical line in subpass 0, and the dynamic-width pipeline draws a horizontal line in subpass 1. Case names put the static topology and width first ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L524)).

## Shader Analysis

The shaders support the test rather than implement the tested property. The vertex shader takes a position and writes `gl_Position`; the fragment shader reads a push-constant color and writes it to the attachment ([shaders](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L428-L447)).

No representative shader walkthrough is included. Reconstructing the shader would explain line rasterization, but the tested property is whether the dynamic line width produced the expected pixel count, which is a host-side counting question.

## Runtime Execution and Result Checking

- `checkSupport()` requires the `wideLines` feature and verifies that both the static and dynamic widths fall within `VkPhysicalDeviceLimits::lineWidthRange`. It also checks pipeline construction requirements ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L449-L472)).
- `iterate()` builds the render pass with two subpasses and a subpass dependency, the color image and view, vertex buffers for the horizontal (dynamic) and vertical (static) lines, and both pipelines. The dynamic pipeline sets `lineWidth` to 0.0 at creation and records `VK_DYNAMIC_STATE_LINE_WIDTH`; the static pipeline bakes in its width ([buildPipeline](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L244-L280)).
- The command buffer begins the render pass, draws the first pipeline in subpass 0, transitions to subpass 1, draws the second pipeline, ends the render pass, inserts a barrier, and copies the image to a host-visible buffer. The draw order follows the selected intermediate node ([iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L319-L404)).
- `verifyResults()` counts pixels along the first column (x=0) matching the dynamic color and pixels along the first row (y=0) matching the static color. The dynamic count must equal the requested dynamic width and the static count must equal the requested static width. A mismatch logs the expected and measured counts and the result image ([verifyResults](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L282-L317)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dyna_static` | The dynamic line width was not applied when the dynamic pipeline drew first, or the dynamic and static pixel counts were confused. |
| `static_dyna` | The dynamic line width was not applied when the dynamic pipeline drew second, or the second-subpass draw did not use the recorded width. |
| Both | `vkCmdSetLineWidth` did not take effect, the wide-lines rasterization is wrong, or the pixel-counting logic is mismatched to the geometry. |

### Cause Analysis

#### Dynamic line width not applied

**Possible failure symptoms:** The measured dynamic pixel count differs from the requested dynamic width, while the static count matches.

**Possible implementation causes:** The implementation may ignore the recorded `vkCmdSetLineWidth`, apply a default width of 1.0, or fail to bind the dynamic state to the dynamic pipeline. The static pipeline is unaffected because its width is baked in, so a dynamic-only mismatch isolates the failure to the dynamic-state path. Whether the defect is in command recording or the wide-line rasterizer requires inspection against the `wideLines` feature contract.

#### Draw-order interaction

**Possible failure symptoms:** One intermediate node passes and the other fails, or the measured counts are swapped relative to the requested widths.

**Possible implementation causes:** The dynamic width may be applied in the wrong subpass, or the second draw may inherit state from the first pipeline. Because the test swaps draw order between the two intermediate nodes, a failure that appears under only one of them points at a subpass or pipeline-binding interaction rather than the width command itself.

#### Static width also wrong

**Possible failure symptoms:** Both the dynamic and static counts are wrong, or neither matches its requested width.

**Possible implementation causes:** The wide-line rasterization may be generally broken on the device, or the line geometry may not line up with the counted row and column. The static pipeline does not use dynamic state, so a static-width error points at the rasterizer or geometry rather than `vkCmdSetLineWidth`.

## Case Pruning

### Requirement-based pruning

- All cases require the `wideLines` feature.
- Both the static and dynamic widths must fall within `VkPhysicalDeviceLimits::lineWidthRange`. Cases whose widths fall outside the range raise `NotSupportedError` at runtime ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L457-L463)).
- Pipeline construction requirements are checked.

### Design-based pruning

- Widths are fixed odd/even pairs assigned by the registration loop. The test does not scan a continuous range; it checks a representative set of widths that exercise wide-line rasterization.
- The dynamic line is always drawn horizontally and the static line vertically, so their pixel counts can be read from orthogonal framebuffer axes without overlap interference.

## Key Takeaways

- The draw order is the behavioral axis, but every case tests the same property: `vkCmdSetLineWidth` must produce exactly the requested pixel count.
- Drawing the dynamic and static lines in separate subpasses, in both orders, checks that the dynamic width applies regardless of when it is set relative to the static draw.
- Exact pixel counting along the first row and column avoids fuzzy comparison. A correct wide-line implementation produces an integer pixel count equal to the requested width.
- A dynamic-only failure isolates the defect to the dynamic-state path; a static-and-dynamic failure points at the wide-line rasterizer or the line geometry.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateLWTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L508-L538) | Registers the two draw-order nodes and the eight topology/width cases. |
| Support checks | [`LineWidthCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L449-L472) | `wideLines` feature and `lineWidthRange` checks. |
| Case naming | [`TestLineWidthParams::rep()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L484-L506) | Encodes topology and width in the registered case name. |
| Pipeline build | [`LineWidthInstance::buildPipeline()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L244-L280) | Static vs. dynamic line-width pipeline construction. |
| Pixel counting | [`LineWidthInstance::verifyResults()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L282-L317) | Row/column pixel-count comparison and failure logging. |
| Command recording | [`LineWidthInstance::iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L319-L404) | Two-subpass render pass and draw-order selection. |
| Shaders | [vert/frag](../../../modules/vulkan/dynamic_state/vktDynamicStateLineWidthTests.cpp#L428-L447) | Position-only vertex and push-constant-color fragment shaders. |
