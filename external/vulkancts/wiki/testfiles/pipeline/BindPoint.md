## Overview

**Core question:** Does each pipeline bind point retain its own pipeline or shader-object state and descriptor state when two types of work are recorded and executed in different orders?

- `vktPipelineBindPointTests.cpp` implements the `pipeline.bind_point` test family and registers the `graphics_compute`, `graphics_raytracing`, and `compute_raytracing` intermediate nodes ([registration](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L1083)).
- Each test case selects two bind points, one descriptor update route for each, a permutation of four setup operations, and a permutation of two execution operations. For shader-object construction variants, the graphics setup operation binds graphics shader objects and dynamic state instead of a `VkPipeline`; compute and ray tracing still use pipelines.
- The selected shaders write distinct values to separate storage buffers. Graphics cases also write a known color to a 1×1 attachment, so a wrong bind-point association reaches host-visible checks.
- The `compute_raytracing` family is present only for monolithic pipeline construction. Non-monolithic construction types retain the two pairs that include graphics.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A pipeline bind point associates a pipeline with the command class that uses it. Vulkan maps graphics shader stages to `VK_PIPELINE_BIND_POINT_GRAPHICS` and draw commands, compute to `VK_PIPELINE_BIND_POINT_COMPUTE` and dispatch commands, and ray-tracing stages to `VK_PIPELINE_BIND_POINT_RAY_TRACING_KHR` and trace-rays commands ([Vulkan shader binding](../../../../vulkan-docs/src/chapters/shaders.adoc#L1747-L1800)).
- Descriptor commands use a pipeline bind point and pipeline layout to establish the descriptor state consumed by that pipeline. Push-descriptor update templates also store the intended bind point, layout, and set number ([descriptor update template fields](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4174-L4209)).

## Registration Hierarchy

```text
pipeline.monolithic.bind_point
├── graphics_compute
├── graphics_raytracing
└── compute_raytracing
```

The source registers the same `bind_point` family under the monolithic, pipeline-library, fast-linked-library, and shader-object construction variants. Only the monolithic variant includes `compute_raytracing`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Bind-point pair | `graphics_compute`, `graphics_raytracing`, `compute_raytracing` | Selects the two independent pipeline or shader-object and descriptor-state paths tested together. | [`testPairs`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L961-L966) |
| Descriptor update route for each selected bind point | `write`, `push`, `template_push` | Selects allocated descriptor-set binding, direct push descriptors, or push descriptors populated through a template. | [`SetUpdateType` conversion](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L854-L869), [registration loops](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1032-L1045) |
| Setup order | 24 permutations of pipeline or graphics-shader-object setup and descriptor binds | Checks whether setup order changes the state later consumed at each bind point. | [`setupSequence`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1047-L1075) |
| Execution order | Two permutations of the selected operations | Checks both orders of draw, dispatch, and trace-rays work. | [`dispatchSequence`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1060-L1070) |
| Pipeline construction type | `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_linked_binary`, `shader_object_linked_spirv`, `shader_object_unlinked_binary`, `shader_object_unlinked_spirv` | Reuses the same bind-point behavior through supported pipeline construction paths. | [`createBindPointTests` parameter](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L973) |

Each pair has 9 ordered descriptor-route combinations, 24 setup orders, and 2 execution orders, for 432 test case leaves. The monolithic family has 1,296 leaves. Each inspected non-monolithic mustpass list has 864 leaves because it contains only the two graphics-containing pairs.

## Behavior Parameters

The primary behavioral axis is the registered bind-point pair. It changes the pipeline stages, command types, resources, feature requirements, and failure localization, while the update routes and order permutations exercise the same state-separation question within each pair.

### `graphics_compute`: graphics and compute state separation

The test prepares graphics state and binds a compute pipeline, supplies one descriptor path for each, then records a draw and a dispatch in both possible orders. The graphics state comes from a graphics pipeline in pipeline-based construction variants and graphics shader objects plus dynamic state in shader-object variants. The fragment shader writes `1` to the graphics buffer and green to the attachment; the compute shader writes `2` to the compute buffer.

### `graphics_raytracing`: graphics and ray-tracing state separation

The test combines a graphics draw with one ray-tracing dispatch. The fragment shader writes `1` and green, while the ray-generation shader writes `3` to its separate buffer. This value also exercises the graphics pipeline or shader-object path and the ray-tracing pipeline and shader binding table setup.

### `compute_raytracing`: compute and ray-tracing state separation

The test combines a compute dispatch with one ray-tracing dispatch. The shaders write `2` and `3` to their separate buffers. The source intentionally excludes this pair from non-monolithic construction variants because those variants skip pairs without graphics.

## Shader Analysis

The shaders are generated test fixtures, not the primary behavior axis. `BindPointTest::initPrograms()` declares one storage-buffer array at set 0, binding 0 and writes one fixed sentinel per pipeline type ([generated programs](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L212-L280)). Graphics also writes a fixed green color. The test does not compare shader algorithms or generated SPIR-V structure, so no representative shader walkthrough is needed. The ray-generation source uses SPIR-V 1.4 because the source supplies that build option.

## Runtime Execution and Result Checking

- `iterate()` creates one host-visible storage buffer for each selected bind point and clears each buffer before recording ([buffer setup](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L428-L454)). Graphics cases additionally create a 1×1 `VK_FORMAT_R8G8B8A8_UNORM` color attachment and framebuffer ([graphics attachment](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L456-L485)).
- The test creates a descriptor-set layout with one `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` binding and a separate pipeline layout for each selected bind point ([set layouts](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L492-L519)). Depending on the route, it allocates and writes a descriptor set, pushes a descriptor, or pushes through a `VkDescriptorUpdateTemplate` configured for the matching bind point and layout ([descriptor setup](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L627-L669)).
- The four setup operations are recorded in the selected order. Each operation binds pipeline state, graphics shader-object state, or descriptor state for the corresponding command class. In shader-object construction variants, `GraphicsPipelineWrapper::bind()` uses `vkCmdBindShadersEXT` and sets the required dynamic graphics state rather than calling `vkCmdBindPipeline` ([graphics wrapper binding](../../../framework/vulkan/vkPipelineConstructionUtil.cpp#L4721-L4761)). The test tracks the setup operations and asserts that both required operations precede the matching draw, dispatch, or trace-rays command ([setup loop](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L671-L769)).
- The selected execution operations are recorded in one of two orders. Graphics begins and ends a render pass around `vkCmdDraw`; compute uses `vkCmdDispatch`; ray tracing uses `cmdTraceRays` with a one-entry ray-generation shader binding table ([execution loop](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L771-L799)).
- After the selected shader stages write their buffers, the test records shader-write to host-read buffer barriers, ends the command buffer, submits it to the universal queue, and waits ([barriers and submission](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L801-L818)).
- The host invalidates and checks each selected storage buffer. Graphics cases also read the attachment and compare every pixel with `(0.0, 1.0, 0.0, 1.0)` ([result checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L820-L849)). Every selected observation must pass.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_compute` | Graphics and compute pipeline or shader-object and descriptor state is not kept independent across the selected setup and execution orders. |
| `graphics_raytracing` | Graphics and ray-tracing pipeline or shader-object and descriptor state is not kept independent, or the ray-tracing path is handled incorrectly. |
| `compute_raytracing` | Compute and ray-tracing pipeline or descriptor state is not kept independent. This pair is registered only for monolithic construction. |

### Cause Analysis

#### Graphics and compute state association

**Possible failure symptoms:** The graphics buffer does not contain `1`, the compute buffer does not contain `2`, or a graphics attachment pixel differs from the expected green value. A failure limited to one execution order or descriptor-route combination narrows the failing state transition, but does not by itself identify one API call.

**Possible implementation causes:** The implementation may associate pipeline, shader-object, or descriptor state with the wrong command class or `VkPipelineBindPoint`, fail to preserve bind-point-specific state across later binds, or mishandle a descriptor-set, push-descriptor, or update-template command. The source binds each descriptor route with the selected bind point and layout, while Vulkan defines the relationship between shader stages, bind points, and commands in the shader-binding table ([Vulkan bind-point contract](../../../../vulkan-docs/src/chapters/shaders.adoc#L1750-L1800)). Source-level investigation is needed to localize a particular failure.

#### Graphics and ray-tracing state association

**Possible failure symptoms:** The graphics buffer or green attachment check fails, the ray-tracing buffer does not contain `3`, or only one of the two execution orders fails. A failure in the ray-tracing path can also indicate that the required ray-generation dispatch did not use the expected pipeline state.

**Possible implementation causes:** The implementation may mix graphics pipeline or shader-object state with ray-tracing state, use the wrong bind point for a descriptor route, mishandle the ray-tracing pipeline or shader binding table, or lower the ray-generation shader incorrectly. Vulkan requires a ray-tracing pipeline to be bound before ray-tracing commands are recorded ([ray-tracing commands](../../../../vulkan-docs/src/chapters/raytracing.adoc#L222-L239)). The test source and specification identify the contract, but source-level investigation is needed to locate a specific defect.

#### Compute and ray-tracing state association

**Possible failure symptoms:** The compute buffer does not contain `2`, the ray-tracing buffer does not contain `3`, or the failure depends on setup or execution order. There is no graphics attachment in this pair, so the two buffer checks are the observable result.

**Possible implementation causes:** The implementation may confuse compute and ray-tracing pipeline state, apply a descriptor binding to the wrong bind point, mishandle `vkCmdDispatch` or `vkCmdTraceRaysKHR`, or use an incorrect ray-tracing pipeline or shader binding table. The test intentionally registers this pair only for monolithic construction, so a failure in that scope remains a monolithic bind-point or shared resource-path issue until source-level investigation narrows it further.

#### Shared descriptor and result-transport paths

**Possible failure symptoms:** Several bind-point pairs or descriptor-route combinations fail with incorrect sentinel values, or buffer checks fail after the device work completes. Graphics-only color failures leave the storage-buffer path passing, while failures across all selected buffers keep the shared setup, barriers, submission, and host invalidation path in scope.

**Possible implementation causes:** The implementation may mishandle storage-buffer descriptor contents, shader-write to host-read availability or visibility, command submission completion, or host-memory invalidation. The CTS records a stage-specific shader-write to host-read barrier and waits for queue completion before invalidating each allocation ([barrier and readback code](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L393-L402), [submission and checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L801-L826)). The observed pattern can narrow the investigation, but it cannot prove a unique fault location.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` requires `VK_KHR_push_descriptor` when either selected route is `push` or `template_push`.
- It also requires `VK_KHR_descriptor_update_template` when a selected route is `template_push` ([support checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L189-L203)).
- Any pair containing ray tracing requires `VK_KHR_ray_tracing_pipeline` ([ray-tracing requirement](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L205-L206)).
- `checkPipelineConstructionRequirements()` enforces the requirements of the selected construction type ([construction check](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L208-L210)).

These checks remove cases that the current device or construction path cannot support. They do not indicate a passing result.

### Design-based pruning

The factory keeps `compute_raytracing` only for monolithic construction. For every other construction type it skips a pair when neither selected bind point is graphics ([pair pruning](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L972-L987)). This avoids repeating a pair outside the construction coverage chosen by the test design; it is separate from extension-based support checks.

## Key Takeaways

- The primary behavior is independence of pipeline or shader-object state and descriptor state between the two selected command classes.
- The nine ordered descriptor-route combinations, 24 setup orders, and two execution orders vary how state is established and consumed without changing the sentinel contract.
- Separate buffers make graphics, compute, and ray-tracing writes independently observable. Graphics adds a second observation through the green attachment.
- The result pattern can narrow whether a failure affects one bind-point path, graphics output, ray tracing, or shared descriptor and readback infrastructure. It does not identify a unique implementation fault without further investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support checks and generated programs | [`BindPointTest::checkSupport` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L189-L280) | Defines feature gates and shader fixtures. |
| Descriptor helpers and barriers | [`makeSetLayout`, update helpers, and `recordBufferBarrier`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L294-L402) | Defines storage-buffer descriptors, update routes, and readback synchronization. |
| Runtime implementation | [`BindPointInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L404-L851) | Creates resources, records commands, submits work, and checks results. |
| Registration matrix | [`createBindPointTests`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L1083) | Defines bind-point pairs, route combinations, permutations, and pruning. |
| Parent registration guard | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L174-L178) and [bind-point include](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L65-L69) | Places the family in the pipeline category and excludes it from Vulkan SC. |
| Graphics state binding | [`GraphicsPipelineWrapper::bind`](../../../framework/vulkan/vkPipelineConstructionUtil.cpp#L4721-L4761) | Shows that shader-object variants bind graphics shader objects and dynamic state instead of a graphics pipeline. |
| Bind-point and command relationship | [Vulkan shader binding](../../../../vulkan-docs/src/chapters/shaders.adoc#L1747-L1800) | Defines the shader-stage to bind-point mapping used by the test. |
| Push-descriptor template contract | [Vulkan descriptor update template](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4174-L4209) | Defines bind point, layout, and set fields for push templates. |
