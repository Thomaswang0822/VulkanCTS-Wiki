# vktRenderPassNestedCommandBuffersTests

## Source

[vktRenderPassNestedCommandBuffersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp)

## Registration

Added to root group (monolithic pipeline, non-SC, no secondary CB).

Registered group name: `"nested_command_buffers"` ([line 670](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L670))

## Test Families

```
nested_command_buffers
|-- NestedCommandBuffersTest
```

### NestedCommandBuffersTest

Tests nested command buffer functionality with render passes ([lines 672-711](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L672-L711)).

**Parameter Dimensions:**

- Extension: EXT / KHR
- Nesting patterns: inline_secondary, secondary_inline
- Total: 2 extensions x 2 first-command x 2 last-command = 8 test cases

**Verification** ([lines 529-580](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L529-L580)):

- 6 quads with specific colors based on position and `beginInline`/`endInline` parameters
- Exact pixel color matching

## Support Requirements

| Requirement | Context |
|---|---|
| VK_EXT_nested_command_buffer | Required for EXT variant, with `nestedCommandBuffer` + `nestedCommandBufferRendering` features ([lines 646-653](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L646-L653)) |
| VK_KHR_maintenance7 | Required for KHR variant, with `maintenance7` feature ([lines 657-661](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L657-L661)) |
| VK_KHR_dynamic_rendering | Core dependency |
| VK_KHR_create_renderpass2 | Core dependency |
