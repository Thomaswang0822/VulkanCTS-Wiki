## Overview

**Core question:** Can one imageless framebuffer accept compatible attachment image views at render pass begin time and produce the same attachment results expected from those views?

- This page covers all six test families implemented and registered by [vktImagelessFramebufferTests.cpp](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp): `color`, `depth_stencil`, `color_resolve`, `depth_stencil_resolve`, `multisubpass`, and `different_attachments`.
- Every family creates a framebuffer with `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT`, leaves `VkFramebufferCreateInfo::pAttachments` null, describes compatible images through `VkFramebufferAttachmentsCreateInfo`, and supplies the actual image views through `VkRenderPassAttachmentBeginInfo` when beginning a render pass.
- The six families vary attachment roles, sample counts, subpass use, and whether one framebuffer is reused with different image views. Host-side reference images and readback comparisons decide the result.

## Background Knowledge

- **Imageless framebuffer.** A normal framebuffer stores its attachment image views at framebuffer creation. An imageless framebuffer stores attachment compatibility information instead. The application provides the actual views when it begins each render pass instance. The feature is exposed by `imagelessFramebuffer` [features.adoc](../../../../vulkan-docs/src/chapters/features.adoc#L3025-L3030).
- **Two-part attachment contract.** `VkFramebufferAttachmentImageInfo` records the image creation flags, usage, dimensions, layer count, and permitted view formats. The views in `VkRenderPassAttachmentBeginInfo` must match that information and the render pass attachment descriptions [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L6180-L6239), [render pass begin validity](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7250-L7257).
- **Resolve attachments.** A multisampled attachment stores several samples per pixel. A resolve attachment stores a single-sample result. Color resolve averages covered color samples in these cases; the depth/stencil case selects sample zero, whose meaning is defined in the render pass chapter [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L6599-L6603).

## Registration Hierarchy

```text
imageless_framebuffer
├── color
├── depth_stencil
├── color_resolve
├── depth_stencil_resolve
├── multisubpass
└── different_attachments
```

Each direct child is an executable test case leaf implemented in the same source file. The six paths appear in the default mustpass list [imageless-framebuffer.txt](../../../mustpass/main/vk-default/imageless-framebuffer.txt#L1-L6).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family / `TestType` | `color` / `TEST_TYPE_COLOR`, `depth_stencil` / `TEST_TYPE_DEPTH_STENCIL`, `color_resolve` / `TEST_TYPE_COLOR_RESOLVE`, `depth_stencil_resolve` / `TEST_TYPE_DEPTH_STENCIL_RESOLVE`, `multisubpass` / `TEST_TYPE_MULTISUBPASS`, `different_attachments` / `TEST_TYPE_DIFFERENT_ATTACHMENTS` | Selects the attachment topology and runtime path. This is the primary behavioral axis. | [`TestType`](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L60-L69), [registration](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2953-L3038) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Supplies the color attachment format for every family. | [registration helpers](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2953-L3022) |
| Depth/stencil format | `VK_FORMAT_UNDEFINED`, `VK_FORMAT_D24_UNORM_S8_UINT` | Enables the combined depth/stencil attachment only for `depth_stencil` and `depth_stencil_resolve`. | [registration helpers](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2965-L2998) |
| Extent and layers | `32 x 32`, one layer | Fixes the framebuffer compatibility dimensions, rendered area, and readback size. | [instance construction](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L953-L969), [attachment image information](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L575-L676) |
| Sample count | `VK_SAMPLE_COUNT_1_BIT`, `VK_SAMPLE_COUNT_4_BIT` | Single-sample families copy attachment images directly. Resolve families also inspect a four-sample source image and a single-sample resolve image. | [single-sample depth path](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1436-L1497), [color resolve](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1684-L1727), [depth/stencil resolve](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1974-L2053) |
| Render pass structure | one subpass, two subpasses, or two render pass instances | Distinguishes ordinary attachment binding, input-attachment reuse across subpasses, and rebinding one framebuffer slot between render pass instances. | [render pass builders](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L233-L548), [`different_attachments` recording](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2596-L2632) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each value changes which attachment compatibility and deferred-binding behavior the test exercises.

### color: one color attachment

`color` is the baseline. The host creates one color image view, creates an imageless framebuffer whose one slot describes a compatible color image, and supplies that view through `VkRenderPassAttachmentBeginInfo`. A draw covers the lower half of the target. The host copies the color image to a buffer and compares it with a black-and-gray reference [runtime path](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1222-L1317).

### depth_stencil: color and combined depth/stencil attachments

`depth_stencil` adds a `VK_FORMAT_D24_UNORM_S8_UINT` view beside the color view. Two overlapping draws produce distinct color, depth, and stencil regions. The test supplies both views at render pass begin, then checks all three aspects independently [attachment binding](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1513-L1524), [result checks](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1586-L1601).

### color_resolve: multisampled color and color resolve

`color_resolve` gives the imageless framebuffer two color-compatible slots: a four-sample render target and a single-sample resolve target. It checks the resolved color image and extracts samples 0 through 3 from the multisampled source for separate comparisons [render and resolve readback](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1684-L1816).

### depth_stencil_resolve: multisampled color/depth/stencil and resolve targets

`depth_stencil_resolve` supplies four views: multisampled color, multisampled depth/stencil, color resolve, and depth/stencil resolve. The render pass uses `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` for both depth and stencil. The host checks the three resolved aspects and every color, depth, and stencil source sample [render pass setup](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L322-L379), [result checks](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2142-L2217).

### multisubpass: input attachment across two subpasses

`multisubpass` supplies two color views to one imageless framebuffer. Subpass 0 writes the first view. Subpass 1 reads it as an input attachment, changes the green channel, and writes the second view. Checking both images verifies the deferred views retain their correct attachment roles across the subpass transition [resource and framebuffer setup](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2285-L2362), [draw and checks](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2383-L2472).

### different_attachments: one framebuffer reused with two views

`different_attachments` creates one imageless framebuffer with one color slot. It begins two render pass instances using the same framebuffer, first with `color0Attachment` and then with `color1Attachment`. Both images must contain the expected draw, proving that the framebuffer does not retain the first supplied view as its fixed attachment [render pass recording](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2533-L2632), [checks](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2672-L2687).

## Shader Analysis

The tests use small vertex and fragment shaders to produce deterministic image patterns, read an input attachment, and extract individual multisample values. Shader compilation and shader semantics are not the tested behavior. The correctness question is whether attachment compatibility descriptions and the image views supplied at render pass begin produce the expected framebuffer results, so this page has no representative shader walkthrough [shader generation](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2724-L2925).

## Runtime Execution and Result Checking

- `makeFramebuffer` builds the common imageless object. It derives one `VkFramebufferAttachmentImageInfo` per attachment slot, chains them through `VkFramebufferAttachmentsCreateInfo`, sets `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT`, and passes `nullptr` for `pAttachments` [framebuffer construction](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L575-L708).
- Each runtime path creates images, memory, views, readback buffers, a compatible render pass, and graphics pipelines. It records the selected views in a `VkRenderPassAttachmentBeginInfo` passed to the render pass begin helper.
- After rendering, image barriers make attachment writes available to transfer operations. The test copies single-sample color, depth, and stencil aspects to host-visible buffers. Resolve cases copy their single-sample resolve images to buffers, then separately render each selected sample from the multisample source into a single-sample verification image and copy that image to a buffer [sample extraction](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L972-L1111).
- The host invalidates mapped memory before reading it. For non-multisampled depth and stencil, helper functions convert aspect values to one-channel color images before comparison [conversion and verification](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L883-L922), [`verifyBuffer`](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1135-L1175).
- `verifyBufferInternal` first tries an exact byte comparison. If that differs, `tcu::intThresholdCompare` permits an unsigned per-channel difference of 1. A family passes only when every aspect, sample, subpass output, or rebound image selected by that family matches its procedural reference [comparison](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1114-L1132).

| Family | Host-visible outputs checked |
|--------|------------------------------|
| `color` | color attachment |
| `depth_stencil` | color, depth, stencil |
| `color_resolve` | resolved color and color samples 0 through 3 |
| `depth_stencil_resolve` | resolved color, depth, stencil and samples 0 through 3 of each source aspect |
| `multisubpass` | subpass 0 color and subpass 1 color |
| `different_attachments` | first supplied color view and second supplied color view |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color` | Basic imageless color-slot creation, begin-time view binding, rendering, or readback did not produce the reference image. |
| `depth_stencil` | Deferred binding or attachment processing failed for the color, depth, or stencil aspect. |
| `color_resolve` | Deferred binding, multisample color storage, color resolve, or per-sample extraction did not match the expected samples and resolve result. |
| `depth_stencil_resolve` | One of the four deferred attachment bindings, sample-zero depth/stencil resolve, color resolve, or per-aspect sample paths produced an incorrect image. |
| `multisubpass` | Attachment roles or visibility across the subpass dependency and input-attachment read produced an incorrect first or second image. |
| `different_attachments` | Reusing one imageless framebuffer retained, redirected, or otherwise mishandled one of the two views supplied to separate render pass instances. |

A failure in any family can also come from the shared copy, synchronization, or comparison path rather than the imageless framebuffer operation itself.

### Cause Analysis

#### Imageless attachment description or begin-time binding mismatch

**Possible failure symptoms:** One or more checked images contain the clear value, data from the wrong image view, missing geometry, or pixels that differ from the procedural reference. In `different_attachments`, one target may be correct while the other remains clear or contains data intended for the other view.

**Possible implementation causes:** The implementation may mishandle the separation between framebuffer compatibility information and the image views supplied through `VkRenderPassAttachmentBeginInfo`. The specification requires matching attachment counts and compatible flags, usage, dimensions, layers, view formats, attachment formats, and sample counts [render pass begin validity](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7250-L7257), [view compatibility rules](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7265-L7357), [sample count rule](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7385-L7399). A defect in slot association or render pass begin state can therefore direct operations to the wrong view or fail to use a supplied view.

#### Attachment-role, resolve, or subpass processing failure

**Possible failure symptoms:** `depth_stencil` reports only color, depth, or stencil as incorrect; a resolve family reports a resolved aspect or named source sample as incorrect; `multisubpass` reports `ColorSubpass0` or `ColorSubpass1` as incorrect.

**Possible implementation causes:** The failing label narrows the affected operation. Possible causes include incorrect use of an imageless slot as a depth/stencil, resolve, or input attachment; incorrect four-sample storage or resolve processing; failure to apply sample-zero depth/stencil resolve; or incorrect execution of the subpass dependency before the input-attachment read. The source checks these outputs separately, so a single-aspect or single-subpass failure need not indicate that all deferred view binding failed.

#### Shared transfer, synchronization, or comparison path failure

**Possible failure symptoms:** Several unrelated families or outputs fail with incorrect readback despite rendering to the intended attachments. Resolve failures may affect the demultisampled verification image rather than only the resolved target.

**Possible implementation causes:** The common path transitions attachment images for transfer or sampling, copies verification images to host-visible buffers, waits for submission, invalidates mapped memory, and performs threshold comparison. Incorrect synchronization, image-to-buffer copy behavior, multisample sampling, or host visibility can corrupt the observation used by the test. Source-level investigation is needed to distinguish such a failure from the framebuffer operation when the logged image does not identify a specific attachment-stage defect.

## Case Pruning

### Requirement-based pruning

- Every family requires `VK_KHR_imageless_framebuffer` functionality and `imagelessFramebuffer == VK_TRUE`. Unsupported implementations report `NotSupported` before execution [base instance checks](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L953-L969).
- `checkImageFormatProperties` rejects a fixed format when the required optimal-tiling usage, one layer, or `32 x 32` extent is unavailable. Depth/stencil families repeat this check for `VK_FORMAT_D24_UNORM_S8_UINT`; resolve families include sampled-image usage because they extract individual samples [format support helper](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L845-L868), [resolve usage checks](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1620-L1629).
- `color_resolve` and `depth_stencil_resolve` require `limits.standardSampleLocations == VK_TRUE` [case support](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2715-L2722).
- `depth_stencil_resolve` also requires `VK_KHR_depth_stencil_resolve` [instance construction](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1835-L1863). Vulkan requires sample-zero support for both depth and stencil resolve modes when those operations are available [limits.adoc](../../../../vulkan-docs/src/chapters/limits.adoc#L3127-L3162).

### Design-based pruning

- Registration creates exactly six fixed leaves. The source does not generate combinations of formats, extents, layer counts, sample counts, resolve modes, or attachment orders [registration](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2953-L3038).
- `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_D24_UNORM_S8_UINT`, a `32 x 32` extent, one layer, and four samples in resolve families are deliberate fixed choices. They keep the matrix focused on attachment roles and deferred image-view binding rather than broad format or size coverage.
- `TEST_TYPE_LAST` is an enum sentinel and is never registered as a test family [test type enum](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L60-L69).

## Key Takeaways

- All six test families exercise the same two-stage contract: compatibility information at framebuffer creation and concrete image views at render pass begin.
- The test-family axis covers basic color, depth/stencil, color resolve, depth/stencil resolve, a two-subpass input attachment, and reuse of one framebuffer with two different views.
- The shaders only create or extract deterministic values. Host-side image comparisons test the framebuffer results.
- The logged aspect, sample, subpass, or target name helps distinguish a slot-binding failure from resolve, subpass, transfer, or readback behavior. See `## Failure Meaning` for the mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Root test category registration | [vktTestPackage.cpp#L1378-L1385](../../../modules/vulkan/vktTestPackage.cpp#L1378-L1385) | Registers `imageless_framebuffer` under `dEQP-VK`. |
| Test type and fixed parameters | [vktImagelessFramebufferTests.cpp#L60-L89](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L60-L89) | Defines the six implementation variants and their parameter record. |
| Imageless framebuffer construction | [vktImagelessFramebufferTests.cpp#L575-L708](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L575-L708) | Builds compatibility descriptions and creates the framebuffer without image views. |
| Common verification path | [vktImagelessFramebufferTests.cpp#L883-L1208](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L883-L1208) | Converts depth/stencil data, extracts samples, generates references, and compares readback. |
| Six runtime implementations | [vktImagelessFramebufferTests.cpp#L1222-L2688](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1222-L2688) | Implements rendering, copyback, and checks for every test family. |
| Support and shader setup | [vktImagelessFramebufferTests.cpp#L2691-L2927](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2691-L2927) | Applies resolve support checks and generates the utility shaders used by each path. |
| Family dispatch and registration | [vktImagelessFramebufferTests.cpp#L2930-L3040](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2930-L3040) | Maps each registered leaf to its instance class and creates the exact six-child hierarchy. |
| Default mustpass entries | [imageless-framebuffer.txt#L1-L6](../../../mustpass/main/vk-default/imageless-framebuffer.txt#L1-L6) | Confirms all six executable paths. |
| Imageless framebuffer specification | [renderpass.adoc#L6180-L6269](../../../../vulkan-docs/src/chapters/renderpass.adoc#L6180-L6269) | Defines attachment compatibility information and `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT`. |
| Begin-time attachment validity | [renderpass.adoc#L7243-L7400](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7243-L7400) | Defines how supplied image views must match an imageless framebuffer and render pass. |
