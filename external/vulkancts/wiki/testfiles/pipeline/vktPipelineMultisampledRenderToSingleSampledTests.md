# vktPipelineMultisampledRenderToSingleSampledTests.cpp

## Overview

[`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1) implements the [`multisampled_render_to_single_sampled`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6103) and [`misc`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6110) topic groups under `multisample`. It verifies VK_EXT_multisampled_render_to_single_sampled functionality, allowing multisampled rendering to single-sampled framebuffer attachments.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1)
- Header: [`vktPipelineMultisampledRenderToSingleSampledTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.multisample.multisampled_render_to_single_sampled
├── basic
├── clear_attachments
├── multi_subpass
├── multi_renderpass
├── input_attachments
├── subpass_resolve_efficiency_query
└── dynamic_rendering
```

Source: [`createMultisampledRenderToSingleSampledTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6101) returns the `multisampled_render_to_single_sampled` group. Both this group and the separate [`misc`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6110) group are added to the `multisample` group by `createMultisampleTests()`. Variant coverage: all variants (conditional on VK_EXT_multisampled_render_to_single_sampled support).

## Test Families

### basic — Basic MSRTSS rendering

Verifies basic multisampled render to single-sampled attachment rendering. Contains leaf test cases parameterized by `{format}`, `{sample_count}`, `{resolve_mode}`, and `{whole_framebuffer,srgb_flags}`.

### clear_attachments — Clear attachments with MSRTSS

Verifies `vkCmdClearAttachments` with MSRTSS. Contains leaf test cases parameterized by `{format}`, `{sample_count}`, and `{resolve_mode}`.

### multi_subpass — Multi-subpass MSRTSS

Verifies MSRTSS across multiple subpasses. Contains leaf test cases parameterized by `{format}` and `{sample_count}`. Not tested with dynamic rendering (multi-subpass requires render pass).

### multi_renderpass — Multi-renderpass MSRTSS

Verifies MSRTSS across multiple render passes. Contains leaf test cases parameterized by `{format}` and `{sample_count}`.

### input_attachments — Input attachment access with MSRTSS

Verifies input attachment access with MSRTSS. Contains leaf test cases parameterized by `{input_type}`, `{format}`, `{sample_count}`, and `{resolve_mode}`. Not tested with dynamic rendering or shader objects.

### subpass_resolve_efficiency_query — Subpass resolve efficiency query

Verifies subpass resolve efficiency query. Only registered when `isMultisampledRenderToSingleSampled` and `pipelineConstructionType == PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` and not using dynamic rendering.

### dynamic_rendering — MSRTSS with dynamic rendering

Verifies MSRTSS with VK_KHR_dynamic_rendering. This subgroup is always added and contains the same test structure as the non-dynamic-rendering path but using dynamic rendering mode. For non-monolithic pipeline construction types, also contains a `garbage_color_attachment` child subgroup that verifies behavior with garbage color attachment data.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkFormat | Loop | VK_FORMAT_R8G8B8A8_UNORM, VK_FORMAT_R32_SFLOAT, etc. |
| Sample count | Array | 2, 4, 8, 16 |
| Resolve mode | Array | VK_RESOLVE_MODE_SAMPLE_ZERO_BIT, VK_RESOLVE_MODE_MAX_BIT, etc. |
| Render area | Struct | Full framebuffer, partial |
| sRGB flags | Bool | With/without sRGB conversion |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_multisampled_render_to_single_sampled` | Primary extension for all tests |
| `VK_KHR_dynamic_rendering` | Dynamic rendering tests |
| `VK_KHR_depth_stencil_resolve` | Depth/stencil resolve tests |
| `VK_EXT_shader_stencil_export` | Stencil export for stencil resolve |

## Verification Methods

- **Pixel comparison**: Render with MSRTSS, compare resolved attachment against expected values
- **Buffer verification**: Use compute shader to read back and verify attachment contents
- **Clear verification**: Verify clear attachment operations produce expected values

## Notes

- The `multisampled_render_to_single_sampled` group is only registered when the extension is supported
- The `misc` group (registered separately as `pipeline.monolithic.multisample.misc`) contains additional dynamic rendering tests and is created by [`createMultisampledMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6108)
