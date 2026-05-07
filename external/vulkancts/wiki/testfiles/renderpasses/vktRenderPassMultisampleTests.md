# vktRenderPassMultisampleTests

## Source

- [vktRenderPassMultisampleTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup within each top-level group
- **Registered group name**: `"multisample"` at [vktRenderPassMultisampleTests.cpp#L2515](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2515)

## Role

Implementation file

## Test Families

### Per-format per-sample-count tests

- **Pattern**: `<formatName>/samples_<N>`
- **Definition**: [vktRenderPassMultisampleTests.cpp#L2458-L2504](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2458-L2504)

### Separate stencil usage

- **Pattern**: `separate_stencil_usage/<formatName>/samples_<N>/test_depth` and `test_stencil`
- **Definition**: [vktRenderPassMultisampleTests.cpp#L2456-L2508](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2456-L2508)

## Test Hierarchy

```
multisample
|-- <formatName>
|   |-- samples_2
|   |-- samples_4
|   |-- samples_8
|   |-- samples_16
|   +-- samples_32
+-- separate_stencil_usage
    +-- <formatName>
        +-- samples_<N>
            |-- test_depth
            +-- test_stencil
```

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Formats | 50 VkFormat values | [vktRenderPassMultisampleTests.cpp#L2394-L2453](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2394-L2453) |
| Sample counts | {2, 4, 8, 16, 32} | [vktRenderPassMultisampleTests.cpp#L2454](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2454) |
| Separate stencil usage | TEST_DEPTH, TEST_STENCIL | [vktRenderPassMultisampleTests.cpp#L99-L100](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L99-L100) |

Note: Non-monolithic pipelines skip sample counts > 4.

## Support Requirements

Defined at [vktRenderPassMultisampleTests.cpp#L2328-L2380](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L2328-L2380):

- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- VK_EXT_separate_stencil_usage + VK_KHR_get_physical_device_properties2 when separateStencilUsage
- VK_KHR_maintenance5 for VK_FORMAT_A8_UNORM_KHR
- Vulkan 1.4 dynamicRenderingLocalReadMultisampledAttachments / dynamicRenderingLocalReadDepthStencilAttachments

## Verification Methods

Defined at [vktRenderPassMultisampleTests.cpp#L1679-L1778](../../../modules/vulkan/renderpass/vktRenderPassMultisampleTests.cpp#L1679-L1778):

- Per-sample pixel comparison with XOR-based reference
- Depth: tcu::floatThresholdCompare with threshold 1.0/1024.0
- Stencil: exact comparison
- Color: dispatches by TextureChannelClass with format-appropriate comparison
