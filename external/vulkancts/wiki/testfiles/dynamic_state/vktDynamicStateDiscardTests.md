# vktDynamicStateDiscardTests.cpp

## Overview

[`vktDynamicStateDiscardTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L1) implements the [`discard`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L749) subgroup of the dynamic_state category. It tests that dynamic state modifications have no visible effect when all fragments are discarded by the fragment shader, verifying that the discard operation correctly prevents any state-dependent output.

## Role

Implementation file.

## Source Code

- Primary source: [`vktDynamicStateDiscardTests.cpp`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L1)
- Shared base: [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)

## Registration Path

This file contributes the [`DynamicStateDiscardTests`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L747) group (named `"discard"`), which is attached under each pipeline construction type subgroup by [`createChildren()`](../../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L56).

## Test Hierarchy

```text
discard
├── stencil
├── viewport
├── scissor
├── depth
├── blend
└── line
```

Source: [`DynamicStateDiscardTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L759).

## Test Families

### 1. Stencil discard

[`stencil`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L762) uses [`StencilTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L360). Sets dynamic stencil compare mask, write mask, and reference via `vkCmdSetStencilCompareMask`, `vkCmdSetStencilWriteMask`, `vkCmdSetStencilReference`. Verifies that the stencil attachment remains at its clear value (0) since all fragments are discarded.

### 2. Viewport discard

[`viewport`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L765) uses [`ViewportTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L421). Sets dynamic viewport via `vkCmdSetViewport`. Verifies that the color attachment remains at its clear value (black) since all fragments are discarded.

### 3. Scissor discard

[`scissor`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L768) uses [`ScissorTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L476). Sets dynamic scissor via `vkCmdSetScissor`. Verifies that the color attachment remains at its clear value since all fragments are discarded.

### 4. Depth discard

[`depth`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L771) uses [`DepthTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L531). Sets dynamic depth bias and depth bounds via `vkCmdSetDepthBias`, `vkCmdSetDepthBounds`. Verifies that the depth attachment remains at its clear value (0.0f) since all fragments are discarded.

### 5. Blend discard

[`blend`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L773) uses [`BlendTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L572). Sets dynamic blend constants via `vkCmdSetBlendConstants`. Verifies that the color attachment remains at its clear value since all fragments are discarded.

### 6. Line discard

[`line`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L776) uses [`LineTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L616). Sets dynamic line width via `vkCmdSetLineWidth`. Verifies that the color attachment remains at its clear value since all fragments are discarded.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Pipeline construction type | Passed from parent group |
| Dynamic state type | 6 values from [`TestDynamicStateDiscard`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L51) enum |
| Dynamic states per test | Stencil: compare mask + write mask + reference; Viewport: viewport; Scissor: scissor; Depth: depth bias + depth bounds; Blend: blend constants; Line: line width |
| Depth/stencil format | Runtime-selected via [`pickSupportedStencilFormat()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L61) (stencil, viewport, scissor, blend, line); `VK_FORMAT_D32_SFLOAT` (depth) |
| Render dimensions | 128x128 |

## Support / Feature Requirements

| Test | Requirement | Check Function |
|---|---|---|
| All tests | Pipeline construction requirements | [`DiscardTestCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L671) |

Additionally, the stencil test queries the device's `depthBounds` feature at runtime to configure the pipeline's depth bounds test state.

## Verification Methods

All test instances verify that **fragments were discarded** by checking that the relevant attachment remains at its clear value:

| Test | What is verified | Expected value |
|---|---|---|
| Stencil | Stencil aspect of depth/stencil image | All pixels == 0 (stencil cleared to 0) |
| Viewport | Color attachment image | All pixels == (0,0,0,1) (black clear color) |
| Scissor | Color attachment image | All pixels == (0,0,0,1) |
| Depth | Depth aspect of depth/stencil image | All pixels == 0.0f (depth cleared to 0) |
| Blend | Color attachment image | All pixels == (0,0,0,1) |
| Line | Color attachment image | All pixels == (0,0,0,1) |

Verification is pixel-by-pixel iteration across the entire framebuffer. Any pixel deviating from the expected clear value results in `QP_TEST_RESULT_FAIL`.

## Test Principles Observed

- **Discard overrides dynamic state**: The fragment shader always discards all fragments (via `discard` keyword when `unif.discard_all == 0`), so dynamic state modifications should have no visible effect.
- **State-independent discard verification**: Each test sets a different dynamic state but all verify the same principle — that discard prevents any state-dependent output.
- **Comprehensive state coverage**: The six tests cover the major categories of dynamic state (viewport, scissor, depth/stencil, blend, line width).

## Notes / Uncertainties

- The fragment shader discards all fragments unconditionally (the uniform buffer is zeroed, so `discard_all == 0` is always true).
- For viewport and scissor tests with shader object construction type, the tests use `cmdSetViewportWithCount`/`cmdSetScissorWithCount` instead of the standard commands.
