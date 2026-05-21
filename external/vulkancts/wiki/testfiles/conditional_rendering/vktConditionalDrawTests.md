# vktConditionalDrawTests.cpp

## Overview

This file registers the `draw` group. It combines each `ConditionalData` row with six draw command names and validates rendered color output against a generated reference image.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktConditionalDrawTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp) |
| Registered group and children | [vktConditionalDrawTests.cpp registration](../../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp#L609-L643) |
| Shared condition-data table | [vktConditionalRenderingTestUtil.hpp](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) |
| Shared capability helper | [checkConditionalRenderingCapabilities()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) |

## Registration Hierarchy

```text
conditional_rendering.draw
├── condition_host_memory_expect_execution
├── condition_host_memory_expect_execution_inverted
├── condition_host_memory_expect_execution_inverted_rp_clear
├── condition_host_memory_expect_execution_rp_clear
├── condition_host_memory_expect_noop
├── condition_host_memory_expect_noop_inverted
├── condition_host_memory_expect_noop_inverted_rp_clear
├── condition_host_memory_expect_noop_rp_clear
├── condition_host_memory_inherited_expect_execution
├── condition_host_memory_inherited_expect_execution_inverted
├── condition_host_memory_inherited_expect_noop
├── condition_host_memory_inherited_expect_noop_inverted
├── condition_host_memory_nested_buffer_expect_execution
├── condition_host_memory_nested_buffer_expect_execution_inverted
├── condition_host_memory_nested_buffer_expect_noop
├── condition_host_memory_nested_buffer_expect_noop_inverted
├── condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── condition_host_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── condition_host_memory_nested_buffer_nested_inherited_expect_noop
├── condition_host_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── condition_host_memory_nested_inherited_expect_execution
├── condition_host_memory_nested_inherited_expect_execution_inverted
├── condition_host_memory_nested_inherited_expect_noop
├── condition_host_memory_nested_inherited_expect_noop_inverted
├── condition_host_memory_secondary_buffer_expect_execution
├── condition_host_memory_secondary_buffer_expect_execution_inverted
├── condition_host_memory_secondary_buffer_expect_noop
├── condition_host_memory_secondary_buffer_expect_noop_inverted
├── condition_host_memory_secondary_buffer_inherited_expect_execution
├── condition_host_memory_secondary_buffer_inherited_expect_execution_inverted
├── condition_host_memory_secondary_buffer_inherited_expect_noop
├── condition_host_memory_secondary_buffer_inherited_expect_noop_inverted
├── condition_local_memory_expect_execution
├── condition_local_memory_expect_execution_inverted
├── condition_local_memory_expect_noop
├── condition_local_memory_expect_noop_inverted
├── condition_local_memory_inherited_expect_execution
├── condition_local_memory_inherited_expect_execution_inverted
├── condition_local_memory_inherited_expect_noop
├── condition_local_memory_inherited_expect_noop_inverted
├── condition_local_memory_nested_buffer_expect_execution
├── condition_local_memory_nested_buffer_expect_execution_inverted
├── condition_local_memory_nested_buffer_expect_noop
├── condition_local_memory_nested_buffer_expect_noop_inverted
├── condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── condition_local_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── condition_local_memory_nested_buffer_nested_inherited_expect_noop
├── condition_local_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── condition_local_memory_nested_inherited_expect_execution
├── condition_local_memory_nested_inherited_expect_execution_inverted
├── condition_local_memory_nested_inherited_expect_noop
├── condition_local_memory_nested_inherited_expect_noop_inverted
├── condition_local_memory_secondary_buffer_expect_execution
├── condition_local_memory_secondary_buffer_expect_execution_inverted
├── condition_local_memory_secondary_buffer_expect_noop
├── condition_local_memory_secondary_buffer_expect_noop_inverted
├── condition_local_memory_secondary_buffer_inherited_expect_execution
├── condition_local_memory_secondary_buffer_inherited_expect_execution_inverted
├── condition_local_memory_secondary_buffer_inherited_expect_noop
├── condition_local_memory_secondary_buffer_inherited_expect_noop_inverted
├── no_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── no_condition_host_memory_secondary_buffer_inherited_expect_execution
├── no_condition_local_memory_nested_buffer_nested_inherited_expect_execution
└── no_condition_local_memory_secondary_buffer_inherited_expect_execution
```

## Test Families

### Direct registered children

The direct children are condition-data names produced from `s_testsData`. Each child contains command leaves named `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect`, `draw_indirect_count`, and `draw_indexed_indirect_count`, as shown by the draw-command enum-to-name function and the registration loop.

## Parameter Dimensions

Parameters come from `ConditionalData` rows in the shared utility header and from the six `DrawCommandType` values. The condition rows cover host versus local condition buffers, primary/secondary/nested command-buffer placement, inherited conditions, inverted conditions, render-pass clear variants, and expected execution versus no-op outcomes.

## Support Requirements

The constructor calls conditional-rendering and nested-command-buffer capability helpers, and `checkSupport()` requires `VK_KHR_draw_indirect_count` for the two indirect-count command variants plus `VK_KHR_maintenance7` when an inherited condition is recorded outside the secondary command buffer.

## Verification Methods

The test reads the rendered color target and compares it with a reference frame using `tcu::fuzzyCompare()` with a `0.05f` threshold.

## Test Principles

The implementation varies whether the conditional-rendering predicate should execute or suppress work, then verifies externally visible image, buffer, or transform-feedback results rather than relying only on successful command submission.

## Notes and Uncertainties

The hierarchy tree lists only one direct level below `conditional_rendering.draw` as required by the wiki registration contract. Deeper generated leaves are described in prose because they are registered below those direct children.
