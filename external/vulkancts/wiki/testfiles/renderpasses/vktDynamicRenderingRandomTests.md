# vktDynamicRenderingRandomTests

## Source

[vktDynamicRenderingRandomTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp)

## Registration

Added to dynamic_rendering root group (no secondary CB).

Registered group name: `"random"` ([line 1097](../../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp#L1097))

## Test Families

```
random
|-- Randomized dynamic rendering tests
```

**Parameter Dimensions** ([lines 1099-1113](../../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp#L1099-L1113)):

- geometry: {true, false}
- tessellation: {true, false}
- multiview: {true, false}
- randomSeed: 0..99
- Total: 2 x 2 x 2 x 100 = 800 tests

**Verification** ([lines 825-851](../../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp#L825-L851)):

- `tcu::floatThresholdCompare` with threshold `Vec4(0.02f)`
- Also verifies occlusion query pool results

## Support Requirements

| Requirement | Context |
|---|---|
| VK_KHR_dynamic_rendering | [line 882](../../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp#L882) |
| VK_KHR_multiview | Required when `enableMultiview` ([lines 885-886](../../../modules/vulkan/renderpass/vktDynamicRenderingRandomTests.cpp#L885-L886)) |
| DEVICE_CORE_FEATURE_GEOMETRY_SHADER | Required when `enableGeometry` |
| DEVICE_CORE_FEATURE_TESSELLATION_SHADER | Required when `enableTessellation` |
