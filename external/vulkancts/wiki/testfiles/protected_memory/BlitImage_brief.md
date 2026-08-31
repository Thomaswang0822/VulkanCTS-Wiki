# Understanding Brief: `protected_memory.image.blit`

## One-Sentence Test Purpose

This test checks whether a protected transfer operation can clear a protected source image and blit it into a protected destination image through either primary or secondary command-buffer recording while preserving the expected color for protected-device validation.

## Background Knowledge

### Protected resources and execution

Protected memory is device-visible but not host-visible. Images backed by protected memory are therefore not read back directly by the CPU. Commands that access them run through protected command buffers, a protected-capable queue, and a protected submission.

Why it matters here:
- Both the source and destination images are created with `VK_IMAGE_CREATE_PROTECTED_BIT` and protected memory.
- The clear, barriers, and blit are recorded in a command pool created for protected command buffers and submitted as protected work.
- Result checking must stay on the device because exposing protected image contents to the host would defeat the protected-memory model.

### Image blits and memory dependencies

`vkCmdBlitImage` is a fixed-function transfer command. It reads a source region, applies the selected filtering rule, and writes a destination region. Here the source and destination regions have the same full-image extent and use `VK_FILTER_NEAREST`, so the operation should reproduce the source clear color across the destination.

Image memory barriers serve two connected purposes: they place image subresources in layouts valid for their next use, and their stage/access scopes make prior writes available and visible to later accesses. The source clear must be visible to the blit read, and the destination blit write must be visible to the validator's shader read.

## One Concrete Example

Consider `dEQP-VK.protected_memory.image.blit.secondary.static.blit_1`:

- The clear color is `(1, 0, 0, 1)`.
- A protected 128 × 128 `VK_FORMAT_R8G8B8A8_UNORM` source image is transitioned from `UNDEFINED` to `GENERAL` and cleared red.
- A transfer-to-transfer barrier changes the source access scope from transfer write to transfer read.
- A protected destination image is transitioned from `UNDEFINED` to `GENERAL`.
- `vkCmdBlitImage` copies the entire source extent to the entire destination extent with nearest filtering.
- A final barrier changes the destination to `SHADER_READ_ONLY_OPTIMAL` and sets its destination access to shader reads.
- Because this is a `secondary` case, those operations are recorded in a secondary command buffer, which is then executed by the protected primary command buffer.
- The image validator samples four coordinates and expects red at each one, allowing a per-component threshold of `0.1`.

## End-to-End Test Flow

```text
[host] select primary or secondary command-buffer mode and a static or seeded-random clear/reference pair
[host] create protected source and destination images, a protected command pool, and command buffers
[host] begin the protected primary command buffer; begin the secondary command buffer when selected
[device] transition the source image from UNDEFINED to GENERAL for transfer writes
[device] clear the complete source image to the selected color
[device] make the clear write available to transfer reads
[device] transition the destination image from UNDEFINED to GENERAL for transfer writes
[device] blit the complete source image into the complete destination image with nearest filtering
[device] make the destination write visible to shader reads and transition it to SHADER_READ_ONLY_OPTIMAL
[host] for secondary mode, end the secondary command buffer and record its execution in the primary command buffer
[host] submit the primary command buffer as protected work and wait on a fence
[host/device] invoke protected image-validation infrastructure
[device] sample four destination coordinates and compare them with the expected clear color
[host] treat completed validation as pass and validation timeout as fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The blit itself has no test-core shader. `vkCmdBlitImage` is fixed-function transfer behavior.

`BlitImageTestCase::initPrograms()` asks the shared `ImageValidator` to add two compute programs:

- `ResetSSBO` initializes a protected helper buffer field used by the validator.
- `ImageValidator` samples the protected destination image at four reference coordinates and compares each result with a reference color using a `0.1` component-wise threshold. On mismatch it enters a non-terminating atomic loop, which causes the protected validation submission to time out.

These helper shaders implement checking infrastructure; they do not implement the blit under test and are not suitable as a representative test-core shader walkthrough.

The case matrix is built in C++:

- seven fixed clear/reference records become `static.blit_1` through `static.blit_7`;
- ten deterministic pseudo-random clear/reference records become `random.blit_1` through `random.blit_10`;
- the same matrix is registered under `primary` and `secondary`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected source image | yes | yes, protected image memory | cleared, then read by transfer operations | no | Supplies the uniform source color for the blit. |
| Protected destination image | yes | yes, protected image memory | written by the blit, then sampled by validation | no | Holds the protected result being checked. |
| Protected command pool and primary command buffer | yes | submitted to a protected-capable queue | executes all protected work | no | Carries the direct commands or executes the selected secondary command buffer. |
| Protected secondary command buffer | yes, for every instance but used only by `secondary` | executed by the primary command buffer in `secondary` cases | records the same barriers, clear, and blit | no | Exercises secondary-command-buffer recording and execution of the protected transfer sequence. |
| Validator sampled-image view and sampler | yes | descriptor binding `0` | validator reads the protected destination | no | Makes protected image contents checkable without host mapping. |
| Protected validator helper buffer | yes | descriptor binding `1` | reset and atomically written on mismatch | no | Converts a mismatch into a validation timeout without exposing protected contents. |
| Unprotected reference uniform buffer | yes | descriptor binding `2` | validator reads coordinates and expected colors | initialized by host; no result readback | Supplies non-secret checking data to the validator. |

## What Is Checked

- The destination image must be sampleable at four reference coordinates after the transfer and layout transitions.
- Each sampled `vec4` must be within `0.1` per component of the selected clear color.
- All four expected values are the clear color, because a full 128 × 128 source image is cleared and then blitted over the full 128 × 128 destination image.
- The validator performs the comparison on the device. A mismatch drives its compute shader into a non-terminating loop, so `validateImage()` returns false when the queue submission reaches its one-second timeout.
- Each registered case is checked independently. There is no aggregate result across cases.

## Behavior Parameter Identification

> **Behavior parameter:** command-buffer mode (intermediate node below the `blit` test family)
>
> **Candidate values:** `primary`, `secondary`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected fixed-function clear/blit execution, image transition/synchronization, or protected image validation did not produce the expected destination samples when commands were recorded directly in the primary command buffer. |
| `secondary` | The same protected transfer or validation path failed, or secondary command-buffer recording/execution did not preserve the protected image operation sequence. |

A failure in both values can point to their shared image allocation, transfer, synchronization, protected submission, or validation path rather than to command-buffer level alone.

## Important Variations and Special Cases

- **Static versus random data.** `static` contains seven fixed clear colors, including different RGB channels, alpha values, and a mixed color. `random` contains ten values generated from the command-line base seed. This changes test data, not the core operation sequence.
- **Primary versus secondary recording.** In `primary`, barriers, clear, and blit are recorded directly in the primary command buffer. In `secondary`, the same sequence is recorded in a secondary command buffer and invoked by `vkCmdExecuteCommands` from the primary command buffer.
- **Vulkan SC secondary support.** A Vulkan SC `secondary` case is unsupported when `secondaryCommandBufferNullOrImagelessFramebuffer` is false, because the secondary command buffer is begun with null render-pass and framebuffer inheritance fields.
- **Fixed transfer shape.** Every case uses one 128 × 128 single-sample `R8G8B8A8_UNORM` layer, equal source and destination extents, and nearest filtering. The matrix does not explore scaling, format conversion, mip levels, array layers, or alternative filters.
- **No host image readback.** The validator uses protected compute work and timeout signaling because protected image memory must not become host-visible.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test family attachment | [vktProtectedMemTests.cpp#L62-L70](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L62-L70) | Places `blit` under `protected_memory.image`. |
| Support and Vulkan SC checks | [vktProtectedMemBlitImageTests.cpp#L84-L104](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L84-L104) | Requires protected-context support and checks the Vulkan SC secondary-command-buffer property. |
| Protected image and command-buffer setup | [vktProtectedMemBlitImageTests.cpp#L125-L167](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L125-L167) | Creates protected images and command buffers and selects the recording target. |
| Barriers, clear, and blit | [vktProtectedMemBlitImageTests.cpp#L169-L304](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L169-L304) | Implements the fixed-function operation and image dependency chain. |
| Submission and validation call | [vktProtectedMemBlitImageTests.cpp#L306-L328](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L306-L328) | Executes secondary commands when needed, submits protected work, and checks the destination. |
| Static and random case generation | [vktProtectedMemBlitImageTests.cpp#L331-L465](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L331-L465) | Defines seven fixed cases and ten seeded-random cases for each command-buffer mode. |
| Command-buffer mode registration | [vktProtectedMemBlitImageTests.cpp#L470-L477](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L470-L477) | Registers `primary` and `secondary` under `blit`. |
| Protected image creation | [vktProtectedMemUtils.cpp#L306-L348](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L348) | Applies the protected image-create flag and protected allocation requirement. |
| Protected submission | [vktProtectedMemUtils.cpp#L460-L496](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L496) | Adds `VkProtectedSubmitInfo` and waits for completion. |
| Validator programs and comparison rule | [vktProtectedMemImageValidator.cpp#L47-L115](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the helper shaders, sampled coordinates, threshold, and mismatch loop. |
| Validator resource setup and result | [vktProtectedMemImageValidator.cpp#L117-L264](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds the protected image and helper resources, dispatches checking, and maps timeout to failure. |
| Vulkan mustpass coverage | [protected-memory.txt#L605-L638](../../../mustpass/main/vk-default/protected-memory.txt#L605-L638) | Lists all Vulkan `primary`/`secondary`, `static`/`random`, and `blit_1` through `blit_10` leaves. |
| Vulkan SC mustpass coverage | [protected-memory.txt#L424-L457](../../../mustpass/main/vksc-default/protected-memory.txt#L424-L457) | Lists the corresponding Vulkan SC leaves. |
| Protected memory semantics | [memory.adoc#L5565-L5654](../../../../vulkan-docs/src/chapters/memory.adoc#L5565-L5654) | Defines protected memory, protected resources, command buffers, submissions, and access rules. |
| Image blit semantics | [copies.adoc#L2333-L2455](../../../../vulkan-docs/src/chapters/copies.adoc#L2333-L2455) | Defines `vkCmdBlitImage`, region mapping, filtering, and format rules. |
| Memory dependencies and image transitions | [synchronization.adoc#L137-L208](../../../../vulkan-docs/src/chapters/synchronization.adoc#L137-L208) | Grounds availability, visibility, access scopes, and layout-transition ordering. |

## Questions / Risk Points for User Audit

- Is command-buffer mode the clearest behavioral axis, given that `static` and `random` change input coverage but not the transfer mechanism?
- Is the distinction between fixed-function blit behavior and validator-only compute shaders explicit enough?
- Is the timeout-based validator explained without implying that protected image contents are read by the host?
- Are the common failure causes separated carefully enough from the secondary-command-buffer-specific cause?

No unresolved source question changes the selected behavioral axis, the fixed-function no-walkthrough decision, or the stated pass/fail rule.

## Conversion Notes for Final Wiki Rewrite

- Keep protected-memory visibility, protected execution, fixed-function blit behavior, and barrier semantics as short prerequisite bullets.
- Carry `primary` and `secondary` into `## Behavior Parameters` as the command-buffer-mode axis.
- Copy the `### Failure Cause Mapping` table exactly into the final page, including the shared-cause paragraph.
- Keep validator shaders in the runtime/checking explanation. Do not create a representative shader walkthrough: `vkCmdBlitImage` is fixed-function, and `BlitImage.md` is approved in `walkthrough_exceptions.py`.
- Preserve the resource table in a compact form because it explains why validation is device-side.
- Move implementation links to the source appendix except where a link directly supports a non-obvious claim.
