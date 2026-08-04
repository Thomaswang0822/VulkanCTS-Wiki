## Overview

**Core question:** Do framebuffer attachment configurations confine rendering to the intended area and handle attachment roles and fragment-output routing correctly?

- [`vktPipelineFramebufferAttachmentTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1) implements the `framebuffer_attachment` test family under each supported pipeline-construction root.
- The family combines image-size, attachment-role, and fragment-output cases: larger images behind a smaller framebuffer, no color attachments, unused references, different attachment sizes, input-plus-resolve pairing, and color attachments that the fragment shader does not export.
- Most leaves validate copied image data with `tcu::intThresholdCompare`; `unused_attachment` passes after successfully creating the render pass and framebuffer and recording render-pass begin/end commands. It does not submit that command buffer.
- The split mustpass files contain 50 monolithic leaves, 49 fast-linked-library leaves, 49 pipeline-library leaves, 48 leaves for each linked or unlinked binary and linked-SPIR-V shader-object root, and 49 unlinked-SPIR-V shader-object leaves.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Framebuffer and render area.** A framebuffer binds image views to a render pass and has a width and height. The image views can cover larger images. The [render area](../../../../vulkan-docs/src/chapters/renderpass.adoc#render-pass-begin) used to begin a render pass, together with the viewport and scissor, constrains the region a draw can modify.
- **Attachment roles.** A subpass can use [color, input, and resolve attachments](../../../../vulkan-docs/src/chapters/renderpass.adoc#render-pass). [`VK_ATTACHMENT_UNUSED`](../../../../vulkan-docs/src/chapters/renderpass.adoc#VK_ATTACHMENT_UNUSED) deliberately leaves an attachment reference unused. Fragment shader output locations select color attachment slots.
- **Image observation.** CTS can transition an attachment to a transfer-source layout, copy it to a host-visible buffer, and compare the copied pixels against an expected image. This family allows a component threshold of `tcu::UVec4(1)`.

## Registration Hierarchy

```text
pipeline.monolithic.framebuffer_attachment
├── 1d_19_32
├── no_attachments
├── unused_attachment
├── diff_attachments_1d_19_32
├── resolve_input_same_attachment
└── multi_attachments_not_exported_2d_64x64_64x64
```

The tree uses the monolithic root as one concrete parseable hierarchy. The same family appears under the supported fast-linked-library, pipeline-library, and shader-object construction roots. The complete leaf inventory is registered by [`addAttachmentTestCasesWithFunctions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1938-L2096).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Pipeline construction type | monolithic, fast-linked-library, pipeline-library, shader-object variants | Reuses the attachment behavior across construction mechanisms; source-level restrictions remove leaves that need a render pass input attachment or the unused-reference path. | [`registration`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2029-L2083) |
| Image view type | `1d`, `1d_array`, `2d`, `2d_array`, `cube`, `cube_array` | Larger-attachment cases cover dimensional and layered image-view handling. | [`case definitions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1941-L2015) |
| Render and attachment sizes | `32` vs `64`, `48`, `39`; `19` vs `32`; 2D equivalents | The attachment is strictly larger than the framebuffer's render extent. | [`case definitions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1941-L2015) |
| Layer count | 1, 4, 6, 12 | Array and cube variants draw and validate every selected layer. | [`case definitions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1952-L1994) |
| Multisampling | single sample, `_ms` with `VK_SAMPLE_COUNT_4_BIT` | The family tests direct color writes and multisample color writes followed by resolve. | [`pipeline state`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L205-L216) |
| Multiple-attachment type | `MULTI_ATTACHMENTS_DIFFERENT_SIZES`, `MULTI_ATTACHMENTS_NOT_EXPORTED` | Selects either different extents for three color attachments or a shader that omits one output. | [`enum`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L75-L80) |

## Behavior Parameters

The primary behavioral axis is the attachment behavior family. It changes the correctness rule, not merely the image dimensions or construction root.

### Larger-than-framebuffer attachments: preserve pixels outside the render area

These leaves create color images larger than the framebuffer and render a full-screen quad through a framebuffer, viewport, scissor, and render area sized from `renderSize`. CTS clears the whole image to black, expects the rendered rectangle to become `(1.0, 0.5, 0.25, 1.0)`, and expects every other checked pixel to remain black. Multisample leaves render to a four-sample image and resolve to the copied single-sample image.

### No attachments: write a storage image without a color attachment

`no_attachments` and `no_attachments_ms` use a render pass with zero color attachments. The fragment shader writes the observable result with `imageStore`, so the test checks fragment execution without a color output attachment. The no-attachment support path requires `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS`, `geometryShader` or `tessellationShader`, and, for `_ms`, `DEVICE_CORE_FEATURE_SAMPLE_RATE_SHADING`.

### Unused attachment: accept `VK_ATTACHMENT_UNUSED`

`unused_attachment` builds a render pass whose color attachment reference is `VK_ATTACHMENT_UNUSED`, creates its framebuffer, and records render-pass begin/end commands. It does not submit the command buffer, so this leaf covers host-side object creation and command recording rather than device execution. This test case leaf is registered only for monolithic and shader-object-unlinked-SPIR-V construction.

### Different attachment sizes: keep three color targets independent

The `diff_attachments_*` leaves use three color attachments with different sizes and clear colors. Their fragment shader writes separate values to locations 0, 1, and 2. The expected images distinguish the rendered region from each target's clear color, which reveals cross-attachment clears, output routing, or copyback errors.

### Resolve/input same attachment: read the resolve target as an input attachment

`resolve_input_same_attachment` uses a multisampled color attachment and a single-sample attachment that appears both as the subpass input attachment and the resolve attachment. The fragment shader loads the input with `subpassLoad` and produces a color containing the input's green component. The source omits this leaf for shader-object construction because this path uses input attachments rather than dynamic rendering.

### Attachments not exported by the fragment shader: route only written color outputs

The `multi_attachments_not_exported_*` leaves bind three color attachments but use a fragment shader that writes locations 0 and 2 only. CTS does not compare the location-1 attachment because its post-draw contents may be undefined; it compares locations 0 and 2 against their expected rendered values.

## Shader Analysis

Shader code supplies the observable writes, but this family tests attachment configuration and output routing rather than shader algorithm correctness. The source generates compact shaders for each behavior:

- [`initColorPrograms`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L296-L331) writes one location-0 color output.
- [`initDifferentAttachmentSizesPrograms`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1785-L1826) writes locations 0, 1, and 2.
- [`initMultiAttachmentsNotExportPrograms`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1828-L1868) declares locations 0, 1, and 2 but writes only 0 and 2.
- [`initInputResolveSameAttachmentPrograms`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1366-L1405) reads `subpassInput` and writes a derived location-0 color.

## Runtime Execution and Result Checking

- The larger-attachment path creates color images, optionally creates a four-sample color image, fills the relevant image with black, transitions it for attachment use, draws one quad per layer, transitions the resolved or single-sample image to a transfer source, and copies the full attachment to a host-visible buffer. [`getExpectedData`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L333-L352) encodes the rendered rectangle and untouched exterior before comparison.
- `testNoAtt` creates and clears a storage image, records a render pass with no color attachments, lets the fragment shader write the storage image, copies it to the host, and compares the expected values. [`testNoAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L768-L954)
- `testMultiAttachments` gives each render target a distinct clear color, renders a quad, and copies all three targets. Different-size leaves compare all three images; not-exported leaves compare locations 0 and 2 and skip location 1. [`testMultiAttachments`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1017-L1364)
- `testInputResolveSameAttachment` creates the multisample color image and the single-sample input/resolve image, clears them to distinct colors, binds the input-attachment descriptor set, draws, copies the single-sample image, and compares it. [`testInputResolveSameAttachment`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1478-L1752)
- `testUnusedAtt` has no pixel readback and does not submit its command buffer. It passes after framebuffer creation and recording render-pass begin/end commands. [`testUnusedAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1754-L1783)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Larger-than-framebuffer attachments | Rasterization, framebuffer extent, viewport/scissor, layer, resolve, or transfer-copy handling writes or reports pixels outside the expected render area. |
| No attachments | The implementation does not execute fragment storage-image writes correctly when the render pass has no color attachment. |
| Unused attachment | Render-pass/framebuffer creation or command recording rejects or mishandles `VK_ATTACHMENT_UNUSED`; this leaf does not submit the recorded commands. |
| Different attachment sizes | Per-attachment clears, output routing, or image copies leak values between color attachments with different extents. |
| Resolve/input same attachment | Input-attachment reads, multisample resolve, or their attachment-role pairing produces the wrong resolved image. |
| Attachments not exported by the fragment shader | One of the two exported outputs produces the wrong copied image. The test does not compare the unexported location-1 attachment, so this result cannot show whether that attachment was modified. |

### Cause Analysis

#### Render-area, rasterization, resolve, or copy handling

**Possible failure symptoms:** A copied image differs from the generated expected image: pixels outside the smaller render area are no longer black, the rendered rectangle has the wrong color, a layer differs, or a multisample result does not match the resolved expected image.

**Possible implementation causes:** Source-level investigation should separate framebuffer or render-area setup from viewport/scissor clipping, layered rendering, color resolve, layout transition, and transfer-copy handling. The test combines those steps before the host compares the complete attachment.

#### Fragment storage-image execution without a color attachment

**Possible failure symptoms:** The no-attachment storage image differs from its expected result after the render pass, including the sample-dependent form.

**Possible implementation causes:** The failure can involve the no-color-attachment render-pass path, fragment-stage `imageStore`, primitive-ID generation, sample-ID handling, image layout transitions, or host copyback. The feature checks make unsupported prerequisites a skip rather than a failed result.

#### Unused attachment reference handling

**Possible failure symptoms:** `unused_attachment` fails before returning its pass status, such as during render-pass or framebuffer creation or command recording.

**Possible implementation causes:** The source performs no draw, queue submission, or comparison in this leaf. A failure points to host-side render-pass/framebuffer creation or command-recording handling for a color attachment reference set to `VK_ATTACHMENT_UNUSED`; it provides no evidence about device execution of the recorded commands.

#### Independent color attachment state and output routing

**Possible failure symptoms:** In a different-size leaf, one of the three copied targets differs from its expected rendered or clear color. In a not-exported leaf, exported location 0 or 2 differs from its expected rendered color; location 1 is copied but deliberately skipped during comparison.

**Possible implementation causes:** A different-size result may indicate incorrect per-attachment extent handling, clear state, fragment output-location routing, image layout transition, or transfer copy. A not-exported result covers routing and result handling for the two written outputs only; because CTS skips location 1, it cannot diagnose unwritten-attachment preservation. The comparisons identify the affected checked target but do not isolate a single internal operation.

#### Input attachment and resolve attachment pairing

**Possible failure symptoms:** The copied single-sample image from `resolve_input_same_attachment` differs from the color derived from the loaded input attachment.

**Possible implementation causes:** The error can involve `subpassLoad`, descriptor binding for `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT`, the transition to `VK_IMAGE_LAYOUT_GENERAL`, multisample resolve, or the attachment-role pairing. The test uses the same single-sample image as input and resolve target, so the final image cannot isolate those stages without source-level investigation.

## Case Pruning

### Requirement-based pruning

- `checkSupportNoAtt` skips the no-attachment leaves when fragment stores and atomics, `geometryShader` or `tessellationShader`, or multisample sample-rate shading are unavailable. [`checkSupportNoAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1923-L1936)
- All leaves call the pipeline-construction requirement checker for their selected construction type. [`checkConstructionTypeSupport`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1912-L1921)
- The resolve/input leaf is not registered for shader objects because input attachments are not supported with dynamic rendering in this test path. [`registration`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2073-L2083)

### Design-based pruning

- Multisample larger-attachment cases cover only `2d` and `2d_array`; the source does not create multisample 1D or cube variants. [`case definitions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1997-L2015)
- `unused_attachment` is intentionally limited to monolithic and shader-object-unlinked-SPIR-V construction. [`registration`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2029-L2033)
- Different-size attachment leaves use 1D and 2D forms, while not-exported attachment leaves use the fixed 2D 64x64 arrangement. [`registration`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2035-L2096)

## Key Takeaways

- The image-comparison leaves observe complete copied images for every checked attachment, so untouched regions matter as much as rendered pixels. The not-exported leaves deliberately exclude the unwritten location-1 attachment from comparison.
- The larger-attachment leaves make the framebuffer extent visible by clearing the full image before drawing only within the smaller render area.
- `no_attachments`, `unused_attachment`, and `resolve_input_same_attachment` cover attachment arrangements that ordinary single-color-output rendering does not exercise.
- A failure in the multi-attachment paths identifies an affected result image but may involve several host and device operations before CTS compares it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Family registration | [`createFramebufferAttachmentTests`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L2101-L2105) | Creates the `framebuffer_attachment` test family. |
| Case matrix and construction restrictions | [`addAttachmentTestCasesWithFunctions`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1938-L2096) | Registers the leaf matrix and its special-case exclusions. |
| Larger attachment test | [`test`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L359-L655) | Validates writes inside a smaller render area on a larger attachment. |
| No attachment test | [`testNoAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L768-L954) | Validates storage-image output from a render pass with no color attachment. |
| Multiple attachment test | [`testMultiAttachments`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1017-L1364) | Validates different-size and not-exported attachment results. |
| Input/resolve test | [`testInputResolveSameAttachment`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1478-L1752) | Validates the input-attachment and resolve-target arrangement. |
| Unused attachment test | [`testUnusedAtt`](../../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1754-L1783) | Covers host-side creation and command recording with `VK_ATTACHMENT_UNUSED`; the command buffer is not submitted. |
| Pipeline dispatcher | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L159) | Attaches the family below each selected construction root. |
