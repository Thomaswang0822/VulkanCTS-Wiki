# vktPipelineMultisampledRenderToSingleSampledTests.cpp

## Overview

[`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1) implements the [`multisampled_render_to_single_sampled`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6103) and [`misc`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6110) topic groups under `multisample`. It verifies VK_EXT_multisampled_render_to_single_sampled functionality, allowing multisampled rendering to single-sampled framebuffer attachments.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1)
- Header: [`vktPipelineMultisampledRenderToSingleSampledTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.hpp#L1)

## Registration Path

- [`createMultisampledRenderToSingleSampledTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6101) returns the `multisampled_render_to_single_sampled` group
- [`createMultisampledMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6108) returns the `misc` group

Both are added to the `multisample` group by `createMultisampleTests()`.

**Variant coverage**: All variants (conditional on VK_EXT_multisampled_render_to_single_sampled support).

## Test Hierarchy

```text
multisampled_render_to_single_sampled
├── basic
│   └── {format}
│       └── {sample_count}
│           └── {resolve_mode}
│               └── {whole_framebuffer,srgb_flags}
├── clear_attachments
│   └── {format}
│       └── {sample_count}
│           └── {resolve_mode}
├── multi_subpass
│   └── {format}
│       └── {sample_count}
├── multi_renderpass
│   └── {format}
│       └── {sample_count}
├── input_attachments
│   └── {input_type}
│       └── {format}
│           └── {sample_count}
│               └── {resolve_mode}
├── subpass_resolve_efficiency_query
├── garbage_color_attachment
└── dynamic_rendering

misc
└── dynamic_rendering
```

## Test Families

| Family | Description |
|---|---|
| Basic MSRTSS test | Verifies basic multisampled render to single-sampled attachment rendering |
| Clear attachments test | Verifies vkCmdClearAttachments with MSRTSS |
| Multi-subpass test | Verifies MSRTSS across multiple subpasses |
| Multi-renderpass test | Verifies MSRTSS across multiple render passes |
| Input attachments test | Verifies input attachment access with MSRTSS |
| Subpass resolve efficiency query | Verifies subpass resolve efficiency query |
| Garbage color attachment test | Verifies behavior with garbage color attachment data |
| Dynamic rendering test | Verifies MSRTSS with VK_KHR_dynamic_rendering |

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
- The `misc` group contains additional dynamic rendering tests
