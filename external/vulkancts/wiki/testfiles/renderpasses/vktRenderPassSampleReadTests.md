# vktRenderPassSampleReadTests

## Source

- [vktRenderPassSampleReadTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.sampleread
├── numsamples_2_add
├── numsamples_2_selected_sample_0
├── numsamples_2_selected_sample_1
├── numsamples_4_add
├── numsamples_4_selected_sample_0
├── numsamples_4_selected_sample_1
├── numsamples_4_selected_sample_2
├── numsamples_4_selected_sample_3
├── numsamples_8_add
├── numsamples_8_selected_sample_0
├── numsamples_8_selected_sample_1
├── numsamples_8_selected_sample_2
├── numsamples_8_selected_sample_3
├── numsamples_8_selected_sample_4
├── numsamples_8_selected_sample_5
├── numsamples_8_selected_sample_6
├── numsamples_8_selected_sample_7
├── numsamples_16_add
├── numsamples_16_selected_sample_0
├── numsamples_16_selected_sample_1
├── numsamples_16_selected_sample_2
├── numsamples_16_selected_sample_3
├── numsamples_16_selected_sample_4
├── numsamples_16_selected_sample_5
├── numsamples_16_selected_sample_6
├── numsamples_16_selected_sample_7
├── numsamples_16_selected_sample_8
├── numsamples_16_selected_sample_9
├── numsamples_16_selected_sample_10
├── numsamples_16_selected_sample_11
├── numsamples_16_selected_sample_12
├── numsamples_16_selected_sample_13
├── numsamples_16_selected_sample_14
├── numsamples_16_selected_sample_15
├── numsamples_32_add
├── numsamples_32_selected_sample_0
├── numsamples_32_selected_sample_1
├── numsamples_32_selected_sample_2
├── numsamples_32_selected_sample_3
├── numsamples_32_selected_sample_4
├── numsamples_32_selected_sample_5
├── numsamples_32_selected_sample_6
├── numsamples_32_selected_sample_7
├── numsamples_32_selected_sample_8
├── numsamples_32_selected_sample_9
├── numsamples_32_selected_sample_10
├── numsamples_32_selected_sample_11
├── numsamples_32_selected_sample_12
├── numsamples_32_selected_sample_13
├── numsamples_32_selected_sample_14
├── numsamples_32_selected_sample_15
├── numsamples_32_selected_sample_16
├── numsamples_32_selected_sample_17
├── numsamples_32_selected_sample_18
├── numsamples_32_selected_sample_19
├── numsamples_32_selected_sample_20
├── numsamples_32_selected_sample_21
├── numsamples_32_selected_sample_22
├── numsamples_32_selected_sample_23
├── numsamples_32_selected_sample_24
├── numsamples_32_selected_sample_25
├── numsamples_32_selected_sample_26
├── numsamples_32_selected_sample_27
├── numsamples_32_selected_sample_28
├── numsamples_32_selected_sample_29
├── numsamples_32_selected_sample_30
└── numsamples_32_selected_sample_31
```

Evidence:
- `sampleread` group created at [`createRenderPassSampleReadTests()`](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1183)
- Direct children are individual test cases added from [vktRenderPassSampleReadTests.cpp#L1148-L1176](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1148-L1176)

Note: The representative root uses `renderpass1`; the same topic group also appears under `renderpass2` and `dynamic_rendering`. Non-monolithic pipelines limit sample counts to {2, 4}.

## Role

Implementation file

## Test Families

### numsamples_2_add — ADD mode with 2 samples

Sums all sample loads for a render target with 2 samples. Uses `TESTMODE_ADD`.

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1156-L1162](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1156-L1162)

### numsamples_2_selected_sample_0 through numsamples_2_selected_sample_1 — SELECT mode with 2 samples

Reads a specific sample index for a render target with 2 samples. Uses `TESTMODE_SELECT`. One test per sample index (0 to sampleCount-1).

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1165-L1175](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1165-L1175)

### numsamples_4_add — ADD mode with 4 samples

Sums all sample loads for a render target with 4 samples. Uses `TESTMODE_ADD`.

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1156-L1162](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1156-L1162)

### numsamples_4_selected_sample_0 through numsamples_4_selected_sample_3 — SELECT mode with 4 samples

Reads a specific sample index for a render target with 4 samples. Uses `TESTMODE_SELECT`. One test per sample index (0 to 3).

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1165-L1175](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1165-L1175)

### numsamples_8_add — ADD mode with 8 samples

Sums all sample loads for a render target with 8 samples. Uses `TESTMODE_ADD`.

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1156-L1162](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1156-L1162)

### numsamples_8_selected_sample_0 through numsamples_8_selected_sample_7 — SELECT mode with 8 samples

Reads a specific sample index for a render target with 8 samples. Uses `TESTMODE_SELECT`. One test per sample index (0 to 7).

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1165-L1175](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1165-L1175)

### numsamples_16_add — ADD mode with 16 samples

Sums all sample loads for a render target with 16 samples. Uses `TESTMODE_ADD`.

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1156-L1162](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1156-L1162)

### numsamples_16_selected_sample_0 through numsamples_16_selected_sample_15 — SELECT mode with 16 samples

Reads a specific sample index for a render target with 16 samples. Uses `TESTMODE_SELECT`. One test per sample index (0 to 15).

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1165-L1175](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1165-L1175)

### numsamples_32_add — ADD mode with 32 samples

Sums all sample loads for a render target with 32 samples. Uses `TESTMODE_ADD`.

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1156-L1162](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1156-L1162)

### numsamples_32_selected_sample_0 through numsamples_32_selected_sample_31 — SELECT mode with 32 samples

Reads a specific sample index for a render target with 32 samples. Uses `TESTMODE_SELECT`. One test per sample index (0 to 31).

- **Definition**: [vktRenderPassSampleReadTests.cpp#L1165-L1175](../../../modules/vulkan/renderpass/vktRenderPassSampleReadTests.cpp#L1165-L1175)

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
