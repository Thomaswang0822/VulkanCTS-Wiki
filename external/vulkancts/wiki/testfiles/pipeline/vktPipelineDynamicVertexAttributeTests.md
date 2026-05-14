# vktPipelineDynamicVertexAttributeTests.cpp

## Overview

[`vktPipelineDynamicVertexAttributeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L1) implements the [`dynamic_vertex_attribute`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L569) topic group of the pipeline category. It verifies that non-sequential vertex attribute locations work correctly with `VK_EXT_vertex_input_dynamic_state`, where vertex input state is set dynamically rather than statically in the pipeline.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineDynamicVertexAttributeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L1)
- Header: [`vktPipelineDynamicVertexAttributeTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_vertex_attribute
└── nonsequential
```

Source: [`createDynamicVertexAttributeTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L565).

## Test Families

### nonsequential — Non-sequential vertex attribute locations

Verifies that non-sequential vertex attribute locations (locations 1 and 7, with 16 total instances) work correctly with `VK_EXT_vertex_input_dynamic_state`. Two pipelines are created with different attribute descriptions bound dynamically, each rendering a colored quad segment, and the results are composited. The test ensures that the dynamic vertex input state correctly handles sparse attribute locations.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| numInstances | Hardcoded | `16u` |
| attributeLocations | Hardcoded | `{1u, 7u}` (non-sequential) |
| pipelineConstructionType | Factory parameter | Monolithic, library, or shader object |

No enumerations or loops over parameter sets in the factory function -- the test is instantiated with fixed parameters.

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `VK_EXT_vertex_input_dynamic_state` + `vertexInputDynamicState` feature | `checkSupport` / `initDeviceCapabilities` | [461](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L461) |
| `VK_EXT_extended_dynamic_state`, `VK_EXT_extended_dynamic_state2` | `initDeviceCapabilities` | [526](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L526) |
| Full `VkPhysicalDeviceFeatures` | `initDeviceCapabilities` | [558](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L558) |
| `VK_EXT_graphics_pipeline_library` + `graphicsPipelineLibrary` feature (library variant) | `initDeviceCapabilities` | [526](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L526) |
| `VK_EXT_shader_object` + `shaderObject` feature (shader object variant) | `initDeviceCapabilities` | [526](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L526) |
| `VK_KHR_dynamic_rendering` + `dynamicRendering` feature (shader object variant) | `initDeviceCapabilities` | [526](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L526) |
| Pipeline construction requirements | `checkSupport` | [473](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L473) |

## Verification Methods

**Reference rendering with float threshold comparison** at [line 415](../../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L415):

```cpp
tcu::floatThresholdCompare(log, "color", "Image compare", referenceAccess, resultPixelAccess,
                            tcu::Vec4(0.01f), tcu::COMPARE_LOG_RESULT)
```

A reference image is constructed programmatically (gradient-like red segment at center of 32x32 image). The rendered result is read back from the color attachment. Pixel-by-pixel comparison with threshold 0.01f.

## Test Principles Observed

- **Sparse attribute location coverage**: Tests non-contiguous attribute locations (1, 7) rather than sequential (0, 1)
- **Dynamic state focus**: Specifically tests the dynamic vertex input state path, not the static pipeline path
- **Multi-pipeline compositing**: Two pipelines with different dynamic attribute descriptions render to the same target, verifying that dynamic state changes take effect correctly

## Notes / Uncertainties

- This is a focused test with a single test case and fixed parameters, unlike the more expansive vertex input tests in `vktPipelineVertexInputTests.cpp`
- The test is relatively small compared to other pipeline topic groups
