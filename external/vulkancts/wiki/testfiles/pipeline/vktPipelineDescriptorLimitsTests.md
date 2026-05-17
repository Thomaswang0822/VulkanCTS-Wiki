# vktPipelineDescriptorLimitsTests.cpp

## Overview

[`vktPipelineDescriptorLimitsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L1) implements the [`descriptor_limits`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L966) topic group. It verifies that descriptor set limits are correctly enforced by testing various descriptor counts up to and beyond device maximums.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDescriptorLimitsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L1)
- Header: [`vktPipelineDescriptorLimitsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.descriptor_limits
├── compute_shader (monolithic only)
└── fragment_shader
```

Source: [`createDescriptorLimitsTests()`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L963).

## Test Families

### compute_shader — Descriptor limits via compute shader (monolithic only)

Tests descriptor limits using a compute shader. Each descriptor type is tested with varying descriptor counts. Only registered for the monolithic pipeline construction type. The generated leaf test cases follow the pattern `<descriptor_type>_<count>`, where descriptor types are `samplers`, `uniform_buffers`, `storage_buffers`, `sampled_images`, and `storage_images`, and counts range over 36 values from 3 to 65535.

### fragment_shader — Descriptor limits via fragment shader

Tests descriptor limits using a fragment shader. Same descriptor types as compute, plus input attachments. Input attachment tests are excluded for the shader object variant. The generated leaf test cases follow the pattern `<descriptor_type>_<count>`, where descriptor types are `samplers`, `uniform_buffers`, `storage_buffers`, `sampled_images`, `storage_images`, and `input_attachments`, and counts range over 36 values from 3 to 65535.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| TestType | [Enum](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L56) | Samplers, UniformBuffers, StorageBuffers, SampledImages, StorageImages, InputAttachments |
| numDescriptors | [Array](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L969) | 36 values: {3..20, 31, 32, 63, 64, 100, 127, 128, 199, 200, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65535} |
| useCompShader | bool | `true` (compute), `false` (fragment) |

## Support / Feature Requirements

| Requirement | Condition | Line |
|---|---|---|
| Per-stage descriptor limits | Checked per TestType | [913](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L913) |
| maxPerStageResources | `descCount <= limits.maxPerStageResources - 1` | [908](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L908) |
| maxDescriptorSetLayoutBindings (VulkanSC) | `descCount <= scProps.maxDescriptorSetLayoutBindings` | [902](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L902) |
| Pipeline construction requirements | `checkPipelineConstructionRequirements()` | [953](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L953) |

## Verification Methods

- **Fragment shader**: `tcu::floatThresholdCompare()` with zero threshold against solid-color reference ([line 740](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L740))
- **Compute shader**: Direct SSBO value comparison against expected `tcu::Vec4(0.0, 1.0, 0.0, 1.0)` ([line 748](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L748))

## Notes / Uncertainties

- For StorageBuffers in compute shader, `getDescCount()` returns `descCount - 1` to account for the output SSBO already using one binding
