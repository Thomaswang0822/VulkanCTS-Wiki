# vktConditionalClearAttachmentTests.cpp

## Overview

This file registers the `clear_attachments` group. For each shared condition row except render-pass-clear rows, it adds a `clear_attachments` leaf that exercises conditional execution of attachment clears.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktConditionalClearAttachmentTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp) |
| Registered group and children | [vktConditionalClearAttachmentTests.cpp registration](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L259-L290) |
| Shared condition-data table | [vktConditionalRenderingTestUtil.hpp](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) |
| Shared capability helper | [checkConditionalRenderingCapabilities()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) |

## Registration Hierarchy

```text
conditional_rendering.clear_attachments
├── condition_host_memory_expect_execution
├── condition_host_memory_expect_execution_inverted
├── condition_host_memory_expect_noop
├── condition_host_memory_expect_noop_inverted
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

Direct children are condition-data names from `s_testsData` after rows with `clearInRenderPass` are skipped. Each direct child contains a `clear_attachments` leaf.

## Parameter Dimensions

The parameter source is the shared `ConditionalData` table. This file uses the condition buffer placement, inversion, inheritance, expected-execution, nested-secondary, and memory-type fields but skips rows marked for render-pass clear.

## Support Requirements

Support is inherited through the conditional-rendering setup helpers used by the draw-style test infrastructure; the shared helper requires `VK_EXT_conditional_rendering`, validates `conditionalRendering`, checks inherited conditional rendering when requested, and checks nested-command-buffer support for nested rows.

## Verification Methods

The test builds a full-frame reference color based on whether execution is expected, reads the color attachment, and compares with `tcu::fuzzyCompare()` using a `0.05f` threshold.

## Test Principles

The implementation varies whether the conditional-rendering predicate should execute or suppress work, then verifies externally visible image, buffer, or transform-feedback results rather than relying only on successful command submission.

## Notes and Uncertainties

The hierarchy tree lists only one direct level below `conditional_rendering.clear_attachments` as required by the wiki registration contract. Deeper generated leaves are described in prose because they are registered below those direct children.
