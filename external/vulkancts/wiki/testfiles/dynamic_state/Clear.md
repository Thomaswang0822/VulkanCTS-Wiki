## Overview

**Core question:** Do image manipulation commands (clear, blit, copy, resolve) corrupt dynamic blend constants that were set earlier in the same command buffer?

This page covers the `image` test family in the `dynamic_state` test category, implemented in [`vktDynamicStateClearTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L1). The test family registers four test case leaves: `clear`, `blit`, `copy`, and `resolve`. Each leaf sets dynamic blend constants, executes one image manipulation command, then draws a line and checks that the blend constants are still in effect.

The four leaves differ only in which Vulkan command runs between state setup and the draw. The shaders are trivial passthrough; the tested behavior lives entirely in fixed-function blend state, not shader code.

## Background Knowledge

- **Dynamic blend constants** are a programmable blend factor set at command buffer recording time via `vkCmdSetBlendConstants`. They are read by blend factors such as `VK_BLEND_FACTOR_CONSTANT_COLOR` and `VK_BLEND_FACTOR_ONE_MINUS_CONSTANT_COLOR`. A correct implementation must preserve these constants across all commands recorded in the same command buffer until the application explicitly changes them.
- **Fixed-function blend** combines the fragment shader output (source) with the existing framebuffer contents (destination) using configurable factors and operations. This test configures both source and destination factors to reference the dynamic blend constants, so any corruption of those constants changes the final pixel color.
- **Image manipulation commands** (`vkCmdClearAttachments`, `vkCmdBlitImage`, `vkCmdCopyImage`, `vkCmdResolveImage`) operate on image memory and are not expected to touch graphics pipeline dynamic state. This test family verifies that expectation by placing each command between dynamic state setup and a draw that depends on that state.

## Registration Hierarchy

```text
dynamic_state.monolithic.image
├── clear
├── blit
├── copy
└── resolve
```

Source: [`DynamicStateClearTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L478). The `image` test family is registered as a `TestCaseGroup` named `"image"` ([L472](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L472)). The four leaves are registered as direct children. Each pipeline construction type variant (`monolithic`, `pipeline_library`, `fast_linked_library`, shader object variants) registers the same four leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image manipulation command | `clear`, `blit`, `copy`, `resolve` | The primary behavioral axis: each leaf inserts a different Vulkan command between dynamic state setup and the draw | [L485-L498](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L485) |
| Pipeline construction type | `monolithic`, `pipeline_library`, `fast_linked_library`, shader object variants | Inherited from the parent group; does not change test logic, only pipeline build path | [L470-L473](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L470) |
| Dynamic blend constants | `(0.75, 0.75, 0.75, 0.75)` | Set once before the image command; the draw output is directly sensitive to these values | [`setDynamicBlendState()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L102) |
| Blend factors | `ONE_MINUS_CONSTANT_COLOR` (both src and dst color), `ONE_MINUS_CONSTANT_ALPHA` (both src and dst alpha) | Both source and destination are scaled by the blend constants, making any corruption visible | [L63-L68](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L63) |
| Sample count | `VK_SAMPLE_COUNT_1_BIT` (clear, blit, copy), `VK_SAMPLE_COUNT_2_BIT` (resolve) | Resolve requires a multisample source image | [L177](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L177), [L368](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L368) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixed across all leaves | [L450](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L450) |
| Render dimensions | 128 x 128 | Inherited from the base class | [`WIDTH`/`HEIGHT`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L90) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf inserts a different image manipulation command between dynamic blend constant setup and the line draw. The test principle is identical across all four: if the intervening command corrupted the blend constants, the drawn line would have the wrong color and the reference comparison would fail.

### clear: clear attachments inside the render pass

The `clear` leaf calls [`vkCmdClearAttachments`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L206) to set the color attachment to white `(1, 1, 1, 1)` inside the active render pass, after dynamic state has been set and after the render pass has begun ([`ClearTestInstance::command(true)`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L190)). The line is then drawn over the white background.

This is the only leaf that runs its image command inside the render pass. Because the attachment is cleared to white, the green line source `(0, 1, 0, 1)` blends against white, producing expected line pixels of `(0.25, 0.5, 0.25, 0.5)`.

### blit: blit image outside the render pass

The `blit` leaf calls [`vkCmdBlitImage`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L270) outside the render pass, after dynamic state setup but before the render pass begins ([`BlitTestInstance::command(false)`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L246)). The blit copies from the color target image to a scratch image using `VK_FILTER_NEAREST`.

The blit destination image is not used by the render pass. The render pass clears the color target to black, so the green line blends against black, producing expected line pixels of `(0.0, 0.25, 0.0, 0.5)`.

### copy: copy image outside the render pass

The `copy` leaf calls [`vkCmdCopyImage`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L330) outside the render pass, using the same timing pattern as `blit` ([`CopyTestInstance::command(false)`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L309)). The copy moves pixel data from the color target image to a scratch image.

Like `blit`, the copy destination is not consumed by the render pass, and the expected line pixels are `(0.0, 0.25, 0.0, 0.5)` against the black render pass clear.

### resolve: resolve multisample image outside the render pass

The `resolve` leaf calls [`vkCmdResolveImage`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L391) outside the render pass, resolving from a `VK_SAMPLE_COUNT_2_BIT` multisample scratch image to the color target image ([`ResolveTestInstance::command(false)`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L371)). A pipeline barrier transitions the source image layout after the resolve ([L413](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L413)).

The render pass then clears the color target to black, overwriting the resolve result. The expected line pixels are `(0.0, 0.25, 0.0, 0.5)`, the same as `blit` and `copy`.

## Shader Analysis

The test uses shared passthrough shaders [`VertexFetch.vert`](../../../data/vulkan/dynamic_state/VertexFetch.vert) and [`VertexFetch.frag`](../../../data/vulkan/dynamic_state/VertexFetch.frag). The vertex shader copies `in_position` to `gl_Position` and passes `in_color` through; the fragment shader writes `in_color` directly to its output.

Shader code is not part of the tested behavior. The blend operation happens in the fixed-function output merger, configured by the pipeline's color blend state and the dynamic blend constants. No shader walkthrough is needed.

## Runtime Execution and Result Checking

All four leaves share one execution flow in [`CmdBaseCase::iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L83):

1. Begin the command buffer and set all dynamic states: viewport, scissor, line width (to the device maximum), blend constants `(0.75, 0.75, 0.75, 0.75)`, and depth/stencil bounds ([L100-L103](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L100)).
2. Create a scratch image (`m_image`) and transition both the color target image and the scratch image to `VK_IMAGE_LAYOUT_GENERAL` with appropriate access masks ([L105-L134](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L105)).
3. Call `command(false)`. For `blit`, `copy`, and `resolve`, this executes the image manipulation command outside the render pass. For `clear`, this call does nothing.
4. Begin the render pass with a clear color of black `(0, 0, 0, 1)`.
5. Call `command(true)`. For `clear`, this executes `vkCmdClearAttachments` inside the render pass, setting the attachment to white. For the other three leaves, this call does nothing.
6. Bind the pipeline, bind the vertex buffer, and draw two vertices as a line (`VK_PRIMITIVE_TOPOLOGY_LINE_LIST`).
7. End the render pass, end the command buffer, and submit.
8. Read back the color target image and compare it against a software reference frame using [`tcu::fuzzyCompare()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L166) with threshold `0.05f`.

Each leaf builds its own reference frame in a `buildReferenceFrame()` override. The reference encodes the expected blended line color against the correct background (white for `clear`, black for the other three). The pass condition is a successful fuzzy comparison.

## Failure Meaning

### Failure Cause Mapping

| If this test case leaf fails | Possible failure cause(s) |
|------------------------------|---------------------------|
| `clear` | Dynamic blend constants were corrupted by `vkCmdClearAttachments`, or the clear attachment value was not applied correctly |
| `blit` | Dynamic blend constants were corrupted by `vkCmdBlitImage` |
| `copy` | Dynamic blend constants were corrupted by `vkCmdCopyImage` |
| `resolve` | Dynamic blend constants were corrupted by `vkCmdResolveImage` or the post-resolve pipeline barrier |

All four leaves share one underlying failure mechanism: the intervening image manipulation command disturbs the dynamic blend constants, causing the drawn line to use wrong blend factors and produce the wrong color.

### Cause Analysis

#### Dynamic blend constant corruption by an image command

**Possible failure symptoms:** The fuzzy image comparison reports a mismatch. The drawn line pixels differ from the expected blended color. Because the blend factors scale both source and destination by `ONE_MINUS_CONSTANT_COLOR` or `ONE_MINUS_CONSTANT_ALPHA`, any change to the blend constants from `(0.75, 0.75, 0.75, 0.75)` shifts the output away from the expected `(0.25, 0.5, 0.25, 0.5)` (clear) or `(0.0, 0.25, 0.0, 0.5)` (blit, copy, resolve).

**Possible implementation causes:** A driver or hardware bug where recording an image manipulation command (`vkCmdClearAttachments`, `vkCmdBlitImage`, `vkCmdCopyImage`, or `vkCmdResolveImage`) incorrectly overwrites or invalidates the command buffer's stored dynamic blend constant state. The Vulkan specification requires that dynamic state set by `vkCmdSetBlendConstants` persists until explicitly changed, regardless of what other commands are recorded. If a driver shares state storage between transfer or clear command handling and graphics dynamic state in a way that clobbers the blend constants, this test would catch it.

#### Incorrect clear attachment application (clear leaf only)

**Possible failure symptoms:** For the `clear` leaf specifically, if `vkCmdClearAttachments` does not set the attachment to white `(1, 1, 1, 1)` as expected, the line would blend against the wrong background color and the reference comparison would fail.

**Possible implementation causes:** A driver bug where `vkCmdClearAttachments` inside a render pass does not write the specified clear value, or writes it to the wrong region. This is a separate failure surface from blend constant corruption and would only affect the `clear` leaf.

## Case Pruning

### Requirement-based pruning

All four leaves check that `VK_FORMAT_R8G8B8A8_UNORM` supports the required sample count for color attachment and transfer usage ([`checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L445)). The `clear`, `blit`, and `copy` leaves require `VK_SAMPLE_COUNT_1_BIT` ([`commonCheckSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L460)). The `resolve` leaf requires `VK_SAMPLE_COUNT_2_BIT` ([`resolveCheckSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L465)). If the format does not support the needed sample count, the leaf is skipped with `NotSupportedError`.

### Design-based pruning

No design-based pruning applies. Each leaf is a single fixed test case with no generated parameter matrix.

## Key Takeaways

- All four leaves test the same property from different angles: an image manipulation command recorded between dynamic blend constant setup and a dependent draw must not change those constants.
- The blend configuration makes the output directly sensitive to the constants: both source and destination are scaled by `ONE_MINUS_CONSTANT_COLOR` and `ONE_MINUS_CONSTANT_ALPHA`, so any corruption shifts the line color away from the expected reference.
- The `clear` leaf is the only one that runs its command inside the render pass; `blit`, `copy`, and `resolve` run outside. All four execute on the universal queue; the split covers both render-pass-interior and render-pass-exterior recording points for the intervening command.
- The image operation results (blit, copy, resolve destinations) are deliberately not consumed by the render pass. Their sole purpose is to act as intervening commands that might corrupt dynamic state.
- See `## Failure Meaning` for the analysis of what a failure implies.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `DynamicStateClearTests::init()` | [`vktDynamicStateClearTests.cpp#L478`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L478) | Registers the four test case leaves under the `image` group |
| `CmdBaseCase::iterate()` | [`vktDynamicStateClearTests.cpp#L83`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L83) | Shared execution flow: set state, run image command, draw, compare |
| Blend state configuration | [`vktDynamicStateClearTests.cpp#L62-L68`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L62) | Sets the `ONE_MINUS_CONSTANT_COLOR` and `ONE_MINUS_CONSTANT_ALPHA` factors |
| `ClearTestInstance::command()` | [`vktDynamicStateClearTests.cpp#L190`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L190) | `vkCmdClearAttachments` inside the render pass |
| `BlitTestInstance::command()` | [`vktDynamicStateClearTests.cpp#L246`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L246) | `vkCmdBlitImage` outside the render pass |
| `CopyTestInstance::command()` | [`vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L309`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L309) | `vkCmdCopyImage` outside the render pass |
| `ResolveTestInstance::command()` | [`vktDynamicStateClearTests.cpp#L371`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L371) | `vkCmdResolveImage` outside the render pass |
| `checkSupport()` | [`vktDynamicStateClearTests.cpp#L445`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L445) | Format and sample count support check |
| Shared base class | [`vktDynamicStateBaseClass.hpp#L43`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Provides dynamic state setup, pipeline, render pass, and image infrastructure |
