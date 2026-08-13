## Overview

**Core question:** Does the device report the minimum `VK_QCOM_image_processing` limits required for image-processing operations?

- This page covers the `image_processing.api.properties` test family implemented by [`vktImageProcessingApiTests.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L48-L144).
- The test queries `VkPhysicalDeviceImageProcessingPropertiesQCOM` through `vkGetPhysicalDeviceProperties2` and checks the extension's minimum limits.
- The source registers one fixed test case, `properties`; the mustpass file contains the corresponding `dEQP-VK.image_processing.api.properties` case.

## Background Knowledge

- Vulkan exposes extension-specific physical-device properties by attaching a structure to the `pNext` chain of `VkPhysicalDeviceProperties2`. The query writes the implementation's advertised limits into that structure; the test then checks the returned fields rather than exercising an image-processing command.
- Vulkan 1.3 promoted the format-feature query structures used by the broader image-processing category. Devices using an older API version need `VK_KHR_format_feature_flags2` for this test's support path.

## Registration Hierarchy

```text
image_processing.api
└── properties
```

The `api` test family is added to the category by [`createChildren()`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L78); [`createImageProcessingApiTests()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L137-L143) registers the `properties` test case.

## Parameter Dimensions and Observed Values

This is a single fixed test case. The only runtime variation is the number of repeated property queries, selected by the deterministic CTS random generator.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case | `properties` | Queries and validates the QCOM property structure. | [`createImageProcessingApiTests()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L137-L143) |
| Query iterations | Random integer from `1` through `20`, inclusive | Repeats the same property-limit checks within one test execution. | [`ImageProcessingApiTestInstance::iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L85-L100) |

## Behavior Parameters

The test has no meaningful behavioral parameter axis: every registered case checks the same seven minimum limits.

- `maxWeightFilterPhases` must be at least `1024`.
- `maxWeightFilterDimension.width` and `.height` must each be at least `64`.
- `maxBoxFilterBlockSize.width` and `.height` must each be at least `64`.
- `maxBlockMatchRegion.width` and `.height` must each be at least `64`.

The comparisons are implemented in [`ImageProcessingApiTestInstance::iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L93-L127).

## Shader Analysis

This test does not create or execute a shader. Its tested behavior is a host-side physical-device property query.

## Runtime Execution and Result Checking

- [host] The support check requires `VK_QCOM_image_processing`. When the used API version is below Vulkan 1.3, it also requires `VK_KHR_format_feature_flags2` ([`checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L66-L72)).
- [host] The instance chooses an iteration count from the inclusive range `1..20`, using a generator seeded with `1234` ([constructor and `iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L74-L99)).
- [host] Each iteration zero-initializes `VkPhysicalDeviceImageProcessingPropertiesQCOM`, attaches it to `VkPhysicalDeviceProperties2`, and calls `getPhysicalDeviceProperties2` ([query path](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L101-L110)).
- [host] The test returns failure at the first property below its minimum. If all iterations pass, it returns `TestStatus::pass("Pass")` ([result path](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L112-L127)).

## Failure Meaning

### Failure Cause Mapping

For this fixed test case, a failure means that at least one required property was reported below the coded extension minimum.

### Cause Analysis

#### Reported image-processing limit is below the required minimum

**Possible failure symptoms:** The test identifies one of `maxWeightFilterPhases`, `maxWeightFilterDimension`, `maxBoxFilterBlockSize`, or `maxBlockMatchRegion` as less than its required value and returns a failure status.

**Possible implementation causes:** The implementation may be reporting an incorrect physical-device limit, may be exposing `VK_QCOM_image_processing` with incomplete property support, or may have a property-query/pNext handling defect. The test does not distinguish among those causes; source-level and implementation-level investigation is needed.

## Case Pruning

### Requirement-based pruning

- The case is not executed when `VK_QCOM_image_processing` is unavailable.
- For API versions below Vulkan 1.3, the case is not executed when `VK_KHR_format_feature_flags2` is unavailable.

### Design-based pruning

There are no additional generated combinations. The repeated query count is an execution detail, not a separate registered test case.

## Key Takeaways

- `properties` is a fixed API-contract test, not a functional block-matching workload.
- A passing result establishes that the queried QCOM property values meet the minimum limits checked by this CTS implementation.
- The test does not establish the correctness of block-matching execution; those checks belong to the `block_matching` test family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category dispatch | [`vktImageProcessingTests.cpp#createChildren()`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L78) | Adds the `api` test family to `image_processing`. |
| API registration | [`createImageProcessingApiTests()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L137-L143) | Registers the `properties` test case. |
| Support gate | [`ImageProcessingApiTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L66-L72) | Defines extension and API-version prerequisites. |
| Property query and checks | [`ImageProcessingApiTestInstance::iterate()`](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L93-L127) | Performs the query, minimum comparisons, and final status. |
| Mustpass case | [`image-processing.txt`](../../../mustpass/main/vk-default/image-processing.txt) | Contains `dEQP-VK.image_processing.api.properties`. |
