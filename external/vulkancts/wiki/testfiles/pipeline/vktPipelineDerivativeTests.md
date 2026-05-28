# vktPipelineDerivativeTests.cpp

## Overview

[`vktPipelineDerivativeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L1) implements the [`derivative`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L172) topic group. It verifies pipeline derivative functionality, testing compute pipeline derivatives where a base pipeline is created first and a derivative pipeline shares compiled code.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDerivativeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L1)
- Header: [`vktPipelineDerivativeTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.derivative
└── compute
```

Source: [`createDerivativeTests()`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L170). Variant coverage: Monolithic only, VK only. Compute pipeline tests not repeated across construction types.

## Test Families

### compute — Compute pipeline derivative tests

Verifies compute pipeline derivative creation and execution. Contains three test cases:
- `derivative_by_handle`: Creates a derivative compute pipeline by handle, using `VK_PIPELINE_CREATE_DERIVATIVE_SOURCE_BIT` on the base pipeline and `VK_PIPELINE_CREATE_DERIVATIVE_DERIVATIVE_BIT` on the derivative.
- `derivative_by_handle_maintenance5`: Same as `derivative_by_handle` but with `VK_KHR_maintenance5` enabled (non-VulkanSC only).
- `derivative_by_index`: Creates a derivative compute pipeline by index, using the base pipeline index in `vkCreateComputePipelines`.

All tests verify that the derivative pipeline produces correct computation results and that the derivative flag bits are correctly handled.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Monolithic only |
| Derivative type | Enum | Base pipeline, derivative pipeline |

## Support / Feature Requirements

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
