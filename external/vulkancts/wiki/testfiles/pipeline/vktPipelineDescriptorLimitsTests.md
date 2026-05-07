# vktPipelineDescriptorLimitsTests.cpp

## Overview

[`vktPipelineDescriptorLimitsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L1) implements the [`descriptor_limits`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L966) topic group. It verifies that descriptor set limits are correctly enforced by testing various descriptor counts up to and beyond device maximums.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDescriptorLimitsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L1)
- Header: [`vktPipelineDescriptorLimitsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.hpp#L1)

## Registration Path

[`createDescriptorLimitsTests()`](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L963) returns the `descriptor_limits` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants. Compute shader sub-group is monolithic only. Input attachments excluded for shader object.

## Test Hierarchy

```text
descriptor_limits
├── compute_shader                        (monolithic only)
│   ├── samplers_<N>
│   ├── uniform_buffers_<N>
│   ├── storage_buffers_<N>
│   ├── sampled_images_<N>
│   └── storage_images_<N>
└── fragment_shader
    ├── samplers_<N>
    ├── uniform_buffers_<N>
    ├── storage_buffers_<N>
    ├── sampled_images_<N>
    ├── storage_images_<N>
    └── input_attachments_<N>             (excluded for shader object)
```

## Test Families

### 1. compute_shader

Tests descriptor limits using a compute shader. Each descriptor type is tested with varying descriptor counts. Only registered for monolithic.

### 2. fragment_shader

Tests descriptor limits using a fragment shader. Same descriptor types as compute, plus input attachments (excluded for shader object variant).

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
