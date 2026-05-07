# vktPipelineMultisampleResolveRenderAreaTests.cpp

## Overview

[`vktPipelineMultisampleResolveRenderAreaTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L1) implements the [`resolve`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L516) topic group under `multisample`. It verifies multisample resolve behavior when the render area is smaller than the attachment size, testing with different shapes and sample counts.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMultisampleResolveRenderAreaTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L1)
- Header: [`vktPipelineMultisampleResolveRenderAreaTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.hpp#L1)

## Registration Path

[`createMultisampleResolveRenderpassRenderAreaTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L514) returns the `resolve` group, added to the `multisample` group by `createMultisampleTests()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
resolve
└── renderpass_renderarea
    └── {shape}_{sample_count}
```

## Test Families

| Family | Description |
|---|---|
| MultisampleRenderAreaTest | Verifies multisample resolve with render areas smaller than attachment size |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| TestShape | Enum | SHAPE_RECTANGLE, SHAPE_DIAMOND, SHAPE_PARALLELOGRAM |
| Sample count | Array | 2, 4, 8, 16 |
| Render area size | Fixed | 32x32 |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| Standard multisample support | Basic multisample feature support |

## Verification Methods

- **Pixel comparison**: Render with restricted render area, resolve, compare resolved image against expected values within the render area
- **Area boundary check**: Verify that pixels outside the render area are not affected

## Notes

- This test specifically focuses on the interaction between render area size and multisample resolve correctness
