# Understanding Brief: `buffer_to_depthstencil` test family

## One-Sentence Test Purpose

This test checks whether `vkCmdCopyBufferToImage` and its extension variants correctly copy depth and stencil aspects separately and in combination from a packed source buffer into a depth/stencil image, while honoring aspect selection, region order, queue family, and command-batching rules.

## Background Knowledge

### Depth/stencil aspect separation in copy commands

A combined depth/stencil Vulkan image (for example `VK_FORMAT_D24_UNORM_S8_UINT` or `VK_FORMAT_D32_SFLOAT_S8_UINT`) stores two logical aspects in one image resource. When `vkCmdCopyBufferToImage` copies into such an image, each `VkBufferImageCopy` region selects exactly one aspect through `imageSubresource.aspectMask` — either `VK_IMAGE_ASPECT_DEPTH_BIT` or `VK_IMAGE_ASPECT_STENCIL_BIT`. The Vulkan spec for `vkCmdCopyBufferToImage` requires that the aspect mask of each region match a single aspect for combined depth/stencil formats; it does not allow a single region to write both aspects at once.

Why it matters here:

- The test exercises every meaningful combination of "which aspect" and "in what order", so a driver that mishandles per-aspect addressing will fail at least one branch.
- The source buffer is *not* a packed D/S image. The test re-packs depth-only and stencil-only data into separate buffer regions, then uses `bufferOffset` to point each copy region at the right packed bytes. This means the test also exercises the implementation's `bufferOffset` arithmetic, not just aspect routing.

### Stencil packing is always 8 bits per texel

For every combined depth/stencil format, the Vulkan spec treats the stencil aspect as a one-byte-per-texel surface, regardless of how the depth aspect is laid out in memory. The CTS source relies on this rule when computing the source buffer size and the stencil region offset.

Why it matters here:

- The test computes the source buffer as `depthBytes + stencilBytes`, where `stencilBytes = width * height` (one byte per stencil texel) and `depthBytes = width * height * depthTexelSize`.
- For `VK_FORMAT_D32_SFLOAT_S8_UINT`, the depth texel size used for buffer sizing is `sizeof(float)` (4 bytes), not the full combined 5-byte texel. The source comment in the implementation makes this explicit.

### `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` and inter-command barriers

`vkCmdCopyBufferToImage` requires the destination image to be in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (or `VK_IMAGE_LAYOUT_GENERAL` / `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` in restricted cases). The test creates the destination image with `VK_IMAGE_LAYOUT_UNDEFINED` and uses the inherited `uploadImage` helper to transition it into `TRANSFER_DST_OPTIMAL` while seeding both aspects with a known gradient. When the test issues one copy command per region, it inserts a `VK_PIPELINE_STAGE_TRANSFER_BIT` → `VK_PIPELINE_STAGE_TRANSFER_BIT` pipeline barrier between consecutive copies to the same image, with `TRANSFER_WRITE` → `TRANSFER_WRITE` access masks and `TRANSFER_DST_OPTIMAL` → `TRANSFER_DST_OPTIMAL` layout (a self-layout transition the spec permits for execution dependency between writes).

Why it matters here:

- The multi-command path with barriers exercises whether the implementation correctly serializes two writes to the same depth/stencil image without losing either aspect.
- The single-command path batches multiple regions into one `vkCmdCopyBufferToImage` call, exercising a different code path in the driver where all regions are processed together.

### Queue-family and extension variants

The same `CopyBufferToDepthStencil` test instance is registered under four sibling test families under `copy_and_blit.core`:

- `buffer_to_depthstencil` — universal queue, standard `vkCmdCopyBufferToImage`.
- `buffer_to_depthstencil_compute_queue` — compute-only queue with `VK_KHR_maintenance10`, requiring `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR`.
- `buffer_to_depthstencil_transfer_queue` — transfer-only queue with `VK_KHR_maintenance10`, requiring the corresponding `_TRANSFER_QUEUE_` format feature bits.
- `memory_to_depthstencil_indirect` — uses `vkCmdCopyMemoryToImageIndirectKHR`, requiring `indirectMemoryToImageCopy` and `VK_FORMAT_FEATURE_2_COPY_IMAGE_INDIRECT_DST_BIT_KHR`.

The same `buffer_to_depthstencil` family is also registered under `dedicated_allocation` (dedicated memory), `copy_commands2` (uses `vkCmdCopyBufferToImage2KHR`), and `device_address` (uses `vkCmdCopyMemoryToImageKHR` with `VkCopyDeviceMemoryImageInfoKHR`).

Why it matters here:

- The same six-case aspect/ordering matrix runs against every command variant, every queue family, and every allocation mode. A failure scoped to one variant exposes a problem in that variant's command path, while a failure across all variants exposes a problem in the shared buffer layout, image setup, or aspect routing.

## One Concrete Example

Take `dEQP-VK.api.copy_and_blit.core.buffer_to_depthstencil.d24_unorm_s8_uint_D_S` as a concrete case. Conceptually reconstructed from the registration loop in `addCopyBufferToDepthStencilTests`:

```text
Format:           VK_FORMAT_D24_UNORM_S8_UINT (combined D/S)
Extent:           defaultExtent (square, single mip, single layer)
Offset mode:       false (whole image, bufferOffset = 0)
Aspect ordering:  _D_S  =>  depth region first, then stencil region, two commands
singleCommand:    false
```

Source buffer layout after the host re-pack loop in `CopyBufferToDepthStencil::iterate`:

```text
[0 .. depthBytes-1]    = packed depth-only texels (3 bytes per texel for D24)
[depthBytes .. end]     = packed stencil-only bytes (1 byte per texel)
```

Two copy regions are issued, in order:

1. `imageSubresource.aspectMask = VK_IMAGE_ASPECT_DEPTH_BIT`, `bufferOffset = 0`.
2. `imageSubresource.aspectMask = VK_IMAGE_ASPECT_STENCIL_BIT`, `bufferOffset = depthBytes`.

Between the two copies the test inserts a transfer-stage pipeline barrier to the destination image. The expected image is computed by `copyRegionToTextureLevel`, which copies the depth-only and stencil-only sub-regions of the source into the corresponding aspect of the destination texture level. The host then reads the GPU image back and compares it to the expected level pixel-by-pixel. Because both aspects were loaded, no aspect clearing is performed before the comparison.

## End-to-End Test Flow

```text
[host] choose format from formats::depthAndStencilFormats and offset mode (false or true)
[host] construct CopyRegion list with depth and/or stencil aspect layers
[host] create source VkBuffer (TRANSFER_SRC, plus DEVICE_ADDRESS when extension requires it)
[host] create destination VkImage (DEPTH/STENCIL format, OPTIMAL tiling, TRANSFER_DST usage)
[host] fill host-side source TextureLevel with a 1-D linear gradient
[host] fill host-side destination TextureLevel with a 2-D gradient (used as the initial image content)
[host] generate expected TextureLevel by copying source regions into destination per aspect
[host] re-pack source data into the source buffer: depth-only bytes first, then stencil-only bytes
[host] compute per-region bufferOffset values (depthOffset, stencilOffset) and rewrite copy regions
[host] flush source allocation
[host] upload destination image to TRANSFER_DST_OPTIMAL with both aspects seeded from the 2-D gradient
[host] insert transfer-stage pipeline barrier on destination image
[host] issue copy: single vkCmdCopyBufferToImage (or 2KHR / IndirectKHR / MemoryToImageKHR variant) when singleCommand=true,
       otherwise one command per region with a transfer-stage barrier between consecutive commands
[host] submit command buffer and wait (with sparse semaphore when sparse binding is used)
[host] read destination image back into a TextureLevel
[host] if depth was not loaded for a combined D/S format, clear depth to 0.0 in result and reference
[host] if stencil was not loaded for a combined D/S format, clear stencil to 0 in result and reference
[host] compare GPU result against software reference pixel-by-pixel via checkTestResult
[host] report pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

This family does not generate shaders. There are no GLSL, SPIR-V, HLSL, Amber, or pipeline-state artifacts. The "program" is purely a sequence of Vulkan copy commands recorded into a primary command buffer.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `m_source` VkBuffer | yes | yes | read by copy commands | host-visible mapping for re-packing | Holds packed depth-only then stencil-only source bytes |
| `m_destination` VkImage | yes | yes | written by copy commands, then read by `readImage` | yes, via `readImage` | Combined depth/stencil target image in `TRANSFER_DST_OPTIMAL` layout |
| `m_destinationTextureLevel` | yes (host-only) | no (used to seed the image) | seeds `m_destination` via `uploadImage` | yes (becomes expected after `generateExpectedResult`) | Provides the pre-copy initial image content used to detect uninitialized or stray writes |
| `m_sourceTextureLevel` | yes (host-only) | no (data is re-packed into `m_source`) | no | yes (used by `copyRegionToTextureLevel` for reference) | Provides the source pattern that gets re-packed per-aspect into the source buffer |
| `m_expectedTextureLevel` | yes (host-only) | no | no | yes (final reference) | Software-computed expected image after all copy regions |
| indirect buffer (INDIRECT_COPY only) | yes | yes (DEVICE_ADDRESS + INDIRECT_BUFFER) | read by `vkCmdCopyMemoryToImageIndirectKHR` | host-visible for `deMemcpy` of `VkCopyMemoryToImageIndirectCommandKHR` records | Carries per-region copy parameters from host memory to the indirect command |
| sparse semaphore (sparse binding only) | yes | yes | synchronizes sparse queue | no | Coordinates sparse memory binding with the copy submission |

## What Is Checked

- The destination image, after all copy commands complete, must equal the software-computed expected image.
- Comparison is per-pixel via `checkTestResult` inherited from the base class. No tolerance is applied; depth values and stencil bytes must match exactly.
- For combined D/S formats where only one aspect was loaded, the *other* aspect is cleared to 0 in both the result and the reference before comparison, so the test verifies that the uncopied aspect was not corrupted.
- For depth-only or stencil-only destination formats, only the loaded aspect is checked.
- The check is performed independently for each generated case. Cases do not aggregate.

## Behavior Parameter Identification

> **Behavior parameter:** aspect selection and command batching (encoded by the test-name suffix)
>
> **Candidate values:** `_DS`, `_D_S`, `_S_D`, `_SD`, `_D`, `_S`

The six suffixes are the primary behavioral axis because they change *what is being tested*: which aspect gets copied, in what order, and whether the test exercises the single-command batched path or the per-region barrier-separated path. Every other dimension (format, offset mode, extension flag, queue family, allocation kind, sparse binding) is a configuration axis that re-runs the same six-case matrix against a different command path or resource setup.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `_DS` (single command, depth region first then stencil) | Single-command batched path mishandles multiple aspect regions in one `vkCmdCopyBufferToImage` call, or packed-buffer offset routing is wrong for the second region in a batched command. |
| `_D_S` (per-command, depth then stencil, with inter-command barrier) | Per-region path mishandles the transfer-stage pipeline barrier between two writes to the same depth/stencil image, or the second command overwrites the first aspect. |
| `_S_D` (per-command, stencil then depth, with inter-command barrier) | Same as `_D_S` but with reversed order, exposing asymmetric aspect ordering dependencies. A failure that only appears here but not in `_D_S` points to ordering-sensitive aspect interaction. |
| `_SD` (single command, stencil region first then depth) | Same batched path as `_DS` but with reversed region order in the command. A failure that only appears here but not in `_DS` points to ordering sensitivity in the batched-command region walker. |
| `_D` (depth only) | Depth-only aspect selection, depth format packing, or `bufferOffset` arithmetic for the depth bytes. For combined D/S formats, the uncopied stencil aspect must be zero in both result and reference; a nonzero stencil after a `_D` case exposes aspect leakage. |
| `_S` (stencil only) | Stencil-only aspect selection, stencil byte packing (always 8-bit per texel), or stencil `bufferOffset` arithmetic. For combined D/S formats, the uncopied depth aspect must be zero in both result and reference; a nonzero depth after an `_S` case exposes aspect leakage. |

Shared infrastructure failure causes that affect every value:

- **Extension-variant dispatch failure**: `COPY_COMMANDS_2` (`vkCmdCopyBufferToImage2KHR`), `INDIRECT_COPY` (`vkCmdCopyMemoryToImageIndirectKHR`), or `DEVICE_ADDRESS_COMMANDS` (`vkCmdCopyMemoryToImageKHR`) region conversion or command dispatch is wrong.
- **Non-universal queue failure**: missing or incorrectly reported `VK_FORMAT_FEATURE_2_DEPTH_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `STENCIL_COPY_ON_COMPUTE_QUEUE_BIT_KHR` / `_TRANSFER_QUEUE_` bits, or wrong queue family ownership transfer for the destination image.
- **Source buffer offset arithmetic failure**: wrong `depthOffset`/`stencilOffset` computation, wrong per-region `bufferOffset` rewrite, or wrong indirect-buffer stride for the indirect variant.
- **Sparse binding failure**: sparse memory binding is incomplete, or sparse semaphore synchronization is incorrect, when `useSparseBinding` is enabled.

## Important Variations and Special Cases

- **`_SD` versus `_DS`**: both use `singleCommand = true` and both aspect regions in one command. The only difference is region order in the `VkBufferImageCopy` array. The pair isolates region-order sensitivity inside the batched path.
- **`_D_S` versus `_S_D`**: both use `singleCommand = false` with a barrier between two single-region commands. The only difference is which aspect is copied first. The pair isolates barrier/serialization sensitivity to aspect order in the per-region path.
- **`buffer_offset_*` cases**: same six suffixes, but with `bufferOffset = 32`, non-zero `bufferRowLength` and `bufferImageHeight`, and a sub-image `imageOffset`. These exercise the tight-pack versus row-padded source buffer layout arithmetic.
- **`memory_to_depthstencil_indirect`** (non-VulkanSC only): the test instance reuses the same `CopyBufferToDepthStencil` code, but the recorded commands use `vkCmdCopyMemoryToImageIndirectKHR` reading `VkCopyMemoryToImageIndirectCommandKHR` records from the indirect buffer. The source buffer must be `HOST_VISIBLE | DEVICE_ADDRESS` for the host to query its address before recording.
- **Sparse binding**: when `useSparseBinding` is enabled (only for the dedicated-allocation `copy_commands2` sparse branch in `addSparseCopyTests`), the destination image is created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, sparse memory is bound via `allocateAndBindSparseImage`, and submission uses `submitCommandsAndWaitWithTransferSync` with the sparse semaphore.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test instance class and `iterate` | [vktApiCopyBufferToDepthStencilTests.cpp#L32-L51](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L32-L51) | Owns resource setup, source re-pack, copy command recording, and result comparison |
| `copyRegionToTextureLevel` (software reference) | [vktApiCopyBufferToDepthStencilTests.cpp#L53-L93](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L53-L93) | Computes expected image; uses `tcu::getEffectiveDepthStencilAccess` to select aspect per region |
| Constructor: format support, buffer size computation, image creation | [vktApiCopyBufferToDepthStencilTests.cpp#L95-L257](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L95-L257) | Validates format support, computes `m_bufferSize` for depth+stencil packing, handles indirect-copy feature check and sparse binding |
| `iterate`: host re-pack loop and per-region `bufferOffset` rewrite | [vktApiCopyBufferToDepthStencilTests.cpp#L259-L395](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L259-L395) | Re-packs source into depth-only then stencil-only bytes; computes `depthOffset` and `stencilOffset`; converts to indirect/2KHR/device-memory forms per extension flag |
| `iterate`: command recording and per-region barriers | [vktApiCopyBufferToDepthStencilTests.cpp#L403-L591](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L403-L591) | Records the transfer-stage image barrier and dispatches to one of four command variants |
| Uncopied-aspect clearing and final check | [vktApiCopyBufferToDepthStencilTests.cpp#L598-L613](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L598-L613) | Clears depth/stencil to 0 in result and reference when only one aspect was loaded, then calls `checkTestResult` |
| `checkSupport`: feature and queue requirements | [vktApiCopyBufferToDepthStencilTests.cpp#L632-L734](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L632-L734) | Validates `VK_KHR_format_feature_flags2`, compute/transfer queue copy bits, indirect copy feature and queue support, sparse image format properties |
| `addCopyBufferToDepthStencilTests`: registration loop and six-case matrix | [vktApiCopyBufferToDepthStencilTests.cpp#L742-L878](../../../modules/vulkan/api/vktApiCopyBufferToDepthStencilTests.cpp#L742-L878) | Generates the six `_DS`/`_D_S`/`_S_D`/`_SD`/`_D`/`_S` leaves for every depth/stencil format and offset mode |
| Parent dispatcher registration | [vktApiCopiesAndBlittingTests.cpp#L119-L230](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L119-L230) | Routes `buffer_to_depthstencil` and its queue-family siblings under `core`, `dedicated_allocation`, `copy_commands2`, and `device_address` |
| Indirect copy branch in parent | [vktApiCopiesAndBlittingTests.cpp#L74-L117](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L74-L117) | Registers `memory_to_depthstencil_indirect` under `core` via `addIndirectCopyTests` with `INDIRECT_COPY` flag (non-VulkanSC) |

## Questions / Risk Points for User Audit

- The `external/vulkan-docs/src/chapters/` directory is not present in this checkout, so the brief was grounded using canonical Vulkan spec semantics for `vkCmdCopyBufferToImage`, depth/stencil aspect selection, `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` requirements, and `VK_KHR_maintenance10` queue-family copy bits. No spec chapter was read directly; this is a residual risk for the implementation-cause claims about barrier layout transitions and aspect routing.
- Is the behavior parameter identification correct? The six suffixes (`_DS`, `_D_S`, `_S_D`, `_SD`, `_D`, `_S`) are the axis that changes *what is being tested*; every other registered dimension (format, offset mode, extension flag, queue family, allocation kind, sparse binding) is treated as a configuration axis that re-runs the same matrix.
- The `_DS`/`_SD` pair differs only in region order inside a single batched command. The `_D_S`/`_S_D` pair differs only in command order across two barrier-separated commands. Is this four-way contrast (single vs. per-command × depth-first vs. stencil-first) the right granularity, or should `_DS`/`_SD` be collapsed into a single "batched both-aspect" cause?
- The "uncopied aspect must be cleared to 0" rule for combined D/S formats is grounded in source inspection (the implementation calls `tcu::clearDepth` / `tcu::clearStencil` on both result and reference), not in spec language. Is this acceptable as a "Possible implementation cause" for an aspect-leakage symptom?
- Sparse binding is only registered for the dedicated-allocation `copy_commands2` branch via `addSparseCopyTests`. The brief mentions this; should the final page treat sparse binding as a full behavioral axis or as a configuration variant?

## Conversion Notes for Final Wiki Rewrite

- The brief's `### Failure Cause Mapping` table above will be copied directly into the final page's `### Failure Cause Mapping`. The `_DS`/`_D_S`/`_S_D`/`_SD`/`_D`/`_S` rows are the primary axis; the four shared infrastructure causes will become `####` subsections under `### Cause Analysis` alongside the six per-value causes.
- The brief's `## Behavior Parameter Identification` conclusion (six suffixes as primary axis, every other dimension as configuration) will be carried into the final page's `## Behavior Parameters` section with one `###` subsection per suffix.
- The brief's `Background Knowledge` will be distilled to a compact bullet list covering (1) depth/stencil aspect separation in copy commands, (2) stencil always being 8-bit packed, (3) `TRANSFER_DST_OPTIMAL` layout and inter-command barriers, and (4) the four sibling test families and three intermediate-node variants.
- The brief's `One Concrete Example` will become the single concrete walkthrough of the `_D_S` flow inside `## Runtime Execution and Result Checking`, not a separate walkthrough section.
- The brief's `End-to-End Test Flow` will be condensed into the final page's `## Runtime Execution and Result Checking` as a compact ordered list.
- The brief's `Bound resources` table will be condensed into a smaller table covering only `m_source`, `m_destination`, the indirect buffer, and the sparse semaphore; the host-only texture levels are not GPU resources and will be folded into prose.
- The brief's `Important Variations and Special Cases` will be split between `## Behavior Parameters` (for `_SD` vs `_DS` and `_S_D` vs `_D_S` contrasts) and `## Case Pruning` (for indirect/sparse gating).
- Source links will move to `## Source Reference Appendix` as the canonical table; inline links will be retained only for the most load-bearing back-ticked concepts.
- The risk about the missing `vulkan-docs` directory will be noted as the only unresolved risk point in the final report.
