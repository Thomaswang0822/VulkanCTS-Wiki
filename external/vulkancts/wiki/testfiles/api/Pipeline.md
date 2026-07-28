## Overview

**Core question:** Can a Vulkan implementation keep pipelines usable after the objects captured at creation time (render pass, pipeline layout) are destroyed, and remain robust when invalid pointers appear only in unused struct fields?

- This page covers the `api.pipeline` test family implemented in [vktApiPipelineTests.cpp](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1) and registered by [createPipelineTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1798-L1809).
- The test family is attached to the `api` test category by [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L121).
- It registers three intermediate nodes under `api.pipeline`: `renderpass`, `pipeline_layout`, and `pipeline_invalid_pointers_unused_structs` (the last is excluded from VKSC builds).
- The nine test case leaves exercise Vulkan deferred-destruction semantics for pipelines, render-pass and framebuffer compatibility, and pipeline-creation robustness against invalid pointers in struct fields whose counts are zero.
- The page explains what each intermediate node tests, how the host validates the result, and what a failure means. Shader behavior is not part of the tested property.

## Background Knowledge

- **Pipeline deferred destruction.** Vulkan allows certain objects captured at pipeline creation time (render pass, pipeline layout) to be destroyed after `vkCreate*Pipelines` returns. The pipeline retains an internal reference; destroying the source object does not invalidate the pipeline or its later use in command buffers.
- **`VK_KHR_maintenance4`.** Extends the deferred-destruction guarantee so that pipeline layouts can be destroyed immediately after `vkCreate*Pipelines` returns, rather than waiting until the pipeline is no longer in use. Vulkan 1.3 promotes this extension to core.
- **Render pass compatibility.** Vulkan defines compatibility rules for render passes that share format, sample count, and attachment structure but differ in load/store ops and initial/final layout. A framebuffer created with one render pass can be used with another compatible render pass.
- **Pointer-field elision.** When a Vulkan struct's count field is zero, the corresponding pointer field is ignored by the implementation. The implementation must not dereference it, even if the pointer value is invalid.

## Registration Hierarchy

```text
api.pipeline
├── renderpass
├── pipeline_layout
└── pipeline_invalid_pointers_unused_structs (non-VKSC only)
```

The `pipeline_layout` intermediate node has a single `lifetime` child that owns five test case leaves; the deeper level is documented in `## Parameter Dimensions and Observed Values` and `## Behavior Parameters` rather than expanded here.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline bind point | `graphics`, `compute` | Selects the graphics or compute pipeline creation path. Graphics cases also need a render pass, framebuffer, and color attachment. | [pipelineLayoutLifetimeTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L848-L1169), [pipelineInvalidPointersUnusedStructsTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1521-L1696) |
| Lifetime mode | destroy after creation, destroy after command buffer end, destroy after pipeline construction | Identifies when the parent object is destroyed relative to pipeline creation, command buffer recording, and submission. The first two rely on core Vulkan deferred destruction; the third requires `VK_KHR_maintenance4`. | [DrawTriangleMode](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L91-L95), [DestroyPipelineLayoutMode](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1250-L1254) |
| Render pass mode | destroy after creation, compatible render pass | Distinguishes between the lifetime case (the render pass used to create a pipeline is destroyed before recording) and the compatibility case (a framebuffer created with one render pass is used with another compatible render pass). | [drawTriangleTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L97-L424), [framebufferCompatibleRenderPassTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L524-L659) |
| Invalid pointer scope | unused-struct invalid pointers | Verifies pipeline creation succeeds when invalid pointers are placed only in pointer fields whose corresponding count is zero. The graphics leaf also enables `rasterizerDiscardEnable` so that viewport, multisample, depth-stencil, and color-blend state pointers are also unused. | [createSimpleGraphicsPipelineInvalidPointers()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1428-L1519) |

The complete set of registered test case leaves is:

| Intermediate node | Test case leaf | Mustpass line |
|---|---|---|
| `renderpass` | `destroy_pipeline_renderpass` | [api.txt#L327783](../../../mustpass/main/vk-default/api.txt#L327783) |
| `renderpass` | `framebuffer_compatible_renderpass` | [api.txt#L327784](../../../mustpass/main/vk-default/api.txt#L327784) |
| `pipeline_layout.lifetime` | `graphics` | [api.txt#L327782](../../../mustpass/main/vk-default/api.txt#L327782) |
| `pipeline_layout.lifetime` | `compute` | [api.txt#L327778](../../../mustpass/main/vk-default/api.txt#L327778) |
| `pipeline_layout.lifetime` | `destroy_after_end` | [api.txt#L327780](../../../mustpass/main/vk-default/api.txt#L327780) |
| `pipeline_layout.lifetime` | `destroy_after_compute_pipeline_construction` | [api.txt#L327779](../../../mustpass/main/vk-default/api.txt#L327779) |
| `pipeline_layout.lifetime` | `destroy_after_graphics_pipeline_construction` | [api.txt#L327781](../../../mustpass/main/vk-default/api.txt#L327781) |
| `pipeline_invalid_pointers_unused_structs` | `compute` | [api.txt#L327776](../../../mustpass/main/vk-default/api.txt#L327776) |
| `pipeline_invalid_pointers_unused_structs` | `graphics` | [api.txt#L327777](../../../mustpass/main/vk-default/api.txt#L327777) |

## Behavior Parameters

The primary behavioral axis is the intermediate node directly below the `api.pipeline` test family. Each value tests a distinct pipeline-related contract.

### `renderpass` — Render pass lifetime and framebuffer compatibility

- Property tested: a graphics pipeline created with a render pass remains usable after that render pass is destroyed, and a framebuffer created with one render pass can be used with another compatible render pass.
- Test mechanism: two test case leaves. `destroy_pipeline_renderpass` destroys the render pass used to create a graphics pipeline before recording the draw, then draws a triangle and verifies the rendered output. `framebuffer_compatible_renderpass` creates a framebuffer with one render pass and begins a render pass instance with another compatible render pass.
- Relation to other values: this is the only intermediate node that exercises the render-pass lifetime and compatibility contract; `pipeline_layout` exercises the analogous contract for pipeline layouts.

### `pipeline_layout` — Pipeline layout lifetime

- Property tested: a pipeline remains usable after its pipeline layout is destroyed, including the `VK_KHR_maintenance4` extension that permits destruction immediately after pipeline construction.
- Test mechanism: five test case leaves under the `lifetime` intermediate node. `graphics` and `compute` cover the two bind points with a pipeline layout destroyed after pipeline creation but before command buffer recording. `destroy_after_end` destroys the layout after `vkEndCommandBuffer` returns. `destroy_after_compute_pipeline_construction` and `destroy_after_graphics_pipeline_construction` destroy the layout immediately after `vkCreate*Pipelines` returns, and require `VK_KHR_maintenance4`.
- Relation to other values: this is the only intermediate node that exercises pipeline-layout lifetime. The two `destroy_after_*_pipeline_construction` leaves are skipped when `VK_KHR_maintenance4` is unsupported; see `## Case Pruning`.

### `pipeline_invalid_pointers_unused_structs` — Invalid pointers in unused struct fields (non-VKSC only)

- Property tested: pipeline creation succeeds when invalid pointers are placed only in pointer fields whose corresponding count is zero.
- Test mechanism: two test case leaves, `graphics` and `compute`. The test passes an invalid pointer value (`reinterpret_cast<void*>(~0)`) in struct fields such as `pVertexAttributeDescriptions`, `pAttachments`, `pInputAttachments`, `pColorAttachments`, `pPreserveAttachments`, `pDependencies`, `pSetLayouts`, and `pPushConstantRanges`, while keeping the matching count fields at zero.
- Relation to other values: this intermediate node is registered only when `CTS_USES_VULKANSC` is not defined and is excluded from VKSC builds. The `graphics` leaf sets `rasterizerDiscardEnable=VK_TRUE` so that viewport, multisample, depth-stencil, and color-blend state pointers are also unused, even though they are non-null.

## Shader Analysis

No shader is involved in the tested behavior. The graphics and compute shaders used by these cases are minimal (vertex positions, a solid red fragment output, or an empty compute body) and exist only to make pipeline creation and command buffer submission legal. They are not part of the tested property and do not get a representative shader walkthrough.

## Runtime Execution and Result Checking

The three intermediate nodes share a common shape: create a parent object, create a pipeline, destroy the parent object, record commands, submit, check result. What differs is what is destroyed, when it is destroyed, and how the result is checked.

### `renderpass` execution and checking

- `destroy_pipeline_renderpass`: the host creates two compatible render passes `renderPassA` and `renderPassB`, creates a graphics pipeline using `renderPassA`, then destroys `renderPassA` before recording the draw. The command buffer begins a render pass instance using `renderPassB`, binds the pipeline, draws a triangle strip, ends the render pass, and copies the color attachment to a host-visible buffer. The host reads one pixel and verifies it is the expected red color (`pixel.x() >= 0.9f`, `pixel.y() <= 0.1f`, `pixel.z() <= 0.1f`, `pixel.w() >= 0.9f`). Failure is reported as `tcu::TestStatus::fail("Fail")`. See [drawTriangleTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L97-L424) and [renderpassLifetimeTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L426-L429).
- `framebuffer_compatible_renderpass`: the host creates a framebuffer with `renderPassA` and begins a render pass instance with the compatible `renderPassB`. The test always passes if `vkQueueSubmit` and `vkQueueWaitIdle` return `VK_SUCCESS`; there is no image or buffer validation. See [framebufferCompatibleRenderPassTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L524-L659).

### `pipeline_layout` execution and checking

- `graphics` and `compute`: the host creates a pipeline using `pipelineLayoutB`, destroys `pipelineLayoutB` after `vkCreate*Pipelines` returns, then binds descriptor sets using two other pipeline layouts (`pipelineLayoutAC`, `pipelineLayoutBC`) and submits the command buffer. The test always passes if execution completes without error. See [pipelineLayoutLifetimeTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L848-L1169).
- `destroy_after_end`: the host creates a compute pipeline, records a dispatch that updates a host-visible storage buffer, destroys the pipeline layout after `vkEndCommandBuffer` returns but before `vkQueueSubmit`, then submits and waits. The host reads back the buffer and checks each element equals `kInitialValue + kBaseValue + i` (50 + 75 + i = 125 + i). Failure reports the unexpected buffer position and value. See [destroyEarlyTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1256-L1409).
- `destroy_after_compute_pipeline_construction` (requires `VK_KHR_maintenance4`): the host creates a compute pipeline, destroys the pipeline layout immediately after `vkCreateComputePipelines` returns, then creates a new pipeline layout with the same descriptor set layout to bind descriptor sets during command buffer recording. The validation logic is identical to `destroy_after_end`. See [destroyAfterCreateComputePipelineTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1416-L1419).
- `destroy_after_graphics_pipeline_construction` (requires `VK_KHR_maintenance4`): the host creates a graphics pipeline, destroys the pipeline layout immediately after `vkCreateGraphicsPipelines` returns, then draws and reads back one pixel. The validation logic is identical to `destroy_pipeline_renderpass`. See [destroyAfterCreateGraphicsPipelineTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1421-L1424).

### `pipeline_invalid_pointers_unused_structs` execution and checking

- Both `graphics` and `compute` leaves create a pipeline with invalid pointers in unused struct fields, then submit a single draw or dispatch. The test always passes if `vkCreateGraphicsPipelines` or `vkCreateComputePipelines` and `vkQueueSubmit` return `VK_SUCCESS` and execution completes without validation errors or crashes. See [pipelineInvalidPointersUnusedStructsTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1521-L1696).
- The `graphics` leaf enables `rasterizerDiscardEnable=VK_TRUE` so that viewport, multisample, depth-stencil, and color-blend state pointers are also unused, even though they are set to the invalid pointer value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `renderpass` | Render-pass lifetime violation, or framebuffer/render-pass compatibility violation. |
| `pipeline_layout` | Pipeline-layout lifetime violation, or descriptor-set binding failure after the original layout is destroyed. |
| `pipeline_invalid_pointers_unused_structs` | Implementation dereferenced an invalid pointer in a struct field whose count was zero. |

### Cause Analysis

#### Render-pass lifetime violation, or framebuffer/render-pass compatibility violation

**Possible failure symptoms:** Two distinct symptoms. For `destroy_pipeline_renderpass`, the host reads back one pixel from the color attachment and finds it is not the expected red color; the test returns `tcu::TestStatus::fail("Fail")` at [drawTriangleTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L414-L416). For `framebuffer_compatible_renderpass`, a non-`VK_SUCCESS` return from `vkQueueSubmit` or `vkQueueWaitIdle`, or a validation error raised during command buffer recording or submission at [framebufferCompatibleRenderPassTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L654-L655).

**Possible implementation causes:** Vulkan states that a graphics pipeline retains a reference to the render pass at creation time, and the render pass object can be destroyed after pipeline creation. The test deliberately destroys `renderPassA` before the pipeline is used to draw, and begins the render pass instance with the compatible `renderPassB`. For framebuffer compatibility, Vulkan defines render-pass compatibility by comparing attachment descriptions for format, sample count, and identity of structure; the test uses two render passes that share format and sample count but differ in load/store ops and final layout, which the spec permits. A failure indicates the implementation retains a dependency on the destroyed render pass object, or enforces a stricter compatibility rule than the spec defines. Source-level investigation of the implementation's render-pass object retention would be needed to confirm a specific cause beyond these spec-level statements.

#### Pipeline-layout lifetime violation, or descriptor-set binding failure after the original layout is destroyed

**Possible failure symptoms:** Three distinct symptom shapes. For `graphics` and `compute`, a non-`VK_SUCCESS` return from `vkQueueSubmit` or `vkQueueWaitIdle`, or a validation error during command buffer recording or submission. For `destroy_after_end`, the host reads back the storage buffer and finds at least one element does not equal the expected `kInitialValue + kBaseValue + i`; the test reports the buffer position and the expected vs. found values at [destroyEarlyTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1395-L1406). For `destroy_after_graphics_pipeline_construction`, the host reads back one pixel and finds it is not the expected red color, with the same `tcu::TestStatus::fail("Fail")` result as `destroy_pipeline_renderpass`.

**Possible implementation causes:** Vulkan states that a pipeline retains a reference to the pipeline layout at creation time, and the pipeline layout can be destroyed after pipeline creation. `VK_KHR_maintenance4` extends this to allow destruction immediately after `vkCreate*Pipelines` returns. The test destroys the pipeline layout at three different points: after pipeline creation but before command buffer recording (`graphics`, `compute`); after `vkEndCommandBuffer` returns but before `vkQueueSubmit` (`destroy_after_end`); and immediately after `vkCreateComputePipelines` or `vkCreateGraphicsPipelines` returns (the two `destroy_after_*_pipeline_construction` leaves). A failure indicates the implementation retains a dependency on the pipeline layout object beyond what the spec permits. For the two `destroy_after_*_pipeline_construction` cases specifically, a failure indicates the implementation does not satisfy the `VK_KHR_maintenance4` destruction guarantee even when the extension is reported as supported. Source-level investigation of the implementation's pipeline-layout object retention would be needed to confirm a specific cause beyond these spec-level statements.

#### Implementation dereferenced an invalid pointer in a struct field whose count was zero

**Possible failure symptoms:** A non-`VK_SUCCESS` return from `vkCreateGraphicsPipelines` or `vkCreateComputePipelines`, a crash during pipeline creation or execution, or a validation error reporting that an invalid pointer was dereferenced at [pipelineInvalidPointersUnusedStructsTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1521-L1696).

**Possible implementation causes:** Vulkan states that pointer fields with a corresponding count of zero are ignored by the implementation. The test deliberately sets such pointer fields to `reinterpret_cast<void*>(~0)` while keeping the matching count at zero, and (for the graphics leaf) sets `rasterizerDiscardEnable=VK_TRUE` to also mark viewport, multisample, depth-stencil, and color-blend state as unused. The fields affected include `pVertexAttributeDescriptions`, `pAttachments`, `pInputAttachments`, `pColorAttachments`, `pPreserveAttachments`, `pDependencies`, `pSetLayouts`, `pPushConstantRanges`, and (in the graphics leaf with `rasterizerDiscardEnable=VK_TRUE`) `pViewportState`, `pMultisampleState`, `pDepthStencilState`, and `pColorBlendState`. A failure indicates the implementation dereferences the pointer without first checking the count field, or applies state validation that should be skipped when `rasterizerDiscardEnable` is `VK_TRUE`. Source-level investigation of the implementation's struct validation order would be needed to identify which specific pointer was dereferenced.

## Case Pruning

### Requirement-based pruning

- `destroy_after_compute_pipeline_construction` and `destroy_after_graphics_pipeline_construction` require the `VK_KHR_maintenance4` extension. The cases are skipped (not failed) when [checkMaintenance4Support()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1245-L1248) reports the extension is unsupported.
- The `destroy_pipeline_renderpass`, `framebuffer_compatible_renderpass`, `pipeline_layout.lifetime.graphics`, and `pipeline_layout.lifetime.compute` leaves require a renderable color attachment format (`VK_FORMAT_B8G8R8A8_UNORM` or `VK_FORMAT_R8G8B8A8_UNORM`); [checkSupport()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1214-L1221) throws `NotSupportedError` if neither is supported.
- The `pipeline_invalid_pointers_unused_structs` leaves also call `checkSupport`, so they share the same color-attachment format requirement even though the `compute` leaf does not render to an attachment.

### Design-based pruning

- The `pipeline_invalid_pointers_unused_structs` intermediate node is excluded from VKSC builds via `#ifndef CTS_USES_VULKANSC` at [createPipelineInvalidPointersUnusedStructsTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1779-L1794). The `renderpass` and `pipeline_layout` intermediate nodes are registered in both Vulkan and VKSC builds.
- The `pipeline_layout.lifetime` intermediate node groups five leaves under a single `lifetime` child rather than registering each leaf directly under `pipeline_layout`. This groups the lifetime-mode variants under one shared axis.
- The `destroy_after_compute_pipeline_construction` leaf uses a compute pipeline, while `destroy_after_graphics_pipeline_construction` uses a graphics pipeline; both exercise the same `VK_KHR_maintenance4` guarantee but through different `vkCreate*Pipelines` entry points.

## Key Takeaways

- The `api.pipeline` test family exercises three distinct pipeline-related contracts: deferred destruction of render passes and pipeline layouts, render-pass and framebuffer compatibility, and robustness against invalid pointers in unused struct fields.
- Vulkan deferred destruction permits destroying the parent object after pipeline creation; `VK_KHR_maintenance4` extends this to allow destruction immediately after `vkCreate*Pipelines` returns.
- Render-pass compatibility rules permit a framebuffer created with one render pass to be used with another compatible render pass, even when load/store ops and initial/final layouts differ.
- Pointer fields with a corresponding count of zero are ignored by the implementation; the test verifies this by passing `~0` as the pointer value.
- See `## Failure Meaning` for the failure interpretation: a failing result means the implementation retains a dependency on a destroyed object, enforces a stricter compatibility rule than the spec defines, or dereferences a pointer that should be ignored.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [createPipelineTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1798-L1809) | Creates the `pipeline` test family root and registers its three direct child intermediate nodes. |
| Header declaration | [vktApiPipelineTests.hpp#L36-L38](../../../modules/vulkan/api/vktApiPipelineTests.hpp#L36-L38) | Declares `createPipelineTests`. |
| Parent registration | [vktApiTests.cpp#L121](../../../modules/vulkan/api/vktApiTests.cpp#L121) | Adds the `pipeline` test family under the `api` test category. |
| `renderpass` registration | [createrenderpassTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1736-L1748) | Registers the `destroy_pipeline_renderpass` and `framebuffer_compatible_renderpass` test case leaves. |
| `pipeline_layout` registration | [createPipelineLayoutTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1770-L1777) | Registers the `pipeline_layout.lifetime` intermediate node. |
| `lifetime` leaf registration | [createPipelineLayoutLifetimeTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1750-L1768) | Registers the five `lifetime` test case leaves and selects their support checks. |
| `pipeline_invalid_pointers_unused_structs` registration | [createPipelineInvalidPointersUnusedStructsTests()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1779-L1794) | Registers the `graphics` and `compute` test case leaves; guarded by `#ifndef CTS_USES_VULKANSC`. |
| `renderpass` lifetime implementation | [drawTriangleTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L97-L424) | Shared implementation for `destroy_pipeline_renderpass` and `destroy_after_graphics_pipeline_construction`. |
| `framebuffer_compatible_renderpass` implementation | [framebufferCompatibleRenderPassTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L524-L659) | Verifies a framebuffer can be used with a compatible render pass. |
| `pipeline_layout` lifetime implementation | [pipelineLayoutLifetimeTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L848-L1169) | Shared implementation for the `graphics` and `compute` leaves of `pipeline_layout.lifetime`. |
| `destroy_after_end` and `destroy_after_compute_pipeline_construction` implementation | [destroyEarlyTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1256-L1409) | Verifies pipeline usability after the pipeline layout is destroyed at different points. |
| `pipeline_invalid_pointers_unused_structs` implementation | [pipelineInvalidPointersUnusedStructsTest()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1521-L1696) | Verifies pipeline creation succeeds with invalid pointers in unused struct fields. |
| `VK_KHR_maintenance4` support check | [checkMaintenance4Support()](../../../modules/vulkan/api/vktApiPipelineTests.cpp#L1245-L1248) | Required by the two `destroy_after_*_pipeline_construction` leaves. |
| Mustpass entries | [api.txt#L327776-L327784](../../../mustpass/main/vk-default/api.txt#L327776-L327784) | Lists the nine `dEQP-VK.api.pipeline.*` test case leaves covered by this page. |
