# vktPipelineCreationFeedbackTests.cpp

## Overview

[`vktPipelineCreationFeedbackTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1) implements the [`creation_feedback`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1509) topic group. It verifies VK_EXT_pipeline_creation_feedback functionality, testing pipeline creation feedback flags and timing information for graphics and compute pipelines.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineCreationFeedbackTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1)
- Header: [`vktPipelineCreationFeedbackTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.hpp#L1)

## Registration Path

[`createCreationFeedbackTests()`](../../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1506) returns the `creation_feedback` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants, VK only.

## Test Hierarchy

```text
creation_feedback
└── creation_feedback
    ├── graphics
    │   └── {test_param}
    └── compute
        └── {test_param}
```

## Test Families

| Family | Description |
|---|---|
| GraphicsTestCase | Verifies pipeline creation feedback for graphics pipelines |
| ComputeTestCase | Verifies pipeline creation feedback for compute pipelines |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Pipeline type | Enum | Graphics, compute |
| Feedback flags | Bitfield | VALID, APPLICATION_PIPELINE_CACHE_HIT, BASE_PIPELINE_ACCELERATION |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_pipeline_creation_feedback` | Primary extension for all tests |
| `VK_KHR_pipeline_binary` | Required for pipeline binary interaction tests |
| `geometryShader` | Required for geometry shader feedback tests |
| `tessellationShader` | Required for tessellation shader feedback tests |

## Verification Methods

- **Feedback flag verification**: Verify that pipeline creation feedback flags are correctly set
- **Cache hit verification**: Verify that cache hit feedback is reported when pipelines are created from cache
- **Timing verification**: Verify that pipeline creation duration values are reasonable

## Notes

- Pipeline creation feedback tests are VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- The feedback structure includes both overall pipeline feedback and per-stage feedback
