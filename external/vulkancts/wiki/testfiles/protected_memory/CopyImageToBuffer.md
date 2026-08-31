## Overview

**Core question:** Does a protected image-to-buffer transfer preserve cleared texels when the transfer is recorded in a primary or secondary command buffer?

- This page covers `protected_memory.buffer.copy_image_to_float_buffer`, implemented by [`vktProtectedMemCopyImageToBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L60-L405).
- Each test clears a protected 8 x 8 color image, copies the image into a protected buffer, and validates selected texels through a protected compute dispatch.
- The registered command-buffer families are `primary` and `secondary`. Each contains `static` and `random` cases, with an additional `_protected_access` variant in non-Vulkan-SC builds.
- The validator shaders are checking infrastructure. The tested operations are the fixed-function image clear, layout transitions, image-to-buffer copy, and protected command-buffer execution.

## Background Knowledge

- **Protected resources and queue operations.** Protected memory is device-visible but must not be visible to the host. Protected images and buffers must be used through protected operation paths, while protected command buffers require a protected-capable queue. The Vulkan protected-memory rules allow protected transfer operations to access protected memory and require protected data to remain hidden from the host. See [`Protected Memory`](../../../../vulkan-docs/src/chapters/memory.adoc#L5564-L5654).
- **Image-to-buffer copy regions.** `vkCmdCopyImageToBuffer` uses a `VkBufferImageCopy` region to select image subresources and define buffer addressing. Zero `bufferRowLength` and `bufferImageHeight` select tightly packed addressing for the copied extent. The source image layout passed to the command must match the layout used for the copy. See [`vkCmdCopyImageToBuffer`](../../../../vulkan-docs/src/chapters/copies.adoc#L1009-L1094).

## Registration Hierarchy

```text
protected_memory.buffer.copy_image_to_float_buffer
├── primary
└── secondary
```

`primary` and `secondary` are command-buffer families. Their `static` and `random` intermediate nodes and their test case leaves are described in `## Parameter Dimensions and Observed Values`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command-buffer family | `primary`, `secondary` | Chooses whether the clear, barriers, copy, and final transfer-to-compute barrier are recorded directly in the primary command buffer or first recorded in a secondary command buffer. | [`createCopyImageToFloatBufferTests()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L390-L405) |
| Input mode | `static`, `random` | Selects six fixed clear/reference datasets or ten deterministic-random clear values and texel positions. | [`createCopyImageToFloatBufferTests()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L303-L388) |
| Static case leaves | `copy_1` through `copy_6` | Selects one of six fixed clear values and four associated reference positions. | [`testData`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L303-L328) |
| Random case leaves | `copy_1` through `copy_10` | Selects a clear color from the test seed and four positions in the first 64 texel slots. | [`copyRandomTests`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L358-L388) |
| Pipeline access variant | no suffix, `_protected_access` | The suffixed cases request `VK_EXT_pipeline_protected_access` when creating the protected context. | [`createInstance()` and case generation](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L94-L105) |
| Image and copy geometry | `VK_FORMAT_R32G32B32B32_UINT` image, 8 x 8 x 1 extent, one color layer | Fixes the protected source image and the one-region transfer shape used by every case. | [`CopyImageToBufferTestInstance`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L126-L154), [`copyRegion`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L243-L261) |

## Behavior Parameters

The primary behavioral axis is the command-buffer family. Both values execute the same fixed-function transfer sequence; `secondary` adds secondary-command-buffer recording and execution to that sequence.

### primary: Transfer commands recorded directly

The test records the image barriers, clear, copy, and buffer barrier in the protected primary command buffer. This is the direct protected transfer path.

### secondary: Transfer commands recorded in a secondary command buffer

The test records the same sequence in a protected secondary command buffer, ends it, and executes it from the protected primary command buffer. This value checks that secondary recording and execution preserve the same protected transfer behavior.

## Shader Analysis

The image clear and image-to-buffer copy are fixed-function commands, so this page has no representative shader walkthrough. `BufferValidator` and `ResetSSBO` are protected compute shaders used only to validate the copied buffer and reset validator state. The source-reviewed no-walkthrough exception for `protected_memory/CopyImageToBuffer.md` is recorded in `.agents/skills/wiki-rewriter/scripts/walkthrough_exceptions.py`.

## Runtime Execution and Result Checking

- `CopyImageToBufferTestInstance` fixes the source image format to `VK_FORMAT_R32G32B32A32_UINT`, creates an 8 x 8 protected image with transfer source and destination usage, and creates a protected destination buffer sized for `BUFFER_SIZE * sizeof(uint32_t)`, or 256 uint32 components (64 `R32G32B32A32` texels).
- The command pool and the relevant command buffers use the protected queue family. For `secondary`, the test begins a protected secondary command buffer with empty render-pass and framebuffer inheritance fields, then executes it from the primary command buffer.
- The transfer sequence first changes the image layout from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL`, with a transfer-write destination access mask. It clears the color image with `vkCmdClearColorImage`. Although the image format is UINT, the source fills `VkClearColorValue.float32` and the validator reads the copied bits through an SFLOAT buffer view; this preserves the float bit patterns rather than performing a numeric UINT-to-float conversion. See [`testData` and random case construction](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L303-L386) and [`VkClearColorValue`](../../../../vulkan-docs/src/chapters/clears.adoc#L445-L470).
- A second image barrier changes the layout from `VK_IMAGE_LAYOUT_GENERAL` to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` and changes the access from transfer write to transfer read.
- One `VkBufferImageCopy` region selects color aspect, mip level `0`, base array layer `0`, and one layer. Its offset is `(0, 0, 0)`, its extent is `(8, 8, 1)`, and both buffer stride fields are zero, so the image data is tightly packed into the destination buffer.
- `vkCmdCopyImageToBuffer` writes the protected destination buffer. A buffer barrier then makes transfer writes visible to the compute shader stage through `VK_ACCESS_SHADER_READ_BIT`.
- The test submits the protected primary command buffer and waits on a fence. The validator creates a host-visible unprotected reference uniform, protected helper storage, and a buffer view over the protected destination buffer. It resets the helper state, dispatches `BufferValidator`, and waits up to one second for the protected validation submission.
- `BufferValidator` fetches four texels at the reference positions and compares them with the four expected `tcu::Vec4` values using an absolute per-component threshold of `0.1`. A successful validator submission returns true and produces a passing status. A fence timeout returns false and produces a failure status; another non-success wait result is passed to `VK_CHECK` and raises a test error rather than returning false. The host never maps the protected destination buffer.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Incorrect protected image clear, layout transition, image-to-buffer copy, transfer-to-compute synchronization, protected buffer access, or validator result. |
| `secondary` | Any primary-path cause, plus incorrect recording or execution of the protected secondary command buffer. |

Both command-buffer values also have default and `_protected_access` case-name variants. A failure in a `_protected_access` case can additionally indicate incorrect handling of `VK_EXT_pipeline_protected_access` support or pipeline access restrictions.

### Cause Analysis

#### Image clear, layout transition, or copy result

**Possible failure symptoms:** The validator reports a mismatch at one or more of the four selected positions, so the copied buffer does not contain the expected cleared value within the `0.1` threshold.

**Possible implementation causes:** The image clear may not produce the requested value, a layout or access transition may not make the transfer valid, or `vkCmdCopyImageToBuffer` may calculate the selected region incorrectly. The Vulkan copy-command rules define the source layout and region addressing; the test source shows the exact barriers and region passed to the command.

#### Transfer-to-compute synchronization or protected buffer access

**Possible failure symptoms:** The validator cannot reliably read the copied values, reports mismatches, times out, or returns a failed submission result.

**Possible implementation causes:** The transfer write may not become visible to the compute shader read, or the protected queue operation may mishandle access to the protected destination buffer. The source inserts a buffer barrier from `VK_ACCESS_TRANSFER_WRITE_BIT` to `VK_ACCESS_SHADER_READ_BIT` before dispatch. If the observed failure does not identify the failing stage, source-level investigation is needed.

#### Protected validator result

**Possible failure symptoms:** The test returns failure when `validateBuffer()` receives `VK_TIMEOUT`, even when no individual mismatch is exposed to the host. A different failed wait result is reported as a test error through `VK_CHECK`.

**Possible implementation causes:** The protected validation dispatch may time out, or a non-success fence-wait result may trigger the checked-error path. The validator uses a protected reset dispatch followed by a protected validation dispatch and reports a boolean only for the timeout path; the specific implementation cause requires source-level investigation.

#### Secondary command buffer recording or execution

**Possible failure symptoms:** A `secondary` case fails while the equivalent `primary` case passes, with a mismatch, timeout, or failed submission during the same validation sequence.

**Possible implementation causes:** The protected secondary command buffer may not preserve the recorded barriers, clear, copy, or buffer barrier when executed by the primary command buffer. Under Vulkan SC, the test also checks `secondaryCommandBufferNullOrImagelessFramebuffer` before allowing this path. The exact implementation cause requires investigation from the reported failure and command-buffer behavior.

#### Pipeline-protected access variant

**Possible failure symptoms:** A case whose name ends in `_protected_access` fails while the corresponding unsuffixed case passes.

**Possible implementation causes:** The device may not support the requested `VK_EXT_pipeline_protected_access` path, or pipeline protected-access restrictions may not match the protected command-buffer use. The test requests the extension during protected-context creation; the specific failure mechanism requires investigation if support checks do not reject the case.

## Case Pruning

### Requirement-based pruning

- `checkProtectedContextSupport(context, false, m_pipelineProtectedAccess)` rejects devices that do not support the protected context or the requested pipeline-protected-access variant.
- Secondary Vulkan SC cases require `secondaryCommandBufferNullOrImagelessFramebuffer` to be `VK_TRUE`. If that property is unavailable, the test reports `NotSupportedError` instead of executing the case.
- Non-Vulkan-SC builds include `_protected_access` cases only when the corresponding extension and feature support can be requested by the protected context.

### Design-based pruning

- The static matrix contains six fixed datasets. The random matrix contains ten cases. The test does not enumerate every possible clear value or texel-position combination.
- Every copy uses one full-image region, one color mip level, and one array layer. These fixed dimensions isolate protected image-to-buffer transfer behavior rather than testing region partitioning.
- Four texel positions are checked per case. Random positions are restricted to `0` through `MAX_POSITION - 1`, where `MAX_POSITION` is `64`, so each position fits within the validator's 64-texel (256-component) buffer.

## Key Takeaways

- The tested data path is protected from image clear through image-to-buffer copy and protected compute validation. The host sees only the final test status.
- `primary` and `secondary` use the same transfer commands. The secondary family adds the requirement that protected secondary recording and execution preserve that sequence.
- Static and random cases vary the clear value and selected texel positions, while the image size, copy region, and validator format remain fixed.
- The buffer validator's shaders check the transfer result. They are not the behavior being compared between the two command-buffer families.
- A mismatch points to the clear, image layout transition, copy, synchronization, protected access, or validation path described in `## Failure Meaning`; it does not by itself identify one implementation layer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Case data and hierarchy construction | [`createCopyImageToFloatBufferTests()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L303-L405) | Registers `copy_image_to_float_buffer`, `primary`, `secondary`, `static`, `random`, and all case-name variants. |
| Support and instance setup | [`CopyImageToBufferTestCase::checkSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L94-L115), [`createInstance()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L76-L105) | Checks protected context support and requests `VK_EXT_pipeline_protected_access` for suffixed cases. |
| Protected resources | [`CopyImageToBufferTestInstance::iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L139-L161) | Creates the protected image, destination buffer, command pool, and command buffers. |
| Clear, barriers, and copy | [`iterate()` transfer commands](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L182-L278) | Records the image layout transitions, clear, `vkCmdCopyImageToBuffer`, and transfer-to-compute barrier. |
| Submission and result | [`iterate()` submission and validation](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L281-L300) | Executes the protected command buffer, submits it, and invokes the validator. |
| Validator shader generation | [`initBufferValidatorPrograms()`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.cpp#L86-L193) | Generates `ResetSSBO` and `BufferValidator` for protected-side checking. |
| Validator resources and dispatches | [`BufferValidator::validateBuffer()`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.hpp#L181-L325) | Creates the buffer view and descriptors, resets helper state, dispatches validation, and checks submission status. |
| Protected utility contracts | [`vktProtectedMemUtils.hpp`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.hpp#L51-L109) | Defines protection modes, command-buffer types, protected submission, and resource helpers used by the test. |
| Image-to-buffer specification | [`vkCmdCopyImageToBuffer`](../../../../vulkan-docs/src/chapters/copies.adoc#L1009-L1094) | Defines copy-region addressing, source layout, and command valid usage. |
| Protected-memory specification | [`Protected Memory`](../../../../vulkan-docs/src/chapters/memory.adoc#L5564-L5654) | Defines protected resources, queue operations, transfer-stage access, and host-visibility guarantees. |
