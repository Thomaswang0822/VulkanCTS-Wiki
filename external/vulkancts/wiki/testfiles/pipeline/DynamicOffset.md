## Overview

**Core question:** Do dynamic descriptor offsets select the intended aligned buffer regions for graphics, compute, and mixed pipeline work?

- [`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1) implements the `dynamic_offset` test family under the `pipeline` test category.
- The family covers graphics and compute cases with dynamic uniform or storage buffer descriptors, plus monolithic mixed graphics-and-compute cases.
- Each case binds descriptor sets with an offset array, executes a draw, dispatch, or both, and checks image data, buffer data, or both.
- This page explains the registered matrix, the offset-ordering behavior, host/device flow, and what a mismatch can mean.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC` or `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC` descriptor combines a descriptor base offset with a dynamic offset supplied at bind time. Vulkan uses their sum as the effective address while keeping the descriptor range fixed ([descriptor buffer information](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3571-L3574), [effective dynamic offset](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4638-L4643)).
- Vulkan consumes dynamic offsets in set order, then binding-number order, then array-element order. `dynamicOffsetCount` must equal the number of dynamic descriptors ([dynamic-offset binding order](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4636)). The test changes how descriptors are grouped to expose mistakes in that ordering.
- Uniform and storage dynamic offsets use different device alignment limits. The source pads its color blocks to the selected limit before creating offset values.

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_offset
├── graphics
├── compute
└── combined_descriptors
```

The `graphics` intermediate node is registered for each construction root. The `compute` and `combined_descriptors` intermediate nodes are added only below `monolithic.dynamic_offset` because compute cannot use the graphics-pipeline-library construction in this implementation. The source registration is in [`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2310-L2545).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Direct intermediate node | `graphics`, `compute`, `combined_descriptors` | Selects the observable pipeline path and result oracle. | [`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2372-L2482) |
| Grouping strategy | `single_set`, `multiset`, `arrays` | Places dynamic descriptors in one set, separate sets, or descriptor arrays. | [`GroupingStrategy`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L71-L75) and layout setup ([compute](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L948-L969)) |
| Descriptor type | `uniform_buffer`, `storage_buffer` | Selects the dynamic descriptor alignment and buffer type. | [`descriptorTypes`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2325-L2330) |
| Command buffers | `numcmdbuffers_1`, `numcmdbuffers_2` | Tests one command buffer or multiple submissions. | [`numCmdBuffers`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2332-L2336) |
| Order | `sameorder`, `reverseorder` | Changes the order in which command buffers are recorded and submitted. `reverseorder` requires two buffers. | [`reverseOrders`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2338-L2343) |
| Descriptor-set bindings | `numdescriptorsetbindings_1`, `numdescriptorsetbindings_2` | Changes the number of descriptor-set bind operations. The value `2` is omitted with two command buffers. | [`numDescriptorSetBindings`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2344-L2348) |
| Dynamic bindings | `numdynamicbindings_1`, `numdynamicbindings_2` | Changes how many input descriptors receive dynamic offsets. | [`numDynamicBindings`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2350-L2354) |
| Non-dynamic bindings | `numnondynamicbindings_0`, `numnondynamicbindings_1` | Adds fixed-offset descriptors beside the dynamic descriptors. | [`numNonDynamicBindings`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2356-L2360) |
| Bind command | `bind`, `bind2` | Selects `vkCmdBindDescriptorSets`; `bind2` selects `vkCmdBindDescriptorSets2KHR` and is absent on VulkanSC. | [`descriptorBindCommands`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2362-L2370) |
| Combined offset mode | `all_offsets`, `single_offset` | Varies every mixed instance or targets one selected offset. | [`combined_descriptors` registration](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2478-L2542) |
| Combined descriptor order | `same_order`, `reverse_order` | Reorders the five mixed descriptor bindings and the offset-array mapping. | [`orders`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2484-L2489) |
| Combined offset count | `16`, `64`, `256` | Selects the number of aligned instances exercised by the mixed case. | [`numOffsets`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2491-L2497) |
| Combined pipeline order | `graphics_first`, `compute_first` | Runs the graphics and compute paths in opposite order. | [`pipelineOrders`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2499-L2503) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below the `dynamic_offset` test family. This choice changes which descriptor consumers run and which observable output the host validates.

### `graphics`: Graphics pipeline dynamic offsets

The `graphics` intermediate node binds dynamic UBO or SSBO descriptors before drawing colored quads. It uses the grouping, descriptor-count, command-buffer, ordering, and bind-command dimensions to vary the mapping from offset-array entries to descriptors. The image comparison detects a quad that uses data from the wrong buffer region.

### `compute`: Compute pipeline dynamic offsets

The `compute` intermediate node binds the same classes of dynamic input descriptors and a dynamic output storage descriptor, then dispatches once per binding operation. The compute shader sums selected color blocks into aligned output slots. This intermediate node exists only for the monolithic construction type.

### `combined_descriptors`: Mixed graphics and compute descriptors

The monolithic-only `combined_descriptors` intermediate node places three dynamic UBOs and two dynamic SSBOs in one descriptor set. Graphics reads vertex, shared, and fragment data; compute reads shared and input SSBO data and writes an output SSBO. `same_order` and `reverse_order` change the descriptor binding order, so the five supplied offsets must follow the resulting binding order.

Within this intermediate node, `all_offsets` exercises every instance in a repeated pattern. `single_offset` supplies explicit offsets for the vertex UBO, shared UBO, fragment UBO, SSBO read, and SSBO write paths, allowing one selected instance to become visible in each output.

## Shader Analysis

The shaders support the descriptor-offset check but do not introduce a separate shader behavior matrix. Ordinary graphics and compute programs consume the selected UBO or SSBO values; combined programs are generated in [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2204-L2293) with binding numbers switched for `same_order` and `reverse_order`. The tested contract is the host-provided descriptor binding and effective offset, not shader control flow.

## Runtime Execution and Result Checking

- The graphics instance determines the selected uniform or storage alignment, pads input color blocks, creates a color image and render passes, builds descriptor layouts, and writes host-visible vertex data ([graphics initialization](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L215-L692)).
- For each command buffer, it binds the pipeline and vertex buffer, creates the dynamic-offset array, binds descriptor sets with either `vkCmdBindDescriptorSets` or `vkCmdBindDescriptorSets2KHR`, and draws one quad for each descriptor-set binding. The command-buffer index is reversed when `reverseorder` is selected.
- After submission, graphics compares the image against the reference renderer with `tcu::intThresholdPositionDeviationCompare()` and threshold `UVec4(2, 2, 2, 2)` ([image verification](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L709-L758)).
- The compute instance creates aligned input and output buffers, writes each descriptor's base range, records offsets for dynamic input and output descriptors, dispatches, and inserts a compute-to-host barrier ([compute command recording](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1216-L1293)). It invalidates the output allocation and compares every `Vec4` with the calculated reference ([compute verification](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1311-L1344)).
- The combined instance creates vertex, color, and SSBO resources, records one command buffer at a time, and submits each recording immediately. It alternates graphics and compute work in the selected order, then binds five offsets per instance ([combined binding](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1965-L2053)). It compares the copied image with `tcu::floatThresholdCompare()` at `0.01f`, then compares SSBO vectors with `0.01f` tolerance ([combined checks](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2056-L2153)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `graphics` | Dynamic-offset address calculation, offset-array ordering, graphics descriptor binding, or image result handling selects wrong data. |
| `compute` | Dynamic-offset address calculation, offset-array ordering, compute descriptor binding, or output-buffer visibility selects wrong data. |
| `combined_descriptors` with `all_offsets` | One or more UBO or SSBO offsets, their alignment, or their reordered binding association selects the wrong region across repeated draws or dispatches. |
| `combined_descriptors` with `single_offset` | A selected UBO, SSBO-read, or SSBO-write offset selects the wrong single target, or graphics and compute use inconsistent descriptor bindings. |

### Cause Analysis

#### `graphics` intermediate node

**Possible failure symptoms:** The rendered quads have the wrong colors or positions, and image comparison reports a mismatch.

**Possible implementation causes:** The implementation may add the dynamic offset to the wrong descriptor base, consume offset entries in the wrong set/binding/array order, or apply a descriptor binding to the wrong graphics pipeline state. The host-side source and image comparison cannot distinguish these subcauses without further investigation.

#### `compute` intermediate node

**Possible failure symptoms:** One or more host-visible output `Vec4` values differ from the color sum calculated by the CTS.

**Possible implementation causes:** The implementation may select an incorrect dynamic input or output region, mishandle alignment, associate offsets with the wrong compute binding, or expose shader writes to the host incorrectly. Source-level investigation is needed to separate descriptor addressing from synchronization or readback defects.

#### Combined descriptors with `all_offsets`

**Possible failure symptoms:** The image gradient or one or more SSBO vectors differs from its expected value after repeated graphics and compute operations.

**Possible implementation causes:** The implementation may apply the five dynamic offsets in the wrong order, mishandle the reordered descriptor layout, or retain stale binding state between draws and dispatches. The combined oracle shows the selected data is wrong but cannot isolate one of the five bindings when their contributions overlap.

#### Combined descriptors with `single_offset`

**Possible failure symptoms:** The selected colored square is at the wrong location, the image uses the wrong color, or the expected SSBO write slot remains unchanged or changes at another index.

**Possible implementation causes:** The implementation may map one explicit offset to the wrong UBO or SSBO, use the wrong binding numbers after `reverse_order`, or fail to preserve descriptor state across the graphics-first and compute-first sequences. Further source-level investigation is needed when more than one result differs.

## Case Pruning

- The factory skips `reverseorder` when `numCmdBuffers` is one because there is no second command buffer to reorder.
- It skips `numDescriptorSetBindings == 2` when two command buffers are selected, avoiding that combination in the registered matrix.
- It omits `compute` and `combined_descriptors` for non-monolithic construction types because the implementation excludes compute from those pipeline construction modes.
- It omits `bind2` on VulkanSC at compile time. On supported non-SC builds, the test's support check requires the pipeline construction requirements and `VK_KHR_maintenance6` for the `bind2` path ([support check](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L789-L795)).
- The inspected split `vk-default/pipeline` mustpass scope contains 1,560 matching leaves: 408 in `monolithic/monolithic.txt` and 192 in each of `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, `shader-object-unlinked-binary.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`.

## Key Takeaways

- Dynamic descriptor offsets are relative additions to descriptor base offsets, and Vulkan orders the offset array by set, binding, and array element.
- The ordinary `graphics` and `compute` intermediate nodes stress descriptor grouping, descriptor type, command-buffer order, dynamic/non-dynamic mixtures, and both bind command forms.
- The combined monolithic intermediate node makes five reordered UBO and SSBO bindings observable through both graphics and compute outputs.
- A failure proves that an expected image or buffer value was not produced. The exact fault location requires follow-up investigation of offset mapping, descriptor state, shader access, synchronization, or host readback.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Original navigation page | [`vktPipelineDynamicOffsetTests.md`](vktPipelineDynamicOffsetTests.md) |
| Implementation and registration | [`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp) |
| Public declaration | [`vktPipelineDynamicOffsetTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.hpp) |
| Pipeline category registration | [`vktPipelineTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L102-L115) |
| Dynamic descriptor semantics | [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3571-L3574) and [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4672) |
| Split mustpass directory | [`vk-default/pipeline`](../../../mustpass/main/vk-default/pipeline/) |
