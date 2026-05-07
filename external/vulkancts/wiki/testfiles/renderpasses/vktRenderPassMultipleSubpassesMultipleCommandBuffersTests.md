# vktRenderPassMultipleSubpassesMultipleCommandBuffersTests

## Source

[vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp)

## Registration

Added to `renderpass1` root group.

Registered group name: `"multiple_subpasses_multiple_command_buffers"` ([L904](../../../modules/vulkan/renderpass/vktRenderPassMultipleSubpassesMultipleCommandBuffersTests.cpp#L904))

## Test Families

```
multiple_subpasses_multiple_command_buffers
+-- MultipleSubpassesMultipleCommandBuffersTest
    Rendering with multiple subpasses across multiple command buffers.
    +-- test
    |   useGeneralLayout=false
    +-- test_general_layout
        useGeneralLayout=true
```

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
