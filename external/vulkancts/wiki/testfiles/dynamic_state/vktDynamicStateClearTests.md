# vktDynamicStateClearTests.cpp

## Overview

[`vktDynamicStateClearTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L1) implements the [`image`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L472) subgroup of the dynamic_state category. It tests that dynamic state (specifically blend constants) is not disturbed by intervening image manipulation commands such as clear, blit, copy, and resolve operations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateClearTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)

## Registration Path

This file contributes the [`DynamicStateClearTests`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L470) group (named `"image"`), which is attached under each pipeline construction type subgroup by [`createChildren()`](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L55).

## Test Hierarchy

```text
image
├── clear
├── blit
├── copy
└── resolve
```

Source: [`DynamicStateClearTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L478).

## Test Families

### 1. Clear

[`clear`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L485) uses [`ClearTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L180). Sets dynamic states (viewport, scissor, line width, blend constants, depth/stencil), then calls `vkCmdClearAttachments` inside a render pass. Verifies that the dynamic blend constants remain in effect when a line is drawn after the clear operation.

### 2. Blit

[`blit`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L489) uses [`BlitTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L236). Sets dynamic states, then calls `vkCmdBlitImage` outside the render pass. Verifies that the dynamic blend constants are not disturbed by the blit operation.

### 3. Copy

[`copy`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L493) uses [`CopyTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L299). Sets dynamic states, then calls `vkCmdCopyImage` outside the render pass. Verifies that the dynamic blend constants are not disturbed by the copy operation.

### 4. Resolve

[`resolve`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L497) uses [`ResolveTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L359). Sets dynamic states, then calls `vkCmdResolveImage` outside the render pass. Uses `VK_SAMPLE_COUNT_2_BIT` for the multisample source image. Verifies that the dynamic blend constants are not disturbed by the resolve operation.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Dynamic blend constants | `(0.75f, 0.75f, 0.75f, 0.75f)` set via [`setDynamicBlendState()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L102) |
| Blend configuration | `SRC_ALPHA * CONSTANT_COLOR + CONSTANT_ALPHA` ([L62-L68](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L62)) |
| Sample count | `VK_SAMPLE_COUNT_1_BIT` (clear, blit, copy), `VK_SAMPLE_COUNT_2_BIT` (resolve) |
| Image format | `VK_FORMAT_R8G8B8A8_UNORM` |
| Render dimensions | 128x128 |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| clear, blit, copy | `VK_FORMAT_R8G8B8A8_UNORM` with `VK_SAMPLE_COUNT_1_BIT` support for color attachment + transfer | [`commonCheckSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L460) |
| resolve | `VK_FORMAT_R8G8B8A8_UNORM` with `VK_SAMPLE_COUNT_2_BIT` support | [`resolveCheckSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L465) |

## Verification Methods

All four test families use **fuzzy image comparison** via [`tcu::fuzzyCompare()`](../../../modules/vulkan/dynamic_state/vktDynamicStateClearTests.cpp#L166) with threshold `0.05f`:

1. Set dynamic states (viewport, scissor, line width, blend constants, depth/stencil).
2. Execute the image manipulation command (clear/blit/copy/resolve).
3. Draw a line using the pipeline with dynamic blend constants.
4. Build a software reference frame encoding the expected blended result.
5. Compare the rendered image against the reference.

The core verification principle: dynamic blend constants set before the image manipulation command must remain in effect when the line is drawn afterward, proving that the intervening command did not disturb the dynamic state.

## Test Principles Observed

- **Dynamic state preservation across commands**: Tests verify that image manipulation commands (clear, blit, copy, resolve) do not disturb previously set dynamic state.
- **Blend constant sensitivity**: The blend configuration uses `CONSTANT_COLOR` and `CONSTANT_ALPHA` factors, making the output directly dependent on the dynamic blend constants.
- **Inside and outside render pass**: The clear test exercises the command inside a render pass, while blit/copy/resolve exercise it outside.

## Notes / Uncertainties

- The group name `"image"` may be confusing since the category is about dynamic state, not image tests. The name likely refers to the image manipulation commands being tested for their non-interference with dynamic state.
