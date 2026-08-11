# Understanding Brief: `image.general_layout`

## One-Sentence Test Purpose

This test checks whether an image kept in `VK_IMAGE_LAYOUT_GENERAL` supports the selected ASTC transfer path, shader visibility dependency, input-attachment read path, or multisample attachment arrangement and produces the expected output.

## Background Knowledge

### General image layout and synchronization

`VK_IMAGE_LAYOUT_GENERAL` is a legal layout for the image uses exercised here, but it does not provide ordering or memory visibility on its own. A barrier can retain `GENERAL` as both old and new layout while establishing the execution and access dependency required by the next operation.

Why it matters here:
- The tests separate layout choice from dependency semantics by retaining `GENERAL` across transfers, shader reads and writes, attachment access, and copies.
- A same-layout image barrier has a synchronization role even when it makes no layout transition.

### Input attachments and dynamic rendering local read

An input attachment lets a fragment shader read an attachment associated with the current rendering operation. `VK_KHR_dynamic_rendering_local_read` supplies the dynamic-rendering mechanism used by the test to map color attachments to input-attachment indices.

Why it matters here:
- The input-attachment cases compare `subpassLoad` with a sampled read of the same image.
- The render-pass and dynamic-rendering alternatives have different setup, but both must preserve the same two-pass data flow.

## One Concrete Example

`dEQP-VK.image.general_layout.memory_barrier.compute.write_read.storage_read_storage_write` uploads random `R32_SFLOAT` texels to a 128 by 128 image in `GENERAL`. A compute shader writes `x + y` through a storage-image declaration. A synchronization2 memory barrier makes that write available to a second compute shader, which reads the storage image and writes the value to a host-visible buffer. The test also copies the image to a separate host-visible buffer. Both outputs must contain `x + y` at every texel.

## End-to-End Test Flow

```text
[host] choose the test family and its registered parameters
[host] check the required extension, feature, format capability, or attachment limit
[host] create images, views, buffers, descriptors, render-pass or dynamic-rendering state, and generated programs
[host] transition the relevant images to VK_IMAGE_LAYOUT_GENERAL and upload or initialize input data
[device] perform the selected transfer, shader, attachment, or resolve operations while images remain in GENERAL
[device] execute the required same-layout memory or image barriers between dependent operations
[host] copy the observable image or shader result to host-visible memory, wait for completion, and compare it with the expected data
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `AstcSampleCase::initPrograms()` generates a fullscreen vertex shader and a fragment shader that samples a combined `sampler2D`.
- `MemoryBarrierCase::initPrograms()` generates compute and fragment write/read pairs. The read program selects `imageLoad` for storage reads or `texture` for sampled reads.
- `InputAttachmentCase::initPrograms()` generates the first read-and-divide pass and the second `subpassLoad` and invert pass. The first pass uses either `subpassInput` or `sampler2D`.
- `MsaaCase::initPrograms()` generates a vertex shader plus fragment shaders that write interpolated texture coordinates to one or to every selected color attachment.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| ASTC source image and combined sampler | yes | yes | transfer or host-copy writes; fragment shader samples | indirectly | Tests compressed-image transfer and sampling while the image remains in `GENERAL`. |
| ASTC source and output buffers | yes | yes | transfer reads/writes | yes | Preserve compressed bytes for copy-out checks and expose sampled pixels for comparison. |
| `R32_SFLOAT` image, storage/sampled descriptors, and output buffers | yes | yes | transfer initializes; shaders read/write; transfer copies | yes | Carry the synchronization2 barrier test's producer and consumer data. |
| Two `R8G8B8A8_UNORM` input-attachment images, descriptors, and readback buffer | yes | yes | transfer initializes; fragment shaders read/write | yes | Support the alternating two-pass attachment data flow. |
| MSAA, single-sample, optional separate MSAA/resolve images, and output buffers | yes | yes | graphics and resolve operations read/write | yes | Test attachment and resolve behavior across the selected attachment count. |

## What Is Checked

- ASTC sampled output is compared against the CTS decompression reference with a per-channel tolerance of `0.04`. `copy_from_image` and `host_copy_from_image` also compare the copied compressed bytes with the original bytes.
- Memory-barrier cases compare every float with `1e-6`. The expected image result is `x + y`; the consumer result is `x + y` for `write_read` and the uploaded random value for `read_write`.
- Input-attachment cases compare every output byte with `255 - input / 2`, allowing an error of one.
- MSAA cases compare every returned pixel of every observed attachment with the generated coordinate pattern, allowing two units in red and green while requiring blue zero and alpha 255.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `astc_sample`, `memory_barrier`, `input_attachment`, `msaa`

The test family is the primary behavioral axis because each value selects a different image-use correctness property. The deeper registered values choose the transfer form, stage/access ordering, attachment-read and rendering form, or attachment arrangement for that property.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `astc_sample` | ASTC image use in `GENERAL`, compressed transfer or host-image-copy handling, mutable alias view setup, fragment sampling, or decoded-output comparison. |
| `memory_barrier` | synchronization2 stage/access dependency, storage versus sampled image access, compute or fragment execution path, or transfer readback after shader work. |
| `input_attachment` | Attachment-local read semantics, selected execution/memory/image barrier path, sampled versus input-attachment descriptor path, render-pass setup, or dynamic-rendering local-read setup. |
| `msaa` | General-layout color attachment use, four-sample rendering, selected attachment routing, resolve handling for `different`, or per-attachment readback comparison. |

## Important Variations and Special Cases

- `memory_barrier` and the ASTC host-copy leaves are not registered in VulkanSC builds. Dynamic-rendering input-attachment leaves remain registered by this source, while their support callback requires the relevant dynamic-rendering extensions.
- `sample_alias` creates an ASTC sRGB image with mutable-format and block-texel-view-compatible flags, then samples it through an ASTC UNORM view.
- The memory-barrier matrix has two stages, two producer/consumer orders, and three access-pair names. The source supplies the read and write access masks directly to the synchronization2 barriers.
- The input-attachment matrix combines `input_attachment` or `sampled`, `execution`, `memory`, or `image`, and `render_pass` or `dynamic_rendering`.
- `msaa` registers `same` and `different` arrangements at attachment counts `4`, `8`, and `16`; support rejects a leaf when `maxColorAttachments` is smaller than its selected count.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| ASTC setup, execution, and validation | [`AstcSampleTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L239-L599) | Shows the compressed data, `GENERAL` barriers, copy variants, sampling pass, and comparisons. |
| ASTC support and generated shaders | [`AstcSampleCase`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L601-L665) | Defines extension/format gates and the generated fullscreen sampling programs. |
| Memory-barrier execution and validation | [`MemoryBarrierTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L690-L1063) | Shows image creation, synchronization2 barriers, shader selection, copyback, and float comparisons. |
| Input-attachment execution and programs | [`InputAttachmentTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1197-L1719), [`initPrograms()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1752-L1791) | Shows the two-pass alternatives and byte-level result check. |
| MSAA execution and programs | [`MsaaTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1812-L2237), [`initPrograms()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2266-L2300) | Shows attachment construction, resolution, and coordinate validation. |
| Registration matrix | [`createImageGeneralLayoutTests()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2304-L2435) | Defines every registered family and parameter dimension. |
| Image layouts and image barriers | [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc), [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Grounds `GENERAL` and dependency semantics. |
| Copy and attachment rules | [`copies.adoc`](../../../../vulkan-docs/src/chapters/copies.adoc), [`renderpass.adoc`](../../../../vulkan-docs/src/chapters/renderpass.adoc) | Grounds copy layouts and attachment/input-attachment usage. |

## Questions / Risk Points for User Audit

- Does test-family-level failure mapping give readers a useful first triage boundary before they inspect the deeper matrix values?
- Does the distinction between retaining `GENERAL` and establishing synchronization remain clear?
- Should the final page retain the compute storage-image walkthrough as the representative shader, or would an input-attachment walkthrough better serve its intended audience?
- Are the VulkanSC registration exclusions and extension-gated dynamic-rendering cases sufficiently explicit?

## Conversion Notes for Final Wiki Rewrite

- Keep only short prerequisite bullets for `GENERAL` layout synchronization and attachment-local reads.
- Use the four test families as the final page's primary behavioral axis; describe their lower matrices in the parameter table and family subsections.
- Copy the `### Failure Cause Mapping` table above unchanged into the final page.
- Use the compute `memory_barrier` storage-image write shader as one formal walkthrough. Its SPIR-V has been compiled, validated, and disassembled for the final page.
- Preserve the source mapping as a compact source appendix and move runtime detail into the execution section.
