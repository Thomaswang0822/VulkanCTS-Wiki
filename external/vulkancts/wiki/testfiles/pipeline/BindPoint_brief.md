# Understanding Brief: Pipeline Bind Points

## One-Sentence Test Purpose

This test checks whether graphics pipeline or shader-object state, compute and ray-tracing pipeline state, and descriptor state remain associated with the correct command class when two work types are recorded in each relevant order.

## Background Knowledge

### Pipeline bind points and commands

A pipeline bind point selects pipeline state used by a class of commands. `vkCmdBindPipeline` binds graphics, compute, or ray-tracing pipelines to their corresponding bind points ([Vulkan shader binding](../../../../vulkan-docs/src/chapters/shaders.adoc#L1747-L1800)). In shader-object construction variants, the graphics path instead binds graphics shader objects and required dynamic state; compute and ray tracing still use pipelines. Descriptor binding commands take a bind point and pipeline layout, so bindings at the same set number must remain associated with the command class that established them.

Why it matters here:

- Each test case records setup for two bind points in one command buffer.
- The test changes the order of pipeline bindings, descriptor bindings, and execution commands to make state leakage observable.

### Descriptor update routes

The test supplies one storage-buffer descriptor through an allocated descriptor set, a pushed descriptor, or a push-descriptor update template. A push-descriptor template is defined for a specific pipeline bind point, pipeline layout, and set number ([descriptor update template fields](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4174-L4209)).

Why it matters here:

- The update route changes how the test supplies a descriptor, not the required association between descriptor state and bind point.
- Each selected shader writes a different value through its own descriptor, which makes an incorrect association visible in host readback.

## One Concrete Example

A `graphics_compute` test case creates graphics pipeline state or graphics shader objects, creates a compute pipeline, gives each command class a separate storage buffer, and records the four setup operations in a selected permutation. It then records a draw and a dispatch in either order. The fragment shader writes `1` to the graphics buffer and produces green in a 1×1 attachment; the compute shader writes `2` to the compute buffer. The host requires both buffer values and the graphics attachment value to match.

## End-to-End Test Flow

```text
[host] select a bind-point pair, two descriptor update types, a setup permutation, and an execution permutation
[host] check extension and pipeline-construction requirements; create only the resources for the selected pair
[host] build the selected graphics, compute, and/or ray-generation programs, layouts, pipelines, and ray-tracing shader binding table
[host] initialize one host-visible storage buffer per selected bind point and record pipeline and descriptor setup in the selected order
[host] record the selected draw, dispatch, and/or trace-rays commands in the selected order
[device] each selected pipeline writes its distinct sentinel value through its storage-buffer descriptor
[host] record shader-write-to-host-read barriers, submit, invalidate the host-visible allocations, and inspect each result
[host] pass only if every selected buffer has its expected sentinel and any graphics attachment is green
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`BindPointTest::initPrograms()` generates the graphics, compute, and ray-generation shader sources only for bind points selected by the test pair ([program generation](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L212-L280)). The shaders are simple fixtures: graphics writes `1`, compute writes `2`, and ray tracing writes `3` to separate storage buffers. The ray-generation source uses `GL_EXT_ray_tracing` and CTS selects SPIR-V 1.4 for it.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| One host-visible storage buffer per selected bind point | Yes | Yes, through set 0 binding 0 | The selected shader writes it | Yes | Separates graphics `1`, compute `2`, and ray-tracing `3` observations. |
| Descriptor-set layout and pipeline layout per selected bind point | Yes | Yes | Used by pipeline and descriptor commands | No | Supplies the stage visibility and bind-point-specific layout. |
| Descriptor set, pushed descriptor, or push-descriptor template | Yes | Yes | Supplies one selected storage buffer | No | Exercises the selected descriptor update route. |
| 1×1 graphics color attachment and framebuffer | Yes, for graphics pairs | Yes | The fragment shader writes green | Yes | Adds a graphics-output check. |
| Ray-tracing pipeline and ray-generation shader binding table | Yes, for ray-tracing pairs | Yes | Used by `cmdTraceRays` | No | Enables the ray-tracing bind-point path. |

## What Is Checked

- `verifyBufferContents()` invalidates each selected host-visible allocation and compares its first `uint32_t` with the graphics, compute, or ray-tracing sentinel ([buffer verifier](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L375-L391), [verification calls](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L820-L826)).
- Graphics cases read the 1×1 attachment and require `(0.0, 1.0, 0.0, 1.0)` ([attachment verification](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L828-L849)).
- The recording logic asserts that the selected pipeline and descriptor state have both been bound before its draw, dispatch, or trace-rays command ([execution switch](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L771-L799)).

## Behavior Parameter Identification

> **Behavior parameter:** bind-point pair
>
> **Candidate values:** `graphics_compute`, `graphics_raytracing`, `compute_raytracing`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics_compute` | Graphics and compute pipeline or shader-object and descriptor state is not kept independent across the selected setup and execution orders. |
| `graphics_raytracing` | Graphics and ray-tracing pipeline or shader-object and descriptor state is not kept independent, or the ray-tracing path is handled incorrectly. |
| `compute_raytracing` | Compute and ray-tracing pipeline or descriptor state is not kept independent. This pair is registered only for monolithic construction. |

## Important Variations and Special Cases

- The factory combines every ordered pair of `write`, `push`, and `template_push` update types with all 24 setup permutations and both execution permutations. Each enabled bind-point pair therefore has 432 test case leaves ([registration loops](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1032-L1079)).
- Non-monolithic construction types retain only pairs that include graphics, so the factory skips `compute_raytracing` ([construction condition](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L972-L987)).
- The monolithic mustpass list contains 1,296 `bind_point` leaves: 432 for each pair. Each of the six inspected non-monolithic lists contains 864 leaves, covering the two graphics-containing pairs.
- `checkSupport()` requires `VK_KHR_push_descriptor` for either push route, `VK_KHR_descriptor_update_template` when a template route occurs, and `VK_KHR_ray_tracing_pipeline` for ray-tracing pairs ([support checks](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L189-L210)). The parent pipeline registration excludes this test family from Vulkan SC ([registration guard](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L65-L69)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Requirements and shader fixtures | [`BindPointTest::checkSupport` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L189-L280) | Defines feature gates and the observable shader writes. |
| Descriptor routes and buffer verification | [descriptor helpers and `verifyBufferContents`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L294-L402) | Shows the storage layout, update methods, barrier, and sentinel comparison. |
| Runtime recording and result checks | [`BindPointInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L404-L851) | Creates resources, records selected permutations, submits work, and validates outputs. |
| Registration matrix | [`createBindPointTests`](../../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L954-L1083) | Defines pairs, dimensions, permutations, and construction-type pruning. |
| Pipeline bind-point contract | [Shader stages and pipeline bind points](../../../../vulkan-docs/src/chapters/shaders.adoc#L1747-L1800) | Links stages, bind points, and command classes. |

## Questions / Risk Points for User Audit

- Does the distinction between descriptor update route and bind-point-specific command-buffer state remain clear?
- Does the concrete graphics/compute example make the two permutation layers understandable?
- Does the scope of the mustpass counts remain clear: one monolithic list and six non-monolithic lists inspected in this repository?

## Conversion Notes for Final Wiki Rewrite

- Use the bind-point pair as the primary behavioral axis.
- Carry the failure-cause mapping table into `BindPoint.md` unchanged.
- Treat shader code as a small observable fixture, rather than the behavior under test.
- Explain the 432-leaf-per-pair matrix as 9 update-route pairs × 24 setup orders × 2 execution orders, and keep monolithic-only pruning separate from feature requirements.
