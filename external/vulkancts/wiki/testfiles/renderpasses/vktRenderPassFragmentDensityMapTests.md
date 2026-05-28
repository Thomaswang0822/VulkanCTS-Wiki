# vktRenderPassFragmentDensityMapTests

## Source

[vktRenderPassFragmentDensityMapTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.fragment_density_map
├── 1_view
├── depth_format
└── properties
```

Registered under all rendering types (renderpass1, renderpass2, dynamic_rendering) at the rendering-type root level, monolithic pipeline only, non-SC. The representative root above shows renderpass1 children; renderpass2 and dynamic_rendering additionally include `2_views`, `4_views`, `6_views`, and `offset` children (multiview is not supported in renderpass1). Registered group name: `"fragment_density_map"` ([L5485](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L5485)).

## Test Families

### 1_view — Single-view fragment density map tests

Static, deferred, and dynamic density maps with subsampled and non-subsampled images for a single view. Contains subgroups organized by render type (render, render_copy), then by size ratio (divisible_density_size, non_divisible_density_size), then by sample count, with leaf FragmentDensityMapTest cases for each fragment area and density map type combination.

### depth_format — Depth format FDM tests (renderpass1 only)

Tests fragment density map behavior with different depth formats (d16_unorm, d32_sfloat, d24_unorm_s8_uint). Only present under renderpass1 since multiview is not supported in renderpass1 and this provides depth-specific coverage. Uses deferred density maps.

### properties — FDM property and feature tests

Tests for various fragment density map properties and features. Contains leaf tests:
- `2_subsampled_samplers`, `4_subsampled_samplers`, `6_subsampled_samplers`, `8_subsampled_samplers` — Subsampled sampler count tests
- `imageless_fb` — Imageless framebuffer with FDM
- `subsampled_loads` — Subsampled image load operations (requires VK_EXT_fragment_density_map2)
- `subsampled_coarse_reconstruction` — Coarse reconstruction with subsampled images (requires VK_EXT_fragment_density_map2)
- `memory_access` — Memory access behavior with FDM
- `maintenance5` — VK_KHR_maintenance5 interactions with FDM

### 2_views, 4_views, 6_views — Multiview FDM tests (renderpass2 and dynamic_rendering only)

Same structure as `1_view` but with 2, 4, and 6 views respectively. Not present under renderpass1 since multiview is not supported in the legacy render pass path.

### offset — FDM offset tests (renderpass2 and dynamic_rendering only)

Fragment density map offset tests using VK_EXT_fragment_density_map_offset. Contains subgroups:
- `oversized_fdm` — Oversized FDM with horizontal and vertical offset variants, including multiview, suspend/resume, and extra large variants
- `min_shift` — Minimum shift by granularity with horizontal and vertical offset variants
- `clamp_to_edge` — Clamp-to-edge behavior with horizontal and vertical offset variants

### density_formula — Density formula verification tests (renderpass2 and dynamic_rendering only)

Tests verification of the fragment density map texel size formula introduced in VK_EXT_fragment_density_map spec version 3: texel size = 2^ceil(log2(floor(framebufferSize / densityMapSize))). Added under each view group (1_view, 2_views, 4_views, 6_views) for renderpass2 and dynamic_rendering only (not renderpass1). Contains a `1_sample` subgroup with three test cases:
- `static_subsampled_4_4` — Static subsampled density map with fragment area {4,4}
- `deferred_subsampled_4_4` — Deferred subsampled density map with fragment area {4,4}
- `dynamic_subsampled_4_4` — Dynamic subsampled density map with fragment area {4,4}

Uses renderMultiplier 33.0f/16.0f, densityMapSize {16,16}.

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| View counts | {1, 2, 4, 6} ([L4963](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4963)) |
| Render types | render, render_copy ([L4973](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4973)) |
| Size ratios | divisible_density_size (4.0), non_divisible_density_size (3.75) ([L4979](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4979)) |
| Sample counts | {1, 2, 4, 8} ([L4985](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4985)) |
| Fragment areas | {1,2}, {2,1}, {2,2} ([L4990](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L4990)) |
| Density map types | static_subsampled, deferred_subsampled, dynamic_subsampled, static_nonsubsampled, deferred_nonsubsampled, dynamic_nonsubsampled |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_EXT_fragment_density_map | Always ([L1515](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L1515)) |
| VK_EXT_fragment_density_map spec version >= 3 | Required by density_formula tests (checkDensityFormula) |
| VK_EXT_fragment_density_map2 | For subsampled loads, coarse reconstruction ([L1566-L1608](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L1566-L1608)) |
| VK_EXT_fragment_density_map_offset / VK_QCOM_fragment_density_map_offset | For offset tests ([L3371-L3373](../../../modules/vulkan/renderpass/vktRenderPassFragmentDensityMapTests.cpp#L3371-L3373)) |
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
| Density formula | Verifies the 2^ceil(log2(floor(fb/fdm))) texel-size formula from VK_EXT_fragment_density_map spec version 3 in verifyImage() |
