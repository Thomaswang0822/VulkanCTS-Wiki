# [vktApiPipelineTests.cpp](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1)

## Overview

Tests Vulkan pipeline object lifetime semantics: render pass lifetime after pipeline creation, pipeline layout lifetime after pipeline creation, compatible render pass usage with framebuffers, and invalid pointer handling in unused pipeline create-info structs.

## Role of File

Implementation-heavy. Contains all test logic, shader source generation, helper functions, and the registration function [createPipelineTests()](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1798). Delegates to sub-group creation functions.

## Source Code

- Implementation: [vktApiPipelineTests.cpp](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1)
- Header: [vktApiPipelineTests.hpp](../../modules/vulkan/api/vktApiPipelineTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L121)

## Registration Path

```
api
  +-- pipeline
```

## Test Hierarchy

```
pipeline
  +-- renderpass
  |     +-- destroy_pipeline_renderpass
  |     +-- framebuffer_compatible_renderpass
  +-- pipeline_layout
  |     +-- lifetime
  |           +-- graphics
  |           +-- compute
  |           +-- destroy_after_end
  |           +-- destroy_after_compute_pipeline_construction
  |           +-- destroy_after_graphics_pipeline_construction
  +-- pipeline_invalid_pointers_unused_structs  [non-SC]
        +-- graphics
        +-- compute
```

## Test Families

### Renderpass Lifetime

[renderpassLifetimeTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp#L426) wraps [drawTriangleTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp#L97) with DTM_DESTROY_RENDER_PASS_AFTER_CREATING_PIPELINE. Creates a graphics pipeline using renderPassA, destroys renderPassA, then begins a render pass with a compatible renderPassB and draws a triangle. Verifies the draw succeeds by checking a pixel value (red channel > 0.9, green/blue < 0.1, alpha > 0.9) at [line 415](../../modules/vulkan/api/vktApiPipelineTests.cpp#L415). Registered at [line 1741](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1741).

[framebufferCompatibleRenderPassTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp#L524) creates a framebuffer with renderPassA, then begins a render pass using a compatible renderPassB (same attachment format but different load/store ops and final layout). Verifies the command buffer submission succeeds. Registered at [line 1744](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1744).

### Pipeline Layout Lifetime

[pipelineLayoutLifetimeGraphicsTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp#L848) creates a graphics pipeline with a pipeline layout, destroys the layout, then binds the pipeline and descriptor sets using the destroyed layout handle. Verifies the draw succeeds. The test uses a vertex+fragment shader pair and checks pixel output.

[pipelineLayoutLifetimeComputeTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp#L848) does the same for a compute pipeline.

[destroyAfterEndCommndBufferTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp) destroys the pipeline layout after recording commands but before submission.

[destroyAfterCreateComputePipelineTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp) and [destroyAfterCreateGraphicsPipelineTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp) destroy the pipeline layout immediately after pipeline creation, requiring VK_KHR_maintenance4. Registered at [lines 1758-1765](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1758).

### Pipeline Invalid Pointers Unused Structs (non-SC)

[pipelineInvalidPointersUnusedStructsGraphicsTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp) and [pipelineInvalidPointersUnusedStructsComputeTest()](../../modules/vulkan/api/vktApiPipelineTests.cpp) test that pipelines can be created with invalid pointers in create-info structs that are not actually used (e.g., pTessellationState when no tessellation is active). Registered at [lines 1785-1790](../../modules/vulkan/api/vktApiPipelineTests.cpp#L1785).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Pipeline bind point | VK_PIPELINE_BIND_POINT_GRAPHICS, VK_PIPELINE_BIND_POINT_COMPUTE |
| DrawTriangleMode | DTM_DESTROY_RENDER_PASS_AFTER_CREATING_PIPELINE, DTM_DESTROY_PIPELINE_LAYOUT_AFTER_CREATING_PIPELINE |
| Render pass compatibility | Same render pass, compatible render pass (different load/store ops) |
| Layout destruction timing | After pipeline creation, after command buffer recording, after end of command buffer |
| Image format | VK_FORMAT_B8G8R8A8_UNORM, VK_FORMAT_R8G8B8A8_UNORM (fallback) |
| Image tiling | VK_IMAGE_TILING_LINEAR, VK_IMAGE_TILING_OPTIMAL (based on format features) |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_maintenance4 | destroy_after_compute_pipeline_construction, destroy_after_graphics_pipeline_construction |
| Color attachment format support | renderpass and pipeline_layout lifetime graphics tests |

## Verification Methods

- **Pixel value checking**: renderpassLifetimeTest reads back a pixel and checks RGBA values against expected red triangle output at [line 415](../../modules/vulkan/api/vktApiPipelineTests.cpp#L415)
- **Pass-by-default**: framebufferCompatibleRenderPassTest and pipeline layout lifetime tests pass if command buffer submission succeeds without errors
- **Image logging**: renderpassLifetimeTest logs the result image for visual inspection at [line 419](../../modules/vulkan/api/vktApiPipelineTests.cpp#L419)
- **VK_CHECK**: all Vulkan API calls are checked for VK_SUCCESS

## Test Principles Observed

- Object lifetime: core focus is verifying that render passes and pipeline layouts can be destroyed after their information has been consumed by pipeline creation
- Compatibility: framebuffer_compatible_renderpass tests the spec rule that compatible render passes can be used interchangeably with a framebuffer
- Robustness: invalid pointers in unused structs tests verify that implementations do not dereference pointers in create-info structs that are not relevant to the pipeline being created
- Format fallback: getRenderTargetFormat() at [line 56](../../modules/vulkan/api/vktApiPipelineTests.cpp#L56) tries B8G8R8A8_UNORM first, then R8G8B8A8_UNORM

## Notes / Uncertainties

- The pipelineInvalidPointersUnusedStructs tests were not fully read in detail but are registered at lines 1785-1790
- The destroyAfterEndCommndBufferTest function was not fully read but is registered at line 1758
- The checkSupport function referenced in the registration is a local function that checks for color attachment format support
