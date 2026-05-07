# vktRenderPassMultisampleResolveTests

## Source

- [vktRenderPassMultisampleResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup within each top-level group
- **Registered group name**: `"multisample_resolve"` at [vktRenderPassMultisampleResolveTests.cpp#L3263](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3263)

## Role

Implementation file

## Test Families

### Basic resolve

- **Pattern**: `<formatName>/samples_<N>`
- **Definition**: [vktRenderPassMultisampleResolveTests.cpp#L3149-L3248](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3149-L3248)

### Base layer offset

- **Pattern**: `<formatName>/samples_<N>_baseLayer1`
- Monolithic pipeline only

### Resolve level

- **Pattern**: `<formatName>/samples_<N>_resolve_level_<L>`
- Monolithic pipeline only

### Max attachments

- **Pattern**: `<formatName>/max_attachments_<P>_samples_<N>`
- **Definition**: [vktRenderPassMultisampleResolveTests.cpp#L3211-L3228](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3211-L3228)

### Compatibility

- **Pattern**: `<formatName>/compatibility_samples_<N>`
- Non-dynamic rendering only

### Multi-layer

- **Pattern**: `layers_<L>/<formatName>/samples_<N>`
- **Definition**: [vktRenderPassMultisampleResolveTests.cpp#L3143-L3254](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3143-L3254)

## Test Hierarchy

```
multisample_resolve
|-- <formatName>
|   |-- samples_<N>
|   |-- samples_<N>_baseLayer1
|   |-- samples_<N>_resolve_level_<L>
|   |-- max_attachments_<P>_samples_<N>
|   +-- compatibility_samples_<N>
+-- layers_<L>
    +-- <formatName>
        +-- samples_<N>
```

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Formats | 48 color-only VkFormat values | [vktRenderPassMultisampleResolveTests.cpp#L3084-L3137](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3084-L3137) |
| Sample counts | {2, 4, 8} | [vktRenderPassMultisampleResolveTests.cpp#L3138](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3138) |
| Layer counts | {1, 3, 6} | [vktRenderPassMultisampleResolveTests.cpp#L3139](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3139) |
| Resolve levels | {2, 3, 4} | [vktRenderPassMultisampleResolveTests.cpp#L3140](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L3140) |
| Max attachment counts | Powers of 2 from 4 to 16 | - |

## Support Requirements

Defined at [vktRenderPassMultisampleResolveTests.cpp#L2995-L3070](../../../modules/vulkan/renderpass/vktRenderPassMultisampleResolveTests.cpp#L2995-L3070):

- VK_KHR_maintenance5 for VK_FORMAT_A8_UNORM_KHR
- DEVICE_CORE_FEATURE_GEOMETRY_SHADER when layerCount > 1
- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering + VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- VK_KHR_portability_subset: multisampleArrayImage check
- maxColorAttachments and maxPerStageDescriptorInputAttachments limits

## Verification Methods

- **Resolve** (line 1008): per-pixel comparison against expected resolve result; float/fixed-point uses tcu::floatThresholdCompare; integer uses tcu::intThresholdCompare
- **Max attachments** (line 2263): compares against reference color (0.0, 0.3, 0.6, 0.75) with format-dependent threshold
