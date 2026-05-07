# vktPipelineMultisampleResolveMaint10Tests.cpp

## Overview

[`vktPipelineMultisampleResolveMaint10Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1) implements the [`m10_resolve`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1585) topic group under `multisample`. It verifies VK_KHR_maintenance10 multisample resolve functionality, testing resolve operations with various methods, formats, aspects, modes, and areas.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleResolveMaint10Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1)
- Header: [`vktPipelineMultisampleResolveMaint10Tests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.hpp#L1)

## Registration Path

[`createMultisampleResolveMaint10Tests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1583) returns the `m10_resolve` group, added to the `multisample` group by `createMultisampleTests()`.

**Variant coverage**: Monolithic, fast-linked-library, and shader_object_unlinked_spirv only. Not registered for other variants.

## Test Hierarchy

```text
m10_resolve
└── {resolve_method}
    └── {format}
        └── {resolve_aspects}
            └── {resolve_mode}
                └── {resolve_area}
                    └── {srgb_flags}
```

## Test Families

| Family | Description |
|---|---|
| Maint10ResolveCase | Verifies VK_KHR_maintenance10 resolve operations with various parameter combinations |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Resolve method | Enum | Renderpass resolve, vkCmdResolveImage2, etc. |
| VkFormat | Loop | Color and depth/stencil formats |
| Resolve aspects | Bitfield | Color, depth, stencil, depth+stencil |
| Resolve mode | Enum | VK_RESOLVE_MODE_SAMPLE_ZERO_BIT, VK_RESOLVE_MODE_MAX_BIT, VK_RESOLVE_MODE_MIN_BIT, VK_RESOLVE_MODE_AVERAGE_BIT |
| Resolve area | Struct | Full framebuffer, partial |
| sRGB flags | Bool | With/without sRGB conversion |
| PipelineConstructionType | Parameter | Limited variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_maintenance10` | Primary extension for all tests |
| `VK_KHR_copy_commands2` | Required when API version < 1.3 |
| `VK_KHR_dynamic_rendering` | Required when API version < 1.3 |
| `VK_KHR_create_renderpass2` | Required when API version < 1.2 |
| `VK_KHR_depth_stencil_resolve` | Required for depth/stencil resolve |
| `VK_EXT_shader_stencil_export` | Required for stencil resolve |

## Verification Methods

- **Pixel comparison**: Resolve multisample image, compare resolved result against expected values
- **Threshold comparison**: Use tolerance-based comparison for floating-point formats

## Notes

- Only registered for monolithic, fast-linked-library, and shader_object_unlinked_spirv pipeline construction types
- Not registered when `useFragmentShadingRate` is true
