# Understanding Brief: tensor.copies

## One-Sentence Test Purpose

This test checks whether `vkCmdCopyTensorARM` preserves tensor element bytes across compatible source and destination formats, linear layouts, explicit strides, and the linear-to-optimal-to-linear path.

## Background Knowledge

### Tensor tiling and strides

A linear tensor stores elements at offsets described by `pStrides`; `pStrides[i]` is the byte distance for increasing coordinate `i`. A packed tensor uses the element size for the innermost stride and the product of the following stride and dimension for each outer stride. An optimal tensor has an implementation-dependent layout, so its `pStrides` must be `NULL` and host code cannot address its storage by walking a known stride array.

Why it matters here:
- The linear tests can compare packed and explicitly padded layouts because host memory can follow either stride array.
- The optimal test must use linear tensors at the host-facing ends and tests the opaque layout through tensor copy commands.
- The source and destination tensors have equal dimensions, while their formats and linear packing may differ.

### Raw copy versus format conversion

`vkCmdCopyTensorARM` behaves like a host `memcpy`: it copies raw tensor data and does not scale, resize, or convert values. The Vulkan specification permits different source and destination formats when they are size-compatible and in the same format class. The CTS therefore pairs signed and unsigned formats of the same width, such as `VK_FORMAT_R16_SINT` and `VK_FORMAT_R16_UINT`; it does not test a numerical signed-to-unsigned conversion.

Why it matters here:
- The host fills source storage with a sequence of values using the C++ type selected for the format width.
- The destination is compared through the same-width host type, so a successful cross-format copy means the copied representation survives, not that Vulkan performed a numeric conversion.
- The copy region describes the complete tensor. The extension currently requires one full-tensor region with zero offsets and equal dimensions.

## One Concrete Example

Consider the registered case `dEQP-VK.tensor.copies.r16_uint_linear_shape_263_269_to_r16_sint_linear_shape_263_269_strides_564_2`.

The source is a packed `VK_FORMAT_R16_UINT` linear tensor with shape `[263, 269]`. The destination is a linear `VK_FORMAT_R16_SINT` tensor with the same shape and strides `[564, 2]`. The destination's row stride is 564 bytes rather than the packed 538 bytes, so each row has 26 bytes of padding. The source host array contains the sequence `0, 1, 2, ...`; the test copies the complete tensor and later indexes the destination using its padded strides. Every logical element must equal the corresponding source element. The padding is part of the destination allocation, but the test compares logical elements rather than treating padding as tensor elements.

The optimal case has a different middle section. For a case such as `r32_uint_optimal_shape_37_43_47_to_r32_sint_optimal_shape_37_43_47`, the implementation creates four tensors in this order:

```text
linear source -> optimal source -> optimal destination -> linear destination
```

The first copy enters the optimal layout, the second tests optimal-to-optimal copying, and the third leaves the optimal layout. The host writes only the first linear tensor and reads only the final linear tensor.

## End-to-End Test Flow

```text
[host] select one of four shapes and one source/destination format pair of the same element width
[host] select packed, explicitly strided linear, or optimal tensor descriptions
[host] create and bind the source and destination tensors with transfer usage
[host] fill a StridedMemoryUtils source array with its logical element sequence
[host] upload source bytes to the source linear tensor and clear the destination
[host] record vkCmdCopyTensorARM for the selected copy path
[host] insert transfer and host visibility barriers
[host] submit the command buffer and wait for completion
[host] download the destination linear data, using a staging buffer when required
[host] compare each logical element with the source sequence
[host] return a failure at the first mismatch or pass the test
```

The optimal path expands the copy step into three commands and inserts a transfer-write to transfer-read memory barrier between adjacent copies. The linear path records one copy and a tensor memory barrier from transfer writes to host reads. The helper submissions also wait before the test reuses or inspects the memory.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

No shader or generated program artifact participates in these cases. The device operation is the transfer command `vkCmdCopyTensorARM`; the test does not create a pipeline, descriptor set, tensor view, or shader module.

The test constructs one `VkTensorCopyARM` region with `dimensionCount` equal to the tensor rank. It leaves offsets and extent `NULL`, which selects zero offsets and the complete tensor according to the extension rules.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Linear source tensor | yes | yes | transfer source | no, except through the upload path | Carries the initialized logical sequence. |
| Linear destination tensor | yes | yes | transfer destination | yes | Provides host-addressable output for comparison. |
| Optimal source tensor | only in the optimal path | yes | transfer source and destination | no | Tests entry into and use of the implementation-dependent layout. |
| Optimal destination tensor | only in the optimal path | yes | transfer source and destination | no | Tests the middle optimal-to-optimal copy. |
| Staging buffer | only when tensor memory is not host visible | yes | transfer source or destination | indirectly | Bridges host memory and tensor allocation. |
| `StridedMemoryUtils<T>` host arrays | yes | no | no | n/a | Fills and indexes logical elements using packed or explicit strides. |

`TensorWithMemory` creates each tensor and binds its complete allocation through the default allocator. The copy test passes an empty queue-family list to `makeTensorCreateInfo`, so it uses the helper's default sharing mode and submits all transfer work to the universal queue. The test does not exercise concurrent sharing or queue-family ownership transfers.

## What Is Checked

- Every source and destination tensor has the same rank and the same size in every dimension.
- The copy uses one full-tensor region. The extension defines `regionCount == 1`, zero offsets, and an extent equal to the tensor dimensions for this operation.
- The destination's logical elements match the source's logical elements at every flattened index. `StridedMemoryUtils` translates each index into multidimensional coordinates and then into the selected byte-stride address.
- The host reports `Comparison failed at index <n>: source = <value>, destination = <value>` at the first mismatch. A complete comparison returns `Tensor test succeeded`.

## Behavior Parameter Identification

> **Behavior parameter:** copy layout path
>
> **Candidate values:** packed to packed linear, packed to non-packed linear, non-packed to packed linear, optimal through linear endpoints

The format pair, shape, and element width vary the instance, but the layout path controls the transfer mechanism under test. The first three values use one `vkCmdCopyTensorARM`; the optimal value uses the three-copy chain through two optimal tensors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| packed to packed linear | Incorrect raw tensor copy, incompatible same-width format handling, linear addressing, or host upload/readback synchronization. |
| packed to non-packed linear | Incorrect handling of explicit destination strides or padding between logical rows, in addition to the common copy and synchronization causes. |
| non-packed to packed linear | Incorrect handling of explicit source strides or logical-to-packed addressing, in addition to the common copy and synchronization causes. |
| optimal through linear endpoints | Incorrect linear-to-optimal, optimal-to-optimal, or optimal-to-linear transfer, missing ordering between chained copies, or incorrect final readback. |

## Important Variations and Special Cases

- The registered shapes are `71693`, `263_269`, `37_43_47`, and `13_17_19_23`. They cover ranks one through four. The code creates non-packed linear variants only when `rank > 1`, so the one-dimensional shape has packed linear and optimal cases but no explicit-stride cases.
- For each C++ element width, `getTestFormats<T>()` supplies the signed and unsigned format pair: `r8`, `r16`, `r32`, or `r64`. Cross-format cases stay within one element size, matching the raw-copy and size-compatibility contract.
- The explicit stride at the innermost dimension equals the element size. Each outer stride adds `13 * elementSize` bytes beyond the packed row or plane extent. This produces a deterministic non-packed layout without changing the logical shape.
- Linear source and destination cases require the corresponding transfer source and destination format features. The optimal path requires both transfer features for both formats in optimal tiling, plus linear transfer source support for the source format and linear transfer destination support for the destination format.
- The copy test does not use shader tensor access. A shader walkthrough would describe behavior that this source does not execute.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Copy registration and case matrix | [addTensorCopyTests](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L456-L519) | Defines shapes, format loops, packed and non-packed variants, and the optimal path. |
| Linear copy execution | [LinearTensorCopyTestInstance::iterate](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L135-L234) | Creates linear tensors, uploads, copies, synchronizes, reads back, and compares. |
| Optimal copy execution | [OptimalTensorCopyTestInstance::iterate](../../../modules/vulkan/tensor/vktTensorCopies.cpp#L314-L452) | Defines the linear-to-optimal-to-optimal-to-linear chain and barriers. |
| Tensor parameter model | [TensorParameters](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L68-L101) | Defines rank, element count, host size, and packed detection. |
| Host logical addressing | [StridedMemoryUtils](../../../framework/vulkan/vkTensorMemoryUtil.hpp#L154-L317) | Fills logical elements and resolves explicit byte strides. |
| Host upload and readback | [tensor memory helpers](../../../framework/vulkan/vkTensorUtil.cpp#L41-L189) | Shows direct host access versus staging buffers and visibility barriers. |
| Tensor creation and binding | [TensorWithMemory](../../../framework/vulkan/vkTensorWithMemory.hpp#L37-L79) | Creates the tensor and binds one complete allocation. |
| Copy operation rules | [Copying Data Between Tensors](../../../../vulkan-docs/src/chapters/copies.adoc#copies-tensors) | Defines raw-copy behavior, compatible formats, and the copy structures. |
| Copy valid usage | [VkCopyTensorInfoARM valid usage](../../../../vulkan-docs/src/chapters/copies.adoc#copies-tensors-format-size-compatibility) | Defines equal dimensions, one full region, transfer features, usage, and binding requirements. |
| Tiling and stride rules | [tensor description](../../../../vulkan-docs/src/chapters/resources.adoc#resources-tensor-description-strides) | Defines packed tensors, explicit strides, and linear versus optimal tiling. |
| Category registration | [tensor test factory](../../../modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Places `copies` under `tensor`; the package registers the `tensor` root. |
| Mustpass coverage | [tensor mustpass entries](../../../mustpass/main/vk-default/tensor.txt#L1-L844) | Contains the registered tensor cases, including the 224 `tensor.copies` entries. |

## Questions / Risk Points for User Audit

- Is `copy layout path` the clearest primary behavioral axis for the final page?
- Does the distinction between raw representation copying and numerical format conversion remain clear?
- Does the linear versus optimal resource picture explain why the optimal path needs four tensors?
- Is the staging-buffer behavior described at the right level without implying that every allocation uses staging?
- Is the default queue-sharing choice clear without claiming that this test covers queue-family ownership transfers?
- Are the rank-dependent omission of explicit-stride cases and the `13 * elementSize` padding rule easy to find?

## Conversion Notes for Final Wiki Page

- Keep the final page's `## Background Knowledge` to the stride/tiling and raw-copy concepts; move the concrete `r16` case into concise parameter and runtime explanations.
- Preserve the one full-tensor region and equal-dimension constraints because they explain why the copy is a whole-tensor test rather than a subregion matrix.
- Describe the optimal path as three copies between four tensors, with the linear endpoints used for host upload and readback.
- Keep the source-backed no-shader statement in `## Shader Analysis` and do not add a walkthrough for a transfer-only test.
- Copy the `### Failure Cause Mapping` table above directly into the final page. Write `### Cause Analysis` separately so it explains symptoms and grounded possible causes rather than repeating the brief.
- Use the mustpass shapes, exact format names, and exact registered `tensor.copies` hierarchy tokens. Keep source links in the appendix rather than turning the page into a file inventory.
