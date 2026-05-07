# vktRenderPassSubpassDependencyTests

## Source

- [vktRenderPassSubpassDependencyTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup within each top-level group
- **Registered group name**: `"subpass_dependencies"` at [vktRenderPassSubpassDependencyTests.cpp#L4587](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4587)

## Role

Implementation file

## Test Families

### External subpass

- **Pattern**: `external_subpass/render_size_<W>_<H>/render_passes_<N>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4207-L4305](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4207-L4305)

### External subpass sync2

- **Pattern**: `external_subpass/render_size_<W>_<H>/render_passes_<N>_sync_2`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4291-L4298](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4291-L4298)

### Implicit dependencies

- **Pattern**: `implicit_dependencies/render_passes_<N>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4307-L4375](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4307-L4375)

### Late fragment tests

- **Pattern**: `late_fragment_tests/render_size_<W>_<H>/subpass_count_<N>/<format>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4377-L4496](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4377-L4496)

### Self dependency

- **Pattern**: `self_dependency/render_size_<W>_<H>/geometry_to_indirectdraw`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4498-L4525](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4498-L4525)

### Separate channels

- **Pattern**: `separate_channels/<formatName>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4527-L4552](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4527-L4552)

### Single attachment

- **Pattern**: `single_attachment/<formatName>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4554-L4580](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4554-L4580)

## Test Hierarchy

```
subpass_dependencies
|-- external_subpass
|   +-- render_size_<W>_<H>
|       |-- render_passes_<N>
|       +-- render_passes_<N>_sync_2
|-- implicit_dependencies
|   +-- render_passes_<N>
|-- late_fragment_tests
|   +-- render_size_<W>_<H>
|       +-- subpass_count_<N>
|           +-- <format>
|-- self_dependency
|   +-- render_size_<W>_<H>
|       +-- geometry_to_indirectdraw
|-- separate_channels
|   +-- <formatName>
+-- single_attachment
    +-- <formatName>
```

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| External subpass renderPassCounts | {2, 3, 5} | - |
| External subpass renderSizes | {(64,64), (128,128), (512,512)} | - |
| External subpass syncType | LEGACY, SYNCHRONIZATION2 | - |
| Implicit renderPassCounts | {2, 3, 5} | - |
| Late fragment renderSizes | {(32,32), (64,64), (128,128)} | - |
| Late fragment subpassCounts | {2, 3, 5} | - |
| Late fragment formats | D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | - |
| Self dependency renderSizes | {(64,64), (128,128), (512,512)} | - |
| Separate channels formats | 4 formats | - |
| Single attachment formats | 5 formats | - |

Note: external, implicit, late fragment, and self dependency tests are excluded for DYNAMIC_RENDERING.

## Support Requirements

Defined at [vktRenderPassSubpassDependencyTests.cpp#L3924-L3975](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3924-L3975):

- VK_KHR_synchronization2 for SYNCHRONIZATION2
- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- DEVICE_CORE_FEATURE_GEOMETRY_SHADER for self dependency

## Verification Methods

- **ExternalDependency**: tcu::floatThresholdCompare with 4.0 * min_presentable_difference
- **SubpassDependency**: verifyDepth() with subpassCount * min_representable_difference; verifyStencil() exact
- **SelfDependency**: software renderer reference + tcu::floatThresholdCompare threshold 0.01f
- **SeparateChannels**: format-dependent thresholds
- **SingleAttachment**: tcu::floatThresholdCompare threshold 0.05f against (0.3, 0.6, 0.0, 1.0)
