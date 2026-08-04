# Understanding Brief: pipeline descriptor limits

## One-sentence test purpose

This implementation checks whether a pipeline can create, bind, and execute a descriptor-set layout with a selected count of one descriptor type, up to the device's supported per-stage limits.

## Background knowledge

### Per-stage descriptor limits

Vulkan reports separate limits for samplers, uniform buffers, storage buffers, sampled images, storage images, and input attachments. Each limit restricts the resources accessible to one shader stage in a pipeline layout. `maxPerStageResources` also caps the combined resources accessible to that stage. A descriptor-set layout binding count is separately bounded by Vulkan SC's `maxDescriptorSetLayoutBindings`.

Why it matters here:

- Each leaf chooses one descriptor type and one count from 36 values between `3` and `65535`.
- The source skips a leaf when its requested count exceeds the relevant type-specific limit or, on Vulkan SC, `maxDescriptorSetLayoutBindings`. The combined-resource gate is normally `maxPerStageResources`; compute storage-buffer leaves use the effective set-0 count and therefore compare the registered count against `maxPerStageResources - 1`, one resource more conservatively than their actual total of set-0 inputs plus the set-1 output SSBO.

### Observable last binding

The test creates contiguous bindings for the selected descriptor type. It writes the first `getDescCount() - 1` bindings with red data and the last binding with green data. For compute storage-buffer leaves, `getDescCount()` is the registered count minus one because the set-1 output SSBO supplies the remaining storage-buffer resource. The generated shader reads only that final set-0 binding. A green result therefore requires the implementation to preserve the high binding number through layout creation, descriptor update, binding, and shader access.

Why it matters here:

- A shader can access one chosen binding while the pipeline layout still accounts for every prior binding.
- The test does not prove that every descriptor contains independent data. It proves that the selected descriptor count can be represented and that the final descriptor is reachable.

## One concrete example

Consider `dEQP-VK.pipeline.monolithic.descriptor_limits.compute_shader.storage_buffers_64`. The CTS creates 63 storage-buffer bindings in set 0 because the compute output buffer occupies an additional storage-buffer binding in set 1. Bindings 0 through 61 refer to a red `vec4`; binding 62 refers to a green `vec4`. The generated compute shader reads set 0, binding 62 and writes that value to set 1, binding 0. After dispatch and a compute-to-host memory barrier, the host invalidates the output allocation and requires `(0.0, 1.0, 0.0, 1.0)`.

## End-to-end test flow

```text
[host] select construction type, shader stage, descriptor type, and requested count
[host] reject unsupported counts using device limits and construction requirements
[host] create a pool, a contiguous descriptor-set layout, descriptor sets, and red/green resources
[host] write red resources to earlier bindings and a green resource to the final binding
[device] bind the pipeline and descriptor set, then dispatch or draw
[device] read the final binding and write or render the observed green value
[host] submit and wait, invalidate or copy back output, and compare it with green
```

## Generated test artifacts and bound resources

| Resource or artifact | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---:|---:|---:|---|
| Contiguous set-0 descriptor layout | yes | pipeline layout and shader interface use it | no | Contains the selected number of same-type bindings. |
| Red and green image or buffer resources | yes | descriptors reference them | no | Make the final binding distinguishable from earlier bindings. |
| Set-1 compute result SSBO | yes | compute shader writes it | yes | Carries the observed value to host comparison. |
| Graphics color image and transfer buffer | yes | fragment shader writes it | yes | Carries the fragment result to image comparison. |
| Generated `test` shader | yes | pipeline executes it | no | Reads the final set-0 binding. |

## What is checked

- Fragment leaves copy the color attachment to a host-visible buffer and compare every pixel with solid green using `tcu::floatThresholdCompare()` and a zero threshold.
- Compute leaves place the shader result in a host-visible storage buffer, insert a compute-write to host-read barrier, invalidate the allocation, and compare the value with green exactly.
- The construction root determines whether compute is registered. `compute_shader` exists only below `monolithic`; fragment leaves exist below all inspected construction roots, except shader-object roots omit input attachments.

## Behavior parameter identification

> **Behavior parameter:** shader-stage intermediate node
>
> **Candidate values:** `compute_shader` and `fragment_shader`.

Within each intermediate node, descriptor type and requested count select the exact descriptor limit and layout size. The two intermediate nodes use different execution and observation paths.

## What failure means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute_shader` | Incorrect compute-stage descriptor-limit accounting, creation or update of a high-numbered binding, descriptor-set or pipeline-layout binding, compute access to the final descriptor, synchronization, or output-buffer readback. |
| `fragment_shader` | Incorrect fragment-stage descriptor-limit accounting, creation or update of a high-numbered binding, graphics descriptor binding, fragment access to the final descriptor, render-pass output, image copy, or image comparison. |

## Important variations and special cases

- `compute_shader` registers five descriptor types: `samplers`, `uniform_buffers`, `storage_buffers`, `sampled_images`, and `storage_images`. It is monolithic-only.
- `fragment_shader` adds `input_attachments`; shader-object construction types omit those leaves.
- For compute storage-buffer leaves, registration retains the requested count but `getDescCount()` subtracts one for set 0 because the set-1 output SSBO consumes the remaining storage-buffer resource. The pool still reserves the requested original count, and the `maxPerStageResources` support gate uses the reduced set-0 count rather than the actual total, making that gate one resource conservative for this path.
- The inspected mustpass scope contains 1,548 leaves: 396 under `monolithic`; 216 each under `pipeline_library` and `fast_linked_library`; and 180 under each of the four shader-object roots.

## Source mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Runtime setup, execution, and checks | [DescriptorLimitTestInstance::iterate()](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L213-L755) | Builds layouts and resources, updates descriptors, executes, and checks output. |
| Generated shaders and support gates | [DescriptorLimitTest::initPrograms() and checkSupport()](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L778-L954) | Emits the final-binding access and enforces device limits. |
| Registration | [createDescriptorLimitsTests()](../../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L963-L1063) | Defines construction-specific intermediate nodes and leaves. |
| Descriptor limits | [per-stage limits](../../../../vulkan-docs/src/chapters/limits.adoc#L151-L272) | Defines the relevant per-stage limits and combined resource count. |
| Pipeline resource rule | [compute pipeline limit](../../../../vulkan-docs/src/chapters/pipelines.adoc#L987-L990) | Requires compute-stage accessible resources not to exceed `maxPerStageResources`. |
| Descriptor-layout binding-count rule | [VkDescriptorSetLayoutCreateInfo](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L201-L204) | Applies the `maxDescriptorSetLayoutBindings` bound. |

## Conversion notes for final wiki rewrite

- Keep the Failure Cause Mapping table unchanged in the final page.
- Use a compute storage-buffer leaf to show the output-SSBO adjustment and a fragment leaf to explain image validation.
- Keep the generated shader discussion narrow: the shader observes the final binding; layout and descriptor accounting are the behavior under test.
