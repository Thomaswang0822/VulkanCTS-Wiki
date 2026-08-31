# Understanding Brief: `protected_memory.attachment.clear_op`

## One-Sentence Test Purpose

This test checks whether `vkCmdClearAttachments` writes the requested color to a protected framebuffer attachment when the command is recorded in a primary or secondary protected command buffer.

## Background Knowledge

### Protected images and protected submissions

Vulkan protected memory is device-only memory that protected queue operations can access. Command buffers allocated from a command pool with `VK_COMMAND_POOL_CREATE_PROTECTED_BIT` are protected command buffers, and a protected submission sets `VkProtectedSubmitInfo::protectedSubmit` to `VK_TRUE`.

Why it matters here:

- The color image uses `VK_IMAGE_CREATE_PROTECTED_BIT` and protected memory.
- The command pool and queue submission use protected modes, so the clear remains in the protected execution path.

### Attachment clears inside a render pass

`vkCmdClearAttachments` clears selected regions of bound framebuffer attachments inside a render pass instance. A color clear acts as a color-attachment write at the color attachment output stage and does not depend on bound graphics pipeline state.

Why it matters here:

- The test clears color attachment `0` across the full render area and its single array layer.
- The render pass starts the attachment with a different color, so the later attachment-clear command must replace that value.

## One Concrete Example

Consider `dEQP-VK.protected_memory.attachment.clear_op.secondary.static.clear_1`:

1. The host creates a protected `128 x 128` `VK_FORMAT_R8G8B8A8_UNORM` image and binds it as color attachment `0`.
2. The render pass starts with a color chosen component by component to differ from the requested red clear value `(1, 0, 0, 1)`.
3. A secondary protected command buffer records `vkCmdClearAttachments` for the whole attachment.
4. The primary protected command buffer executes the secondary buffer, ends the render pass, and transitions the image for shader reads.
5. The image validator samples four coordinates and expects red at each one, with a component threshold of `0.1`.

## End-to-End Test Flow

```text
[host] choose the primary or secondary command-buffer path and a static or seeded-random clear value
[host] create a protected 128 x 128 color image, image view, render pass, and framebuffer
[host] allocate primary and secondary command buffers from a protected command pool
[host] transition the image from UNDEFINED to COLOR_ATTACHMENT_OPTIMAL
[host] begin the render pass with an initial color that differs from the requested clear color
[host] record vkCmdClearAttachments in the selected target command buffer
[device] clear color attachment 0 over the full render area and layer 0
[host] execute the secondary command buffer when the secondary path is selected
[host] end the render pass and transition the image to SHADER_READ_ONLY_OPTIMAL
[host] submit the primary command buffer as protected work and wait for completion
[device] run the image-validator compute passes on a protected queue
[device] sample four image coordinates and trigger a timeout path if any value differs beyond the threshold
[host] report pass when validation completes, or fail when validation times out
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The attachment clear itself uses fixed-function Vulkan behavior and has no test shader or graphics pipeline. `AttachmentClearTestCase::initPrograms` asks the shared `ImageValidator` to add two compute programs:

- `ResetSSBO` initializes the validator helper state.
- `ImageValidator` samples four coordinates, compares each sampled color with a reference using a `0.1` threshold, and enters the validator's timeout path on a mismatch.

These compute shaders check the result. They do not implement the attachment clear under test.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected color image | yes | yes, framebuffer attachment and sampled image | written by `vkCmdClearAttachments`; read by validator | no | Holds the result without exposing protected image contents to host mapping. |
| Color image view and framebuffer | yes | yes | select color attachment `0` | no | Bind the protected image to the render pass. |
| Protected command pool and command buffers | yes | yes | carry the clear and image barriers | no | Keep command recording and submission in the protected path. |
| Reference uniform buffer | yes | yes, validator binding `2` | read by validator | host initializes it | Supplies four sample coordinates and expected colors. |
| Protected helper storage buffer | yes | yes, validator binding `1` | reset and updated by validator | no | Supports the timeout-based mismatch signal. |
| Combined image sampler | yes | yes, validator binding `0` | samples the protected color image | no | Lets the validator compare selected image locations. |

## What Is Checked

- The validator samples four coordinates stored in `ValidationData.coords`.
- Each sampled `vec4` must differ from its expected clear value by no more than `0.1` in every component.
- All four expected values equal the case's requested clear color.
- A mismatch sends the validator into a nonterminating atomic loop. `validateImage` treats the resulting one-second queue timeout as failure.
- The host does not map or copy back the protected image. Completion of the validator submission is the pass signal.

## Behavior Parameter Identification

> **Behavior parameter:** command-buffer path, represented by the intermediate node below `clear_op`
>
> **Candidate values:** `primary`, `secondary`

The `static` and `random` intermediate nodes vary clear-value generation. They do not change the `vkCmdClearAttachments` mechanism or the protected resource path.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected attachment clearing or result visibility fails when `vkCmdClearAttachments` is recorded inline in the primary command buffer. |
| `secondary` | Protected attachment clearing, secondary command-buffer inheritance or execution, or result visibility fails when the clear is recorded in a secondary command buffer. |

Failures in both values can also come from shared protected image creation, protected submission, color conversion, synchronization, or validator infrastructure.

## Important Variations and Special Cases

- Each command-buffer path has `static` and `random` intermediate nodes.
- `static` registers seven test case leaves, `clear_1` through `clear_7`, covering red, green, blue, black with alpha one, repeated red, red with alpha zero, and `(0.1, 0.2, 0.3, 0.0)`.
- `random` registers ten leaves, `clear_1` through `clear_10`. A seed from the CTS command line generates one clear color per leaf.
- Every case uses the same image format, extent, color aspect, attachment index, full-image clear rectangle, and one array layer.
- The primary and secondary paths share the same validation data. The secondary path adds render-pass inheritance and execution through `vkCmdExecuteCommands`.
- Unsupported implementations are pruned when Vulkan 1.1, the protected-memory feature, or a queue family with protected graphics and compute support is absent.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category attachment | [vktProtectedMemTests.cpp#L50-L60](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L50-L60) | Adds `clear_op` below `protected_memory.attachment`. |
| Case and support setup | [vktProtectedMemAttachmentClearTests.cpp#L55-L113](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L55-L113) | Defines the case data, validator programs, and protected-context check. |
| Protected image and command setup | [vktProtectedMemAttachmentClearTests.cpp#L115-L165](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L115-L165) | Creates the protected target and records its first layout transition. |
| Attachment clear command | [vktProtectedMemAttachmentClearTests.cpp#L167-L216](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L167-L216) | Sets a different initial color, records `vkCmdClearAttachments`, and executes the secondary path when selected. |
| Transition, submit, and validation | [vktProtectedMemAttachmentClearTests.cpp#L218-L261](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L218-L261) | Makes the image shader-readable, submits protected work, and calls the validator. |
| Static and random registration | [vktProtectedMemAttachmentClearTests.cpp#L264-L399](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L264-L399) | Registers seven fixed and ten seeded-random cases for each command-buffer path. |
| `clear_op` registration | [vktProtectedMemAttachmentClearTests.cpp#L404-L411](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L404-L411) | Registers `primary` and `secondary`. |
| Protected support checks | [vktProtectedMemUtils.cpp#L80-L127](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L80-L127) | Requires Vulkan 1.1, protected memory, and protected queue support. |
| Protected resource and submit helpers | [vktProtectedMemUtils.cpp#L306-L380](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L380), [vktProtectedMemUtils.cpp#L460-L495](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495), [vktProtectedMemUtils.cpp#L512-L525](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525) | Creates protected images, buffers, command pools, and submissions. |
| Validator programs | [vktProtectedMemImageValidator.cpp#L47-L115](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Generates the reset and comparison compute shaders. |
| Validator execution | [vktProtectedMemImageValidator.cpp#L117-L264](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds the image and reference data, dispatches validation, and maps timeout to failure. |
| Mustpass inventory | [protected-memory.txt#L1-L34](../../../mustpass/main/vk-default/protected-memory.txt#L1-L34) | Confirms all 34 registered attachment-clear paths. |
| `vkCmdClearAttachments` semantics | [clears.adoc#L244-L285](../../../../vulkan-docs/src/chapters/clears.adoc#L244-L285) | Defines in-render-pass attachment clears and their pipeline-stage behavior. |
| Protected clear validity | [clears.adoc#L350-L359](../../../../vulkan-docs/src/chapters/clears.adoc#L350-L359) | States the protected command-buffer and protected attachment pairing rules. |
| Protected memory property | [memory.adoc#L953-L960](../../../../vulkan-docs/src/chapters/memory.adoc#L953-L960) | Defines protected memory as device-only memory accessible to protected queue operations. |
| Protected command pools | [cmdbuffers.adoc#L318-L340](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L318-L340) | Defines command pools that allocate protected command buffers. |

## Questions / Risk Points for User Audit

- Does the primary/secondary command-buffer path capture the behavior axis better than the static/random data-source split?
- Is the distinction between fixed-function clear behavior and compute-shader validation clear?
- Does the timeout-based validator explanation avoid implying host readback of protected image contents?
- Is four-point sampling described with enough precision without claiming whole-image readback?

No unresolved source ambiguity affects the final page. The validator proves the expected color at its four selected coordinates; the documentation must not claim that it scans every pixel.

## Conversion Notes for Final Wiki Rewrite

- Keep protected memory, protected command buffers, and in-render-pass attachment clears as brief prerequisite bullets.
- Use `primary` and `secondary` as the `## Behavior Parameters` subsections.
- Copy the `### Failure Cause Mapping` table without changes.
- Explain the seven static and ten random values in the parameter table, not as separate behavior subsections.
- Keep `## Shader Analysis` short. The operation under test is `vkCmdClearAttachments`; the shared compute shaders are validator infrastructure and do not warrant a representative shader walkthrough.
- Preserve the protected resource and synchronization sequence in `## Runtime Execution and Result Checking`.
- State the four-sample, `0.1`-threshold, timeout-based pass condition without expanding it into whole-image validation.
