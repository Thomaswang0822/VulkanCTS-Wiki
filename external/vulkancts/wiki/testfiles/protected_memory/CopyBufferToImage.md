## Overview

**Core question:** Can protected transfer commands fill a protected buffer and copy its exact contents into a protected image through either command-buffer form?

- This page covers `vktProtectedMemCopyBufferToImageTests.cpp`, which implements the `protected_memory.image.copy_buffer_to_image` test family.
- Each case fills a 1,024-byte protected buffer with one repeated 32-bit word, copies it into an 8 x 8 `VK_FORMAT_R32G32B32A32_SFLOAT` protected image, and validates four sampled coordinates.
- The registered `primary` and `secondary` values choose direct recording or secondary command-buffer execution. Each contains `static` and `random` intermediate nodes.
- The tested work is the fixed-function `vkCmdFillBuffer` and `vkCmdCopyBufferToImage` sequence. Compute shaders only provide protected image validation.

## Background Knowledge

- Protected memory is device-only memory that protected queue operations can access. The source buffer, destination image, command pool, and submission therefore use compatible protected states.
- `vkCmdFillBuffer` repeats one 4-byte word across its destination range. Here that word is the bit representation of a float, so each `R32G32B32A32_SFLOAT` texel receives four copies of the selected value.
- `VkBufferImageCopy` controls buffer-to-image addressing. Zero `bufferRowLength` and `bufferImageHeight` select tight packing based on the 8 x 8 x 1 image extent.
- Barriers make the buffer fill visible to the copy, transition the image for transfer writes, and make the copied image visible to shader reads during validation.

## Registration Hierarchy

```text
protected_memory.image.copy_buffer_to_image
├── primary
└── secondary
```

The two test families each contain `static` and `random` intermediate nodes. `static` contains `copy_1` through `copy_6`; `random` contains `copy_1` through `copy_10`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command-buffer type | `primary`, `secondary` | Selects direct primary recording or recording in a secondary command buffer executed by the primary. | [`copy_buffer_to_image` factory](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L431-L438) |
| Input set | `static`, `random` | Selects six fixed records or ten records generated from the command-line base seed. | [`createCopyBufferToImageTests`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L294-L426) |
| Static test case leaf | `copy_1` through `copy_6` | Selects fill values `0.0`, `1.0`, `0.2`, `0.55`, `0.82`, or `0.96`, with four fixed sample coordinates and matching expected vectors. | [`testData`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L294-L383) |
| Random test case leaf | `copy_1` through `copy_10` | Selects one generated float and four generated sample coordinates. All expected components equal the generated float. | [`random` case construction](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L395-L419) |
| Resource shape | 1,024-byte buffer; 8 x 8 x 1 image; `VK_FORMAT_R32G32B32A32_SFLOAT` | The buffer exactly covers 64 texels at 16 bytes per texel, so the copy consumes the complete buffer and image. | [`resource creation`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L51-L56), [`iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L136-L144) |
| Copy region | offset `0`, row length `0`, image height `0`, color aspect, mip `0`, layer `0`, one layer | Selects one tightly packed full-image copy with no row or slice padding. | [`VkBufferImageCopy`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L228-L246) |

## Behavior Parameters

The primary behavioral axis is command-buffer type. The data branches change the fill value and validation coordinates, but they use the same fixed-function transfer sequence.

### primary: direct primary recording

The test records the source-buffer barriers, `vkCmdFillBuffer`, image transition, `vkCmdCopyBufferToImage`, and final image transition directly in the primary command buffer. It submits that command buffer as protected work.

### secondary: executed secondary recording

The test records the same sequence in a secondary command buffer. Its inheritance information has no render pass or framebuffer. The primary command buffer executes the secondary command buffer before protected submission, which checks the same protected transfer through secondary command-buffer execution.

## Shader Analysis

`vkCmdFillBuffer` and `vkCmdCopyBufferToImage` are fixed-function transfer commands, so this test has no test-core shader to walk through. `ImageValidator` generates `ResetSSBO` and `ImageValidator` compute programs only to check the copied protected image. They do not implement either tested transfer operation.

## Runtime Execution and Result Checking

- `CopyBufferToImageTestCase::checkSupport()` requires Vulkan 1.1, protected-memory support, and a protected queue. Under Vulkan SC, `secondary` also requires `secondaryCommandBufferNullOrImagelessFramebuffer`.
- The test creates an 8 x 8 protected `VK_FORMAT_R32G32B32A32_SFLOAT` image with sampled and transfer-destination usage. It also creates a 1,024-byte protected buffer with uniform-texel, transfer-source, and transfer-destination usage.
- A protected command pool supplies primary and secondary command buffers. The selected command-buffer type determines the target for the complete transfer sequence.
- A buffer barrier permits transfer writes, then `vkCmdFillBuffer` repeats the selected 32-bit float representation across the source buffer.
- A second buffer barrier changes the source dependency from `VK_ACCESS_TRANSFER_WRITE_BIT` to `VK_ACCESS_TRANSFER_READ_BIT`.
- An image barrier changes the destination from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` with transfer-write access.
- `vkCmdCopyBufferToImage` copies one color subresource from offset zero. The zero row-length and image-height fields select tight packing, and the extent covers the full 8 x 8 x 1 image.
- A final barrier changes the destination to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` and makes transfer writes visible to compute-shader reads.
- For `secondary`, the test ends the secondary command buffer and records `vkCmdExecuteCommands` in the primary. It then submits the primary command buffer as protected work and waits on a fence.
- `ImageValidator::validateImage()` receives four coordinates and expected values through a host-visible uniform buffer. A compute shader samples the protected image and compares each component with an absolute threshold of `0.1`.
- The validator resets `helper.zero` to `0`. A mismatch enters `error()`, whose loop cannot advance with that value, so the validation submission times out and returns failure. Successful completion returns pass. Neither protected transfer resource is mapped for host inspection.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected primary-command-buffer recording or execution, buffer fill and synchronization, `vkCmdCopyBufferToImage`, image transition, or destination validation failed. |
| `secondary` | Protected secondary-command-buffer recording, inheritance, execution from the primary, buffer fill and synchronization, `vkCmdCopyBufferToImage`, image transition, or destination validation failed. |

Both values share the protected resources, transfer region, expected-value rule, queue submission, and validator. A failure can therefore come from shared transfer or validation behavior rather than the selected command-buffer form.

### Cause Analysis

#### Protected fill, synchronization, or buffer-to-image copy

**Possible failure symptoms:** The validator does not complete, or one of its four sampled destination vectors differs from the selected fill value by more than `0.1` in at least one component. Static and random cases produce the same symptom because each derives its expected vectors from the fill word.

**Possible implementation causes:** The fill may not repeat the 4-byte pattern across the protected source, the buffer barrier may not make those writes available to transfer reads, the image barrier may not establish the destination layout and access dependency, or the copy may address or transfer the tightly packed region incorrectly. Vulkan requires transfer-source usage on the buffer, transfer-destination usage and a compatible layout on the image, and enough source storage for the addressed region. The test supplies those conditions. A failing case needs source-level or driver investigation to identify which operation broke.

#### Command-buffer recording and execution form

**Possible failure symptoms:** A `primary` failure occurs on the direct recording path. A `secondary` failure can also arise while executing the recorded secondary command buffer from the primary. Both paths eventually produce a validation timeout or a non-passing result when the destination samples do not match.

**Possible implementation causes:** A secondary-only failure may involve secondary command-buffer inheritance, protected secondary execution, or `vkCmdExecuteCommands`. A primary-only failure points away from that extra execution layer but does not identify a specific component. The failing command-buffer form and validation log must guide further investigation.

#### Destination validation

**Possible failure symptoms:** The protected validation submission times out after any sampled component exceeds the `0.1` threshold, or validation fails to complete for another checked queue error. The validator checks four coordinates, so the result does not establish that it compared every destination texel independently.

**Possible implementation causes:** A mismatch can come from the tested transfer path, a wrong image layout or access dependency before sampling, an incorrect image view or sampler path, wrong reference data, or validator execution. The source exposes the comparison symptom but cannot distinguish these causes without a failing run.

## Case Pruning

### Requirement-based pruning

- `checkProtectedContextSupport()` skips cases below Vulkan 1.1 or without protected-memory and protected-queue support.
- Under Vulkan SC, `secondary` cases are skipped when `secondaryCommandBufferNullOrImagelessFramebuffer` is `VK_FALSE`.

### Design-based pruning

- The format stays `VK_FORMAT_R32G32B32A32_SFLOAT`, the image stays 8 x 8, and the copy always covers one complete color subresource. The test does not vary mip levels, array layers, offsets, partial extents, row padding, or slice padding.
- Six static cases and ten base-seed-dependent random cases vary the data without changing the fill or copy mechanism.
- Validation samples four coordinates rather than comparing every texel independently. This is the selected protected-image validation design.

## Key Takeaways

- The test checks fixed-function protected buffer fill and buffer-to-image copy, not shader-based copying.
- The 1,024-byte source exactly matches the 8 x 8 four-component 32-bit-float destination, and tight packing maps the repeated word across every image component.
- `primary` and `secondary` are the behavior values because they select two command-buffer execution forms for the same transfer sequence.
- The validator samples four coordinates after transfer writes become visible in `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`.
- Failure interpretation must cover the shared protected transfer and validator paths as well as the selected command-buffer form.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support checks and validator setup | [`CopyBufferToImageTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L73-L113) | Requires protected support, checks the Vulkan SC secondary property, and initializes validator programs. |
| Protected resource and command-buffer setup | [`CopyBufferToImageTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L128-L170) | Creates the exact buffer and image and selects the recording target. |
| Fill and pre-copy barriers | [`source buffer and destination setup`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L172-L226) | Records `vkCmdFillBuffer`, makes it readable by transfer, and transitions the image. |
| Copy region and final transition | [`vkCmdCopyBufferToImage` recording](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L228-L269) | Defines the tightly packed full-image copy and shader-readable final layout. |
| Protected submission and validation | [`submit and validate`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L271-L291) | Executes the optional secondary buffer, submits protected work, and decides pass or fail. |
| Static and random matrix | [`createCopyBufferToImageTests`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L294-L426) | Defines six static cases, ten random cases, and their reference records. |
| Registered command-buffer forms | [`copy_buffer_to_image` factory](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L431-L438) | Registers `primary` and `secondary`. |
| Protected context requirements | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks Vulkan version, protected memory, and protected queue support. |
| Protected resource creation and submission | [`protected-memory helpers`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L380), [`queueSubmit`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L496) | Applies protected create flags and memory requirements and attaches `VkProtectedSubmitInfo`. |
| Validator shader and threshold | [`ImageValidator::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the four-sample comparison and mismatch path. |
| Validator resources and execution | [`ImageValidator::validateImage`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Configures references, the protected helper buffer, sampled destination, and completion-based result. |
| Buffer fill semantics | [`clears.adoc`](../../../../vulkan-docs/src/chapters/clears.adoc#L661-L687) | Defines the repeated 4-byte fill word and transfer-operation classification. |
| Buffer-to-image addressing and command | [`copies.adoc`](../../../../vulkan-docs/src/chapters/copies.adoc#L819-L1006) | Defines tight buffer-image addressing and `vkCmdCopyBufferToImage`. |
| Protected command-buffer compatibility | [`copy_buffer_to_image_command_buffer_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/copy_buffer_to_image_command_buffer_common.adoc) | Defines protected source-buffer and destination-image access rules. |
