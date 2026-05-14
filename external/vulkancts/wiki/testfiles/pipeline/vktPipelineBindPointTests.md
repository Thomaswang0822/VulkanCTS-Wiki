# vktPipelineBindPointTests.cpp

## Overview

[`vktPipelineBindPointTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1) implements the [`bind_point`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L959) topic group. It verifies pipeline bind point behavior, testing that pipelines are correctly bound to the appropriate bind points (graphics, compute, ray tracing) and that descriptor sets are correctly accessed.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineBindPointTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1)
- Header: [`vktPipelineBindPointTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.bind_point
├── graphics_compute
├── graphics_raytracing
└── compute_raytracing (monolithic only)
```

Source: [`createBindPointTests()`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954).

## Test Families

### graphics_compute — Graphics and compute bind point interaction

Tests the interaction between graphics and compute pipeline bind points. Each pair group contains update-type subgroups (combinations of descriptor set update methods such as normal sets, push descriptors, and descriptor update templates), which in turn contain setup-sequence subgroups, which contain leaf test cases for each dispatch-sequence permutation. Verifies that pipelines bound to graphics and compute bind points access the correct descriptor sets regardless of binding order.

### graphics_raytracing — Graphics and ray tracing bind point interaction

Tests the interaction between graphics and ray tracing pipeline bind points. Same hierarchical structure as `graphics_compute`, with update-type, setup-sequence, and dispatch-sequence subgroups. Requires `VK_KHR_ray_tracing_pipeline` support. Verifies that graphics and ray tracing pipelines do not interfere with each other's descriptor set bindings.

### compute_raytracing — Compute and ray tracing bind point interaction (monolithic only)

Tests the interaction between compute and ray tracing pipeline bind points. Only registered under the monolithic variant because non-monolithic variants skip pairs that do not include a graphics bind point. Same hierarchical structure as the other pair groups. Requires `VK_KHR_ray_tracing_pipeline` support.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Pipeline bind point pair | Enum pair | graphics+compute, graphics+raytracing, compute+raytracing |
| Descriptor set update type | Enum | Normal, push descriptor, descriptor update template |
| Setup sequence | Permutation | Pipeline binds and set binds in all orderings |
| Dispatch sequence | Permutation | Draw/compute/trace calls in all orderings |
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
