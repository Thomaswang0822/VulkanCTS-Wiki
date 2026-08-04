# Understanding Brief: BindVertexBuffers2

## One-Sentence Test Purpose

This test checks whether `vkCmdBindVertexBuffers2` supplies the intended vertex-buffer offsets, sizes, and dynamic strides to later draws when bindings are updated together, one at a time, or under the `VK_KHR_maintenance5` bound-range rules.

## Background Knowledge

### Vertex-buffer binding state

A vertex attribute names a vertex binding, and a draw fetches that attribute from the buffer state currently associated with that binding. [`vkCmdBindVertexBuffers2`](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L765-L849) replaces the buffer, start offset, optional bound size, and optional stride for consecutive binding numbers. The command affects subsequent draws that use those bindings.

`pSizes[i]` describes the bound range beginning at `pOffsets[i]`. With `VK_KHR_maintenance5`, `VK_WHOLE_SIZE` means the rest of the buffer after that offset. When the pipeline enables `VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE`, the command also replaces the binding stride.

Why it matters here:

- The regular matrix changes offsets and strides while the pipeline's static binding descriptions carry an ignored stride value.
- The maintenance5 matrix changes the range as well as offsets and strides, so it can distinguish the whole remaining buffer from a shorter explicit range.

### Robust vertex fetch from a bound range

The `robustness2` leaves create a device with `robustBufferAccess` and `robustBufferAccess2`. Their data deliberately places some coordinate reads beyond either the buffer allocation or the explicit bound size. The test expects the defined robust result, rather than ordinary geometry from those bytes.

## One Concrete Example

A `single.stride_5_8_offset_15_22.count_2` leaf creates four bindings: two color bindings with the selected color stride and offset, and two position bindings with the selected vertex stride and offset. It records one `vkCmdBindVertexBuffers2` call for all four bindings, then draws four instances into four image quadrants. The generated vertex shader reconstructs a `vec4` color and position from four `vec2` inputs. An incorrect offset or stride changes the fetched color or position, so the host comparison finds a wrong quadrant.

## End-to-End Test Flow

```text
[host] select a construction type and a registered regular, mismatch, or maintenance5 path
[host] check extended dynamic state and construction support; maintenance5 and robustness2 leaves check their extra requirements
[host] create the color image, framebuffer, pipeline, vertex buffers, command buffer, and host-visible readback buffer
[host] fill vertex buffers with known values, then record vkCmdBindVertexBuffers2 and a draw
[device] use the supplied binding offsets, sizes, and strides for vertex fetch
[device] render color from the fetched attributes into the color image
[host] copy the image, submit and wait, invalidate readback memory, then evaluate pixels
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Regular and mismatch cases generate GLSL whose input layout changes with `count_1` through `count_4`. The vertex shader rebuilds a position and color from those inputs; the fragment shader writes the interpolated color ([source](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1551-L1616)).
- `maintenance5` generates one `vec3` color input plus one `vec2` position input for each additional buffer. It sums the position inputs and forwards the color ([source](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1672-L1701)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffers | yes | yes, through `vkCmdBindVertexBuffers2` | read by vertex fetch | no | Their padding, offsets, sizes, and strides form the tested state. |
| Color image | yes | color attachment | written by rendering | copied to a buffer | Makes vertex-fetch errors observable. |
| Host-visible readback buffer | yes | transfer destination | written by image copy | yes | Supplies the image used by each oracle. |
| Graphics pipeline | yes | bound before the command | uses generated shaders | no | Maps shader locations to the tested bindings and enables dynamic stride. |

## What Is Checked

- Regular leaves compare every pixel of the 32 by 32 result with the expected color for its quadrant ([comparison](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L559-L600)).
- `dynamic_stride.binding_stride_index_mismatch` uses bindings 0 and 2, so the two stride-array elements must associate with the two command-array elements rather than with contiguous binding numbers ([setup](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L678-L689)).
- Maintenance5 leaves count clear-color pixels in the upper-left quarter and sample its inner corner. Non-robust leaves require a non-clear sample and no clear-color mismatch. Robustness2 leaves require a below-threshold sample and a clear-color mismatch below 25 percent ([oracle](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1413-L1461)).

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node below the `bind_buffers_2` test family
>
> **Candidate values:** `single`, `separate`, `dynamic_stride`, `maintenance5`

The direct intermediate nodes select different command shapes or range semantics. Stride, offset, count, topology, seed, and size choices refine those behaviors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single` | Incorrect multi-binding replacement, offset/size/stride application, or vertex fetch. |
| `separate` | Incorrect persistence or replacement of state supplied by successive one-binding calls. |
| `dynamic_stride` | Incorrect association of stride-array elements with non-contiguous binding numbers. |
| `maintenance5` | Incorrect bound-size, `VK_WHOLE_SIZE`, maintenance5, or robust bound-range vertex-fetch behavior. |

## Important Variations and Special Cases

- `single` calls `vkCmdBindVertexBuffers2` once for all `2 * count` regular bindings. `separate` performs one call per binding ([recording](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L517-L543)).
- The regular matrix uses seven exact stride/offset tuples and `count_1` through `count_4` under each binding mode ([registration](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1783-L1904)).
- `dynamic_stride.binding_stride_index_mismatch` is registered only for monolithic construction.
- `maintenance5` is not built for Vulkan SC. Its ordinary leaves use `triangle_list` or `triangle_strip`, 5 or 9 buffers, seeds 321 or 432, and `whole_size` or `true_size`. Its `robustness2` leaves use seeds 543 or 654 and add `beyond_buffer` or, for `true_size`, `beyond_size` ([registration](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1906-L2016)).

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Category registration | [pipeline registration](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L188-L191) | Adds `bind_buffers_2` to the pipeline test category. |
| Regular registration | [`createCmdBindBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1780-L1904) | Defines the direct intermediate nodes and the regular matrix. |
| Maintenance5 registration | [`createCmdBindVertexBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1906-L2016) | Defines the topology, count, seed, size, and robustness paths. |
| Regular execution | [`BindBuffers2Instance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L266-L600) | Records the bind calls, draw, readback, and exact pixel comparison. |
| Maintenance5 execution | [`BindVertexBuffers2Instance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1331-L1510) | Builds the range cases and their two image predicates. |
| API contract | [vertex-input command semantics](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L765-L849) | Defines updated offsets, sizes, `VK_WHOLE_SIZE`, and dynamic strides. |

## Questions / Risk Points for User Audit

- Does the direct-intermediate-node axis make the differences between the regular, mismatch, and maintenance5 paths clear?
- Does the account distinguish a short bound size from the physical allocation size?
- Does the robustness2 oracle make clear that it is a threshold-and-coverage check, not a full pixel-for-pixel image comparison?

## Conversion Notes for Final Wiki Rewrite

- Root the final hierarchy at `pipeline.monolithic.bind_buffers_2` and document other construction roots outside the fenced tree.
- Copy the failure table unchanged into `## Failure Meaning`.
- Keep shader analysis focused on the generated input reconstruction. The test observes fixed-function vertex-fetch state, so it does not need a reconstructed SPIR-V artifact.
- Preserve the Vulkan SC exclusion and distinguish ordinary maintenance5 range cases from robustness2 leaves.
