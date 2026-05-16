# vktRenderPassMultipleSubpassesMultipleCommandBuffersTests

## Source

[vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.multiple_subpasses_multiple_command_buffers
├── test
└── test_general_layout
```

Available under `renderpass1` only. Registered at [L904](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L904).

## Test Families

### test — Multiple subpasses with multiple command buffers

Rendering with multiple subpasses across multiple command buffers with `useGeneralLayout=false` ([L906](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L906)).

### test_general_layout — Multiple subpasses with general layout

Rendering with multiple subpasses across multiple command buffers with `useGeneralLayout=true` ([L907](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L907)).

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Test variants | "test" (useGeneralLayout=false), "test_general_layout" (useGeneralLayout=true) ([L906-L907](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L906-L907)) |

## Support Requirements

No explicit extension requirements beyond base Vulkan.

## Verification

| Aspect | Method |
|--------|--------|
| Image A | Red left, green right |
| Image B | Blue left, yellow right |
| Comparison | tcu::floatThresholdCompare with threshold tcu::Vec4(0.02f) ([L879-L894](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L879-L894)) |
