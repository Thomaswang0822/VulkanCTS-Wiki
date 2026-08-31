# Understanding Brief: Protected Image Copy

## One-Sentence Test Purpose

This test checks whether a protected `vkCmdCopyImage` operation copies a complete protected color image into a second protected image and preserves the source values when recorded in either a primary or secondary command buffer.

## Background Knowledge

### Protected resources and command buffers

A protected command buffer and the resources it accesses must use compatible protection states. The protected-memory feature and a queue family with `VK_QUEUE_PROTECTED_BIT` allow the test to submit work that accesses protected images. This page uses protected images for both sides of the copy and records the copy either directly in a primary command buffer or in a secondary command buffer that the primary executes.

Why it matters here:
- The source and destination images must be created with protected memory and used from protected command-buffer work.
- The secondary case adds command-buffer inheritance and execution without changing the image-copy operation itself.

### Image transfer state

`vkCmdCopyImage` reads the source image in the supplied source layout and writes the destination image in the supplied destination layout. Image memory barriers establish the layouts and access masks around the clear, copy, and later read. The copy region identifies one color aspect, one mip level, one array layer, zero offsets, and the full image extent.

Why it matters here:
- The source clear must become a transfer read before the copy.
- The destination must become a transfer write target before the copy and a shader-readable image before validation.

## One Concrete Example

A representative static case clears a protected `VK_FORMAT_R8G8B8A8_UNORM` source image to red, copies its 128 by 128 color subresource to a second protected image, and validates four sampled coordinates in the destination. Each reference value for that case is red, so a successful copy makes all four sampled values match the expected color within the validator's threshold.

The secondary variant records the same barriers, clear, copy, and final barrier in a secondary command buffer. The primary command buffer executes that secondary command buffer before submission.

## End-to-End Test Flow

```text
[host] choose a static or base-seed-dependent random clear color and four reference coordinates/values
[host] require Vulkan 1.1, protected memory, and a protected queue
[host] create protected 128 x 128 source and destination images with VK_FORMAT_R8G8B8A8_UNORM
[host] create a protected command pool and primary command buffer; for the secondary variant also allocate a secondary command buffer
[host] begin the selected recording target and transition the source image from VK_IMAGE_LAYOUT_UNDEFINED to VK_IMAGE_LAYOUT_GENERAL
[device] clear the source image in VK_IMAGE_LAYOUT_GENERAL
[host] add a transfer barrier that makes the source clear available as VK_ACCESS_TRANSFER_READ_BIT
[host] transition the destination image from VK_IMAGE_LAYOUT_UNDEFINED to VK_IMAGE_LAYOUT_GENERAL with transfer-write access
[host] record vkCmdCopyImage for the full color subresource and 128 x 128 x 1 extent
[host] transition the destination image to VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL for validation
[host] close and execute the secondary command buffer when the selected command-buffer type is secondary
[host] close the primary command buffer and submit it to the protected queue, waiting on a fence
[host] run the image validator against four reference coordinates and values
[host] pass the test only when all four sampled values are within the validator threshold
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The copy test itself does not generate a shader that performs the tested operation. `CopyImageTestCase::initPrograms()` asks `ImageValidator` to register the `ResetSSBO` and `ImageValidator` compute programs used after the copy. Those programs support result checking; they are not part of the copy operation.

The static matrix contains seven fixed clear colors and reference records. The random matrix contains ten cases. Each random case uses the test command-line base seed to generate a clear color and four reference vectors, then expects the clear color at all four validation coordinates after the copy.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected source `colorImageSrc` | yes | yes, as a transfer source | cleared and read by `vkCmdCopyImage` | no | Holds the value that the copy must preserve. |
| Protected destination `colorImage` | yes | yes, as a transfer destination and sampled image | written by `vkCmdCopyImage`, sampled by validation | no | Shows whether the protected image copy produced the expected pixels. |
| Host-visible reference uniform | yes | yes, as a validator uniform buffer | read by the validator compute shader | initialized by host | Carries four reference coordinates and four expected `tcu::Vec4` values. It is intentionally unprotected. |
| Protected helper buffer | yes | yes, as a validator storage buffer | reset and atomically incremented by the validator | no direct host read in this helper | Supplies the validator's zero control value and error counter. |
| Image view and sampler | yes | yes, in the validator descriptor set | used to sample the destination image | no | Presents the final destination layout to the validator. |

Both images are 2D, one mip level, one array layer, and use `VK_IMAGE_ASPECT_COLOR_BIT`. The source has `VK_IMAGE_USAGE_TRANSFER_SRC_BIT` in addition to sampled and transfer-destination usage. The destination has sampled and transfer-destination usage.

## What Is Checked

- `ImageValidator::validateImage()` dispatches one validator workgroup and samples four coordinates from the destination image.
- Each sampled `vec4` is compared with its corresponding reference value using an absolute per-component threshold of `0.1`.
- A mismatch enters the validator's `error()` path. Because `helper.zero` is reset to `0`, that path does not advance its loop and the validation submission can time out.
- The test returns pass when validation submission completes successfully. A timeout while submitting validation is treated as failure; other queue errors are checked as Vulkan errors.

## Behavior Parameter Identification

> **Behavior parameter:** command-buffer type
>
> **Candidate values:** `primary`, `secondary`

The `static` versus `random` intermediate nodes vary the input and expected data, but both use the same image-copy mechanism. The command-buffer type changes how that mechanism is recorded and executed, so it is the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected primary-command-buffer recording or execution, image state transitions, `vkCmdCopyImage`, or destination validation failed. |
| `secondary` | Protected secondary-command-buffer recording, inheritance, execution from the primary, image state transitions, `vkCmdCopyImage`, or destination validation failed. |

Both values share the same protected image setup, copy region, queue submission, validator, and expected-value rules. A failure in either value can therefore indicate a common image-copy or validation problem rather than a command-buffer-specific problem.

## Important Variations and Special Cases

- `static` contains seven fixed cases. Its expected values exercise distinct RGBA clear values, including fully and partially populated channels.
- `random` contains ten cases generated from the CTS base seed. The clear color and expected values are generated together, so the expected destination is the chosen clear color at each checked coordinate.
- `primary` records the copy directly in the primary command buffer.
- `secondary` records the copy in a secondary command buffer with a `VkCommandBufferInheritanceInfo` that has no render pass or framebuffer, then executes it from the primary command buffer.
- Under Vulkan SC, the secondary cases require `secondaryCommandBufferNullOrImagelessFramebuffer`; the test skips them when that property is `VK_FALSE`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test case support checks and program initialization | [`CopyImageTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L72-L111) | Requires protected context support and initializes the validator programs. |
| Protected image creation and command-buffer selection | [`CopyImageTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L125-L167) | Defines the two protected images and primary/secondary recording targets. |
| Barriers, clear, and image copy | [`vkCmdCopyImage` recording](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L169-L300) | Establishes source and destination state and records the full-image copy. |
| Submission and final validation | [`submit and validateImage`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L303-L325) | Shows the protected submission and pass/fail decision. |
| Static and random matrix construction | [`createCopyImageTests`](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L328-L462) | Defines seven static cases, ten random cases, and the registered intermediate nodes. |
| Primary and secondary registration | [`createCopyImageTests` overload](../../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L467-L474) | Adds the `primary` and `secondary` test families under `copy`. |
| Protected context requirements | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Grounds the Vulkan version, feature, and protected queue requirements. |
| Command-buffer names | [`getCmdBufferTypeStr`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L575-L588) | Maps the command-buffer enum values to `primary` and `secondary`. |
| Image validation shader and comparison | [`ImageValidator::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Shows the validator's sampler, references, threshold, and error path. |
| Validator execution and descriptors | [`ImageValidator::validateImage`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Shows protected helper resources, destination sampling, and compute validation. |
| Copy command validity | [`copy_image_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/copy_image_common.adoc) | Grounds nonzero extents, subresource, offset, and image-copy constraints. |
| Protected command-buffer validity | [`copy_image_command_buffer_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/copy_image_command_buffer_common.adoc) | Grounds compatible protected and unprotected image use with protected commands. |

## Questions / Risk Points for User Audit

- Is the distinction between the fixed-function copy and the validator's compute shader clear?
- Is the command-buffer type the right primary behavioral axis, with `static` and `random` treated as input dimensions?
- Does the description of the secondary command buffer make its null render-pass and framebuffer inheritance clear without implying a render pass?
- Are the protected queue and Vulkan SC secondary-command-buffer requirements scoped correctly?
- Should the final page mention the validator's internal error counter even though the public result is returned through `validateImage()`?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to protected resource compatibility and image transfer state; move the concrete red example into the behavior or runtime explanation.
- Use `protected_memory.image.copy` with direct children `primary` and `secondary` in the registration tree. Explain `static` and `random` in the parameter section rather than expanding the parseable tree.
- Carry the command-buffer-type axis and the `### Failure Cause Mapping` table into the final page unchanged.
- Keep `## Shader Analysis` concise. `vkCmdCopyImage` is fixed-function, and `ResetSSBO` plus `ImageValidator` are validation infrastructure, so no representative shader walkthrough is needed.
- Put the barrier sequence, protected image roles, and validator threshold in `## Runtime Execution and Result Checking` and `## Failure Meaning`; keep source navigation in the appendix.
- Preserve the exact registered identifiers and source links. Do not claim that the host directly reads the helper buffer when the inspected validator returns through its protected submission path.
