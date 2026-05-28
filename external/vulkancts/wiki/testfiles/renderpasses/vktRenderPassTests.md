# vktRenderPassTests

## Source

- [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp)
- [vktRenderPassTests.hpp](../../../modules/vulkan/renderpass/vktRenderPassTests.hpp)

## Registration Hierarchy

```text
renderpasses
├── renderpass1
├── renderpass2
└── dynamic_rendering (non-SC only)
```

## Role

Registration file + Implementation file. This file both registers the top-level groups and contains core test implementations.

## Notes

The historical Vulkan API test plan describes multipass tests for data-flow configurations including target formats, attachment counts, load/store, resolves, dependencies, exhaustive dimensions, and randomized tests ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L302-L308)); current source and mustpass remain authoritative for exact behavior.

## Test Families

### renderpass1 — Legacy render pass (RENDERING_TYPE_RENDERPASS_LEGACY)

Registered at [vktRenderPassTests.cpp#L8685](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8685). Direct children in mustpass:

- `custom_resolve` (non-SC, monolithic, no secondary CB)
- `dedicated_allocation`
- `depth_stencil_write_conditions` (non-SC only)
- `dithering` (non-SC only)
- `fragment_density_map` (non-SC only)
- `multiple_subpasses_multiple_command_buffers`
- `nested_command_buffers` (non-SC, monolithic, no secondary CB)
- `no_draws`
- `performance_counters_by_region` (non-SC only)
- `remaining_array_layers`
- `suballocation`

Both `suballocation` and `dedicated_allocation` contain the core test groups defined in this file: `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`.

### renderpass2 — Render pass 2 (RENDERING_TYPE_RENDERPASS2)

Registered at [vktRenderPassTests.cpp#L8686](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8686). Direct children in mustpass:

- `custom_resolve` (non-SC, monolithic, no secondary CB)
- `dedicated_allocation`
- `depth_stencil_resolve`
- `dithering` (non-SC only)
- `fragment_density_map` (non-SC only)
- `multiview_per_view` (non-SC only)
- `nested_command_buffers` (non-SC, monolithic, no secondary CB)
- `no_draws`
- `performance_counters_by_region` (non-SC only)
- `remaining_array_layers`
- `suballocation`

Both `suballocation` and `dedicated_allocation` contain the core test groups defined in this file: `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`.

### dynamic_rendering — Dynamic rendering (RENDERING_TYPE_DYNAMIC_RENDERING, non-SC only)

Registered at [vktRenderPassTests.cpp#L8688](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8688). Direct children in mustpass:

- `complete_secondary_cmd_buff`
- `graphics_pipeline_library`
- `partial_secondary_cmd_buff`
- `primary_cmd_buff`

These correspond to different pipeline construction types and command buffer configurations. Each contains `dedicated_allocation` and `suballocation` subgroups with the core test groups.

## Core Test Groups

Defined in this file and added to both suballocation/dedicated_allocation subgroups:

### simple

- **Definition**: [vktRenderPassTests.cpp#L8446](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8446)
- **Function**: [vktRenderPassTests.cpp#L7353](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7353)
- 9 basic single-attachment tests:
  - color, depth, stencil, depth_stencil, color_depth, color_stencil, color_depth_stencil, no_attachments, color_unused_omit_blend_state

### formats

- **Definition**: [vktRenderPassTests.cpp#L8448](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8448)
- **Function**: [vktRenderPassTests.cpp#L7589](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7589)
- Per-format tests across 47+1 color formats and 5 depth/stencil formats
- Load/store op combinations, input attachment variants, and self-dependency patterns

### attachment

- **Definition**: [vktRenderPassTests.cpp#L8452](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8452)
- **Function**: [vktRenderPassTests.cpp#L6369](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6369)
- Randomly generated attachment format/count tests
- 1/3/4/8 attachments with 100-200 cases each

### attachment_write_mask

- **Definition**: [vktRenderPassTests.cpp#L8457](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8457)
- **Function**: [vktRenderPassTests.cpp#L6584](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6584)
- Color write mask tests with 1/2/3/4/8 attachments

### attachment_allocation

- **Definition**: [vktRenderPassTests.cpp#L8462](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8462)
- **Function**: [vktRenderPassTests.cpp#L6674](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6674)
- Multi-subpass allocation pattern tests: grow, shrink, roll, grow_shrink, input_output_chain, input_output

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| RenderingType | RENDERPASS_LEGACY, RENDERPASS2, DYNAMIC_RENDERING | [vktRenderPassGroupParams.hpp#L34-L39](../../../modules/vulkan/renderpass/vktRenderPassGroupParams.hpp#L34-L39) |
| AllocationKind | SUBALLOCATED, DEDICATED | [vktRenderPassTests.cpp#L147-L151](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L147-L151) |
| GroupParams | renderingType, useSecondaryCmdBuffer, secondaryCmdBufferCompletelyContainsDynamicRenderpass, pipelineConstructionType | [vktRenderPassGroupParams.hpp#L48-L63](../../../modules/vulkan/renderpass/vktRenderPassGroupParams.hpp#L48-L63) |
| Color formats | 47+1 formats | [vktRenderPassTests.cpp#L6314-L6361](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6314-L6361) |
| Depth/stencil formats | 5 formats | [vktRenderPassTests.cpp#L6363-L6367](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6363-L6367) |
| LoadOps | CLEAR, LOAD, DONT_CARE | - |
| StoreOps | STORE, DONT_CARE | - |
| RenderTypes | NONE, CLEAR, DRAW, CLEAR\|DRAW | - |
| CommandBufferTypes | INLINE, SECONDARY | - |
| ImageMemory | STRICT, LAZY | - |

## Support / Feature Requirements

Defined at [vktRenderPassTests.cpp#L5504-L5676](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5504-L5676):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering for DYNAMIC_RENDERING
- VK_KHR_dynamic_rendering_local_read for dynamic rendering with multiple subpasses
- VK_KHR_maintenance5 for VK_FORMAT_A8_UNORM_KHR
- VK_KHR_dedicated_allocation for dedicated allocation
- VK_KHR_maintenance2 for input aspects / DS read-only layouts
- DEVICE_CORE_FEATURE_INDEPENDENT_BLEND for write mask tests
- maxColorAttachments limit checks
- dynamicRenderingLocalReadDepthStencilAttachments / dynamicRenderingLocalReadMultisampledAttachments (Vulkan 1.4)

## Verification Methods

Defined at [vktRenderPassTests.cpp#L5355-L5480](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5355-L5480):

- Software reference rendering: compute reference values via renderReferenceValues, generate reference images, compare GPU output using verifyDepthAttachment / verifyStencilAttachment / pixel comparison with epsilon tolerance
- Undefined pixels filled with 3x3 grid pattern for visual distinction

## Included Implementation Files

All 28 implementation headers are included at [vktRenderPassTests.cpp#L24-L60](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L24-L60). See individual Level-3 docs for details.
