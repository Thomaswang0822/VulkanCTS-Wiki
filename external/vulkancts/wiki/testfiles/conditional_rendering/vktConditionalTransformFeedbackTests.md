# vktConditionalTransformFeedbackTests.cpp

## Overview

This file registers the `transform_feedback` group. It adds one direct leaf for each transform-feedback draw command variant.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktConditionalTransformFeedbackTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp) |
| Registered group and children | [vktConditionalTransformFeedbackTests.cpp registration](../../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L719-L744) |
| Shared condition-data table | [vktConditionalRenderingTestUtil.hpp](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) |
| Shared capability helper | [checkConditionalRenderingCapabilities()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) |

## Registration Hierarchy

```text
conditional_rendering.transform_feedback
├── draw
├── draw_indexed
├── draw_indexed_indirect
├── draw_indexed_indirect_count
├── draw_indirect
├── draw_indirect_byte_count_ext
├── draw_indirect_count
├── draw_multi_ext
└── draw_multi_indexed_ext
```

## Test Families

### Direct registered children

The direct children correspond to draw, indexed draw, indirect draw, multi-draw, indirect-byte-count, and indirect-count command variants returned by `getDrawCommandTypeName()`.

## Parameter Dimensions

The command enum provides nine observed command names. The test spec also supplies vertex and fragment shader names for the transform-feedback draw path.

## Support / Feature Requirements

Each case requires `VK_EXT_conditional_rendering` and `VK_EXT_transform_feedback`. Indirect-count command variants require `VK_KHR_draw_indirect_count`, multi-draw variants require `VK_EXT_multi_draw`, and the transform-feedback feature check requires `geometryStreams`.

## Verification Methods

The test validates the transform-feedback buffer contents by comparing observed float values at each index with expected values and failing on the first mismatch.

## Test Principles

The implementation varies whether the conditional-rendering predicate should execute or suppress work, then verifies externally visible image, buffer, or transform-feedback results rather than relying only on successful command submission.

## Notes and Uncertainties

The hierarchy tree lists only one direct level below `conditional_rendering.transform_feedback` as required by the wiki registration contract. Deeper generated leaves are described in prose because they are registered below those direct children.
