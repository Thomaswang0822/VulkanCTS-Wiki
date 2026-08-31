## Overview

**Core question:** Does `vkCmdClearColorImage` write the requested color to a protected image and expose it to the protected validator through both command-buffer paths?

- This page covers the `protected_memory.image.clear_color` test family implemented in [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp).
- Each case clears a protected `128 x 128` `VK_FORMAT_R8G8B8A8_UNORM` image over its single color subresource range, then checks four sampled coordinates.
- `primary` records the clear in the submitted primary command buffer. `secondary` records the same sequence in a secondary command buffer and executes it from the primary.
- The validator uses compute shaders as checking infrastructure. The operation under test is fixed-function `vkCmdClearColorImage`.

## Background Knowledge

- **Protected memory and submissions.** Memory with `VK_MEMORY_PROPERTY_PROTECTED_BIT` is device-only and accessible to protected queue operations. A protected command pool allocates protected command buffers, and `VkProtectedSubmitInfo::protectedSubmit` marks a submission as protected. The reference data used by validation can remain in an unprotected host-visible uniform buffer.
- **Image clear layouts.** `vkCmdClearColorImage` accepts `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`, and the image subresources must be in the named layout when the command executes. A later shader read needs a dependency from the clear's transfer write to shader-read access.

## Registration Hierarchy

```text
protected_memory.image.clear_color
├── primary
└── secondary
```

Each command-buffer path contains the intermediate nodes `static` and `random`, followed by the registered `clear_1` through `clear_7` or `clear_10` test case leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command-buffer path | `primary`, `secondary` | Selects whether the clear sequence is recorded in the submitted primary command buffer or in a secondary command buffer executed by that primary. | [top-level registration](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L387-L394), [command-buffer selection](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L141-L146) |
| Data source | `static`, `random` | Selects seven fixed clear/reference values or ten values generated from the CTS command-line base seed. | [case generation](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L247-L382) |
| Static test case leaf | `clear_1` through `clear_7` | Covers red, green, blue, black with alpha one, red again, red with alpha zero, and `(0.1, 0.2, 0.3, 0.0)`. | [static data](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L251-L345) |
| Random test case leaf | `clear_1` through `clear_10` | Gives each base-seed-generated clear value a separate registered test case. | [random registration](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L357-L375) |
| Target image | `128 x 128`, `VK_FORMAT_R8G8B8A8_UNORM`, one mip level, one array layer | Fixes the image shape while the command-buffer path and clear value vary. | [image constants and creation](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L51-L55), [image setup](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L134-L137) |
| Cleared subresource range | color aspect, mip level `0`, one level, array layer `0`, one layer | Covers the complete image because the image has one mip level and one layer. | [subresource range](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L148-L154) |

The mustpass inventory contains 34 paths: 17 under `primary` and the same 17 under `secondary` [protected-memory.txt](../../../mustpass/main/vk-default/protected-memory.txt#L639-L672).

## Behavior Parameters

The primary behavioral axis is the command-buffer path below the `clear_color` test family. It changes where the clear sequence is recorded and how it reaches the protected queue submission.

### `primary` - clear recorded in the primary command buffer

The primary path records the image barriers and `vkCmdClearColorImage` directly in the primary command buffer. That command buffer is submitted as protected work.

### `secondary` - clear recorded in a secondary command buffer

The secondary path records the image barriers and clear in a secondary command buffer allocated from the protected command pool. The primary records `vkCmdExecuteCommands` and submits the primary as protected work. The secondary command buffer uses null render-pass inheritance fields because this is an image-transfer sequence, not a render-pass continuation.

The `static` and `random` intermediate nodes change only the clear value and reference data. They do not change the clear mechanism, image shape, layout sequence, or validator.

## Shader Analysis

The tested operation is fixed-function `vkCmdClearColorImage`, so this page has no representative shader walkthrough. `ClearColorImageTestCase::initPrograms` adds `ResetSSBO` and `ImageValidator` from the shared `ImageValidator`; these compute programs reset validator state and compare four samples after the clear. They observe the result and do not implement the image clear [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L88-L95), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115). This source-reviewed no-walkthrough exception is recorded for `ClearColorImage.md` in the protected-memory exception registry.

## Runtime Execution and Result Checking

- The host creates a protected 2D image with `VK_IMAGE_CREATE_PROTECTED_BIT`, `VK_IMAGE_USAGE_TRANSFER_DST_BIT`, and `VK_IMAGE_USAGE_SAMPLED_BIT`. `createImage2D` gives it the fixed extent, format, one mip level, one array layer, and the selected protected queue family [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L347).
- The test creates a protected command pool, allocates one primary and one secondary command buffer, and selects the target from `m_cmdBufferType` [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L141-L146), [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525).
- The selected command buffer records an image barrier from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL`, with transfer-write access as the destination access [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L148-L196).
- It records `vkCmdClearColorImage` for the complete color subresource range in `VK_IMAGE_LAYOUT_GENERAL` [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L198-L200).
- It records a second barrier from transfer-write to shader-read access and changes the image to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L202-L220).
- On the secondary path, the primary executes the finished secondary command buffer, then the primary command buffer is submitted with `VkProtectedSubmitInfo::protectedSubmit = VK_TRUE` and a fence [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L222-L232), [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495).
- `ImageValidator` creates an unprotected host-visible reference uniform buffer, a protected helper storage buffer, a sampler, and an image view. Descriptor bindings `0`, `1`, and `2` hold the sampled image, helper buffer, and reference data respectively [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L143-L210).
- The validator first resets the helper buffer, then dispatches one workgroup for the comparison pass. It samples four coordinates and requires each component to be within `0.1` of its reference. A mismatch enters the atomic error loop, and the one-second queue timeout is reported as failure [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L71-L89), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L218-L263).

| Resource | Protection and binding | Device access | Validation role |
|----------|------------------------|---------------|-----------------|
| Color image | Protected image and protected memory; sampled at validator binding `0` | Cleared by transfer, then sampled by compute | Holds the value being tested without host readback. |
| Primary command buffer | Allocated from a protected command pool and submitted as protected work | Records barriers and either the clear or secondary execution | Provides the submitted execution path. |
| Secondary command buffer | Allocated from the same protected command pool | Records the clear sequence for `secondary` | Exercises recording and execution through a secondary command buffer. |
| Helper storage buffer | Protected buffer at binding `1` | Reset and updated by validator compute | Carries the mismatch signal. |
| Reference uniform buffer | Unprotected host-visible buffer at binding `2` | Read by validator compute | Supplies four coordinates and expected colors. |

The case passes when the validation submission completes. It fails when the validator times out after detecting a mismatched sample or when another checked operation returns an error. The validator checks four coordinates, not every pixel in the image.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected image clearing or result visibility fails when `vkCmdClearColorImage` is recorded in the primary command buffer. |
| `secondary` | Protected image clearing, secondary command-buffer recording or execution, or result visibility fails when the clear is recorded in a secondary command buffer. |

Failures in both values can also come from shared protected image creation, protected submission, image layout synchronization, format conversion, or validator infrastructure.

### Cause Analysis

#### Protected image clearing or result visibility on the primary path

**Possible failure symptoms:** One or more of the four validator samples differs from its reference by more than `0.1` in a component, so the validation submission times out. An image creation, command recording, submission, or validation error can also fail the case [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L230-L244), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L254-L263).

**Possible implementation causes:** The implementation may fail to perform the transfer clear, apply the clear value correctly to `VK_FORMAT_R8G8B8A8_UNORM`, or make the transfer write visible to the later shader read. The Vulkan specification requires the image to have transfer-destination usage, to be in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or `VK_IMAGE_LAYOUT_GENERAL`, and to use a color aspect for this command [clears.adoc#L43-L79](../../../../vulkan-docs/src/chapters/clears.adoc#L43-L79). The recorded barrier and final shader-read layout are the source-level synchronization path; separating a clear defect from a synchronization or validator defect needs further implementation investigation.

#### Protected image clearing, secondary recording, or secondary execution

**Possible failure symptoms:** `secondary` cases time out in validation while equivalent `primary` cases pass, or the primary's `vkCmdExecuteCommands` submission fails before validation. A sampled coordinate contains a value outside the allowed threshold after the secondary sequence runs.

**Possible implementation causes:** The implementation may mishandle protected secondary command-buffer recording or execution, fail to execute the clear sequence from `vkCmdExecuteCommands`, or lose the transfer write before shader validation. The test allocates the secondary from a protected command pool and executes it from the primary [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L141-L146), [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L222-L228). Source-level investigation is needed to distinguish secondary command-buffer behavior from the shared image, synchronization, or validator path.

#### Shared protected resource, submission, synchronization, or validator path

**Possible failure symptoms:** Both `primary` and `secondary` values fail across fixed and random colors, protected submission returns an error, or the validator times out without distinguishing command-buffer placement.

**Possible implementation causes:** The shared protected image allocation, protected queue selection, command-pool configuration, protected submission, layout dependency, format conversion, descriptor setup, or validator compute path may be responsible. Protected memory is device-only and cannot be combined with host-visible, host-coherent, or host-cached memory types [memory.adoc#L953-L960](../../../../vulkan-docs/src/chapters/memory.adoc#L953-L960). The shared failure does not identify `vkCmdClearColorImage` by itself; source-level investigation must isolate the clear from checking infrastructure.

## Case Pruning

### Requirement-based pruning

- `checkProtectedContextSupport` rejects the case when the API version is below Vulkan 1.1, the protected-memory feature is unavailable, or no protected queue exists [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127).
- Queue-family selection requires graphics, compute, and protected queue capabilities because the case performs protected image work and compute validation [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L129-L159).
- On Vulkan SC builds, secondary cases also require `secondaryCommandBufferNullOrImagelessFramebuffer`; otherwise the test reports unsupported [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L96-L104).
- An unsupported requirement prunes the case as unsupported rather than recording a test failure.

### Design-based pruning

- The matrix fixes one 2D image extent, `VK_FORMAT_R8G8B8A8_UNORM`, one mip level, one array layer, the color aspect, and a complete subresource range. It does not cover other formats, partial ranges, multiple layers, mip levels, or depth/stencil aspects.
- Seven fixed values provide named coverage, including alpha changes and a non-integer color. Ten base-seed-generated values broaden input coverage without making the registered matrix unbounded [vktProtectedMemClearColorImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L247-L375).
- The test compares primary and secondary recording paths but does not add other command-buffer nesting or queue-family transfer variants.

## Key Takeaways

- `protected_memory.image.clear_color` checks a fixed-function clear of protected image memory with `vkCmdClearColorImage`.
- The main behavioral axis is where the clear sequence is recorded: directly in the primary command buffer or in a secondary command buffer executed by the primary.
- Both paths use the same `GENERAL` clear layout, shader-read transition, protected submission, and four-coordinate validator.
- The validator's compute shaders only observe the result. A timeout identifies a failed check, not automatically a defect in the clear command. See `## Failure Meaning` for the possible causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Case and support check | [ClearColorImageTestCase](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L73-L112) | Defines the test case, initializes validator programs, and checks protected support. |
| Image and command-buffer setup | [ClearColorImageTestInstance::iterate](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L126-L146) | Creates the protected image and chooses the primary or secondary target. |
| Barriers and clear | [clear sequence](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L148-L228) | Records both layout transitions, `vkCmdClearColorImage`, and secondary execution. |
| Protected submission and case result | [submit and result](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L230-L244) | Submits protected work and calls `validateImage`. |
| Static and random case matrix | [case registration](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L247-L382) | Registers seven fixed and ten base-seed-generated leaves per path. |
| Top-level test family registration | [clear_color](../../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L387-L394) | Registers the `primary` and `secondary` intermediate nodes. |
| Validator shader generation | [ImageValidator::initPrograms](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Generates the reset and four-sample comparison compute programs. |
| Validator resources and timeout | [ImageValidator::validateImage](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds resources, dispatches validation, and maps timeout to failure. |
| Protected support and queue selection | [support and queue](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L159) | Checks Vulkan 1.1, protected memory, and queue capabilities. |
| Protected image and buffer allocation | [protected resource helpers](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L380) | Applies protected flags and memory requirements. |
| Protected command pool and submit | [protected command pool](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495), [command-pool helper](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525) | Enables protected submission and protected command-buffer allocation. |
| Mustpass paths | [protected-memory.txt#L639-L672](../../../mustpass/main/vk-default/protected-memory.txt#L639-L672) | Confirms the 34 primary/secondary static/random paths. |
| `vkCmdClearColorImage` semantics | [clears.adoc#L1-L121](../../../../vulkan-docs/src/chapters/clears.adoc#L1-L121) | Defines the clear value, valid layouts, transfer-destination usage, and protected-image rules. |
| Protected memory property | [memory.adoc#L953-L960](../../../../vulkan-docs/src/chapters/memory.adoc#L953-L960) | Defines device-only protected memory and host-visibility restrictions. |
| Protected command pools | [cmdbuffers.adoc#L318-L340](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L318-L340) | Defines protected command buffers allocated from the pool. |
