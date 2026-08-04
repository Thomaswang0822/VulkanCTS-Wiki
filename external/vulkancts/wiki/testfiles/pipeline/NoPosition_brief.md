# Understanding Brief: NoPosition

## One-Sentence Test Purpose

This test checks whether graphics pipelines execute correctly when selected pre-rasterization shader stages do not assign the `Position` built-in, while the test observes both the rendered attachment and, when requested, stage execution through an SSBO.

## Background Knowledge

### `Position` in the pre-rasterization interface

The Vulkan `Position` built-in carries the position produced by the last pre-rasterization shader stage. That value feeds primitive assembly, clipping, and rasterization. Vertex, tessellation-control, tessellation-evaluation, and geometry shaders can declare the built-in, and later stages receive the preceding stage's output through the corresponding `gl_PerVertex` interface. See the [`Position` built-in definition](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4147-L4165).

Why it matters here:

- The generator can install vertex, tessellation, and geometry stages, then choose which of those stages assign `gl_Position`.
- A color image that remains blue does not by itself prove that a primitive was rasterized, because the render pass clears the attachment to blue and the fragment shader also writes blue.

### Interface declaration versus assignment

GLSL can use the implicit `gl_PerVertex` declaration or declare the block explicitly. Both forms describe the shader interface. An assignment such as `gl_Position = in_pos` is a separate operation, and the test varies that operation with the stage write mask.

Why it matters here:

- `implicit_declarations` and `explicit_declarations` select the declaration form.
- A leaf name such as `v1_c0_e1_g0` records the selected stages and which selected stages assign `gl_Position`: vertex writes, tessellation-control does not, tessellation-evaluation writes, and geometry does not.

## One Concrete Example

The `pipeline.monolithic.no_position.explicit_declarations.basic.single_view.v0` case creates a vertex shader with an explicit output `gl_PerVertex` block but leaves its `main` function without a `gl_Position` assignment. The host still provides three vertex positions and installs a fragment shader that writes blue. The render pass also clears its `VK_FORMAT_R8G8B8A8_UNORM` attachment to blue. The case therefore checks that the pipeline accepts and executes the no-position shader path without using a blue result as evidence that rasterization produced the pixels.

For an SSBO case such as `pipeline.monolithic.no_position.explicit_declarations.ssbo_writes.multiview.v1_c0_e0_g0`, the selected stages also execute `atomicAdd` against per-stage counters. Those counters provide the separate evidence that the selected shader stages ran.

## End-to-End Test Flow

```text
[host] choose declaration form, basic or SSBO observation, view mode, selected stages, and a gl_Position write mask
[host] generate GLSL for the selected vertex, optional tessellation and geometry, and fragment stages
[host] create the 64x64 color image, render pass, framebuffer, graphics pipeline, vertex buffer, and optional SSBO
[host] clear the attachment to blue, bind the pipeline and optional descriptor set, and issue one triangle draw for each subpass
[device] execute the installed pre-rasterization stages and fragment shader; SSBO variants atomically count selected-stage invocations
[host] transition and copy the color image to a host-visible verification buffer, submit, and wait
[host] require blue pixels in every view and, for SSBO variants, require the minimum counter values for selected stages
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`NoPositionCase::initPrograms()` generates GLSL for the selected stages and an always-present fragment shader. The vertex shader reads `in_pos`. Tessellation-control sets all tessellation levels, tessellation-evaluation interpolates input positions when its write bit is set, and geometry emits three vertices while optionally copying each input position. `explicit_declarations` adds explicit `gl_PerVertex` blocks. The fragment shader writes the blue background color.

For `ssbo_writes`, each generated stage includes a `std430` storage-buffer declaration at set `0`, binding `0`. The source reserves one counter range for each of the four possible pre-rasterization stages. A selected stage calls `atomicAdd`; multiview and device-group cases index the counter with `gl_ViewIndex`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | color attachment | cleared and fragment-written | yes, through an image copy | The blue result checks command completion and readback, but cannot distinguish the clear from fragment output. |
| Vertex buffer | yes | vertex-input binding 0 | read by the vertex shader | no | Supplies the three triangle positions. |
| Optional SSBO | yes | descriptor set binding 0 | atomically incremented by selected pre-rasterization stages | yes | Provides direct evidence of selected-stage execution. |
| Graphics pipeline and shader modules | yes | bound before each draw | execute the selected stages | no | Carry declaration, stage-selection, and write-mask choices. |
| Host-visible verification buffer | yes | transfer destination | written by the image copy | yes | Lets CTS inspect every view's color image. |

## What Is Checked

- The host scans every pixel in every view copied from the color image and requires the pixel to equal the blue background color.
- An `ssbo_writes` case reads its counter buffer after the submission. Selected vertex, tessellation-control, and tessellation-evaluation stages must reach at least `3` invocations per view. A selected geometry stage must reach at least `1` invocation per view.
- The implementation accepts a counter equal to the minimum or to a nonzero multiple of that minimum. A stage omitted from `selectedStages` has an expected counter of zero.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node `basic` or `ssbo_writes`
>
> **Candidate values:** `basic`, `ssbo_writes`

These values choose the primary observation mechanism. Declaration form, view mode, selected-stage mask, and write mask vary the same behavior without changing that distinction.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | The generated stage/interface combination, pipeline execution, color attachment handling, or image readback does not preserve the expected blue image. |
| `ssbo_writes` | A `basic`-path cause, or selected pre-rasterization stages do not execute or expose their atomic SSBO writes as required. |

## Important Variations and Special Cases

- `implicit_declarations` uses GLSL's implicit built-in interface. `explicit_declarations` emits explicit `gl_PerVertex` input and output blocks.
- `single_view` uses one image layer. `multiview` uses a multiview render pass and array image layers. `device_index_as_view_index` creates a device group, derives the view count from its physical-device count, and uses `VK_PIPELINE_CREATE_VIEW_INDEX_FROM_DEVICE_INDEX_BIT`.
- `basic` registers one and two views. `ssbo_writes` also registers `device_index_as_view_index`, so it can verify counters selected with `gl_ViewIndex`.
- Shader-object construction skips view modes other than `single_view`. Tessellation, geometry, multiview, vertex-pipeline atomics, device-group, and pipeline-construction requirements can also make a case unsupported.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Pipeline-category registration | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L171-L175) | Adds `no_position` below each pipeline construction variant. |
| Test registration | [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1094-L1190) | Builds declaration, observation, view, stage-mask, and write-mask paths. |
| Program generation | [`NoPositionCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L213-L394) | Emits selected shader stages, declarations, writes, and SSBO instrumentation. |
| Support checks | [`NoPositionCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L401-L445) | Gates stage features, multiview, SSBO atomics, device groups, and construction types. |
| Runtime and result checks | [`NoPositionInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L684-L1089) | Creates resources, records the draw, copies the image, and validates pixels and counters. |
| `Position` contract | [`interfaces.adoc`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4147-L4184) | Defines the built-in and its role after the last pre-rasterization stage. |

## Questions / Risk Points for User Audit

- Is the distinction between blue-image completion evidence and SSBO execution evidence clear?
- Does `basic` versus `ssbo_writes` identify the primary behavioral axis while leaving declaration and stage/write-mask choices as dimensions?
- Does the example avoid implying that a blue image proves rasterization occurred?

## Conversion Notes for Final Wiki Rewrite

Use `basic` and `ssbo_writes` as the final page's `Behavior Parameters` subsections. Copy the failure-cause table into the final page unchanged. Keep shader analysis centered on generated interface declarations, optional `gl_Position` assignments, and SSBO counters. Include the mustpass counts by pipeline construction variant and state that shader-object registrations contain only `single_view` cases.
