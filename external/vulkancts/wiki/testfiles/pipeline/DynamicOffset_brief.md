# Understanding Brief: pipeline dynamic descriptor offsets

## One-Sentence Test Purpose

This implementation checks that dynamic uniform and storage buffer descriptors select the intended aligned buffer regions when descriptor sets are bound for graphics, compute, and mixed graphics-plus-compute work.

## Background Knowledge

### Dynamic buffer descriptors

A `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC` or `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC` descriptor supplies a base `VkDescriptorBufferInfo::offset` and a fixed range. At descriptor-set bind time, Vulkan adds the corresponding dynamic offset to that base address; the descriptor range remains fixed. The offset array has one entry per dynamic descriptor, ordered by set, binding number, and array element.

Why it matters here:

- The ordinary cases change how dynamic bindings occupy sets, bindings, or arrays while keeping the address-selection rule constant.
- The mixed cases use five dynamic descriptors with reordered layout bindings, so an incorrect offset-array order can select valid but wrong data.

### Alignment and bind points

Dynamic uniform offsets must satisfy `minUniformBufferOffsetAlignment`; dynamic storage offsets must satisfy `minStorageBufferOffsetAlignment`. Descriptor-set bindings are independent at graphics and compute bind points, even when they use compatible layouts.

Why it matters here:

- The ordinary tests round color-block stride up to the relevant device limit before producing offsets.
- The mixed tests bind the same descriptor set before either a draw or a dispatch, then read graphics and compute results separately.

## One Concrete Example

Consider the monolithic leaf family `dEQP-VK.pipeline.monolithic.dynamic_offset.combined_descriptors.single_offset.same_order_16_graphics_first`.

The CTS creates one descriptor set with five dynamic bindings: vertex UBO, shared UBO, writable SSBO, fragment UBO, and readable SSBO. It binds a five-element offset array, draws a 32 by 32 image, then dispatches compute. In the `single_offset` variant, the supplied offsets choose one specific vertex position, shared and fragment colors, SSBO read value, and SSBO write slot. The expected image contains one colored square at the selected vertex position, and the expected output buffer contains a nonzero value only at the selected writable SSBO slot.

## End-to-End Test Flow

```text
[host] choose a construction type and either ordinary graphics/compute parameters or a combined-descriptor leaf
[host] create aligned buffer blocks, descriptor-set layouts, descriptor sets, pipelines, and graphics or compute output resources
[host] write descriptor base offsets and record vkCmdBindDescriptorSets or vkCmdBindDescriptorSets2KHR with dynamic offsets
[device] execute a draw, a dispatch, or both; shaders access the buffer regions selected by those offsets
[host] submit and wait; copy graphics output when needed; invalidate host-visible allocations
[host] compare the image, output buffer, or both against source-generated reference values
```

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Host setup | Device use | Why it matters |
|---|---|---|---|
| Aligned input color blocks | Pads blocks to the relevant dynamic-offset alignment | Dynamic UBO or SSBO reads select blocks | Separates legal offset placement from descriptor ordering. |
| Descriptor layouts and sets | Uses `single_set`, `multiset`, or `arrays` layout grouping | Bind commands consume dynamic-offset arrays | Exercises set, binding, and array ordering. |
| Render target or output buffer | Creates image readback for graphics and host-visible output for compute | Draw or dispatch writes observable values | Gives each path a host-visible oracle. |
| Generated `vert`, `frag`, and `comp` programs | Builds GLSL from the selected binding order in combined cases | Reads UBOs and SSBOs | Makes each selected dynamic region observable. |

## What Is Checked

- Ordinary graphics cases render reference-renderer quads and use `tcu::intThresholdPositionDeviationCompare()` with `UVec4(2, 2, 2, 2)`.
- Ordinary compute cases calculate expected color sums and compare each aligned output `Vec4` exactly.
- Combined cases compare the copied image with `tcu::floatThresholdCompare()` at `Vec4(0.01f)` and compare each SSBO output vector at `0.01f` tolerance.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `graphics`, `compute`, `combined_descriptors`

The family selects the observable pipeline path. Within `combined_descriptors`, the direct intermediate nodes `all_offsets` and `single_offset` select whether every instance receives a changing offset array or whether one set of offsets targets one instance.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `graphics` | Dynamic-offset address calculation, offset-array ordering, graphics descriptor binding, or image result handling selects wrong data. |
| `compute` | Dynamic-offset address calculation, offset-array ordering, compute descriptor binding, or output-buffer visibility selects wrong data. |
| `combined_descriptors` with `all_offsets` | One or more UBO or SSBO offsets, their alignment, or their reordered binding association selects the wrong region across repeated draws or dispatches. |
| `combined_descriptors` with `single_offset` | A selected UBO, SSBO-read, or SSBO-write offset selects the wrong single target, or graphics and compute use inconsistent descriptor bindings. |

## Important Variations and Special Cases

- `graphics` is registered for all pipeline construction roots. `compute` and `combined_descriptors` are registered only for `monolithic` because compute cannot use `VK_EXT_graphics_pipeline_library` in this test.
- Ordinary cases cover `single_set`, `multiset`, and `arrays`; dynamic uniform and storage descriptors; one or two command buffers; binding order; dynamic/non-dynamic binding counts; and `bind` or non-VulkanSC `bind2` commands.
- `reverseorder` is omitted with one command buffer, and two descriptor-set binding operations are omitted with two command buffers.
- `bind2` requires `VK_KHR_maintenance6` through the source support check and uses `vkCmdBindDescriptorSets2KHR`.
- The split `vk-default/pipeline` mustpass files contain 1,560 `dynamic_offset` leaves: 408 under `monolithic/monolithic.txt` and 192 under each of six non-monolithic pipeline files.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Parameters and ordinary registration | [`TestParams` and `createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L55-L154) | Defines the parameter model used by graphics and compute cases. |
| Graphics execution and oracle | [`DynamicOffsetGraphicsTestInstance`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L215-L758) | Creates aligned buffers, records draws, and compares the image. |
| Compute execution and oracle | [`DynamicOffsetComputeTestInstance`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L916-L1344) | Records dispatches and verifies host-visible output vectors. |
| Combined execution and generated programs | [`DynamicOffsetMixedTestInstance` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1530-L2293) | Runs five mixed dynamic bindings and verifies image plus SSBO output. |
| Registration | [`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2310-L2545) | Registers construction-type and parameter combinations. |
| Vulkan dynamic-offset contract | [descriptor sets](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3571-L3574) and [binding order/effective offset](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4643) | Defines base offset, dynamic-offset order, count, and effective address. |
| Split mustpass evidence | [`pipeline`](../../../mustpass/main/vk-default/pipeline/) | Contains the selected `dynamic_offset` leaves. |

## Questions / Risk Points for User Audit

- The ordinary graphics source passes `m_params.numDynamicBindings` as the legacy command's `dynamicOffsetCount`; this is correct there because graphics has no dynamic output descriptor. The ordinary compute path has one extra dynamic output binding and adds its output offset.
- Combined leaves check both graphics and compute outputs. A mismatch can identify an incorrect selected region but cannot by itself isolate the wrong UBO/SSBO binding when several values contribute to the final result.

## Conversion Notes for Final Wiki Rewrite

- Keep the Failure Cause Mapping table unchanged in the final page.
- Use test family as the primary behavior axis and retain `all_offsets` and `single_offset` as mixed-family behavior distinctions.
- Treat generated shaders as descriptor consumers rather than the behavior under test; document their read/write roles without a shader walkthrough.
