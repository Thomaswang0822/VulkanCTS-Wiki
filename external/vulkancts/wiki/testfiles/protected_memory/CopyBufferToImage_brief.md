# Understanding Brief: Protected Buffer-to-Image Copy

## One-Sentence Test Purpose

This test checks whether protected transfer commands can fill a protected buffer and copy its complete contents into a protected image when the commands run directly in a primary command buffer or through a secondary command buffer.

## Background Knowledge

### Protected transfer resources

Protected memory is device-only memory that protected queue operations can access. The source buffer, destination image, command pool, and queue submission must use compatible protected states. The test enables protection for both resources and submits the work as a protected submission.

Why it matters here:
- The host cannot initialize or read the protected transfer resources through mapped memory.
- `vkCmdFillBuffer` initializes the source on the device, and the image validator checks the destination without copying protected contents to the host.

### Buffer-to-image addressing and synchronization

`vkCmdCopyBufferToImage` maps bytes from a buffer into image texels according to `VkBufferImageCopy`. A zero `bufferRowLength` and zero `bufferImageHeight` select tightly packed rows and slices based on the image extent. Barriers make the fill visible to the copy, transition the image to a transfer destination layout, and make the copied image visible to the validator.

Why it matters here:
- The 1,024-byte source buffer exactly covers the 8 x 8 `VK_FORMAT_R32G32B32A32_SFLOAT` image: 64 texels at 16 bytes per texel.
- Repeating one 32-bit float bit pattern across the buffer supplies the same value to all four components of every image texel.

## One Concrete Example

In static `copy_2`, the test takes the 32-bit representation of `1.0f`, repeats that word across the protected source buffer with `vkCmdFillBuffer`, and copies the tightly packed buffer into the protected 8 x 8 image. Each destination texel should become `(1.0, 1.0, 1.0, 1.0)`. The validator samples four coordinates and compares each sampled vector with that value using its `0.1` per-component threshold.

The `secondary` form records the fill, barriers, copy, and final image transition in a secondary command buffer. A primary command buffer executes it before protected queue submission.

## End-to-End Test Flow

```text
[host] choose one static or base-seed-dependent random floating-point fill value and its reference record
[host] require Vulkan 1.1, protected memory, and a protected queue
[host] create a 1,024-byte protected source buffer and an 8 x 8 protected VK_FORMAT_R32G32B32A32_SFLOAT image
[host] create a protected command pool and primary command buffer; allocate a secondary command buffer for the secondary form
[host] begin the selected recording target
[host] record a barrier that permits transfer writes to the source buffer
[device] vkCmdFillBuffer repeats the selected 32-bit word across the source buffer
[host] record a transfer-write to transfer-read buffer barrier
[host] transition the image from VK_IMAGE_LAYOUT_UNDEFINED to VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL
[device] vkCmdCopyBufferToImage copies one tightly packed 8 x 8 x 1 color region
[host] transition the image to VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL for validation
[host] close and execute the secondary command buffer when the selected form is secondary
[host] submit the primary command buffer as protected work and wait on a fence
[host] invoke the image validator with four coordinates and expected vectors
[device] the validator samples the destination and compares each result with a threshold of 0.1
[host] pass only when validation completes successfully
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The tested operation uses fixed-function transfer commands. `CopyBufferToImageTestCase::initPrograms()` registers the `ResetSSBO` and `ImageValidator` compute programs for result checking. These shaders do not fill the source buffer or perform the buffer-to-image copy.

The test generator creates six fixed cases and ten base-seed-dependent random cases for each command-buffer form. A random case generates one float in `[0, 1]`, uses its bit pattern as the fill word, and expects that float in every component at all four generated sample coordinates.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected source buffer | yes | yes, as a transfer resource | filled by `vkCmdFillBuffer`, read by `vkCmdCopyBufferToImage` | no | Holds the repeated 32-bit pattern copied into the image. |
| Protected destination image | yes | yes, as transfer destination and sampled image | written by the copy, sampled by validation | no | Contains the result of the tested transfer. |
| Host-visible reference uniform | yes | yes, as validator uniform data | read by the validator | initialized by host | Carries four sample coordinates and four expected vectors. |
| Protected helper buffer | yes | yes, as validator storage | reset and used by the validator error path | no direct host read | Converts a comparison mismatch into validation failure behavior. |
| Destination image view and sampler | yes | yes, in the validator descriptor set | used by the validator to sample the copied image | no | Exposes the destination in its final shader-readable layout. |

## What Is Checked

- The fixed-function path must repeat the selected 32-bit word across the source buffer and copy all 1,024 bytes into the image.
- `ImageValidator::validateImage()` samples four coordinates from the destination image.
- Each sampled `vec4` must be within `0.1` of the corresponding expected value in every component.
- A mismatch enters the validator's non-terminating `error()` loop because `helper.zero` was reset to zero. The validation submission then times out and returns failure.
- Successful completion of the validation submission produces the passing result. The test does not map either protected transfer resource for host inspection.

## Behavior Parameter Identification

> **Behavior parameter:** command-buffer type
>
> **Candidate values:** `primary`, `secondary`

The `static` and `random` intermediate nodes vary fill words and sample coordinates. The command-buffer type changes how the same transfer sequence is recorded and executed, so it is the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected primary-command-buffer recording or execution, buffer fill and synchronization, `vkCmdCopyBufferToImage`, image transition, or destination validation failed. |
| `secondary` | Protected secondary-command-buffer recording, inheritance, execution from the primary, buffer fill and synchronization, `vkCmdCopyBufferToImage`, image transition, or destination validation failed. |

Both values share the protected resources, transfer region, expected-value rule, queue submission, and validator. A failure can therefore come from shared transfer or validation behavior rather than the selected command-buffer form.

## Important Variations and Special Cases

- `static` has six cases with fill values `0.0`, `1.0`, `0.2`, `0.55`, `0.82`, and `0.96`.
- `random` has ten cases generated from the CTS base seed. Each generated float supplies both the buffer fill bits and all four expected vector components.
- `primary` records the complete transfer sequence directly in the primary command buffer.
- `secondary` records the sequence in a secondary command buffer with null render-pass and framebuffer inheritance, then executes it from the primary command buffer.
- Under Vulkan SC, secondary cases require `secondaryCommandBufferNullOrImagelessFramebuffer`.
- The format, image extent, subresource, buffer offset, and packing stay fixed. The matrix does not cover partial copies or padded buffer rows.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support checks and validator program setup | [`CopyBufferToImageTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L73-L113) | Requires protected support, checks the Vulkan SC secondary property, and initializes validator programs. |
| Protected resources and command-buffer selection | [`CopyBufferToImageTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L128-L170) | Creates the source buffer, destination image, and recording targets. |
| Buffer fill and transfer barriers | [`source buffer setup`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L172-L226) | Records the fill and establishes transfer read/write dependencies and the destination layout. |
| Copy region and final image transition | [`buffer-to-image copy`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L228-L269) | Defines the tightly packed full-image copy and makes the result shader-readable. |
| Protected submission and result decision | [`submit and validate`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L271-L291) | Executes the optional secondary command buffer, submits protected work, and invokes validation. |
| Static and random case generation | [`createCopyBufferToImageTests`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L294-L426) | Defines six static cases, ten random cases, and the `static` and `random` intermediate nodes. |
| Registered command-buffer forms | [`copy_buffer_to_image` factory](../../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L431-L438) | Registers `primary` and `secondary`. |
| Protected context requirements | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks Vulkan version, protected-memory support, and protected queue support. |
| Validator programs and threshold | [`ImageValidator::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the checking shaders, four samples, threshold, and error path. |
| Validator resources and submission | [`ImageValidator::validateImage`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Configures the reference uniform, protected helper buffer, sampled image, and completion-based result. |
| Buffer-to-image copy semantics | [`copies.adoc`](../../../../vulkan-docs/src/chapters/copies.adoc#L819-L1006) | Defines buffer-image addressing and `vkCmdCopyBufferToImage`. |
| Protected copy command rules | [`copy_buffer_to_image_command_buffer_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/copy_buffer_to_image_command_buffer_common.adoc) | Defines protected command-buffer compatibility for the source buffer and destination image. |

## Questions / Risk Points for User Audit

- Is the distinction between the fixed-function fill/copy operations and the validator shaders clear?
- Is command-buffer type the correct behavioral axis, with `static` and `random` treated as data dimensions?
- Is the exact 1,024-byte buffer-to-image size relationship explained clearly enough?
- Is it clear that four sampled coordinates validate the selected observations rather than independently checking every texel?
- Does the failure mapping avoid assigning a specific implementation cause without evidence from a failing run?

## Conversion Notes for Final Wiki Rewrite

- Distill protected resource compatibility and tightly packed buffer-image addressing into the final Background Knowledge section.
- Use `protected_memory.image.copy_buffer_to_image` with `primary` and `secondary` as direct children in the registration tree.
- Carry the command-buffer-type behavior axis and the `### Failure Cause Mapping` table into the final page unchanged.
- Keep Shader Analysis short. The tested `vkCmdFillBuffer` and `vkCmdCopyBufferToImage` operations are fixed-function commands; validator shaders are checking infrastructure, so no representative shader walkthrough belongs on this page.
- Put the fill, barriers, copy region, protected submission, and four-sample validator in Runtime Execution and Result Checking.
- Keep source links in the appendix and preserve exact registered identifiers.
