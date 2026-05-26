# vktRenderPassPerformanceCountersByRegionTests

## Source

[vktRenderPassPerformanceCountersByRegionTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.performance_counters_by_region
└── r8g8b8a8_unorm
```

Registered in all three rendering-type roots (non-SC) via [`createRenderPassPerformanceCountersByRegionTests`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1615). The single direct child `r8g8b8a8_unorm` is a format-named subgroup created in [`initTests`](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1581).

## Test Families

### r8g8b8a8_unorm — R8G8B8A8_UNORM format tests

Contains layer-count tests for VK_ARM_performance_counters_by_region with the sole tested format VK_FORMAT_R8G8B8A8_UNORM ([L1583](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1583)):

- **layers_1** — Single layer configuration ([L1598-L1607](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1598-L1607)).
- **layers_2** — Two layer configuration ([L1598-L1607](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1598-L1607)).

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM only ([L1583](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1583)) |
| Layer counts | 1 and 2 ([L1598-L1607](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1598-L1607)) |
| Counter | "Fragment warps" with min=0, max=0, fragment=256 |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_KHR_buffer_device_address | Always ([L1535](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1535)) |
| VK_EXT_separate_stencil_usage | Always ([L1536](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1536)) |
| VK_ARM_performance_counters_by_region | Always ([L1537](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1537)) |
| VK_KHR_get_physical_device_properties2 | Always as an instance functionality check ([L1538](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1538)) |
| VK_KHR_create_renderpass2 | For `RENDERING_TYPE_RENDERPASS2` ([L1540-L1541](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1540-L1541)) |
| VK_KHR_dynamic_rendering | For `RENDERING_TYPE_DYNAMIC_RENDERING` ([L1543-L1544](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1543-L1544)) |
| VK_KHR_pipeline_library / VK_EXT_graphics_pipeline_library | For library pipeline construction, with `graphicsPipelineLibrary` feature ([L1546-L1552](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1546-L1552)) |
| VK_KHR_shader_clock with shaderDeviceClock feature | ([L1555-L1558](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1555-L1558)) |
| performanceCountersByRegion feature | ([L1560-L1569](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1560-L1569)) |

## Verification

| Aspect | Method |
|--------|--------|
| Counter validation | Per-region counters within expected min/max ranges ([L1223-L1275](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1223-L1275)) |
| Timestamp validation | No overlap between different logical devices ([L1445-L1478](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1445-L1478)) |
| Attachment validation | Color is blue (0,0,1,1) with tolerance 0.01 ([L1313-L1344](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1313-L1344)) |
| Results | tcu::ResultCollector for aggregate results |
