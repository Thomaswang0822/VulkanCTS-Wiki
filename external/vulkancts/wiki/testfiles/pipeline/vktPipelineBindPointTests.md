# vktPipelineBindPointTests.cpp

## Overview

[`vktPipelineBindPointTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1) implements the [`bind_point`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L959) topic group. It verifies pipeline bind point behavior, testing that pipelines are correctly bound to the appropriate bind points (graphics, compute, ray tracing) and that descriptor sets are correctly accessed.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineBindPointTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1)
- Header: [`vktPipelineBindPointTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.hpp#L1)

## Registration Path

[`createBindPointTests()`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L957) returns the `bind_point` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants, VK only.

## Test Hierarchy

```text
bind_point
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| BindPointTest | Verifies pipeline bind point behavior for graphics, compute, and ray tracing pipelines |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Pipeline bind point | Enum | GRAPHICS, COMPUTE, RAY_TRACING |
| Descriptor type | Enum | Storage buffer, uniform buffer |
| PipelineConstructionType | Parameter | All variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_push_descriptor` | Required for push descriptor tests |
| `VK_KHR_descriptor_update_template` | Required for descriptor update template tests |
| `VK_KHR_ray_tracing_pipeline` | Required for ray tracing bind point tests |

## Verification Methods

- **Buffer verification**: Write to storage buffer via pipeline, read back and verify correct values
- **Bind point verification**: Verify that pipelines bound to different bind points access correct descriptor sets

## Notes

- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- Tests include ray tracing pipeline bind point tests when the extension is supported
