# vktRayTracingPipelineLibraryTests

This registered implementation file registers `pipeline_library` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1225-L1229).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1225-L1245) |

## Registration Hierarchy

```text
ray_tracing_pipeline.pipeline_library
└── configurations
```

## Test Families

### pipeline_library — Registered branch

Pipeline-library tests create linked ray tracing pipeline-library configurations and check shader group handles, capture-replay, and optimization variants. The registered group name is created in [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1227-L1230). Direct children observed in mustpass/source include `configurations`.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `pipeline_library` direct children | `configurations` | [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1227-L1247) |

## Support Requirements

Support requires `VK_KHR_ray_tracing_pipeline` and `VK_KHR_pipeline_library`; non-default handle-check cases require `VK_EXT_pipeline_library_group_handles`, link-time optimization cases require `VK_EXT_graphics_pipeline_library`, maintenance5 cases require `VK_KHR_maintenance5`, and capture/replay cases require `rayTracingPipelineShaderGroupHandleCaptureReplay` [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L298-L318).

## Verification Methods

The implementation verifies shader group handles for non-default cases, compares capture/replay output vectors when capture replay is included, and otherwise reports collected result failures [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L804-L824), [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L985-L995), [vktRayTracingPipelineLibraryTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingPipelineLibraryTests.cpp#L1024).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
