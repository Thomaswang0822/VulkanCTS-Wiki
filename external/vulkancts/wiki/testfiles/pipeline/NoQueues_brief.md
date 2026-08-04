# Understanding Brief: Pipeline creation and binary reuse without queues

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation can create pipelines and capture reusable pipeline, pipeline-binary, and shader-binary data on a logical device created with zero queues, then use the captured data on a device with one queue.

## Background Knowledge

### A logical device can be created without queues

The test supplies `queueCreateInfoCount = 0` on its first device-creation pass. That device can create objects needed for pipeline construction, but it cannot submit command buffers. The test therefore uses the zero-queue device to create and capture state, and a second one-queue device to execute the pipeline and validate output.

### Three reuse mechanisms have different contracts

- A `VkPipelineCache` stores implementation-managed data that a later pipeline creation call may use. Passing `VK_NULL_HANDLE` disables the explicit pipeline-cache input for that call. The [pipeline-cache description](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-cache) defines this as a creation input, not as a guarantee that a later call will produce a particular cache size.
- `VK_KHR_pipeline_binary` exposes opaque pipeline binary keys and data. The test retrieves those values from a pipeline created on the zero-queue device and supplies them to a later pipeline creation call.
- `VK_EXT_shader_object` exposes opaque shader binary data. The shader-binary family creates shader objects from SPIR-V on the first pass, retrieves their binary data, and creates shader objects from that data on the second pass.

## One Concrete Example

Consider `dEQP-VK.pipeline.no_queues.pipeline_binary.compute`.

The host creates a device with no queues, creates the compute pipeline and its supporting objects, and extracts pipeline binary keys and data from the resulting pipeline. It then creates a second device with one universal queue, recreates the supporting state, supplies the saved binary data through `VkPipelineBinaryInfoKHR`, and creates the compute pipeline again. The second pass dispatches the compute work and checks the output buffer. The example captures the central split: queue absence affects device creation and submission, while pipeline creation and binary extraction remain observable on the first device.

## End-to-End Test Flow

```text
[host] check Vulkan 1.1 and the selected ray-tracing, mesh, pipeline-binary, or shader-object requirements
[host] select one test type and one shader-stage value
[host] generate stage-appropriate GLSL programs and compile them to SPIR-V
[host] create a logical device with zero queues
[host] create cache or binary-support objects, descriptors, layouts, shaders, and the selected pipeline
[host] extract pipeline-cache data, pipeline-binary keys/data, or shader-binary data
[host] destroy the zero-queue device and create a second logical device with one universal queue
[host] recreate supporting objects and use the saved data to create a pipeline or shader objects
[host] submit the selected compute, graphics, or ray-tracing commands on the one-queue device
[host] invalidate the output allocation and compare each output element with 1.0
[host] return PASS only when every tested invocation produced the expected value
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` generates GLSL for the selected stage. Compute, graphics, mesh, and ray-tracing paths use stage-specific entry points and pipeline state. The test uses specialization constants for workgroup dimensions and width. The generated programs sample a one-by-one texture whose opaque-white border color drives the output-store condition. The shader source establishes valid pipeline work; the test's main subject is reuse across the two device configurations.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| `VkPipelineCache` | yes for `pipeline_cache` | passed to pipeline creation | implementation-managed cache state | cache size is queried on the first pass | carries cache data to the second pass |
| `VkPipeline` | yes for `pipeline_cache` and `pipeline_binary` | used by the selected command path | drives compute, graphics, or ray-tracing work | no direct handle comparison | is the reusable object produced from source or binary data |
| `VkShaderEXT` | yes for `shader_binary` | bound with shader-object commands | executes the selected stage | no direct handle comparison | supplies the shader-binary round trip |
| sampled image and sampler | yes | descriptor binding 0 | shader reads the border texel | no | makes the shader write a deterministic value |
| storage buffers | yes | descriptor bindings 1 through 4 | shader writes output and related data | output buffer is read by host | provides the observable result and supporting addresses |
| command buffer and universal queue | only on the second pass | submitted to the queue | executes the selected work | host waits for completion | separates creation on a zero-queue device from execution on a one-queue device |

## What Is Checked

- `checkSupport()` requires Vulkan 1.1 and `VK_KHR_maintenance9` for every leaf. Ray-tracing stages require `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, and the corresponding features. Task and mesh stages require `VK_EXT_mesh_shader` features.
- `pipeline_binary` requires `VK_KHR_pipeline_binary`.
- `shader_binary` requires `VK_EXT_shader_object` and excludes the six ray-tracing stage values.
- The first pass must create the selected pipeline or shader objects successfully and must retrieve the selected cache or binary data successfully.
- The second pass must consume the saved data, submit the selected work, and produce `1.0f` in every checked output element.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family
>
> **Candidate values:** `pipeline_cache`, `pipeline_binary`, `shader_binary`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `pipeline_cache` | Zero-queue pipeline creation, pipeline-cache data export/import, or execution of the recreated pipeline |
| `pipeline_binary` | Pipeline-binary extraction, key/data pairing, binary-backed pipeline creation, or execution of the recreated pipeline |
| `shader_binary` | Shader-binary extraction, binary-backed shader-object creation, shader binding, or execution of the recreated shader |

## Important Variations and Special Cases

- `stageCases[]` contains 14 values: `compute`, `raygen`, `isect`, `ahit`, `chit`, `miss`, `callable`, `vertex`, `fragment`, `geometry`, `tessctrl`, `tesseval`, `task`, and `mesh`.
- `shader_binary` intentionally prunes the six KHR ray-tracing stages because the source does not create shader binaries for them.
- Compute, ordinary graphics, mesh, and ray-tracing cases select different pipeline bind points and command sequences, but all use the same two-pass capture and reuse model.
- Geometry, tessellation, task, and mesh stages use `threadsPerWorkgroupX = 32` and `threadsPerWorkgroupY = 1`; other stages use 8 by 8. Both configurations use two workgroups in each dimension.
- The source excludes Vulkan SC with `#ifndef CTS_USES_VULKANSC` around the registration entry point. The documented registration is therefore VK-only.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Support checks | [`NoQueuesTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L220-L279) | Defines API, extension, feature, and stage prerequisites. |
| Program generation | [`NoQueuesTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L281-L591) | Shows how the selected stage's valid shader artifacts are generated. |
| Two-device loop | [`NoQueuesTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L614-L670) | Creates the zero-queue and one-queue devices. |
| Cache and binary capture | [`iterate()` capture branch](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1265-L1319) | Extracts cache, pipeline-binary, or shader-binary data after the first pass. |
| Execution and output check | [`iterate()` submission and validation](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1658-L1710) | Submits the second-pass work and checks output values. |
| Registration | [`createNoQueuesTests()`](../../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1723-L1785) | Defines the three test families, 14 stages, and shader-binary pruning. |
| Mustpass leaves | [`no-queues.txt`](../../../mustpass/main/vk-default/pipeline/no-queues.txt#L1-L37) | Records the 37 executable VK leaves. |

## Questions / Risk Points for User Audit

- Does the page keep the zero-queue capture pass distinct from the one-queue execution pass?
- Are opaque cache and binary data described as reusable inputs without claiming byte-level or cache-hit equivalence?
- Is the `shader_binary` exclusion of ray-tracing stages clear?
- Does the final page distinguish pipeline creation success from the later output-buffer validation?

## Conversion Notes for Final Wiki Rewrite

- Keep the registered test family as the primary behavioral axis, with one subsection for each of the three direct intermediate nodes.
- Preserve the exact failure-mapping table in the final page.
- Explain shader generation only to establish valid stage-specific pipeline inputs. A shader walkthrough and SPIR-V disassembly are not useful for this host-side binary-reuse property.
- Keep the two-device timeline and the 37-leaf mustpass count visible in the final page.
