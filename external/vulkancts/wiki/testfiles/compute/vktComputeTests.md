# vktComputeTests.cpp

## Overview

[`vktComputeTests.cpp`](../../../modules/vulkan/compute/vktComputeTests.cpp#L26-L36) is the compute category dispatcher. It includes the root-level compute subgroup headers and registers the same child-building callback under the pipeline construction variants created in [`createTests()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85). The Vulkan API test plan states that compute dispatch tests validate call parameters and that work-group counts and invocation IDs are passed correctly to shader invocations ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L676-L681)).

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktComputeTests.cpp`](../../../modules/vulkan/compute/vktComputeTests.cpp#L1)
- Related utility header: [`vkComputePipelineConstructionUtil.hpp`](../../../framework/vulkan/vkComputePipelineConstructionUtil.hpp#L1)

## Registration Hierarchy

```text
compute
├── pipeline
├── shader_object_spirv (non-VulkanSC only)
└── shader_object_binary (non-VulkanSC only)
```

## Test Families

### pipeline — Standard compute-pipeline construction

[`createTests()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L70-L71) registers `pipeline` with [`createChildren()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64) and `COMPUTE_PIPELINE_CONSTRUCTION_TYPE_PIPELINE`.

### shader_object_spirv — SPIR-V shader-object construction

For non-VulkanSC builds, [`shader_object_spirv`](../../../modules/vulkan/compute/vktComputeTests.cpp#L72-L76) reuses the same children with `COMPUTE_PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_SPIRV`.

### shader_object_binary — Binary shader-object construction

For non-VulkanSC builds, [`shader_object_binary`](../../../modules/vulkan/compute/vktComputeTests.cpp#L72-L83) reuses the same children with `COMPUTE_PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_BINARY`.

## Parameter Dimensions

The dispatcher parameterizes the category by compute pipeline construction type and delegates the actual test matrices to child files registered from [`createChildren()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L52-L62).

## Support / Feature Requirements

No device feature checks are implemented directly here. The conditional registration excludes shader-object and extension-heavy branches from VulkanSC builds through `CTS_USES_VULKANSC` guards in [`createTests()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L72-L84) and [`createChildren()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L55-L63).

## Verification Methods

No verification logic is implemented in this dispatcher; verification is performed by the registered implementation files.

## Test Principles Observed

- Category registration is split from implementation by forwarding the same child builder to multiple construction-type roots ([`createTests()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L70-L76)).
- Root-level implementation branches are added in a fixed order by [`createChildren()`](../../../modules/vulkan/compute/vktComputeTests.cpp#L52-L62).

## Notes / Uncertainties

- The `shader_object_spirv` and `shader_object_binary` roots are conditionally absent in VulkanSC builds; the hierarchy tree notes this condition rather than claiming unconditional registration.
