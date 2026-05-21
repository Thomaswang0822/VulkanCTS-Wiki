# Conditional Rendering Tests

## Summary

The conditional rendering category exercises `VK_EXT_conditional_rendering` behavior around commands that are conditionally executed and commands that are expected to ignore the active conditional-rendering state. The root registration file adds six direct child groups. Source evidence is concentrated under `external/vulkancts/modules/vulkan/conditional_rendering/`; `doc/testspecs/VK/apitests.adoc` was inspected, but no conditional-rendering-specific section was found there.

## Registration Entry Point

| Item | Evidence |
|---|---|
| Package root registration | [`addRootChild("conditional_rendering", ...)`](../../modules/vulkan/vktTestPackage.cpp#L1377-L1380) |
| Category factory | [`conditional::createTests()`](../../modules/vulkan/conditional_rendering/vktConditionalTests.cpp#L56-L59) |
| Direct child registration | [`createChildren()`](../../modules/vulkan/conditional_rendering/vktConditionalTests.cpp#L42-L52) |

## Subgroup Structure

```text
conditional_rendering
├── draw
├── dispatch
├── clear_attachments
├── draw_clear
├── conditional_ignore
└── transform_feedback
```

## File Inventory

| File | Registered group | Role |
|---|---:|---|
| [vktConditionalTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalTests.cpp) | `conditional_rendering` | Category dispatcher registering six direct children. |
| [vktConditionalDrawTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp) | `draw` | Draw-command implementation. |
| [vktConditionalDispatchTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp) | `dispatch` | Dispatch-command implementation. |
| [vktConditionalClearAttachmentTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp) | `clear_attachments` | Clear-attachments implementation. |
| [vktConditionalDrawAndClearTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalDrawAndClearTests.cpp) | `draw_clear` | Draw/clear interaction implementation. |
| [vktConditionalIgnoreTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp) | `conditional_ignore` | Commands expected to ignore conditional rendering. |
| [vktConditionalTransformFeedbackTests.cpp](../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp) | `transform_feedback` | Transform-feedback implementation. |
| [vktConditionalRenderingTestUtil.cpp](../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp) / [vktConditionalRenderingTestUtil.hpp](../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp) | helper only | Shared condition data, naming, buffers, and capability checks; no separate Level-3 page because it does not register tests. |

## Recurring Themes

- Shared `ConditionalData` rows encode condition placement, inversion, inheritance, expected execution, nested secondary command buffers, render-pass-clear behavior, and host/local memory choices.
- Draw, dispatch, and clear-attachment groups use the shared condition rows to verify whether command effects are present or absent.
- `conditional_ignore` documents command classes that should still produce their expected effects while conditional rendering is active.
- `transform_feedback` combines conditional rendering with transform-feedback draw command variants.

## Recurring Parameters

| Dimension | Evidence |
|---|---|
| Condition buffer memory and command-buffer placement | [`ConditionalData`](../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L59) and [`s_testsData`](../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L61-L144) |
| Condition-name generation | [`operator<<`](../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L138-L185) |
| Draw command names | [`getDrawCommandTypeName()`](../../modules/vulkan/conditional_rendering/vktConditionalDrawTests.cpp#L63-L83) |
| Dispatch command names | [`getDispatchCommandTypeName()`](../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L50-L64) |
| Transform-feedback command names | [`getDrawCommandTypeName()`](../../modules/vulkan/conditional_rendering/vktConditionalTransformFeedbackTests.cpp#L64-L90) |

## Support Requirements

The shared helper requires `VK_EXT_conditional_rendering`, checks the `conditionalRendering` and `inheritedConditionalRendering` feature bits where applicable, requires `VK_EXT_nested_command_buffer` for nested rows, and requires `VK_KHR_maintenance7` for inherited primary-command-buffer cases. Individual files add command-specific gates such as `VK_KHR_draw_indirect_count`, `VK_KHR_device_group` for `dispatch_base`, `VK_EXT_transform_feedback`, `VK_EXT_multi_draw`, `VK_EXT_shader_object`, `VK_KHR_ray_tracing_pipeline`, `VK_KHR_ray_tracing_maintenance1`, `VK_KHR_maintenance5`, and `VK_KHR_device_address_commands` where their source paths require them.

## Verification Methods

Verification is result-oriented: draw and clear tests compare rendered images against references; dispatch tests compare an output counter to the expected number of shader invocations; transform-feedback tests compare captured float values; ignore tests compare command-specific image, depth/stencil, or buffer outputs.

## Level-3 Pages

- [vktConditionalTests.md](../testfiles/conditional_rendering/vktConditionalTests.md)
- [vktConditionalDrawTests.md](../testfiles/conditional_rendering/vktConditionalDrawTests.md)
- [vktConditionalDispatchTests.md](../testfiles/conditional_rendering/vktConditionalDispatchTests.md)
- [vktConditionalClearAttachmentTests.md](../testfiles/conditional_rendering/vktConditionalClearAttachmentTests.md)
- [vktConditionalDrawAndClearTests.md](../testfiles/conditional_rendering/vktConditionalDrawAndClearTests.md)
- [vktConditionalIgnoreTests.md](../testfiles/conditional_rendering/vktConditionalIgnoreTests.md)
- [vktConditionalTransformFeedbackTests.md](../testfiles/conditional_rendering/vktConditionalTransformFeedbackTests.md)

## Scope Notes

Only files under the conditional-rendering source directory that register tests have Level-3 pages. The shared utility file is documented as supporting evidence but is not given a Level-3 page because it does not register a test group.
