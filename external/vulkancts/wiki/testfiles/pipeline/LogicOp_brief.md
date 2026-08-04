# Understanding Brief: pipeline logic operations

## One-Sentence Test Purpose

This source file checks that a Vulkan implementation applies each static `VkLogicOp` to integer color attachments and leaves floating-point and sRGB color attachments unaffected when a logic operation is enabled.

## Background Knowledge

### Fixed-function logical operations

`logicOpEnable` and `logicOp` in `VkPipelineColorBlendStateCreateInfo` select a bitwise operation between the fragment output and the value already held by a color attachment. Vulkan applies these operations only to signed and unsigned integer color formats; it does not apply them to floating-point or sRGB color formats. `logicOp` support is also a device feature requirement.

Why it matters here:

- `logic_op` checks the computed bitwise result on UINT attachments.
- `logic_op_na_formats` checks that an enabled operation does not alter the normal float or sRGB output path.

### A logic operation needs a source and a destination

The fragment shader supplies the source color through a push constant. A render pass clear supplies the destination color. For each used attachment component, the integer family evaluates the selected operation and masks the result to the component width. The test deliberately uses values whose high and low nibbles contain different patterns, so a channel mix-up can change the result.

## One Concrete Example

A representative `logic_op` leaf is:

```text
dEQP-VK.pipeline.monolithic.logic_op.r8g8b8a8_uint.xor
```

The host clears a 32 by 32 `VK_FORMAT_R8G8B8A8_UINT` attachment with `kFbColor`, pushes `kQuadColor`, and draws a full-screen strip. The pipeline enables `VK_LOGIC_OP_XOR`. The reference image applies `calcOpResult(VK_LOGIC_OP_XOR, kQuadColor[c], kFbColor[c])` for each channel and then applies the 8-bit channel mask. `tcu::intThresholdCompare` uses a zero threshold.

For an inapplicable-format leaf such as `dEQP-VK.pipeline.monolithic.logic_op_na_formats.r8_srgb.xor_blend`, the pipeline still enables a logic operation. Because `logicOpEnable == VK_TRUE` disables blending, the expected image contains the fragment color, converted with `tcu::linearToSRGB` for the sRGB target, even for `_blend` leaves. Those leaves use source factor `ZERO` and destination factor `ONE`, so an implementation that incorrectly performs blending would preserve the clear color and become observable. The selected blend state still changes the format-support gate even though blending must not execute.

## End-to-End Test Flow

```text
[host] choose a construction type, attachment format, `VkLogicOp`, and, for inapplicable formats, blend flag
[host] require `logicOp`, pipeline-construction support, color-attachment support, and blend support when selected
[host] compile the small vertex and fragment programs
[host] allocate a 32 by 32 color attachment, image view, render pass, layouts, pipeline, command pool, and command buffer
[device] clear the attachment, receive the push-constant source color, and draw a full-screen triangle strip
[device] apply the enabled logic operation only when the attachment format permits it
[host] submit, wait, read the attachment, build a reference image, and compare it
```

## Generated Test Artifacts and Bound Resources

### Generated program artifacts

- `LogicOpTest::initPrograms()` emits a GLSL 4.30 vertex shader that makes a full-screen strip and a fragment shader that writes `uvec4 QUAD_COLOR.val`.
- `LogicOpInapplicableFormatsTest::initPrograms()` uses the same vertex shape and emits a fragment output type that matches the number of attachment components and whether the format is integer or floating point.
- The shaders provide source values only. The tested logic operation runs in fixed-function color output state.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color attachment image | yes | yes | clear and color output write it | yes | Holds the destination before the draw and the final result after it. |
| Image view and render pass | yes | yes | rendering uses them | no | Connect the selected format to the single color attachment. |
| Push-constant range and values | yes | yes | fragment shader reads them | no | Carry `quadColor`, the logic-operation source. |
| `VkPipelineColorBlendStateCreateInfo` | yes | yes | fixed-function output state reads it | no | Enables `logicOp` and selects its operation. |
| Command buffer | yes | yes | queue executes it | no | Records the clear, push constants, bind, and draw. |

## What Is Checked

- `logic_op` reads the UINT attachment, computes every component from the selected `VkLogicOp`, and performs `tcu::intThresholdCompare` with zero threshold.
- `logic_op_na_formats` expects the pushed fragment color rather than a bitwise or blended result. `logicOpEnable == VK_TRUE` disables blending; the `_blend` state uses `ZERO` source and `ONE` destination factors to expose an implementation that blends anyway. The oracle converts the fragment color for sRGB attachments and uses `tcu::floatThresholdCompare` with threshold `0.01f`.
- The inapplicable-format family runs every operation with `_noblend` and `_blend`; the latter additionally requires `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BLEND_BIT`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `logic_op`, `logic_op_na_formats`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `logic_op` | Incorrect operation selection or per-component integer evaluation, incorrect channel-width masking, color-attachment setup, or readback/reference comparison. |
| `logic_op_na_formats` | A logical operation is incorrectly applied to floating-point or sRGB output, blending incorrectly remains active while `logicOpEnable` is true, sRGB conversion differs from the expected value, blend-support gating is wrong, or readback/reference comparison is incorrect. |

## Important Variations and Special Cases

- `logic_op` has 14 registered UINT formats, 16 operations per format, giving 224 leaves for each construction root.
- `logic_op_na_formats` has 18 float or sRGB formats, 16 operations, and both blend choices, giving 576 leaves for each construction root.
- Each inspected mustpass file contains exactly 800 leaves from this source file: 224 `logic_op` leaves plus 576 `logic_op_na_formats` leaves. The inspected roots are `monolithic`, `pipeline_library`, `fast_linked_library`, and the four shader-object roots.
- The source registers these families under every construction type passed to `createChildren()`; actual mustpass roots demonstrate the construction variants selected by the configuration.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Logical-operation implementation and format checks | [logic-op source](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L56-L226) | Defines feature, attachment-format checks, and generated programs. |
| UINT runtime and oracle | [`LogicOpTestInstance`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L267-L503) | Creates the draw, records the command buffer, and computes the exact integer reference. |
| Inapplicable-format support and oracle | [`LogicOpInapplicableFormatsTest`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L551-L876) | Adds optional blend support and expects the unmodified float or sRGB output. |
| Registration | [`createLogicOpTests()` and `createLogicOpInapplicableFormatsTests()`](../../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L886-L1030) | Defines operations, formats, and registered leaves. |
| Vulkan logical-operation contract | [Logical Operations](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1676-L1756) | States applicable format classes and source/destination behavior. |
| Mustpass evidence | [pipeline mustpass files](../../../mustpass/main/vk-default/pipeline/) | Supplies selected registered leaves across construction roots. |

## Questions / Risk Points for User Audit

- The page uses the two registered families as its behavior axis; format, operation, and blend choice remain parameter dimensions.
- The full-screen shaders are intentionally not given a shader walkthrough or SPIR-V block because they only provide the source color. The fixed-function output stage performs the tested operation.
- `shader_object_unlinked_spirv` has 836 broad pattern matches due to its broader root contents; the ordinary source-family count is 800 in the directly comparable mustpass roots.

## Conversion Notes for Final Wiki Rewrite

- Keep the two-row Failure Cause Mapping table unchanged in the final page.
- Use a compact representative registration tree and keep all complete format/operation coverage in parameter prose.
- Link the format-applicability claim to the narrow Logical Operations specification range.
- Explain the difference between the exact UINT oracle and the float/sRGB no-effect oracle.
