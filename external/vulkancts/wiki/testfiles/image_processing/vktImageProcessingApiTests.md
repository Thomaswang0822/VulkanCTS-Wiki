# vktImageProcessingApiTests.cpp

## Overview

This file implements the `api` test group for the `image_processing` category. It contains a single test case (`properties`) that validates the minimum property limits reported by the `VK_QCOM_image_processing` extension via `VkPhysicalDeviceImageProcessingPropertiesQCOM`.

This is an **implementation file** that both registers and implements its test cases. It is not a registration-only file; the test logic (instance class) resides here as well.

**Source:** [vktImageProcessingApiTests.cpp](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp)

## Registration Hierarchy

```text
image_processing.api
└── properties
```

## Registration Details

### `createImageProcessingApiTests()` (line 137)

Creates the `api` test group and adds a single child:

| Test Case | Line | Class |
|---|---|---|
| `properties` | [L141](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L141) | `ImageProcessingApiTest` |

Exported via [vktImageProcessingApiTests.hpp](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.hpp#L39).

## Test Families

### properties

Verifies that the `VK_QCOM_image_processing` extension reports property values that meet or exceed the minimum required limits specified by the extension specification.

**Test class:** `ImageProcessingApiTest` ([L48](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L48))
**Instance class:** `ImageProcessingApiTestInstance` ([L74](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L74))

#### Support / Feature Requirements

| Requirement | Line | Detail |
|---|---|---|
| Vulkan 1.3+ or `VK_KHR_format_feature_flags2` | [L68-L69](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L68) | `VK_KHR_format_feature_flags2` is required if API version < 1.3 |
| `VK_QCOM_image_processing` | [L71](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L71) | Device extension must be supported |

#### Verification Method

The test calls `vkGetPhysicalDeviceProperties2` with the `VkPhysicalDeviceImageProcessingPropertiesQCOM` pNext chain, then validates each property against its minimum required value. The query is repeated a random number of times (1-20 iterations, seeded at [L97](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L97)) to ensure consistent results across multiple queries.

| Property | Minimum Required | Line |
|---|---|---|
| `maxWeightFilterPhases` | >= 1024 | [L112](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L112) |
| `maxWeightFilterDimension.width` | >= 64 | [L115](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L115) |
| `maxWeightFilterDimension.height` | >= 64 | [L116](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L116) |
| `maxBoxFilterBlockSize.width` | >= 64 | [L119](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L119) |
| `maxBoxFilterBlockSize.height` | >= 64 | [L120](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L120) |
| `maxBlockMatchRegion.width` | >= 64 | [L123](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L123) |
| `maxBlockMatchRegion.height` | >= 64 | [L124](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L124) |

#### Parameter Dimensions

This test has no parameterized dimensions. It is a single, fixed test case.

## Dependencies

| Include | Role |
|---|---|
| `vktImageProcessingBase.hpp` | Base test class (`ImageProcessingTest`) |
| `vktImageProcessingTests.hpp` | Category-level declarations |
| `vktImageProcessingTestsUtil.hpp` | Utility types and helpers |
| `vktTestCase.hpp` | Core test case framework |
| `vkDefs.hpp` | Vulkan type definitions |
| `deRandom.hpp` | Random number generation for iteration count |
