# Understanding Brief: `protected_memory.image.clear_color`

## One-Sentence Test Purpose

This test checks whether `vkCmdClearColorImage` writes the requested color to a protected image and makes that result available to the protected validation pass through both primary and secondary command-buffer paths.

## Background Knowledge

### Protected images and protected submissions

Vulkan protected memory is device-only memory that protected queue operations can access. A protected image is created with `VK_IMAGE_CREATE_PROTECTED_BIT` and bound to protected memory. A command pool created with `VK_COMMAND_POOL_CREATE_PROTECTED_BIT` allocates protected command buffers, and a protected submission sets `VkProtectedSubmitInfo::protectedSubmit` to `VK_TRUE`.

Why it matters here:

- The target image and the helper validation buffer use protected resources.
- The clear and validation submissions stay on the protected queue path, while the reference uniform buffer remains host-visible and unprotected so the host can initialize expected values.

### Image clear and layout visibility

`vkCmdClearColorImage` is a transfer command that clears selected subresources of an image in a specified layout. The application must make the image layout and access masks match the command and must add a dependency before a later operation reads the result.

Why it matters here:

- The test transitions the target image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL` before the clear.
- It then transitions the image to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` with a transfer-write to shader-read dependency before the validator samples it.

## One Concrete Example

Consider `dEQP-VK.protected_memory.image.clear_color.secondary.static.clear_1`:

1. The host creates a protected `128 x 128` `VK_FORMAT_R8G8B8A8_UNORM` image and selects the red clear value `(1, 0, 0, 1)`.
2. A protected primary and a protected secondary command buffer are allocated from the same protected command pool.
3. The secondary command buffer records the initial image barrier, `vkCmdClearColorImage`, and the barrier to shader-read layout. The primary executes the secondary command buffer.
4. The host submits the primary command buffer with protected submission enabled.
5. The image validator samples four stored coordinates and compares each sample with the expected red value using a per-component threshold of `0.1`.

## End-to-End Test Flow

```text
[host] choose the primary or secondary command-buffer path and a fixed or base-seed-generated clear value
[host] create a protected 128 x 128 VK_FORMAT_R8G8B8A8_UNORM image with transfer-destination and sampled-image usage
[host] allocate primary and secondary command buffers from a protected command pool
[host] record a barrier from VK_IMAGE_LAYOUT_UNDEFINED to VK_IMAGE_LAYOUT_GENERAL
[host] record vkCmdClearColorImage for the full color subresource range
[host] record a transfer-write to shader-read barrier and set VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL
[host] execute the secondary command buffer from the primary when the secondary path is selected
[host] submit the primary command buffer as protected work and wait for its fence
[host] initialize an unprotected host-visible reference uniform buffer with four coordinates and four expected colors
[device] reset the protected validator helper buffer
[device] sample four coordinates from the cleared image and compare them with the reference values
[host] report pass when the validation submission completes, or fail when it times out
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The clear operation is fixed-function Vulkan behavior and does not use a graphics or compute shader. `ClearColorImageTestCase::initPrograms` adds two compute programs supplied by the shared `ImageValidator`:

- `ResetSSBO` sets the helper buffer's `zero` field to zero.
- `ImageValidator` samples four image coordinates and enters the validator's error loop when any sample differs from its reference by more than `0.1` in a component.

These programs check the clear result. They do not implement `vkCmdClearColorImage`.

The test registers seven fixed color cases and ten random color cases for each command-buffer path. Random colors and their reference data are generated from the CTS command-line base seed.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected color image | yes | yes, as clear target and sampled image | written by `vkCmdClearColorImage`; sampled by validator | no | Holds the result without host mapping or image copyback. |
| Primary and secondary command buffers | yes | yes | carry barriers, clear, and secondary execution | no | Select where the clear is recorded while keeping execution protected. |
| Protected helper storage buffer | yes | yes, validator binding `1` | reset and updated by validator | no | Carries the validator's mismatch signal. |
| Reference uniform buffer | yes | yes, validator binding `2` | read by validator | host initializes it | Supplies four sample coordinates and expected clear colors. |
| Combined image sampler and image view | yes | yes, validator binding `0` | samples the protected image | no | Provides the validator's read path. |

## What Is Checked

- `ValidationData` supplies four image coordinates and four reference colors.
- For each coordinate, the validator samples the image and requires every component to be within `0.1` of the corresponding reference value.
- Static cases use the requested fixed clear color as all four reference values. Random cases use the generated color in all four reference entries.
- A mismatch enters an atomic loop whose increment is controlled by a zero helper value. `validateImage` treats a one-second queue timeout as failure.
- The host does not map or copy back the protected image. Completion of the protected validation submission is the pass signal.

## Behavior Parameter Identification

> **Behavior parameter:** command-buffer path, represented by the intermediate node below `clear_color`
>
> **Candidate values:** `primary`, `secondary`

The `static` and `random` intermediate nodes change only how the clear value and reference data are produced. They use the same image, layout transitions, clear command, submission, and validation path.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected image clearing or result visibility fails when `vkCmdClearColorImage` is recorded in the primary command buffer. |
| `secondary` | Protected image clearing, secondary command-buffer recording or execution, or result visibility fails when the clear is recorded in a secondary command buffer. |

Failures in both values can also come from shared protected image creation, protected submission, image layout synchronization, format conversion, or validator infrastructure.

## Important Variations and Special Cases

- Each command-buffer path contains a `static` intermediate node with seven leaves, `clear_1` through `clear_7`. The fixed values are red, green, blue, black with alpha one, red again, red with alpha zero, and `(0.1, 0.2, 0.3, 0.0)`.
- Each path also contains a `random` intermediate node with ten leaves, `clear_1` through `clear_10`. The base seed generates one clear color and four unrelated sample coordinates for each leaf.
- Every case uses one `128 x 128` 2D image, one mip level, one array layer, and the color aspect. The clear covers that complete subresource range.
- The primary path records the clear directly. The secondary path records the same sequence in a secondary command buffer with null render-pass inheritance fields, then executes it from the primary.
- Cases are unsupported when Vulkan 1.1, the protected-memory feature, or a protected queue is unavailable. The source also contains a Vulkan SC secondary-command-buffer property check.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test case and support setup | [ClearColorImageTestCase](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L57-L112) | Defines the case, adds validator programs, and checks protected support. |
| Protected image and command setup | [ClearColorImageTestInstance::iterate](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L126-L146) | Creates the target image and chooses the primary or secondary command buffer. |
| Layout transitions and clear | [clear recording](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L148-L228) | Records the image barriers, `vkCmdClearColorImage`, and secondary execution. |
| Protected submit and result check | [submit and validation](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L230-L244) | Submits protected work and invokes image validation. |
| Static and random registration | [case registration](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L247-L382) | Registers seven fixed and ten base-seed-generated cases for each path. |
| Top-level registration | [clear_color registration](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L387-L394) | Registers `primary` and `secondary` below `clear_color`. |
| Validator shader generation | [ImageValidator::initPrograms](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the four-sample comparison, threshold, and mismatch loop. |
| Validator resource and timeout path | [ImageValidator::validateImage](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds resources, dispatches both compute passes, and maps timeout to failure. |
| Protected support and queue selection | [protected support](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L159) | Requires Vulkan 1.1, protected memory, and a suitable queue family. |
| Protected image and buffer helpers | [protected resources](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L380) | Applies protected image/buffer flags and memory requirements. |
| Protected submit and command pool | [protected submission](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495), [protected command pool](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525) | Enables protected submission and protected command-buffer allocation. |
| Mustpass inventory | [protected-memory.txt#L639-L672](../../../mustpass/main/vk-default/protected-memory.txt#L639-L672) | Confirms the 34 primary/secondary, static/random paths. |
| Image clear semantics | [clears.adoc#L42-L105](../../../../vulkan-docs/src/chapters/clears.adoc#L42-L105) | Defines `vkCmdClearColorImage` as a transfer clear and its layout requirements. |
| Protected memory property | [memory.adoc#L953-L960](../../../../vulkan-docs/src/chapters/memory.adoc#L953-L960) | Defines protected device-only memory and its host-visibility restrictions. |
| Protected command pools | [cmdbuffers.adoc#L318-L340](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L318-L340) | Defines `VK_COMMAND_POOL_CREATE_PROTECTED_BIT`. |

## Questions / Risk Points for User Audit

- Is the distinction between the fixed-function clear and the compute validator clear enough?
- Does the primary/secondary command-buffer path capture the behavioral axis better than the `static`/`random` data-source split?
- Is the four-coordinate, `0.1`-threshold check clearly separated from whole-image validation?
- Is the timeout-based failure path clear without implying host access to protected image contents?

No unresolved source ambiguity affects the final page. The validator checks four selected coordinates and does not scan every pixel.

## Conversion Notes for Final Wiki Rewrite

- Keep protected memory, protected command buffers, image layouts, and transfer-clear semantics as concise prerequisite bullets.
- Use `primary` and `secondary` as the `## Behavior Parameters` subsections.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Put the seven fixed values and ten random values in the parameter table and pruning section rather than creating behavior subsections for them.
- Keep `## Shader Analysis` as a concise no-walkthrough explanation. The tested operation is `vkCmdClearColorImage`; `ResetSSBO` and `ImageValidator` are checking infrastructure.
- Preserve the protected image, two layout barriers, protected submit, and four-sample validator sequence in `## Runtime Execution and Result Checking`.
