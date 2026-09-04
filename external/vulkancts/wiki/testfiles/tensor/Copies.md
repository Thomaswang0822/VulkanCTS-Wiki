## Overview

**Core question:** Does `vkCmdCopyTensorARM` preserve every logical element across compatible tensor formats and layouts?

- This page covers the `tensor.copies` test family, registered by [`createTensorCopyTests`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L521-L530) and added below the `tensor` test category by [`createTests`](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49).
- The implementation tests packed linear tensors, explicitly strided linear tensors, and a three-copy path through optimal tensors. It pairs signed and unsigned formats at 8, 16, 32, and 64 bits.
- Each case uses equal source and destination dimensions and one full-tensor `vkCmdCopyTensorARM` region. The destination readback must match the source at every logical element.
- The test matrix also covers host upload and readback, transfer ordering, and support checks. These tests issue transfer commands only, so they have no shader behavior to describe.

## Background Knowledge

- **Tensor tiling.** Linear tensors use byte strides to locate elements. Optimal tensors use an implementation-dependent arrangement and require `pStrides` to be `NULL`, so the test uses linear tensors for host-facing input and output.
- **Packed and non-packed tensors.** A packed tensor has an innermost stride equal to the element size and outer strides equal to the following stride multiplied by its dimension. Explicit linear strides can add padding between rows or higher dimensions when the `tensorNonPacked` feature is enabled.
- **Raw tensor copies.** `vkCmdCopyTensorARM` copies tensor data like a host `memcpy`. It does not scale, resize, or numerically convert values. Different source and destination formats are valid here only when they are size-compatible and belong to the same format class.

## Registration Hierarchy

```text
tensor.copies
```

The `copies` test family expands into generated leaves whose names encode source parameters, destination parameters, shape, and, for non-packed linear tensors, strides. The complete generated matrix is described below rather than expanded into the hierarchy tree.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Element width and format | `r8_uint`, `r8_sint`, `r16_uint`, `r16_sint`, `r32_uint`, `r32_sint`, `r64_uint`, `r64_sint` | `getTestFormats<T>()` supplies one signed and one unsigned format for each host element type. Cross-format copies keep the same element width. | [`getTestFormats<T>()`](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L115-L156) |
| Shape | `71693`, `263_269`, `37_43_47`, `13_17_19_23` | Covers ranks one through four and supplies the equal source and destination dimensions required by the copy operation. | [`shapes`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L459-L464) |
| Linear layout | packed to packed, packed to non-packed, non-packed to packed | Selects empty strides for packed tensors or explicit strides for one linear endpoint. | [`addTensorCopyTests`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L472-L507) |
| Optimal layout | optimal to optimal | Selects the four-tensor path with linear host endpoints and two optimal tensors in the middle. | [`addTensorCopyTests`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L509-L515) |
| Explicit strides | `r`, `r * next_dimension + 13 * elementSize` for outer dimensions | Keeps the innermost stride at the element size and adds deterministic padding to each outer stride. The registered names contain the resulting byte strides. | [`paddedStrides`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L480-L489) |

The source and destination format values appear in each generated case name as `<source_parameters>_to_<destination_parameters>`. For example, `r16_uint_linear_shape_263_269_to_r16_sint_linear_shape_263_269_strides_564_2` identifies the copy direction, formats, tiling, shape, and destination strides.

## Behavior Parameters

The primary behavioral axis is the layout path. Format width, signedness, shape, and explicit stride values vary the instance within each path.

### Packed to packed linear: host-addressable copy

Both tensors use linear tiling with empty stride vectors. `makeTensorDescription` passes `NULL` strides, and the implementation supplies packed strides. The test records one copy from the source tensor to the destination tensor.

### Packed to non-packed linear: padded destination

The source uses packed linear addressing. The destination uses explicit strides. For ranks greater than one, the test adds `13 * elementSize` bytes to each outer packed stride, so the destination contains padding between logical rows or higher-dimensional slices. The test must preserve the logical element at each destination coordinate despite those gaps.

### Non-packed to packed linear: strided source

The source uses explicit strides and the destination uses packed linear addressing. The host source array follows the explicit byte strides, while the comparison indexes the destination with its packed layout. This reverses which endpoint carries the padding from the packed-to-non-packed case.

### Optimal through linear endpoints: three transfer stages

The optimal case creates a linear source, an optimal source, an optimal destination, and a linear destination. The command sequence is linear to optimal, optimal to optimal, and optimal to linear. The source and destination formats may differ within the same element width, but the dimensions remain equal.

## Shader Analysis

These tests do not create or execute shaders. `vktTensorCopies.cpp` creates tensors, records `vkCmdCopyTensorARM`, submits transfer work, and compares host data. No shader walkthrough is applicable to this page.

## Runtime Execution and Result Checking

- Each test requires `VK_ARM_tensors` and checks both tensor ranks against `maxTensorDimensionCount`.
- The test creates each tensor with `makeTensorDescription`, sets `VK_TENSOR_USAGE_TRANSFER_SRC_BIT_ARM` on source tensors and `VK_TENSOR_USAGE_TRANSFER_DST_BIT_ARM` on destination tensors, then binds each object with `TensorWithMemory`.
- `TensorParameters` carries the format, tiling, dimensions, and optional strides. `StridedMemoryUtils<T>` derives packed strides when the vector is empty, fills each logical element with its flattened index, and computes its byte-stride address for explicit layouts.
- The helper uploads the source host bytes. If the tensor allocation is host visible, it writes and flushes the allocation directly. Otherwise it copies through a host-visible staging buffer into a buffer aliasing the tensor allocation, inserts a transfer-to-memory barrier, and waits for the queue submission.
- The helper clears the destination before the copy. The clear follows the same direct or staging route as upload.
- The linear instance records one `VkTensorCopyARM` region with `dimensionCount` equal to the rank and `pSrcOffset`, `pDstOffset`, and `pExtent` left `NULL`. The command therefore copies the complete tensor from zero offsets.
- The linear instance records a tensor memory barrier from transfer writes to host reads after `vkCmdCopyTensorARM`. The command buffer is submitted to the universal queue and the test waits for completion.
- The optimal instance records three full-tensor copies. It places a transfer-write to transfer-read memory barrier between the first and second copies and between the second and third copies. It places a final tensor barrier from the last transfer write to host read.
- The test downloads the final linear destination. A non-host-visible allocation uses a buffer alias, a host-visible readback buffer, pre-transfer and post-transfer memory barriers, queue completion, invalidation, and a host `memcpy`. A host-visible tensor allocation uses invalidation followed by a direct host copy.
- The host compares `inputData[element_idx]` with `result[element_idx]` for every logical element. The first mismatch returns `Comparison failed at index <n>: source = <value>, destination = <value>`; otherwise the case returns `Tensor test succeeded`.

The extension's copy rules require equal rank and equal dimension sizes, one region, zero offsets, and a full extent. The test's `VkTensorCopyARM` initialization follows those restrictions. The source and destination tensors also require the matching transfer format features, transfer usage bits, and complete contiguous bindings required by the specification.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| packed to packed linear | Incorrect raw tensor copy, incompatible same-width format handling, linear addressing, or host upload/readback synchronization. |
| packed to non-packed linear | Incorrect handling of explicit destination strides or padding between logical rows, in addition to the common copy and synchronization causes. |
| non-packed to packed linear | Incorrect handling of explicit source strides or logical-to-packed addressing, in addition to the common copy and synchronization causes. |
| optimal through linear endpoints | Incorrect linear-to-optimal, optimal-to-optimal, or optimal-to-linear transfer, missing ordering between chained copies, or incorrect final readback. |

### Cause Analysis

#### Packed linear copy or same-width format handling

**Possible failure symptoms:** A packed linear case reports a logical element mismatch after the destination readback. The same symptom can appear when a signed and unsigned format of the same width is copied with the wrong raw representation.

**Possible implementation causes:** The copy implementation may address a packed tensor incorrectly or reject or mishandle the compatible format pair. The specification defines this command as a raw copy and limits different formats to compatible classes, so the result should not undergo a numerical conversion. If the mismatch occurs only after host transfer, inspect the upload and readback path separately.

#### Explicit destination stride handling

**Possible failure symptoms:** A packed-to-non-packed case reports a mismatch at an element in a later row or higher-dimensional slice. Elements in earlier rows may match while the destination's padded layout is wrong.

**Possible implementation causes:** The implementation may calculate a destination address as if the tensor were packed, skip the explicit outer stride, or copy padding as though it were logical tensor data. The source creates strides in bytes and the host comparison uses the same destination stride model, so a failure points to copy addressing or the handling of non-packed tensor descriptions. The source does not establish a more specific driver or hardware cause.

#### Explicit source stride handling

**Possible failure symptoms:** A non-packed-to-packed case reports a mismatch at an index whose source coordinate crosses a padded row or higher-dimensional slice.

**Possible implementation causes:** The implementation may read source elements using packed offsets instead of the explicit source strides. The tensor description rules require valid positive, element-size-multiple strides, and the test creates them from the source element size. Further attribution requires implementation-level investigation.

#### Optimal layout transfer ordering or conversion

**Possible failure symptoms:** A case fails only after the three-stage path, or the final linear destination differs even though the single linear copy cases pass. The mismatch can result from any of the three transitions or from reading the final tensor before the last transfer write becomes host visible.

**Possible implementation causes:** The implementation may mishandle an optimal tensor's opaque layout, one direction of the linear and optimal transitions, or the optimal-to-optimal copy. The recorded transfer barriers establish ordering between adjacent copies, and the final tensor barrier plus queue wait establishes host visibility. A failure that remains after checking those test-side conditions needs source and implementation investigation.

## Case Pruning

### Requirement-based pruning

- The test skips the case when `VK_ARM_tensors` is unavailable.
- The test skips a case when either tensor rank exceeds `maxTensorDimensionCount`.
- Linear cases require `VK_FORMAT_FEATURE_2_TRANSFER_SRC_BIT` for the source format and tiling and `VK_FORMAT_FEATURE_2_TRANSFER_DST_BIT` for the destination format and tiling.
- Optimal cases require transfer-source and transfer-destination support for both optimal formats, linear transfer-source support for the source format, and linear transfer-destination support for the destination format.
- Linear cases with explicit strides skip when `deviceSupportsNonPackedTensors` reports that `tensorNonPacked` is unavailable.

These are support decisions made by `checkSupport`; they do not represent failed copies.

### Design-based pruning

- The matrix pairs only the signed and unsigned formats returned by `getTestFormats<T>()` for the same element width. It does not test a size-changing format conversion.
- Non-packed variants require rank greater than one because a one-dimensional explicit stride would add no meaningful outer-dimension padding.
- The copy region always covers the entire tensor. The current extension valid usage rules require one region with zero offsets and dimensions equal to the tensor dimensions, so the CTS does not generate subregion or offset cases.
- The optimal path uses linear endpoints because the host helpers need a known linear layout for manual upload and readback. It does not claim to test host access to optimal tensor storage.

## Key Takeaways

- `vkCmdCopyTensorARM` is tested as a raw, whole-tensor transfer, not as a numerical conversion operation.
- Linear cases make explicit stride handling observable by comparing logical elements through packed and padded host layouts.
- Optimal cases test all three transfer directions in a linear to optimal to optimal to linear chain while keeping host access at the linear endpoints.
- Transfer barriers, queue completion, allocation invalidation, and optional staging buffers are part of the correctness path. A mismatch can therefore reflect copy addressing, layout handling, or host/device visibility.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Copy registration matrix | [`addTensorCopyTests`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L456-L519) | Defines formats, shapes, strides, layout paths, and generated case names. |
| Linear copy instance | [`LinearTensorCopyTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L135-L234) | Creates linear tensors, performs one copy, synchronizes, reads back, and compares. |
| Optimal copy instance | [`OptimalTensorCopyTestInstance::iterate`](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L314-L452) | Creates four tensors and performs the three-copy chain. |
| Tensor category factory | [`createTests`](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Registers `copies` below the `tensor` test category. |
| Vulkan package registration | [`VulkanTestPackage::init`](../../../modules/vulkan/vktTestPackage.cpp#L1397-L1400) | Registers the `tensor` test category at the `dEQP-VK` package root. |
| Tensor parameters | [`TensorParameters`](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L68-L101) | Defines rank, element count, host data size, and packed detection. |
| Host strided storage | [`StridedMemoryUtils`](../../../framework/vulkan/vkTensorMemoryUtil.hpp#L154-L317) | Fills logical elements and resolves coordinates through byte strides. |
| Tensor upload, readback, and clear | [`vkTensorUtil.cpp`](../../../framework/vulkan/vkTensorUtil.cpp#L41-L189) | Defines direct host access, staging aliases, barriers, waits, and invalidation. |
| Tensor creation description | [`makeTensorDescription`](../../../framework/vulkan/vkObjUtil.cpp#L849-L867) | Passes tiling, format, dimensions, strides, and usage to tensor creation. |
| Tensor object and memory | [`TensorWithMemory`](../../../framework/vulkan/vkTensorWithMemory.hpp#L37-L79) | Creates a tensor and binds its allocation. |
| Copy command semantics | [Copying Data Between Tensors](../../../../vulkan-docs/src/chapters/copies.adoc#copies-tensors) | Defines raw copying, compatible formats, and copy structures. |
| Copy constraints | [Tensor copy valid usage](../../../../vulkan-docs/src/chapters/copies.adoc#copies-tensors-format-size-compatibility) | Defines equal dimensions, one full region, transfer features, usage, and binding requirements. |
| Tiling and stride semantics | [Tensor description strides](../../../../vulkan-docs/src/chapters/resources.adoc#resources-tensor-description-strides) | Defines packed tensors, explicit strides, and linear versus optimal tiling. |
| Tensor transfer usage | [Tensor usage flags](../../../../vulkan-docs/src/chapters/resources.adoc#VkTensorUsageFlagBitsARM) | Defines transfer source and destination usage. |
| Tensor mustpass entries | [`tensor.txt`](../../../mustpass/main/vk-default/tensor.txt#L1-L844) | Lists the registered tensor cases, including the `tensor.copies` matrix. |
