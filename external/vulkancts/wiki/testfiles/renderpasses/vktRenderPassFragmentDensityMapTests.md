# vktRenderPassFragmentDensityMapTests

## Source

[vktRenderPassFragmentDensityMapTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp)

## Registration

Added to root group (monolithic pipeline, non-SC).

Registered group name: `"fragment_density_map"` ([L5410](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L5410))

## Test Families

```
fragment_density_map
+-- FragmentDensityMapTest
|   Static, deferred, and dynamic density maps with
|   subsampled and non-subsampled images.
+-- FDMOffsetOversizedFDMCase
|   Oversized FDM with offsets.
+-- FDMOffsetMinShiftCase
|   Minimum shift by granularity.
+-- FDMOffsetClampToEdgeCase
|   Clamp-to-edge behavior.
+-- Properties sub-group
    +-- subsampled_sampler_counts
    +-- imageless_fb
    +-- subsampled_loads
    +-- coarse_reconstruction
    +-- memory_access
    +-- maintenance5
+-- Offset sub-groups
    +-- oversized_fdm
    |   Horizontal and vertical offset variants.
    +-- min_shift
    |   Horizontal and vertical offset variants.
    +-- clamp_to_edge
        Horizontal and vertical offset variants.
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| View counts | {1, 2, 4, 6} ([L4931](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4931)) |
| Render types | render, render_copy ([L4941](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4941)) |
| Size ratios | divisible_density_size (4.0), non_divisible_density_size (3.75) ([L4947](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4947)) |
| Sample counts | {1, 2, 4, 8} ([L4953](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4953)) |
| Fragment areas | {1,2}, {2,1}, {2,2} ([L4958](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4958)) |
| Density map types | static_subsampled, deferred_subsampled, dynamic_subsampled, static_nonsubsampled, deferred_nonsubsampled, dynamic_nonsubsampled |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_EXT_fragment_density_map | Always ([L1515](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L1515)) |
| VK_EXT_fragment_density_map2 | For subsampled loads, coarse reconstruction ([L1566-L1608](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L1566-L1608)) |
| VK_EXT_fragment_density_map_offset / VK_QCOM_fragment_density_map_offset | For offset tests ([L3337-L3339](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L3337-L3339)) |
| VK_KHR_dynamic_rendering | As needed |
| VK_KHR_dynamic_rendering_local_read | As needed |
| VK_KHR_multiview | As needed |
| VK_KHR_imageless_framebuffer | As needed |
| VK_KHR_maintenance5 | As needed |
| DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING | Always |
| Offset granularity checks | Runtime validation |

## Verification

| Aspect | Method |
|--------|--------|
| Main FDM | Histogram of colors; checks FragSizeEXT variable values and color counts |
| Oversized FDM | tcu::floatThresholdCompare with zero threshold on half-image regions |
| Min shift | Exact match via tcu::floatThresholdCompare; if not exact, checks high-density pixel preservation with QualityWarning |
| Clamp to edge | tcu::floatThresholdCompare on half-image regions |
