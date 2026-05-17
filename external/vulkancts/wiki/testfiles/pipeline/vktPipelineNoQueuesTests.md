# vktPipelineNoQueuesTests.cpp

## Overview

[`vktPipelineNoQueuesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1) implements the [`no_queues`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1726) independent root branch. It verifies pipeline creation on a device with no queues, testing that pipelines can be created and cached without any queue family being available.

## Role

Implementation file. This is an independent root branch, not a topic group under variant roots.

## Source Code

- Primary source: [`vktPipelineNoQueuesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1)
- Header: [`vktPipelineNoQueuesTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.no_queues
├── pipeline_cache
├── pipeline_binary
└── shader_binary
```

Source: [`createNoQueuesTests()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1724) returns the `no_queues` group, registered as a direct child of `pipeline` (not under any variant root). Independent root branch, VK only.

## Test Families

### pipeline_cache — Pipeline cache tests on no-queue device

Verifies pipeline creation on a device with no queues using pipeline caches. Each test creates a pipeline for a specific shader stage (compute, raygen, isect, ahit, chit, miss, callable, vertex, fragment, geometry, tessctrl, tesseval, task, mesh) on a device with no queue families, then verifies that pipeline cache creation and retrieval works correctly.

### pipeline_binary — Pipeline binary tests on no-queue device

Verifies pipeline creation on a device with no queues using pipeline binaries. Same shader stage coverage as `pipeline_cache`. Tests that pipeline binary serialization and deserialization works correctly on a no-queue device.

### shader_binary — Shader binary tests on no-queue device

Verifies pipeline creation on a device with no queues using shader binaries. Excludes ray tracing KHR stages (raygen, isect, ahit, chit, miss, callable) since shader binaries do not apply to them. Covers compute, vertex, fragment, geometry, tessctrl, tesseval, task, and mesh stages.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Pipeline type | Enum | Compute, graphics, ray tracing, mesh |
| Pipeline cache | Bool | With/without pipeline cache |
| Shader stage | [`stageCases[]`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1734) | 14 stages (compute, raygen, isect, ahit, chit, miss, callable, vertex, fragment, geometry, tessctrl, tesseval, task, mesh) |
| Test type | [`ttCases[]`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1742) | `pipeline_cache`, `pipeline_binary`, `shader_binary` |

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
