## Overview

**Core question:** Does Vulkan apply the selected stencil state to each fragment and leave coverage unchanged when no stencil attachment exists?

- [`vktPipelineStencilTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1) implements the `pipeline.*.stencil` family.
- `format` and `nocolor` vary stencil operations, comparisons, masks, references, formats, and layouts, then compare GPU results with `ReferenceRenderer`.
- The `no_stencil_att` intermediate node enables stencil testing without a stencil attachment and checks that the draw's color and depth results remain correct.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A stencil test masks the attachment value and reference, compares them with `VkCompareOp`, and can remove sample coverage. If the comparison fails, Vulkan uses `failOp`; if it passes, Vulkan chooses `depthFailOp` or `passOp` according to the depth-test result. The write mask limits the update to the stencil attachment.
- Vulkan selects front or back stencil state from polygon facing. A test can therefore require different operations, masks, and references for the two faces.
- If no stencil attachment is present, the stencil test leaves the coverage mask unmodified. The `no_stencil_att` family tests that rule directly.

## Registration Hierarchy

```text
pipeline.monolithic.stencil
├── format
├── nocolor
└── no_stencil_att
```

[`createStencilTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1469-L1664) builds the same `stencil` family for the applicable pipeline-construction variants. Mustpass entries occur in `monolithic`, `pipeline_library`, `fast_linked_library`, and `shader_object_unlinked_spirv`; `no_stencil_att` has the narrower construction-type coverage recorded below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `format`, `nocolor`, `no_stencil_att` | Selects normal stencil testing with color, normal stencil testing without color, or the missing-stencil-attachment rule. | [`createStencilTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1482-L1664) |
| Stencil format | `s8_uint`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint` | Tests stencil-only and combined depth/stencil formats. | [`formats::stencilFormats` loop](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1492-L1500) |
| Main stencil state | 8 `VkStencilOp` values for each of `failOp`, `passOp`, and `depthFailOp`; 8 `VkCompareOp` values | Selects the state-machine branch and resulting stencil update. The front state follows the nested loops; the back state comes from a deterministic seeded permutation. | [`stencilOps`, `compareOps`, and iterator](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L179-L235) |
| Attachment arrangement | color enabled or disabled | Distinguishes `format` from `nocolor` while retaining the stencil attachment. | [`colorAttachmentEnabled`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1485-L1487) |
| Layout | `any`, `general`; separate-layout suffix for combined formats | Tests ordinary attachment layout use, a bounded `GENERAL` subset, and separate depth/stencil layouts when available. | [layout loop](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1571-L1586) |
| `no_stencil_att` mode | `render_passes` or `dynamic_rendering`; `static_enable` or `dynamic_enable` | Checks no-attachment behavior through render-pass or dynamic-rendering setup and static or dynamic stencil enable. | [special-family registration](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1612-L1659) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node beneath the `stencil` test family. The operation, comparison, format, and layout dimensions expand each intermediate node's coverage.

### `format` - stencil with a color attachment

This intermediate node checks normal stencil behavior while fragment output also writes a color attachment. It draws four overlapping quads, supplies distinct front/back masks and references in each quad's pipeline state, and checks color plus stencil output against a software rasterizer.

### `nocolor` - stencil without a color attachment

This intermediate node uses the same stencil-state matrix without binding a color attachment. It isolates whether stencil operations continue to work when no color output attachment participates in rendering.

### `no_stencil_att` - enabled stencil test without a stencil attachment

This intermediate node configures stencil test enable even though the rendering setup provides no stencil attachment. The specification requires unmodified coverage in this condition, so the full-screen triangle must still produce the expected blue color and depth result. If the backing depth format also has a stencil aspect, that aspect must retain its clear value.

## Shader Analysis

The GLSL shaders are not the tested behavior. Main-matrix shaders pass positions and, when present, color to the fragment output; stencil comparison and update occur in fixed-function fragment operations. The `no_stencil_att` shaders only draw a full-screen blue triangle at pushed depth `0.75`. No representative shader walkthrough or SPIR-V disassembly would audit the stencil property, so this page has none.

## Runtime Execution and Result Checking

- Main-matrix cases create a stencil or depth/stencil image and, for `format`, a color image. The command buffer transitions attachments, clears them, begins rendering, and draws four quads. Each draw binds its matching pipeline and vertex-buffer slice.
- Each quad's pipeline carries that quad's front/back compare masks, write masks, and references. The selected case supplies the operation and comparison choices.
- After queue completion, `verifyImage()` configures `ReferenceRenderer` with the same front/back operation state and per-quad mask/reference values. It compares read-back stencil output in all cases and color output when present with `intThresholdPositionDeviationCompare`, threshold `(2, 2, 2, 2)` and position deviation `(1, 1, 0)`.
- `no_stencil_att` clears color to black, depth to `0.5`, and an available stencil aspect to `255`; its vertex shader draws at depth `0.75`. It copies results to host-visible buffers and expects blue color, depth `0.75` within `0.000025`, and an unchanged available stencil aspect of `255`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `format` | Incorrect front/back stencil comparison, operation selection, masked update, layout handling, or color-and-stencil attachment interaction. |
| `nocolor` | Incorrect stencil behavior when no color attachment is present, including attachment setup or fixed-function execution that depends on color output. |
| `no_stencil_att` | Stencil test changes coverage or attachment contents despite the absence of a stencil attachment, or static/dynamic enabling diverges from the required behavior. |

### Cause Analysis

#### Stencil state evaluation or update

**Possible failure symptoms:** The read-back stencil image, and color image for `format`, differs from the reference after one or more quad draws.

**Possible implementation causes:** The implementation may select the wrong front/back state, mask the reference or attachment value incorrectly, choose the wrong operation after stencil or depth failure, or merge the generated value with the attachment using the wrong write mask. These are the stages defined by the Vulkan stencil-test rules.

#### Attachment arrangement or layout handling

**Possible failure symptoms:** A mismatch appears only in `format`, only in `nocolor`, or only for a format/layout suffix.

**Possible implementation causes:** Attachment setup, format support, aspect selection, or layout handling may differ between color-plus-stencil and stencil-only rendering. A source-level investigation is needed to localize a failure beyond the observed family, format, and layout.

#### Missing stencil attachment handling

**Possible failure symptoms:** `no_stencil_att` returns unexpected color, depth, or an available stencil value after the draw.

**Possible implementation causes:** The implementation may let enabled stencil state reject coverage despite no stencil attachment, may apply an operation to an absent attachment, or may handle static and dynamic stencil enable differently. The specification states that no stencil attachment leaves coverage unmodified.

## Case Pruning

### Requirement-based pruning

- Main-matrix cases require depth/stencil attachment support for the chosen format. Separate layouts require `VK_KHR_separate_depth_stencil_layouts`; portability-subset implementations also need `separateStencilMaskRef` when the test uses separate mask/reference values.
- `no_stencil_att.dynamic_rendering` requires `VK_KHR_dynamic_rendering`. Its `dynamic_enable` cases require `VK_EXT_extended_dynamic_state` unless shader objects provide the corresponding state path.
- The special family registers only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction types. Shader-object variants omit `render_passes`; Vulkan SC omits `dynamic_rendering`.

### Design-based pruning

- The full `any` layout matrix covers all operation and comparison combinations. `general` covers only indices `0` through `2` in each of its four state dimensions, which bounds that supplementary layout coverage.
- Separate-depth/stencil-layout cases occur only for formats that contain both aspects. Classic render-pass `no_stencil_att` cases skip depth formats that also contain a stencil aspect because that path cannot declare a separate missing stencil attachment.

## Key Takeaways

- The main matrix tests the fixed-function stencil state machine, including independent front/back state, rather than shader stencil code.
- `format` and `nocolor` use the same reference-rendered stencil oracle while changing whether color attachment output is present.
- `no_stencil_att` checks the explicit Vulkan rule that an enabled stencil test cannot alter coverage when rendering has no stencil attachment.

## Source Reference Appendix

| Topic | Source link | Purpose |
|-------|-------------|---------|
| Registration and matrix generation | [`createStencilTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1469-L1664) | Defines hierarchy, formats, operation loops, layouts, and special-family gates. |
| Main support checks and shader setup | [`StencilTest::checkSupport()` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L265-L328) | Shows requirements and the shaders' limited observability role. |
| Main draw and reference oracle | [`StencilTestInstance::iterate()` and `verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L755-L880) | Records four draws and compares GPU images with `ReferenceRenderer`. |
| Missing-attachment setup and checks | [`NoStencilAttachmentInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1036-L1427) | Defines dynamic/static enable, rendering paths, readback, and expected values. |
| Vulkan semantics | [`Stencil Test`](../../../../vulkan-docs/src/chapters/fragops.adoc#L1508-L1590) | Defines state selection, comparison, operation choice, masks, and no-attachment behavior. |
| Mustpass evidence | [`pipeline mustpass files`](../../../mustpass/main/vk-default/pipeline/) | Contains selected registered `pipeline.*.stencil` cases for the relevant variants. |
