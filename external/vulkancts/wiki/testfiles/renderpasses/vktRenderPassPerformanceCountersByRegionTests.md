# vktRenderPassPerformanceCountersByRegionTests

## Source

[vktRenderPassPerformanceCountersByRegionTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp)

## Registration

Added to root group (non-SC).

Registered group name: `"performance_counters_by_region"` ([L1618](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1618))

## Test Families

```
performance_counters_by_region
+-- PerformanceCountersByRegionRenderPassTestInstance
    Tests VK_ARM_performance_counters_by_region with render passes.
    +-- layers_1
    |   Single layer configuration.
    +-- layers_2
        Two layer configuration.
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Format | VK_FORMAT_R8G8B8A8_UNORM only ([L1583](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1583)) |
| Layer counts | 1 and 2 ([L1598-L1607](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1598-L1607)) |
| Counter | "Fragment warps" with min=0, max=0, fragment=256 |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_KHR_buffer_device_address | Always ([L1544](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1544)) |
| VK_EXT_separate_stencil_usage | Always ([L1545](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1545)) |
| VK_ARM_performance_counters_by_region | Always ([L1546](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1546)) |
| VK_KHR_get_physical_device_properties2 | Always ([L1547](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1547)) |
| VK_KHR_shader_clock with shaderDeviceClock feature | ([L1564-L1567](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1564-L1567)) |
| performanceCountersByRegion feature | ([L1578](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1578)) |

## Verification

| Aspect | Method |
|--------|--------|
| Counter validation | Per-region counters within expected min/max ranges ([L1223-L1275](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1223-L1275)) |
| Timestamp validation | No overlap between different logical devices ([L1445-L1478](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1445-L1478)) |
| Attachment validation | Color is blue (0,0,1,1) with tolerance 0.01 ([L1313-L1344](../../../modules/vulkan/renderpass/vktRenderPassPerformanceCountersByRegionTests.cpp#L1313-L1344)) |
| Results | tcu::ResultCollector for aggregate results |
