## Overview

**Core question:** Does the device expose the operation-specific properties required by `VK_QCOM_image_processing`?

- This page covers the four host-side property cases in [`vktImageProcessingApiTests.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L48-L207).

## Background Knowledge

- Vulkan exposes extension-specific physical-device properties by attaching a structure to `VkPhysicalDeviceProperties2` through `pNext`. The query writes the implementation's limits into that structure; the test then checks the fields relevant to the selected operation rather than executing an image-processing command.
- Vulkan 1.3 promoted the format-feature query structures used by the broader image-processing category. Devices using an older API version need `VK_KHR_format_feature_flags2` for this test's support path.

## Registration Hierarchy

```text
image_processing.api
├── properties_block_matching_sad
├── properties_block_matching_ssd
├── properties_weight_sampling
└── properties_box_filtering
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning | Evidence |
|---|---|---|---|
| Operation | `block_matching_sad`, `block_matching_ssd`, `weight_sampling`, `box_filtering` | Selects feature and property checks. | [`createImageProcessingApiTests()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L192-L207) |
| Iterations | `1..20` | Repeats the deterministic query. | [`iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L104-L181) |

## Behavior Parameters

The operation selects the relevant feature and minimum limits:

- `maxBlockMatchRegion.width` and `.height` must each be at least `64` for SAD and SSD;
- `maxWeightFilterPhases` must be at least `1024`, and both dimensions of `maxWeightFilterDimension` must be at least `64` for weighted sampling;
- both dimensions of `maxBoxFilterBlockSize` must be at least `64` for box filtering.

The comparisons are implemented in [`ImageProcessingApiTestInstance::iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L104-L181).

## Shader Analysis

No shader is created or executed.

## Runtime Execution and Result Checking

- [host] The support check requires `VK_QCOM_image_processing`. When the used API version is below Vulkan 1.3, it also requires `VK_KHR_format_feature_flags2`; each operation additionally requires its corresponding feature ([support](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L75-L105)).
- [host] The instance chooses an iteration count from the inclusive range `1..20`, using a generator seeded with `1234` ([constructor and iterate](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L104-L123)).
- [host] Each iteration zero-initializes `VkPhysicalDeviceImageProcessingPropertiesQCOM`, attaches it to `VkPhysicalDeviceProperties2`, and calls `getPhysicalDeviceProperties2` ([query and checks](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L124-L181)).
- [host] The test returns failure at the first relevant property below its minimum; if all iterations pass, it returns `TestStatus::pass("Pass")`.

## Failure Meaning

### Failure Cause Mapping

A failure indicates an unavailable operation feature or an advertised property below the required minimum.

### Cause Analysis

#### Property query or feature exposure

**Possible failure symptoms:** The selected case is reported unsupported or a checked property is below its minimum.

**Possible implementation causes:**

The implementation may expose incomplete feature support, report an incorrect limit, or mishandle the properties2 pNext query. The test does not distinguish these causes.

## Case Pruning

### Requirement-based pruning

Missing required extensions or the operation-specific feature causes the corresponding case to be unsupported.

### Design-based pruning

There are no generated combinations beyond the four operation cases and repeated queries.

## Key Takeaways

- These are host-side limit checks, not functional image-processing workloads.
- SAD and SSD share block-match limits; weighted sampling and box filtering use separate property groups.

## Source Reference Appendix

| Entry point | Link | Purpose |
|---|---|---|
| Registration | [`createImageProcessingApiTests()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L192-L207) | Registers the four cases. |
| Checks | [`ImageProcessingApiTest`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L75-L181) | Implements support, query, and validation behavior. |
| Mustpass | [`image-processing.txt`](../../../mustpass/main/vk-default/image-processing.txt) | Lists the cases. |