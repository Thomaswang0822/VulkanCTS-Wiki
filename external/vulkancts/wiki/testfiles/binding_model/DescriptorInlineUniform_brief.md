# Understanding Brief: `binding_model.inline_uniform_blocks`

## One-Sentence Test Purpose

This test checks whether Vulkan inline uniform block descriptor writes and descriptor copies transfer the requested four-byte-aligned data ranges to the byte offsets that a fragment shader reads.

## Background Knowledge

### Inline uniform block storage and shader interface

An inline uniform block is a uniform-like descriptor whose storage is held in the descriptor set rather than in a separate buffer object. A descriptor-set layout binding of type `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` uses `descriptorCount` as its capacity in bytes, not as the number of array elements. The capacity and every update size are multiples of four in the rules used by this test ([inline uniform block](../../../../vulkan-docs/src/chapters/descriptors.adoc#L430-L458), [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L452)).

The shader declares the resource as a `Uniform` storage-class block with `OpTypeStruct` in SPIR-V. In the generated GLSL, each four-byte slot becomes one `int` member. The binding number and set number must match the descriptor-set layout, and the block members must fit inside `maxInlineUniformBlockSize` ([inline uniform block interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1316-L1326), [resource interface table](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1536-L1540)).

Why it matters here:

- A 4, 8, or 16 byte binding exposes 1, 2, or 4 generated `int` members.
- The test uses `dstArrayElement` as a byte offset into the binding, so offset 4 selects the second four-byte slot.
- The fragment shader turns descriptor contents into an observable green or non-green render result.

### Inline uniform block writes and copies

For an inline uniform block write, `VkWriteDescriptorSet::dstArrayElement` is the destination byte offset and `VkWriteDescriptorSet::descriptorCount` is the number of bytes to update. The data comes from a `VkWriteDescriptorSetInlineUniformBlock` structure in the write's `pNext` chain. Its `dataSize` must equal `descriptorCount`, and its data size must be a multiple of four ([`VkWriteDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3059-L3093), [inline block write data](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3153-L3159), [`VkWriteDescriptorSetInlineUniformBlock`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3714-L3743)).

For a descriptor copy, `srcArrayElement` and `dstArrayElement` are the source and destination byte offsets, while `descriptorCount` is the number of bytes copied. The source and destination offsets and the byte count must be multiples of four ([`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3925), [copy validity rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3972-L3986)).

Why it matters here:

- The write cases exercise a complete binding, then a partial range at destination offset 4.
- The copy cases exercise complete ranges, a nonzero destination offset, and a nonzero source offset.
- The source implementation emits descriptor writes before copies so the source data for each copy has been initialized before the copy operation is submitted.

## One Concrete Example

The smallest write case constructs the following operation model:

```text
dEQP-VK.binding_model.inline_uniform_blocks.write_size_4

binding_model.inline_uniform_blocks
└── write_size_4

Descriptor set 0, binding 0: inline uniform block capacity 4 bytes
Write: destination offset 0, data size 4 bytes
Initial word data: [1]
Expected shader-visible word after the write: [1]
```

The source stores the word in `m_dataToWrite`, points `pData` at that word, and records the update as `UPD_STATUS_WRITTEN`. The generated fragment shader declares one `int data1` member and compares it with the expected value `1`. It writes `(0, 1, 0, 1)` when the comparison succeeds and `(1, 0, 1, 0)` otherwise ([write-case construction](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L798), [fragment generation](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L721-L763)).

## End-to-End Test Flow

```text
[host] choose one of the nine registered write or copy cases
[host] create the operation model with descriptor set, binding, byte capacity, byte offsets, and byte count
[host] seed each descriptor's four-byte words with unique values and record expected verification data
[host] create a descriptor pool with inline uniform block capacity and descriptor-set layouts whose binding counts are byte capacities
[host] allocate the descriptor sets
[host] build inline uniform block writes with VkWriteDescriptorSetInlineUniformBlockEXT in pNext
[host] build any VkCopyDescriptorSet operations with source and destination byte offsets
[host] submit descriptor writes and copies through vkUpdateDescriptorSets
[host] generate and compile the fixed vertex and case-specific fragment shaders
[device] render six vertices into a 1 x 16 color attachment
[device] load the updated inline uniform block members and choose green when all emitted comparisons pass
[host] wait for completion, copy the image to a host-visible buffer, and invalidate the allocation
[host] compare every pixel with the exact green reference and return Pass or Fail
```

`DescriptorOps::copyDescriptor` updates the destination verification values from the source data before it records the source and destination writes and the copy. This models the value that the destination block should expose after the copy ([operation bookkeeping](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L336-L385)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test builds two GLSL programs in `DescriptorInlineUniformTestCase::initPrograms`:

- A fixed GLSL 4.50 vertex shader emits a six-vertex full-screen rectangle using `gl_VertexIndex` ([vertex generation](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L704-L720)).
- A fragment shader emits one `uniform IubK` block for every modeled descriptor. The block contains one `int` member per four bytes. It compares only members whose source-side update status is not `UPD_STATUS_NONE`, then chooses green or magenta ([fragment generation](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L721-L763)).

No shader computes descriptor offsets. The host writes those offsets into Vulkan update structures, while the generated member order provides the shader-visible observation points.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Inline uniform block descriptors | yes | yes, set 0 at binding 0, and binding 1 for copy cases | read by the fragment shader | indirectly through the color image | Hold the byte ranges under test without a separate buffer object. |
| Descriptor pool and set layouts | yes | yes | used by descriptor lookup | no | The pool accounts for total inline-uniform bytes and the layout declares each binding's byte capacity. |
| Color image and view | yes | color attachment | written by the fragment shader | yes, through a transfer copy | Carries the shader comparison result to host validation. |
| Host-visible output buffer | yes | transfer destination | written by `copyImageToBuffer` | yes | Supplies all `1 x 16` pixels to `verifyResultImage`. |

The operation model's `m_dataToWrite`, `m_verificationData`, and `m_updateStatus` vectors are host-side bookkeeping, not Vulkan resources. The source initializes one four-byte word per slot with a unique value starting at 1 ([descriptor model](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L78-L147)).

## What Is Checked

| Operation shape | Registered cases | Device observation | Host pass condition |
|-----------------|------------------|--------------------|---------------------|
| Complete write sizes | `write_size_4`, `write_size_8`, `write_size_16` | Read 1, 2, or 4 updated `int` members from binding 0 | Every pixel is exactly `(0, 1, 0, 1)`. |
| Nonzero write destination | `write_offset_nonzero` | Write 8 bytes at destination byte offset 4 in a 16-byte binding | Every pixel is exactly green for the members that the source marks as written. |
| Complete copy sizes | `copy_size_4`, `copy_size_8`, `copy_size_16` | Copy 1, 2, or 4 four-byte slots from binding 0 to binding 1 | Every pixel is exactly green for the destination comparisons. |
| Nonzero copy destination | `copy_at_offset_nonzero` | Copy 8 bytes from source offset 0 to destination offset 4 | Every pixel is exactly green for the destination comparisons emitted by the source. |
| Nonzero copy source | `copy_from_offset_nonzero` | Copy 8 bytes from source offset 4 to destination offset 0 | Every pixel is exactly green for the destination comparisons emitted by the source. |

`verifyResultImage` constructs a `1 x 16` all-green reference and uses a zero threshold. A mismatch anywhere makes the case fail. The returned failure text is `Rendered image(s) are incorrect` ([image verification](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L464-L483), [final result](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L659-L666)).

The status bookkeeping has a source-level range detail that matters when interpreting coverage. `changeStatus` computes `updIdx = offset / 4` and `updSize = size / 4`, then marks indices from `updIdx` while `i < updSize`. For offset zero this covers the requested slots. For a nonzero offset, it does not mark every slot through `updIdx + updSize - 1`; for example, an offset of 4 and size 8 marks only index 1. The generated shader therefore does not independently compare every byte requested by the nonzero-offset operation. This is the actual source behavior, not a Vulkan rule ([status update](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L109-L155)).

## Behavior Parameter Identification

> **Behavior parameter:** operation shape, grouping the registered leaves by the inline uniform update range they exercise
>
> **Candidate values:** `complete_write_sizes`, `nonzero_write_destination`, `complete_copy_sizes`, `nonzero_copy_destination`, `nonzero_copy_source`

These five values preserve all nine registered leaves while separating write semantics from copy semantics and distinguishing a destination offset from a source offset.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `complete_write_sizes` | Complete inline uniform write handling. |
| `nonzero_write_destination` | Nonzero write destination handling. |
| `complete_copy_sizes` | Complete inline uniform copy handling. |
| `nonzero_copy_destination` | Nonzero copy destination handling. |
| `nonzero_copy_source` | Nonzero copy source handling. |

## Important Variations and Special Cases

- The write capacities and copy capacities are exactly 4, 8, and 16 bytes. Every capacity, write size, copy size, and offset used by the test is four-byte aligned. The Vulkan validity rules require those alignment choices; the test does not register invalid alignment cases ([layout validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L533-L549), [write validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3280-L3293), [copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3972-L3986)).
- All descriptors use set 0. Write cases use binding 0. Copy cases use source binding 0 and destination binding 1, both in set 0 ([write and copy registration](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L842)).
- For a copy, `updateVerificationData` reads the source data before the source and destination writes are registered. The operation model expects the destination range to match the source range, but the fragment shader checks only slots whose status is marked by `changeStatus`.
- The source file is guarded by `#ifndef CTS_USES_VULKANSC`, and each case requires `VK_EXT_inline_uniform_block`. Vulkan SC builds therefore do not register this family, while devices without the required inline uniform block functionality receive a support failure before execution ([support check and guard](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L65-L80), [support check](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L699-L702)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L72) | Attaches the inline uniform block group under `binding_model`. |
| Descriptor data model | [`InlineUniformBlockDescriptor`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L78-L155) | Defines four-byte storage, unique initial values, verification data, and update status. |
| Write and copy operation builders | [`DescriptorOps`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L280-L385) | Records ranges, expected copy results, descriptor writes, and descriptor copies. |
| Descriptor setup and update | [`DescriptorInlineUniformTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L486-L573) | Creates the pool and layouts, then submits write and copy updates. |
| Generated shaders | [`DescriptorInlineUniformTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L699-L763) | Defines descriptor declarations, slot comparisons, and green or magenta output. |
| Host result validation | [`verifyResultImage()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L464-L483) | Requires an exact all-green `1 x 16` result. |
| Registered write leaves | [`createInlineUniformWriteTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L766-L798) | Defines the four write cases and their capacities, offsets, and sizes. |
| Registered copy leaves | [`createInlineUniformCopyTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L800-L843) | Defines the five copy cases and their source and destination ranges. |
| Family factory | [`createDescriptorInlineUniformTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorInlineUniformTests.cpp#L846-L853) | Creates `inline_uniform_blocks` and attaches write and copy leaves. |
| Mustpass coverage | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L46183-L46191) | Confirms the exact nine default mustpass leaves. |
| Inline uniform block model | [Inline Uniform Block](../../../../vulkan-docs/src/chapters/descriptors.adoc#L430-L458) | Defines descriptor-set-backed storage and byte-capacity semantics. |
| Descriptor layout rules | [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L452) | Defines byte counts and four-byte alignment for inline uniform bindings. |
| Write rules | [`VkWriteDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3059-L3159) | Defines destination byte offsets, byte counts, and the `pNext` data source. |
| Inline write structure | [`VkWriteDescriptorSetInlineUniformBlock`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3714-L3743) | Defines `dataSize`, `pData`, and four-byte data alignment. |
| Copy rules | [`VkCopyDescriptorSet`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3888-L3986) | Defines source and destination byte offsets and copy alignment. |
| Shader interface | [Inline uniform block interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1316-L1326) | Defines the SPIR-V `Uniform` and `OpTypeStruct` representation. |

## Questions / Risk Points for User Audit

- Is the operation shape axis clearer than a simple `write` versus `copy` split? Resolved: the five groups preserve the size and source/destination offset distinctions that drive the cases.
- Does the final page need a shader walkthrough? Resolved: yes, one `write_size_4` fragment walkthrough is enough because all cases use the same generated shader pattern; the final page must carry compiler-generated, validated full SPIR-V for that exact fragment.
- Are the nonzero-offset host checks described accurately? Resolved: the page records the source's `changeStatus` loop and limits its claim to the comparisons emitted by the source.
- Are feature and build gates clear? Resolved: the source requires `VK_EXT_inline_uniform_block` and excludes the family under `CTS_USES_VULKANSC`.
- Are all registered leaves covered? Resolved: the nine names match both source registration and the default mustpass file.
- No unresolved semantic risk remains after checking the implementation, registration, mustpass evidence, descriptor and inline-uniform specification chapters, and shader interface rules.

## Conversion Notes for Final Wiki Rewrite

- Start the final page at `## Overview` and omit the old page's top-level title.
- Use the five operation-shape groups as the primary behavior axis, with exact registered leaves listed in the parameter table and behavior subsections.
- Copy the `### Failure Cause Mapping` table above into the final page without changing bytes.
- Distill the descriptor storage, byte-count, offset, and shader interface rules into a short `## Background Knowledge` section.
- Include one `### Representative Shader Walkthrough 1` for `write_size_4`, generated from the exact fragment builder and followed by the complete validated SPIR-V subsection. Do not add walkthroughs for the fixed vertex shader or offset variants because the fragment generator pattern is unchanged.
- Explain the descriptor pool, layouts, writes, copies, draw, image copyback, exact green comparison, support gate, and source-level status bookkeeping in the final page.
- Keep source and spec links in a focused appendix and retain mustpass provenance.
- Write `### Cause Analysis` fresh in the final page. Do not copy analysis prose from this brief.
