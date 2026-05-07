# vktDynamicRenderingTests

## Source

[vktDynamicRenderingTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp)

## Registration

Added to dynamic_rendering root group (no secondary CB).

Registered group name: `"basic"` ([line 3731](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3731))

## Test Families

```
basic
|-- single_cmdbuffer
|-- single_cmdbuffer_resuming
|-- 2_cmdbuffers_resuming
|-- 2_secondary_cmdbuffers_resuming
|-- 2_secondary_2_primary_cmdbuffers_resuming
|-- contents_secondary_cmdbuffers
|-- contents_2_secondary_cmdbuffers
|-- contents_2_secondary_cmdbuffers_resuming
|-- contents_2_secondary_2_primary_cmdbuffers_resuming
|-- contents_primary_secondary_cmdbuffers_resuming
|-- contents_secondary_primary_cmdbuffers_resuming
|-- contents_2_primary_secondary_cmdbuffers_resuming
|-- contents_secondary_2_primary_cmdbuffers_resuming
|-- secondary_cmdbuffer_out_of_rendering_commands
|-- partial_binding_depth_stencil
```

14 TestType values defined at [lines 72-122](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L72-L122), names at [lines 3703-3719](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3703-L3719).

**Parameter Dimensions:**

- TestType: 14+ values
- endRendering2: {false, true} (appends `_end_rendering_2` when true)
- Fixed: VK_FORMAT_R8G8B8A8_UNORM, render size 32x32

**Verification** ([lines 1185](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1185), [1217](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1217), [1256](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L1256)):

- Color: `tcu::floatThresholdCompare` with threshold `Vec4(0.02f)`
- Depth: `verifyDepth()`
- Stencil: `verifyStencil()`

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 3571](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3571) |
| VK_KHR_maintenance10 | Required when `endRendering2` is true ([line 3575](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3575)) |
| VK_EXT_dynamic_rendering_unused_attachments | Required for `PARTIAL_BINDING_DEPTH_STENCIL` ([line 3580](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3580)) |
| dynamicRendering feature | Must be true |
