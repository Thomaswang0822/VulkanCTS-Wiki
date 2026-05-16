# vktRenderPassCustomResolveTests

## Source

[vktRenderPassCustomResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.custom_resolve
├── fast_lib
└── monolithic
```

Registered under renderpass1, renderpass2, and dynamic_rendering root groups (non-SC, no secondary CB or partial secondary CB). The representative root above shows renderpass1 children; dynamic_rendering additionally includes a `shader_objects` child. Registered group name: `"custom_resolve"` ([L5777](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5777)).

## Test Families

### monolithic — Monolithic pipeline construction

Custom resolve tests using monolithic pipeline construction (PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC). Contains leaf test cases for various resolve configurations including:
- `simple_average` — Simple average resolve
- `simple_fixed` — Simple fixed-value resolve
- `simple_sample_2` — Simple selected-sample resolve
- Complex configurations with multiple color/depth/stencil attachments, format changes, and attachment index changes
- FragmentRegionCase tests for fragment density map region interactions
- FDMCase tests for fragment density map variants with custom resolve

### fast_lib — Fast-linked graphics pipeline library

Custom resolve tests using fast-linked graphics pipeline library construction (PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY). Contains the same test structure as monolithic.

### shader_objects — Shader object construction (dynamic_rendering only)

Custom resolve tests using shader object construction with unlinked SPIR-V (PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_UNLINKED_SPIRV). Only present under the dynamic_rendering variant. Contains the same test structure as monolithic.

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Pipeline construction types | MONOLITHIC, FAST_LINKED_LIBRARY, SHADER_OBJECT_UNLINKED_SPIRV ([L5786-L5790](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5786-L5790)) |
| Depth/stencil formats | 7 formats ([L5792-L5800](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5792-L5800)) |
| Resolve types | AVERAGE, FIXED_VALUE, SELECTED_SAMPLE |
| Attachment configurations | Various color/depth/stencil attachment setups |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| customResolve feature | From VkCustomResolveFeaturesEXT ([L593](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L593)) |
| dynamicRenderingLocalRead feature | ([L605](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L605)) |
| VK_EXT_dynamic_rendering_unused_attachments | When unused attachments present ([L665](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L665)) |
| VK_EXT_shader_stencil_export | When stencil aspect used ([L691](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L691)) |
| Format and sample count support | Runtime checks |

## Verification

| Aspect | Method |
|--------|--------|
| Color | tcu::floatThresholdCompare with format-adaptive thresholds ([L3465](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3465)) |
| Depth/stencil | tcu::dsThresholdCompare ([L3410](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3410)) |
| sRGB formats | Thresholds widened by 2x ([L3462](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3462)) |
