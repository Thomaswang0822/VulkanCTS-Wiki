# vktPipelineNoQueuesTests.cpp

## Overview

[`vktPipelineNoQueuesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1) implements the [`no_queues`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1726) independent root branch. It verifies pipeline creation on a device with no queues, testing that pipelines can be created and cached without any queue family being available.

## Role

Implementation file. This is an independent root branch, not a topic group under variant roots.

## Source Code

- Primary source: [`vktPipelineNoQueuesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1)
- Header: [`vktPipelineNoQueuesTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.hpp#L1)

## Registration Path

[`createNoQueuesTests()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1724) returns the `no_queues` group, registered as a direct child of `pipeline` (not under any variant root).

**Variant coverage**: Independent root branch, VK only. Not a `createChildren()` topic group.

## Test Hierarchy

```text
no_queues
├── compute
│   └── {test_case}
├── graphics
│   └── {test_case}
├── ray_tracing
│   └── {test_case}
└── mesh
    └── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| NoQueuesTestCase | Verifies pipeline creation on a device with no queues |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Pipeline type | Enum | Compute, graphics, ray tracing, mesh |
| Pipeline cache | Bool | With/without pipeline cache |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_ray_tracing_pipeline` | Required for ray tracing pipeline tests |
| `VK_KHR_acceleration_structure` | Required for ray tracing pipeline tests |
| `VK_EXT_mesh_shader` | Required for mesh shader pipeline tests |

## Verification Methods

- **Pipeline creation verification**: Create pipeline on a device with no queues, verify creation succeeds
- **Cache verification**: Verify that pipeline cache works correctly with no-queue device

## Notes

- This is the only independent root branch in the pipeline category
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- Uses a custom device creation with no queue families
