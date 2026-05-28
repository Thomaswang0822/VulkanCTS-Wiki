# vktConditionalTests.cpp

## Overview

`vktConditionalTests.cpp` is the category registration dispatcher for conditional-rendering tests. Its `createChildren()` function adds the six direct category children documented below, and `createTests()` wraps those children in the category group name supplied by the Vulkan test package.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktConditionalTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalTests.cpp) |
| Direct child registration | [`createChildren()`](../../../modules/vulkan/conditional_rendering/vktConditionalTests.cpp#L42-L52) |
| Category factory | [`createTests()`](../../../modules/vulkan/conditional_rendering/vktConditionalTests.cpp#L56-L59) |
| Root package registration | [`addRootChild("conditional_rendering", ...)`](../../../modules/vulkan/vktTestPackage.cpp#L1377-L1380) |

## Registration Hierarchy

```text
conditional_rendering
├── draw
├── dispatch
├── clear_attachments
├── draw_clear
├── conditional_ignore
└── transform_feedback
```

## Test Families

### draw

Registered through `ConditionalDrawTests`, this child covers graphics draw commands under conditional rendering.

### dispatch

Registered through `ConditionalDispatchTests`, this child covers compute dispatch commands, including extra groups for condition-size, allocation-offset, and compute-queue cases.

### clear_attachments

Registered through `ConditionalClearAttachmentTests`, this child focuses on `vkCmdClearAttachments` behavior under conditional rendering.

### draw_clear

Registered through `ConditionalRenderingDrawAndClearTests`, this child groups draw and clear interactions in a separate implementation file.

### conditional_ignore

Registered through `ConditionalIgnoreTests`, this child covers operations that the implementation expects to proceed even when conditional rendering is active.

### transform_feedback

Registered through `ConditionalTransformFeedbackTests`, this child covers transform-feedback draw commands combined with conditional rendering.

## Parameter Dimensions

This dispatcher does not define test parameters itself. It delegates to implementation files whose constructors and `init()` methods build the child groups.

## Support / Feature Requirements

No support gates are enforced in this dispatcher. Extension and feature checks are implemented in the registered child files.

## Verification Methods

This file contains registration only; verification occurs in the implementation files.

## Notes and Uncertainties

The displayed category name is not hardcoded here; it is passed into `createTests()` and supplied by the package registration as `conditional_rendering`.
