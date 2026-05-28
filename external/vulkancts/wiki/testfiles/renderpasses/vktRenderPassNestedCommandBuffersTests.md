# vktRenderPassNestedCommandBuffersTests

## Source

[vktRenderPassNestedCommandBuffersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.nested_command_buffers
├── ext
└── khr
```

Available under `renderpass1`, `renderpass2`, and dynamic-rendering primary command-buffer groups (non-SC, monolithic pipeline, no secondary CB). Representative root shown for `renderpass1`. The root registration adds this group when `useSecondaryCmdBuffer == false` inside the monolithic-pipeline block ([vktRenderPassTests.cpp#L8571-L8592](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8592)); the source file creates the registered group at [L670](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L670).

## Test Families

### ext — EXT_nested_command_buffer variant

Tests nested command buffer functionality using VK_EXT_nested_command_buffer ([lines 646-653](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L646-L653)). Each extension group contains two nesting-pattern subgroups:

- `inline_secondary` — first command is inline, last is secondary
- `secondary_inline` — first command is secondary, last is inline

Each nesting-pattern subgroup contains 2 leaf tests (one per `lastCommand` variant), for a total of 4 tests per extension.

### khr — KHR_maintenance7 variant

Tests nested command buffer functionality using VK_KHR_maintenance7 ([lines 657-661](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L657-L661)). Same subgroup structure as `ext`:

- `inline_secondary` — first command is inline, last is secondary
- `secondary_inline` — first command is secondary, last is inline

Each nesting-pattern subgroup contains 2 leaf tests (one per `lastCommand` variant), for a total of 4 tests per extension.

Total: 2 extensions x 2 first-command x 2 last-command = 8 test cases.

## Parameter Dimensions

- Extension: EXT / KHR
- Nesting patterns: inline_secondary, secondary_inline
- Total: 2 extensions x 2 first-command x 2 last-command = 8 test cases

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| VK_EXT_nested_command_buffer | Required for EXT variant, with `nestedCommandBuffer` + `nestedCommandBufferRendering` features ([lines 646-653](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L646-L653)) |
| VK_KHR_maintenance7 | Required for KHR variant, with `maintenance7` feature ([lines 657-661](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L657-L661)) |
| VK_KHR_dynamic_rendering | Required only when the group parameters use `RENDERING_TYPE_DYNAMIC_RENDERING` ([lines 635-638](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L635-L638)) |
| VK_KHR_create_renderpass2 | Required only when the group parameters use `RENDERING_TYPE_RENDERPASS2` ([lines 639-642](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L639-L642)) |

## Verification

| Aspect | Method |
|---|---|
| Render output | 6 quads with specific colors based on position and `beginInline`/`endInline` parameters ([lines 529-580](../../../modules/vulkan/renderpass/vktRenderPassNestedCommandBuffersTests.cpp#L529-L580)) |
| Comparison | Exact pixel color matching |
