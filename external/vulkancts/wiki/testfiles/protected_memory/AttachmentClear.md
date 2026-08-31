## Overview

**Core question:** Does `vkCmdClearAttachments` replace the contents of a protected color attachment through both primary and secondary protected command-buffer paths?

- This page covers the `protected_memory.attachment.clear_op` test family implemented in [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp).
- Each case clears a protected `VK_FORMAT_R8G8B8A8_UNORM` framebuffer attachment during a render pass. The render pass starts with another color so the validator can detect a missing clear.
- The `primary` and `secondary` paths change where the clear command is recorded. Both paths submit the work through a protected queue and validate four image coordinates with shared compute infrastructure.
- Each command-buffer path contains seven fixed clear colors and ten colors generated from the CTS base seed.

## Background Knowledge

- **Protected memory and submissions.** Memory with `VK_MEMORY_PROPERTY_PROTECTED_BIT` permits device access through protected queue operations and cannot also be host visible. Protected command buffers come from a command pool created with `VK_COMMAND_POOL_CREATE_PROTECTED_BIT`, and protected submissions set `VkProtectedSubmitInfo::protectedSubmit`.
- **Attachment clears inside a render pass.** `vkCmdClearAttachments` clears selected regions of framebuffer attachments during a render pass instance. A color clear executes as a color-attachment write at the color attachment output stage and does not depend on bound graphics pipeline state.
- **Primary and secondary command buffers.** A primary command buffer can contain the clear inline. A secondary command buffer records the same command with render-pass inheritance, then a primary command buffer executes it within the active render pass.

## Registration Hierarchy

```text
protected_memory.attachment.clear_op
├── primary
└── secondary
```

Both direct children contain `static` and `random` intermediate nodes. The test case leaves below those nodes are listed in the parameter table.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command-buffer path | `primary`, `secondary` | Selects whether `vkCmdClearAttachments` is recorded inline in the submitted primary command buffer or in an inherited secondary command buffer executed by the primary. | [execution](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L134-L216), [registration](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L395-L411) |
| Data source | `static`, `random` | Separates seven fixed clear colors from ten clear colors generated with the CTS base seed. | [case generation](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L264-L398) |
| Static test case leaf | `clear_1` through `clear_7` | Covers red, green, blue, black with alpha one, a repeated red case, red with alpha zero, and `(0.1, 0.2, 0.3, 0.0)`. | [static data](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L264-L372) |
| Random test case leaf | `clear_1` through `clear_10` | Gives each generated clear value its own registered case while retaining deterministic generation from the command-line base seed. | [random registration](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L374-L393) |
| Target image | `128 x 128`, `VK_FORMAT_R8G8B8A8_UNORM`, one mip level, one layer | Keeps the resource shape fixed while command-buffer placement and clear values vary. | [image setup](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L49-L53), [image creation](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L123-L131) |
| Clear region | color attachment `0`, full render area, layer `0` | Applies the requested value to the complete attachment region used by the case. | [`vkCmdClearAttachments` arguments](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L195-L208) |

The mustpass list contains 34 paths: 17 under `primary` and the same 17 under `secondary` [protected-memory.txt](../../../mustpass/main/vk-default/protected-memory.txt#L1-L34).

## Behavior Parameters

The primary behavioral axis is the command-buffer path represented by the intermediate node under the `clear_op` test family. It changes how the attachment clear reaches the active render pass.

### `primary` - inline clear recording

The primary path begins the render pass with `VK_SUBPASS_CONTENTS_INLINE` and records `vkCmdClearAttachments` in the primary protected command buffer. The same command buffer contains both image barriers, owns the render pass, and is submitted to the protected queue [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L141-L177), [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L195-L245).

### `secondary` - inherited clear recording

The secondary path begins the render pass with `VK_SUBPASS_CONTENTS_SECONDARY_COMMAND_BUFFERS`. It records the clear in a protected secondary command buffer whose inheritance information names the active render pass, subpass `0`, and framebuffer. The primary then calls `vkCmdExecuteCommands` before ending the render pass [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L173-L193), [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L195-L216).

The `static` and `random` intermediate nodes change the source of the clear value. They use the same protected image, clear region, synchronization, submission, and validator path.

## Shader Analysis

The behavior under test is the fixed-function `vkCmdClearAttachments` operation, so this page has no representative shader walkthrough. The clear does not use a graphics pipeline or a test shader. The shared `ImageValidator` generates two compute shaders to reset validator state and sample the cleared image, but those shaders are checking infrastructure rather than the implementation of the attachment clear [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115).

## Runtime Execution and Result Checking

- The host creates a protected `128 x 128` color image with color-attachment and sampled-image usage, then creates its view, render pass, and framebuffer [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L123-L132).
- A protected command pool provides one primary and one secondary command buffer. The case selects either buffer as the target for `vkCmdClearAttachments` [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L134-L140), [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525).
- The primary command buffer transitions the image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`. The render pass begins with a component-wise zero-or-one color chosen to differ from the requested clear color [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L141-L177).
- The selected target command buffer records one `vkCmdClearAttachments` call for color attachment `0`, the full render area, and its single layer. The secondary path executes that command buffer from the primary [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L179-L216).
- After the render pass, a color-attachment-write to shader-read barrier transitions the image to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L218-L239).
- The host submits the primary command buffer with protected submission enabled and waits on a fence [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L241-L245), [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495).
- `ImageValidator` binds the protected image as a combined image sampler, a protected helper storage buffer, and a host-initialized reference uniform buffer. Its compute shader samples four coordinates and accepts a per-component difference of at most `0.1` [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L90), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L210).
- A mismatched sample enters the validator's atomic loop. The validator treats a one-second queue timeout as failure; completion is success [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L71-L89), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L236-L263).

| Resource | Protection and binding | Device access | Validation role |
|----------|------------------------|---------------|-----------------|
| Color image | Protected image and memory; framebuffer color attachment and validator sampled image | Written by the attachment clear, then sampled by compute | Holds the clear result without host mapping or image copyback. |
| Primary command buffer | Allocated from a protected command pool and submitted as protected work | Carries barriers, render-pass control, and either the clear or secondary execution | Exercises the inline path and submits both behavior variants. |
| Secondary command buffer | Allocated from the same protected command pool with render-pass inheritance | Records the clear for the `secondary` path | Tests clear execution through a secondary command buffer. |
| Reference uniform buffer | Unprotected host-visible buffer at validator binding `2` | Read by validation compute | Supplies four coordinates and the expected clear color. |
| Helper storage buffer | Protected buffer at validator binding `1` | Reset and updated by validation compute | Converts a color mismatch into a validator timeout. |

The test passes when validation completes. It fails when the validator times out after finding a sampled value outside the threshold; an API error during protected submission is propagated before validation instead. This is a four-coordinate check, not a host scan of every pixel.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected attachment clearing or result visibility fails when `vkCmdClearAttachments` is recorded inline in the primary command buffer. |
| `secondary` | Protected attachment clearing, secondary command-buffer inheritance or execution, or result visibility fails when the clear is recorded in a secondary command buffer. |

Failures in both values can also come from shared protected image creation, protected submission, color conversion, synchronization, or validator infrastructure.

### Cause Analysis

#### Protected attachment clearing or result visibility on the primary path

**Possible failure symptoms:** At least one of the four validator samples differs from the expected clear color by more than `0.1` in a component, so the validation submission times out and `iterate()` returns a failing status [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L256-L261), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L77-L89).

**Possible implementation causes:** The implementation may fail to apply the full-area color-attachment write from `vkCmdClearAttachments` to protected image memory, may use an incorrect conversion from the floating-point clear value to `VK_FORMAT_R8G8B8A8_UNORM`, or may fail to make color-attachment writes visible to the later compute sample despite the recorded layout transition and memory barrier. Vulkan defines this command as a color-attachment write in the color attachment output stage [clears.adoc](../../../../vulkan-docs/src/chapters/clears.adoc#L275-L285).

#### Secondary command-buffer inheritance or execution

**Possible failure symptoms:** `secondary` cases time out in validation while equivalent `primary` cases pass, or protected submission reports an API error before validation. The expected color is absent at one or more sampled coordinates after the primary executes the secondary command buffer.

**Possible implementation causes:** The implementation may mishandle render-pass continuation state inherited by the secondary command buffer, fail to execute its clear command in the active subpass, or lose the clear's color-attachment write before the primary ends the render pass. Source inspection confirms that the inheritance structure names the same render pass, subpass, and framebuffer used by the primary [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L179-L193).

#### Shared protected resource, submission, or validator path

**Possible failure symptoms:** Both command-buffer paths fail across fixed and random colors, protected queue submission returns an error, or the validator times out without distinguishing clear-command placement.

**Possible implementation causes:** The shared protected image allocation, protected command pool, protected queue submission, color-to-sampled-image synchronization, or validator compute path may be faulty. Because the validator is part of the observed result path, a shared failure does not by itself identify `vkCmdClearAttachments` as the source. Source-level investigation must separate clear execution from protected validation infrastructure.

## Case Pruning

### Requirement-based pruning

- `checkProtectedContextSupport` rejects the case when the API version is below Vulkan 1.1, `protectedMemory` is false, or no protected queue is available [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L80-L127).
- Context creation needs a queue family that supports graphics, compute, and protected operations because the case performs an attachment clear and compute validation [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L129-L159).
- Rejected requirements produce an unsupported result rather than a test failure.

### Design-based pruning

- The test fixes the target to one `128 x 128` `VK_FORMAT_R8G8B8A8_UNORM` image, color attachment `0`, one mip level, one layer, and a full-render-area rectangle. It does not generate partial rectangles, multiple attachments, array-layer ranges, depth/stencil clears, formats, or image sizes.
- Seven static values give named fixed coverage, while ten seeded-random values broaden color input without creating an unbounded case set [vktProtectedMemAttachmentClearTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L264-L393).
- Primary and secondary command-buffer paths use the same clear and validation mechanics. The matrix does not add other command-buffer nesting or render-pass variants.

## Key Takeaways

- `protected_memory.attachment.clear_op` tests an in-render-pass fixed-function color clear on protected image memory.
- The primary behavioral axis is command-buffer placement: inline in the primary command buffer or inherited and executed from a secondary command buffer.
- The render pass starts from another color, and four compute-shader samples must match the requested clear value within `0.1` per component.
- The validator shaders observe the result but do not implement the operation under test. See `## Failure Meaning` when a timeout or submission failure occurs.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test category attachment | [vktProtectedMemTests.cpp#L50-L60](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L50-L60) | Adds `clear_op` below `protected_memory.attachment`. |
| Case definition and support check | [vktProtectedMemAttachmentClearTests.cpp#L55-L113](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L55-L113) | Stores clear/reference data, adds validator programs, and checks protected-context support. |
| Protected image and command setup | [vktProtectedMemAttachmentClearTests.cpp#L115-L165](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L115-L165) | Creates the protected target, framebuffer, command buffers, and initial barrier. |
| Render pass and attachment clear | [vktProtectedMemAttachmentClearTests.cpp#L167-L216](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L167-L216) | Chooses the initial color, records `vkCmdClearAttachments`, and handles secondary execution. |
| Final barrier, submit, and check | [vktProtectedMemAttachmentClearTests.cpp#L218-L261](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L218-L261) | Makes the image shader-readable, submits protected work, and calls the validator. |
| Case matrix registration | [vktProtectedMemAttachmentClearTests.cpp#L264-L411](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L264-L411) | Registers static/random leaves under primary/secondary paths and the `clear_op` test family. |
| Protected support and queue selection | [vktProtectedMemUtils.cpp#L80-L159](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L80-L159) | Requires Vulkan 1.1, protected memory, and a suitable protected queue family. |
| Protected resource helpers | [vktProtectedMemUtils.cpp#L306-L380](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L380) | Creates protected images and buffers with protected memory requirements. |
| Protected submission and command pool | [vktProtectedMemUtils.cpp#L460-L495](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495), [vktProtectedMemUtils.cpp#L512-L525](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525) | Enables protected submission and allocates protected command buffers. |
| Validator shader generation | [vktProtectedMemImageValidator.cpp#L47-L115](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the four-sample comparison and mismatch signal. |
| Validator resource and dispatch path | [vktProtectedMemImageValidator.cpp#L117-L264](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds protected validation resources and maps timeout to failure. |
| Mustpass paths | [protected-memory.txt#L1-L34](../../../mustpass/main/vk-default/protected-memory.txt#L1-L34) | Confirms the 34 primary/secondary, static/random test paths. |
| Attachment-clear semantics | [clears.adoc#L244-L285](../../../../vulkan-docs/src/chapters/clears.adoc#L244-L285) | Defines `vkCmdClearAttachments` regions and color-attachment execution behavior. |
| Protected attachment validity | [clears.adoc#L350-L359](../../../../vulkan-docs/src/chapters/clears.adoc#L350-L359) | Defines protected command-buffer and attachment compatibility. |
| Protected memory property | [memory.adoc#L953-L960](../../../../vulkan-docs/src/chapters/memory.adoc#L953-L960) | Defines protected memory access and host-visibility restrictions. |
| Protected command pools | [cmdbuffers.adoc#L318-L340](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L318-L340) | Defines command pools that allocate protected command buffers. |
