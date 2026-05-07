# vktRenderPassSampleReadTests

## Source

- [vktRenderPassSampleReadTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp)

## Registration

- **Path**: Added to `suballocation` subgroup within each top-level group
- **Registered group name**: `"sampleread"` at [vktRenderPassSampleReadTests.cpp#L1183](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1183)

## Role

Implementation file

## Test Families

### ADD mode

- **Pattern**: `numsamples_<N>_add`
- **Description**: Sums all sample loads
- **Definition**: [vktRenderPassSampleReadTests.cpp#L1156-L1162](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1156-L1162)

### SELECT mode

- **Pattern**: `numsamples_<N>_selected_sample_<S>`
- **Description**: Reads specific sample index
- **Definition**: [vktRenderPassSampleReadTests.cpp#L1165-L1175](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1165-L1175)

## Test Hierarchy

```
sampleread
|-- numsamples_<N>_add
+-- numsamples_<N>_selected_sample_<S>
```

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| Sample counts | {2, 4, 8, 16, 32} | [vktRenderPassSampleReadTests.cpp#L1145](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1145) |
| TestMode | TESTMODE_ADD, TESTMODE_SELECT | [vktRenderPassSampleReadTests.cpp#L497-L503](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L497-L503) |
| Selected sample | 0 to sampleCount-1 for SELECT mode | - |

## Support Requirements

Defined at [vktRenderPassSampleReadTests.cpp#L1110-L1122](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1110-L1122):

- DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING
- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING

## Verification Methods

Defined at [vktRenderPassSampleReadTests.cpp#L1004-L1024](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1004-L1024):

- Shader-internal validation: outputs 1.0 if sample read matches expected value
- tcu::floatThresholdCompare with zero threshold against all-1.0 reference
