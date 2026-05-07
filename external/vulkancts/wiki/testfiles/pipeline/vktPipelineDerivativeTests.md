# vktPipelineDerivativeTests.cpp

## Overview

[`vktPipelineDerivativeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L1) implements the [`derivative`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L172) topic group. It verifies pipeline derivative functionality, testing compute pipeline derivatives where a base pipeline is created first and a derivative pipeline shares compiled code.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDerivativeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L1)
- Header: [`vktPipelineDerivativeTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.hpp#L1)

## Registration Path

[`createDerivativeTests()`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L170) returns the `derivative` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Monolithic only, VK only. Compute pipeline tests not repeated across construction types.

## Test Hierarchy

```text
derivative
└── compute
    └── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| Compute derivative test | Verifies compute pipeline derivative creation and execution |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Monolithic only |
| Derivative type | Enum | Base pipeline, derivative pipeline |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| Compute pipeline support | Required for all derivative tests |

## Verification Methods

- **Execution verification**: Verify that derivative compute pipeline produces correct results
- **Derivative flag verification**: Verify that `VK_PIPELINE_CREATE_DERIVATIVE_SOURCE_BIT` and `VK_PIPELINE_CREATE_DERIVATIVE_DERIVATIVE_BIT` are correctly handled

## Notes

- Only registered for monolithic pipeline construction type
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- Compute pipeline derivative tests are not applicable to graphics pipeline library variants
