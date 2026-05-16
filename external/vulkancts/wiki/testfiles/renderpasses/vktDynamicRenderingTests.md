# vktDynamicRenderingTests

## Source

[vktDynamicRenderingTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp)

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.basic
├── 2_cmdbuffers_resuming
├── 2_cmdbuffers_resuming_end_rendering_2
├── 2_secondary_2_primary_cmdbuffers_resuming
├── 2_secondary_2_primary_cmdbuffers_resuming_end_rendering_2
├── 2_secondary_cmdbuffers_resuming
├── 2_secondary_cmdbuffers_resuming_end_rendering_2
├── contents_2_primary_secondary_cmdbuffers_resuming
├── contents_2_primary_secondary_cmdbuffers_resuming_end_rendering_2
├── contents_2_secondary_2_primary_cmdbuffers_resuming
├── contents_2_secondary_2_primary_cmdbuffers_resuming_end_rendering_2
├── contents_2_secondary_cmdbuffers
├── contents_2_secondary_cmdbuffers_end_rendering_2
├── contents_2_secondary_cmdbuffers_resuming
├── contents_2_secondary_cmdbuffers_resuming_end_rendering_2
├── contents_primary_secondary_cmdbuffers_resuming
├── contents_primary_secondary_cmdbuffers_resuming_end_rendering_2
├── contents_secondary_2_primary_cmdbuffers_resuming
├── contents_secondary_2_primary_cmdbuffers_resuming_end_rendering_2
├── contents_secondary_cmdbuffers
├── contents_secondary_cmdbuffers_end_rendering_2
├── contents_secondary_primary_cmdbuffers_resuming
├── contents_secondary_primary_cmdbuffers_resuming_end_rendering_2
├── partial_binding_depth_stencil
├── partial_binding_depth_stencil_end_rendering_2
├── secondary_cmdbuffer_out_of_rendering_commands
├── secondary_cmdbuffer_out_of_rendering_commands_end_rendering_2
├── single_cmdbuffer
├── single_cmdbuffer_end_rendering_2
├── single_cmdbuffer_resuming
└── single_cmdbuffer_resuming_end_rendering_2
```

Registered under `primary_cmd_buff` only ([vktRenderPassTests.cpp#L8533](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8533)). The `basic` group is created at [line 3731](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3731).

## Test Families

15 TestType values defined at [lines 72-122](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L72-L122), names at [lines 3703-3719](../../../modules/vulkan/renderpass/vktDynamicRenderingTests.cpp#L3703-L3719). Each test type is instantiated twice: once with `endRendering2=false` and once with `endRendering2=true` (appending `_end_rendering_2` to the name).

### single_cmdbuffer / single_cmdbuffer_end_rendering_2 — Single primary command buffer

Draw two triangles in a single primary command buffer, beginning and ending the render pass instance.

### single_cmdbuffer_resuming / single_cmdbuffer_resuming_end_rendering_2 — Single primary CB resuming

Draw two triangles in a single primary command buffer, across two render pass instances, with the second RESUMING the first.

### 2_cmdbuffers_resuming / 2_cmdbuffers_resuming_end_rendering_2 — Two primary CBs resuming

Draw two triangles in two primary command buffers, across two render pass instances, with the second RESUMING the first.

### 2_secondary_cmdbuffers_resuming / 2_secondary_cmdbuffers_resuming_end_rendering_2 — Two secondary CBs resuming

Draw two triangles in two secondary command buffers, across two render pass instances, with the second RESUMING the first, both recorded to the same primary command buffer.

### 2_secondary_2_primary_cmdbuffers_resuming / 2_secondary_2_primary_cmdbuffers_resuming_end_rendering_2 — Two secondary CBs in two primary CBs

Draw two triangles in two secondary command buffers, across two render pass instances, with the second RESUMING the first, executed in the two primary command buffers.

### contents_secondary_cmdbuffers / contents_secondary_cmdbuffers_end_rendering_2 — CONTENTS_SECONDARY single secondary CB

Using CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw two triangles in one secondary command buffer, and execute it inside a single render pass instance in one primary command buffer.

### contents_2_secondary_cmdbuffers / contents_2_secondary_cmdbuffers_end_rendering_2 — CONTENTS_SECONDARY two secondary CBs

Using CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw two triangles in two secondary command buffers, and execute them inside a single render pass instance in one primary command buffer.

### contents_2_secondary_cmdbuffers_resuming / contents_2_secondary_cmdbuffers_resuming_end_rendering_2 — CONTENTS_SECONDARY two secondary CBs resuming

Using CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw two triangles in two secondary command buffers, and execute them inside two render pass instances, with the second RESUMING the first, both recorded in the same primary command buffer.

### contents_2_secondary_2_primary_cmdbuffers_resuming / contents_2_secondary_2_primary_cmdbuffers_resuming_end_rendering_2 — CONTENTS_SECONDARY two secondary CBs in two primary CBs resuming

Using CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw two triangles in two secondary command buffers, and execute them inside two render pass instances, with the second RESUMING the first, recorded into two primary command buffers.

### contents_primary_secondary_cmdbuffers_resuming / contents_primary_secondary_cmdbuffers_resuming_end_rendering_2 — Primary then secondary CB resuming

In one primary command buffer, record two render pass instances, with the second resuming the first. In the first, draw one triangle directly in the primary command buffer. For the second, use CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw the second triangle in a secondary command buffer, and execute it in that second render pass instance.

### contents_secondary_primary_cmdbuffers_resuming / contents_secondary_primary_cmdbuffers_resuming_end_rendering_2 — Secondary then primary CB resuming

In one primary command buffer, record two render pass instances, with the second resuming the first. In the first, use CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw the first triangle in a secondary command buffer, and execute it in that first render pass instance. In the second, draw one triangle directly in the primary command buffer.

### contents_2_primary_secondary_cmdbuffers_resuming / contents_2_primary_secondary_cmdbuffers_resuming_end_rendering_2 — Two primary CBs, primary then secondary resuming

In two primary command buffers, record two render pass instances (one in each), with the second resuming the first. In the first, draw one triangle directly in the primary command buffer. For the second, use CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw the second triangle in a secondary command buffer, and execute it in that second render pass instance.

### contents_secondary_2_primary_cmdbuffers_resuming / contents_secondary_2_primary_cmdbuffers_resuming_end_rendering_2 — Two primary CBs, secondary then primary resuming

In two primary command buffers, record two render pass instances (one in each), with the second resuming the first. In the first, use CONTENTS_SECONDARY_COMMAND_BUFFER_BIT_KHR, draw the first triangle in a secondary command buffer, and execute it in that first render pass instance. In the second, draw one triangle directly in the primary command buffer.

### secondary_cmdbuffer_out_of_rendering_commands / secondary_cmdbuffer_out_of_rendering_commands_end_rendering_2 — Secondary CB out-of-rendering commands

Draw triangles inside rendering of secondary command buffer, and after rendering is ended copy results on secondary buffer. Tests mixing inside & outside render pass commands in secondary command buffers.

### partial_binding_depth_stencil / partial_binding_depth_stencil_end_rendering_2 — Partial binding depth/stencil

Test partial binding of depth/stencil formats. 3 sets of tests: (1) Clears bound resource and leaves the other untouched, (2) Clears and draws to the resource leaving the unbound as is, (3) Previous ones with secondary commands to check inheritance works as expected.

**Parameter Dimensions:**

- TestType: 15 values
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
