## Overview

**Core question:** Can protected fixed-function image blits produce the expected destination contents when recorded in either a primary or secondary command buffer?

- This page covers the `protected_memory.image.blit` test family implemented by [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp).
- Every case clears a protected source image, blits its full extent into a protected destination image with `vkCmdBlitImage`, then validates four destination samples without exposing protected contents to the host.
- The main behavioral split is command-buffer mode: `primary` records the operation sequence directly, while `secondary` records it in a secondary command buffer executed by the primary command buffer.
- Each mode contains seven fixed-color `static` cases and ten seeded `random` cases. These vary the transferred color while keeping the image format, extent, filter, barriers, and validation method fixed.

## Background Knowledge

- **Protected memory and protected execution.** Protected memory is device-visible but not host-visible. Protected images must be used through protected command buffers, a protected-capable queue, and protected submissions, so this test checks its result on the device rather than mapping the image on the host.
- **Fixed-function image blits.** `vkCmdBlitImage` is a transfer command that reads a source region and writes a destination region using a selected filter. This test uses equal full-image source and destination extents with `VK_FILTER_NEAREST`, so no scaling or format conversion is intended.
- **Image memory dependencies.** Image barriers combine access dependencies with layout transitions. The source clear must become visible to the blit's transfer read, and the destination blit write must become visible to the validator's shader read.

## Registration Hierarchy

```text
protected_memory.image.blit
├── primary
└── secondary
```

Both intermediate nodes contain `static` and `random` descendants. The complete Vulkan and Vulkan SC mustpass sets contain 34 leaves each: seven static and ten random leaves under each command-buffer mode.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command-buffer mode | `primary`, `secondary` | Selects whether the clear, barriers, and blit are recorded directly in the primary command buffer or in a secondary command buffer executed by it. | [mode selection and execution](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L143-L167), [registration](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L470-L477) |
| Data set | `static`, `random` | Chooses seven fixed clear/reference records or ten records generated from the command-line base seed. | [case generation](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L331-L465) |
| Test case leaf | `blit_1` through `blit_7` in `static`; `blit_1` through `blit_10` in `random` | Selects one clear color and its four expected sample values. | [static names](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L431-L439), [random names](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L441-L459) |
| Image shape and format | 128 × 128, one mip level, one layer, `VK_FORMAT_R8G8B8A8_UNORM`, single-sample | Keeps resource shape fixed so the cases focus on protected transfer execution rather than format or subresource variation. | [fixed dimensions and format](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L51-L55), [image setup](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L113-L140), [image helper](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L348) |
| Blit region and filter | full source extent to full destination extent; `VK_FILTER_NEAREST` | Copies the cleared color over the entire destination without intended scaling. | [blit region and command](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L258-L280) |
| Validation samples | four coordinates; component threshold `0.1` | Checks representative destination locations against the clear color while allowing the validator's fixed comparison tolerance. | [reference records](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L337-L429), [validator comparison](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L90) |

## Behavior Parameters

The primary behavioral axis is command-buffer mode, represented by the `primary` and `secondary` intermediate nodes below the `blit` test family. The data-set and leaf dimensions change the color samples but not the protected transfer mechanism.

### `primary` (direct recording)

The image transitions, source clear, transfer dependency, full-image blit, and final destination transition are recorded directly in the protected primary command buffer. Passing shows that the protected fixed-function transfer sequence and subsequent device-side validation produce the selected color when no secondary execution is involved.

### `secondary` (secondary recording and execution)

The same operation sequence is recorded in a protected secondary command buffer. After that command buffer ends, the protected primary command buffer invokes it with `vkCmdExecuteCommands`. Passing checks the shared transfer path and the extra requirement that secondary recording and execution preserve the protected image operations and their ordering.

## Shader Analysis

The tested operation has no test-core shader: `vkCmdBlitImage` is a fixed-function transfer command. The shared `ImageValidator` does use compute shaders to sample the protected destination and turn a mismatch into a timeout, but those shaders are checking infrastructure rather than the behavior under test. For that reason, this page has no representative shader walkthrough; `BlitImage.md` is listed in the approved protected-memory walkthrough exceptions.

## Runtime Execution and Result Checking

- The host creates two protected 128 × 128 `VK_FORMAT_R8G8B8A8_UNORM` images. The source supports transfer writes and reads; the destination supports transfer writes and later sampled access [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L125-L140).
- A protected command pool supplies primary and secondary command buffers. The selected command-buffer mode determines the target for the barriers, clear, and blit [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L141-L167).
- The source moves from `UNDEFINED` to `GENERAL` for transfer writes, is cleared to the case color, then receives a transfer-write-to-transfer-read barrier before the blit [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L169-L231).
- The destination moves from `UNDEFINED` to `GENERAL` for the transfer write. One `VkImageBlit` covers the complete source and destination color subresources, and `vkCmdBlitImage` uses nearest filtering [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L233-L280).
- A final barrier changes the destination from `GENERAL` to `SHADER_READ_ONLY_OPTIMAL`, with transfer-write source access and shader-read destination access. Its destination stage is `ALL_GRAPHICS`; the subsequent fence wait completes the protected transfer submission and makes its writes visible to later validator commands [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L282-L316), [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L496).
- For `secondary`, the host ends the secondary command buffer and records `vkCmdExecuteCommands` in the primary. It then submits the primary command buffer as protected work and waits on a fence [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L306-L317), [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L496).
- `ImageValidator::validateImage()` samples four coordinates from the protected destination. Each component must be within `0.1` of the expected clear color. A mismatch enters a non-terminating atomic loop; the one-second validation submission timeout makes `validateImage()` return false [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L90), [vktProtectedMemImageValidator.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L236-L264).

| Resource | Protection and access | Role in the test |
|----------|-----------------------|------------------|
| Source image | Protected; transfer destination and source | Receives the clear color, then supplies the blit input. |
| Destination image | Protected; transfer destination and sampled image | Receives the blit and remains device-only for validation. |
| Protected primary command buffer | Protected submission | Records the transfer sequence directly or executes the secondary command buffer. |
| Protected secondary command buffer | Used by `secondary` cases | Records the same transfer sequence for secondary execution. |
| Validator sampled-image descriptor | Reads the protected destination | Lets protected compute work compare image samples without host readback. |
| Protected helper buffer | Reset and atomically written by validator compute work | Converts a sample mismatch into a validation timeout. |
| Unprotected reference uniform | Host-initialized, device-read | Provides four coordinates and four expected colors; it contains reference data, not protected image contents. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Protected fixed-function clear/blit execution, image transition/synchronization, or protected image validation did not produce the expected destination samples when commands were recorded directly in the primary command buffer. |
| `secondary` | The same protected transfer or validation path failed, or secondary command-buffer recording/execution did not preserve the protected image operation sequence. |

A failure in both values can point to their shared image allocation, transfer, synchronization, protected submission, or validation path rather than to command-buffer level alone.

### Cause Analysis

#### Protected transfer result or validation failure

**Possible failure symptoms:** One or more destination samples differ from the case's clear color by more than `0.1` in at least one component. The validator then fails to finish within one second, `validateImage()` returns false, and the case reports failure. A queue submission or Vulkan command error can also stop the case before validation completes.

**Possible implementation causes:** The source clear or fixed-function blit may write incorrect texel values; protected image allocation or access may not preserve the expected data; or the barrier access scopes/layout transitions may fail to make the clear visible to the blit or the blit visible to validation. A failure can also arise in shared protected submission or validator infrastructure, so a failing sample does not by itself isolate the defect to `vkCmdBlitImage`.

#### Secondary command-buffer recording or execution failure

**Possible failure symptoms:** `secondary` cases fail while equivalent `primary` cases with the same static or seeded-random input pass, or protected secondary execution produces missing, stale, or incorrect destination samples.

**Possible implementation causes:** Secondary command-buffer recording, inheritance handling, or `vkCmdExecuteCommands` execution may not preserve the recorded protected barriers and transfer commands. On Vulkan SC, the case is pruned rather than failed when null-or-imageless-framebuffer secondary inheritance is unsupported, so this cause applies only after the support check passes.

## Case Pruning

### Requirement-based pruning

- The cases require Vulkan 1.1, the `protectedMemory` feature, and a suitable protected-capable queue. Missing support produces `NotSupported`, not a conformance failure [vktProtectedMemUtils.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L78-L127).
- On Vulkan SC, `secondary` cases additionally require `secondaryCommandBufferNullOrImagelessFramebuffer`, because the secondary command buffer is begun with null render-pass and framebuffer inheritance. If the property is false, those cases are unsupported [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L95-L103), [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L153-L167).

### Design-based pruning

- The test matrix fixes the image to a single-sample, one-layer, one-mip 128 × 128 `R8G8B8A8_UNORM` image. It does not register format conversion, scaling, mip-level, array-layer, or multisample variants.
- Source and destination extents are identical and the filter is always `VK_FILTER_NEAREST`; filtering differences are outside this test family's intended protected-transfer shape.
- `static` registers seven curated color records, while `random` registers exactly ten records from a deterministic base seed. Other colors are not separate registered leaves [vktProtectedMemBlitImageTests.cpp](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L331-L459).

## Key Takeaways

- `protected_memory.image.blit` tests a fixed-function, full-image protected blit rather than shader implementation of a copy.
- `primary` and `secondary` are the behavioral axis; they run the same transfer sequence through different command-buffer recording paths.
- Source-clear visibility, destination-write visibility, image layouts, and protected submission are part of the conformance path, not incidental setup.
- The destination is never mapped by the host. Protected validator compute work checks four samples and signals mismatch through timeout behavior.
- See `## Failure Meaning` when distinguishing a shared protected transfer/validation failure from a secondary-command-buffer-specific failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family attachment | [vktProtectedMemTests.cpp#L62-L70](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L62-L70) | Adds `blit` under the `protected_memory.image` path. |
| Support checks | [vktProtectedMemBlitImageTests.cpp#L84-L104](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L84-L104) | Requires protected-context support and gates the Vulkan SC secondary mode. |
| Runtime operation | [vktProtectedMemBlitImageTests.cpp#L125-L328](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L125-L328) | Creates images, records barriers/clear/blit, submits protected work, and calls validation. |
| Case generation | [vktProtectedMemBlitImageTests.cpp#L331-L465](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L331-L465) | Defines the static and seeded-random leaves for each command-buffer mode. |
| Command-buffer mode registration | [vktProtectedMemBlitImageTests.cpp#L470-L477](../../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L470-L477) | Registers `primary` and `secondary` under `blit`. |
| Protected image helper | [vktProtectedMemUtils.cpp#L306-L348](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L306-L348) | Creates protected images and requires protected memory allocation. |
| Protected command and submission helpers | [vktProtectedMemUtils.cpp#L444-L496](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L444-L496) | Begins secondary command buffers and performs protected queue submission. |
| Validator programs | [vktProtectedMemImageValidator.cpp#L47-L115](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines validation-only compute shaders and the sample comparison rule. |
| Validator execution | [vktProtectedMemImageValidator.cpp#L117-L264](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds resources, dispatches protected checking, and maps timeout to failure. |
| Vulkan mustpass paths | [protected-memory.txt#L605-L638](../../../mustpass/main/vk-default/protected-memory.txt#L605-L638) | Confirms all 34 Vulkan leaves. |
| Vulkan SC mustpass paths | [protected-memory.txt#L424-L457](../../../mustpass/main/vksc-default/protected-memory.txt#L424-L457) | Confirms the corresponding 34 Vulkan SC leaves. |
| Protected memory specification | [memory.adoc#L5565-L5654](../../../../vulkan-docs/src/chapters/memory.adoc#L5565-L5654) | Defines protected resources, execution, visibility restrictions, and access rules. |
| Image blit specification | [copies.adoc#L2333-L2455](../../../../vulkan-docs/src/chapters/copies.adoc#L2333-L2455) | Defines `vkCmdBlitImage`, region mapping, filtering, and format behavior. |
| Synchronization specification | [synchronization.adoc#L137-L208](../../../../vulkan-docs/src/chapters/synchronization.adoc#L137-L208) | Defines memory dependencies, access scopes, availability/visibility, and image transitions. |
