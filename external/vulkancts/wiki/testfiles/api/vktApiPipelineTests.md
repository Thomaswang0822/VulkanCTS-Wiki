# [vktApiPipelineTests.cpp](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1)

## Overview

Tests Vulkan pipeline object lifetime semantics, render pass compatibility, and pipeline creation with invalid pointers in unused structs. Validates that pipeline layouts and render passes can be destroyed after pipeline creation and the pipelines remain functional.

## Role of File

Implementation-heavy. Contains test logic for pipeline layout lifetime, render pass lifetime, and invalid pointer handling. The public entry point [createPipelineTests()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1798) assembles the test tree.

## Source Code

- Source: [vktApiPipelineTests.cpp](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1)
- Header: [vktApiPipelineTests.hpp](../../../../../modules/vulkan/api/vktApiPipelineTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L121) adds `pipeline` group to `api`

## Registration Path

```
api
 +-- pipeline
      +-- renderpass
      |    +-- destroy_pipeline_renderpass
      |    +-- framebuffer_compatible_renderpass
      +-- pipeline_layout
      |    +-- lifetime
      |         +-- graphics
      |         +-- compute
      |         +-- destroy_after_end
      |         +-- destroy_after_compute_pipeline_construction
      |         +-- destroy_after_graphics_pipeline_construction
      +-- pipeline_invalid_pointers_unused_structs   (non-VKSC only)
           +-- graphics
           +-- compute
```

## Test Hierarchy

```
pipeline
 +-- renderpass
 |    +-- destroy_pipeline_renderpass        -- draw after destroying the renderpass used to create a pipeline
 |    +-- framebuffer_compatible_renderpass  -- use framebuffer created with another compatible render pass
 +-- pipeline_layout
 |    +-- lifetime
 |         +-- graphics                              -- destroy layout after graphics pipeline creation
 |         +-- compute                               -- destroy layout after compute pipeline creation
 |         +-- destroy_after_end                     -- destroy layout after ending command buffer
 |         +-- destroy_after_compute_pipeline_construction  -- destroy layout after compute pipeline built (VK_KHR_maintenance4)
 |         +-- destroy_after_graphics_pipeline_construction -- destroy layout after graphics pipeline built (VK_KHR_maintenance4)
 +-- pipeline_invalid_pointers_unused_structs  (non-VKSC only)
      +-- graphics                          -- graphics pipeline with invalid pointers in unused pNext structs
      +-- compute                           -- compute pipeline with invalid pointers in unused pNext structs
```

## Test Families

### renderpass

Tests render pass lifetime and compatibility. `destroy_pipeline_renderpass` verifies that a pipeline created with a render pass remains valid after the render pass is destroyed, and drawing still works. `framebuffer_compatible_renderpass` verifies that a framebuffer created with one render pass can be used with a compatible render pass. Implemented by [renderpassLifetimeTest()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L97) and [framebufferCompatibleRenderPassTest()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp).

### pipeline_layout / lifetime

Tests that pipeline layouts can be destroyed after pipeline creation and the pipelines remain functional. The `graphics` and `compute` variants test basic lifetime. The `destroy_after_end` variant destroys the layout after recording commands. The `destroy_after_compute_pipeline_construction` and `destroy_after_graphics_pipeline_construction` variants test VK_KHR_maintenance4 semantics where the layout can be destroyed immediately after pipeline construction. Implemented by [createPipelineLayoutLifetimeTests()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1750).

### pipeline_invalid_pointers_unused_structs (non-VKSC only)

Tests that pipelines can be created with invalid pointers in pNext chains of unused struct fields without crashing. Both graphics and compute pipeline variants are tested. Implemented by [pipelineInvalidPointersUnusedStructsTest()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Pipeline Bind Point | graphics, compute |
| Lifetime Mode | destroy after creation, destroy after command buffer end, destroy after pipeline construction |
| Render Pass Mode | destroy after creation, compatible render pass |

## Support / Feature Requirements

- `VK_KHR_maintenance4` required for `destroy_after_compute_pipeline_construction` and `destroy_after_graphics_pipeline_construction` tests ([checkMaintenance4Support()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp))
- Graphics tests require a renderable color attachment format
- `pipeline_invalid_pointers_unused_structs` group is excluded from VKSC builds

## Verification Methods

- Lifetime tests: Destroy the layout/render pass, create pipeline, record and submit command buffer, verify queue submission succeeds
- Render pass compatibility: Create framebuffer with one render pass, begin render pass with a compatible render pass, verify no errors
- Invalid pointers: Create pipeline with invalid pNext pointers in unused structs, verify pipeline creation and execution succeed without crashes

## Test Principles Observed

- Vulkan deferred destruction semantics: objects can be destroyed after they are captured by pipeline creation
- VK_KHR_maintenance4 extends lifetime guarantees to allow destruction immediately after pipeline construction
- Invalid pointer tests verify implementation robustness against uninitialized pNext fields

## Notes / Uncertainties

- The group name is `pipeline` as confirmed in [createPipelineTests()](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1800)
- The `destroy_after_end` test destroys the pipeline layout after `vkEndCommandBuffer` but before `vkQueueSubmit`, testing an intermediate lifetime point
- The `pipeline_invalid_pointers_unused_structs` tests are guarded by `#ifndef CTS_USES_VULKANSC` ([L1779](../../../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1779))
